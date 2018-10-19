# -*- coding: utf-8 -*-
import FastNet, pkt
import Signals
from PyQt5 import QtCore, QtWidgets, uic
import Client
import App
import LoginDialog
import time
import hashlib
import requests
import json
import tabs.PythonHighlighter
import importlib


class MainWindow(QtWidgets.QMainWindow):

    def WriteLog(self, log):
        msg = "{} - {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), log)
        self.textEditOutLog.append("<a style='color: black;'>{}</a>".format(msg))

    def WriteErrorLog(self, log):
        msg = "{} - {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), log)
        self.textEditOutLog.append("<a style='color: red;'>{}</a>".format(msg))

    def timerEvent(self, event):
        App.App.Instance.Update()

    def closeEvent(self, event):

        for v in self.tabs.values():
            if hasattr(v,'OnDestory'):
                v.OnDestory()

        #self.timer.Stop()
        #self.timer = None

        App.App.Instance.Settings.setValue("MainWindow/Geometry", self.saveGeometry())

        if self.tabWidget.currentIndex() > -1:
            App.App.Instance.Settings.setValue('MainWindow/currentTabText',
                                               self.tabWidget.tabText(self.tabWidget.currentIndex()))

        self.killTimer(self.m_timerID)

        self.isClose = True
        self.loginDialog.destroy()

        if self.client is not None:
            self.client.Close()
            self.client = None

        event.accept()

    def OnSocketConnect(self, v):

        if v is False:
            if self.isClose is False:
                if QtWidgets.QMessageBox.Yes == \
                        QtWidgets.QMessageBox.critical(self, '网络错误', '连接服务器失败,是否重试?',
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Yes):
                    #self.client.ReConnect()

                    cfgs = App.App.Instance.Cfgs['Client']
                    self.client.Connect(str(cfgs['serverAddress']), 0,"",cfgs['serverId'],True)
                else:
                    self.close()
        else:
            if self.client.IsGateServer is False:
                self.WriteLog('连接登录服务器成功!')
                self.ShowLoginDialog()
            else:
                self.WriteLog('连接管理服务器成功!')

    @property
    def TabValues(self):
        return self.tabValues

    @property
    def Tabs(self):
        return self.tabs

    def GetTab(self, name):
        if name in self.tabs:
            return self.tabs[name]
        return None

    def OnAnyRes(self, classId, data):

        if classId in self.tabs:
            self.tabs[classId].RefreshData(data)
        else:
            print(data)
            self.WriteLog('没找到标签页 {} {}'.format(classId,self.tabs))


    def OnAccountVerifySucceedRes(self, role_id):
        self.WriteLog('账号验证成功!')
        self.WriteLog('现在进行登录...')
        self.client.RoleLogin(role_id)
        self.roleId = role_id


    def OnRoleLoginSucceedRes(self, message):        
        self.WriteLog('帐号登录成功!')
        self.setWindowTitle("后台管理工具 - " + message.name)
        #self.uid = message.uid 
        self.name = message.name

        
        self.tabValues = {}
        
        for v in self.tabs.values():
            v.deleteLater()

        self.tabs = {}
        self.tabWidget.clear()

        tabValues = json.loads(message.tabs)
        for k, v in tabValues.items():
            
            self.tabValues[k] = v

            m = importlib.import_module('tabs.{}'.format(k))
            importlib.reload(m)
            widget = eval('m.{}(self.tabWidget,v[1])'.format(k))
            
            self.tabs[k] = widget

            if v[0] == True:
                self.tabWidget.addTab(widget, widget.windowTitle())
            else:
                widget.hide()

        currentTabText = App.App.Instance.Settings.value("MainWindow/currentTabText")
        for i in range(0, self.tabWidget.count()):
            if currentTabText == self.tabWidget.tabText(i):
                self.tabWidget.setCurrentIndex(i)
                break

    def DelayStartup(self):

        tabs.PythonHighlighter.PythonHighlighter.initializeFormats()

        self.loginDialog = LoginDialog.LoginDialog(self)
        self.loginDialog.setModal(True)
        self.loginDialog.hide()

        self.loginDialog.accepted.connect(self.OnLoginAccepted)
        self.loginDialog.rejected.connect(self.OnLoginRejected)

        value = App.App.Instance.Settings.value("MainWindow/Geometry")
        if value is not None:
            self.restoreGeometry(value)

        #self.timer = FastNet.App.Instance.CreateTimer(self,'OnTestTimer')
        #self.timer.Start(5000,10000,-1)


    def __init__(self): 
        super(MainWindow, self).__init__()

        self.tabs = {}
        self.tabValues = None
        self.name = ''

        self.roleId = ""
        #self.serverGotoToken = None

        self.setWindowTitle("后台管理工具")
        self.splitter = QtWidgets.QSplitter(self)

        self.tabWidget = QtWidgets.QTabWidget(self)
        self.textEditOutLog = QtWidgets.QTextEdit(self)
        self.loginDialog = None

        self.splitter.addWidget(self.tabWidget)
        self.splitter.addWidget(self.textEditOutLog)
        self.splitter.setOrientation(QtCore.Qt.Vertical)

        self.splitter.setSizes([700, 100])

        self.setCentralWidget(self.splitter)

        Signals.gSignals.SocketConnect.connect(self.OnSocketConnect)
        Signals.gSignals.AccountVerifySucceedRes.connect(self.OnAccountVerifySucceedRes)
        Signals.gSignals.RoleLoginSucceedRes.connect(self.OnRoleLoginSucceedRes)
        Signals.gSignals.AnyRes.connect(self.OnAnyRes)
        #Signals.gSignals.ServerGoto.connect(self.OnServerGoto)

        self.client = None
        self.isClose = False

        self.username = ''
        self.password = ''

        self.m_timerID = self.startTimer(100)

        cfgs = App.App.Instance.Cfgs['Client']
        self.client = Client.Client()
        self.client.Connect(str(cfgs['serverAddress']), 0,"",cfgs['serverId'],True)

        QtCore.QTimer.singleShot(0, self.DelayStartup)

    @property
    def SessionId(self):
        return self.client.SessionId

    def OnLoginAccepted(self):
        self.username = self.loginDialog.GetResult()[0]
        self.password = self.loginDialog.GetResult()[1]

        md5 = hashlib.md5()
        md5.update(self.password.encode('utf8'))

        jsonValue = json.dumps({'username': self.username, 'password': md5.hexdigest(), 'type': 'client'})

        headers = dict()
        headers['Content-Type'] = 'application/json'
        headers['Content-Length'] = str(len(jsonValue))

        cfgs = App.App.Instance.Cfgs['Client']
        ret = requests.post(cfgs['accountVerifyUrl'], data=jsonValue, headers=headers).json()
        if ret['status'] == 1:
            self.client.AccountVerify('000', json.dumps({'token':ret['token']}))
            self.WriteLog('正在进行账号验证...')
            self.loginDialog.hide()
        else:
            self.WriteLog('帐号验证出错!')
        

    def OnLoginRejected(self):
        self.close()  

    def ShowLoginDialog(self):
        self.loginDialog.setModal(True)
        self.loginDialog.move(
            self.pos().x() + self.size().width()/2 - self.loginDialog.size().width()/2,
            self.pos().y() + self.size().height()/2 - self.loginDialog.size().height()/2)

        self.loginDialog.show()
