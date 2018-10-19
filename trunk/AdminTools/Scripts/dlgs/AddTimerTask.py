# -*- coding: utf-8 -*-
import FastNet, pkt, json, time
import Signals
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import App,Signals


class AddTimerTaskDialog(QtWidgets.QDialog):
    def __init__(self, parent,values=None):
        super(AddTimerTaskDialog, self).__init__(parent)
        uic.loadUi('ui/addtimertask.ui', self)

        Signals.gSignals.QuerySvnLogs.connect(self.OnQuerySvnLogs)

        self.comboBoxType.addItem('更新代码','updateCode')
        self.comboBoxType.addItem('更新配置','updateCfg')
        self.comboBoxType.addItem('重启','restart')
        self.comboBoxType.addItem('启动','start')
        self.comboBoxType.addItem('停止','stop')

        self.btnOK.clicked.connect(self.OnOk)
        self.btnCancel.clicked.connect(self.reject)

        self.comboBoxCode.currentTextChanged.connect(self.OnSvnChanged)
        self.comboBoxCfg.currentTextChanged.connect(self.OnSvnChanged)

        for v in values:
            self.comboBoxCfg.addItem(v)
            self.comboBoxCode.addItem(v)

        self.comboBoxType.currentIndexChanged.connect(self.OnTypeChanged)

        self.resize(450,0)

    def OnTypeChanged(self,index):
        if self.comboBoxType.itemData(index) == 'updateCode':
            self.comboBoxCfg.setEnabled(True)
            self.comboBoxCfgRevision.setEnabled(True)
        else:
            self.comboBoxCfg.setEnabled(False)
            self.comboBoxCfgRevision.setEnabled(False)

    def OnSvnChanged(self,text):
        m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
        m.classId = 'ServerMgr'
        m.data = json.dumps({'type': 'query',
                                'val':'svns' ,
                                'key': text,
                                'cmbox': text
                            })
        Signals.gSignals.SendMsg.emit(m)

    def closeEvent(self, event):
        Signals.gSignals.QuerySvnLogs.disconnect(self.OnQuerySvnLogs)
        event.accept()

    def OnQuerySvnLogs(self,key,data):

        def SetComboBox(cb):
            cb.clear()

            for v in data:
                text = '{}|{}|{}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(v[0])),v[1],v[2])
                cb.addItem(text)

        if key == self.comboBoxCode.currentText():
            SetComboBox(self.comboBoxCodeRevision)

        if key == self.comboBoxCfg.currentText():
            SetComboBox(self.comboBoxCfgRevision)

    def OnOk(self):
        self.done(QtWidgets.QDialog.Accepted)
        self.datas = {}
        self.datas['type'] = self.comboBoxType.itemData(self.comboBoxType.currentIndex())
        self.datas['code'] = self.comboBoxCode.currentText()
        self.datas['code_revision'] = self.comboBoxCodeRevision.currentText()
        self.datas['time'] = self.dateTimeEdit.dateTime().toTime_t()

        if self.datas['type'] == 'updateCode': 
            self.datas['cfg'] = self.comboBoxCfg.currentText()
            self.datas['cfg_revision'] = self.comboBoxCfgRevision.currentText()

    def GetData(self):
        ret = self.exec_()
        self.deleteLater()
        if ret == QtWidgets.QDialog.Accepted:
            return self.datas
        return None

