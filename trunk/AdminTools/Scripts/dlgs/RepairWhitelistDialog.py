# -*- coding: utf-8 -*-
import FastNet, pkt, json
import Signals
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import App
import dlgs.AddPlatform
from tabs.TableViewModel import TableViewModel

class RepairWhitelistDialog(QtWidgets.QDialog):
    def __init__(self, parent, model, title = None):
        super(RepairWhitelistDialog, self).__init__(parent)

        if title is not None:
            self.setWindowTitle(title)
        else:
            self.setWindowTitle('维护白名单管理')

        self.model = model


        self.tableView = QtWidgets.QTableView(self)
        self.tableView.setModel(model)

        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.tableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested['QPoint'].connect(self.OnCustomContextMenuRequested)
        self.tableView.selectionModel().currentChanged.connect(self.OnTableViewActivated)

        self.tableView.hideColumn(2)

        self.modelIps = TableViewModel()
        self.tableViewIps = QtWidgets.QTableView(self)
        self.tableViewIps.setModel(self.modelIps)

        self.tableViewIps.horizontalHeader().setStretchLastSection(True)
        self.tableViewIps.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableViewIps.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableViewIps.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.tableViewIps.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableViewIps.customContextMenuRequested['QPoint'].connect(self.OnCustomContextMenuRequested)
        
        hboxLayout = QtWidgets.QHBoxLayout(self)
        hboxLayout.addWidget(self.tableView)
        hboxLayout.addWidget(self.tableViewIps)

        self.resize(800,400)


        columnLabels = ['IP地址', '描述']

        self.modelIps.setHorizontalHeaderLabels(columnLabels)
        self.modelIps.setColumnCount(len(columnLabels))

    
    def OnTableViewActivated(self, index, r):
        if index.isValid() is True:

            self.modelIps.setRowCount(0)
            ips = self.model.index(index.row(), 2).data()
            for v in ips:
                self.modelIps.appendRow(QtGui.QStandardItem())
                row = self.modelIps.rowCount() - 1

                self.modelIps.setData(self.modelIps.index(row, 0), v['ip'])
                self.modelIps.setData(self.modelIps.index(row, 1), v['desc'])


    def OnMenuAdd(self):

        values = []
        values.append({'key':'name','name':'名称'})
        values.append({'key':'desc','name':'描述'})

        dlg = dlgs.AddPlatform.AddPlatform(self,'repairWhitelists','添加白名单',values)
        data = dlg.GetData()
        if data is not None: 
            data['param'] = []
            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = 'ServerMgr'
            m.data = json.dumps({'type': 'add',
                                    'val':'repairWhitelists' ,
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
        values.append({'key':'desc','name':'描述','defaultVal':self.model.item(row, 1).text()})

        dlg = dlgs.AddPlatform.AddPlatform(self,'repairWhitelists','修改描述',values)  
        data = dlg.GetData()
        if data is not None:   
            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = 'ServerMgr'
            m.data = json.dumps({'type': 'modify',
                                    'val':'repairWhitelists' ,
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
                                'val':'repairWhitelists' ,
                                'key': self.model.index(index.row(), 0).data()
                            })
        Signals.gSignals.SendMsg.emit(m)




    def OnMenuAddIp(self):

        if self.tableView.currentIndex().isValid() is False:
            return

        values = []
        values.append({'key':'name','name':'IP地址'})
        values.append({'key':'desc','name':'描述'})

        dlg = dlgs.AddPlatform.AddPlatform(self,'repairWhitelists_ip','添加IP',values)
        data = dlg.GetData()
        if data is not None: 

            ips = []
            for row in range(0,self.modelIps.rowCount()):
                if self.modelIps.item(row,0).text() == data['name']:
                    App.App.Instance.MainWindow.WriteErrorLog('添加白名单IP失败,IP重复！')
                    return

                ips.append({'ip':self.modelIps.item(row,0).text(),'desc':self.modelIps.item(row,1).text()})
                
            ips.append({'ip':data['name'],'desc':data['desc']})
            
            self.modelIps.appendRow(QtGui.QStandardItem())
            row = self.modelIps.rowCount() - 1

            self.modelIps.setData(self.modelIps.index(row, 0), data['name'])
            self.modelIps.setData(self.modelIps.index(row, 1), data['desc'])

            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = 'ServerMgr'
            m.data = json.dumps({'type': 'modify',
                                    'val':'repairWhitelists' ,
                                    'key': self.model.index(self.tableView.currentIndex().row(), 0).data() ,
                                    'data':{'param':ips}
                                })
            Signals.gSignals.SendMsg.emit(m)

    def OnMenuDelIp(self):
        if self.tableView.currentIndex().isValid() is False:
            return

        index = self.tableViewIps.currentIndex()
        if index.isValid() is False:
            return

        self.modelIps.removeRow(index.row())

        ips = []
        for row in range(0,self.modelIps.rowCount()):
            ips.append({'ip':self.modelIps.item(row,0).text(),'desc':self.modelIps.item(row,1).text()})

        m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
        m.classId = 'ServerMgr'
        m.data = json.dumps({'type': 'modify',
                                'val':'repairWhitelists' ,
                                'key': self.model.index(self.tableView.currentIndex().row(), 0).data(),
                                'data':{'param':ips}
                            })
        Signals.gSignals.SendMsg.emit(m)


    def OnMenuModifyIp(self):

        if self.tableView.currentIndex().isValid() is False:
            return

        index = self.tableViewIps.currentIndex()
        if index.isValid() is False:
            return

        values = []
        values.append({'key':'name','name':'IP地址'})
        values.append({'key':'desc','name':'描述'})

        dlg = dlgs.AddPlatform.AddPlatform(self,'repairWhitelists_ip','修改',values)
        data = dlg.GetData()
        if data is not None: 

            ips = []
            for row in range(0,self.modelIps.rowCount()):
                if self.modelIps.item(row,0).text() == data['name'] and row != index.row():
                    App.App.Instance.MainWindow.WriteErrorLog('修改白名单IP失败,IP重复！')
                    return

            self.modelIps.setData(self.modelIps.index(index.row(), 0), data['name'])
            self.modelIps.setData(self.modelIps.index(index.row(), 1), data['desc'])

            for row in range(0,self.modelIps.rowCount()):
                ips.append({'ip':self.modelIps.item(row,0).text(),'desc':self.modelIps.item(row,1).text()})

            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = 'ServerMgr'
            m.data = json.dumps({'type': 'modify',
                                    'val':'repairWhitelists' ,
                                    'key': self.model.index(self.tableView.currentIndex().row(), 0).data() ,
                                    'data':{'param':ips}
                                })
            Signals.gSignals.SendMsg.emit(m)

    def OnCustomContextMenuRequested(self,pt):
        if self.sender() == self.tableView:

            actionAdd = QtWidgets.QAction("添加",self.sender(),triggered=self.OnMenuAdd)
            actionModify = QtWidgets.QAction("修改描述",self.sender(),triggered=self.OnMenuModify)
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

        else:
            actionAdd = QtWidgets.QAction("添加",self.sender(),triggered=self.OnMenuAddIp)
            actionDel = QtWidgets.QAction("删除",self.sender(),triggered=self.OnMenuDelIp)
            actionModify = QtWidgets.QAction("修改描述",self.sender(),triggered=self.OnMenuModifyIp)

            index = self.tableViewIps.currentIndex()
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


