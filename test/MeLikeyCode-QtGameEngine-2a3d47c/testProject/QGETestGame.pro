include(../qge/qge.pri)
INCLUDEPATH += ../

TARGET = qgeTestGame # this is what our executable is called
TEMPLATE = app # make an executable (not static or dynamic lib)

#QMAKE_CXXFLAGS = -Wno-unused-parameter -Wno-reorder -Wno-sign-compare

SOURCES += \
    main.cpp \
    MyEventHandler.cpp \
    SpiderCreator.cpp \
    taste.cpp

HEADERS += \
    MyEventHandler.h \
    SpiderCreator.h \


DESTDIR = $$PWD/../bin/qgeTestGame
OBJECTS_DIR = $$PWD/../build/qgeTestGame
MOC_DIR = $$PWD/../build/qgeTestGame
RCC_DIR = $$PWD/../build/qgeTestGame
UI_DIR = $$PWD/../build/qgeTestGame
UNITY_TMP_DIR=$$clean_path($$PWD/../build/unity/)
UNITY_BUILD = 1
UNITY_MOC_MODE = MOC_LVL_1

include(../../../qmakeUnity/qmake_unity.pri)
