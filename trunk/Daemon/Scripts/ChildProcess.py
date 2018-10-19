# -*- coding: utf-8 -*-
import FastNet
import sys,json, subprocess, signal, os, platform, shutil
import pkt,time
import cfg
import svn.remote
import svn.local
class ChildProcess(object):

    def __init__(self,data):
        super(ChildProcess, self).__init__()

        #self.cmd = data['cmd']
        
        self.url_code = None
        self.username_code = None
        self.password_code = None
        self.revision_code = None

        self.url_cfg = None
        self.username_cfg = None
        self.password_cfg = None
        self.revision_cfg = None

        self.serverId = 0

        self.codeDir = None
        self.workDir = None
        self.cfgDir = None


        self.process = None
        self.isStop = True
        self.isRepair = True

        self.projectName = ''

        self.cmd = None

        self.modifyServer(data)

    def DeleteDirs(self,dir):
        try:
            if os.path.exists(dir) is True:
                if platform.system() =="Windows":
                    os.system('rd /s /q {}'.format(dir))
                elif platform.system() == "Linux":
                    os.system('rm -r -f {}'.format(dir))
                else:
                    shutil.rmtree(dir)

        except Exception as e:
            FastNet.LogException('ChildProcess.DeleteDirs {} {}'.format(dir,e))

    def Delete(self):
        self.DeleteDirs(self.codeDir)
        self.DeleteDirs(self.workDir)
        self.DeleteDirs(self.cfgDir)

    @property
    def IsStop(self):
        return self.isStop
    
    def CheckAlive(self):

        if self.isStop is False:
            if self.process is None or self.process.poll() is not None:
                try:
                    self.process = subprocess.Popen(self.cmd,stdin = subprocess.DEVNULL, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
                    time.sleep(0.5)

                    if self.isRepair is True:
                        self.beginRepairServer()

                except Exception as e:
                    FastNet.LogException('ChildProcess.CheckAlive start child ' + str(e))
                    FastNet.App.Instance.PublishErrorMessage('启动服务器-{} 失败!'.format(self.serverId))

                    self.isStop = True

        return self.process is not None and self.process.poll() is None

    def _DoUpdateCode(self):

        try:

            if os.path.exists(self.codeDir) is False:
                rc = svn.remote.RemoteClient(self.url_code,username=self.username_code,password=self.password_code)

                args = []
                args += ['--no-auth-cache']
                args += ['-r', str(self.revision_code)]
                args += [self.url_code, self.codeDir]
                rc.run_command('checkout', args,return_binary = True)
            else:
                lc = svn.local.LocalClient(self.codeDir)
                args = [self.url_code,self.codeDir,'--ignore-ancestry']
                lc.run_command('switch', args,return_binary = True)

                args = [self.codeDir,'--no-auth-cache']
                args += ['--username',self.username_code]
                args += ['--password',self.password_code]
                args += ['-r', str(self.revision_code)]
                args.insert(0,self.codeDir)
                lc.run_command('update', args,return_binary = True)

        except Exception as e:
            FastNet.LogException('ChildProcess._DoUpdateCode ' + str(e))


    def modifyServer(self,data):

        try:

            self.serverId = data['id']

            self.codeDir = os.path.normpath(FastNet.GetWorkPath() + r'/childs/code/{}'.format(self.serverId))
            self.workDir = os.path.normpath(FastNet.GetWorkPath() + r'/childs/work/{}'.format(self.serverId))
            self.cfgDir = os.path.normpath(FastNet.GetWorkPath() + r'/childs/cfg/{}'.format(self.serverId))

            if os.path.exists(self.workDir) is False:
                os.makedirs(self.workDir)

            
            self.isStop = data['isstop']
            self.isRepair = data['repair']

            self.projectName = data['projectName']

            binFile = ""
            if FastNet.IsDebugMode() == True:
                binFile = '/Bin/{}d'.format(self.projectName)
            else:
                binFile = '/Bin/{}'.format(self.projectName)

            self.cmd = r"{}{} --wp={} --cp={} --sp={} --pn={} --lp={}".format    \
            (   \
                self.codeDir,
                binFile,
                self.workDir,
                self.cfgDir,
                self.codeDir,
                self.projectName,
                os.path.split(FastNet.__file__)[0]
            )

            shutil.copyfile(FastNet.GetWorkPath() + r'/server_{}.crt'.format(FastNet.App.Instance.GateId),
                self.workDir + r'/server_{}.crt'.format(FastNet.App.Instance.GateId))


            url_code = data['url_code']
            username_code = data['username_code']
            password_code = data['password_code']
            revision_code = data['revision_code']

            self.url_code = url_code
            self.username_code = username_code
            self.password_code = password_code
            self.revision_code = revision_code


            url_cfg = data['url_cfg']
            username_cfg = data['username_cfg']
            password_cfg = data['password_cfg']
            revision_cfg = data['revision_cfg']

            self.url_cfg = url_cfg
            self.username_cfg = username_cfg
            self.password_cfg = password_cfg
            self.revision_cfg = revision_cfg

            if url_cfg != self.url_cfg or revision_cfg == self.revision_cfg:
                #.self._DoUpdateCfg()

                params = {}
                params['cfgDir'] = self.cfgDir
                params['url_cfg'] = self.url_cfg
                params['username_cfg'] = self.username_cfg
                params['password_cfg'] = self.password_cfg
                params['revision_cfg'] = self.revision_cfg

                if self.isStop is False:
                    FastNet.App.Instance.Publish(self.serverId,json.dumps({'key':'updateCfg','param':params}))
                else:
                    import Helper
                    Helper.UpdateCfg(params)

                    #if platform.system() =="Windows":
                    #    shutil.copyfile(self.cfgDir + '/' + self.projectName + '.exe',self.workDir + '/' + self.projectName + '.exe')
                    #else:
                    #    shutil.copyfile(self.cfgDir + '/' + self.projectName,self.workDir + '/' + self.projectName)

                    self._DoUpdateCode()

            self.param = {}
            self.param['key'] = 'updateParam'
            #self.param['newEnterNoticeMail'] = data['newEnterNoticeMail']
            self.param['newEnterNoticeNum'] = data['newEnterNoticeNum']
            self.param['overflowPlayerNum'] = data['overflowPlayerNum']
            self.param['crowdingPlayerNum'] = data['crowdingPlayerNum']
            self.param['smoothPlayerPlayerNum'] = data['smoothPlayerPlayerNum']
            self.param['maxPlayerNum'] = data['maxPlayerNum']
            self.param['warningPlayerNum'] = data['warningPlayerNum']
            self.param['perMinuteEntryPlayerNum'] = data['perMinuteEntryPlayerNum']


            if self.isStop is False:
                FastNet.App.Instance.Publish(self.serverId,json.dumps(self.param))
  
            with open(r'{}/{}.cfg'.format(self.workDir,self.projectName), 'w') as f:
                f.write(data['startParam'])          

        except Exception as e:
            FastNet.LogException('ChildProcess.UpdateCfg ' + str(e))

    def startServer(self,val = None):
        if self.isStop is True:

            self.isStop = False

    def stopServer(self,val = None):
        if self.isStop is False:
            self.isStop = True

            if self.process is not None:

                FastNet.App.Instance.Publish(self.serverId,json.dumps({'key':'stop'}))
                try:
                    self.process.wait(30)
                except Exception as e:
                    pass

                if self.process.poll() is None:
                    self.process.kill()
                    FastNet.LogException('ChildProcess.stop kill serverId:' + self.serverId)


    def beginRepairServer(self,val = None):
        if self.isRepair is False:
            self.isRepair = True

            if self.isStop is False:
                FastNet.App.Instance.Publish(self.serverId,json.dumps({'key':'beginRepairServer','ips':val['ips']}))

    def endRepairServer(self,val = None):
        if self.isRepair is True:
            self.isRepair = False

            if self.isStop is False:
                FastNet.App.Instance.Publish(self.serverId,json.dumps({'key':'endRepair'}))
