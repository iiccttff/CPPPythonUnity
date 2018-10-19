#pragma once


#include "FastNet/core/Message.h"
#include "FastNet/core/Callback.h"
#include "FastNet/timer/TimerManager.h"
#include "FastNet/pkt/protocols.h"
#include "FastNet/core/Socket.h"

namespace FastNet {


    class FASTNET_API Client :public Object,public Callback {
	public:
		Client(PyObject* obj);
		virtual ~Client();

		void Connect
			(
			const std::string& serverAddress,
			UInt32 reconnectCount,
			const std::string& subscribeKey = "",
			UInt32 serverId = 0,
			bool enableSSL = false
			);

		void Close();

		bool IsConnect();

		void SendMsg(const MessagePtr& message);

		std::function<void(SocketEvent, const std::string&)> OnSocketEvent;
		std::function<void(const std::string&)> OnRoleLogin;

		UInt32 ServerId()const { return m_serverId; }
		UInt32 SessionId()const { return m_sessionId; }
		String Token()const { return m_token; }

		void AccountVerify(String channel, String jsonData);
		void RoleLogin(String roleId);
		void RoleReconnect(const String& roleId, const String& token);

		void Publish(UInt32 id, const String& message,bool isPublic = false);
		void Subscribe(UInt32 id);
		void Unsubscribe(UInt32 id);

		UInt32 NetworkDelayMS() { return m_networkDelayMS; }

		String ServerAddress() { return m_serverAddress; }

	private:
		Client(const Client&) = delete;
		Client& operator = (const Client&) = delete;

		friend class App;
		friend class TimerManager;

		void DispatchSocketEvent(SocketEvent e, const std::string& msg);

		void DoSendMessage(const MessagePtr& message);
		void DoRecvMessage();

		void DoConnect(bool reconnect);
		void DoClose(const std::string& msg, bool reconnect = false);

        void OnSocketEventRes(const boost::shared_ptr<pkt::protocols::LocalSocketEvent>& message);
		void OnSocketConnectRes(const boost::shared_ptr<pkt::protocols::SocketConnect>& message);
		void OnRoleLoginRes(const boost::shared_ptr<pkt::protocols::RoleLoginRes>& message);
		void OnUpdateRoleTokenRes(const boost::shared_ptr<pkt::protocols::UpdateRoleTokenRes>& message);

        void OnRecvPackage(MessageHead* mh);

        void Reconnect();
	
		void HandleConnect(const boost::system::error_code& error,bool reconnect, ObjectRef selfRef);
		void HandleShake(const boost::system::error_code& error, bool reconnect, ObjectRef selfRef);

		void OnConnectSucceed(const ObjectRef& selfRef);

		bool OnVerifyCertificate(bool preverified, boost::asio::ssl::verify_context& ctx);
	private:

		UInt32 m_reconnectTime = 0;
		UInt32 m_reconnectCount = 0;
		UInt32 m_currentReconnectCount = 0;
		std::string m_serverAddress;

		std::string m_token;

        ObjectRef m_appRef;

		boost::shared_ptr<TMInfo> m_timerManager;
        std::shared_ptr<Socket> m_socket;
		
		TimerPtr m_timerHeartbeat;
		TimerPtr m_timerSendHeartbeat;
		TimerPtr m_timerReconnect;
		TimerPtr m_timerConnect;

        UInt8 m_status;

		MessageHead m_mh;
		Buffer m_buffer;

		UInt32 m_sessionId;

		UInt32 m_serverId;
		bool m_enableSSL;

		bool m_sendMessage = false;
		std::queue<MessagePtr> m_messages;

		std::shared_ptr<boost::asio::ssl::context> m_sslContext;

		std::string m_subscribeKey;

		UInt32 m_networkDelayMS;
	};

	typedef std::shared_ptr<Client> ClientPtr;

}
