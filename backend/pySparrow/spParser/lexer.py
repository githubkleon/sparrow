from ply.lex import *
import splog as log

keywords = (
    "IF", "ELSE", "ELIF",
    "CASE", 
    "FOR",
    "GIF", "GELSE", "GELIF",
    "GCASE", 
    "GFOR",
    "DATA", "TYPE",
    "CONTAINER", "INTERFACE",
    "INPUT", "OUTPUT", "IN", "OUT", "INOUT",
    "MASTER", "SLAVE",
    "VARIABLE", "VAR",
    "INSTANCE", "INS",
    "INFIX", "INFIXR", "INFIXL",
    "IMPORT", "AS", "EXCEPT", "REGISTER", "CONTEXT",
    )

tokens = keywords + (
    "OPERATOR",
    # "NUMBER",
    'FLOATNUMBER', 'STRING_LITERAL',
    'INTNUMBER_DEC', 'SIGNED_INTNUMBER_DEC',
    'INTNUMBER_HEX', 'SIGNED_INTNUMBER_HEX',
    'INTNUMBER_OCT', 'SIGNED_INTNUMBER_OCT',
    'INTNUMBER_BIN', 'SIGNED_INTNUMBER_BIN',
    "COLON", "SEMICOLON", "DUALCOLON",
    "INDENT",
    "DEDENT",
    "WS",
    "NEWLINE",
    "ENDMARKER",
    "ID",
    "EQUALS",
    "QUESTIONMARK",
    "LARROW", "RARROW", "BARROW",
    "LPAREN", "RPAREN",
    "LBRACKET", "RBRACKET",
    "LBRACE", "RBRACE",
    "COMMA", "DOT",
)

reserved = {}
for keyword in keywords:
    reserved[keyword.lower()] = keyword

# ((->)|(<-)|(<>)|(=)|(\?))([+\-*/<>^%&~?\|=]+))
operator = r"""(?!//)[+\-*/<>^%&~\?\|=!]+"""

@TOKEN(operator)
def t_OPERATOR(t):
    # print (t.value)
    if   t.value == t_LARROW:
        t.type = "LARROW"
    elif t.value == t_RARROW:
        t.type = "RARROW"
    elif t.value == t_BARROW:
        t.type = "BARROW"
    elif t.value == t_EQUALS:
        t.type = "EQUALS"
    elif t.value == s_QUESTIONMARK:
        t.type = "QUESTIONMARK"

    return t

t_COLON = r':'
t_SEMICOLON = r';'
t_DUALCOLON = r'::'
t_EQUALS = r'='
s_QUESTIONMARK = '?'
t_COMMA = r','
t_DOT = r'.'
# t_NUMBER = r'\d+'

def t_LPAREN(t):
    r'\('
    t.lexer.paren_count += 1
    return t

def t_RPAREN(t):
    r'\)'
    t.lexer.paren_count -= 1
    return t

t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LARROW = r'<-'
t_RARROW = r'->'
t_BARROW = r'<>'

identifier = r"""(([a-zA-Z_])([a-zA-Z_0-9$])*)|((\\\S)(\S)*)"""

bin_number = '[0-9]*\'[bB][0-1xXzZ?][0-1xXzZ?_]*'
signed_bin_number = '[0-9]*\'[sS][bB][0-1xZzZ?][0-1xXzZ?_]*'
octal_number = '[0-9]*\'[oO][0-7xXzZ?][0-7xXzZ?_]*'
signed_octal_number = '[0-9]*\'[sS][oO][0-7xXzZ?][0-7xXzZ?_]*'
hex_number = '[0-9]*\'[hH][0-9a-fA-FxXzZ?][0-9a-fA-FxXzZ?_]*'
signed_hex_number = '[0-9]*\'[sS][hH][0-9a-fA-FxXzZ?][0-9a-fA-FxXzZ?_]*'

decimal_number = '([0-9]*\'[dD][0-9xXzZ?][0-9xXzZ?_]*)|([0-9][0-9_]*)'
signed_decimal_number = '[0-9]*\'[sS][dD][0-9xXzZ?][0-9xXzZ?_]*'

exponent_part = r"""([eE][-+]?[0-9]+)"""
fractional_constant = r"""([0-9]*\.[0-9]+)|([0-9]+\.)"""
float_number = '(((('+fractional_constant+')'+exponent_part+'?)|([0-9]+'+exponent_part+')))'

simple_escape = r"""([a-zA-Z\\?'"])"""
octal_escape = r"""([0-7]{1,3})"""
hex_escape = r"""(x[0-9a-fA-F]+)"""
escape_sequence = r"""(\\("""+simple_escape+'|'+octal_escape+'|'+hex_escape+'))'
string_char = r"""([^"\\\n]|"""+escape_sequence+')'
string_literal = '"'+string_char+'*"'

@TOKEN(identifier)
def t_ID(t):
    t.type = reserved.get(t.value, 'ID')
    return t

@TOKEN(float_number)
def t_FLOATNUMBER(t):
    return t

@TOKEN(string_literal)
def t_STRING_LITERAL(t):
    return t

@TOKEN(signed_bin_number)
def t_SIGNED_INTNUMBER_BIN(t):
    return t

@TOKEN(bin_number)
def t_INTNUMBER_BIN(t):
    return t

@TOKEN(signed_octal_number)
def t_SIGNED_INTNUMBER_OCT(t):
    return t

@TOKEN(octal_number)
def t_INTNUMBER_OCT(t):
    return t

@TOKEN(signed_hex_number)
def t_SIGNED_INTNUMBER_HEX(t):
     return t

@TOKEN(hex_number)
def t_INTNUMBER_HEX(t):
     return t

@TOKEN(signed_decimal_number)
def t_SIGNED_INTNUMBER_DEC(t):
    return t

@TOKEN(decimal_number)
def t_INTNUMBER_DEC(t):
    return t

def t_WS(t):
    r'[ ]+'
    if t.lexer.at_line_start and t.lexer.paren_count == 0:
        return t

def t_newline(t):
    r'\n+'
    t.lineno += len(t.value)
    t.type = "NEWLINE"
    # print (t.lexer.paren_count)
    if t.lexer.paren_count == 0:
        return t

def t_comment(t):
    r"[\s]*//[^\n]*"
    pass

def t_error(t):
    raise TypeError("Unknown text '%s'" % (t.value,))

class If(object):
    def __init__(self, name, suite=[]):
        self.name = name
        self.suite = suite
    def __repr__(self):
        return "If(%r, %r)" % (self.name, self.suite)

class Name(object):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return "Name(%r)" % (self.name)


# Python's syntax has three INDENT states
#  0) no colon hence no need to indent
#  1) "if 1: go()" - simple statements have a COLON but no need for an indent
#  2) "if 1:\n  go()" - complex statements have a COLON NEWLINE and must indent
NO_INDENT = 0
MAY_INDENT = 1
MUST_INDENT = 2

# only care about whitespace at the start of a line
def track_tokens_filter(lexer, tokens):
    lexer.at_line_start = at_line_start = True
    indent = NO_INDENT
    saw_colon = False
    for token in tokens:
        log.spInfo(0, "PROCESS", token)
        token.at_line_start = at_line_start

        if token.type == "COLON":
            at_line_start = False
            indent = MAY_INDENT
            token.must_indent = False
            
        elif token.type == "NEWLINE":
            at_line_start = True
            if indent == MAY_INDENT:
                indent = MUST_INDENT
            token.must_indent = False

        elif token.type == "WS":
            assert token.at_line_start == True
            at_line_start = True
            token.must_indent = False

        else:
            # A real token; only indent after COLON NEWLINE
            if indent == MUST_INDENT:
                token.must_indent = True
            else:
                token.must_indent = False
            at_line_start = False
            indent = NO_INDENT

        yield token
        lexer.at_line_start = at_line_start

def _new_token(type, lineno):
    tok = LexToken()
    tok.type = type
    tok.value = None
    tok.lineno = lineno
    return tok

# Synthesize a DEDENT tag
def DEDENT(lineno):
    return _new_token("DEDENT", lineno)

# Synthesize an INDENT tag
def INDENT(lineno):
    return _new_token("INDENT", lineno)


# Track the indentation level and emit the right INDENT / DEDENT events.
def indentation_filter(tokens):
    # A stack of indentation levels; will never pop item 0
    levels = [0]
    token = None
    depth = 0
    prev_was_ws = False
    for token in tokens:
##        if 1:
##            print "Process", token,
##            if token.at_line_start:
##                print "at_line_start",
##            if token.must_indent:
##                print "must_indent",
##            print
                
        # WS only occurs at the start of the line
        # There may be WS followed by NEWLINE so
        # only track the depth here.  Don't indent/dedent
        # until there's something real.
        if token.type == "WS":
            assert depth == 0
            depth = len(token.value)
            prev_was_ws = True
            # WS tokens are never passed to the parser
            continue

        if token.type == "NEWLINE":
            depth = 0
            if prev_was_ws or token.at_line_start:
                # ignore blank lines
                continue
            # pass the other cases on through
            yield token
            continue

        # then it must be a real token (not WS, not NEWLINE)
        # which can affect the indentation level

        prev_was_ws = False
        if token.must_indent:
            # The current depth must be larger than the previous level
            if not (depth > levels[-1]):
                raise IndentationError("expected an indented block")

            levels.append(depth)
            log.spInfo(0, "INDENT")
            yield INDENT(token.lineno)

        elif token.at_line_start:
            # Must be on the same level or one of the previous levels
            if depth == levels[-1]:
                # At the same level
                pass
            elif depth > levels[-1]:
                raise IndentationError("indentation increase but not in new block")
            else:
                # Back up; but only if it matches a previous level
                try:
                    i = levels.index(depth)
                except ValueError:
                    raise IndentationError("inconsistent indentation")

                for x in range(i+1, len(levels)):
                    log.spInfo(0, "DEDENT")
                    yield DEDENT(token.lineno)
                    levels.pop()

        yield token

    ### Finished processing ###

    # Must dedent any remaining levels
    if len(levels) > 1:
        assert token is not None
        for _ in range(1, len(levels)):
            log.spInfo(0, "DEDENT")
            yield DEDENT(token.lineno)

# The top-level filter adds an ENDMARKER, if requested.
# Python's grammar uses it.
def filter(lexer, add_endmarker = True):
    token = None
    tokens = iter(lexer.token, None)
    tokens = track_tokens_filter(lexer, tokens)
    for token in indentation_filter(tokens):
        yield token

    if add_endmarker:
        lineno = 1
        if token is not None:
            lineno = token.lineno
        yield _new_token("ENDMARKER", lineno)

class IndentLexer(object):
    def __init__(self, debug=0, optimize=0, lextab='lextab', reflags=0):
        self.lexer = lex(debug=debug, optimize=optimize,
                             lextab=lextab, reflags=reflags)
        self.token_stream = None

    def input(self, s):
        self.lexer.paren_count = 0
        self.lexer.input(s)
        self.token_stream = filter(self.lexer, True)

    def token(self):
        try:
            return next(self.token_stream)
        except StopIteration:
            return None