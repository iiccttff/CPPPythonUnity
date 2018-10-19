# -*- coding: utf-8 -*-
import FastNet
import pkt
import json

class Global(FastNet.Global):
    def __init__(self,name):
        super(Global,self).__init__(self,name)

        self.datas = {}

    def OnCreate(self):
        pass

    def OnDestory(self):
        pass

    def OnCache(self,sr):
        self.datas = sr.ReadList('datas',self.datas)

    def OnFlush(self,sw):
        sw.WriteList('datas',self.datas)

    def OnRoleLogin(self,role):
        self.SendInitData(role)

    def OnRoleLogout(self,role):
        pass

    def OnRoleDisconnect(self,role):
        pass

    def OnRoleReconnect(self,role):
        self.SendInitData(role)

    def GetAnyReq(self,data,role):
 
        t = data['type']
        k = data['key']
        if t == 'add':
            if k not in self.datas:
                self.datas[k] = data['val']
                return data
            else:
                role.Session.SendErrorMessage(None,'添加失败,名称重复:' + k)
        elif t == 'del':
            if k in self.datas:
                self.datas.pop(k)
                return data
            else:
                role.Session.SendErrorMessage(None,'删除失败,没有找到名称:' + k)
        elif t == 'modify':
            if k in self.datas:
                for kk,vv in data['val'].items():
                    self.datas[k][kk] = vv
                return data
            else:
                role.Session.SendErrorMessage(None,'保存失败,没有找到名称:' + k)
        return None

    def SendInitData(self,role):
        m = pkt.common.AnyRes()
        m.classId = self.__class__.__name__
        m.data = json.dumps({'type':'init','val':self.datas})
        role.Session.SendMsg(m)