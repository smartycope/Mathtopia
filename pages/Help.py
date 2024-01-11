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
- In code, the expression provided is an expression, not a function. Cause all expressions
are just headless functions. So feel free to add equal signs in there.
    - `=` signs are converted to `-` signs in the expression, because of how sympy works
    (when solving, expressions are assumed to equal 0, so `8x - 4 = 0` == `8x = 4`)
    - `==` signs (and other operators) are parsed as Eq() classes
        - When you use `==` signs though, be the deselect 'Auto-Remove f(x)` option
- There may be multiple solutions, they're all displayed.
- If it says 'Evaluated Directly' in the solutions area, that means we didn't solve
the function symbolically, instead we put in all the variable substitutions you specified
and it came out with a value.
    - It determines whether it should evaluate directly based on other criteria though,
    so you might see it other times as well.








Credits:
Copeland Carter

https://github.com/smartycope/Mathtopia

See my other streamlit project at [ezregex.org](http://ezregex.org)!
""", unsafe_allow_html=True)
