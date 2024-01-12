from .Equation import Equation
from .namespaces import waves


complexWaveform = Equation('y_t == A * cos(k * x - ohmega * t + phi) + y', waves,
    help='This may be incorrect, I think I might have messed it up')

sinusoid = Equation('y_t == A * sin(ohmega * t + phi) + y', waves, defaults={'phi': 0, 'y': 0})
cosinusiod = Equation('y_t == A * sin(ohmega * t + phi) + y', waves, defaults={'phi': 0, 'y': 0})

angularFrequency2frequency = frequency2angularFrequency = Equation('angF == 2*pi*f', waves)
period2angFrequency = angularFrequency2period = Equation('T == (2*pi) / angF', waves)
frequency2period = period2frequency = Equation('f == 1/period', waves)

# angFrequency = 2*pi*frequency
# period = (2*pi) / angFrequency
# frequency = 1/period

all_wave_equations = set([var for name, var in globals().items() if not name.startswith('__') and isinstance(var, Equation)])
