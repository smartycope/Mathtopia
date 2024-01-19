import streamlit as st
import matplotlib.pyplot as plt
from sympy import *
from Cope import ensure_not_iterable
from code_editor import code_editor
from sympy.matrices.common import ShapeError
from sympy.plotting import plot, plot3d
from src.SS import ss
from itertools import repeat

# Anything here will get preserved between pages, and is ensured to exist properly
# Defaults are specified here, not in their own boxes
# Set this up before the local imports, so they're setup by time they get called
ss.setup(
    # Used for the code box
    prev_id=-1,
    code={'text': '', 'id': -1},
    # An iterable of solutions
    solutions=[],
    vars={},
    # The raw inputs. The parsed Expr input is exprs or ss[f'_expr{i}']
    _exprs=[''],
    # The raw inputs. The parse Expr input is ss[f'eq{i}']
    _eqs=[0],
    set_expr={},
    func_intros={0: 'f()'},
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
    plot_num=0,
    do_code=False,
    do_check_point=False,
    do_ui_reset=False,
    use_area_box=False,
    left_interval='oo',
    right_interval='oo',
    num_funcs=1,
    left_open=False,
    right_open=False,
)

# This handles a very odd error that only comes up every other run
try:
    from src.parse import parse, get_atoms, detect_equals
    from src.code import run_code
    from src.helper import *
    from src.helper import _solve
except KeyError:
    print('Weird error, rerunning')
    st.rerun()

# TODO: print(ss.just_loaded)
func_name = 'f'
_default_value = S(0)
ss.note_page(__file__)
ss.func_names = func_names = ('f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'o', 'p')
st.set_page_config(layout='wide')

# ─── Sidebar configs ───────────────────────────────────────────────────────────
with st.sidebar:
    interval_container = st.container()
    # Set the sidebar interval UI elements
    interval_container.write('Interval')
    left, d = interval_container.columns(2)
    left_open = left.checkbox('Left Open', key='left_open')
    right_open = d.checkbox('Right Open', key='right_open')
    left, d = interval_container.columns(2)
    left_interval = parse(left.text_input(f'var {"<" if left_open else "≤"}', value=ss.left_interval, key='left_interval'))
    right_interval = parse(d.text_input(f'var {">" if right_open else "≥"}', value=ss.right_interval, key='right_interval'))
    interval = Interval(left_interval, right_interval, left_open=left_open, right_open=right_open)

    num_funcs = st.number_input('Number of Functions', 1, len(func_names), key='num_funcs')
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
    if do_plot:
        plot_num = func_names.index(st.selectbox('Which function to plot', func_names[:num_funcs], index=0,  key='plot_num'))
    do_code = st.checkbox('Include Custom Code Box',             value=ss.do_code,            key='do_code',     help='Adds a code area where we can run Python & sympy code directly on the expression')
    do_check_point = st.empty()
    if st.button('Reset Variables', key='reset_vars', help='Reset all variables back to their Symbols'):
        for v in ss.vars.keys():
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

# ─── The expr boxes ────────────────────────────────────────────────────────────
exprs = []
vars = []
for i in range(num_funcs):
    _ex = ''

    # If we have something, like from another page, add that
    if len(ss._exprs) > i:
        _ex = ss._exprs[i]

    # If we have a previous box value, set it to the current box value
    _ex = ss[f'_expr{i}'] or _ex

    # High priority: if it exists, immediately put it in the box
    if i in ss.set_expr:
        _ex = ss.set_expr[i]
        del ss.set_expr[i]

    # Put the value we just determined into the box
    ss[f'_expr{i}'] = _ex

    # Creating the actual box
    box_type = st.text_area if use_area_box else st.text_input
    intro = ss.func_intros.get(i) or f'{func_names[i]}()'
    raw = box_type(intro, key=f'_expr{i}', on_change=reset_ui)

    # If there's an equals sign in it, stick the right side in the eq box
    raw, equals = detect_equals(raw, i)
    if equals is not None:
        ss[f'eq{i}'] = equals
        ss.set_expr[i] = raw
        print('Detected =, rerunning...')
        st.rerun()

    # Now parse whatever we got, and stick it in exprs so we can do stuff with it later
    expr = parse(raw, interpret_as_latex)
    exprs.append(expr)

    # Preserve it across pages
    if len(ss._exprs) > i:
        ss._exprs.append(ss[f'_expr{i}'])
    else:
        ss._exprs[i] = ss[f'_expr{i}']

    # Now get the variables from it
    v = set(get_atoms(expr))
    vars.append(v)

    # Now add captions to each one
    caption(expr, v, interval)


# ─── Do all the things ─────────────────────────────────────────────────────────
# Show all the expressions
map(show_sympy, exprs)

# ─── Set the updated vars in the f(x) display at the top ───────────────────────
for i in range(num_funcs):
    intro = f'# {func_names[i]}({",".join(map(str, vars[i]))})='
    if i not in ss.func_intros or intro != ss.func_intros[i]:
        ss.func_intros[i] = intro
        st.rerun()

if len(ss['_expr0']):
    st.divider()

# ─── The f(inputs) box ─────────────────────────────────────────────────────────
for i in range(num_funcs):
    v = vars[i]
    if len(v):
        'Solve for:'
        a, *b, c, d = st.columns([.08] + ([.7/len(v)]*len(v)) + [.15, .2])
        a.markdown(f'## {func_names[i]}(')
        ss.check_changed()
        # First, all the variable boxes
        for s, v in zip(b, v):
            if (len(ss.vars) > i and v in ss.vars[i] and
                (
                    ss.vars_changed or
                    ss.page_changed or
                    ss.just_loaded
                )
            ):
                value = str(ss.vars[i][v])
                # If it's emtpy, refill it to the default var name
                if value == 'None' or not len(value):
                    value = str(v)
                ss[f'{v}_set_to'] = value

            # If the the box is empty, be sure to fill it
            if len(ss.vars) > i and  ss.vars[i].get(v) in (None, 'None', ''):
                print('setting with default value')
                value = str(v)
                ss[f'{v}_set_to'] = value

            # This is only created a few lines below. It just resets the variable if there's nothing
            # in the variable box
            # The i is so it if there's the same variable in multiple boxes, streamlit still needs unique keys
            if ss[f'_{v}{i}_set_to'] is not None:
                ss[f'{v}{i}_set_to'] = ss[f'_{v}{i}_set_to']
                del ss[f'_{v}{i}_set_to']

            if not len(s.text_input(str(v), key=f'{v}{i}_set_to', args=(v,))):
                value = str(v)
                ss[f'_{v}{i}_set_to'] = value
                st.rerun()

        c.markdown('## ) =')
        # The '=' Box
        _eq = None
        if len(ss._eqs) > i:
            _eq = ss._eqs[i]
        ss[f'eq{i}'] = ss[f'disable_eq{i}'] or ss[f'eq{i}'] or _eq or '0'
        parse(d.text_input(' ', key=f'eq{i}', disabled=bool(ss[f'disable_eq{i}']), label_visibility='hidden'))
        if len(ss._eqs) > i:
            ss._eqs[i] = ss[f'eq{i}']
        else:
            ss._eqs.append(ss[f'eq{i}'])
        # copy_full_expression.code(func_intro[2:] + str(eq))

# ─── Matrix stuff ──────────────────────────────────────────────────────────────
if num_funcs == 1 and isinstance(exprs[0], MatrixBase):
    # This is only relevant if we have a matrix
    do_check_point = do_check_point.checkbox('Check if a point is within the space of the matrix', key='do_check_point')

    # RREF
    "Row Reduction:"
    rref, pivots = exprs[0].rref()
    show_sympy(rref)
    f"Pivot columns: `{pivots}`"

    if do_check_point:
        # Check if Point is in Space
        "Check if Point is in Space:"
        cols = st.columns(exprs[0].cols-1)
        for col, i in zip(cols, range(exprs[0].cols-1)):
            col.text_input(f'col {i}', key=f'{i}_row')
        m = 'Matrix(['
        for i in range(exprs[0].cols-1):
            m += '[' + ss[f'{i}_row'] + '], '
        m += '])'
        space, matches = split_matrix(exprs[0])
        try:
            space @ parse(m) == matches
        except ShapeError as err:
            st.error(err)

vars_dicts = [{v: v if (new := ss[f'{v}_set_to']) in (None, 'None', '') else parse(new) for v in var_list} for var_list in vars]
exprs = [(exprs[i].subs(vars_dicts[i]) if exprs[i] is not None else _default_value) for i in range(num_funcs)]

# Save the parsed sympy expression, just in case we need it elsewhere
ss.exprs = exprs
ss.vars = vars_dicts

# Update the copy boxes
copy_expression.code(str(exprs[0]))
copy_expression_latex.code(latex(exprs[0]))
copy_expression_repr.code(srepr(exprs[0]))

if len(ss['_expr0']):
    st.divider()

# ─── Display the solutions ─────────────────────────────────────────────────────
for i in range(num_funcs):
    if do_solve and len(vars[i]):
        with st.expander(f'Solutions for {func_names[i]}', i == 0):
            solution = _solve(exprs[i], i)
            if len(ss.solutions) <= i:
                ss.solutions.append(solution)
            else:
                ss.solutions[i] = solution
            for k in solution:
                show_sympy(k)
                # Don't add the extra divider at the bottom
                if k != solution[-1]:
                    st.divider()

# ─── Update the Copy Boxes ─────────────────────────────────────────────────────
if num_funcs == 1 and do_solve and len(vars[0]):
    copy_solution.code(str(ensure_not_iterable(ss.solutions[0])))
    copy_solution_latex.code(latex(ensure_not_iterable(ss.solutions[0])))
    copy_solution_repr.code(srepr(ensure_not_iterable(ss.solutions[0])))

# ─── The graph ─────────────────────────────────────────────────────────────────
if do_plot:
    var = list(vars[plot_num])[0]
    expr = exprs[plot_num]
    # So it *will* plot it if we've specified some of the variables
    match len(list(filter(lambda i: isinstance(i, Symbol), vars_dicts[plot_num].values()))):
        case 0:
            st.toast(':warning: Can\'t plot 0 variables')
        case 1:
            x = critical_points(expr, var)
            y = [expr.subs({var: i}) for i in x]
            st.write("Critical Points:")
            st.write(dict(zip(map(str, x), y)))
            plot(expr)
            plt.scatter(x, y)
            st.pyplot(plt)
        case 2:
            plot3d(expr)
            st.pyplot(plt)
        case _:
            st.toast(':warning: Can\'t plot more than 2 variables')

# ─── Code box ──────────────────────────────────────────────────────────────────
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

ss.reset_changed()
