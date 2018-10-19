#pragma once


#include "FastNet/core/Defs.h"
#include "FastNet/core/Object.h"
#include "FastNet/core/Singleton.h"

#include "FastNet/timer/Timer.h"
#include "FastNet/core/Session.h"

namespace FastNet {

	class FASTNET_API Helper final : public Singleton<Helper>{
	public:

		Helper();
		~Helper();

		virtual void OnCreate();
		virtual void OnDestory();

		void AccountVerify(Session* session,const String& channel, const String& data);
		void PutChannelCode(const String& channel, const String& code);

		bool AddAccount(const String& account, const String& password, const String& channel);
		bool DeleteAccount(const String& account, const String& channel);
		bool ModifyAccount(const String& account, const String& password, const String& channel);

		bool IsExistUserId(const String& uid);

	private:

		void runMsg(const String& jsonValue);

		void CheckProcess(boost::python::object& process);
	private:

		bool m_run;

		struct AccountVerifyReq {
			String data;
			String channel;
			ObjectRef session;
		};

		struct AccountVerifyRes {
			ObjectRef session;
			String uid;
			String channel;
		};

		Poco::Thread m_msgThread;

		std::mutex m_mutexAccountVerifyReq;
		std::queue<std::shared_ptr<AccountVerifyReq> > m_accountVerifyReqs;

		std::mutex m_mutexAccountVerifyRes;
		std::queue<std::shared_ptr<AccountVerifyRes> > m_accountVerifyRess;

		TimerPtr m_timerUpdate;
		TimerPtr m_timerUpdateToken;

		String m_token;

		boost::python::object m_accountVerifyProcess;
		boost::python::object m_helperProcess;

		Poco::Event m_event;

		std::shared_ptr<mongocxx::client> m_mongocxxClient;

		//std::atomic<UInt32> m_indexId;

		UInt16 m_httpPort, m_httpPort2;
	};

}