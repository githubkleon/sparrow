from backend.pySparrow.spParser.ast import *
from backend.pySparrow.spParser.lexer import *
from ply import *


def p_file_input_end(p):
    """
    file_input_end : file_input ENDMARKER
    """
    p[0] = p[1]


def p_file_input(p):
    """
    file_input : package 
               | NEWLINE
               | package NEWLINE
    """
    if (len(p) == 3):
        p[0] = p[1]
    else:
        if isinstance(p[1], str):
            p[0] = None
        else:
            p[0] = p[1]


def p_package(p):
    """
    package : module
    """
    p[0] = Package(module=p[1], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_module(p):
    """
    module : statements
    """
    p[0] = Module(stmts=p[1], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_statements(p):
    """
    statements : statements statement_stmt
    """
    if p[1]:
        if p[2]:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[2]]
    else:
        p[0] = [p[2]]
    p.set_lineno(0, p.lineno(1))


def p_statements_one(p):
    """
    statements : statement_stmt
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_statement_stmt(p):
    """
    statement_stmt : statement NEWLINE
                   | statement
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_statement(p):
    """
    statement : function_def
              | function_cons
              | operator_def
              | operator_cons
              | operator_infix
              | container_def
              | interface_def
              | type_def
              | type_rename
              | gen_structure
              | import_decl
              | register_decl
              | context_def
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_function_def(p):
    """
    function_def : identifier argument_list EQUALS suite_indent
    """
    p[0] = FunctionDef(name=p[1], args=p[2], suite=p[4], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_argument_list(p):
    """
    argument_list : LPAREN arguments RPAREN
    """
    p[0] = p[2]
    p.set_lineno(0, p.lineno(1))


def p_argument_list_one(p):
    """
    argument_list : argument_name
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_argument_list_empty(p):
    """
    argument_list : empty
    """
    p[0] = []
    p.set_lineno(0, p.lineno(1))


def p_arguments(p):
    """
    arguments : arguments_begin argument_end
    """
    if p[2]:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_arguments_one(p):
    """
    arguments : argument_end
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_arguments_begin(p):
    """
    arguments_begin : arguments_begin argument
    """
    p[0] = p[1] + [p[2]]
    p.set_lineno(0, p.lineno(1))


def p_arguments_begin_one(p):
    """
    arguments_begin : argument
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_argument_end(p):
    """
    argument_end : argument_name
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_argument_end_empty(p):
    """
    argument_end : empty
    """
    p[0] = None
    p.set_lineno(0, p.lineno(1))


def p_argument(p):
    """
    argument : argument_name COMMA
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_argument_name(p):
    """
    argument_name : ID
    """
    p[0] = Argument(p[1], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_operator_def(p):
    """
    operator_def : OPERATOR argument_list EQUALS suite_indent
    """
    p[0] = OperatorDef(name=p[1], args=p[2], suite=p[4], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_operator_def_binary(p):
    """
    operator_def : argument_end OPERATOR argument_end EQUALS statement
    
    """
    p[0] = OperatorDef(name=p[2], args=[p[1], p[3]], suite=p[5], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_operator_def_unary(p):
    """
    operator_def : OPERATOR argument_end EQUALS statement
    
    """
    p[0] = OperatorDef(name=p[1], args=[p[2]], suite=p[4], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_function_cons(p):
    """
    function_cons : identifier DUALCOLON cons_indent
    """
    p[0] = FunctionCons(name=p[1], cons=p[3], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_input_typechain_list(p):
    """
    input_typechain_list : LPAREN typechains RPAREN RARROW
    """
    p[0] = p[2]
    p.set_lineno(0, p.lineno(1))


def p_input_typechain_list_one(p):
    """
    input_typechain_list : typechain_one RARROW
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_input_typechain_list_empty(p):
    """
    input_typechain_list : empty
    """
    p[0] = []
    p.set_lineno(0, p.lineno(1))


def p_output_typechain_list_paren(p):
    """
    output_typechain_list : LPAREN typechain_one RPAREN
    """
    p[0] = [p[2]]
    p.set_lineno(0, p.lineno(1))


def p_output_typechain_list(p):
    """
    output_typechain_list : typechain_one
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_typechains(p):
    """
    typechains : typechains_begin typechain_end
    """
    if p[2]:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_typechains_one(p):
    """
    typechains : typechain_end
    """
    if p[1]:
        p[0] = [p[1]]
    else:
        p[0] = []
    p.set_lineno(0, p.lineno(1))


def p_typechains_begin(p):
    """
    typechains_begin : typechains_begin typechain
    """
    p[0] = p[1] + [p[2]]
    p.set_lineno(0, p.lineno(1))


def p_typechains_begin_one(p):
    """
    typechains_begin : typechain
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_typechain_end(p):
    """
    typechain_end : typechain_one
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_typechain_end_empty(p):
    """
    typechain_end : empty
    """
    p[0] = None
    p.set_lineno(0, p.lineno(1))


def p_typechain(p):
    """
    typechain : typechain_one COMMA
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_typechain_one(p):
    """
    typechain_one : types
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_types(p):
    """
    types : types_begin type_end
    """
    p[0] = p[1] + [p[2]]
    p.set_lineno(0, p.lineno(1))


def p_types_one(p):
    """
    types : type_end
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_types_begin(p):
    """
    types_begin : types_begin type
    """
    p[0] = p[1] + [p[2]]
    p.set_lineno(0, p.lineno(1))


def p_types_begin_one(p):
    """
    types_begin : type
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_type_end(p):
    """
    type_end : type_name
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_type(p):
    """
    type : type_name RARROW
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_type_name(p):
    """
    type_name : pointer
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_cons_indent(p):
    """
    cons_indent : input_typechain_list output_typechain_list NEWLINE
                | NEWLINE INDENT input_typechain_list output_typechain_list NEWLINE DEDENT 
    
    """
    if len(p) == 4:
        p[0] = Cons(inputs=p[1], outputs=p[2], lineno=p.lineno(1))
    else:
        p[0] = Cons(inputs=p[3], outputs=p[4], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_operator_cons(p):
    """
    operator_cons : operators DUALCOLON cons_indent
    
    """
    p[0] = OperatorCons(ops=p[1], cons=p[3], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_operator_infix(p):
    """
    operator_infix : infix_type_decl precedence operators NEWLINE
    
    """
    p[0] = OperatorInfix(ops=p[3], infix=p[1], prec=p[2], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_operators(p):
    """
    operators : operators_begin operator_end
    """
    p[0] = p[1] + [p[2]]
    p.set_lineno(0, p.lineno(1))

def p_operators_one(p):
    """
    operators : operator_end
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))

def p_operators_begin(p):
    """
    operators_begin : operators_begin operator_one
    """
    p[0] = p[1] + [p[2]]
    p.set_lineno(0, p.lineno(1))


def p_operators_begin_one(p):
    """
    operators_begin : operator_one
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_operator_one(p):
    """
    operator_one : OPERATOR COMMA
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_operator_end(p):
    """
    operator_end : OPERATOR
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))

def p_infix_type_decl(p):
    """
    infix_type_decl : INFIX
                    | INFIXR
                    | INFIXL
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_precedence(p):
    """
    precedence : INTNUMBER_DEC
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_type_def(p):
    """
    type_def : DATA type_name EQUALS constructor_list
    """
    p[0] = TypeDef(name=p[2], constructors=p[4], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_constructor_list(p):
    """
    constructor_list : constructors
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_constructors(p):
    """
    constructors : constructors_begin constructor_end
    """
    if p[2]:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = p[1]

    p.set_lineno(0, p.lineno(1))


def p_constructors_one(p):
    """
    constructors : constructor_end
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_constructors_begin(p):
    """
    constructors_begin : constructors_begin constructor
    """
    if p[1]:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[2]]
    p.set_lineno(0, p.lineno(1))


def p_constructors_begin_one(p):
    """
    constructors_begin : constructor
    """
    if p[1]:
        p[0] = [p[1]]
    else:
        p[0] = []
    p.set_lineno(0, p.lineno(1))


def p_constructor_end(p):
    """
    constructor_end : constructor_one
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_constructor_one(p):
    """
    constructor_one : constructor_name constructor_param_list
    """
    p[0] = Constructor(name=p[1], elements=p[2], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))

def p_constructor(p):
    """
    constructor : constructor_name constructor_param_list QUESTIONMARK
    """
    p[0] = Constructor(name=p[1], elements=p[2], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_constructor_name(p):
    """
    constructor_name : ID
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_constructor_param_list_empty(p):
    """
    constructor_param_list : empty
    """
    p[0] = []
    p.set_lineno(0, p.lineno(1))


def p_constructor_param_list(p):
    """
    constructor_param_list : LPAREN constructor_params RPAREN
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_constructor_params(p):
    """
    constructor_params : constructor_params_begin constructor_param_end
    """
    p[0] = p[1] + p[2]
    p.set_lineno(0, p.lineno(1))


def p_constructor_params_begin(p):
    """
    constructor_params_begin : constructor_params_begin constructor_param_one
    """
    p[0] = p[1] + [p[2]]
    p.set_lineno(0, p.lineno(1))


def p_constructor_params_begin_one(p):
    """
    constructor_params_begin : constructor_param_one
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_constructor_param_end(p):
    """
    constructor_param_end : constructor_param
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_constructor_param_end_empty(p):
    """
    constructor_param_end : empty
    """
    p[0] = []
    p.set_lineno(0, p.lineno(1))


def p_constructor_param_one(p):
    """
    constructor_param_one : constructor_param COMMA
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_constructor_param(p):
    """
    constructor_param : type_name identifier
    """
    p[0] = ConstructorParameter(type=p[1], identifier=p[2], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_type_rename(p):
    """
    type_rename : TYPE type_name EQUALS type_name
    """
    p[0] = TypeRename(name=p[2], type=p[4], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_import_decl(p):
    """
    import_decl : IMPORT identifier keyword_as keyword_except argument_list
    """
    p[0] = ImportDecl(package=p[2], scope=p[3], nothiding=p[4], args=p[5], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_keyword_as(p):
    """
    keyword_as : AS identifier 
    """
    p[0] = p[2]
    p.set_lineno(0, p.lineno(1))


def p_keyword_as_empty(p):
    """
    keyword_as : empty
    """
    p[0] = None
    p.set_lineno(0, p.lineno(1))


def p_keyword_except(p):
    """
    keyword_except : EXCEPT 
    """
    p[0] = False
    p.set_lineno(0, p.lineno(1))


def p_keyword_except_empty(p):
    """
    keyword_except : empty
    
    """
    p[0] = True
    p.set_lineno(0, p.lineno(1))


def p_register_decl(p):
    """
    register_decl : REGISTER LBRACKET identifier RBRACKET identifier keyword_as keyword_except argument_list
    
    """
    p[0] = RegisterDecl(filetype=p[3], package=p[5], scope=p[6], nothiding=p[7], args=p[8], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_gen_structure(p):
    """
    gen_structure : gen_if_structure
        | gen_case_structure
        | gen_for_structure
    
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_gen_if_structure(p):
    """
    gen_if_structure : GIF expression COLON gsuite_indent gelifs gels
    """
    p[0] = GenIfStructure(test=p[2], suite=p[4], elifs=p[5], els=p[6], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_gelifs(p):
    """
    gelifs : gelifs gelif_one
    """
    p[0] = p[1] + [p[2]]
    p.set_lineno(0, p.lineno(1))


def p_gelifs_one(p):
    """
    gelifs : gelif_one
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_gelifs_empty(p):
    """
    gelifs : empty
    
    """
    p[0] = []
    p.set_lineno(0, p.lineno(1))


def p_gelif_one(p):
    """
    gelif_one : GELIF expression COLON gsuite_indent
    
    """
    p[0] = IfStructure(test=p[2], suite=p[4], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_gels(p):
    """
    gels : GELSE COLON gsuite_indent
    """
    p[0] = IfStructure(test=None, suite=p[3], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_gels_empty(p):
    """
    gels : empty
    """
    p[0] = None
    p.set_lineno(0, p.lineno(1))


def p_gen_case_structure(p):
    """
    gen_case_structure : GCASE expression COLON case_list_indent
    """
    p[0] = GenCaseStructure(test=p[2], suites=p[4], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_gen_for_structure(p):
    """
    gen_for_structure : GFOR identifier IN expression COLON gsuite_indent
    
    """
    p[0] = GenForStructure(name=p[2], list=p[4], suite=p[6], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_suite_indent_gen(p):
    """
    gsuite_indent : gsuite
                 | NEWLINE INDENT gsuite DEDENT

    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[3]
    p.set_lineno(0, p.lineno(1))


def p_suite_gen(p):
    """
    gsuite : case_list
          | gen_structure
          | gexpression_stmt
    """
    print ("GSUITE")
    print (p[1])
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_expression_stmt_gen(p):
    """
    gexpression_stmt : gexpression NEWLINE
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_expression_gen(p):
    """
    gexpression : unary_operation
               | binary_operation
               | LPAREN expression RPAREN
               | partial_selection
               | tensor_list
               | function_call
               | pointer
               | identifier
               | const_expression
               | OPERATOR
    """
    if len(p) == 2:
        # print (p[1])
        p[0] = p[1]
    else:
        p[0] = ParenCombine(expr=p[2], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_pointer(p):
    """
    pointer : identifier tensor_list
    
    """
    p[0] = Pointer(name=p[1], tensors=p[2], lineno=p.lineno(1))


def p_context_def(p):
    """
    context_def : CONTEXT identifier inherit COLON declarations_indent
    """
    p[0] = ContextDef(identifier=p[2], inherit=p[3], decls=p[5], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


##Container Definition

def p_container_def(p):
    """
    container_def : CONTAINER identifier inherit parameterdef_list bus_list COLON declarations_indent
    """
    p[0] = ContainerDef(name=p[2], paras=p[4], buses=p[5], inherit=p[3], decls=p[7], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_inherit(p):
    """
    inherit : LBRACE argument_end RBRACE
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_inherit_brace(p):
    """
    inherit : LBRACE RBRACE
    """
    p[0] = None
    p.set_lineno(0, p.lineno(1))


def p_inherit_empty(p):
    """
    inherit : empty
    """
    p[0] = None
    p.set_lineno(0, p.lineno(1))


def p_parameterdef_list(p):
    """
    parameterdef_list : LBRACKET parameterdefs RBRACKET
    """
    p[0] = p[2]
    p.set_lineno(0, p.lineno(1))


def p_parameterdef_list_bracket(p):
    """
    parameterdef_list : LBRACKET RBRACKET
    """
    p[0] = []
    p.set_lineno(0, p.lineno(1))


def p_parameterdef_list_empty(p):
    """
    parameterdef_list : empty
    """
    p[0] = []
    p.set_lineno(0, p.lineno(1))


def p_parameterdefs(p):
    """
    parameterdefs : parameterdefs_begin parameterdef_end
    """
    if p[1]:
        if p[2]:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = p[1]
    else:
        if p[2]:
            p[0] = [p[2]]
        else:
            p[0] = []
    p.set_lineno(0, p.lineno(1))


def p_parameterdefs_one(p):
    """
    parameterdefs : parameterdef_end
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_parameterdefs_begin(p):
    """
    parameterdefs_begin : parameterdefs_begin parameterdef
    """
    if p[1]:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[2]]
    p.set_lineno(0, p.lineno(1))


def p_parameterdefs_begin_one(p):
    """
    parameterdefs_begin : parameterdef
    """
    p[0] = [p[2]]
    p.set_lineno(0, p.lineno(1))


def p_parameterdef_end(p):
    """
    parameterdef_end : parameterdef_one
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_parameterdef_end_empty(p):
    """
    parameterdef_end : empty
    """
    p[0] = None
    p.set_lineno(0, p.lineno(1))


def p_parameterdef(p):
    """
    parameterdef : parameterdef_one COMMA
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_parameterdef_one(p):
    """
    parameterdef_one : type_name parameters
    """
    p[0] = ParameterDef(type=p[1], paras=p[2], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_bus_list(p):
    """
    bus_list : LPAREN buses RPAREN
    """
    p[0] = p[2]
    p.set_lineno(0, p.lineno(1))


def p_bus_list_paren(p):
    """
    bus_list : LPAREN RPAREN
    """
    p[0] = []
    p.set_lineno(0, p.lineno(1))


def p_bus_list_empty(p):
    """
    bus_list : empty
    """
    p[0] = []
    p.set_lineno(0, p.lineno(1))


def p_buses(p):
    """
    buses : buses_begin bus_end
    """
    if p[1]:
        if p[2]:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = p[1]
    else:
        if p[2]:
            p[0] = [p[2]]
        else:
            p[0] = []
    p.set_lineno(0, p.lineno(1))


def p_buses_one(p):
    """
    buses : bus_end
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_buses_begin(p):
    """
    buses_begin : buses_begin bus
    """
    if p[2]:
        p[0] = p[1] + [p[2]]
    p.set_lineno(0, p.lineno(1))


def p_buses_begin_one(p):
    """
    buses_begin : bus
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_bus_end(p):
    """
    bus_end : bus_one
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_bus_end_empty(p):
    """
    bus_end : empty
    """
    p[0] = None
    p.set_lineno(0, p.lineno(1))


def p_bus(p):
    """
    bus : bus_one SEMICOLON
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_bus_one_bus(p):
    """
    bus_one : bus_direction interface_name parameter_list arguments
    """
    p[0] = BusDef(direct=p[1], interface=p[2], paras=p[3], buses=p[4], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_bus_one_port(p):
    """
    bus_one : port_direction typechain_one parameter_list arguments
    """
    p[0] = PortDef(direct=p[1], type=p[2], paras=p[3], ports=p[4], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_interface_name(p):
    """
    interface_name : ID
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_port_direction(p):
    """
    port_direction : INPUT 
                   | IN 
                   | OUTPUT 
                   | OUT 
                   | INOUT
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_declarations_indent(p):
    """
    declarations_indent : declarations
        | NEWLINE INDENT declarations DEDENT
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[3]
    p.set_lineno(0, p.lineno(1))


def p_declarations(p):
    """
    declarations : declarations declaration
    """
    p[0] = p[1] + [p[2]]
    p.set_lineno(0, p.lineno(1))


def p_declarations_one(p):
    """
    declarations : declaration
    
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_declaration(p):
    """
    declaration : variable_def
                | anonymous_function_def
                | instance_def
    
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_structure(p):
    """
    structure : if_structure
        | case_structure    
        | for_structure
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_variable_def(p):
    """
    variable_def : keyword_variable types parameter_list pointer initial_value structure_maybe
    """
    p[0] = VariableDef(pointer=p[4], type=p[2], paras=p[3], init=p[5], decls=p[6], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_keyword_variable(p):
    """
    keyword_variable : VARIABLE 
                     | VAR
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_structure_maybe(p):
    """
    structure_maybe : COLON suite_indent
    """
    p[0] = p[2]
    p.set_lineno(0, p.lineno(1))


def p_structure_maybe_empty(p):
    """
    structure_maybe : empty
    
    """
    p[0] = None
    p.set_lineno(0, p.lineno(1))


def p_anonymous_function_def(p):
    """
    anonymous_function_def : identifier EQUALS suite_indent
    
    """
    p[0] = AnonymousFunctionDef(name=p[1], suite=p[3], lineno=p.lineno(1))


def p_instance_def(p):
    """
    instance_def : keyword_instance identifier identifier parameter_list instance_port_list
    """
    p[0] = InstanceDef(pointer=p[2], container=p[3], paras=p[4], args=p[5], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_keyword_instance(p):
    """
    keyword_instance : INSTANCE 
                     | INS
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_instance_port_list(p):
    """
    instance_port_list : LPAREN instance_ports RPAREN
    """
    p[0] = p[2]
    p.set_lineno(0, p.lineno(1))


def p_instance_port_list_empty(p):
    """
    instance_port_list : empty
    """
    p[0] = []
    p.set_lineno(0, p.lineno(1))


def p_instance_ports(p):
    """
    instance_ports : instance_ports_begin instance_port_end
    """
    if p[2]:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_instance_ports_one(p):
    """
    instance_ports : instance_port_end
    """
    if p[1]:
        p[0] = [p[1]]
    else:
        p[0] = []
    p.set_lineno(0, p.lineno(1))


def p_instance_ports_begin(p):
    """
    instance_ports_begin : instance_ports_begin instance_port
    """
    p[0] = p[1] + [p[2]]
    p.set_lineno(0, p.lineno(1))


def p_instance_ports_begin_one(p):
    """
    instance_ports_begin : instance_port
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_instance_port_end(p):
    """
    instance_port_end : instance_port_one
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_instance_port_end_empty(p):
    """
    instance_port_end : empty
    """
    p[0] = None
    p.set_lineno(0, p.lineno(1))


def p_instance_port(p):
    """
    instance_port : instance_port_one COMMA
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_instance_port_one(p):
    """
    instance_port_one : instance_name
        | input_instance_port
        | output_instance_port
        | inout_instance_port
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_instance_name(p):
    """
    instance_name : expression
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_input_instance_port(p):
    """
    input_instance_port : partial_selection LARROW expression
    """
    p[0] = InputInstancePort(inspart=p[1], expr=p[3], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_output_instance_port(p):
    """
    output_instance_port : partial_selection RARROW partial_selection
    """
    p[0] = OutputInstancePort(inspart=p[1], outpart=p[3], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_inout_instance_port(p):
    """
    inout_instance_port : partial_selection BARROW partial_selection
    
    """
    p[0] = InoutInstancePort(inspart=p[1], outpart=p[3], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_partial_selection(p):
    """
    partial_selection : identifier tensor_select_list
    
    """
    p[0] = PartialSelection(name=p[1], tensorsels=p[2], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_tensor_select_list(p):
    """
    tensor_select_list : LBRACKET expression COLON expression RBRACKET
    """
    p[0] = TensorSelection(expr0=p[2], expr1=p[4], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_tensor_select_list_one(p):
    """
    tensor_select_list : tensor_list
    
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_interface_def(p):
    """
    interface_def : INTERFACE identifier bus_direction parameterdef_list COLON interface_bus_list
    """
    p[0] = InterfaceDef(name=p[2], direct=p[3], paras=p[4], buses=p[5])
    p.set_lineno(0, p.lineno(1))


def p_bus_direction(p):
    """
    bus_direction : MASTER 
                  | SLAVE
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_interface_bus_list(p):
    """
    interface_bus_list : interface_buses interface_bus
    """
    p[0] = p[1] + [p[2]]
    p.set_lineno(0, p.lineno(1))


def p_interface_buses(p):
    """
    interface_buses : interface_bus
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_interface_bus(p):
    """
    interface_bus : bus_one
    
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_parameter_list(p):
    """
    parameter_list : LBRACKET parameters RBRACKET
    """
    p[0] = p[2]
    p.set_lineno(0, p.lineno(1))


def p_parameter_list_empty(p):
    """
    parameter_list : empty
    """
    p[0] = []
    p.set_lineno(0, p.lineno(1))


def p_parameters(p):
    """
    parameters : parameters_begin parameter_end
    """
    if p[2]:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_parameters_one(p):
    """
    parameters : parameter_end
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_parameters_begin(p):
    """
    parameters_begin : parameters_begin parameter
    """
    p[0] = p[1] + [p[2]]
    p.set_lineno(0, p.lineno(1))


def p_parameters_begin_one(p):
    """
    parameters_begin : parameter
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_parameter_end(p):
    """
    parameter_end : parameter_one
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_parameter_end_empty(p):
    """
    parameter_end : empty
    """
    p[0] = None
    p.set_lineno(0, p.lineno(1))


def p_parameter(p):
    """
    parameter : parameter_one COMMA
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_parameter_one(p):
    """
    parameter_one : identifier tensor_list LARROW expression
    """
    p[0] = Parameter(name=p[1], tensors=p[2], expr=p[4], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_parameter_one_no_expr(p):
    """
    parameter_one : identifier tensor_list
    """
    p[0] = Parameter(name=p[1], tensors=p[2], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_parameter_number(p):
    """
    parameter_one : expression
    """
    p[0] = Parameter(name=p[1], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_tensor_list(p):
    """
    tensor_list : LBRACKET expressions RBRACKET
    """
    p[0] = TensorList(tensors=p[2], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_tensor_list_empty(p):
    """
    tensor_list : empty
    """
    p[0] = []
    p.set_lineno(0, p.lineno(1))


def p_if_structure(p):
    """
    if_structure : IF expression COLON suite_indent elifs els
    """
    p[0] = IfStructure(test=p[2], suite=p[4], elifs=p[5], els=p[6], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_elifs(p):
    """
    elifs : elifs elif_one
    """
    p[0] = p[1] + [p[2]]
    p.set_lineno(0, p.lineno(1))


def p_elifs_one(p):
    """
    elifs : elif_one
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_elifs_empty(p):
    """
    elifs : empty
    
    """
    p[0] = []
    p.set_lineno(0, p.lineno(1))


def p_elif_one(p):
    """
    elif_one : ELIF expression COLON suite_indent
    
    """
    p[0] = IfStructure(test=p[2], suite=p[4], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_els(p):
    """
    els : ELSE COLON suite_indent
    """
    p[0] = IfStructure(test=None, suite=p[3], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_els_empty(p):
    """
    els : empty
    """
    p[0] = None
    p.set_lineno(0, p.lineno(1))


def p_case_structure(p):
    """
    case_structure : CASE expression COLON case_list_indent
    """
    p[0] = CaseStructure(test=p[2], suites=p[4], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_for_structure(p):
    """
    for_structure : FOR identifier IN expression COLON suite_indent
    
    """
    p[0] = ForStructure(name=p[2], list=p[4], suite=p[6], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_suite_indent(p):
    """
    suite_indent : suite
                 | NEWLINE INDENT suite DEDENT
    
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[3]
    p.set_lineno(0, p.lineno(1))


def p_suite(p):
    """
    suite : structure
          | expression_stmt
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_case_list_indent(p):
    """
    case_list_indent : case_list
                     | NEWLINE INDENT case_list DEDENT    
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[3]
    p.set_lineno(0, p.lineno(1))


def p_case_list(p):
    """
    case_list : case_list case_entry
              | case_entry
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        if p[1]:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[2]]
    p.set_lineno(0, p.lineno(1))


def p_case_entry(p):
    """
    case_entry : expression COLON suite_indent
    """
    p[0] = Case(test=p[1], suite=p[3], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_case_entry_gen(p):
    """
    case_entry : gen_structure
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


# def p_expression_indent(p):
#     """
#     expression_indent : expression_stmt
#                       | NEWLINE INDENT expression_stmt DEDENT
#     """
#     if len(p) == 2:
#         p[0] = p[1]
#     else:
#         p[0] = p[3]
#     p.set_lineno(0, p.lineno(1))

def p_expression_stmt(p):
    """
    expression_stmt : expression NEWLINE
                    | expression
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_expressions(p):
    """
    expressions : expressions_begin expression_end
    """
    p[0] = p[1] + p[2]
    p.set_lineno(0, p.lineno(1))


def p_expressions_one(p):
    """
    expressions : expression_end
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_expressions_begin(p):
    """
    expressions_begin : expressions_begin expression_comma
    """
    p[0] = p[1] + p[2]
    p.set_lineno(0, p.lineno(1))


def p_expressions_begin_one(p):
    """
    expressions_begin : expression_comma
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_expression_end(p):
    """
    expression_end : expression
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_expression_comma(p):
    """
    expression_comma : expression COMMA
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_initial_value(p):
    """
    initial_value : LARROW expression
    
    """
    p[0] = p[2]
    p.set_lineno(0, p.lineno(1))


def p_expression(p):
    """
    expression : unary_operation
               | binary_operation
               | LPAREN expression RPAREN
               | partial_selection
               | tensor_list
               | function_call
               | pointer
               | identifier
               | const_expression
               | operator_decl
    """
    if len(p) == 2:
        # print (p[1])
        p[0] = p[1]
    else:
        p[0] = ParenCombine(expr=p[2], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_operator_decl(p):
    """
    operator_decl : OPERATOR
    """
    p[0] = Operator(p[1], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_unary_operation(p):
    """
    unary_operation : OPERATOR expression
    """
    p[0] = UnaryOperation(op=p[1], expr=p[2], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_binary_operation(p):
    """
    binary_operation : expression OPERATOR expression
    
    """
    p[0] = BinaryOperation(expr0=p[1], op=p[2], expr1=p[3], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_function_call(p):
    """
    function_call : identifier instance_port_list
    
    """
    p[0] = FunctionCall(name=p[1], args=p[2], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_const_expression(p):
    """
    const_expression : int_number
        | float_number
        | string_literal
    
    """
    p[0] = p[1]
    p.set_lineno(0, p.lineno(1))


def p_int_number(p):
    """
    int_number : INTNUMBER_DEC
        | SIGNED_INTNUMBER_DEC
        | INTNUMBER_BIN
        | SIGNED_INTNUMBER_BIN
        | INTNUMBER_OCT
        | SIGNED_INTNUMBER_OCT
        | INTNUMBER_HEX
        | SIGNED_INTNUMBER_HEX
    
    """
    p[0] = IntNumber(value=p[1], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_string_literal(p):
    """
    string_literal : STRING_LITERAL
    
    """
    p[0] = StringLiteral(value=p[1], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_float_number(p):
    """
    float_number : FLOATNUMBER
    
    """
    p[0] = FloatNumber(value=p[1], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_identifier(p):
    """
    identifier : scopes ID
               | ID
    """
    if len(p) == 2:
        p[0] = Identifier(name=p[1], lineno=p.lineno(1))
    else:
        p[0] = Identifier(name=p[2], scopes=p[1], lineno=p.lineno(1))
    p.set_lineno(0, p.lineno(1))


def p_scopes(p):
    """
    scopes : scopes scope
           | scope
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[2]


def p_scope(p):
    """
    scope : ID DOT
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_scope_pointer(p):
    """
    scope : pointer DOT
    """
    p[0] = [p[1]]
    p.set_lineno(0, p.lineno(1))


def p_empty(p):
    """
    empty : 
    """
    pass


def p_error(p):
    raise TypeError("unknown text %r at %r" % (p.value, p.lineno))


class SparrowParser(object):
    'Sparrow Parser'

    def __init__(self):
        self.lexer = IndentLexer()
        self.parser = yacc.yacc(start="file_input_end")

    def parse(self, code):
        self.lexer.input(code)
        result = self.parser.parse(lexer=self.lexer)
        return result
