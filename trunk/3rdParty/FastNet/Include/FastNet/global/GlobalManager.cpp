#include "GlobalManager.h"
#include "FastNet/core/Log.h"
#include "FastNet/store/StoreManager.h"
#include "FastNet/store/Store.h"

namespace FastNet {

	GlobalManager::GlobalManager() {

	}

	GlobalManager::~GlobalManager() {
		
	}

	void GlobalManager::OnDestory() {
		for (auto& v : m_globals) {
			StoreManager::Instance()->AddStoreInfo(v.second.get());

			try {
				boost::python::call_method<void>(v.second->GetObject(), "OnDestory");
				v.second->OnDestory();
			}
			catch (const std::exception& e)
			{
				LogException("GlobalManager::OnDestory %s", e.what());
			}
			PythonCallbackException
		}
		m_globals.clear();
	}

	void GlobalManager::RegisterGlobal(const String& name, boost::python::object clsGlobal) {

		if (m_globals.end() != m_globals.find(name)) {
			LogError("GlobalManager::RegisterGlobal %s already exist!", name.c_str());
		}
		else {	

			try {
				boost::python::object global = clsGlobal();

				GlobalPtr globalPtr = boost::python::extract<GlobalPtr>(global);
				m_globals.emplace(name, globalPtr);
				StoreManager::Instance()->Add(globalPtr);

				globalPtr->OnCreate();
				boost::python::call_method<void>(globalPtr->GetObject(), "OnCreate");
			}
			catch (const std::exception& e)
			{
				LogException("GlobalManager::RegisterGlobal %s", e.what());
			}
			PythonCallbackException
		}
	}

	GlobalPtr GlobalManager::GetGlobal(const String& name) {
		auto itGlobal = m_globals.find(name);
		if (m_globals.end() != itGlobal) {
			return itGlobal->second;
		}
		else {
			return nullptr;
		}
	}

	void GlobalManager::RoleLogin(RolePtr role) {
		for (auto& v : m_globals) {
			v.second->OnRoleLogin(role);
			boost::python::call_method<void>(v.second->GetObject(), "OnRoleLogin", role);
		}
	}

	void GlobalManager::RoleLogout(RolePtr role) {
		for (auto& v : m_globals) {
			boost::python::call_method<void>(v.second->GetObject(), "OnRoleLogout", role);
			v.second->OnRoleLogout(role);
		}
	}

	void GlobalManager::RoleDisconnect(RolePtr role) {
		for (auto& v : m_globals) {
			boost::python::call_method<void>(v.second->GetObject(), "OnRoleDisconnect", role);
			v.second->OnRoleDisconnect(role);
		}
	}

	void GlobalManager::RoleReconnect(RolePtr role) {
		for (auto& v : m_globals) {
			v.second->OnRoleReconnect(role);
			boost::python::call_method<void>(v.second->GetObject(), "OnRoleReconnect", role);
		}
	}
}
