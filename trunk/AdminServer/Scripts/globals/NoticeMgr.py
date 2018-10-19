# -*- coding: utf-8 -*-
import FastNet
import pkt
import json
import App
import globals.Global

class NoticeMgr(globals.Global.Global):
    def __init__(self):
        super(NoticeMgr,self).__init__('NoticeMgr')


    def Authentication(self,role,data):
        noticeMgrTabInfo = role.Tabs.get('NoticeMgr',None)
        if noticeMgrTabInfo is None or noticeMgrTabInfo[0] == False:
            return False

        platformMgrTabInfo = role.Tabs.get('PlatformMgr',None)
        if platformMgrTabInfo is None:
            return False

        platformMgrTabInfo = platformMgrTabInfo[1]

        param = data['param']
        sendType = param['type']
        if sendType == 'AllServer':
            if 'AllowAllServer' not in noticeMgrTabInfo[1]:
                return False

        elif sendType == 'Platform':
            if 'AllowPlatform' not in noticeMgrTabInfo[1]:
                return False
                    
            if 'AllowAll' not in platformMgrTabInfo['Platform'] and param['param'] not in platformMgrTabInfo['Platform']:
                return False

        elif sendType == 'Server':
            if 'AllowServer' not in noticeMgrTabInfo[1]:
                return False

            if 'AllowAll' not in platformMgrTabInfo['Server'] and param['param'] not in platformMgrTabInfo['Server']:
                return False

        elif sendType == 'Channel':
            if 'AllowAll' not in platformMgrTabInfo['Channel'] and param['param'] not in platformMgrTabInfo['Channel']:
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
    
                data['val']['role'] = role.NickName
                self.datas[k] = data['val']
                return data
    
        elif t == 'modify':
            return None

        return super(NoticeMgr,self).GetAnyReq(data,role)

    def SendInitData(self,role):

        noticeMgrTabInfo = role.Tabs.get('NoticeMgr',None)
        if noticeMgrTabInfo is None or noticeMgrTabInfo[0] == False:
            return

        if 'AllowCheck' not in noticeMgrTabInfo[1]:

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