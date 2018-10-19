#coding:utf-8
import sys,os,getopt,types,random,imp
#from inspect import getmembers
import importlib,hashlib
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
importlib.reload(sys)

class Enum:
    __clsname__ = 'Enum'
    __clscode__ = 1
    __defaultVal__ = 0
        
    def __init__(self,val):
        Enum.__defaultVal__ = val
        self.__name__ = self.__class__.__name__

class Struct:
    __clsname__ = 'Struct'
    __clscode__ = 2

class Message:
    __clsname__ = 'Message'
    __clscode__ = 3
    
class Buffer:
    __clsname__ = 'Buffer'
    __clscode__ = 4
    __defaultVal__ = False

    def __init__(self,val):
        self.__defaultVal__ = val
        self.__name__ = self.__class__.__name__

class Bool:
    __clsname__ = 'Bool'
    __clscode__ = 4
    __defaultVal__ = False
        
    def __init__(self,val):
        self.__defaultVal__ = val
        self.__name__ = self.__class__.__name__

class UInt8:
    __clsname__ = 'UInt8'
    __clscode__ = 4
    __defaultVal__ = 0

    def __init__(self,val):
        self.__defaultVal__ = val
        self.__name__ = self.__class__.__name__

class UInt16:
    __clsname__ = 'UInt16'
    __clscode__ = 4
    __defaultVal__ = 0

    def __init__(self,val):
        self.__defaultVal__ = val
        self.__name__ = self.__class__.__name__

class UInt32:
    __clsname__ = 'UInt32'
    __clscode__ = 4
    __defaultVal__ = 0

    def __init__(self,val):
        self.__defaultVal__ = val
        self.__name__ = self.__class__.__name__

class UInt64:
    __clsname__ = 'UInt64'
    __clscode__ = 4
    __defaultVal__ = 0

    def __init__(self,val):
        self.__defaultVal__ = val
        self.__name__ = self.__class__.__name__

class Int8:
    __clsname__ = 'Int8'
    __clscode__ = 4
    __defaultVal__ = 0

    def __init__(self,val):
        self.__defaultVal__ = val
        self.__name__ = self.__class__.__name__

class Int16:
    __clsname__ = 'Int16'
    __clscode__ = 4
    __defaultVal__ = 0

    def __init__(self,val):
        self.__defaultVal__ = val
        self.__name__ = self.__class__.__name__

class Int32:
    __clsname__ = 'Int32'
    __clscode__ = 4
    __defaultVal__ = 0

    def __init__(self,val):
        self.__defaultVal__ = val
        self.__name__ = self.__class__.__name__

class Int64:
    __clsname__ = 'Int64'
    __clscode__ = 4
    __defaultVal__ = 0

    def __init__(self,val = 0):
        self.__defaultVal__ = val
        self.__name__ = self.__class__.__name__

class Float:
    __clsname__ = 'Float'
    __clscode__ = 4
    __defaultVal__ = '0.0f'

    def __init__(self,val):
        self.__defaultVal__ = val
        self.__name__ = self.__class__.__name__

class Double:
    __clsname__ = 'Double'
    __clscode__ = 4
    __defaultVal__ = 0.0

    def __init__(self,val):
        self.__defaultVal__ = val
        self.__name__ = self.__class__.__name__

class String:
    __clsname__ = 'String'
    __clscode__ = 4
    __defaultVal__ = ""

    def __init__(self,val):
        self.__defaultVal__ = val
        self.__name__ = self.__class__.__name__

class Export:

    def GetMainModuleName(self):
        mod = sys.modules['__main__']
        file = getattr(mod, '__file__', None)
        return file and os.path.splitext(os.path.basename(file))[0] 

    def IsDependent(self,t1,t2):
        if t1.__clscode__ == 1 or  t1.__clscode__ == 4:
            return False

        if t1 == t2:
            return True
                
        members = dir(t1)
        for m in members:

            if m == '__doc__' or m == '__module__' or m == '__clsname__' or m == '__clscode__':
                continue

            TMember = getattr(t1, m)
            if hasattr(TMember,'__name__') and TMember.__name__ == m:
                continue

            if isinstance(TMember,list):
                if len(TMember) == 1:
                    if self.IsDependent(TMember[0],t2):
                        return True
                elif len(TMember) == 2:
                    if self.IsDependent(TMember[0],t2) or self.IsDependent(TMember[1],t2):
                        return True
                else:
                    assert(False)
            else:
                if t2 == TMember:
                    
                    return True

        return False

    def IsDependentExt(self,t1,code):
        ret = False
        if t1.__clscode__ == 4:
            return False

        members = dir(t1)
        for m in members:

            if m == '__doc__' or m == '__module__' or m == '__clsname__' or m == '__clscode__':
                continue
            
            TMember = getattr(t1, m)
            if hasattr(TMember,'__name__') and TMember.__name__ == m:
                continue

            if isinstance(TMember,list):
                if len(TMember) == 1:
                    if TMember[0].__clscode__ == code or self.IsDependentExt(TMember[0],code):
                        ret = True
                        break
                elif len(TMember) == 2:
                    if TMember[0].__clscode__ == code or self.IsDependentExt(TMember[0],code) or TMember[1].__clscode__ == code or self.IsDependentExt(TMember[1],code):
                        ret = True
                        break
                else:
                    #
                    print('TMember == ',TMember,code)
                    assert(False)
            else:    
                if hasattr(TMember,'__clscode__') and code == TMember.__clscode__:
                    ret = True
                    break

        return ret

    def ReversedCmp(self,t1, t2):
        t1code = t2code = None
        if hasattr(t1,'__clscode__'):
            t1code = getattr(t1,'__clscode__')

        if hasattr(t2,'__clscode__'):
            t2code = getattr(t2,'__clscode__')

        assert(t1code != None and t2code != None)
        assert(t1code != 4 and t2code != 4)

        if t1code == 1:
            if t2code == 1:
                return 0
            else:
                return -1;
        elif t1code == 2:
            if t2code == 1:
                return 1
            elif t2code == 3:
                return -1
        elif t1code == 3:
            if t2code == 1 or t2code == 2:
                return 1

        if (self.IsDependent(t1,t2) == True):
            return 1
        elif (self.IsDependent(t2,t1) == True):
            return -1
        else:
            return 0

    def CalcStringCrc(self, s):
        import binascii
        result = "0x%x" % (binascii.crc32(bytearray(s.encode('utf8'))) & 0xffffffff)    
        return int(result,16)

    def CalcMessageSign(self,t,module):
        stringVal = ""
        for m in vars(t):
            if m == '__doc__' or m == '__module__':
                continue
            
            TMember = getattr(t, m)
            if hasattr(TMember,'__name__') and TMember.__name__ == m:
                continue

            stringVal += self.GetType_Cpp(TMember,module,True)
        
        return self.CalcStringCrc(stringVal)

    def ErrorCheck(self,t,allowScope = True):
        for m in vars(t):
            if m == '__doc__' or m == '__module__':
                continue

            TMember = getattr(t, m)
            if hasattr(TMember,'__name__') and TMember.__name__ == m:
                if allowScope == False:
                    if t.__clscode__ == 1:
                        print('\'Enum:{}\' not allowed nesting!'.format(t.__name__,m))
                    elif t.__clscode__ == 2:
                        print('\'Struct:{}\' not allowed multiple nesting!'.format(t.__name__))
                    elif t.__clscode__ == 3:
                        print('\'Message:{}\' not allowed multiple nesting!'.format(t.__name__))
                    return True
                continue

            isMessageDependent = self.IsDependentExt(t,Message.__clscode__)
            isStructDependent = self.IsDependentExt(t,Struct.__clscode__)
            isEnumDependent = self.IsDependentExt(t,Enum.__clscode__)
            
            if t.__clscode__ == 1:
                if isMessageDependent == True or isStructDependent == True or isEnumDependent == True:
                    print('\'Enum:{}\' only include int number:{}!'.format(t.__name__,m))
                    return True
            elif t.__clscode__ == 2:
                if isMessageDependent == True:
                    print('\'Struct:{}\' cannot include \'Message:{}\'!'.format(t.__name__,m))
                    return True
            elif t.__clscode__ == 3:
                if isMessageDependent == True:
                    print('\'Message:{}\' cannot include \'Message:{}\'!'.format(t.__name__,m))
                    return True
        return False

    def GetType_Cpp(self,t,module,expandStruct = False,csharp = False,score = None):
        if isinstance(t,list) == True:
            if len(t) == 1:
                if csharp == True:
                    return 'List<{}>'.format(self.GetType_Cpp(t[0],module,expandStruct,csharp))
                else:
                    return 'std::vector<{}>'.format(self.GetType_Cpp(t[0],module,expandStruct,csharp))
            else:
                if csharp == True:
                    return 'Dictionary<{},{}>'.format(self.GetType_Cpp(t[0],module,expandStruct,csharp),self.GetType_Cpp(t[1],module,expandStruct,csharp))
                else:
                    return 'std::map<{},{}>'.format(self.GetType_Cpp(t[0],module,expandStruct,csharp),self.GetType_Cpp(t[1],module,expandStruct,csharp))
        else:
            
            if expandStruct == True and hasattr(t,'__clscode__') and (t.__clscode__ == 2 or t.__clscode__ == 3):
                stringVal = ""
                for m in vars(t):
                    if m == '__doc__' or m == '__module__':
                        continue

                    stringVal += self.GetType_Cpp(getattr(t, m),module,expandStruct,csharp)
                return stringVal
            else:
                if module != t.__module__ and t.__module__ != 'GenProto':
                    if t.__module__.find('.') != -1:
                        namespaces = os.path.split(t.__module__.replace(".", os.sep))
                    else:
                        namespaces = [t.__module__]

                    if csharp == True: 
                        namespace = self.pkt + '.'
                    else:
                        namespace = self.pkt + '::'
                    for n in range(0,len(namespaces)):
                        if csharp == True: 
                            namespace += namespaces[n] + '.';
                        else:
                            namespace += namespaces[n] + '::';

                    if score != None and csharp == True:
                        namespace += score + '.'

                    return namespace + t.__name__
                else:
                    return t.__name__

    def Export_CSharp(self,inputFile,exportTypes,modulename,outDir,namespaces):
        #print 'Export_CSharp:' + inputFile
        relpath = os.path.relpath(inputFile,self.rootDir).replace('.py','.cs')

        outfilename = outDir + os.sep + relpath
        outfilepath = os.path.dirname(outfilename)
        if os.path.isdir(outfilepath) == False:
             os.makedirs(outfilepath)

        stream = open(outfilename, 'w')

        stream.write('using System;\n')
        stream.write('using System.IO;\n')
        stream.write('using System.Collections.Generic;\n')
        stream.write('\n\n')

        #begin namespace
        stream.write('namespace {}{}\n'.format(self.pkt,'{'))
        if len(namespaces) > 0:
            for i in range(0,len(namespaces)):
                stream.write('namespace {}{}\n'.format(namespaces[i],'{'))
            stream.write('\n')
        else:
            stream.write('\n')

        stream.write('using UInt8 = Byte;\n')
        stream.write('using Int8 = SByte;\n')
        stream.write('using Float = Single;\n')
        stream.write('using Bool = Boolean;\n')

        #error check
        for t in exportTypes:
            if self.ErrorCheck(t):
                print('Error: gen csharp fail ' + relpath)
                return

        #gen enum
        for t in exportTypes:
            if t.__clscode__ == 1:
                self.WriteEnumDef_CSharp(stream,t,modulename)

        #gen struct
        for t in exportTypes:
            if t.__clscode__ == 2:

                if self.pkt == 'cfg':
                    self.indexType = 'UInt32'
                    self.indexType = self.indexs[modulename + '.' + t.__name__]

                if self.WriteStruct_CSharp(stream,t,modulename) == False:
                    print('Error: gen csharp fail ' + relpath)
                    return

        #gen message
        for t in exportTypes:
            if t.__clscode__ == 3:
                if self.WriteStruct_CSharp(stream,t,modulename) == False:
                    print('Error: gen csharp fail ' + relpath)
                    return    
    
        #end namespace
        if len(namespaces) > 0:
            for i in range(0,len(namespaces)):
                stream.write('{} //end namespace {}\n'.format('}',namespaces[i]))
        stream.write('{} //end namespace {}\n'.format('}',self.pkt))    

        print('Success: gen csharp ' + relpath)

    def Export_Lua(self,exportTypes,modulename):
        #print 'Export_CSharp:' + inputFile
            
        

        #error check
        for t in exportTypes:
            if self.ErrorCheck(t):
                print('Error: gen lua fail ' + modulename)
                return
        
        def ExportType(self,t,modulename,modulename_old):

            retValues = {}
            retValues['clsName'] = modulename + "." + t.__name__
            retValues['clsId'] = 0
            retValues['signId'] = 0
            retValues['type'] = ''
            if self.pkt == 'pkt':
                retValues['type'] = t.__clsname__
            
            retValues['index'] = ''

            if self.pkt == 'cfg':
                self.indexType = 'UInt32'
                self.indexType = self.indexs[modulename_old + '.' + t.__name__]
                retValues['index'] = self.indexType


            if t.__clscode__ == 2 or t.__clscode__ == 3:
                retValues['clsId'] = self.CalcStringCrc(modulename+'.' + t.__name__)
                retValues['signId'] = self.CalcMessageSign(t,modulename_old)
            
            attrs = []
            for m in vars(t):
                if m == '__doc__' or m == '__module__':
                    continue

                TMember = getattr(t, m)
                if hasattr(TMember,'__name__') == True and TMember.__name__ == m:
                    if self.ErrorCheck(TMember,False):
                        return False
                    ExportType(self,TMember,modulename + "." + t.__name__,modulename_old)
                else:
                    attr = {}
                    attr['name'] = m

                    if t.__clscode__ == 1:
                        attr['type'] = ''
                        attr['value'] = str(TMember)
                    else:
                        scoreMessage = None
                        if hasattr(TMember,'__name__') == True and hasattr(t,TMember.__name__) == True:
                            
                            tttt = eval('t.{}'.format(TMember.__name__))
                            if tttt == TMember:
                                scoreMessage = t.__name__

                        if hasattr(TMember,"__clscode__") and TMember.__clscode__ != 2 and TMember.__clscode__ != 3:
                            attr['type'] = self.GetType_Cpp(TMember,modulename,False,True,scoreMessage)
                            attr['value'] = str(TMember.__defaultVal__)
                        else:
                            attr['type'] = self.GetType_Cpp(TMember,modulename,False,True,scoreMessage)
                            attr['value'] = ''
                    attrs.append(attr)
            retValues['attrs'] = attrs
            
            
            if self.pkt == 'cfg':
                retValues['cfgPath'] = '/{}/{}.bytes'.format(modulename.replace('.','/'),t.__name__)
            else:
                retValues['cfgPath'] = ''

            self.luaJsonValues.append(retValues)

        for t in exportTypes:
            ExportType(self,t,self.pkt + "." + modulename,modulename)
        
    
        print('Success: gen lua ' + modulename)

    def WriteEnumDef_CSharp(self,stream,t,modulename,scope = 1):
        tabnum = scope*'\t'

        members = []
        for m in vars(t):
            if m == '__doc__' or m == '__module__':
                continue
            members.append(m)    

        stream.write('{}public enum {}:int {}\n'.format(tabnum,t.__name__,'{'))
        for m in members:
            stream.write('{}\t{} = {},\n'.format(tabnum,m,getattr(t,m)))
        stream.write('{}{}\n\n'.format(tabnum,'}'))

    def WriteEnumDef_Cpp(self,stream,t,modulename,scope = 1):
        tabnum = scope*'\t'

        members = []
        for m in vars(t):
            if m == '__doc__' or m == '__module__':
                continue
            members.append(m)    

        stream.write('{}enum class {}:FastNet::Int32 {}\n'.format(tabnum,t.__name__,'{'))
        for m in members:
            stream.write('{}\t{} = {},\n'.format(tabnum,m,getattr(t,m)))
        stream.write('{}{};\n\n'.format(tabnum,'}'))

    def WriteEnumPythonDef_Cpp(self,stream,tabnum,t):
        stream.write('\t\t{0}boost::python::enum_<{1}> e_{1}("{1}");\n'.format(tabnum,t.__name__))
        for m in vars(t):
            if m == '__doc__' or m == '__module__':
                continue
            stream.write('\t\t{0}e_{2}.value("{1}", {2}::{1});\n'.format(tabnum,m,t.__name__))

    def GetTypeResetStr_Cpp(self,t,m,modulename):
        if isinstance(t,list) == True:
            if len(t) == 1 or len(t) == 2:
                return m + ".clear()"
            else:
                assert(False)
        elif t.__clscode__ == 2:
            return m + '.Reset()'
        elif t.__clscode__ == 3:
            return m + '.Reset()'
        else:
            if t.__clscode__ == 1:
                return m + "=({}){}".format(self.GetType_Cpp(t,modulename),t.__defaultVal__)
            elif t.__clsname__ == 'String':
                return m + "=\"" + str(t.__defaultVal__) + "\""
            else:
                if t.__clsname__ == 'Bool':
                    if t.__defaultVal__ == True:
                        return m + "=true"
                    else:
                        return m + "=false"
                else:        
                    return m + "=" + str(t.__defaultVal__)

    def GetTypeInitDefStr_Cpp(self,t,m,modulename):
        if isinstance(t,list) != True:
            if t.__clscode__ == 1:
                return m + "=({}){}".format(self.GetType_Cpp(t,modulename),t.__defaultVal__)
            elif t.__clsname__ == 'String':
                return m + "=\"" + str(t.__defaultVal__) + "\""
            elif t.__clscode__ == 4:
                if t.__clsname__ == 'Bool':
                    if t.__defaultVal__ == True:
                        return m + "=true"
                    else:
                        return m + "=false"
                else:        
                    return m + "=" + str(t.__defaultVal__)
        return m

    '''def GetTypeResetStr_CSharp(self,t,m,modulename):
        if isinstance(t,list) == True:
            if len(t) == 1 or len(t) == 2:
                return m + ".Clear()"
            else:
                assert(False)
        elif t.__clscode__ == 2 or t.__clscode__ == 3:
            return m + '.Reset()'
        else:
            if t.__clscode__ == 1:
                return m + "=({}){}".format(self.GetType_Cpp(t,modulename,False,True),t.__defaultVal__)
            elif t.__clsname__ == 'String':
                return m + "=\"" + str(t.__defaultVal__) + "\""
            else:
                if t.__clsname__ == 'Bool':
                    if t.__defaultVal__ == True:
                        return m + "=true"
                    else:
                        return m + "=false"
                else:        
                    return m + "=" + str(t.__defaultVal__)'''

    def GetTypeInitDefStr_CSharp(self,t,m,modulename):
        if isinstance(t,list) != True:
            if t.__clscode__ == 1:
                return m + "=({}){}".format(self.GetType_Cpp(t,modulename,False,True),t.__defaultVal__)
            elif t.__clsname__ == 'String':
                return m + "=\"" + str(t.__defaultVal__) + "\""
            elif t.__clscode__ == 4:
                if t.__clsname__ == 'Bool':
                    if t.__defaultVal__ == True:
                        return m + "=true"
                    else:
                        return m + "=false"
                else:        
                    return m + "=" + str(t.__defaultVal__)
            else:
                if self.pkt == 'pkt':
                    return m + "=new {}()".format(self.GetType_Cpp(t,modulename,False,True))
                else:
                    return m + "=null"
        else:
            return m + "=new {}()".format(self.GetType_Cpp(t,modulename,False,True))
        return m

    def WriteStructDef_Cpp(self,members,stream,t,modulename,scope = 1,parentName = ""):
        tabnum = scope*'\t'

        if scope == 2:
            if t.__clscode__ == 2:
                if self.pkt == 'cfg':
                    stream.write('{0}struct {1} final: FastNet::Struct<{1},{2}> {3}\n'.format(tabnum,t.__name__,self.indexType,'{'))
                else:
                    stream.write('{}struct {} final: FastNet::Struct {}\n'.format(tabnum,t.__name__,'{'))

                stream.write('{}\tbool operator==({} const& ) const {} return false; {}\n'.format(tabnum,t.__name__,'{','}'))
                stream.write('{}\tbool operator!=({} const& ) const {} return true; {}\n'.format(tabnum,t.__name__,'{','}'))

                fullName = self.pkt + '.' + modulename+ '.' + parentName + '.' + t.__name__

                stream.write('\t{}DefStruct("{}",{},{})\n'.format(tabnum,fullName,self.CalcStringCrc(fullName),self.CalcMessageSign(t,modulename)))

        import GridTableView
        existMembers = False        
        for m in members:
            tmember = getattr(t,m)
            if hasattr(tmember,'__name__') and tmember.__name__ == m:
                continue
            existMembers = True
            cppMemberType = self.GetType_Cpp(tmember,modulename)

            if self.pkt == 'cfg' and cppMemberType not in GridTableView.GridTableView.BasicTypes:
                stream.write('\t{}boost::shared_ptr<{}> {};\n'.format(tabnum,cppMemberType,self.GetTypeInitDefStr_Cpp(tmember,m,modulename)))  
            else:
                stream.write('\t{}{} {};\n'.format(tabnum,cppMemberType,self.GetTypeInitDefStr_Cpp(tmember,m,modulename))) 
                          
        stream.write('\n')

        if existMembers == True:
            stream.write('\t{}virtual void Deserialize(FastNet::StreamRead& stream) {}'.format(tabnum,'{'))
            for m in members:
                tmember = getattr(t,m)
                if hasattr(tmember,'__name__') and tmember.__name__ == m:
                    continue
                stream.write('\n\t\t{}stream.read({});'.format(tabnum,m))
            stream.write('\n\t{}{}\n'.format(tabnum,'}'))

            stream.write('\n\t{}virtual void Serialize(FastNet::StreamWrite& stream) {}'.format(tabnum,'{'))       
            for m in members:
                tmember = getattr(t,m)
                if hasattr(tmember,'__name__') and tmember.__name__ == m:
                    continue

                stream.write('\n\t\t{}stream.write({});'.format(tabnum,m))
            stream.write('\n\t{}{}\n'.format(tabnum,'}'))


            '''
            if self.pkt == 'pkt':
                stream.write('\n\t{}virtual void SerializeToBson(FastNet::BsonWrite& bson) {}'.format(tabnum,'{'))       
                for m in members:
                    tmember = getattr(t,m)
                    if hasattr(tmember,'__name__') and tmember.__name__ == m:
                        continue

                    if hasattr(tmember,'__clscode__') and tmember.__clscode__ == 1:
                        stream.write('\n\t\t{}bson.write(\"{}\",(Int32){});'.format(tabnum,m,m))
                    else:
                        stream.write('\n\t\t{}bson.write(\"{}\",{});'.format(tabnum,m,m))
                stream.write('\n\t{}{}\n'.format(tabnum,'}'))


                stream.write('\t{}virtual void DeserializeFromBson(FastNet::BsonRead& bson) {}'.format(tabnum,'{'))
                for m in members:
                    tmember = getattr(t,m)
                    if hasattr(tmember,'__name__') and tmember.__name__ == m:
                        continue

                    if hasattr(tmember,'__clscode__') and tmember.__clscode__ == 1:
                        stream.write('\n\t\t{}bson.read(\"{}\",(Int32&){});'.format(tabnum,m,m))
                    else:
                        stream.write('\n\t\t{}bson.read(\"{}\",{});'.format(tabnum,m,m))
                          
                stream.write('\n\t{}{}\n'.format(tabnum,'}'))
            '''


            stream.write('\n\t{}virtual FastNet::UInt32 SerializeSize() override{}\n'.format(tabnum,'{'))
            stream.write('{}\t\tFastNet::UInt32 size(0);'.format(tabnum))        
            for m in members:
                tmember = getattr(t,m)
                if hasattr(tmember,'__name__') and tmember.__name__ == m:
                    continue

                stream.write('\n\t\t{}CalcSerializeSize(size,{});'.format(tabnum,m))
            stream.write('\n\t\t{}return size;'.format(tabnum,m))
            stream.write('\n\t{}{}\n'.format(tabnum,'}'))

            if self.pkt == 'pkt':
                stream.write('\n\t{}virtual void Reset() override{}\n'.format(tabnum,'{'))    
                for m in members:
                    tmember = getattr(t,m)
                    if hasattr(tmember,'__name__') and tmember.__name__ == m:
                        continue

                    stream.write('\t\t{}{};\n'.format(tabnum,self.GetTypeResetStr_Cpp(tmember,m,modulename)))
                stream.write('\t{}{}\n'.format(tabnum,'}'))

        stream.write('\n\t{}static void Export(){}\n'.format(tabnum,'{'))

        if t.__clscode__ == 2:
            stream.write('\t\t{1}boost::python::class_<{0},boost::python::bases<FastNet::Struct>,boost::shared_ptr<{0}>,boost::noncopyable> _e("{0}");\n'.format(t.__name__,tabnum))

            if self.pkt == 'cfg':
                stream.write('\t\t{0}FastNet::App::AddCfgReloadCallback(&{1}::Reload);\n'.format(tabnum,t.__name__))
                stream.write('\t\t{0}FastNet::App::AddCfgInitCallback(&{1}::Init);\n'.format(tabnum,t.__name__))
                stream.write('\t\t{0}FastNet::App::RegisterStlVector<std::vector<boost::shared_ptr<{1}> > >(\"{2}\");\n'.format(tabnum,t.__name__,'v_{}'.format(self.CalcStringCrc(modulename+t.__name__))))
                stream.write('\t\t{0}{1}::ExportCfg(_e,\"{2}{1}.bytes\");\n'.format(tabnum,t.__name__,'cfg/' + modulename.replace('.','/') + '/'))

        elif t.__clscode__ == 3:
            stream.write('\t\t{1}boost::python::class_<{0},boost::python::bases<FastNet::Message>,boost::shared_ptr<{0}>,boost::noncopyable> _e("{0}");\n'.format(t.__name__,tabnum))
        else:
            assert(False)
            
        stream.write('\t\t{}boost::python::scope _s = _e;\n'.format(tabnum))
        for m in members:
            if scope != 1:
                continue
            tmember = getattr(t,m)

            if hasattr(tmember,'__clscode__') and tmember.__clscode__ == 1 and tmember.__name__ == m and tmember.__module__ == modulename:
                self.WriteEnumPythonDef_Cpp(stream,tabnum,tmember)

        for m in members:
            if scope != 1:
                continue
            tmember = getattr(t,m)

            if hasattr(tmember,'__clscode__') and tmember.__clscode__ == 2 and tmember.__name__ == m and tmember.__module__ == modulename:
                stream.write('\t\t{}{}::Export();\n'.format(tabnum,tmember.__name__))

        for m in members:
            tmember = getattr(t,m)
            if hasattr(tmember,'__name__') and tmember.__name__ == m:
                continue

            if isinstance(tmember,list) == True:
                if len(tmember) == 1:
                    stream.write('\t\t{2}FastNet::App::RegisterStlVector<{0} >(\"{1}\");\n'.format(self.GetType_Cpp(tmember,modulename),'v_{}'.format(self.CalcStringCrc(modulename+t.__name__+m)),tabnum))
                elif len(tmember) == 2:
                    if hasattr(tmember[1],'__clsname__') and tmember[1].__clsname__ == 'String':
                        stream.write('\t\t{2}FastNet::App::RegisterStlMap<{0},true>(\"{1}\");\n'.format(self.GetType_Cpp(tmember,modulename),'m_{}'.format(self.CalcStringCrc(modulename+t.__name__+m)),tabnum))
                    else:
                        stream.write('\t\t{2}FastNet::App::RegisterStlMap<{0} >(\"{1}\");\n'.format(self.GetType_Cpp(tmember,modulename),'m_{}'.format(self.CalcStringCrc(modulename+t.__name__+m)),tabnum))

            stream.write('\t\t{2}_e.def_readwrite("{0}",&{1}::{0});\n'.format(m,t.__name__,tabnum))
        if t.__clscode__ == 2 or t.__clscode__ == 3:
            stream.write('\t\t{1}_e.add_static_property("sClsId",&{0}::sClsId);\n'.format(t.__name__,tabnum))
            stream.write('\t\t{1}_e.add_static_property("sClsName",&{0}::sClsName);\n'.format(t.__name__,tabnum))
            stream.write('\t\t{1}_e.add_static_property("sSignId",&{0}::sSignId);\n'.format(t.__name__,tabnum))

        stream.write('\t{}{}\n'.format(tabnum,'}'))
        stream.write('{}{};\n\n'.format(tabnum,'}'))    


    def WriteStructDef_CSharp(self,members,stream,t,modulename,scope = 1,parentName = ""):
        tabnum = scope*'\t'

        if scope == 2:
            if t.__clscode__ == 2:
                if self.pkt == "cfg":
                    stream.write('{}public class {} : FastNet.Cfg<{},{}> {}\n'.format(tabnum,t.__name__,t.__name__,self.indexType,'{'))
                else:
                    stream.write('{}public class {} : FastNet.Struct {}\n'.format(tabnum,t.__name__,'{'))


            fullName = self.pkt + '.' + modulename+ '.' + parentName + '.' +t.__name__
            stream.write(
                '{0}\tpublic static UInt32 sClsId{4}\n'
                '{0}\t\tget{4}\n'
                '{0}\t\t\treturn {1};\n'
                '{0}\t\t{5}\n'
                '{0}\t{5}\n'
                '{0}\tpublic override UInt32 ClsId{4}\n'
                '{0}\t\tget{4}\n'
                '{0}\t\t\treturn {1};\n'
                '{0}\t\t{5}\n'
                '{0}\t{5}\n'
                '{0}\tpublic override String ClsName{4}\n'
                '{0}\t\tget{4}\n'
                '{0}\t\t\treturn "{2}";\n'
                '{0}\t\t{5}\n'
                '{0}\t{5}\n'
                '{0}\tpublic override UInt32 SignId{4}\n'
                '{0}\t\tget{4}\n'
                '{0}\t\t\treturn {3};\n'
                '{0}\t\t{5}\n'
                '{0}\t{5}\n'
                '{0}\tpublic static UInt32 sSignId{4}\n'
                '{0}\t\tget{4}\n'
                '{0}\t\t\treturn {3};\n'
                '{0}\t\t{5}\n{0}\t{5}\n\n'.format(tabnum,self.CalcStringCrc(fullName),fullName,self.CalcMessageSign(t,modulename),'{','}'))

        existMembers = False  
        for m in members:
            tmember = getattr(t,m)
            if hasattr(tmember,'__name__') and tmember.__name__ == m:
                continue

            existMembers = True
            stream.write('\t{}public {} {};\n'.format(tabnum,self.GetType_Cpp(tmember,modulename,False,True),self.GetTypeInitDefStr_CSharp(tmember,m,modulename)))

        stream.write('\n')

        if existMembers == True:
            stream.write('\t{}public override void Deserialize(BinaryReader stream){}\n'.format(tabnum,'{'))
            for m in members:
                tmember = getattr(t,m)
                if hasattr(tmember,'__name__') and tmember.__name__ == m:
                    continue
                #stream.write('\n\t\t{}sr.read({});'.format(tabnum,m))

                if self.pkt == 'pkt':
                    stream.write('\t\t{}doDeserialize (stream,ref {});\n'.format(tabnum,m))
                else:
                    if hasattr(tmember,'__clscode__') == True and tmember.__clscode__ == 2:
                        stream.write('\t\t{0}{1} = {2}.GetItem({2}.ReadKey(stream));\n'.format(tabnum,m,self.GetType_Cpp(tmember,modulename,False,True)))
                    else:
                        stream.write('\t\t{}doDeserialize (stream,ref {});\n'.format(tabnum,m))

            stream.write('\t{}{}\n'.format(tabnum,'}'))
        
            if self.pkt == 'pkt':
                stream.write('\n\t{}public override void Serialize(BinaryWriter stream) {}\n'.format(tabnum,'{'))    
                for m in members:
                    tmember = getattr(t,m)
                    if hasattr(tmember,'__name__') and tmember.__name__ == m:
                        continue
                    stream.write('\t\t{}doSerialize (stream,{});\n'.format(tabnum,m))
                stream.write('\t{}{}\n'.format(tabnum,'}'))

        if self.pkt == "cfg":

            relPath = '\"/cfg/{}/{}.bytes\"'.format(modulename.replace('.','/'),t.__name__)
            stream.write('\n\t{}public static void Init() {}\n'.format(tabnum,'{'))
            stream.write('\t\t{}{}.Load(FastNet.App.WorkPath + {},true);\n'.format(tabnum,t.__name__,relPath))
            stream.write('\t{}{}\n'.format(tabnum,'}'))

        stream.write('{}{}\n'.format(tabnum,'}'))
 

    def WriteStruct_CSharp(self,stream,t,modulename):
        if t.__clscode__ == 2:
            if self.pkt == "cfg":
                stream.write('\tpublic class {} : FastNet.Cfg<{},{}> {}\n'.format(t.__name__,t.__name__,self.indexType,'{'))
            else:
                stream.write('\tpublic class {} : FastNet.Struct {}\n'.format(t.__name__,'{'))
        elif t.__clscode__ == 3:    
            stream.write('\tpublic class {} : FastNet.Message {}\n'.format(t.__name__,'{'))
        else:
            assert(False)

        fullName = self.pkt + '.' + modulename+ '.' +t.__name__
        stream.write(
            '{0}\tpublic static UInt32 sClsId{4}\n'
            '{0}\t\tget{4}\n'
            '{0}\t\t\treturn {1};\n'
            '{0}\t\t{5}\n'
            '{0}\t{5}\n'
            '{0}\tpublic override UInt32 ClsId{4}\n'
            '{0}\t\tget{4}\n'
            '{0}\t\t\treturn {1};\n'
            '{0}\t\t{5}\n'
            '{0}\t{5}\n'
            '{0}\tpublic override String ClsName{4}\n'
            '{0}\t\tget{4}\n'
            '{0}\t\t\treturn "{2}";\n'
            '{0}\t\t{5}\n'
            '{0}\t{5}\n'
            '{0}\tpublic override UInt32 SignId{4}\n'
            '{0}\t\tget{4}\n'
            '{0}\t\t\treturn {3};\n'
            '{0}\t\t{5}\n'
            '{0}\t{5}\n'
            '{0}\tpublic static UInt32 sSignId{4}\n'
            '{0}\t\tget{4}\n'
            '{0}\t\t\treturn {3};\n'
            '{0}\t\t{5}\n{0}\t{5}\n\n'.format('\t',self.CalcStringCrc(fullName),fullName,self.CalcMessageSign(t,modulename),'{','}',self.pkt))

        members = []
        scopeTypes = []
        for m in vars(t):
            if m == '__doc__' or m == '__module__':
                continue

            TMember = getattr(t, m)
            if hasattr(TMember,'__name__') == True and TMember.__name__ == m:
                if self.ErrorCheck(TMember,False):
                    return False
                scopeTypes.append(TMember)
    
            members.append(m)
        
        #write scope types
        for TMember in scopeTypes:
            if TMember.__clscode__ == 1:
                self.WriteEnumDef_CSharp(stream,TMember,modulename,2)

        for TMember in scopeTypes:
            if TMember.__clscode__ == 2:
                
                tmembers = []
                for m in vars(TMember):
                    if m == '__doc__' or m == '__module__':
                        continue
                    tmembers.append(m)
    
                self.WriteStructDef_CSharp(tmembers,stream,TMember,modulename,2,t.__name__)  
                        
        self.WriteStructDef_CSharp(members,stream,t,modulename)    


    def WriteStruct_Cpp(self,stream,t,modulename):

        if t.__clscode__ == 2:
            if self.pkt == 'cfg':
                stream.write('\tstruct {0} final: public FastNet::Struct,FastNet::Cfg<{0},{1}> {2}\n'.format(t.__name__,self.indexType,'{'))
            else:
                stream.write('\tstruct {} : public FastNet::Struct {}\n'.format(t.__name__,'{'))
            stream.write('\t\tbool operator==({} const& ) const {} return false; {}\n'.format(t.__name__,'{','}'))
            stream.write('\t\tbool operator!=({} const& ) const {} return true; {}\n'.format(t.__name__,'{','}'))

            fullName = self.pkt + '.' + modulename+ '.' +t.__name__
            stream.write('\t\tDefStruct("{}",{},{})\n'.format(fullName,self.CalcStringCrc(fullName),self.CalcMessageSign(t,modulename)))
        elif t.__clscode__ == 3:    
            stream.write('\tclass {} final: public FastNet::Message {}\n'.format(t.__name__,'{'))
            stream.write('\tpublic:\n')

            fullName = self.pkt + '.' + modulename+ '.' +t.__name__
            stream.write('\t\tDefStruct("{}",{},{})\n'.format(fullName,self.CalcStringCrc(fullName),self.CalcMessageSign(t,modulename)))
        else:
            assert(False)

        members = []
        scopeTypes = []
        for m in vars(t):
            if m == '__doc__' or m == '__module__':
                continue

            TMember = getattr(t, m)
            if hasattr(TMember,'__name__') == True and TMember.__name__ == m:
                if self.ErrorCheck(TMember,False):
                    return False
                scopeTypes.append(TMember)
    
            members.append(m)
        
        #write scope types
        for TMember in scopeTypes:
            if TMember.__clscode__ == 1:
                self.WriteEnumDef_Cpp(stream,TMember,modulename,2)

        for TMember in scopeTypes:
            if TMember.__clscode__ == 2:
                
                tmembers = []
                for m in vars(TMember):
                    if m == '__doc__' or m == '__module__':
                        continue
                    tmembers.append(m)
    
                self.WriteStructDef_Cpp(tmembers,stream,TMember,modulename,2,t.__name__)    
                        
        self.WriteStructDef_Cpp(members,stream,t,modulename)    
        
        if self.pkt == 'cfg':
            self.allClassMembers[modulename + '.' + t.__name__] = members,self.CalcMessageSign(t,modulename)


    def GetBasicTypes(self,t,basicTypes):
        if isinstance(t,list) == True:
            if len(t) == 1:
                self.GetBasicTypes(t[0],basicTypes)
            else:
                self.GetBasicTypes(t[0],basicTypes)
                self.GetBasicTypes(t[1],basicTypes)
        else:
            if hasattr(t,'__clscode__') and t.__clscode__ == 4:
                basicTypes.add(t.__clsname__)

    def GetRefMoudleList(self,t,modulename,refList):

        if hasattr(t,'__module__') and modulename != t.__module__ and t.__module__ != 'GenProto':
            refList.add(t.__module__)

        members = vars(t)
        for m in members:
            if m == '__doc__' or m == '__module__':
                continue

            tmember = getattr(t,m)
            #if hasattr(tmember,'__clscode__') and (tmember.__clscode__ == 2 or tmember.__clscode__ == 3):
            if isinstance(tmember,list) == True:
                if len(tmember) == 1:
                    self.GetRefMoudleList(tmember[0],modulename,refList)
                else:
                    self.GetRefMoudleList(tmember[0],modulename,refList)
                    self.GetRefMoudleList(tmember[1],modulename,refList)
            else:
                if hasattr(tmember,'__module__') and modulename != tmember.__module__ and tmember.__module__ != 'GenProto':
                    refList.add(tmember.__module__)


    def GetScopeStructName(self,t,modulename,structList):

        if hasattr(t,'__module__') and modulename == t.__module__ and t.__module__ != 'GenProto':
            if t.__clscode__ == 2 or t.__clscode__ == 3:
                structList.add(t.__name__)

        members = vars(t)
        for m in members:
            if m == '__doc__' or m == '__module__':
                continue

            tmember = getattr(t,m)
            if hasattr(tmember,'__module__') and modulename == tmember.__module__ and tmember.__module__ != 'GenProto' and tmember.__name__ == m:
                if tmember.__clscode__ == 2 or tmember.__clscode__ == 3:
                    structList.add( t.__name__ + '::' + tmember.__name__)

    def Export_Cpp(self,inputFile,exportTypes,modulename,outDir,namespaces):

        outModuleName = 'module' + str(self.CalcStringCrc(modulename))

        relpath = os.path.relpath(inputFile,self.rootDir).replace('.py','.h')

        outfilename = outDir + os.sep + relpath
        outfilepath = os.path.dirname(outfilename)
        if os.path.isdir(outfilepath) == False:
             os.makedirs(outfilepath)

        streamCpp = open(outfilename.replace('.h','.cpp'), 'w')

        stream = open(outfilename, 'w')
        stream.write('#pragma once\n')
        stream.write('#include "FastNet/core/ClassFactory.h"\n')
        stream.write('#include "FastNet/core/Stream.h"\n')
        stream.write('#include "FastNet/core/App.h"\n')
        stream.write('#include "FastNet/core/Cfg.h"\n')

        streamCpp.write('#include "{}"\n\n'.format(os.path.basename(outfilename)))

        refList = set()    
        structList = set()
        for t in exportTypes:
            self.GetRefMoudleList(t,modulename,refList)
            self.GetScopeStructName(t,modulename,structList)

        for r in refList:
            stream.write('#include "{}.h"\n'.format(r.replace('.','/')))

        stream.write('\n\n')

        needWriteRegisterCallback = False

        #begin namespace
        namespacesCpp = self.pkt + '::'
        stream.write('namespace {}{}\n'.format(self.pkt,'{'))
        streamCpp.write('namespace {}{}\n'.format(self.pkt,'{'))
        if len(namespaces) > 0:
            for i in range(0,len(namespaces)):
                stream.write('namespace {}{}\n'.format(namespaces[i],'{'))
                streamCpp.write('namespace {}{}\n'.format(namespaces[i],'{'))
                namespacesCpp += namespaces[i] + '::'
            stream.write('\n')
            streamCpp.write('\n')
        else:
            stream.write('\n')
            streamCpp.write('\n')

        #using basic type
        stream.write('using FastNet::UInt8;\n')
        stream.write('using FastNet::UInt16;\n')
        stream.write('using FastNet::UInt32;\n')
        stream.write('using FastNet::UInt64;\n')
        stream.write('using FastNet::Int8;\n')
        stream.write('using FastNet::Int16;\n')
        stream.write('using FastNet::Int32;\n')
        stream.write('using FastNet::Int64;\n')
        stream.write('using FastNet::Double;\n')
        stream.write('using FastNet::Float;\n')
        stream.write('using FastNet::String;\n')
        stream.write('using FastNet::Bool;\n')
        '''basicTypes = set()    
        for t in exportTypes:
            members = vars(t)
            for m in members:
                if m == '__doc__' or m == '__module__':
                    continue

                self.GetBasicTypes(getattr(t,m),basicTypes)

        if len(basicTypes) > 0:
            for v in basicTypes:
                stream.write('using FastNet::{};\n'.format(v))
            stream.write('\n')'''

        #error check
        for t in exportTypes:
            if self.ErrorCheck(t):
                print('Error: gen cpp fail ' + relpath)
                return

        #gen enum
        for t in exportTypes:
            if t.__clscode__ == 1:
                needWriteRegisterCallback = True
                self.WriteEnumDef_Cpp(stream,t,modulename)

        #gen struct
        for t in exportTypes:
            if t.__clscode__ == 2:
                if self.pkt == 'cfg':
                    self.indexType = 'UInt32'
                    self.indexType = self.indexs[modulename + '.' + t.__name__]
                    self.indexType = 'FastNet::' + self.indexType

                if self.WriteStruct_Cpp(stream,t,modulename) == False:
                    print('Error: gen cpp fail ' + relpath)
                    return
                needWriteRegisterCallback = True

                

        #gen message
        for t in exportTypes:
            if t.__clscode__ == 3:
                if self.WriteStruct_Cpp(stream,t,modulename) == False:
                    print('Error: gen cpp fail ' + relpath)
                    return
                needWriteRegisterCallback = True
        
        if needWriteRegisterCallback:
            filenameNoext = os.path.split(inputFile)[1].replace('.py','')
            #stream.write('namespace {}{}\n'.format(filenameNoext,'{'))
            streamCpp.write('\tBOOST_PYTHON_MODULE({}){}\n'.format(outModuleName,'{'))

            for t in exportTypes:
                if t.__clscode__ == 1:
                    self.WriteEnumPythonDef_Cpp(streamCpp,'',t)

            for t in exportTypes:
                if t.__clscode__ == 3 or t.__clscode__ == 2:
                    streamCpp.write('\t\t{0}::Export();\n'.format(t.__name__))

            for t in exportTypes:
                if t.__clscode__ == 3:
                    streamCpp.write('\t\tFastNet::ClassFactory::Instance()->Register<{0}>();\n'.format(t.__name__))

            streamCpp.write('\t}\n\n')

            streamCpp.write('\tstruct _{}_Reister{}\n'.format(filenameNoext,'{'))
            streamCpp.write('\t\t_{}_Reister(){}\n'.format(filenameNoext,'{'))
            streamCpp.write('\t\t\tPyImport_AppendInittab("{0}",PyInit_{0});\n'.format(outModuleName))

            if self.pkt == 'cfg':
                #initString = 'import {}\\n'.format(outModuleName)
                #initString += 'cfg.SetNamespaces({},{},\'{}\')'.format(namespaces,structList,outModuleName)
                #streamCpp.write('\t\t\tFastNet::App::AddCfgStructs("{}");\n'.format(initString))
                streamCpp.write('\t\t\tstd::vector<std::string> namespaces;\n')  
                for v in namespaces:
                    streamCpp.write('\t\t\tnamespaces.emplace_back(\"{}\");\n'.format(v))

                streamCpp.write('\t\t\tstd::vector<std::string> types;\n')
                for v in structList:
                    streamCpp.write('\t\t\ttypes.emplace_back(\"{}\");\n'.format(v))

                streamCpp.write('\t\t\tFastNet::App::AddCfgStructs(namespaces,types,\"{}\");\n'.format(outModuleName))

            else:
                #initString = 'import {}\\n'.format(outModuleName)
                messageList = []
                for t in exportTypes:
                    if t.__clscode__ == 3 or t.__clscode__ == 2 or t.__clscode__ == 1:
                        messageList.append(t.__name__)

                #initString += 'pkt.SetNamespaces({},{},\'{}\')'.format(namespaces,messageList,outModuleName)
                streamCpp.write('\t\t\tstd::vector<std::string> namespaces;\n')
                for v in namespaces:
                    streamCpp.write('\t\t\tnamespaces.emplace_back(\"{}\");\n'.format(v))
                streamCpp.write('\t\t\tstd::vector<std::string> types;\n')
                for v in messageList:
                    streamCpp.write('\t\t\ttypes.emplace_back(\"{}\");\n'.format(v))
                streamCpp.write('\t\t\tFastNet::App::AddPktStructs(namespaces,types,\"{}\");\n'.format(outModuleName))

                #streamCpp.write('\t\t\tFastNet::App::AddPktStructs("{}");\n'.format(initString))

            streamCpp.write('\t\t}\n')
            streamCpp.write('\t{} s_{}_Reister;\n'.format('}',filenameNoext))

        stream.write('\n')
        streamCpp.write('\n')
        #end namespace
        if len(namespaces) > 0:
            for i in range(0,len(namespaces)):
                stream.write('{} //end namespace {}\n'.format('}',namespaces[i]))
                streamCpp.write('{} //end namespace {}\n'.format('}',namespaces[i]))
        stream.write('{} //end namespace {}\n'.format('}',self.pkt))
        streamCpp.write('{} //end namespace {}\n'.format('}',self.pkt))

        if needWriteRegisterCallback:
            streamCpp.write('\n#if (_MSC_VER == 1900)\n')
            for t in structList:
                streamCpp.write('BoostLink_VS2015_Update3({0}{1})\n'.format(namespacesCpp,t))
            streamCpp.write('#endif\n')


        print('Success: gen cpp ' + relpath)

    def FindPyFile(self,dirname):
        for i in os.listdir(dirname):
            path = dirname + os.sep + i
            if os.path.isdir(path):
                self.FindPyFile(path)
            elif os.path.isfile(path):
                extname = os.path.splitext(i)
                if len(extname) < 2 or extname[0] == 'GenProto' or extname[0] == '__init__' or extname[1] != '.py':  
                    continue

                if dirname in self.allDirs:
                    self.allDirs[dirname].append(i)
                else:
                    self.allDirs[dirname] = [i]

        def GetResult(self):
            return self.result

    @property
    def AllClassMembers(self):
        return self.allClassMembers

    @staticmethod
    def GetFileMd5(filePath):
        size = os.path.getsize(filePath)
        run = True
        with open(filePath,'rb') as f:
            md5 = hashlib.md5()
            while run:
                d = None
                if size > 129536:
                    d = f.read(129536)
                    size -= 129536
                else:
                    d = f.read(size)

                if not d:
                    run = False

                md5.update(d)

            hashValue = md5.hexdigest()
            md5 = str(hashValue).lower()
        return md5
        
    def __init__(self,rootDir,cppOutDir,csharpOutDir,luaOutDir,pkt = 'pkt',indexs = {}):
        self.indexs = indexs
        self.pkt = pkt
        self.mainModuleName = self.GetMainModuleName()
        self.mainModule = __import__(self.mainModuleName)
        self.rootDir = './'
        self.result = 1
        self.rootDir = os.path.abspath(rootDir)
        self.allClassMembers = {}

        self.luaJsonValues = []

        if self.rootDir not in sys.path:
            sys.path.append(self.rootDir)

        if cppOutDir:
            cppOutDir = os.path.abspath(cppOutDir)
            cppOutDir = os.path.join(cppOutDir,self.pkt)
            if os.path.isdir(cppOutDir) == False:
                os.makedirs(cppOutDir)

        if csharpOutDir:    
            csharpOutDir = os.path.abspath(csharpOutDir)
            csharpOutDir = os.path.join(csharpOutDir,self.pkt)
            if os.path.isdir(csharpOutDir) == False:
                os.makedirs(csharpOutDir)

        if luaOutDir:
            luaOutDir = os.path.abspath(luaOutDir)
            if os.path.isdir(luaOutDir) == False:
                os.makedirs(luaOutDir)
        
                                
        self.allDirs = {}
        self.FindPyFile(self.rootDir)
        for k,v in self.allDirs.items():
            if k == self.rootDir:
                continue

            if len(v) > 0:
                with open('{}{}__init__.py'.format(k,os.sep), 'w') as f:
                    f.write('#coding:utf-8')

        for k,v in self.allDirs.items():
            for filename in v:
                exportTypes = list()
                fullpath = os.path.join(k, filename)
                relpath = os.path.relpath(k,self.rootDir)    
                relpath = relpath.replace(os.sep,'.')

                module = None
                modulename = ''
                if relpath == '.':
                    modulename = filename.replace('.py','')
                else:
                    modulename = relpath + '.' + filename.replace('.py','')

                module = importlib.import_module(modulename)
                importlib.reload(module)
                for k2,v2 in vars(module).items():
                    if not hasattr(v2,'__module__') or (hasattr(v2,'__clscode__') and v2.__clscode__ == 4) or k2 == 'Enum' or k2 == 'Struct' or k2 == 'Message':
                        continue
                    
                    if v2.__module__ != modulename:
                        continue

                    exportTypes.append(v2)

                namespaces =  modulename.split(".")

                enums = []
                structs = []
                messages = []

                for v in exportTypes:
                    if v.__clscode__ == 1:
                        enums.append(v)
                    elif v.__clscode__ == 2:
                        structs.append(v)
                    elif v.__clscode__ == 3:
                        messages.append(v)
                    else:
                        assert(False)

                def MySorted(l,cmp):
                    size = len(l)
                    for i in range(0,size):
                        for j in range(0,size):
                            x = l[i]
                            y = l[j]
                            if x == y:
                                continue

                            ret = cmp(x,y)
                            if ret == -1:
                                l[i] = y
                                l[j] = x
                    return l

                
                enums = MySorted(enums,self.ReversedCmp)
                structs = MySorted(structs,self.ReversedCmp)
                messages = MySorted(messages,self.ReversedCmp)
                enums = MySorted(enums,self.ReversedCmp)
                structs = MySorted(structs,self.ReversedCmp)
                messages = MySorted(messages,self.ReversedCmp)
                exportTypes = enums + structs + messages

                if cppOutDir:
                    self.Export_Cpp(fullpath,exportTypes,modulename,cppOutDir,namespaces)

                if csharpOutDir:
                    self.Export_CSharp(fullpath,exportTypes,modulename,csharpOutDir,namespaces)

                if luaOutDir:
                    if self.pkt == 'pkt':
                        self.Export_Lua(exportTypes,modulename)
                    else:
                        self.Export_Lua(exportTypes,modulename)

        if luaOutDir:
            if self.pkt == 'pkt':
                luaOutDir = luaOutDir + "/pkt_table.bytes"
            else:
                luaOutDir = luaOutDir + "/cfg_table.bytes"

            with open(luaOutDir,'w') as f:
                import json
                json.dump(self.luaJsonValues,f)

            self.luaJsonValues = None  