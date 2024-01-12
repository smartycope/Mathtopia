from .Equation import Equation
from .namespaces import chemistry
from .constants import c, h

wavelength = frequency = Equation('c == λ * nu', chemistry, defaults={'c': c})
photonEnergy = Equation('E == h*nu', chemistry, help='E is energy of the photon', defaults={'h': h})
photonEnergy2 = Equation('E == (h*c) / λ', chemistry, help='E is energy of the photon', defaults={'h': h, 'c':c})
orbitalEnergy = Equation('E_n == -2.18*(10**-18) * ((Z**2)/(n**2))', chemistry)
denisty = Equation('d == m/v', chemistry)
