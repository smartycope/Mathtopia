import streamlit as st
from sympy import *
from Cope import ensure_not_iterable
from Cope.sympy import *
from src.helper import *
from src.helper import _solve
from code_editor import code_editor
from sympy.matrices.common import ShapeError
# This handles a very odd error that only comes up every other run
try:
    from src.parse import parse, get_atoms
    from src.code import run_code
except KeyError:
    print('Weird error, rerunning')
    st.rerun()

st.set_page_config(layout='wide')

# Used for the code box
if 'prev_id' not in st.session_state:
    st.session_state['prev_id'] = -1
# An iterable of solutions
if 'solution' not in st.session_state:
    st.session_state['solution'] = None
# If we DO have it, and it's none, make it '', as well as if we don't have it
# The raw expression given
if st.session_state.get('_expr') is None:
    st.session_state['_expr'] = ''
# A list of all the variables we have (not their values)
if 'vars' not in st.session_state:
    st.session_state['vars'] = []
# A Symbol, None, or 'eq' that says what thing we're solving for
if 'disabled' not in st.session_state:
    st.session_state['disabled'] = []

# Sidebar configs
with st.sidebar:
    # Don't do this anymore. We now handle equal signs by putting them in the = box
    # remove_fx = st.checkbox('Auto-Remove `f(x) =`',              key='remove_fx',   value=True)
    func_name = st.text_input('Function Name',                   key='func_name',   value='f')
    interpret_as_latex = st.checkbox('Interpret input as LaTeX', key='interpret_as_latex',       help='The expression box will automatically detect LaTeX code for you. Click this to manually tell it that it is LaTeX, in case the detection doesnt work')
    impl_mul = st.checkbox('Implicit Multiplication',            key='impl_mul',    value=True,  help='Allows you to do things like `3x` and `3(x+1) without throwing errors')
    do_solve = st.checkbox('Solve',                              key='do_solve',    value=True,  help='Whether to solve the equation or not. Helpful if you want to look at things that take a long time to solve, like some integrals.')
    do_simplify = st.checkbox('Simplify Solution',               key='do_simplify', value=True,  help='This reduces the equation down to its most simple form')
    do_it = st.checkbox('Evaluate the Solution',                 key='do_it',       value=do_simplify, help='This is distinct from simplifying the expression. Simplifying will reduce down to, say, an integral, as opposed to actually evaluating (symbolically) the integral.')
    num_eval = st.checkbox('Give a non-symbolic answer',         key='num_eval',    value=False, help='Evaluate the function numerically instead of symbolically')
    filter_imag = st.checkbox('Filter out Imaginary Solutions',  key='filter_imag', value=True,  help='Whether we should include answers with `i` in them or not')
    do_code = st.checkbox('Include Custom Code Box',             key='do_code',     value=False, help='Adds a code area where we can run Python & sympy code directly on the expression')
    do_check_point = st.empty()
    if st.button('Reset Variables', key='reset_vars', help='Reset all variables back to their Symbols'):
        for v in st.session_state.vars:
            st.session_state[f'{v}_set_to'] = f'Symbol("{v}")'
    if num_eval:
        do_round = st.number_input('Round to:', format='%d', value=3, key='do_round')
    else:
        st.session_state['do_round'] = 10

    with st.expander('Copy', False):
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
        left, right = st.columns(2)
        left.write('# Function Call')
        copy_full_expression = right.empty()

    with st.expander('Advanced Options'):
        # get_vars_from_vars = st.checkbox('Get variables from set variables', key='get_vars_from_vars')
        st.session_state['get_vars_from_vars'] = False
        use_area_box = st.checkbox('Use Text Area Instead of Single Line', key='use_area_box', help='Instead of using a single line to specify the function, use a larger text box')

func_name_top_line = st.empty()
func_name_same_line, right = st.columns([.2, .95])
func_name_same_line.empty()

_ex = st.session_state.get('set_expr') or st.session_state.get('_expr') or ''
# WHY is this necissary??
st.session_state['_expr'] = _ex
if 'set_expr' in st.session_state:
    del st.session_state['set_expr']
box_type = right.text_area if use_area_box else right.text_input
expr = parse(box_type(' ', label_visibility='hidden', value=_ex, key='_expr'), interpret_as_latex)

# This shouldn't be necissary. I have no idea why it is. And it's STILL inconsistent
# This is for toasting units of constants we've replaced
if (bread := st.session_state.get('to_toast')) is not None and len(bread):
    for _ in range(len(bread)):
        print('toasting from main')
        st.toast(bread.pop())


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
    func_intro = f'# {func_name}({",".join(map(str, vars))})='
    if len(func_intro) > 10:
        func_name_top_line.markdown(func_intro)
    else:
        func_name_same_line.markdown(func_intro)

    st.divider()

    # The f(inputs) box
    if len(vars):
        'Solve for:'
        a, *b, c, d = st.columns([.05] + ([.7/len(vars)]*len(vars)) + [.15, .2])
        a.markdown(f'## {func_name}(')
        for s, v in zip(b, vars):
            s.text_input(str(v), f'Symbol("{v}")', key=f'{v}_set_to', disabled=st.session_state.disabled == v)
        c.markdown('## ) =')
        # The '=' Box
        eq = parse(d.text_input(' ', '0', label_visibility='hidden', key='eq', disabled=st.session_state.disabled == 'eq'))

        copy_full_expression.code(func_intro[2:] + str(eq))

    # Matrix stuff
    if isinstance(expr, MatrixBase):
        # This is only relevant if we have a matrix
        do_check_point = do_check_point.checkbox('Check if a point is within the space of the matrix', key='do_check_point')

        # RREF
        "Row Reduction:"
        rref, pivots = expr.rref()
        show_sympy(rref)
        f"Pivot columns: `{pivots}`"

        if do_check_point:
            # Check if Point is in Space
            "Check if Point is in Space:"
            cols = st.columns(expr.cols-1)
            for col, i in zip(cols, range(expr.cols-1)):
                col.text_input(f'col {i}', key=f'{i}_row')
            m = 'Matrix(['
            for i in range(expr.cols-1):
                m += '[' + st.session_state[f'{i}_row'] + '], '
            m += '])'
            space, matches = split_matrix(expr)
            try:
                space @ parse(m) == matches
            except ShapeError as err:
                st.error(err)

    vars_dict = {v: parse(st.session_state[f'{v}_set_to']) for v in vars}
    expr = expr.subs(vars_dict)

    # Save the parsed sympy expression, just in case we need it elsewhere
    st.session_state['expr'] = expr
    st.session_state['vars'] = vars
    st.session_state['vars_dict'] = vars_dict

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
                - `expr`:Expr
                    - The current expression
                - `solution`:List[Expr]
                    - The current solutions
                - `equals`:Expr
                    - The expression the function is set to equal
                - `vars`:Dict[Symbol: Expr]
                    - All the variables and what they're set to
                - Everything in the default sympy scope, and sympy.abc
                - Everything in the pages/funcs.py

                print() statements should go to the Output tab, but they don't work yet.

                Errors get handled and put in the Errors tab.

                The last line in the box gets shown to the right (no need to print or set to a variable)

                Don't forget to hit ctrl+enter to submit the code to be run
            ''')

else:
    func_name_same_line.markdown('# f()=')
