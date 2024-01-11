import streamlit as st
from sympy import *
from streamlit_extras.grid import grid
from streamlit_extras.switch_page_button import switch_page
from src.parse import parse
from src.helper import show_sympy

# For parse. Not technically necissary, unless they bookmark the Add_Matrix page
if 'impl_mul' not in st.session_state:
    st.session_state['impl_mul'] = True
if 'remove_fx' not in st.session_state:
    st.session_state['remove_fx'] = False

st.set_page_config(layout='wide')
st.session_state['_expr'] = st.session_state.get('_expr')

_grid = grid([1, 2], [1, 1], [1, .35, 1, 4], vertical_align="center")

end = _grid.text_input('End')
_grid.empty()
_grid.image('assets/sum_image.png', width=200)

expr = _grid.text_input('Expression', st.session_state.get('_expr'))
# left, mid, right = st.columns([.45, .1, .45])
var = _grid.text_input('Variable', st.session_state.vars[0] if len(st.session_state.vars) == 1 else '')
_grid.markdown('# =')
start = _grid.text_input('Start')

if len(var) and len(end) and len(start) and len(expr):
    st.divider()
    'Copy this into the main equation:'
    left, right = st.columns([.8, .2])
    result = f'Sum({expr}, ({var}, {start}, {end}))'
    left.code(result)
    show_sympy(parse(result))
    if right.button('Overwrite Main Expression'):
        st.session_state['set_expr'] = result
        switch_page('main ')
