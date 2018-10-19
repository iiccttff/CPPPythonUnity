# -*- coding: utf-8 -*-
import FastNet, pkt, json, time
import Signals
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import App,Signals


class AddPlatform(QtWidgets.QDialog):
    def __init__(self, parent,key,title,values=None):
        super(AddPlatform, self).__init__(parent)
        #uic.loadUi('ui/addplatform.ui', self)

        self.setWindowTitle(title)

        self.key = key


        vboxLayout = QtWidgets.QVBoxLayout(self)

        self.datas = {}

        for v in values:
            hboxLayout = QtWidgets.QHBoxLayout()
            cb = None
            revision = v.get('svnRevision', None)

            widget = v.get('widget', 'ReadOnlyText')
            if widget == 'ReadOnly':
                cb = QtWidgets.QLineEdit(self)
                cb.setText(v.get('defaultVal', ''))
                cb.setReadOnly(True)
            elif widget == 'Password':
                cb = QtWidgets.QLineEdit(self)
                cb.setEchoMode(QtWidgets.QLineEdit.Password)
                cb.setText(v.get('defaultVal', ''))

                self.datas[v['key']] = cb
            else:
                cb = QtWidgets.QComboBox(self)

                self.datas[v['key']] = cb

                enums = v.get('enums', None)
                if enums is not None:
                    for vv in enums:
                        cb.addItem(vv)
                else:
                    cb.setEditable(True)
                    ret = App.App.Instance.Settings.value("AddPlatform/{}_{}".format(self.key, v['key']), None)
                    if ret is not None:
                        for vv in json.loads(ret):
                            cb.addItem(vv)

                defaultVal = v.get('defaultVal', None)
                if defaultVal is not None: 
                    cb.setCurrentText(defaultVal)

            cb.revision = revision
            if revision is not None:
                hboxLayout = QtWidgets.QHBoxLayout()
                hboxLayout.addWidget(QtWidgets.QLabel(v['name'], self), 1)
                hboxLayout.addWidget(cb, 1)
                cb2 = QtWidgets.QComboBox(self)
                hboxLayout.addWidget(cb2, 3)
                vboxLayout.addLayout(hboxLayout)

                def OnSvnChanged(text, cmboxKey = v['key']):
                    m = FastNet.Message.Create(pkt.common.AnyReq.sClsId)
                    m.classId = 'ServerMgr'
                    m.data = json.dumps({'type': 'query',
                                            'val':'svns' ,
                                            'key': text,
                                            'cmbox': cmboxKey,
                                        })
                    Signals.gSignals.SendMsg.emit(m)

                cb.currentTextChanged.connect(OnSvnChanged)
                OnSvnChanged(cb.currentText())

                cb.cb2 = cb2
                
            else:
                hboxLayout.addWidget(QtWidgets.QLabel(v['name'], self), 1)
                hboxLayout.addWidget(cb, 4)
                vboxLayout.addLayout(hboxLayout)
        
        hboxLayout = QtWidgets.QHBoxLayout()
        btnOK = QtWidgets.QPushButton("确认", self)
        btnCancel = QtWidgets.QPushButton("取消", self)
        hboxLayout.addWidget(btnOK)
        hboxLayout.addWidget(btnCancel)
        vboxLayout.addLayout(hboxLayout)


        btnOK.clicked.connect(self.OnOk)
        btnCancel.clicked.connect(self.reject)

        Signals.gSignals.QuerySvnLogs.connect(self.OnQuerySvnLogs)

        

    def closeEvent(self, event):
        Signals.gSignals.QuerySvnLogs.disconnect(self.OnQuerySvnLogs)
        event.accept()

    def OnQuerySvnLogs(self,key,data):
        ret = self.datas.get(key,None)
        if ret is not None and hasattr(ret,'cb2') is True:
            ret.cb2.clear()

            currentText = None
            
            for v in data:
                text = '{}|{}|{}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(v[0])),v[1],v[2])
                ret.cb2.addItem(text)

                if str(v[1]) == ret.revision:
                    currentText = text
           
            if currentText is not None:
                ret.cb2.setCurrentText(currentText)

    def OnOk(self):
        self.done(QtWidgets.QDialog.Accepted)

        datas = {}
        for k,v in self.datas.items():
            if isinstance(v,QtWidgets.QLineEdit):
                datas[k] = v.text()
            else:
                if hasattr(v,'cb2') is True:
                    datas[k] = v.currentText() + '|' + v.cb2.currentText().split('|')[1]
                else:
                    datas[k] = v.currentText()

                ret = App.App.Instance.Settings.value("AddPlatform/{}_{}".format(self.key,k),None)
                if ret is not None:
                    jval = json.loads(ret)
                    if v.currentText() in jval:
                        jval.remove(v.currentText())

                    jval.insert(0,v.currentText())
                    if len(jval) > 10:
                        jval.pop()

                    App.App.Instance.Settings.setValue("AddPlatform/{}_{}".format(self.key,k),json.dumps(jval))
                else:
                    App.App.Instance.Settings.setValue("AddPlatform/{}_{}".format(self.key,k),json.dumps([v.currentText()]))

        self.datas = datas

    def GetData(self):
        ret = self.exec_()
        self.deleteLater()
        if ret == QtWidgets.QDialog.Accepted:
            return self.datas
        return None

