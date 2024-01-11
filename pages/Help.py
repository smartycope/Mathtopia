import streamlit as st

"""
# Welcome to Mathtopia!
"""
st.caption('Yes, I know its a stupid name, but I couldnt think of anything better')

st.markdown("""
Enter an expression, and it will parse it, convert it to a sympy expression, and
solve it for you, give you information on it, and let you play with it in code.

### Notes
- The expression must be valid Python syntax, with some exceptions:
    - *if* implicit multiplication is selected, then you can do things like `3x**2`, and it will parse
    it as 3 * x<sup>2</sup>
        - It will, however, parse `x3*4` as x<sub>3</sub> * 4, **not** x * 3 * 4
    - It will interpret the `^` operator as the exponent operator, *not* the xor operator.
    - You can paste valid LaTeX code into the expression box, and it will parse it
    for you. MathML is not supported, unfortunately.
- Sympy variables like `oo` for infinity are accepted
- There may be multiple solutions, they're all displayed.
- If you specify all the variables manually, it will just return the fuction for you,
it won't try to solve for anything. So you can ignore `= 0` part.
""", unsafe_allow_html=True)

st.divider()

"""
Credits:
Copeland Carter

https://github.com/smartycope/Mathtopia

See my other streamlit project at [ezregex.org](http://ezregex.org)!
"""
