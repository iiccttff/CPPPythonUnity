#include "FastNet.h"
#include <signal.h>
#include <stdlib.h>

#include "Poco/Path.h"
#include "Poco/Environment.h"
#include "boost/crc.hpp"
#include "Poco/Process.h"
#include "Poco/Environment.h"
#include "Poco/UUIDGenerator.h"
#include "Poco/MD5Engine.h"
#include "Poco/RecursiveDirectoryIterator.h"

#include "FastNet/core/ClassFactory.h"
#include "FastNet/core/Callback.h"

#include "boost/python/return_opaque_pointer.hpp"
#include "boost/python/return_value_policy.hpp"
#include "boost/python/str.hpp"
#include "boost/process.hpp"
#include <boost/program_options.hpp>


#include "FastNet/store/StoreManager.h"
#include "FastNet/room/RoomManager.h"
#include "FastNet/role/RoleManager.h"
#include "FastNet/global/GlobalManager.h"
#include "FastNet/role/RoleModule.h"

#include "FastNet/core/Helper.h"


//#include "boost/filesystem.hpp"



#if defined(POCO_OS_FAMILY_UNIX)
#include <sys/resource.h>
#endif

#if (_MSC_VER == 1900)
BoostLink_VS2015_Update3(FastNet::Struct)
BoostLink_VS2015_Update3(FastNet::Message)
BoostLink_VS2015_Update3(FastNet::Server)
BoostLink_VS2015_Update3(FastNet::Session)
BoostLink_VS2015_Update3(FastNet::Client)
BoostLink_VS2015_Update3(FastNet::App)

BoostLink_VS2015_Update3(FastNet::RoleManager)
BoostLink_VS2015_Update3(FastNet::GlobalManager)
BoostLink_VS2015_Update3(FastNet::RoomManager)
BoostLink_VS2015_Update3(FastNet::Store)
BoostLink_VS2015_Update3(FastNet::Global)
BoostLink_VS2015_Update3(FastNet::Role)
BoostLink_VS2015_Update3(FastNet::RoleModule)
BoostLink_VS2015_Update3(FastNet::Room)
BoostLink_VS2015_Update3(FastNet::Helper)
#endif

namespace python = boost::python;

//extern "C" PyObject* PyInit_pkt();
//extern "C" PyObject* PyInit_cfg();


namespace FastNet {
	extern App* g_app;
	extern void Initialize_Log();
	extern void Finalize_Log();
    extern std::unique_ptr<std::vector<_inittab> > g_registerCallbacks;
	extern void AddLogQueryTask(const String& key, UInt32 beginTime, UInt32 endTime, UInt32 appId, SessionPtr session);
	extern void AddLogQueryTaskNotRun(const String& key, UInt32 beginTime, UInt32 endTime, UInt32 appId, SessionPtr session);

	std::atomic<UInt64> g_inputNet;
	std::atomic<UInt64> g_outputNet;

	Poco::Thread::TID g_mainThreadId = 0;
	std::string g_workPath;
	std::string g_dataPath;
	std::string g_projectName;
	std::string g_mongodbUri;
	std::string g_mongodbDB;
	UInt32 g_appId = 0;

	bool g_consoleLog = false;

	boost::python::object JsonConfigs;

	boost::python::object g_callMethod;


	String GetVersion() {
		return "1.0";
	}

	String GetProjectName() {
		return g_projectName;
	}

	UInt32 GetAppId() {
		return g_appId;
	}

	bool IsDebugMode() {
#if defined(DEBUG) || defined(_DEBUG)
		return true;
#else
		return false;
#endif
	}

	void DeleteDirs(const String& dir) {
		try {
			boost::filesystem::remove_all(dir);
		}
		catch (std::exception& e) {
			LogException("FastNet::DeleteDirs %s-%s", dir.c_str(),e.what());
		}
	}

	void PrintPythonError() {

		if (PyErr_Occurred()) {
			PyErr_Print();
		}
		PyErr_Clear();
	}

	void Execute(int argc, char **argv) {

		g_inputNet = 0;
		g_outputNet = 0;

		std::string workPath;
		std::string configPath;
		std::string scriptPath;
		
		//std::string startupParam;
		std::string libraryPath;

		namespace po = boost::program_options;

		po::options_description opts("Generic options");
		opts.add_options()
			("v", "print version string")
			("h", "produce help message")
			("wp", po::value<String>(&workPath)->default_value(""), "work path")
			("cp", po::value<String>(&configPath)->default_value(""), "config path")
			("sp", po::value<String>(&scriptPath)->default_value(""), "script path")
			("lp", po::value<String>(&libraryPath)->default_value(""), "library path")
			//("p", po::value<String>(&startupParam)->default_value(""), "startup param")
			("pn", po::value<String>(&g_projectName)->default_value(""), "project name")
			;

		po::variables_map vm;

		try {
			po::store(po::parse_command_line(argc, argv, opts), vm);
			po::notify(vm);
		}
		catch ( std::exception& e) {
			std::cerr << "input param:" << e.what() << std::endl;
			std::cout << opts << std::endl;
			return;
		}

		if (vm.empty()) {
			std::cout << "no options found" << std::endl;
			return;
		}else if (vm.count("help") || vm.count("h")) {
			std::cout << opts << std::endl;
			return;
		}else if (vm.count("version") || vm.count("v")) {
			std::cout << GetVersion() << std::endl;
			return;
		}

		std::string startupFile = scriptPath + "/App.py";
		std::string startupClass = "App";
		std::string startupConfig = g_projectName +".cfg";


		{
			Poco::File fileWork(workPath);
			if (!fileWork.exists() || !fileWork.isDirectory()) {
				fileWork.createDirectories();
			}
		}

		Poco::Path pathWork(workPath);
		Poco::Path pathConfig(configPath);

		g_workPath = pathWork.absolute().toString();
		g_dataPath = configPath = pathConfig.absolute().toString();

		

		g_mainThreadId = Poco::Thread::currentTid();

		std::srand(std::time(nullptr));

#if defined(POCO_OS_FAMILY_UNIX)
		struct rlimit rlim, rlim_new;
		if (getrlimit(RLIMIT_NOFILE, &rlim) == 0)
		{
			rlim_new.rlim_cur = rlim_new.rlim_max = RLIM_INFINITY;
			if (setrlimit(RLIMIT_NOFILE, &rlim_new) != 0)
			{
				rlim_new.rlim_cur = rlim_new.rlim_max = rlim.rlim_max;
				(void)setrlimit(RLIMIT_NOFILE, &rlim_new);
			}
		}
#endif

		LogNormal("osName:%s", Poco::Environment::osName().c_str());
		LogNormal("osDisplayName:%s", Poco::Environment::osDisplayName().c_str());
		LogNormal("osVersion:%s", Poco::Environment::osVersion().c_str());
		LogNormal("osArchitecture:%s", Poco::Environment::osArchitecture().c_str());
		LogNormal("nodeName:%s", Poco::Environment::nodeName().c_str());
		LogNormal("processorCount:%d", Poco::Environment::processorCount());
		LogNormal("processId:%d", Poco::Process::id());
		LogNormal("mainThreadId:%lld", g_mainThreadId);
		LogNormal("workDir:%s", g_workPath.c_str());
		LogNormal("configDir:%s", configPath.c_str());

		Py_Initialize();

		boost::python::object moduleMain = boost::python::import("__main__");
		boost::python::object globalMain = moduleMain.attr("__dict__");

		try {
			Poco::Path pathLibraryPath(libraryPath);
			libraryPath = pathLibraryPath.absolute().toString();

			auto execString = Poco::format(	\
				"import os, sys\n"
				"sys.path.append(r'%s')\n"
				"sys.path.append(r'%s/../../../Scripts')\n"
				"sys.path.append(r'%s')", scriptPath, libraryPath, libraryPath);

			boost::python::exec(execString.c_str(),globalMain, globalMain);
			boost::python::exec_file(startupFile.c_str(), globalMain, globalMain);
		}
		PythonCallbackException

		App::InitCfgStructs();
		App::InitCfgs(configPath);
		App::ReloadCfgs();


		try {
			boost::python::object moduleFastNet = boost::python::import("FastNet");
	
			auto execString = Poco::format("with open(r'%s') as f:\n\timport yaml\n\tJsonConfigs = yaml.safe_load(f)", g_workPath + "/" + startupConfig);
			boost::python::exec(execString.c_str(), globalMain, moduleFastNet.attr("__dict__"));

			JsonConfigs = moduleFastNet.attr("JsonConfigs");

			auto cfgApp = JsonConfigs["App"];
			if (cfgApp.contains("consoleLog")) {
				g_consoleLog = boost::python::extract<bool>(cfgApp["consoleLog"]);
			}

			g_appId = 0;
			if (cfgApp.contains("id")) {
				g_mongodbUri = "mongodb://127.0.0.1:27017/?minPoolSize=1&maxPoolSize=3";
				g_appId = boost::python::extract<UInt32>(cfgApp["id"]);
				g_mongodbDB = g_projectName + "_" + std::to_string(g_appId);
			}
		}
		PythonCallbackException

		Initialize_Log();

		try {

			boost::python::object helperProcess = boost::python::import("Helper");
			g_callMethod = helperProcess.attr("CallMehtod");

			boost::python::exec(Poco::format(
				"import FastNet\n"
				"FastNet.App.Instance = %s()\n"
				"Main(FastNet.App.Instance)", startupClass).c_str(), globalMain, globalMain);
		}
		PythonCallbackException


		JsonConfigs = python::object();
		g_callMethod = python::object();

		python::object main = python::import("__main__");
		python::object global(main.attr("__dict__"));
		python::object fastNet = python::import("FastNet");
		if (fastNet.attr("App").attr("Instance")) {
			fastNet.attr("App").attr("Instance").del();
		}

		Finalize_Log();
	}

	std::string GetWorkPath() {
		return g_workPath;
	}

	std::string GetDataPath() {
		return g_dataPath;
	}

	BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(RoleManager_GetRole_stubs, GetRole, 2, 3)

	BOOST_PYTHON_MODULE(FastNet)
	{
		FastNet::App::RegisterStlVector<std::vector<UInt8> >("VectorUInt8");
		FastNet::App::RegisterStlVector<std::vector<UInt16> >("VectorUInt16");
		FastNet::App::RegisterStlVector<std::vector<UInt32> >("VectorUInt32");
		FastNet::App::RegisterStlVector<std::vector<UInt64> >("VectorUInt64");
		FastNet::App::RegisterStlVector<std::vector<UInt8> >("VectorInt8");
		FastNet::App::RegisterStlVector<std::vector<Int8> >("VectorInt16");
		FastNet::App::RegisterStlVector<std::vector<Int16> >("VectorInt32");
		FastNet::App::RegisterStlVector<std::vector<Int64> >("VectorInt64");
		FastNet::App::RegisterStlVector<std::vector<Bool> >("VectorBool");
		FastNet::App::RegisterStlVector<std::vector<Float> >("VectorFloat");
		FastNet::App::RegisterStlVector<std::vector<Double> >("VectorDouble");
		FastNet::App::RegisterStlVector<std::vector<String> >("VectorString");
		FastNet::App::RegisterStlMap<std::map<String,String> >("MapStringString");

		python::enum_<SocketEvent>("SocketEvent")
			.value("kConnectSucceed", kConnectSucceed)
			.value("kConnectFailure", kConnectFailure)
			.value("kConnectClosed", kConnectClosed)
			.value("kReConnecting", kReConnecting)
			.value("kReConnectFailure", kReConnectFailure)
			.value("kErrorMessage", kErrorMessage);

		python::class_<Struct, boost::shared_ptr<Struct>, boost::noncopyable>("Struct")
			.def("ToArray", &Struct::ToArray_Python)
			.def("FromArray", &Struct::FromArray_Python);

		python::class_<Message, boost::python::bases<Struct>, boost::shared_ptr<Message>, boost::noncopyable>("Message")
			.def_readonly("ClsId", &Message::ClsId)
			.def_readonly("ClsName", &Message::ClsName)
			.def_readonly("SignId", &Message::SignId)
			.def("Create", &Message::Create_Python).staticmethod("Create");

		python::class_<Callback, boost::noncopyable>("Callback")
			.def("BindMessage", &Callback::BindMessage_Python);

		python::class_<Client, boost::python::bases<Callback>, boost::noncopyable>("Client", python::init<PyObject*>())
			.def("Connect", &Client::Connect)
			.def("Close", &Client::Close)
			.def_readonly("IsConnect", &Client::IsConnect)
			.def_readonly("ServerId", &Client::ServerId)
			.def_readonly("SessionId", &Client::SessionId)
			.def_readonly("Token", &Client::Token)
			.def_readonly("ServerAddress", &Client::ServerAddress)
			.def("AccountVerify", &Client::AccountVerify)
			.def("RoleLogin", &Client::RoleLogin)
			.def("RoleReconnect", &Client::RoleReconnect)
			.def("SendMsg", &Client::SendMsg)
			.def("Publish", &Client::Publish)
			.def("Subscribe", &Client::Subscribe)
			.def("Unsubscribe", &Client::Unsubscribe);

		python::class_<Server, boost::python::bases<Callback>, boost::noncopyable>("Server", python::init<PyObject*, boost::python::object, UInt32, bool, std::string>())
			.def("Start", &Server::Start)
			.def("Stop", &Server::Stop)
			.def("SendMsg", &Server::SendMsg)
			.def("AddIpToWhitelist", &Server::AddIpToWhitelist)
			.def("AddIpToBlacklist", &Server::AddIpToBlacklist)
			.def("DeleteIpFromWhitelist", &Server::DeleteIpFromWhitelist)
			.def("DeleteIpFromBlacklist", &Server::DeleteIpFromBlacklist)
			.def("BeginRepair", &Server::BeginRepair)
			.def("EndRepair", &Server::EndRepair)
			.def_readonly("IsRepair", &Server::IsRepair)
			.def("Publish", &Server::Publish)
			.def("AllowSubPub", &Server::AllowSubPub)
			.def("SetSubscribeKey", &Server::SetSubscribeKey)
			.def("BroadcastMsg", &Server::BroadcastMsg_Python)
			.def_readonly("ListenAddress", &Server::GetListenAddress)
			.def_readonly("ListenAddressWan", &Server::GetListenAddressWan)
			.def_readonly("OnlineNumber", &Server::GetOnlineNumber)
			.def("ClearWhitelist", &Server::ClearWhitelist)
			.def("ClearBlacklist", &Server::ClearBlacklist)
			.def("SetMd5Values", &Server::SetMd5Values);
		

		{
			python::scope scopeSession = boost::python::class_<Session, boost::noncopyable>("Session", python::init<PyObject*, boost::shared_ptr<Session::CreateParam> >())
				.def("SendMsg", &Session::SendMsg)
				.def("SendErrorCode", &Session::SendErrorCode)
				.def_readonly("SessionId", &Session::GetSessionId)
				.def_readonly("RoleId", &Session::GetRoleId)
				.def("AccountVerifySucceed", &Session::AccountVerifySucceed)
				.def("Stop", &Session::Stop);

			python::class_<Session::CreateParam, boost::shared_ptr<Session::CreateParam>, boost::noncopyable>("CreateParam", python::no_init);
		}
		
		void (Timer::*TimerStart)(UInt32 , UInt32 , Int32 ) = &Timer::Start;

		python::class_<Timer, boost::shared_ptr<Timer>, boost::noncopyable>("Timer", python::no_init)
			.def("Start", TimerStart)
			.def("Stop", &Timer::Stop)
			.def("Update", &Timer::Update);

		python::class_<App, boost::noncopyable>("App", python::init<boost::python::object>())
			.def("CreateTimer", &App::CreateTimer_Python)
			.def("Start", &App::Start)
			.def("Stop", &App::Stop)
			.def("Run", &App::Run)
			.def("Update", &App::Update)
			.def("ReloadCfgs", &App::ReloadCfgs).staticmethod("ReloadCfgs")
			.def("OnCreateSubscribeClient", &App::OnCreateSubscribeClient)
			.def("SetServer", &App::SetServer)
			.def("UpdateSystemMemory",&App::UpdateSystemMemory)
			.def_readonly("Server", &App::GetServer)
			.def("ExecutePythonCode", &App::ExecutePythonCode).staticmethod("ExecutePythonCode");
		

		python::class_<Store, boost::shared_ptr<Store>, boost::noncopyable>("Store", python::init<PyObject*, String, String>())
			.def("Save", &Store::Save)
			.def_readonly("Id", &Store::Id);

		python::class_<StoreRead, boost::shared_ptr<StoreRead>, boost::noncopyable>("StoreRead", python::no_init)
			.def("ReadString", &StoreRead::ReadString)
			.def("ReadUInt32", &StoreRead::ReadUInt32)
			.def("ReadUInt64", &StoreRead::ReadUInt64)
			.def("ReadInt32", &StoreRead::ReadInt32)
			.def("ReadInt64", &StoreRead::ReadInt64)
			.def("ReadDouble", &StoreRead::ReadDouble)
			.def("ReadBool", &StoreRead::ReadBool)
			.def("ReadList", &StoreRead::ReadList)
			.def("ReadDict", &StoreRead::ReadDict);


		python::class_<StoreWrite, boost::shared_ptr<StoreWrite>, boost::noncopyable>("StoreWrite", python::no_init)
			.def("WriteString", &StoreWrite::WriteString)
			.def("WriteUInt32", &StoreWrite::WriteUInt32)
			.def("WriteUInt64", &StoreWrite::WriteUInt64)
			.def("WriteInt32", &StoreWrite::WriteInt32)
			.def("WriteInt64", &StoreWrite::WriteInt64)
			.def("WriteDouble", &StoreWrite::WriteDouble)
			.def("WriteBool", &StoreWrite::WriteBool)
			.def("WriteList", &StoreWrite::WriteList)
			.def("WriteDict", &StoreWrite::WriteDict);


		python::class_<Global, boost::python::bases<Store>, boost::shared_ptr<Global>, boost::noncopyable>("Global", python::init<PyObject*, String>());
		
		python::class_<Room, boost::shared_ptr<Room>, boost::noncopyable>("Room", python::init<PyObject*>())
			.def_readonly("Id", &Room::Id)
			.def_readonly("IsStoped", &Room::IsStoped)
			.def_readonly("IsAllReady", &Room::IsAllReady)
			.def_readonly("Start", &Room::IsStoped)
			.def_readonly("Stop", &Room::IsAllReady);

		python::class_<Role, boost::python::bases<Store>, boost::shared_ptr<Role>, boost::noncopyable>("Role", python::init<PyObject*, String>())
			.def("Frozen", &Role::Frozen)
			.def_readonly("IsFrozen", &Role::IsFrozen)
			.def_readonly("FrozenTime", &Role::FrozenTime)
			.def_readonly("Status", &Role::GetStatus)
			.def_readonly("Session", &Role::GetSession_Python)
			.def("Module", &Role::Module)
			.def("Modules", &Role::Modules_Python)
			.def("JoinRoom", &Role::JoinRoom)
			.def("ReadyRoom", &Role::ReadyRoom)
			.def("LeaveRoom", &Role::LeaveRoom)
			.def("Modules", &Role::SendRoomMsg)
			.def_readonly("UserId", &Role::UserId)
			.def_readonly("ChannelId", &Role::ChannelId)
			.add_property("Level", &Role::Level, &Role::SetLevel);
		

		
		python::class_<RoleModule, boost::python::bases<Store>, boost::shared_ptr<RoleModule>, boost::noncopyable>("RoleModule", python::init<PyObject*, String, RolePtr>())
			.def_readonly("Role", &RoleModule::GetRole);

		python::class_<GlobalManager, boost::shared_ptr<GlobalManager>, boost::noncopyable>("GlobalManager", python::no_init)
			.add_static_property("Instance", &GlobalManager::Instance)
			.def("RegisterGlobal", &GlobalManager::RegisterGlobal)
			.def("GetGlobal", &GlobalManager::GetGlobal);

		python::class_<RoomManager, boost::shared_ptr<RoomManager>, boost::noncopyable>("RoomManager", python::no_init)
			.add_static_property("Instance", &RoomManager::Instance)
			.def("RegisterRoom", &RoomManager::RegisterRoom)
			.def("GetRooms", &RoomManager::GetRooms_Python)
			.def("CreateRoom", &RoomManager::CreateRoom)
			.def("DeleteRoom", &RoomManager::DeleteRoom);

		python::class_<RoleManager, boost::shared_ptr<RoleManager>, boost::noncopyable>("RoleManager", python::no_init)
			.add_static_property("Instance", &RoleManager::Instance)
			.def("GetRole", (RolePtr(RoleManager::*)(const String&, const String&, bool))0, RoleManager_GetRole_stubs())
			.def("CreateRole", &RoleManager::CreateRole)
			.def("GetRoleBySessionId", &RoleManager::GetRoleBySessionId)
			.def("MulticastMessage", &RoleManager::MulticastMessage)
			.def("RegisterRole", &RoleManager::RegisterRole)
			.def("DeleteRole", &RoleManager::DeleteRole)
			.def("RegisterModule", &RoleManager::RegisterModule);
		

		python::class_<Helper, boost::shared_ptr<Helper>, boost::noncopyable>("Helper", python::no_init)
			.add_static_property("Instance", &Helper::Instance)
			.def("PutChannelCode", &Helper::PutChannelCode)
			.def("AccountVerify", &Helper::AccountVerify)
			.def("AddAccount", &Helper::AddAccount)
			.def("DeleteAccount", &Helper::DeleteAccount)
			.def("ModifyAccount", &Helper::ModifyAccount)
			.def("IsExistUserId", &Helper::IsExistUserId);

		python::class_<StoreManager, boost::shared_ptr<StoreManager>, boost::noncopyable>("StoreManager", python::no_init)
			.add_static_property("Instance", &StoreManager::Instance)
			.def("GetRoleIds", &StoreManager::GetRoleIds_Python)
			.def("AccountToUid", &StoreManager::AccountToUid).staticmethod("AccountToUid");


		void(*pfLogNormal)(const std::string& log) = LogNormal;
		void(*pfLogDebug)(const std::string& log) = LogDebug;
		void(*pfLogWarning)(const std::string& log) = LogWarning;
		void(*pfLogError)(const std::string& log) = LogError;
		void(*pfLogException)(const std::string& log) = LogException;

		python::def("LogNormal", pfLogNormal);
		python::def("LogDebug", pfLogDebug);
		python::def("LogWarning", pfLogWarning);
		python::def("LogError", pfLogError);
		python::def("LogException", pfLogException);

		python::def("GetWorkPath", GetWorkPath);
		python::def("GetVersion", GetVersion);
		python::def("IsDebugMode", IsDebugMode);

		python::def("GetDataPath", GetDataPath);
		python::def("GetProjectName", GetProjectName);
		python::def("GetAppId", GetAppId);

		python::def("DeleteDirs", DeleteDirs);

		python::def("AddLogQueryTask", AddLogQueryTask);
		python::def("AddLogQueryTaskNotRun", AddLogQueryTaskNotRun);
	}
}






