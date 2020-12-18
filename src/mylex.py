import ply.lex as lex
import ply.yacc as yacc

# === Lexical tokens component ===


reserved = {
    'if' : 'IF',
    'else' : 'ELSE',
    'for' : 'FOR',
    'to' : 'TO'
}

# List of possible token namesthat can be produced by the lexer
# NAME: variable name, L/RPAREN: Left/Right Parenthesis
tokens = [
    'NAME', 'NUMBER',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO', 'EQUALS', 'POWER', 'SQUARE',
    'LPAREN', 'RPAREN',
    'EQUAL', 'NOTEQ', 'LARGE', 'SMALL', 'LRGEQ', 'SMLEQ',
] + list(reserved.values())

# Regular expression rules for tokens format: t_<TOKEN>
# Simple tokens: regex for literals +,-,*,/,%,=,(,) and variable names (alphanumeric)
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_MODULO  = r'%'
t_POWER   = r'\^'
t_SQUARE  = r'\*\*'
t_EQUALS  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_EQUAL   = r'\=\='
t_NOTEQ   = r'\!\='
t_LARGE   = r'\>'
t_SMALL   = r'\<'
t_LRGEQ   = r'\>\='
t_SMLEQ   = r'\<\='


# complex tokens
# number token
def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'NAME')    # Check for reserved words
    return t


# complex tokens
# number token
def t_NUMBER(t):
    r'\d+'  # digit special character regex
    t.value = int(t.value)  # convert str -> int
    return t


# Ignored characters
t_ignore = " \t"  # spaces & tabs regex


# newline character
def t_newline(t):
    r'\n+'  # newline special character regex
    t.lexer.lineno += t.value.count("\n")  # increase current line number accordingly


# error handling for invalid character
def t_error(t):
    print("Illegal character '%s'" % t.value[0])  # print error message with causing character
    t.lexer.skip(1)  # skip invalid character


# Build the lexer
lex.lex()

# === Yacc parsing/grammar component ===

# Precedence & associative rules for the arithmetic operators
# 1. Unary, right-associative minus.
# 2. Binary, left-associative multiplication, division, and modulus
# 3. Binary, left-associative addition and subtraction
# Parenthesis precedence defined through the grammar
precedence = (
    ('if','IF'),
    ('left', 'ELSE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULO'),
    ('right', 'UMINUS'),
)

# dictionary of names (for storing variables)
names = {}

# --- Grammar:
# <statement> -> NAME = <expression> | <expression>
# <expression> -> <expression> + <expression>
#               | <expression> - <expression>
#               | <expression> * <expression>
#               | <expression> / <expression>
#               | <expression> % <expression>
#               | - <expression>
#               | ( <expression> )
#               | NUMBER
#               | NAME
# ---
# defined below using function definitions with format string/comment
# followed by logic of changing state of engine

# if statement
def p_statement_if(p):
    '''statement    : IF LPAREN comparison RPAREN NAME EQUALS expression
                    | IF LPAREN comparison RPAREN NAME EQUALS expression ELSE NAME EQUALS expression '''

    if p[3]:
        names[p[5]] = p[7]
    elif not p[3]:
        if p[9] is not None:
            names[p[9]]=p[11]


def p_statement_for(p):
    '''statement    : FOR NAME EQUALS NUMBER TO NUMBER PLUS
                    | FOR NAME EQUALS NUMBER TO NUMBER TIMES'''
    i=p[2]
    num1=p[4]
    num2=p[6]
    if(p[7]=='+'):
        total = 0
        for i in range(num1,num2+1):
            total+=i
    elif(p[7]=='*'):
        total = 1
        for i in range(num1,num2+1):
            total=total*i      
    names[p[2]]=total


# assignment statement: <statement> -> NAME = <expression>
def p_statement_assign(p):
    'statement : NAME EQUALS expression'
    names[p[1]] = p[3]  # PLY engine syntax, p stores parser engine state


# expression statement: <statement> -> <expression>
def p_statement_expr(p):
    'statement : expression'
    print(p[1])


# comparison
def p_comparison_binop(p):
    '''comparison : expression EQUAL expression
                          | expression NOTEQ expression
                          | expression LARGE expression
                          | expression SMALL expression
                          | expression LRGEQ expression
                          | expression SMLEQ expression'''
    if p[2] == '==':
        p[0] = p[1] == p[3]
    elif p[2] == '!=':
        p[0] = p[1] != p[3]
    elif p[2] == '>':
        p[0] = p[1] > p[3]
    elif p[2] == '<':
        p[0] = p[1] < p[3]
    elif p[2] == '>=':
        p[0] = p[1] >= p[3]
    elif p[2] == '<=':
        p[0] = p[1] <= p[3]


# binary operator expression: <expression> -> <expression> + <expression>
#                                          | <expression> - <expression>
#                                          | <expression> * <expression>
#                                          | <expression> / <expression>
#                                          | <expression> % <expression>
def p_expression_binop(p):
    '''expression : expression PLUS expression
                          | expression MINUS expression
                          | expression TIMES expression
                          | expression DIVIDE expression
                          | expression MODULO expression
                          | expression POWER  expression
                          | expression SQUARE expression'''
    if p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]
    elif p[2] == '*':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        p[0] = p[1] / p[3]
    elif p[2] == '%':
        p[0] = p[1] % p[3]
    elif p[2] == '^':
        p[0] = p[1] ** p[3]
    elif p[2] == '**':
        p[0] = p[1] ** (1/p[3])


# unary minus operator expression: <expression> -> - <expression>
def p_expression_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    p[0] = -p[2]


# parenthesis group expression: <expression> -> ( <expression> )
def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]


# number literal expression: <expression> -> NUMBER
def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]


# variable name literal expression: <expression> -> NAME
def p_expression_name(p):
    'expression : NAME'
    # attempt to lookup variable in current dictionary, throw error if not found
    try:
        p[0] = names[p[1]]
    except LookupError:
        print("Undefined name '%s'" % p[1])
        p[0] = 0


# handle parsing errors
def p_error(p):
    print("Syntax error at '%s'" % p.value)


# build parser
yacc.yacc()

# start interpreter and accept input using commandline/console
while True:
    try:
        s = input('calc > ')  # get user input. use raw_input() on Python 2
    except EOFError:
        break
    yacc.parse(s)  # parse user input string
