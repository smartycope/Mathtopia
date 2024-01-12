from .Equation import Equation
from .namespaces import fundamentalMath, multivariableCalculus

circumference = Equation('C == 2*pi*r', fundamentalMath, tags={'geometry', 'circles'})
circleArea = Equation('A == pi*r**2', fundamentalMath, tags={'geometry', 'area', 'circles'})

dimensionEqu = Equation('objectDim == vars - numEqu', namespace=multivariableCalculus)

all_math_equations = set([var for name, var in globals().items() if not name.startswith('__') and isinstance(var, Equation)])
