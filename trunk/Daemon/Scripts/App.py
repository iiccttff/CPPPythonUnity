# -*- coding: utf-8 -*-
import FastNet,Helper
import sys, json, os
#import SSLServer
import pkt,cfg
import ChildProcess
import traceback
from inspect import isfunction

class App(FastNet.App):
    def __init__(self):
        super(App, self).__init__(self)

        FastNet.LogDebug("App.__init__")
        pass

    def __del__(self):
        FastNet.LogDebug("App.__del__")
        pass

    @property
    def Cfgs(self):
        return FastNet.JsonConfigs

    def OnLogQueryReq(self,key,beginTime,endTime,appId,session):

        c = self.childProcess.get(str(appId),None)
        if c is not None:
            if c.CheckAlive() is True:
                FastNet.AddLogQueryTask(key,beginTime,endTime,appId,session)
            else:
                FastNet.AddLogQueryTaskNotRun(key,beginTime,endTime,appId,session)

    def OnTimer(self):
        
        childs = {}
        for k,v in self.childProcess.items():
            childs[k] = v.CheckAlive()

        self.Publish(self.adminId,json.dumps({'key':'daemon_heartbeat','data':str(FastNet.GetAppId()),'childs':childs}),False)

    def OnCreate(self):

        self.childProcess = {}

        self.adminId = FastNet.JsonConfigs['App']['adminId']
        self.gateId = FastNet.JsonConfigs['App']['gateId']

        self.timer = FastNet.App.Instance.CreateTimer(self,'OnTimer')
        self.timer.Start(3000,3000,-1)

        Helper.gEventLogQuery.Add(self.OnLogQueryReq)

    def OnDestory(self):

        Helper.gEventLogQuery.Remove(self.OnLogQueryReq)

        self.timer.Stop()
        self.timer = None

        for v in self.childProcess.values():
            v.stopServer() 

    def PublishErrorMessage(self,msg):
        self.Publish(self.adminId,json.dumps({'key':'error','data':msg}),True)

    @property
    def GateId(self):
        return self.gateId

    def OnPublish(self,id,j,isPublic):
        #FastNet.LogDebug('App.OnPublish id:{},message:{},isPublic:{}'.format(id,message,isPublic))

        if isPublic is True:
            return
        elif id == FastNet.GetAppId():

            key = j['key']
            val = j['data']

            if key == 'servers':
                for v in val:
                    serverId = v['id']

                    c = self.childProcess.get(serverId,None)
                    if c is None:
                        c = ChildProcess.ChildProcess(v)
                        self.childProcess[serverId] = c
                    else:
                        c.modifyServer(v)

            elif key == 'add':
                serverId = val['id']

                if serverId not in self.childProcess:
                    c = ChildProcess.ChildProcess(val)
                    self.childProcess[serverId] = c
                else:
                    self.PublishErrorMessage('repeat add serverId:{}'.format(serverId))

            elif key == 'del':
                serverId = val['id']

                c = self.childProcess.get(serverId,None)
                if c is None:
                    self.PublishErrorMessage('no find serverId:{}'.format(serverId))
                else:

                    if c.IsStop is False:
                        self.PublishErrorMessage('no stop serverId:{}'.format(serverId))
                    else:
                        c.stopServer()
                        c.Delete()
                        del self.childProcess[serverId]
                
            elif isinstance(val,dict):
                serverId = val['id']

                c = self.childProcess.get(serverId,None)
                if c is None:
                    self.PublishErrorMessage('no find serverId:{}'.format(serverId))
                else:
                    
                    f = getattr(c,key,None)
                    if f is not None:
                            
                        try:
                            f(val)
                        except Exception as e:
                            FastNet.LogException('App.OnPublish {}'.format(e))
                    else:
                        self.PublishErrorMessage('no find callback:{}'.format(key))

    def OnSubscribe(self,id):
        FastNet.LogDebug('App.OnSubscribe id:{}'.format(id))

        if id == FastNet.GetAppId() or id == self.adminId:
            args = {}
            args['key'] = 'daemon_init'
            args['data'] = str(FastNet.GetAppId())
            args['logServerAddress'] = self.LogServer.ListenAddress
            args['logServerAddressWan'] = self.LogServer.ListenAddressWan

            self.Publish(self.adminId,json.dumps(args),False)

    def OnUnsubscribe(self,id):
        FastNet.LogDebug('App.OnUnsubscribe id:{}'.format(id))


def Main(app):

	try:
	    app.Run()
	except Exception as e:
	    traceback.print_exc()