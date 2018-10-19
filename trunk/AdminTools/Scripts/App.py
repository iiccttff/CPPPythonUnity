# -*- coding: utf-8 -*-
import FastNet
import sys,json,subprocess
from PyQt5 import QtCore, QtGui, QtWidgets
import MainWindow
import traceback
from PyQt5.QtWebEngineWidgets import QWebEngineView

class App(FastNet.App):
	def __init__(self):
		#QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)

		super(App, self).__init__(self)

		self.qtApp = QtWidgets.QApplication([])
		self.settings = QtCore.QSettings(FastNet.GetWorkPath() + '/AdminTools.data',QtCore.QSettings.IniFormat)

		FastNet.LogNormal("App.__init__")

	def __del__(self):
		FastNet.LogNormal("App.__del__")
		pass

	def Exec(self):
		try:
		    self.qtApp.exec_()
		except Exception as e:
		    FastNet.LogException("App.Exec " + str(e))

	@property
	def Cfgs(self):
		return FastNet.JsonConfigs

	@property
	def Settings(self):
		return self.settings

	def OnCreate(self):

	    self.mainWindow = MainWindow.MainWindow()
	    self.mainWindow.show()

	def OnDestory(self):
		self.mainWindow = None

	@property
	def MainWindow(self):
		return self.mainWindow

	def OnPublish(self,id,message,isPublic):
		pass

def Main(app):
    QtWidgets.QApplication.addLibraryPath("./PyQt5/Qt/plugins")
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
    

    app.Start()
    app.Exec()
    app.Stop()
    app.Update()