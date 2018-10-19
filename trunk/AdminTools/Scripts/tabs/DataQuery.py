# -*- coding: utf-8 -*-
import FastNet, pkt, cfg
from PyQt5 import QtWidgets, uic, QtGui, QtCore
import App, Signals, json, time, random, importlib

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel


class LogQueryClient(FastNet.Client):
    def __init__(self,key,beginTime,endTime,appId,dataQuery):
        super(LogQueryClient, self).__init__(self)

        self.key = key
        self.beginTime = beginTime
        self.endTime = endTime
        self.appId = appId

        self.dataQuery = dataQuery

        self.BindMessage(pkt.protocols.LogQueryRes.sClsId,'OnLogQueryRes')

    def __del__(self):
        pass

    def OnLogQueryRes(self,message):
        self.dataQuery.OnLogQueryRes(message)

    def OnSocketEvent(self,e,info):
        if e == FastNet.SocketEvent.kConnectSucceed:
            print('OnSocketEvent')
            #self.Subscribe(FastNet.GetAppId())
            
            m = FastNet.Message.Create(pkt.protocols.LogQueryReq.sClsId)
            m.key = self.key
            m.beginTime = self.beginTime
            m.endTime = self.endTime
            m.appId = self.appId
            self.SendMsg(m)


class DataQuery(QtWidgets.QWidget):
    def __del__(self):
        print('DataQuery.__del__')

        #if self.currentWidget is not None:
        #    self.currentWidget.deleteLater()

    def OnDestory(self):

        for v in self.logQueryClients.values():
            v.Close()
            del v

        del self.logQueryClients

    def __init__(self, parent,datas):
        super(DataQuery, self).__init__(parent)

        uic.loadUi('ui/data_query.ui', self)

        self.datas = {}
        self.logQueryClients = {}

        self.btnQuery.clicked.connect(self.OnQuery)
        self.btnExport.clicked.connect(self.OnExport)

        self.comboBoxQueryType.currentIndexChanged.connect(self.OnInterfaceChanged)

        self.interfaces = datas

        self.currentWidget = None

        self.comboBoxTheme.addItem("None","none")
        self.comboBoxTheme.addItem("Avocado","avocado")
        self.comboBoxTheme.addItem("Dark Blue","dark-blue")
        self.comboBoxTheme.addItem("Dark Green","dark-green")
        self.comboBoxTheme.addItem("Dark Unica","dark-unica")
        self.comboBoxTheme.addItem("Gray","gray")
        self.comboBoxTheme.addItem("Grid","grid")
        self.comboBoxTheme.addItem("Grid Light","grid-light")
        self.comboBoxTheme.addItem("Sand Signika","sand-signika")
        self.comboBoxTheme.addItem("Skies","skies")
        self.comboBoxTheme.addItem("Sunset","sunset")
        self.comboBoxTheme.currentIndexChanged.connect(self.OnChartThemeChanged)


        self.comboBoxTimeType.addItem("最近一小时","hour")
        self.comboBoxTimeType.addItem("最近一天","day")
        self.comboBoxTimeType.addItem("最近一周","week")
        #self.comboBoxTimeType.addItem("最近一月","month")
        #self.comboBoxTimeType.addItem("最近一年","year")
        self.comboBoxTimeType.addItem("自定义时间","custom")
        self.comboBoxTimeType.currentIndexChanged.connect(self.OnTimeTypeChanged)

        self.timeType = 'hour'

        self.beginTime.setEnabled(False)
        self.endTime.setEnabled(False)


        self.comboBoxLogType.addItem("不限制","AllLog")
        self.comboBoxLogType.addItem("正常","Normal")
        self.comboBoxLogType.addItem("调试","Debug")
        self.comboBoxLogType.addItem("警告","Warning")
        self.comboBoxLogType.addItem("错误","Error")
        self.comboBoxLogType.addItem("异常","Exception")
        self.comboBoxLogType.currentIndexChanged.connect(self.OnLogTypeChanged)
        

        for v in self.interfaces:
            item = cfg.globals.modules.DataQuery.GetValue(v)
            if item is not None:
                self.comboBoxQueryType.addItem(item.name,v)

    def OnLogTypeChanged(self, index):
        if self.currentWidget is not None:
            self.currentWidget.OnLogTypeChanged(self.comboBoxLogType.itemData(index))

    def OnChartThemeChanged(self, index):
        theme = self.comboBoxTheme.itemData(index)
        if self.currentWidget is not None and self.currentWidget.GetTheme() != theme:
            App.App.Instance.Settings.setValue("DataQuery/{}".format(self.currentWidget.__class__.__name__), self.comboBoxTheme.itemText(index))

            self.currentWidget.SetTheme(theme)

    def OnTimeTypeChanged(self, index):
        theme = self.comboBoxTimeType.itemData(index)
        if theme != 'custom':
            self.beginTime.setEnabled(False)
            self.endTime.setEnabled(False)
        else:
            self.beginTime.setEnabled(True)
            self.endTime.setEnabled(True)

    def CreateWidget(self, k):
        try:
            m = importlib.import_module('log.{}'.format(k))
            importlib.reload(m)
            return eval('m.{0}(self)'.format(k))
        except BaseException as e:
            App.App.Instance.MainWindow.WriteErrorLog(str(e))
        return None

    def OnInterfaceChanged(self, index):
        text = self.comboBoxQueryType.itemData(index)
        if text not in self.interfaces:
            return

        if self.currentWidget is not None:
            self.horizontalLayout.removeWidget(self.currentWidget)
            self.currentWidget.deleteLater()
            self.currentWidget = None

        self.labelTheme.setEnabled(False)
        self.comboBoxTheme.setEnabled(False)

        self.currentWidget = self.CreateWidget(text)
        if self.currentWidget is not None:
            if self.currentWidget.IsAllowExport() is False:
                self.btnExport.setEnabled(False)

            if self.currentWidget.IsChartMode() is True:
                self.labelTheme.setEnabled(True)
                self.comboBoxTheme.setEnabled(True)

                theme = App.App.Instance.Settings.value("DataQuery/{}".format(self.currentWidget.__class__.__name__), None)
                if theme is None:
                    theme = 'None'

                self.comboBoxTheme.setCurrentText(theme)
                #self.currentWidget.SetTheme(theme,True)
                self.comboBoxLogType.setEnabled(False)
            else:
                self.comboBoxLogType.setEnabled(True)

            self.horizontalLayout.addWidget(self.currentWidget)

    def OnExport(self):
        if self.currentWidget is not None:
            self.currentWidget.Export()

    def OnQuery(self):

        if self.currentWidget is not None:

            beginTime = 0
            endTime = 0

            self.timeType = self.comboBoxTimeType.itemData(self.comboBoxTimeType.currentIndex())
            if self.timeType == 'custom':
                beginTime = self.beginTime.dateTime().toTime_t()
                endTime = self.endTime.dateTime().toTime_t()

                if endTime <= beginTime:
                    App.App.Instance.MainWindow.WriteErrorLog("查询失败,结束时间必须大于开始时间！")
                    return

                if (endTime - beginTime) >= 3600 * 24 * 7:
                    App.App.Instance.MainWindow.WriteErrorLog("查询失败,查询时间范围必须在7天以内！")
                    return

            elif self.timeType == 'hour':
                endTime = int(time.time())
                beginTime = endTime - 3600
            elif self.timeType == 'day':
                endTime = int(time.time())
                beginTime = endTime - 3600 * 24
            elif self.timeType == 'week':
                endTime = int(time.time())
                beginTime = endTime - 3600 * 24 * 7


            serverMgr = App.App.Instance.MainWindow.GetTab('ServerMgr')

            serverName = self.comboBoxQueryServerName.currentText()
            serverId = None
            model = serverMgr.Model
            for i in range(0,model.rowCount()):
                if model.item(i, 0).text() == serverName:
                    serverId = int(model.item(i, 1).text())
                    break

            if serverId is None:
                App.App.Instance.MainWindow.WriteErrorLog("查询失败,服务器: {} 查询异常！".format(serverName))
                return
            
            logServerAddressWan = ""
            if self.currentWidget.__class__.__name__ == 'TimerTaskLog' or \
                self.currentWidget.__class__.__name__ == 'OperationLog':
                logServerAddressWan = daemons[daemonName]['logServerAddressWan']
            else:
                daemonName = None
                daemons = serverMgr.Datas['daemons']
                servers = serverMgr.Datas['servers']
                for v in servers.values():
                    if int(v['id']) == serverId: 
                        daemonName = v['daemon']
                        if daemonName in daemons:
                            logServerAddressWan = daemons[daemonName]['logServerAddressWan']
                            break

            if logServerAddressWan == "":
                App.App.Instance.MainWindow.WriteErrorLog('查询日志失败,没有找到对应的守护进程Id:' + serverId)
                return None

            key = self.currentWidget.__class__.__name__
            if key == 'ServerLog':
                key = 'AllLog'

            if serverId in self.logQueryClients:
                self.logQueryClients[serverId].Close()
                del self.logQueryClients[serverId]

            lqc = LogQueryClient(key,beginTime,endTime,serverId,self)
            lqc.Connect(logServerAddressWan,10000,"",0,False)
            self.logQueryClients[serverId] = lqc

            
            self.currentWidget.Query(beginTime,endTime)

    def OnLogQueryRes(self,message):
        if self.currentWidget is not None:
            self.currentWidget.OnQueryData(message)

    def RefreshData(self, j):

        type = j['type']

        if type == 'init':
            self.datas = j['val']

            self.comboBoxQueryServerName.setModel(App.App.Instance.MainWindow.GetTab('ServerMgr').Model)
            
        '''elif type == 'queryLogRes':
            data = j['data']
            if self.currentWidget is not None and self.currentWidget.__class__.__name__ == data['logType']:
                self.currentWidget.OnQueryData(data['data'])

        elif type == 'queryLogEndRes':
            data = j['data']
            if self.currentWidget is not None and self.currentWidget.__class__.__name__ == data['logType']:
                self.currentWidget.OnQueryData(None)
        '''