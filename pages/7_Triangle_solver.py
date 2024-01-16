from sympy import *
from Cope import *
import streamlit as st
from src.parse import parse
from copy import copy
from sympy import N

# Save the main UI state so we can come back to it
st.session_state['_expr'] = st.session_state.get('_expr')
st.session_state['eq'] = st.session_state.get('eq')
st.session_state['vars'] = st.session_state.get('vars')

st.set_page_config(layout='wide')
st.session_state['square'] = '90'
invalid = False

if 'user_inputted' not in st.session_state:
    st.session_state['user_inputted'] = []

left, mid, right = st.columns(3)
# This is DIFFERENT from num_eval, by intent. Don't get them confused.
eval_num = left.checkbox('Evaluate Non-Symbolically', key='eval_num')
eval_num_changed = st.session_state.get('prev_eval_num') != eval_num
st.session_state['prev_eval_num'] = eval_num

if eval_num:
    rnd = right.number_input('Round to:', value=3)

reset = mid.button('Reset All') or eval_num_changed

left, mid, right = st.columns([.3, .4, .3])
mid.image('assets/triangle.png')


if 'top_left'     not in st.session_state or reset:     st.session_state['top_left'] = ''
if 'top_right'    not in st.session_state or reset:    st.session_state['top_right'] = ''
if 'bottom_left'  not in st.session_state or reset:  st.session_state['bottom_left'] = ''
if 'bottom_right' not in st.session_state or reset: st.session_state['bottom_right'] = ''
if 'left_side'    not in st.session_state or reset:    st.session_state['left_side'] = ''
if 'right_side'   not in st.session_state or reset:   st.session_state['right_side'] = ''
if 'left_width'   not in st.session_state or reset:   st.session_state['left_width'] = ''
if 'right_width'  not in st.session_state or reset:  st.session_state['right_width'] = ''
if 'top_center'   not in st.session_state or reset:   st.session_state['top_center'] = ''
if 'height'       not in st.session_state or reset:       st.session_state['height'] = ''
if 'total_width'  not in st.session_state or reset:  st.session_state['total_width'] = ''

def set_as_user_inputted(name):
    st.session_state['user_inputted'].append(name)

top_left     = left.text_input('Top Left',      st.session_state['top_left'],     on_change=lambda: set_as_user_inputted('top_left'), key='_top_left');     st.session_state['top_left']     = top_left
top_right    = right.text_input('Top Right',    st.session_state['top_right'],    on_change=lambda: set_as_user_inputted('top_right'), key='_top_right');    st.session_state['top_right']    = top_right
bottom_left  = left.text_input('Bottom Left',   st.session_state['bottom_left'],  on_change=lambda: set_as_user_inputted('bottom_left'), key='_bottom_left');  st.session_state['bottom_left']  = bottom_left
bottom_right = right.text_input('Bottom Right', st.session_state['bottom_right'], on_change=lambda: set_as_user_inputted('bottom_right'), key='_bottom_right'); st.session_state['bottom_right'] = bottom_right

left_side    = left.text_input('Left Side',     st.session_state['left_side'],    on_change=lambda: set_as_user_inputted('left_side'), key='_left_side');    st.session_state['left_side']    = left_side
right_side   = right.text_input('Right Side',   st.session_state['right_side'],   on_change=lambda: set_as_user_inputted('right_side'), key='_right_side');   st.session_state['right_side']   = right_side
left_width   = left.text_input('Left Width',    st.session_state['left_width'],   on_change=lambda: set_as_user_inputted('left_width'), key='_left_width');   st.session_state['left_width']   = left_width
right_width  = right.text_input('Right Width',  st.session_state['right_width'],  on_change=lambda: set_as_user_inputted('right_width'), key='_right_width');  st.session_state['right_width']  = right_width

top_center   = st.text_input('Top Center',      st.session_state['top_center'],   on_change=lambda: set_as_user_inputted('top_center'), key='_top_center');   st.session_state['top_center']   = top_center
height       = st.text_input('Height',          st.session_state['height'],       on_change=lambda: set_as_user_inputted('height'), key='_height');       st.session_state['height']       = height
total_width  = st.text_input('Total Width',     st.session_state['total_width'],  on_change=lambda: set_as_user_inputted('total_width'), key='_total_width');  st.session_state['total_width']  = total_width


angles = (top_left, top_right, bottom_left, bottom_right, top_center)
lines  = (left_side, right_side, left_width, right_width, height, total_width)
combined = angles + lines

prev = copy(combined)

def have(*stuff):
    rtn = all(stuff)
    return rtn

def calc(setTo, expr):
    global invalid
    if setTo != 'square' or eval_num_changed:
        expr = str(round(simplify(N(expr)), rnd) if st.session_state.eval_num else expr)

        if len(st.session_state[setTo]):
            if st.session_state[setTo] != expr and not setTo in st.session_state['user_inputted']:
                # This says that the user-inputted values are invalid (which makes you wonder about the validity of the answers this provides)
                # invalid = f'{st.session_state[setTo]} != {expr}'
                pass
        else:
            st.session_state[setTo] = expr


# Do all the calculations
# Underscored variables indicate it's a string name, while the non-underscored indicate it's an Expr
# Calculate any of the obviously missing things
if have(bottom_left,  bottom_right): calc('top_center',   parse(bottom_left) + parse(bottom_right))
if have(bottom_left,  top_center):   calc('bottom_right', parse(top_center)  - parse(bottom_left))
if have(bottom_right, top_center):   calc('bottom_left',  parse(top_center)  - parse(bottom_right))

if have(left_width,  right_width):   calc('total_width',  parse(left_width)   + parse(right_width))
if have(total_width, left_width):    calc('right_width',  parse(total_width)  - parse(left_width))
if have(total_width, right_width):   calc('left_width',   parse(total_width)  - parse(right_width))


# All triangles must contain 180 degrees
triangle_angles = (
    ('top_center', 'bottom_right', 'bottom_left'),
    ('bottom_right', 'top_right', 'square'),
    ('bottom_left', 'top_left', 'square'),
)
for _a, _b, _c in triangle_angles:
    a, b, c = map(lambda k: parse(st.session_state.get(k)), (_a, _b, _c))
    if have(a, b): calc(_c, pi - a - b)
    if have(a, c): calc(_b, pi - a - c)
    if have(b, c): calc(_a, pi - b - c)


# Trig stuff
angleRelations = (
    ('bottom_right', 'height',      'right_width', 'right_side'),
    ('top_right',    'right_width', 'height',      'right_side'),
    ('bottom_left',  'height',      'left_width',  'left_side'),
    ('top_left',     'left_width',  'height',      'left_side'),
)
for _ang, _opp, _adj, _hyp in angleRelations:
    ang, opp, adj, hyp = map(lambda k: parse(st.session_state.get(k)), (_ang, _opp, _adj, _hyp))

    # Soh Cah Toa
    if have(opp, hyp): calc(_ang, asin(opp) / (hyp))
    if have(adj, hyp): calc(_ang, acos(adj) / (hyp))
    if have(opp, adj): calc(_ang, atan(opp) / (adj))

    if have(ang):
        theta = ang
        if have(hyp):
            calc(_opp, hyp * sin(theta))
            calc(_adj, hyp * cos(theta))
        if have(opp):
            calc(_hyp, opp / sin(theta))
            calc(_adj, opp / tan(theta))
        if have(adj):
            calc(_hyp, adj / cos(theta))
            calc(_opp, adj * tan(theta))


# Pythagorean theorem
right_triangle_lines = (
    ('right_side', 'right_width', 'height'),
    ('left_side',  'left_width',  'height'),
)
for _a, _b, _c in right_triangle_lines:
    a, b, c = map(lambda k: parse(st.session_state.get(k)), (_a, _b, _c))
    if have(a, b): calc(_c, sqrt(a**2 + b**2))
    if have(a, c): calc(_b, sqrt(a**2 + c**2))
    if have(b, c): calc(_a, sqrt(b**2 + c**2))


#* If we have top_center and a line adjacent to it, we can make an imaginary triangle on the outside,
#   and then solve for that triangle's opposite (height) and adjecent (base)
# imaginaryOutsideTriangles = (
#     (right_side, right_width),
#     (_left_side, left_width)
# )
# if have(top_center):
#     for hyp, base in imaginaryOutsideTriangles:
#         if have(hyp):
#             theta = rad(180) - top_center
#             # print('theta:', theta)
#             # print('hyp:', hyp)
#             # print('cos(theta):', cos(theta))
#             # print('sin(theta):', sin(theta))
#             calc(base, hyp * cos(theta))
#             calc(height, hyp * sin(theta))


angles = map(st.session_state.get, ('top_left', 'top_right', 'bottom_left', 'bottom_right', 'top_center'))
lines  = map(st.session_state.get, ('left_side', 'right_side', 'left_width', 'right_width', 'height', 'total_width'))
combined = tuple(angles) + tuple(lines)

if invalid:
    st.warning(f'Invalid Triangle: {invalid}')

st.divider()

"""
Put in the values you *do* have, and this will solve for the values you *don't* have.

If you're rounding, be sure to set the digits to round to *before* entering your values, otherwise it won't work.
"""

# Keep calculating until we can't anymore
if prev != combined:
    st.rerun()
