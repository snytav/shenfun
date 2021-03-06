r"""
Solve Poisson equation in 1D with possibly inhomogeneous Dirichlet bcs

    \nabla^2 u = f,

The equation to solve is

     (\nabla^2 u, v) = (f, v)

"""
import sys
from sympy import symbols, sin
import numpy as np
from shenfun import inner, div, grad, TestFunction, TrialFunction, \
    Array, Function, FunctionSpace, dx

assert len(sys.argv) == 3, 'Call with two command-line arguments'
assert sys.argv[-1] in ('legendre', 'chebyshev', 'jacobi')
assert isinstance(int(sys.argv[-2]), int)

# Get family from args
family = sys.argv[-1].lower()

# Use sympy to compute a rhs, given an analytical solution
domain = (0., 4.)
a = 1.
b = -1.
if family == 'jacobi':
    a = 0
    b = 0

x = symbols("x")
d = 2./(domain[1]-domain[0])
x_map = -1+(x-domain[0])*d
ue = sin(4*np.pi*x_map)*(x_map-1)*(x_map+1) + a*(1-x_map)/2. + b*(1+x_map)/2.
fe = ue.diff(x, 2)

# Size of discretization
N = int(sys.argv[-2])

SD = FunctionSpace(N, family=family, bc=(a, b), domain=domain, scaled=True)
u = TrialFunction(SD)
v = TestFunction(SD)

# Get f on quad points
fj = Array(SD, buffer=fe)

# Compute right hand side of Poisson equation
f_hat = Function(SD)
f_hat = inner(v, fj, output_array=f_hat)

# Get left hand side of Poisson equation
A = inner(v, div(grad(u)))

u_hat = Function(SD)
u_hat = A.solve(f_hat, u_hat)
uj = u_hat.backward()
uh = uj.forward()

# Compare with analytical solution
ua = Array(SD, buffer=ue)
print("Error=%2.16e" %(np.sqrt(dx((uj-ua)**2))))
assert np.allclose(uj, ua)
