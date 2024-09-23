from parsing import get_next_split
import re

def has_x(f):
  return "x" in f

def is_x(f):
  return 'x' in f and set(f) - set('()x') == set()

def is_zero(f):
  return f in ["0", "0.0", "-0.0", "-0"] and set(f) - set('-().0') == set()


def is_one(f):
  return f in ["1", "1.0"] and set(f) - set('()1.0') == set()

def is_number(f):
  try:
    eval(f)
    return True
  except:
    return False

import decimal

def float_to_string(number, precision=25):
    return '{0:.{prec}f}'.format(
        number, prec=precision,
    ).rstrip('0').rstrip('.') or '0'

def to_number(f):
  result = eval(f.replace("^", "**"))
  if type(result) == float:
    return float_to_string(result)
  return str(result)


REGISTERED_FUNCTIONS = set(['cos', 'sin', 'factorial', 'sec', 'tan', 'log', 'ln'])
OPERATIONS = set(["+", "-", "*", "/", "^"])
pat = r"^(" + r"|".join(["[e0-9.]*"] + [ f + r"\([^()]*\)" for f in REGISTERED_FUNCTIONS]) + ")$"
func_pat  = re.compile(pat)
single_pat = re.compile('\(*[^()]*\)*')

def is_whole_match(f):
  assert(f[0] == "(")
  cnt = 1
  i = 1
  while cnt != 0 and i < len(f):
    if f[i] == '(':
      cnt += 1
    elif f[i] == ')':
      cnt -= 1
    i += 1
  return i == len(f)

def remove_parens(f):
  while len(f) > 0 and f[0] == '(' and is_whole_match(f):
    f = f[1:-1]
  return f

def has_no_ops(f):
  return func_pat.fullmatch(f)
  
def is_registered_function(f):
  return any([f.startswith(fun) for fun in REGISTERED_FUNCTIONS])

from math import factorial, pi, sin, cos, log

def cleanup(f):
  f = remove_parens(f)
  if f == "e":
    return "e"
  elif f == "ln(e)":
    return "1"
  elif is_number(f):
    return to_number(f)
  elif has_no_ops(f) and is_registered_function(f):
    i = f.index('(')
    return f[0:i] + '(' + cleanup(f[i:]) + ')'
  elif is_x(f):
    return "x"
  else:
    s = get_next_split(f)
    left = remove_parens(cleanup(f[0:s].strip()))
    op = f[s]
    right = remove_parens(cleanup(f[s+1:].strip()))
    if op == "+" and is_zero(left):
      return right
    elif op == "+" and is_zero(right):
      return left
    elif op == "-" and is_zero(right):
      return left
    elif op == "*" and (is_zero(left) or is_zero(right)):
      return "0"
    elif op == "*" and is_one(left):
      return right
    elif op == "*" and is_one(right):
      return left
    elif op == "^" and is_zero(right):
      return "1"
    elif op == "^" and is_one(right):
      return left
    elif op == "/" and is_zero(left):
      return "0"
    elif op == "/" and is_one(right):
      return left
    elif len(left) > 1 or len(right) > 1:
      left = ("(" + left + ")") if not has_no_ops(left) else left
      right = ("(" + right + ")") if not has_no_ops(right) else right
      return left + op + right
    return left + op + right