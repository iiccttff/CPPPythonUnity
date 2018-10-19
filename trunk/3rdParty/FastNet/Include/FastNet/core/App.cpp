#include "App.h"
#include "Log.h"
#include "Server.h"
#include "Client.h"
#include "FastNet/pkt/protocols.h"

#include "Poco/Process.h"
#include "Poco/Environment.h"


#include "boost/interprocess/mapped_region.hpp"
#include "boost/interprocess/ipc/message_queue.hpp"


#include "FastNet/store/StoreManager.h"
#include "FastNet/room/RoomManager.h"
#include "FastNet/role/RoleManager.h"
#include "FastNet/global/GlobalManager.h"
#include "FastNet/role/RoleModule.h"

#include "FastNet/core/Helper.h"


#ifdef _WIN32
#include <time.h> 
#include <windows.h>  
#include <DbgHelp.h>

#pragma comment(lib, "DbgHelp.lib")

#ifdef _DEBUG
//#include "vld.h"
#endif

namespace FastNet {
	extern std::string g_workPath;
	extern std::string g_dataPath;
	extern boost::python::object g_callMethod;
	extern std::string g_mongodbUri;
	extern std::string g_mongodbDB;
	extern std::string g_projectName;

	extern std::atomic<UInt64> g_inputNet;
	extern std::atomic<UInt64> g_outputNet;
}

LONG WINAPI TopLevelFilter(struct _EXCEPTION_POINTERS *pExceptionInfo)
{ 
	LONG ret = EXCEPTION_CONTINUE_SEARCH;

	time_t  nowtime;
	time(&nowtime);
	struct tm *pTime = localtime(&nowtime);
	char szFile[256] = { 0 };
   
	sprintf(szFile, "%s/FastNet_%4d.%02d.%02d_%02d.%02d.%02d.dmp", FastNet::g_workPath.c_str(), pTime->tm_year + 1900, pTime->tm_mon + 1, pTime->tm_mday, pTime->tm_hour, pTime->tm_min, pTime->tm_sec);

	HANDLE hFile = ::CreateFileA(szFile, GENERIC_WRITE, FILE_SHARE_WRITE, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);

	if (hFile != INVALID_HANDLE_VALUE)
	{
		MINIDUMP_EXCEPTION_INFORMATION ExInfo;

		ExInfo.ThreadId = ::GetCurrentThreadId();
		ExInfo.ExceptionPointers = pExceptionInfo;
		ExInfo.ClientPointers = NULL;

		// write the dump  
		BOOL bOK = MiniDumpWriteDump(GetCurrentProcess(), GetCurrentProcessId(), hFile, MiniDumpNormal, &ExInfo, NULL, NULL);
		ret = EXCEPTION_EXECUTE_HANDLER;
		::CloseHandle(hFile);
	}

	return ret;
}

#endif

namespace FastNet {

	extern const std::type_info& s_typeSession;
	extern const std::type_info& s_typeClient;
    extern boost::python::object JsonConfigs;


	std::unique_ptr<std::vector<_inittab> > g_registerCallbacks;
	std::unique_ptr<std::vector<void(*)()> > g_reloadCfgCallbacks;
	std::unique_ptr<std::vector<void(*)(const std::string&)> > g_initCfgCallbacks;

	std::vector<std::tuple<std::vector<std::string>, std::vector<std::string>, std::string> > g_cfgModules;
	std::vector<std::tuple<std::vector<std::string>, std::vector<std::string>, std::string> > g_pktModules;

	extern Poco::Thread::TID g_mainThreadId;


	App* g_app = nullptr;

	std::map<UInt32, std::pair<boost::python::list*, boost::python::list*> > g_cfgCachePyObjects;


App& App::Instance() {
	return *g_app;
}



App::App(boost::python::object obj)
    :TimerManager(true,obj.ptr())
	,m_signals(this->GetIoService())
	,m_queueDestory(16384)
	,m_queueRecv(16384)
	,m_queueRecovery(16384)
{
	m_nextIoService = 0;

	g_app = this;

#ifdef _WIN32
	::SetUnhandledExceptionFilter(TopLevelFilter);
#endif


	m_signals.add(SIGINT);
	m_signals.add(SIGTERM);
	m_signals.add(SIGABRT);

	m_signals.async_wait(
		[this](boost::system::error_code ec, int signo)
	{
		LogWarning("App::Run receive signal:%d", signo);
		Stop();
	});

	//m_signals.add(SIGSEGV);
#if defined(SIGQUIT)
	m_signals.add(SIGQUIT);
#endif // defined(SIGQUIT)

}

App::~App() {
	g_app = nullptr;
}


void App::UpdateSystemMemory
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

) {
	m_systemMemoryInfo.total = total;
	m_systemMemoryInfo.available = available;
	m_systemMemoryInfo.percent = percent;
	m_systemMemoryInfo.used = used;
	m_systemMemoryInfo.free = free;

	LogEvent("SystemResource","%lld|%lld|%.2f|%.2f|%lld|%lld", rss, vms, memory_percent, cpu_percent, (UInt64)g_inputNet, (UInt64)g_outputNet);
}

void App::PushDestoryObject(PyObject* obj) {

	if (!m_queueDestory.push(obj)) {
		poco_assert_dbg(false);
	}
}

void App::PushRecvMessage(Callback::Queue* v ){
	m_queueRecv.push(v);
}

boost::shared_ptr<TMInfo> App::GeTimerManager()
{ 
	std::unique_lock<std::mutex> ul(m_mutexTimerManager);
	auto& tm = m_timerManagers[m_nextIoService];
	++m_nextIoService;
	if (m_nextIoService == m_timerManagers.size())
		m_nextIoService = 0;
	return tm;
}



bool App::GetFileData(const String& file, UInt32 offset, UInt32 size, Buffer& outBuffer) {
	try
	{
		if (size < 1) {
			return false;
		}

		Poco::ScopedReadRWLock ul(m_rwlockCacheFile);
		auto itCacheFile = m_cacheFiles.find(file);
		if (m_cacheFiles.end() == itCacheFile) {

			Poco::File f(g_dataPath + "/" + file);
			if (!f.exists() || !f.isFile()) {
				return false;
			}

			if (f.getSize() < 1) {
				return false;
			}

			itCacheFile = m_cacheFiles.emplace(file, CacheFileInfo()).first;

			if (f.getSize() > 10485760) {
				itCacheFile->second.mapping = std::move(boost::interprocess::file_mapping(f.path().c_str(), boost::interprocess::read_only));
				itCacheFile->second.region = std::move(boost::interprocess::mapped_region(itCacheFile->second.mapping, boost::interprocess::read_only));
			}
			else {
				std::ifstream ifs(f.path().c_str(),std::ios::in|std::ios::binary);
				itCacheFile->second.buffer.resize(f.getSize());
				ifs.read((char*)&itCacheFile->second.buffer.at(0), f.getSize());
			}
		}

		outBuffer.resize(size);
		itCacheFile->second.accessTime = std::time(nullptr);

		if (itCacheFile->second.buffer.empty()) {
			char* addr = (char*)itCacheFile->second.region.get_address();
			std::size_t region_size = itCacheFile->second.region.get_size();

			if (offset + size > region_size) {
				return false;
			}

			std::memcpy( &outBuffer.at(0), addr + offset, size);
		}
		else {
			if (offset + size > itCacheFile->second.buffer.size()) {
				return false;
			}

			std::memcpy( &outBuffer.at(0), &itCacheFile->second.buffer.at(offset), size);
		}
		
		return true;
	}
	catch (const std::exception& e)
	{
		LogException("App::GetFileData %s", e.what());
		return false;
	}
}


void App::Stop() {
	if (!m_run) {
		return;
	}

	m_run = false;


	auto doStop = [this]()
	{
		try {

			boost::python::object moduleHelperProcess = boost::python::import("Helper");
			
			g_callMethod(boost::python::borrowed(m_obj), "OnDestory");

			this->OnDestory();

			moduleHelperProcess.attr("AppOnDestory")();
			
		}
		catch (const std::exception& e)
		{
			LogException("App::Exit %s", e.what());
		}
		PythonCallbackException


		m_timerDestory->Stop();
		m_timerDispatch->Stop();
		m_timerCheckCache->Stop();

		m_timerDestory = nullptr;
		m_timerDispatch = nullptr;
		m_timerCheckCache = nullptr;


		Helper::Destory();
		RoomManager::Destory();
		RoleManager::Destory();
		GlobalManager::Destory();
		StoreManager::Destory();

		
		TimerManager::Stop();

		for (auto& v : m_timerManagers) {
			v->timerSend->Stop();
		}

		/*for (auto& v : m_timerManagers) {
			if (v->threadRecv.isRunning()) {
				v->threadRecv.join();
			}
		}*/


		for (auto& v : m_timerManagers) {
			v->tm->Stop();
		}

		Callback::Queue* q;


		for (auto& v : m_timerManagers) {
			while (v->queueSend.pop(q)) {
				delete q;
			}
		}

		/*for (auto& v : m_timerManagers) {
			while (v->queueRecv.pop(q)) {
				delete q;
			}
		}*/

		while (m_queueRecv.pop(q)) {
			delete q;
		}


		while (m_queueRecovery.pop(q)) {
			delete q;
		}

		PyObject* objPy = nullptr;
		while (m_queueDestory.pop(objPy)) {
			Py_DECREF(objPy);
		}

		m_timerManagers.clear();

		m_mongocxxInstance.reset();

		m_signals.cancel();

		m_loadJson = boost::python::object();
		m_dumpJson = boost::python::object();

		for (auto& v: g_cfgCachePyObjects) {
			if (v.second.first) {
				delete v.second.first;
			}

			if (v.second.first) {
				delete v.second.second;
			}
			
		}
		
	};

	this->GetIoService().post(doStop);
}

void App::Start() {
	m_run = true;

	auto cfgApp = JsonConfigs["App"];
	UInt16 threadNum = boost::python::extract<UInt16>(cfgApp["threadNum"]);
	
	m_loadJson = boost::python::import("yaml").attr("safe_load");
	m_dumpJson = boost::python::import("yaml").attr("safe_dump");


	m_mongocxxInstance = bsoncxx::stdx::make_unique<mongocxx::instance>(bsoncxx::stdx::make_unique<NoopLogger>());



	if (JsonConfigs.contains("StoreManager")) {
		StoreManager::Create();
	}

	if (JsonConfigs.contains("RoomManager")) {
		RoomManager::Create();
	}

	if (JsonConfigs.contains("RoleManager")) {
		RoleManager::Create();
	}

	if (JsonConfigs.contains("GlobalManager")) {
		GlobalManager::Create();
	}

	if (JsonConfigs.contains("Helper")) {
		Helper::Create();
	}


	if (threadNum <= 0) {
		LogError("App::Start thread number must > 0!", threadNum);
		return;
	}
	else {
		LogNormal("App::Start threadNum:%d", threadNum);
	}

	m_timerManagers.resize(threadNum);

	for (auto& v : m_timerManagers) {
		v.reset(new TMInfo());

		v->tm = boost::make_shared<TimerManager>(false);
        v->timerSend = v->tm->CreateTimer([this,&v]() {
			Callback::Queue* qr;
			Session* session = nullptr;
			Client* client = nullptr;

			while (v->queueSend.pop(qr)) {

				if (session = dynamic_cast<Session*>(qr->ref.Get())) {
					session->DoSendMessage(qr->message);
				}
				else if (client = dynamic_cast<Client*>(qr->ref.Get())) {
					client->DoSendMessage(qr->message);
				}

				if (qr->message->isMainThread) {
					m_queueRecovery.push(qr);
				}
				else {
					delete qr;
				}
			}
		});

        v->timerSend->Start(5);

		/*v->threadRecv.setName("Recv");
        v->threadRecv.startFunc([this,&v]() {
			Callback::Queue* qr;

            auto sleepTime(std::chrono::milliseconds(5));
			while (m_run) {
				std::this_thread::sleep_for(sleepTime);

				while (v->queueRecv.pop(qr)) {

					try {
						qr->info->func(qr->ref.Get(), qr->message);
					}
					catch (std::exception& e) {
						LogException("App::Initialize Callback:%s", e.what());
					}

					delete qr;
				}
			}
		});*/
	}

	m_timerDestory = TimerManager::CreateTimer([this]() {

		PyObject* objPy = nullptr;
		while (m_queueDestory.pop(objPy)) {
			Py_DECREF(objPy);
		}

		Callback::Queue* qr;
		while (m_queueRecovery.pop(qr)) {
			delete qr;
		}
	});

	m_timerDispatch = TimerManager::CreateTimer([this]() {

		Callback::Queue* qr;
		while (m_queueRecv.pop(qr)) {

			try {
				if (!qr->info->name.empty()) {
					g_callMethod(boost::python::borrowed(qr->ref.Get()->GetObject()), qr->info->name.c_str(), boost::python::make_tuple(qr->message));
                    //boost::python::call_method<void>(qr->ref.Get()->GetObject(), qr->info->name.c_str(), qr->message);
				}
				else {
                    qr->info->func(qr->ref.Get(), qr->message);
				}
			}
			catch (std::exception& e) {
				LogException("App::Callback %s", e.what());
			}
			PythonCallbackException

			delete qr;
		}
	});


	m_timerCheckCache = TimerManager::CreateTimer([this]() {

		if (m_rwlockCacheFile.tryWriteLock()) {

			std::vector<decltype(m_cacheFiles.begin())> removeCacheFiles;

			UInt32 now = std::time(nullptr) - 3600 ;

			for (auto itCacheFile = m_cacheFiles.begin(); itCacheFile != m_cacheFiles.end() ;++itCacheFile) {
				if (itCacheFile->second.accessTime < now) {
					removeCacheFiles.emplace_back(itCacheFile);
				}
			}

			for (auto& v: removeCacheFiles) {
				m_cacheFiles.erase(v);
			}

			m_rwlockCacheFile.unlock();
		}
	});

	m_timerDestory->Start(2000);
    m_timerDispatch->Start(30);
	m_timerCheckCache->Start(30000);

	try
	{ 
		boost::python::object moduleHelperProcess = boost::python::import("Helper");
		moduleHelperProcess.attr("AppOnCreate")();

		this->OnCreate();
		g_callMethod(boost::python::borrowed(m_obj), "OnCreate");
	}
	catch (const std::exception& e)
	{
		LogException("App::Initialize %s", e.what());
	}
	PythonCallbackException
}


boost::python::object App::LoadJson(const String& s) {
	return m_loadJson(s);
}

boost::python::object App::DumpJson(boost::python::object o) {
	return m_dumpJson(o);
}

void App::Run() {

	Start();

	try {
		TimerManager::Run();
	}
	catch (std::exception& e) {
		LogException("App::Run %s", e.what());
	}
}

void App::Update() {
	TimerManager::Update();
}

void App::OnCreateSubscribeClient(boost::python::object c) {

	ClientPtr pubSubClient = boost::python::extract<ClientPtr>(c.ptr());

	pubSubClient->BindMessage<pkt::protocols::PublishRes>([this](Object* obj, const boost::shared_ptr<pkt::protocols::PublishRes>& message) {

		

		auto j = LoadJson(message->message);
		if (message->isPublic == false) {
			if (j.contains("key")) {
				String key = boost::python::extract<String>(j["key"]);

				if ("updateCfg" == key) {

					{
						Poco::ScopedWriteRWLock ul(m_rwlockCacheFile);
						m_cacheFiles.clear();

						auto moduleHelper = boost::python::import("Helper");
						moduleHelper.attr("UpdateCfg")(j["param"]);
						moduleHelper.attr("AppUpdateMd5Values")();
					}

					App::ReloadCfgs();
					StoreManager::Instance()->ReloadCfgs();
					return;
				}
				else if ("stop" == key) {
					LogWarning("PubSubClient::OnPublishRes receive signal: stop");
					this->Stop();
					return;
				}
				/*else if ("queryLog" == key) {
					.QueryLog(message->message);
					return;
				}*/
				else if ("beginRepair" == key) {
					if (m_server) {
						boost::shared_ptr<Server> serverPtr = boost::python::extract<boost::shared_ptr<Server> >(m_server);
						serverPtr->BeginRepair();
						serverPtr->ClearWhitelist();

						String jsonIps = boost::python::extract<String >(DumpJson(j['ips']));
						auto docIps = bsoncxx::from_json(jsonIps);
						for (auto& v : docIps.view()) {
							serverPtr->AddIpToWhitelist(v.get_utf8().value.to_string());
						}
					}
					else {
						LogError("PubSubClient::OnPublishRes 'beginRepair' no find Server instance");
					}
				}
				else if ("endRepair" == key) {
					if (m_server) {
						boost::shared_ptr<Server> serverPtr = boost::python::extract<boost::shared_ptr<Server> >(m_server);
						serverPtr->EndRepair();
						serverPtr->ClearWhitelist();
					}
					else {
						LogError("PubSubClient::OnPublishRes 'endRepair' no find Server instance");
					}
				}
			}
		}

		g_callMethod(boost::python::borrowed(this->GetObject()), "OnPublish", boost::python::make_tuple(message->id, j, message->isPublic));

	});

	pubSubClient->BindMessage<pkt::protocols::SubscribeRes>([this](Object* obj, const boost::shared_ptr<pkt::protocols::SubscribeRes>& message) {
		g_callMethod(boost::python::borrowed(this->GetObject()), "OnSubscribe", boost::python::make_tuple(message->id));
		this->OnSubscribe(message->id);
	});

	pubSubClient->BindMessage<pkt::protocols::UnsubscribeRes>([this](Object* obj, const boost::shared_ptr<pkt::protocols::UnsubscribeRes>& message) {
		g_callMethod(boost::python::borrowed(this->GetObject()), "OnUnsubscribe", boost::python::make_tuple(message->id));
		this->OnUnsubscribe(message->id);
	});

	/*
	c->OnSocketEvent = [this](SocketEvent e, const std::string& info) {

		if (e == FastNet::SocketEvent::kConnectSucceed) {
			ClientPtr pubSubClient = boost::python::extract<ClientPtr>(m_pubSubClient.ptr());

			pubSubClient->Subscribe(m_subscribeId);
		}
	};*/
}

void App::OnCreate() {

	/*auto cfgApp = JsonConfigs["App"];

	if (cfgApp.contains("subscribeServer")) {
		boost::python::object moduleHelperProcess = boost::python::import("Helper");

		String adminServerAddress = boost::python::extract<String>(cfgApp["adminServerAddress"]);
		String subscribeKey = boost::python::extract<String>(cfgApp["subscribeKey"]);
		UInt32 adminServerId = boost::python::extract<UInt32>(cfgApp["adminServerId"]);
		m_subscribeId = boost::python::extract<UInt32>(cfgApp["subscribeId"]);

		m_pubSubClient = moduleHelperProcess.attr("PubSubClient")();
		ClientPtr pubSubClient = boost::python::extract<ClientPtr>(m_pubSubClient.ptr());

		
			

		pubSubClient->Connect(adminServerAddress, 10000000, subscribeKey, adminServerId, true);
	}*/

}

void App::OnDestory() {
	
	/*if (m_pubSubClient) {
		ClientPtr pubSubClient = boost::python::extract<ClientPtr>(m_pubSubClient.ptr());
		pubSubClient->Close();
		pubSubClient = nullptr;

		m_pubSubClient = boost::python::object();
	}*/
}


void App::AddCfgCachePyObject(UInt32 clsId, boost::python::list* keys, boost::python::list* vals) {
	g_cfgCachePyObjects[clsId] = std::make_pair(keys, vals);
}



void App::AddResiterCallback(const char* moduleName, PyObject*(*initfunc)()) {
	if (!g_registerCallbacks) {
		g_registerCallbacks.reset(new std::vector<_inittab>());
	}

	_inittab t;
	t.initfunc = initfunc;
	t.name = (char*)moduleName;
	g_registerCallbacks->emplace_back(t);
}

void App::AddCfgReloadCallback(void(*reloadfunc)()) {
	if (!g_reloadCfgCallbacks) {
		g_reloadCfgCallbacks.reset(new std::vector<void(*)()>());
	}

	g_reloadCfgCallbacks->emplace_back(reloadfunc);
}

void App::ReloadCfgs() {
	if (g_reloadCfgCallbacks) {
		for (auto v : *g_reloadCfgCallbacks) {
			try {
				v();
			}
			catch (std::exception& e) {
				FastNet::LogException("App::ReloadCfg %s", e.what());
			}
		}
	}
}

void App::AddCfgInitCallback(void(*initfunc)(const std::string&)) {
	if (!g_initCfgCallbacks) {
		g_initCfgCallbacks.reset(new std::vector<void(*)(const std::string&)>());
	}

	g_initCfgCallbacks->emplace_back(initfunc);
}

void App::InitCfgs(const std::string& basepath) {
	if (g_initCfgCallbacks) {
		for (auto v : *g_initCfgCallbacks) {
			try {
				v(basepath);
			}
			catch (std::exception& e) {
				FastNet::LogException("App::InitCfgs %s", e.what());
			}
		}
	}
}

void App::ExecutePythonCode(const std::string& code) {
	try
	{
		boost::python::object main = boost::python::import("__main__");
		boost::python::object global(main.attr("__dict__"));
		boost::python::exec(code.c_str(), global, global);
	}
	catch (std::exception& e) {
		FastNet::LogException("App::ExecutePythonCode %s", e.what());
	}
	PythonCallbackException
}


class Pkt_Python {
public:
};

BOOST_PYTHON_MODULE(pkt)
{
	boost::python::class_<Pkt_Python, boost::noncopyable>("Pkt");
}

class Cfg_Python {
public:
};

BOOST_PYTHON_MODULE(cfg)
{
	boost::python::class_<Cfg_Python, boost::noncopyable>("Cfg");
}

struct _Pkt_Reister {
	_Pkt_Reister() {
		PyImport_AppendInittab("pkt", PyInit_pkt);
	}
} s_Pkt_Reister;

struct _Cfg_Reister {
	_Cfg_Reister() {
		PyImport_AppendInittab("cfg", PyInit_cfg);
	}
} s_Cfg_Reister;

void App::AddCfgStructs(const std::vector<std::string>& namespaces, const std::vector<std::string>& types, const std::string&  m)
{
	g_cfgModules.emplace_back(std::make_tuple(namespaces, types, m));
}

void App::AddPktStructs(const std::vector<std::string>& namespaces, const std::vector<std::string>& types, const std::string&  m)
{
	g_pktModules.emplace_back(std::make_tuple(namespaces, types, m));
}

void App::InitCfgStructs() {

	auto fSetNamespaces = [](const std::vector<std::string>& namespaces, const std::vector<std::string>& names, const std::string&  m, bool v) {

		boost::python::object global;
		boost::python::object modulePkt;

		boost::python::object main = boost::python::import("__main__");
		boost::python::object globalMain(main.attr("__dict__"));

		std::string pkt,Pkt;
		
		if (v) {
			modulePkt = boost::python::import("pkt");
			pkt = "pkt";
			Pkt = "Pkt";
		}
		else {
			modulePkt = boost::python::import("cfg");
			pkt = "cfg";
			Pkt = "Cfg";
		}

		std::string fullNamespace(pkt);
		std::string shortNamespace;

		global = modulePkt.attr("__dict__");
	
		try
		{
			for (auto& v : namespaces) {
			
				auto ret = boost::python::exec(Poco::format(
					"import %s\n"
					"if hasattr(%s,'%s') == False:\n"
					"	%s.%s = %s.%s()", pkt,fullNamespace,v, fullNamespace,v, pkt,Pkt).c_str(), globalMain, globalMain);

				fullNamespace = fullNamespace + "." + v;

				if (shortNamespace.empty()) {
					shortNamespace = v;
				}
				else {
					shortNamespace = shortNamespace + "." + v;
				}
			
			}

			boost::python::object module = boost::python::import(m.c_str());
			boost::python::object obj = boost::python::eval(shortNamespace.c_str(), global, global);
			for (auto& v : names) {
				obj.attr(v.c_str()) = module.attr(v.c_str());
			}

		}
		PythonCallbackException
	};

	for (auto& v : g_pktModules) {
		fSetNamespaces(std::get<0>(v), std::get<1>(v), std::get<2>(v),true);
	}

	for (auto& v : g_cfgModules) {
		fSetNamespaces(std::get<0>(v), std::get<1>(v), std::get<2>(v), false);
	}

	g_pktModules.clear();
	g_cfgModules.clear();
}


bool App::IsExistsType(const std::type_info* t) {
	static std::set<const std::type_info*> s_types;
	for (auto v : s_types) {
		if (*v == *t) {
			return true;
		}
	}
	s_types.emplace(t);
	return false;
}








}
