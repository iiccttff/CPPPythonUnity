# -*- coding: utf-8 -*-
import FastNet
import pkt
import json, time
import App
import globals.Global

class MailMgr(globals.Global.Global):
    def __init__(self):
        super(MailMgr,self).__init__('MailMgr')


    def Authentication(self,role,data):
        mailMgrTabInfo = role.Tabs.get('MailMgr',None)
        if mailMgrTabInfo is None or mailMgrTabInfo[0] == False:
            return False

        platformMgrTabInfo = role.Tabs.get('PlatformMgr',None)
        if platformMgrTabInfo is None:
            return False

        platformMgrTabInfo = platformMgrTabInfo[1]
        param = data['param']
        sendType = param['type']
        if sendType == 'AllServer':
            if 'AllowAllServer' not in mailMgrTabInfo[1]:
                return False

        elif sendType == 'Platform':
            if 'AllowPlatform' not in mailMgrTabInfo[1]:
                return False
                    
            if 'AllowAll' not in platformMgrTabInfo['Platform'] and param['param'] not in platformMgrTabInfo['Platform']:
                return False

        elif sendType == 'Server':
            if 'AllowServer' not in mailMgrTabInfo[1]:
                return False

            if 'AllowAll' not in platformMgrTabInfo['Server'] and param['param'] not in platformMgrTabInfo['Server']:
                return False

        elif sendType == 'Channel':
            if 'AllowAll' not in platformMgrTabInfo['Channel'] and param['param'] not in platformMgrTabInfo['Channel']:
                return False

        elif sendType == 'Roles':
            serverList = platformMgrTabInfo['Server']
            if 'AllowAll' not in serverList:
                for v in param['param']:
                    if v[1] not in serverList:
                        return False

        return True

    def GetAnyReq(self,data,role):

        t = data['type']
        k = data['key']
        if t == 'add':
            
            if k not in self.datas:

                if self.Authentication(role,data['val']) is False:
                    role.Session.SendErrorMessage(None,'没有操作权限!')
                    return None

                if data['val']['valid'] == 0:
                    data['val']['valid'] = 7

                data['val']['role'] = role.NickName
                self.datas[k] = data['val']
                return data

        elif t == 'del':
            o = self.datas.get(k,None)
            if o is not None:
                if o['status'] == True:
                    return None
                
        elif t == 'modify':
            return None

        return super(MailMgr,self).GetAnyReq(data,role)

    def SendInitData(self,role):

        mailMgrTabInfo = role.Tabs.get('MailMgr',None)
        if mailMgrTabInfo is None or mailMgrTabInfo[0] == False:
            return

        if 'AllowCheck' not in mailMgrTabInfo[1]:

            datas = {}
            for k,v in self.datas.items():
                if v['role'] == role.NickName:
                    datas[k] = v

            m = pkt.common.AnyRes()
            m.classId = self.__class__.__name__
            m.data = json.dumps({'type':'init','val':datas})
            role.Session.SendMsg(m)
        else:
            m = pkt.common.AnyRes()
            m.classId = self.__class__.__name__
            m.data = json.dumps({'type':'init','val':self.datas})
            role.Session.SendMsg(m)