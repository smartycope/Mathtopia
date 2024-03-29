import streamlit as st
from sympy import *
from streamlit_extras.switch_page_button import switch_page
from src.parse import parse
from Cope.streamlit import ss

st.set_page_config(layout='centered')
ss.update(__file__)

# left, right = st.columns(2)
cols = st.number_input('Columns', value=3, min_value=1)
# rows = left.number_input('Rows', value=3, min_value=1)

left, right = st.columns(2)
data = left.data_editor(
    # ([['0'] * cols] * rows) if (d := ss.get('data')) is None else d,
    [['0'] * cols] * 3,
    hide_index=True,
    use_container_width=False,
    column_config={str(cnt): st.column_config.TextColumn(default='0', label='') for cnt in range(cols)},
    num_rows='dynamic',
)
input_right = right.empty()

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

input_right.latex(latex(parse(result)))

if right.button('Overwrite Main Expression'):
    ss.set_expr[0] = result
    switch_page('main ')

# st.dataframe(matrix2numpy(parse(result)), hide_index=False)
