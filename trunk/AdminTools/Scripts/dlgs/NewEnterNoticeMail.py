# -*- coding: utf-8 -*-
import FastNet, pkt, json
import Signals
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import App
import dlgs.AddPlatform
from tabs.TableViewModel import TableViewModel

class NewEnterNoticeMailDialog(QtWidgets.QDialog):
    def __init__(self, parent, model, title = None):
        super(NewEnterNoticeMailDialog, self).__init__(parent)

        if title is not None:
            self.setWindowTitle(title)
        else:
            self.setWindowTitle('邮件通知管理')

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

        self.modelAddress = TableViewModel()
        self.tableViewIps = QtWidgets.QTableView(self)
        self.tableViewIps.setModel(self.modelAddress)

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


        columnLabels = ['邮件地址', '描述']

        self.modelAddress.setHorizontalHeaderLabels(columnLabels)
        self.modelAddress.setColumnCount(len(columnLabels))

    
    def OnTableViewActivated(self, index, r):
        if index.isValid() is True:

            self.modelAddress.setRowCount(0)
            ips = self.model.index(index.row(), 2).data()
            for v in ips:
                self.modelAddress.appendRow(QtGui.QStandardItem())
                row = self.modelAddress.rowCount() - 1

                self.modelAddress.setData(self.modelAddress.index(row, 0), v['address'])
                self.modelAddress.setData(self.modelAddress.index(row, 1), v['desc'])


    def OnMenuAdd(self):

        values = []
        values.append({'key':'name','name':'名称'})
        values.append({'key':'desc','name':'描述'})

        dlg = dlgs.AddPlatform.AddPlatform(self,'newEnterNoticeMails','添加邮件通知',values)
        data = dlg.GetData()
        if data is not None: 
            data['param'] = []
            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = 'ServerMgr'
            m.data = json.dumps({'type': 'add',
                                    'val':'newEnterNoticeMails' ,
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

        dlg = dlgs.AddPlatform.AddPlatform(self,'newEnterNoticeMails','修改描述',values)  
        data = dlg.GetData()
        if data is not None:   
            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = 'ServerMgr'
            m.data = json.dumps({'type': 'modify',
                                    'val':'newEnterNoticeMails' ,
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
                                'val':'newEnterNoticeMails' ,
                                'key': self.model.index(index.row(), 0).data()
                            })
        Signals.gSignals.SendMsg.emit(m)




    def OnMenuAddAddress(self):

        if self.tableView.currentIndex().isValid() is False:
            return

        values = []
        values.append({'key':'name','name':'IP地址'})
        values.append({'key':'desc','name':'描述'})

        dlg = dlgs.AddPlatform.AddPlatform(self,'newEnterNoticeMails_address','添加IP',values)
        data = dlg.GetData()
        if data is not None: 

            ips = []
            for row in range(0,self.modelAddress.rowCount()):
                if self.modelAddress.item(row,0).text() == data['name']:
                    App.App.Instance.MainWindow.WriteErrorLog('添加白名单IP失败,IP重复！')
                    return

                ips.append({'address':self.modelAddress.item(row,0).text(),'desc':self.modelAddress.item(row,1).text()})
                
            ips.append({'address':data['name'],'desc':data['desc']})
            
            self.modelAddress.appendRow(QtGui.QStandardItem())
            row = self.modelAddress.rowCount() - 1

            self.modelAddress.setData(self.modelAddress.index(row, 0), data['name'])
            self.modelAddress.setData(self.modelAddress.index(row, 1), data['desc'])

            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = 'ServerMgr'
            m.data = json.dumps({'type': 'modify',
                                    'val':'newEnterNoticeMails' ,
                                    'key': self.model.index(self.tableView.currentIndex().row(), 0).data() ,
                                    'data':{'param':ips}
                                })
            Signals.gSignals.SendMsg.emit(m)

    def OnMenuDelAddress(self):
        if self.tableView.currentIndex().isValid() is False:
            return

        index = self.tableViewIps.currentIndex()
        if index.isValid() is False:
            return

        self.modelAddress.removeRow(index.row())

        ips = []
        for row in range(0,self.modelAddress.rowCount()):
            ips.append({'address':self.modelAddress.item(row,0).text(),'desc':self.modelAddress.item(row,1).text()})

        m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
        m.classId = 'ServerMgr'
        m.data = json.dumps({'type': 'modify',
                                'val':'newEnterNoticeMails' ,
                                'key': self.model.index(self.tableView.currentIndex().row(), 0).data(),
                                'data':{'param':ips}
                            })
        Signals.gSignals.SendMsg.emit(m)


    def OnMenuModifyAddress(self):

        if self.tableView.currentIndex().isValid() is False:
            return

        index = self.tableViewIps.currentIndex()
        if index.isValid() is False:
            return

        values = []
        values.append({'key':'name','name':'IP地址'})
        values.append({'key':'desc','name':'描述'})

        dlg = dlgs.AddPlatform.AddPlatform(self,'newEnterNoticeMails_address','修改',values)
        data = dlg.GetData()
        if data is not None: 

            ips = []
            for row in range(0,self.modelAddress.rowCount()):
                if self.modelAddress.item(row,0).text() == data['name'] and row != index.row():
                    App.App.Instance.MainWindow.WriteErrorLog('修改失败,地址重复！')
                    return

            self.modelAddress.setData(self.modelAddress.index(index.row(), 0), data['name'])
            self.modelAddress.setData(self.modelAddress.index(index.row(), 1), data['desc'])

            for row in range(0,self.modelAddress.rowCount()):
                ips.append({'address':self.modelAddress.item(row,0).text(),'desc':self.modelAddress.item(row,1).text()})

            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = 'ServerMgr'
            m.data = json.dumps({'type': 'modify',
                                    'val':'newEnterNoticeMails' ,
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
            actionAdd = QtWidgets.QAction("添加",self.sender(),triggered=self.OnMenuAddAddress)
            actionDel = QtWidgets.QAction("删除",self.sender(),triggered=self.OnMenuDelAddress)
            actionModify = QtWidgets.QAction("修改描述",self.sender(),triggered=self.OnMenuModifyAddress)

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


