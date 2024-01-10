import streamlit as st
from sympy import *
from streamlit_extras.grid import grid
from streamlit_extras.switch_page_button import switch_page

_grid = grid([1, 1, 3], [1, 1, 1], [1, 1, 4], vertical_align="bottom")


st.session_state['_expr'] = st.session_state.get('_expr')
st.session_state['selected_var'] = st.session_state.get('selected_var')

# to = _grid.text_input('To:')
_grid.image('assets/partial_derivative.png', width=100)
func = _grid.text_input('Func:', st.session_state.get('_expr'))
_grid.empty()

_grid.image('assets/divided_by.png', width=200)
# _grid.image('assets/divided_by.png', width=200)
# _grid.divider()
_grid.empty()
# _grid.divider()
_grid.empty()

_grid.image('assets/partial_derivative.png', width=100)
var = _grid.text_input('Var:', st.session_state.get('selected_var'))
# _grid.empty()
# from_ = _grid.text_input('From:')
# _expr is the raw input from the main page


if (func is not None and len(func) and var is not None and len(var)):
    st.divider()
    'Copy this into the main equation:'
    left, right = st.columns([.8, .2])
    result = f'Derivative({func}, {var})'
    left.code(result)
    if right.button('Overwrite Main Expression'):
        st.session_state['_expr'] = result
        switch_page('main ')
