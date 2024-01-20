import streamlit as st
from sympy import *
from streamlit_extras.switch_page_button import switch_page
from src.parse import parse
from src.helper import show_sympy
from src.SS import ss

st.set_page_config(layout='centered')
ss.update(__file__)

_, left, right = st.columns([.4, .1, .5])
left.markdown('# lim')
expr = right.text_input('Expression', ss[f'_expr0'])

left, mid, right = st.columns((.45, .1, .45))
var = left.text_input('Var', list(ss.vars[0].keys())[0] if len(ss.vars[0].keys()) == 1 else '')
mid.markdown('# ->')
to = right.text_input('To')

dir = st.radio('Direction', ['# -', '# +'])

if len(expr) and len(to) and len(var):
    left, right = st.columns([.8, .2])
    result = f'Limit({expr}, {var}, {to}, "{dir[2]}")'
    left.code(result)
    show_sympy(parse(result))
    if right.button('Overwrite Main Expression'):
        ss.set_expr[0] = result
        switch_page('main ')
