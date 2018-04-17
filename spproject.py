import json
import splog as log
import backend.spBackend as backend
import os
from spdefines import file_suffix, project_extension

project_info = {}
project_info['name'] = 'newproject'
project_info['hierarchy'] = {}
project_info['top'] = {}

def create(name, path):
    log.spInfo(9, "Creating project %s in %s"%(name, path))
    if (isProjectExisted(path)):
        log.spError(log.SPError.PROJECT_EXIST_ERROR)
    else:
        createProjectFile(name, path)

def addFile(file_path):
    abs_file_path = os.path.abspath(file_path)
    if not (isSupportedFileType(file_path)):
        log.spError(log.SPError.FILETYPE_NOT_SUPPORT_ERROR)
    project_root, project_hier, project_file_name = preprocessProject(file_path)
    updateHierarchy(project_root, abs_file_path, project_hier)
    createProjectFile(project_file_name, project_root)

def removeFile(file_path, all = False):
    abs_file_path = os.path.abspath(file_path)
    if not (isSupportedFileType(file_path)):
        log.spError(log.SPError.FILETYPE_NOT_SUPPORT_ERROR)
    project_root, project_hier, project_file_name = preprocessProject(file_path)
    removeHierarchy(project_root, abs_file_path, project_hier, all)
    createProjectFile(project_file_name, project_root)

def getTopFile():
    log.spInfo(9, "The top file is " + topFile())

def topFile():
    file_path = preprocessProject(getCWD())[0]
    file_list = project_info['top']
    if not file_list:
        log.spError(log.SPError.TOP_NOT_SET_ERROR)
    for i in range(len(file_list)):
        file_path = os.path.join(file_path, file_list[i])
    return file_path

def setTopFile(file_path):
    global project_info
    project_root, project_hier, project_file_name = preprocessProject(file_path)
    file_list = getFilePathList(project_root, os.path.abspath(file_path))
    if (isInProject(file_list, project_hier)):
        project_info['top'] = file_list
        log.spInfo(9, os.path.abspath(file_path) + " has been set as the top file.")
        createProjectFile(project_file_name, project_root)
    else:
        log.spWarning("File has not been added into project.")
    
def isInProject(file_list, hier, depth = 0):
    isLast = len(file_list) == depth + 1
    if (file_list[depth] in hier):
        if (isLast):
            return True
        else:
            return isInProject(file_list, hier[file_list[depth]], depth + 1)
    else:
        return False

def preprocessProject(file_path):
    global project_info
    project_root = getProjectRoot(getCWD())
    project_file_name = loadProjectFile(project_root)
    return project_root, project_info['hierarchy'], project_file_name

def addFolder(folder_path, all):
    for elem in preprocessFolder(folder_path):
        addFile(elem)
    if (all):
        for elem in getSubFolder(folder_path):
            addFolder(elem, True)

def removeFolder(folder_path, all):
    for elem in preprocessFolder(folder_path):
        removeFile(elem, all)
    if (all):
        for elem in getSubFolder(folder_path, not_empty = False): 
            removeFolder(elem, True)

def preprocessFolder(folder_path):
    filelist = []
    for i in os.listdir(folder_path):
        if (os.path.splitext(i)[1]) in file_suffix:
            filelist.append(os.path.join(folder_path, i))
    return filelist

def removeEmptyFolder(folder_path):
    abs_file_path = os.path.abspath(folder_path)
    project_root, project_hier, project_file_name = preprocessProject(folder_path)
    removeHierarchy(project_root, abs_file_path, project_hier)
    createProjectFile(project_file_name, project_root)

def getEmptyFolder(folder_path):
    folderlist = []
    for i in os.listdir(folder_path):
        sub_path = os.path.join(os.path.abspath(folder_path),i)
        if (os.path.isdir(sub_path)):
            if (len(os.listdir(sub_path)) == 0):
                folderlist.append(sub_path)
    return folderlist

def getSubFolder(folder_path, not_empty = False):
    folderlist = []
    for i in os.listdir(folder_path):
        sub_path = os.path.join(os.path.abspath(folder_path),i)
        if (os.path.isdir(sub_path)):
            if (not_empty):
                if (len(os.listdir(sub_path)) > 0):
                    folderlist.append(sub_path)
            else:
                folderlist.append(sub_path)
    return folderlist

def createProjectFile(name, path):
    filename = name + project_extension
    filepath = os.path.join(path,filename)
    with open(filepath, 'w') as project_file:
        json.dump(project_info, project_file)

def loadProjectFile(path):
    global project_info
    project_file_name = getProejctFileName(path)
    filename = project_file_name + project_extension
    filepath = os.path.join(path, filename)
    with open(filepath, 'r') as project_file:
        project_info = json.load(project_file)
    return project_file_name


def getProejctFileName(path):
    for i in os.listdir(path):
        # log.spDebug(os.path.splitext(i)[1])
        if os.path.splitext(i)[1] == project_extension:
            return os.path.splitext(i)[0]
    return ""

def isProjectExisted(path):
    for i in os.listdir(path):
        # log.spDebug(os.path.splitext(i)[1])
        if os.path.splitext(i)[1] == project_extension:
            return True
    return False

def getCWD():
    return os.getcwd()

def getProjectRoot(path):
    # log.spDebug("Searching " + path)
    if isProjectExisted(path):
        # log.spInfo(9, "Project is found in " + path)
        return path
    elif (os.path.split(path)[1] == ""):
        log.spError(log.SPError.PROJECT_NOT_FOUND_ERROR)
        return ""
    else:
        return getProjectRoot(os.path.split(path)[0])

def updateHierarchy(ref_path, path, hier):
    return buildHierarchy(hier, getFilePathList(ref_path, path), ref_path)

def removeHierarchy(ref_path, path, hier, all = False):
    return unbuildHierarchy(hier, getFilePathList(ref_path, path), ref_path, all)

def getFilePathList(ref_path, path):
    path_list = []
    path_list.append(os.path.split(path)[1])
    path_list = getFileHierarchy(ref_path, os.path.split(path)[0], path_list)
    path_list.reverse()
    return path_list

def getFileHierarchy(ref_path, path, path_list):
    if (ref_path == path):
        return path_list
    else:
        path_list.append(os.path.split(path)[1])
        path = os.path.split(path)[0]
        return getFileHierarchy(ref_path, path, path_list)

def buildHierarchy(hier, path_list, cur_path):
    currentHier = hier
    isLasts = [0] * (len(path_list) - 1)
    isLasts.append(1)
    for elem,isLast in zip(path_list, isLasts):
        # print (isLast)
        # print (currentHier)
        # print (elem)
        if elem in currentHier:
            if (isLast):
                log.spWarning(os.path.join(cur_path,elem) + " is already existed.")
        else:
            if (isLast):
                log.spInfo(9, os.path.join(cur_path,elem) + " is added.")
            currentHier[elem] = {}
        currentHier = currentHier[elem]
        cur_path = os.path.join(cur_path, elem)
    return hier

def unbuildHierarchy(hier, path_list, cur_path, all = False, depth = 0):
    currentHier = hier
    isLast = depth == (len(path_list)-1)
    elem = path_list[depth]
    if elem in currentHier:
        if (isLast):
            del currentHier[elem]
            log.spInfo(9, os.path.join(cur_path,elem) + " is deleted.")
            return
    else:
        log.spWarning(os.path.join(cur_path,elem) + " is not included in project.")
        return
    unbuildHierarchy (currentHier[path_list[depth]], path_list, os.path.join(cur_path, elem), all, depth + 1)
    if (all and not currentHier[elem]):
        del currentHier[elem]

def isSupportedFileType(path):
    # print (os.path.splitext(os.path.split(path)[1]))
    if os.path.splitext(os.path.split(path)[1])[1] in file_suffix:
        return True
    else:
        return False

def showHierarchy():
    project_hier = preprocessProject(getCWD)[1]
    # print (project_hier)
    printHierarchy(project_hier)

def printHierarchy(hier):
    # print (hier)
    print ("root")
    for elem in hier.items():
        printSubHierarchy(elem, 1)

def printSubHierarchy(hier, layer):
    # print (hier)
    # print (layer)
    space = '----' * layer
    # print (hier[0])
    if hier[1] == {}:
        print (space + hier[0])
    else:
        print (space + hier[0])

    if hier[1] == {}:
        return None
    else:
        for elem in hier[1].items():
            printSubHierarchy(elem, layer + 1)

def compile(verbose, include):
    log.spInfo(9, "Compiling " + topFile())
    backend.compile(topFile(), include, getProjectRoot(getCWD()), os.path.split(os.path.realpath(__file__))[0])