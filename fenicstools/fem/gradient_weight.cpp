
#include "dolfin.h"

namespace dolfin
{
  void compute_weight(Function& DG)
  { // Compute weights for averaging with neighboring cells
      
    // Get the mesh, element and dofmap
    boost::shared_ptr<const FunctionSpace> V = DG.function_space(); 
    boost::shared_ptr<const Mesh> mesh = V->mesh();
    boost::shared_ptr<const FiniteElement> element = V->element();
    boost::shared_ptr<const GenericDofMap> dofmap_u = V->dofmap();
    
    // Allocate storage for weights on one cell
    std::vector<double> ws(element->space_dimension()); 
        
    // Compute weights
    GenericVector& dg_vector = *DG.vector();  
    dg_vector.zero();
    for (CellIterator cell(*mesh); !cell.end(); ++cell)
    {
      const std::vector<dolfin::la_index>& dofs
        = dofmap_u->cell_dofs(cell->index());
        
      std::fill(ws.begin(), ws.end(), 1./cell->volume());
      dg_vector.add(ws.data(), dofs.size(), dofs.data());      
    }  
    dg_vector.apply("insert");  
  }
  
  std::size_t dof_owner(std::vector<std::pair<std::size_t, std::size_t> > all_ranges,
                        std::size_t dof)
  {
    for (std::size_t i=0; i < all_ranges.size(); i++)
    {
      if (dof >= all_ranges[i].first && dof < all_ranges[i].second)
        return i;
    }
  }
  
  void compute_DG0_to_CG_weight_matrix(GenericMatrix& A, Function& DG)
  {
    compute_weight(DG);

    std::vector<std::size_t> columns;
    std::vector<double> values;
    std::vector<std::vector<std::size_t> > allcolumns;
    std::vector<std::vector<double> > allvalues;
    
    const std::pair<std::size_t, std::size_t> row_range = A.local_range(0);
    const std::size_t m = row_range.second - row_range.first;
    GenericVector& weight = *DG.vector();
    const std::pair<std::size_t, std::size_t> weight_range = weight.local_range();
    int dm = weight_range.second-weight_range.first;
    
    // Communicate local_ranges of weights
    std::vector<std::pair<std::size_t, std::size_t> > all_ranges;
    MPI::all_gather(weight_range, all_ranges);
    
    // Number of MPI processes
    std::size_t num_processes = MPI::num_processes();

    // Some weights live on other processes and need to be communicated
    // Create list of off-process weights
    std::vector<std::vector<std::size_t> > dofs_needed(num_processes);    
    for (std::size_t row = 0; row < m; row++)
    {   
      // Get global row number
      const std::size_t global_row = row + row_range.first;
      
      A.getrow(global_row, columns, values);
      
      for (std::size_t i = 0; i < columns.size(); i++)
      {
        std::size_t dof = columns[i];
        if (dof < weight_range.first || dof >= weight_range.second)
        {
          std::size_t owner = dof_owner(all_ranges, dof);
          dofs_needed[owner].push_back(dof);
        }
      }
    }
    
    // Communicate to all which weights are needed by the process
    std::vector<std::vector<std::size_t> > dofs_needed_recv;
    MPI::all_to_all(dofs_needed, dofs_needed_recv);
    
    // Fetch the weights that must be communicated
    std::vector<std::vector<double> > weights_to_send(num_processes);    
    for (std::size_t p = 0; p < num_processes; p++)
    {
      if (p == MPI::process_number())
        continue;
      
      std::vector<std::size_t> dofs = dofs_needed_recv[p];
      std::map<std::size_t, double> send_weights;
      for (std::size_t k = 0; k < dofs.size(); k++)
      {
        weights_to_send[p].push_back(weight[dofs[k]]);
      }
    }
    std::vector<std::vector<double> > weights_to_send_recv;
    MPI::all_to_all(weights_to_send, weights_to_send_recv);
    
    // Create a map for looking up received weights
    std::map<std::size_t, double> received_weights;
    for (std::size_t p = 0; p < num_processes; p++)
    {
      if (p == MPI::process_number())
        continue;
      
      for (std::size_t k = 0; k < dofs_needed[p].size(); k++)
        received_weights[dofs_needed[p][k]] = weights_to_send_recv[p][k]; 
    }
    
    for (std::size_t row = 0; row < m; row++)
    {   
      // Get global row number
      const std::size_t global_row = row + row_range.first;
      
      A.getrow(global_row, columns, values);
      for (std::size_t i = 0; i < values.size(); i++)
      {
       std::size_t dof = columns[i];
        if (dof < weight_range.first || dof >= weight_range.second)
        {
          values[i] = received_weights[dof];
        }
        else
        {
          values[i] = weight[columns[i]];  
        }
//        values[i] = 1./values[i];
      }
      
      double s = std::accumulate(values.begin(), values.end(), 0.0);
      std::transform(values.begin(), values.end(), values.begin(),
                std::bind2nd(std::multiplies<double>(), 1./s));      

      for (std::size_t i=0; i<values.size(); i++)
      {
        double w;
        std::size_t dof = columns[i];
        if (dof < weight_range.first || dof >= weight_range.second)
        {
          w = received_weights[dof];
        }
        else
        {
          w = weight[dof];  
        }        
        values[i] = values[i]*w;
//        values[i] = values[i]*values[i];
        
      }     
      
      allvalues.push_back(values);
      allcolumns.push_back(columns);
    }
    for (std::size_t row = 0; row < m; row++)
    {       
      // Get global row number
      const std::size_t global_row = row + row_range.first;
      
      A.setrow(global_row, allcolumns[row], allvalues[row]);
    }
    A.apply("insert");
  }  
  
  void MatMatMult(GenericMatrix& A, GenericMatrix& B, GenericMatrix& C)
  {
    const dolfin::PETScMatrix* Ap = &as_type<const dolfin::PETScMatrix>(A);
    const dolfin::PETScMatrix* Bp = &as_type<const dolfin::PETScMatrix>(B);
    dolfin::PETScMatrix* Cp = &as_type<dolfin::PETScMatrix>(C);  
    // This used to work with MatMatMult modifying C in place.
    //Mat CC = Cp->mat();
    //PetscErrorCode ierr = MatMatMult(Ap->mat(), Bp->mat(), MAT_INITIAL_MATRIX, PETSC_DEFAULT, &CC);
    //C = PETScMatrix(CC);
    PetscErrorCode ierr = MatMatMult(*Ap->mat(), *Bp->mat(), MAT_INITIAL_MATRIX, PETSC_DEFAULT, &(*Cp->mat()));    
  }  

  void compute_weighted_gradient_matrix(GenericMatrix& A, GenericMatrix& dP, GenericMatrix& C, Function& DG)
  {
    compute_DG0_to_CG_weight_matrix(A, DG);
    MatMatMult(A, dP, C);
  }  
}        
