#pragma once

//#include "FastNet/role/Role.h"
#include "FastNet/store/Store.h"

namespace FastNet {

	class Role;

	class FASTNET_API RoleModule :public Store {

	public:

		RoleModule(PyObject* obj, const String& clsName, boost::shared_ptr<Role> role);

		virtual ~RoleModule();

		boost::shared_ptr<Role> GetRole() const;

		virtual void OnRoleLogin() {}
		virtual void OnRoleLogout() {}
		virtual void OnRoleDisconnect() {}
		virtual void OnRoleReconnect() {}

	private:

		virtual void Cache() final;
		virtual std::shared_ptr<StoreInfo> Flush() final;

	private:
		const String m_roleId;
		const String m_clsName;
	};

	typedef boost::shared_ptr<RoleModule> RoleModulePtr;
}