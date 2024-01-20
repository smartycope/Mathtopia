import streamlit as st
from Cope import RedirectStd, ensure_iterable
from src.funcs import *
import io
from src.helper import show_sympy
from src.SS import ss
from src.parse import parse
# ss = st.session_state.ss

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

        _locals = locals()
        _locals[ss.func_name] = lambda *args: expr.subs(vars)
        for i in range(ss.num_funcs):
            _locals[f'{ss.func_names[i]}'] = ss.exprs[i]
            _locals[f'{ss.func_names[i]}_vars'] = ss.vars[i]
            _locals[f'{ss.func_names[i]}_equals'] = parse(ss[f'_eq{i}'])
            if len(ss.solutions) > i:
                _locals[f'{ss.func_names[i]}_solutions'] = ss.solutions[i]

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
