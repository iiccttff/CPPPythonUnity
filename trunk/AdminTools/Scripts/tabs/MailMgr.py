# -*- coding: utf-8 -*-
import FastNet
import App, Signals, pkt, json, cfg, hashlib, time
from PyQt5 import QtWidgets, uic, QtCore, QtGui
import importlib

from tabs.TableViewModel import TableViewModel

class MailMgr(QtWidgets.QWidget):
    def __init__(self, parent,datas):
        super(MailMgr, self).__init__(parent)

        uic.loadUi('ui/mail.ui', self)

        self.model = TableViewModel()

        self.tableViewMailList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableViewMailList.customContextMenuRequested['QPoint'].connect(self.OnCustomContextMenuRequested)

        self.tableViewMailList.setModel(self.model)
        self.tableViewMailList.horizontalHeader().setStretchLastSection(True)
        self.tableViewMailList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableViewMailList.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableViewMailList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        #self.tableViewMailList.selectionModel().currentChanged.connect(self.OnTableViewActivated)


        columnLabels = ['ID','标题', '发送状态', '发送时间', '有效天数', '参数', '附件' ,'操作人', '描述']

        self.model.setHorizontalHeaderLabels(columnLabels)
        self.model.setColumnCount(len(columnLabels))

        self.tableViewMailList.setColumnWidth(0,140)
        self.tableViewMailList.setColumnWidth(3,140)
        self.tableViewMailList.setColumnWidth(5,180)
        self.tableViewMailList.setColumnWidth(6,180)
        #self.tableViewMailList.hideColumn(0)

        self.tab_datas = datas


    def UpdateStatusText(self,row,status):
        if status is True:
            self.model.setData(self.model.index(row, 2),"已发送")
            self.model.item(row,2).setForeground(QtGui.QColor(242,63,64))
        else:  
            self.model.setData(self.model.index(row, 2),"未发送")
            self.model.item(row,2).setForeground(QtGui.QColor(65,173,66))
            

    def UpdateDateText(self,row,date):
        self.model.setData(self.model.index(row, 3),time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(date)))


    def UpdateAttachText(self,row,attach):

        attachText = []
        for v in attach:
            attachText.append('{}*{}'.format(v[0],v[1]))

        showText = '[' + ', '.join(attachText) + ']'

        self.model.setData(self.model.index(row, 6),showText)

    def UpdateParamText(self,row,param):
        showText = ''
        t = param['type']
        if t == 'Roles':
            paramText = []
            for v in param['param']:
                paramText.append('{}:{}'.format(v[1],v[0]))

            showText = '角色:[' + ', '.join(paramText) + ']'
        elif t == 'Server':
            showText = '服务器:'+ param['param']
        elif t == 'Platform':
            showText = '平台:' + param['param']
        elif t == 'Channel':
            showText = '渠道:'+ param['param']
        elif t == 'AllServer':
            showText = '全服'

        self.model.setData(self.model.index(row, 5),showText)

    def OnTableViewActivated(self, index, r):
        if index.isValid() is True:
            param = index.data()
            self.model.index(row, 0)
            #self.modelTree

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
                self.UpdateDateText(row,v.get('date',None))
                #self.model.setData(self.model.index(row, 3), v['date'])
                self.model.setData(self.model.index(row, 4), v['valid'])
                #self.model.setData(self.model.index(row, 5), v['param'])
                self.UpdateParamText(row,v['param'])
                #self.model.setData(self.model.index(row, 5), v['attach'])
                self.UpdateAttachText(row,v['attach'])
                self.model.setData(self.model.index(row, 7), v['role'])
                self.model.setData(self.model.index(row, 8), v['desc'])

        elif t == 'add':
            d = j['val']
            k = j['key']

            self.model.appendRow(QtGui.QStandardItem())

            row = self.model.rowCount() - 1

            self.model.setData(self.model.index(row, 0), d['name'])
            self.model.setData(self.model.index(row, 1), d['title'])
            #self.model.setData(self.model.index(row, 2), d['status'])
            self.UpdateStatusText(row,d.get('status',None))
            self.UpdateDateText(row,d.get('date',None))
            #self.model.setData(self.model.index(row, 3), d['date'])
            self.model.setData(self.model.index(row, 4), d['valid'])
            #self.model.setData(self.model.index(row, 5), d['param'])
            self.UpdateParamText(row,d['param'])
            #self.model.setData(self.model.index(row, 5), d['attach'])
            self.UpdateAttachText(row,d['attach'])
            self.model.setData(self.model.index(row, 7), d['role'])
            self.model.setData(self.model.index(row, 8), d['desc'])

            App.App.Instance.MainWindow.WriteLog('邮件:{} 添加成功!'.format(d['name']))


        elif t == 'del':
            k = j['key']

            for i in range(0, self.model.rowCount()):
                if self.model.index(i, 0).data() == k:
                    self.model.removeRow(i)
                    App.App.Instance.MainWindow.WriteLog('邮件:{} 删除成功!'.format(k))
                    break

    def OnMenuAdd(self):
        
        m = importlib.import_module('dlgs.AddMail')
        importlib.reload(m)

        dlg = m.AddMail(self,self.tab_datas)
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
        index = self.tableViewMailList.currentIndex()
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
        

        index = self.tableViewMailList.currentIndex()
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