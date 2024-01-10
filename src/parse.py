from sympy import *
from sympy.abc import *
from sympy.core.function import AppliedUndef, UndefinedFunction
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import (convert_xor, implicit_multiplication,
                                        implicit_multiplication_application,
                                        lambda_notation, parse_expr,
                                        standard_transformations)
from sympy.physics.units import *
from sympy.physics.units.prefixes import Prefix
import re
import streamlit as st
from sympy.parsing.latex import parse_latex
from sympy.parsing import parse_expr
import ezregex as er

arrowRegex    = (er.group(er.chunk) + '->' + er.group(er.chunk)).compile()
doubleEqRegex = (er.group(er.chunk) + '==' + er.group(er.chunk)).compile()
eqRegex       = (er.group(er.chunk) + '='  + er.group(er.chunk)).compile()

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
    eq = re.subn(doubleEqRegex, r'Eq(\g<1>, \g<2>)',     eq, 1)[0]
    eq = re.subn(eqRegex,       r'\g<2> - \g<1>', eq, 1)[0]

    # eq = re.sub((match('e') + optional(ifPrecededBy(digit())) + ifNotFollowedBy(anyAlphaNum()) + ifNotPrecededBy(alpha())).str(), 'E', eq)

    return eq

def get_atoms(expr):
    return list(filter(lambda i: isinstance(i, Symbol), expr.atoms()))

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

def parse(text):
    #* If there's nothing there, it's okay
    if text is not None and not len(text):
        return

    #* Now calculate everything
    # First, run the input string through our function to make sure we take care
    # of the things sympy won't take care of for us (= to Eq() and the like)
    if _detectLatex(text):
        text = _convertLatex(text)

    sanatized = _sanatizeInput(text)

    # Actually parse the expression (but don't solve it yet!)
    # expr = parse_expr(sanatized, transformations=st.session_state.transformation, evaluate=False)
    expr = parse_expr(sanatized, evaluate=False)

    # See if we need to remove one side of the equation
    if st.session_state.remove_fx and isinstance(expr, Eq):
        expr = expr.rhs

    return expr
