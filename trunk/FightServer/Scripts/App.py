# -*- coding: utf-8 -*-
import FastNet
import sys, json, os
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
        self.Publish(self.logicId,json.dumps({'key':'fight_heartbeat','data':str(FastNet.GetAppId())}),False)

    def OnCreate(self):

        self.logicId = FastNet.JsonConfigs['App']['logicId']

        self.timer = FastNet.App.Instance.CreateTimer(self,'OnTimer')
        self.timer.Start(3000,3000,-1)

    def OnDestory(self):

        self.timer.Stop()
        self.timer = None

    def OnPublish(self,id,j,isPublic):

        if isPublic is True:
            return
        else:
            key = j['key']
            FastNet.LogDebug('App.OnPublish j:{}'.format(j))

    def OnSubscribe(self,id):
        FastNet.LogDebug('App.OnSubscribe id:{}'.format(id))

    def OnUnsubscribe(self,id):
        FastNet.LogDebug('App.OnUnsubscribe id:{}'.format(id))


def Main(app):

	try:
	    app.Run()
	except Exception as e:
	    traceback.print_exc()