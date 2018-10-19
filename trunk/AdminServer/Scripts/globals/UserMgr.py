
# -*- coding: utf-8 -*-
import FastNet
import pkt, cfg
import json
import globals.Global

class UserMgr(globals.Global.Global):
    def __init__(self):
        super(UserMgr,self).__init__('UserMgr')

    def GetAnyReq(self,data,role):

        userMgrTabInfo = role.Tabs.get('UserMgr',None)
        if userMgrTabInfo is None or userMgrTabInfo[0] == False:
            role.Session.SendErrorMessage(None,'没有操作权限!')
            return None
 
        t = data['type']
        k = data['key']
        if t == 'add':
            if k not in self.datas:
                val = data['val']

                uid = FastNet.StoreManager.AccountToUid(val['account'],'000')
                roleIds = FastNet.StoreManager.Instance.GetRoleIds(uid)
                if len(roleIds) > 0:
                    role.Session.SendErrorMessage(None,'添加失败,账号已经存在:' + val['account'])
                    return None

                if FastNet.Helper.Instance.AddAccount(val['account'],val['password'],'000') == False:
                    role.Session.SendErrorMessage(None,'添加失败,账号已经存在:' + val['account'])
                    return None

                roleNew = FastNet.RoleManager.Instance.CreateRole(uid,'000','role')
                roleNew.NickName = val['name']
                roleNew.Tabs = val['permissions']
                roleNew.Save()

                self.datas[k] = val
                return data

        elif t == 'del':
            if k in self.datas:
                val = self.datas[k]
                FastNet.Helper.Instance.DeleteAccount(val['account'],'000')

                uid = FastNet.StoreManager.AccountToUid(val['account'],'000')
                roleIds = FastNet.StoreManager.Instance.GetRoleIds(uid)
                for v in roleIds:
                    FastNet.RoleManager.Instance.DeleteRole(v,'role')

                self.datas.pop(k)
                return data
                
        elif t == 'modify':
            if k in self.datas:
                val = data['val']
                o = self.datas[k]
                o['password'] = val['password']
                o['desc'] = val['desc']
                o['permissions'] = val['permissions']

                uid = FastNet.StoreManager.AccountToUid(o['account'],'000')
                roleIds = FastNet.StoreManager.Instance.GetRoleIds(uid)
                roleOld = FastNet.RoleManager.Instance.GetRole(roleIds[0],'role',True)
                roleOld.Tabs = o['permissions']
                roleOld.Save()

                #self.datas[k]['password'] = val['password']
                FastNet.Helper.Instance.ModifyAccount(val['account'],val['password'],'000')
                return data

        return super(UserMgr,self).GetAnyReq(data,role)

    def SendInitData(self,role):
        userMgrTabInfo = role.Tabs.get('UserMgr',None)
        if userMgrTabInfo is None or userMgrTabInfo[0] == False:
            return None

        return super(UserMgr,self).SendInitData(role)