import streamlit as st
from sympy import *
from streamlit_extras.grid import grid
from streamlit_extras.switch_page_button import switch_page
from src.parse import parse
from src.helper import show_sympy

# Save the main UI state so we can come back to it
st.session_state['_expr'] = st.session_state.get('_expr')
st.session_state['eq'] = st.session_state.get('eq')
st.session_state['vars_dict'] = st.session_state.get('vars_dict')

if 'num_eval' not in st.session_state:
    st.session_state['num_eval'] = False

st.set_page_config(layout='centered')

_grid = grid([1, 4], [1, 1, 4], [1, 1, 4], vertical_align="center")

_grid.image('assets/partial_derivative.png', width=100)
_grid.empty()

_grid.image('assets/divided_by.png', width=200)
_grid.empty()
func = _grid.text_input('Func:', st.session_state.get('_expr'))

_grid.image('assets/partial_derivative.png', width=100)
var = _grid.text_input('Var:', list(st.session_state.vars_dict.keys())[0] if len(st.session_state.vars_dict.keys()) == 1 else '')

if (func is not None and len(func) and var is not None and len(var)):
    st.divider()
    'Copy this into the main equation:'
    left, right = st.columns([.8, .2])
    result = f'Derivative({func}, {var})'
    left.code(result)
    show_sympy(parse(result))
    if right.button('Overwrite Main Expression'):
        st.session_state['set_expr'] = result
        switch_page('main ')
