QT -= gui

CONFIG += c++11 console
CONFIG -= app_bundle

include(tasks/generated/generated.pri)

SOURCES += \
        $$PWD/factory.cpp \
        $$PWD/main.cpp \
        $$PWD/task.cpp \
        $$PWD/taskexecutor.cpp \
        $$PWD/tasks/good_namespace/tasknamespacea.cpp \
        tasks/good_namespace/tasknamespaceb.cpp \
        tasks/includeguardtask1.cpp \
        $$PWD/tasks/legacy_namespace/tasklegacynamespacea.cpp \
        tasks/legacy_namespace/tasklegacynamespaceb.cpp \
        tasks/singletask.cpp \
        tasks/task1.cpp \
        tasks/subtasks/subtask1.cpp \
        tasks/subtasks/subtask2.cpp \
        ../incrementalTest/tasks/task2.cpp

HEADERS += \
    $$PWD/factory.h \
    $$PWD/task.h \
    $$PWD/taskexecutor.h \
    $$PWD/tasks/good_namespace/tasknamespacea.h \
    tasks/good_namespace/tasknamespaceb.h \
    tasks/includeguardtask1.h \
    $$PWD/tasks/legacy_namespace/tasklegacynamespacea.h \
    tasks/legacy_namespace/tasklegacynamespaceb.h \
    tasks/singletask.h \
    tasks/task1.h \
    tasks/subtasks/subtask1.h \
    tasks/subtasks/subtask2.h \
    ../incrementalTest/tasks/task2.h

UNITY_BUILD = 1
UNITY_MOC_MODE = MOC_LVL_0
include(../../qmakeUnity/qmake_unity.pri)
