#pragma once

#include "FastNet/global/Global.h"
#include "FastNet/core/Singleton.h"

namespace FastNet {

	class FASTNET_API GlobalManager final:public Singleton<GlobalManager> {
	public:

		GlobalManager();

		virtual ~GlobalManager();

		void OnDestory();
			
		void RegisterGlobal(const String& name, boost::python::object clsGlobal);
		GlobalPtr GetGlobal(const String& name);

		//角色相关事件
		void RoleLogin(RolePtr role);
		void RoleLogout(RolePtr role);
		void RoleDisconnect(RolePtr role);
		void RoleReconnect(RolePtr role);

	private:
		std::unordered_map<String, GlobalPtr> m_globals;
	};

}
