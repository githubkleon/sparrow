from ply import *

class Node(object):
    source = None
    drains = []
    traced = False

class Package(Node):
    def __init__(self, module, lineno=0):
        self.module = module
        self.lineno = lineno

    def __repr__(self):
        return "Package{%r}" % (self.module)


class Module(Node):
    def __init__(self, stmts=[], lineno=0):
        self.stmts = stmts
        self.lineno = lineno

    def __repr__(self):
        return "Module{%r}" % (self.stmts)


# FunctionDef(Identifier name, ArgumentList args, Structure suite)
class FunctionDef(Node):
    def __init__(self, name, args=[], suite=None, lineno=0):
        self.name = name
        self.args = args
        self.cons = None
        self.suite = suite
        self.lineno = lineno

    def __repr__(self):
        return "FunctionDef{%r, args=%r, suite=%r, cons=%r}" % (
            self.name, self.args, self.suite, self.cons)


# FunctionCons(Identifier name, TypeChainList inputs, TypeChainList outputs)
class FunctionCons(Node):
    def __init__(self, name, cons, lineno=0):
        self.name = name
        self.cons = cons
        self.lineno = lineno

    def __repr__(self):
        return "FunctionCons{%r, cons=%r}" % (
            self.name, self.cons)


class Cons(Node):
    def __init__(self, inputs, outputs, lineno=0):
        self.inputs = inputs
        self.outputs = outputs
        self.lineno = lineno

    def __repr__(self):
        return "Cons{inputs=%r, outputs=%r}" % (self.inputs, self.outputs)

class Argument(Node):
    def __init__(self, name, lineno=0):
        self.name = name
        self.type = None
        self.lineno = lineno

    def __repr__(self):
        return "Argument{%r}" % (
            self.name)

# OperatorDef(Operator name, ArgumentList args, Structure suite)
class OperatorDef(Node):
    def __init__(self, name, args=[], suite=None, lineno=0):
        self.name = name
        self.args = args
        self.suite = suite
        self.lineno = lineno

    def __repr__(self):
        return "OperatorDef{%r, args=%r, suite=%r}" % (
            self.name, self.args, self.suite)

class Operator(Node):
    def __init__(self, op, suite=None, lineno=0):
        self.op = op
        self.lineno = lineno

    def __repr__(self):
        return "Operator{%r}" % (self.op)

# OperatorCons(Operator ops, TypeChainList inputs, TypeChainList outputs)
class OperatorCons(Node):
    def __init__(self, ops, cons, lineno=0):
        self.ops = ops
        self.cons = cons
        self.lineno = lineno

    def __repr__(self):
        return "OperatorCons{%r, cons=%r}" % (
            self.ops, self.cons)


# OperatorInfix(Operator [], Infix infix, Number prec)
class OperatorInfix(Node):
    def __init__(self, ops, infix=None, prec=None, lineno=0):
        self.ops = ops
        self.infix = infix
        self.prec = prec
        self.lineno = lineno

    def __repr__(self):
        return "OperatorInfix{%r, infix=%r, prec=%r}" % (
            self.ops, self.infix, self.prec)


class TypeDef(Node):
    def __init__(self, name, constructors=[], lineno=0):
        self.name = name
        self.constructors = constructors
        self.lineno = lineno

    def __repr__(self):
        return "TypeDef{%r, \n%r}" % (self.name, self.constructors)


class Constructor(Node):
    def __init__(self, name, elements=[], lineno=0):
        self.name = name
        self.elements = elements
        self.lineno = lineno

    def __repr__(self):
        return "Constructor{%r, \n%r}" % (self.name, self.elements)


class ConstructorParameter(Node):
    def __init__(self, type, identifier, lineno=0):
        self.type = type
        self.identifier = identifier
        self.lineno = lineno

    def __repr__(self):
        return "ConstructorParameter{%r\n %r\n}" % (self.identifier, self.type)


class Element(Node):
    def __init__(self, type, varname, lineno=0):
        self.type = type
        self.varname = varname
        self.lineno = lineno

    def __repr__(self):
        return "Element{%r, \n%r}" % (self.type, self.varname)


class ContextDef(Node):
    def __init__(self, identifier, inherit=[], decls=[], lineno=0):
        self.identifier = identifier
        self.inherit = inherit
        self.decls = decls
        self.lineno = lineno

    def __repr__(self):
        return "ContextDef{%r, \ninherit=%r, \ndecls=%r}" % (
            self.identifier, self.inherit, self.decls)

class ContainerDef(Node):
    def __init__(self, name, paras=[], buses=[], inherit=None, decls=[], lineno=0):
        self.name = name
        self.paras = paras
        self.buses = buses
        self.inherit = inherit
        self.decls = decls
        self.lineno = lineno
        self.clock = None
        self.reset = None

    def __repr__(self):
        return "ContainerDef{%r, \nclock=%r, \nreset=%r, \nparas=%r, \nbuses=%r, \ninherit=%r, \ndecls=%r}" % (
            self.name, self.clock, self.reset, self.paras, self.buses, self.inherit, self.decls)


class InterfaceDef(Node):
    def __init__(self, name, direct, paras=[], buses=[], lineno=0):
        self.name = name
        self.paras = paras
        self.buses = buses
        self.lineno = lineno

    def __repr__(self):
        return "InterfaceDef{%r, paras=%r, buses=%r}" % (
            self.name, self.paras, self.buses)


class Identifier(Node):
    def __init__(self, name, scopes=[], lineno=0):
        self.name = name
        self.scopes = scopes
        self.lineno = lineno

    def __repr__(self):
        if (self.scopes):
            return "Identifier{%r, \n%r}" % (self.scopes, self.name)
        else:
            return "Identifier{%r}" % (self.name)

    def __eq__(self, other):
        return self.name == other.name


class Pointer(Node):
    def __init__(self, name, tensors=[], lineno=0):
        self.name = name
        self.tensors = tensors
        self.lineno = lineno

    def __repr__(self):
        return "Pointer{%r, \ntensors=%r}" % (self.name, self.tensors)

    def __eq__(self, other):
        return self.name == other.name


class ParameterDef(Node):
    def __init__(self, type, paras=[], lineno=0):
        self.type = type
        self.paras = paras
        self.lineno = lineno

    def __repr__(self):
        return "ParameterDef{%r, \n%r}" % (self.type, self.paras)


class BusDef(Node):
    def __init__(self, direct, interface, paras=[], buses=[], name=None, lineno=0):
        self.direct = direct
        self.interface = interface
        self.paras = paras
        self.buses = buses
        self.name = name
        self.lineno = lineno

    def __repr__(self):
        return "BusDef{%r, \n%r, \n%r, \n%r, \n%r}" % (self.direct, self.interface, self.paras, self.buses, self.name)


class PortDef(Node):
    def __init__(self, direct, type, paras=[], ports=[], name=None, lineno=0):
        self.direct = direct
        self.type = type
        self.paras = paras
        self.ports = ports
        self.name = name
        self.var = False
        self.lineno = lineno

    def __repr__(self):
        return "PortDef{%r, \n%r, \n%r, \n%r, \n%r, \n%r}" % (self.name, self.direct, self.type, self.paras, self.ports, self.source)


class VariableDef(Node):
    def __init__(self, pointer, type, paras=[], init=None, decls=None, lineno=0):
        self.pointer = pointer
        self.type = type
        self.paras = paras
        self.init = init
        self.decls = decls
        self.lineno = lineno

    def __repr__(self):
        return "VariableDef{%r, \n%r, \n%r, \n%r, \n%r}" % (self.pointer, self.type, self.paras, self.init, self.decls)


class AnonymousFunctionDef(Node):
    def __init__(self, name, suite, returntype=None, lineno=0):
        self.name = name
        self.suite = suite
        self.lineno = lineno
        self.returntype = returntype

    def __repr__(self):
        return "AnonymousFunctionDef{%r, \n%r, \n%r, \nsource=%r}" % (self.name, self.suite, self.returntype, self.source)


class Parameter(Node):
    def __init__(self, name, num=False, tensors=[], expr=None, lineno=0):
        self.name = name
        self.num = num
        self.tensors = tensors
        self.expr = expr
        self.lineno = lineno

    def __repr__(self):
        return "Parameter{%r, \n%r, \n%r, \n%r}" % (self.name, self.num, self.tensors, self.expr)


class IfStructure(Node):
    def __init__(self, test, suite, elifs=[], els=None, lineno=0):
        self.test = test
        self.suite = suite
        self.elifs = elifs
        self.els = els
        self.lineno = lineno

    def __repr__(self):
        return "IfStructure{%r,%r,%r,%r}" % (self.test, self.suite, self.elifs, self.els)


class CaseStructure(Node):
    def __init__(self, test, suites, lineno=0):
        self.test = test
        self.suites = suites
        self.lineno = lineno

    def __repr__(self):
        return "CaseStructure{%r, \n%r}" % (self.test, self.suites)


class Case(Node):
    def __init__(self, test, suite, lineno=0):
        self.test = test
        self.suite = suite
        self.lineno = lineno

    def __repr__(self):
        return "Case{%r, \n%r}" % (self.test, self.suite)


# ForStructure(ForList iter, Structure suite)
class ForStructure(Node):
    def __init__(self, name, list=[], suite=None, lineno=0):
        self.name = name
        self.list = list
        self.suite = suite
        self.lineno = lineno

    def __repr__(self):
        return "ForStructure{%r, \n%r, \n%r}" % (self.name, self.list, self.suite)


class GenIfStructure(Node):
    def __init__(self, test, suite, elifs=[], els=None, lineno=0):
        self.test = test
        self.suite = suite
        self.elifs = elifs
        self.els = els
        self.lineno = lineno

    def __repr__(self):
        return "GenIfStructure{%r,%r,%r,%r}" % (self.test, self.suite, self.elifs, self.els)


class GenCaseStructure(Node):
    def __init__(self, test, suites, lineno=0):
        self.test = test
        self.suites = suites
        self.lineno = lineno

    def __repr__(self):
        return "GenCaseStructure{%r, \n%r}" % (self.test, self.suites)


# ForStructure(ForList iter, Structure suite)
class GenForStructure(Node):
    def __init__(self, name, list=[], suite=None, lineno=0):
        self.name = name
        self.list = list
        self.suite = suite
        self.lineno = lineno

    def __repr__(self):
        return "GenForStructure{%r, \n%r, \n%r}" % (self.name, self.list, self.suite)


class UnaryOperation(Node):
    def __init__(self, op, expr, lineno=0):
        self.op = op
        self.expr = expr
        self.lineno = lineno

    def __repr__(self):
        return "UnaryOp{%r, \n%r}" % (self.op, self.expr)


class BinaryOperation(Node):
    def __init__(self, expr0, op, expr1, lineno=0):
        self.expr0 = expr0
        self.op = op
        self.expr1 = expr1
        self.lineno = lineno

    def __repr__(self):
        return "BinaryOp{%r, \n%r, \n%r}" % (self.expr0, self.op, self.expr1)


class ParenCombine(Node):
    def __init__(self, expr, lineno=0):
        self.expr = expr
        self.lineno = lineno

    def __repr__(self):
        return "ParenCombine{%r}" % (self.expr)


# FunctionCall(Identifier name, ArgumentList args)
class FunctionCall(Node):
    def __init__(self, name, args, lineno=0):
        self.name = name
        self.args = args
        self.returntype = None
        self.lineno = lineno

    def __repr__(self):
        return "FunctionCall{name=%r, args=%r, source=%r}" % (self.name, self.args, self.source)


# InstanceDef(Pointer name, Identifier container, ParameterList paras, ArgumentList args)
class InstanceDef(Node):
    def __init__(self, pointer, container, paras, args, lineno=0):
        self.pointer = pointer
        self.container = container
        self.paras = paras
        self.args = args
        self.lineno = lineno

    def __repr__(self):
        return "InstanceDef{%r, \n%r, \n%r, \n%r}" % (self.pointer, self.container, self.paras, self.args)


class InputInstancePort(Node):
    def __init__(self, inspart, expr, lineno=0):
        self.inspart = inspart
        self.expr = expr
        self.lineno = lineno

    def __repr__(self):
        return "InputInstancePort{%r, \n%r}" % (self.inspart, self.expr)


class OutputInstancePort(Node):
    def __init__(self, inspart, outpart, lineno=0):
        self.inspart = inspart
        self.outpart = outpart
        self.lineno = lineno

    def __repr__(self):
        return "OutputInstancePort{%r, \n%r}" % (self.inspart, self.outpart)


class InoutInstancePort(Node):
    def __init__(self, inspart, outpart, lineno=0):
        self.inspart = inspart
        self.outpart = outpart
        self.lineno = lineno

    def __repr__(self):
        return "InoutInstancePort{%r, \n%r}" % (self.inspart, self.outpart)


# PartialSelection(Identifier name, TensorSelectList tensorsels)
class PartialSelection(Node):
    def __init__(self, name, tensorsels, lineno=0):
        self.name = name
        self.tensorsels = tensorsels
        self.lineno = lineno

    def __repr__(self):
        return "PartialSelection{%r, \n%r}" % (self.name, self.tensorsels)


class TensorSelection(Node):
    def __init__(self, expr0, expr1, lineno=0):
        self.expr0 = expr0
        self.expr1 = expr1
        self.lineno = lineno

    def __repr__(self):
        return "TensorSelection{%r, \n%r}" % (self.expr0, self.expr1)


class TensorList(Node):
    def __init__(self, tensors=[], lineno=0):
        self.tensors = tensors
        self.lineno = lineno

    def __repr__(self):
        return "TensorList{%r}" % (self.tensors)


class IntNumber(Node):
    def __init__(self, value, lineno=0):
        self.value = value
        self.lineno = lineno

    def __repr__(self):
        return "IntNumber{%r}" % (self.value)


class FloatNumber(Node):
    def __init__(self, value, lineno=0):
        self.value = value
        self.lineno = lineno

    def __repr__(self):
        return "FloatNumber{%r}" % (self.value)


class StringLiteral(Node):
    def __init__(self, value, lineno=0):
        self.value = value
        self.lineno = lineno

    def __repr__(self):
        return "StringLiteral{%r}" % (self.value)


# ImportDecl(Identifier package, Identifier scope, ArgumentList args, Bool nothiding)
class ImportDecl(Node):
    def __init__(self, package, scope, args, nothiding, lineno=0):
        self.package = package
        self.scope = scope
        self.args = args
        self.nothiding = nothiding
        self.lineno = lineno

    def __repr__(self):
        return "ImportDecl{%r, \n%r, \n%r, \n%r}" % (self.package, self.scope, self.args, self.nothiding)


# RegisterDecl(FileType filetype, Identifier package,  Identifier scope, ArgumentList args, Bool Hiding)
class RegisterDecl(Node):
    def __init__(self, filetype, package, scope=None, args=[], nothiding=False, lineno=0):
        self.filetype = filetype
        self.package = package
        self.scope = scope
        self.args = args
        self.nothiding = nothiding
        self.lineno = lineno

    def __repr__(self):
        return "RegisterDecl{%r, \n%r, \n%r, \n%r, \n%r}" % (
        self.filetype, self.package, self.scope, self.args, self.nothiding)


# TypeRename(Identifier name, Identifier type)
class TypeRename(Node):
    def __init__(self, name, type, lineno=0):
        self.name = name
        self.type = type
        self.lineno = lineno

    def __repr__(self):
        return "TypeRename{%r, \n%r}" % (self.name, self.type)
