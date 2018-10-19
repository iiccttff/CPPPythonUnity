# -*- coding: utf-8 -*-


import sys,getopt
import MainWindow
import GlobalObjs
import PyQt5


class App(PyQt5.QtWidgets.QApplication):

    def __init__(self):
        PyQt5.QtWidgets.QApplication.__init__(self,sys.argv)

    def __del__(self):
        print('App.__del__')
        pass

if __name__ == "__main__":

    #reload(sys)
    #sys.setdefaultencoding( "utf-8" )

    PyQt5.QtWidgets.QApplication.addLibraryPath("./PyQt5/Qt/plugins")

    def Usage():
        print(' --cpp_out|csharp_out|lua_out output folder')
        print(' --root protocol root folder,default current folder')
        print(' --help get help info')

    opts, args = getopt.getopt(sys.argv[1:], "",['cpp_out=','csharp_out=','lua_out=','root=','help','cmdmode'])
    cppOutDir = csharpOutDir = luaOutDir = None
    rootDir = './'
    cmdMode = False

    for op, value in opts:
        if op == '--cpp_out':
            cppOutDir = value
        elif op == '--csharp_out':
            csharpOutDir = value
        elif op == '--lua_out':
            luaOutDir = value
        elif op == '--root':
            rootDir = value
        elif op == '--help':
            Usage()
            sys.exit()
        elif op == '--cmdmode':
            cmdMode = True

    if cmdMode == True:
        try:
            import GenProto,json
            GenProto.Export(rootDir,cppOutDir,csharpOutDir,luaOutDir)

            if luaOutDir is not None:
                versions = {}
                versions['pkt_table.bytes'] = GenProto.Export.GetFileMd5(luaOutDir + '/pkt_table.bytes')

                with open(luaOutDir + '/pkt_version.bytes','w') as f:
                    f.write(json.dumps(versions))

        except Exception as e:
            import traceback
            for v in traceback.format_exc().splitlines():
                print(v)
    else:
        
        GlobalObjs.Init()
        app = App()

        mainWindow = MainWindow.MainWindow()
        mainWindow.show()
        
        GlobalObjs.SetValue('App', app)
        GlobalObjs.SetValue('MainWindow', mainWindow)

        app.exec_()
        app.deleteLater()

        mainWindow = None
        app = None

        GlobalObjs.Uninit()