#include "Global.h"
#include "FastNet/core/Log.h"

namespace FastNet {
	extern boost::python::object g_callMethod;

	Global::Global(PyObject* obj,const String& name)
		:Store(obj, "globals", name){

	}

	void Global::Cache() {
		try {
			auto doc = GetColl();
			if (doc) {
				auto sr = boost::make_shared<StoreRead>(doc);
				this->OnCache(sr);

				g_callMethod(boost::python::borrowed(m_obj), "OnCache", boost::python::make_tuple(sr));
				//boost::python::call_method<void>(m_obj, "OnCache", sr);
			}
		}
		catch (std::exception& e) {
			LogException("Global::Cache %s", e.what());
		}
		PythonCallbackException
	}

	std::shared_ptr<Store::StoreInfo> Global::Flush() {


		try {
			auto ret = std::make_shared<Store::StoreInfo>();
			ret->name = CollName();
			ret->id = Id();
			auto sw = boost::make_shared<StoreWrite>(ret->doc);
			this->OnFlush(sw);
			//boost::python::call_method<void>(m_obj, "OnFlush", sw);
			g_callMethod(boost::python::borrowed(m_obj), "OnFlush", boost::python::make_tuple(sw));
			return ret;
		}
		catch (std::exception& e) {
			LogException("Global::OnFlush %s", e.what());
		}
		PythonCallbackException
		return nullptr;
	}
}