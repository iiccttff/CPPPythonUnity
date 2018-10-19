# -*- coding: utf-8 -*-
import FastNet
import pkt
import json
import App
import globals.Global

class DataQuery(globals.Global.Global):
    def __init__(self):
        super(DataQuery,self).__init__('DataQuery')

    def SendInitData(self,role):

        mailMgrTabInfo = role.Tabs.get('MailMgr',None)
        if mailMgrTabInfo is None or mailMgrTabInfo[0] == False:
            return

        super(DataQuery,self).SendInitData(role)