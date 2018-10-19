#include "modules.h"

namespace cfg{
namespace globals{
namespace modules{

	BOOST_PYTHON_MODULE(module2309362749){
		NoticeMgr::Export();
		PlatformMgr::Export();
		ServerMgr::Export();
		UserMgr::Export();
		DataQuery::Export();
		MailMgr::Export();
	}

	struct _modules_Reister{
		_modules_Reister(){
			PyImport_AppendInittab("module2309362749",PyInit_module2309362749);
			std::vector<std::string> namespaces;
			namespaces.emplace_back("globals");
			namespaces.emplace_back("modules");
			std::vector<std::string> types;
			types.emplace_back("MailMgr");
			types.emplace_back("NoticeMgr");
			types.emplace_back("PlatformMgr");
			types.emplace_back("DataQuery");
			types.emplace_back("UserMgr");
			types.emplace_back("ServerMgr");
			FastNet::App::AddCfgStructs(namespaces,types,"module2309362749");
		}
	} s_modules_Reister;

} //end namespace globals
} //end namespace modules
} //end namespace cfg

#if (_MSC_VER == 1900)
BoostLink_VS2015_Update3(cfg::globals::modules::MailMgr)
BoostLink_VS2015_Update3(cfg::globals::modules::NoticeMgr)
BoostLink_VS2015_Update3(cfg::globals::modules::PlatformMgr)
BoostLink_VS2015_Update3(cfg::globals::modules::DataQuery)
BoostLink_VS2015_Update3(cfg::globals::modules::UserMgr)
BoostLink_VS2015_Update3(cfg::globals::modules::ServerMgr)
#endif
