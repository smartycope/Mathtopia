import streamlit as st
from Cope.streamlit import ss
from Cope.sympy import categorize
from pages.Custom_Functions import min_max, get_interval_desc

if len(ss.exprs) > 1:
    st.info('This info only applies to function `f`')
expr = ss.exprs[0]

if len(ss.vars) == 1:
    var = list(ss.vars)[0]
    # Categories
    try:
        "Categories:"
        tuple(categorize(expr, var))
    except Exception as err:
        st.exception(err)

    try:
        'Interval Properties:'
        get_interval_desc(expr, var, ss.interval)
    except Exception as err:
        st.exception(err)

    # Min max
    try:
        min, max = min_max(expr, var)
        'Min:'
        min
        'Max:'
        max
    except Exception as err:
        st.exception(err)
