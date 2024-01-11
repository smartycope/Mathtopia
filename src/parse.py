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

arrowRegex    = (er.group(er.chunk) + er.ow + '->' + er.ow + er.group(er.chunk)).compile()
doubleEqRegex = (er.group(er.chunk) + er.ow + '==' + er.ow + er.group(er.chunk)).compile()
eqRegex       = (er.group(er.chunk) + er.ow + er.anyCharExcept('<>!=') + '=' + er.anyCharExcept('<>!=') + er.ow + er.group(er.chunk)).compile()

varTypes = (Symbol, Derivative, Function, Integral)
funcTypes = (AppliedUndef, UndefinedFunction) #, Function, WildFunction)


def _detectLatex(s):
    return '\\' in s or '{' in s or '}' in s

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

def _sanatizeInput(eq:str):
    eq = re.sub('−', '-', eq)
    eq = re.sub('π', 'pi', eq)
    eq = re.sub('∞', 'oo', eq)
    eq = re.sub('⋅', '*', eq)
    eq = re.sub('×', '*', eq)
    eq = re.sub('→', '->', eq)
    eq = re.sub('∫', 'Integral', eq)

    eRegex = 'e' + er.ifNotPrecededBy(er.wordChar) + er.ifNotFollowedBy(er.wordChar)
    eq = re.sub(str(eRegex), 'E', eq)

    eq = re.subn(arrowRegex,    r'Lambda(\g<1>, \g<2>)', eq, 1)[0]

    # These have the same groups, and shouldn't both be in the same equation (that doesn't make sense)
    m = re.search(doubleEqRegex, eq) or re.search(eqRegex, eq)
    if m is not None:
        eq = m.group(1)
        st.session_state['set_expr'] = m.group(1)
        st.session_state['eq'] = m.group(2)
        # Because this is being called parse(), which is being called just after
        # we get the text from the user, rerun so it loads the updated text given here
        st.rerun()

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
    atoms = list(filter(atom_filter, expr.atoms()))
    # if isinstance(expr, MatrixBase):
        # atoms += [Symbol(f'col_{i}') for i in range(expr.cols)]
    return atoms

    # Old code that works, but I feel like the above line is better
    atoms = set()

    if st.session_state.get_vars_from_vars:
        # TODO
        NotImplemented
        #* Get any variables that are exclusively defined in the variable setter, and add them to atoms
        # iterate through the variables that have been changed
        # for i in filter(lambda x: x.valueChanged, self.vars):
        #     # Get that atoms in the value of i
        #     atoms = atoms.union(i.value.atoms(*self.varTypes+self.funcTypes))
        #     funcs = set()
        #     for func in i.value.atoms(*self.funcTypes):
        #         funcs = funcs.union((type(func),))
        #     atoms = atoms.union(funcs)

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

# def updateVars(expr):
    # atoms = _getAtoms(expr)

    # #* Get all the things in atoms that aren't already in self.vars and add them
    # # Get a set of the symbols in self.vars
    # curSymbols = set([v.symbol for v in self.vars])
    # for s in atoms.difference(curSymbols):
    #     # If it's likely a unit, fill it with that first
    #     self.vars.append(Variable(s))

    # #* Now get all the things in self.vars that aren't in atoms and delete them
    # if not self.options.rememberVarNames.isChecked():
    #     for s in curSymbols.difference(atoms):
    #         del self.vars[getIndexWith(self.vars, lambda x: x.symbol == s)]

    # #* Double check that this is a set, and not a list (no duplicates)
    # # But varHandler wants a list, I guess
    # self.vars = sorted(list(set(self.vars)), key=lambda var: var.name)

def parse(text, manual_latex=False) -> Expr:
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

    sanatized = _sanatizeInput(text)

    # Because we're including locals in the parsing, parse these too
    i = I
    e = E

    # Actually parse the expression (but don't solve it yet!)
    # expr = parse_expr(sanatized, transformations=st.session_state.transformation, evaluate=False)
    trans = (convert_xor, lambda_notation) + standard_transformations
    if st.session_state.impl_mul:
        trans += (implicit_multiplication,)
    try:
        expr = parse_expr(sanatized, evaluate=False, transformations=trans, local_dict=locals())
    except Exception as err:
        st.markdown('#### Invalid syntax in expression')
        st.exception(err)
    else:
        # See if we need to remove one side of the equation
        if st.session_state.remove_fx and isinstance(expr, Eq):
            expr = expr.rhs

        return expr
