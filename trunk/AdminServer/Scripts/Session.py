# -*- coding: utf-8 -*-
import FastNet
import sys,json
import pkt,time


class Session(FastNet.Session):
    def __init__(self,cp):
        super(Session, self).__init__(self,cp)

        self.role = None

        self.isAccountVerifySucceed = False

        FastNet.LogDebug('Session.__init__')

    @property
    def IsAccountVerifySucceed(self):
        return self.isAccountVerifySucceed

    def SendErrorMessage(self,code,msg):
        m = FastNet.Message.Create(pkt.protocols.ErrorMessage.sClsId)
        if code is not None:
            m.key = code
        if msg is not None:
            m.msg = str(msg)
        self.SendMsg(m)

    def __del__(self):
        FastNet.LogDebug('Session.__del__')

    def OnCreate(self):
        FastNet.LogDebug('Session.OnCreate:{}'.format(self.SessionId))

    def OnDestory(self):
        FastNet.LogDebug('Session.OnDestory:{}'.format(self.SessionId))

    def OnRoleLogin(self,roleId):
        self.role = FastNet.RoleManager.Instance.GetRole(roleId,'role')
        FastNet.LogDebug('Session.OnRoleLogin:{}'.format(roleId))
        return self.role

    def OnAccountVerifySucceed(self, uid, channel):
        FastNet.LogDebug('Session.OnAccountVerifySucceed' + str(uid) + str(channel))

        m = FastNet.Message.Create(pkt.common.AccountVerifySucceedRes.sClsId)
        roleIds = FastNet.StoreManager.Instance.GetRoleIds(uid)
        if len(roleIds) > 0:
            m.roleId = roleIds[0]
        else:
            role = FastNet.RoleManager.Instance.CreateRole(uid,channel,'role')
            m.roleId = role.Id

        self.SendMsg(m)
        
        self.isAccountVerifySucceed = True

    def OnAnyReq(self,message):
        if self.role is not None and message.classId in self.role.Tabs:

            g = FastNet.GlobalManager.Instance.GetGlobal(message.classId)
            if g is not None:
                ret = g.GetAnyReq(json.loads(message.data),self.role)
                if ret is not None:
                    m = pkt.common.AnyRes()
                    m.classId = message.classId
                    m.data = json.dumps(ret)
                    self.SendMsg(m)