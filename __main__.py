import streamlit as st
from sympy import *
from Cope import ensure_not_iterable
from Cope.sympy import *
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
    # get_vars_from_vars = st.checkbox('Get variables from set variables', key='get_vars_from_vars')
    st.session_state['get_vars_from_vars'] = False
    interpret_as_latex = st.checkbox('Interpret input as LaTeX', key='interpret_as_latex')
    impl_mul = st.checkbox('Implicit Multiplication', key='impl_mul', value=True)
    remove_fx = st.checkbox('Auto-Remove `f(x) =`', key='remove_fx', value=True)
    do_solve = st.checkbox('Solve', key='do_solve', value=True)
    do_simplify = st.checkbox('Simplify Solution', key='do_simplify', value=True)
    num_eval = st.checkbox('Give a non-symbolic answer', key='num_eval')
    if num_eval:
        do_round = st.number_input('Round to:', format='%d', value=3, key='do_round')
    else:
        st.session_state['do_round'] = 10
    do_code = st.checkbox('Include Custom Code Box', key='do_code', value=True)

    with st.expander('Copy', True):
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
expr = parse(right.text_input('Expression:', '' if (cur := st.session_state.get('_expr')) is None else cur, key='_expr'), interpret_as_latex)

def _solve(expr, eq):
    # If it's a Matrix, don't solve it
    if isinstance(expr, MatrixBase):
        return expr

    sol = solve(Eq(expr, eq))
    if not len(sol):
        sol = [expr]
    if st.session_state.do_simplify:
        expr = simplify(expr)
    new_sol = []
    # Multivariable problems return dicts
    for s in sol:
        if isinstance(s, (Dict, dict)):
            if st.session_state.num_eval:
                try:
                    new_sol.append({key: round(N(val), st.session_state.do_round) for key, val in s.items()})
                except TypeError:
                    new_sol.append({key: N(val) for key, val in s.items()})
            else:
                new_sol.append(s)
        else:
            if st.session_state.num_eval:
                try:
                    new_sol.append(round(N(s), st.session_state.do_round))
                except TypeError:
                    new_sol.append(N(s))
            else:
                new_sol.append(s)
    return sol

def show_sympy(expr):
    if isinstance(expr, (Dict, dict)):
        st.write(ensure_not_iterable(expr.keys()))
        tmp = ensure_not_iterable(expr.values())
        if isinstance(tmp, MatrixBase):
            st.dataframe(matrix2numpy(expr), hide_index=True, column_config={str(cnt): st.column_config.TextColumn(default='0', label='') for cnt in range(len(expr))})
        else:
            st.write(tmp)
    else:
        if isinstance(expr, MatrixBase):
            st.dataframe(matrix2numpy(expr), hide_index=True, column_config={str(cnt): st.column_config.TextColumn(default='0', label='') for cnt in range(len(expr))})
        else:
            st.write(expr)

# Do all the things
if expr is not None:
    vars = get_atoms(expr)

    # Show expr
    show_sympy(expr)

    # Top captions
    left, right = st.columns((.65, .35))
    left.caption(f"Parsed as: `{expr}`")
    if len(vars) == 1:
        right.caption(f'Catagories: `{tuple(categorize(expr, list(vars)[0]))}`')

    # Set the updated vars in the f(x) display at the top
    _left.markdown(f'# f({", ".join(map(str, vars))})=')

    st.divider()

    # The f(inputs) box
    if len(vars):
        'Solve for:'
        a, *b, c, d = st.columns([.05] + ([.7/len(vars)]*len(vars)) + [.05, .2])
        a.markdown('# f(')
        for s, v in zip(b, vars):
            s.text_input(str(v), f'Symbol("{v}")', key=f'{v}_set_to')
        c.markdown('# ) =')
        eq = parse(d.text_input(' ', '0', label_visibility='hidden', key='eq'))

    if isinstance(expr, MatrixBase):
        "Row Reduction:"
        rref, pivots = expr.rref()
        show_sympy(rref)
        f"Pivot columns: `{pivots}`"

    expr = expr.subs({v: parse(st.session_state[f'{v}_set_to']) for v in vars})

    # Save the parsed sympy expression, just in case we need it elsewhere
    st.session_state['expr'] = expr
    st.session_state['vars'] = vars

    copy_expression.code(str(expr))
    copy_expression_latex.code(latex(expr))
    copy_expression_repr.code(srepr(expr))

    # Display the solutions
    if do_solve and len(vars):
        with st.expander('Solutions', True):
            solution = _solve(expr, eq)
            st.session_state['solution'] = solution
            for i in solution:
                show_sympy(i)
                # Don't add the extra divider at the bottom
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

                Don't forget to hit ctrl+enter to submit the code to be run
            ''')

else:
    _left.markdown('# f()=')


# P(1 +r/n)^{nt}  compound intrest equation
