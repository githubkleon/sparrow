import splog as log
from backend.pySparrow.spParser.ast import *
import backend.spLibrary as spLib
from math import ceil

class Vertex:
    def __init__(self, delay, depth, mapping=None, drains=[], source=None, marks=[]):
        self.delay = delay
        self.directs = []
        self.depth = depth
        self.mapping = mapping
        self.source = source
        self.drains = drains
        self.marks = marks
        self.processed = False

    def __repr__(self):
        return "Vertex{%r, \n%r, \n%r, \nmapping=%r, \nsource=%r, \ndrains=%r}" % (self.delay, self.directs, self.depth, self.mapping, self.source, self.drains)

# class Edge:
#     def __init__(self, drain, source):
#         self.drain = drain
#         self.source = source
#
#     def __repr__(self):
#         return "Edge{%r, \n%r}"%(self.drain, self.source)

class Mark:
    def __init__(self):
        self.traced = False
        self.cutDepth = 0
        self.cutPoint = 0

    def __repr__(self):
        return "Mark{%r, \n%r, \n%r}"%(self.traced, self.cutDepth, self.cutPoint)

class PathNode:
    def __init__(self, mapping=None, last=None):
        self.mapping = mapping
        self.last = last

    def __repr__(self):
        return "Node{mapping=%r, \nlast=%r}"%(self.mapping, self.last)


def pipelineContainer(ast, container):
    if container.clock:
        clockCycle = spLib.SCINOTATION['Giga'] / spLib.SCINOTATION[container.clock.args[2].name] / float(container.clock.args[1].value)
    else:
        clockCycle = 1000
    log.spInfo(0, "CLOCK CYCLE", clockCycle)
    outputs = getOutputPorts(container.buses)
    drain = Vertex(0, 0, None, buildGraph(outputs, clockCycle), None, genMarks(len(outputs)))
    # log.spInfo(0, log.genAST(drain))
    maxDelay, paths = getMaxGraphPathDelay(drain, 0, 0, PathNode(None, None))
    paths = sortPaths(paths)
    log.spInfo(0, "MAX GRAPH DELAY: ", maxDelay)
    # log.spInfo(0, "PATHS: ", paths)
    maxCut = getMaxCut(maxDelay, clockCycle)
    log.spInfo(0, "MAX GRAPH CUT: ", maxCut)
    for path in paths:
        curMaxCut = cutGraph(path, 0, maxCut, 0, clockCycle)
        if curMaxCut > maxCut:
            maxCut = curMaxCut
    # cutGraph(paths[0], 0, maxCut, 0, clockCycle)
    container.decls.extend(removeDuplicatedVar(genVariableNode(drain, [])))



def genVariableNode(root, processedNodes):
    # log.spInfo(0, "CUR VERTEX:", root)
    varlist = []
    if isinstance(root.mapping, PortDef):
        if root.mapping.direct == "input" or root.mapping.direct == "in":
            return []
    if isinstance(root.mapping, FunctionCall):
        print("GENERATING VAR NODE:", root.marks)
        if not root.mapping in processedNodes:
            for i in range(len(root.marks)):
                if root.marks[i].cutPoint > 0:
                    log.spInfo(0, "ARG ORIGIN NAME", root.mapping.args[i])
                    varnodes, argname = genVariable(root.mapping.args[i], root.marks[i].cutPoint)
                    root.mapping.args[i] = argname
                    log.spInfo(0, "ARG NAME:", argname)
                    log.spInfo(0, "CUT POINT CON:", root)
                    varlist.extend(varnodes)
        processedNodes.append(root.mapping)

    for drain in root.drains:
        varlist.extend(genVariableNode(drain, processedNodes))
    return varlist

def removeDuplicatedVar(vars):
    log.spInfo(0, "VARS:", vars)
    resvars = []
    for var in vars:
        dup = False
        for var1 in resvars:
            if isPointerEqual(var.pointer, var1.pointer):
                dup = True
                break
        if not dup:
            resvars.append(var)
    return resvars


def isPointerEqual(pt1, pt2):
    if not isIdentifierEqual(pt1.name, pt2.name):
        return False
    return True


def genVariable(arg, number):
    varlist = []
    varname = Identifier(arg.name)

    for i in range(number):
        if arg.source:
            newvarname = Identifier(varname.name + "_r")
            varlist.append(VariableDef(type=arg.source.returntype, paras=[], pointer=Pointer(name=newvarname, tensors=[]), init=IntNumber("0"), decls=varname))
            varname = newvarname
    return varlist, varname

def sortPaths(paths):
    sortedPaths = []
    for i in range(len(paths)):
        maxDelay = 0
        maxNumber = 0
        # log.spInfo(0, "LEN OF PATH:", len(paths))
        for j in range(len(paths)):
            # log.spInfo(0, "CUR PATH DELAY:", paths[j][0])
            if paths[j][0] > maxDelay:
                maxDelay = paths[j][0]
                maxNumber = j
        log.spInfo(0, "MAX NUMBER:", maxNumber, " MAX DELAY:", maxDelay)
        sortedPaths.append(paths[maxNumber][1])
        del paths[maxNumber]
    return sortedPaths


def getMaxCut(maxDelay, cycle):
    return ceil(maxDelay / cycle) - 1


def getDrainPosition(drains, node):
    for i in range(len(drains)):
        if drains[i] == node:
            return i
    # if isinstance(node.mapping, PortDef):
    #     for i in range(len(drains)):
    #         if isinstance(drains[i].mapping, PortDef):
    #             if isPortDefEqual(drains[i].mapping, node.mapping):
    #                 return i
    # elif isinstance(node.mapping, BinaryOperation):
    #     for i in range(len(drains)):
    #         if isinstance(drains[i].mapping, BinaryOperation):
    #             if drains[i] == node:
    #                 return i


def isPortDefEqual(port1, port2):
    if port1.direct != port2.direct:
        return False
    if not isIdentifierEqual(port1.name, port2.name):
        return False
    return True

def isIdentifierEqual(id1, id2):
    if id1.name != id2.name:
        return False
    return True

def cutGraph(path, curCut, maxCut, curDelay, cycle):
    # log.spInfo(0, "CUR CUT:", curCut)
    # log.spInfo(0, "MAX CUT:", maxCut)
    # log.spInfo(0, "CUR DELAY:", curDelay)
    # log.spInfo(0, "MARKS:", path.mapping.marks)
    # if (path.last.mapping):
    #     log.spInfo(0, "CUR path Last delay:", path.last.mapping.delay)
    # log.spInfo(0, "CUR path:", path)
    mark = path.last.mapping.marks[getDrainPosition(path.last.mapping.drains, path.mapping)]
    if curDelay + path.last.mapping.delay > cycle:
        if mark.traced == True:
            if mark.cutPoint > 0:
                curCut += mark.cutDepth
        else:
            if path.last.last.mapping:
                marklast = path.last.last.mapping.marks[getDrainPosition(path.last.last.mapping.drains, path.last.mapping)]
            else:
                marklast = Mark()

            if marklast.traced == True:
                mark.cutPoint = marklast.cutDepth - curCut - 1
                log.spInfo(0, "Cut POINT", mark.cutPoint)
                curCut += mark.cutPoint
            else:
                mark.cutPoint = 1
                curCut += mark.cutPoint
            mark.traced = True
            mark.cutDepth = curCut
            curDelay = path.last.mapping.delay
    else:
        if mark.traced == True:
            if mark.cutPoint > 0:
                curCut += mark.cutPoint
        else:
            if path.last.last.mapping:
                marklast = path.last.last.mapping.marks[getDrainPosition(path.last.last.mapping.drains, path.last.mapping)]
            else:
                marklast = Mark()
            if marklast.traced == True:
                log.spInfo(0, "FOUND TRACED EDGE", marklast, mark, path)
                if marklast.cutPoint > 0:
                    mark.cutPoint = marklast.cutDepth - curCut - 1
                    curCut += mark.cutPoint
                    if mark.cutPoint > 0:
                        curDelay = path.last.mapping.delay
                    else:
                        curDelay += path.last.mapping.delay
                else:
                    mark.traced = True
                    mark.cutDepth = curCut
                    curDelay += path.last.mapping.delay

                log.spInfo(0, "FOUND TRACED EDGE", marklast, mark)
            else:
                mark.traced = True
                mark.cutDepth = curCut
                curDelay += path.last.mapping.delay

    if path.last.last.mapping:
        return cutGraph(path.last, curCut, maxCut, curDelay, cycle)
    else:
        if curCut > maxCut:
            return curCut
        else:
            return maxCut

    # if isinstance(path.mapping.mapping, PortDef) and (path.mapping.mapping.direct == "input" or path.mapping.mapping.direct == "in"):
    #     log.spInfo(0, "MARKS INPUT", path.last.mapping.marks)
    #     mark = path.last.mapping.marks[getDrainPosition(path.last.mapping.drains, path.mapping)]
    #     mark.traced = True
    #     mark.cutDepth = 0
    #     mark.cutPoint = 0
    #     return cutGraph(path.last, curCut, maxCut, curDelay, cycle)
    # elif isinstance(path.mapping.mapping, BinaryOperation):
    #     if curDelay + path.last.mapping.delay > cycle:
    #         pass
    #     else:
    #         mark = path.last.mapping.marks[getDrainPosition(path.last.mapping.drains, path.mapping)]
    #         mark.traced = True
    #         mark.cutDepth = curCut
    #         mark.cutPoint = 0
    #         return cutGraph(path.last, curCut, maxCut, curDelay, cycle)
    # elif isinstance(path.mapping.mapping, FunctionCall):
    #     if curDelay + path.mapping.delay > cycle:
    #         mark = path.mapping.marks[getDrain]

    # if (isinstance(path.last.mapping, PortDef) and
    #     (path.last.mapping.direct == "output" or path.last.mapping.direct == "out")):
    #     if curDelay + path.last.mapping.delay > cycle:
    #         pass
    # else:
    #     if curCut == maxCut:
    #         return
    #     else:
    #         insertCut(maxCut - curCut, path.mapping)

def insertCut(cutNumber, node):
    pass



def getMaxGraphPathDelay(root, curDelay, maxDelay, path):
    pathlist = []
    # log.spInfo(0, "CUR VERTEX:", root)
    # log.spInfo(0, "CUR DELAY:", curDelay)
    # log.spInfo(0, "MAX DELAY:", maxDelay)
    if isinstance(root.mapping, PortDef):
        if root.mapping.direct == "input" or root.mapping.direct == "in":
            if curDelay > maxDelay:
                return curDelay, [(curDelay, PathNode(root, path))]
            else:
                return maxDelay, [(curDelay, PathNode(root, path))]
    for drain in root.drains:
        if (drain == None):
            log.spInfo(0, "MOTHER OF NONE:", root)
        curMaxDelay, paths = getMaxGraphPathDelay(drain, curDelay + root.delay, maxDelay, PathNode(root, path))
        pathlist.extend(paths)
        # log.spInfo(0, "CUR VERTEX:", root)
        # log.spInfo(0, "CURMAX DELAY:", curMaxDelay)
        # log.spInfo(0, "MAX DELAY:", maxDelay)
        if curMaxDelay > maxDelay:
            maxDelay = curMaxDelay
    return maxDelay, pathlist


def getOutputPorts(buses):
    outputs = []
    for bus in buses:
        if isinstance(bus, PortDef):
            if bus.direct == "output" or bus.direct == "out":
                outputs.append(bus)
    return outputs


def buildGraph(outputs, cycle):
    vertexlist = []
    for output in outputs:
        vertexlist.append(traceOpNodeBack(output, 0, cycle, output))
    return vertexlist

def genMarks(length):
    marks = []
    for i in range(length):
        marks.append(Mark())
    return marks


def traceOpNodeBack(drain, depth, cycle, last_drain):
    # log.spInfo(0, "TRACING OPNODE: ", log.genAST(drain))
    # log.spInfo(0, "LAST DRAIN: ", log.genAST(last_drain))
    if isinstance(drain, PortDef):
        if drain.direct == "output" or drain.direct == "out":
            return traceOpNodeBack(drain.source, depth, cycle, drain)
        elif drain.direct == "input" or drain.direct == "in":
            return Vertex(0, depth + 1, drain, [], last_drain, [])
    elif isinstance(drain, AnonymousFunctionDef):
        return traceOpNodeBack(drain.suite, depth, cycle, drain)
    elif isinstance(drain, Identifier):
        return traceOpNodeBack(drain.source, depth, cycle, drain)
    elif isinstance(drain, BinaryOperation):
        opDelay = getOpDelay(drain.op)
        vertextlist = []
        vertextlist.append(traceOpNodeBack(drain.expr0, depth + 1, cycle, drain))
        vertextlist.append(traceOpNodeBack(drain.expr1, depth + 1, cycle, drain))
        return Vertex(opDelay, depth + 1, drain, vertextlist, last_drain, genMarks(len(vertextlist)))
    elif isinstance(drain, FunctionCall):
        funcDelay = getFunctionDelay(drain.source)
        # log.spInfo(0, "FINAL FUNCTION DELAY:", drain.source.name.name, ":", funcDelay)
        vertextlist = []
        for arg in drain.args:
            vertextlist.append(traceOpNodeBack(arg.source, depth, cycle, drain))
        if funcDelay < cycle:
            return Vertex(funcDelay, depth + 1, drain, vertextlist, last_drain, genMarks(len(vertextlist)))
    elif isinstance(drain, FunctionDef):
        pass
    elif isinstance(drain, PartialSelection):
        return traceOpNodeBack(drain.source, depth, cycle, drain)
    else:
        return Vertex(0, depth + 1, drain, [], last_drain, [])


def getFunctionDelay(func):
    maxDelay = 0
    nodes = []
    delay =  getMaxFunctionDelay(func.suite, 0, maxDelay, nodes)
    # log.spInfo(0, "GET FUNCTION DELAY: ", func.name.name, ":", delay)
    return delay

def getMaxFunctionDelay(func, curDelay, maxDelay, nodes):
    # log.spInfo(0, "MAX FUNCTION DELAY:", func, " ", curDelay, " ",  maxDelay, nodes)
    if isinstance(func, BinaryOperation):
        opDelay = getOpDelay(func.op)
        maxDelay1 = getMaxFunctionDelay(func.expr0, curDelay + opDelay, maxDelay, nodes)
        return getMaxFunctionDelay(func.expr1, curDelay + opDelay, maxDelay1, nodes)
    elif isinstance(func, UnaryOperation):
        opDelay = getOpDelay(func.op)
        return getMaxFunctionDelay(func.expr, curDelay + opDelay, maxDelay, nodes)
    elif isinstance(func, FunctionCall):
        curDelay += getFunctionDelay(func.source)
        if curDelay > maxDelay:
            return curDelay
        else:
            return maxDelay
    else:
        if curDelay > maxDelay:
            return curDelay
        return maxDelay

def getOpDelay(op):
    for stmt in spLib.TIMING.module.stmts:
        if isinstance(stmt, ContextDef):
            if stmt.identifier.name == "BasicTiming":
                for decl in stmt.decls:
                    for op0 in decl.suite.args[2].tensors:
                        log.spInfo(0, "Op Timing: ", op0)
                        if op == op0.op:
                            sci = decl.suite.args[1].name
                            if sci in spLib.SCINOTATION.keys():
                                log.spInfo(0, "Timing: ", op, " ",
                                           float(decl.suite.args[0].value) * spLib.SCINOTATION[sci]
                                           / spLib.SCINOTATION['Nano'])
                                return float(decl.suite.args[0].value) * spLib.SCINOTATION[sci] \
                                       / spLib.SCINOTATION['Nano']
    log.spError(log.SPError.UNDEFINE_TIMING_INFO, "Operator " + op + " has no timing info defined.")