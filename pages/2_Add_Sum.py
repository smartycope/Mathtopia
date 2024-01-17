import streamlit as st
from sympy import *
from streamlit_extras.grid import grid
from streamlit_extras.switch_page_button import switch_page
from src.parse import parse
from src.helper import show_sympy
from src.SS import ss

st.set_page_config(layout='wide')
ss.update(__file__)

mode = st.radio('Mode', options=['Sum', 'Product'], horizontal=True)

_grid = grid([1, 2], [1, 1], [1, .35, 1, 4], vertical_align="center")

end = _grid.text_input('End')
_grid.empty()
_grid.image('assets/sum_image.png' if mode == 'Sum' else 'assets/product.png', width=200)

expr = _grid.text_input('Expression', ss._expr or '')
# left, mid, right = st.columns([.45, .1, .45])
var = _grid.text_input('Variable', list(ss.vars_dict.keys())[0] if len(ss.vars_dict.keys()) == 1 else '')
_grid.markdown('# =')
start = _grid.text_input('Start')

if len(var) and len(end) and len(start) and len(expr):
    st.divider()
    'Copy this into the main equation:'
    left, right = st.columns([.8, .2])
    result = f'{mode}({expr}, ({var}, {start}, {end}))'
    left.code(result)
    show_sympy(parse(result))
    if right.button('Overwrite Main Expression'):
        ss['set_expr'] = result
        switch_page('main ')
