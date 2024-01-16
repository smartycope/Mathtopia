import streamlit as st
from sympy import *
from streamlit_extras.grid import grid
from streamlit_extras.switch_page_button import switch_page
from src.parse import parse
from src.helper import show_sympy

st.set_page_config(layout='centered')

# Save the main UI state so we can come back to it
st.session_state['_expr'] = st.session_state.get('_expr')
st.session_state['eq'] = st.session_state.get('eq')
st.session_state['vars'] = st.session_state.get('vars')

_grid = grid([1, 1, 2], [4, 1, 1], [1, 1, 2], vertical_align="bottom")

_grid.empty()
to = _grid.text_input('To:')
_grid.empty()
_grid.image('assets/integral.png', width=200)
func = _grid.text_input('Func:', st.session_state.get('_expr'))
var = _grid.text_input('Var:', st.session_state.vars[0] if len(st.session_state.vars) == 1 else '')
_grid.empty()
from_ = _grid.text_input('From:')

if (bool(len(to)) ^ bool(len(from_))) and (func is not None and len(func) and var is not None and len(var)):
    st.warning('Please specify `to` and `from` or neither (don\'t just specify one)')
elif (func is not None and len(func) and var is not None and len(var)):
    st.divider()
    label = st.empty()
    left, right = st.columns([.8, .2])
    if len(to):
        label.write("Definite Integral:")
        result = f'Integral({func}, ({var}, {from_}, {to}))'
        left.code(result)
    else:
        label.write("Indefinite Integral:")
        result = f'Integral({func}, {var})'
        left.code(result)

    show_sympy(parse(result))

    if right.button('Overwrite Main Expression'):
        st.session_state['set_expr'] = result
        switch_page('main ')
