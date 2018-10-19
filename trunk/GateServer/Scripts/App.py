# -*- coding: utf-8 -*-
import FastNet
import cfg

class App(FastNet.App):
    def __init__(self):
        super(App, self).__init__(self)

        FastNet.LogDebug('App.__init__')

    def __del__(self):
        FastNet.LogDebug('App.__del__')
        pass

    def OnCreate(self):
        pass

    def OnDestory(self):
        pass

def Main(app):

	try:
	    app.Run()
	except Exception as e:
	    traceback.print_exc()