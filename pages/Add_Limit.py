import streamlit as st
from sympy import *
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(layout='centered')
st.session_state['_expr'] = st.session_state.get('_expr')

_, left, right = st.columns([.4, .1, .5])
left.markdown('# lim')
expr = right.text_input('expr', st.session_state.get('_expr'))

left, mid, right = st.columns((.45, .1, .45))
var = left.text_input('Var', st.session_state.vars[0] if len(st.session_state.vars) == 1 else '')
mid.markdown('# ->')
to = right.text_input('To')

dir = st.radio('Direction', ['# -', '# +'])

if len(expr) and len(to) and len(var):
    left, right = st.columns([.8, .2])
    result = f'Limit({expr}, {var}, {to}, "{dir[2]}")'
    left.code(result)
    if right.button('Overwrite Main Expression'):
        st.session_state['_expr'] = result
        switch_page('main ')
