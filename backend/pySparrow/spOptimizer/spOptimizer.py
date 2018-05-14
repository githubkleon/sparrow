import backend.pySparrow.spOptimizer.astOperator as astOp
import backend.pySparrow.spConvertor.spConvertor as spConv
import backend.pySparrow.spOptimizer.astPipeline as pipe
import splog as log
import backend.hparser as hp


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
        log.spInfo(7, "Sparrow AST Before Preprocess", log.genAST(self.handler.ast))
        astOp.traceParameter(self.handler.ast)
        log.spInfo(7, "Sparrow AST After Trace Parameter", log.genAST(self.handler.ast))
        astOp.expandGenStructures(self.handler.ast)
        log.spInfo(7, "Sparrow AST After expandGen", log.genAST(self.handler.ast))
        astOp.setClockReset(self.handler.ast)
        log.spInfo(7, "Sparrow AST After Preprocess", log.genAST(self.handler.ast))

    """
    Check 
    """
    def buildGraph(self):
        containers = astOp.getContainerList(self.handler.ast)
        for con in containers:
            astOp.expandBuses(con)
        log.spInfo(7, "Sparrow AST Before Tracing Back", log.genAST(self.handler.ast))
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


    """
    Check interface
    """
    def integrate(self):
        interfaces = astOp.getInterfaceList(self.handler.ast)
        if len(interfaces) > 1:
            log.spError(log.SPError.MULTI_DEFINED_ERROR, "You MUST specify only one interface.")
        elif not interfaces:
            log.spInfo(9, "No interface defined.")
        else:
            log.spInfo(0, "Interface ", interfaces[0])
            parser_name = interfaces[0].name.name
            print (parser_name)
            if interfaces[0].inherit.name == "simple_axis":
                typedef = astOp.getTypeDefinition(self.handler.ast, interfaces[0].buses.interface)
                header, parser_vector = astOp.genParseVector(typedef)
                log.spInfo(0, "HEADER:", header, "parserVec:", parser_vector)
                hp.genIntegration(parser_name=parser_name, header=header/8, data_width=8, data_length_str="length",
                                  data_protocol="AXIS", data_endian="big", parser_vector=parser_vector)

