import streamlit as st
from sympy import *
from streamlit_extras.grid import grid
from streamlit_extras.switch_page_button import switch_page
import re
from src.parse import parse
from src.helper import show_sympy
from Cope.streamlit import ss
import matplotlib.pyplot as plt
from Cope import debug
import numpy as np

# TODO: This is resetting and it's preventing proper editing

st.set_page_config(layout='wide')
ss.update(__file__)

add_line = st.checkbox('Draw a line between them', True)

left, right = st.columns(2)
cols = 2

def add_row():
    if len(ss.data) > ss.rows:
        ss.data.pop()
    elif len(ss.data) < ss.rows:
        ss.data.append([ss.rows, 0])

rows = left.number_input('Rows', value=3, min_value=1, on_change=add_row, key='rows')

names = ('x', 'f(x)')

ss.watch('data', [[1, 0], [2, 0], [3, 0]])

ss.data = left.data_editor(
    ss.data,
    hide_index=True,
    use_container_width=False,
    column_config={str(cnt): st.column_config.NumberColumn(default='0', label=names[cnt]) for cnt in range(cols)},
    key='_data'
)

data = np.array(ss.data).T
plt.scatter(data[0], data[1])
if add_line:
    plt.plot(data[0], data[1])
right.pyplot(plt)
