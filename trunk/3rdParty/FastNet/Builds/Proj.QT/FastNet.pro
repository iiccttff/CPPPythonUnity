#-------------------------------------------------
#
# Project created by QtCreator 2018-01-24T12:24:03
#
#-------------------------------------------------

QT       -= core gui

TARGET = FastNet
TEMPLATE = lib

DEFINES += FASTNET_LIBRARY FASTNET_EXPORTS BOOST_ALL_DYN_LINK

CONFIG+=debug_and_release


CONFIG(debug, debug|release) {
	DESTDIR = $$PWD/../../Bin/Ubuntu/Debug
	DEFINES += DEBUG
}
CONFIG(release, debug|release) {
	DESTDIR = $$PWD/../../Bin/Ubuntu/Release
}


CONFIG += c++11 

# The following define makes your compiler emit warnings if you use
# any feature of Qt which as been marked as deprecated (the exact warnings
# depend on your compiler). Please consult the documentation of the
# deprecated API in order to know how to port your code away from it.
DEFINES += QT_DEPRECATED_WARNINGS

# You can also make your code fail to compile if you use deprecated APIs.
# In order to do so, uncomment the following line.
# You can also select to disable deprecated APIs only up to a certain version of Qt.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0


unix {
    target.path = /usr/lib
    INSTALLS += target
}

HEADERS += \
    ../../Include/FastNet/core/App.h \
    ../../Include/FastNet/core/Callback.h \
    ../../Include/FastNet/core/Cfg.h \
    ../../Include/FastNet/core/ClassFactory.h \
    ../../Include/FastNet/core/Client.h \
    ../../Include/FastNet/core/Defs.h \
    ../../Include/FastNet/core/Helper.h \
    ../../Include/FastNet/core/Log.h \
	../../Include/FastNet/core/Message.h \
    ../../Include/FastNet/core/Object.h \
    ../../Include/FastNet/core/Server.h \
    ../../Include/FastNet/core/Session.h \
    ../../Include/FastNet/core/Singleton.h \
    ../../Include/FastNet/core/Socket.h \
    ../../Include/FastNet/core/Stream.h \
    ../../Include/FastNet/core/Types.h \
    ../../Include/FastNet/global/Global.h \
    ../../Include/FastNet/global/GlobalManager.h \
    ../../Include/FastNet/module/Module.h \
    ../../Include/FastNet/pkt/protocols.h \
    ../../Include/FastNet/role/Role.h \
    ../../Include/FastNet/role/RoleManager.h \
    ../../Include/FastNet/role/RoleModule.h \
    ../../Include/FastNet/room/Room.h \
    ../../Include/FastNet/room/RoomManager.h \
    ../../Include/FastNet/store/Store.h \
    ../../Include/FastNet/store/StoreManager.h \
    ../../Include/FastNet/timer/Timer.h \
    ../../Include/FastNet/timer/TimerImpl.h \
    ../../Include/FastNet/timer/TimerManager.h \
    ../../Include/FastNet/FastNet.h

SOURCES += \
    ../../Include/FastNet/core/App.cpp \
    ../../Include/FastNet/core/Callback.cpp \
    ../../Include/FastNet/core/ClassFactory.cpp \
    ../../Include/FastNet/core/Client.cpp \
    ../../Include/FastNet/core/Helper.cpp \
    ../../Include/FastNet/core/Log.cpp \
    ../../Include/FastNet/core/Message.cpp \
    ../../Include/FastNet/core/Object.cpp \
    ../../Include/FastNet/core/Server.cpp \
    ../../Include/FastNet/core/Session.cpp \
    ../../Include/FastNet/core/Socket.cpp \
    ../../Include/FastNet/core/Stream.cpp \
    ../../Include/FastNet/global/Global.cpp \
    ../../Include/FastNet/global/GlobalManager.cpp \
    ../../Include/FastNet/module/Module.cpp \
    ../../Include/FastNet/pkt/protocols.cpp \
    ../../Include/FastNet/role/Role.cpp \
    ../../Include/FastNet/role/RoleManager.cpp \
    ../../Include/FastNet/role/RoleModule.cpp \
    ../../Include/FastNet/room/Room.cpp \
    ../../Include/FastNet/room/RoomManager.cpp \
    ../../Include/FastNet/store/Store.cpp \
    ../../Include/FastNet/store/StoreManager.cpp \
    ../../Include/FastNet/timer/Timer.cpp \
    ../../Include/FastNet/timer/TimerManager.cpp \
    ../../Include/FastNet/FastNet.cpp


#unix: LIBS += -L$$PWD/../../3rdParty/boost_1_65_1/OutLibs/Linux/ -lboost_atomic-vc140-mt-1_65_1

INCLUDEPATH += $$PWD/../../3rdParty/boost_1_65_1
DEPENDPATH += $$PWD/../../3rdParty/boost_1_65_1

INCLUDEPATH += $$PWD/../../3rdParty/poco-1.7.9-all/Foundation/include
DEPENDPATH += $$PWD/../../3rdParty/poco-1.7.9-all/Foundation/include

INCLUDEPATH += $$PWD/../../3rdParty/poco-1.7.9-all/Data/include
DEPENDPATH += $$PWD/../../3rdParty/poco-1.7.9-all/Data/include

INCLUDEPATH += $$PWD/../../3rdParty/poco-1.7.9-all/Data/SQLite/include
DEPENDPATH += $$PWD/../../3rdParty/poco-1.7.9-all/Data/SQLite/include

INCLUDEPATH += $$PWD/../../Include
DEPENDPATH += $$PWD/../../Include

INCLUDEPATH += /usr/include/python2.7
DEPENDPATH += /usr/include/python2.7

unix: LIBS += -lpthread -lssl -lcrypto
unix: LIBS += -L$$PWD/../../3rdParty/boost_1_65_1/OutLibs/Ubuntu
unix: LIBS += -L$$PWD/../../3rdParty/poco-1.7.9-all/OutLibs/Ubuntu

unix: LIBS += -lboost_python -Wl,-rpath,../3rdParty/FastNet/3rdParty/boost_1_65_1/OutLibs/Ubuntu/ 
unix: LIBS += -lboost_random -Wl,-rpath,../3rdParty/FastNet/3rdParty/boost_1_65_1/OutLibs/Ubuntu/
unix: LIBS += -lboost_thread -Wl,-rpath,../3rdParty/FastNet/3rdParty/boost_1_65_1/OutLibs/Ubuntu/

unix:CONFIG(release, debug|release): LIBS += -lPocoFoundation -Wl,-rpath,../3rdParty/FastNet/3rdParty/poco-1.7.9-all/OutLibs/Ubuntu/ 
unix:CONFIG(release, debug|release): LIBS += -lPocoData -Wl,-rpath,../3rdParty/FastNet/3rdParty/poco-1.7.9-all/OutLibs/Ubuntu 
unix:CONFIG(release, debug|release): LIBS += -lPocoDataSQLite -Wl,-rpath,../3rdParty/FastNet/3rdParty/poco-1.7.9-all/OutLibs/Ubuntu

unix:CONFIG(debug, debug|release): LIBS += -lPocoFoundationd -Wl,-rpath,../3rdParty/FastNet/3rdParty/poco-1.7.9-all/OutLibs/Ubuntu
unix:CONFIG(debug, debug|release): LIBS += -lPocoDatad -Wl,-rpath,../3rdParty/FastNet/3rdParty/poco-1.7.9-all/OutLibs/Ubuntu
unix:CONFIG(debug, debug|release): LIBS += -lPocoDataSQLited -Wl,-rpath,../3rdParty/FastNet/3rdParty/poco-1.7.9-all/OutLibs/Ubuntu

