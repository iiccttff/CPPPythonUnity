#include "base.h"

namespace cfg{
namespace globals{
namespace base{

	BOOST_PYTHON_MODULE(module1833498635){
		Language::Export();
		ErrorCode::Export();
		Items::Export();
	}

	struct _base_Reister{
		_base_Reister(){
			PyImport_AppendInittab("module1833498635",PyInit_module1833498635);
			std::vector<std::string> namespaces;
			namespaces.emplace_back("globals");
			namespaces.emplace_back("base");
			std::vector<std::string> types;
			types.emplace_back("Items");
			types.emplace_back("Language");
			types.emplace_back("ErrorCode");
			FastNet::App::AddCfgStructs(namespaces,types,"module1833498635");
		}
	} s_base_Reister;

} //end namespace globals
} //end namespace base
} //end namespace cfg

#if (_MSC_VER == 1900)
BoostLink_VS2015_Update3(cfg::globals::base::Items)
BoostLink_VS2015_Update3(cfg::globals::base::Language)
BoostLink_VS2015_Update3(cfg::globals::base::ErrorCode)
#endif
