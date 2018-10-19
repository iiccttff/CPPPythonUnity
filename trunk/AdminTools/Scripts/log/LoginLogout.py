import FastNet, pkt, cfg
from PyQt5 import QtWidgets, uic, QtGui, QtCore
import App, Signals, json, time, random

import log.WebEngineView

class LoginLogout(log.WebEngineView.WebEngineView):

    def Query(self):

        parent = self.parent()
        
        beginTime = 0
        endTime = 0

        timeType = parent.comboBoxTimeType.itemData(parent.comboBoxTimeType.currentIndex())
        if timeType == 'custom':
            beginTime = parent.beginTime.dateTime().toTime_t()
            endTime = parent.endTime.dateTime().toTime_t()

            if endTime <= beginTime:
                App.App.Instance.MainWindow.WriteErrorLog("查询失败,结束时间必须大于开始时间！")
                return

        elif timeType == 'hour':
            endTime = int(time.time())
            beginTime = endTime - 3600
        elif timeType == 'day':
            endTime = int(time.time())
            beginTime = endTime - 3600 * 24
        elif timeType == 'week':
            endTime = int(time.time())
            beginTime = endTime - 3600 * 24 * 7
        elif timeType == 'month':
            endTime = int(time.time())
            beginTime = endTime - 3600 * 24 * 30
        elif timeType == 'year':
            endTime = int(time.time())
            beginTime = endTime - 3600 * 24 * 365

        
        args = {}
        args['key'] = ''
        args['type'] = 'queryLog_req'
        args['logType'] = self.__class__.__name__
        #args['classId'] = 'AllLog'
        args['beginTime'] = str(beginTime)
        args['endTime'] = str(endTime)
        args['sessionId'] = str(App.App.Instance.MainWindow.SessionId)

        serverName = parent.comboBoxQueryServerName.currentText()
        model = App.App.Instance.MainWindow.GetTab('ServerMgr').Model
        for i in range(0,model.rowCount()):
            if model.item(i, 0).text() == serverName:
                args['toServerId'] = int(model.item(i, 1).text())
                break

        m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
        m.classId = parent.__class__.__name__
        m.data = json.dumps(args)

        Signals.gSignals.SendMsg.emit(m)

    def IsAllowExport(self):
        return False

    def IsChartMode(self):
        return True

    def OnQueryData(self,data):
        print(data)
        self.reload()

    def Categories(self):
        return self.categories

    def Datas(self):
        return self.datas

    def __init__(self,parent):
        super(LoginLogout, self).__init__(parent)

        self.categories = []

        self.datas = \
        [
            {
                'name': '登录',
                'data': []
            },
            {
                'name': '退出',
                'data': []
            },
            {
                'name': '在线',
                'data': []
            }
        ]