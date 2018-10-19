# -*- coding: utf-8 -*-
from GenProto import *

class ErrorMessage(Message):
	key = String
	msg = String

class AccountVerifyReq(Message):
	channel = String
	jsonData = String

class RoleLoginReq(Message):
	roleId = String

class RoleLoginRes(Message):
	roleId = String
	token = String

class UpdateRoleTokenRes(Message):
	token = String

class RoleReconnectReq(Message):
	roleId = String
	token = String

class SocketHeartbeat(Message):
	time = UInt32
	pass

class SocketClose(Message):
	pass


class PublishReq(Message):
	isPublic = Bool
	message = String
	id = UInt32

class PublishRes(Message):
	isPublic = Bool
	message = String
	id = UInt32

class SubscribeReq(Message):
	id = UInt32

class SubscribeRes(Message):
	id = UInt32

class UnsubscribeReq(Message):
	id = UInt32

class UnsubscribeRes(Message):
	id = UInt32

class LocalSocketEvent(Message):
	info = String
	evt = UInt8

class SocketConnect(Message):
	sessionId = UInt32
	serverId = UInt32
	md5Values = String

class SocketConnectReq(Message):
	deviceId = String
	subscribeKey = String
	token = String

class RoomMessageReq(Message):
	roomId = UInt32
	roleId = String
	clsId = UInt32
	signId = UInt32
	data = String

class RoomMessageRes(Message):
	roomId = UInt32
	roleId = String
	clsId = UInt32
	signId = UInt32
	data = String


class DownloadFileListReq(Message):
	files = [String]

class DownloadFileListRes(Message):
	files = [String,UInt32]

class DownloadFileRes(Message):
	file = String
	data = [UInt8]
	indexPart = UInt32


class LogInfo(Struct):
	key = String
	log = String
	time = UInt32

class LogQueryRes(Message):
	isEnd = Bool
	logs = [LogInfo]


class LogQueryReq(Message):
	key = String
	beginTime = UInt32
	endTime = UInt32
	appId = UInt32



class ReceiveMailReq(Message):
    id = UInt32

class ReceiveMailRes(Message):
    id = UInt32

class MailRes(Message):
    id = UInt32
    title = String
    text = String
    vaild = UInt32
    attachIds = [UInt32,UInt64]

class LoginNoticeRes(Message):
    title = String
    text = String

class GameNoticeRes(Message):
    title = String
    text = String
    duration = UInt32
    beginTime = UInt32
    endTime = UInt32