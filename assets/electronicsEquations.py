from .Equation import Equation, Unit
from .namespaces import electronics
from sympy import symbols, parse_expr, And, Eq, Piecewise

def parallel(*resistors):
    bottom = 0
    for r in resistors:
        bottom += 1/r
    return 1/bottom

def series(*resistors):
    return sum(resistors)

def voltDivider(inVoltage, r1, r2) -> 'voltage in the middle':
    return (inVoltage * r2) / (r1 + r2)

def splitEvenly(amount, *avenues):
    net = parallel(*avenues)
    return [((net / r) * amount) for r in avenues]

def voltageBetweenCapacitors(Vin, C1, C2):
    vn2 = symbols('vn2')
    C1Charge = capacitor(v=Vin-vn2, C=C1)
    C2Charge = capacitor(v=vn2,     C=C2)
    return ensureNotIterable(solve(Eq(C1Charge, C2Charge), vn2))

def maxPower(Vth, Rth) -> 'P_Rl':
    return (Vth ** 2) / ( 4 * Rth)

def norton2Thevinin(In, Rn):
    return (In * Rn, Rn)

def thevinin2Norton(Vth, Rth):
    return (Vth / Rth, Rth)

fivePercentResistor = (1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1)
def roundToMultipliers(value, multipliers=fivePercentResistor, scale=1000):
    return multipliers[findIndex(multipliers, round(value, log(scale, 10) - 1) / scale)] * scale


ll = parallel
s = series

parallelCapacitors = llCap = series
seriesCapacitors = sCap = parallel

parallelInductors = llInd = parallel
seriesInductors = sInd = series

seriesImpedances = series
parallelImpedances = series

seriesAdmittances = parallel
parallelAdmittances = series


ohmsLaw = Equation("v == i*r", electronics)
conductanceSolver = Equation("iGn == (i*Gn)/Geq",{
    'Geq': 'equivalent conductance',
    'Gn': 'conductance of the chosen resistor',
    'i': 'current into resistor',
    'iGn': 'current through the chosen resistoR',
})

#* Op Amps:
opAmpOutput = Equation("Vout == Av * Vin", {
    'Vout': 'the output voltage of the op amp',
    'Av': 'Voltage Gain, Vin = voltage in'
})
invertingOpAmpGain    = Equation("Av == -(Rf / Rin)", electronics.child(
    Unit('Av', 'Voltage Gain'),
    Unit('Rf', 'the resistor connecting the op amp Vout and the op amp negative in terminals'),
    Unit('Rin', 'the resistor between Vin and the op amp negative in'),
    Unit('Vout', 'the output voltage of the op amp'),
    Unit('Vin', 'voltage connected to Rin'),
))
noninvertingOpAmpGain = Equation('Av == 1 + (Rf / R)', electronics.child(
    Unit('Av', 'Voltage Gain'),
    Unit('Rf', 'the resistor connecting the op amp Vout and the op amp negative in terminals'),
    Unit('R', 'the resistor between ground and the op amp negative in'),
    Unit('Vout', 'the output voltage of the op amp'),
    Unit('Vin', 'voltage connected to the op amp positive in'),
))

#* Capacitors:
capacitorEnergy = Equation('W == (1/2) * C * v**2', electronics)
capacitorCurrent = Equation('i == C * Derivative(v, t)', electronics)
capacitorVoltage = Equation('v == (1/C) * Integral(i(t2), (t2, t_0, 1)) + v(t_0)', electronics)
capacitorCharge = Equation('q == C * v', electronics)
plateCapaitor = Equation('C == er*e0 * A/d', electronics.child(Unit('A', 'surface area of each capacitor plate')),  defaults={'e0': 8.854*10**(-12)})

#* Inductors:
# the emf induced in an electric circuit is proportional to the rate of change of the mangetic flux linking the circuit
inductorEnergy = Equation('W == (1/2) * L * i**2', electronics.child(Unit('i', 'final current in the inductor')))
inductorCurrent = Equation('i == (1/L) * Integral(v(t2), (t2, t_0, 1)) + ii', electronics)
inductorVoltage = Equation('v == L * Derivative(i, t)', electronics)
faradayslaw = Equation('vL_t == Derivative(phi, t)', electronics)
# Changing currents in coils induce coil voltages opposite current changes
lenzsLaw = Equation('L == vL_t / Derivative(i, t)', electronics)

solenoid = Equation('L == (N**2 * mu * A) / l', electronics.child(
    Unit('A', 'cross sectional area of the solenoid', 'meters^2'),
    Unit('mu', 'permeability of the core material', 'Henrys/meter'),
    Unit('l', 'length of the solenoid', 'meters')
))

transformerVoltage = Equation('Vs / Vp == Ns / Np', electronics)
transformerCurrent = Equation('Is / Ip == Np / Ns', electronics)

#* Source-Free circuits
# RC == resistor-capacitor circuit
# RL == resistor-inductor circuit
# t == tc * ln(v0/v(t))
# v_c(t) = V_o*E**(-1/tc) -- discharge equation for a source free rc circuit
RCDischargeVoltage = Equation('v_t == vi * _e ** (-t/tc)', electronics)
RCTimeConstant = Equation('tc == Req * C', electronics)
RCChargeVoltage = Equation('v_t == vs + (vi - vs) * _e**(-t/tc)', electronics)
RCChargeCurrent = Equation('i_t == (vs/r) * _e**(-t/tc)', electronics)
someImportantRCEquation = Equation('x_t == x_f+ (x_i - x_f)*_e**(-t/tc)', electronics)

# i_L(t) == I_0*e*(-t/tc)
RLDischargeCurrent = Equation('i_t == ii * _e**(-t/tc)', electronics)
RLTimeConstant = Equation('tc == L/Req', electronics)
# RLChargeCurrent = Equation('i_t == (vs/r) + ((ii - (vs/r)) * _e**(-t/tc))', electronics)
# RLChargeCurrent = Equation('v_t == vs * _e**(-t/tc)', electronics)
# RLChargeCurrent = Equation('v_t == vs * _e**(-t/tc)', electronics)


# inductorCurrent = iL(t) == (1/L) * Integral(high=t, low=0, vL(dummy)ddummy) + i_0
#? Vp = -Np * Derivative(phi, t)
# inductorEnergy = w=integral(high=t, low=t_0, p(t))
#? capacitorVoltage ( vc(t) = 1/C * integrral(t, 0, ???))
#? w = L*integral(i(t), low=0, ???)
# watts == joules / second
# Coulomb = amps / second

#* AC Current
# ACPowerLoss = Equation*('P_loss == i**2 * R_loss', electronics)
ACSine = Equation('v_t == V_m * sin(2*pi*f*t + ph)', electronics)
frequency = Equation('T == 1/f', electronics)

angFrequency = Equation('wThing = 2*pi*f', electronics)

rect2polarMag = Equation('mag == sqrt(a**2 + b**2)', electronics)
rect2polarAng = Equation('theta == atan(b/a)', electronics)

#* Phasors
EulersFormula = Equation('_e**(_i*theta) == cos(theta) + _i*sin(theta)', electronics)
# ohmega == wthing == angularsomething radians/second
EulersFormula = Equation('_e**(_i*ohmega*theta) == cos(ohmega*theta) + _i*sin(ohmega*theta)', electronics)

# somePhasorThing = Equation('v(t) == (r*_e**(_i * phaseAngle) * _e**(_i*ohmega*t))', electronics)

# phasor = Equation('phasor == r*_e**(j*phase)', electronics)
timeDerivativeOfPhasor = Equation('Derivative(cos(2*pi*f*t), t) == (-2*pi*f)*sin(2*pi*f*t)', electronics)
capacitorCurrent = Equation('i_c_t == C*Derivative(v_c_t, t)*i_c_t', electronics)
inductorVoltage  = Equation('v_L_t == L*Derivative(i_L_t, t)*v_L_t', electronics)


#* Impedance
# reactance is the resistance to voltage flow
# resistance is the restistance to current flow
# Or the other way around?

# For inductors
inductorImpedance = Equation('phZ_L == phV_L/phI_L', electronics)
inductorImpedance2 = Equation('phZ_L == _i*ohmega*L', electronics)
inductorImpedance3 = Equation('phZ_L == _i*X_L', electronics)
seriesRLImpedance = Equation('Z_eq_RL == R+_i*X_L', electronics)
inductorReactance = Equation('X_L == ohmega*L', electronics)

#? X_L=delta(ohmega*L)

# For capacitors
capacitorImpedance = Equation('phZ_C == phV_C/phi_C', electronics)
capacitorImpedance2 = Equation('phZ_C == 1/(_i*ohmega*C)', electronics)
capacitorImpedance3 = Equation('phZ_C == -_i*X_C', electronics)
seriesRCImpedance = Equation('Z_eq_RC == R-_i*X_C', electronics)
capacitorReactance = Equation('X_C == 1/(ohmega*C)', electronics)
capacitorReactance2 = Equation('X_C == V_m/I_m', electronics)
# Equation('X_C == 1/(2*pi*f*C)', electronics)(f=5*k, )

resistorImpedance = Equation('phZ == r', electronics)
inductorImpedance = Equation('phZ == _i*X', electronics)
inductorImpedance2 = Equation('phZ == _i*ohmega*L', electronics)
capacitorImpedance4 = Equation('phZ == -_i*X', electronics)
capacitorImpedance5 = Equation('phZ == 1/(_i*ohmega*C)', electronics)

ohmsLawImpedance = Equation('phV == phZ*phI', electronics)

#? X_C == delta(1/(ohmega*C))

impedance = Equation('phZ == phv/phi', electronics)
# impedance = Equation('phZ == r(ohmega) + _i*X(ohmega)', electronics)
admittance = Equation('phY == 1/phZ', electronics)
# impedance = Equation('phY == G(ohmega) + _i*B(ohmega)', electronics)
reactance = Equation('reactance == im(Z)', electronics)

# impedance of a purely resistive AC circuit is R<_0
# Z of an idea capacitor == -j*(1/2*pi*f*c)
# Z of an idea inductor == j*(2*pi*f*L)

# Capcitor current alwasy leasts capacitor voltage by 90 degress

#* AC Power
instantPower = Equation('p_t == v_t * i_t', electronics)
instantPowerSine = Equation('p_t == (1/2) * v_m*i_m * cos(dph) + (1/2)*v_m*i_m * cos(2*ohmega*t + theta_v + theta_i)', electronics)
instantVoltage = Equation('v_t == v_m * cos(ohmega*t + theta_v)', electronics)
instantCurrent = Equation('i_t == i_m * cos(ohmega*t + theta_i)', electronics)

# The average power, in watts, is the average of the instantaneous power over one period.
averagePower = Equation('p == (1/T) * Integral(p_t, (t, 0, T))', electronics)
# Integral(val, (var, low, high))
averagePowerExpanded = Equation('p == (1/T) * Integral((1/2) * v_m*i_m * cos(dph), (t, 0, T)) + (1/T) * Integral((1/2)*v_m*i_m * cos(2*ohmega*t + theta_v + theta_i), (t, 0, T))', electronics)
averagePower2 = Equation('p == (1/2) * v_m * i_m * cos(dph)', electronics, defaults={'theta_i':0, 'theta_v':0})
averagePowerPhasors = Equation('p == (1/2) * re(phV * phI)', electronics)

pureResistivePower = Equation('p == (1/2) * i_m**2 * r', electronics)
pureReactivePower = Equation('p == 0', electronics)

rms = Equation('i_eff == i_rms', electronics)
rmsCurrent = Equation('i_eff == sqrt((1/T) * Integral(i_t**2, (t, 0, T)))', electronics)
rmsVoltage = Equation('i_eff == sqrt((1/T) * Integral(v_t**2, (t, 0, T)))', electronics)
rmsVoltageExpanded = Equation('i_eff == sqrt((1/T) * Integral(i_m**2 * cos(2*pi*f*t), (t, 0, T)))', electronics)
averagePower3 = Equation('p == v_rms*i_rms*cos(dph)', electronics)

#! ADD THESE!
# v_r = phI*r
# phI = phV_s / Z_eq
# P_r = 1/2 * |v_r| * I_m * cos(dph)

deciblePowerScale = Equation('G_db == 10*log(P_out/P_in, 10)', electronics)
decibleVoltageScale = Equation('A_vdb == 20*log(V_out/V_in, 10)', electronics)
systemTransferFunction = Equation('phH == phIn/phOut', electronics)
frequencyDependantVoltageDivider = Equation('V_out == V_s * (Z_C / (r + Z_C))', electronics)
# 1/sqrt(2) -- .707 -- -3db --some important constant?
# when a circuit has a voltage gain magnitude of -3db, the output voltage has a smaller magnitude than the input voltage

#* Diodes
ShockleyDiodeEquation = Equation('I_D==I_S*(_e**(V_D/(n*V_T))-1)', namespace=electronics.child({
    'n':   'Fudge factor depending on application',
}), defaults={'n': 1, 'V_T': 25*(1/1000)})

thermoVoltage = Equation('V_T==(k*temp)/elemC', electronics, defaults={'k': 1.3806503 * 10**-23, 'elemC': 1.602176634*10**-19})


# avgACPowerAbsorved = Equation('P_ac == R/T*Integral(I**2(t), (t, 0, T))', electronics) # 1/T * Integral(I**2(t)*R, (t, 0, T))
avgDCPowerAsorbed = Equation('P_dc == (I_eff**2)*R', electronics)
# I_rmsACSomething = Equation('I_eff == sqrt((1/T)*Integral(I**2(t)*R), (t, 0, T))', electronics)

I_rmsSine = Equation('I_rms == (I_p / sqrt(2))', electronics)
# These 2 are equivalent
# V_rmsSine = Equation('V_rms == (V_p / sqrt(2))', electronics)
V_rmsSine = Equation('V_rms == .707*V_p', electronics)
V_rmsRectified = Equation('V_rms == 1.57 * V_avg', electronics)
V_avgRectified = Equation('(2*V_p) / pi == V_avg', electronics)

# peak2peakRippleVoltage = Equation('V_R == I_load / (f_R*C_f)', electronics.child({'f_R': 'ripple frequency', 'C_f': 'Capacitor in farads', 'V_R': 'ripple voltage'}))

transistorDCCurrentGain = Equation('G_I == C_I / B_I', electronics.child({
    'G_I': 'Current Gain',
    'C_I': 'Collector Current',
    'B_I': 'Base Current'
}))

transistorNortonResistance = Equation('R_n == 𝚫V_CE / 𝚫I_C', electronics.child({
    'R_n': "Norton Resistance",
    '𝚫V_CE': "Voltage across the collector (output) and the emitter (input)",
    '𝚫I_C': "Current at the collector (output)"
}))

transistors = electronics.child({
    'I_C': 'Current at the collector (equals I_E)',
    'I_B': 'Current at the base',
    'B': 'Beta',
    'V_BB': 'Voltage at base',
    'R_E': 'Resistor at the Emitter',
    'V_BE': 'Base voltage with emitter as reference (V_E - V_B)',
    'V_B': 'Voltage at the base',
    'V_E': 'Voltage at the emitter',
    'V_k': 'Knee voltage of the transistor',
    'I_E': 'Current at the emitter (equals I_C)',
})
V_BE = Equation('V_BE == V_E - V_B', transistors)
transistorBeta = Equation('B == I_C/I_B', transistors)
emitterCurrent = Equation('I_E == (V_BB - V_BE)/R_E', transistors)
emitterVoltage = Equation('V_E == V_BB - V_BE', transistors)
baseVoltage = Equation('V_B == (V_src * R2) / (R1 + R2)', transistors)
emitterCurrent2 = Equation('I_E == V_E/R_E', transistors)
transistorCurrent = Equation("I_C == B*I_B", transistors)
voltageGainMagnitude = Equation('A_V == V_out_p / V_in_p', electronics.child({
    'A_V': 'Voltage Gain',
}))
voltageGain = Equation('-abs(A_V) + _i*0 == -V_out_p / V_in_p', electronics.child({
    'A_V': 'Voltage Gain',
}))
"Z_in(base) == Beta * Derivative(r_e(emitterResistor))"  # T model of modeling transistors
commonEmitter = Equation("A_V == -r_c/r_ep", electronics.child({
    'A_V': 'Voltage Gain',
    'r_c': 'resistor at the collector',
    'r_e': 'resistor at the emitter',
}), "Z_in(base) == Beta * Derivative(r_e(emitterResistor)) -- T model of modeling transistors")

peak2peakRippleVoltage = Equation('V_R == I_load / (f_R*C_f)', electronics.child({'f_R': 'ripple frequency', 'C_f': 'Capacitor in farads', 'V_R': 'ripple voltage'}))

V_rmsSine = Equation('V_rms == .707*V_p', electronics)
V_rmsRectified = Equation('V_rms == 1.57 * V_avg', electronics)
V_avgRectified = Equation('(2*V_p) / pi == V_avg', electronics)

relatedToCallendarVanDusen = Equation('V_out == (A_V * (V_plus - V_minus)) + V_ref', electronics)
callendarVanDusenEquation = Equation('T_C == (-R_0*a+sqrt(R_0**2*a**2-4*R_0*b*(R_0-R_prt))) / (2*R_0*b)', electronics, defaults={
    'a': 3.9083*10**-3,
    'b': -5.7750*10**-7,
    'R_0': 1000
})

transistorNortonResistance = Equation('R_n == dV_CE / dI_C', electronics.child({
    'R_n': "Norton Resistance",
    'dV_CE': "Voltage difference across the collector (output) and the emitter (input)",
    'dI_C': "Current difference at the collector (output)"
}))

VDB_AC_Amplifier = transistors.child({
    "Z_in": 'Input Impedance',
    "Z_out": 'outputImpedance',
    'V_in': 'AC Input voltage',
    'I_in': 'Input current',
    'A_V': 'Voltage Gain',
    'r_c': 'resistor at the collector (small AC signal collector resistance)',
    'r_ep': "resistor at the emitter (r_e prime/ r_e')",
    'R1': 'the top left resistor',
    'R2': 'the bottom right resistor',
    'R_E': 'the resistor connected from ground to r_e',
    # 'r_e': 'R_E, when dealing with AC (apparently?)',
    'r_e': 'the resistor connected to the transistor emitter to R_E and C3',
    'C3': 'the capacitor in parallel with R_E',
    'R_c': 'The resistor connected to the transistor collector and V_cc',
    'V_cc': 'DC imput voltage (I think it\'s DC?)',
    'V_B': 'Voltage at the base',
    'R_load': 'The resistor on the far right after C2 (connected to the transistor collector via C2)',
})
isStiffVoltageSource = Equation('R_s < 0.01*R_load', electronics)
# 'A_V == V_out_p / V_in_p' # at a phase angle of -180°
# # Technically:
# '-|A_V| + j0 == -V_out_p / V_in_p'
# voltageGainMagnitude = Equation('A_V == V_out_p / V_in_p', VDB_AC_Amplifier)
VDBVoltageGainMagnitude = Equation('A_V == V_out_p / V_in_p', VDB_AC_Amplifier,
    'at a phase angle of 180°. Technically the equation would be -|A_V| + j0 == -V_out_p / V_in_p')
# total current through ac collector resistance r_c equals beta*i_b
acCollector = Equation('V_out == -B*i_b*r_c', VDB_AC_Amplifier)
# We want a large input and small output impedances
# also equal to paralell(R1, R2, beta*r_ep)
ACInputImpedance = Equation('Z_in == V_in/i_in', VDB_AC_Amplifier)
inputBaseImpedance = Equation('Z_in == B*(r_ep+r_e)', VDB_AC_Amplifier)
inputTotalImpedance = Equation('Z_in_total == paralell(R1, R2, Z_in_base)', VDB_AC_Amplifier)
ACOutputImepdance = Equation('Z_out == r_c', VDB_AC_Amplifier)
# T model of modeling transistors
tModel = Equation("Z_in == B * Derivative(r_e, emitterResistor)", VDB_AC_Amplifier,
    'This is unsure (and Z_in relates to the base?')
commonEmitterPiModel = Equation("A_V == -r_c/r_ep", VDB_AC_Amplifier)
VDBVoltageGain2 = Equation('A_V == -r_c / (r_ep + r_e)', VDB_AC_Amplifier)
VDBAmp1 = Equation('V_B == (V_cc*R2)/(R1+R2)', VDB_AC_Amplifier)
VDBAmp2 = Equation('I_E == V_E / (r_e + R_E)', VDB_AC_Amplifier)
VDBAmp2_5 = Equation('I_E == V_E / R_E', VDB_AC_Amplifier, 'use this one?')
VDBAmp3 = Equation('r_ep == 0.025/I_E', VDB_AC_Amplifier, '(V_B - V_k ) has something to do with given')
VDBAmp4 = Equation('r_c == paralell(R_C, R_load)', VDB_AC_Amplifier)
VDBAmp5 = Equation('V_E == V_B - V_K', VDB_AC_Amplifier)
VDB = 'Voltage Divider Bias'
# V_E = V_B - V_K
# I_E = V_E / R_E
# This should already be somewhere
# 'X_C == 1/(2*pi*f*C)'


VBECurrentLimiter = transistors.child({
    'V_BE': '',
    'Q1': 'The left transistor limiting the current through Q2',
    'Q2': 'The right transistor',
    'Rcl': 'The right resistor connected between Q2 emitter / Q1 base and the Q1 emitter',
    'R1': 'Right top resistor connected to Q1 collector and Q2 base',
})
VBECurrentLimiter1Untested = Equation('Z_in_base_Q2 == B*r_e2', VBECurrentLimiter)
VBECurrentLimiter2Untested = Equation('r_e1 == parellel(R_E, R_L)', VBECurrentLimiter)
VBECurrentLimiter3Untested = Equation('r_e1p == 25*m / I_E', VBECurrentLimiter)
VBECurrentLimiter4Untested = Equation('Av1 == -r_c1 / r_e1p', VBECurrentLimiter, ' == A_VCE')

darlingtonConfig = transistors.child({})
darlingtonConfig1 = Equation('B_total == B1*B2', darlingtonConfig)
darlingtonConfig2 = Equation('I_B2 == I_E2/B2', darlingtonConfig)
darlingtonConfig3 = Equation('I_B1 == I_E1/B1', darlingtonConfig)
darlingtonConfig4 = Equation('A_I == I_E2 / I_B1', darlingtonConfig)

commonCollectorAmp = transistors.child({
    'Ai': 'Current Gain',
    'Z_in_base': 'Impedance in at the base (Usually > 10 kohm)',
    'r_ep': 'r_e\' (should be around 20 ohms or so)',
    'r_e': '',
    'R_th': 'Thevenin equivalent resistance of something?',
    'Av': 'Voltage Gain',
    'R_E': '',
    'R_L': '',
    'I_E': '',
})
commonCollectorAmp1 = Equation('A_i == B', commonCollectorAmp)
commonCollectorAmp2 = Equation('Z_in_base == B * (r_ep + r_e)', commonCollectorAmp)
commonCollectorAmp3 = Equation('Z_out == parallel(R_E, (r_ep + (R_th / B)))', commonCollectorAmp)
commonCollectorAmp4 = Equation('Av == r_e / (r_ep + r_e)', commonCollectorAmp)

mosfets = transistors.child({
    'R_DS_on': 'Resistance between the drain and the soure in the ohmic region when on',
    'V_t': 'Threshold voltage: the voltage you have to apply to turn it on/off, much like knee voltage (get from datasheet)',
    'V_GD': 'Voltage between the drain and the gate',
    'V_DS': 'Voltage between the drain and the source',
    'Fi': 'electic Feild Intensity',
    'mu': 'charge carrier mobility',
    'C_ox': 'gate capacitance per unit area',
    'WL': 'ratio of width / length',
})
mosfets1 = Equation('I_D == I_DSS * (1 - (V_GS / V_GS_off))**2', mosfets)
mosfets2 = Equation('R_DS_on == V_DS_on / I_DS_on', mosfets)
mosfets3 = Equation('V_DS == V_GD - V_t', mosfets)
mosfets4 = Equation('V_SD == V_SG - V_VD', mosfets)
mosfets5 = Equation('B_n == mu_n*C_ox*WL', mosfets)
mosfets6 = Equation('mu == velocity / abs(F_i)', mosfets)
mosfetNChannelActiveRegion = Equation('I_D == (B_n/2)*((V_GS-V_T)**2)', mosfets)
mosfetNChannelOhmicRegion = Equation('I_D == B_n*((V_GS - V_T)*V_DS - ((V_DS**2)/2))', mosfets)

V_GS, V_T, V_DS, I_D = symbols('V_GS, V_T, V_DS, I_D')
cutoff = (0, V_GS < V_T)
active = (parse_expr('(B_n/2)*((V_GS-V_T)**2)'), And(V_GS >= V_T, 0 < V_DS))
ohmic  = (parse_expr('B_n*((V_GS - V_T)*V_DS - ((V_DS**2)/2))'), And(V_GS >= V_T, And(0 <= V_DS, V_DS < V_GS - V_T)))
sahsEq_NChannel = Equation(Eq(I_D, Piecewise(cutoff, active, ohmic)), mosfets)

V_SG, V_T, V_SD, I_D = symbols('V_SG, V_T, V_SD, I_D')
cutoff = (0, V_SG < abs(V_T))
ohmic  = (parse_expr('-B_n*((V_SG - Abs(V_T))*V_SD - ((V_SD**2)/2))'), And(V_SG >= abs(V_T), And(0 <= V_SD, V_SD < V_SG - abs(V_T))))
active = (parse_expr('(-B_n/2)*((V_SG-Abs(V_T))**2)'), And(V_SG >= abs(V_T), V_SD >= V_SG - abs(V_T)))
sahsEq_PChannel = Equation(Eq(I_D, Piecewise(cutoff, active, ohmic)), mosfets)

# at a phase angle of -180°
# Technically:
# impedance of an inductor approches oo as frequency approaches oo
# impedance of a capacitor approches 0 as frequency approaches oo

# e**jwt == ohmega*t
# 'r*_e**(_i*ohmega*t) == ohmega*t'

# magnitude for cos(theta) + j*sin(tehta) == sqrt(cos(theta)**2 + sin(theta)**2)
# mag of cos(theta) + j*sin(theta) ALWAYS == 1
# angle of cos(theta) + j *sin(theta) ALWAYS == theta

# differentiation in the time domain == multiplying by j*ohmega in the phasor domain
# integration in the time domain == dividing by j*ohmega in the phasor domain

# q = C*V_v
# dq/dt = C * dv_c/dt
# i_c(t) = C * d*v_c/dt
# q=Cv_

# series connected capacitors all have the same seperated charge
# 2 capacitors in series --
# The imaginary part of impedance is reactance

#! # for constant dc current, a capaciter behaves like an open circuit -- and no current passes through

# powerDelivered to a capacitor = v*i = v * (C*dv/dt)

# power is the energy rate, p = dw/dt
# energy = w = integral(high=t, low=t_0, p(0) * something he changed the slide)


#* Misc:
# coulombsLaw = Equation()
# magneticFlux =



# t_setup is the min time from signal posedge to clk posedge
#     min time data must be present prior to clk posedge
# t_hold is the min time from clk posedge to signal negedge
#     minimum amount of time the signal has to be held after the clk posedge
# t_clk-q is min time from clk posedge till the combinational logic has an output which is stable
#     delay from clk posedge till flip-flop out
# t_comb is the time the combinational logic takes to run
# t_path == t_clk-q + t_comb + t_setup
# t_path == t_clk-q + t_comb + t_setup










parallelCapacitors = llCap = series
seriesCapacitors = sCap = parallel

parallelInductors = llInd = parallel
seriesInductors = sInd = series

seriesImpedances = series
parallelImpedances = series

seriesAdmittances = parallel
parallelAdmittances = series







all_electronics_equations = set([var for name, var in globals().items() if not name.startswith('__') and isinstance(var, Equation)])
