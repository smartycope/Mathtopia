import streamlit as st
from sympy import *


end = st.text_input('End')
st.image('assets/sum_image.png')

left, mid, right = st.columns([.45, .1, .45])
var = left.text_input('Variable')
mid.markdown('# =')
start = right.text_input('Start')

if not len(var):
    st.toast('Variable not specified')
elif not len(end):
    st.toast('End not specified')
elif not len(start):
    st.toast('Start not specified')
else:
    st.divider()
    'Copy this into the main equation:'
    st.code(f'Sum({var}, ({var}, {start}, {end}))')
        # st.toast('Copied!')
