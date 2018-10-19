# -*- coding: utf-8 -*-


import FastNet
import pkt
import cfg
import Signals
import json, traceback

class Client(FastNet.Client):
    def __init__(self,gateServer = False):
        super(Client, self).__init__(self)
        Signals.gSignals.SendMsg.connect(self.OnSendMsg)

        self.BindMessage(pkt.common.AccountVerifySucceedRes.sClsId, 'OnAccountVerifySucceedRes')
        self.BindMessage(pkt.common.RoleLoginSucceedRes.sClsId, 'OnRoleLoginSucceedRes')
        self.BindMessage(pkt.protocols.ErrorMessage.sClsId, 'OnErrorMessage')
        self.BindMessage(pkt.common.AnyRes.sClsId, 'OnAnyRes')
        #self.BindMessage(pkt.common.ServerGotoRes.sClsId, 'OnServerGotoRes')
        self.roleId = None
        self.destory = False
        self.isGateServer = gateServer

    def Destory(self):
        self.destory = True
        self.Close()

    @property
    def RoleId(self):
        return self.roleId

    @property
    def IsGateServer(self):
        return self.isGateServer

    def OnSendMsg(self, message):
        self.SendMsg(message)

    def OnErrorMessage(self,message):
        print(message.key)
        cfgItem = cfg.globals.base.ErrorCode.GetValue(message.key)
        if cfgItem is not None:
            FastNet.App.Instance.MainWindow.WriteErrorLog(cfgItem.msg)
        elif len(message.msg) > 0:
            FastNet.App.Instance.MainWindow.WriteErrorLog(message.msg)
        else:
            FastNet.App.Instance.MainWindow.WriteErrorLog("未知的错误标识 {}".format(message.key))

    def OnRoleLogin(self, roleId):
        self.roleId = roleId

    def OnAccountVerifySucceedRes(self, message):
        Signals.gSignals.AccountVerifySucceedRes.emit(message.roleId)

    def OnRoleLoginSucceedRes(self, message):
        Signals.gSignals.RoleLoginSucceedRes.emit(message)

    def OnAnyRes(self, message):
        try:
            Signals.gSignals.AnyRes.emit(message.classId, json.loads(message.data))
        except:
            traceback.print_exc()

    #def OnServerGotoRes(self, message):
    #    Signals.gSignals.ServerGoto.emit(message.serverAddress,message.token,message.serverId)

    def OnSocketEvent(self, e, info):
        if e == FastNet.SocketEvent.kConnectSucceed:
            Signals.gSignals.SocketConnect.emit(True)
        elif e == FastNet.SocketEvent.kErrorMessage:
            FastNet.App.Instance.MainWindow.WriteLog(info)
        elif e == FastNet.SocketEvent.kConnectClosed or \
            e == FastNet.SocketEvent.kConnectFailure or \
            e == FastNet.SocketEvent.kReConnectFailure:

            if self.destory is False:
                Signals.gSignals.SocketConnect.emit(False)
                FastNet.LogError('Client.OnSocketEvent ' + info)
