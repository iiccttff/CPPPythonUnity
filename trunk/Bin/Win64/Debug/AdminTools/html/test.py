#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys, json
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSlot, QUrl, Qt
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView

class CallHandler(QObject):
    @pyqtSlot(result=str)
    def GetData(self):
        data = {}
        #data['pointStart'] = 2010
        data['titleY'] = '数量'
        data['categories'] = ['2018-07-10 12:00','2018-07-10 12:00','2018-07-10 12:00','2018-07-10 12:00','2018-07-10 12:00','2018-07-10 12:00','2018-07-10 12:00','2018-07-10 12:00']
        data['title'] = '登录退出'
        data['series'] = \
        [
            {
                'name': '登录',
                'data': [43934, 52503, 57177, 69658, 97031, 119931, 137133, 154175,43934, 52503, 57177, 69658, 97031, 119931, 137133, 154175,43934, 52503, 57177, 69658, 97031, 119931, 137133, 154175]
            },
            {
                'name': '退出',
                'data': [24916, 24064, 29742, 29851, 32490, 30282, 38121, 40434,24916, 24064, 29742, 29851, 32490, 30282, 38121, 40434,24916, 24064, 29742, 29851, 32490, 30282, 38121, 40434]
            },
            {
                'name': '在线',
                'data': [234, 566, 3231, 12169, 15112, 22452, 34400, 34227,234, 566, 3231, 12169, 15112, 22452, 34400, 34227,234, 566, 3231, 12169, 15112, 22452, 34400, 34227]
            }
        ]

        return json.dumps(data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = QWebEngineView()
    channel = QWebChannel()
    handler = CallHandler()
    channel.registerObject('pyjs', handler)
    view.page().setWebChannel(channel)
    url_string = "file:///./index.htm"
    view.load(QUrl(url_string))
    view.show()
    view.setContextMenuPolicy(Qt.NoContextMenu)

    sys.exit(app.exec_())