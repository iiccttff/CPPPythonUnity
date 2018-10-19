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

    def OnCreate(self):
        self.adminId = FastNet.JsonConfigs['App']['adminId']

        self.loginServers = {}

    def OnDestory(self):
        pass

    def OnPublish(self,id,j,isPublic):

        if isPublic is True:
            return
        else:
            key = j['key']
   
            if 'onlineNumber' == key:
                #self.FightHeartbeat(int(j['data']))

                self.loginServers[j['id']] = j['data']

    def OnSubscribe(self,id):
        FastNet.LogDebug('App.OnSubscribe id:{}'.format(id))

    def OnUnsubscribe(self,id):
        FastNet.LogDebug('App.OnUnsubscribe id:{}'.format(id))

def Main(app):

	try:
	    app.Run()
	except Exception as e:
	    traceback.print_exc()