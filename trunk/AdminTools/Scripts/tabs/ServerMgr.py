# -*- coding: utf-8 -*-
import FastNet, pkt, cfg, json, sys, time
import Signals
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import App
import dlgs.AddPlatform
import dlgs.AddServer
import dlgs.AddTimerTask

from tabs.TableViewModel import TableViewModel

class ServerMgr(QtWidgets.QWidget):
    def __init__(self, parent, datas):
        super(ServerMgr, self).__init__(parent)

        uic.loadUi('ui/server_mgr.ui', self)


        self.tableViewServer=QtWidgets.QTableView(self)
        self.verticalLayout.insertWidget(1,self.tableViewServer)

        self.tableViewServer.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableViewServer.customContextMenuRequested['QPoint'].connect(self.OnCustomContextMenuRequested)

        self.model = TableViewModel()

        self.tableViewServer.setModel(self.model)
        self.tableViewServer.horizontalHeader().setStretchLastSection(True)
        self.tableViewServer.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableViewServer.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableViewServer.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)


        columnLabels = ['名称', '编号', '状态', '维护', '定时任务','添加时间', '描述']

        self.model.setHorizontalHeaderLabels(columnLabels)
        self.model.setColumnCount(len(columnLabels))

        self.tableViewServer.setColumnWidth(2,60)
        self.tableViewServer.setColumnWidth(4,210)
        self.tableViewServer.setColumnWidth(5,140)
        #self.tableViewServer.doubleClicked.connect(self.OnTableViewDoubleClicked)
        


        self.modelSVNMgr = TableViewModel()
        columnLabels = ['名称', '地址', '用户名', '密码', '描述']

        self.modelSVNMgr.setHorizontalHeaderLabels(columnLabels)
        self.modelSVNMgr.setColumnCount(len(columnLabels))

        self.modelDaemon = TableViewModel()
        columnLabels = ['名称', 'ID', '状态' , '描述']

        self.modelDaemon.setHorizontalHeaderLabels(columnLabels)
        self.modelDaemon.setColumnCount(len(columnLabels))


        self.modelRepairWhitelist = TableViewModel()
        columnLabels = ['名称', '描述', '参数']

        self.modelRepairWhitelist.setHorizontalHeaderLabels(columnLabels)
        self.modelRepairWhitelist.setColumnCount(len(columnLabels))


        self.modelNewEnterNoticeMail = TableViewModel()
        columnLabels = ['名称', '描述', '参数']

        self.modelNewEnterNoticeMail.setHorizontalHeaderLabels(columnLabels)
        self.modelNewEnterNoticeMail.setColumnCount(len(columnLabels))




        labelText = ''
        if datas is not None:
            for v in datas:
            
                item = cfg.globals.modules.ServerMgr.GetValue(v)
                if item is not None:
                    labelText += "<a style='color: blue;' href = {}>{}</a> ".format(item.key,item.name)
        
        self.labelBtns.setText(labelText)
        self.labelBtns.linkActivated.connect(self.OnLinkActivated)


        self.names = []

        self.names.append(['名称','name'])
        self.names.append(['唯一ID','id'])
        self.names.append(['辅助进程','daemon'])
        #self.names.append(['内网地址','lan'])
        self.names.append(['外网地址','wan'])
        self.names.append(['项目名称','projectName'])
        self.names.append(['启动参数','startParam'])
        self.names.append(['代码','code'])
        self.names.append(['配置文件','cfg'])
        self.names.append(['客户端资源','client'])
        self.names.append(['维护白名单','repairWhitelist'])
        self.names.append(['新进通知人数','newEnterNoticeNum'])
        self.names.append(['新进通知邮件','newEnterNoticeMail'])

        self.names.append(['爆满人数','overflowPlayerNum'])
        self.names.append(['拥挤人数','crowdingPlayerNum'])
        self.names.append(['流畅人数','smoothPlayerPlayerNum'])
        self.names.append(['最高同时在线人数','maxPlayerNum'])
        self.names.append(['预警人数','warningPlayerNum'])
        self.names.append(['排队期间每分钟进入人数','perMinuteEntryPlayerNum'])
        self.names.append(['描述','desc'])

        #self.datas = {}

    #def OnTableViewDoubleClicked(self, index):
    #    self.OnMenuModify()

    @property
    def Datas(self):
        return self.datas

    def OnLinkActivated(self,url):
        if 'addServer' == url:
            self.OnMenuAdd()
        else:
            dlg = None
            if 'svnMgr' == url:
                import dlgs.SVNMgrDialog
                dlg = dlgs.SVNMgrDialog.SVNMgrDialog(self,self.modelSVNMgr)

            elif 'daemon' == url:
                import dlgs.DaemonMgrDialog
                dlg = dlgs.DaemonMgrDialog.DaemonMgrDialog(self,self.modelDaemon)

            elif 'repairWhitelists' == url:
                import dlgs.RepairWhitelistDialog
                dlg = dlgs.RepairWhitelistDialog.RepairWhitelistDialog(self,self.modelRepairWhitelist)

            elif 'newEnterNoticeMails' == url:
                import dlgs.NewEnterNoticeMail
                dlg = dlgs.NewEnterNoticeMail.NewEnterNoticeMailDialog(self,self.modelNewEnterNoticeMail)


            if dlg is not None:
                dlg.exec_()
                dlg.destroy()

    def UpdateDaemonStatusText(self,status,row):
        if status != 0:
            self.modelDaemon.setData(self.modelDaemon.index(row, 2),"已连接")
            self.modelDaemon.item(row,2).setForeground(QtGui.QColor(65,173,66))
        else:
            self.modelDaemon.setData(self.modelDaemon.index(row, 2),"未连接")
            self.modelDaemon.item(row,2).setForeground(QtGui.QColor(242,63,64))


    def UpdateServerTimerTaskText(self,value,row):
        if value == '':
            self.model.setData(self.model.index(row, 4),"")
            #self.model.item(row,4).setForeground(QtGui.QColor(242,63,64))
        else:

            updateTime = time.strftime("%Y-%m-%d %H:%M", time.localtime(value['time']))

            if value['type'] == 'updateCode':
                self.model.setData(self.model.index(row, 4),"{} 更新代码".format(updateTime))
            else:
                self.model.setData(self.model.index(row, 4),"{} 更新配置".format(updateTime))
            
            self.model.item(row,4).setForeground(QtGui.QColor(173,193,33))

    def UpdateStatusText(self,status,repair,row):

        def _UpdateStatusTextForRow(self,row):
            serverName = self.model.item(row, 0).text()
            daemonName = self.datas['servers'][serverName]['daemon']
            daemonStatus = self.datas['daemons'][daemonName]['status']

            if repair == 'true':
                self.model.setData(self.model.index(row, 3),"维护中")
                self.model.item(row,3).setForeground(QtGui.QColor(242,63,64))
            else:
                self.model.setData(self.model.index(row, 3),"开放中")
                self.model.item(row,3).setForeground(QtGui.QColor(65,173,66))

            if daemonStatus != 0:
                if status == 'stop':
                    self.model.setData(self.model.index(row, 2),"停止")
                    self.model.item(row,2).setForeground(QtGui.QColor(242,63,64))
                elif status == 'starting':
                    self.model.setData(self.model.index(row, 2),"启动中")
                    self.model.item(row,2).setForeground(QtGui.QColor(56,139,240))
                elif status == 'running':
                    self.model.setData(self.model.index(row, 2),"运行")
                    self.model.item(row,2).setForeground(QtGui.QColor(65,173,66))
                elif status == 'stoping':
                    self.model.setData(self.model.index(row, 2),"停止中")
                    self.model.item(row,2).setForeground(QtGui.QColor(255,173,56))
                else:
                    self.model.setData(self.model.index(row, 2),"未知")
                    self.model.item(row,2).setForeground(QtCore.Qt.yellow)
            else:
                self.model.setData(self.model.index(row, 2),"未连接辅助进程")
                self.model.item(row,2).setForeground(QtGui.QColor(242,63,64))

        if row is not None:
            _UpdateStatusTextForRow(self,row)
        else:
            for i in range(0,self.model.rowCount()):
                _UpdateStatusTextForRow(self,i)

    @property
    def Model(self):
        return self.model

    def RefreshData(self, j):
        type = j['type']

        if type == 'init':
            self.datas = j

            for k,v in sorted(self.datas['servers'].items(), key=lambda x: x[1]['addtime']):
                self.model.appendRow(QtGui.QStandardItem())

                row = self.model.rowCount() - 1

                self.model.setData(self.model.index(row, 0), v['name'])
                self.model.setData(self.model.index(row, 1), v['id'])
                self.UpdateStatusText(v['status'],v['repair'],row)
                #self.model.setData(self.model.index(row, 4), v['timerTask'])
                self.UpdateServerTimerTaskText(v['timerTask'],row)

                self.model.setData(self.model.index(row, 5), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(v['addtime']))) )
                self.model.setData(self.model.index(row, 6), v['desc'])

            for k,v in self.datas['svns'].items():
                self.modelSVNMgr.appendRow(QtGui.QStandardItem())

                row = self.modelSVNMgr.rowCount() - 1

                self.modelSVNMgr.setData(self.modelSVNMgr.index(row, 0), v['name'])
                self.modelSVNMgr.setData(self.modelSVNMgr.index(row, 1), v['url'])
                self.modelSVNMgr.setData(self.modelSVNMgr.index(row, 2), v['username'])
                self.modelSVNMgr.setData(self.modelSVNMgr.index(row, 3), v['password'])
                self.modelSVNMgr.setData(self.modelSVNMgr.index(row, 4), v['desc'])


            for k,v in self.datas['daemons'].items():
                self.modelDaemon.appendRow(QtGui.QStandardItem())

                row = self.modelDaemon.rowCount() - 1

                self.modelDaemon.setData(self.modelDaemon.index(row, 0), v['name'])
                self.modelDaemon.setData(self.modelDaemon.index(row, 1), v['id'])
                #self.modelDaemon.setData(self.modelDaemon.index(row, 2), v['status'])
                self.UpdateDaemonStatusText(v['status'],row)
                self.modelDaemon.setData(self.modelDaemon.index(row, 3), v['desc'])

            for k,v in self.datas['repairWhitelists'].items():
                self.modelRepairWhitelist.appendRow(QtGui.QStandardItem())

                row = self.modelRepairWhitelist.rowCount() - 1

                self.modelRepairWhitelist.setData(self.modelRepairWhitelist.index(row, 0), v['name'])
                self.modelRepairWhitelist.setData(self.modelRepairWhitelist.index(row, 1), v['desc'])
                self.modelRepairWhitelist.setData(self.modelRepairWhitelist.index(row, 2), v['param'])


            for k,v in self.datas['newEnterNoticeMails'].items():
                self.modelNewEnterNoticeMail.appendRow(QtGui.QStandardItem())

                row = self.modelNewEnterNoticeMail.rowCount() - 1

                self.modelNewEnterNoticeMail.setData(self.modelNewEnterNoticeMail.index(row, 0), v['name'])
                self.modelNewEnterNoticeMail.setData(self.modelNewEnterNoticeMail.index(row, 1), v['desc'])
                self.modelNewEnterNoticeMail.setData(self.modelNewEnterNoticeMail.index(row, 2), v['param'])


            

        elif type == 'daemon_status':
            k = j['key']

            for i in range(0, self.modelDaemon.rowCount()):
                if k == self.modelDaemon.item(i, 0).text():
                    self.datas['daemons'][k]['status'] = j['data']
                    self.UpdateDaemonStatusText(j['data'],i)

                    for i in range(0, self.model.rowCount()):
                        serverName = self.model.item(i, 0).text()
                        serverStatus = self.datas['servers'][serverName]['status']
                        self.UpdateStatusText(serverStatus,self.datas['servers'][serverName]['repair'],i)

                    break

        elif type == 'status':
            k = j['key']

            for i in range(0, self.model.rowCount()):
                if k == self.model.item(i, 0).text():
                    self.datas['servers'][k]['status'] = j['status']
                    self.datas['servers'][k]['repair'] = j['repair']
                    self.UpdateStatusText(j['status'],j['repair'],i)

                    if 'timerTask' in j:
                        self.UpdateServerTimerTaskText(j['timerTask'],i)

                    break

        elif type == 'query':
            k = j['key']
            v = j['val']
            d = j['data']
            if v == 'svns':
                Signals.gSignals.QuerySvnLogs.emit(j['cmbox'],d)
                 
        elif type == 'add':
            d = j['data']
            k = j['key']
            v = j['val']

            self.datas[v][k] = d

            if v == 'servers':
                self.model.appendRow(QtGui.QStandardItem())

                row = self.model.rowCount() - 1

                self.model.setData(self.model.index(row, 0), d['name'])
                self.model.setData(self.model.index(row, 1), d['id'])
                self.UpdateStatusText(d['status'],d['repair'],row)
                self.UpdateServerTimerTaskText(d['timerTask'],row)
                #self.model.setData(self.model.index(row, 4), d['timerTask'])
                self.model.setData(self.model.index(row, 5), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(d['addtime']))) )
                self.model.setData(self.model.index(row, 6), d['desc'])

                App.App.Instance.MainWindow.WriteLog('服务器:{} 添加成功!'.format(d['name']))
            
            elif v == 'svns':
                self.modelSVNMgr.appendRow(QtGui.QStandardItem())

                row = self.modelSVNMgr.rowCount() - 1

                self.modelSVNMgr.setData(self.modelSVNMgr.index(row, 0), d['name'])
                self.modelSVNMgr.setData(self.modelSVNMgr.index(row, 1), d['url'])
                self.modelSVNMgr.setData(self.modelSVNMgr.index(row, 2), d['username'])
                self.modelSVNMgr.setData(self.modelSVNMgr.index(row, 3), d['password'])
                self.modelSVNMgr.setData(self.modelSVNMgr.index(row, 4), d['desc'])

                App.App.Instance.MainWindow.WriteLog('svn 地址:{} 添加成功!'.format(d['name']))

            elif v == 'daemons':
                self.modelDaemon.appendRow(QtGui.QStandardItem())

                row = self.modelDaemon.rowCount() - 1

                self.modelDaemon.setData(self.modelDaemon.index(row, 0), d['name'])
                self.modelDaemon.setData(self.modelDaemon.index(row, 1), d['id'])
                #self.modelDaemon.setData(self.modelDaemon.index(row, 2), d['status'])
                self.UpdateDaemonStatusText(d['status'],row)
                self.modelDaemon.setData(self.modelDaemon.index(row, 3), d['desc'])
                App.App.Instance.MainWindow.WriteLog('辅助进程:{} 添加成功!'.format(d['name']))

            elif v == 'repairWhitelists':
                self.modelRepairWhitelist.appendRow(QtGui.QStandardItem())

                row = self.modelRepairWhitelist.rowCount() - 1

                self.modelRepairWhitelist.setData(self.modelRepairWhitelist.index(row, 0), d['name'])
                self.modelRepairWhitelist.setData(self.modelRepairWhitelist.index(row, 1), d['desc'])
                self.modelRepairWhitelist.setData(self.modelRepairWhitelist.index(row, 2), d['param'])
                App.App.Instance.MainWindow.WriteLog('维护白名单:{} 添加成功!'.format(d['name']))


            elif v == 'newEnterNoticeMails':
                self.modelNewEnterNoticeMail.appendRow(QtGui.QStandardItem())

                row = self.modelNewEnterNoticeMail.rowCount() - 1

                self.modelNewEnterNoticeMail.setData(self.modelNewEnterNoticeMail.index(row, 0), d['name'])
                self.modelNewEnterNoticeMail.setData(self.modelNewEnterNoticeMail.index(row, 1), d['desc'])
                self.modelNewEnterNoticeMail.setData(self.modelNewEnterNoticeMail.index(row, 2), d['param'])
                App.App.Instance.MainWindow.WriteLog('邮件通知列表:{} 添加成功!'.format(d['name']))


        elif type == 'modify':
            d = j['data']
            k = j['key']
            v = j['val']

            for kk,vv in d.items():
                self.datas[v][k][kk] = vv

            if v == 'servers': 
                for i in range(0, self.model.rowCount()):
                    if k == self.model.item(i, 0).text():
                        if 'timerTask' in d:
                            self.UpdateServerTimerTaskText(d['timerTask'],i)
                            #self.model.setData(self.model.index(i, 4), d['timerTask'])

                        if 'desc' in d:
                            self.model.setData(self.model.index(i, 6), d['desc'])

                        App.App.Instance.MainWindow.WriteLog('服务器:{} 修改成功!'.format(k))
                        break
            elif v == 'svns': 
                for i in range(0, self.modelSVNMgr.rowCount()):
                    if k == self.modelSVNMgr.item(i, 0).text():
                        self.modelSVNMgr.setData(self.modelSVNMgr.index(i, 1), d['url'])
                        self.modelSVNMgr.setData(self.modelSVNMgr.index(i, 2), d['username'])
                        self.modelSVNMgr.setData(self.modelSVNMgr.index(i, 3), d['password'])
                        self.modelSVNMgr.setData(self.modelSVNMgr.index(i, 4), d['desc'])
                        App.App.Instance.MainWindow.WriteLog('svn 地址:{} 修改成功!'.format(k))
                        break

            elif v == 'daemons':
                for i in range(0, self.modelDaemon.rowCount()):
                    if k == self.modelDaemon.item(i, 0).text():
                        self.modelDaemon.setData(self.modelDaemon.index(i, 1), d['id'])
                        self.modelDaemon.setData(self.modelDaemon.index(i, 3), d['desc'])
                        App.App.Instance.MainWindow.WriteLog('辅助进程:{} 修改成功!'.format(k))
                        break

            elif v == 'repairWhitelists':
                for i in range(0, self.modelRepairWhitelist.rowCount()):
                    if k == self.modelRepairWhitelist.item(i, 0).text():
                        if 'desc' in d:
                            self.modelRepairWhitelist.setData(self.modelRepairWhitelist.index(i, 1), d['desc'])

                        if 'param' in d:
                            self.modelRepairWhitelist.setData(self.modelRepairWhitelist.index(i, 2), d['param'])

                        App.App.Instance.MainWindow.WriteLog('维护白名单:{} 修改成功!'.format(k))
                        break   
                    
            elif v == 'newEnterNoticeMails':
                for i in range(0, self.modelNewEnterNoticeMail.rowCount()):
                    if k == self.modelNewEnterNoticeMail.item(i, 0).text():
                        if 'desc' in d:
                            self.modelNewEnterNoticeMail.setData(self.modelNewEnterNoticeMail.index(i, 1), d['desc'])

                        if 'param' in d:
                            self.modelNewEnterNoticeMail.setData(self.modelNewEnterNoticeMail.index(i, 2), d['param'])

                        App.App.Instance.MainWindow.WriteLog('邮件通知列表:{} 修改成功!'.format(k))
                        break 



        elif type == 'del':
            k = j['key']
            v = j['val']
            
            self.datas[v].pop(k)

            if v == 'servers':
                for i in range(0, self.model.rowCount()):
                    if self.model.item(i, 0).text() == k:
                        self.model.removeRow(i)
                        App.App.Instance.MainWindow.WriteLog('服务器:{} 删除成功!'.format(k))
                        break

            elif v == 'svns':
                for i in range(0, self.modelSVNMgr.rowCount()):
                    if self.modelSVNMgr.item(i, 0).text() == k:
                        self.modelSVNMgr.removeRow(i)
                        App.App.Instance.MainWindow.WriteLog('svn 地址:{} 删除成功!'.format(k))
                        break

            elif v == 'daemons':
                for i in range(0, self.modelDaemon.rowCount()):
                    if self.modelDaemon.item(i, 0).text() == k:
                        self.modelDaemon.removeRow(i)
                        App.App.Instance.MainWindow.WriteLog('辅助进程:{} 删除成功!'.format(k))
                        break

            elif v == 'repairWhitelists':
                for i in range(0, self.modelRepairWhitelist.rowCount()):
                    if self.modelRepairWhitelist.item(i, 0).text() == k:
                        self.modelRepairWhitelist.removeRow(i)
                        App.App.Instance.MainWindow.WriteLog('维护白名单:{} 删除成功!'.format(k))
                        break

            elif v == 'newEnterNoticeMails':
                for i in range(0, self.modelNewEnterNoticeMail.rowCount()):
                    if self.modelNewEnterNoticeMail.item(i, 0).text() == k:
                        self.modelNewEnterNoticeMail.removeRow(i)
                        App.App.Instance.MainWindow.WriteLog('邮件通知列表:{} 删除成功!'.format(k))
                        break



    def OnMenuAdd(self):

        values = []

        for name,key in self.names:
            if key in ['daemon','code', 'cfg' , 'client' ,'repairWhitelist','newEnterNoticeMail']:

                if 'daemon' == key:
                    enums = list(self.datas['daemons'].keys())
                    values.append({'key':key,'name':name,'enums':enums})
                elif 'code' != key and 'cfg' != key and 'client' != key :
                    enums = list(self.datas[key + 's'].keys())
                    enums.insert(0,'')

                    values.append({'key':key,'name':name,'enums':enums})
                else:
                    enums = list(self.datas['svns'].keys())
                    values.append({'key':key,'name':name,'svnRevision':'','enums':enums})
            else:
                values.append({'key':key,'name':name})
                

        dlg = dlgs.AddServer.AddServer(self,'servers','添加服务器',values)
        data = dlg.GetData()
        if data is not None:
            data['timerTask'] = ""
            data['status'] = "stop"
            data['repair'] = "true"
            data['addtime'] = int(time.time())
            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = self.__class__.__name__
            m.data = json.dumps({'type': 'add',
                                 'val':'servers',
                                 'key': data['name'],
                                 'data':data
                                })

            Signals.gSignals.SendMsg.emit(m)

    def OnMenuModify(self):
        index = self.tableViewServer.currentIndex()
        if index.isValid() is False:
            return

        data = self.datas['servers'][self.model.item(index.row(), 0).text()]
        values = []

        for name,key in self.names:
            if key in ['daemon','code', 'cfg' ,'client', 'repairWhitelist','newEnterNoticeMail']:
                
                if 'daemon' == key:
                    enums = list(self.datas['daemons'].keys())
                    values.append({'key':key,'name':name,'enums':enums,'defaultVal':data[key]})

                elif 'code' != key and 'cfg' != key and 'client' != key:
                    enums = list(self.datas[key + 's'].keys())
                    enums.insert(0,'')
                    
                    if key in ['name','id']:
                        values.append({'key':key,'name':name,'enums':enums,'defaultVal':data[key],'widget':'ReadOnly'})
                    else:
                        values.append({'key':key,'name':name,'enums':enums,'defaultVal':data[key]})
                else:
                    enums = list(self.datas['svns'].keys())
                    values.append({
                        'key':key,
                        'name':name,
                        'enums':enums,
                        'svnRevision':data[key].split('|')[1],
                        'defaultVal':data[key].split('|')[0]})
            else:
                values.append({'key':key,'name':name,'defaultVal':data[key]})
                

        dlg = dlgs.AddServer.AddServer(self,'servers','编辑服务器',values)
        data = dlg.GetData()
        if data is not None:

            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = self.__class__.__name__
            m.data = json.dumps({'type': 'modify',
                                 'val':'servers',
                                 'key': self.model.item(index.row(), 0).text(),
                                 'data':data
                                })

            Signals.gSignals.SendMsg.emit(m)

    
    def OnMenuDel(self):
        index = self.tableViewServer.currentIndex()
        if index.isValid() is False:
            return

        m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
        m.classId = self.__class__.__name__
        m.data = json.dumps({'type': 'del',
                                'val':'servers',
                                'key': self.model.item(index.row(), 0).text()
                            })
        Signals.gSignals.SendMsg.emit(m)


    def OnMenuServerStart(self):
        index = self.tableViewServer.currentIndex()
        if index.isValid() is True:
            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = self.__class__.__name__
            m.data = json.dumps({'type': 'start',
                                    'val':'servers',
                                    'key': self.model.item(index.row(), 0).text()
                                })

            Signals.gSignals.SendMsg.emit(m)

    def OnMenuServerStop(self):
        index = self.tableViewServer.currentIndex()
        if index.isValid() is True:
            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = self.__class__.__name__
            m.data = json.dumps({'type': 'stop',
                                    'val':'servers',
                                    'key': self.model.item(index.row(), 0).text()
                                })

            Signals.gSignals.SendMsg.emit(m)


    def OnMenuServerBeginRepair(self):
        index = self.tableViewServer.currentIndex()
        if index.isValid() is True:
            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = self.__class__.__name__
            m.data = json.dumps({'type': 'beginRepair',
                                    'val':'servers',
                                    'key': self.model.item(index.row(), 0).text()
                                })

            Signals.gSignals.SendMsg.emit(m)

    def OnMenuServerEndRepair(self):
        index = self.tableViewServer.currentIndex()
        if index.isValid() is True:
            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = self.__class__.__name__
            m.data = json.dumps({'type': 'endRepair',
                                    'val':'servers',
                                    'key': self.model.item(index.row(), 0).text()
                                })

            Signals.gSignals.SendMsg.emit(m)

    def OnMenuServerTimerTask(self):
        index = self.tableViewServer.currentIndex()
        if index.isValid() is True:

            dlg = dlgs.AddTimerTask.AddTimerTaskDialog(self,self.datas['svns'].keys())
            data = dlg.GetData()
            if data is not None:
                m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
                m.classId = self.__class__.__name__
                m.data = json.dumps({'type': 'modify',
                                        'val':'servers',
                                        'key': self.model.item(index.row(), 0).text(),
                                        'data':{'timerTask':data}
                                    })

                Signals.gSignals.SendMsg.emit(m)

    def OnMenuUnServerTimerTask(self):
        index = self.tableViewServer.currentIndex()
        if index.isValid() is True:

            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = self.__class__.__name__
            m.data = json.dumps({'type': 'modify',
                                    'val':'servers',
                                    'key': self.model.item(index.row(), 0).text(),
                                    'data':{'timerTask':''}
                                })

            Signals.gSignals.SendMsg.emit(m)

    def OnCustomContextMenuRequested(self, pt):

        actionServerStart = QtWidgets.QAction("启动", None, triggered=self.OnMenuServerStart)
        actionServerStop = QtWidgets.QAction("停止", None, triggered=self.OnMenuServerStop)

        actionServerBeginRepair = QtWidgets.QAction("开始维护", None, triggered=self.OnMenuServerBeginRepair)
        actionServerEndRepair = QtWidgets.QAction("结束维护", None, triggered=self.OnMenuServerEndRepair)

        actionServerTimerTask = QtWidgets.QAction("设置定时任务", None, triggered=self.OnMenuServerTimerTask)
        actionServerUnTimerTask = QtWidgets.QAction("取消定时任务", None, triggered=self.OnMenuUnServerTimerTask)

        actionModify = QtWidgets.QAction("修改", None, triggered=self.OnMenuModify)
        actionDel = QtWidgets.QAction("删除", None, triggered=self.OnMenuDel)
        
        actionServerStop.setEnabled(False)
        actionServerStart.setEnabled(False)

        actionServerBeginRepair.setEnabled(False)
        actionServerEndRepair.setEnabled(False)
        actionServerTimerTask.setEnabled(False)
        actionServerUnTimerTask.setEnabled(False)

        index = self.tableViewServer.currentIndex()
        if index.isValid() is True:

            serverName = self.model.item(index.row(),0).text()

            status = self.datas['servers'][serverName]['status']
            repair = self.datas['servers'][serverName]['repair']
            timerTask = self.datas['servers'][serverName]['timerTask']

            if status != 'stop':
                actionDel.setEnabled(False)
                #actionModify.setEnabled(False)

            else:
                actionServerStart.setEnabled(True)

            if repair == 'true':
                actionServerEndRepair.setEnabled(True)
            else:
                actionServerBeginRepair.setEnabled(True)

            if status == 'running':
                actionServerStop.setEnabled(True)

            if status == 'starting':
                actionServerStop.setEnabled(True)

            if status == 'stop':
                if timerTask == '':
                    actionServerTimerTask.setEnabled(True)
                else:
                    actionServerUnTimerTask.setEnabled(True)
            
        else:
            actionDel.setEnabled(False)
            actionModify.setEnabled(False)
            actionServerStart.setEnabled(False)

            actionServerBeginRepair.setEnabled(False)
            actionServerEndRepair.setEnabled(False)

        menu = QtWidgets.QMenu("menu")
        menu.addAction(actionServerStart)
        menu.addAction(actionServerStop)
        menu.addSeparator()
        menu.addAction(actionServerBeginRepair)
        menu.addAction(actionServerEndRepair)
        menu.addSeparator()
        menu.addAction(actionServerTimerTask)
        menu.addAction(actionServerUnTimerTask)
        menu.addSeparator()
        menu.addAction(actionModify)
        menu.addSeparator()
        menu.addAction(actionDel)
        menu.exec_(QtGui.QCursor.pos())
        menu.destroy()