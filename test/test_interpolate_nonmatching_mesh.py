#!/usr/bin/env python

from dolfin import *
from fenicstools import *

def test():
    from dolfin import *
    from numpy import arange
    import time

    # Test for nonmatching mesh and FunctionSpace
    mesh = UnitCubeMesh(16, 16, 16)
    mesh2 = UnitCubeMesh(32, 32, 32)
    V = FunctionSpace(mesh, 'CG', 1)
    V2 = FunctionSpace(mesh2, 'CG', 1)
    # Just create some random data to be used for probing
    x0 = interpolate(Expression('x[0]'), V)
    x0.update()
    u = interpolate_nonmatching_mesh(x0, V2)
    
    VV = VectorFunctionSpace(mesh, 'CG', 1)
    VV2 = VectorFunctionSpace(mesh2, 'CG', 1)
    v0 = interpolate(Expression(('x[0]', '2*x[1]', '3*x[2]')), VV)    
    v0.update()
    v = interpolate_nonmatching_mesh(v0, VV2)
    
    plot(u)
    plot(v, interactive=True)
    
if __name__ == "__main__":
    test()

