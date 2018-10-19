
#include "Role.h"
#include "RoleModule.h"
#include "FastNet/global/GlobalManager.h"
#include "FastNet/store/StoreManager.h"
#include "FastNet/core/Session.h"
#include "FastNet/room/RoomManager.h"


namespace FastNet {

	extern boost::python::object JsonConfigs;
	extern boost::python::object g_callMethod;

	Role::Role(PyObject* obj, const String& id):Store(obj, "roles", id){
		m_createTime = std::time(nullptr);
		m_lastLoginTime = m_createTime;
		m_lastLogoutTime = m_createTime;
		m_status = Status::Offline;
	}

	Role::~Role() {
		
	}

	bool Role::AddModule(const String& name, boost::shared_ptr<RoleModule> module) {
		auto itModule = m_modules.find(name);
		if (m_modules.end() != itModule) {
			return false;
		}
		else {
			m_modules.emplace(name,module);
			return true;
		}
	}

	boost::shared_ptr<RoleModule> Role::Module(const String& name) {
		auto itModule = m_modules.find(name);
		if (m_modules.end() != itModule) {
			return itModule->second;
		}
		else {
			return nullptr;
		}
	}


	const std::map<String, boost::shared_ptr<RoleModule> >& Role::Modules() {
		return m_modules;
	}

	std::map<String, boost::shared_ptr<RoleModule> > Role::Modules_Python() {
		return m_modules;
	}

	void Role::Cache() {
		try {	
			auto doc = GetColl();
			if (doc) {
				auto sr = boost::make_shared<StoreRead>(doc);
				m_uid = sr->ReadString("uid", "");
				m_channelId = sr->ReadString("channelId", "");
				m_frozenTime = sr->ReadUInt32("frozenTime", 0);
				m_createTime = sr->ReadUInt32("createTime", 0);
				m_lastLoginTime = sr->ReadUInt32("lastLoginTime", 0);
				m_lastLogoutTime = sr->ReadUInt32("lastLogoutTime", 0);

				this->OnCache(sr);
				g_callMethod(boost::python::borrowed(m_obj), "OnCache", boost::python::make_tuple(sr));
				//boost::python::call_method<void>(m_obj, "OnCache", sr);
			}
		}
		catch (std::exception& e) {
			LogException("Role::Cache %s", e.what());
		}
		PythonCallbackException
	}

	std::shared_ptr<Store::StoreInfo> Role::Flush() {

		try {
			auto ret = std::make_shared<Store::StoreInfo>();
			ret->name = CollName();
			ret->id = Id();
			auto sw = boost::make_shared<StoreWrite>(ret->doc);
			sw->WriteString("uid", m_uid);
			sw->WriteString("channelId", m_channelId);
			sw->WriteUInt32("frozenTime", m_frozenTime);
			sw->WriteUInt32("createTime", m_createTime);
			sw->WriteUInt32("lastLoginTime", m_lastLoginTime);
			sw->WriteUInt32("lastLogoutTime", m_lastLogoutTime);

			this->OnFlush(sw);
			g_callMethod(boost::python::borrowed(m_obj), "OnFlush", boost::python::make_tuple(sw));
			//boost::python::call_method<void>(m_obj, "OnFlush", sw);
			return ret;
		}
		catch (std::exception& e) {
			LogException("Role::OnFlush %s", e.what());
		}
		PythonCallbackException
		return nullptr;
	}

	void Role::Login(Object* session) {

		try {

			if (this->IsFrozen()) {
				return;
			}

			m_status = Status::Online;
			m_session = session;

			m_lastLoginTime = std::time(nullptr);

			this->OnLogin();

			//boost::python::call_method<void>(m_obj, "OnLogin");
			g_callMethod(boost::python::borrowed(m_obj), "OnLogin");

			for (auto& v : m_modules) {
				v.second->OnRoleLogin();

				g_callMethod(boost::python::borrowed(v.second->GetObject()) , "OnRoleLogin");
				//boost::python::call_method<void>(v.second->GetObject(), "OnRoleLogin");
			}

			RolePtr self = boost::python::extract<RolePtr>(GetObject());
			GlobalManager::Instance()->RoleLogin(self);
		}
		PythonCallbackException
	}

	void Role::Logout() {
		try {
			m_status = Status::Offline;

			m_lastLogoutTime = std::time(nullptr);

			for (auto& v : m_roomIds) {
				LeaveRoom(v);
			}

			RolePtr self = boost::python::extract<RolePtr>(GetObject());
			GlobalManager::Instance()->RoleLogout(self);

			g_callMethod(boost::python::borrowed(m_obj), "OnLogout");
			//boost::python::call_method<void>(m_obj, "OnLogout");

			this->OnLogout();

			for (auto& v : m_modules) {
				g_callMethod(boost::python::borrowed(v.second->GetObject()), "OnRoleLogout");
				//boost::python::call_method<void>(v.second->GetObject(), "OnRoleLogout");
				v.second->OnRoleLogout();
			}

			m_session = nullptr;
		}
		PythonCallbackException
	}

	void Role::Reconnect(Object* session) {
		try {

			if (this->IsFrozen()) {
				return;
			}

			m_status = Status::Online;
			m_session = session;

			m_lastLoginTime = std::time(nullptr);

			this->OnReconnect();

			g_callMethod(boost::python::borrowed(m_obj), "OnReconnect");
			//boost::python::call_method<void>(m_obj, "OnReconnect");

			for (auto& v : m_modules) {	
				v.second->OnRoleReconnect();
				//boost::python::call_method<void>(v.second->GetObject(), "OnRoleReconnect");
				g_callMethod(boost::python::borrowed(v.second->GetObject()), "OnRoleReconnect");
			}

			RolePtr self = boost::python::extract<RolePtr>(GetObject());
			GlobalManager::Instance()->RoleReconnect(self);
		}
		PythonCallbackException
	}

	void Role::Disconnect() {
		try {
			m_status = Status::WaitReconnect;

			m_lastLogoutTime = std::time(nullptr);

			RolePtr self = boost::python::extract<RolePtr>(GetObject());
			GlobalManager::Instance()->RoleDisconnect(self);

			for (auto& v : m_modules) {
				//boost::python::call_method<void>(v.second->GetObject(), "OnRoleDisconnect");
				g_callMethod(boost::python::borrowed(v.second->GetObject()), "OnRoleDisconnect");
				v.second->OnRoleDisconnect();
			}

			g_callMethod(boost::python::borrowed(m_obj), "OnDisconnect");
			//boost::python::call_method<void>(m_obj, "OnDisconnect");

			this->OnDisconnect();
			m_session = nullptr;	

		}
		PythonCallbackException
	}

	UInt32 Role::CreateTime() const {
		return m_createTime;
	}

	UInt32 Role::LastLoginTime() const {
		return m_lastLoginTime;
	}

	UInt32 Role::LastLogoutTime() const {
		return m_lastLogoutTime;
	}

	UInt32 Role::Level() const {
		return m_level;
	}

	void Role::SetLevel(UInt32 level) {
		m_level = level;
	}

	Session* Role::GetSession() {
		return m_session.Get<Session>();
	}

	boost::python::object Role::GetSession_Python() {
		auto session = m_session.Get();
		if (session) {
			return boost::python::object(boost::python::detail::borrowed_reference(session->GetObject()));
		}
		else {
			return boost::python::object();
		}
	}

	const String Role::UserId() const {
		return m_uid;
	}

	void Role::SetUserId(const String& uid) {
		m_uid = uid;
	}

	const String Role::ChannelId() const {
		return m_channelId;
	}

	void Role::SetChannelId(const String& channelId) {
		m_channelId = channelId;
	}

	void Role::Frozen(UInt32 time) {
		m_frozenTime = time;
	}

	bool Role::IsFrozen() const {
		return m_frozenTime != 0;
	}

	UInt32 Role::FrozenTime() const {
		return m_frozenTime;
	}


	Role::Status Role::GetStatus() const {
		return m_status;
	}

	void Role::Destory(bool del) {

		if (!del) {
			StoreManager::Instance()->AddStoreInfo(this);

			for (auto& v : m_modules) {
				StoreManager::Instance()->AddStoreInfo(v.second.get());
			}
		}
		else {
			StoreManager::Instance()->AddDeleteStore(this);
		}

		m_modules.clear();
	}


	void Role::JoinRoom(UInt32 id) {
		auto itSession = m_roomIds.find(id);
		if (m_roomIds.end() == itSession) {
			auto room = RoomManager::Instance()->GetRoom(id);
			if (room) {
				RolePtr self = boost::python::extract<RolePtr>(m_obj);
				room->Join(self);
				m_roomIds.emplace(id);
			}
		}
		else {
			LogError("Role::JoinRoom roleId£º%s repeat join roomId:%d", m_id.c_str(), id);
		}

	}

	void Role::ReadyRoom(UInt32 id) {
		auto itSession = m_roomIds.find(id);
		if (m_roomIds.end() == itSession) {
			LogError("Role::ReadyRoom roleId£º%s no find roomId:%d", m_id.c_str(), id);
		}
		else {
			auto room = RoomManager::Instance()->GetRoom(id);
			if (room) {
				room->Ready(m_id);
			}
		}
	}

	void Role::LeaveRoom(UInt32 id) {
		auto itSession = m_roomIds.find(id);
		if (m_roomIds.end() == itSession) {
			LogError("Role::LeaveRoom roleId£º%s no find roomId:%d", m_id.c_str(), id);
		}
		else {
			auto room = RoomManager::Instance()->GetRoom(id);
			if (room) {
				room->Leave(m_id);
			}
			m_roomIds.erase(itSession);
		}
	}

	void Role::SendRoomMsg(UInt32 id,const MessagePtr& message) {
		
		auto itSession = m_roomIds.find(id);
		if (m_roomIds.end() == itSession) {
			LogError("Role::SendRoomMsg roleId£º%s no find roomId:%d", m_id.c_str(), id);
		}
		else {
			auto room = RoomManager::Instance()->GetRoom(id);
			if (room) {
				room->SendMsg(message, m_id);
			}
		}
	}
}