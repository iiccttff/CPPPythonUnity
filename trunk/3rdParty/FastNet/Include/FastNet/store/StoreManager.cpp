


#include "StoreManager.h"
#include "FastNet/core/App.h"
#include "Poco/MD5Engine.h"

namespace FastNet {
	extern boost::python::object JsonConfigs;

	extern std::string g_mongodbUri;
	extern std::string g_mongodbDB;

	extern boost::python::object g_callMethod;

	StoreManager::StoreManager() {
		using bsoncxx::builder::basic::make_document;

		
		m_mongocxxClient = bsoncxx::stdx::make_unique<mongocxx::client>(mongocxx::uri(g_mongodbUri));
		auto db = m_mongocxxClient->database(g_mongodbDB);

		for (auto& v : db.list_collections()) {
			m_collectionNames.emplace(v["name"].get_utf8().value.to_string());
		}

		m_run = true;
		m_thread.setName("StoreManager");
		m_thread.startFunc(std::bind(&StoreManager::run, this));
	}

	StoreManager::~StoreManager() {
		
	}

	mongocxx::database StoreManager::GetDatabase() {
		return m_mongocxxClient->database(g_mongodbDB);
	}

	void StoreManager::OnCreate() {


		m_timerSave = App::Instance().CreateTimer([this]() {

			std::vector<decltype(m_stores.begin())> removeStores;
			auto now = std::time(nullptr);
			std::unique_lock<std::mutex> ul(m_mutex);
			for (auto itStore=m_stores.begin();itStore != m_stores.end();itStore++)
			{
				auto storePtr = itStore->Get<Store>();
				if (storePtr) {
					if (storePtr->GetExpireTime() <= now) {
						storePtr->SetExpireTime(now + 7200);

						auto si = storePtr->Flush();
						if (si) {
							m_storeItems.emplace(si);
						}
					}
				}
				else {
					removeStores.emplace_back(itStore);
				}
			}

			for (auto& v : removeStores) {
				m_stores.erase(v);
			}
		});

		m_timerSave->Start(30000);
	}

	void StoreManager::OnDestory() {

		

		m_run = false;
		if (m_thread.isRunning()) {
			m_thread.join();
		}

		m_mongocxxClient.reset();
		

		m_timerSave->Stop();
		m_timerSave = nullptr;
	}

	void StoreManager::ReloadCfgs() {
		for (auto itStore = m_stores.begin();itStore != m_stores.end();itStore++)
		{
			auto storePtr = itStore->Get<Store>();
			if (storePtr) {

				try {
					storePtr->OnReloadCfg();
				}
				catch (std::exception& e) {
					LogException("StoreManager::ReloadCfgs %s",e.what());
				}

				g_callMethod(boost::python::borrowed(storePtr->GetObject()), "OnReloadCfg");
			}
		}
	}

	void StoreManager::AddStoreInfo(Store* storePtr) {
		auto si = storePtr->Flush();
		if (si) {
			std::unique_lock<std::mutex> ul(m_mutex);
			m_storeItems.emplace(si);
		}
	}

	void StoreManager::AddDeleteStore(Store* storePtr) {

		auto si = std::make_shared<Store::StoreInfo>();
		si->name = storePtr->CollName();
		si->id = storePtr->Id();
		si->del = true;

		std::unique_lock<std::mutex> ul(m_mutex);
		m_storeItems.emplace(si);
	}

	void StoreManager::Add(StorePtr store) {

		if (m_collectionNames.emplace(store->CollName()).second) {
			try {
				auto db = GetDatabase();
				mongocxx::options::index index_options{};
				index_options.unique(true);

				using bsoncxx::builder::basic::kvp;
				db[store->CollName()].create_index(bsoncxx::builder::basic::make_document(kvp("id", 1)), index_options);
			}
			catch (std::exception& e) {
				LogException("StoreManager::Add %s", e.what());
			}
		}

		m_stores.emplace_back(store.get());
		
		store->Cache();
	}

	void StoreManager::run() {

		using bsoncxx::builder::basic::kvp;
		using bsoncxx::builder::stream::open_document;
		using bsoncxx::builder::stream::close_document;
		using bsoncxx::builder::basic::make_document;

		auto mongocxxClient = bsoncxx::stdx::make_unique<mongocxx::client>(mongocxx::uri(g_mongodbUri));
		auto db = mongocxxClient->database(g_mongodbDB);

		mongocxx::options::update update;
		update.upsert(true);

		auto doSave = [this,&db,&update]() {
			
			std::unique_lock<std::mutex> ul(m_mutex);
			if (m_storeItems.empty()) {
				return;
			}

			auto storeItems(std::move(m_storeItems));
			ul.unlock();

			while (!storeItems.empty()) {
				auto item = storeItems.front();
				storeItems.pop();
				if (item) {
						
					try {
						if (item->del) {
							db[item->name].delete_one(make_document(kvp("id", bsoncxx::types::b_utf8{ item->id })));

						}else if (!item->doc.view().empty()) {
							db[item->name].update_one(
								make_document(kvp("id", bsoncxx::types::b_utf8{ item->id })),
								make_document(kvp("$set", item->doc.view())), update);
						}
					}
					catch (std::exception& e) {
						LogException("StoreManager::doSave %s", e.what());
					}
				}
			}	
		};

		while (m_run) {
			std::this_thread::sleep_for(std::chrono::milliseconds(1000));
			doSave();	
		}
		
		try {
			doSave();
		}
		catch (std::exception& e) {
			LogException("StoreManager::run %s", e.what());
		}
	}

	void StoreManager::AddRoleId(const String& uid, const String& roleId)
	{
		using bsoncxx::builder::basic::kvp;
		using bsoncxx::builder::basic::make_document;
		using bsoncxx::builder::stream::close_document;
		using bsoncxx::builder::stream::open_document;

		try {

			mongocxx::options::update update;
			update.upsert(true);

			auto db = m_mongocxxClient->database(g_mongodbDB);
			db["roles"].update_one(make_document(kvp("id", bsoncxx::types::b_utf8{ roleId }) ), 
				make_document(
					kvp("$set",
						make_document(
							kvp("uid", bsoncxx::types::b_utf8{ uid }))
					)
				)
				, update);
		}
		catch (std::exception& e) {
			LogException("StoreManager::AddRoleId %s", e.what());
		}
	}


	std::set<String> StoreManager::GetRoleIds(const String& uid) {

		using bsoncxx::builder::basic::kvp;
		using bsoncxx::builder::basic::make_document;

		std::set<String> ret;
		try {
			mongocxx::options::find opts;
			opts.projection(make_document(kvp("id", 1)));

			auto db = m_mongocxxClient->database(g_mongodbDB);
			auto cursor = db["roles"].find(make_document(kvp("uid", uid)), opts);
			for (auto&& v : cursor) {
				ret.emplace(v["id"].get_utf8().value.to_string());
			}
		}
		catch (std::exception& e) {
			LogException("StoreManager::GetRoleIds %s", e.what());
		}

		return ret;
	}

	std::vector<String> StoreManager::GetRoleIds_Python(const String& uid) {
		std::vector<String> ret;
		auto roleIds = GetRoleIds(uid);
		for (auto& v : roleIds) {
			ret.emplace_back(v);
		}
		return ret;
	}

	String StoreManager::AccountToUid(const String& account, const String& channel) {
		Poco::MD5Engine engine;
		engine.update(account + "_" + channel);
		return Poco::DigestEngine::digestToHex(engine.digest());
	}

}
