# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets


class TableViewModel(QtGui.QStandardItemModel):
    def __init__(self, *args):
        super(TableViewModel, self).__init__(*args)

    def data(self,index, role = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter
        else:
            return super(TableViewModel, self).data(index, role)

    def headerData(self,section,orientation, role = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter
        else:
            return super(TableViewModel, self).headerData(section,orientation, role)

    #def sort(self, column, order):
    #    for i in range(0, self.model.rowCount()):
    #
    #    pass