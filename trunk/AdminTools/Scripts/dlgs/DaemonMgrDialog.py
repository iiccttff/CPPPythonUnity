# -*- coding: utf-8 -*-
import FastNet, pkt, json
import Signals
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import App
import dlgs.AddPlatform

class DaemonMgrDialog(QtWidgets.QDialog):
    def __init__(self, parent, model, title = None):
        super(DaemonMgrDialog, self).__init__(parent)

        if title is not None:
            self.setWindowTitle(title)
        else:
            self.setWindowTitle('辅助进程管理')

        self.model = model

        vboxLayout = QtWidgets.QVBoxLayout(self)

        self.tableView = QtWidgets.QTableView(self)
        self.tableView.setModel(model)

        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.tableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested['QPoint'].connect(self.OnCustomContextMenuRequested)


        vboxLayout.addWidget(self.tableView)

        self.resize(600,300)

    def OnMenuAdd(self):

        values = []
        values.append({'key':'name','name':'名称'})
        values.append({'key':'id','name':'ID'})
        values.append({'key':'desc','name':'描述'})

        dlg = dlgs.AddPlatform.AddPlatform(self,'daemons','添加辅助进程',values)
        data = dlg.GetData()
        if data is not None: 
            data['status'] = 0
            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = 'ServerMgr'
            m.data = json.dumps({'type': 'add',
                                    'val':'daemons' ,
                                    'key': data['name'],
                                    'data':data
                                })
            Signals.gSignals.SendMsg.emit(m)

    def OnMenuModify(self):
        index = self.tableView.currentIndex()
        if index.isValid() is False:
            return

        row = index.row()
        values = []
        values.append({'key':'name','name':'名称','defaultVal':self.model.item(row, 0).text(),'widget':'ReadOnly'})
        values.append({'key':'id','name':'ID','defaultVal':self.model.item(row, 1).text()})
        values.append({'key':'desc','name':'描述','defaultVal':self.model.item(row, 2).text()})

        dlg = dlgs.AddPlatform.AddPlatform(self,'daemons','修改辅助进程',values)  
        data = dlg.GetData()
        if data is not None:   
            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = 'ServerMgr'
            m.data = json.dumps({'type': 'modify',
                                    'val':'daemons' ,
                                    'key': self.model.item(row, 0).text(),
                                    'data':data
                                })
            Signals.gSignals.SendMsg.emit(m)

    def OnMenuDel(self):
        index = self.tableView.currentIndex()
        if index.isValid() is False:
            return

        m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
        m.classId = 'ServerMgr'
        m.data = json.dumps({'type': 'del',
                                'val':'daemons' ,
                                'key': self.model.index(index.row(), 0).data()
                            })
        Signals.gSignals.SendMsg.emit(m)

    def OnCustomContextMenuRequested(self,pt):
        actionAdd = QtWidgets.QAction("添加",self.sender(),triggered=self.OnMenuAdd)
        actionModify = QtWidgets.QAction("修改",self.sender(),triggered=self.OnMenuModify)
        actionDel = QtWidgets.QAction("删除",self.sender(),triggered=self.OnMenuDel)
        
        index = self.tableView.currentIndex()
        if index.isValid() is False:
            actionDel.setEnabled(False)
            actionModify.setEnabled(False)

        menu = QtWidgets.QMenu("menu")
        menu.addAction(actionAdd)
        menu.addAction(actionModify)
        menu.addSeparator()
        menu.addAction(actionDel)
        menu.exec_(QtGui.QCursor.pos())

        actionAdd.deleteLater()
        actionDel.deleteLater()
        menu.destroy()

