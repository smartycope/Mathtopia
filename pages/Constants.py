import streamlit as st
from src.SS import ss

ss.maintain_state()

constants = {
    'speed_of_light': {
        'value': '299_792_458',
        'unit': 'meters/second',
    },
    'reduced_plank_constant': {
        'value': '1.054571817 * (10**-34)',
        'unit': 'Joules/second',
    },
}

constants
