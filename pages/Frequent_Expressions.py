import streamlit as st
from streamlit_extras.switch_page_button import switch_page

def button(eq):
    if st.button(eq):
        st.session_state['_expr'] = eq
        switch_page('main ')

with st.expander('Volume and Area'):
    "Volume of a Cylinder"
    button("π * height * radius**2")

    "Volume of a Cone"
    button("(1/3) * π * height * radius**2")

    "Volume of a Prism"
    button("base * height")

    "Volume of a Sphere"
    button("(4/3) * π * radius**3")

    "Circumfrence of a Circle"
    button("2 * π * radius")

    "Area of a Circle"
    button("π * radius**2")

    "Area of a Traingle"
    button("(base * height) / 2")

    "Surface Area of a Sphere"
    button("4 * radius**2")

    "Lateral Surface Area of a Cone"
    button("π * radius * slantHeight")

    "Area Between 2 Functions"
    button("Integral(f(x) - g(x), (x, lowerbound, upperbound))")

with st.expander('Math Formulae'):
    "Definition of a Derivative"
    button("Limit((f(x+h) - f(x)) / h, h, 0)")

    "Pythagorean Theorem"
    button("sqrt(a**2 + b**2) = c")

    "Slope Function"
    button("a*x + b = y")

    "Function of a Circle"
    button("x**2 + y**2 = radius**2")

with st.expander('Electronics'):
    "Kirchoff's current law"
    st.caption("The sum of the currents entering a node or closed loop is 0")
    button("Sum(nthCurrentEnteringNode, (n, 1, numBrachesConnectedToNode)) = 0")

    # "Kirchoff's voltage law"
    # st.caption("The sum of the voltages around a closed loop is 0")
    # button("Sum(high=numBrachesInLoop, low='n=1', nthVoltage) == 0")

    "Resistance of a Wire"
    button("resistivity * (length / crossSectionalArea) = Resistance ")

    "Charge or Something"
    button("Integral(time, time_0, current(time) = Charge(time)")

with st.expander('Physics'):
    "Get Velocity with a Constant Acceleration"
    button("velocity_0 + (constantAcceleration * time) = velocity")

    "x Position given a Constant Acceleration"
    button("x_0 + (1/2) * (velocity - velocity_0) * time = x")

    "x Position given a Constant Acceleration 2"
    button("x_0 + (velocity_0 * time) + ((1/2) * constantAcceleration * (time**2)) = x")

    "Velocity**2 given a Constant Acceleration"
    button("(velocity_0**2) + 2 * constantAcceleration * (x - x_0) = velocity**2")

    "Power"
    button("torque * speed = power ")

with st.expander('Motion'):
    "Vertical Velocity"
    button("velocity_y0 - gravity * time = velocity_y ")

    "Vertical Velocity at time"
    button("y_0 + velocity_y0 * time - (1/2)*gravity*(time**2) = y")

    "Hybird Veritical Velocity"
    button("sqrt((velocity_y0**2) - 2 * gravity * (y-y_0)) = velocity_y")

    "Average Angular Speed (𝜔)"
    st.caption("angle is in radians")
    button(" 𝚫angle/𝚫time = avgAngSpeed")

    "Angular Acceleration (𝛼)"
    button("𝚫avgAngSpeed/𝚫time = angAccel")
