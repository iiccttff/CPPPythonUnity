
#include "RoleManager.h"

#include "FastNet/store/StoreManager.h"
#include "FastNet/role/RoleModule.h"
#include "Poco/UUIDGenerator.h"
#include "Poco/MD5Engine.h"
#include "FastNet/core/Session.h"
#include "FastNet/core/Helper.h"

#include "Poco/Clock.h"

namespace FastNet {
	extern boost::python::object JsonConfigs;
	extern UInt32 g_appId;
	

	RoleManager::RoleManager() {


	}

	RoleManager::~RoleManager() {

	}

	void RoleManager::Login(RolePtr role, Session* session) {

		role->Login(session);
		m_sessionRoles.emplace(session->GetSessionId(), role);
	}

	void RoleManager::Reconnect(RolePtr role, Session* session) {
		role->Reconnect(session);
		m_sessionRoles.emplace(session->GetSessionId(), role);
	}

	void RoleManager::Logout(RolePtr role, Session* session) {
		if (role->GetSession() == session) {
			if (session) {
				m_sessionRoles.erase(session->GetSessionId());
			}

			role->Logout();
		}	
	}

	void RoleManager::Disconnect(RolePtr role, Session* session) {
		if (role->GetSession() == session) {
			if (session) {
				m_sessionRoles.erase(session->GetSessionId());
			}

			role->Disconnect();
		}
	}

	RolePtr RoleManager::LoadRole(const String& id, const String& name) {
		auto itRoleCls = m_roleCls.find(name);
		if (m_roleCls.end() == itRoleCls) {
			LogError("RoleManager::LoadRole role class '%s' no register!", name.c_str());
			return nullptr;
		}

		RolePtr role = boost::python::extract<RolePtr>(itRoleCls->second.first(id).ptr());
		if (role == nullptr) {
			LogError("RoleManager::LoadRole role class '%s' create fail!", name.c_str());
			return nullptr;
		}

		m_cacheRoles.emplace(id, role);
		StoreManager::Instance()->Add(role);

		auto& moduleCls = m_roleCls[name].second;
		for (auto& v : moduleCls) {
			boost::python::object module = v.second(v.first, role);
			RoleModulePtr roleModulePtr = boost::python::extract<RoleModulePtr>(module.ptr());
			StoreManager::Instance()->Add(roleModulePtr);

			role->AddModule(v.first, roleModulePtr);
		}

		return role;
	}

	RolePtr RoleManager::CreateRole(const String& uid , const String& channel, const String& name) {

		Double now = boost::python::extract<Double>(boost::python::import("time").attr("time")());
		String roleId;
		Poco::format(roleId,"%?i|%s|%?i" , g_appId, channel, UInt64(now*1000000));

		RolePtr role = LoadRole(roleId, name);
		role->SetUserId(uid);
		role->SetChannelId(channel);
		role->Save();
		StoreManager::Instance()->AddRoleId(uid, roleId);

		for (auto& v: role->Modules()) {
			v.second->Save();
		}

		return role;
	}

	bool RoleManager::DeleteRole(const String& id, const String& name) {
		auto role = RoleManager::GetRole(id, name, true);
		if (!role) {
			return false;
		}

		auto session = role->GetSession();
		if (session) {
			session->Stop();
		}

		role->Destory(true);
		m_cacheRoles.erase(role->Id());
		
		return true;
	}


	RolePtr RoleManager::GetRole(const String& id, const String& name, bool fromDB) {

		if (!id.empty()) {
			auto itRole = m_cacheRoles.find(id);
			if (m_cacheRoles.end() != itRole) {
				return itRole->second;
			}
			else {
				if (fromDB) {
					return LoadRole(id, name);
				}
				else {
					return nullptr;
				}
			}
		}
		else {
			return nullptr;
		}
	}

	void RoleManager::OnCreate() {

		m_timerCheckTimeout = App::Instance().CreateTimer([this]() {
			UInt32 now = std::time(nullptr);
			std::vector<RolePtr> removeRoles;

			for (auto& v: m_cacheRoles) {
				auto status = v.second->GetStatus();

				if ((now - v.second->LastLogoutTime())  > 30) {

					if (status == Role::Status::WaitReconnect) {
						RoleManager::Logout(v.second, v.second->GetSession());
					}
					else if (status == Role::Status::Offline && v.second.unique()) {
						removeRoles.emplace_back(v.second);
					}
				}
			}

			for (auto v : removeRoles) {
				v->Destory();
				m_cacheRoles.erase(v->Id());
			}
		});

		m_timerCheckTimeout->Start(5000);
	}

	void RoleManager::OnDestory() {
		m_timerCheckTimeout->Stop();
		m_timerCheckTimeout = nullptr;

		for (auto v : m_cacheRoles) {
			v.second->Destory();
		}

		m_cacheRoles.clear();
		m_sessionRoles.clear();
	}

	RolePtr RoleManager::GetRoleBySessionId(UInt32 sessionId) {
		auto itRole = m_sessionRoles.find(sessionId);
		if (m_sessionRoles.end() == itRole) {
			return nullptr;
		}
		else {
			return itRole->second;
		}
	}

	void RoleManager::MulticastMessage(MessagePtr message) {
		for (auto& v : m_sessionRoles) {
			auto session = v.second->GetSession();
			if (session) {
				session->SendMsg(message);
			}
		}
	}

	void RoleManager::RegisterRole(const String& name, boost::python::object cls) {
		auto itRoleCls = m_roleCls.find(name);
		if (m_roleCls.end() != itRoleCls) {
			LogError("RoleManager::RegisterRole rolename %s already exist!", name.c_str());
		}
		else {
			std::pair<boost::python::object, std::map<String, boost::python::object> > p;
			p.first = cls;
			m_roleCls.emplace(name, std::move(p));
		}
	}

	void RoleManager::RegisterModule(const String& name, const String& module, boost::python::object cls) {
		auto itRoleCls = m_roleCls.find(name);
		if (m_roleCls.end() == itRoleCls) {
			LogError("RoleManager::RegisterModule rolename %s no find!", name.c_str());
		}
		else {
			if (!itRoleCls->second.second.emplace(module, cls).second) {
				LogError("RoleManager::RegisterModule modulename %s:%s already exist!", name.c_str(), module.c_str());
			}
		}
	}


}
