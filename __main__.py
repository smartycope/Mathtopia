import streamlit as st
from sympy import *
from src.parse import parse, get_atoms
from Cope import ensure_not_iterable
from Cope.sympy import *
from clipboard import copy
# st.set_page_config(initial_sidebar_state='expanded')

with st.sidebar:
    remove_fx = st.checkbox('Auto-Remove `f(x) =`', key='remove_fx')
    transformation = st.checkbox('Transform', key='transformation')
    get_vars_from_vars = st.checkbox('Get variables from set variables', key='get_vars_from_vars')
    do_solve = st.checkbox('Solve for the Selected Variable', key='do_solve', value=True)
    do_categorize = st.checkbox('Catagorize the Expression', key='do_categorize', value=True)

    with st.expander('Copy'):
        copy_expression = st.button('Expression', key='copy_expression')
        copy_solution = st.button('Solution', key='copy_solution')
        copy_expression_latex = st.button('Expression LaTeX', key='copy_expression_latex')
        copy_solution_latex = st.button('Solution LaTeX', key='copy_solution_latex')
        copy_expression_repr = st.button('Expression Representation', key='copy_expression_repr')
        copy_solution_repr = st.button('Solution Representation', key='copy_solution_repr')

expr = parse(st.text_area('Expression:', key='_expr'))
# Save the parsed sympy expression, just in case we need it elsewhere
st.session_state['expr'] = expr

# Do all the things
if expr is not None:
    f"Parsed as: `{expr}`"

    vars = get_atoms(expr)
    var = st.selectbox('Selected Variable:', vars)

    if do_categorize and len(vars) == 1:
        'Catagories:'
        st.write(categorize(expr, list(vars)[0]))

    if do_solve:
        with st.expander('Solutions', True):
            solution = solve(expr, var)
            for i in solution:
                st.write(i)

    # All the copy buttons
    if copy_expression:
        copy(str(expr))
    if copy_solution:
        if not do_solve:
            solution = solve(expr, var)
        copy(str(ensure_not_iterable(solution)))
    if copy_expression_latex:
        copy(latex(expr))
    if copy_solution_latex:
        if not do_solve:
            solution = solve(expr, var)
        copy(latex(ensure_not_iterable(solution)))
    if copy_expression_repr:
        copy(srepr(expr))
    if copy_solution_repr:
        if not do_solve:
            solution = solve(expr, var)
        copy(srepr(ensure_not_iterable(solution)))
