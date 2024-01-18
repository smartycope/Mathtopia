import streamlit as st
import matplotlib.pyplot as plt
from sympy import *
from Cope import ensure_not_iterable
import decimal
from decimal import Decimal as D
from src.parse import get_atoms
from src.SS import ss
# ss = st.session_state.ss

# if 'num_eval' not in ss:
#     ss['num_eval'] = False
# if 'vars_dict' not in ss:
#     ss['vars_dict'] = {}

def _solve(expr, eq):
    # If it's a Matrix, don't solve it, main will handle it
    if isinstance(expr, MatrixBase):
        return expr

    # Solve for *all* the variables, not just a random one
    sol = []
    for var in (get_atoms(expr) + get_atoms(eq)):
        sol += solve(Eq(expr, eq), var, dict=True, simplify=ss.do_simplify)

    # If we've passed parameters, there's nothing to solve, just return expr verbatim
    if not len(sol):
        # Make a Symbol that looks like a function call, for when we display it in the solutions box
        fake_func_call = f'{ss.func_name}({",".join(map(str, ss.vars_dict.values()))})'
        sol = [{Symbol(fake_func_call): expr}]

        ss.check_changed()
        if ss.disable_eq is False or ss.vars_dict_changed:#ss.eq != str(expr):
            ss.disable_eq = str(expr)
            # We have to rerun once here (and in the else statement below) so the UI will immediately
            # reflect the change we've made here
            # In addition, we only want to rerun if we've made a change, otherwise we get stuck in an
            # infinite loop
            st.rerun()
    else:
        # is not False here, it gets set to a string when true
        if ss.disable_eq is not False:
            ss.disable_eq = False
            st.rerun()

    if ss.do_it:
        simplified = [i.doit() for i in sol if hasattr(i, 'doit')]
        # Don't simplify it if it doesn't give anything.
        # This happens when solving for multiple variables symbolically
        # We want to let the dic stuff below handle that.
        if len(simplified):
            sol = simplified

    if ss.do_simplify:
        expr = simplify(expr)

    new_sol = []
    # Multivariable problems return dicts
    # I had all this in ONE LINE if I didn't need a try except statement there
    for s in sol:
        if isinstance(s, (Dict, dict)):
            if ss.num_eval:
                try:
                    new_sol.append({key: round(N(val), ss.do_round) for key, val in s.items()})
                except TypeError as err:
                    new_sol.append({key: N(val) for key, val in s.items()})
            else:
                new_sol.append(s)
        else:
            if ss.num_eval:
                try:
                    new_sol.append(round(N(s), ss.do_round))
                except TypeError as err:
                    new_sol.append(N(s))
            else:
                new_sol.append(s)

    if ss.filter_imag:
        real = list(filter(lambda i: I not in (i.atoms() if not isinstance(i, (Dict, dict)) else list(i.values())[0].atoms()), sol))
        # Only filter out the imaginary solutions if there are real solutions
        if len(real):
            # If we filtered any out, notify the user
            if len(sol) != len(real):
                st.toast('Imaginary Solutions Hidden')
            sol = real
        elif len(sol) != len(real):
            st.toast('Only imaginary solutions available')

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
    else:
        if isinstance(expr, MatrixBase):
            to.dataframe(matrix2numpy(expr), hide_index=True, column_config={str(cnt): to.column_config.TextColumn(default='0', label='') for cnt in range(len(expr))})
        else:
            if ss.num_eval:
                try:
                    to.write(round(expr, ss.do_round))
                except:
                    to.write(expr)
            else:
                to.write(expr)

def reset_ui():
    """ Reset all the vars and the equal box, because we have a new expression provided """
    if ss['do_ui_reset']:
        ss['vars_dict'] = {}
        ss['eq'] = '0'
        ss['disable_eq'] = False

def split_matrix(mat):
    bulk = mat[:mat.cols-1, :mat.cols-1]
    end = mat[:mat.cols-1, mat.cols-1]
    return bulk, end
