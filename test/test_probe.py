#!/usr/bin/env python

from dolfin import *
from fenicstools import *

def test():
    import time
    #set_log_active(False)
    set_log_level(20)

    mesh = UnitCubeMesh(16, 16, 16)
    #mesh = UnitSquareMesh(10, 10)
    V = FunctionSpace(mesh, 'CG', 1)
    Vv = VectorFunctionSpace(mesh, 'CG', 1)
    W = V * Vv
    
    # Just create some random data to be used for probing
    x0 = interpolate(Expression('x[0]'), V)
    y0 = interpolate(Expression('x[1]'), V)
    z0 = interpolate(Expression('x[2]'), V)
    s0 = interpolate(Expression('exp(-(pow(x[0]-0.5, 2)+ pow(x[1]-0.5, 2) + pow(x[2]-0.5, 2)))'), V)
    v0 = interpolate(Expression(('x[0]', '2*x[1]', '3*x[2]')), Vv)
    w0 = interpolate(Expression(('x[0]', 'x[1]', 'x[2]', 'x[1]*x[2]')), W)
        
    x0.update()
    y0.update()
    z0.update()
    s0.update()
    v0.update()
    w0.update()
    
    x = array([[1.5, 0.5, 0.5], [0.2, 0.3, 0.4], [0.8, 0.9, 1.0]])
    p = Probes(x.flatten(), W)
    x = x*0.9 
    p.add_positions(x.flatten(), W)
    for i in range(6):
        p(w0)
        
    print p.array(2, "testarray")         # dump snapshot 2
    print p.array(filename="testarray")   # dump all snapshots
    print p.dump("testarray")

    # Test StructuredGrid
    # 3D box
    origin = [0.25, 0.25, 0.25]               # origin of box
    vectors = [[1, 0, 0], [0, 1, 0], [0, 0, 1]] # coordinate vectors (scaled in StructuredGrid)
    dL = [0.5, 0.5, 0.5]                      # extent of slice in both directions
    N  = [9, 9, 3]                           # number of points in each direction
    
    ## 2D slice
    #origin = [-0.5, -0.5, 0.5]               # origin of slice
    #vectors = [[1, 0, 0], [0, 1, 0]]    # directional tangent directions (scaled in StructuredGrid)
    #dL = [2., 2.]                      # extent of slice in both directions
    #N  = [50, 50]                           # number of points in each direction
   
    # Test scalar first
    sl = StructuredGrid(V, N, origin, vectors, dL)
    sl(s0)     # probe once
    sl(s0)     # probe once more
    sl.surf(0) # check first probe
    sl.tovtk(0, filename="dump_scalar.vtk")
    sl.toh5(0, 1, 'dump_scalar.h5')
   # sl.toh5(0, 2, 'dump_scalar.h5')
   # sl.toh5(0, 3, 'dump_scalar.h5')
    print sl.arithmetic_mean()
    
    # then vector
    sl2 = StructuredGrid(Vv, N, origin, vectors, dL)
    for i in range(5): 
        sl2(v0)     # probe a few times
    sl2.surf(3)     # Check the fourth probe instance
    sl2.tovtk(3, filename="dump_vector.vtk")
    sl2.toh5(0, 1, 'dump_vector.h5')
    #sl2.toh5(0, 2, 'dump_vector.h5')
    #sl2.toh5(0, 3, 'dump_vector.h5')
    
    # Test statistics
    sl3 = StructuredGrid(V, N, origin, vectors, dL, True)
    for i in range(10): 
        sl3(x0, y0, z0)     # probe a few times
        #sl3(v0)
    sl3.surf(0)     # Check 
    sl3.tovtk(0, filename="dump_mean_vector.vtk")
    sl3.tovtk(1, filename="dump_latest_snapshot_vector.vtk")
    sl3.toh5(0, 1, 'reslowmem.h5')    
        
    # Restart probes from sl3
    sl4 = StructuredGrid(V, restart='reslowmem.h5')
    for i in range(10): 
        sl4(x0, y0, z0)     # probe a few more times    
    sl4.tovtk(0, filename="dump_mean_vector_restart_h5.vtk")
    sl4.toh5(0, 0, 'restart_reslowmem.h5')
    
    # Try mixed space
    sl5 = StructuredGrid(W, N, origin, vectors, dL)
    sl5(w0)     # probe once
    sl5(w0)     # probe once more
    sl5.toh5(0, 1, 'dump_mixed.h5')
    sl6 = StructuredGrid(W, restart='dump_mixed.h5')
    sl6.toh5(0, 1, 'dump_mixed_again.h5')
    
    ## 3D box
    #tol = 1e-8
    #origin = [0.+tol, -1.+tol, -1.+tol]                     # origin of box
    #vectors = [[1, 0, 0], [0, 1, 0], [0, 0, 1]] # coordinate vectors (scaled in StructuredGrid)
    #dL = [4.-2*tol, 2.-2*tol, 2.-2*tol]                           # extent of slice in both directions
    #N  = [10, 10, 10]                           # number of points in each direction
    #mesh = BoxMesh(0., -1., -1., 4., 1., 1., 10, 10, 10)
    #V = FunctionSpace(mesh, 'CG', 1)
    #x0 = interpolate(Expression('x[0]'), V)
    #y0 = interpolate(Expression('x[1]'), V)
    #z0 = interpolate(Expression('x[2]'), V)
    #slc = ChannelGrid(V, N, origin, vectors, dL, True)
    #slc(x0, y0, z0)
    #slc.tovtk(0, 'testing_dump.vtk')
    #slc.toh5(0, 1, 'testing_dump.h5')
    
    
    #WS = W * W
    ##w11 = interpolate(Expression(('x[0]', 'x[1]', 'x[2]', 'x[1]*x[2]', 'x[0]', 'x[1]', 'x[2]', 'x[1]*x[2]')), WS)
    #w11 = interpolate_nonmatching_mesh(Expression(('x[0]', 'x[1]', 'x[2]', 'x[1]*x[2]', 'x[0]', 'x[1]', 'x[2]', 'x[1]*x[2]')), WS)
    #WS2 = W2 * W2
    #w11.update()
    ##x1 = interpolate_nonmatching_mesh(w11, WS2)

    ##ff = File('test_project_nonmatching.pvd')
    ##ff << u
    ##plot(u)
    #plot(w11[0], title='mixed')
    #list_timings()
    
    interactive()
    
if __name__ == "__main__":
    test()

