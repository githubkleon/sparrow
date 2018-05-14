from backend.pySparrow.spParser.spParser import *
from backend.pySparrow.spOptimizer.spOptimizer import *
from backend.pySparrow.spConvertor.spConvertor import *
import backend.spLibrary as spLib
import os
import splog as log
from spdefines import sparrow_suffix

def compile(file_path, include_paths, project_path, exec_root):
    global spLib
    spLib.BASICS = loadLibrary("Basic", exec_root, include_paths)
    spLib.TIMING = loadLibrary("Timing", exec_root, include_paths)
    spLib.CONTEXT = loadLibrary("Context", exec_root, include_paths)
    sp_tree = buildTree(file_path, include_paths, project_path)
    sp_tree.preprocess()
    sp_tree.buildGraph()
    sp_tree.optimize()
    sp_conv = SparrowConvertor(sp_tree)
    sp_conv.convert()
    printCompiledFiles(sp_conv)

def loadLibrary(name, exec_root, include_paths):
    spHandler = SparrowHandler(os.path.join(os.path.join(exec_root, "library"), name + ".spr"), include_paths)
    spHandler.parse()
    return spHandler.getAST()

def buildTree(file_path, include_paths, project_path):
    log.spInfo(0, "BuildTree:" + file_path)
    spHandler = SparrowHandler(file_path, include_paths)
    spHandler.parse()
    log.spInfo(8, "Sparrow AST:", log.genAST(spHandler.getAST()))
    import_list = spHandler.getImportList()
    # print (import_list)
    scopelist = []
    for file in import_list:
        file.path = genAbsPath(file.path_list, project_path)
        file.scope_handle = buildTree(file.path, include_paths, project_path)
    return SparrowScope(file_path, spHandler, import_list)

def genAbsPath(pathlist, project_path):
    concatpath = ""
    for path in pathlist:
        concatpath = os.path.join(concatpath,path)
    project_relative_path = os.path.join(project_path, concatpath) + sparrow_suffix
    if (os.path.isfile(project_relative_path)):
        return project_relative_path
    log.spError(log.SPError.MODULE_NOT_FOUND_ERROR, concatpath + " : ")

def printCompiledFiles(result):
    pass

def integrate(file_path, project_path):
    sp_tree = buildTree(file_path, [], project_path)
    sp_tree.integrate()