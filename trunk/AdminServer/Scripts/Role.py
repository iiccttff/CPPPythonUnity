# -*- coding: utf-8 -*-
import FastNet
import sys,json
import cfg,pkt,time


class Role(FastNet.Role):
    def __init__(self,id):
        super(Role, self).__init__(self,id)

        self.nickName = '超级管理员'
        self.tabs = {}
        self.isAdmin = None

    def __del__(self):
        print('Role.__del__',self.Id)
        pass


    @property
    def IsAdmin(self):
        if self.isAdmin == None:
            if FastNet.StoreManager.Instance.AccountToUid('admin',self.ChannelId) == self.UserId:
                self.isAdmin = True
            else:
                self.isAdmin = False

        return self.isAdmin

    @property
    def NickName(self):
        return self.nickName

    @property
    def Tabs(self):
        return self.tabs

    @Tabs.setter
    def Tabs(self,value):
        self.tabs = value

    @NickName.setter
    def NickName(self,value):
        self.nickName = value

    def OnCache(self,sr):
        #print 'Role.OnCache',self.Id
        self.nickName = sr.ReadString("nickName",self.nickName)
        self.tabs = sr.ReadDict("tabs",self.tabs)
        pass

    def OnFlush(self,sw):
        
        #print 'Role.OnFlush',self.Id
        sw.WriteString("nickName",self.nickName)
        sw.WriteDict("tabs",self.tabs)
        pass

    def _DoLogin(self):
        #FastNet.LogDebug('Role._DoLogin:{}'.format(self.Id))

        if self.IsAdmin:
            self.tabs = {}
            #FastNet.GlobalManager.Instance.RegisterGlobal('ServerMgr',globals.ServerMgr.ServerMgr)

            self.tabs['PlatformMgr'] = (True,{'Server':['AllowAll'],'Platform':['AllowAll'],'Channel':['AllowAll']})
            self.tabs['ServerMgr'] = (True,cfg.globals.modules.ServerMgr.GetKeys())
            self.tabs['UserMgr'] = (True,None)
            self.tabs['DataQuery'] = (True,cfg.globals.modules.DataQuery.GetKeys())
            self.tabs['NoticeMgr'] = (True,['AllowAllServer','AllowPlatform','AllowServer','AllowCheck'])
            self.tabs['MailMgr'] = (True,['AllowAllServer','AllowPlatform','AllowServer','AllowCheck'])

        m = pkt.common.RoleLoginSucceedRes()
        m.roleId = self.Id
        m.name = self.NickName
        m.tabs = json.dumps(self.tabs)
        self.Session.SendMsg(m)

    def OnLogin(self):
        self._DoLogin()

    def OnLogout(self):
        #FastNet.LogDebug('Role.OnLogout:{}'.format(self.Id))
        pass

    def OnDisconnect(self):
        #print 'Role.OnDisconnect',self.Id
        pass

    def OnReconnect(self):
        self._DoLogin()
        pass