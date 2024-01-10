import streamlit as st
from sympy import *
from streamlit_extras.grid import grid

_grid = grid([1, 1, 2], [4, 1, 1], [1, 1, 2], vertical_align="bottom")


st.session_state['_expr'] = st.session_state.get('_expr')
st.session_state['selected_var'] = st.session_state.get('selected_var')

# left, mid, right = st.columns(3)
_grid.empty()
to = _grid.text_input('To:')
_grid.empty()
_grid.image('assets/integral.png', width=200)
func = _grid.text_input('Func:', st.session_state.get('_expr'))
var = _grid.text_input('Var:', st.session_state.get('selected_var'))
_grid.empty()
from_ = _grid.text_input('From:')
# _expr is the raw input from the main page

if (bool(len(to)) ^ bool(len(from_))) and (func is not None and len(func) and var is not None and len(var)):
    st.warning('Please specify `to` and `from` or neither (don\'t just specify one)')
elif (func is not None and len(func) and var is not None and len(var)):
    if len(to):
        "Definite Integral:"
        st.code(f'Integral({func}, ({var}, {from_}, {to}))')
    else:
        "Indefinite Integral:"
        st.code(f'Integral({func}, {var})')
