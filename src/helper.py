import streamlit as st
import matplotlib.pyplot as plt
from sympy import *
from Cope import ensure_not_iterable

def _solve(expr, eq):
    # Reset this
    st.session_state['disabled'] = None

    # If it's a Matrix, don't solve it, main will handle it
    if isinstance(expr, MatrixBase):
        return expr

    sol = solve(Eq(expr, eq), dict=True)
    # If we've passed parameters, there's nothing to solve, just return expr verbatim
    if not len(sol):
        fake_func_call = f'{st.session_state.func_name}({",".join(map(str, st.session_state.vars_dict.values()))})'
        sol = [{Symbol(fake_func_call): expr}]

    # print(sol)

    if st.session_state.do_it:
        simplified = [i.doit() for i in sol if hasattr(i, 'doit')]
        # Don't simplify it if it doesn't give anything.
        # This happens when solving for multiple variables symbolically
        # We want to let the dic stuff below handle that.
        if len(simplified):
            sol = simplified

    if st.session_state.do_simplify:
        expr = simplify(expr)

    new_sol = []
    # Multivariable problems return dicts
    # I had all this in ONE LINE if I didn't need a try except statement there
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

    if st.session_state.filter_imag:
        real = list(filter(lambda i: I not in (i.atoms() if not isinstance(i, (Dict, dict)) else list(i.values())[0].atoms()), sol))
        # Only filter out the imaginary solutions if there are real solutions
        if len(real):
            # If we filtered any out, notify the user
            if len(sol) != len(real):
                st.toast('Imaginary Solutions Hidden')
            sol = real
    return sol

def show_sympy(expr):
    if isinstance(expr, (Dict, dict)):
        # print('here')
        left, mid, right = st.columns((.2, .05, .65))
        left.write(ensure_not_iterable(expr.keys()))
        mid.write('#### =')
        tmp = ensure_not_iterable(expr.values())
        if isinstance(tmp, MatrixBase):
            right.dataframe(matrix2numpy(expr), hide_index=True, column_config={str(cnt): st.column_config.TextColumn(default='0', label='') for cnt in range(len(expr))})
        else:
            right.write(tmp)
    else:
        if isinstance(expr, MatrixBase):
            st.dataframe(matrix2numpy(expr), hide_index=True, column_config={str(cnt): st.column_config.TextColumn(default='0', label='') for cnt in range(len(expr))})
        else:
            st.write(expr)

def split_matrix(mat):
    bulk = mat[:mat.cols-1, :mat.cols-1]
    end = mat[:mat.cols-1, mat.cols-1]
    return bulk, end
