#pragma once
#include "FastNet/core/ClassFactory.h"
#include "FastNet/core/Stream.h"
#include "FastNet/core/App.h"
#include "FastNet/core/Cfg.h"


namespace pkt{
namespace protocols{

using FastNet::UInt8;
using FastNet::UInt16;
using FastNet::UInt32;
using FastNet::UInt64;
using FastNet::Int8;
using FastNet::Int16;
using FastNet::Int32;
using FastNet::Int64;
using FastNet::Double;
using FastNet::Float;
using FastNet::String;
using FastNet::Bool;
	struct LogInfo : public FastNet::Struct {
		bool operator==(LogInfo const& ) const { return false; }
		bool operator!=(LogInfo const& ) const { return true; }
		DefStruct("pkt.protocols.LogInfo",956022818,1733085687)
		String key="";
		String log="";
		UInt32 time=0;

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(key);
			stream.read(log);
			stream.read(time);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(key);
			stream.write(log);
			stream.write(time);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,key);
			CalcSerializeSize(size,log);
			CalcSerializeSize(size,time);
			return size;
		}

		virtual void Reset() override{
			key="";
			log="";
			time=0;
		}

		static void Export(){
			boost::python::class_<LogInfo,boost::python::bases<FastNet::Struct>,boost::shared_ptr<LogInfo>,boost::noncopyable> _e("LogInfo");
			boost::python::scope _s = _e;
			_e.def_readwrite("key",&LogInfo::key);
			_e.def_readwrite("log",&LogInfo::log);
			_e.def_readwrite("time",&LogInfo::time);
			_e.add_static_property("sClsId",&LogInfo::sClsId);
			_e.add_static_property("sClsName",&LogInfo::sClsName);
			_e.add_static_property("sSignId",&LogInfo::sSignId);
		}
	};

	class ErrorMessage final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.ErrorMessage",3011211716,3742882662)
		String key="";
		String msg="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(key);
			stream.read(msg);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(key);
			stream.write(msg);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,key);
			CalcSerializeSize(size,msg);
			return size;
		}

		virtual void Reset() override{
			key="";
			msg="";
		}

		static void Export(){
			boost::python::class_<ErrorMessage,boost::python::bases<FastNet::Message>,boost::shared_ptr<ErrorMessage>,boost::noncopyable> _e("ErrorMessage");
			boost::python::scope _s = _e;
			_e.def_readwrite("key",&ErrorMessage::key);
			_e.def_readwrite("msg",&ErrorMessage::msg);
			_e.add_static_property("sClsId",&ErrorMessage::sClsId);
			_e.add_static_property("sClsName",&ErrorMessage::sClsName);
			_e.add_static_property("sSignId",&ErrorMessage::sSignId);
		}
	};

	class AccountVerifyReq final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.AccountVerifyReq",2110615719,3742882662)
		String channel="";
		String jsonData="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(channel);
			stream.read(jsonData);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(channel);
			stream.write(jsonData);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,channel);
			CalcSerializeSize(size,jsonData);
			return size;
		}

		virtual void Reset() override{
			channel="";
			jsonData="";
		}

		static void Export(){
			boost::python::class_<AccountVerifyReq,boost::python::bases<FastNet::Message>,boost::shared_ptr<AccountVerifyReq>,boost::noncopyable> _e("AccountVerifyReq");
			boost::python::scope _s = _e;
			_e.def_readwrite("channel",&AccountVerifyReq::channel);
			_e.def_readwrite("jsonData",&AccountVerifyReq::jsonData);
			_e.add_static_property("sClsId",&AccountVerifyReq::sClsId);
			_e.add_static_property("sClsName",&AccountVerifyReq::sClsName);
			_e.add_static_property("sSignId",&AccountVerifyReq::sSignId);
		}
	};

	class RoleLoginReq final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.RoleLoginReq",27255320,2568140703)
		String roleId="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(roleId);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(roleId);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,roleId);
			return size;
		}

		virtual void Reset() override{
			roleId="";
		}

		static void Export(){
			boost::python::class_<RoleLoginReq,boost::python::bases<FastNet::Message>,boost::shared_ptr<RoleLoginReq>,boost::noncopyable> _e("RoleLoginReq");
			boost::python::scope _s = _e;
			_e.def_readwrite("roleId",&RoleLoginReq::roleId);
			_e.add_static_property("sClsId",&RoleLoginReq::sClsId);
			_e.add_static_property("sClsName",&RoleLoginReq::sClsName);
			_e.add_static_property("sSignId",&RoleLoginReq::sSignId);
		}
	};

	class RoleLoginRes final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.RoleLoginRes",4019290932,3742882662)
		String roleId="";
		String token="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(roleId);
			stream.read(token);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(roleId);
			stream.write(token);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,roleId);
			CalcSerializeSize(size,token);
			return size;
		}

		virtual void Reset() override{
			roleId="";
			token="";
		}

		static void Export(){
			boost::python::class_<RoleLoginRes,boost::python::bases<FastNet::Message>,boost::shared_ptr<RoleLoginRes>,boost::noncopyable> _e("RoleLoginRes");
			boost::python::scope _s = _e;
			_e.def_readwrite("roleId",&RoleLoginRes::roleId);
			_e.def_readwrite("token",&RoleLoginRes::token);
			_e.add_static_property("sClsId",&RoleLoginRes::sClsId);
			_e.add_static_property("sClsName",&RoleLoginRes::sClsName);
			_e.add_static_property("sSignId",&RoleLoginRes::sSignId);
		}
	};

	class UpdateRoleTokenRes final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.UpdateRoleTokenRes",2169161796,2568140703)
		String token="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(token);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(token);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,token);
			return size;
		}

		virtual void Reset() override{
			token="";
		}

		static void Export(){
			boost::python::class_<UpdateRoleTokenRes,boost::python::bases<FastNet::Message>,boost::shared_ptr<UpdateRoleTokenRes>,boost::noncopyable> _e("UpdateRoleTokenRes");
			boost::python::scope _s = _e;
			_e.def_readwrite("token",&UpdateRoleTokenRes::token);
			_e.add_static_property("sClsId",&UpdateRoleTokenRes::sClsId);
			_e.add_static_property("sClsName",&UpdateRoleTokenRes::sClsName);
			_e.add_static_property("sSignId",&UpdateRoleTokenRes::sSignId);
		}
	};

	class RoleReconnectReq final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.RoleReconnectReq",589866478,3742882662)
		String roleId="";
		String token="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(roleId);
			stream.read(token);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(roleId);
			stream.write(token);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,roleId);
			CalcSerializeSize(size,token);
			return size;
		}

		virtual void Reset() override{
			roleId="";
			token="";
		}

		static void Export(){
			boost::python::class_<RoleReconnectReq,boost::python::bases<FastNet::Message>,boost::shared_ptr<RoleReconnectReq>,boost::noncopyable> _e("RoleReconnectReq");
			boost::python::scope _s = _e;
			_e.def_readwrite("roleId",&RoleReconnectReq::roleId);
			_e.def_readwrite("token",&RoleReconnectReq::token);
			_e.add_static_property("sClsId",&RoleReconnectReq::sClsId);
			_e.add_static_property("sClsName",&RoleReconnectReq::sClsName);
			_e.add_static_property("sSignId",&RoleReconnectReq::sSignId);
		}
	};

	class SocketHeartbeat final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.SocketHeartbeat",890548039,215971539)
		UInt32 time=0;

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(time);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(time);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,time);
			return size;
		}

		virtual void Reset() override{
			time=0;
		}

		static void Export(){
			boost::python::class_<SocketHeartbeat,boost::python::bases<FastNet::Message>,boost::shared_ptr<SocketHeartbeat>,boost::noncopyable> _e("SocketHeartbeat");
			boost::python::scope _s = _e;
			_e.def_readwrite("time",&SocketHeartbeat::time);
			_e.add_static_property("sClsId",&SocketHeartbeat::sClsId);
			_e.add_static_property("sClsName",&SocketHeartbeat::sClsName);
			_e.add_static_property("sSignId",&SocketHeartbeat::sSignId);
		}
	};

	class SocketClose final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.SocketClose",4256359424,0)


		static void Export(){
			boost::python::class_<SocketClose,boost::python::bases<FastNet::Message>,boost::shared_ptr<SocketClose>,boost::noncopyable> _e("SocketClose");
			boost::python::scope _s = _e;
			_e.add_static_property("sClsId",&SocketClose::sClsId);
			_e.add_static_property("sClsName",&SocketClose::sClsName);
			_e.add_static_property("sSignId",&SocketClose::sSignId);
		}
	};

	class PublishReq final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.PublishReq",2355507917,752654989)
		Bool isPublic=false;
		String message="";
		UInt32 id=0;

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(isPublic);
			stream.read(message);
			stream.read(id);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(isPublic);
			stream.write(message);
			stream.write(id);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,isPublic);
			CalcSerializeSize(size,message);
			CalcSerializeSize(size,id);
			return size;
		}

		virtual void Reset() override{
			isPublic=false;
			message="";
			id=0;
		}

		static void Export(){
			boost::python::class_<PublishReq,boost::python::bases<FastNet::Message>,boost::shared_ptr<PublishReq>,boost::noncopyable> _e("PublishReq");
			boost::python::scope _s = _e;
			_e.def_readwrite("isPublic",&PublishReq::isPublic);
			_e.def_readwrite("message",&PublishReq::message);
			_e.def_readwrite("id",&PublishReq::id);
			_e.add_static_property("sClsId",&PublishReq::sClsId);
			_e.add_static_property("sClsName",&PublishReq::sClsName);
			_e.add_static_property("sSignId",&PublishReq::sSignId);
		}
	};

	class PublishRes final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.PublishRes",1651004385,752654989)
		Bool isPublic=false;
		String message="";
		UInt32 id=0;

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(isPublic);
			stream.read(message);
			stream.read(id);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(isPublic);
			stream.write(message);
			stream.write(id);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,isPublic);
			CalcSerializeSize(size,message);
			CalcSerializeSize(size,id);
			return size;
		}

		virtual void Reset() override{
			isPublic=false;
			message="";
			id=0;
		}

		static void Export(){
			boost::python::class_<PublishRes,boost::python::bases<FastNet::Message>,boost::shared_ptr<PublishRes>,boost::noncopyable> _e("PublishRes");
			boost::python::scope _s = _e;
			_e.def_readwrite("isPublic",&PublishRes::isPublic);
			_e.def_readwrite("message",&PublishRes::message);
			_e.def_readwrite("id",&PublishRes::id);
			_e.add_static_property("sClsId",&PublishRes::sClsId);
			_e.add_static_property("sClsName",&PublishRes::sClsName);
			_e.add_static_property("sSignId",&PublishRes::sSignId);
		}
	};

	class SubscribeReq final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.SubscribeReq",2884920292,215971539)
		UInt32 id=0;

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(id);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(id);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,id);
			return size;
		}

		virtual void Reset() override{
			id=0;
		}

		static void Export(){
			boost::python::class_<SubscribeReq,boost::python::bases<FastNet::Message>,boost::shared_ptr<SubscribeReq>,boost::noncopyable> _e("SubscribeReq");
			boost::python::scope _s = _e;
			_e.def_readwrite("id",&SubscribeReq::id);
			_e.add_static_property("sClsId",&SubscribeReq::sClsId);
			_e.add_static_property("sClsName",&SubscribeReq::sClsName);
			_e.add_static_property("sSignId",&SubscribeReq::sSignId);
		}
	};

	class SubscribeRes final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.SubscribeRes",1174012616,215971539)
		UInt32 id=0;

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(id);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(id);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,id);
			return size;
		}

		virtual void Reset() override{
			id=0;
		}

		static void Export(){
			boost::python::class_<SubscribeRes,boost::python::bases<FastNet::Message>,boost::shared_ptr<SubscribeRes>,boost::noncopyable> _e("SubscribeRes");
			boost::python::scope _s = _e;
			_e.def_readwrite("id",&SubscribeRes::id);
			_e.add_static_property("sClsId",&SubscribeRes::sClsId);
			_e.add_static_property("sClsName",&SubscribeRes::sClsName);
			_e.add_static_property("sSignId",&SubscribeRes::sSignId);
		}
	};

	class UnsubscribeReq final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.UnsubscribeReq",2796758889,215971539)
		UInt32 id=0;

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(id);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(id);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,id);
			return size;
		}

		virtual void Reset() override{
			id=0;
		}

		static void Export(){
			boost::python::class_<UnsubscribeReq,boost::python::bases<FastNet::Message>,boost::shared_ptr<UnsubscribeReq>,boost::noncopyable> _e("UnsubscribeReq");
			boost::python::scope _s = _e;
			_e.def_readwrite("id",&UnsubscribeReq::id);
			_e.add_static_property("sClsId",&UnsubscribeReq::sClsId);
			_e.add_static_property("sClsName",&UnsubscribeReq::sClsName);
			_e.add_static_property("sSignId",&UnsubscribeReq::sSignId);
		}
	};

	class UnsubscribeRes final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.UnsubscribeRes",1220363845,215971539)
		UInt32 id=0;

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(id);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(id);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,id);
			return size;
		}

		virtual void Reset() override{
			id=0;
		}

		static void Export(){
			boost::python::class_<UnsubscribeRes,boost::python::bases<FastNet::Message>,boost::shared_ptr<UnsubscribeRes>,boost::noncopyable> _e("UnsubscribeRes");
			boost::python::scope _s = _e;
			_e.def_readwrite("id",&UnsubscribeRes::id);
			_e.add_static_property("sClsId",&UnsubscribeRes::sClsId);
			_e.add_static_property("sClsName",&UnsubscribeRes::sClsName);
			_e.add_static_property("sSignId",&UnsubscribeRes::sSignId);
		}
	};

	class LocalSocketEvent final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.LocalSocketEvent",1714455482,2634531576)
		String info="";
		UInt8 evt=0;

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(info);
			stream.read(evt);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(info);
			stream.write(evt);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,info);
			CalcSerializeSize(size,evt);
			return size;
		}

		virtual void Reset() override{
			info="";
			evt=0;
		}

		static void Export(){
			boost::python::class_<LocalSocketEvent,boost::python::bases<FastNet::Message>,boost::shared_ptr<LocalSocketEvent>,boost::noncopyable> _e("LocalSocketEvent");
			boost::python::scope _s = _e;
			_e.def_readwrite("info",&LocalSocketEvent::info);
			_e.def_readwrite("evt",&LocalSocketEvent::evt);
			_e.add_static_property("sClsId",&LocalSocketEvent::sClsId);
			_e.add_static_property("sClsName",&LocalSocketEvent::sClsName);
			_e.add_static_property("sSignId",&LocalSocketEvent::sSignId);
		}
	};

	class SocketConnect final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.SocketConnect",3867250737,2040317094)
		UInt32 sessionId=0;
		UInt32 serverId=0;
		String md5Values="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(sessionId);
			stream.read(serverId);
			stream.read(md5Values);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(sessionId);
			stream.write(serverId);
			stream.write(md5Values);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,sessionId);
			CalcSerializeSize(size,serverId);
			CalcSerializeSize(size,md5Values);
			return size;
		}

		virtual void Reset() override{
			sessionId=0;
			serverId=0;
			md5Values="";
		}

		static void Export(){
			boost::python::class_<SocketConnect,boost::python::bases<FastNet::Message>,boost::shared_ptr<SocketConnect>,boost::noncopyable> _e("SocketConnect");
			boost::python::scope _s = _e;
			_e.def_readwrite("sessionId",&SocketConnect::sessionId);
			_e.def_readwrite("serverId",&SocketConnect::serverId);
			_e.def_readwrite("md5Values",&SocketConnect::md5Values);
			_e.add_static_property("sClsId",&SocketConnect::sClsId);
			_e.add_static_property("sClsName",&SocketConnect::sClsName);
			_e.add_static_property("sSignId",&SocketConnect::sSignId);
		}
	};

	class SocketConnectReq final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.SocketConnectReq",1638288233,4068542651)
		String deviceId="";
		String subscribeKey="";
		String token="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(deviceId);
			stream.read(subscribeKey);
			stream.read(token);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(deviceId);
			stream.write(subscribeKey);
			stream.write(token);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,deviceId);
			CalcSerializeSize(size,subscribeKey);
			CalcSerializeSize(size,token);
			return size;
		}

		virtual void Reset() override{
			deviceId="";
			subscribeKey="";
			token="";
		}

		static void Export(){
			boost::python::class_<SocketConnectReq,boost::python::bases<FastNet::Message>,boost::shared_ptr<SocketConnectReq>,boost::noncopyable> _e("SocketConnectReq");
			boost::python::scope _s = _e;
			_e.def_readwrite("deviceId",&SocketConnectReq::deviceId);
			_e.def_readwrite("subscribeKey",&SocketConnectReq::subscribeKey);
			_e.def_readwrite("token",&SocketConnectReq::token);
			_e.add_static_property("sClsId",&SocketConnectReq::sClsId);
			_e.add_static_property("sClsName",&SocketConnectReq::sClsName);
			_e.add_static_property("sSignId",&SocketConnectReq::sSignId);
		}
	};

	class RoomMessageReq final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.RoomMessageReq",2621212155,3516244101)
		UInt32 roomId=0;
		String roleId="";
		UInt32 clsId=0;
		UInt32 signId=0;
		String data="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(roomId);
			stream.read(roleId);
			stream.read(clsId);
			stream.read(signId);
			stream.read(data);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(roomId);
			stream.write(roleId);
			stream.write(clsId);
			stream.write(signId);
			stream.write(data);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,roomId);
			CalcSerializeSize(size,roleId);
			CalcSerializeSize(size,clsId);
			CalcSerializeSize(size,signId);
			CalcSerializeSize(size,data);
			return size;
		}

		virtual void Reset() override{
			roomId=0;
			roleId="";
			clsId=0;
			signId=0;
			data="";
		}

		static void Export(){
			boost::python::class_<RoomMessageReq,boost::python::bases<FastNet::Message>,boost::shared_ptr<RoomMessageReq>,boost::noncopyable> _e("RoomMessageReq");
			boost::python::scope _s = _e;
			_e.def_readwrite("roomId",&RoomMessageReq::roomId);
			_e.def_readwrite("roleId",&RoomMessageReq::roleId);
			_e.def_readwrite("clsId",&RoomMessageReq::clsId);
			_e.def_readwrite("signId",&RoomMessageReq::signId);
			_e.def_readwrite("data",&RoomMessageReq::data);
			_e.add_static_property("sClsId",&RoomMessageReq::sClsId);
			_e.add_static_property("sClsName",&RoomMessageReq::sClsName);
			_e.add_static_property("sSignId",&RoomMessageReq::sSignId);
		}
	};

	class RoomMessageRes final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.RoomMessageRes",1915938007,3516244101)
		UInt32 roomId=0;
		String roleId="";
		UInt32 clsId=0;
		UInt32 signId=0;
		String data="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(roomId);
			stream.read(roleId);
			stream.read(clsId);
			stream.read(signId);
			stream.read(data);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(roomId);
			stream.write(roleId);
			stream.write(clsId);
			stream.write(signId);
			stream.write(data);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,roomId);
			CalcSerializeSize(size,roleId);
			CalcSerializeSize(size,clsId);
			CalcSerializeSize(size,signId);
			CalcSerializeSize(size,data);
			return size;
		}

		virtual void Reset() override{
			roomId=0;
			roleId="";
			clsId=0;
			signId=0;
			data="";
		}

		static void Export(){
			boost::python::class_<RoomMessageRes,boost::python::bases<FastNet::Message>,boost::shared_ptr<RoomMessageRes>,boost::noncopyable> _e("RoomMessageRes");
			boost::python::scope _s = _e;
			_e.def_readwrite("roomId",&RoomMessageRes::roomId);
			_e.def_readwrite("roleId",&RoomMessageRes::roleId);
			_e.def_readwrite("clsId",&RoomMessageRes::clsId);
			_e.def_readwrite("signId",&RoomMessageRes::signId);
			_e.def_readwrite("data",&RoomMessageRes::data);
			_e.add_static_property("sClsId",&RoomMessageRes::sClsId);
			_e.add_static_property("sClsName",&RoomMessageRes::sClsName);
			_e.add_static_property("sSignId",&RoomMessageRes::sSignId);
		}
	};

	class DownloadFileListReq final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.DownloadFileListReq",3892002974,3204821990)
		std::vector<String> files;

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(files);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(files);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,files);
			return size;
		}

		virtual void Reset() override{
			files.clear();
		}

		static void Export(){
			boost::python::class_<DownloadFileListReq,boost::python::bases<FastNet::Message>,boost::shared_ptr<DownloadFileListReq>,boost::noncopyable> _e("DownloadFileListReq");
			boost::python::scope _s = _e;
			FastNet::App::RegisterStlVector<std::vector<String> >("v_3872902936");
			_e.def_readwrite("files",&DownloadFileListReq::files);
			_e.add_static_property("sClsId",&DownloadFileListReq::sClsId);
			_e.add_static_property("sClsName",&DownloadFileListReq::sClsName);
			_e.add_static_property("sSignId",&DownloadFileListReq::sSignId);
		}
	};

	class DownloadFileListRes final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.DownloadFileListRes",167059890,2638689951)
		std::map<String,UInt32> files;

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(files);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(files);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,files);
			return size;
		}

		virtual void Reset() override{
			files.clear();
		}

		static void Export(){
			boost::python::class_<DownloadFileListRes,boost::python::bases<FastNet::Message>,boost::shared_ptr<DownloadFileListRes>,boost::noncopyable> _e("DownloadFileListRes");
			boost::python::scope _s = _e;
			FastNet::App::RegisterStlMap<std::map<String,UInt32> >("m_2870963731");
			_e.def_readwrite("files",&DownloadFileListRes::files);
			_e.add_static_property("sClsId",&DownloadFileListRes::sClsId);
			_e.add_static_property("sClsName",&DownloadFileListRes::sClsName);
			_e.add_static_property("sSignId",&DownloadFileListRes::sSignId);
		}
	};

	class DownloadFileRes final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.DownloadFileRes",905004720,720761691)
		String file="";
		std::vector<UInt8> data;
		UInt32 indexPart=0;

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(file);
			stream.read(data);
			stream.read(indexPart);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(file);
			stream.write(data);
			stream.write(indexPart);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,file);
			CalcSerializeSize(size,data);
			CalcSerializeSize(size,indexPart);
			return size;
		}

		virtual void Reset() override{
			file="";
			data.clear();
			indexPart=0;
		}

		static void Export(){
			boost::python::class_<DownloadFileRes,boost::python::bases<FastNet::Message>,boost::shared_ptr<DownloadFileRes>,boost::noncopyable> _e("DownloadFileRes");
			boost::python::scope _s = _e;
			_e.def_readwrite("file",&DownloadFileRes::file);
			FastNet::App::RegisterStlVector<std::vector<UInt8> >("v_4046837044");
			_e.def_readwrite("data",&DownloadFileRes::data);
			_e.def_readwrite("indexPart",&DownloadFileRes::indexPart);
			_e.add_static_property("sClsId",&DownloadFileRes::sClsId);
			_e.add_static_property("sClsName",&DownloadFileRes::sClsName);
			_e.add_static_property("sSignId",&DownloadFileRes::sSignId);
		}
	};

	class LogQueryRes final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.LogQueryRes",426821530,3300748031)
		Bool isEnd=false;
		std::vector<LogInfo> logs;

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(isEnd);
			stream.read(logs);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(isEnd);
			stream.write(logs);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,isEnd);
			CalcSerializeSize(size,logs);
			return size;
		}

		virtual void Reset() override{
			isEnd=false;
			logs.clear();
		}

		static void Export(){
			boost::python::class_<LogQueryRes,boost::python::bases<FastNet::Message>,boost::shared_ptr<LogQueryRes>,boost::noncopyable> _e("LogQueryRes");
			boost::python::scope _s = _e;
			_e.def_readwrite("isEnd",&LogQueryRes::isEnd);
			FastNet::App::RegisterStlVector<std::vector<LogInfo> >("v_110131366");
			_e.def_readwrite("logs",&LogQueryRes::logs);
			_e.add_static_property("sClsId",&LogQueryRes::sClsId);
			_e.add_static_property("sClsName",&LogQueryRes::sClsName);
			_e.add_static_property("sSignId",&LogQueryRes::sSignId);
		}
	};

	class LogQueryReq final: public FastNet::Message {
	public:
		DefStruct("pkt.protocols.LogQueryReq",4152272566,605709401)
		String key="";
		UInt32 beginTime=0;
		UInt32 endTime=0;
		UInt32 appId=0;

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(key);
			stream.read(beginTime);
			stream.read(endTime);
			stream.read(appId);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(key);
			stream.write(beginTime);
			stream.write(endTime);
			stream.write(appId);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,key);
			CalcSerializeSize(size,beginTime);
			CalcSerializeSize(size,endTime);
			CalcSerializeSize(size,appId);
			return size;
		}

		virtual void Reset() override{
			key="";
			beginTime=0;
			endTime=0;
			appId=0;
		}

		static void Export(){
			boost::python::class_<LogQueryReq,boost::python::bases<FastNet::Message>,boost::shared_ptr<LogQueryReq>,boost::noncopyable> _e("LogQueryReq");
			boost::python::scope _s = _e;
			_e.def_readwrite("key",&LogQueryReq::key);
			_e.def_readwrite("beginTime",&LogQueryReq::beginTime);
			_e.def_readwrite("endTime",&LogQueryReq::endTime);
			_e.def_readwrite("appId",&LogQueryReq::appId);
			_e.add_static_property("sClsId",&LogQueryReq::sClsId);
			_e.add_static_property("sClsName",&LogQueryReq::sClsName);
			_e.add_static_property("sSignId",&LogQueryReq::sSignId);
		}
	};


} //end namespace protocols
} //end namespace pkt
