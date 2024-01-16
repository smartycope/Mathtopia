import streamlit as st

# Save the main UI state so we can come back to it
st.session_state['_expr'] = st.session_state.get('_expr')
st.session_state['eq'] = st.session_state.get('eq')
st.session_state['vars_dict'] = st.session_state.get('vars_dict')

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
