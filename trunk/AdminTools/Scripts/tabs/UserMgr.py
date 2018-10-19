# -*- coding: utf-8 -*-
import FastNet
import App, Signals, pkt, json, cfg
from PyQt5 import QtWidgets, uic, QtCore, QtGui
import importlib

from tabs.TableViewModel import TableViewModel

class UserMgr(QtWidgets.QWidget):
    def __init__(self, parent,datas):
        super(UserMgr, self).__init__(parent)

        uic.loadUi('ui/user_mgr.ui', self)

        self.model = TableViewModel()

        self.tableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested['QPoint'].connect(self.OnCustomContextMenuRequested)

        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        #self.tableView.selectionModel().currentChanged.connect(self.OnTableViewActivated)


        columnLabels = ['名字' ,'账号', '权限', '密码', '描述']

        self.model.setHorizontalHeaderLabels(columnLabels)
        self.model.setColumnCount(len(columnLabels))

        #self.tableView.setColumnWidth(0,200)
        #self.tableView.setColumnWidth(1,200)
        self.tableView.setColumnWidth(2,400)

        #self.tableView.hideColumn(2)
        self.tableView.hideColumn(3)

        self.datas = datas


    def UpdatePermissionText(self,row,param):
        showText = '['

        tabs = []
        for k,v in param.items():
            if v[0] is True:
                tabs.append(App.App.Instance.MainWindow.Tabs[k].windowTitle())

        self.model.setData(self.model.index(row, 2),'[' + ','.join(tabs) + ']')
        self.model.setData(self.model.index(row, 2),param,QtCore.Qt.UserRole + 2)

    def RefreshData(self, j):

        t = j['type']
        if t == 'init':
            self.datas = j

            for k,v in j['val'].items():
                self.model.appendRow(QtGui.QStandardItem())

                row = self.model.rowCount() - 1

                self.model.setData(self.model.index(row, 0), v['name'])
                self.model.setData(self.model.index(row, 1), v['account'])
                self.UpdatePermissionText(row,v['permissions'])
                self.model.setData(self.model.index(row, 3), v['password'])
                self.model.setData(self.model.index(row, 4), v['desc'])

        elif t == 'add':
            d = j['val']
            k = j['key']

            self.model.appendRow(QtGui.QStandardItem())

            row = self.model.rowCount() - 1

            self.model.setData(self.model.index(row, 0), d['name'])
            self.model.setData(self.model.index(row, 1), d['account'])
            self.UpdatePermissionText(row,d['permissions'])
            self.model.setData(self.model.index(row, 3), d['password'])
            self.model.setData(self.model.index(row, 4), d['desc'])

            App.App.Instance.MainWindow.WriteLog('用户:{} 添加成功!'.format(d['name']))

        elif t == 'modify':
            d = j['val']
            k = j['key']

            for i in range(0, self.model.rowCount()):
                if k == self.model.item(i, 0).text():

                    if 'permissions' in d:
                        self.UpdatePermissionText(i,d['permissions'])

                    if 'desc' in d:
                        self.model.setData(self.model.index(i, 4), d['desc'])

                    if 'password' in d:
                        self.model.setData(self.model.index(i, 3), d['password'])

                    App.App.Instance.MainWindow.WriteLog('用户:{} 修改成功!'.format(k))
                    break

        elif t == 'del':
            k = j['key']

            for i in range(0, self.model.rowCount()):
                if self.model.item(i, 0).text() == k:
                    self.model.removeRow(i)
                    App.App.Instance.MainWindow.WriteLog('用户:{} 删除成功!'.format(k))
                    break


    def OnMenuAdd(self):

        m = importlib.import_module('dlgs.AddUser')
        importlib.reload(m)

        dlg = m.AddUser(self)
        data = dlg.GetData()

        if data is not None:

            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = self.__class__.__name__
            m.data = json.dumps({'type': 'add',
                                    'key':data['name'],
                                    'val':data
                                })
            Signals.gSignals.SendMsg.emit(m)

    def OnMenuModify(self):
        index = self.tableView.currentIndex()
        if index.isValid() is False:
            return


        m = importlib.import_module('dlgs.AddUser')
        importlib.reload(m)

        datas = {}
        datas['permissions'] = self.model.index(index.row(), 2).data(QtCore.Qt.UserRole + 2)
        datas['name'] = self.model.index(index.row(), 0).data()
        datas['account'] = self.model.index(index.row(), 1).data()
        datas['password'] = self.model.index(index.row(), 3).data()
        datas['desc'] = self.model.index(index.row(), 4).data()
      
        dlg = m.AddUser(self,datas)
        data = dlg.GetData()
        if data is not None:

            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = self.__class__.__name__
            m.data = json.dumps({'type': 'modify',
                                    'key':data['name'],
                                    'val':data
                                })
            Signals.gSignals.SendMsg.emit(m)
    
    def OnMenuDel(self):
        index = self.tableView.currentIndex()
        if index.isValid() is False:
            return

        m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
        m.classId = self.__class__.__name__
        m.data = json.dumps({'type': 'del',
                                'key': self.model.item(index.row(), 0).text()
                            })
        Signals.gSignals.SendMsg.emit(m)
    
        
    def OnCustomContextMenuRequested(self, pt):

        actionAdd = QtWidgets.QAction("添加", None, triggered=self.OnMenuAdd)
        actionModify = QtWidgets.QAction("修改", None, triggered=self.OnMenuModify)
        actionDel = QtWidgets.QAction("删除", None, triggered=self.OnMenuDel)

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
        menu.destroy()