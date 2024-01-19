import streamlit as st
import matplotlib.pyplot as plt
from sympy import *
from Cope import ensure_not_iterable, confidence
import decimal
from Cope.sympy import *
from decimal import Decimal as D
from src.parse import get_atoms, parse
from src.SS import ss


def _solve(expr, i):
    eq = parse(ss[f'eq{i}']) or S(0)
    # If it's a Matrix, don't solve it, main will handle it
    if isinstance(expr, MatrixBase):
        return expr

    # If we've specified all the variables, don't solve, just return the expression verbatim
    if all(key != val for key, val in ss.vars[i].items()):
        # Make a Symbol that looks like a function call, for when we display it in the solutions box
        fake_func_call = f'f({",".join(map(str, ss.vars[i].values()))})'
        sol = [{Symbol(fake_func_call): expr}]

        ss.check_changed()
        if ss[f'disable_eq{i}'] is False or ss.vars_changed:
            ss[f'disable_eq{i}'] = str(expr)
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

        # Solve for *all* the variables, not just a random one
        sol = []
        for var in (get_atoms(expr) + get_atoms(eq)):
            sol += solve(Eq(expr, eq), var, dict=True, simplify=ss.do_simplify)

    if not len(sol):
        st.toast(f':warning: No solutions exist for function {ss.func_names[i]}')

    if ss.do_it:
        simplified = [k.doit() for k in sol if hasattr(k, 'doit')]
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

def caption(expr, vars, interval):
    if expr is None: return
    # "Parsed as"
    a, b, c, d = st.columns(4)
    a.caption(f"Parsed as: `{expr}`")

    if len(vars) == 1:
        var = list(vars)[0]
        # Categories
        d.caption(f'Catagories: `{tuple(categorize(expr, var))}`')

        c.caption('In Interval: `' + str(get_interval_desc(expr, var, interval)) + '`')

        # Min max
        min, max = min_max(expr, var)
        b.caption(f'Min: {min}, Max: {max}')

def reset_ui():
    """ Reset all the vars and the equal box, because we have a new expression provided """
    if ss['do_ui_reset']:
        ss['vars'] = {}
        ss['eq'] = '0'
        ss['disable_eq'] = False

def split_matrix(mat):
    bulk = mat[:mat.cols-1, :mat.cols-1]
    end = mat[:mat.cols-1, mat.cols-1]
    return bulk, end


def critical_points(expr, var, interval=...) -> tuple:
    diff = expr.diff(var)
    if interval is not Ellipsis:
        return [ans for ans in solve(diff, var) if ans in interval]
    else:
        return solve(diff, var)

# @confidence(90)
# def getCriticalPoints(expr, var, interval=Interval(-oo, oo), order=1) -> 'iterable':
#     return ensureIterable(solveset(Eq(expr.diff(var, order), 0), var, domain=interval).simplify())
    # return solveset(Derivative(expr, (var, order)), var, domain=S.Reals).simplify()


@confidence(80)
def getCriticalIntervals(expr, var, overInterval=Interval(-oo, oo)):
    criticalPoints = getCriticalPoints(expr, var)
    criticalPoints = [overInterval.start] + sorted(list(criticalPoints)) + [overInterval.end]

    intervals = []
    for i in range(len(criticalPoints) - 1):
        intervals.append(Interval(criticalPoints[i], criticalPoints[i+1]))
    return intervals

@confidence(49)
def getCriticalPointsOverInterval(expr, var, interval, order=1):
    #* THIS SHOULD WORK DANG IT
    # return [i for i in ensureIterable(solveset(expr.diff(var, order), var)) if isBetween(i, interval.start, interval.end)]
    # try:
    #     a, b = solveset(Derivative(expr, (var, order)), var, domain=interval)
    # except:
    #     a = solveset(Derivative(expr, (var, order)), var, domain=interval)
    #     b = None
    # ans = []
    # if isBetween(a, interval.start, interval.end):
    #     ans.append(a)
    # if isBetween(b, interval.start, interval.end):
    #     ans.append(b)
    # return ans
    start = expr.subs(var, interval.start)
    end = expr.subs(var, interval.end)
    crit = getCriticalPoints(expr, var)
    evalPoints = []
    solvedEvalPoints = []

    for i in crit:
        i = i.simplify()
        if is_between(i, interval.start, interval.end, True, True):
            evalPoints.append(i)
    # print('Critical Points between the interval:', evalPoints)
    return evalPoints

def min_max(expr, var, interval=...) -> (('minx', 'miny'), ('maxx', 'maxy')):
    crit_points = critical_points(expr, var, interval=...)
    crit_values = [(point, expr.subs(var, point)) for point in crit_points]
    if len(crit_values):
        return min(crit_values, key=lambda i: i[1]), max(crit_values, key=lambda i: i[1])
    else:
        return (tuple(), tuple())

# @confidence('sorta')
def minMaxOverInterval(expr, var, interval) -> (('minx', 'miny'), ('maxx', 'maxy')):
    start = expr.subs(var, interval.start)
    end = expr.subs(var, interval.end)
    crit = getCriticalPoints(expr, var)
    evalPoints = []
    solvedEvalPoints = []

    for i in crit:
        i = i.simplify()
        # if is_between(i, interval.start, interval.end, True, True):
        if i in interval:
            evalPoints.append(i)

    #* This for loop does work and i have NO idea why
    # for k in evalPoints:
        # print('running:', k)
        # solvedEvalPoints.append(expr.subs(var, k))
    solvedEvalPoints.append(expr.subs(var, evalPoints[0]))
    solvedEvalPoints.append(expr.subs(var, evalPoints[1]))

    solvedEvalPoints += [start, end]
    for i in crit:
        try:
            solvedEvalPoints.remove(i)
        except: pass
    return (min(solvedEvalPoints).simplify(), min(crit)), (max(solvedEvalPoints).simplify(), max(crit))
    # return f'Min: {min(solvedEvalPoints).simplify()} at {var} = {min(crit)}, Max: {max(solvedEvalPoints).simplify()} at {var} = {max(crit)}'


def get_interval_desc(expr, var, interval):
    rtn = ['constant', 'increasing', 'decreasing']
    diff = expr.diff(var, 1)

    crit = critical_points(expr, var, interval)

    if not len(crit):
        rtn.clear()

    for point in crit:
        # constant
        if diff.subs(var, point) == 0:
            rtn.remove('increasing')
            rtn.remove('decreasing')
        # increasing
        elif diff.subs(var, point) > 0:
            rtn.remove('decreasing')
            rtn.append('constant')
        # decreasing
        else:
            rtn.append('constant')
            rtn.append('increasing')

    minmax = min_max(expr, var, interval)
    if len(minmax[0]):
        # If min > 0, they're all positive
        if minmax[0][1] > 0:
            rtn.append('positive')
        # If max < 0, they're all negative
        if minmax[1][1] < 0:
            rtn.append('negative')
        # Save as positive, except >=
        if minmax[0][1] >= 0:
            rtn.append('nonnegative')

    return rtn
