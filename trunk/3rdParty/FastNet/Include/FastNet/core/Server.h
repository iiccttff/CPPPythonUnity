#pragma once


#include "FastNet/core/Session.h"
#include "FastNet/timer/TimerManager.h"
#include "FastNet/core/Callback.h"
#include "FastNet/core/Client.h"

namespace FastNet {

    class FASTNET_API Server :public Object, public Callback {
	public:
		Server(PyObject* obj,boost::python::object clsSession,UInt32 serverId, bool enableSSL = false,std::string certificatePassword = "");
		virtual ~Server();

		void Start(
			const String& listenAddress,
			const String& listenAddressWan
		);

		void Stop();

		void SendMsg(const MessagePtr& message,UInt32 sessionId);

		virtual void OnCreate() {}
		virtual void OnDestory() {}


		void ClearWhitelist();
		void ClearBlacklist();

		void AddIpToWhitelist(const std::string& ip);
		void AddIpToBlacklist(const std::string& ip);

		void DeleteIpFromWhitelist(const std::string& ip);
		void DeleteIpFromBlacklist(const std::string& ip);

		void BeginRepair();
		void EndRepair();
		bool IsRepair();

		UInt32 Id() { return m_id; }

		String GetListenAddress() { return m_listenAddress; }
		String GetListenAddressWan() { return m_listenAddressWan; }
		
		std::string GetCertificatePassword() const { return m_certificatePassword; }

		void Publish(UInt32 id,const String& message,bool isPublic);
		void Subscribe(UInt32 id, Object* session);
		void Unsubscribe(UInt32 id, Object* session);

		void AllowSubPub(bool val);
		void SetSubscribeKey(const String& key) { m_subscribeKey=key; }
		const String& SubscribeKey() {return m_subscribeKey;}

		
		void BroadcastMsg(const MessagePtr& message, const std::function<bool(Session*)>& f = nullptr);
		void BroadcastMsg_Python(const MessagePtr& message, PyObject* obj = nullptr);

		UInt32 GetOnlineNumber();

		void SetMd5Values(const String& v);

	private:
		friend class App;
		friend class Session;

		Server(const Server&) = delete;
		Server& operator = (const Server&) = delete;

		void DoAccept();
		void AcceptSucceed(boost::shared_ptr<Socket> socket, boost::shared_ptr<TMInfo>);
		void HandleAccept(const boost::system::error_code& error, boost::shared_ptr<Socket> socket, boost::shared_ptr<TMInfo>);
		void HandleShake(const boost::system::error_code& error, boost::shared_ptr<Socket> socket, boost::shared_ptr<TMInfo>);

        void AddSession(UInt32 sessionId, Object* session);
		void RemoveSession(UInt32 sessionId);
		ObjectRef GetSession(UInt32 sessionId);

		std::shared_ptr<String> GetMd5Values();
		std::shared_ptr<std::map<String, UInt32>> GetDownloadFiles();

	private:

        std::atomic<bool> m_run;

        ObjectRef m_appRef;

		boost::python::object m_clsSession;

		std::shared_ptr<TimerManager> m_timerMgr;

		boost::asio::ip::tcp::acceptor m_acceptor;

		std::mutex m_mutexSession;
        std::map<UInt32, ObjectRef > m_sessions;

		std::mutex m_mutexSocket;
		std::queue<std::pair<boost::shared_ptr<Socket>,
			boost::shared_ptr<TMInfo> > > m_sockets;

		TimerPtr m_timerCreateSession;
		TimerPtr m_timerUpdateRoleToken;

		std::set<std::string> m_ipWhitelist;
		std::set<std::string> m_ipBlacklist;

		std::map<std::string,UInt32> m_ipSecurityCheck;
		std::map<std::string,std::time_t> m_ipBlacklistSystem;
		std::time_t m_ipSecurityCheckResetTime;

		UInt32 m_id;
		bool m_enableSSL;

		std::string m_certificatePassword;

		std::shared_ptr<boost::asio::ssl::context> m_sslContext;

		std::atomic<bool> m_isRepair;

		std::mutex m_mutexSubscribeId;
		std::map<UInt32, std::set<Object*> > m_subscribeIds;

		std::atomic<bool> m_allowSubPub;

		String m_subscribeKey;

		String m_listenAddress, m_listenAddressWan;

		std::mutex m_mutexToken;
		std::unordered_map<String, std::pair<String, UInt32> > m_tokens;


		std::shared_ptr<String> m_md5Values;
		std::shared_ptr<std::map<String, UInt32> > m_downloadFiles;
	};

}
