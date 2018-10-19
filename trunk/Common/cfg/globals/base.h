#pragma once
#include "FastNet/core/ClassFactory.h"
#include "FastNet/core/Stream.h"
#include "FastNet/core/App.h"
#include "FastNet/core/Cfg.h"


namespace cfg{
namespace globals{
namespace base{

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
	struct Language final: public FastNet::Struct,FastNet::Cfg<Language,FastNet::UInt32> {
		bool operator==(Language const& ) const { return false; }
		bool operator!=(Language const& ) const { return true; }
		DefStruct("cfg.globals.base.Language",1162455557,201825498)
		UInt32 id=0;
		String text="";

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(id);
			stream.read(text);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(id);
			stream.write(text);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,id);
			CalcSerializeSize(size,text);
			return size;
		}

		static void Export(){
			boost::python::class_<Language,boost::python::bases<FastNet::Struct>,boost::shared_ptr<Language>,boost::noncopyable> _e("Language");
			FastNet::App::AddCfgReloadCallback(&Language::Reload);
			FastNet::App::AddCfgInitCallback(&Language::Init);
			FastNet::App::RegisterStlVector<std::vector<boost::shared_ptr<Language> > >("v_2784968950");
			Language::ExportCfg(_e,"cfg/globals/base/Language.bytes");
			boost::python::scope _s = _e;
			_e.def_readwrite("id",&Language::id);
			_e.def_readwrite("text",&Language::text);
			_e.add_static_property("sClsId",&Language::sClsId);
			_e.add_static_property("sClsName",&Language::sClsName);
			_e.add_static_property("sSignId",&Language::sSignId);
		}
	};

	struct ErrorCode final: public FastNet::Struct,FastNet::Cfg<ErrorCode,FastNet::String> {
		bool operator==(ErrorCode const& ) const { return false; }
		bool operator!=(ErrorCode const& ) const { return true; }
		DefStruct("cfg.globals.base.ErrorCode",576514151,3742882662)
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

		static void Export(){
			boost::python::class_<ErrorCode,boost::python::bases<FastNet::Struct>,boost::shared_ptr<ErrorCode>,boost::noncopyable> _e("ErrorCode");
			FastNet::App::AddCfgReloadCallback(&ErrorCode::Reload);
			FastNet::App::AddCfgInitCallback(&ErrorCode::Init);
			FastNet::App::RegisterStlVector<std::vector<boost::shared_ptr<ErrorCode> > >("v_101252395");
			ErrorCode::ExportCfg(_e,"cfg/globals/base/ErrorCode.bytes");
			boost::python::scope _s = _e;
			_e.def_readwrite("key",&ErrorCode::key);
			_e.def_readwrite("msg",&ErrorCode::msg);
			_e.add_static_property("sClsId",&ErrorCode::sClsId);
			_e.add_static_property("sClsName",&ErrorCode::sClsName);
			_e.add_static_property("sSignId",&ErrorCode::sSignId);
		}
	};

	struct Items final: public FastNet::Struct,FastNet::Cfg<Items,FastNet::UInt32> {
		bool operator==(Items const& ) const { return false; }
		bool operator!=(Items const& ) const { return true; }
		DefStruct("cfg.globals.base.Items",998444613,2040317094)
		UInt32 id=0;
		boost::shared_ptr<Language> name;

		virtual void Deserialize(FastNet::StreamRead& stream) {
			stream.read(id);
			stream.read(name);
		}

		virtual void Serialize(FastNet::StreamWrite& stream) {
			stream.write(id);
			stream.write(name);
		}

		virtual FastNet::UInt32 SerializeSize() override{
			FastNet::UInt32 size(0);
			CalcSerializeSize(size,id);
			CalcSerializeSize(size,name);
			return size;
		}

		static void Export(){
			boost::python::class_<Items,boost::python::bases<FastNet::Struct>,boost::shared_ptr<Items>,boost::noncopyable> _e("Items");
			FastNet::App::AddCfgReloadCallback(&Items::Reload);
			FastNet::App::AddCfgInitCallback(&Items::Init);
			FastNet::App::RegisterStlVector<std::vector<boost::shared_ptr<Items> > >("v_3121021058");
			Items::ExportCfg(_e,"cfg/globals/base/Items.bytes");
			boost::python::scope _s = _e;
			_e.def_readwrite("id",&Items::id);
			_e.def_readwrite("name",&Items::name);
			_e.add_static_property("sClsId",&Items::sClsId);
			_e.add_static_property("sClsName",&Items::sClsName);
			_e.add_static_property("sSignId",&Items::sSignId);
		}
	};


} //end namespace globals
} //end namespace base
} //end namespace cfg
