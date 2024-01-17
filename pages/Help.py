import streamlit as st
from src.SS import ss

st.set_page_config(layout='wide')
ss.update(__file__)

"""
# Welcome to Mathland!
"""
st.caption('Yes, I know its a stupid name, but I couldnt think of anything better')
print('', )
st.markdown("""
Enter a function, and it will do a bunch of useful stuff to it, like parsing it, converting it to a
sympy expression, solve it for you, give you information on it, and let you play with it in code.

### Usage Notes
- The expression accepts valid Python syntax, with some exceptions:
    - If implicit multiplication is selected, then you can do things like `3x**2`, and it will parse
    it as 3 * x<sup>2</sup>
        - It will, however, parse `x3*4` as x<sub>3</sub> * 4, **not** x * 3 * 4
    - It will interpret the `^` operator as the exponent operator, *not* the xor operator.
    - You can paste valid LaTeX code into the expression box, and it will parse it
    for you.
- Sympy variables like `oo` for infinity are accepted
- All solutions for all variables are displayed
- Feel free to use whole words as variable names for clarity
- If you specify all the variables manually, it will solve the function for you instead of trying to
for anything
- If you use `=` or `==`, it will automatically put the right side in the f(...) = box

#### Bug Notes
- As usual, if something goes wrong, just restart the page, it'll probably fix it.
- If you see an warning saying "The widget with key "..." was created with a default value but also had its value set via the Session State API.",
just ignore it. It's not a problem.
""", unsafe_allow_html=True)

st.divider()

"""
Credits:

Copeland Carter

https://github.com/smartycope/Mathtopia

See my other streamlit project at [ezregex.org](http://ezregex.org)!
"""
