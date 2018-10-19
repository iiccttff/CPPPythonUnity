import FastNet, pkt
from PyQt5 import QtWidgets, uic, QtGui, QtCore
import App, Signals, json, time, random
from tabs.TableViewModel import TableViewModel

class ServerLog(QtWidgets.QTableView):
    def __init__(self,parent):
        super(ServerLog, self).__init__(parent)

        self.model = QtGui.QStandardItemModel()

        self.setModel(self.model)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        columnLabels = ['时间', '日志级别', '日志内容','logType']

        self.model.setHorizontalHeaderLabels(columnLabels)
        self.model.setColumnCount(len(columnLabels))

        self.setColumnWidth(0,200)
        self.setColumnWidth(1,100)

        self.hideColumn(3)

    def IsAllowExport(self):
        return True

    def IsChartMode(self):
        return False

    def Query(self,beginTime,endTime):
        parent = self.parent()
        self.queryType = parent.comboBoxLogType.itemData(parent.comboBoxLogType.currentIndex())
        self.model.setRowCount(0)


    def OnLogTypeChanged(self,data):
        self.queryType = data
        #self.model.setRowCount(0)
        self.RefreshData()

    def RefreshData(self):
        for row in reversed(range(0,self.model.rowCount())):
            if self.queryType == 'AllLog' or self.model.item(row,3).text() == self.queryType:
                self.showRow(row)
            else:
                self.hideRow(row)

    def OnQueryData(self,data):

        for v in data.logs:
            if self.queryType != 'AllLog' and self.queryType != v.key:
                continue

            self.model.appendRow(QtGui.QStandardItem())

            row = self.model.rowCount() - 1
            
            logType = ''
            if v.key == 'Normal':
                self.model.setData(self.model.index(row, 1), '正常')
                self.model.item(row,1).setForeground(QtGui.QColor(0,0,0))
            elif v.key == 'Debug':
                self.model.setData(self.model.index(row, 1), '调试')
                self.model.item(row,1).setForeground(QtGui.QColor(44,63,205))
            elif v.key == 'Warning':
                self.model.setData(self.model.index(row, 1), '警告')
                self.model.item(row,1).setForeground(QtGui.QColor(192,185,0))
            elif v.key == 'Error':
                self.model.setData(self.model.index(row, 1), '错误')
                self.model.item(row,1).setForeground(QtGui.QColor(242,63,64))
            elif v.key == 'Exception':
                self.model.setData(self.model.index(row, 1), '异常')
                self.model.item(row,1).setForeground(QtGui.QColor(163,34,32))


            self.model.setData(self.model.index(row, 0), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(v.time)))
            self.model.setData(self.model.index(row, 2), v.log)
            self.model.setData(self.model.index(row, 3), v.key)

            self.model.item(row,2).setTextAlignment(QtCore.Qt.AlignLeft)
            self.model.item(row,1).setTextAlignment(QtCore.Qt.AlignCenter)
            self.model.item(row,0).setTextAlignment(QtCore.Qt.AlignCenter)

        self.RefreshData()

        