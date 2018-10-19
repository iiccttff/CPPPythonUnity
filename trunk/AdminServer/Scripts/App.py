# -*- coding: utf-8 -*-
import FastNet
import sys, json, os, time, hashlib, uuid
import pkt
import Role
import modules.Email
import globals.UserMgr
import globals.ServerMgr
import globals.DataQuery
import globals.PlatformMgr
import globals.MailMgr
import globals.NoticeMgr

import traceback

class App(FastNet.App):
    def __init__(self):
        super(App, self).__init__(self)

        FastNet.LogDebug("App.__init__")

    def __del__(self):
        FastNet.LogDebug("App.__del__")
        pass

    @property
    def Cfgs(self):
        return FastNet.JsonConfigs

    def OnCreate(self):
        FastNet.RoleManager.Instance.RegisterRole("role",Role.Role)
        FastNet.RoleManager.Instance.RegisterModule("role","Email",modules.Email.Email)
        #FastNet.RoleManager.Instance.RegisterModule("role","UserMgr",modules.UserMgr.UserMgr)

        FastNet.GlobalManager.Instance.RegisterGlobal('ServerMgr',globals.ServerMgr.ServerMgr)
        FastNet.GlobalManager.Instance.RegisterGlobal('UserMgr',globals.UserMgr.UserMgr)
        FastNet.GlobalManager.Instance.RegisterGlobal('DataQuery',globals.DataQuery.DataQuery)
        FastNet.GlobalManager.Instance.RegisterGlobal('PlatformMgr',globals.PlatformMgr.PlatformMgr)
        FastNet.GlobalManager.Instance.RegisterGlobal('NoticeMgr',globals.NoticeMgr.NoticeMgr)
        FastNet.GlobalManager.Instance.RegisterGlobal('MailMgr',globals.MailMgr.MailMgr)

        self.serverMgr = FastNet.GlobalManager.Instance.GetGlobal('ServerMgr')
        self.Server.BindMessage(pkt.common.AnyReq.sClsId,'OnAnyReq')

    def OnDestory(self):
        self.serverMgr = None
 
    def OnPublish(self,id,j,isPublic):

        key = j['key']

        if isPublic == True:

            if 'error' == key:
                def IsValid(session):
                    return session.IsAccountVerifySucceed

                m = FastNet.Message.Create(pkt.protocols.ErrorMessage.sClsId)
                m.msg = j['data']
                self.Server.BroadcastMsg(m,IsValid)

                FastNet.LogError('OnPublish {}-{}'.format(id, j['data']))
        else:

            if 'daemon_init' == key:
                self.serverMgr.DaemonInit(j)

            elif 'daemon_heartbeat' == key:
                self.serverMgr.DaemonHeartbeat(int(j['data']),j['childs'])

            elif 'onlineNumber' == key:
                self.serverMgr.UpdateOnlineNumber(j)

    def OnSubscribe(self,id):
        FastNet.LogDebug('App.OnSubscribe id:{}'.format(id))

    def OnUnsubscribe(self,id):
        FastNet.LogDebug('App.OnUnsubscribe id:{}'.format(id))

def Main(app):

	try:
	    app.Run()
	except Exception as e:
	    traceback.print_exc()