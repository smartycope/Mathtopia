from .Equation import Equation
from .namespaces import logic


clockPeriod = Equation('T == t_comb + t_setup + t_clk2q', logic)
clockFrequency = Equation('f == 1/(t_comb + t_setup + t_clk2q)', logic)
t_path = Equation('t_path == t_clk2q + t_comb + t_setup', logic)
maxFrequency = Equation('f_max == 1/(t_clk2q + t_comb + t_setup)', logic)
frequency2period = Equation('f == 1/T', logic)
