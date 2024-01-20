import streamlit as st
from Cope.streamlit import ss

ss.update(__file__)

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
