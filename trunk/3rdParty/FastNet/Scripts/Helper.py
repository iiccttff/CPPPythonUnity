# -*- coding: utf-8 -*-
import FastNet
import multiprocessing
import os, time, json, sys, traceback, gc, importlib
import threading,requests
import base64,subprocess
import HttpServer
import psutil


class Event:
    def __init__(self):
        self.events = []

    def RemoveAll(self,):
        self.events = []

    def Add(self,f):
        if f not in self.events:
            self.events.append(f)
    
    def Remove(self,f):
        if f in self.events:
            self.events.remove(f)
    
    def Dispatch(self,*args):
         for v in self.events:
            try:
                v(*args)
            except Exception as e:
                FastNet.LogException('Event.Dispatch ' + str(e))

gEventLogQuery = Event()

class PubSubClient(FastNet.Client):
    def __init__(self):
        super(PubSubClient, self).__init__(self)

    def __del__(self):
        pass

    def OnSocketEvent(self,e,info):
        if e == FastNet.SocketEvent.kConnectSucceed:
            self.Subscribe(FastNet.GetAppId())

class PubSubSession(FastNet.Session):
    def __init__(self,cp):
        super(PubSubSession, self).__init__(self,cp)

    def OnCreate(self):
        pass

    def OnDestory(self):
        pass


class LogSession(FastNet.Session):
    def __init__(self,cp):
        super(LogSession, self).__init__(self,cp)

    def OnCreate(self):
        pass

    def OnDestory(self):
        pass

    def OnLogQueryReq(self,message):
        gEventLogQuery.Dispatch(message.key,message.beginTime,message.endTime,message.appId,self)
        #FastNet.AddLogQueryTask(message.key,message.beginTime,message.endTime,message.appId,self)

class PubSubServer(FastNet.Server):
    def __init__(self,id,ssl,password_cert,session):
        super(PubSubServer, self).__init__(self,session,id,ssl,password_cert)

    def __del__(self):
        pass

    def OnCreate(self):
        pass

    def OnDestory(self):
        pass

def GetExceptionInfo():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    return ''.join(traceback.format_exception(exc_type, exc_value,exc_traceback))



def SendMail(subject,text,receive,sender,password,address,port):
    import smtplib, email.utils, email.mime.text
 
    try:
        msg= email.mime.text.MIMEText(text,'plain','utf-8')
        msg['From']=email.utils.formataddr([sender,sender])
        msg['To']= email.utils.formataddr([receive,receive])
        msg['Subject']= subject
 
        server=smtplib.SMTP_SSL(address, port)
        server.login(sender, password)
        server.sendmail(sender,[receive,],msg.as_string())
        server.quit()

    except Exception as e:
        FastNet.LogException('SendMail {}'.format(e))

def CallMehtod(obj,name,args = None):
    try:
        f = getattr(obj,name,None)
        if f is None:
            FastNet.LogDebug("CallMehtod name={},f==None".format(name))
            return None

        #FastNet.LogDebug("CallMehtod:" + name)
        l = 0
        if args is not None:
            l = len(args)
        if l == 0:
            return f()
        elif l == 1:
            return f(args[0])
        elif l == 2:
            return f(args[0],args[1])
        elif l == 3:
            return f(args[0],args[1],args[2])
        elif l == 4:
            return f(args[0],args[1],args[2],args[3])
        else:
            FastNet.LogError("CallMehtod name={},l={}".format(name,l))

    except:
        FastNet.LogException(GetExceptionInfo())


def AppUpdateMd5Values():

    app = FastNet.App.Instance
    if app.Server is None:
        return

    cfgApp = FastNet.JsonConfigs["App"]
    if cfgApp.get('clientResourceUpdate',None) == True:
        md5Values = {}

        filename = FastNet.GetDataPath() + r'/cfg_version.bytes'
        if os.path.exists(filename) and os.path.isfile(filename):
            with open(filename,'r' ) as f:
                md5Values = json.loads(f.read())

        filename = FastNet.GetDataPath() + r'/pkt_version.bytes'
        if os.path.exists(filename) and os.path.isfile(filename):
            with open(filename,'r' ) as f:
                ret = json.loads(f.read())
                md5Values['pkt_table.bytes'] = ret['pkt_table.bytes']

        filename = FastNet.GetDataPath() + r'/client_version.bytes'
        if os.path.exists(filename) and os.path.isfile(filename):
            with open(filename,'r' ) as f:
                ret = json.loads(f.read())
                for k,v in ret.items():
                    md5Values[k] = v

        app.Server.SetMd5Values(json.dumps(md5Values))

def AppOnCreate():
    import pkt

    app = FastNet.App.Instance
    cfgApp = FastNet.JsonConfigs["App"]


    app.LogServer = None
    if 'LogServer' in FastNet.JsonConfigs:
        cfgLogServer = FastNet.JsonConfigs["LogServer"]
        app.LogServer = PubSubServer(0,False,'',LogSession)
        app.LogServer.BindMessage(pkt.protocols.LogQueryReq.sClsId,'OnLogQueryReq')
        app.LogServer.Start(cfgLogServer['address'],cfgLogServer['addressWan'])

    def OnUpdateSystemMemory():
        v = psutil.virtual_memory()
        p = psutil.Process(os.getpid())

        mi = p.memory_info()
        
        FastNet.App.Instance.UpdateSystemMemory(
            int(v.total),
            int(v.available),
            int(v.percent),
            int(v.used),
            int(v.free),
            int(mi.rss),
            int(mi.vms),
            float(p.memory_percent()),
            float(p.cpu_percent(None))
            )

    app._timerUpdateSystemMemory = None
    if cfgApp.get('monitorSystemResource',None) == True:
        app._OnUpdateSystemMemory = OnUpdateSystemMemory
        app._timerUpdateSystemMemory = FastNet.App.Instance.CreateTimer(app,'_OnUpdateSystemMemory')
        app._timerUpdateSystemMemory.Start(60000,3000,-1)

    app._subscribeList = None

    if 'server' in cfgApp:
        server = cfgApp['server']

        sessionClass = PubSubSession
        if 'sessionModule' in server and 'sessionClass' in server:
            m = importlib.import_module(server['sessionModule'])
            sessionClass = eval('m.{}'.format(server['sessionClass']))

        if 'subscribeKey' in server:
            app.SetServer(PubSubServer(server['id'],True,server['passwordCert'],sessionClass))
            app.Server.Start(server['address'],server['addressWan'])
            app.Server.SetSubscribeKey(server['subscribeKey'])
            app.Server.AllowSubPub(True)
        else:
            if server['enableSsl'] == True:
                app.SetServer(PubSubServer(server['id'],True,server['passwordCert'],sessionClass))
            else:
                app.SetServer(PubSubServer(server['id'],False,"",sessionClass))

            app.Server.Start(server['address'],server['addressWan'])


    AppUpdateMd5Values()

    app._mongodbServer = None
    if 'mongodbServer' in cfgApp and cfgApp['mongodbServer'] == True:

        app._mongodbPath = '{}/mongo_data_dir'.format(FastNet.GetWorkPath())
        if os.path.exists(app._mongodbPath) is False or os.path.isdir(app._mongodbPath) is False:
            os.mkdir(app._mongodbPath)

        app._mongodbServer = subprocess.Popen(
            r'mongod --port 27017 --dbpath {} --logpath mongo.log --logappend --bind_ip 127.0.0.1'.format(app._mongodbPath),
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE)


    if 'subscribeList' in cfgApp:
        app._subscribeList = {}
        app._subscribeIndex = 0
        app._subscribeIds = []
        for v in cfgApp['subscribeList']:
            c = PubSubClient()
            c.Connect(v['address'], 10000000, v['key'], v['id'], True);
            app.OnCreateSubscribeClient(c)
            app._subscribeList[v['id']] = c
            app._subscribeIds.append(v['id'])

    def GetValidSubscribeClient():
        app = FastNet.App.Instance
        _subscribeIndex = app._subscribeIndex
        subscribeIdCount = len(app._subscribeIds)
        while True:
            subscribeId = app._subscribeIds[_subscribeIndex]
            c = app._subscribeList.get(subscribeId,None)

            if c is not None and c.IsConnect is True:
                _subscribeIndex += 1
                if _subscribeIndex >= subscribeIdCount:
                    _subscribeIndex = 0

                app._subscribeIndex = _subscribeIndex
                return c
           
            if _subscribeIndex == app._subscribeIndex:
                return None

    def Publish(id,message,isPublic = False):
        
        c = GetValidSubscribeClient()
        if c is not None:
            c.Publish(int(id),message,isPublic)
        else:
            FastNet.LogError('App.Publish no valid subscribe client! %s' % message)

    app.Publish = Publish
    pass

def AppOnDestory():
    app = FastNet.App.Instance

    if app._timerUpdateSystemMemory is not None:
        app._timerUpdateSystemMemory.Stop()
        app._timerUpdateSystemMemory = None

    if app.Server is not None:
        app.Server.Stop()
        app.SetServer(None)

    if app.LogServer is not None:
        app.LogServer.Stop()
        app.LogServer = None
    
    if app._subscribeList is not None:
        for v in app._subscribeList.values():
            v.Close()

        del app._subscribeList

    if app._mongodbServer is not None:
        app._mongodbServer.terminate()
        app._mongodbServer.wait()
        del app._mongodbServer

def RunProcess(params):

    process = subprocess.Popen(['python',os.path.split(__file__)[0] + '/ChildProcess.py',params,os.path.split(FastNet.__file__)[0]])
    time.sleep(0.15)
         

    return process

def CheckProcess(process):
    status = process.poll()

    if status == None:
        return True
    else:
        return False


def UpdateCfg(param):
    try:  
        cfgDir = param['cfgDir']
        url_cfg = param['url_cfg']
        username_cfg = param['username_cfg']
        password_cfg = param['password_cfg']
        revision_cfg = param['revision_cfg']

        import svn.local,svn.remote

        if os.path.exists(cfgDir) is False:
            rc = svn.remote.RemoteClient(url_cfg,username=username_cfg,password=password_cfg)

            args = []
            args += ['--no-auth-cache']
            args += ['-r', str(revision_cfg)]
            args += [url_cfg, cfgDir]
            rc.run_command('checkout', args,return_binary = True)

        else:

            lc = svn.local.LocalClient(cfgDir)
            args = [url_cfg,cfgDir,'--ignore-ancestry']
            lc.run_command('switch', args,return_binary = True)

            args = [cfgDir,'--no-auth-cache']
            args += ['--username',username_cfg]
            args += ['--password',password_cfg]
            args += ['-r', str(revision_cfg)]
            args.insert(0,cfgDir)
            lc.run_command('update', args,return_binary = True)

    except Exception as e:
        FastNet.LogException('UpdateCfg ' + str(e))


def GetCode(port):
    accountVerify = \
'''
def AccountVerify(data):
    import requests,json

    jsonValue = json.dumps({'token':str(data['token']),'type':'server'})

    headers = {}
    headers['Content-Type'] = 'application/json'
    headers['Content-Length'] = str(len(jsonValue))

    ret = requests.post('http://127.0.0.1:%d/AccountVerify',data=jsonValue,headers=headers).json()
    if ret['status'] == 1:
        return {'status':1,'uid':ret['uid']}
    else:
        return {'status':0}
''' % port

    pay = \
'''
def PayNotice(handle):
    pass
'''
    return json.dumps({'accountVerify':accountVerify,'pay':pay})