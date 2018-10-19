#pragma once

#include "FastNet/core/Callback.h"
#include "FastNet/timer/TimerManager.h"
#include "FastNet/core/ClassFactory.h"
//#include "boost/thread/thread.hpp"
//#include "boost/thread/tss.hpp"

#include "boost/lockfree/queue.hpp"

#include "FastNet/role/Role.h"
#include "FastNet/global/Global.h"

namespace FastNet {

	class FASTNET_API App :
        public TimerManager {
		static bool IsExistsType(const std::type_info*);
	public:

		App(boost::python::object obj);

		virtual ~App();

		static App& Instance();

		void Start();
		void Stop();

		void Run();
		void Update();

		virtual void OnCreate();
		virtual void OnDestory();

		template <typename T>
		static void RegisterStlVector(const char* name) {

			if (!App::IsExistsType(&typeid(T))) {
				boost::python::class_<T>(name)
					.def(boost::python::vector_indexing_suite<T>());
			}
		}

		template <typename T, bool NoProxy = false>
		static void RegisterStlMap(const char* name) {
			if (!App::IsExistsType(&typeid(T))) {
				boost::python::class_<T>(name)
					.def(boost::python::map_indexing_suite<T, NoProxy>());
			}
		}

		static void AddResiterCallback(const char* moduleName, PyObject*(*initfunc)());
		static void AddCfgReloadCallback(void(*reloadfunc)());
		static void AddCfgInitCallback(void(*initfunc)(const std::string&));

		static void InitCfgs(const std::string&);
		static void InitCfgStructs();
		static void AddCfgStructs(const std::vector<std::string>& namespaces, const std::vector<std::string>& types, const std::string&  m);
		static void AddPktStructs(const std::vector<std::string>& namespaces, const std::vector<std::string>& types, const std::string&  m);

		static void ReloadCfgs();
		static void ExecutePythonCode(const std::string& code);

		virtual void OnPublish(UInt32 id, const String& message, bool isPublic) {}
		virtual void OnSubscribe(UInt32 id) {}
		virtual void OnUnsubscribe(UInt32 id) {}

		void OnCreateSubscribeClient(boost::python::object c);

		boost::python::object LoadJson(const String&);
		boost::python::object DumpJson(boost::python::object);


		bool GetFileData(const String& file,UInt32 offset,UInt32 size,Buffer& outBuffer);
		
		boost::python::object GetServer() { return m_server; }
		void SetServer(boost::python::object server) { m_server = server; }

		void UpdateSystemMemory
		(
			UInt64 total,
			UInt64 available,
			UInt32 percent,
			UInt64 used,
			UInt64 free,
			UInt64 rss,
			UInt64 vms,
			float memory_percent,
			float cpu_percent
		);

		const SystemMemoryInfo& GetSystemMemoryInfo() { return m_systemMemoryInfo; }

		static void AddCfgCachePyObject(UInt32 clsId, boost::python::list* keys, boost::python::list* vals);

	private:
		App(const App&) = delete;
		App& operator = (const App&) = delete;

		friend class Object;
		friend class Server;
		friend class Session;
		friend class Client;
		friend class TimerManager;

		boost::shared_ptr<TMInfo> GeTimerManager();

		void PushDestoryObject(PyObject*);
        void PushRecvMessage(Callback::Queue*);

	private:
        std::atomic<bool> m_run;
		std::atomic<UInt32> m_nextIoService;

        std::vector<boost::shared_ptr<TMInfo> > m_timerManagers;

		boost::lockfree::queue<PyObject*> m_queueDestory;

		boost::lockfree::queue<Callback::Queue*> m_queueRecv;
		boost::lockfree::queue<Callback::Queue*> m_queueRecovery;

		TimerPtr m_timerDestory;
		TimerPtr m_timerDispatch;
		TimerPtr m_timerCheckCache;

		std::mutex m_mutexTimerManager;

		std::unique_ptr<mongocxx::instance> m_mongocxxInstance;

		boost::asio::signal_set m_signals;

		boost::python::object m_loadJson, m_dumpJson;

		boost::python::object m_server;

		SystemMemoryInfo m_systemMemoryInfo;


		struct CacheFileInfo {
			UInt32 accessTime;
			boost::interprocess::file_mapping mapping;
			boost::interprocess::mapped_region region;

			Buffer buffer;
		};

		Poco::RWLock m_rwlockCacheFile;
		std::map<String, CacheFileInfo > m_cacheFiles;
	};
}
