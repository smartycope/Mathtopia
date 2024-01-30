import streamlit as st
import matplotlib.pyplot as plt
from sympy import *
from Cope import ensure_not_iterable, confidence
import decimal
from Cope.sympy import *
from decimal import Decimal as D
from src.parse import get_atoms, parse
from Cope.streamlit import ss
from pages.Custom_Functions import min_max, get_interval_desc
from Cope import debug, flatten
from sympy.plotting.plot import Plot
import matplotlib.pyplot as plt


def _solve(expr, i):
    eq = parse(ss[f'_eq{i}']) or S(0)

    # If it's a Matrix, don't solve it, main will handle it
    if isinstance(expr, MatrixBase):
        return expr

    # If there aren't any variables in any of the variable values, we've specified all of them.
    solvable = bool(len(get_atoms(sum(flatten(ss.vars[i].values())))))
    if any(map(lambda v: isinstance(v, (tuple, Tuple)), ss.vars[i].values())):
        solvable = False
    sol = []
    if solvable:
        # Solve for *all* the variables, not just a random one
        for var in (get_atoms(expr) | get_atoms(eq)):
            try:
                sol += solve(Eq(expr, eq), var, dict=True, simplify=ss.do_simplify)
            except NotImplementedError as err:
                st.error(err)

        # Nevermind, we tried, and it actually isn't solvable
        solvable = bool(len(sol))

    dont_change_eq = False
    # If there's no vars to solve for, or if we've tried and failed to solve it, then the solution
    # is the expression, just simply and evaluate it.
    if not solvable:
        # If we're given a list of values, main will substitute them for us.
        # Here, we're taking those substitutions, and displaying them as solutions
        if isinstance(list(ss.vars[i].values())[0], (tuple, Tuple)):
            dont_change_eq = True
            for key, vals in ss.vars[i].items():
                for cnt, val in enumerate(vals):
                    fake_func_call = f'f({val})'
                    sol += [{Symbol(fake_func_call): expr[cnt]}]
        else:
            # Make a Symbol that looks like a function call, for when we display it in the solutions box
            fake_func_call = f'f({",".join(map(str, ss.vars[i].values()))})'
            sol += [{Symbol(fake_func_call): expr}]

        ss.check_changed()
        if (
            # If we failed to get a solution, don't disable the eq box
            not bool(len(get_atoms(sum(flatten(ss.vars[i].values()))))) and
            ((ss[f'disable_eq{i}'] is False or sol != ss.solutions[i]))
            # Don't set the eq box if we're display multiple solutions for multiple inputs.
            # It makes it break when you change the function and it tries to reparse what left in the
            # eq box
        ):
            ss[f'disable_eq{i}'] = '' if dont_change_eq else str(expr)
            ss.solutions[i] = sol
            # We have to rerun once here (and in the else statement below) so the UI will immediately
            # reflect the change we've made here
            # In addition, we only want to rerun if we've made a change, otherwise we get stuck in an
            # infinite loop
            st.rerun()
    else:
        # is not False here: it gets set to a string when true
        if ss[f'disable_eq{i}'] is not False:
            ss[f'disable_eq{i}'] = False
            st.rerun()

    if not len(sol):
        st.toast(f':warning: No solutions exist for function {ss.func_names[i]}')

    new_sol = []
    for s in sol:
        new_d = {}
        for k, v in s.items():
            if ss.do_it:
                v = v.doit()
            if ss.do_simplify:
                v = simplify(v)
            if ss.num_eval:
                try:
                    v = round(N(v), ss.do_round)
                except TypeError:
                    v = N(v)

            new_d[k] = v
        new_sol.append(new_d)
    sol = new_sol


    # if ss.do_it:
    #     done = [{k: v.doit() for k, v in j.items()} for j in sol]
    #     # Don't simplify it if it doesn't give anything.
    #     # This happens when solving for multiple variables symbolically
    #     # We want to let the dic stuff below handle that.
    #     if len(done):
    #         sol = done

    # # Simplify again, after doing it
    # if ss.do_simplify:
    #     sol = [{k: simplify(v) for k, v in j.items()} for j in sol]

    # if ss.num_eval:
    #     sol = [{k: round(N(v), ss.do_round) for k, v in j.items()} for j in sol]

    # new_sol = []
    # I had all this in ONE LINE if I didn't need a try except statement there
    # for s in sol:
    #     if isinstance(s, (Dict, dict)):
    #         if ss.num_eval:
    #             try:
    #                 new_sol.append({key: round(N(val), ss.do_round) for key, val in s.items()})
    #             except TypeError as err:
    #                 new_sol.append({key: N(val) for key, val in s.items()})
    #         else:
    #             new_sol.append(s)
    #     else:
    #         if ss.num_eval:
    #             try:
    #                 new_sol.append(round(N(s), ss.do_round))
    #             except TypeError as err:
    #                 new_sol.append(N(s))
    #         else:
    #             new_sol.append(s)

    if ss.filter_imag:
        real = list(filter(lambda k: I not in (k.atoms() if not isinstance(k, (Dict, dict)) else list(k.values())[0].atoms()), sol))
        # Only filter out the imaginary solutions if there are real solutions
        if len(real):
            # If we filtered any out, notify the user
            if len(sol) != len(real):
                st.toast(f'Imaginary Solutions Hidden for {ss.func_names[i]}')
            sol = real
        elif len(sol) != len(real):
            st.toast(f'Only imaginary solutions available for {ss.func_names[i]}')

    return sol

def show_sympy(expr, to=st):
    if isinstance(expr, (Dict, dict)):
        left, mid, right = to.columns((.2, .05, .65))
        left.write(ensure_not_iterable(expr.keys()))
        mid.write('#### =')
        tmp = ensure_not_iterable(expr.values())
        if isinstance(tmp, MatrixBase):
            right.dataframe(matrix2numpy(expr), hide_index=True, column_config={str(cnt): to.column_config.TextColumn(default='0', label='') for cnt in range(len(expr))})
        else:
            if ss.num_eval:
                try:
                    right.write(round(tmp, ss.do_round))
                except:
                    right.write(tmp)
            else:
                right.write(tmp)
    elif isinstance(expr, MatrixBase):
        to.latex(latex(expr))
    elif isinstance(expr, Plot):
        to.pyplot(plt)
    else:
        if ss.num_eval:
            try:
                to.write(round(expr, ss.do_round))
            except:
                to.write(expr)
        else:
            to.write(expr)

def caption(expr, vars, interval):
    if expr is None: return
    # "Parsed as"
    a, b, c, d = st.columns(4)
    a.caption(f"Parsed as: `{expr}`")

    if len(vars) == 1:
        var = list(vars)[0]
        # Categories
        try:
            d.caption(f'Catagories: `{tuple(categorize(expr, var))}`')
        except: pass

        try:
            c.caption('Interval Properties: `' + str(get_interval_desc(expr, var, interval)) + '`')
        except: pass

        # Min max
        try:
            min, max = min_max(expr, var)
            b.caption(f'Min: {min}, Max: {max}')
        except: pass

def reset_ui():
    """ Reset all the vars and the equal box, because we have a new expression provided """
    if ss['do_ui_reset']:
        ss['vars'] = {}
        ss['eq'] = '0'
        ss['disable_eq'] = False

def only_value(d):
    return list(d.values())[0]

def only_key(d):
    return list(d.keys())[0]
