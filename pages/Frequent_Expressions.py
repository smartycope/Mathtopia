import streamlit as st
from streamlit_extras.switch_page_button import switch_page

def eq(expr):
    if st.button(expr):
        st.session_state['_expr'] = expr
        switch_page('main ')

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
