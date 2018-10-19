# -*- coding: utf-8 -*-
from GenProto import *

'''
支持的类型
基础类型
UInt8,UInt16,UInt32,UInt64
Int8,Int16,Int32,Int64
Float,Double,Bool,String
stl类型
[t] 代表 std::vector<t>
[key,value] 代表 std::map<key,value> 注意:key只能为基础类型

协议命名规范
协议名和协议字段统一采用<驼峰式命名法>
客户端发给服务端的协议统一都用 Req 结尾，表示 client to server
服务端发给客户端的协议统一都用 Res 结尾，表示 server to client
'''

class AccountVerifySucceedRes(Message):
    roleId = String

class RoleLoginSucceedRes(Message):
    roleId = String
    tabs = String
    name = String

class AnyReq(Message):
    classId = String
    data = String

class AnyRes(Message):
    classId = String
    data = String
