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
        self.fileListing = None
        self.headers = []

    def writeToDisk(self, unityDirectory):
        # the generated header will be read by moc and by the C++ compiler
        mask = '/unityheader_%i.h'
        # to generate make dependencies and to be able to update the groups later
        # ex : unityheader_1.h: myHeader1.h myHeader2.h
        maskListing = '/unityheaderlisting_%i.txt'
        if not self.file:
            for i in range(9999):
                file = unityDirectory + (mask % (i))
                if not os.path.exists(file):
                    self.file = file
                    self.fileListing = unityDirectory + (maskListing % (i))
                    break

        '''
        #pragma once
        #ifdef Q_MOC_RUN
        // copy of HEADER 1
        // copy of HEADER 2
        // copy of HEADER 3
        #else
        #include "header1.h"
        #include "header2.h"
        #include "header3.h"
        #endif
        '''
        outputLines = []
        outputLines.append('#pragma once\n')

        # Include the headers files even if we paste their content bellow.
        # This helps with relative header includes.
        # Ex :
        # Lib1/core/core.h => #include "engine.h"
        # Lib1/core/engine.h
        # If there is no -I (include path) that contains core directory, the generated header file that contains both
        # cannot include engine.h (not in path), because it was taken from a subdirectory
        for header in self.headers:
            outputLines.append('#include "%s"' % (header.RelativePath()))

        outputLines.append('\n\n')
        outputLines.append('#ifdef Q_MOC_RUN\n')

        for header in self.headers:
            outputLines.append("// Copy of " + header.FileName() + "\n")
            outputLines.append(header.ReadContent())

        outputLines.append('\n\n#endif // Q_MOC_RUN')

        outputFileContent = '\n'.join(outputLines)
        outputFileContent += "\n"

        # we write only if the content has been modified
        fileOldContent = ''
        try:
            with open(self.file, encoding="utf-8") as file:
                fileOldContent = file.read()
        except:
            pass

        if fileOldContent != outputFileContent:
            #print("update " + str(len(fileOldContent)) + " " + str(len(fileContent)))
            with open(self.file, mode="w+", encoding="utf-8") as file:
                #print("write to : " + self.file)
                print(outputFileContent, end='', flush=True, file=file)

        with open(self.fileListing, mode="w+", encoding="utf-8") as file:
            headersPath = [header.pathFromProject for header in self.headers]
            print("\n".join(headersPath), end='', flush=True, file=file)


    def removeFromDisk(self):
        file_remove(self.file)
        file_remove(self.fileListing)

    def mergeAsMainGroup(self, groupOther):
        #print("merge " + groupOther.file + " in " + self.file)
        self.headers.extend(groupOther.headers)
        groupOther.headers.clear()

    @staticmethod
    def removeDeletedHeaderFiles(groupList, headerList):
        # this function is not optimized for big projects
        headerSet = set(headerList)
        for group in groupList:
            group.headers[:] = [header for header in group.headers if header in headerSet]

        all_files_in_groups = set()
        for group in groupList:
            # delete the duplicated elements in the existing group
            group.headers[:] = list(dict.fromkeys(group.headers))

            # delete the duplicated elements that belong to different existing groups
            group.headers[:] = [header for header in group.headers if header not in all_files_in_groups]
            all_files_in_groups.update(group.headers)

    @staticmethod
    def addNewHeaderFiles(groupList, headerList, desiredGroupsSize):
        # common algorithm

        knownHeaderSet = Group.getAllHeadersSetFromGroupList(groupList)
        newHeaderList = [header for header in headerList if header not in knownHeaderSet]

        if not newHeaderList:
            return

        nbNewHeaders = len(newHeaderList)
        i = 0

        # fill not empty groups
        for group in groupList:
            while group.headers and len(group.headers) < desiredGroupsSize:
                group.headers.append(newHeaderList[i])
                i += 1
                if i >= nbNewHeaders:
                    return

        # fill empty groups
        for group in groupList:
            while len(group.headers) < desiredGroupsSize:
                group.headers.append(newHeaderList[i])
                i += 1
                if i >= nbNewHeaders:
                    return

        # create missing groups
        j = 0
        headers = []
        while i+j < nbNewHeaders:
            headers.append(newHeaderList[i+j])
            j += 1
            if j % desiredGroupsSize == 0:
                g = Group()
                # creates a copy of the list
                g.headers = list(headers)
                groupList.append(g)
                headers.clear()

        # create last group
        if headers:
            g = Group()
            g.headers = list(headers)
            groupList.append(g)

    @staticmethod
    def deleteEmptyGroupsFromDisk(groupList):
        # common algorithm

        for group in groupList:
            if not group.headers:
                group.removeFromDisk()
        # we remove these groups from the list passed by parameter
        groupList[:] = [group for group in groupList if group.headers]

    @staticmethod
    def mergeLittleGroups(groupList, desiredGroupsSize):
        # common algorithm

        i = 1
        while i < len(groupList):
            group = groupList[i]
            for j in range(i):
                otherGroup = groupList[j]
                if len(group.headers) + len(otherGroup.headers) <= desiredGroupsSize:
                    if len(group.headers) > len(otherGroup.headers):
                        group.mergeAsMainGroup(otherGroup)
                        groupList.pop(j).removeFromDisk()
                    else:
                        otherGroup.mergeAsMainGroup(group)
                        groupList.pop(i).removeFromDisk()
                    break
            i += 1

    @staticmethod
    def writeGroupsToDisk(groupList, unityDirectory):
        # common algorithm

        for group in groupList:
            assert(len(group.headers) > 0)
            group.writeToDisk(unityDirectory)

    @staticmethod
    def readGroupsFromDirectory(unityDirectory):
        mask = "unityheader_*.h"
        maskListing = "unityheaderlisting_*.txt"

        fileList = glob.glob(unityDirectory + "/" + mask)
        fileListingList = glob.glob(unityDirectory + "/" + maskListing)
        listGroups = [Group.readGroupFromListingFile(fileListing) for fileListing in fileListingList]

        knownFileSet = set([g.file for g in listGroups])
        knownListingFileSet = set([g.fileListing for g in listGroups])

        # delete malformed groups (header but no listing and the contrary)
        for file in fileList:
            if file not in knownFileSet:
                file_remove(file)

        for file in fileListingList:
            if file not in knownListingFileSet:
                file_remove(file)

        #print_debug("Found groups : " + str(len(listGroups)))
        return listGroups

    @staticmethod
    def getAllHeadersSetFromGroupList(groupList):
        # common algorithm

        headerSet = set()
        for group in groupList:
            headerSet.update(group.headers)
        return headerSet

    @staticmethod
    def readGroupFromListingFile(relPath):
        group = Group();
        group.fileListing = relPath
        group.file = relPath.replace('listing', '').replace(".txt", ".h")

        #cd = os.getcwd()
        #absPath = os.path.join(cd, relPath)
        lines = []
        with open(group.fileListing, encoding="utf-8") as file:
            lines = utf8_file_readlines(file)

        for line in lines:
            line = line.replace("\n","")
            if line:
                header = ProjectSourceFile(line)
                group.headers.append(header)
        return group

    @staticmethod
    def writePriFile(groupList, unityPriFile, priWriteMode):
        with open(unityPriFile, mode=priWriteMode, encoding="utf-8") as file:
            # add merged headers to the build
            groupFiles = [group.file for group in groupList]
            print("HEADERS += " + " ".join(groupFiles), file=file)

            # Remove original headers that has been merged from the build
            # To remove a header file from qmake, you must type the exact same path as qmake passed it to this script through unityHeaders.txt
            headerFiles = [header.pathFromProject for group in groupList for header in group.headers]
            print("HEADERS -= " + " ".join(headerFiles), file=file)

            for group in groupList:
                # add makefile custom targets to maintain merged header state

                # Ex : unityheader_0
                commandName = os.path.basename(group.file).replace(".h","")
                relPathToGroup = os.path.relpath(group.file)
                relPathToGroupListing = os.path.relpath(group.fileListing)
                thisScriptPath = os.path.realpath(__file__)
                commandScript = 'python ' + thisScriptPath + ' --mode update_group --groupFileListing ' + relPathToGroupListing

                command = []
                command.append('%s.target = %s' % (commandName, relPathToGroup))
                command.append('%s.depends = %s' % (commandName, ' '.join([header.AbsolutePath() for header in group.headers])))
                command.append('%s.commands = cd %s & %s' % (commandName, os.getcwd(), commandScript))
                command.append('QMAKE_EXTRA_TARGETS *= %s' % commandName)
                command.append('')
                print('\n'.join(command), file=file)


def generateUnityBuildFiles(unityPriFile, unityDirectory, groupList, headerList, desiredGroupsSize, priWriteMode):
        Group.removeDeletedHeaderFiles(groupList, headerList)
        Group.addNewHeaderFiles(groupList, headerList, desiredGroupsSize)
        Group.deleteEmptyGroupsFromDisk(groupList)
        # merge groups and delete the ones that are no more usefull (empty ones)
        Group.mergeLittleGroups(groupList, desiredGroupsSize)
        Group.writeGroupsToDisk(groupList, unityDirectory)
        Group.writePriFile(groupList, unityPriFile, priWriteMode)


def removeIncompatibleHeadersFromList(headerList):
    usingNamespaceRegex = re.compile('using(\s)+namespace')

    res = []
    for header in headerList:
        if not header.pathFromProject.endswith('.h'):
            # We don't try to support hpp (templates)
            print_debug('unity - note : file not supported (not a header)  \"' + header.pathFromProject + '"')
            continue

        if not header.HasUtf8Content():
            print_debug("unity - warning: File not encoded in UTF-8 :" + header.pathFromProject)
            continue

        content = header.ReadContent()

        if "Q_OBJECT" not in content:
            continue
        elif "@NO_UNITY" in content:
            continue
        elif "#pragma once" not in content:
            print_debug('unity - note: file not supported (missing pragma once) \"' + header.pathFromProject + '"')
            continue
        elif "Q_DECLARE_PRIVATE" in content:
            print_debug('unity - note: file not supported (PIMPL) \"' + header.pathFromProject + '"')
            continue
        elif usingNamespaceRegex.search(content) != None:
            print_debug('unity - note: file not supported (using namespace) \"' + header.pathFromProject + '"')
            continue
        else:
            res.append(header)

    return res


def argumentsCheckModeGenerateGroups(unityDirectory, projectHeaderList):
    assert "unity" in unityDirectory, "The folder " + unityDirectory + " must contain the keyword 'unity'"
    assert os.path.exists(unityDirectory), "The folder " + unityDirectory + " doesn't exists. This error is probably the consequence of another error"
    cd = os.getcwd()
    assert os.path.realpath(unityDirectory) != os.path.realpath(cd), "The file 'unity.pri' must not be in the current folder !"

    for header in projectHeaderList:
        assert header.pathFromProject.endswith(".h") or header.pathFromProject.endswith('.hpp'), "Error : this file is not a header : " + header.pathFromProject

def buildArgsParser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--mode', type=str, choices=('update_group', 'generate_groups'))
    parser.add_argument('--headerListPath', type=str)
    parser.add_argument('--groupFileListing', type=str)

    return parser

def main():
    # must be executed from the project's source directory (which contains the .pro file)
    # print_dev("current dir : " + os.getcwd())
    cliArgs = buildArgsParser().parse_args()

    try:
        mode = cliArgs.mode
        inputProjectHeaderListFile = cliArgs.headerListPath
        groupFileListing = cliArgs.groupFileListing
        
        if mode == 'generate_groups':
            # file that contains the content qmake "HEADERS" variable
            assert os.path.exists(inputProjectHeaderListFile), "The headers file list doesn't exists : " + inputProjectHeaderListFile + ". This error is probably the consequence of another error."

            with open(inputProjectHeaderListFile) as file:
                projectHeaderListPath = utf8_file_read(file).replace('\r','').split("\n")
            projectHeaderListPath[:] = filter(None, projectHeaderListPath) # removes empty entries

            projectHeaderList = [ProjectSourceFile(header) for header in projectHeaderListPath]
            unityDirectory = os.path.dirname(inputProjectHeaderListFile)
            unityPriFile = os.path.normpath(unityDirectory + "/unity_headers.pri")

            dupplicateHeaderFilesSet = ProjectSourceFile.GetDupplicatedFileNameList(projectHeaderList)
            if len(dupplicateHeaderFilesSet) > 0:
                raise InlineException("Error : these files are build twice : " + ", ".join(dupplicateHeaderFilesSet))

            argumentsCheckModeGenerateGroups(unityDirectory, projectHeaderList)
            headerList = removeIncompatibleHeadersFromList(projectHeaderList)

            headerGroupList = Group.readGroupsFromDirectory(unityDirectory)
            headerGroupSize = MOC_GROUPSIZE

            generateUnityBuildFiles(unityPriFile, unityDirectory, headerGroupList, headerList, headerGroupSize, "w+")

        if mode == 'update_group':
            unityDirectory = os.path.dirname(groupFileListing)
            group = Group.readGroupFromListingFile(groupFileListing)
            assert(len(group.headers) > 0)
            group.writeToDisk(unityDirectory)



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
