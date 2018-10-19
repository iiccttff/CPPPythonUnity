#pragma once

#include "FastNet/role/Role.h"
#include "FastNet/role/RoleModule.h"
#include "FastNet/global/Global.h"
#include "FastNet/timer/Timer.h"
#include "FastNet/core/Singleton.h"

namespace FastNet {

	class FASTNET_API StoreManager final: public Singleton<StoreManager>{
	public:

		StoreManager();

		virtual ~StoreManager();

		mongocxx::database GetDatabase();

		void OnCreate();
		void OnDestory();

		std::set<String> GetRoleIds(const String& uid);
		std::vector<String> GetRoleIds_Python(const String& uid);

		static String AccountToUid(const String& account,const String& channel);

		void ReloadCfgs();

	private:
		void run();

		friend class App;
		friend class Role;
		friend class StoreRead;
		friend class StoreWrite;
		friend class RoleManager;
		friend class GlobalManager;

		void Add(StorePtr store);
		void AddStoreInfo(Store*);
		void AddDeleteStore(Store*);

		void AddRoleId(const String& uid, const String& roleId);

	private:
		std::list<ObjectWeakRef > m_stores;

		std::mutex m_mutex;
		Poco::Thread m_thread;
		bool m_run = false;

		
		std::shared_ptr<mongocxx::client> m_mongocxxClient;

		std::set<String> m_collectionNames;

		TimerPtr m_timerSave;

		std::queue<std::shared_ptr<Store::StoreInfo> > m_storeItems;
	};

}
