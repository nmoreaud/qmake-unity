#!/usr/bin/env python3

import os
import sys



def GenerateTask(idTask):
    cppTemplate = ""
    with open("template/task.cpp.tpl") as file:
        cppTemplate = file.read()

    headerTemplate = ""
    with open("template/task.h.tpl") as file:
        headerTemplate = file.read()
    
    cppTemplate = cppTemplate.replace("XXX", str(idTask))
    headerTemplate = headerTemplate.replace("XXX", str(idTask))
    
    cppDest = f"generatedtask_{idTask}.cpp"
    headerDest = f"generatedtask_{idTask}.h"

    with open(cppDest, mode="w+", encoding="utf-8") as file:
        print(cppTemplate, flush=True, file=file)

    with open(headerDest, mode="w+", encoding="utf-8") as file:
        print(headerTemplate, flush=True, file=file)        
    
def GenerateTasks(nbTasks):
    for i in range(nbTasks):
        GenerateTask(i)
    CreatePriFile(nbTasks)

def CreatePriFile(nbTasks):
    content = "SOURCES += \\\n"
    
    sources = []
    for idTask in range(nbTasks):
        sources.append(f"    $$PWD/generatedtask_{idTask}.cpp")
    content += " \\\n".join(sources)
    
    content += "\n\n"
    content += "HEADERS += \\\n"
    headers = []
    for idTask in range(nbTasks):
        headers.append(f"    $$PWD/generatedtask_{idTask}.h")
    content += " \\\n".join(headers)
        
    with open("generated.pri", mode="w+", encoding="utf-8") as file:
        print(content, flush=True, file=file)        
    


GenerateTasks(int(sys.argv[1]))