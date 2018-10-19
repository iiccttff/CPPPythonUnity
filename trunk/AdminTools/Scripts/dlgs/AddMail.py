# -*- coding: utf-8 -*-
import FastNet, pkt, cfg, json, time, hashlib
import Signals
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import App,Signals
from tabs.TableViewModel import TableViewModel



class ItemNumberDelegate(QtWidgets.QItemDelegate):

    def __init__(self, parent=None):
        super(ItemNumberDelegate, self).__init__(parent)
        
    def createEditor(self, parent, option, index):
        editor = super(ItemNumberDelegate, self).createEditor(parent, option, index)
        editor.setMinimum(1)
        return editor

class ServerNameDelegate(QtWidgets.QItemDelegate):

    def __init__(self, parent=None):
        super(ServerNameDelegate, self).__init__(parent)
        
    def createEditor(self, parent, option, index):
        combo = QtWidgets.QComboBox(parent)

        platformMgrTabInfo = App.App.Instance.MainWindow.TabValues.get('PlatformMgr',None)
        if 'AllowAll' in platformMgrTabInfo[1]['Server']:
            combo.setModel(App.App.Instance.MainWindow.GetTab('ServerMgr').Model)
        else:
            for v in platformMgrTabInfo[1]['Server']:
                combo.addItem(v)

        #combo.setModel(App.App.Instance.MainWindow.GetTab('ServerMgr').Model)
        combo.setMaxVisibleItems(20)
        #combo.setEditable(True)
        return combo

    def setEditorData(self, editor, index):
        d = index.model().data(index, QtCore.Qt.EditRole)
        if d is not None:
            editor.setCurrentText(str(d))

    def setModelData(self, editor, model, index):
        if editor.currentIndex() >= 0:
            realidx = editor.model().index(editor.currentIndex(), 0) #确保取第一列的值
            value = editor.model().data(realidx)
            model.setData(index, value, QtCore.Qt.EditRole)


class ComboBoxDelegate(QtWidgets.QItemDelegate):

    def __init__(self, comboModel,modelAttach, parent=None):
        super(ComboBoxDelegate, self).__init__(parent)
        self.comboModel = comboModel
        self.modelAttach = modelAttach

    def __createComboView(self, parent):
        view = QtWidgets.QTableView(parent)
        #view.setModel(self.comboModel)
        view.setAutoScroll(False)
        view.horizontalHeader().setStretchLastSection(True)
        view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        view.resizeColumnsToContents()
        view.resizeRowsToContents()
        view.setMinimumWidth(300)
        return view

    def createEditor(self, parent, option, index):
        combo = QtWidgets.QComboBox(parent)
        combo.setModel(self.comboModel)
        combo.setView(self.__createComboView(parent))
        combo.setMaxVisibleItems(20)
        combo.setEditable(True)
        return combo

    def setEditorData(self, editor, index):
        d = index.model().data(index, QtCore.Qt.EditRole)
        if d is not None:
            editor.setCurrentText(str(d))

    def setModelData(self, editor, model, index):
        if editor.currentIndex() >= 0:
            realidx = editor.model().index(editor.currentIndex(), 0) #确保取第一列的值
            value = editor.model().data(realidx)
            model.setData(index, value, QtCore.Qt.EditRole)
            
            ret = cfg.globals.base.Items.GetValue(int(value))
            if ret is not None:
                self.modelAttach.setData(self.modelAttach.index(index.row(), 2), ret.name.text)

class AddMail(QtWidgets.QDialog):
    def __init__(self, parent,datas):
        super(AddMail, self).__init__(parent)
        uic.loadUi('ui/addmail.ui', self)

        self.datas = {}

        self.btnOK.clicked.connect(self.OnOk)

        self.modelAttach = TableViewModel()

        columnLabels = ['ID','数量','名称']
        self.modelAttach.setHorizontalHeaderLabels(columnLabels)
        self.modelAttach.setColumnCount(len(columnLabels))


        self.modelRoles = TableViewModel()
        columnLabels = ['角色ID']
        self.modelRoles.setHorizontalHeaderLabels(columnLabels)
        self.modelRoles.setColumnCount(len(columnLabels))

        self.tableViewRoles.setModel(self.modelRoles)
        self.tableViewRoles.horizontalHeader().setStretchLastSection(True)
        #self.tableViewRoles.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        #self.tableViewRoles.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        #self.tableViewRoles.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.tableViewRoles.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableViewRoles.customContextMenuRequested['QPoint'].connect(self.OnCustomContextMenuRequested)
        #self.tableViewRoles.setItemDelegateForColumn(1, ServerNameDelegate(self.tableViewRoles))



        self.modelItems = TableViewModel()

        columnLabels = ['ID','名称']
        self.modelItems.setHorizontalHeaderLabels(columnLabels)
        self.modelItems.setColumnCount(len(columnLabels))

        for v in cfg.globals.base.Items.GetValues():
            self.modelItems.appendRow(QtGui.QStandardItem())
            row = self.modelItems.rowCount() - 1

            self.modelItems.setData(self.modelItems.index(row, 0), v.id)
            if v.name is not None:
                self.modelItems.setData(self.modelItems.index(row, 1), v.name.text)

        self.tableViewAttachs.setModel(self.modelAttach)
        self.tableViewAttachs.horizontalHeader().setStretchLastSection(True)
        #self.tableViewAttachs.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        #self.tableViewAttachs.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        #self.tableViewAttachs.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.tableViewAttachs.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableViewAttachs.customContextMenuRequested['QPoint'].connect(self.OnCustomContextMenuRequested)
        self.tableViewAttachs.setItemDelegateForColumn(0, ComboBoxDelegate(self.modelItems,self.modelAttach, self.tableViewAttachs))
        self.tableViewAttachs.setItemDelegateForColumn(1, ItemNumberDelegate(self.tableViewAttachs)) 

        self.radioButtonAllServer.clicked.connect(self.OnRadioChanged)
        self.radioButtonAllServer.btnName = 'AllServer'
        #self.comboBoxAllServer

        self.radioButtonServer.clicked.connect(self.OnRadioChanged)
        self.radioButtonServer.btnName = 'Server'
        #self.comboBoxServer

        self.radioButtonPlatform.clicked.connect(self.OnRadioChanged)
        self.radioButtonPlatform.btnName = 'Platform'

        #self.comboBoxPlatform

        self.radioButtonChannel.clicked.connect(self.OnRadioChanged)
        self.radioButtonChannel.btnName = 'Channel'

        #self.comboBoxChannel

        self.radioButtonRoles.clicked.connect(self.OnRadioChanged)
        self.radioButtonRoles.btnName = 'Roles'

        self.radioButtonAllServer.setEnabled(True if 'AllowAllServer' in datas else False)
        self.radioButtonPlatform.setEnabled(True if 'AllowPlatform' in datas else False)
        self.radioButtonServer.setEnabled(True if 'AllowServer' in datas else False)
        

        platformMgrTabInfo = App.App.Instance.MainWindow.TabValues.get('PlatformMgr',None)
        if platformMgrTabInfo is not None:
            if 'AllowAll' in platformMgrTabInfo[1]['Server']:
                self.comboBoxServer.setModel(App.App.Instance.MainWindow.GetTab('ServerMgr').Model)
            else:
                for v in platformMgrTabInfo[1]['Server']:
                    self.comboBoxServer.addItem(v)

            if 'AllowAll' in platformMgrTabInfo[1]['Platform']:
                self.comboBoxPlatform.setModel(App.App.Instance.MainWindow.GetTab('PlatformMgr').modelPlatform)
            else:
                for v in platformMgrTabInfo[1]['Platform']:
                    self.comboBoxPlatform.addItem(v)

            if 'AllowAll' in platformMgrTabInfo[1]['Channel']:
                self.comboBoxChannel.setModel(App.App.Instance.MainWindow.GetTab('PlatformMgr').modelChannel)
            else:
                for v in platformMgrTabInfo[1]['Channel']:
                    self.comboBoxChannel.addItem(v)

            #self.comboBoxServer.setModel(App.App.Instance.MainWindow.GetTab('ServerMgr').Model)
            #self.comboBoxPlatform.setModel(App.App.Instance.MainWindow.GetTab('PlatformMgr').modelPlatform)
            #self.comboBoxChannel.setModel(App.App.Instance.MainWindow.GetTab('PlatformMgr').modelChannel)

        #radioButtonSelect = self.radioButtonChannel
        #ret = App.App.Instance.Settings.value("AddMail/radioButtonSelect", None)
        #if ret is not None:
        #    radioButtonSelect = eval('self.radioButton{}'.format(ret))
        
        #radioButtonSelect.setChecked(True)
        self.OnRadioChanged(None)

    def OnRadioChanged(self,b):

        
        for v in[self.radioButtonAllServer,self.radioButtonServer,self.radioButtonPlatform,self.radioButtonChannel,self.radioButtonRoles]:
            if v.isChecked():
                self.radioButtonSelectName = v.btnName

        obj = None
        if self.radioButtonSelectName == 'Roles':
            obj = self.tableViewRoles
        else:
            obj = eval('self.comboBox{}'.format(self.radioButtonSelectName))

        obj.setEnabled(True)

        for v in [self.comboBoxAllServer,self.comboBoxServer,self.comboBoxPlatform,self.comboBoxChannel,self.tableViewRoles]:
            if v != obj:
                v.setEnabled(False)
    
    def OnOk(self):

        attach = []
        attachIds = set()
        for i in range(0, self.modelAttach.rowCount()):
            itemId = self.modelAttach.index(i, 0).data()
            itemNum = self.modelAttach.index(i, 1).data()
            if itemId is None:
                continue

            if itemId in attachIds: 
                QtWidgets.QMessageBox.critical(self, '参数错误', '附件ID重复,请删除重复的物品ID后再试!',QtWidgets.QMessageBox.Yes)
                return

            attachIds.add(itemId)
            attach.append((int(itemId),itemNum))

        
        param = {'type':self.radioButtonSelectName}
        if self.radioButtonSelectName == 'Roles':
            roleIds = []
            for i in range(0, self.modelRoles.rowCount()):
                roleId = self.modelRoles.index(i, 0).data()
                #serverName = self.modelRoles.index(i, 1).data()
                if roleId in roleIds:
                    QtWidgets.QMessageBox.critical(self, '参数错误', '角色ID重复,请删除重复的角色ID后再试!',QtWidgets.QMessageBox.Yes)
                    return

                #if serverName is None:
                #    QtWidgets.QMessageBox.critical(self, '参数错误', '服务器不能为空!',QtWidgets.QMessageBox.Yes)
                #    return

                roleIds.append(roleId)

            param['param'] = roleIds
        else:
            obj = eval('self.comboBox{}'.format(self.radioButtonSelectName))
            param['param'] = obj.currentText()

            if self.radioButtonSelectName != 'AllServer' and obj.currentText() == '':
                QtWidgets.QMessageBox.critical(self, '参数错误', '参数不能为空!',QtWidgets.QMessageBox.Yes)
                return

        now = time.time()
        data_head = time.strftime("%Y%m%d%H%M%S", time.localtime(now))
        data_secs = (now - int(now)) * 1000

        self.datas['name'] = "%s.%02d" % (data_head, data_secs)
        self.datas['title'] = self.comboBoxMailTitle.currentText()
        self.datas['text'] = self.textEditMailText.toPlainText()
        self.datas['date'] = self.dateTimeEdit.dateTime().toTime_t()
        self.datas['param'] = param
        self.datas['attach'] = attach
        self.datas['valid'] = self.spinBoxValidDayNum.value()
        self.datas['level'] = self.spinBoxLevel.value()
        self.datas['role'] = ''
        self.datas['desc'] = self.comboBoxDesc.currentText()
        self.datas['status'] = False
    
        #App.App.Instance.Settings.setValue("AddMail/radioButtonSelect",self.radioButtonSelectName)


        self.done(QtWidgets.QDialog.Accepted)

    def GetData(self):
        ret = self.exec_()
        self.deleteLater()
        if ret == QtWidgets.QDialog.Accepted:
            return self.datas
        return None


    def OnMenuAdd(self):
        
        tableView = self.sender().parent()

        model = None
        if tableView == self.tableViewAttachs:
            model = self.modelAttach
            model.appendRow(QtGui.QStandardItem())

            row = model.rowCount() - 1

            model.setData(model.index(row, 1), 1)
            model.setData(model.index(row, 2), '')

            item = model.item(row, 2)
            item.setFlags(item.flags() & (~QtCore.Qt.ItemIsEditable))

        elif tableView == self.tableViewRoles:
            model = self.modelRoles
            model.appendRow(QtGui.QStandardItem())

            row = model.rowCount() - 1

            model.setData(model.index(row, 1), '')
            model.setData(model.index(row, 2), '')
        

    def OnMenuDel(self):
        tableView = self.sender().parent()
        index = tableView.currentIndex()
        if index.isValid() is False:
            return

        if tableView == self.tableViewAttachs:
            self.modelAttach.removeRow(index.row())
        elif tableView == self.tableViewRoles:
            self.modelRoles.removeRow(index.row())
        
    def OnCustomContextMenuRequested(self, pt):

        actionAdd = QtWidgets.QAction("添加", self.sender(), triggered=self.OnMenuAdd)
        #actionModify = QtWidgets.QAction("查看", None, triggered=self.OnMenuModify)
        actionDel = QtWidgets.QAction("删除", self.sender(), triggered=self.OnMenuDel)
        

        index = self.sender().currentIndex()
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