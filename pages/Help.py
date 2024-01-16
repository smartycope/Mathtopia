import streamlit as st

# Save the main UI state so we can come back to it
st.session_state['_expr'] = st.session_state.get('_expr')
st.session_state['eq'] = st.session_state.get('eq')
st.session_state['vars_dict'] = st.session_state.get('vars_dict')

"""
# Welcome to Mathland!
"""
st.caption('Yes, I know its a stupid name, but I couldnt think of anything better')
print('', )
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
- Feel free to use whole words as variable names!
- If you specify all the variables manually, it will just return the fuction for you,
it won't try to solve for anything. So you can ignore `= 0` part.
- As usual, if something goes wrong, just restart the page, it'll probably fix it.
- If you see an warning saying "The widget with key "..." was created with a default value but also had its value set via the Session State API.",
just ignore it. It's not a problem, and I haven't figured out how to get rid of it yet.
- If you use `=` or `==`, it will automatically put the right side in the f(...) = box
""", unsafe_allow_html=True)

st.divider()

"""
Credits:

Copeland Carter

https://github.com/smartycope/Mathtopia

See my other streamlit project at [ezregex.org](http://ezregex.org)!
"""
