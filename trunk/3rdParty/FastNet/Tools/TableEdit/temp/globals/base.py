# -*- coding: utf-8 -*-
from GenProto import *



class Language(Struct):
	id = UInt32
	text = String
	pass


class ErrorCode(Struct):
	key = String
	msg = String
	pass


class Items(Struct):
	id = UInt32
	name = Language
	pass
