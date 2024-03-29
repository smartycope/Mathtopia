import streamlit as st
from sympy import *
from streamlit_extras.grid import grid
from streamlit_extras.switch_page_button import switch_page
from src.parse import parse
from src.helper import show_sympy
from Cope.streamlit import ss

st.set_page_config(layout='centered')
ss.update(__file__)

_grid = grid([1, 1, 2], [4, 1, 1], [1, 1, 2], vertical_align="bottom")

_grid.empty()
to = _grid.text_input('To:')
_grid.empty()
_grid.image('assets/integral.png', width=200)
func = _grid.text_input('Func:', ss[f'_expr0'])
var = _grid.text_input('Var:', list(ss.vars[0].keys())[0] if len(ss.vars[0].keys()) == 1 else '')
_grid.empty()
from_ = _grid.text_input('From:')

order = st.columns(2)[0].number_input('Order', 1, value=1, step=1)

if (bool(len(to)) ^ bool(len(from_))) and (func is not None and len(func) and var is not None and len(var)):
    st.warning('Please specify `to` and `from` or neither (don\'t just specify one)')
elif (func is not None and len(func) and var is not None and len(var)):
    st.divider()
    label = st.empty()
    left, right = st.columns([.8, .2])
    result = f'Integral({func}, '
    if len(to):
        label.write("Definite Integral:")
        new = f'({var}, {from_}, {to})'
    else:
        label.write("Indefinite Integral:")
        new = str(var)

    if order != 1:
        result += ', '.join([str(new)]*order)
    else:
        result += new
    result += ')'

    left.code(result)
    show_sympy(parse(result))

    if right.button('Overwrite Main Expression'):
        ss.set_expr[0] = result
        switch_page('main ')
