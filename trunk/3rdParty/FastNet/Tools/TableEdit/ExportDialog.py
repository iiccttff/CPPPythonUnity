from PyQt5 import QtCore, QtGui, QtWidgets
import os,GenProto,traceback
from PyQt5.QtCore import (QAbstractItemModel, QFileInfo, QItemSelectionModel,
        QModelIndex, Qt)

from PyQt5.QtGui import QStandardItemModel,QStandardItem
import struct,time,hashlib
import GlobalObjs,MainWindow,json,GridTableView
import PyQt5.uic



class ExportClass(object):
    def __init__(self,clsName):
        self.clsName=clsName
        self.members=[]
        self.isExistsOtherType = None
        self.memberKeys=set()

    @property
    def ClsName(self):
        return self.clsName

    def WriteToFile(self,f):

        f.write('\n\n')
        f.write('class {}(Struct):\n'.format(self.clsName))

        for vv in self.members:
            f.write('\t{} = {}\n'.format(vv[0],vv[1]))

        f.write('\tpass\n')

    def AddMember(self,n,t):
        self.memberKeys.add(t)
        self.members.append((n,t))

    @property
    def IsExistsOtherType(self):
        if self.isExistsOtherType is None:
            self.isExistsOtherType = False
            for v in self.members:
                if v[1] not in GridTableView.GridTableView.BasicTypes:
                    self.isExistsOtherType = True
                    break

        return self.isExistsOtherType

    @staticmethod
    def Cmp(l, r):
        if r.ClsName in l.memberKeys:
            return False

        return True

    @staticmethod
    def Sorted(l):
        size = len(l)
        for i in range(0,size):
            for j in range(0,size):
                x = l[i]
                y = l[j]
                if x == y:
                    continue

                ret = ExportClass.Cmp(x,y)
                if ret == True:
                    l[i] = y
                    l[j] = x
        return l

class ExportDialog(QtWidgets.QDialog):
    def __init__(self,parent):
        super(ExportDialog, self).__init__(parent)
        #self.setupUi(self)
        PyQt5.uic.loadUi("ExportDialog.ui",self)

        historyPaths = parent.Settings.get('CppHistoryPaths',None)
        if historyPaths != None:
            ll = list(historyPaths)
            for v in ll:
                if os.path.exists(v) == False or os.path.isdir(v) == False:
                    historyPaths.remove(v)
                else:
                    self.comboBoxCpp.addItem(v) 

        historyPaths = parent.Settings.get('CSharpHistoryPaths',None)
        if historyPaths != None:
            ll = list(historyPaths)
            for v in ll:
                if os.path.exists(v) == False or os.path.isdir(v) == False:
                    historyPaths.remove(v)
                else:
                    self.comboBoxCSharp.addItem(v) 

        historyPaths = parent.Settings.get('DataHistoryPaths',None)
        if historyPaths != None:
            ll = list(historyPaths)
            for v in ll:
                if os.path.exists(v) == False or os.path.isdir(v) == False:
                    historyPaths.remove(v)
                else:
                    self.comboBoxData.addItem(v)

        historyPaths = parent.Settings.get('LuaHistoryPaths',None)
        if historyPaths != None:
            ll = list(historyPaths)
            for v in ll:
                if os.path.exists(v) == False or os.path.isdir(v) == False:
                    historyPaths.remove(v)
                else:
                    self.comboBoxLua.addItem(v)

    def GetCppPath(self):
        path = self.comboBoxCpp.currentText()
        if os.path.exists(path) and os.path.isdir(path):
            return path
        else:
            return None
    
    def GetLuaPath(self):
        path = self.comboBoxLua.currentText()
        if os.path.exists(path) and os.path.isdir(path):
            return path
        else:
            return None

    def GetCSharpPath(self):
        path = self.comboBoxCSharp.currentText()
        if os.path.exists(path) and os.path.isdir(path):
            return path
        else:
            return None

    def GetFolder(self,defaultPath):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self,'',defaultPath)
        if folder != None and len(folder) > 0 and os.path.exists(folder) == True and os.path.isdir(folder) == True:
            return folder
        else:
            return ''

    def RemoveDirs(self,dir):
        if os.path.isdir(dir) == True:
            for p in os.listdir(dir):
                self.RemoveDirs(os.path.join(dir,p))
            os.rmdir(dir)
        elif os.path.isfile(dir) == True and os.path.exists(dir) == True:
            os.remove(dir)

    def CalcStringCrc(self, s):
        import binascii
        result = '0x%x' % (binascii.crc32(s.encode('utf8')) & 0xffffffff)    
        return int(result,16)

    def WriteData(self,path,model,export,relpath,indexs):
        with open(path,'wb') as f:

            classMembers,cfgCodeVersion = export.AllClassMembers[relpath]
            cfgDataVersion = 0

            f.write(struct.pack('1I',cfgCodeVersion))
            f.write(struct.pack('1I',cfgDataVersion))
            f.write(struct.pack('1I',model.rowCount()-2))
            
            m = hashlib.md5()
            m.update(str((model.rowCount()-2)*model.columnCount()).encode('utf8'))

            indexValues = []
            indexType = 'UInt32'
            if model.activeColumn != -1:
                indexType = model.data(model.index(0,model.activeColumn))
                for j in range(2,model.rowCount()):
                    indexValues.append(model.data(model.index(j,model.activeColumn)))
            else:
                for j in range(2,model.rowCount()):
                    indexValues.append(0)
            
            for v in indexValues:
                if indexType == 'UInt8':
                    f.write(struct.pack('1B',int(v)))
                elif indexType == 'UInt16':
                    f.write(struct.pack('1H',int(v)))
                elif indexType == 'UInt32':
                    f.write(struct.pack('1I',int(v)))
                elif indexType == 'UInt64':
                    f.write(struct.pack('1Q',int(v)))
                elif indexType == 'Int8':
                    f.write(struct.pack('1b',int(v)))
                elif indexType == 'Int16':
                    f.write(struct.pack('1h',int(v)))
                elif indexType == 'Int32':
                    f.write(struct.pack('1i',int(v)))
                elif indexType == 'Int64':
                    f.write(struct.pack('1q',int(v)))
                elif indexType == 'Bool':
                    f.write(struct.pack('1?',int(v)))
                elif indexType == 'Float':
                    f.write(struct.pack('1f',float(v)))
                elif indexType == 'Double':
                    f.write(struct.pack('1d',float(v)))
                elif indexType == 'String':
                    #f.write(struct.pack('1I',len(v)))
                    #for s in v:
                    #    f.write(struct.pack('1c',bytes(s,'utf8')))
                    v = str(v).encode('utf8')
                    f.write(struct.pack('1I',len(v)))
                    f.write(struct.pack('{}s'.format(len(v)),v))
                else:
                    assert(False)

            for i in range(2,model.rowCount()):
                values = {}
                for j in range(0,model.columnCount()):
                    values[model.headerData(j,Qt.Horizontal)] = (model.data(model.index(i,j)),model.data(model.index(0,j)))

                for v in classMembers:
                    value,typename = values[v]
                    
                    if value == '' or value is None:
                        if typename != 'String':
                            value = '0'
                        else:
                            value = ''
                    else:
                        m.update(value.encode('utf8'))

                    if typename not in GridTableView.GridTableView.BasicTypes:
                        typename = indexs[typename]

                    if typename == 'UInt8':
                        f.write(struct.pack('1B',int(value)))
                    elif typename == 'UInt16':
                        f.write(struct.pack('1H',int(value)))
                    elif typename == 'UInt32':
                        f.write(struct.pack('1I',int(value)))
                    elif typename == 'UInt64':
                        f.write(struct.pack('1Q',int(value)))
                    elif typename == 'Int8':
                        f.write(struct.pack('1b',int(value)))
                    elif typename == 'Int16':
                        f.write(struct.pack('1h',int(value)))
                    elif typename == 'Int32':
                        f.write(struct.pack('1i',int(value)))
                    elif typename == 'Int64':
                        f.write(struct.pack('1q',int(value)))
                    elif typename == 'Bool':
                        f.write(struct.pack('1?',int(value)))
                    elif typename == 'Float':
                        f.write(struct.pack('1f',float(value)))
                    elif typename == 'Double':
                        f.write(struct.pack('1d',float(value)))
                    elif typename == 'String':
                        value = str(value).encode('utf8')

                        f.write(struct.pack('1I',len(value)))
                        f.write(struct.pack('{}s'.format(len(value)),value))

                        #for s in bytes(value,'utf8'):
                        #    print(s,type(s))
                        #    f.write(struct.pack('1s',s))
                    else:
                        assert(False)

            cfgDataVersion = self.CalcStringCrc(m.hexdigest())

            f.seek(4)
            f.write(struct.pack('1I',cfgDataVersion))

    def OnExport(self):

        if os.path.exists(self.comboBoxCpp.currentText()) == False or os.path.isdir(self.comboBoxCpp.currentText()) == False:
            QtWidgets.QMessageBox.critical(self,'Error','Cpp input path error!')
        elif os.path.exists(self.comboBoxCSharp.currentText()) == False or os.path.isdir(self.comboBoxCSharp.currentText()) == False:
            QtWidgets.QMessageBox.critical(self,'Error','CSharp input path error!')
        elif os.path.exists(self.comboBoxData.currentText()) == False or os.path.isdir(self.comboBoxData.currentText()) == False:
            QtWidgets.QMessageBox.critical(self,'Error','Data input path error!')
        else:
            self.parent().Settings['CppHistoryPaths'] = self.AddItem(self.comboBoxCpp,self.comboBoxCpp.currentText())
            self.parent().Settings['CSharpHistoryPaths'] = self.AddItem(self.comboBoxCSharp,self.comboBoxCSharp.currentText())
            self.parent().Settings['DataHistoryPaths'] = self.AddItem(self.comboBoxData,self.comboBoxData.currentText())
            self.parent().Settings['LuaHistoryPaths'] = self.AddItem(self.comboBoxLua,self.comboBoxLua.currentText())
            try:
                temp = os.path.join(os.getcwd(),'temp')
                
                gMainWindow = GlobalObjs.GetValue('MainWindow')

                if os.path.exists(temp) == True and os.path.isdir(temp) == True:
                    try:
                        self.RemoveDirs(temp)
                    except Exception as e: 
                        pass

                if os.path.exists(temp) == False or os.path.isdir(temp) == False:
                    os.mkdir(temp)

                dataPath = self.comboBoxData.currentText() + '/cfg/'

                def LoadModels(item,indexs):

                    for i in range(0,item.rowCount()):
                        childItem = item.child(i,0)
                        if childItem.data() == 2 or childItem.data() == 1:
  
                            k = gMainWindow.GetTreeItemShortPath(childItem)
                            paths = k.split('.')
                            path = '/'.join(paths)
                            paths.pop()
                            basepath = '/'.join(paths)
                            currentPath = path

                            path = os.path.join(temp,path)
                            basepath = os.path.join(temp,basepath)
                            

                            if os.path.exists(basepath) == False or os.path.isdir(basepath) == False:
                                os.mkdir(basepath)
                                with open(basepath + os.sep + '__init__.py','w') as f:
                                    f.write('# -*- coding: utf-8 -*-\n')

                            if childItem.data() == 1:
                                LoadModels(childItem,indexs)
                                continue

                            with open(path+'.py','w') as f:
                                f.write('# -*- coding: utf-8 -*-\n')
                                f.write('from GenProto import *\n\n')

                                imports = set()

                                for i in range(0,childItem.rowCount()):
                                    tableItem = childItem.child(i,0)
                                    model = tableItem.data(QtCore.Qt.UserRole+2)
                                    indexs[k + '.' + tableItem.text()] = 'UInt32'

                                    for j in range(0,model.columnCount()):
                                        
                                        itemType = model.index(0,j).data()
                                        if j == model.activeColumn:
                                            indexs[k + '.' + tableItem.text()] = itemType

                                        if itemType not in GridTableView.GridTableView.BasicTypes:

                                            itemTypes = itemType.split('.')
                                            itemTypes.pop()
                                            itemType = '.'.join(itemTypes)

                                            if currentPath != itemType.replace('.','/') and itemType not in imports:
                                                print(currentPath,itemType)
                                                imports.add(itemType)
                                                f.write('import {}\n'.format(itemType))
                                
                                classList = []
                                for i in range(0,childItem.rowCount()):
                                    tableItem = childItem.child(i,0)
                                    model = tableItem.data(QtCore.Qt.UserRole+2)
                                    
                                    classMembers = ExportClass(tableItem.text())
                                    #f.write('\n\n')
                                    #f.write('class {}(Struct):\n'.format(tableItem.text()))
                                    for j in range(0,model.columnCount()):
                                        itemName = model.headerData(j,Qt.Horizontal)
                                        itemType = model.index(0,j).data()
                                        if itemType in GridTableView.GridTableView.BasicTypes:
                                            #f.write('\t{} = {}\n'.format(itemName,itemType))
                                            classMembers.AddMember(itemName,itemType)
                                        else:
                                            itemTypes = itemType.split('.')
                                            itemTypeNew = itemTypes[-1]
                                            itemTypes.pop()
                                            
                                            if currentPath == '/'.join(itemTypes):
                                                classMembers.AddMember(itemName,itemTypeNew)
                                                #f.write('\t{} = {}\n'.format(itemName,itemTypeNew))
                                            else:
                                                #f.write('\t{} = {}\n'.format(itemName,itemType))
                                                classMembers.AddMember(itemName,itemType)

                                    #f.write('\tpass\n')
                                    classList.append(classMembers)
    
                                for v in ExportClass.Sorted(classList):
                                    v.WriteToFile(f)

                indexs = {}
                LoadModels(gMainWindow.TreeRootItem,indexs)

                versions = {}
                export = GenProto.Export(temp,self.GetCppPath(),self.GetCSharpPath(),self.GetLuaPath(),'cfg',indexs)

                def WriteDatas(item,versions):
                           
                    for i in range(0,item.rowCount()):
                        childItem = item.child(i,0)
                        if childItem.data() == 2 or childItem.data() == 1:
  
                            k = gMainWindow.GetTreeItemShortPath(childItem)
                            paths = k.split('.')
                            path = '/'.join(paths)
                            bytesPath = os.path.join(dataPath,path)

                            if os.path.exists(bytesPath) == False or os.path.isdir(bytesPath) == False:
                                os.makedirs(bytesPath)

                            if childItem.data() == 1:
                                WriteDatas(childItem,versions)
                                continue

                            for i in range(0,childItem.rowCount()):
                                tableItem = childItem.child(i,0)
                                model = tableItem.data(QtCore.Qt.UserRole+2)

                                filePath = bytesPath + '/' + tableItem.text() + '.bytes'
                                self.WriteData(filePath,model,export,k + '.' + tableItem.text(),indexs)
                                versions['cfg/' + path + '/' + tableItem.text() + '.bytes'] = GenProto.Export.GetFileMd5(filePath)

                versions = {}
                WriteDatas(gMainWindow.TreeRootItem,versions)

                versions['cfg_table.bytes'] = GenProto.Export.GetFileMd5(self.comboBoxData.currentText() + '/cfg_table.bytes')

                if self.GetLuaPath() is not None:
                    with open(self.comboBoxData.currentText() + '/cfg_version.bytes','w') as f:
                        f.write(json.dumps(versions))

            except Exception as e:  
                QtWidgets.QMessageBox.critical(self,'Error',str(traceback.format_exc().splitlines()))

            self.done(QtWidgets.QDialog.Accepted)

    def AddItem(self,obj,s):
        

        paths = []
        for i in range(0,obj.count()):
            
            if s == obj.itemText(i):
                obj.removeItem(i)
                continue

            #paths.append(obj.itemText(i))
        
        obj.insertItem(0,s)

        for i in range(0,obj.count()):
            paths.append(obj.itemText(i))

        #paths.append(s)
        #paths.reverse()

        obj.setCurrentText(s)

        return paths

    def OnCppBrowse(self):
        s = self.GetFolder(self.comboBoxCpp.currentText())
        if s != '':
            self.comboBoxCpp.setCurrentText(s)

    def OnCSharpBrowse(self):
        s = self.GetFolder(self.comboBoxCSharp.currentText())
        if s != '':
            self.comboBoxCSharp.setCurrentText(s)

    def OnDataBrowse(self):
        s = self.GetFolder(self.comboBoxData.currentText())
        if s != '':
            self.comboBoxData.setCurrentText(s)

    def OnLuaBrowse(self):
        s = self.GetFolder(self.comboBoxLua.currentText())
        if s != '':
            self.comboBoxLua.setCurrentText(s)