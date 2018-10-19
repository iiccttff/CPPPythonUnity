# -*- coding: utf-8 -*-
import FastNet
import pkt
import json
import time, datetime
import svn.exception
import svn.remote
import globals.Global

class ServerMgr(globals.Global.Global):
    def __init__(self):
        super(ServerMgr,self).__init__('ServerMgr')

        self.servers = {}
        self.daemons = {}

        self.datas = {
            'svns':{},
            'repairWhitelists':{},
            'newEnterNoticeMails':{},
           }

        self.serverOnlineNum = {}

    @property
    def Servers(self):
        return self.servers

    @property
    def Daemons(self):
        return self.daemons
        
    def OnTimer(self):

        now = int(time.time())
        for k,v in self.daemons.items():
            if (now - v['status']) > 15:
                v['status'] = 0

            self.UpdateDaemonStatus(k,v['status'])

        self.UpdateServerStatus()

    def UpdateOnlineNumber(self,data):
        self.serverOnlineNum[int(data['id'])] = int(data['data'])

        for v in self.servers.values():
            if v['projectName'] == 'LoginServer':
                FastNet.App.Instance.Publish(daemonId,json.dumps(data),False)

    def DaemonInit(self,j):

        daemonId = int(j['data'])
        logServerAddress = j['logServerAddress']
        logServerAddressWan = j['logServerAddressWan']

        for v in self.daemons.values():
            if int(v['id']) == daemonId:
                v['status'] = int(time.time())
                v['logServerAddress'] = logServerAddress
                v['logServerAddressWan'] = logServerAddressWan

        servers = []
        for v in self.servers.values():
            if int(self.daemons[v['daemon']]['id']) != daemonId:
                continue
            
            servers.append(self.MakeServerInfo(v))

        FastNet.App.Instance.Publish(daemonId,json.dumps({'key':'servers','data':servers}),False)

    def DaemonHeartbeat(self,daemonId,childs):
        for v in self.daemons.values():
            if int(v['id']) == daemonId:
                v['status'] = int(time.time())

        for k,v in self.servers.items():
            isrun = childs.get(v['id'],None)

            if isrun is not None:

                status = v['status']
                if isrun is True:
                    v['status'] = 'running'
                elif isrun is False:
                    v['status'] = 'stop'

    def OnCreate(self):
        self.timer = FastNet.App.Instance.CreateTimer(self,'OnTimer')
        self.timer.Start(2000,0,-1)
        pass

    def OnDestory(self):
        self.timer.Stop()
        self.timer = None
        pass

    def OnCache(self,sr):
        for k,v in self.datas.items():
            self.datas[k] = sr.ReadList(k,v)

        self.servers = sr.ReadList('servers',self.servers)
        self.daemons = sr.ReadList('daemons',self.daemons)

    def OnFlush(self,sw):

        for k,v in self.datas.items():
            sw.WriteList(k,v)

        sw.WriteList('servers',self.servers)
        sw.WriteList('daemons',self.daemons)

    def SendInitData(self,role):
        m = pkt.common.AnyRes()
        m.classId = self.__class__.__name__
        datas = {'type':'init'}
        for k,v in self.datas.items():
            datas[k] = v

        datas['servers'] = self.servers
        datas['daemons'] = self.daemons

        m.data = json.dumps(datas)
        role.Session.SendMsg(m)

    def MakeServerInfo(self,server):
        
        param = {}
        param['projectName'] = server['projectName']
        param['id'] = server['id']
        param['startParam'] = server['startParam']

        status = server['status']
        if status == 'stop' or status == 'stoping':
            param['isstop'] = True
        else:
            param['isstop'] = False

        param['repair'] = server['repair'] == 'true'

        codeStr = server['code']
        code = self.datas['svns'][codeStr[:codeStr.rfind('|')]]
        param['url_code'] = code['url']
        param['username_code'] = code['username']
        param['password_code'] = code['password']
        param['revision_code'] = codeStr[codeStr.rfind('|') + 1:]

        cfgStr = server['cfg']
        cfg = self.datas['svns'][cfgStr[:cfgStr.rfind('|')]]
        param['url_cfg'] = cfg['url']
        param['username_cfg'] = cfg['username']
        param['password_cfg'] = cfg['password']
        param['revision_cfg'] = cfgStr[cfgStr.rfind('|') + 1:]

        param['newEnterNoticeNum'] = int(server['newEnterNoticeNum'])
        param['overflowPlayerNum'] = int(server['overflowPlayerNum'])
        param['crowdingPlayerNum'] = int(server['crowdingPlayerNum'])
        param['smoothPlayerPlayerNum'] = int(server['smoothPlayerPlayerNum'])
        param['maxPlayerNum'] = int(server['maxPlayerNum'])
        param['warningPlayerNum'] = int(server['warningPlayerNum'])
        param['perMinuteEntryPlayerNum'] = int(server['perMinuteEntryPlayerNum'])

        return param

    def GetAnyReq(self,data,role):

        serverMgrTabInfo = role.Tabs.get('ServerMgr',None)
        if serverMgrTabInfo is None or serverMgrTabInfo[0] == False:
            role.Session.SendErrorMessage(None,'没有操作权限!')
            return None
 
        t = data['type']
        k = data['key']
        v = data['val']
        o = None

        if v == 'servers':
            o = self.servers
        elif v == 'daemons':
            o = self.daemons
        else:
            o = self.datas.get(v,None)

        if o is not None:

            if v == 'servers':

                if t == 'add':
                    d = data['data']
                    serverId = d['id']
                    for kkk,vvv in o.items():
                        if vvv['id'] == serverId:
                            role.Session.SendErrorMessage(None,'添加服务器失败,唯一ID重复:' + serverId)
                            return

                    if k not in o:
                        daemonName = d['daemon']
                        daemonId = self.daemons[daemonName]['id']
                        param = self.MakeServerInfo(d)
                        FastNet.App.Instance.Publish(daemonId,json.dumps({'key':'add','data':param}),False)

                elif t == 'del':
                    if k in o:
                        daemonName = o[k]['daemon']
                        daemonId = self.daemons[daemonName]['id']

                        app = FastNet.App.Instance
                        app.Publish(daemonId,json.dumps({'key':'del','data':o[k]}),False)

                elif t == 'start':
                    status = o[k]['status']
                    if status == 'stop':
                        o[k]['status'] = 'starting'
                        self._StartServer(k,role)

                elif t == 'stop':
                    status = o[k]['status']
                    if status == 'running':
                        o[k]['status'] = 'stoping'
                        self._StopServer(k,role)

                elif t == 'beginRepair':
                    if o[k]['repair'] == 'false':
                        o[k]['repair'] = 'true'
                        self._BeginRepairServer(k,role)
            
                elif t == 'endRepair':
                    if o[k]['repair'] == 'true':
                        o[k]['repair'] = 'false'
                        self._EndRepairServer(k,role)

                elif t == 'updateCfg':
                    self._UpdateServerCfg(k,role)

                elif t == 'modify':
                    self._ModifyServer(k,role)

            elif v == 'svns':
                if t == 'query':
                    ret = o.get(k,None)
                    if ret is not None:
                        
                        try:
                            logs = []
                            rc = svn.remote.RemoteClient(ret['url'],
                                                            username=ret['username'],
                                                            password=ret['password'])

                            for e in rc.log_default():
                                date = e.date.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
                                logs.append((int(time.mktime(date.timetuple())),e.revision,e.author))

                            data['data'] = logs
                            return data
                        except svn.exception.SvnException as e:
                            role.Session.SendErrorMessage(None,'获取SVN日志出错:' + str(e))


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

    def _BeginRepairServer(self,k,role):

        try:

            server = self.servers[k]
            daemonName = server['daemon']
            daemonId = self.daemons[daemonName]['id']

            if self.daemons[daemonName]['status'] == 0:
                raise Exception('未检测到辅助进程')

            ips = []

            repairWhitelist = server['repairWhitelist']
            repairWhitelists = self.datas['repairWhitelists']
            if repairWhitelist in repairWhitelists :
                for v in repairWhitelists[repairWhitelist]['param']:
                    ips.append(v['ip'])

            FastNet.App.Instance.Publish(daemonId,json.dumps({'key':'beginRepairServer','data':{'id':server['id'],'ips':ips}}),False)
            
        except Exception as e:
            role.Session.SendErrorMessage(None,'开始维护服务器 {} 失败:{}'.format(k,e))


    def _EndRepairServer(self,k,role):

        try:
            server = self.servers[k]
            daemonName = server['daemon']
            daemonId = self.daemons[daemonName]['id']

            if self.daemons[daemonName]['status'] == 0:
                raise Exception('未检测到辅助进程')

            FastNet.App.Instance.Publish(daemonId,json.dumps({'key':'endRepairServer','data':server}),False)
            
        except Exception as e:
            role.Session.SendErrorMessage(None,'停止维护服务器 {} 失败:{}'.format(k,e))

    def _StartServer(self,k,role):

        try:
            server = self.servers[k]
            daemonName = server['daemon']
            daemonId = self.daemons[daemonName]['id']

            if self.daemons[daemonName]['status'] == 0:
                raise Exception('未检测到辅助进程')

            FastNet.App.Instance.Publish(daemonId,json.dumps({'key':'startServer','data':server}),False)
            
        except Exception as e:
            role.Session.SendErrorMessage(None,'启动服务器 {} 失败:{}'.format(k,e))

    def _StopServer(self,k,role):

        try: 
            server = self.servers[k]
            daemonName = server['daemon']
            daemonId = self.daemons[daemonName]['id']

            if self.daemons[daemonName]['status'] == 0:
                raise Exception('未检测到辅助进程')

            FastNet.App.Instance.Publish(daemonId,json.dumps({'key':'stopServer','data':server}),False)

        except Exception as e:
            role.Session.SendErrorMessage(None,'停止服务器 {} 失败:{}'.format(k,e))



    def _ModifyServer(self,serverName,role):
        try:
            server = self.servers[serverName]
            param = self.MakeServerInfo(server)

            daemonName = server['daemon']
            daemonId = self.daemons[daemonName]['id']
            FastNet.App.Instance.Publish(daemonId,json.dumps({'key':'modifyServer','data':param}),False)

        except Exception as e:
            role.Session.SendErrorMessage(None,'更新服务器 {} 失败:{}'.format(serverName,e))


    def UpdateDaemonStatus(self,daemonName,daemonStatus):

        def IsValid(session):
            return session.IsAccountVerifySucceed
        try:
            m = pkt.common.AnyRes()
            m.classId = self.__class__.__name__
            m.data = json.dumps({'type':'daemon_status','key':daemonName,'data':daemonStatus})

            FastNet.App.Instance.Server.BroadcastMsg(m,IsValid)

        except Exception as e:
            FastNet.LogException('ServerMgr.UpdateDaemonStatus {} {}'.format(daemonName,e))


    def UpdateServerStatus(self):

        def IsValid(session):
            return session.IsAccountVerifySucceed
        try:

            for k,v in self.servers.items():

                m = pkt.common.AnyRes()
                m.classId = self.__class__.__name__
                m.data = json.dumps({'type':'status','key':k,'status':v['status'],'repair':v['repair']})
                FastNet.App.Instance.Server.BroadcastMsg(m,IsValid)

        except Exception as e:
            FastNet.LogException('ServerMgr.UpdateServerStatus {}'.format(e))

    