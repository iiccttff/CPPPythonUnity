import FastNet, pkt, cfg
from PyQt5 import QtWidgets, uic, QtGui, QtCore
import App, Signals, json, time, random

import log.WebEngineView

class SystemResource(log.WebEngineView.WebEngineView):

    def Query(self,beginTime,endTime):

        self.beginTime = beginTime
        self.endTime = endTime

        self.categories = []

        self.tickInterval = 1

        self.datas = \
        [
            {
                'name': '物理内存',
                'data': []
            },
            {
                'name': '虚拟内存',
                'data': []
            },
            {
                'name': '内存百分比',
                'data': []
            },
            {
                'name': 'CPU百分比',
                'data': []
            },
            {
                'name': '网络入口',
                'data': []
            },
            {
                'name': '网络出口',
                'data': []
            }
        ]

    def IsAllowExport(self):
        return False

    def IsChartMode(self):
        return True

    def OnQueryData(self,data):

        parent = self.parent()

        rss = []
        vms = []
        memory_percent = []
        cpu_percent = []
        inputNet = []
        outputNet = []

        categories = []

        self.tickInterval = 1
        if parent.timeType == 'hour':
            self.tickInterval = 1
            self.xAxisMax = 60
        elif parent.timeType == 'day':
            self.tickInterval = 30
            self.xAxisMax = 12 * 2
        elif parent.timeType == 'week':
            self.tickInterval = 120
            self.xAxisMax = 8 * 7
        
        #categories = range(self.beginTime,self.endTime,self.tickInterval*60)
        #for v in categories:
        #    self.categories.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(v)))

        for v in data.logs:
            t = v.time*1000
            
            vals = v.log.split('|')
            rss.append([t,int(vals[0])])
            vms.append([t,int(vals[1])])
            memory_percent.append([t,float(vals[2])])
            cpu_percent.append([t,float(vals[3])])
            inputNet.append([t,int(vals[4])])
            outputNet.append([t,int(vals[5])])

        self.datas[0]['data'] += rss
        self.datas[1]['data'] += vms
        self.datas[2]['data'] += memory_percent
        self.datas[3]['data'] += cpu_percent
        self.datas[4]['data'] += inputNet
        self.datas[5]['data'] += outputNet

        if data.isEnd is True:
            self.reload()

    def Categories(self):
        return self.categories

    def Datas(self):
        return self.datas

    def __init__(self,parent):
        super(SystemResource, self).__init__(parent)

        
        self.categories = []

        self.datas = \
        [
            {
                'name': '物理内存',
                'data': []
            },
            {
                'name': '虚拟内存',
                'data': []
            },
            {
                'name': '内存百分比',
                'data': []
            },
            {
                'name': 'CPU百分比',
                'data': []
            },
            {
                'name': '网络入口',
                'data': []
            },
            {
                'name': '网络出口',
                'data': []
            }
        ]