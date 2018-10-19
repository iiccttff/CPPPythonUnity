# -*- coding: utf-8 -*-
import FastNet
import multiprocessing
import os,time,json
import threading,requests
import base64
import uuid,hashlib
import pymongo,urllib,inspect

from http.server import BaseHTTPRequestHandler,HTTPServer

class HttpServerRequestHandle(BaseHTTPRequestHandler):
    #def __init__(self, request, client_address, server):
    #    BaseHTTPRequestHandler.__init__(self,request, client_address, server)

    def ClientAccountVerify(self,username,password):
        status = 0
        token = ''
        ret = self.server.MongoClient.accounts.find_one({"account":username })
        if ret != None and ret['account'] == username and ret['password'] == password:
            status = 1;

            md5 = hashlib.md5()
            md5.update(str(uuid.uuid1()).encode('utf8'))
            token = md5.hexdigest()
            self.server.MongoClient.accountTokens.update_one({"uid":username },{'$set':{"uid":username, "token": token, "time":int(time.time())}},True)

        if status == 0:
            return {'status':0}
        else:
            return {'status':status,'token':token}

    def ServerAccountVerify(self,token):

        status = 0
        uid = ''
        retAccountTokens = self.server.MongoClient.accountTokens.find_one({"token":token})
        if retAccountTokens != None:
            now = int(time.time())
            uid = retAccountTokens['uid']
            if retAccountTokens["time"] + 300 > now:	
                retAccounts = self.server.MongoClient.accounts.find_one({"account":uid })
                if retAccounts != None and retAccounts['account'] == uid:
                    self.server.MongoClient.accountTokens.delete_one({"token":token})
                    status = 1

        if status == 1:
            return {'status':status,'uid':uid}
        else:
            return {'status':0}

    def SendResponse(self,message):
        
        value = json.dumps(message)
        self.send_response(200)
        self.send_header('Content-Length',len(value) )
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(value,'utf8'))

    def AccountVerifyReq(self,data):
        channel = data['channel']
        ret = self.server.ChannelCodes.get(channel,None)
        if ret != None:
            try:
                print(json.loads(data['data']))

                self.SendResponse(ret[0](json.loads(data['data'])))
            except Exception as e:
                self.SendResponse({'status':0,'message':str(e)})
        else:
            self.SendResponse({'status':0,'message':"no find channel:{}".format(channel)})

        
    def do_POST(self):

        if self.path == '/PutChannelCode':
            data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            if data['token'] == self.server.Token:
                self.server.PutChannelCode(data)
            self.SendResponse({'status':1})

        elif self.path == '/AccountVerifyReq':
            data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            if data['token'] == self.server.Token:
                self.AccountVerifyReq(data)
            else:
                self.SendResponse({'status':0,'message':'token error'})
        elif self.path == '/AccountVerify':
            ret = {'status':0}
            contentLength = int(self.headers['Content-Length'])
            contentType = self.headers['Content-Type']

            if contentLength > 0 and contentType == 'application/json':
                data = json.loads(self.rfile.read(contentLength))

                type = data.get("type", "")
                if "server" == type:
                    ret = self.ServerAccountVerify(data['token'])
                elif "client" == type:
                    ret = self.ClientAccountVerify(data['username'],data['password'])
            
            self.SendResponse(ret)
        elif len(self.path) > 11 and self.path[0:11] == '/PayNotice/':
            self.server.PayNoticeReq(self.path[11:],self)
        else:
            self.SendResponse({'status':0})

class HttpServer(HTTPServer):
    def __init__(self, value):
        server_address = ('0.0.0.0', value['port'])
        self.mongoClient = pymongo.MongoClient(value['mongodbUri'])
        self.mongodbDB = value['mongodbDB']
        self.token = value['token']
        self.channelCodes = {}
        HTTPServer.__init__(self,server_address, HttpServerRequestHandle)

    @property
    def ChannelCodes(self):
        return self.channelCodes

    @property
    def MongoClient(self):
        return eval("self.mongoClient.{0}".format(self.mongodbDB))

    def PutChannelCode(self,data):
        code = json.loads(base64.b64decode(data['code']))

        execLocals = {}
        exec(code['accountVerify'],execLocals)
        accountVerifyCode = execLocals['AccountVerify']

        execLocals = {}
        exec(code['pay'],execLocals)
        payNotice = execLocals['PayNotice']

        if inspect.isfunction(accountVerifyCode) and inspect.isfunction(payNotice):
            self.channelCodes[data['channel']] = (accountVerifyCode,payNotice)

    @property
    def Token(self):
        return self.token

    def PayNoticeReq(self,channel,handle):
        ret = self.channelCodes.get(channel,None)
        if ret != None:
            try:
                ret[1](handle)
            except Exception as e:
                pass