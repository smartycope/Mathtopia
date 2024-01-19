from sympy.abc import *
from sympy.core.function import AppliedUndef, UndefinedFunction
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import (convert_xor, implicit_multiplication,
                                        implicit_multiplication_application,
                                        lambda_notation, parse_expr,
                                        standard_transformations)
from sympy.physics.units import *
from sympy.physics.units.prefixes import Prefix
from sympy import *
import re
import streamlit as st
from sympy.parsing.latex import parse_latex
from sympy.parsing import parse_expr
import ezregex as er
from pages.Constants import constants

# ss = st.session_state.ss
from src.SS import ss

arrowRegex    = (er.group(er.chunk) + er.ow + '->' + er.ow + er.group(er.chunk)).compile()
doubleEqRegex = (er.group(er.chunk) + er.ow + '==' + er.ow + er.group(er.chunk)).compile()
eqRegex       = (er.group(er.chunk) + er.ow + er.anyCharExcept('<>!=') + '=' + er.anyCharExcept('<>!=') + er.ow + er.group(er.chunk)).compile()

varTypes = (Symbol, Derivative, Function, Integral)
funcTypes = (AppliedUndef, UndefinedFunction) #, Function, WildFunction)

replacements = {
    '−': '-',
    'π': 'pi',
    '∞': 'oo',
    '⋅': '*',
    '×': '*',
    '→': '->',
    '∫': 'Integral',
}

def _detectLatex(s):
    return '\\' in s or '{' in s or '}' in s or '$' in s

def _sanatizeLatex(latex):
    if latex[-1] == '.':
        latex = latex[:-1]
    latex = re.sub('\$_', '', latex)
    latex = re.sub('\$', '', latex)
    latex = re.sub('\\dfrac', '\\frac', latex)
    latex = re.sub(r'\\displaystyle', '', latex)
    # latex = re.sub(r'\\ ', '', latex)
    latex = re.sub(r'\\ dx', 'dx', latex)
    return latex

def _convertLatex(s):
    return str(parse_latex(_sanatizeLatex(s)))

def detect_equals(s, expr_index) -> ('lhs', 'rhs'):
    # These have the same groups, and shouldn't both be in the same equation (that doesn't make sense)
    m = re.search(doubleEqRegex, s) or re.search(eqRegex, s)
    if m is not None:
        # eq = m.group(1)
        # ss['set_expr'] = m.group(1)
        # ss._exprs[expr_index] = m.group(1)
        return m.group(1), m.group(2)
        # ss[f'_expr{i}'] = m.group(1)
        # ss._eqs[expr_index] = m.group(2)
        # Because this is being called parse(), which is being called just after
        # we get the text from the user, rerun so it loads the updated text given here
        print('rerunning...')
        # st.rerun()
    else:
        return s, None


def _sanatizeInput(eq:str, replace_constants=True):
    for symbol, replacement in replacements.items():
        eq = re.sub(symbol, replacement, eq)

    if replace_constants:
        for default, replacement in constants.items():
            found = re.search(default, eq)
            # So it only toasts if it's relevant
            if found is not None:
                eq = re.sub(default, replacement['value'], eq)
                # Make sure they know the correct units
                if ss.get('to_toast') is not None:
                    ss['to_toast'] = ss['to_toast'].append(f"{default} is in units of {replacement['unit']}")
                else:
                    ss['to_toast'] = [f"{default} is in units of {replacement['unit']}"]
                # For good measure, try to toast, even though it doesn't work here
                # (for some scudding reason)
                st.toast(f"{default} is in units of {replacement['unit']}")

    # eRegex = 'e' + er.ifNotPrecededBy(er.wordChar) + er.ifNotFollowedBy(er.wordChar)
    # eq = re.sub(str(eRegex), 'E', eq)

    eq = re.subn(arrowRegex, r'Lambda(\g<1>, \g<2>)', eq, 1)[0]


    # eq = re.subn(eqRegex,       r'\g<2> - \g<1>', eq, 1)[0]
    # eq = re.subn(doubleEqRegex, r'Eq(\g<1>, \g<2>)',     eq, 1)[0]

    # eq = re.sub((match('e') + optional(ifPrecededBy(digit())) + ifNotFollowedBy(anyAlphaNum()) + ifNotPrecededBy(alpha())).str(), 'E', eq)

    return eq

def get_atoms(expr):
    # return sorted(list(filter(lambda i: isinstance(i, Symbol), expr.atoms())), reverse=False, key=str)
    def atom_filter(i):
        return (
            isinstance(i, Symbol) and
            str(i) not in ('-', '+', ' ', '')
        )
    if expr is None:
        return []

    atoms = list(filter(atom_filter, expr.atoms()))
    # if isinstance(expr, MatrixBase):
        # atoms += [Symbol(f'col_{i}') for i in range(expr.cols)]
    return atoms

    # Old code that works, but I feel like the above line is better
    atoms = set()

    #* Get the atoms in the input equation
    atoms = atoms.union(expr.atoms(*varTypes))
    funcs = set()
    for func in expr.atoms(*funcTypes):
        funcs = funcs.union((type(func),))
    atoms = atoms.union(funcs)

    #* Get the atoms in the solution
    # TODO
    # atoms = atoms.union(self.solvedExpr.atoms(*self.varTypes))

    # Remove any unit from atoms (we only want to touch those internally)
    # todo('this needs more work')
    atoms = filter(lambda a: type(a) not in (Quantity, Prefix), atoms)
    atoms = set(atoms)

    return atoms

def parse(text, manual_latex=False, replace_constants=True) -> Expr:
    # Not technically necissary, unless they bookmark a page that uses parse
    if 'impl_mul' not in ss:
        ss['impl_mul'] = True
    # if 'remove_fx' not in ss:
        # ss['remove_fx'] = False

    # print('attempting to parse ', text, ' ', sep='`')
    #* If there's nothing there, it's okay
    if text is None or not len(text.strip()):
        return

    #* Now calculate everything
    # First, run the input string through our function to make sure we take care
    # of the things sympy won't take care of for us (= to Eq() and the like)
    if _detectLatex(text) or manual_latex:
        if not manual_latex:
            st.toast('Detected LaTeX, converting')
        text = _convertLatex(text)

    sanatized = _sanatizeInput(text, replace_constants)

    # Because we're including locals in the parsing, parse these too
    i = I
    e = E

    # Actually parse the expression (but don't solve it yet!)
    # expr = parse_expr(sanatized, transformations=ss.transformation, evaluate=False)
    trans = (convert_xor, lambda_notation) + standard_transformations
    if ss.impl_mul:
        trans += (implicit_multiplication,)
    try:
        expr = parse_expr(sanatized, evaluate=False, transformations=trans, local_dict=locals())
    except Exception as err:
        st.markdown('#### Invalid syntax in expression')
        st.exception(err)
    # Don't do this anymore. We now handle equal signs by putting them in the = box
    else:
        # See if we need to remove one side of the equation
        # if ss.remove_fx and isinstance(expr, Eq):
            # expr = expr.rhs
        # print(f'Parsed `{text}` as `{expr}`')
        return expr
