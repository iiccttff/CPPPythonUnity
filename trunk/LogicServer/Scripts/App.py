# -*- coding: utf-8 -*-
import FastNet
import sys, json, os, time
import pkt,cfg
import traceback

class App(FastNet.App):
    def __init__(self):
        super(App, self).__init__(self)

        FastNet.LogNormal("App.__init__")
        pass

    def __del__(self):
        FastNet.LogNormal("App.__del__")
        pass

    @property
    def Cfgs(self):
        return FastNet.JsonConfigs

    def OnTimer(self):
        now = int(time.time())
        removeFights = []
        for k,v in self.fights.items():
            if (now - v) > 60:
                removeFights.append(k)

        for v in removeFights:
            del self.fights[v]

        param = {}
        param['key'] = 'onlineNumber'
        param['data'] = self.Server.OnlineNumber
        param['id'] = FastNet.GetAppId()

        self.Publish(self.adminId,json.dumps(param))

    def OnCreate(self):

        self.fights = {}

        self.timer = FastNet.App.Instance.CreateTimer(self,'OnTimer')
        self.timer.Start(3000,0,-1)

        self.adminId = FastNet.JsonConfigs['App']['adminId']

    def OnDestory(self):

        self.timer.Stop()
        self.timer = None

    def FightHeartbeat(self,data):
        self.fights[data] = int(time.time())


    def OnPublish(self,id,j,isPublic):

        if isPublic is True:
            return
        else:
            key = j['key']
   
            if 'fight_heartbeat' == key:
                self.FightHeartbeat(int(j['data']))

            elif key == 'testReq':
                import QATest
                t = QATest.QATest()
                t.run()


    def OnSubscribe(self,id):
        FastNet.LogDebug('App.OnSubscribe id:{}'.format(id))

    def OnUnsubscribe(self,id):
        FastNet.LogDebug('App.OnUnsubscribe id:{}'.format(id))

def Main(app):

	try:
	    app.Run()
	except Exception as e:
	    traceback.print_exc()