import streamlit as st
from streamlit_extras.switch_page_button import switch_page

def eq(expr):
    if st.button(expr):
        st.session_state['_expr'] = expr
        switch_page('main ')


"# Math"
with st.expander('Volume and Area'):
    "Volume of a Cylinder"
    eq("π * height * radius**2")

    "Volume of a Cone"
    eq("(1/3) * π * height * radius**2")

    "Volume of a Prism"
    eq("base * height")

    "Volume of a Sphere"
    eq("(4/3) * π * radius**3")

    "Circumfrence of a Circle"
    eq("2 * π * radius")

    "Area of a Circle"
    eq("π * radius**2")

    "Area of a Traingle"
    eq("(base * height) / 2")

    "Surface Area of a Sphere"
    eq("4 * radius**2")

    "Lateral Surface Area of a Cone"
    eq("π * radius * slantHeight")

    "Area Between 2 Functions"
    eq("Integral(f(x) - g(x), (x, lowerbound, upperbound))")


with st.expander('Math Formulae'):
    "Definition of a Derivative"
    eq("Limit((f(x+h) - f(x)) / h, h, 0)")

    "Pythagorean Theorem"
    eq("sqrt(a**2 + b**2) = c")

    "Slope Function"
    eq("a*x + b = y")

    "Function of a Circle"
    eq("x**2 + y**2 = radius**2")


with st.expander('Linear Algebra'):
    "Vector Magnitude"
    eq('sqrt(rx**2 + ry**2) = magnitude')

    "Vector Theta"
    eq('atan(ry/rx) = theta')


"# Physics"
with st.expander('Physics'):
    "Newton's Law"
    eq('mass * acceleration = force')

    "Newton's Law Friction"
    eq('coefficient_friction * newtons = force')

    "Drag Equation"
    eq('-b * velocity = draw_force')

    "Thrust"
    eq('mass_flow_rate * exhaust_velocity = force')

    "Power"
    eq("torque * speed = power ")


with st.expander('Motion'):
    "Vertical Velocity"
    eq("velocity_y0 - gravity * time = velocity_y ")

    "Vertical Velocity at time"
    eq("y_0 + velocity_y0 * time - (1/2)*gravity*(time**2) = y")

    "Hybird Veritical Velocity"
    eq("sqrt((velocity_y0**2) - 2 * gravity * (y-y_0)) = velocity_y")

    "Average Angular Speed (𝜔)"
    st.caption("angle is in radians")
    eq(" 𝚫angle/𝚫time = avgAngSpeed")

    "Angular Acceleration (𝛼)"
    eq("𝚫avgAngSpeed/𝚫time = angAccel")

    "Average Velocity"
    eq('displacement / time = velocity')

    "Get Velocity with a Constant Acceleration"
    eq("velocity_0 + (constantAcceleration * time) = velocity")

    "x Position given a Constant Acceleration"
    eq("x_0 + (1/2) * (velocity - velocity_0) * time = x")

    "x Position given a Constant Acceleration 2"
    eq("x_0 + (velocity_0 * time) + ((1/2) * constantAcceleration * (time**2)) = x")

    "Velocity**2 given a Constant Acceleration"
    eq("(velocity_0**2) + 2 * constantAcceleration * (x - x_0) = velocity**2")

    "Final Velocity"
    eq('velocity_initial + acceleration + delta_time = velocity_final')

    "Final Velocity Alternate"
    eq('sqrt(velocity_initial**2 + 2 * acceleration * dvec) = velocity_final')

    "Motion 1"
    eq('velocity_initial - acceleration * time = velocity')

    "Motion 2"
    eq('position_initial + velocity_initial * time - (1/2) * a * (time**2) = position')

    "Motion 3"
    eq('sqrt((velocity_initial**2) - 2 * a * (momentum - momentum_initial)) = velocity')

    "Angular to Linear Velocity"
    eq('radius * angular_velocity = velocity')

    "Angular to Linear Acceleration"
    eq('radius * angular_acceleration = acceleration')

    "Angle to Distnace"
    eq('distnace / radius = angle')


with st.expander('Angular Kinematics'):
    "Centripital Motion"
    eq('(velocity_tangential**2)/radius = acceleration_centripetal')

    "Angular Acceleration"
    eq('delta_angular_speed / delta_time = velocity_angular')

    "Angular Velocity to Velocity"
    eq("angular_velocity * radius = velocity")

    "Angular Acceleration"
    eq('Derivative(angular_velocity, time) = angular_acceleration')

    "Rolling Kinetic Energy"
    eq('(1/2) * i * angular_velocity**2 + (1/2) * mass * velocity**2')

    "Radians per Second to Angular Velocity"
    eq('2 * π * period = angular_velocity')

    "Radians per Second to Linear Velocity"
    eq('2 * π * radians * period = linear_velocity')


with st.expander('Energy'):
    "Kinetic Energy"
    eq('(1/2) * mass * velocity**2')

    "Potential Energy due to Gravity"
    eq('mass * gravity * height * 2 * radius')

    "Spring Potential Energy"
    eq('(1/2) * k * delta_x**2')

    "Loop Potential Energy"
    eq('mass * gravity * 2 * radius')

    "Total Energy"
    eq('energy_kinetic + energy_potential')


"# Electronics"
with st.expander('Electronics'):
    "Kirchoff's current law"
    st.caption("The sum of the currents entering a node or closed loop is 0")
    eq("Sum(nthCurrentEnteringNode, (n, 1, numBrachesConnectedToNode)) = 0")

    # "Kirchoff's voltage law"
    # st.caption("The sum of the voltages around a closed loop is 0")
    # eq("Sum(high=numBrachesInLoop, low='n=1', nthVoltage) == 0")

    "Resistance of a Wire"
    eq("resistivity * (length / crossSectionalArea) = Resistance ")

    "Charge or Something"
    eq("Integral(time, time_0, current(time) = Charge(time)")
