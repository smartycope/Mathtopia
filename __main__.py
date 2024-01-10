import streamlit as st
from sympy import *
from src.parse import parse, get_atoms
from src.code import run_code
from Cope import ensure_not_iterable
from Cope.sympy import *
from clipboard import copy
from code_editor import code_editor
# st.set_page_config(initial_sidebar_state='expanded')

if 'prev_id' not in st.session_state:
    st.session_state['prev_id'] = -1
if 'solution' not in st.session_state:
    st.session_state['solution'] = None
# If we DO have it, and it's none, make it '', as well as if we don't have it
if st.session_state.get('_expr') is None:
    st.session_state['_expr'] = ''

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

expr = parse(st.text_input('Expression:', '' if (cur := st.session_state.get('_expr')) is None else cur, key='_expr'))
# Save the parsed sympy expression, just in case we need it elsewhere
st.session_state['expr'] = expr

# Do all the things
if expr is not None:
    f"Parsed as: `{expr}`"

    vars = get_atoms(expr)
    var = st.selectbox('Selected Variable:', vars, key='selected_var')

    # Display the catagories
    if do_categorize and len(vars) == 1:
        f'Catagories: `{tuple(categorize(expr, list(vars)[0]))}`'

    # Display the solutions
    if do_solve:
        with st.expander('Solutions', True):
            solution = solve(expr, var)
            st.session_state['solution'] = solution
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

    left, right = st.columns(2)
    with left:
        code_tab, output_tab, errors_tab = st.tabs(('Code', 'Output', 'Errors'))
        with code_tab:
            resp = code_editor('' if (cur := st.session_state.get('code')) is None else cur['text'], lang='python', key='code')
            code = resp['text']
            id = resp['id']
            if id != st.session_state.prev_id:
                rtn = right.container(border=True)
                run_code(code, rtn, output_tab, errors_tab)
