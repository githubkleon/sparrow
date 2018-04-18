import backend.pySparrow.spOptimizer.astOperator as astOp
import backend.pySparrow.spConvertor.spConvertor as spConv
import backend.pySparrow.spOptimizer.astPipeline as pipe
import splog as log


class SparrowScope:
    def __init__(self, abspath, handler, import_list):
        self.abspath = abspath
        self.result = None
        self.handler = handler
        self.scopes = import_list

    def __repr__(self):
        return "abspath=%r,handler=%r,scope=%r"%(self.abspath, self.handler, self.scopes)

    """
    Preprocess
    """
    def preprocess(self):
        log.spInfo(9, "Preprocessing...")
        astOp.traceParameter(self.handler.ast)
        astOp.expandGenStructures(self.handler.ast)
        astOp.setClockReset(self.handler.ast)
        log.spInfo(7, log.genAST(self.handler.ast))

    """
    Check 
    """
    def buildGraph(self):
        containers = astOp.getContainerList(self.handler.ast)
        for con in containers:
            astOp.expandBuses(con)
        log.spInfo(7, self.handler.ast)
        for con in containers:
            # slaves, inputs = astOp.getSourceList(con)
            masters, outputs = astOp.getDrainList(con)
            for output in outputs:
                astOp.tracebackdrain(output, con, self.handler.ast)

    """
    Optimize
    """
    def optimize(self):
        containers = astOp.getContainerList(self.handler.ast)
        for con in containers:
            pipe.pipelineContainer(self.handler.ast, con)
        log.spInfo(0, "CONTAINERS", containers)
        log.spInfo(9, "Optimizing...")