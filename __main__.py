import streamlit as st
from sympy import *
from Cope import ensure_not_iterable
from Cope.sympy import *
from clipboard import copy
from code_editor import code_editor
# This handles a very odd error that only comes up every other run
try:
    from src.parse import parse, get_atoms
    from src.code import run_code
except KeyError:
    print('Weird error, rerunning')
    st.rerun()

st.set_page_config(layout='wide')

if 'prev_id' not in st.session_state:
    st.session_state['prev_id'] = -1
if 'solution' not in st.session_state:
    st.session_state['solution'] = None
# If we DO have it, and it's none, make it '', as well as if we don't have it
if st.session_state.get('_expr') is None:
    st.session_state['_expr'] = ''
if 'vars' not in st.session_state:
    st.session_state['vars'] = []

# Sidebar configs
with st.sidebar:
    remove_fx = st.checkbox('Auto-Remove `f(x) =`', key='remove_fx')
    transformation = st.checkbox('Transform', key='transformation')
    get_vars_from_vars = st.checkbox('Get variables from set variables', key='get_vars_from_vars')
    do_solve = st.checkbox('Solve for the Selected Variable', key='do_solve', value=True)
    do_categorize = st.checkbox('Catagorize the Expression', key='do_categorize', value=True)
    do_code = st.checkbox('Include Custom Code Box', key='do_code', value=True)
    do_simplify = st.checkbox('Simplify Solution', key='do_simplifiy', value=True)

    with st.expander('Copy'):
        left, right = st.columns(2)
        left.write('# Expression')
        copy_expression = right.empty()
        left, right = st.columns(2)
        left.write('LaTeX')
        copy_expression_latex = right.empty()
        left, right = st.columns(2)
        left.write('Expanded Code')
        copy_expression_repr = right.empty()
        left, right = st.columns(2)
        left.write('# Solution')
        copy_solution = right.empty()
        left, right = st.columns(2)
        left.write('LaTeX')
        copy_solution_latex = right.empty()
        left, right = st.columns(2)
        left.write('Expanded Code')
        copy_solution_repr = right.empty()

_left, right = st.columns([.2, .95])
_left.empty()
expr = parse(right.text_input('Expression:', '' if (cur := st.session_state.get('_expr')) is None else cur, key='_expr'))

def _solve(expr, var):
    if st.session_state.do_simplifiy:
        expr = simplify(expr)
    return solve(expr, var)


# Do all the things
if expr is not None:
    f"Parsed as: `{expr}`"

    # The Selected Variable
    left, right = st.columns([.3, .7])
    vars = get_atoms(expr)
    var = left.selectbox('Solve for:', vars, key='selected_var')

    # The f(x) variable setter
    a, *b, c = st.columns([.05] + ([.9/len(vars)]*len(vars)) + [.05])
    a.markdown('# f(')
    for s, v in zip(b, vars):
        s.text_input(str(v), f'Symbol("{v}")', key=f'{v}_set_to')
    c.markdown('# )')

    # Set the updated vars in the f(x) display at the top
    # if st.session_state.vars != vars:
    _left.markdown(f'# f({", ".join(map(str, vars))})=')

    expr = expr.subs({v: parse(st.session_state[f'{v}_set_to']) for v in vars})

    # Save the parsed sympy expression, just in case we need it elsewhere
    st.session_state['expr'] = expr
    st.session_state['vars'] = vars

    copy_expression.code(str(expr))
    copy_expression_latex.code(latex(expr))
    copy_expression_repr.code(srepr(expr))


    # Display the catagories
    if do_categorize and len(vars) == 1:
        f'Catagories: `{tuple(categorize(expr, list(vars)[0]))}`'

    # Display the solutions
    if do_solve:# or copy_solution or copy_solution_latex or copy_expression_repr:
        with st.expander('Solutions', True):
            solution = solve(expr, var)
            st.session_state['solution'] = solution
            if not len(solution):
                st.caption('Evaluated Directly')
                st.write(expr)
            else:
                for i in solution:
                    st.write(i)
                    if i != solution[-1]:
                        st.divider()
        copy_solution.code(str(ensure_not_iterable(solution)))
        copy_solution_latex.code(latex(ensure_not_iterable(solution)))
        copy_solution_repr.code(srepr(ensure_not_iterable(solution)))

    # Code box
    if do_code:
        left, right = st.columns(2)
        with left:
            code_tab, output_tab, errors_tab, help_tab = st.tabs(('Code', 'Output', 'Errors', 'Help'))
            with code_tab:
                resp = code_editor('' if (cur := st.session_state.get('code')) is None else cur['text'], lang='python', key='code')
                code = resp['text']
                id = resp['id']
                if id != st.session_state.prev_id:
                    rtn = right.container(border=True)
                    run_code(code, rtn, output_tab, errors_tab)

            help_tab.markdown('''
                ### In the code box, you can run sympy expressions directly on the current expression
                The code box accepts valid Python, and has the following variables in scope:
                - `expr`: The current expression. Is of type `Expr`
                - `solution`: The current solutions. Is a list
                - Everything in the default sympy scope, and sympy.abc
                - Everything in the pages/funcs.py

                print() statements should go to the Output tab, but they don't work yet.

                Errors get handled and put in the Errors tab.

                The last line in the box gets shown to the right (no need to print or set to a variable)
            ''')

else:
    _left.markdown('# f()=')
