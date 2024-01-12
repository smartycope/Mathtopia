from .Equation import Equation, Unit
from .namespaces import physics
from sympy import Symbol
from .constants import *


newtonsLaw = Equation("f == m*a", physics)
newtonsLawGravity = Equation('f == m * g', physics, defaults={'g': 9.805})
newtonsLawFriction = Equation('f == mu * f_N', physics)
# newtonsLawWeight = Equation('w == m * a', physics)
dragEqu = Equation('R == -b * v', physics, tags={'drag'})

thrust = Equation('f == m*v', physics.child(
    Unit('m', 'Mass Flow Rate', 'kg/s'),
    Unit('v', 'Exhaust velocity', 'm/s')
))

# Frantic notes from the notes page
avgVelocity           = Equation('v == d/t',                                                 physics)
# directionalVeloctiy   = Equation('v == Derivative(vec, t)',                                  physicsNamespace)
# directionalAccel      = Equation('a == Derivative(v, t)',                                    physicsNamespace)
# # directionalAccel2     = Equation('a == Derivative(vec**2, t**2)',                            physicsNamespace) # This throws an error??
# finalVec              = Equation('vecf == veci + vi * dt + (1/2)*a*dt**2',                   physicsNamespace)
finalVelocity         = Equation('vf == vi + a*dt',                                          physics)
finalVelocity2        = Equation('vf**2 == vi**2 + 2*a*dvec',                                physics)
vectorMagnitude       = Equation('mag == sqrt(rx**2 + ry**2)',                               physics)
vectorTheta           = Equation('theta == atan(ry/rx)',                                     physics)
# angularAccelIThink    = Equation('a == (v**2) / r',                                          physicsNamespace)
# angularAccelIThink2   = Equation('a == wThing * r',                                          physicsNamespace)
# angularAccelIThink3   = Equation('a == a_t + a_r',                                           physicsNamespace)
# wThingFinal           = Equation('wThingf == wThingi + aThing * dt',                         physicsNamespace)
# wThingFinal2          = Equation('wThingf**2 == wThingi**2 + 2 * aThing * dtheta',           physicsNamespace)
# springForce           = Equation('fs == -k*dx',                                              physicsNamespace)
# anotherWorkEqu        = Equation('Wnet == deltaKE',                                          physicsNamespace)
# anotherWorkEqu2       = Equation('W == F * dvec',                                            physicsNamespace)
# anotherWorkEqu3       = Equation('W == F * vec * cos(theta)',                                physicsNamespace)
# anotherWorkEqu4       = Equation('W_nc == dke + dpe',                                        physicsNamespace)
# powerSomething        = Equation('P == Derivative(W, t)',                                    physicsNamespace)
# finalTheta            = Equation('thetaf == thetai + wThingi * dt + (1/2) * aThing * dt**2', physicsNamespace)
# powerSomething2       = Equation('P == f * v',                                               physicsNamespace)
# someForceThing        = Equation('f == -Derivative(U, r)',                                   physicsNamespace)
# noClueWhatThisIs      = Equation('s == mag * theta',                                         physicsNamespace)
# whatIsThis            = Equation('T == (2*pi*r) / v',                                        physicsNamespace)
# wThing                = Equation('wThing == Derivative(theta, t)',                           physicsNamespace)
# whatIsThis2           = Equation('T == (2*pi) / wThing',                                     physicsNamespace)
# explainMe             = Equation('fNet == m * ((v**2) / r)',                                 physicsNamespace)
# someLeftoverLine      = Equation('f_smax == staticFriction * netForce',                      physicsNamespace)


#* Obvious ones for masterSolve
deltaV = Equation('dv == initv - finalv', physics, tags={'motion'})
deltaV = Equation('v == dv', physics, tags={'motion'})

#* Angular Kinematics
centripitalMotion = Equation('a == (v**2)/r', physics.child(
    Unit('a', 'centripetal acceleration'),
    Unit('v', 'tangential (regular) velocity'),
    Unit('r', 'radius')
), 'The centripetal acceleration is always pointing towards the center', tags={'motion', 'angular motion'})
# angularSpeed = Equation('angs == dang/dt', physicsNamespace)
angularAccel = Equation('angA == dangs/dt', physics, tags={'motion', 'angular motion'})
angularVelocity = Equation('v == angV * r', physics, tags={'motion', 'angular motion'})
angularAcceleration = Equation('angA == Derivative(angV, t)', physics, tags={'motion', 'angular motion'})
kineticEnergyRolling = Equation('ker == (1/2) * I * angV**2 + (1/2) * m * v**2', physics.child(Unit('m', 'the mass of the center of mass')),
    defaults={'v': Symbol('angV')*Symbol('r')},
    help='Remember that v is linear velocity, while angV is the angular velocity!',
    tags={'energy', 'kinetic energy', 'rolling', 'motion'}
)
rps2angV = Equation('angV == 2*pi*T', physics)
rps2linV = Equation('linV == 2*pi*r*T', physics)

#* Kinematics
motionEqu1 = Equation("v == initv - a * t", physics, tags={'motion'})
motionEqu2 = Equation("pos == initPos + initv * t - (1/2)*a*(t**2)", physics, tags={'motion'})
motionEqu3 = Equation("v == sqrt((initv**2) - 2 * a * (p-initp))", physics, tags={'motion'})
angV2linV = linV2angV = Equation("v == r*angV", physics, tags={'motion', 'angular motion'})
angA2linA = linA2angA = Equation('a == r*angA', physics)
ang2dist = dist2ang = Equation('theta == d/r', physics)

#* Energy
kineticEnergy = Equation("ke == (1/2) * m * v**2", physics, tags={'energy', 'kinetic energy'})
gravityPotentialEnergy = Equation("peg == m * g * h", physics, defaults={"g": 9.805}, tags={'energy', 'potential energy'})
# springPotentialEnergy = Equation('pes == (1/2) * k * (dx**2)', physicsNamespace)
loopPotentialEnergy = Equation("pec == m * g * 2 * r", physics, defaults={"g": 9.805}, tags={'energy', 'potential energy'})
totalEnergy = Equation("te == ke + pe", physics, tags={'energy'})
mechanicalEnergy = Equation("me == pe + ke", physics, tags={'energy'})













###################### here #####################






#* Work
# work == delta KE
work = Equation('W == dke', physics)
workEqu = Equation("W == f * mag * cos(theta)", physics, tags={'work'})
workSimple = Equation("W == f * d", physics, tags={'work'})
workEnergyTheorem = Equation("W == ((1/2) * m * vf**2) - ((1/2) * m * vi ** 2)", physics, help='Work is the net work', tags={'work', 'energy'})
workDoneByGravity = Equation("W == m * g * h", physics, defaults={"g": 9.805}, tags={'work'})
conservativeForcePotentialEnergy = Equation('pef - pei == -Integral(Fx, x)', physics, tags={'work'})
workAgainstNonConservativeForce = Equation('mei - wdaf == mef', physics, tags={'work', 'friction'})
workDoneByNonConservativeForce = Equation('W == f * d * cos(theta)', physics.child(
    Unit('W', 'Work done by the force (i.e. friction)'),
    Unit('theta', 'The angle at which the force is pushing the object')
), tags={'work', 'friction'})
friction = Equation('f == mu_k * N', physics, tags={'friction'})

#* Springs
springForce = Equation("f == -k*x", physics, tags={'springs'})
springWork = Equation("W == (1/2) * k * x**2", physics, tags={'springs', 'work'})
springPotentialEnergy = Equation("pes == (1/2) * k * (dx**2)", physics, help='dx is in meters, k is in Newtons/meter', tags={'springs', 'energy', 'potential energy'})

#* Power
physicsPower = Equation('P == W / s', physics, tags={'power'})
physicsPower2 = Equation('P == f / v', physics, tags={'power'})

#* Momentum
momentum = Equation('p == m * v', physics, tags={'momentum'})
# newtonsLawD = Equation('f == m * Derivative(v, t)', physicsNamespace)
newtonsLawD = Equation('f == Derivative(m*v, t)', physics, tags={'momentum'})
newtonsLawMomentum = Equation('f == Derivative(p, t)', physics, tags={'momentum'})
conservationOfLinearMomentum = Equation('p1i + p2i == p1f + p2f', physics.child(
    Unit('p1i', 'object 1\'s initial momentum'),
    Unit('p2i', 'object 2\'s initial momentum'),
    Unit('p1f', 'object 1\'s final momentum'),
    Unit('p2f', 'object 2\'s final momentum'),
), help='Only applies if theres only 2 objects, acting soley from forces caused by each other',
    tags={'momentum'}
)
momentum2energy = energy2momentum = Equation('ke == (p**2)/(2*m)', physics, tags={'momentum', 'energy'})

#* Impulse
# Impulse equals average force over time
avgForceOverTime = Equation('imp == f_avg', physics, tags={'impulse'})
impulse = Equation('imp == Integral(f, t)', physics, tags={'impulse'})
impulseMomentumTheorem = Equation('imp == p_f - p_i', physics, tags={'impulse', 'momentum'})

frequency = Equation('T == 1/f', physics, tags={'frequency', 'waves'})

#* Inertia
rotationalKineticEnergy = Equation('ker == (1/2) * I * wThing**2', physics, tags={'energy', 'kinetic', 'angular motion'})
momentOfInertia = Equation('I == Sum(m_i * r_i**2, (i, 1, n))', physics.child(
    Unit('m_i', 'The mass of a concentric inscribed disk'),
    Unit('r_i', 'The radius of a concentric inscribed disk'),
), tags={'motion', 'inertia'})
momentOfInertiaHoop = Equation('I == m * r**2', physics, tags={'inertia'})
momentOfInertiaCylinder = momentOfInertiaDisk = Equation('I == (1/2) * m * r**2', physics, tags={'inertia'})
momentOfInertiaSphere = Equation('I == (2/5) * m * r**2', physics, tags={'inertia'})
momentOfInertiaPoint = Equation('I == m * r**2', physics, tags={'inertia'})
inertiaEnergyThing = Equation('m*g*h == (1/2) * m * v**2 + (1/2) * I * angV**2', physics, tags={'inertia', 'energy'})
# velocityInertiaEnergyThing = Equation('v == ((2*g*h) / (1 + (I / (m*r**2))))**(1/2)', physics, tags={'inertia', 'energy'}, defaults={"g": 9.805})
velocityInertiaEnergyThing = Equation('v == sqrt(2)*sqrt(h*m*r**2*g/(m*r**2 + I))', physics, tags={'inertia', 'energy'}, defaults={"g": 9.805})
kineticEnergyFlywheel = Equation('kew == (1/2) * I * angv', physics)


#* Torque
torque3 = Equation('tau == f*r*sin(theta)', physics, tags={'torque'})
torque = Equation('tau == cross(f, r)', physics, tags={'torque'})
torque2 = Equation('tau == I*angA', physics, tags={'torque'})
# Just a derivation of the above 2 equations:
inertia2Force = Equation('I*angA == f*r*sin(theta)', physics)
# torque = forceAt90DegreeAngle

# ! net torque in a non-moving system is 0
# radius (and all positions) can be vectors


# Positive torque = counterclockwise
# Negative torque = clockwise

#* Angular Momentum
angularMomentum = Equation('L == cross(r, p)', physics)
angularImpulseMomentumTheorem = Equation('T == Derivative(L, t)', physics, tags={'impulse', 'momentum'})
angularMomentumInertia = Equation('L_xaxis == I * angS', physics)
conservationOfAngularMomentum = Equation('L_i == L_f', physics)

#* SPESS
universalGravityEquation = gravityEqu = Equation('f == G*((m1 * m2)/r**2)', physics, defaults={'G': G, 'm2': 1})
infiniteGravityPotentialEnergy = Equation('pe == (-G*m1*m2)/r', physics, defaults={'G': G, 'm2': 1})
escapeVelocity = Equation('v_esc == sqrt((2*G*M_E/R_E))', physics, defaults={'G': G})
keplers3rdLaw = Equation('T == sqrt(((4*pi**2)/(G*(m1+m2)))*sma**3)', physics, defaults={'G': G, 'm2': 1})


# Kepler's three laws are:
# Planets move in elliptical orbits, with the sun at one focus of the ellipse.
# A line drawn between the sun and a planet sweeps out equal areas during equal intervals of time.
# The square of a planet’s orbital period is proportional to the cube of the semi-major axis length of the elliptical orbit.

all_physics_equations = set([var for name, var in globals().items() if not name.startswith('__') and isinstance(var, Equation)])
