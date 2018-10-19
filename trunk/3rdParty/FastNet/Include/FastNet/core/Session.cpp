#include "Session.h"
#include "Server.h"
#include "Log.h"

#include "Poco/UUIDGenerator.h"
#include "Poco/MemoryStream.h"
#include "FastNet/pkt/protocols.h"

#include "boost/asio.hpp"

#include "App.h"
#include "Stream.h"
#include "Helper.h"

#include "FastNet/role/RoleManager.h"
#include "FastNet/room/RoomManager.h"
#include "FastNet/store/StoreManager.h"

#include "boost/asio/buffers_iterator.hpp"

namespace FastNet {


	extern std::atomic<UInt64> g_inputNet;
	extern std::atomic<UInt64> g_outputNet;

	extern boost::python::object g_callMethod;

	Session::Session(PyObject* obj, boost::shared_ptr<CreateParam> cp)
        :Object(obj){
	
        boost::python::object objRef = boost::python::object(boost::python::borrowed(obj));
		objRef.attr("Server") = boost::python::borrowed(cp->server->GetObject());

		m_timerManager = cp->timerManager;
		m_sessionId = Poco::hash(Poco::UUIDGenerator::defaultGenerator().createOne().toString());
		m_socket = cp->socket;
		m_server = cp->server;
		m_serverRef = cp->server;
		m_callbacks = &cp->server->m_callbacks;

		m_appRef = &App::Instance();
		
		m_stop = false;
		m_sizeHead = 0;
		m_sizeContent = 0;

		m_updateTokenTime = 0;

		//m_bufferHead.resize(FastNet_MessageHeadSize);

		ObjectRef selfRef(this);
		m_timerManager->tm->GetIoService().post([this, selfRef]() {

			m_timerHeartbeat = m_timerManager->tm->CreateTimer([this, selfRef]() {
				this->Stop(true,"heartbeat timeout");
			});

			m_timerHeartbeat->Start(10000);

			DoRead();
		});	

		//LogDebug("Session::Session() %lld", m_sessionId);
    }

	Session::~Session() {
		//LogDebug("Session::~Session() %lld", m_sessionId);

        //this->Stop();

		poco_assert_dbg(m_stop);
	}

	void Session::Stop(bool remove,const String& info) {
		LogDebug("Session::Stop %s" , info.c_str() );

		if (m_stop) {
			return;
		}

		m_stop = true;

		if (remove) {
			m_server->RemoveSession(m_sessionId);
		}

		auto subscribeIds = m_subscribeIds;
		for (auto& v : subscribeIds) {
			m_server->Unsubscribe(v,this);

			auto subscribeRes = Message::Create<pkt::protocols::UnsubscribeRes>();
			subscribeRes->id = v;
			this->SendMsg(subscribeRes);
		}
		
		m_subscribeIds.clear();

		ObjectRef selfRef(this);

		auto roleId = m_roleId;
		m_roleId.clear();

		App::Instance().GetIoService().dispatch([this, selfRef, roleId]() {

			try
			{
				g_callMethod(boost::python::borrowed(m_obj), "OnDestory");
				this->OnDestory();

				if (!roleId.empty()) {
					auto role = RoleManager::Instance()->GetRole(roleId,"");
					if (role && role->GetSession() == this) 
					{
						RoleManager::Instance()->Disconnect(role, this);
					}
				}
			}
			catch (const std::exception& e)
			{
				LogException("Session::Stop %s", e.what());
			}
		});
		
		m_timerManager->tm->GetIoService().dispatch([this, selfRef]() {

			boost::system::error_code ec;
			if (m_socket->IsEnableSSL()) {
				m_socket->GetSocketSSL()->lowest_layer().cancel(ec);
			}
			else {
				m_socket->GetSocket()->cancel(ec);
			}

			m_timerHeartbeat->Stop();
			m_timerHeartbeat = nullptr;
		});

	}

	void Session::SendMsg(const MessagePtr& message) {

        auto qr = new Callback::Queue();
		qr->info = nullptr;
		qr->message = message;
        qr->ref = this;

		if (!m_timerManager->queueSend.push(qr)) {
			poco_assert_dbg(false);
        }
	}


	void Session::SendErrorCode(const String& errCode, const String& msg) {
		auto errorMessage = Message::Create<pkt::protocols::ErrorMessage>();
		errorMessage->key = errCode;
		errorMessage->msg = msg;
		this->SendMsg(errorMessage);
	}


	void Session::DoSendFile() {

		while (!m_downloadFiles.empty()) {
			auto itDownloadFile = m_downloadFiles.begin();

			if (itDownloadFile->second.empty()) {
				m_downloadFiles.erase(itDownloadFile);
				continue;
			}
			else {
				auto& downloadFilePart = itDownloadFile->second.front();
				auto& fileName = itDownloadFile->first;
				
				auto downloadFileRes = Message::Create<pkt::protocols::DownloadFileRes>();
				downloadFileRes->file = fileName;
				downloadFileRes->indexPart = downloadFilePart.first;

				if (App::Instance().GetFileData(fileName, downloadFilePart.first, downloadFilePart.second, downloadFileRes->data)) {
					DoSendMessage(downloadFileRes);
				}
				else {
					LogError("App::DoSendFile %s get data fail!", fileName.c_str());
				}

				itDownloadFile->second.pop_front();
			}
			
		}
	}


	void Session::DoSendBuffer() {
		try {
			if (m_sendMessage) {
				return;
			}

			m_sendMessage = true;

			auto buffers = std::make_shared<std::vector<boost::asio::const_buffer> >();
			auto bufferPtrs = std::make_shared<std::vector<BufferPtr> >();

			UInt32 bufferSize = 0;
			while (!m_buffers.empty()) {
				auto buffer = m_buffers.front();
				m_buffers.pop();

				if ((bufferSize + buffer->size()) > FastNet_MaxMessageLength && bufferSize > 0) {
					break;
				}

				bufferSize += buffer->size();
				
				bufferPtrs->emplace_back(buffer);
				buffers->emplace_back(boost::asio::buffer(*buffer));
			}

			ObjectRef selfRef(this);
			auto onWrite = [this, selfRef, buffers, bufferPtrs, bufferSize](const boost::system::error_code& ec, std::size_t bytesTransferred) {

				for (auto& v : *bufferPtrs) {
					m_timerManager->queueSendBuffer.emplace(v);
				}
				
				if (ec) {
					Stop(true, "onWrite:" + Poco::format("error code %?i", ec.value()));
					return;
				}
				else if (bytesTransferred != bufferSize) {
					Stop(true, Poco::format("bytesTransferred %?i != buffersize %?i", bytesTransferred, bufferSize));
					return;
				}
				else {
					m_sendMessage = false;

					g_outputNet += bufferSize;

					if (!m_buffers.empty()) {
						this->DoSendBuffer();
					}
					else if (!m_downloadFiles.empty()) {
						this->DoSendFile();
					}
				}
			};

			if (m_socket->IsEnableSSL()) {
				boost::asio::async_write(*m_socket->GetSocketSSL(), *buffers, onWrite);
			}
			else {
				boost::asio::async_write(*m_socket->GetSocket(), *buffers, onWrite);
			}

		}
		catch (std::exception& e) {
			LogException("Session::DoSendMessage %s", e.what());
			Stop(true, e.what());
		}
	}

    void Session::DoSendMessage(const MessagePtr& message) {

		if (m_stop) {
			return;
		}

		try {
			
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

			m_buffers.emplace(sendBuffer);

			DoSendBuffer();
		}
		catch (std::exception& e) {
			LogException("Session::DoSendMessage %s", e.what());
			Stop(true, e.what());
		}

	}

	void Session::OnRecvPackage(MessageHead* mh) {

		if (mh->id == pkt::protocols::SocketClose::sClsId())
		{
			Stop(true, "client close");
			return;
		}
		else {

			m_timerHeartbeat->Update(10000);

			try {
				MessagePtr message = ClassFactory::Instance()->Create(mh->id);

				if (mh->size > 0) {

					if (mh->signatureId != message->SignId()) {
						LogWarning("Session::ReadContent signId check error,message %s", message->ClsName());
						return;
					}

					Poco::MemoryInputStream mis((char*)&m_bufferContent.at(0), m_bufferContent.size());
					FastNet::StreamRead stream(mis);
					message->Deserialize(stream);
				}

				if (mh->id == pkt::protocols::RoomMessageReq::sClsId()) {
					auto rmq = boost::dynamic_pointer_cast<pkt::protocols::RoomMessageReq>(message);

					MessagePtr roomMessage = ClassFactory::Instance()->Create(rmq->clsId);
					if (roomMessage == nullptr) {
						LogError("Session::ReadContent no find room message id:%d", rmq->clsId);
					}
					else {

						if (rmq->signId == roomMessage->SignId()) {

							if (rmq->data.size() > 0) {
								Poco::MemoryInputStream mis(rmq->data.c_str(), rmq->data.size());
								FastNet::StreamRead stream(mis);
								roomMessage->Deserialize(stream);
							}

							RoomManager::Instance()->OnRoomMessage(rmq->roomId, rmq->roleId, roomMessage);
						}
						else {
							LogWarning("Session::ReadContent signId check error,room message clsId:%d", rmq->clsId);
						}
					}
				}
				else if (mh->id == pkt::protocols::SocketHeartbeat::sClsId()) {
					this->DoSendMessage(message);

					auto now = std::time(nullptr);
					if (m_updateTokenTime != 0 && (now - m_updateTokenTime) > 60) {
						m_updateTokenTime = now;

						auto updateRoleTokenRes = Message::Create<pkt::protocols::UpdateRoleTokenRes>();
						updateRoleTokenRes->token = Poco::UUIDGenerator::defaultGenerator().createOne().toString();;
						this->DoSendMessage(updateRoleTokenRes);

						std::unique_lock<std::mutex> ul(m_server->m_mutexToken);
						m_server->m_tokens[m_roleId] = std::make_pair(updateRoleTokenRes->token, now);
					}
				}
				else {

					auto itCallback = m_callbacks->find(mh->id);
					if (m_callbacks->end() == itCallback) {
						LogError("Session::ReadContent no register callback? message id:%lld", mh->id);
						return;
					}

					auto qr = new Callback::Queue();
					qr->info = &itCallback->second;
					qr->message = message;
					message.reset();

					qr->ref = this;

					//if (itCallback->second.mainThread) {
					App::Instance().PushRecvMessage(qr);
					//}
					/*else {
						if (!m_timerManager->queueRecv.push(qr)) {
							poco_assert_dbg(false);
						}
					}*/
				}
			}
			catch (std::exception& e) {
				LogException("Session::ReadContent %s", e.what());
				Stop(true, e.what());
			}

		}
	}

	void Session::DoRead() {
		if (m_stop) {
			return;
		}

		ObjectRef selfRef(this);

		auto onReadHead = [this, selfRef](boost::system::error_code ec, std::size_t bytes_transferred)
		{
			if (m_stop) {
				return;
			}
			else if (ec)
			{
				Stop(true, "onReadHead:" + Poco::format("error code %?i", ec.value()) );
				return;
			}
			else if (bytes_transferred == FastNet_MessageHeadSize)
			{
				if (m_mh.size >= FastNet_MaxMessageLength) {
					Stop(true, "m_mh.size too long");
					return;
				}

				if (m_mh.size == 0) {
					OnRecvPackage(&m_mh);

					DoRead();
				}
				else {
					m_bufferContent.resize(m_mh.size);

					g_inputNet += bytes_transferred;


					auto onReadData = [this, selfRef](boost::system::error_code ec, std::size_t bytes_transferred)
					{
						if (m_stop) {
							return;
						}
						else if (ec) {
							Stop(true, "onReadData:" + Poco::format("error code %?i", ec.value()));
							return;
						}
						else if (bytes_transferred != m_bufferContent.size()) {
							Stop(true, "bytes_transferred error");
							return;
						}
						else {
							g_inputNet += bytes_transferred;

							OnRecvPackage(&m_mh);

							DoRead();
						}
					};

					if (m_socket->IsEnableSSL()) {
						boost::asio::async_read(*m_socket->GetSocketSSL(), boost::asio::buffer(m_bufferContent), onReadData);
					}
					else {
						boost::asio::async_read(*m_socket->GetSocket(), boost::asio::buffer(m_bufferContent), onReadData);
					}
				}
			}
			else {
				this->DoRead();
			}
		};

		if (m_socket->IsEnableSSL()) {
			boost::asio::async_read(*m_socket->GetSocketSSL(), boost::asio::buffer(&m_mh, FastNet_MessageHeadSize), onReadHead);
		}
		else {
			boost::asio::async_read(*m_socket->GetSocket(), boost::asio::buffer(&m_mh, FastNet_MessageHeadSize), onReadHead);
		}

	}




	UInt32 Session::GetSessionId() {
		return m_sessionId;
	}


	void Session::DownloadFileListReq(const boost::shared_ptr<pkt::protocols::DownloadFileListReq>& message) {

		auto downloadFiles = m_server->GetDownloadFiles();

		static const UInt32 s_maxBlockSize = FastNet_MaxMessageLength - FastNet_MessageHeadSize;
		auto downloadFileListRes = Message::Create<pkt::protocols::DownloadFileListRes>();

		for (auto& v : message->files) {
			if (m_downloadFiles.find(v) != m_downloadFiles.end()) {
				continue;
			}

			auto itDownloadFile = downloadFiles->find(v);
			if (downloadFiles->end() != itDownloadFile) {

				auto fileSize = itDownloadFile->second;
				if (fileSize < 1) {
					continue;
				}

				UInt32 fileOffet = 0;
				auto& file = m_downloadFiles[v];
				downloadFileListRes->files.emplace(v, fileSize);

				while (fileSize > s_maxBlockSize) {
					file.emplace_back(fileOffet, s_maxBlockSize);
					fileOffet += s_maxBlockSize;
					fileSize -= s_maxBlockSize;
				}

				if (fileSize > 0) {
					file.emplace_back(fileOffet, fileSize);
					fileOffet += fileSize;
					fileSize = 0;
				}
			}
		}

		this->SendMsg(downloadFileListRes);
	}

	void Session::PublishReq(const boost::shared_ptr<pkt::protocols::PublishReq>& message) {
		if (m_isPublicSubscribe) {
			message->isPublic = true;
		}

		m_server->Publish(message->id, message->message, message->isPublic);
	}

	void Session::SubscribeReq(const boost::shared_ptr<pkt::protocols::SubscribeReq>& message) {


		m_server->Subscribe(message->id,this);

		if (m_subscribeIds.emplace(message->id).second) {
			auto subscribeRes = Message::Create<pkt::protocols::SubscribeRes>();
			subscribeRes->id = message->id;
			m_server->BroadcastMsg(subscribeRes);
		}	
	}

	void Session::UnsubscribeReq(const boost::shared_ptr<pkt::protocols::UnsubscribeReq>& message) {


		m_server->Unsubscribe(message->id,this);

		auto itSubscribeId = m_subscribeIds.find(message->id);
		if (itSubscribeId != m_subscribeIds.end()) {
			auto subscribeRes = Message::Create<pkt::protocols::UnsubscribeRes>();
			subscribeRes->id = message->id;
			m_server->BroadcastMsg(subscribeRes);

			m_subscribeIds.erase(itSubscribeId);
		}
	}

	void Session::AccountVerifySucceed(const String& account,const String& channel) {
		try
		{
			m_account = account;
			g_callMethod(boost::python::borrowed(m_obj),"OnAccountVerifySucceed", boost::python::make_tuple(account, channel));
			//boost::python::call_method<void>(m_obj, "OnAccountVerifySucceed", account, channel);
			this->OnAccountVerifySucceed(account, channel);
		}
		catch (const std::exception& e)
		{
			LogException("Session::AccountVerifySucceed %s", e.what());
		}
	}

	void Session::RoleLogin(const boost::shared_ptr<pkt::protocols::RoleLoginReq>& message) {
		try
		{
			if (m_account.empty()) {
				this->SendErrorCode("AccountNoVerify");
				return;
			}

			if (message->roleId == m_roleId) {
				this->SendErrorCode("RoleAlreadyLogin");
				return;
			}
			

			{
				auto role = RoleManager::Instance()->GetRole(message->roleId, "", false);
				if (role != nullptr && role->GetStatus() == Role::Status::Online) {
					auto session = role->GetSession();
					if (session != nullptr) {
						session->SendErrorCode("AccountLoginOtherDevice");
					}
				}
			}

			{
				auto roleIds = StoreManager::Instance()->GetRoleIds(m_account);
				if (roleIds.end() == roleIds.find(message->roleId)) {
					this->SendErrorCode("NoFindRole");
					return;	
				}
			}

			m_roleId = message->roleId;
			
			this->OnRoleLogin(message->roleId);
			RolePtr role = boost::python::extract<RolePtr>(g_callMethod(boost::python::borrowed(m_obj), "OnRoleLogin", boost::python::make_tuple( message->roleId )));
			//RolePtr role = boost::python::call_method<RolePtr>(m_obj, "OnRoleLogin", message->roleId, message->reconnect);
			
			if (role == nullptr) {
				LogException("Session::RoleLogin roleId '%s' login fail! callback == nullptr", m_roleId.c_str());
				m_roleId.clear();
			}
			else {

				if (role->GetStatus() == Role::Status::WaitReconnect) {
					RoleManager::Instance()->Reconnect(role, this);
				}
				else {
					RoleManager::Instance()->Login(role, this);
				}	

				auto roleLoginRes = Message::Create<pkt::protocols::RoleLoginRes>();
				roleLoginRes->roleId = m_roleId;
				roleLoginRes->token = Poco::UUIDGenerator::defaultGenerator().createOne().toString();;
				this->SendMsg(roleLoginRes);

				m_updateTokenTime = std::time(nullptr);

				std::unique_lock<std::mutex> ul(m_server->m_mutexToken);
				m_server->m_tokens[m_roleId] = std::make_pair(roleLoginRes->token, m_updateTokenTime);
			}
		}
		catch (const std::exception& e)
		{
			LogException("Session::RoleLogin %s", e.what());
		}
	}
	

	void Session::RoleReconnectReq(const boost::shared_ptr<pkt::protocols::RoleReconnectReq>& message) {

		auto now = std::time(nullptr);
		std::unique_lock<std::mutex> ul(m_server->m_mutexToken);
		auto itToken = m_server->m_tokens.find(message->roleId);

		if (m_server->m_tokens.end() != itToken && 
			itToken->second.first == message->token && 
			(now - itToken->second.second) < 180 
			) 
		{

			m_server->m_tokens.erase(itToken);
			

			auto role = RoleManager::Instance()->GetRole(message->roleId, "" , false);
			if (role) {
				m_roleId = message->roleId;

				auto roleLoginRes = Message::Create<pkt::protocols::RoleLoginRes>();
				roleLoginRes->roleId = m_roleId;
				roleLoginRes->token = Poco::UUIDGenerator::defaultGenerator().createOne().toString();;
				this->SendMsg(roleLoginRes);

				m_updateTokenTime = std::time(nullptr);
				m_server->m_tokens.emplace(m_roleId, std::make_pair(roleLoginRes->token, m_updateTokenTime));
			}

			ul.unlock();

			if (role) {
				if (role->GetStatus() == Role::Status::WaitReconnect) {
					RoleManager::Instance()->Reconnect(role, this);
				}
				else {
					RoleManager::Instance()->Login(role, this);
				}
			}
		}

	}


	void Session::SocketConnectReq(const boost::shared_ptr<pkt::protocols::SocketConnectReq>& message) {	
		//m_deviceId = message->deviceId;
		auto socketConnect = Message::Create<pkt::protocols::SocketConnect>();
		socketConnect->sessionId = m_sessionId;
		socketConnect->serverId = m_server->Id();

		auto md5Values = m_server->GetMd5Values();
		if (md5Values->size() > 0) {
			socketConnect->md5Values = *md5Values;
		}
		
		m_isPublicSubscribe = message->subscribeKey != m_server->SubscribeKey();
		this->SendMsg(socketConnect);
	}

	void Session::AccountVerifyReq(const boost::shared_ptr<pkt::protocols::AccountVerifyReq>& message) {

		m_roleId.clear();
		m_account.clear();

		Helper::Instance()->AccountVerify(this, message->channel, message->jsonData);
	}
	
}
