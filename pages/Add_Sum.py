import streamlit as st
from sympy import *
from streamlit_extras.switch_page_button import switch_page

end = st.text_input('End')
st.image('assets/sum_image.png')

left, mid, right = st.columns([.45, .1, .45])
var = left.text_input('Variable')
mid.markdown('# =')
start = right.text_input('Start')

# if not len(var):
#     st.toast('Variable not specified')
# elif not len(end):
#     st.toast('End not specified')
# elif not len(start):
#     st.toast('Start not specified')
# else:

if len(var) and len(end) and len(start):
    st.divider()
    'Copy this into the main equation:'
    left, right = st.columns([.8, .2])
    result = f'Sum({var}, ({var}, {start}, {end}))'
    st.code(result)
    if right.button('Overwrite Main Expression'):
        st.session_state['_expr'] = result
        switch_page('main ')
