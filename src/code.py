import streamlit as st
from Cope import RedirectStd, ensure_iterable
from src.funcs import *
import io
from src.helper import show_sympy


def formatInput2code(s):
    # keywords = set(dir(builtins) + dir(er) + re.findall((lineStart + group(word) + ifFollowedBy(ow + '=')).str(), s))
    # print(anyExcept(anyof(*keywords), type='.*'))
    # s = re.sub((anyExcept('literal', type='.*')).str(), '"' + replace_entire.str() + '"', s)
    if not len(s):
        return ''
    lines = s.splitlines()
    # Remove the last lines which are actually comments
    if len(lines) > 1:
        while s.splitlines()[-1].strip().startswith('#'):
            lines.pop(-1)
    # Insert the variable assignment to the last line
    lines.append('\n_rtn = '  + lines.pop(-1))
    return '\n'.join(lines)


def run_code(code, rtn_tab, output_tab, errors_tab):
        std = io.StringIO()
        err = io.StringIO()
        expr = st.session_state.expr
        solution = st.session_state.solution
        equals = st.session_state.eq
        vars = st.session_state.vars_dict

        _locals = locals()
        _locals[st.session_state.func_name] = lambda *args: expr.subs(vars)
        with RedirectStd(stdout=std, stderr=err):
            try:
                exec(formatInput2code(code), globals(), _locals)
            except Exception as err:
                errors_tab.exception(err)
            else:
                rtn = _locals.get('_rtn')
                if rtn is not None:
                    if isinstance(rtn, (Dict, dict)):
                        # rtn_tab.write(rtn)
                        show_sympy(rtn, rtn_tab)
                        # rtn_tab.
                    else:
                        for i in ensure_iterable(rtn):
                            # rtn_tab.write(i)
                            show_sympy(i, rtn_tab)
                output_tab.write(std.read())
                errors_tab.write(err.read())
