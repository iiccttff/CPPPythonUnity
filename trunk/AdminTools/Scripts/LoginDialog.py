# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets,uic

import FastNet,App,json
class LoginDialog(QtWidgets.QDialog):
    def __init__(self,parent): 
        super(LoginDialog, self).__init__(parent)
        uic.loadUi('ui/logindialog.ui',self)

        self.btnLogin.clicked.connect(self.OnAccept)

        value = App.App.Instance.Settings.value("LoginData/accounts")
        if value != None:
            self.cfgs = value.split(';')

            for v in self.cfgs:
                self.comboBoxUsername.addItem(v)

            if len(self.cfgs) > 0:
                self.comboBoxUsername.setCurrentText(self.cfgs[0])
        else:
            self.cfgs = []

    def GetResult(self):
        return self.username,self.password

    def OnAccept(self):

        if self.comboBoxUsername.currentText() != "" and self.editPassword.text() != "":
            if self.comboBoxUsername.currentText() in self.cfgs:
                self.cfgs.remove(self.comboBoxUsername.currentText())

            self.cfgs.insert(0,self.comboBoxUsername.currentText())

            App.App.Instance.Settings.setValue('LoginData/accounts',';'.join(self.cfgs))

            self.username = self.comboBoxUsername.currentText()
            self.password = self.editPassword.text()
            self.done(QtWidgets.QDialog.Accepted)