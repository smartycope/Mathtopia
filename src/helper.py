import streamlit as st
from sympy import *

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

def split_matrix(mat):
    bulk = mat[:mat.cols-1, :mat.cols-1]
    end = mat[:mat.cols-1, mat.cols-1]
    return bulk, end
