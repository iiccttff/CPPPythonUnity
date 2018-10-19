# -*- coding: utf-8 -*-

import FastNet, pkt, json, yaml, time
import App,Helper
import Signals

from PyQt5 import QtWidgets, uic,QtCore, QtGui

import dlgs.AddPlatform
import dlgs.EditCodeDialog

from tabs.TableViewModel import TableViewModel


class PlatformMgr(QtWidgets.QWidget):
    def __init__(self, parent,datas):
        super(PlatformMgr, self).__init__()

        uic.loadUi('ui/platform_mgr.ui', self)

        keys = {'Platform':(['名称', '键值', '枚举值', '描述', '渠道列表'],[4]),
                'Channel':(['名称', '键值', '枚举值','登录公告', '描述','代码', '服务器分组列表'],[3,5,6]),
                'ServerGroup':(['名称', '描述','服务器列表'],[2]),
                'Platform2':(['平台对应渠道'],[]),
                'Channel2':(['渠道对应服务器分组'],[]),
                'ServerGroup2':(['服务器'],[])
                }

        for k,v in keys.items():
            exec('self.model{} = TableViewModel()'.format(k))
            tableView = eval('self.tableView{}'.format(k))
            model = eval('self.model{}'.format(k))

            tableView.setModel(model)
            tableView.horizontalHeader().setStretchLastSection(True)
            tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            tableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

            tableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            tableView.customContextMenuRequested['QPoint'].connect(self.OnCustomContextMenuRequested)

            tableView.selectionModel().currentChanged.connect(self.OnTableViewActivated)

            model.setHorizontalHeaderLabels(v[0])
            model.setColumnCount(len(v[0]))

            for vv in v[1]:
                tableView.hideColumn(vv)
            

        #self.modelLoginNotice = TableViewModel()

        #columnLabels = ['名称', '标题','公告']
        #self.modelLoginNotice.setHorizontalHeaderLabels(columnLabels)
        #self.modelLoginNotice.setColumnCount(len(columnLabels))

        #self.labelChannel.linkActivated.connect(self.OnLinkActivated)
        #self.labelChannel.setText(self.labelChannel.text() + " <a style='color: blue;' href = LoginNotice>编辑登录公告</a>  <a style='color: blue;' href = Code>编辑代码</a>")
        

        self.tableViewPlatform2.verticalHeader().setVisible(False)
        self.tableViewChannel2.verticalHeader().setVisible(False)
        self.tableViewServerGroup2.verticalHeader().setVisible(False)


    @property
    def ChannelModel(self):
        return self.modelChannel

    #def OnLinkActivated(self,url):
    #    if url == 'LoginNotice':
    #        dlg = dlgs.LoginNoticeDialog.LoginNoticeDialog(self,self.modelLoginNotice)
    #        dlg.exec_()
    #        dlg.destroy()
    #    else:
    #        dlg = dlgs.EditCodeDialog.EditCodeDialog(self)
    #        dlg.exec_()
    #        dlg.destroy()

    #def GetLoginNoticeList(self):
    #    values = ['']
    #    for i in range(0, self.modelLoginNotice.rowCount()):
    #        values.append(self.modelLoginNotice.item(i, 0).text())
    #    return values

    def GetChannelList(self):
        values = []
        for i in range(0, self.modelChannel.rowCount()):
            values.append(self.modelChannel.item(i, 0).text())
        return values

    def GetPlatformList(self):
        values = []
        for i in range(0, self.modelPlatform.rowCount()):
            values.append(self.modelPlatform.item(i, 0).text())
        return values

    def GetServerGroupList(self):
        values = []
        for i in range(0, self.modelServerGroup.rowCount()):
            values.append(self.modelServerGroup.item(i, 0).text())
        return values

    def GetServerList(self):
        model = App.App.Instance.MainWindow.GetTab('ServerMgr').Model
        values = []
        for i in range(0, model.rowCount()):
            values.append(model.item(i, 0).text())
        return values

    def OnTableViewActivated(self, index, r):
        if index.isValid() is True:

            if self.sender().parent() == self.tableViewPlatform:
                self.modelPlatform2.setRowCount(0)
                j = self.modelPlatform.index(index.row(), 4).data()
                if len(j) > 0:
                    for v in json.loads(j):
                        self.modelPlatform2.appendRow(QtGui.QStandardItem(v))
            elif self.sender().parent() == self.tableViewChannel:
                self.modelChannel2.setRowCount(0)
                j = self.modelChannel.index(index.row(), 6).data()
                if len(j) > 0:
                    for v in json.loads(j):
                        self.modelChannel2.appendRow(QtGui.QStandardItem(v))
            elif self.sender().parent() == self.tableViewServerGroup:
                self.modelServerGroup2.setRowCount(0)
                j = self.modelServerGroup.index(index.row(), 2).data()
                if len(j) > 0:
                    for v in json.loads(j):
                        self.modelServerGroup2.appendRow(QtGui.QStandardItem(v))  

    def RefreshData(self, j):
        type = j['type']
        if type == 'init':
            channels = j['channels']
            platforms = j['platforms']
            servergroups = j['servergroups']
            #loginnotices = j['loginnotices']

            self.modelChannel.setRowCount(0)
            for k, v in channels.items():
                self.modelChannel.appendRow(QtGui.QStandardItem())
                row = self.modelChannel.rowCount() - 1
                self.modelChannel.setData(self.modelChannel.index(row, 0), v['name'])
                self.modelChannel.setData(self.modelChannel.index(row, 1), v['key'])
                self.modelChannel.setData(self.modelChannel.index(row, 2), v['value'])
                self.modelChannel.setData(self.modelChannel.index(row, 3), v['loginNotice'])
                self.modelChannel.setData(self.modelChannel.index(row, 4), v['desc'])
                self.modelChannel.setData(self.modelChannel.index(row, 5), v['code'])
                self.modelChannel.setData(self.modelChannel.index(row, 6), v['param'])

            self.modelPlatform.setRowCount(0)
            for k, v in platforms.items():
                self.modelPlatform.appendRow(QtGui.QStandardItem())
                row = self.modelPlatform.rowCount() - 1
                self.modelPlatform.setData(self.modelPlatform.index(row, 0), v['name'])
                self.modelPlatform.setData(self.modelPlatform.index(row, 1), v['key'])
                self.modelPlatform.setData(self.modelPlatform.index(row, 2), v['value'])
                self.modelPlatform.setData(self.modelPlatform.index(row, 3), v['desc'])
                self.modelPlatform.setData(self.modelPlatform.index(row, 4), v['param'])

            self.modelServerGroup.setRowCount(0)
            for k, v in servergroups.items():
                self.modelServerGroup.appendRow(QtGui.QStandardItem())
                row = self.modelServerGroup.rowCount() - 1
                self.modelServerGroup.setData(self.modelServerGroup.index(row, 0), v['name'])
                self.modelServerGroup.setData(self.modelServerGroup.index(row, 1), v['desc'])
                self.modelServerGroup.setData(self.modelServerGroup.index(row, 2), v['param'])

            '''self.modelLoginNotice.setRowCount(0)
            for k, v in loginnotices.items():
                self.modelLoginNotice.appendRow(QtGui.QStandardItem())
                row = self.modelLoginNotice.rowCount() - 1
                self.modelLoginNotice.setData(self.modelLoginNotice.index(row, 0), v['name'])
                self.modelLoginNotice.setData(self.modelLoginNotice.index(row, 1), v['title'])
                self.modelLoginNotice.setData(self.modelLoginNotice.index(row, 2), v['text'])
            '''

        elif type == 'add':
            k = j['key']
            v = j['val']
            d = j['data']

            if v == 'platforms':
                self.modelPlatform.appendRow(QtGui.QStandardItem())
                row = self.modelPlatform.rowCount() - 1
                self.modelPlatform.setData(self.modelPlatform.index(row, 0), d['name'])
                self.modelPlatform.setData(self.modelPlatform.index(row, 1), d['key'])
                self.modelPlatform.setData(self.modelPlatform.index(row, 2), d['value'])
                self.modelPlatform.setData(self.modelPlatform.index(row, 3), d['desc'])
                self.modelPlatform.setData(self.modelPlatform.index(row, 4), d['param'])
                App.App.Instance.MainWindow.WriteLog('平台:{} 添加成功!'.format(k))
            elif v == 'channels':
                self.modelChannel.appendRow(QtGui.QStandardItem())
                row = self.modelChannel.rowCount() - 1
                self.modelChannel.setData(self.modelChannel.index(row, 0), d['name'])
                self.modelChannel.setData(self.modelChannel.index(row, 1), d['key'])
                self.modelChannel.setData(self.modelChannel.index(row, 2), d['value'])
                self.modelChannel.setData(self.modelChannel.index(row, 3), d['loginNotice'])
                self.modelChannel.setData(self.modelChannel.index(row, 4), d['desc'])
                self.modelChannel.setData(self.modelChannel.index(row, 5), d['code'])
                self.modelChannel.setData(self.modelChannel.index(row, 6), d['param'])
                App.App.Instance.MainWindow.WriteLog('渠道:{} 添加成功!'.format(k))
            elif v == 'servergroups':
                self.modelServerGroup.appendRow(QtGui.QStandardItem())
                row = self.modelServerGroup.rowCount() - 1
                self.modelServerGroup.setData(self.modelServerGroup.index(row, 0), d['name'])
                self.modelServerGroup.setData(self.modelServerGroup.index(row, 1), d['desc'])
                self.modelServerGroup.setData(self.modelServerGroup.index(row, 2), d['param'])
                App.App.Instance.MainWindow.WriteLog('服务器分组:{} 添加成功!'.format(k))
            '''elif v == 'loginnotices':
                self.modelLoginNotice.appendRow(QtGui.QStandardItem())
                row = self.modelLoginNotice.rowCount() - 1
                self.modelLoginNotice.setData(self.modelLoginNotice.index(row, 0), d['name'])
                self.modelLoginNotice.setData(self.modelLoginNotice.index(row, 1), d['title'])
                self.modelLoginNotice.setData(self.modelLoginNotice.index(row, 2), d['text'])
                App.App.Instance.MainWindow.WriteLog('渠道登录公告:{} 添加成功!'.format(k))   
            ''' 

        elif type == 'del':
            k = j['key']
            v = j['val']

            model = None
            if v == 'platforms':
                model = self.modelPlatform
                App.App.Instance.MainWindow.WriteLog('平台:{} 删除成功!'.format(k))
                self.modelPlatform2.setRowCount(0)
            elif v == 'channels':
                model = self.modelChannel
                App.App.Instance.MainWindow.WriteLog('渠道:{} 删除成功!'.format(k))
                self.modelChannel2.setRowCount(0)
            elif v == 'servergroups':
                model = self.modelServerGroup
                App.App.Instance.MainWindow.WriteLog('服务器分组:{} 删除成功!'.format(k))
                self.modelServerGroup2.setRowCount(0)
            #elif v == 'loginnotices':
            #    model = self.modelLoginNotice
            #    App.App.Instance.MainWindow.WriteLog('渠道登录公告:{} 删除成功!'.format(k))

            if model is not None:
                for i in range(0, model.rowCount()):
                    item = model.item(i, 0)
                    if k == item.text():
                        model.removeRow(item.row())
                        break

        elif type == 'modify':
            k = j['key']
            v = j['val']
            d = j['data']

            if v == 'platforms':
                row = None
                for i in range(0, self.modelPlatform.rowCount()):
                    if k == self.modelPlatform.item(i, 0).text():
                        row = i
                        break

                if row is None:
                    return

                if 'desc' in d:
                    self.modelPlatform.setData(self.modelPlatform.index(row, 3), d['desc'])
                
                if 'param' in d:
                    self.modelPlatform.setData(self.modelPlatform.index(row, 4), d['param'])

                    currentIndex = self.tableViewPlatform.currentIndex()
                    if currentIndex.isValid() is True and row == currentIndex.row():
                        self.modelPlatform2.setRowCount(0)
                        if len(j) > 0:
                            for v in json.loads(d['param']):
                                self.modelPlatform2.appendRow(QtGui.QStandardItem(v))

                App.App.Instance.MainWindow.WriteLog('平台:{} 保存成功!'.format(k))
            elif v == 'channels':
                row = None
                for i in range(0, self.modelChannel.rowCount()):
                    if k == self.modelChannel.item(i, 0).text():
                        row = i
                        break


                if row is None:
                    return

                if 'loginNotice' in d:
                    self.modelChannel.setData(self.modelChannel.index(row, 3), d['loginNotice'])
                if 'desc' in d:
                    self.modelChannel.setData(self.modelChannel.index(row, 4), d['desc'])
                if 'code' in d:
                    self.modelChannel.setData(self.modelChannel.index(row, 5), d['code'])
                if 'param' in d:
                    self.modelChannel.setData(self.modelChannel.index(row, 6), d['param'])

                    currentIndex = self.tableViewChannel.currentIndex()
                    if currentIndex.isValid() is True and row == currentIndex.row():
                        self.modelChannel2.setRowCount(0)
                        if len(j) > 0:
                            for v in json.loads(d['param']):
                                self.modelChannel2.appendRow(QtGui.QStandardItem(v))

                App.App.Instance.MainWindow.WriteLog('渠道:{} 保存成功!'.format(k))
            elif v == 'servergroups':
                row = None
                for i in range(0, self.modelServerGroup.rowCount()):
                    if k == self.modelServerGroup.item(i, 0).text():
                        row = i
                        break

                if row is None:
                    return

                if 'param' in d:
                    self.modelServerGroup.setData(self.modelServerGroup.index(row, 2), d['param'])

                    currentIndex = self.tableViewServerGroup.currentIndex()
                    if currentIndex.isValid() is True and row == currentIndex.row():
                        self.modelServerGroup2.setRowCount(0)
                        if len(j) > 0:
                            for v in json.loads(d['param']):
                                self.modelServerGroup2.appendRow(QtGui.QStandardItem(v))

                App.App.Instance.MainWindow.WriteLog('服务器分组:{} 保存成功!'.format(k))
            '''elif v == 'loginnotices':
                row = None
                for i in range(0, self.modelLoginNotice.rowCount()):
                    if k == self.modelLoginNotice.item(i, 0).text():
                        row = i
                        break

                if 'title' in d:
                    self.modelLoginNotice.setData(self.modelLoginNotice.index(row, 1), d['title'])

                if 'text' in d:
                    self.modelLoginNotice.setData(self.modelLoginNotice.index(row, 2), d['text'])

                App.App.Instance.MainWindow.WriteLog('渠道登录公告:{} 保存成功!'.format(k))
            '''

    def OnMenuAdd(self):
        if self.sender().parent() == self.tableViewPlatform:

            values = []
            values.append({'key':'name','name':'名称'})
            values.append({'key':'key','name':'键值'})
            values.append({'key':'value','name':'枚举值'})
            values.append({'key':'desc','name':'描述'})

            dlg = dlgs.AddPlatform.AddPlatform(self,'platforms','添加平台',values)
            data = dlg.GetData()
            if data is not None: 

                data['param'] = ""

                m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
                m.classId = self.__class__.__name__
                m.data = json.dumps({'type': 'add', 'key': data['name'],'val': 'platforms','data': data})
                Signals.gSignals.SendMsg.emit(m)
        elif self.sender().parent() == self.tableViewChannel:
            values = []
            values.append({'key':'name','name':'名称'})
            values.append({'key':'key','name':'键值'})
            values.append({'key':'value','name':'枚举值'})
            #values.append({'key':'loginNotice','name':'登录公告','enums':self.GetLoginNoticeList()})
            values.append({'key':'desc','name':'描述'})

            dlg = dlgs.AddPlatform.AddPlatform(self,'channels', '添加渠道',values)
            data = dlg.GetData()
            if data is not None: 

                data['param'] = ""
                data['loginNotice'] = {'title':'','text':'','beginTime':int(time.time()),'endTime':int(time.time())}
                data['code'] = json.loads(Helper.GetCode(80))

                m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
                m.classId = self.__class__.__name__
                m.data = json.dumps({'type': 'add', 'key': data['name'],'val': 'channels','data':data })
                Signals.gSignals.SendMsg.emit(m)

        elif self.sender().parent() == self.tableViewServerGroup:
            values = []
            values.append({'key':'name','name':'名称'})
            values.append({'key':'desc','name':'描述'})

            dlg = dlgs.AddPlatform.AddPlatform(self,'servergroups', '添加服务器分组',values)
            data = dlg.GetData()
            if data is not None: 
                data['param'] = ""

                m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
                m.classId = self.__class__.__name__
                m.data = json.dumps({'type': 'add', 'key': data['name'],'val': 'servergroups','data': data})
                Signals.gSignals.SendMsg.emit(m)
        elif self.sender().parent() == self.tableViewPlatform2:
            currentIndex = self.tableViewPlatform.currentIndex()
            if currentIndex.isValid() is False:
                return

            values = []
            values.append({'key':'name','name':'选择渠道','enums':self.GetChannelList()})

            dlg = dlgs.AddPlatform.AddPlatform(self,'platforms2', '附加新渠道',values)
            data = dlg.GetData()
            if data is not None: 
                names = []
                newName = data['name']
                if len(newName) < 1:
                    return

                for i in range(0, self.modelPlatform2.rowCount()):
                    names.append(self.modelPlatform2.item(i, 0).text())

                if newName not in names:
                    names.append(newName)
                    m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
                    m.classId = self.__class__.__name__
                    m.data = json.dumps({'type': 'modify', 
                                         'key': self.modelPlatform.item(currentIndex.row(),0).text(),
                                         'val': 'platforms',
                                         'data': {'param':json.dumps(names)}}
                                        )

                    Signals.gSignals.SendMsg.emit(m)

        elif self.sender().parent() == self.tableViewChannel2:
            currentIndex = self.tableViewChannel.currentIndex()
            if currentIndex.isValid() is False:
                return

            values = []
            values.append({'key':'name','name':'选择分组','enums':self.GetServerGroupList()})
            dlg = dlgs.AddPlatform.AddPlatform(self,'channels2', '附加新服务器分组',values)
            data = dlg.GetData()
            if data is not None:
                names = []
                newName = data['name']
                if len(newName) < 1:
                    return

                for i in range(0, self.modelChannel2.rowCount()):
                    names.append(self.modelChannel2.item(i, 0).text())

                if newName not in names:
                    names.append(newName)
                    m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
                    m.classId = self.__class__.__name__
                    m.data = json.dumps({'type': 'modify', 
                                         'key': self.modelChannel.item(currentIndex.row(),0).text(),
                                         'val': 'channels',
                                         'data': {'param':json.dumps(names)}}
                                        )

                    Signals.gSignals.SendMsg.emit(m)
        elif self.sender().parent() == self.tableViewServerGroup2:
            currentIndex = self.tableViewServerGroup.currentIndex()
            if currentIndex.isValid() is False:
                return

            values = []
            values.append({'key':'name','name':'选择服务器','enums':self.GetServerList()})
            dlg = dlgs.AddPlatform.AddPlatform(self,'servergroups2', '附加服务器',values)
            data = dlg.GetData()
            if data is not None:
                names = []
                newName = data['name']
                if len(newName) < 1:
                    return

                for i in range(0, self.modelServerGroup2.rowCount()):
                    names.append(self.modelServerGroup2.item(i, 0).text())

                if newName not in names:
                    names.append(newName)
                    m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
                    m.classId = self.__class__.__name__
                    m.data = json.dumps({'type': 'modify', 
                                         'key': self.modelServerGroup.item(currentIndex.row(),0).text(),
                                         'val': 'servergroups',
                                         'data': {'param':json.dumps(names)}}
                                        )

                    Signals.gSignals.SendMsg.emit(m)


    def OnMenuDel(self):

        index = self.sender().parent().currentIndex()
        if index.isValid() is True:
            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = self.__class__.__name__

            data = {'type': 'del'}
            if self.sender().parent() == self.tableViewPlatform:
                data['val'] = 'platforms'
                data['key'] = self.modelPlatform.index(index.row(), 0).data()
            elif self.sender().parent() == self.tableViewChannel:
                data['val'] = 'channels'
                data['key'] = self.modelChannel.index(index.row(), 0).data()
            elif self.sender().parent() == self.tableViewServerGroup:
                data['val'] = 'servergroups'
                data['key'] = self.modelServerGroup.index(index.row(), 0).data()
            elif self.sender().parent() == self.tableViewPlatform2:
                self.modelPlatform2.removeRow(index.row())

                index = self.tableViewPlatform.currentIndex()
                if index.isValid() is False:
                    return

                data = {'type': 'modify'}
                data['val'] = 'platforms'
                data['key'] = self.modelPlatform.index(index.row(), 0).data()

                names = []
                for i in range(0, self.modelPlatform2.rowCount()):
                    names.append(self.modelPlatform2.item(i, 0).text())

                data['data'] = {'param':json.dumps(names)}

                m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
                m.classId = self.__class__.__name__
                m.data = json.dumps(data)
                Signals.gSignals.SendMsg.emit(m)

            elif self.sender().parent() == self.tableViewChannel2:
                self.modelChannel2.removeRow(index.row())

                index = self.tableViewChannel.currentIndex()
                if index.isValid() is False:
                    return

                data = {'type': 'modify'}
                data['val'] = 'channels'
                data['key'] = self.modelChannel.index(index.row(), 0).data()

                names = []
                for i in range(0, self.modelChannel2.rowCount()):
                    names.append(self.modelChannel2.item(i, 0).text())

                data['data'] = {'param':json.dumps(names)}

                m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
                m.classId = self.__class__.__name__
                m.data = json.dumps(data)
                Signals.gSignals.SendMsg.emit(m)

            elif self.sender().parent() == self.tableViewServerGroup2:
                self.modelServerGroup2.removeRow(index.row())

                index = self.tableViewServerGroup.currentIndex()
                if index.isValid() is False:
                    return

                data = {'type': 'modify'}
                data['val'] = 'servergroups'
                data['key'] = self.modelServerGroup.index(index.row(), 0).data()

                names = []
                for i in range(0, self.modelServerGroup2.rowCount()):
                    names.append(self.modelServerGroup2.item(i, 0).text())

                data['data'] = {'param':json.dumps(names)}

                m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
                m.classId = self.__class__.__name__
                m.data = json.dumps(data)
                Signals.gSignals.SendMsg.emit(m)

            m.data = json.dumps(data)
            Signals.gSignals.SendMsg.emit(m)

    def OnMenuEdit(self):
        val = ""
        desc = ""

        model = self.sender().parent().model()
        index = self.sender().parent().currentIndex()

        if self.sender().parent() == self.tableViewPlatform:
            desc = model.index(index.row(), 3).data()
            val = "platforms"
        elif self.sender().parent() == self.tableViewChannel:
            desc = model.index(index.row(), 4).data()
            val = "channels"
        elif self.sender().parent() == self.tableViewServerGroup:
            desc = model.index(index.row(), 1).data()
            val = "servergroups"

        ret,okPressed = QtWidgets.QInputDialog.getText(self,'修改渠道','请输入描述:',QtWidgets.QLineEdit.Normal,desc)
        if okPressed is True and len(ret) > 0 and ret != desc:
            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = self.__class__.__name__
            m.data = json.dumps({'type': 'modify',
                                    'val':val ,
                                    'key': model.index(index.row(), 0).data(),
                                    'data':{'desc':ret}
                                })
            Signals.gSignals.SendMsg.emit(m)
    
    def OnMenuEditCode(self):
        if self.sender().parent() != self.tableViewChannel:
            return

        index = self.tableViewChannel.currentIndex()
        if index.isValid() is True:

            dlg = dlgs.EditCodeDialog.EditCodeDialog(self,index.row())
            dlg.exec_()
            dlg.destroy()


    def OnCustomContextMenuRequested(self, pt):
        actionAdd = QtWidgets.QAction("添加", self.sender(), triggered=self.OnMenuAdd)
        actionDel = QtWidgets.QAction("删除", self.sender(), triggered=self.OnMenuDel)
        
        #actionEditLoginVerifyCode = QtWidgets.QAction("编辑登录验证代码", self.sender(), triggered=self.OnMenuEditLoginVerifyCode)
        actionEditCode = QtWidgets.QAction("编辑代码", self.sender(), triggered=self.OnMenuEditCode)
        #actionEditLoginNotice = QtWidgets.QAction("编辑登录公告", self.sender(), triggered=self.OnMenuEditLoginNotice)
        actionEdit = QtWidgets.QAction("编辑描述", self.sender(), triggered=self.OnMenuEdit)

        menu = QtWidgets.QMenu("menu")
        menu.addAction(actionAdd)
        #menu.addAction(actionEdit)
        
        index = None
        if self.sender() == self.tableViewPlatform:
            index = self.tableViewPlatform.indexAt(pt)
        elif self.sender() == self.tableViewChannel:
            index = self.tableViewChannel.indexAt(pt)
            menu.addSeparator()
            #menu.addAction(actionEditLoginVerifyCode)
            #menu.addAction(actionEditPayNoticeCode)
            #menu.addAction(actionEditLoginNotice)
            menu.addAction(actionEditCode)
            
        elif self.sender() == self.tableViewServerGroup:
            index = self.tableViewServerGroup.indexAt(pt)

        if index is None or index.isValid() is False:
            actionDel.setEnabled(False)
            actionEdit.setEnabled(False)
            #actionEditLoginVerifyCode.setEnabled(False)
            actionEditCode.setEnabled(False)
            #actionEditLoginNotice.setEnabled(False)

        if index is not None:
            menu.addAction(actionEdit)

        menu.addSeparator()
        menu.addAction(actionDel)

        if self.sender() == self.tableViewPlatform2:
            if self.tableViewPlatform.currentIndex().isValid() is True:
                actionAdd.setEnabled(True)
                if self.tableViewPlatform2.currentIndex().isValid() is True:
                    actionDel.setEnabled(True)
                else:
                    actionDel.setEnabled(False)
            else:
                actionAdd.setEnabled(False)
                actionDel.setEnabled(False)

        elif self.sender() == self.tableViewChannel2:
            if self.tableViewChannel.currentIndex().isValid() is True:
                actionAdd.setEnabled(True)
                if self.tableViewChannel2.currentIndex().isValid() is True:
                    actionDel.setEnabled(True)
                else:
                    actionDel.setEnabled(False)
            else:
                actionAdd.setEnabled(False)
                actionDel.setEnabled(False)

        elif self.sender() == self.tableViewServerGroup2:
            if self.tableViewServerGroup.currentIndex().isValid() is True:
                actionAdd.setEnabled(True)
                if self.tableViewServerGroup2.currentIndex().isValid() is True:
                    actionDel.setEnabled(True)
                else:
                    actionDel.setEnabled(False)
            else:
                actionAdd.setEnabled(False)
                actionDel.setEnabled(False)

        menu.exec_(QtGui.QCursor.pos())

        #actionEditLoginNotice.deleteLater()
        actionEdit.deleteLater()
        actionAdd.deleteLater()
        actionDel.deleteLater()
        actionEditCode.deleteLater()
        menu.destroy()
