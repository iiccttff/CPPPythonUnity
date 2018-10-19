from PyQt5.QtCore import (QAbstractItemModel, QFileInfo, QItemSelectionModel,
        QModelIndex, Qt)
from PyQt5.QtWidgets import QApplication, QMainWindow,QHBoxLayout,QSplitter,QTabWidget,QTextEdit,QHeaderView,QSpinBox,QTableWidget,QUndoStack
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QAbstractItemView,QStyleFactory,QTabBar,
        QFileIconProvider, QListView, QTableView, QTreeView,QUndoCommand,QItemDelegate,QStyledItemDelegate,QInputDialog)
from PyQt5.QtGui import QStandardItemModel,QStandardItem

import InputDialog
import json,os
import GlobalObjs

class TableViewAddRowCommand(QUndoCommand):
    def __init__(self,rowCount,model):
        super(TableViewAddRowCommand, self).__init__()
        self.rowCount = rowCount
        self.model = model
        pass

    def undo(self):
        self.model.setRowCount(self.model.rowCount() - self.rowCount)
        pass

    def redo(self):
        self.model.setRowCount(self.model.rowCount() + self.rowCount)
        pass

class TableViewDelRowCommand(QUndoCommand):
    def __init__(self,rows,model):
        super(TableViewDelRowCommand, self).__init__()
        self.rows = rows
        self.model = model
        self.backupDatas = []

        columnCount = model.columnCount()
        for i in self.rows:
            datas = []
            for j in range(0,columnCount):
                datas.append(model.data(model.index(i,j)))

            self.backupDatas.append(datas)

    def undo(self):
        columnCount = self.model.columnCount()
        for i in range(0,len(self.rows)):
            row = self.rows[i]
            self.model.insertRow(row)
            backupData = self.backupDatas[i]

            for j in range(0,columnCount): 
                data = backupData[j]
                if data != None:
                    self.model.setData(self.model.index(row,j),data)

    def redo(self):
        for i in reversed(self.rows):
            self.model.removeRow(i)

class TableViewAddColumnCommand(QUndoCommand):
    def __init__(self,model,text):
        super(TableViewAddColumnCommand, self).__init__()
        self.text = text
        self.model = model 
        pass

    def undo(self):
        self.model.setColumnCount(self.model.columnCount() - 1)
        pass

    def redo(self):
        self.model.setColumnCount(self.model.columnCount() + 1)
        self.model.setHeaderData(self.model.columnCount() - 1,Qt.Horizontal,self.text)
        self.model.setData(self.model.index(0,self.model.columnCount() - 1),'UInt8')
        self.model.setData(self.model.index(1,self.model.columnCount() - 1),'')
        pass

class TableViewDelColumnCommand(QUndoCommand):
    def __init__(self,model,cols):
        super(TableViewDelColumnCommand, self).__init__()
        self.cols = cols
        self.model = model 
        self.backTables = []
        self.backDatas = []

        for i in range(0,self.model.columnCount()): 
            d = []
            for j in range(2,self.model.rowCount()):
                d.append(self.model.data(self.model.index(j,i)))
            self.backDatas.append(d)

            self.backTables.append((self.model.headerData(i,Qt.Horizontal),
                                   self.model.data(self.model.index(0,i)),
                                   self.model.data(self.model.index(1,i))))

    def undo(self):
        for i in self.cols:
            self.model.insertColumn(i)

            v = self.backTables[i]
            self.model.setHeaderData(i,Qt.Horizontal,v[0])
            self.model.setData(self.model.index(0,i),v[1])
            self.model.setData(self.model.index(1,i),v[2])

        for i in range(0,len(self.backDatas)): 
            d = self.backDatas[i]
            for j in range(0,len(d)): 
                self.model.setData(self.model.index(j+2,i),d[j])

    def redo(self):
        for i in reversed(self.cols):
            self.model.removeColumn(i)

class TableViewEditItemCommand(QUndoCommand):
    def __init__(self,row,col,oldText,newText,model,label = False):
        super(TableViewEditItemCommand, self).__init__()

        self.row = row
        self.col = col
        self.oldText = oldText
        self.newText = newText
        self.model = model
        self.label = label
        pass

    def undo(self):
        
        if self.label == False:
            index = self.model.index(self.row,self.col)
            self.model.setData(index,self.oldText, Qt.EditRole)
        else:
            self.model.setHeaderData(self.col,Qt.Horizontal,self.oldText)
        pass

    def redo(self):
        if self.label == False:
            index = self.model.index(self.row,self.col)
            self.model.setData(index,self.newText, Qt.EditRole)
        else:
            self.model.setHeaderData(self.col,Qt.Horizontal,self.newText)
        pass
    
class TableViewSetActiveColumnCommand(QUndoCommand):
    def __init__(self,model,column):
        super(TableViewSetActiveColumnCommand, self).__init__()
        self.model = model 
        self.column = column
        self.oldColumn = self.model.activeColumn
        

    def undo(self):

        self.model.beginResetModel()
        self.model.activeColumn = self.oldColumn
        self.model.endResetModel()

    def redo(self):

        self.model.beginResetModel()
        self.model.activeColumn = self.column
        self.model.endResetModel()
        pass

class TableViewPasteExcelCommand(QUndoCommand):
    def __init__(self,model,datas):
        super(TableViewPasteExcelCommand, self).__init__()
        self.model = model 
        self.datas = datas
        self.backDatas = []
        self.backTables = []

        for i in range(0,self.model.columnCount()):
            index0 = self.model.data(self.model.index(0,i))
            index1 = self.model.data(self.model.index(1,i))
            o = (i,self.model.headerData(i,Qt.Horizontal),index0,index1)
            self.backTables.append(o)

        for i in range(2,self.model.rowCount()):
            d = []
            for j in range(0,self.model.columnCount()): 
                v = self.model.data(self.model.index(i,j))
                if v == None:
                    d.append('')
                else:
                    d.append(v)
            self.backDatas.append(d)


    def undo(self):
        
        self.model.setRowCount(len(self.backDatas) + 2)
        self.model.setColumnCount(len(self.backTables))

        for v in self.backTables:
            self.model.setHeaderData(v[0],Qt.Horizontal,v[1])
            self.model.setData(self.model.index(0,v[0]),v[2])
            self.model.setData(self.model.index(1,v[0]),v[3])

        for i in range(0,len(self.backDatas)):
            v = self.backDatas[i]
            for j in range(0,len(v)):
                self.model.setData(self.model.index(i+2,j),v[j])

    def redo(self):
                
        self.model.setRowCount(len(self.datas))
        self.model.setColumnCount(len(self.datas[0]))

        for i in range(0,self.model.columnCount()):
            self.model.setHeaderData(i,Qt.Horizontal,'{}'.format(i+1))
            self.model.setData(self.model.index(0,i),'UInt8')
            self.model.setData(self.model.index(1,i),'')

        for i in range(0,len(self.datas)):
            v = self.datas[i]
            for j in range(0,len(v)):
                self.model.setData(self.model.index(i+2,j),v[j])

class TableViewItemModel(QStandardItemModel):
    def __init__(self, *args):
        super(TableViewItemModel, self).__init__(*args)
        self.activeColumn = -1

    def data(self,index, role = Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        elif index.isValid() and role == Qt.BackgroundColorRole:
            if index.column() == self.activeColumn:
                return QtGui.QColor(231,233,235)
            else:
                return super(TableViewItemModel, self).data(index, role)
        else:
            return super(TableViewItemModel, self).data(index, role)

    def headerData(self,section,orientation, role = Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        elif role == Qt.DisplayRole and orientation == Qt.Vertical:
            if section == 0:
                return 'Type'
            elif section == 1:
                return 'Describe'
            else:
                return str(section - 2 + 1)
        else:
            return super(TableViewItemModel, self).headerData(section,orientation, role)


class TableViewSelectTypes(QtWidgets.QDialog):
    def setText(self, text):
        self._text = text

        if text in GridTableView.BasicTypes:
            self.tree.expand(self.bacisItem.index())
            for i in range(self.bacisItem.rowCount()):
                childItem = self.bacisItem.child(i,0)
                if childItem.text() == text:
                    self.tree.setCurrentIndex(childItem.index())
                 
        else:
            self.tree.expand(self.otherItem.index())
            names = text.split('.')
            parentItem = self.otherItem
            for v in names:
                isBreak = False
                for i in range(parentItem.rowCount()):
                    if isBreak == True:
                        continue

                    if parentItem.child(i,0).text() == v:
                        parentItem = parentItem.child(i,0)
                        self.tree.expand(parentItem.index())
                        isBreak = True
                        continue
            
            self.tree.setCurrentIndex(parentItem.index())

    def text(self):
        return self._text

    def __init__(self, *args):
        super(TableViewSelectTypes, self).__init__(args[1])

        self.tableView = args[1]
        self._text = ''
        
        
        gMainWindow = GlobalObjs.GetValue('MainWindow')
        
        self.setModal(True)
        #self.setModel(True)
        self.setWindowTitle('Select Type')
        
        self.vboxLayout = QtWidgets.QVBoxLayout(self)
        self.tree = QTreeView(self)
        self.model = QStandardItemModel(self)
        self.tree.setHeaderHidden(True)

        self.tree.setModel(self.model)

        self.bacisItem = QStandardItem()
        self.bacisItem.setText('BasicTypes')
        self.bacisItem.setFlags(QtCore.Qt.ItemIsEnabled)
        self.model.appendRow(self.bacisItem)
        self.tree.expand(self.bacisItem.index())

        for v in GridTableView.BasicTypes:
            item = QStandardItem()
            item.setFlags(QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable)
            item.setText(v)
            item.setData(True)
            self.bacisItem.appendRow(item)

        if self.tableView.Model.activeColumn != args[2]:
            self.otherItem = QStandardItem()
            self.otherItem.setText('Other')
            self.otherItem.setFlags(QtCore.Qt.ItemIsEnabled)
            self.model.appendRow(self.otherItem)
            self.tree.expand(self.otherItem.index())
            def LoadOtherTypes(item,parent):
                for i in range(0,item.rowCount()):
                    childItem = item.child(i,0)
                    if childItem.data(Qt.UserRole+2) == self.tableView.Model:
                        continue

                    itemAdd = QStandardItem()
                    itemAdd.setText(childItem.text())

                    if childItem.data() == 3:
                        itemAdd.setFlags(QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable)
                    else:
                        itemAdd.setFlags(QtCore.Qt.ItemIsEnabled)
                        LoadOtherTypes(childItem,itemAdd)

                    parent.appendRow(itemAdd)

            LoadOtherTypes(gMainWindow.TreeRootItem,self.otherItem)

        self.vboxLayout.addWidget(self.tree)

        self.tree.doubleClicked.connect(self.OnDoubleClicked)
        self.tree.setFocus()

        self.show()

    def OnDoubleClicked(self,index):
        item = self.model.itemFromIndex(index)
        if item.flags() == QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable:
            if item.data() == True:
                self.setText(index.data())
            else:
                names = []
                parent = index
                while True:
                    names.append(parent.data())
                    parent = parent.parent()
                    if parent.isValid() == False or self.otherItem.index() == parent:
                        break

                self.setText('.'.join(reversed(names)))

            self.done(QtWidgets.QDialog.Accepted)


class TableViewDelegate(QStyledItemDelegate):

    def __init__(self,tableView, *args):
        super(TableViewDelegate, self).__init__(*args)
        self.tableView = tableView

    def createEditor(self, parent, option, index):
        if index.row() == 0:
            editor = TableViewSelectTypes(parent,self.tableView,index.column())
            return editor
        elif index.row() == 1:
            editor = QtWidgets.QPlainTextEdit(parent)
            editor.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
            return editor
        else:
            return QStyledItemDelegate.createEditor(self,parent, option, index)
            typename = index.model().data(index.model().index(0,index.column()))
            editor = None
            if typename in GridTableView.BasicTypes:
                #editor = QStyledItemDelegate.createEditor(self,parent, option, index)
                editor = QtWidgets.QLineEdit(parent)
                '''import numpy as np

                if typename == 'UInt8':
                    editor.setValidator(QtGui.QIntValidator(np.iinfo(np.uint8).min,np.iinfo(np.uint8).max))
                elif typename == 'UInt16':
                    editor.setValidator(QtGui.QIntValidator(np.iinfo(np.uint16).min,np.iinfo(np.uint16).max))
                elif typename == 'UInt32':
                    editor.setValidator(QtGui.QIntValidator(np.iinfo(np.uint32).min,np.iinfo(np.uint32).max))
                elif typename == 'UInt64':
                    editor.setValidator(QtGui.QIntValidator(np.iinfo(np.uint64).min,np.iinfo(np.uint64).max))
                elif typename == 'Int8':
                    editor.setValidator(QtGui.QIntValidator(np.iinfo(np.int8).min,np.iinfo(np.int8).max))
                elif typename == 'Int16':
                    editor.setValidator(QtGui.QIntValidator(np.iinfo(np.int16).min,np.iinfo(np.int16).max))
                elif typename == 'Int32':
                    editor.setValidator(QtGui.QIntValidator(np.iinfo(np.int32).min,np.iinfo(np.int32).max))
                elif typename == 'Int64':
                    editor.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("^-?(255|[1,2]?[0-4]?\d|[1,2]?5[0-4]?)$")))
                    #editor.setValidator(QtGui.QIntValidator(np.iinfo(np.int64).min,np.iinfo(np.int64).max))
                elif typename == 'String':
                    editor.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("^\w+$")))
                elif typename == 'Float' or typename == 'Double':
                    minVal = np.finfo(np.float).min
                    maxVal = np.finfo(np.float).max
                    editor.setValidator(QtGui.QDoubleValidator(minVal,maxVal,5))
                elif typename == 'Bool':
                    editor.setValidator(QtGui.QIntValidator(0,1))
                else:
                    assert(False)'''
            else:
                import GlobalObjs
                gMainWindow = GlobalObjs.GetValue('MainWindow')

                editor = QtWidgets.QComboBox(parent)
                editor.setFrame(False)
                editor.setEditable(True)

                model = gMainWindow.GetTreeModel()

                row = -1
                typename = typename.split('.')[-1]
                '''for i in range(0,model.columnCount()):
                    if model.headerData(i,Qt.Horizontal) == typename:
                        for j in model.rowCount():'''


            return editor

    def setEditorData(self, editor, index):
        if index.row() == 0:
            value = index.model().data(index, Qt.EditRole)
            editor.setText(str(value))
            import GlobalObjs
            gMainWindow = GlobalObjs.GetValue('MainWindow')

            rect = gMainWindow.geometry()
            editor.setGeometry(rect.x() + (rect.width()/2 - 200), rect.y() + (rect.height()/2 - 260),400,520)
            
        else:
            QStyledItemDelegate.setEditorData(self,editor, index)

    def setModelData(self, editor, model, index):
        oldText = model.data(index)

        value = ''
        if index.row() == 0:
            value = editor.text()
        elif index.row() == 1:
            value = editor.toPlainText()
        else:
            value = editor.text()

        if oldText != value:
            self.tableView.PushUndoStack(TableViewEditItemCommand(index.row(),index.column(),oldText,value,model))

    def updateEditorGeometry(self,editor,option,index):
        editor.setGeometry(option.rect);  

class GridTableView(QTableView):
    BasicTypes = ['UInt8','UInt16','UInt32','UInt64','Int8','Int16','Int32','Int64','Bool','Float','Double','String']


    def __init__(self,model, *args):
        super(GridTableView, self).__init__(*args)


        #self.path = path

        self.model = model
        self.setModel(model)
        
       
        self.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.verticalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.horizontalHeader().customContextMenuRequested['QPoint'].connect(self.OnCustomContextMenuRequestedH)
        self.verticalHeader().customContextMenuRequested['QPoint'].connect(self.OnCustomContextMenuRequestedV)
        self.setItemDelegate(TableViewDelegate(self))
        self.verticalHeader().setSectionsMovable(True)

        self.setRowHeight(1,150)

        self.undoStack = QUndoStack()
        self.undoStackIndex = 0

        self.undoStack.indexChanged.connect(self.OnUndoStackIndexChanged)

        self.setCornerButtonEnabled(False)

    @property
    def Model(self):
        return self.model

    def Paste(self,fileName):
        import xlrd
        workbook = xlrd.open_workbook(fileName)
        if len(workbook.sheet_names()) > 0:

            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Select Sheet")
            vBoxLayout = QtWidgets.QVBoxLayout(dialog)

            comboBox = QtWidgets.QComboBox(dialog)
            comboBox.addItems(workbook.sheet_names())

            hBoxLayout = QtWidgets.QHBoxLayout()

            nextBtn = QtWidgets.QPushButton(dialog)
            nextBtn.setText('Paste')
            nextBtn.setDefault(True)
 
            def OnNextBtnClicked(args,dialog = dialog):
                dialog.done(QtWidgets.QDialog.Accepted)
                dialog = None

            nextBtn.clicked.connect(OnNextBtnClicked)

            hBoxLayout.addStretch(2)
            hBoxLayout.addWidget(nextBtn,1)

            vBoxLayout.addWidget(comboBox)
            vBoxLayout.addLayout(hBoxLayout)

            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                sheet = workbook.sheet_by_name(comboBox.currentText())

                datas = []
                for row in range(sheet.nrows):  
                    colData = []
                    for col in range(sheet.ncols): 
                        cell = sheet.cell(row, col) 
                        if cell.ctype == 3:
                            colData.append(xlrd.xldate.xldate_as_datetime(cell.value,1).strftime("%Y-%m-%d %H:%M:%S"))
                        elif cell.ctype == 2:
                            if cell.value % 1 == 0.0:
                                colData.append(str(int(cell.value)))
                            else:
                                colData.append(str(cell.value))
                        else:
                            colData.append(str(cell.value))

                    datas.append(colData)

                if len(datas) <= 0 or len(datas[0]) <= 0:
                    QtWidgets.QMessageBox.critical(self,'Error','Format error!')
                else:
                    self.PushUndoStack(TableViewPasteExcelCommand(self.model,datas))
            dialog.destroy()

    def Undo(self):
        self.undoStack.undo()
    
    def Redo(self):
        self.undoStack.redo()
        
    def PushUndoStack(self,v):
        self.undoStack.push(v)

    def CreateDirs(self,path):
        
        try:
            paths = os.path.split(path)
            os.makedirs(paths[0])
        except Exception as e:
            pass

    def Save(self):
        if self.undoStackIndex != self.undoStack.index():
            self.undoStackIndex = self.undoStack.index()

            try:
                data = []
                table = []
                for i in range(0,self.model.columnCount()):
                    index0 = self.model.data(self.model.index(0,i))
                    index1 = self.model.data(self.model.index(1,i))
                    o = (i,self.model.headerData(i,Qt.Horizontal),index0,index1)
                    table.append(o)

                for i in range(2,self.model.rowCount()):
                    d = []
                    for j in range(0,self.model.columnCount()): 
                        v = self.model.data(self.model.index(i,j))
                        if v == None:
                            d.append('')
                        else:
                            d.append(v)

                    data.append(d)

                return json.dumps({'data':data,'table':table,'activeColumn':self.model.activeColumn},indent=1,ensure_ascii=False)

            except Exception as e:
                pass
        
        return None

    def OnUndoStackIndexChanged(self,index):
        gMainWindow = GlobalObjs.GetValue('MainWindow')
        if self.undoStackIndex == index:
            gMainWindow.EnableSave(False,self)
        else:
            gMainWindow.EnableSave(True,self)
        pass

    @property
    def IsChanged(self):
        index = self.undoStack.index()
        return self.undoStackIndex != index

    def OnCustomContextMenuRequestedH(self,pt):
        self.OnCustomContextMenuRequested(pt,self.horizontalHeader())

    def OnCustomContextMenuRequestedV(self,pt):
        self.OnCustomContextMenuRequested(pt,self.verticalHeader())

    def OnAddCol(self):
        inputDialog = InputDialog.InputDialog(self)
        if inputDialog.exec_() == QtWidgets.QDialog.Accepted:
            for i in range(0,self.model.columnCount()):
                if inputDialog.GetTextValue() == self.model.headerData(i,Qt.Horizontal):
                    QtWidgets.QMessageBox.critical(self,'Error','Duplicate name!')
                    return

            self.PushUndoStack(TableViewAddColumnCommand(self.model,inputDialog.GetTextValue()))

    def OnAddRow(self):
        self.PushUndoStack(TableViewAddRowCommand(1,self.model))
        pass

    def OnAddRowN(self):
        ret = QInputDialog.getInt(self,'Message','Please enter row number:',1,1,1000)
        if ret[1] == True:
            self.PushUndoStack(TableViewAddRowCommand(int(ret[0]),self.model))
        pass

    def OnDelCol(self):
        indexs = self.selectionModel().selectedColumns()
        if indexs != None and len(indexs) > 0:
            cols = []
            for v in indexs:
                cols.append(v.column())
            self.PushUndoStack(TableViewDelColumnCommand(self.model,cols))

    def OnEditCol(self):
        index = self.horizontalHeader().logicalIndexAt(self.sender().data())
        if index != None and index >= 0:
            v = self.model.headerData(index,Qt.Horizontal)
            inputDialog = InputDialog.InputDialog(self,str(v))
            if inputDialog.exec_() == QtWidgets.QDialog.Accepted:
                for i in range(0,self.model.columnCount()):
                    if inputDialog.GetTextValue() == self.model.headerData(i,Qt.Horizontal) and i != index:
                        QtWidgets.QMessageBox.critical(self,'Error','Duplicate name!')
                        return

                self.PushUndoStack(TableViewEditItemCommand(None,index,v,inputDialog.GetTextValue(),self.model,True))

    def OnSetColIndex(self):
        column = self.horizontalHeader().logicalIndexAt(self.sender().data())
        if column != None and column >= 0:
            if self.model.activeColumn != column:
                typename = self.model.data(self.model.index(0,column))
                if typename not in GridTableView.BasicTypes:
                    QtWidgets.QMessageBox.critical(self,'Error','column index must be the basic type!')
                else:
                    self.PushUndoStack(TableViewSetActiveColumnCommand(self.model,column))

    def OnDelRow(self):
        indexs = self.selectionModel().selectedRows()
        if indexs != None and len(indexs) > 0:

            rows = []
            for v in indexs:
                if v.row() != 0 and v.row() != 1:
                    rows.append(v.row())

            self.PushUndoStack(TableViewDelRowCommand(rows,self.model))

    def OnCustomContextMenuRequested(self,pt,header):

        action_AddCol = QtWidgets.QAction("添加列",None,triggered=self.OnAddCol)
        
        action_DelCol = QtWidgets.QAction("删除列",None,triggered=self.OnDelCol)
        action_EditCol = QtWidgets.QAction("编辑列",None,triggered=self.OnEditCol)
        action_SetColIndex = QtWidgets.QAction("设置为索引列",None,triggered=self.OnSetColIndex)

        action_AddRow = QtWidgets.QAction("添加行",None,triggered=self.OnAddRow)
        action_AddRowN = QtWidgets.QAction("添加多行",None,triggered=self.OnAddRowN)
        action_DelRow = QtWidgets.QAction("删除行",None,triggered=self.OnDelRow)
        

        action_DelCol.setData(pt)
        action_EditCol.setData(pt)
        action_SetColIndex.setData(pt)

        action_DelRow.setData(pt)

        menu = QtWidgets.QMenu("menuTable")
        menu.addAction(action_AddCol)
        menu.addAction(action_EditCol)
        menu.addAction(action_SetColIndex)
        menu.addAction(action_DelCol)
        menu.addSeparator()
        menu.addAction(action_AddRow)
        menu.addAction(action_AddRowN)
        menu.addAction(action_DelRow)

        if header.orientation() == Qt.Vertical:
            index = header.logicalIndexAt(pt)
            if index == -1 or index == 0 or index == 1:
                action_DelRow.setEnabled(False) 

            action_DelCol.setEnabled(False)
            action_EditCol.setEnabled(False) 
            action_SetColIndex.setEnabled(False)
        elif header.orientation() == Qt.Horizontal:
            index = header.logicalIndexAt(pt)
            if index == -1:
                action_DelCol.setEnabled(False) 
                action_EditCol.setEnabled(False) 
                action_SetColIndex.setEnabled(False)

            action_DelRow.setEnabled(False) 

    
        menu.exec_(QtGui.QCursor.pos())
        menu.destroy()

        pass


