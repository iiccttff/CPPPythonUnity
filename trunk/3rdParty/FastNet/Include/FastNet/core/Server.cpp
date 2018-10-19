#include "Server.h"
#include "Log.h"
#include "App.h"

#include "boost/asio.hpp"

#include "Poco/File.h"
#include "Poco/Path.h"

#include "Poco/Process.h"
#include "Poco/Pipe.h"
#include "Poco/PipeStream.h"

#include "boost/process.hpp"

namespace python = boost::python;

namespace FastNet {
	extern Poco::Thread::TID g_mainThreadId;
	extern std::string g_workPath;
	extern boost::python::object g_callMethod;
	extern std::string g_dataPath;

	Server::Server(PyObject* obj,boost::python::object clsSession, UInt32 serverId, bool enableSSL, std::string certificatePassword)
        :Object(obj)
		,m_clsSession(clsSession)
		, m_timerMgr(new TimerManager(false))
		//,m_ioServiceWork(new boost::asio::io_service::work(m_ioService))
		,m_acceptor(m_timerMgr->GetIoService())
		,m_id(serverId){

        m_appRef = &App::Instance();
        m_run = false;
		m_enableSSL = enableSSL;
		m_isRepair = false;
		m_allowSubPub = false;

		m_downloadFiles.reset(new std::map<String, UInt32>());
		m_md5Values.reset(new String());

		this->BindMessage(&Session::RoleLogin);
		this->BindMessage(&Session::SocketConnectReq);
		this->BindMessage(&Session::AccountVerifyReq);
		
		this->BindMessage(&Session::PublishReq);
		this->BindMessage(&Session::SubscribeReq);
		this->BindMessage(&Session::UnsubscribeReq);

		//this->BindMessage(&Session::GotoServerReq, false);
		this->BindMessage(&Session::RoleReconnectReq);

		this->BindMessage(&Session::DownloadFileListReq);

		if (enableSSL) {

			if (certificatePassword.empty()) {
				LogError("Server::Server The certificate password can not be empty!");
				return;
			}

			auto serverKey = g_workPath + "/server_" + std::to_string(serverId) + ".key";
			auto serverCrt = g_workPath + "/server_" + std::to_string(serverId) + ".crt";
			auto dhPem = g_workPath + "/dh1024_" + std::to_string(serverId) + ".pem";
			auto serverCsr = g_workPath + "/server_" + std::to_string(serverId) + ".csr";

			Poco::File fServerCrt(serverCrt);
			Poco::File fServerKey(serverKey);
			Poco::File fDhPem(dhPem);

			if (!fServerCrt.exists() || !fServerCrt.isFile() ||
				!fServerKey.exists() || !fServerKey.isFile() ||
				!fDhPem.exists() || !fDhPem.isFile() ) {

				LogWarning("Server::Server no find certificate file,now re created!");

				auto moduleFastNet = boost::python::import("FastNet");
				auto moduleOS = boost::python::import("os");
				String fileDir = boost::python::extract<String>(moduleFastNet.attr("__file__"));
				fileDir = boost::python::extract<String>(moduleOS.attr("path").attr("dirname")(fileDir));

#ifdef POCO_OS_FAMILY_UNIX
				Poco::Path cmdPath(fileDir + "/../../../../openssl-1.0.2o/bin.ubuntu/openssl");
#elif POCO_OS_FAMILY_WINDOWS
				Poco::Path cmdPath(fileDir + "/../../../../openssl-1.0.2o/bin/openssl");
#endif

				Poco::Path cfgPath(fileDir + "/../../../../openssl-1.0.2o/ssl/openssl.cnf");
				cfgPath = cfgPath.absolute();

				cmdPath = cmdPath.absolute();
				
				auto runOpenSSL = [&cmdPath, cfgPath](const std::vector<std::string>& args)
				{	
					auto cmd = cmdPath.toString();
					for (auto& v:args) {
						cmd = cmd + " " + v;
					}

					namespace bp = boost::process;
					bp::child c(cmd, bp::std_out > bp::null, bp::std_err > bp::null, bp::std_in < bp::null, bp::env["OPENSSL_CONF"] += cfgPath.toString());
					c.wait();

					poco_assert_msg(c.exit_code() == 0, "runOpenSSL ret != 0");
				};

				
				std::vector<std::string> args;
				args.push_back("genrsa");
				args.push_back("-des3");
				args.push_back("-passout");
				args.push_back("pass:" + certificatePassword);
				args.push_back("-out");
				args.push_back(serverKey);
				args.push_back("1024");
				runOpenSSL(args);

				args.clear();
				args.push_back("req");
				args.push_back("-new");
				args.push_back("-key");
				args.push_back(serverKey);
				args.push_back("-passin");
				args.push_back("pass:" + certificatePassword);
				args.push_back("-out");
				args.push_back(serverCsr);
				args.push_back("-subj");
				args.push_back("\"/C=CN/ST=GD/L=SZ/O=cmge/OU=ZhanShen/CN=cmge.com/emailAddress=cmge@cmge.com\"");
				runOpenSSL(args);

				args.clear();
				args.push_back("x509");
				args.push_back("-req");
				args.push_back("-days");
				args.push_back("365");
				args.push_back("-in");
				args.push_back(serverCsr);
				args.push_back("-signkey");
				args.push_back(serverKey);
				args.push_back("-passin");
				args.push_back("pass:" + certificatePassword);
				args.push_back("-out");
				args.push_back(serverCrt);
				runOpenSSL(args);

				args.clear();
				args.push_back("dhparam");
				args.push_back("-out");
				args.push_back(dhPem);
				args.push_back("1024");
				runOpenSSL(args);

				args.clear();
				args.push_back("rsa");
				args.push_back("-in");
				args.push_back(serverKey);
				args.push_back("-passin");
				args.push_back("pass:" + certificatePassword);
				args.push_back("-out");
				args.push_back(serverKey);
				runOpenSSL(args);

				Poco::File fServerCsr(serverCsr);
				if (fServerCsr.exists() && fServerCsr.isFile()) {
					fServerCsr.remove();
				}
				
			}

			m_certificatePassword = certificatePassword;
			m_sslContext = std::make_shared<boost::asio::ssl::context>(boost::asio::ssl::context::sslv23);
			m_sslContext->set_options(
				boost::asio::ssl::context::default_workarounds
				| boost::asio::ssl::context::no_sslv2
				| boost::asio::ssl::context::single_dh_use);

			m_sslContext->set_password_callback(boost::bind(&Server::GetCertificatePassword, this));

			m_sslContext->use_certificate_chain_file(serverCrt);
			m_sslContext->use_private_key_file(serverKey, boost::asio::ssl::context::pem);
			m_sslContext->use_tmp_dh_file(dhPem);
		}
	}

	Server::~Server() {
		Stop();
	}

	void Server::BroadcastMsg(const MessagePtr& message, const std::function<bool(Session*)>& f) {
		std::unique_lock<std::mutex> ul(m_mutexSession);
		for (auto& v : m_sessions) {
			auto session = v.second.Get<Session>();

			if (f) {
				if (f(session) == true) {
					session->SendMsg(message);
				}
			}
			else {
				session->SendMsg(message);
			}
		}
	}

	void Server::BroadcastMsg_Python(const MessagePtr& message, PyObject* f) {
		std::unique_lock<std::mutex> ul(m_mutexSession);
		for (auto& v : m_sessions) {
			auto session = v.second.Get<Session>();
			if (f != nullptr) {
				bool ret = boost::python::call<bool>(f, boost::python::borrowed(session->GetObject()));
				if (ret == true) {
					session->SendMsg(message);
				}
			}
			else {
				session->SendMsg(message);
			}
		}
	}

	void Server::SetMd5Values(const String& v) {
		auto downloadFiles = std::make_shared<std::map<String, UInt32> >();

		auto doc = bsoncxx::from_json(v);
		for (auto&v : doc.view()) {

			Poco::File f(g_dataPath + "/" + v.key().to_string());
			if (f.exists() && f.isFile()) {
				downloadFiles->emplace(v.key(),f.getSize());
			}
			else {
				LogError("Server::SetMd5Values file:%s no exists!", v.key().data());
			}
		}

		m_downloadFiles = downloadFiles;
		m_md5Values = std::make_shared<String>(v);
	}

	std::shared_ptr<String> Server::GetMd5Values() {
		return m_md5Values;
	}

	std::shared_ptr<std::map<String, UInt32>> Server::GetDownloadFiles() {
		return m_downloadFiles;
	}

	void Server::AllowSubPub(bool val) {
		m_allowSubPub = val;
	}

	void Server::Publish(UInt32 id, const String& message,bool isPublic) {
		if (!m_allowSubPub) {
			return;
		}

		std::unique_lock<std::mutex> ul(m_mutexSubscribeId);
		auto itSubscribeId = m_subscribeIds.find(id);
		if (m_subscribeIds.end() != itSubscribeId) {
			auto publishRes = Message::Create<pkt::protocols::PublishRes>();
			publishRes->id = id;
			publishRes->message = message;
			publishRes->isPublic = isPublic;
			for (auto& v : itSubscribeId->second) {
				Session* session = (Session*)v;

				if (isPublic == false && session->IsPublicSubscribe() == true) {
					//exclude private message for public session
					continue;
				}

				session->SendMsg(publishRes);
			}
		}
	}

	void Server::Subscribe(UInt32 id, Object* session) {
		if (!m_allowSubPub) {
			return;
		}

		std::unique_lock<std::mutex> ul(m_mutexSubscribeId);
		auto ret = m_subscribeIds.emplace(id,std::set<Object*>());
		if (ret.first->second.emplace(session).second) {

			auto sessionPtr = (Session*)session;
			LogDebug("Server::Subscribe id:%lld sessionId:%lld", id, sessionPtr->GetSessionId());
		}
	}

	void Server::Unsubscribe(UInt32 id, Object* session) {
		if (!m_allowSubPub) {
			return;
		}

		std::unique_lock<std::mutex> ul(m_mutexSubscribeId);
		auto itSubscribeId = m_subscribeIds.find(id);
		if (m_subscribeIds.end() != itSubscribeId) {
			itSubscribeId->second.erase(session);

			auto sessionPtr = (Session*)session;
			LogDebug("Server::Unsubscribe id:%lld sessionId:%lld", id, sessionPtr->GetSessionId());
		}
	}

	/*void Server::GotoConnectReq(const String& username, const String& password, Session* session) {
		std::unique_lock<std::mutex> ul(m_mutexGotoServerToken);
		auto itGotoServerToken = m_gotoServerTokens.find(username);
		if (m_gotoServerTokens.end() != itGotoServerToken ) {
			if (itGotoServerToken->second.token != password) {
				session->Stop();
				m_gotoServerTokens.erase(itGotoServerToken);
				return;
			}

			auto message = boost::make_shared<pkt::protocols::GotoConnectRes>();
			message->userId = itGotoServerToken->second.userId;
			session->SendMsg(message);

			m_gotoServerTokens.erase(itGotoServerToken);
		}
	}*/

	void Server::ClearWhitelist() {
		m_acceptor.get_io_service().post([this]() {
			m_ipWhitelist.clear();
		});
	}

	void Server::ClearBlacklist() {
		m_acceptor.get_io_service().post([this]() {
			m_ipBlacklist.clear();
		});
	}

	void Server::AddIpToWhitelist(const std::string& ip) {
		m_acceptor.get_io_service().post([this, ip]() {
			if (m_ipWhitelist.emplace(ip).second) {
				LogError("Server::AddIpToWhitelist ip:%s already exist!", ip.c_str());
			}
		});
	}

	void Server::AddIpToBlacklist(const std::string& ip) {
		m_acceptor.get_io_service().post([this, ip]() {
			if (m_ipBlacklist.emplace(ip).second) {
				LogError("Server::AddIpToBlacklist ip:%s already exist!", ip.c_str());
			}
		});
	}

	void Server::DeleteIpFromWhitelist(const std::string& ip) {
		m_acceptor.get_io_service().post([this, ip]() {
			auto itDelete = m_ipWhitelist.find(ip);
			if (m_ipWhitelist.end() != itDelete) {
				LogError("Server::DeleteIpFromWhitelist ip:%s no exist!", ip.c_str());
			}
			else {
				m_ipWhitelist.erase(itDelete);
			}
		});
	}

	void Server::DeleteIpFromBlacklist(const std::string& ip) {
		m_acceptor.get_io_service().post([this, ip]() {
			auto itDelete = m_ipBlacklist.find(ip);
			if (m_ipBlacklist.end() != itDelete) {
				LogError("Server::DeleteIpFromBlacklist ip:%s no exist!", ip.c_str());
			}
			else {
				m_ipBlacklist.erase(itDelete);
			}
		});
	}

	void Server::BeginRepair() {
		m_isRepair = true;
	}

	void Server::EndRepair() {
		m_isRepair = false;
	}

	bool Server::IsRepair() { 
		return m_isRepair; 
	}

	void Server::AcceptSucceed(boost::shared_ptr<Socket> socket, boost::shared_ptr<TMInfo> timerManager) {

		auto now = std::time(nullptr);

		if ((now - m_ipSecurityCheckResetTime) >= 30) {
			m_ipSecurityCheckResetTime = now;
			m_ipSecurityCheck.clear();

			for (auto itBegin = m_ipBlacklistSystem.begin();itBegin != m_ipBlacklistSystem.end();) {
				if ((now - itBegin->second) > 300) {
					itBegin = m_ipBlacklistSystem.erase(itBegin);
				}
				else {
					++itBegin;
				}
			}
		}

		boost::system::error_code ignore;
		std::string remoteIp;
		if (m_enableSSL) {
			remoteIp = socket->GetSocketSSL()->lowest_layer().remote_endpoint(ignore).address().to_string();
		}
		else {
			remoteIp = socket->GetSocket()->remote_endpoint(ignore).address().to_string();
		}

		bool allowConnect = true;

		if (m_isRepair == true) {
			if (m_ipWhitelist.end() == m_ipWhitelist.find(remoteIp)) {
				allowConnect = false;
			}
		}
		else {
			if (m_ipBlacklist.end() != m_ipBlacklist.find(remoteIp)) {
				allowConnect = false;
			}
			else {

				auto itBlacklistSystem = m_ipBlacklistSystem.find(remoteIp);
				if (m_ipBlacklistSystem.end() != itBlacklistSystem) {
					itBlacklistSystem->second = std::time(nullptr);
					allowConnect = false;
				}
				else {
					auto retConnectCount = m_ipSecurityCheck.emplace(remoteIp, 1);
					if (retConnectCount.second == false) {
						if (retConnectCount.first->second >= 100) {
							retConnectCount.first->second = 0;
							m_ipBlacklistSystem[remoteIp] = std::time(nullptr);

							allowConnect = false;
						}

						retConnectCount.first->second++;
					}
				}
			}
		}

		if (allowConnect == true) {

			std::unique_lock<std::mutex> ul(m_mutexSocket);
			m_sockets.emplace(std::make_pair( socket, timerManager));
		}
		else {

			if (m_enableSSL) {
				socket->GetSocketSSL()->shutdown(ignore);
				//socket->GetSocketSSL()->lowest_layer().close(ignore);
			}
			else {
				socket->GetSocket()->shutdown(boost::asio::ip::tcp::socket::shutdown_both, ignore);
				//socket->GetSocket()->close(ignore);
			}
		}
	}
	/*
	void Server::AddToken(const String& token, const String& roleId) {
		std::unique_lock<std::mutex> ul(m_mutexToken);
		m_tokens.emplace(token,std::make_pair(roleId,std::time(nullptr)));
	}

	bool Server::VerifyToken(const String& token, const String& roleId) {
		std::unique_lock<std::mutex> ul(m_mutexToken);
		auto itToken = m_tokens.find(token);
		if (m_tokens.end() != itToken){
			if (roleId == itToken->second.first) {
				m_tokens.erase(itToken);
				return true;
			}
			else {
				m_tokens.erase(itToken);
				return false;
			}
		}
		else {
			return false;
		}
	}*/

	void Server::HandleAccept(const boost::system::error_code& ec, boost::shared_ptr<Socket> socket, boost::shared_ptr<TMInfo> timerManager) {
		if (!m_run || !m_acceptor.is_open())
		{
			return;
		}

		if (ec) {
			LogError("Server::HandleAccept %s", ec.message().c_str());
		}
		else {
			if (m_enableSSL) {
				socket->GetSocketSSL()->async_handshake(boost::asio::ssl::stream_base::server, boost::bind(&Server::HandleShake, this, boost::placeholders::_1, socket, timerManager));
			}
			else {
				this->AcceptSucceed(socket, timerManager);
			}
		}

		DoAccept();
	}

	void Server::HandleShake(const boost::system::error_code& ec, boost::shared_ptr<Socket> socket, boost::shared_ptr<TMInfo> timerManager) {
		if (!m_run || !m_acceptor.is_open())
		{
			return;
		}

		if (ec) {
			LogError("Server::HandleShake %s", ec.message().c_str());
		}
		else {
			this->AcceptSucceed(socket, timerManager);
		}

		DoAccept();
	}

	void Server::DoAccept() {

		auto timerManager = App::Instance().GeTimerManager();
		boost::shared_ptr<Socket> socket;
		if (m_enableSSL) {
			socket = boost::make_shared<Socket>(timerManager->tm->GetIoService(), *m_sslContext);
			m_acceptor.async_accept(socket->GetSocketSSL()->lowest_layer(), boost::bind(&Server::HandleAccept, this, boost::placeholders::_1, socket, timerManager));
		}
		else {
			socket = boost::make_shared<Socket>(timerManager->tm->GetIoService());
			m_acceptor.async_accept(*socket->GetSocket(), boost::bind(&Server::HandleAccept, this, boost::placeholders::_1, socket, timerManager));
		}
	}

    void Server::AddSession(UInt32 sessionId,Object* session) {
		std::unique_lock<std::mutex> ul(m_mutexSession);
		m_sessions.emplace(sessionId, session);
	}

	void Server::RemoveSession(UInt32 sessionId) {
		std::unique_lock<std::mutex> ul(m_mutexSession);
		m_sessions.erase(sessionId);
	}

	ObjectRef Server::GetSession(UInt32 sessionId) {
		std::unique_lock<std::mutex> ul(m_mutexSession);
		auto itSession = m_sessions.find(sessionId);
		if (m_sessions.end() != itSession) {
			return itSession->second;
		}
		else {
			return nullptr;
		}
	}


	UInt32 Server::GetOnlineNumber() {
		std::unique_lock<std::mutex> ul(m_mutexSession);
		return m_sessions.size();
	}

	void Server::Stop() {
		poco_assert_msg(Poco::Thread::currentTid() == g_mainThreadId, "Server::Stop calls must be is main thread!");

		if (m_run) {
			m_run = false;


			m_timerCreateSession->Stop();
			m_timerCreateSession = nullptr;

			m_timerUpdateRoleToken->Stop();
			m_timerUpdateRoleToken = nullptr;

			
			try
			{
				g_callMethod(boost::python::borrowed(m_obj), "OnDestory");
				//boost::python::call_method<void>(m_obj, "OnDestory");
				this->OnDestory();
			}
			catch (const std::exception& e)
			{
				LogException("Server::Stop %s", e.what());
			}
			PythonCallbackException
			

			{
				std::unique_lock<std::mutex> ul(m_mutexSession);
				
				for (auto& session : m_sessions) {
                    ((Session*)session.second.Get())->Stop(false);
				}
				m_sessions.clear();
			}

			m_acceptor.cancel();
			m_acceptor.close();

			m_timerMgr->Stop();
			m_timerMgr.reset();
		}
	}

	void Server::Start
	(	
		const String& listenAddress,
		const String& listenAddressWan
	) {
		poco_assert_msg(m_run == false, "Cannot repeat call 'Start'");
		poco_assert_msg(Poco::Thread::currentTid() == g_mainThreadId, "Server::Start calls must be is main thread!");

		m_run = true;

		m_ipSecurityCheckResetTime = std::time(nullptr);

		try {

			/*m_thread = std::thread([this]() {
				while (m_run)
				{
					try {
						m_ioService.run();
					}
					catch (std::exception& e) {
						LogException("Server::Start %s",e.what());
					}

					m_ioService.stop();
					m_ioService.reset();
				}
			});*/


			boost::asio::ip::tcp::resolver resolver(App::Instance().GetIoService());
			String listenIp;
			String listenPort;
			{
				auto index = listenAddress.rfind(':');
				listenIp = listenAddress.substr(0,index);
				listenPort = listenAddress.substr(index + 1);
			}

			m_listenAddress = listenAddress;
			m_listenAddressWan = listenAddressWan;

			boost::asio::ip::tcp::endpoint endpoint = *resolver.resolve({ listenIp,listenPort });
			m_acceptor.open(endpoint.protocol());
			m_acceptor.set_option(boost::asio::ip::tcp::acceptor::reuse_address(true));

			boost::system::error_code ec;
			m_acceptor.bind(endpoint, ec);

			if (ec) {
				LogError("Server::Start %s", ec.message().c_str());
				return;
			}

			m_acceptor.listen();

			m_timerUpdateRoleToken = m_timerMgr->CreateTimer([this]() {
				auto now = std::time(nullptr);
				std::unique_lock<std::mutex> ul(m_mutexToken);

				std::vector<decltype(m_tokens.begin())> removeTokens;
				for (auto itToken = m_tokens.begin(); itToken != m_tokens.end() ;++itToken) {
					if ((now - itToken->second.second) > 60) {
						removeTokens.emplace_back(itToken);
					}
				}

				for (auto& v : removeTokens) {
					m_tokens.erase(v);
				}
			});

			m_timerUpdateRoleToken->Start(30000);

			m_timerCreateSession = App::Instance().CreateTimer([this]() {

				std::unique_lock<std::mutex> ul(m_mutexSocket);
				if (!m_sockets.empty()) {
					auto sockets = std::move(m_sockets);
					ul.unlock();

					while (!sockets.empty())
					{
						auto& socket = sockets.front();

						try {

							auto cp = boost::make_shared<Session::CreateParam>();
							cp->socket = socket.first;
							cp->server = this;
							cp->timerManager = socket.second;

							boost::python::object objSession = m_clsSession(cp);
							SessionPtr sessionPtr = boost::python::extract<SessionPtr>(objSession.ptr());

							try
							{
								sessionPtr->OnCreate();
								g_callMethod(boost::python::borrowed(sessionPtr->GetObject()), "OnCreate");
								//boost::python::call_method<void>(sessionPtr->GetObject(), "OnCreate");
							}
							catch (const std::exception& e)
							{
								LogException("Session::Start %s", e.what());
							}
							PythonCallbackException
							
							this->AddSession(sessionPtr->GetSessionId(), sessionPtr.get());
						}
						catch (std::exception& e) {
							LogException("App::CreateSession %s", e.what());
						}
						PythonCallbackException

						sockets.pop();
					}
				}

			});


			m_timerCreateSession->Start(500);

			DoAccept();

			try
			{
				this->OnCreate();
				g_callMethod(boost::python::borrowed(m_obj), "OnCreate");
				//boost::python::call_method<void>(m_obj, "OnCreate");
			}
			catch (const std::exception& e)
			{
				LogException("Server::Start %s", e.what());
			}
			PythonCallbackException

			LogNormal("Server::Start listen %s:%s", listenIp.c_str(), listenPort.c_str());
			
		}
		catch (std::exception& e) {
			LogException("Server::Start %s", e.what());
		}
	}


	void Server::SendMsg(const MessagePtr& message, UInt32 sessionId) {
		std::unique_lock<std::mutex> ul(m_mutexSession);
		auto itSession = m_sessions.find(sessionId);
		if (m_sessions.end() != itSession) {
			auto session = itSession->second;
			ul.unlock();

            ((Session*)session.Get())->SendMsg(message);
		}
		else {
			LogDebug("Server::SendMsg no find sessionId:%lld", sessionId);
		}
	}

}
