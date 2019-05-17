#!/usr/bin/env python3

import argparse
import glob
import os
import re
import sys
from math import ceil
from unity_common import *


class Group:
    def __init__(self):
        self.file = None
        self.sources = []
        self.type = "cpp"

    def writeToDisk(self, type, unityDirectory):
        if type == 'cpp':
            mask = '/unity_%i.cpp'
        else:
            mask = '/unitymoc_%i.cpp'

        if not self.file:
            for i in range(99999):
                file = unityDirectory + (mask % (i))
                if not os.path.exists(file):
                    self.file = file
                    break

        fileContent = ""
        fileIncludes = []
        
        sourcesPathFromProject = [s.pathFromProject for s in self.sources]
        fileContent += "//ORIGINAL_PATH: " + "----".join(sourcesPathFromProject)
        fileContent += "\n\n"
        
        for source in self.sources:
            if type == 'cpp':
                fileIncludes.append('#include "%s"' % (source.RelativePath()))
            else:
                # Does not work with #pragma once and mingw...
                # grouping #include "moc_XXX.cpp" makes qmake not calling moc on XXX.h...
                
                # works well with include guards and mingw.
                
                # Todo : improve and create test cases
                # 2 cases : parent/subdir
                # 3 cases : normal/shadow/bin
                # 4 cases : raw, MOC_LVL_[0,1,2]                
                # moc_afile.h
                mocHeaderRelPath = source.FileName()
                dotIndex = mocHeaderRelPath.rfind('.')
                mocCppRelPath = mocHeaderRelPath
                if dotIndex >= 0:
                    mocCppRelPath = mocCppRelPath[0:dotIndex]
                
                # moc_afile.cpp
                mocCppRelPath = mocCppRelPath + ".cpp"
                fileIncludes.append('#include "%s"' % mocCppRelPath)
        
        fileContent += "\n".join(fileIncludes)
        fileContent += "\n"

        # we write only if the content has been modified
        fileOldContent = ''
        try:
            with open(self.file, encoding="utf-8") as file:
                fileOldContent = file.read()
        except:
            pass

        if fileOldContent != fileContent:
            #print("update " + str(len(fileOldContent)) + " " + str(len(fileContent)))
            with open(self.file, mode="w+", encoding="utf-8") as file:
                #print("write to : " + self.file)
                print(fileContent, end='', flush=True, file=file)
                
    def dump(self):
        sources = ", ".join([s.pathFromProject for s in self.sources])
        return "Group : " + os.path.basename(self.file) + ", type : " + self.type + ", sources : " + sources

    def removeFromDisk(self):
        file_remove(self.file)

    def mergeAsMainGroup(self, groupOther):
        #print("merge " + groupOther.file + " in " + self.file)
        self.sources.extend(groupOther.sources)
        groupOther.sources.clear()

    @staticmethod
    def removeDeletedSourceFiles(groupList, sourceList):
        # not optimized for big projects
        # sourceList = cpps or mocs
        
        sourceSet = set(sourceList)
        #print_dev(", ".join([s.pathFromProject for s in sourceSet]))
        
        for group in groupList:
            #print_dev("before : " + group.dump())
            group.sources[:] = [s for s in group.sources if s in sourceSet]
            #print_dev("after :  " + group.dump() + "\n")

        all_files_in_groups = set()
        for group in groupList:
            # remove the duplicated items from the existing group
            group.sources[:] = list(dict.fromkeys(group.sources))

            # remove the duplicated items shared by the already existing groups
            group.sources[:] = [s for s in group.sources if s not in all_files_in_groups]
            all_files_in_groups.update(group.sources)

    @staticmethod
    def addNewSourceFiles(groupList, sourceList, type, desiredGroupsSize):
        # common algorithm

        knownSourceSet = Group.getAllSourcesSetFromGroupList(groupList)
        newSourceList = [cpp for cpp in sourceList if cpp not in knownSourceSet]

        if not newSourceList:
            return

        nbNewSources = len(newSourceList)
        i = 0

        # fill not empty groups
        for group in groupList:
            while group.sources and len(group.sources) < desiredGroupsSize:
                group.sources.append(newSourceList[i])
                i += 1
                if i >= nbNewSources:
                    return

        # fill empty groups
        for group in groupList:
            while len(group.sources) < desiredGroupsSize:
                group.sources.append(newSourceList[i])
                i += 1
                if i >= nbNewSources:
                    return

        # create missing groups
        j = 0
        sources = []
        while i+j < nbNewSources:
            sources.append(newSourceList[i+j])
            j += 1
            if j % desiredGroupsSize == 0:
                g = Group()
                g.type = type
                # creates a copy of the list
                g.sources = list(sources)
                groupList.append(g)
                sources.clear()

        # create last group
        if sources:
            g = Group()
            g.type = type
            g.sources = list(sources)
            groupList.append(g)

    @staticmethod
    def deleteEmptyGroupsFromDisk(groupList):
        # common algorithm

        for group in groupList:
            if not group.sources:
                group.removeFromDisk()
                # we remove these groups from the list passed by parameter
        groupList[:] = [group for group in groupList if group.sources]

    @staticmethod
    def mergeLittleGroups(groupList, desiredGroupsSize):
        # common algorithm

        i = 1
        while i < len(groupList):
            group = groupList[i]
            for j in range(i):
                otherGroup = groupList[j]
                if len(group.sources) + len(otherGroup.sources) <= desiredGroupsSize:
                    if len(group.sources) > len(otherGroup.sources):
                        group.mergeAsMainGroup(otherGroup)
                        groupList.pop(j).removeFromDisk()
                    else:
                        otherGroup.mergeAsMainGroup(group)
                        groupList.pop(i).removeFromDisk()
                    break
            i += 1

    @staticmethod
    def writeGroupsToDisk(groupList, type, unityDirectory):
        # common algorithm

        for group in groupList:
            assert(len(group.sources) > 0)
            group.writeToDisk(type, unityDirectory)

    @staticmethod
    def readGroupsFromDirectory(unityDirectory, type):
        if type == 'cpp':
            mask = "unity_*.cpp"
        else:
            mask = "unitymoc_*.cpp"
        listFiles = glob.glob(unityDirectory + "/" + mask)
        listGroups = [Group.readGroupFromFile(file, type) for file in listFiles]
        #print_debug("Found groups : " + str(len(listGroups)))
        return listGroups

    @staticmethod
    def getAllSourcesSetFromGroupList(groupList):
        # common algorithm

        sourceSet = set()
        for group in groupList:
            sourceSet.update(group.sources)
        return sourceSet

    @staticmethod
    def readGroupFromFile(relPath, type):
        #cd = os.getcwd()
        #absPath = os.path.join(cd, relPath)
        group = Group();
        group.file = relPath
        group.type = type

        lines = []
        with open(relPath, encoding="utf-8") as file:
            lines = file.readlines()
        
        for line in lines:
            #includeRegexp = re.compile('^(\s)*#include(\s)*"(.*)"(\s)*$')
            #for line in lines:
            #    match = includeRegexp.match(line)
            #    if not match:
            #        continue
            #    include = match.group(3)
            
            # The idea here is to compare the source path exactly as expressed in the .pro file.
            if not line.startswith("//ORIGINAL_PATH: "):
                continue
            includes = line[len("// ORIGINAL_PATH:"):].strip().split("----")
            for include in includes:
                #print_debug("include : " + include)
                source = ProjectSourceFile(include)
                group.sources.append(source)
            
            break
        return group

    @staticmethod
    def writePriFile(groupList, unityPriFile, type, priWriteMode):
        with open(unityPriFile, mode=priWriteMode, encoding="utf-8") as file:
            groupFiles = [group.file for group in groupList]
            print("SOURCES += " + " ".join(groupFiles), file=file)

            # To remove a cpp file from qmake, you must type the exact same path as qmake passed it to this script through unitySources.txt
            if type == 'cpp':
                sourceFiles = [source.pathFromProject for group in groupList for source in group.sources]
                print("SOURCES -= " + " ".join(sourceFiles), file=file)



def generateUnityBuildFiles(unityPriFile, unityDirectory, mode, type, groupList, sourceList, desiredGroupsSize, priWriteMode):
        Group.removeDeletedSourceFiles(groupList, sourceList)
        if mode == "update":
            # updates the list of groups
            Group.addNewSourceFiles(groupList, sourceList, type, desiredGroupsSize)
        Group.deleteEmptyGroupsFromDisk(groupList)
        # merge groups and deletes the ones that are no longer necessary (empty)
        Group.mergeLittleGroups(groupList, desiredGroupsSize)
        Group.writeGroupsToDisk(groupList, type, unityDirectory)
        Group.writePriFile(groupList, unityPriFile, type, priWriteMode)

def getMocList(cppList):
    mocList = []
    for cpp in cppList:
        content = ''
        headerFilePath = cpp.pathFromProject.replace('.cpp', '.h')
        try:
            with open(headerFilePath, encoding="utf-8") as file:
                try:
                    content = file.read()
                except UnicodeDecodeError as err:
                    print_debug("unity - warning: Fichier pas encodé en UTF-8 :" + file.name)
                    continue
        except FileNotFoundError:
            continue

        if "Q_OBJECT" in content:
            moccedHeaderFileName = "moc_" + os.path.basename(headerFilePath)
            moccedHeaderFilePath = os.path.join(os.path.dirname(cpp.pathFromProject), moccedHeaderFileName)
            mocList.append(ProjectSourceFile(moccedHeaderFilePath))

    return mocList

usingNamespaceRegex = re.compile('using(\s)+namespace')
usingAllowedNamespaceRegex = re.compile('using(?:\s)+namespace(?:\s)+(.*);')
qtWindowsHeaderRegex = re.compile('#include(\s)+<qt_windows.h>')    

def removeIncompatibleSourcesFromList(cppList):
    global usingNamespaceRegex
    global usingAllowedNamespaceRegex
    global qtWindowsHeaderRegex
    
    res = []
    for cpp in cppList:
        content = ''

        if not cpp.pathFromProject.endswith('.cpp'):
            print_debug('unity - note : file not supported (not a cpp)  \"' + cpp.pathFromProject + '"')
            continue

        if not cpp.HasUtf8Content():
            print_debug("unity - warning: file not encoded in UTF-8 :" + cpp.pathFromProject)
            continue

        content = cpp.ReadContent()

        if qtWindowsHeaderRegex.search(content) != None:
            print_debug('unity - note: file not supported (header qt_windows.h) \"' + cpp.pathFromProject + '"')
            continue
        elif "@NO_UNITY" in content:
            continue
        elif "Q_DECLARE_PUBLIC" in content:
            print_debug('unity - note: file not supported (PIMPL) \"' + cpp.pathFromProject + '"')
            continue
        elif (not NAMESPACE_WHITELIST) and usingNamespaceRegex.search(content) != None:
            print_debug('unity - note: file not supported (using namespace) \"' + cpp.pathFromProject + '"')
            continue
        
        if NAMESPACE_WHITELIST:
            shouldContinue = False
            for namespace in usingAllowedNamespaceRegex.finditer(content):
                if namespace.group(1) not in NAMESPACE_WHITELIST:
                    print_debug('unity - note: file not supported (using namespace \"' + namespace.group(1) + '\") \"' + cpp.pathFromProject + '"')
                    shouldContinue = True
                    break
            if shouldContinue:
                continue
        
        res.append(cpp)
    return res


def argumentsCheck(mode, unityDirectory, strategy, cppList):
    assert mode in ["update","clear"], "Incorrect mode : " + mode
    if (mode != "clear"):
        assert strategy in ["incremental","per-processor","single-compilation-unit"], "Unknown strategy : " + strategy
    assert "unity" in unityDirectory, "The folder " + unityDirectory + " must contain the keyword 'unity'"
    assert os.path.exists(unityDirectory), "The folder " + unityDirectory + " doesn't exists. This error is probably the consequence of another error"
    cd = os.getcwd()
    assert os.path.realpath(unityDirectory) != os.path.realpath(cd), "The file 'unity.pri' must not be in the current folder !"

    for cpp in cppList:
        assert cpp.pathFromProject.endswith(".cpp") or cpp.pathFromProject.endswith('.c'), "Error : this file is not a CPP : " + cpp

def buildArgsParser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--mode', type=str, choices=('update', 'clear'))
    parser.add_argument('--strategy', default='incremental', choices=('incremental', 'per-processor', 'single-compilation-unit'),
                        help='Strategy for grouping files together')
    parser.add_argument('--tmpDir', type=str)
    parser.add_argument('--mocMode', type=str, choices=('MOC_LVL_0', 'MOC_LVL_1', 'MOC_LVL_2'), default='MOC_LVL_1')
    parser.add_argument('--sourceListPath', type=str)

    return parser
    
def main():
    try:
        # Must be executed from the project's source directory (which contains the .pro file)
        # print_dev("current dir : " + os.getcwd())
        cliArgs = buildArgsParser().parse_args()
        
        mode = cliArgs.mode
        strategy = cliArgs.strategy
        unityDirectory = os.path.normpath(cliArgs.tmpDir)
        unityPriFile = os.path.normpath(unityDirectory + "/unity.pri")
        mocMode = cliArgs.mocMode
        inputProjectCppListFile = cliArgs.sourceListPath

        projectCppListPath = []
        if inputProjectCppListFile is not None:
            assert os.path.exists(inputProjectCppListFile), "The sources file list doesn't exists : " + inputProjectCppListFile + ". This error is probably the consequence of another error."

            with open(inputProjectCppListFile) as file:
                projectCppListPath = utf8_file_read(file).replace('\r','').split("\n")

        projectCppListPath[:] = filter(None, projectCppListPath) # removes empty entries

        projectCppList = [ProjectSourceFile(cpp) for cpp in projectCppListPath]

        dupplicateCppFilesSet = ProjectSourceFile.GetDupplicatedFileNameList(projectCppList)
        if len(dupplicateCppFilesSet) > 0:
            raise InlineException("Error : these files are built twice : " + ", ".join(dupplicateCppFilesSet))

        argumentsCheck(mode, unityDirectory, strategy, projectCppList)
        cppList = removeIncompatibleSourcesFromList(projectCppList)
        mocList = getMocList(cppList)

        cppGroupList = Group.readGroupsFromDirectory(unityDirectory, 'cpp')
        mocGroupList = Group.readGroupsFromDirectory(unityDirectory, 'moc')

        if mode == "clear":
            for group in cppGroupList:
                group.removeFromDisk()
            for group in mocGroupList:
                group.removeFromDisk()
            with open(unityPriFile, mode="w+", encoding="utf-8") as file:
                print('', file=file)
            return

        cppGroupSize = 6
        if strategy == "incremental":
            if len(cppList) > 30:
                cppGroupSize = 8
            if len(cppList) > 100:
                cppGroupSize = 12
        elif strategy == "per-processor":
            cppGroupSize = ceil(len(cppList) / NB_PROCESSORS)
        else:
            cppGroupSize = len(cppList)

        generateUnityBuildFiles(unityPriFile, unityDirectory, mode, 'cpp', cppGroupList, cppList, cppGroupSize, "w+")
        
        if mocMode == 'MOC_LVL_1':
            # LVL_0 = no moc optimization
            # LVL_1 = moc files, the group them for CL step
            # LVL_2 = group moc calls before the CL step ; see unity_moc_headers
            generateUnityBuildFiles(unityPriFile, unityDirectory, mode, 'moc', mocGroupList, mocList, MOC_GROUPSIZE, "a")
        else:
            for group in mocGroupList:
                group.removeFromDisk()


    except InlineException as err:
        sys.stderr.write(err.message + "\n")
    except AssertionError as err:
        if len(err.args) >= 1:
            # If a message is present, we display it on one line
            sys.stderr.write(err.args[0] + "\n")
        else:
            # we display the stacktrace
            raise

if __name__ == "__main__":
    main()
