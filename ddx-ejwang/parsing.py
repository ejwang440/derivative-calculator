import enum
import re

class TokenType(enum.Enum):
    T_NUM = 0
    T_PLUS = 1
    T_MINUS = 2
    T_MULT = 3
    T_DIV = 4
    T_LPAR = 5
    T_RPAR = 6
    T_END = 7
    T_VAR = 8
    T_POW = 9
    T_FUN = 10


class Node:
    def __init__(self, token_type, value=None, charno=-1):
        self.token_type = token_type
        self.value = value
        self.charno = charno
        self.children = []

    def __str__(self):
      if self.token_type in [TokenType.T_NUM, TokenType.T_VAR]:
        return str(self.value)
      elif self.token_type == TokenType.T_FUN:
        return self.value[0] + "(" + str(self.value[1]) + ")"
      else:
        return str(self.value) + (("(" + ", ".join([str(x) for x in self.children]) + ")") if len(self.children) > 0 else "")


def lexical_analysis(s):
    mappings = {
        '+': TokenType.T_PLUS,
        '-': TokenType.T_MINUS,
        '*': TokenType.T_MULT,
        '/': TokenType.T_DIV,
        '^': TokenType.T_POW,
        '(': TokenType.T_LPAR,
        ')': TokenType.T_RPAR}

    tokens = []
    for i, c in enumerate(s):
        if c in mappings:
            token_type = mappings[c]
            token = Node(token_type, value=c, charno=i)
        elif re.match(r'[0-9.]', c):
            token = Node(TokenType.T_NUM, value=c, charno=i)
        elif re.match(r'[a-z]', c):
            token = Node(TokenType.T_VAR, value=c, charno=i)
        elif re.match(r'\s', c):
          continue
        else:
            raise Exception('Invalid token: {}'.format(c))
        if len(tokens) > 0 and token.token_type == tokens[-1].token_type and token.token_type in [TokenType.T_NUM, TokenType.T_VAR]:
          tokens[-1].value += token.value
        else:
          tokens.append(token)
    tokens.append(Node(TokenType.T_END))
    return tokens


def match(tokens, token):
    if tokens[0].token_type == token:
        return tokens.pop(0)
    else:
        raise Exception('Invalid syntax on token {}'.format(tokens[0].token_type))


def parse_e(tokens):
    left_node = parse_e2(tokens)

    while tokens[0].token_type in [TokenType.T_PLUS, TokenType.T_MINUS]:
        node = tokens.pop(0)
        node.children.append(left_node)
        node.children.append(parse_e2(tokens))
        left_node = node

    return left_node


def parse_e2(tokens):
    left_node = parse_e3(tokens)

    while tokens[0].token_type in [TokenType.T_MULT, TokenType.T_DIV]:
        node = tokens.pop(0)
        node.children.append(left_node)
        node.children.append(parse_e3(tokens))
        left_node = node

    return left_node

def parse_e3(tokens):
    left_node = parse_e4(tokens)

    while tokens[0].token_type in [TokenType.T_POW]:
        node = tokens.pop(0)
        node.children.append(left_node)
        node.children.append(parse_e4(tokens))
        left_node = node

    return left_node

def parse_e4(tokens):
    if tokens[0].token_type in [TokenType.T_NUM]:
        return tokens.pop(0)
    elif tokens[0].token_type in [TokenType.T_VAR]:
        if len(tokens) == 1 or tokens[1].token_type != TokenType.T_LPAR:
            return tokens.pop(0)
        else:
          f = tokens.pop(0)
          match(tokens, TokenType.T_LPAR)
          expression = parse_e(tokens)
          match(tokens, TokenType.T_RPAR)
          return Node(TokenType.T_FUN, value=(f.value, expression.value), charno=f.charno)
    elif tokens[0].token_type == TokenType.T_MINUS:
      minus = 0
      while tokens[0].token_type == TokenType.T_MINUS:
        minus = 1 - minus
        tokens.pop(0)
      tokens[0].value = ("-"*minus) + tokens[0].value
      return tokens.pop(0)
    match(tokens, TokenType.T_LPAR)
    expression = parse_e(tokens)
    match(tokens, TokenType.T_RPAR)

    return expression


def parse(inputstring):
    tokens = lexical_analysis(inputstring)
    ast = parse_e(tokens)
    match(tokens, TokenType.T_END)
    return ast

def get_next_split(f):
  return parse(f).charno
