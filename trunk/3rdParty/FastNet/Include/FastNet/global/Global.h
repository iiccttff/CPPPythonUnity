#pragma once

#include "FastNet/store/Store.h"
#include "FastNet/role/Role.h"


namespace FastNet {

	class FASTNET_API Global :public Store {
	public:

		Global(PyObject* obj,const String& name);

		virtual ~Global() = default;

		virtual void OnCreate() {}
		virtual void OnDestory() {}


		virtual void Cache() final;
		virtual  std::shared_ptr<StoreInfo> Flush() final;

		//角色相关事件
		virtual void OnRoleLogin(RolePtr role) {}
		virtual void OnRoleLogout(RolePtr role) {}
		virtual void OnRoleDisconnect(RolePtr role) {}
		virtual void OnRoleReconnect(RolePtr role) {}

	private:
	};

	typedef boost::shared_ptr<Global> GlobalPtr;


}