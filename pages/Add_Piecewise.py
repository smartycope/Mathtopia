import streamlit as st
from sympy import *
from streamlit_extras.grid import grid
from streamlit_extras.switch_page_button import switch_page
from ezregex import *
import re
from src.parse import parse
from src.helper import show_sympy

# This is only here so it preserves the current expression, if we go to this page
# then go back without changing anythign
st.session_state['_expr'] = st.session_state.get('_expr')

# For parse. Not technically necissary, unless they bookmark the Add_Matrix page
if 'impl_mul' not in st.session_state:
    st.session_state['impl_mul'] = True
if 'remove_fx' not in st.session_state:
    st.session_state['remove_fx'] = False

if 'states' not in st.session_state:
    st.session_state['states'] = []

st.set_page_config(layout='wide')

op = ow + anyof('<=', '>=', '<', '>', '!=') + ow
interval = group(chunk, name='a') + group(op, name='op1') + group(chunk, name='b') + group(op, name='op2') + group(chunk, name='c')
repl = '(' + rgroup('a') + ' ' + rgroup('op1') + ' ' + rgroup('b') + ') & (' + rgroup('b') + ' ' + rgroup('op2') + ' ' + rgroup('c') + ')'

def _parse_interval(condition):
    return re.sub(interval.str(), repl.str(), condition, count=1)

# 3 lists (expr, for, condition) of length 1 more than we have already
left, right = st.columns([.2, .8])
left.image('assets/piecewise.png', width=450)

l, r = right.columns((.55, .45))
l.markdown('Expression')
r.markdown('Condition')

states = []
for i in range(len(st.session_state.states) + 1):
    l, m, r = right.columns((.45, .1, .45))
    expr = l.text_input(' ', label_visibility='hidden', key=f'{i}_expr')
    m.markdown('# for')
    condition = r.text_input(' ', label_visibility='hidden', key=f'{i}_condition')
    if len(expr) and len(condition):
        states.append((expr, condition))

if len(st.session_state.states) != len(states):
    st.session_state.states = states
    st.rerun()

st.session_state.states = states

if len(states):
    left, right = st.columns([.8, .2])
    result = 'Piecewise('
    for expr, condition in states:
        result += f'({expr}, {_parse_interval(condition)}), '
    # Remove trailing ,
    result = result[:-2]
    result += ')'

    left.code(result)
    show_sympy(parse(result))

    if right.button('Overwrite Main Expression'):
        st.session_state['set_expr'] = result
        switch_page('main ')
