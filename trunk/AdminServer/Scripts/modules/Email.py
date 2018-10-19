# -*- coding: utf-8 -*-
import FastNet
import sys,json
import pkt,time


class Email(FastNet.RoleModule):
    """description of class"""

    def __init__(self,name,role):

        self.emails = {}

        return super(Email, self).__init__(self,name,role)

    def __del__(self):
        print('Email.__del__',self.Role.Id)
    
    def OnRoleLogin(self):
        pass

    def OnRoleLogout(self):
        pass

    def OnRoleDisconnect(self):
        pass

    def OnRoleReconnect(self):
        pass

    def OnCache(self,sr):
        self.emails = sr.ReadDict('emails',self.emails);
        pass

    def OnFlush(self,sw):
        sw.WriteDict('emails',self.emails);
        pass