#pragma once
#include "FastNet/core/ClassFactory.h"
#include "FastNet/core/Stream.h"
#include "FastNet/core/App.h"
#include "FastNet/core/Cfg.h"


namespace pkt{
namespace common{

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
	class AccountVerifySucceedRes final: public FastNet::Message {
	public:
		DefStruct("pkt.common.AccountVerifySucceedRes",3008152104,2568140703)
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
			boost::python::class_<AccountVerifySucceedRes,boost::python::bases<FastNet::Message>,boost::shared_ptr<AccountVerifySucceedRes>,boost::noncopyable> _e("AccountVerifySucceedRes");
			boost::python::scope _s = _e;
			_e.def_readwrite("roleId",&AccountVerifySucceedRes::roleId);
			_e.add_static_property("sClsId",&AccountVerifySucceedRes::sClsId);
			_e.add_static_property("sClsName",&AccountVerifySucceedRes::sClsName);
			_e.add_static_property("sSignId",&AccountVerifySucceedRes::sSignId);
		}
	};

	class GotoServerTokenRes final: public FastNet::Message {
	public:
		DefStruct("pkt.common.GotoServerTokenRes",1234268567,2568140703)
		String toekn="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(toekn);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(toekn);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,toekn);
			return size;
		}

		virtual void Reset() override{
			toekn="";
		}

		static void Export(){
			boost::python::class_<GotoServerTokenRes,boost::python::bases<FastNet::Message>,boost::shared_ptr<GotoServerTokenRes>,boost::noncopyable> _e("GotoServerTokenRes");
			boost::python::scope _s = _e;
			_e.def_readwrite("toekn",&GotoServerTokenRes::toekn);
			_e.add_static_property("sClsId",&GotoServerTokenRes::sClsId);
			_e.add_static_property("sClsName",&GotoServerTokenRes::sClsName);
			_e.add_static_property("sSignId",&GotoServerTokenRes::sSignId);
		}
	};

	class RoleLoginSucceedRes final: public FastNet::Message {
	public:
		DefStruct("pkt.common.RoleLoginSucceedRes",2771882275,4068542651)
		String roleId="";
		String tabs="";
		String name="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(roleId);
			stream.read(tabs);
			stream.read(name);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(roleId);
			stream.write(tabs);
			stream.write(name);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,roleId);
			CalcSerializeSize(size,tabs);
			CalcSerializeSize(size,name);
			return size;
		}

		virtual void Reset() override{
			roleId="";
			tabs="";
			name="";
		}

		static void Export(){
			boost::python::class_<RoleLoginSucceedRes,boost::python::bases<FastNet::Message>,boost::shared_ptr<RoleLoginSucceedRes>,boost::noncopyable> _e("RoleLoginSucceedRes");
			boost::python::scope _s = _e;
			_e.def_readwrite("roleId",&RoleLoginSucceedRes::roleId);
			_e.def_readwrite("tabs",&RoleLoginSucceedRes::tabs);
			_e.def_readwrite("name",&RoleLoginSucceedRes::name);
			_e.add_static_property("sClsId",&RoleLoginSucceedRes::sClsId);
			_e.add_static_property("sClsName",&RoleLoginSucceedRes::sClsName);
			_e.add_static_property("sSignId",&RoleLoginSucceedRes::sSignId);
		}
	};

	class AnyReq final: public FastNet::Message {
	public:
		DefStruct("pkt.common.AnyReq",1862303533,3742882662)
		String classId="";
		String data="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(classId);
			stream.read(data);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(classId);
			stream.write(data);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,classId);
			CalcSerializeSize(size,data);
			return size;
		}

		virtual void Reset() override{
			classId="";
			data="";
		}

		static void Export(){
			boost::python::class_<AnyReq,boost::python::bases<FastNet::Message>,boost::shared_ptr<AnyReq>,boost::noncopyable> _e("AnyReq");
			boost::python::scope _s = _e;
			_e.def_readwrite("classId",&AnyReq::classId);
			_e.def_readwrite("data",&AnyReq::data);
			_e.add_static_property("sClsId",&AnyReq::sClsId);
			_e.add_static_property("sClsName",&AnyReq::sClsName);
			_e.add_static_property("sSignId",&AnyReq::sSignId);
		}
	};

	class AnyRes final: public FastNet::Message {
	public:
		DefStruct("pkt.common.AnyRes",2165186049,3742882662)
		String classId="";
		String data="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(classId);
			stream.read(data);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(classId);
			stream.write(data);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,classId);
			CalcSerializeSize(size,data);
			return size;
		}

		virtual void Reset() override{
			classId="";
			data="";
		}

		static void Export(){
			boost::python::class_<AnyRes,boost::python::bases<FastNet::Message>,boost::shared_ptr<AnyRes>,boost::noncopyable> _e("AnyRes");
			boost::python::scope _s = _e;
			_e.def_readwrite("classId",&AnyRes::classId);
			_e.def_readwrite("data",&AnyRes::data);
			_e.add_static_property("sClsId",&AnyRes::sClsId);
			_e.add_static_property("sClsName",&AnyRes::sClsName);
			_e.add_static_property("sSignId",&AnyRes::sSignId);
		}
	};


} //end namespace common
} //end namespace pkt
