
from PyQt5 import QtCore, QtGui, QtWidgets, uic

class InputDialog(QtWidgets.QDialog):
    def __init__(self,parent,text = ''):
        super(InputDialog, self).__init__(parent)
        uic.loadUi('InputDialog.ui', self)

        self.lineEdit.setText(text)
        self.lineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("^\w+$")))

        if len(text) > 0:
            self.lineEdit.selectAll()

    def GetTextValue(self):
        return self.textValue

    def OnCancel(self):
        self.done(QtWidgets.QDialog.Rejected)
        pass
    
    def OnOK(self):
        self.textValue = str(self.lineEdit.text())

        self.done(QtWidgets.QDialog.Accepted)
        pass