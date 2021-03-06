r"""
Solve Biharmonic equation in 2D with homogeneous Dirichlet and
Neumann boundary conditions in both directions

    \nabla^4 u = f,

Use Shen's Biharmonic basis for both directions.

"""
import sys
import os
from sympy import symbols, sin
import numpy as np
from shenfun import inner, div, grad, TestFunction, TrialFunction, Array, \
    Function, TensorProductSpace, FunctionSpace, comm
from shenfun.la import SolverGeneric2ND

assert comm.Get_size() == 1, "Two non-periodic directions only have solver implemented for serial"

# Collect basis and solver from either Chebyshev or Legendre submodules
family = sys.argv[-1].lower() if len(sys.argv) == 2 else 'chebyshev'

# Use sympy to compute a rhs, given an analytical solution
x, y = symbols("x,y", real=True)
ue = (sin(2*np.pi*x)*sin(4*np.pi*y))*(1-x**2)*(1-y**2)
fe = ue.diff(x, 4) + ue.diff(y, 4) + 2*ue.diff(x, 2, y, 2)

# Size of discretization
N = (30, 30)

S0 = FunctionSpace(N[0], family=family, bc='Biharmonic')
S1 = FunctionSpace(N[1], family=family, bc='Biharmonic')
T = TensorProductSpace(comm, (S0, S1), axes=(0, 1))

u = TrialFunction(T)
v = TestFunction(T)

# Get f on quad points
fj = Array(T, buffer=fe)

# Compute right hand side of biharmonic equation
f_hat = inner(v, fj)

# Get left hand side of biharmonic equation
matrices = inner(v, div(grad(div(grad(u)))))

# Create linear algebra solver
H = SolverGeneric2ND(matrices)

# Solve and transform to real space
u_hat = Function(T)           # Solution spectral space
u_hat = H(f_hat, u_hat)       # Solve
uq = u_hat.backward()

# Compare with analytical solution
uj = Array(T, buffer=ue)
print(abs(uj-uq).max())
assert np.allclose(uj, uq)

if 'pytest' not in os.environ:
    import matplotlib.pyplot as plt
    plt.figure()
    X = T.local_mesh(True)
    plt.contourf(X[0], X[1], uq)
    plt.colorbar()

    plt.figure()
    plt.contourf(X[0], X[1], uj)
    plt.colorbar()

    plt.figure()
    plt.contourf(X[0], X[1], uq-uj)
    plt.colorbar()
    plt.title('Error')
    plt.show()
