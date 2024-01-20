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
    solutions={},
    vars={0: {}},
    exprs={},
    # The raw inputs. The parsed Expr input is exprs or ss[f'_expr{i}']
    # _exprs={0: ''},
    # The raw inputs. The parse Expr input is ss[f'eq{i}']
    # _eqs={0: 0},
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


# An explanation of variables:
# Raw values. These are also keys to their respective widgets
# ss[f'_expr{i}']
#   The raw values in the expression boxes
# ss[f'_eq{i}']
#   The raw values in the = ____ boxes
# ss[f'{var}{i}_set_to']
#   The raw values of the variables

# Read only parsed containers
# ss.vars
#   A list of dicts of the variables in each expression. Goes {parsed_var: parsed_value}.
#   Is indexed in the same order the functions are in
#   ss.vars is READ ONLY. Any changes will be overwritten.
#   To write to the boxes, use ss[f'{var}{i}_set_to']
# ss.exprs
#   A dict of the form {index: parsed_and_subbed_expr}. Is READ ONLY like ss.vars
#   To write to the expressions, use ss[f'_expr{i}']
# ss.solutions
#   A dict of the form {index: solution}
#   Also READ ONLY

# Overwriting variables
# ss.set_expr
#   A dict of the form {index: raw_expr} that takes priority over the value in ss[f'_expr{i}']
#   Self-destructs when read
#// ss.set_eq
#//   A dict of the form {index: raw_expr} that takes priority over the value in ss[f'_eq{i}']
#//   Self-destructs when read

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
        tmp = st.selectbox('Which function to plot', func_names[:num_funcs], index=0,  key='plot_num')
        # Streamlit has a weird return for selectboxes
        if tmp == 0:
            plot_num = 0
        else:
            plot_num = func_names.index(tmp)
    do_code = st.checkbox('Include Custom Code Box',             value=ss.do_code,            key='do_code',     help='Adds a code area where we can run Python & sympy code directly on the expression')
    do_check_point = st.empty()

    if st.button('Reset Variables', key='reset_vars', help='Reset all variables back to their Symbols'):
        for i in ss.vars.keys():
            for v in i.keys():
                ss[f'{v}{i}_set_to'] = str(v)

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
# Dict of parsed expressions that don't have the variable values subsituted yet
unsubbed_exprs = {}
# Dict of {index: set(Symbols)} of varibles in each expression
var_variables = {}
for i in range(num_funcs):
    # If we have a previous box value, set it to the current box value
    _ex = ss[f'_expr{i}'] or ''

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
    unsubbed_exprs[i] = expr

    # Preserve it across pages
    ss.watch(f'_expr{i}', '')

    # Now get the variables from it
    v = set(get_atoms(expr))
    var_variables[i] = v

    # Now add captions to each one
    caption(expr, v, interval)

    # Show the expression
    show_sympy(expr)

# ─── Set the updated vars in the f(x) names in the function boxes ──────────────
for i in range(num_funcs):
    intro = f'# {func_names[i]}({",".join(map(str, var_variables[i]))})='
    if i not in ss.func_intros or intro != ss.func_intros[i]:
        ss.func_intros[i] = intro
        st.rerun()

if len(ss._expr0): st.divider()

# ─── The f(inputs) box ─────────────────────────────────────────────────────────
for i in range(num_funcs):
    ss.vars[i] = {}
    if len(var_variables[i]):
        'Solve for:'
        col_alignments = [.08] + ([.7/len(var_variables[i])]*len(var_variables[i])) + [.15, .2]
        func_col, *var_cols, label_col, eq_col = st.columns(col_alignments)

        # The f( part
        func_col.markdown(f'## {func_names[i]}(')

        # Second, all the variable boxes
        # Loop through all the variables in this function, and their associated columns
        for col, var in zip(var_cols, var_variables[i]):
            # By default, it's whatever it was before
            value = ss[f'{var}{i}_set_to']

            # If the the box is empty, be sure to fill it with a default value instead
            if value in (None, 'None', ''):
                value = str(var)

            # This loads the variable box with the variable we just determined
            ss[f'{var}{i}_set_to'] = value

            # The actual variable box
            set_to = col.text_input(str(var), key=f'{var}{i}_set_to')
            if not len(set_to):
                # If it's empty, then rerun. The above if-statement will catch it and fix it.
                st.rerun()

            # Parse it and immediately stick it in ss.vars
            ss.vars[i][var] = parse(set_to)

            # So it's preserved across pages
            ss.watch(f'{var}{i}_set_to', '')

        label_col.markdown('## ) =')

        # The '=' Box
        print(ss[f'disable_eq{i}'])
        ss[f'_eq{i}'] = ss[f'disable_eq{i}'] or ss[f'_eq{i}'] or '0'
        parse(eq_col.text_input(' ', key=f'_eq{i}', disabled=bool(ss[f'disable_eq{i}']), label_visibility='hidden'))
        # So it's preserved across pages
        ss.watch(f'_eq{i}', '')

# ─── Matrix stuff ──────────────────────────────────────────────────────────────
if num_funcs == 1 and isinstance(unsubbed_exprs[0], MatrixBase):
    # This is only relevant if we have a matrix
    do_check_point = do_check_point.checkbox('Check if a point is within the space of the matrix', key='do_check_point')

    # RREF
    "Row Reduction:"
    rref, pivots = unsubbed_exprs[0].rref()
    show_sympy(rref)
    f"Pivot columns: `{pivots}`"

    if do_check_point:
        # Check if Point is in Space
        "Check if Point is in Space:"
        cols = st.columns(unsubbed_exprs[0].cols-1)
        for col, i in zip(cols, range(unsubbed_exprs[0].cols-1)):
            col.text_input(f'col {i}', key=f'{i}_row')
        m = 'Matrix(['
        for i in range(unsubbed_exprs[0].cols-1):
            m += '[' + ss[f'{i}_row'] + '], '
        m += '])'
        space, matches = split_matrix(unsubbed_exprs[0])
        try:
            space @ parse(m) == matches
        except ShapeError as err:
            st.error(err)

# Update the session_state expressions
ss.exprs = {
    i: (expr.subs(ss.vars[i]) if expr is not None else _default_value)
    for i, expr in unsubbed_exprs.items()
}

# Update the copy boxes
copy_expression.code(str(ss.exprs[0]))
copy_expression_latex.code(latex(ss.exprs[0]))
copy_expression_repr.code(srepr(ss.exprs[0]))

if len(ss._expr0): st.divider()

# ─── Display the solutions ─────────────────────────────────────────────────────
for i in range(num_funcs):
    if do_solve and len(ss.vars[i]):
        with st.expander(f'Solutions for {func_names[i]}', i == 0):
            solution = _solve(ss.exprs[i], i)
            ss.solutions[i] = solution
            # if len(ss.solutions) <= i:
            #     ss.solutions.append(solution)
            # else:
            #     ss.solutions[i] = solution
            for k in solution:
                show_sympy(k)
                # Don't add the extra divider at the bottom
                if k != solution[-1]:
                    st.divider()

# ─── Update the Copy Boxes ─────────────────────────────────────────────────────
if num_funcs == 1 and do_solve and len(ss.vars[0]):
    copy_solution.code(str(ensure_not_iterable(ss.solutions[0])))
    copy_solution_latex.code(latex(ensure_not_iterable(ss.solutions[0])))
    copy_solution_repr.code(srepr(ensure_not_iterable(ss.solutions[0])))

# ─── The graph ─────────────────────────────────────────────────────────────────
if do_plot:
    if not len(ss.vars[plot_num]):
        st.toast(':warning: Can\'t plot 0 variables')
    else:
        var = list(ss.vars[plot_num])[0]
        expr = ss.exprs[plot_num]
        # So it *will* plot it if we've specified some of the variables
        match len(list(filter(lambda i: isinstance(i, Symbol), ss.vars[plot_num].values()))):
            case 0:
                st.toast(':warning: Can\'t plot 0 variables')
            case 1:
                x = critical_points(expr, var)
                y = [expr.subs({var: i}) for i in x]
                st.write("Critical Points:")
                st.write(dict(zip(map(str, x), y)))
                print(expr)
                try:
                    plot(expr)
                except:
                    st.warning(f"Can't plot function {func_names[plot_num]}")
                else:
                    plt.scatter(x, y)
                    st.pyplot(plt)
            case 2:
                try:
                    plot3d(expr)
                except:
                    st.warning(f"Can't plot function {func_names[plot_num]}")
                else:
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
