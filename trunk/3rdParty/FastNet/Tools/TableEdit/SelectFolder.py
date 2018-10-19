# -*- coding: utf-8 -*-

import os,json,zipfile
from PyQt5 import QtCore, QtGui, QtWidgets, uic


class SelectFolder(QtWidgets.QDialog):
    def __init__(self,parent):
        super(SelectFolder, self).__init__(parent)
        uic.loadUi('SelectFolder.ui', self)

        self.folder = ''

        historyPaths = parent.Settings.get('HistoryPaths',None)
        if historyPaths != None:
            ll = list(historyPaths)
            for v in ll:
                if os.path.exists(v) == False or os.path.isfile(v) == False:
                    historyPaths.remove(v)
                else:
                    self.listWidget.addItem(v) 

    def GetFolder(self):
        return self.folder

    def OnCreateNew(self):
        oldFolder = ''
        if self.listWidget.count() > 0:
            item = self.listWidget.itemAt(self.listWidget.count()-1,0)
            oldFolder =  os.path.split(item.text())[0]

        folder = QtWidgets.QFileDialog.getSaveFileName(self,'',oldFolder,'SQlite DB File (*.db)')
        if folder != None and len(folder) > 0 and len(folder[0]) > 0:

            import sqlite3
            db = sqlite3.connect(folder[0])
            db.cursor().execute('create table datas(k text primary key,v TEXT,t smallint)')
            db.close()

            self.folder = folder[0]
            self.listWidget.addItems([self.folder])
            self.done(QtWidgets.QDialog.Accepted)


            if 'HistoryPaths' in self.parent().Settings:
                historyPaths = self.parent().Settings['HistoryPaths']
                if self.folder in historyPaths:
                    historyPaths.remove(self.folder)

                historyPaths.append(self.folder)
            else:
                self.parent().Settings['HistoryPaths'] = [self.folder]

    def OnBrowseOther(self):

        oldFolder = ''
        if self.listWidget.count() > 0:
            item = self.listWidget.itemAt(self.listWidget.count()-1,0)
            oldFolder =  os.path.split(item.text())[0]

        folder = QtWidgets.QFileDialog.getOpenFileName(self,'',oldFolder,'SQlite DB File (*.db)')
        if folder != None and len(folder) > 0 and len(folder[0]) > 0 and os.path.exists(folder[0]) == True and os.path.isfile(folder[0]) == True:
            self.folder = folder[0]
            self.listWidget.addItems([self.folder])
            self.done(QtWidgets.QDialog.Accepted)


            if 'HistoryPaths' in self.parent().Settings:
                historyPaths = self.parent().Settings['HistoryPaths']
                if self.folder in historyPaths:
                    historyPaths.remove(self.folder)

                historyPaths.append(self.folder)
            else:
                self.parent().Settings['HistoryPaths'] = [self.folder]



    def OnListViewClicked(self,item):
        folder = item.text()
        if folder != None and len(folder) > 0 and os.path.exists(folder) == True and os.path.isfile(folder) == True:
            self.done(QtWidgets.QDialog.Accepted)
            self.folder = folder
        pass