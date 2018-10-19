# -*- coding: utf-8 -*-
import FastNet, pkt, cfg, json, time, hashlib
import Signals
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import App,Signals
from tabs.TableViewModel import TableViewModel


class AddNotice(QtWidgets.QDialog):
    def __init__(self, parent,datas):
        super(AddNotice, self).__init__(parent)
        uic.loadUi('ui/addnotice.ui', self)

        self.datas = {}

        self.btnAdd.clicked.connect(self.OnOk)


        self.radioButtonAllServer.clicked.connect(self.OnRadioChanged)
        self.radioButtonAllServer.btnName = 'AllServer'
        #self.comboBoxAllServer

        self.radioButtonServer.clicked.connect(self.OnRadioChanged)
        self.radioButtonServer.btnName = 'Server'
        #self.comboBoxServer

        self.radioButtonPlatform.clicked.connect(self.OnRadioChanged)
        self.radioButtonPlatform.btnName = 'Platform'

        #self.comboBoxPlatform

        self.radioButtonChannel.clicked.connect(self.OnRadioChanged)
        self.radioButtonChannel.btnName = 'Channel'

        platformMgrTabInfo = App.App.Instance.MainWindow.TabValues.get('PlatformMgr',None)
        if platformMgrTabInfo is not None:
            if 'AllowAll' in platformMgrTabInfo[1]['Server']:
                self.comboBoxServer.setModel(App.App.Instance.MainWindow.GetTab('ServerMgr').Model)
            else:
                for v in platformMgrTabInfo[1]['Server']:
                    self.comboBoxServer.addItem(v)

            if 'AllowAll' in platformMgrTabInfo[1]['Platform']:
                self.comboBoxPlatform.setModel(App.App.Instance.MainWindow.GetTab('PlatformMgr').modelPlatform)
            else:
                for v in platformMgrTabInfo[1]['Platform']:
                    self.comboBoxPlatform.addItem(v)

            if 'AllowAll' in platformMgrTabInfo[1]['Channel']:
                self.comboBoxChannel.setModel(App.App.Instance.MainWindow.GetTab('PlatformMgr').modelChannel)
            else:
                for v in platformMgrTabInfo[1]['Channel']:
                    self.comboBoxChannel.addItem(v)


        #radioButtonSelect = self.radioButtonChannel
        #ret = App.App.Instance.Settings.value("AddNotice/radioButtonSelect", None)
        #if ret is not None:
        #    radioButtonSelect = eval('self.radioButton{}'.format(ret))
        
        #radioButtonSelect.setChecked(True)
        self.OnRadioChanged(None)

        self.comboBoxNoticeType.currentIndexChanged.connect(self.OnNoticeTypeIndexChanged)

        self.comboBoxNoticeType.addItem('登录公告','login')
        self.comboBoxNoticeType.addItem('滚动公告','game')
        self.comboBoxNoticeType.addItem('推送公告','push') 

        self.radioButtonAllServer.setEnabled(True if 'AllowAllServer' in datas else False)
        self.radioButtonPlatform.setEnabled(True if 'AllowPlatform' in datas else False)
        self.radioButtonServer.setEnabled(True if 'AllowServer' in datas else False)
        

    def OnNoticeTypeIndexChanged(self,index):
        t = self.comboBoxNoticeType.itemData(index)
        if t == 'game':
            self.lineEditTitle.setEnabled(False)
        else:
            self.lineEditTitle.setEnabled(True)

    def OnRadioChanged(self,b):

        
        for v in[self.radioButtonAllServer,self.radioButtonServer,self.radioButtonPlatform,self.radioButtonChannel]:
            if v.isChecked():
                self.radioButtonSelectName = v.btnName

        obj = eval('self.comboBox{}'.format(self.radioButtonSelectName))
        obj.setEnabled(True)

        for v in [self.comboBoxAllServer,self.comboBoxServer,self.comboBoxPlatform,self.comboBoxChannel]:
            if v != obj:
                v.setEnabled(False)
    
    def OnOk(self):

        param = {'type':self.radioButtonSelectName}
        obj = eval('self.comboBox{}'.format(self.radioButtonSelectName))
        param['param'] = obj.currentText()

        if self.radioButtonSelectName != 'AllServer' and obj.currentText() == '':
            QtWidgets.QMessageBox.critical(self, '参数错误', '参数不能为空!',QtWidgets.QMessageBox.Yes)
            return
                

        now = time.time()
        data_head = time.strftime("%Y%m%d%H%M%S", time.localtime(now))
        data_secs = (now - int(now)) * 1000

        self.datas['name'] = "%s.%02d" % (data_head, data_secs)
        self.datas['title'] = self.lineEditTitle.text()
        self.datas['text'] = self.textEditText.toPlainText()
        self.datas['beginTime'] = self.dateTimeEditBegin.dateTime().toTime_t()
        self.datas['endTime'] = self.dateTimeEditBegin.dateTime().toTime_t()
        self.datas['param'] = param
        self.datas['duration'] = self.spinBoxDuration.value()
        self.datas['role'] = ''
        self.datas['desc'] = self.lineEditDesc.text()
        self.datas['status'] = False
        self.datas['type'] = self.comboBoxNoticeType.itemData(self.comboBoxNoticeType.currentIndex())
    
        #App.App.Instance.Settings.setValue("AddNotice/radioButtonSelect",self.radioButtonSelectName)


        self.done(QtWidgets.QDialog.Accepted)

    def GetData(self):
        ret = self.exec_()
        self.deleteLater()
        if ret == QtWidgets.QDialog.Accepted:
            return self.datas
        return None