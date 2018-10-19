# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets,uic

from PyQt5.QtCore import (QAbstractItemModel, QFileInfo, QItemSelectionModel,QFileSystemWatcher,
        QModelIndex, Qt)
from PyQt5.QtWidgets import QApplication, QMainWindow,QHBoxLayout,QSplitter,QTabWidget,QTextEdit,QHeaderView,QSpinBox,QTableWidget,QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QAbstractItemView,QStyleFactory,QTabBar,
        QFileIconProvider, QListView, QTableView, QTreeView,QUndoCommand,QItemDelegate,QStyledItemDelegate)
from PyQt5.QtGui import QStandardItemModel,QStandardItem,QColor

import time,os,json,sys

import SelectFolder,InputDialog,GridTableView,ExportDialog,GenProto
import traceback,zipfile,sqlite3

class MainWindow(QtWidgets.QMainWindow):

    Folder = 1
    File = 2
    Table = 3

    LogInfo = 101
    LogWarning = 102
    LogError = 103


    def LoadTableData(self,data,model):
        
        try:
            value = json.loads(data)
            table = value['table']
            model.setColumnCount(len(table))

            data = value['data']
            model.setRowCount(len(data) + 2)

            for v in table:
                model.setHeaderData(v[0],Qt.Horizontal,v[1])
                model.setData(model.index(0,v[0]),v[2])
                model.setData(model.index(1,v[0]),v[3])

            for i in range(0,len(data)):
                v = data[i]
                for j in range(0,len(v)):
                    model.setData(model.index(i+2,j),v[j])
                
            model.activeColumn = value['activeColumn']
        except Exception as e:
            pass

    def AddTreeItem(self,parent,text,type,isexpand = True):

        if parent == None:
            texts = text.split('.')
            if len(texts) > 1:
                rootItem = self.rootItem
                for i in range(0,len(texts)-1):
                    t = texts[i]
                    childItem = None
                    for j in range(0,rootItem.rowCount()):
                        childItem = rootItem.child(j,0)
                        if t == childItem.data():
                            break

                    rootItem = childItem
                parent = rootItem
                text = texts[-1]
            else:
                parent = self.rootItem

        lastFolderItem = None
        for i in range(0,parent.rowCount()):
            childItem = self.model.itemFromIndex(self.model.index(i,0,parent.index()))
            if childItem.data() == MainWindow.Folder:
                lastFolderItem = childItem

            if text == childItem.text():
                return None

        icon = None
        if type == MainWindow.Folder:
            icon = self.iconProvider.icon(QFileIconProvider.Folder)
        elif type == MainWindow.File:
            icon = self.iconProvider.icon(QFileIconProvider.File)
        elif type == MainWindow.Table:
            icon = self.iconProvider.icon(QFileIconProvider.Desktop)

        item = QStandardItem(parent)
        
        item.setIcon(icon)
        item.setText(text)
        item.setData(type)
        item.setFlags(QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable)

        if type == MainWindow.Folder and lastFolderItem != None:
            parent.insertRow(lastFolderItem.row()+1,item)
        else:
            parent.appendRow(item)
        
        if isexpand == True:
            self.tree.expand(parent.index())

        return item

    def SetRootTreeItem(self,text):
        self.rootItem = QStandardItem()
        self.rootItem.setIcon(self.iconProvider.icon(QFileIconProvider.Folder))
        self.rootItem.setText(text)
        self.rootItem.setData(MainWindow.Folder)

        self.model.appendRow(self.rootItem)

        for i in range(0,self.model.columnCount()):
            colItem = self.model.itemFromIndex(self.model.index(0,i))
            colItem.setFlags(QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable)

    def GetTreeItemShortPath(self,item):
        tempItem = item
        names = []
        while True:
            names.append(tempItem.text())
            tempItem = tempItem.parent()
            if tempItem == self.rootItem:
                break

        return '.'.join(reversed(names))

    def OnTreeCustomContextMenuRequested(self,pt):
        index = self.tree.indexAt(pt);  
        if index.isValid():

            item = self.model.itemFromIndex(index)

            parent = item.parent()
            if parent != None:
                item = self.model.itemFromIndex(self.model.index(item.row(),0,parent.index()))

            def OnAddTreeItem(self,item,type):
                inputDialog = InputDialog.InputDialog(self)
                ret = inputDialog.exec_()
                inputDialog.destroy()

                if QtWidgets.QDialog.Rejected == ret:
                    return

                if len(inputDialog.GetTextValue()) == 0:
                    return

                itemTable = self.AddTreeItem(item,str(inputDialog.GetTextValue()),type)

                if MainWindow.Table == type:
                    model = GridTableView.TableViewItemModel(2,0)
                    model.setParent(self.tree)
                    itemTable.setData(model,Qt.UserRole+2)

                cursor = None
                try:
                    cursor = self.db.cursor()
                    cursor.execute('insert into datas (k, v, t) values (\'{}\', \'{}\', {})'.format(self.GetTreeItemShortPath(itemTable),"None",type))
                    self.db.commit()
                except Exception as e:
                    pass
                finally:
                    cursor.close()

            def OnAddFolder(index,self = self,item = item):
                OnAddTreeItem(self,item,MainWindow.Folder)

            def OnAddFile(index,self = self,item = item):
                OnAddTreeItem(self,item,MainWindow.File)

            def OnAddTable(index,self = self,item = item):
                OnAddTreeItem(self,item,MainWindow.Table)

            def OnRename(index,self = self,item = item):
                inputDialog = InputDialog.InputDialog(self,item.text())
                ret = inputDialog.exec_()
                inputDialog.destroy()

                if QtWidgets.QDialog.Rejected == ret:
                    return

                text = inputDialog.GetTextValue()
                if len(text) == 0:
                    return

                #old_shortpath = self.GetTreeItemShortPath(item)
                

                items = []
                oldpaths = []

                if item.data() == MainWindow.Table:
                    items.append(item)
                else:
                    def GetAllChildItems(items,item):
                        for i in range(0,item.rowCount()):
                            childItem = item.child(i,0)

                            if childItem.data() != MainWindow.Table:
                                GetAllChildItems(items,childItem)
                            else:
                                items.append(childItem)
                        items.append(item)

                    GetAllChildItems(items,item)
                for v in items:
                    oldpaths.append(self.GetTreeItemShortPath(v))

                item.setText(text)
                cursor = self.db.cursor()
                for i in range(0,len(items)):
                    v = items[i]
                    oldpath = oldpaths[i]
                    cursor.execute('update datas set k=? where k=?', (self.GetTreeItemShortPath(v),oldpath))

                    findTabIndex = False
                    for i in range(0,self.tabWidget.count()):
                        if findTabIndex == True:
                            continue

                        if oldpath == self.tabWidget.tabToolTip(i):
                            findTabIndex = True
                            self.tabWidget.setTabToolTip(i,self.GetTreeItemShortPath(v))
                            if v == item and item.data() == MainWindow.Table:
                                self.tabWidget.setTabText(i,text)  
                    
                cursor.close()      
                self.db.commit()

            def OnDelete(index,self = self,item = item):
                if item == self.rootItem:
                    return

                deleyeKeys = set()
                cursor = self.db.cursor()

                if item.data() == MainWindow.Folder or item.data() == MainWindow.File:
                    cursor.execute('select * from datas')
                    shortpath = self.GetTreeItemShortPath(item)
                    for i in range(0,self.tabWidget.count()):
                        tabText = self.tabWidget.tabToolTip(i)
                        if len(tabText) >= len(shortpath) and tabText[0:len(shortpath)] == shortpath:
                            self.tabWidget.removeTab(i)
                            #if self.OnCloseTab(i) == False:
                            #    return

                    def DeleteChildItems(cursor,item):
                        for i in range(0,item.rowCount()):
                            childItem = item.child(i,0)

                            if item.data() != MainWindow.Table:
                                cursor.execute('delete from datas where k=?', (self.GetTreeItemShortPath(childItem),))
                                DeleteChildItems(cursor,childItem)
                        cursor.execute('delete from datas where k=?', (self.GetTreeItemShortPath(item),))

                    DeleteChildItems(cursor,item)
                    self.model.removeRow(item.row(),item.parent().index())

                elif item.data() == MainWindow.Table:
                    shortpath = self.GetTreeItemShortPath(item)
                    for i in range(0,self.tabWidget.count()):
                        if self.tabWidget.tabToolTip(i) == shortpath:
                            self.tabWidget.removeTab(i)
                            #if self.OnCloseTab(i) == False:
                            #    return
                    deleyeKeys.add(shortpath)
                    self.model.removeRow(item.row(),item.parent().index())

                for v in deleyeKeys:
                    try:
                        cursor.execute('delete from datas where k=?', (v,))
                    except Exception as e:
                        pass
                cursor.close()      
                self.db.commit()
            
            action_AddDir = QtWidgets.QAction("添加目录",None,triggered=OnAddFolder)
            action_AddConfig = QtWidgets.QAction("添加文件",None,triggered=OnAddFile)
            action_AddTable = QtWidgets.QAction("添加配置表",None,triggered=OnAddTable)
            action_Rename = QtWidgets.QAction("重命名",None,triggered=OnRename)
            action_Delete = QtWidgets.QAction("删除",None,triggered=OnDelete)

            menuTree = QtWidgets.QMenu("menuTree",self.tree)
            menuTree.addAction(action_AddDir)
            menuTree.addAction(action_AddConfig)
            menuTree.addAction(action_AddTable)
            menuTree.addSeparator()
            menuTree.addAction(action_Rename)
            menuTree.addSeparator()
            menuTree.addAction(action_Delete)

            if item == self.rootItem:
                action_Rename.setDisabled(True)

            if item.data() == MainWindow.Folder:
                action_AddTable.setDisabled(True)
                if item == self.rootItem:
                    action_Delete.setDisabled(True)
            elif item.data() == MainWindow.File:
                action_AddDir.setDisabled(True)
                action_AddConfig.setDisabled(True)
            elif item.data() == MainWindow.Table:
                action_AddTable.setDisabled(True)
                action_AddDir.setDisabled(True)
                action_AddConfig.setDisabled(True)
            else:
                return

            menuTree.exec_(QtGui.QCursor.pos())
            menuTree.destroy()

    def closeEvent(self, event):
        
        count = self.tabWidget.count()
        for i in reversed(range(0,count)):
            self.OnCloseTab(i)

        event.accept()

    def OnPaste(self):
        tableView = self.tabWidget.currentWidget()
        if tableView != None:
            if tableView.IsChanged == True:
                if QMessageBox.Yes == QMessageBox.information(self,'Save','Do you save changes?',QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel,QMessageBox.Yes):
                    tableView.Save()

            fileName,fileType = QtWidgets.QFileDialog.getOpenFileName(self,'Open File','','Excel File(*.xls *.xlsx)')
            if os.path.exists(fileName) and os.path.isfile(fileName):
                tableView.Paste(fileName)

    def OnExport(self):

        dialog = ExportDialog.ExportDialog(self)
        dialog.exec_()

    def DoSave(self,tableView):
        datas = tableView.Save()
        if datas != None:
            tabIndex = self.tabWidget.indexOf(tableView)

            cursor = None
        
            try:
                cursor = self.db.cursor()

                k = self.tabWidget.tabToolTip(tabIndex)
                cursor.execute('select * from datas where k=?', (k,))
                values = cursor.fetchall()

                if len(values) > 0 and values[0][0] == k:
                    cursor.execute('update datas set v=? where k=?', (datas,k))
                else:
                    cursor.execute('insert into datas (k, v, t) values (\'{}\', \'{}\', {})', (k,datas,MainWindow.Table))
                self.db.commit()
            except Exception as e:
                pass
            finally:
                if cursor != None:
                    cursor.close()

    def OnSave(self):
        tableView = self.tabWidget.currentWidget()
        if tableView != None and tableView.IsChanged == True:
            self.DoSave(tableView)
            tabIndex = self.tabWidget.indexOf(tableView)
            self.tabWidget.tabBar().setTabTextColor(tabIndex,QColor(0,0,0))

    def OnSaveAll(self):
        for i in range(0,self.tabWidget.count()):
            tableView = self.tabWidget.widget(i)
            if tableView.IsChanged == True:
                self.DoSave(tableView)
                self.tabWidget.tabBar().setTabTextColor(i,QColor(0,0,0))


    def OnUndo(self):
        tableView = self.tabWidget.currentWidget()
        if tableView != None:
            tableView.Undo()

    def OnRedo(self):
        tableView = self.tabWidget.currentWidget()
        if tableView != None:
            tableView.Redo()

    def EnableSave(self,enable,tableView):

        if enable == True:
            self.tabWidget.tabBar().setTabTextColor(self.tabWidget.indexOf(tableView),QColor(233,21,10))
        else:
            self.tabWidget.tabBar().setTabTextColor(self.tabWidget.indexOf(tableView),QColor(0,0,0))

    def OnTreeDoubleClicked(self,index):
        if index.isValid() == False:
            return

        item = self.model.itemFromIndex(index)
        shortpath = self.GetTreeItemShortPath(item)

        findTabIndex = -1
        if item.data() == MainWindow.Table:
            for i in range(0,self.tabWidget.count()):
                if self.tabWidget.tabToolTip(i) == shortpath:
                    findTabIndex = i
                    break
            if findTabIndex != -1:
                self.tabWidget.setCurrentIndex(findTabIndex)
            else:
                tableView = GridTableView.GridTableView(item.data(Qt.UserRole+2),self.tabWidget)

                tabIndex = self.tabWidget.addTab(tableView,item.text())
                self.tabWidget.setTabToolTip(tabIndex,shortpath)
                self.tabWidget.setCurrentWidget(tableView)
            pass
        pass

    def OnCloseTab(self,tabId):
        tableView = self.tabWidget.widget(tabId)
        if tableView.IsChanged == True:
            ret = QMessageBox.information(self,'Save','Do you save changes?',QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel,QMessageBox.Yes)
            if QMessageBox.Yes == ret:
                self.DoSave(tableView)
            elif QMessageBox.Cancel == ret:
                return False

        self.tabWidget.removeTab(tabId)
        return True

    @property
    def Settings(self):

        if self.setting == None:
            self.setting = {}
            try:
                with open("Settings.cfg",'r') as f:
                    self.setting = json.load(f)
            except IOError as e:
                pass

        return self.setting

    def GetTreeModel(self):
        return self.model

    def __del__(self):
        print('MainWindow.__del__')

        if self.db!= None:
            self.db.close()

        try:
            with open("Settings.cfg",'w') as f:
                json.dump(self.setting,f)
        except IOError as e:
            pass
        finally:
            pass
        pass


    def __init__(self): 
        super(MainWindow, self).__init__()
        
        uic.loadUi('MainWindow.ui', self)

        self.db = None
        self.rootItem = None
        self.setting = None
        self.fileSystemWatcher = QFileSystemWatcher()

        self.oldWindowTitle = self.windowTitle()
        
        self.iconProvider = QFileIconProvider()

        splitterH = QSplitter(self.centralwidget)
        self.verticalLayout.addWidget(splitterH)

        self.tree = QTreeView(splitterH)

        self.model = QStandardItemModel(self.tree)
        self.model.setHorizontalHeaderLabels(['Name'])
        self.model.setColumnCount(1)

        self.tree.setModel(self.model)

        selectionModel = QItemSelectionModel(self.model)
        self.tree.setSelectionModel(selectionModel)
        self.tree.setUniformRowHeights(True)
        self.tree.header().setStretchLastSection(False)
        self.tree.viewport().setAttribute(Qt.WA_StaticContents)
        self.tree.setAttribute(Qt.WA_MacShowFocusRect, False)

        self.tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tree.header().setStretchLastSection(False);

        self.tree.setHeaderHidden(True)

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested['QPoint'].connect(self.OnTreeCustomContextMenuRequested)
        self.tree.doubleClicked.connect(self.OnTreeDoubleClicked)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        self.tree.setSizePolicy(sizePolicy)

        splitterH.addWidget(self.tree)

        self.setStatusBar(None)

        self.tabWidget = QTabWidget(splitterH)
        self.tabWidget.setTabsClosable(True)

        self.tabWidget.resize(self.tabWidget.size().width(),self.size().height()/3*1)

        self.tabWidget.tabCloseRequested['int'].connect(self.OnCloseTab)
        

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(7)
        self.tabWidget.setSizePolicy(sizePolicy)

        splitterH.addWidget(self.tabWidget)
       
        self.action_Save.setShortcut(Qt.CTRL|Qt.Key_S)
        self.action_Save.triggered.connect(self.OnSave)

        self.actionParse_Excel.triggered.connect(self.OnPaste)
        #self.action_Export_Code.triggered.connect(self.OnExportData)

        self.actionUndo.setShortcut(Qt.CTRL|Qt.Key_Z)
        self.actionUndo.triggered.connect(self.OnUndo)

        self.actionRedo.setShortcut(Qt.CTRL|Qt.Key_Y)
        self.actionRedo.triggered.connect(self.OnRedo)

        self.SetRootTreeItem('root')

        #self.currentZip = ''
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.DelayStart)
        self.timer.start(100)

    def GetAllDatasFromDB(self):
        cursor = self.db.cursor()
        cursor.execute('select * from datas order by k asc')
        values = cursor.fetchall()
        cursor.close()
        return values

    @property
    def TreeRootItem(self):
        return self.rootItem

    def DelayStart(self):
        self.timer.stop()
        self.timer = None
   
        sf = SelectFolder.SelectFolder(self)
        if sf.exec_() == QtWidgets.QDialog.Rejected:
            self.close()

        sf.destroy()
        currentPath = sf.GetFolder()

        if os.path.exists(currentPath) == False:
            return

        self.setWindowTitle(self.oldWindowTitle + ' - ' + currentPath)

        self.db = sqlite3.connect(currentPath)
        values = self.GetAllDatasFromDB()
        for k,v,t in values:
            item = self.AddTreeItem(None,k, t,False)

            if t == MainWindow.Table:  
                model = GridTableView.TableViewItemModel(2,0)
                model.setParent(self.tree)
                if v != 'None':
                    self.LoadTableData(v,model)

                item.setData(model,Qt.UserRole+2)

        self.tree.expand(self.rootItem.index())



        