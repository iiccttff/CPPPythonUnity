# -*- coding: utf-8 -*-
import FastNet
import sys,json
import pkt,time
import cfg


class Session(FastNet.Session):
    def __init__(self,cp):
        super(Session, self).__init__(self,cp)

    def __del__(self):
        FastNet.LogNormal('Session.__del__ ')

    def OnCreate(self):
        FastNet.LogNormal('Session.OnCreate')

    def OnDestory(self):
    	FastNet.LogNormal('Session.OnDestory')