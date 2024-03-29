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

st.set_page_config(layout='wide')
ss.update(__file__)

add_line = st.checkbox('Draw a line between them', True)

left, right = st.columns(2)
cols = 2

names = ('x', 'f(x)')

data = left.data_editor(
    [[1, 0], [2, 0], [3, 0]],
    hide_index=True,
    use_container_width=False,
    column_config={str(cnt): st.column_config.NumberColumn(default='0', label=names[cnt]) for cnt in range(cols)},
    num_rows='dynamic',
    key='_data'
)

data = np.array(data).T
plt.scatter(data[0], data[1])
if add_line:
    plt.plot(data[0], data[1])
right.pyplot(plt)
