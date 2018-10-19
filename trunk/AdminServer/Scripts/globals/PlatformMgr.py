# -*- coding: utf-8 -*-
import FastNet
import pkt
import json
import globals.Global

class PlatformMgr(globals.Global.Global):
    def __init__(self):
        super(PlatformMgr,self).__init__('PlatformMgr')

        self.channels = {}
        self.platforms = {}
        self.servergroups = {}

    @property
    def Channels(self):
        return self.channels

    @property
    def Platforms(self):
        return self.platforms

    def OnCache(self,sr):
        self.channels = sr.ReadList('channels',self.channels)
        self.platforms = sr.ReadList('platforms',self.platforms)
        self.servergroups = sr.ReadList('servergroups',self.servergroups)
        

    def OnFlush(self,sw):
        sw.WriteList('channels',self.channels)
        sw.WriteList('platforms',self.platforms)
        sw.WriteList('servergroups',self.servergroups)


    def GetAnyReq(self,data,role):

        platformMgrTabInfo = role.Tabs.get('PlatformMgr',None)
        if platformMgrTabInfo is None or platformMgrTabInfo[0] == False:
            role.Session.SendErrorMessage(None,'没有操作权限!')
            return None

        t = data['type']
        k = data['key']
        v = data['val']

        o = None
        if v == 'channels':
            o = self.channels
        elif v == 'servergroups':
            o = self.servergroups
        elif v == 'platforms':
            o = self.platforms

        if o is not None:
            if t == 'add':

                d = data['data']
                if k not in o:
                    o[k] = d
                    return data
                else:
                    role.Session.SendErrorMessage(None,'添加失败,名称重复:' + k)

            elif t == 'del':
                if k in o:
                    o.pop(k)
                    return data
                else:
                    role.Session.SendErrorMessage(None,'删除失败,没有找到名称:' + k)

            elif t == 'modify':
                d = data['data']
                if k in o:
                    for kk,vv in d.items():
                        o[k][kk] = vv
                    return data
                else:
                    role.Session.SendErrorMessage(None,'保存失败,没有找到名称:' + k)

        return None

    def SendInitData(self,role):

        m = pkt.common.AnyRes()
        m.classId = self.__class__.__name__
        m.data = json.dumps(    \
            {'type':'init',
             'channels':self.channels,
             'platforms':self.platforms,
             'servergroups':self.servergroups
             })

        role.Session.SendMsg(m)