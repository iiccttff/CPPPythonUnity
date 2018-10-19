# -*- coding: utf-8 -*-
import FastNet, pkt, cfg, json, time, hashlib
import Signals
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import App,Signals
#from tabs.TableViewModel import TableViewModel


class AddUser(QtWidgets.QDialog):
    def __init__(self, parent,data = None):
        super(AddUser, self).__init__(parent)
        uic.loadUi('ui/adduser.ui', self)


        self.btnOK.clicked.connect(self.OnOk)

        self.model = QtGui.QStandardItemModel()
        self.model.setColumnCount(1)

        self.treeView.setModel(self.model)
        self.treeView.header().hide()
        self.treeView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        if data is not None:
            self.setWindowTitle('编辑用户')

            permissions = data['permissions']

            self.lineEditName.setReadOnly(True)
            self.lineEditAccount.setReadOnly(True)

            self.lineEditName.setText(data['name'])
            self.lineEditAccount.setText(data['account'])
            self.lineEditPassword.setText(data['password'])
            self.lineEditDesc.setText(data['desc'])


            for k,v in App.App.Instance.MainWindow.Tabs.items():
                self.Append(v.windowTitle(),k,permissions[k])
        else:
            for k,v in App.App.Instance.MainWindow.Tabs.items():
                self.Append(v.windowTitle(),k,None)


    def Append(self,name,key,val = None,parent = None,checkable = True):

        item = QtGui.QStandardItem()
        
        item.setText(name)
        item.setData(key,QtCore.Qt.UserRole + 2)

        if checkable == True:
            item.setCheckable(True)
            item.setFlags(QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable)

            if val is not None and val[0] is True:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)

        else:
            item.setFlags(QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable)


        if parent is None:
            self.model.appendRow(item)
        else:
            parent.appendRow(item)

        values = []

        if key == 'PlatformMgr_Channel':
            if val is not None:
                values.append(('允许访问所有渠道','AllowAll','AllowAll' in val))
                platformMgr = App.App.Instance.MainWindow.GetTab('PlatformMgr')
                for v in platformMgr.GetChannelList():
                    values.append((v,v,v in val))
            else:
                values.append(('允许访问所有渠道','AllowAll',False))
                platformMgr = App.App.Instance.MainWindow.GetTab('PlatformMgr')
                for v in platformMgr.GetChannelList():
                    values.append((v,v,False))

        elif key == 'PlatformMgr_Platform':
            if val is not None:
                values.append(('允许访问所有平台','AllowAll','AllowAll' in val))
                platformMgr = App.App.Instance.MainWindow.GetTab('PlatformMgr')
                for v in platformMgr.GetPlatformList():
                    values.append((v,v,v in val))
            else:
                values.append(('允许访问所有平台','AllowAll',False))
                platformMgr = App.App.Instance.MainWindow.GetTab('PlatformMgr')
                for v in platformMgr.GetPlatformList():
                    values.append((v,v,False))
            
        elif key == 'PlatformMgr_Server':
            if val is not None:
                values.append(('允许访问所有服务器','AllowAll','AllowAll' in val))
                platformMgr = App.App.Instance.MainWindow.GetTab('PlatformMgr')
                for v in platformMgr.GetServerList():
                    values.append((v,v,v in val))
            else:
                values.append(('允许访问所有服务器','AllowAll',False))
                platformMgr = App.App.Instance.MainWindow.GetTab('PlatformMgr')
                for v in platformMgr.GetServerList():
                    values.append((v,v,False))

        elif key == 'DataQuery':
            for v in cfg.globals.modules.DataQuery.GetValues():
                if val is not None and val[0] is True:
                    values.append((v.name,v.key,v.key in val[1]))
                else:
                    values.append((v.name,v.key,False))

        elif key == 'PlatformMgr':
            if val is not None:
                self.Append('渠道','PlatformMgr_Channel',val[1]['Channel'],item,False)
                self.Append('平台','PlatformMgr_Platform',val[1]['Platform'],item,False)
                self.Append('服务器','PlatformMgr_Server',val[1]['Server'],item,False)
            else:
                self.Append('渠道','PlatformMgr_Channel',None,item,False)
                self.Append('平台','PlatformMgr_Platform',None,item,False)
                self.Append('服务器','PlatformMgr_Server',None,item,False)

        elif key == 'NoticeMgr':

            if val is not None and val[0] is True:
                values.append(('允许发送全服公告','AllowAllServer','AllowAllServer' in val[1]))
                values.append(('允许发送平台公告','AllowPlatform','AllowPlatform' in val[1]))
                values.append(('允许发送服务器公告','AllowServer','AllowServer' in val[1]))
                values.append(('允许查看其他用户的公告列表','AllowCheck','AllowCheck' in val[1]))
            else:
                values.append(('允许发送全服公告','AllowAllServer',False))
                values.append(('允许发送平台公告','AllowPlatform',False))
                values.append(('允许发送服务器公告','AllowServer',False))
                values.append(('允许查看其他用户的公告列表','AllowCheck',False))
        elif key == 'MailMgr':

            if val is not None and val[0] is True:
                values.append(('允许发送全服邮件','AllowAllServer','AllowAllServer' in val[1]))
                values.append(('允许发送平台邮件','AllowPlatform','AllowPlatform' in val[1]))
                values.append(('允许发送服务器邮件','AllowServer','AllowServer' in val[1]))
                values.append(('允许查看其他用户的邮件列表','AllowCheck','AllowCheck' in val[1]))
            else:
                values.append(('允许发送全服邮件','AllowAllServer',False))
                values.append(('允许发送平台邮件','AllowPlatform',False))
                values.append(('允许发送服务器邮件','AllowServer',False))
                values.append(('允许查看其他用户的邮件列表','AllowCheck',False))

        for n,k,v in values:
            c = QtGui.QStandardItem()
            c.setCheckable(True)
            c.setText(n)
            c.setData(k,QtCore.Qt.UserRole + 2)
            c.setFlags(QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable)

            if v:
                c.setCheckState(QtCore.Qt.Checked)
            else:
                c.setCheckState(QtCore.Qt.Unchecked)

            item.appendRow(c)

    def GetChildItemData(self,item):
        values = []
        for i in range(0,item.rowCount()):
            c = item.child(i,0)
            if c.checkState() != QtCore.Qt.Checked:
                continue
            
            values.append(c.data(QtCore.Qt.UserRole + 2))
        return values

    def OnOk(self):
        self.permissions = {}
        self.name = self.lineEditName.text()
        self.account = self.lineEditAccount.text()
        self.password = self.lineEditPassword.text()
        self.desc = self.lineEditDesc.text()

        if len(self.name) < 1 or len(self.account) < 1 or len(self.password) < 1:
            QtWidgets.QMessageBox.critical(self, '参数错误', '请输入正确的参数',
                QtWidgets.QMessageBox.Yes , QtWidgets.QMessageBox.Yes)
            return

        for i in range(0,self.model.rowCount()):
            item = self.model.item(i,0)
            key = item.data(QtCore.Qt.UserRole + 2)
            enabled = item.checkState() == QtCore.Qt.Checked

            if key == 'PlatformMgr':
                server = []
                platform = []
                channel = []

                for j in range(0,item.rowCount()):
                    c = item.child(j,0)
                    c_key = c.data(QtCore.Qt.UserRole + 2)
                    
                    if c_key == 'PlatformMgr_Server':
                        server = self.GetChildItemData(c)
                    elif c_key == 'PlatformMgr_Platform':
                        platform = self.GetChildItemData(c)
                    elif c_key == 'PlatformMgr_Channel':
                        channel = self.GetChildItemData(c)

                self.permissions[key] = (enabled,{'Server':server,'Platform':platform,'Channel':channel})
            elif key == 'ServerMgr':
                if enabled is True:
                    self.permissions[key] = (enabled,cfg.globals.modules.ServerMgr.GetKeys())
                else:
                    self.permissions[key] = (enabled,None)

            elif key == 'UserMgr':
                self.permissions[key] = (enabled,None)

            elif key == 'DataQuery':
                self.permissions[key] = (enabled,self.GetChildItemData(item))

            elif key == 'NoticeMgr' or key == 'MailMgr':
                if enabled is True:
                    self.permissions[key] = (enabled,self.GetChildItemData(item))
                else:
                    self.permissions[key] = (enabled,None)

        self.done(QtWidgets.QDialog.Accepted)

    def GetData(self):
        ret = self.exec_()
        self.deleteLater()
        if ret == QtWidgets.QDialog.Accepted:
            datas = {}
            datas['permissions'] = self.permissions
            datas['name'] = self.name
            datas['account'] = self.account
            datas['password'] = self.password
            datas['desc'] = self.desc
            return datas
        return None