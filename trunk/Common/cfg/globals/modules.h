#pragma once
#include "FastNet/core/ClassFactory.h"
#include "FastNet/core/Stream.h"
#include "FastNet/core/App.h"
#include "FastNet/core/Cfg.h"


namespace cfg{
namespace globals{
namespace modules{

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
	struct NoticeMgr final: public FastNet::Struct,FastNet::Cfg<NoticeMgr,FastNet::String> {
		bool operator==(NoticeMgr const& ) const { return false; }
		bool operator!=(NoticeMgr const& ) const { return true; }
		DefStruct("cfg.globals.modules.NoticeMgr",692628191,3742882662)
		String name="";
		String key="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(name);
			stream.read(key);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(name);
			stream.write(key);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,name);
			CalcSerializeSize(size,key);
			return size;
		}

		static void Export(){
			boost::python::class_<NoticeMgr,boost::python::bases<FastNet::Struct>,boost::shared_ptr<NoticeMgr>,boost::noncopyable> _e("NoticeMgr");
			FastNet::App::AddCfgReloadCallback(&NoticeMgr::Reload);
			FastNet::App::AddCfgInitCallback(&NoticeMgr::Init);
			FastNet::App::RegisterStlVector<std::vector<boost::shared_ptr<NoticeMgr> > >("v_3399128793");
			NoticeMgr::ExportCfg(_e,"cfg/globals/modules/NoticeMgr.bytes");
			boost::python::scope _s = _e;
			_e.def_readwrite("name",&NoticeMgr::name);
			_e.def_readwrite("key",&NoticeMgr::key);
			_e.add_static_property("sClsId",&NoticeMgr::sClsId);
			_e.add_static_property("sClsName",&NoticeMgr::sClsName);
			_e.add_static_property("sSignId",&NoticeMgr::sSignId);
		}
	};

	struct PlatformMgr final: public FastNet::Struct,FastNet::Cfg<PlatformMgr,FastNet::String> {
		bool operator==(PlatformMgr const& ) const { return false; }
		bool operator!=(PlatformMgr const& ) const { return true; }
		DefStruct("cfg.globals.modules.PlatformMgr",1674269620,3742882662)
		String name="";
		String key="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(name);
			stream.read(key);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(name);
			stream.write(key);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,name);
			CalcSerializeSize(size,key);
			return size;
		}

		static void Export(){
			boost::python::class_<PlatformMgr,boost::python::bases<FastNet::Struct>,boost::shared_ptr<PlatformMgr>,boost::noncopyable> _e("PlatformMgr");
			FastNet::App::AddCfgReloadCallback(&PlatformMgr::Reload);
			FastNet::App::AddCfgInitCallback(&PlatformMgr::Init);
			FastNet::App::RegisterStlVector<std::vector<boost::shared_ptr<PlatformMgr> > >("v_452881255");
			PlatformMgr::ExportCfg(_e,"cfg/globals/modules/PlatformMgr.bytes");
			boost::python::scope _s = _e;
			_e.def_readwrite("name",&PlatformMgr::name);
			_e.def_readwrite("key",&PlatformMgr::key);
			_e.add_static_property("sClsId",&PlatformMgr::sClsId);
			_e.add_static_property("sClsName",&PlatformMgr::sClsName);
			_e.add_static_property("sSignId",&PlatformMgr::sSignId);
		}
	};

	struct ServerMgr final: public FastNet::Struct,FastNet::Cfg<ServerMgr,FastNet::String> {
		bool operator==(ServerMgr const& ) const { return false; }
		bool operator!=(ServerMgr const& ) const { return true; }
		DefStruct("cfg.globals.modules.ServerMgr",920194243,3742882662)
		String name="";
		String key="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(name);
			stream.read(key);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(name);
			stream.write(key);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,name);
			CalcSerializeSize(size,key);
			return size;
		}

		static void Export(){
			boost::python::class_<ServerMgr,boost::python::bases<FastNet::Struct>,boost::shared_ptr<ServerMgr>,boost::noncopyable> _e("ServerMgr");
			FastNet::App::AddCfgReloadCallback(&ServerMgr::Reload);
			FastNet::App::AddCfgInitCallback(&ServerMgr::Init);
			FastNet::App::RegisterStlVector<std::vector<boost::shared_ptr<ServerMgr> > >("v_3574280389");
			ServerMgr::ExportCfg(_e,"cfg/globals/modules/ServerMgr.bytes");
			boost::python::scope _s = _e;
			_e.def_readwrite("name",&ServerMgr::name);
			_e.def_readwrite("key",&ServerMgr::key);
			_e.add_static_property("sClsId",&ServerMgr::sClsId);
			_e.add_static_property("sClsName",&ServerMgr::sClsName);
			_e.add_static_property("sSignId",&ServerMgr::sSignId);
		}
	};

	struct UserMgr final: public FastNet::Struct,FastNet::Cfg<UserMgr,FastNet::String> {
		bool operator==(UserMgr const& ) const { return false; }
		bool operator!=(UserMgr const& ) const { return true; }
		DefStruct("cfg.globals.modules.UserMgr",522108523,3742882662)
		String name="";
		String key="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(name);
			stream.read(key);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(name);
			stream.write(key);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,name);
			CalcSerializeSize(size,key);
			return size;
		}

		static void Export(){
			boost::python::class_<UserMgr,boost::python::bases<FastNet::Struct>,boost::shared_ptr<UserMgr>,boost::noncopyable> _e("UserMgr");
			FastNet::App::AddCfgReloadCallback(&UserMgr::Reload);
			FastNet::App::AddCfgInitCallback(&UserMgr::Init);
			FastNet::App::RegisterStlVector<std::vector<boost::shared_ptr<UserMgr> > >("v_602083920");
			UserMgr::ExportCfg(_e,"cfg/globals/modules/UserMgr.bytes");
			boost::python::scope _s = _e;
			_e.def_readwrite("name",&UserMgr::name);
			_e.def_readwrite("key",&UserMgr::key);
			_e.add_static_property("sClsId",&UserMgr::sClsId);
			_e.add_static_property("sClsName",&UserMgr::sClsName);
			_e.add_static_property("sSignId",&UserMgr::sSignId);
		}
	};

	struct DataQuery final: public FastNet::Struct,FastNet::Cfg<DataQuery,FastNet::String> {
		bool operator==(DataQuery const& ) const { return false; }
		bool operator!=(DataQuery const& ) const { return true; }
		DefStruct("cfg.globals.modules.DataQuery",1484661923,3742882662)
		String name="";
		String key="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(name);
			stream.read(key);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(name);
			stream.write(key);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,name);
			CalcSerializeSize(size,key);
			return size;
		}

		static void Export(){
			boost::python::class_<DataQuery,boost::python::bases<FastNet::Struct>,boost::shared_ptr<DataQuery>,boost::noncopyable> _e("DataQuery");
			FastNet::App::AddCfgReloadCallback(&DataQuery::Reload);
			FastNet::App::AddCfgInitCallback(&DataQuery::Init);
			FastNet::App::RegisterStlVector<std::vector<boost::shared_ptr<DataQuery> > >("v_3148617893");
			DataQuery::ExportCfg(_e,"cfg/globals/modules/DataQuery.bytes");
			boost::python::scope _s = _e;
			_e.def_readwrite("name",&DataQuery::name);
			_e.def_readwrite("key",&DataQuery::key);
			_e.add_static_property("sClsId",&DataQuery::sClsId);
			_e.add_static_property("sClsName",&DataQuery::sClsName);
			_e.add_static_property("sSignId",&DataQuery::sSignId);
		}
	};

	struct MailMgr final: public FastNet::Struct,FastNet::Cfg<MailMgr,FastNet::String> {
		bool operator==(MailMgr const& ) const { return false; }
		bool operator!=(MailMgr const& ) const { return true; }
		DefStruct("cfg.globals.modules.MailMgr",1879507711,3742882662)
		String name="";
		String key="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(name);
			stream.read(key);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(name);
			stream.write(key);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,name);
			CalcSerializeSize(size,key);
			return size;
		}

		static void Export(){
			boost::python::class_<MailMgr,boost::python::bases<FastNet::Struct>,boost::shared_ptr<MailMgr>,boost::noncopyable> _e("MailMgr");
			FastNet::App::AddCfgReloadCallback(&MailMgr::Reload);
			FastNet::App::AddCfgInitCallback(&MailMgr::Init);
			FastNet::App::RegisterStlVector<std::vector<boost::shared_ptr<MailMgr> > >("v_1291497156");
			MailMgr::ExportCfg(_e,"cfg/globals/modules/MailMgr.bytes");
			boost::python::scope _s = _e;
			_e.def_readwrite("name",&MailMgr::name);
			_e.def_readwrite("key",&MailMgr::key);
			_e.add_static_property("sClsId",&MailMgr::sClsId);
			_e.add_static_property("sClsName",&MailMgr::sClsName);
			_e.add_static_property("sSignId",&MailMgr::sSignId);
		}
	};


} //end namespace globals
} //end namespace modules
} //end namespace cfg
