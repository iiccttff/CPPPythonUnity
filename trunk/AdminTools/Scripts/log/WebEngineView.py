import FastNet, pkt, cfg

from PyQt5 import QtWidgets, uic, QtGui, QtCore
import App, Signals, json, time, random

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel


class CallHandler(QtCore.QObject):
    def __init__(self, cb,parent):
        super(CallHandler, self).__init__()
        self.cb = cb
        self.parent = parent

    @QtCore.pyqtSlot(result=str)
    def GetData(self):
        return self.cb()

    @QtCore.pyqtSlot(result=str)
    def GetDivSize(self):

        h = self.parent.height()
        if h > 50:
            h -= 20
        return str(h)

class WebEngineView(QWebEngineView):


    def __init__(self, parent):
        super(WebEngineView, self).__init__(parent = parent)

        self.channel = QWebChannel(parent)
        self.handler = CallHandler(self.OnData,self)
        self.channel.registerObject('pyjs', self.handler)
        self.page().setWebChannel(self.channel)
        self.setUrl(QtCore.QUrl('file:///./html/highcharts.htm'))

        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.theme = None
        self.tickInterval = 1
        self.xAxisMax = 60

    def __del__(self):
        print('WebEngineView.__del__')

    def OnData(self):
        data = {}
        data['height'] = self.handler.GetDivSize()
        data['theme'] = self.GetTheme()
        
        data['categories'] = self.Categories()
        data['series'] = self.Datas()
        data['tickInterval'] = self.tickInterval
        data['xAxisMax'] = self.xAxisMax

        return json.dumps(data)

    def Categories(self):
        return []

    def Datas(self):
        return []

    def Query(self):
        pass

    def Export(self,param = None):
        pass

    def IsAllowExport(self):
        return False

    def IsChartMode(self):
        return False

    def OnQueryData(self,data):
        pass

    def SetTheme(self, theme, forceFlush = False):
        if self.theme != theme or forceFlush == True:
            htmlVal = ''
            with open('html/highcharts.src.htm', 'r') as ifs:
                htmlVal = ifs.read()

                if theme == 'none':
                    htmlVal = htmlVal.replace('<script type="text/javascript" src="highcharts/themes/avocado.js"></script>','')
                else:
                    htmlVal = htmlVal.replace('<script type="text/javascript" src="highcharts/themes/avocado.js"></script>',
                                '<script type="text/javascript" src="highcharts/themes/{}.js"></script>'.format(theme))
            with open(FastNet.GetWorkPath() + '/html/highcharts.htm', 'w') as ofs:
                ofs.write(htmlVal)

            self.reload()

        self.theme = theme

    def GetTheme(self):
        return self.theme
