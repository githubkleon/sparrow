import pyverilog.vparser.ast as vast
from backend.pySparrow.spParser.ast import *
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
import backend.pySparrow.spOptimizer.astOperator as astOp
import splog as log

BasicWords = ['UInt', 'SInt', 'Bit']

op_power = '**'
op_times = '*'
op_div = '/'
op_mod = '%'
op_plus = '+'
op_minus = '-'
op_sll = '<<'
op_srl = '>>'
op_sla = '<<<'
op_sra = '>>>'
op_lt = '<'
op_gt = '>'
op_le = '<='
op_ge = '>='
op_eq = '=='
op_ne = '!='
op_eql = '==='
op_nel = '!=='
op_and = '&'
op_xor = '^'
op_xnor = '~^'
op_or = '|'
op_land = '&&'
op_lor = '||'
op_not = '~'
op_lnot = '!'
op_nand = '~&'
op_nor = '~|'

class SparrowConvertor:
    def __init__(self, tree, language="Verilog"):
        self.tree = tree
        self.language = language
        self.verilogast = None
        self.ast = self.tree.handler.ast

    def convert(self):
        log.spInfo(9, "Converting...")
        log.spInfo(8, "Sparrow AST Before Conversion:", log.genAST(self.ast))
        self.verilogast = self.genSource(self.ast)
        if (log.LOG_PRIORITY < 8):
            self.verilogast.show()
        self.genVerilogCode()

    def genVerilogCode(self):
        log.spInfo(9, "Generating " + self.language + "...")
        codegen = ASTCodeGenerator()
        self.tree.result = codegen.visit(self.verilogast)
        log.spInfo(9, self.tree.result)

    def genSource(self, package):
        return vast.Source(name='', description=self.genDescription(package.module))

    def genDescription(self, module):
        return vast.Description(definitions=self.genModules(module))

    def genModules(self, module):
        containers = self.getContainersFromStmts(module.stmts)
        modules = ()
        for con in containers:
            modules += (self.genModule(con),)
        return modules

    def genModule(self, container):
        return vast.ModuleDef(name=container.name.name,
                              paramlist=vast.Paramlist(
                                  params=self.genParamList(container.paras)),
                              portlist= self.genPortList(container.buses, container),
                              items=self.genModuleItems(container.decls),
                              lineno=container.lineno)

    def genClockReset(self, container):
        width = self.genWidth(1)
        if astOp.containSequentialLogic(container):
            return (vast.Ioport(vast.Input(name="clk", width=width)),) + (vast.Ioport(vast.Input(name="rst", width=width)),)
        else:
            return ()

    def genParamList(self, paras):
        paraList = ()
        for para in paras:
            width = self.genWidth(self.getTypeWidth(para.type))
            for elem in para.paras:
                paraList += (vast.Decl(tuple([vast.Parameter(
                    name=elem.name.name, value=vast.IntConst("1"), width=width)])),)
        return paraList

    def genPortList(self, ports, container):
        portList = ()
        width = None

        portList += self.genClockReset(container)

        for port in ports:
            # print (port.type)
            width = self.genWidth(self.getTypeWidth(port.type))

            ioport = None
            # print (port.direct)
            if port.direct == "input" or port.direct == "in":
                ioport = vast.Ioport(vast.Input(name=port.name.name, width=width))
            elif port.direct == "output" or port.direct == "out":
                ioport = vast.Ioport(vast.Output(name=port.name.name, width=width))
            elif port.direct == "inout":
                ioport = vast.Ioport(vast.Inout(name=port.name.name, width=width))
            portList += (ioport,)

        return vast.Portlist(ports=portList)

    def getTypeWidth(self, type):
        if len(type) == 1:
            type = type[0]
            if type.name.name in BasicWords:
                if type.tensors.tensors:
                    if isinstance(type.tensors.tensors[0], IntNumber):
                        return int(type.tensors.tensors[0].value)
                    elif isinstance(type.tensors.tensors[0], Identifier):
                        return self.genIdentifier(type.tensors.tensors[0])
                    else:
                        return self.genExpression(type.tensors.tensors[0])
            return 1

    def genWidth(self, msb):
        if isinstance(msb, int):
            if msb == 1:
                return None
            else:
                return vast.Width(vast.IntConst(str(msb-1)), vast.IntConst('0'))
        else:
            return vast.Width(vast.Minus(msb,vast.IntConst(1)), vast.IntConst('0'))

    def genModuleItems(self, decls):
        localparamdecls = ()
        wiredecls = ()
        regdecls = ()
        decllist = ()
        functionlist = ()
        funcs = astOp.getUsedFunctionList(self.ast)
        # print("LEN of USED FUNCTION:", len(funcs))
        # print(funcs)
        # print("BEFOREAST")
        # print(self.ast)
        for func in funcs:
            if astOp.onlyOutput(func):
                log.spInfo (0, "ONLY Output: %r"%func)
                astOp.convertFunc2AnonymousFunc(func, self.ast)
                log.spInfo (0, "AFTER CONVERSION: %r"%func.cons.cons.outputs[0])

                decls.append(AnonymousFunctionDef(func.name, func.suite, func.cons.cons.outputs[0]))
            else:
                functionlist += (self.genFunctionDef(func),)
        log.spInfo(0, "FUNCTIONLIST")
        for func in functionlist:
            func.show()
        # print("AFTERAST")
        # print(self.ast)

        for decl in decls:
            if isinstance(decl, VariableDef):
                variable = self.genVariable(decl)
                localparamdecls += variable[0]
                decllist += variable[1]
                regdecls += variable[2]
            elif isinstance(decl, AnonymousFunctionDef):
                if isinstance(decl.suite, IfStructure) or isinstance(decl.suite, CaseStructure):
                    regdecls += (self.genRegDecl(decl.name.name, self.genWidth(self.getTypeWidth(decl.returntype))),)
                    decllist += (self.genAlwaysAtStar(decl),)
                else:
                    log.spInfo(0, "SOME THING WRONG", decl)
                    if decl.traced == True:
                        wiredecls += (vast.Decl(tuple([self.genWire(decl.name.name, self.getTypeWidth(decl.returntype))])),)
                        decllist += (self.genAssign(decl),)

        return localparamdecls + wiredecls + regdecls + decllist + functionlist

    def genFunctionDef(self, func):
        # print ("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        # print (func)
        return vast.Function(func.name.name, self.genWidth(self.getTypeWidth(func.cons.cons.outputs[0])),
                             self.genFunctionPort(func) + (self.genSuite(func.suite, func.name, nonblock=False),))

    def genFunctionPort(self, func):
        ports = ()
        for arg in func.args:
            ports += (vast.Decl(tuple([self.genInputPort(arg.name, self.getTypeWidth(arg.type))])),)
        return ports

    def genWire(self, name, width):
        if width == 1:
            return vast.Wire(name=name)
        else:
            return vast.Wire(name=name, width=self.genWidth(width))

    def genInputPort(self, name, width):
        if width == 1:
            return vast.Input(name=name)
        else:
            return vast.Input(name=name, width=self.genWidth(width))

    def genAlwaysAtStar(self, decl):
        return vast.Always(sens_list=vast.SensList((vast.Sens(
            None, 'all'),)),
            statement=vast.Block(statements=(self.genSuite(decl.suite, decl.name, False),)))

    def genAssign(self, decl):
        return vast.Assign(
            vast.Lvalue(vast.Identifier(decl.name.name)),
            vast.Rvalue(self.genExpression(decl.suite)))

    def genVariable(self, variable):
        localparamdecls = ()
        alwaysblocks = ()
        isFSM, typedef, width = self.isTypeFSM(variable.type[0])
        if isFSM:
            localparamdecls += (self.genFSMlocalparam(typedef),)
        alwaysblocks += (self.genAlwaysBlock(variable),)
        regdecls = (self.genRegDecl(variable.pointer.name.name, width),)
        return localparamdecls, alwaysblocks, regdecls

    def genRegDecl(self, name, width):
        return vast.Decl(tuple([vast.Reg(name=name, width=width)]))

    def genAlwaysBlock(self, variable):
        return vast.Always(sens_list=vast.SensList((vast.Sens(
            sig=vast.Identifier('clk'),type='posedge'),)),
            statement=vast.Block(statements=(self.genVarSuite(variable),)))

    def genVarSuite(self, var):
        return vast.IfStatement(
            cond=vast.Identifier('rst'),
            true_statement=vast.Block(
                statements=(self.genNonblockingSubstitution(var.pointer.name, var.init),)),
            false_statement=self.genSuite(var.decls, var.pointer.name))

    def genCaseStatement(self, stmt, name, nonblock=True):
        caselist = ()
        for suite in stmt.suites:
            log.spInfo(0, "Case suites:", suite)
            if isinstance(suite.test, Identifier):
                # print (suite.test.name)
                if suite.test.name == "_":
                    suite.test.name = "default"
            caselist += (vast.Case(cond=(self.genExpression(suite.test),), statement=self.genSuite(suite.suite, name, nonblock)),)
        return vast.CaseStatement(comp=self.genExpression(stmt.test), caselist=caselist)

    def genIfStatement(self, stmt, name, nonblock=True):
        return vast.IfStatement(cond=self.genExpression(stmt.test),
                                true_statement=self.genSuite(stmt.suite, name, nonblock),
                                false_statement=self.genElifsels(stmt, 0, name, nonblock))

    def genElifsels(self, stmt, state, name, nonblock=True):
        if state == len(stmt.elifs):
            if stmt.els:
                return self.genSuite(stmt.els.suite, name, nonblock)
            else:
                return self.genNonblockingSubstitution(name, name)
        else:
            return vast.IfStatement(
                cond=self.genExpression(stmt.elifs[state].test),
                true_statement=self.genSuite(stmt.elifs[state].suite, name, nonblock),
                false_statement=self.genElifsels(stmt, state + 1, name, nonblock))

    def genSuite(self, suite, name, nonblock=True):
        stmt = None
        if isinstance(suite, IfStructure):
            stmt = self.genIfStatement(suite, name, nonblock)
        elif isinstance(suite, CaseStructure):
            stmt = self.genCaseStatement(suite, name, nonblock)
        else:
            log.spInfo(0, "Not If or Case Suite:", suite)
            if nonblock:
                stmt = self.genNonblockingSubstitution(name, suite)
            else:
                stmt = self.genblockingSubstitution(name, suite)
        return vast.Block((stmt,))

    def genNonblockingSubstitution(self, name, value):
        return vast.NonblockingSubstitution(
                    left=self.genIdentifier(name),
                    right=self.genExpression(value))

    def genblockingSubstitution(self, name, value):
        return vast.BlockingSubstitution(
            left=self.genIdentifier(name),
            right=self.genExpression(value))

    def genExpression(self, expr):
        if isinstance(expr, Identifier):
            return vast.Identifier(expr.name)
        elif isinstance(expr, ParenCombine):
            return self.genExpression(expr.expr)
        elif isinstance(expr, BinaryOperation):
            if expr.op == op_power:
                return vast.Power(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_times:
                return vast.Times(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_div:
                return vast.Divide(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_mod:
                return vast.Mod(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_plus:
                return vast.Plus(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_minus:
                return vast.Minus(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_sll:
                return vast.Sll(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_srl:
                return vast.Srl(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_sla:
                return vast.Sll(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_sra:
                return vast.Sra(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_lt:
                return vast.LessThan(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_gt:
                return vast.GreaterThan(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_le:
                return vast.LessEq(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_ge:
                return vast.GreaterEq(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_eq:
                return vast.Eq(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_ne:
                return vast.NotEq(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_eql:
                return vast.Eql(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_nel:
                return vast.NotEql(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_and:
                return vast.And(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_xor:
                return vast.Xor(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_xnor:
                return vast.Xnor(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_or:
                return vast.Or(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_land:
                return vast.Land(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            elif expr.op == op_lor:
                return vast.Lor(self.genExpression(expr.expr0), self.genExpression(expr.expr1))
            else:
                pass # genBinaryFunction

        elif isinstance(expr, UnaryOperation):
            if expr.op == op_minus:
                return vast.Uminus(self.genExpression(expr.expr))
            elif expr.op == op_plus:
                return vast.Uplus(self.genExpression(expr.expr))
            elif expr.op == op_lnot:
                return vast.Ulnot(self.genExpression(expr.expr))
            elif expr.op == op_not:
                return vast.Unot(self.genExpression(expr.expr))
            elif expr.op == op_and:
                return vast.Uand(self.genExpression(expr.expr))
            elif expr.op == op_nand:
                return vast.Unand(self.genExpression(expr.expr))
            elif expr.op == op_nor:
                return vast.Unor(self.genExpression(expr.expr))
            elif expr.op == op_or:
                return vast.Uor(self.genExpression(expr.expr))
            elif expr.op == op_xnor:
                return vast.Uxnor(self.genExpression(expr.expr))
            elif expr.op == op_xor:
                return vast.Uxor(self.genExpression(expr.expr))
            else:
                pass # genUnaryFunction
        elif isinstance(expr, IntNumber):
            return vast.IntConst(expr.value)
        elif isinstance(expr, FloatNumber):
            return vast.FloatConst(expr.value)
        elif isinstance(expr, StringLiteral):
            return vast.String(expr.value)
        elif isinstance(expr, FunctionCall):
            return self.genFunctionCall(expr)
        elif isinstance(expr, Pointer):
            return self.genPointer(expr)
        elif isinstance(expr, PartialSelection):
            return self.genPartialSelection(expr)
        else:
            log.spInfo(0, "Unhandled AST Node:", expr)
            return vast.Identifier("Unhandled")


    def genPartialSelection(self, expr):
        return vast.Partselect(vast.Identifier(expr.name.name),
                               self.genExpression(expr.tensorsels.expr0),
                               self.genExpression(expr.tensorsels.expr1))


    def genFunctionCall(self, func):
        args = ()
        for arg in func.args:
            args += (self.genExpression(arg),)
        return vast.FunctionCall(vast.Identifier(func.name.name), args)

    def genPointer(self, pt):
        return vast.Pointer(vast.Identifier(pt.name.name), self.genExpression(pt.tensors.tensors[0]))

    def genIdentifier(self, id):
        return vast.Identifier(name=id.name)

    def isTypeFSM(self, type):
        if type.name.name in BasicWords:
            return False, None, self.genWidth(self.getTypeWidth([type]))
        typedef = astOp.findTypeDef(type, self.ast)
        isFSM = True
        for constructor in typedef.constructors:
            if constructor.elements:
                isFSM = False
                break
        return isFSM, typedef, self.genWidth(len(typedef.constructors))

    def genFSMlocalparam(self, typedef):
        paramlist = []
        length = len(typedef.constructors)
        onehothead = str(len(typedef.constructors)) + "'b"
        onehotbody = list(len(typedef.constructors) * '0')
        counter = 0
        for constructor in typedef.constructors:
            onehotstring = list(onehotbody)
            onehotstring[length - 1 - counter] = '1'
            onehotstring = onehothead + "".join(onehotstring)
            paramlist.append(vast.Localparam(name=constructor.name, value=vast.IntConst(onehotstring)))
            counter += 1
        return vast.Decl(tuple(paramlist))

    def getContainersFromStmts(self, stmts):
        containers = []
        for stmt in stmts:
            if isinstance(stmt, ContainerDef):
                containers.append(stmt)
        return containers
