from backend.pySparrow.spParser.parser import SparrowParser
import backend.pySparrow.spOptimizer.astOperator as astOp

class SparrowHandler(object):
    def __init__(self, file_path, include_paths):
        self.file_path = file_path
        self.include_paths = include_paths
        self.parser = SparrowParser()
        self.ast = ()

    def parse(self):
        text = open(self.file_path).read()
        self.ast = self.parser.parse(text)

    def getDirectives(self):
        return self.directives

    def getAST(self):
        return self.ast

    def getImportList(self):
        return astOp.getImportList(self.ast)

