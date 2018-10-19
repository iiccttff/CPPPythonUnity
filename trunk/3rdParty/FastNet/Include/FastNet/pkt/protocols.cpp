#include "protocols.h"

namespace pkt{
namespace protocols{

	BOOST_PYTHON_MODULE(module1688994316){
		LogInfo::Export();
		ErrorMessage::Export();
		AccountVerifyReq::Export();
		RoleLoginReq::Export();
		RoleLoginRes::Export();
		UpdateRoleTokenRes::Export();
		RoleReconnectReq::Export();
		SocketHeartbeat::Export();
		SocketClose::Export();
		PublishReq::Export();
		PublishRes::Export();
		SubscribeReq::Export();
		SubscribeRes::Export();
		UnsubscribeReq::Export();
		UnsubscribeRes::Export();
		LocalSocketEvent::Export();
		SocketConnect::Export();
		SocketConnectReq::Export();
		RoomMessageReq::Export();
		RoomMessageRes::Export();
		DownloadFileListReq::Export();
		DownloadFileListRes::Export();
		DownloadFileRes::Export();
		LogQueryRes::Export();
		LogQueryReq::Export();
		FastNet::ClassFactory::Instance()->Register<ErrorMessage>();
		FastNet::ClassFactory::Instance()->Register<AccountVerifyReq>();
		FastNet::ClassFactory::Instance()->Register<RoleLoginReq>();
		FastNet::ClassFactory::Instance()->Register<RoleLoginRes>();
		FastNet::ClassFactory::Instance()->Register<UpdateRoleTokenRes>();
		FastNet::ClassFactory::Instance()->Register<RoleReconnectReq>();
		FastNet::ClassFactory::Instance()->Register<SocketHeartbeat>();
		FastNet::ClassFactory::Instance()->Register<SocketClose>();
		FastNet::ClassFactory::Instance()->Register<PublishReq>();
		FastNet::ClassFactory::Instance()->Register<PublishRes>();
		FastNet::ClassFactory::Instance()->Register<SubscribeReq>();
		FastNet::ClassFactory::Instance()->Register<SubscribeRes>();
		FastNet::ClassFactory::Instance()->Register<UnsubscribeReq>();
		FastNet::ClassFactory::Instance()->Register<UnsubscribeRes>();
		FastNet::ClassFactory::Instance()->Register<LocalSocketEvent>();
		FastNet::ClassFactory::Instance()->Register<SocketConnect>();
		FastNet::ClassFactory::Instance()->Register<SocketConnectReq>();
		FastNet::ClassFactory::Instance()->Register<RoomMessageReq>();
		FastNet::ClassFactory::Instance()->Register<RoomMessageRes>();
		FastNet::ClassFactory::Instance()->Register<DownloadFileListReq>();
		FastNet::ClassFactory::Instance()->Register<DownloadFileListRes>();
		FastNet::ClassFactory::Instance()->Register<DownloadFileRes>();
		FastNet::ClassFactory::Instance()->Register<LogQueryRes>();
		FastNet::ClassFactory::Instance()->Register<LogQueryReq>();
	}

	struct _protocols_Reister{
		_protocols_Reister(){
			PyImport_AppendInittab("module1688994316",PyInit_module1688994316);
			std::vector<std::string> namespaces;
			namespaces.emplace_back("protocols");
			std::vector<std::string> types;
			types.emplace_back("LogInfo");
			types.emplace_back("ErrorMessage");
			types.emplace_back("AccountVerifyReq");
			types.emplace_back("RoleLoginReq");
			types.emplace_back("RoleLoginRes");
			types.emplace_back("UpdateRoleTokenRes");
			types.emplace_back("RoleReconnectReq");
			types.emplace_back("SocketHeartbeat");
			types.emplace_back("SocketClose");
			types.emplace_back("PublishReq");
			types.emplace_back("PublishRes");
			types.emplace_back("SubscribeReq");
			types.emplace_back("SubscribeRes");
			types.emplace_back("UnsubscribeReq");
			types.emplace_back("UnsubscribeRes");
			types.emplace_back("LocalSocketEvent");
			types.emplace_back("SocketConnect");
			types.emplace_back("SocketConnectReq");
			types.emplace_back("RoomMessageReq");
			types.emplace_back("RoomMessageRes");
			types.emplace_back("DownloadFileListReq");
			types.emplace_back("DownloadFileListRes");
			types.emplace_back("DownloadFileRes");
			types.emplace_back("LogQueryRes");
			types.emplace_back("LogQueryReq");
			FastNet::App::AddPktStructs(namespaces,types,"module1688994316");
		}
	} s_protocols_Reister;

} //end namespace protocols
} //end namespace pkt

#if (_MSC_VER == 1900)
BoostLink_VS2015_Update3(pkt::protocols::PublishReq)
BoostLink_VS2015_Update3(pkt::protocols::RoleLoginRes)
BoostLink_VS2015_Update3(pkt::protocols::PublishRes)
BoostLink_VS2015_Update3(pkt::protocols::AccountVerifyReq)
BoostLink_VS2015_Update3(pkt::protocols::UpdateRoleTokenRes)
BoostLink_VS2015_Update3(pkt::protocols::RoomMessageRes)
BoostLink_VS2015_Update3(pkt::protocols::SocketClose)
BoostLink_VS2015_Update3(pkt::protocols::DownloadFileRes)
BoostLink_VS2015_Update3(pkt::protocols::LogQueryRes)
BoostLink_VS2015_Update3(pkt::protocols::SubscribeRes)
BoostLink_VS2015_Update3(pkt::protocols::RoleLoginReq)
BoostLink_VS2015_Update3(pkt::protocols::LogQueryReq)
BoostLink_VS2015_Update3(pkt::protocols::LocalSocketEvent)
BoostLink_VS2015_Update3(pkt::protocols::DownloadFileListRes)
BoostLink_VS2015_Update3(pkt::protocols::SubscribeReq)
BoostLink_VS2015_Update3(pkt::protocols::RoomMessageReq)
BoostLink_VS2015_Update3(pkt::protocols::LogInfo)
BoostLink_VS2015_Update3(pkt::protocols::RoleReconnectReq)
BoostLink_VS2015_Update3(pkt::protocols::SocketHeartbeat)
BoostLink_VS2015_Update3(pkt::protocols::SocketConnectReq)
BoostLink_VS2015_Update3(pkt::protocols::ErrorMessage)
BoostLink_VS2015_Update3(pkt::protocols::DownloadFileListReq)
BoostLink_VS2015_Update3(pkt::protocols::UnsubscribeReq)
BoostLink_VS2015_Update3(pkt::protocols::SocketConnect)
BoostLink_VS2015_Update3(pkt::protocols::UnsubscribeRes)
#endif
