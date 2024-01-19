import streamlit as st
import matplotlib.pyplot as plt
from sympy import *
from Cope import ensure_not_iterable
from Cope.sympy import *
from code_editor import code_editor
from sympy.matrices.common import ShapeError
from sympy.plotting import plot, plot3d
from src.SS import ss
from itertools import repeat

# Anything here will get preserved between pages, and is ensured to exist properly
# Defaults are specified here, not in their own boxes
# Set this up before the local imports, so they're setup by time they get called
func_name = 'f'
ss.setup('_expr',
    # Used for the code box
    prev_id=-1,
    code={'text': '', 'id': -1},
    # An iterable of solutions
    solution=None,
    vars_dict={},
    # The raw input. The parsed Expr input is expr
    _expr='',
    eq=0,
    # func_name='f',
    interpret_as_latex=False,
    impl_mul=True,
    do_template=False,
    do_solve=True,
    do_simplify=True,
    # Don't handle this here, so it changes with do_simplify
    # do_it=True if ss.do_simplify is None else ss.do_simplify,
    num_eval=False,
    do_round=3,
    filter_imag=True,
    do_plot=False,
    do_code=False,
    do_check_point=False,
    do_ui_reset=False,
    use_area_box=False,
    left_interval='oo',
    right_interval='oo',
    left_open=False,
    right_open=False,
)
ss.note_page(__file__)

# print(ss.just_loaded)

# This handles a very odd error that only comes up every other run
try:
    from src.parse import parse, get_atoms
    from src.code import run_code
    from src.helper import *
    from src.helper import _solve
except KeyError:
    print('Weird error, rerunning')
    st.rerun()

st.set_page_config(layout='wide')

# ─── Sidebar configs ────────────────────────────────────────────────────────────
with st.sidebar:
    # Don't do this anymore. We now handle equal signs by putting them in the = box
    # remove_fx = st.checkbox('Auto-Remove `f(x) =`',              key='remove_fx',   value=True)
    # func_name = st.text_input('Function Name',                   key='func_name')
    interval_container = st.container()
    impl_mul = st.checkbox('Implicit Multiplication',            value=ss.impl_mul,           key='impl_mul',    help='Allows you to do things like `3x` and `3(x+1) without throwing errors')
    interpret_as_latex = st.checkbox('Interpret input as LaTeX', value=ss.interpret_as_latex, key='interpret_as_latex', help='The expression box will automatically detect LaTeX code for you. Click this to manually tell it that it is LaTeX, in case the detection doesnt work')
    do_template = st.checkbox('Include a Template Function',     value=ss.do_template,        key='do_template', help='Includes a Template function on which the base function gets called on')
    do_solve = st.checkbox('Solve',                              value=ss.do_solve,           key='do_solve',    help='Whether to solve the equation or not. Helpful if you want to look at things that take a long time to solve, like some integrals.')
    if do_solve:
        do_simplify = st.checkbox('Simplify Solutions',          value=ss.do_simplify,        key='do_simplify', help='This reduces the equation down to its most simple form')
        do_it = st.checkbox('Evaluate Solutions',                value=ss.do_it,              key='do_it',       help='This is distinct from simplifying the expression. Simplifying will reduce down to, say, an integral, as opposed to actually evaluating (symbolically) the integral.')
        num_eval = st.checkbox('Give Non-Symbolic Solutions',    value=ss.num_eval,           key='num_eval',    help='Evaluate the function numerically instead of symbolically')
        _do_round = st.empty()
        filter_imag = st.checkbox('Only Inlcude Real Solutions', value=ss.filter_imag,        key='filter_imag', help='Whether we should include answers with `i` in them or not')
    do_plot = st.checkbox('Plot the function',                   value=ss.do_plot,            key='do_plot',     help='Only 1 and 2 unknowns can be plotted')
    do_code = st.checkbox('Include Custom Code Box',             value=ss.do_code,            key='do_code',     help='Adds a code area where we can run Python & sympy code directly on the expression')
    do_check_point = st.empty()
    if st.button('Reset Variables', key='reset_vars', help='Reset all variables back to their Symbols'):
        for v in ss.vars_dict.keys():
            ss[f'{v}_set_to'] = str(v)
    if do_solve and num_eval:
        do_round = _do_round.number_input('Round to:', format='%d', value=3, key='do_round')
    else:
        ss.do_round = 3

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
        do_ui_reset = st.checkbox('Reset UI when a new expression is given', value=ss.do_ui_reset,  key='do_ui_reset',  help='Reset the variables provided and the equals expression provided whenever the function is changed')
        use_area_box = st.checkbox('Use Text Area Instead of Single Line',   value=ss.use_area_box, key='use_area_box', help='Instead of using a single line to specify the function, use a larger text box. Will wrap lines instead of scrolling them.')

# This shouldn't be necissary. I have no idea why it is. And it's STILL inconsistent
# This is for toasting units of constants we've replaced
if (bread := ss.to_toast) is not None and len(bread):
    for _ in range(len(bread)):
        st.toast(bread.pop())

# ─── The function Names ─────────────────────────────────────────────────────────
if do_template:
    # Template
    temp_name_top_line = st.empty()
    temp_name_same_line, temp_right = st.columns([.2, .95])
    temp_name_same_line.empty()

# Expr
func_name_top_line = st.empty()
func_name_same_line, func_right = st.columns([.2, .95])
func_name_same_line.empty()

if do_template:
    temp_box_type = temp_right.text_area if use_area_box else temp_right.text_input
    # The template box
    temp = parse(temp_box_type(' ', label_visibility='hidden', key='_temp', on_change=reset_ui), interpret_as_latex)

# ─── The expr box ───────────────────────────────────────────────────────────────
_ex = ss.set_expr or ss._expr or ''
# This is necissary so pages fill the main box properly for some reason
ss._expr = _ex
if 'set_expr' in ss:
    del ss.set_expr
func_box_type = func_right.text_area if use_area_box else func_right.text_input
expr = parse(func_box_type(' ', label_visibility='hidden', key='_expr', on_change=reset_ui), interpret_as_latex)


# Do all the things
if expr is not None:
    vars = get_atoms(expr)
    if do_template:
        # Remove the func_name from the in-expression vars
        temp_vars = set(get_atoms(temp)) - set(vars) - set((Symbol(func_name),))

    # Show expr & template
    if do_template:
        # func_type = type(func_name, (Function,), {})
        # class _F(Function):
        #     @classmethod
        #     def eval(cls, *args):

        # show_sympy(temp.subs(Symbol(func_name)=_F))
        show_sympy(temp)
        # So it's in the middle
        # st.write(Symbol('->'))
    show_sympy(expr)

    # ─── Top captions ────────────────────────────────────────────────────────────
    # left, mid, right = st.columns((.65, .35))
    left, mid1, mid, right = st.columns(4)
    left.caption(f"Parsed as: `{expr}`")
    if len(vars) == 1:
        right.caption(f'Catagories: `{tuple(categorize(expr, list(vars)[0]))}`')

    # ─── Interval box ────────────────────────────────────────────────────────────
    if len(vars) == 1:
        interval_container.write('Interval')
        left, right = interval_container.columns(2)
        left_open = left.checkbox('Left Open', key='left_open')
        right_open = right.checkbox('Right Open', key='right_open')
        left, right = interval_container.columns(2)
        left_interval = parse(left.text_input(f'{vars[0]} {"<" if left_open else "≤"}', value=ss.left_interval, key='left_interval'))
        right_interval = parse(right.text_input(f'{vars[0]} {">" if right_open else "≥"}', value=ss.right_interval, key='right_interval'))
        mid.caption('In Interval: `' + str(get_interval_desc(expr, vars[0], Interval(left_interval, right_interval, left_open=left_open, right_open=right_open))) + '`')

    # ─── Min max ──────────────────────────────────────────────────────────────────
        min, max = min_max(expr, vars[0])
        mid1.caption(f'Min: {min}, Max: {max}')

    # ─── Set the updated vars in the F(X) display at the top ──────────────────────
    func_intro = f'# {func_name}({",".join(map(str, vars))})='
    if len(func_intro) > 10:
        func_name_top_line.markdown(func_intro)
    else:
        func_name_same_line.markdown(func_intro)

    # ─── Set the update vars in the T(x) display at the top ────────────────────────
    if do_template and temp is not None:
        # Add the func_name as the first custom var
        # temp_intro = f'# T({",".join(map(str, [func_name] + vars))};{",".join(map(str, temp_vars))})='
        # Or not
        temp_intro = f'# T({",".join(map(str, vars))};{",".join(map(str, temp_vars))})='
        if len(temp_intro) > 10:
            temp_name_top_line.markdown(temp_intro)
        else:
            temp_name_same_line.markdown(temp_intro)
    elif do_template:
        temp_name_same_line.markdown(f'# T({",".join(map(str, vars))};)')

    st.divider()

    # ─── The f(inputs) box ──────────────────────────────────────────────────────────
    eq = 0
    if len(vars):
        'Solve for:'
        a, *b, c, d = st.columns([.05] + ([.7/len(vars)]*len(vars)) + [.15, .2])
        a.markdown(f'## {func_name}(')
        ss.check_changed()
        # First, all the variable boxes
        for s, v in zip(b, vars):
            if (v in ss.vars_dict and
                (
                    ss.vars_dict_changed or
                    ss.page_changed or
                    ss.just_loaded
                )
            ):
                value = str(ss.vars_dict[v])
                # If it's emtpy, refill it to the default var name
                if value == 'None' or not len(value):
                    value = str(v)
                ss[f'{v}_set_to'] = value

            # If the the box is empty, be sure to fill it
            if ss.vars_dict.get(v) in (None, 'None', ''):
                print('setting with default value')
                value = str(v)
                ss[f'{v}_set_to'] = value

            # This is only created a few lines below. It just resets the variable if there's nothing
            # in the variable box
            if ss[f'_{v}_set_to'] is not None:
                ss[f'{v}_set_to'] = ss[f'_{v}_set_to']
                del ss[f'_{v}_set_to']

            if not len(s.text_input(str(v), key=f'{v}_set_to', args=(v,))):
                value = str(v)
                ss[f'_{v}_set_to'] = value
                st.rerun()

        c.markdown('## ) =')
        # The '=' Box
        ss.eq = ss.disable_eq or ss.eq or '0'
        eq = parse(d.text_input(' ', key='eq', disabled=bool(ss.disable_eq), label_visibility='hidden'))

        copy_full_expression.code(func_intro[2:] + str(eq))

    # ─── Matrix stuff ───────────────────────────────────────────────────────────────
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
                m += '[' + ss[f'{i}_row'] + '], '
            m += '])'
            space, matches = split_matrix(expr)
            try:
                space @ parse(m) == matches
            except ShapeError as err:
                st.error(err)

    vars_dict = {v: v if (new := ss[f'{v}_set_to']) in (None, 'None', '') else parse(new) for v in vars}
    expr = expr.subs(vars_dict)

    # Save the parsed sympy expression, just in case we need it elsewhere
    ss.expr = expr
    ss.vars_dict = vars_dict

    # Update the copy boxes
    copy_expression.code(str(expr))
    copy_expression_latex.code(latex(expr))
    copy_expression_repr.code(srepr(expr))

    # ─── Display the solutions ───────────────────────────────────────────────────
    if do_solve and len(vars):
        with st.expander('Solutions', True):
            solution = _solve(expr, eq or S(0))
            ss.solution = solution
            for i in solution:
                show_sympy(i)
                # Don't add the extra divider at the bottom
                if i != solution[-1]:
                    st.divider()
        copy_solution.code(str(ensure_not_iterable(solution)))
        copy_solution_latex.code(latex(ensure_not_iterable(solution)))
        copy_solution_repr.code(srepr(ensure_not_iterable(solution)))

    # ─── The graph ───────────────────────────────────────────────────────────────
    if do_plot:
        # So it *will* plot it if we've specified some of the variables
        match len(list(filter(lambda i: isinstance(i, Symbol), vars_dict.values()))):
            case 0:
                st.toast(':warning: Can\'t plot 0 variables')
            case 1:
                x = critical_points(expr, vars[0])
                y = [expr.subs({vars[0]: i}) for i in x]
                st.write("Critical Points:")
                st.write(dict(zip(x, y)))
                plot(expr)
                plt.scatter(x, y)
                st.pyplot(plt)
            case 2:
                plot3d(expr)
                st.pyplot(plt)
            case _:
                st.toast(':warning: Can\'t plot more than 2 variables')

    # ─── Code box ───────────────────────────────────────────────────────────────
    if do_code:
        left, right = st.columns(2)
        with left:
            code_tab, output_tab, errors_tab, help_tab = st.tabs(('Code', 'Output', 'Errors', 'Help'))
            with code_tab:
                resp = code_editor(ss.code['text'], lang='python', key='code')
                code = resp['text']
                id = resp['id']
                if id != ss.prev_id:
                    rtn = right.container(border=True)
                    run_code(code, rtn, output_tab, errors_tab)

            help_tab.markdown('''
                ##### In the code box, you can run sympy expressions directly on the current expression
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
    if do_template:
        temp_name_same_line.markdown('# T()=')

ss.reset_changed()
