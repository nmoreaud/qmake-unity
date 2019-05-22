import os
import sys
from unity_config import *

# private config options
LOG_DEV = False

class InlineException(Exception):
    def __init__(self, message):
        self.message = message

def utf8_file_readlines(file):
    try:
        return file.readlines()
    except UnicodeDecodeError:
        raise InlineException("unity - note: File not encoded in UTF-8 :" + file.name)

def utf8_file_read(file):
    try:
        return file.read()
    except UnicodeDecodeError:
        raise InlineException("unity - note: File not encoded in UTF-8 :" + file.name)

def file_remove(filePath):
    if SAFE_MODE:
        print_debug('SAFE MODE - simulate delete file "' + filePath + '" (' + os.path.abspath(filePath) + ')', True)
    else:
        os.remove(filePath)

def print_dev(msg):
    if LOG_DEV:
        print("dev - " + msg)
        
def print_debug(msg, forced = False):
    if LOG_DEBUG or forced:
        #print("debug - " + msg)
        sys.stderr.write("debug - " + msg + "\n")


def get_duplicated_elements(l):
    seen = set()
    seen_add = seen.add
    # adds all elements it doesn't know yet to seen and all other to seen_twice
    seen_twice = set( x for x in l if x in seen or seen_add(x) )
    # turn the set into a list (as requested)
    return seen_twice



class ProjectSourceFile:
    def __init__(self, pathFromProject):
        assert isinstance(pathFromProject, str)
        self.pathFromProject = pathFromProject
        self.relPath = None
        self.absPath = None
        self.content = None

    def ReadContent(self):
        if not self.content:
            with open(self.pathFromProject, encoding="utf-8") as file:
                self.content = file.read()
        return self.content

    def HasUtf8Content(self):
        if self.content:
            return True
        try:
            self.ReadContent()
            return True
        except UnicodeDecodeError as err:
            return False

    def FileName(self):
        return os.path.basename(self.pathFromProject)

    def AbsolutePath(self):
        if not self.absPath:
            self.absPath = os.path.abspath(self.pathFromProject).replace("\\", "/")
        return self.absPath

    def RelativePath(self):
        if not self.relPath:
            self.relPath = os.path.relpath(self.pathFromProject).replace("\\", "/")
        return self.relPath

    def __hash__(self):
        return hash(self.pathFromProject)

    def __eq__(self, other):
        #print_dev('test eq "' + self.pathFromProject + '", "' + other.pathFromProject + '"')
        return self.pathFromProject == other.pathFromProject
    
    @staticmethod
    def GetDupplicatedFileNameList(headerList):
        headerRelPathList = [header.RelativePath() for header in headerList]
        return get_duplicated_elements(headerRelPathList)
