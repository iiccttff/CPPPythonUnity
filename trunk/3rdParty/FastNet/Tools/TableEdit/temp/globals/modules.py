# -*- coding: utf-8 -*-
from GenProto import *



class NoticeMgr(Struct):
	name = String
	key = String
	pass


class PlatformMgr(Struct):
	name = String
	key = String
	pass


class ServerMgr(Struct):
	name = String
	key = String
	pass


class UserMgr(Struct):
	name = String
	key = String
	pass


class DataQuery(Struct):
	name = String
	key = String
	pass


class MailMgr(Struct):
	name = String
	key = String
	pass
