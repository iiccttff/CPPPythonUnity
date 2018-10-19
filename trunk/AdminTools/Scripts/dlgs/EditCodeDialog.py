# -*- coding: utf-8 -*-
import FastNet, pkt, json, base64
import Signals
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import App
import tabs.PythonHighlighter


class EditCodeDialog(QtWidgets.QDialog):
    def __init__(self, parent,row):
        super(EditCodeDialog, self).__init__(parent)
        uic.loadUi('ui/editcodedialog.ui', self)

        self.textEditAccountVerify = tabs.PythonHighlighter.TextEdit(self)
        self.textEditPayNotice = tabs.PythonHighlighter.TextEdit(self)

        self.highlighterAccountVerify = tabs.PythonHighlighter.PythonHighlighter(self.textEditAccountVerify)
        self.highlighterPayNotice = tabs.PythonHighlighter.PythonHighlighter(self.textEditPayNotice)

        self.verticalLayoutL.insertWidget(1,self.textEditAccountVerify)
        self.verticalLayoutR.insertWidget(1,self.textEditPayNotice)
        
        #self.model = App.App.Instance.MainWindow.GetTab('PlatformMgr').ChannelModel
        #self.tableView.setModel(self.model)

        #self.tableView.horizontalHeader().setStretchLastSection(True)
        #self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        #self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        #self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        #self.tableView.selectionModel().currentChanged.connect(self.OnTableViewActivated)

        #self.tableView.hideColumn(6)
        #self.tableView.hideColumn(5)
        #self.tableView.hideColumn(3)

        self.btnSave.clicked.connect(self.OnSave)
        self.btnRestore.clicked.connect(self.OnRestore)

        self.row = row

        self.OnRestore(None)

    #def OnTableViewActivated(self, index, r):
    #    if index.isValid() is True:

    #        code = self.model.index(index.row(), 5).data()
    #        self.textEditAccountVerify.setText(code['accountVerify'])
    #        self.textEditPayNotice.setText(code['pay'])

    def OnSave(self,b):

        try:
            exec(self.textEditAccountVerify.toPlainText())
        except Exception as e:
            App.App.Instance.MainWindow.WriteLog('登录验证代码保存失败:' + e.message)
            return

        try:
            exec(self.textEditPayNotice.toPlainText())
        except Exception as e:
            App.App.Instance.MainWindow.WriteLog('充值回调代码保存失败:' + e.message)
            return


        model = App.App.Instance.MainWindow.GetTab('PlatformMgr').ChannelModel

        code = {}
        code['accountVerify'] = self.textEditAccountVerify.toPlainText()
        code['pay'] = self.textEditPayNotice.toPlainText()

        m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
        m.classId = 'PlatformMgr'
        m.data = json.dumps({'type': 'modify',
                                'val':'channels' ,
                                'key': model.index(self.row, 0).data(),
                                'data':{'code':code}
                            })

        Signals.gSignals.SendMsg.emit(m)
        
    def OnRestore(self,b):
        #index = self.tableView.currentIndex()
        #if index.isValid() is True:
        model = App.App.Instance.MainWindow.GetTab('PlatformMgr').ChannelModel
        code = model.index(self.row , 5).data()
        self.textEditAccountVerify.setText(code['accountVerify'])
        self.textEditPayNotice.setText(code['pay'])