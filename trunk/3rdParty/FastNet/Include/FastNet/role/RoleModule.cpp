#include "RoleModule.h"

#include "FastNet/store/StoreManager.h"
#include "FastNet/role/Role.h"
#include "FastNet/core/Log.h"
#include "FastNet/role/RoleManager.h"

namespace FastNet {
	extern boost::python::object JsonConfigs;
	extern boost::python::object g_callMethod;

	RoleModule::RoleModule(PyObject* obj, const String& clsName, RolePtr role)
		:Store(obj, String("rolemodule_") + clsName, role->Id()), m_roleId(role->Id()) ,m_clsName(clsName){

	}

	RoleModule::~RoleModule() {

	}

	RolePtr RoleModule::GetRole() const {
		auto instance = RoleManager::Instance();
		if (instance) {
			return instance->GetRole(m_roleId, "", false);
		}
		else {
			return nullptr;
		}
	}

	using bsoncxx::builder::basic::kvp;
	using bsoncxx::builder::basic::make_document;
	using bsoncxx::builder::stream::open_document;
	using bsoncxx::builder::stream::close_document;

	void RoleModule::Cache() {

		try {
			auto doc = GetColl();

			if (doc) {
				auto itDoc = doc->view().find(m_roleId);
				if (doc->view().end() != itDoc) {
					bsoncxx::stdx::optional<bsoncxx::document::value> moduleDoc(itDoc->get_document());
					auto sr = boost::make_shared<StoreRead>(moduleDoc);
					this->OnCache(sr);

					g_callMethod(boost::python::borrowed(m_obj), "OnCache", boost::python::make_tuple(sr));
					//boost::python::call_method<void>(m_obj, "OnCache", sr);
				}
			}
		}
		catch (std::exception& e) {
			LogException("RoleModule::Cache %s", e.what());
		}
		PythonCallbackException
	}

	std::shared_ptr<Store::StoreInfo> RoleModule::Flush() {

		try {
			auto ret = std::make_shared<Store::StoreInfo>();
			ret->name = CollName();
			ret->id = Id();
			//ret->doc << m_clsName << open_document;
			auto sw = boost::make_shared<StoreWrite>(ret->doc);
			this->OnFlush(sw);
			g_callMethod(boost::python::borrowed(m_obj), "OnFlush", boost::python::make_tuple(sw));
			//boost::python::call_method<void>(m_obj, "OnFlush", sw);
			//ret->doc << close_document;
			return ret;
		}
		catch (std::exception& e) {
			LogException("RoleModule::Flush %s", e.what());
		}
		PythonCallbackException
		return nullptr;
	}
}
