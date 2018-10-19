#include "common.h"

namespace pkt{
namespace common{

	BOOST_PYTHON_MODULE(module3857477713){
		AccountVerifySucceedRes::Export();
		GotoServerTokenRes::Export();
		RoleLoginSucceedRes::Export();
		AnyReq::Export();
		AnyRes::Export();
		FastNet::ClassFactory::Instance()->Register<AccountVerifySucceedRes>();
		FastNet::ClassFactory::Instance()->Register<GotoServerTokenRes>();
		FastNet::ClassFactory::Instance()->Register<RoleLoginSucceedRes>();
		FastNet::ClassFactory::Instance()->Register<AnyReq>();
		FastNet::ClassFactory::Instance()->Register<AnyRes>();
	}

	struct _common_Reister{
		_common_Reister(){
			PyImport_AppendInittab("module3857477713",PyInit_module3857477713);
			std::vector<std::string> namespaces;
			namespaces.emplace_back("common");
			std::vector<std::string> types;
			types.emplace_back("AccountVerifySucceedRes");
			types.emplace_back("GotoServerTokenRes");
			types.emplace_back("RoleLoginSucceedRes");
			types.emplace_back("AnyReq");
			types.emplace_back("AnyRes");
			FastNet::App::AddPktStructs(namespaces,types,"module3857477713");
		}
	} s_common_Reister;

} //end namespace common
} //end namespace pkt

#if (_MSC_VER == 1900)
BoostLink_VS2015_Update3(pkt::common::AnyReq)
BoostLink_VS2015_Update3(pkt::common::AccountVerifySucceedRes)
BoostLink_VS2015_Update3(pkt::common::AnyRes)
BoostLink_VS2015_Update3(pkt::common::GotoServerTokenRes)
BoostLink_VS2015_Update3(pkt::common::RoleLoginSucceedRes)
#endif
