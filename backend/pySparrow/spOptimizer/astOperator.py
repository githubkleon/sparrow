from backend.pySparrow.spParser.ast import *
import backend.spLibrary as spLib
import splog as log
import copy


class Operator:
    def __init__(self, op):
        self.op = op

    def __repr__(self):
        return "%r" % self.op


def getImportList(ast):
    import_list = []
    for stmt in ast.module.stmts:
        if (isinstance(stmt, ImportDecl)):
            path_list = stmt.package.scope
            path_list.append(stmt.package.name)
            arg_list = stmt.args
            scope = stmt.scope
            nothiding = stmt.nothiding
            import_list.append(importEntry(path_list, arg_list, scope, nothiding))
    return import_list


class importEntry:
    def __init__(self, path_list, arg_list, scopename, nothiding):
        self.path_list = path_list
        self.arg_list = arg_list
        self.scopename = scopename
        self.nothiding = nothiding
        self.path = ""
        self.scope_handle = None


def findTypeDef(type, ast):
    for stmt in ast.module.stmts:
        if (isinstance(stmt, TypeDef)):
            return stmt
    return None


def getContainerList(ast):
    cont = []
    for stmt in ast.module.stmts:
        if (isinstance(stmt, ContainerDef)):
            cont.append(stmt)
    return cont


def getSourceList(container):
    slaves = []
    inputs = []
    for bus in container.buses:
        if (isinstance(bus, BusDef)):
            if (bus.direct == "slave"):
                slaves.append(bus)
        if (isinstance(bus, PortDef)):
            if (bus.direct == "input" or bus.direct == "in"):
                inputs.append(bus)
    return slaves, inputs


def getDrainList(container):
    slaves = []
    inputs = []
    for bus in container.buses:
        if (isinstance(bus, BusDef)):
            if (bus.direct == "master"):
                slaves.append(bus)
        if (isinstance(bus, PortDef)):
            if (bus.direct == "output" or bus.direct == "out"):
                inputs.append(bus)
    return slaves, inputs


def tracebackdrain(drain, container, ast, expectedType=None):
    # print("TRACING")
    log.spInfo(0, "TRACING BACK DRAIN:\n", log.genAST(drain))
    if (isinstance(drain, PortDef)):
        if drain.direct == "output" or drain.direct == "out":
            srcs = findSources(drain.name.name, container, ast, True)
            log.spInfo(0, "Sources Found")
            checkMultiDrive(srcs, "Output port " + str(drain.name))
            drain.source = srcs[0]
            if isinstance(srcs[0], VariableDef):
                drain.var = True
            determineType(srcs[0], drain.type)
            drain.traced = True
            tracebackdrain(srcs[0], container, ast)
        elif drain.direct == "input" or drain.direct == "in":
            if drain.type != expectedType:
                log.spError(log.SPError.TYPE_NOT_MATCH_ERROR,
                            "The type of the input port " + str(drain.name.name) +
                            " is expected as " + getTypeChainString([drain.type]) +
                            ", but " + expectedType.name.name + " is inferred.")
    elif isinstance(drain, AnonymousFunctionDef):
        log.spInfo(0, "Look to anonymousfunc %r"%drain)
        drain.source = tracebackdrain(drain.suite, container, ast, drain.returntype)
        drain.traced = True
    elif isinstance(drain, Identifier):
        srcs = findSources(drain.name, container, ast)
        log.spInfo(0, "Sources Found:")
        log.spInfo(0, srcs)
        checkMultiDrive(srcs, "Wire " + str(drain.name))
        determineType(srcs[0], expectedType)
        tracebackdrain(srcs[0], container, ast)
        drain.source = srcs[0]
        return srcs[0]
    elif isinstance(drain, FunctionCall):
        funcs = findFunctions(drain.name.name, container, ast)
        log.spInfo(0, "%r Function Define Found"%drain)
        checkMultiDefine(funcs, "Function " + str(drain.name.name))
        foundFunc = determineFunctionType(funcs[0], expectedType, container, ast)
        for arg, expType in zip(drain.args, foundFunc.cons.cons.inputs):
            if not (isinstance(arg, IntNumber) or isinstance(arg, FloatNumber) or isinstance(arg, StringLiteral)):
                srcs = findSources(arg.name, container, ast)
                log.spInfo(0, "Sources Found")
                checkMultiDrive(srcs, "Wire " + str(arg.name))
                arg.source = srcs[0]
                determineType(srcs[0], expType)
                arg.traced = True
                tracebackdrain(srcs[0], container, ast)
        drain.source = foundFunc
        return foundFunc
    elif isinstance(drain, BinaryOperation):
        inputTypes = traceOperatorInputType(drain.op, expectedType)
        inferredTypes=[0,0]
        if isTypeChainTypeVariable(inputTypes[0]):
            inferredTypes[0] = traceTypeBack(drain.expr0, container, ast)
        else:
            inferredTypes[0] = inputTypes[0]
        if isTypeChainTypeVariable(inputTypes[1]):
            inferredTypes[1] = traceTypeBack(drain.expr1, container, ast)
        else:
            inferredTypes[1] = inputTypes[1]
        log.spInfo(0, "inferred types:", inferredTypes)
        inputTypes = checkBinaryOperationTypes(inputTypes, inferredTypes)
        drain.expr0.source = tracebackdrain(drain.expr0, container, ast, inputTypes[0])
        drain.expr1.source = tracebackdrain(drain.expr1, container, ast, inputTypes[1])
        return drain
    elif isinstance(drain, UnaryOperation):
        inputTypes = traceOperatorInputType(drain.op, expectedType)
        drain.expr.source = tracebackdrain(drain.expr, container, ast, expectedType[0])
        return drain
    elif isinstance(drain, PartialSelection):
        log.spInfo(0, "AM I PARTIALSECTION")
        srcs = findSources(drain.name.name, container, ast)
        log.spInfo(0, "Sources Found")
        checkMultiDrive(srcs, "Wire " + str(drain.name))
        determineType(srcs[0], expectedType)
        tracebackdrain(srcs[0], container, ast, expectedType)
        drain.source = srcs[0]
        return srcs[0]
    else:
        log.spInfo(0, "NOBODY")
        log.spInfo(0, drain)
        pass


def checkBinaryOperationTypes(inputTypes, inferredTypes):
    if typechainlistEqual(inputTypes[0], inputTypes[1]):
        if typechainlistEqual(inferredTypes[0], inferredTypes[1]):
            return inferredTypes
        else:
            log.spError(log.SPError.TYPE_NOT_MATCH_ERROR,
                        "The expected binary operation types are: "
                        + getTypeChainString(inputTypes[0]) + "and "
                        + getTypeChainString(inputTypes[1]) + ", but"
                        + getTypeChainString(inferredTypes[0]) + "and "
                        + getTypeChainString(inferredTypes[1]) + " are inferred.")


def traceTypeBack(drain, container, ast):
    if (isinstance(drain, PortDef)):
        if drain.direct == "output" or drain.direct == "out":
            log.spError(log.SPError.PORT_TYPE_NOT_MATCH,
                        str(drain.name.name) + "is expected as an input port, but output port is declared")
        elif drain.direct == "input" or drain.direct == "in":
            return drain.type
    elif (isinstance(drain, AnonymousFunctionDef)):
         return traceTypeBack(drain.suite, container, ast)
    elif (isinstance(drain, Identifier)):
        srcs = findSources(drain.name, container, ast)
        checkMultiDrive(srcs, "Wire " + str(drain.name))
        return traceTypeBack(srcs[0], container, ast)
    elif (isinstance(drain, VariableDef)):
        if not isTypeChainTypeVariable(drain.type):
            return drain.type
    elif (isinstance(drain, TypeDef)):
        return [drain.name]

def isTypeChainTypeVariable(typechain):
    return len(typechain) == 1 and isTypeVariable(typechain[0])

def checkMultiDrive(srcs, info):
    log.spInfo(0, srcs)
    if len(srcs) > 1:
        log.spError(log.SPError.MULTI_DRIVED_ERROR, info)


def checkMultiDefine(srcs, info):
    log.spInfo(0, srcs)
    if len(srcs) > 1:
        log.spError(log.SPError.MULTI_DEFINED_ERROR, info)


def determineFunctionType(funcin, expectedType, container, ast):
    func = copy.deepcopy(funcin)
    funcConses = findConstrains(func.name, ast)
    if funcConses:
        checkMultiDrive(funcConses, "Constraints of function" + str(func.name.name))
        checkConstraints(func, funcConses[0])
        if not checktype(func.cons.outputs[0], expectedType):
            log.spError(log.SPError.TYPE_NOT_MATCH_ERROR,
                        "The output type of " + str(func.name.name) +
                        " is expected as " + getTypeChainString(func.cons.outputs[0]) +
                        ", but " + expectedType.name.name + " is inferred.")
        func.cons = funcConses[0]
    else:
        log.spInfo(0, "DETERMING FUNCTION TYPE:", func)
        func.cons = FunctionCons(func.name, Cons(determineFunctionInputTypes(func, container, ast, expectedType),
                                                 [expectedType]))
    return func


def determineFunctionInputTypes(func, container, ast, expectedType):
    log.spInfo(0, "determing Function INput Types")
    log.spInfo(0, expectedType)
    func.suite = reshapeSuite(func.suite, ast)
    log.spInfo(0, "func suite after reshape:", func.suite)
    traceExprType(func.suite, expectedType, func, container, ast)
    types = []
    for arg in func.args:
        if arg.traced == False:
            log.spError(log.SPError.TYPE_NOT_MATCH_ERROR,
                        "The argument of " + func.name.name + " " + arg.name + " is not used.")
        if arg.type == None:
            log.spError(log.SPError.TYPE_NOT_MATCH_ERROR,
                        "The argument of " + func.name.name + " " + arg.name + " cannot be inferred")
        types.append(arg.type)
    return types


def traceOperatorInputType(op_name, typechain):
    for stmt in spLib.BASICS.module.stmts:
        if isinstance(stmt, OperatorCons):
            for op in stmt.ops:
                if op == op_name:
                    if isCoincide(stmt.cons.outputs[0], typechain):
                        return inferInputTypes(stmt.cons, typechain)
    log.spError(log.SPError.FUNCTION_NOT_DEFINED_ERROR, "Operator constraint " + op_name)


def inferInputTypes(cons, typechain):
    inputTypes = copy.deepcopy(cons.inputs)
    indexes = range(len(cons.outputs[0]))
    for type, index in zip(cons.outputs[0], indexes):
        if isTypeVariable(type):
            indexes1 = range(len(inputTypes))
            for inputTypechain, idx1 in zip(inputTypes, indexes1):
                indexes2 = range(len(inputTypechain))
                for inputType, idx2 in zip(inputTypechain, indexes2):
                    if inputType == type:
                        inputTypes[idx1][idx2] = typechain[index]
    return inputTypes


def isCoincide(typechain0, typechain1):
    log.spInfo(0, "TYPECHAINES")
    log.spInfo(0, typechain0)
    log.spInfo(0, typechain1)
    result = True
    if len(typechain0) == len(typechain1):
        indexes = range(len(typechain0))
        for type, index in zip(typechain1, indexes):
            if isTypeVariable(type):
                if not isTypeVariable(typechain0[index]):
                    log.spError(log.SPError.TYPE_NOT_MATCH_ERROR,
                                getTypeChainString(typechain0) + " is expected, but " +
                                getTypeChainString(typechain1) + " is inferred.")
                else:
                    indexes0 = getIndexesOfSameTypeVariable(typechain0[index], typechain0)
                    indexes1 = getIndexesOfSameTypeVariable(type, typechain1)
                    if indexes0 != indexes1:
                        log.spError(log.SPError.TYPE_NOT_MATCH_ERROR,
                                    getTypeChainString(typechain0) + " is expected, but " +
                                    getTypeChainString(typechain1) + " is inferred.")
            else:
                if not isTypeVariable(typechain0[index]):
                    if type != typechain0[index]:
                        log.spError(log.SPError.TYPE_NOT_MATCH_ERROR,
                                    getTypeChainString(typechain0) + " is expected, but " +
                                    getTypeChainString(typechain1) + " is inferred.")
                else:
                    indexes0 = getIndexesOfSameTypeVariable(typechain0[index], typechain0)
                    indexes1 = getIndexesOfSameTypeVariable(type, typechain1)
                    if indexes0 != indexes1:
                        log.spError(log.SPError.TYPE_NOT_MATCH_ERROR,
                                    getTypeChainString(typechain0) + " is expected, but " +
                                    getTypeChainString(typechain1) + " is inferred.")
    else:
        log.spError(log.SPError.TYPE_NOT_MATCH_ERROR,
                    getTypeChainString(typechain0) + " is expected, but " +
                    getTypeChainString(typechain1) + " is inferred.")
    return result


def getIndexesOfSameTypeVariable(type, typechain):
    indexes = range(len(typechain))
    returnIndexes = []
    for t, index in zip(typechain, indexes):
        if t == type:
            returnIndexes.append(index)
    return returnIndexes


def isTypeVariable(type):
    return type.name.name[0].islower()


def traceExprType(expr, expectedType, func, container, ast):
    if isinstance(expr, UnaryOperation):
        inputTypes = traceOperatorInputType(func.suite.op, expectedType)
        traceExprType(expr.expr, inputTypes[0], func, container, ast)
    elif isinstance(expr, BinaryOperation):
        inputTypes = traceOperatorInputType(func.suite.op, expectedType)
        traceExprType(expr.expr0, inputTypes[0], func, container, ast)
        traceExprType(expr.expr1, inputTypes[1], func, container, ast)
    elif isinstance(expr, Identifier):
        for arg in func.args:
            if arg.name == expr.name:
                if (arg.traced):
                    if arg.type != expectedType:
                        log.spError(log.SPError.TYPE_NOT_MATCH_ERROR,
                                    "The argument of " + func.name.name + " " +
                                    arg.name + " gets conflicted inferred types : " +
                                    getTypeChainString(arg.type) + " and " +
                                    getTypeChainString(expectedType))
                else:
                    arg.traced = True
                    arg.type = expectedType
    elif isinstance(expr, FunctionCall):
        expr.returntype = expectedType
        funcs = findFunctions(expr.name.name, container, ast)
        log.spInfo(0, "Function Define Found %r"%funcs)
        checkMultiDefine(funcs, "Function " + str(expr.name.name))
        expr.source = determineFunctionType(funcs[0], expr.returntype, container, ast)
        for arg, expType in zip(expr.args, expr.source.cons.cons.inputs):
            traceExprType(arg, expType, func, container, ast)
    else:
        pass


def reshapeSuite(suite, ast):
    tokens = getTokens(suite)
    suffixExpr = infixExpr2SuffixExpr(tokens)
    exprTree = suffixExpr2ExprTree(suffixExpr)
    return exprTree


def suffixExpr2ExprTree(tokens):
    exprStack = []
    for token in tokens:
        if isinstance(token, Operator):
            num = getInputArgNumOp(token.op)
            if (num == 1):
                if exprStack:
                    exprStack.append(UnaryOperation(token.op, exprStack.pop()))
                else:
                    log.spError(log.SPError.ILLEGAL_EXPRESSION_ERROR, token.op)
            elif (num == 2):
                if len(exprStack) >= 2:
                    expr0 = exprStack[-2]
                    expr1 = exprStack[-1]
                    exprStack.pop()
                    exprStack.pop()
                    exprStack.append(BinaryOperation(expr0, token.op, expr1))
                else:
                    log.spError(log.SPError.ILLEGAL_EXPRESSION_ERROR, token.op)
            else:
                log.spError(log.SPError.ILLEGAL_OPERATOR_ERROR, token.op)
        else:
            exprStack.append(token)
        # print ("_+_+_+_+_+__+_+_++")
        # print (exprStack)
    return exprStack.pop()


def getInputArgNumOp(op_name):
    for stmt in spLib.BASICS.module.stmts:
        if isinstance(stmt, OperatorCons):
            for op in stmt.ops:
                if op == op_name:
                    return len(stmt.cons.inputs)
    log.spError(log.SPError.FUNCTION_NOT_DEFINED_ERROR, "Operator " + op_name)


def infixExpr2SuffixExpr(tokens):
    infixStack = []
    suffixExpr = []
    last_token_is_value = False
    for token in tokens:
        if isinstance(token, Operator):
            if token.op == "(":
                infixStack.append(token)
                last_token_is_value = False
            elif token.op == ")":
                while (True):
                    if isinstance(infixStack[-1], Operator):
                        if infixStack[-1].op == "(":
                            infixStack.pop()
                            break
                        else:
                            suffixExpr.append(infixStack.pop())
                    else:
                        suffixExpr.append(infixStack.pop())
                last_token_is_value = True
            else:
                if token.op == "-" or token.op == "+":
                    if not last_token_is_value:
                        suffixExpr.append(IntNumber('0'))
                while (True):
                    if infixStack:
                        if lowerThanPrec(token, infixStack[-1]):
                            suffixExpr.append(infixStack.pop())
                        else:
                            infixStack.append(token)
                            break
                    else:
                        infixStack.append(token)
                        break
                last_token_is_value = True
        else:
            suffixExpr.append(token)
            last_token_is_value = True
    while (infixStack):
        suffixExpr.append(infixStack.pop())
    return suffixExpr


def lowerThanPrec(op0, op1):
    if op1.op == "(" or op1.op == ")":
        return False
    infix1, prec1 = getOperatorInfix(op0.op)
    infix2, prec2 = getOperatorInfix(op1.op)
    if prec1 < prec2:
        return True
    elif prec1 == prec2:
        if infix1 != infix2:
            log.spError(log.SPError.ASSOCIATIVITY_ERROR, op0.op + " and " + op1.op)
        else:
            if infix1 == "infixr":
                return False
            elif infix1 == "infixl":
                return True
            elif infix1 == "infix":
                log.spError(log.SPError.CANNOT_ASSOCIATE_ERROR, op0.op + " and " + op1.op)
    else:
        return False


def getOperatorInfix(op_name):
    # print("infix " + op_name)
    for stmt in spLib.BASICS.module.stmts:
        if isinstance(stmt, OperatorInfix):
            for op in stmt.ops:
                if op == op_name:
                    return stmt.infix, stmt.prec
    log.spError(log.SPError.FUNCTION_NOT_DEFINED_ERROR, "Operator " + op_name)


def getTokens(suite):
    tokens = []
    if isinstance(suite, UnaryOperation):
        tokens.append(Operator(suite.op))
        tokens.extend(getTokens(suite.expr))
    elif isinstance(suite, BinaryOperation):
        tokens.extend(getTokens(suite.expr0))
        tokens.append(Operator(suite.op))
        tokens.extend(getTokens(suite.expr1))
    elif isinstance(suite, ParenCombine):
        tokens.append(Operator('('))
        tokens.extend(getTokens(suite.expr))
        tokens.append(Operator(')'))
    else:
        tokens.append(suite)
    return tokens


def getTypeChainString(typeChain):
    typeStr = ""
    indexes = [0] * (len(typeChain) - 1)
    indexes.append(1)
    for type, index in zip(typeChain, indexes):
        if (index):
            typeStr += getTypeString(type)
        else:
            typeStr += getTypeString(type) + " -> "
    return typeStr


def getTypeString(type):
    return getPointerString(type)


def getPointerString(type):
    return type.name.name


def checkConstraints(func, funcCons):
    if not len(func.args) == len(funcCons.cons.inputs):
        log.spError(log.SPError.CONSTRAINTS_NOT_MATCH_FUNCTION_ERROR, func.name.name)
    if not len(funcCons.cons.outputs):
        log.spError(log.SPError.CONSTRAINTS_MULTIPLE_OUTPUTS_ERROR, "Constraints " + func.name.name)


def determineType(src, type):
    if isinstance(src, AnonymousFunctionDef):
        src.returntype = type
    elif isinstance(src, VariableDef):
        # print ("CHECKING TYPE")
        # print (src.type)
        # print (type)
        if not checktype(src.type, type):
            log.spError(log.SPError.TYPE_NOT_MATCH_ERROR,
                        "%s : %r is expected, but %r is given." % (
                            src.pointer.name.name, type, src.type))


def findConstrains(name, ast):
    conses = []
    for stmt in ast.module.stmts:
        if isinstance(stmt, FunctionCons):
            if stmt.name == name:
                conses.append(stmt)
    return conses


def findFunctions(name, container, ast):
    funcs = []
    for stmt in ast.module.stmts:
        if isinstance(stmt, FunctionDef):
            if stmt.name.name == name:
                funcs.append(stmt)
    return funcs


def findSources(name, container, ast, output=False):
    log.spInfo(0, "FINDING SOURCES", name)
    srcs = []
    for decl in container.decls:
        if (isinstance(decl, AnonymousFunctionDef)):
            # print (decl.name)
            if (decl.name.name == name):
                srcs.append(decl)
        elif (isinstance(decl, VariableDef)):
            if decl.pointer.name.name == name:
                srcs.append(decl)
    if not output:
        for bus in container.buses:
            if (isinstance(bus, PortDef)):
                if bus.name.name == name:
                    srcs.append(bus)
    for stmt in ast.module.stmts:
        if (isinstance(stmt, FunctionDef)):
            if (stmt.name.name == name):
                srcs.append(stmt)
        elif (isinstance(stmt, TypeDef)):
            for constructor in stmt.constructors:
                if (constructor.name == name) and not constructor.elements:
                    srcs.append(stmt)
    return srcs


def expandBuses(container):
    expandedBuses = []
    for bus in container.buses:
        if (isinstance(bus, BusDef)):
            for busdef in bus.buses:
                expandedBuses.append(BusDef(bus.direct, bus.interface, bus.paras, name=busdef))
        if (isinstance(bus, PortDef)):
            for portdef in bus.ports:
                # print (portdef)
                expandedBuses.append(PortDef(bus.direct, bus.type, bus.paras, name=portdef))
    container.buses = expandedBuses


def checktype(typea, typeb):
    if typea == typeb:
        return True
    else:
        return False


def getUsedFunctionList(ast):
    funcs = []
    for stmt in ast.module.stmts:
        if isinstance(stmt, ContainerDef):
            for bus in stmt.buses:
                if isinstance(bus, PortDef) and (bus.direct == "output" or bus.direct == "out"):
                    log.spInfo(0, "USED BUS:", bus)
                    funcs.extend(getUsedFunctions(bus.source, ast))
    # print("USED FUNCTIONS:")
    # print(len(funcs))
    # print(funcs)
    # print("END OF USED FUNCTIONS")
    filtered_funcs = []
    for func in funcs:
        if not functionDefInFunctionDefList(func, filtered_funcs):
            filtered_funcs.append(func)
    # print("*************************************")
    # print(filtered_funcs)
    return filtered_funcs


def functionDefInFunctionDefList(func, func_list):
    for func_elem in func_list:
        if functionDefEqual(func, func_elem):
            return True
    return False


def functionDefEqual(func1, func2):
    if not identifierEqual(func1.name, func2.name):
        return False
    if not functionconsEqual(func1.cons.cons, func2.cons.cons):
        return False
    return True


def identifierEqual(id1, id2):
    if not id1 == id2:
        return False
    return True


def functionconsEqual(cons1, cons2):
    # print ("FUNCTION CONS == ", cons1, cons2)
    if not consListEqual(cons1.inputs, cons2.inputs):
        return False
    if not consListEqual(cons1.outputs, cons2.outputs):
        return False
    return True


def consListEqual(conslist1, conslist2):
    if len(conslist1) != len(conslist2):
        return False
    for i in range(len(conslist1)):
        if not typechainlistEqual(conslist1[i], conslist2[i]):
            return False
    return True


def typechainlistEqual(tpcl1, tpcl2):
    log.spInfo(0, "typechainlistEqual:", tpcl1, tpcl2)
    if len(tpcl1) != len(tpcl2):
        return False
    for i in range(len(tpcl1)):
        if not typeEqual(tpcl1[i], tpcl2[i]):
            return False
    return True


def typeEqual(tpl1, tpl2):
    log.spInfo(0, "typeEqual:", tpl1, tpl2)
    if not pointerEqual(tpl1, tpl2):
        return False
    return True


def pointerEqual(pt1, pt2):
    log.spInfo(0, "typeEqual:", pt1, pt2)
    if not identifierEqual(pt1.name, pt2.name):
        return False
    if pt1.tensors and pt1.tensors:
        if not vectorEqual(pt1.tensors.tensors, pt2.tensors.tensors):
            return False
    return True


def vectorEqual(vc1, vc2):
    if len(vc1) != len(vc2):
        return False
    for i in range(len(vc1)):
        if vc1[i] != vc2[i]:
            return False
    return True


def getUsedFunctions(decl, ast):
    funcs = []
    log.spInfo(0, "GET USED FUNCTIONS PROCESS:")
    log.spInfo(0, decl)
    if isinstance(decl, AnonymousFunctionDef):
        if isinstance(decl.suite, Identifier):
            return funcs + getUsedFunctions(decl.source, ast)
        elif isinstance(decl.suite, BinaryOperation):
            return funcs + getUsedSpFunctions(decl.source, ast)
        elif isinstance(decl.suite, UnaryOperation):
            return funcs + getUsedSpFunctions(decl.source, ast)
        elif isinstance(decl.suite, FunctionCall):
            funcs += [decl.source]
            funcs += getUsedSpFunctions(decl.source.suite, ast)
            for arg in decl.suite.args:
                funcs += getUsedFunctions(arg.source, ast)
            return funcs
        elif isinstance(decl.suite, IfStructure):
            funcs += getUsedFunctions(decl.suite.suite, ast)
            for selif in decl.suite.elifs:
                funcs += getUsedFunctions(selif.suite, ast)
            return funcs + getUsedFunctions(decl.suite.els, ast)
        elif isinstance(decl.suite, CaseStructure):
            for case in decl.suite.suites:
                funcs += getUsedFunctions(case.suite, ast)
            return funcs
        else:
            return []
    else:
        return []


def getUsedSpFunctions(decl, ast):
    funcs = []
    log.spInfo(0, "SP FUNCTIONS：", decl)
    if isinstance(decl, BinaryOperation):
        return funcs + getUsedSpFunctions(decl.expr0, ast) + getUsedSpFunctions(decl.expr1, ast)
    elif isinstance(decl, UnaryOperation):
        return funcs + getUsedSpFunctions(decl.expr, ast)
    elif isinstance(decl, FunctionCall):
        funcs += [decl.source]
        for arg in decl.args:
            funcs += getUsedFunctions(arg.source, ast)
        return funcs + getUsedSpFunctions(decl.source.suite, ast)
    elif isinstance(decl, IfStructure):
        funcs += getUsedFunctions(decl.suite, ast)
        for selif in decl.elifs:
            funcs += getUsedFunctions(selif.suite, ast)
        return funcs + getUsedFunctions(decl.els, ast)
    elif isinstance(decl, CaseStructure):
        for case in decl.suites:
            funcs += getUsedFunctions(case.suite, ast)
        return funcs
    else:
        log.spInfo(0, "NO BODY WANT ME:", decl)
        return []


def onlyOutput(func):
    # print("ONLY CHECK A")
    # print(func)
    # print("ONLY CHECK B")
    if func.cons.cons.inputs:
        return False
    else:
        return True


def convertFunc2AnonymousFunc(func, ast):
    for stmt in ast.module.stmts:
        if isinstance(stmt, ContainerDef):
            for decl in stmt.decls:
                convert2AnonymousFunc(decl, func, ast)


def convert2AnonymousFunc(decl, func, ast):
    if isinstance(decl, AnonymousFunctionDef):
        if isinstance(decl.suite, FunctionCall) and identifierEqual(decl.suite.name, func.name):
            decl.suite = decl.suite.name
        else:
            convert2AnonymousFunc(decl.suite, func, ast)
    elif isinstance(decl, BinaryOperation):
        if isinstance(decl.expr0, FunctionCall) and identifierEqual(decl.expr0.name, func.name):
            decl.expr0 = decl.expr0.name
        elif isinstance(decl.expr1, FunctionCall) and identifierEqual(decl.expr1.name, func.name):
            decl.expr1 = decl.expr1.name
        else:
            convert2AnonymousFunc(decl.expr0, func, ast)
            convert2AnonymousFunc(decl.expr1, func, ast)
    elif isinstance(decl, UnaryOperation):
        if isinstance(decl.suite, FunctionCall) and identifierEqual(decl.suite.name, func.name):
            decl.suite = decl.suite.name
        else:
            convert2AnonymousFunc(decl.expr, func, ast)
    elif isinstance(decl, VariableDef):
        if isinstance(decl.decls, FunctionCall) and identifierEqual(decl.decls.name, func.name):
            decl.decls = decl.decls.name
        else:
            convert2AnonymousFunc(decl.decls, func, ast)
    elif isinstance(decl, IfStructure):
        if isinstance(decl.suite, FunctionCall) and identifierEqual(decl.suite.name, func.name):
            decl.suite = decl.suite.name
        else:
            convert2AnonymousFunc(decl.suite, func, ast)
        for selif in decl.elifs:
            if isinstance(selif.suite, FunctionCall) and identifierEqual(selif.suite.name, func.name):
                selif.suite = selif.suite.name
            else:
                convert2AnonymousFunc(selif.suite, func, ast)
        if isinstance(decl.els, FunctionCall) and identifierEqual(decl.els.name, func.name):
            decl.els = decl.els.name
        else:
            convert2AnonymousFunc(decl.els, func, ast)
    elif isinstance(decl, CaseStructure):
        for case in decl.suites:
            if isinstance(case.suite, FunctionCall) and identifierEqual(case.suite.name, func.name):
                case.suite = case.suite.name
            else:
                convert2AnonymousFunc(case.suite, func, ast)
    elif isinstance(decl, ParenCombine):
        if isinstance(decl.expr, FunctionCall) and identifierEqual(decl.expr.name, func.name):
            decl.expr = decl.expr.name
        else:
            convert2AnonymousFunc(decl.expr, func, ast)

def containSequentialLogic(container):
    for decl in container.decls:
        if isinstance(decl, VariableDef):
            return True
    return False


def traceParameter(ast):
    pass

def expandGenStructures(ast):
    for stmt in ast.module.stmts:
        if (isinstance(stmt, ContainerDef)):
            for decl in stmt.decls:
                if (isinstance(decl, AnonymousFunctionDef)):
                    expandGenStructInSuite(decl.suite)

def expandGenStructInSuite(suite):
    if (isinstance(suite, CaseStructure)):
        expandSuites = []
        for suite_one in suite.suites:
            expandSuites.extend(expandGenStructInSuite(suite_one))
        suite.suites = expandSuites
    elif (isinstance(suite, GenForStructure)):
        expandSuites = []
        forlist = []
        iterator_id = ""
        if isinstance(suite.list, FunctionCall):
            if suite.list.name.name == "range":
                if len(suite.list.args) == 1:
                    forlist = range(int(suite.list.args[0].value))
            iterator_id = suite.name.name
        if isinstance(suite.suite, list):
            if isinstance(suite.suite[0], Case):
                log.spInfo(0, "INSIDE GENFORSTRUCTURE")
                for case_entry in suite.suite:
                    for i in forlist:
                        expandSuites.append(Case(test=replaceid(i, case_entry.test, iterator_id),
                                                 suite=replaceid(i, case_entry.suite, iterator_id)))
            return expandSuites
    elif isinstance(suite, Case):
        return [Case(test=suite.test, suite=expandGenStructInSuite(suite.suite))]

def replaceid(res, suite, id):
    log.spInfo(0, "replaceid", res, suite, id)
    if isinstance(suite, Identifier):
        if suite.name == id:
            if isinstance(res, int):
                return genIntNumber(res)
        else:
            return suite
    elif isinstance(suite, IntNumber):
        return suite
    elif isinstance(suite, FloatNumber):
        return suite
    elif isinstance(suite, StringLiteral):
        return suite
    elif isinstance(suite, BinaryOperation):
        return BinaryOperation(expr0=replaceid(res, suite.expr0, id),
                                         op=suite.op, expr1=replaceid(res, suite.expr1, id))
    elif isinstance(suite, UnaryOperation):
        return UnaryOperation(expr=replaceid(res, suite.expr, id),
                                         op=suite.op)


def genIntNumber(value):
    return IntNumber(value=str(value))


def setClockReset(ast):
    for stmt in ast.module.stmts:
        if isinstance(stmt, ContainerDef):
            for decl in stmt.decls:
                if isinstance(decl, AnonymousFunctionDef):
                    if decl.name.name == "clock" and decl.name.scopes[0] == "self":
                        stmt.clock = decl.suite
                    if decl.name.name == "reset" and decl.name.scopes[0] == "self":
                        stmt.reset = decl.suite
