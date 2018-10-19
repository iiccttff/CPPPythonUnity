#include "Client.h"
#include "App.h"
#include "Log.h"
#include "Poco/UUIDGenerator.h"
#include "Poco/MemoryStream.h"

#include "boost/random/random_device.hpp"
#include "boost/random/uniform_int_distribution.hpp"
#include <codecvt>
#include <locale>

namespace FastNet {

	extern boost::python::object g_callMethod;
	extern Poco::Thread::TID g_mainThreadId;
	extern std::string g_workPath;

	enum class ClientStatus {
		NoConnect = 1,
		Connecting,
		ConnectSucceed,
		ConnectFailure,
        ConnectCloseing,
		ConnectClosed,
		ReConnecting,
		ReConnectFailure
	};

	Client::Client(PyObject* obj)
        : Object(obj)
		, m_timerManager(App::Instance().GeTimerManager()){

		m_status = (UInt8)ClientStatus::NoConnect;

        m_appRef = &App::Instance();

		m_sessionId = 0;

        this->BindMessage<Client, pkt::protocols::LocalSocketEvent>(&Client::OnSocketEventRes);
		this->BindMessage<Client, pkt::protocols::SocketConnect>(&Client::OnSocketConnectRes);
		this->BindMessage<Client, pkt::protocols::RoleLoginRes>(&Client::OnRoleLoginRes);
		this->BindMessage<Client, pkt::protocols::UpdateRoleTokenRes>(&Client::OnUpdateRoleTokenRes);
    }
	
    Client::~Client() {

	}

	void Client::AccountVerify(String channel, String jsonData)
	{
		auto accountVerifyReq = Message::Create<pkt::protocols::AccountVerifyReq>();
		accountVerifyReq->channel = channel;
		accountVerifyReq->jsonData = jsonData;
		this->SendMsg(accountVerifyReq);
	}

	void Client::RoleLogin(String roleId)
	{
		auto roleLoginReq = Message::Create<pkt::protocols::RoleLoginReq>();
		//roleLoginReq->token = m_token;
		roleLoginReq->roleId = roleId;
		this->SendMsg(roleLoginReq);
	}

	void Client::RoleReconnect(const String& roleId,const String& token) {
		auto roleReconnectReq = Message::Create<pkt::protocols::RoleReconnectReq>();
		roleReconnectReq->token = token;
		roleReconnectReq->roleId = roleId;
		this->SendMsg(roleReconnectReq);
	}

	bool Client::OnVerifyCertificate(bool preverified, boost::asio::ssl::verify_context& ctx) {
		return preverified;
	}

	void Client::OnSocketEventRes(const boost::shared_ptr<pkt::protocols::LocalSocketEvent>& message) {

		try
		{
			if (this->OnSocketEvent) {
				this->OnSocketEvent((SocketEvent)message->evt, message->info);
			}
			
			g_callMethod(boost::python::borrowed(m_obj), "OnSocketEvent", boost::python::make_tuple((SocketEvent)message->evt, message->info));
		}
		catch (const std::exception& e)
		{
			LogException("Client::OnSocketEvent %s", e.what());
		}
	}

	void Client::OnRoleLoginRes(const boost::shared_ptr<pkt::protocols::RoleLoginRes>& message) {
		try
		{
			if (this->OnRoleLogin) {
				this->OnRoleLogin(message->roleId);
			}

			g_callMethod(boost::python::borrowed(m_obj), "OnRoleLogin", boost::python::make_tuple(message->roleId));

			m_token = message->token;
		}
		catch (const std::exception& e)
		{
			LogException("Client::OnRoleLoginRes %s", e.what());
		}
	}

	void Client::OnUpdateRoleTokenRes(const boost::shared_ptr<pkt::protocols::UpdateRoleTokenRes>& message) {
		m_token = message->token;
	}

	

	void Client::OnSocketConnectRes(const boost::shared_ptr<pkt::protocols::SocketConnect>& message) {
		if (m_status == (UInt8)ClientStatus::ConnectSucceed) {
			m_sessionId = message->sessionId;
			m_serverId = message->serverId;
			DispatchSocketEvent(SocketEvent::kConnectSucceed, "connect succeed!");
		}
	}

	void Client::Connect
		(
		const std::string& serverAddress,
		UInt32 reconnectCount,
		const std::string& subscribeKey,
		UInt32 serverId,
		bool enableSSL
		) {

		poco_assert_msg(g_mainThreadId == Poco::Thread::currentTid(), "Client::Connect calls must be is main thread!");

        ObjectRef selfRef(this);
		m_timerManager->tm->GetIoService().dispatch([this, serverAddress,reconnectCount,selfRef, subscribeKey, serverId, enableSSL](){

            if (m_status == (UInt8)ClientStatus::NoConnect ||
                m_status == (UInt8)ClientStatus::ConnectFailure ||
                m_status == (UInt8)ClientStatus::ReConnectFailure ||
				m_status == (UInt8)ClientStatus::ConnectClosed ) {

				m_serverId = serverId;
				m_enableSSL = enableSSL;

                m_status = (UInt8)ClientStatus::Connecting;

                m_serverAddress = serverAddress;
                m_reconnectCount = reconnectCount;
                m_currentReconnectCount = 0;
                m_reconnectTime = 800;
				m_subscribeKey = subscribeKey;

                DoConnect(true);
            }
            else {
                
            }
        });
	}

	void Client::OnConnectSucceed(const ObjectRef& selfRef) {
		m_currentReconnectCount = 0;
		m_reconnectTime = 800;
		m_sendMessage = false;
		m_networkDelayMS = 0;

		m_status = (UInt8)ClientStatus::ConnectSucceed;
		
		m_timerHeartbeat = m_timerManager->tm->CreateTimer([this, selfRef]() {
			DoClose("heartbeat timeout!", true);
		});

		m_timerSendHeartbeat = m_timerManager->tm->CreateTimer([this, selfRef]() {
			static auto s_socketHeartbeat = boost::make_shared<pkt::protocols::SocketHeartbeat>();

			auto time_now = std::chrono::system_clock::now();
			auto duration_in_ms = std::chrono::duration_cast<std::chrono::milliseconds>(time_now.time_since_epoch());
			s_socketHeartbeat->time = duration_in_ms.count();

			this->DoSendMessage(s_socketHeartbeat);
		});

		m_timerHeartbeat->Start(10000);
		m_timerSendHeartbeat->Start(3000);

		DoRecvMessage();

		if (m_timerConnect != nullptr) {
			m_timerConnect->Stop();
			m_timerConnect = nullptr;
		}

		static auto socketHeartbeat = boost::make_shared<pkt::protocols::SocketConnectReq>();
		socketHeartbeat->subscribeKey = m_subscribeKey;
		this->DoSendMessage(socketHeartbeat);
	}

	void Client::HandleShake(const boost::system::error_code& ec, bool reconnect, ObjectRef selfRef) {
		if (m_status != (UInt8)ClientStatus::ReConnecting &&
			m_status != (UInt8)ClientStatus::Connecting) {
			return;
		}

		if (ec) {
			if (reconnect) {
				DoClose(Poco::format("error code %?i", ec.value()), true);
			}
			else {
				m_status = (UInt8)ClientStatus::ConnectFailure;
				DispatchSocketEvent(SocketEvent::kConnectFailure, Poco::format("error code %?i", ec.value()));
			}
			return;
		}
		else {
			this->OnConnectSucceed(selfRef);
		}
	}

	void Client::HandleConnect(const boost::system::error_code& ec, bool reconnect, ObjectRef selfRef) {
		if (m_status != (UInt8)ClientStatus::ReConnecting &&
			m_status != (UInt8)ClientStatus::Connecting) {
			return;
		}

		if (ec) {
			if (reconnect) {
				DoClose(Poco::format("error code %?i", ec.value()), true);
			}
			else {
				m_status = (UInt8)ClientStatus::ConnectFailure;
				DispatchSocketEvent(SocketEvent::kConnectFailure, Poco::format("error code %?i", ec.value()));
			}
			return;
		}
		else {

			if (m_sslContext) {
				m_socket->GetSocketSSL()->async_handshake(boost::asio::ssl::stream_base::client, boost::bind(&Client::HandleShake, this, boost::placeholders::_1, reconnect, selfRef));
			}
			else {
				this->OnConnectSucceed(selfRef);
			}
		}
	}

	void Client::DoConnect(bool reconnect) {


		boost::system::error_code ec;
        boost::asio::ip::tcp::resolver resolver(m_timerManager->tm->GetIoService());

		String host, port;
		{
			auto index = m_serverAddress.rfind(':');
			host = m_serverAddress.substr(0, index);
			port = m_serverAddress.substr(index + 1);
		}

		boost::asio::ip::tcp::resolver::query query(host,port);
		boost::asio::ip::tcp::resolver::iterator iterator = resolver.resolve(query);


		boost::system::error_code ignored_ec;

		
        ObjectRef selfRef(this);

		if (m_enableSSL) {

			m_sslContext = std::make_shared<boost::asio::ssl::context>(boost::asio::ssl::context::sslv23);

			auto caPem = g_workPath + "/server_" + std::to_string(m_serverId) + ".crt";
			m_sslContext->load_verify_file(caPem);

			m_socket = std::make_shared<Socket>(m_timerManager->tm->GetIoService(), *m_sslContext);
			m_socket->GetSocketSSL()->set_verify_mode(boost::asio::ssl::verify_peer);
			m_socket->GetSocketSSL()->set_verify_callback(boost::bind(&Client::OnVerifyCertificate, this, _1, _2));

			auto socket = m_socket->GetSocketSSL();
			boost::asio::async_connect(socket->lowest_layer(), iterator, boost::bind(&Client::HandleConnect, this, boost::placeholders::_1, reconnect, selfRef));
		}
		else {
			m_socket = std::make_shared<Socket>(m_timerManager->tm->GetIoService());
			boost::asio::async_connect(*m_socket->GetSocket(), iterator, boost::bind(&Client::HandleConnect, this, boost::placeholders::_1, reconnect, selfRef));
		}

		if (m_timerConnect != nullptr) {
			m_timerConnect->Stop();
			m_timerConnect = nullptr;
		}

		m_timerConnect = m_timerManager->tm->CreateTimer([this, selfRef]() {
			DoClose("connect timeout!", true);
		});

		m_timerConnect->Start(10000, 1);
	}

	void Client::Close() {

        if (m_status == (UInt8)ClientStatus::NoConnect ||
            m_status == (UInt8)ClientStatus::ConnectClosed ||
            m_status == (UInt8)ClientStatus::ConnectCloseing ||
            m_status == (UInt8)ClientStatus::ConnectFailure ||
            m_status == (UInt8)ClientStatus::ReConnectFailure) {
            return;
        }

        m_status = (UInt8)ClientStatus::ConnectCloseing;

		poco_assert_msg(g_mainThreadId == Poco::Thread::currentTid(), "Client::Close calls must be is main thread!");

        ObjectRef selfRef(this);
		m_timerManager->tm->GetIoService().post([this, selfRef]() {
			DoClose("User Close", false);
		});
	}


    void Client::Reconnect()
    {
        if (m_status != (UInt8)ClientStatus::ConnectClosed) {
            return;
        }

        if (m_currentReconnectCount >= m_reconnectCount) {

            m_status = (UInt8)ClientStatus::ReConnectFailure;
            DispatchSocketEvent(SocketEvent::kReConnectFailure, "reconnect failure");
        }
        else {

            m_currentReconnectCount++;

            m_reconnectTime += 2000;
            if (m_reconnectTime > 45000) {
                m_reconnectTime = 45000;
            }

            m_status = (UInt8)ClientStatus::ReConnecting;
            DispatchSocketEvent(SocketEvent::kReConnecting, "reconnecting");

            if (m_timerReconnect) {
                m_timerReconnect->Stop();
            }

            ObjectRef selfRef(this);
            m_timerReconnect = m_timerManager->tm->CreateTimer([this, selfRef]() {
                if (this->IsConnect()) {
                    return;
                }

                m_status = (UInt8)ClientStatus::ReConnecting;
                DoConnect(true);
            });

            m_timerReconnect->Start(m_reconnectTime, 1);
        }
    }

	void Client::DoClose(const std::string& msg, bool reconnect) {

		LogDebug("Client::DoClose %s", msg.c_str());

        if (m_status == (UInt8)ClientStatus::ConnectClosed) {
            return;
        }

		if (reconnect == false) {
			static auto s_socketClose = boost::make_shared<pkt::protocols::SocketClose>();
			this->DoSendMessage(s_socketClose);
		}

		boost::system::error_code ignored_ec;
		if (m_enableSSL) {
			m_socket->GetSocketSSL()->lowest_layer().cancel(ignored_ec);
			m_socket->GetSocketSSL()->lowest_layer().close(ignored_ec);
			m_socket->GetSocketSSL()->lowest_layer().shutdown(boost::asio::socket_base::shutdown_both, ignored_ec);
		}
		else {
			m_socket->GetSocket()->cancel(ignored_ec);
			m_socket->GetSocket()->close(ignored_ec);
			m_socket->GetSocket()->shutdown(boost::asio::socket_base::shutdown_both, ignored_ec);
		}

		//m_socket = nullptr;

		if (m_timerHeartbeat) {
			m_timerHeartbeat->Stop();
		}
		
		if (m_timerSendHeartbeat) {
			m_timerSendHeartbeat->Stop();
		}

        if (m_timerReconnect) {
            m_timerReconnect->Stop();
        }

		if (m_timerConnect != nullptr) {
			m_timerConnect->Stop();
		}

        m_timerReconnect = nullptr;
        m_timerHeartbeat = nullptr;
        m_timerSendHeartbeat = nullptr;
		m_timerConnect = nullptr;


		m_status = (UInt8)ClientStatus::ConnectClosed;

        if (reconnect && m_reconnectCount > 0){
            this->Reconnect();
        }else{
            DispatchSocketEvent(SocketEvent::kConnectClosed, msg);
        }
	}

	bool Client::IsConnect() {

		if (m_status == (UInt8)ClientStatus::ConnectSucceed) {
			return true;
		}

		return false;
	}

	void Client::SendMsg(const MessagePtr& message) {

        if (m_status != (UInt8)ClientStatus::ConnectSucceed) {
			return;
		}

		auto qr = new Callback::Queue();
		qr->info = nullptr;
		qr->message = message;
        qr->ref = this;

		if (!m_timerManager->queueSend.push(qr)) {
			poco_assert_dbg(false);
        }
	}

	void Client::DoSendMessage(const MessagePtr& message) {

        if (!IsConnect()){
            return;
        }

		if (m_sendMessage) {
			m_messages.emplace(message);
			return;
		}

		try {
			m_sendMessage = true;

			MessageHead head;
			head.id = message->ClsId();
			head.signatureId = message->SignId();
            head.size = message->SerializeSize();

			BufferPtr sendBuffer;
            if (!m_timerManager->queueSendBuffer.empty()){
                sendBuffer = m_timerManager->queueSendBuffer.front();
                m_timerManager->queueSendBuffer.pop();
            }else{
                sendBuffer = boost::make_shared<Buffer>();
            }

            sendBuffer->resize(FastNet_MessageHeadSize + head.size);
            memcpy(&sendBuffer->at(0), &head, FastNet_MessageHeadSize);

            if (head.size > 0){
                Poco::MemoryOutputStream mos((char*)&sendBuffer->at(FastNet_MessageHeadSize),head.size);
				FastNet::StreamWrite stream(mos);
                message->Serialize(stream);
			}

            ObjectRef selfRef(this);

			auto onWrite = [this, sendBuffer, selfRef](const boost::system::error_code& ec, std::size_t bytesTransferred) {

				m_timerManager->queueSendBuffer.emplace(sendBuffer);

				if (!this->IsConnect()) {
					return;
				}

				if (ec) {
					DoClose(Poco::format("error code %?i", ec.value()), true);
					return;
				}
				else if (bytesTransferred != sendBuffer->size()) {
					DoClose("package send error", true);
					return;
				}
				else {
					m_sendMessage = false;

					if (!m_messages.empty()) {
						auto message = m_messages.front();
						m_messages.pop();
						this->DoSendMessage(message);
					}
				}
			};

			if (m_enableSSL) {
				boost::asio::async_write(*m_socket->GetSocketSSL(), boost::asio::buffer(*sendBuffer), onWrite);
			}
			else {
				boost::asio::async_write(*m_socket->GetSocket(), boost::asio::buffer(*sendBuffer), onWrite);
			}
            
		}
		catch (std::exception& e) {
			DoClose("DoSendMessage data error", false);
		}
	}


    void Client::OnRecvPackage(MessageHead* mh){
        if (!this->IsConnect()) {
            return;
        }

        try {

            MessagePtr message = ClassFactory::Instance()->Create(mh->id);

            if (mh->size > 0) {
                if (mh->signatureId != message->SignId()) {
                    DispatchSocketEvent(kErrorMessage, Poco::format("signatureId check error,message id:%?i", mh->id));
                    return;
                }

                Poco::MemoryInputStream mis((char*)&m_buffer.at(0), m_buffer.size());
				FastNet::StreamRead stream(mis);
                message->Deserialize(stream);
            }

			if (mh->id == pkt::protocols::SocketHeartbeat::sClsId()) {
				auto socketHeartbeat = boost::dynamic_pointer_cast<pkt::protocols::SocketHeartbeat>(message);
				auto time_now = std::chrono::system_clock::now();
				auto duration_in_ms = std::chrono::duration_cast<std::chrono::milliseconds>(time_now.time_since_epoch());
				m_networkDelayMS = duration_in_ms.count() - socketHeartbeat->time;
			}
			else {
				auto itCallback = m_callbacks.find(mh->id);
				if (m_callbacks.end() == itCallback) {
					DispatchSocketEvent(kErrorMessage, Poco::format("no register callback? message id:%?i", mh->id));
					return;
				}

				auto qr = new Callback::Queue();
				qr->info = &itCallback->second;
				qr->message = message;
				qr->ref = this;

				//if (itCallback->second.mainThread) {
				App::Instance().PushRecvMessage(qr);
				//}
				//else {

				//	if (!m_timerManager->queueRecv.push(qr)) {
				//		poco_assert_dbg(false);
				//	}
				//}
			}    
        }
        catch (std::exception& e) {
            DoClose(Poco::format("exception package:%s,message id:%?i", std::string(e.what()), mh->id));
            return;
        }
        

        m_timerHeartbeat->Update(10000);

		this->DoRecvMessage();
    }

	void Client::DoRecvMessage() {
        if (!IsConnect()) {
			return;
        }

        ObjectRef selfRef(this);
		auto onReadHead = [this, selfRef](boost::system::error_code ec, std::size_t bytes_transferred)
		{
			if (!IsConnect()) {
				return;
			}
			else if (ec) {
				DoClose(Poco::format("error code %?i", ec.value()), true);
				return;
			}
			else if (bytes_transferred == FastNet_MessageHeadSize) {

				if (m_mh.size >= FastNet_MaxMessageLength) {
					DoClose("m_mh.size too long", true);
					return;
				}

				if (m_mh.size == 0) {
					OnRecvPackage(&m_mh);
				}
				else {

					m_buffer.resize(m_mh.size);


					auto onReadData = [this, selfRef](boost::system::error_code ec, std::size_t bytes_transferred)
					{
						if (!IsConnect()) {
							return;
						}
						else if (ec) {
							DoClose(Poco::format("error code %?i",ec.value()), true);
							return;
						}
						else if (bytes_transferred != m_buffer.size()) {
							DoClose("bytes_transferred error", true);
							return;
						}
						else {
							OnRecvPackage(&m_mh);
						}
					};

					
					if (m_enableSSL) {
						boost::asio::async_read(*m_socket->GetSocketSSL(), boost::asio::buffer(m_buffer), onReadData);
					}
					else {
						boost::asio::async_read(*m_socket->GetSocket(), boost::asio::buffer(m_buffer), onReadData);
					}
				}
			}
			else {
				this->DoRecvMessage();
			}
		};

		if (m_enableSSL) {
			boost::asio::async_read(*m_socket->GetSocketSSL(), boost::asio::buffer(&m_mh, FastNet_MessageHeadSize), onReadHead);
		}
		else {
			boost::asio::async_read(*m_socket->GetSocket(), boost::asio::buffer(&m_mh, FastNet_MessageHeadSize), onReadHead);
		}
    }

	std::string gb2312_to_utf8(std::string const &strGb2312)
	{
		std::vector<wchar_t> buff(strGb2312.size());
#ifdef _MSC_VER
		std::locale loc("zh-CN");
#else
		std::locale loc("zh_CN.GB18030");
#endif
		wchar_t* pwszNext = nullptr;
		const char* pszNext = nullptr;
		mbstate_t state = {};
		int res = std::use_facet<std::codecvt<wchar_t, char, mbstate_t> >
			(loc).in(state,
				strGb2312.data(), strGb2312.data() + strGb2312.size(), pszNext,
				buff.data(), buff.data() + buff.size(), pwszNext);

		if (std::codecvt_base::ok == res)
		{
			std::wstring_convert<std::codecvt_utf8<wchar_t>> cutf8;
			return cutf8.to_bytes(std::wstring(buff.data(), pwszNext));
		}

		return "";
	}

	void Client::DispatchSocketEvent(SocketEvent e, const std::string& msg) {

        auto itCallback = m_callbacks.find(pkt::protocols::LocalSocketEvent::sClsId());
		if (m_callbacks.end() != itCallback) {

			auto qr = new Callback::Queue();
			qr->info = &itCallback->second;
            auto message = boost::make_shared<pkt::protocols::LocalSocketEvent>();
			message->evt = e;
			message->info = gb2312_to_utf8(msg);
			qr->message = message;
            qr->ref = this;

            App::Instance().PushRecvMessage(qr);
		}
	}

	void Client::Publish(UInt32 id, const String& msg,bool isPublic) {
		auto message = Message::Create<pkt::protocols::PublishReq>();
		message->id = id;
		message->message = msg;
		message->isPublic = isPublic;
		this->SendMsg(message);
	}

	void Client::Subscribe(UInt32 id) {
		auto message = Message::Create<pkt::protocols::SubscribeReq>();
		message->id = id;
		this->SendMsg(message);
	}

	void Client::Unsubscribe(UInt32 id) {
		auto message = Message::Create<pkt::protocols::UnsubscribeReq>();
		message->id = id;
		this->SendMsg(message);
	}
}
