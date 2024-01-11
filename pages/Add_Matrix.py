import streamlit as st
from sympy import *
from streamlit_extras.switch_page_button import switch_page
from src.parse import parse

st.set_page_config(layout='centered')

# For parse. Not technically necissary, unless they bookmark the Add_Matrix page
if 'impl_mul' not in st.session_state:
    st.session_state['impl_mul'] = True
if 'remove_fx' not in st.session_state:
    st.session_state['remove_fx'] = False

left, right = st.columns(2)
cols = right.number_input('Columns', value=3, min_value=1)
rows = left.number_input('Rows', value=3, min_value=1)

data = st.data_editor(
    [['0'] * cols] * rows,
    hide_index=True,
    use_container_width=False,
    column_config={str(cnt): st.column_config.TextColumn(default='0', label='') for cnt in range(cols)},
)

parsed = []
for cnt, col in enumerate(data):
    parsed.append([])
    for row in col:
        parsed[cnt].append(parse(row) if row is not None else S(0))

st.divider()
'Copy this into the main equation:'
left, right = st.columns([.8, .2])
result = f'Matrix(['
x = len(data)
y = len(data[0])
for _x in range(x):
    result += f"[{', '.join(map(lambda i: str(parse(i) if i is not None else 0), data[_x]))}],"
# Remove the trailing comma
result = result[:-1]
result += '])'
left.code(result)
if right.button('Overwrite Main Expression'):
    st.session_state['_expr'] = result
    switch_page('main ')

# st.dataframe(matrix2numpy(parse(result)), hide_index=False)