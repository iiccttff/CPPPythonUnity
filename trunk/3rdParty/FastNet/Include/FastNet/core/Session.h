#pragma once

#include "FastNet/core/Message.h"
#include "FastNet/core/Callback.h"
#include "FastNet/timer/TimerManager.h"

#include "FastNet/core/Socket.h"
#include "FastNet/pkt/protocols.h"

namespace FastNet {
    class SessionImpl;
    class Server;

    class FASTNET_API Session : public Object
	{

	public:
		struct CreateParam {
			Server* server;
			boost::shared_ptr<Socket> socket;
			boost::shared_ptr<TMInfo> timerManager;
		};

		Session(PyObject* obj, boost::shared_ptr<CreateParam> cp);
		virtual ~Session();

		void SendMsg(const MessagePtr&);
		void SendErrorCode(const String& errCode,const String& msg = "");
		Server* GetServer() { return m_server; }

		UInt32 GetSessionId();

		virtual void OnCreate() {}
		virtual void OnDestory() {}

		virtual void OnAccountVerifySucceed(const String& uid, const String& channel) {}
		virtual void OnRoleLogin(const String& roleId) {}

		void Stop(bool remove = true,const String& info = "");

		const String GetRoleId() const { return m_roleId; }

		bool IsPublicSubscribe() {return m_isPublicSubscribe;}

		void AccountVerifySucceed(const String& account, const String& channel);

	private:

		Session(const Session&) = delete;
		Session& operator = (const Session&) = delete;

		void DoSendMessage(const MessagePtr& message);
		void DoSendBuffer();
		void DoSendFile();
		void DoRead();

		friend class App;
		friend class Server;
		friend class TimerManager;
		friend class Helper;

		void RoleLogin(const boost::shared_ptr<pkt::protocols::RoleLoginReq>& message);
		void SocketConnectReq(const boost::shared_ptr<pkt::protocols::SocketConnectReq>& message);
		void AccountVerifyReq(const boost::shared_ptr<pkt::protocols::AccountVerifyReq>& message);
		void RoleReconnectReq(const boost::shared_ptr<pkt::protocols::RoleReconnectReq>& message);
	
		void PublishReq(const boost::shared_ptr<pkt::protocols::PublishReq>& message);
		void SubscribeReq(const boost::shared_ptr<pkt::protocols::SubscribeReq>& message);
		void UnsubscribeReq(const boost::shared_ptr<pkt::protocols::UnsubscribeReq>& message);

		void DownloadFileListReq(const boost::shared_ptr<pkt::protocols::DownloadFileListReq>& message);

		//void GotoConnectReq(const boost::shared_ptr<pkt::protocols::GotoConnectReq>& message);
		//void GotoServerReq(const boost::shared_ptr<pkt::protocols::GotoServerReq>& message);
		
	private:
        void OnRecvPackage(MessageHead*);
	private:
        std::atomic<bool> m_stop;

		UInt32 m_sessionId = 0;

        ObjectRef m_appRef;
        ObjectRef m_serverRef;
		Server* m_server = nullptr;

        boost::shared_ptr<TMInfo> m_timerManager;
		boost::shared_ptr<Socket> m_socket;

        std::array<UInt8,1024> m_readBuffer;

        UInt32 m_sizeHead = 0;
        UInt32 m_sizeContent = 0;
		//Buffer m_bufferHead;
		MessageHead m_mh;
		Buffer m_bufferContent;

		TimerPtr m_timerHeartbeat;

		std::map<UInt32, Callback::Info>* m_callbacks = nullptr;

		bool m_sendMessage = false;
		//std::queue<MessagePtr> m_messages;

		std::shared_ptr<boost::asio::ssl::context> m_sslContext;

		String m_roleId;
		String m_account;

		std::set<UInt32> m_subscribeIds;

		bool m_isPublicSubscribe = true;

		UInt32 m_updateTokenTime;
		
		std::map<String,std::deque<std::pair<UInt32,UInt32> > > m_downloadFiles;
		
		std::queue<BufferPtr> m_buffers;
	};

	typedef boost::shared_ptr<Session> SessionPtr;
}
