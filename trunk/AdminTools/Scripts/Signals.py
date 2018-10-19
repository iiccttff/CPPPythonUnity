from PyQt5 import QtCore


class Signals(QtCore.QObject):
    SocketConnect = QtCore.pyqtSignal(bool)
    SendMsg = QtCore.pyqtSignal(object)

    AccountVerifySucceedRes = QtCore.pyqtSignal(object)
    RoleLoginSucceedRes = QtCore.pyqtSignal(object)

    AnyRes = QtCore.pyqtSignal(object,object)

    QuerySvnLogs = QtCore.pyqtSignal(object,object)

    #ServerGoto = QtCore.pyqtSignal(str,str,int)

gSignals = Signals()