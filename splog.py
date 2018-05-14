from enum import Enum, auto
import os
import sys

DEBUG = True

LOG_PRIORITY = 0

class SPError(Enum):
    PROJECT_EXIST_ERROR = auto()
    PROJECT_NOT_FOUND_ERROR = auto()
    FILETYPE_NOT_SUPPORT_ERROR = auto()
    MODULE_NOT_FOUND_ERROR = auto()
    TOP_NOT_SET_ERROR = auto()
    MULTI_DRIVED_ERROR = auto()
    TYPE_NOT_MATCH_ERROR = auto()
    MULTI_DEFINED_ERROR = auto()
    CONSTRAINTS_NOT_MATCH_FUNCTION_ERROR = auto()
    CONSTRAINTS_MULTIPLE_OUTPUTS_ERROR = auto()
    FUNCTION_NOT_DEFINED_ERROR = auto()
    ASSOCIATIVITY_ERROR = auto()
    CANNOT_ASSOCIATE_ERROR = auto()
    ILLEGAL_EXPRESSION_ERROR = auto()
    ILLEGAL_OPERATOR_ERROR = auto()
    UNDEFINE_TIMING_INFO = auto()


projectExistError = "Project already existed."
projectNotFoundError = "Project is not found."
undefinedError = "Undefined Error."
moduleNotFoundError = "Module is not found."
fileTypeNotSupportError = "Unsupported file type."
topNotSetError = "Top file has not been set."
multiDrivedError = " is drived by two or more sources."
typeNotMatchError = "[Type not match] "
multiDefinedError = " has two or more definitions."
constraintsNotMatchError = " has an unmatched constraint."
constraintsMultipleOutputsError = " has multiple outputs."
functionNotFoundError = " is used but not defined."
associativityError = " have the same precedence but different associativity."
cannotAssociateError = " can not be associated."




def spError(errType, errContent=''):
    if (errType == SPError.PROJECT_EXIST_ERROR):
        printError(projectExistError)
    elif (errType == SPError.PROJECT_NOT_FOUND_ERROR):
        printError(projectNotFoundError)
    elif (errType == SPError.FILETYPE_NOT_SUPPORT_ERROR):
        printError(fileTypeNotSupportError)
    elif (errType == SPError.MODULE_NOT_FOUND_ERROR):
        printError(errContent + moduleNotFoundError)
    elif (errType == SPError.TOP_NOT_SET_ERROR):
        printError(topNotSetError)
    elif (errType == SPError.MULTI_DRIVED_ERROR):
        printError(errContent + multiDrivedError)
    elif (errType == SPError.TYPE_NOT_MATCH_ERROR):
        printError(typeNotMatchError + errContent)
    elif errType == SPError.MULTI_DEFINED_ERROR:
        printError(errContent + multiDefinedError)
    elif errType == SPError.CONSTRAINTS_NOT_MATCH_FUNCTION_ERROR:
        printError(errContent + constraintsNotMatchError)
    elif errType == SPError.CONSTRAINTS_MULTIPLE_OUTPUTS_ERROR:
        printError(errContent + constraintsMultipleOutputsError)
    elif errType == SPError.FUNCTION_NOT_DEFINED_ERROR:
        printError(errContent + functionNotFoundError)
    elif errType == SPError.ASSOCIATIVITY_ERROR:
        printError(errContent + associativityError)
    elif errType == SPError.CANNOT_ASSOCIATE_ERROR:
        printError(errContent + cannotAssociateError)
    elif errType == SPError.ILLEGAL_EXPRESSION_ERROR:
        printError("[Illegal Expression] Encounter an error when parsing operator " + errContent)
    elif errType == SPError.ILLEGAL_OPERATOR_ERROR:
        printError("[Illegal Operator] " + errContent + " has none or more than two input arguments.")
    elif errType == SPError.UNDEFINE_TIMING_INFO:
        printError(errContent)
    else:
        printError(undefinedError + errContent)


def printError(errContent):
    print("ERROR: " + errContent)
    sys.exit(1)


def spInfo(priority=0, info0 = "", info1 = "", info2="", info3="", info4="", info5="", info6=""):
    if priority >= LOG_PRIORITY:
        print("INFO: " + str(info0) + str(info1) + str(info2) + str(info3) + str(info4) + str(info5) + str(info6))


def spAST(info):
    print (genAST(info))


def genAST(info):
    output_string = str(info)
    indented_string = ""
    indent_len = 0
    for i in output_string:
        if i == '{':
            indent_len += 1
            indented_string += i + '\n' + indent_len * 4 * ' '
        elif i == '}':
            indent_len -= 1
            indented_string += i
        elif i == '[':
            # indent_len += 1
            indented_string += i
        elif i == ']':
            # indent_len -= 1
            indented_string += i
        elif i == '\n':
            indented_string += i + indent_len * 4 * ' '
        else:
            indented_string += i
    return indented_string

def spWarning(info):
    print("WARNING: " + info)

def spDebug(info):
    if DEBUG :
        print("DEBUG: " + info)
