#pragma once

#include "FastNet/role/Role.h"
#include "FastNet/core/Singleton.h"
#include "FastNet/timer/Timer.h"

namespace FastNet {

	class Session;

	class FASTNET_API RoleManager final: public Singleton<RoleManager> {
	public:
		RoleManager();
		virtual ~RoleManager();

		void Login(RolePtr role, Session* session);
		void Reconnect(RolePtr role, Session* session);
		void Logout(RolePtr role, Session* session);
		void Disconnect(RolePtr role, Session* session);

		RolePtr GetRole(const String& id, const String& name,bool fromDB = true);
		RolePtr GetRoleBySessionId(UInt32 sessionId);
			
		RolePtr CreateRole(const String& uid, const String& channel, const String& name);
		bool DeleteRole(const String& id,const String& name);

		void MulticastMessage(MessagePtr);

		void RegisterRole(const String& name,boost::python::object cls);
		void RegisterModule(const String& name,const String& module, boost::python::object cls);

		virtual void OnCreate();
		virtual void OnDestory();


	private:
		RolePtr LoadRole(const String& id, const String& name);
	private:

		std::unordered_map<UInt32,RolePtr> m_sessionRoles;
		std::unordered_map<String,RolePtr> m_cacheRoles;

		std::map<String, std::pair<boost::python::object,std::map<String, boost::python::object> > > m_roleCls;

		TimerPtr m_timerCheckTimeout;
	};


}
