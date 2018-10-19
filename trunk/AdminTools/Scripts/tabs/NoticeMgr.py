# -*- coding: utf-8 -*-
import FastNet
import App, Signals, pkt, json, cfg, time
from PyQt5 import QtWidgets, uic, QtCore, QtGui
import importlib

from tabs.TableViewModel import TableViewModel

class NoticeMgr(QtWidgets.QWidget):
    def __init__(self, parent,datas):
        super(NoticeMgr, self).__init__(parent)

        uic.loadUi('ui/notice.ui', self)

        self.tab_datas = datas
        self.model = TableViewModel()

        self.tableViewNoticeList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableViewNoticeList.customContextMenuRequested['QPoint'].connect(self.OnCustomContextMenuRequested)

        self.tableViewNoticeList.setModel(self.model)
        self.tableViewNoticeList.horizontalHeader().setStretchLastSection(True)
        self.tableViewNoticeList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableViewNoticeList.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableViewNoticeList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        #self.tableViewNoticeList.selectionModel().currentChanged.connect(self.OnTableViewActivated)


        columnLabels = ['ID','标题', '发送状态', '类型', '开始时间', '结束时间', '持续(秒)', '参数' ,'操作人', '描述']

        self.model.setHorizontalHeaderLabels(columnLabels)
        self.model.setColumnCount(len(columnLabels))

        self.tableViewNoticeList.setColumnWidth(0,140)
        self.tableViewNoticeList.setColumnWidth(4,140)
        self.tableViewNoticeList.setColumnWidth(5,180)
        self.tableViewNoticeList.setColumnWidth(7,140)

        self.datas = None



    def UpdateNoticeTypeText(self,row,t):
        if 'login' == t:
            self.model.setData(self.model.index(row, 3),"登录公告")
        elif 'game' == t:
            self.model.setData(self.model.index(row, 3),"滚动公告")
        elif 'push' == t:
            self.model.setData(self.model.index(row, 3),"推送公告")
             
    def UpdateStatusText(self,row,status):
        if status is True:
            self.model.setData(self.model.index(row, 2),"已发送")
            self.model.item(row,2).setForeground(QtGui.QColor(242,63,64))
        else:  
            self.model.setData(self.model.index(row, 2),"未发送")
            self.model.item(row,2).setForeground(QtGui.QColor(65,173,66))


    def ToDateText(self,date):
        #self.model.setData(self.model.index(row, 3),)
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(date))

    def UpdateParamText(self,row,param):
        showText = ''
        t = param['type']
        if t == 'Server':
            showText = '服务器:'+ param['param']
        elif t == 'Platform':
            showText = '平台:' + param['param']
        elif t == 'Channel':
            showText = '渠道:'+ param['param']
        elif t == 'AllServer':
            showText = '全服'

        self.model.setData(self.model.index(row, 7),showText)

    def RefreshData(self, j):

        t = j['type']
        if t == 'init':
            self.datas = j

            for k,v in j['val'].items():
                self.model.appendRow(QtGui.QStandardItem())

                row = self.model.rowCount() - 1

                self.model.setData(self.model.index(row, 0), v['name'])
                self.model.setData(self.model.index(row, 1), v['title'])
                #self.model.setData(self.model.index(row, 2), v['status'])
                self.UpdateStatusText(row,v.get('status',None))

                self.UpdateNoticeTypeText(row,v.get('type',None))
                

                self.model.setData(self.model.index(row, 4), self.ToDateText(v['beginTime']))
                self.model.setData(self.model.index(row, 5), self.ToDateText(v['endTime']))

                self.model.setData(self.model.index(row, 6), v['valid'])
                self.UpdateParamText(row,v['param'])

                self.model.setData(self.model.index(row, 8), v['role'])
                self.model.setData(self.model.index(row, 9), v['desc'])

        elif t == 'add':
            d = j['val']
            k = j['key']

            self.model.appendRow(QtGui.QStandardItem())

            row = self.model.rowCount() - 1

            self.model.setData(self.model.index(row, 0), d['name'])
            self.model.setData(self.model.index(row, 1), d['title'])
            #self.model.setData(self.model.index(row, 2), d['status'])
            self.UpdateStatusText(row,d.get('status',None))

            self.UpdateNoticeTypeText(row,d.get('type',None))
            
            self.model.setData(self.model.index(row, 4), self.ToDateText(d['beginTime']))
            self.model.setData(self.model.index(row, 5), self.ToDateText(d['endTime']))

            self.model.setData(self.model.index(row, 6), d['valid'])
            self.UpdateParamText(row,d['param'])

            self.model.setData(self.model.index(row, 8), d['role'])
            self.model.setData(self.model.index(row, 9), d['desc'])

            App.App.Instance.MainWindow.WriteLog('公告:{} 添加成功!'.format(d['name']))


        elif t == 'del':
            k = j['key']

            for i in range(0, self.model.rowCount()):
                if self.model.index(i, 0).data() == k:
                    self.model.removeRow(i)
                    App.App.Instance.MainWindow.WriteLog('公告:{} 删除成功!'.format(k))
                    break

    def OnMenuAdd(self):
        
        m = importlib.import_module('dlgs.AddNotice')
        importlib.reload(m)

        dlg = m.AddNotice(self,self.tab_datas)
        data = dlg.GetData()
        if data is not None:

            m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
            m.classId = self.__class__.__name__
            m.data = json.dumps({'type': 'add',
                                    'key':data['name'],
                                    'val':data
                                })
            Signals.gSignals.SendMsg.emit(m)

    def OnMenuDel(self):
        index = self.tableViewNoticeList.currentIndex()
        if index.isValid() is False:
            return

        m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
        m.classId = self.__class__.__name__
        m.data = json.dumps({'type': 'del',
                                'key': self.model.index(index.row(), 0).data()
                            })
        Signals.gSignals.SendMsg.emit(m)
    

    def OnCustomContextMenuRequested(self, pt):

        actionAdd = QtWidgets.QAction("添加", None, triggered=self.OnMenuAdd)
        #actionModify = QtWidgets.QAction("查看", None, triggered=self.OnMenuModify)
        actionDel = QtWidgets.QAction("删除", None, triggered=self.OnMenuDel)
        

        index = self.tableViewNoticeList.currentIndex()
        if index.isValid() is False:
            actionDel.setEnabled(False)
            #actionModify.setEnabled(False)

        menu = QtWidgets.QMenu("menu")
        menu.addAction(actionAdd)
        #menu.addAction(actionModify)
        menu.addSeparator()
        menu.addAction(actionDel)
        menu.exec_(QtGui.QCursor.pos())
        menu.destroy()