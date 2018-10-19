#include "Log.h"
#include <iostream>

#include "Poco/Path.h"
#include "Poco/File.h"
#include "Poco/LocalDateTime.h"
#include "Poco/Format.h"
#include "Poco/Process.h"
#include "Poco/Thread.h"
#include "Poco/ObjectPool.h"
#include "Poco/FileStream.h"

#include "boost/lockfree/queue.hpp"
//#include "leveldb/db.h"  
//#include "leveldb/write_batch.h" 
#include "FastNet/pkt/protocols.h"

#include "FastNet/core/App.h" 
#include "FastNet/core/Session.h" 

#include <stdarg.h>


#include "Poco/Data/Date.h"
#include "Poco/Data/SQLChannel.h"
#include "Poco/Data/SessionFactory.h"
#include "Poco/Data/SQLite/Connector.h"
#include "Poco/Data/SQLite/Utility.h"
#include "Poco/Data/SQLite/Notifier.h"
#include "Poco/Data/SQLite/Connector.h"
#include "Poco/Data/RecordSet.h"


#include "boost/interprocess/ipc/message_queue.hpp"

namespace FastNet {

	extern std::string g_workPath;
	extern bool g_consoleLog;
	extern boost::python::object JsonConfigs;

	struct LogInfo {
		String log;
		String type;
		Poco::DateTime time;
	};

	struct QueryTaskInfo {
		char key[64];
		Poco::UInt32 beginTime;
		Poco::UInt32 endTime;
	};


	struct QueryTaskRes {
		Poco::UInt32 type;
		Poco::UInt32 time;
		char key[64];
		char log[128];
	};

	boost::lockfree::queue<LogInfo*, boost::lockfree::capacity<16384> > g_cacheLogs;
	Poco::ObjectPool<LogInfo> g_logInfoPool(10000, 10000);

	extern UInt32 g_appId;

	//using namespace leveldb;

	class LogHelper {
	public:


		void run() {
			while (!g_cacheLogs.empty()) {
				LogInfo* log = nullptr;
				g_cacheLogs.pop(log);

				try {

					if (g_consoleLog || !m_session) {

						Poco::LocalDateTime ldt(log->time);

						std::string logText;
						Poco::format(logText, "[%?i-%02?i-%02?i %02?i:%02?i:%02?i.%05?i][%s] - %s",
							ldt.year(),
							ldt.month(),
							ldt.day(),
							ldt.hour(),
							ldt.minute(),
							ldt.second(),
							ldt.millisecond(),
							log->type,
							log->log);

						std::cout << logText << std::endl;
					}

					if (m_session) {
						*m_session << "INSERT INTO logs VALUES(?, ?, ?)",
							Poco::Data::Keywords::useRef(log->type),
							Poco::Data::Keywords::useRef(log->log),
							Poco::Data::Keywords::bind((UInt64)log->time.timestamp().epochTime()),
							Poco::Data::Keywords::now;
					}

				}
				catch (std::exception& e) {
					std::cerr << "LogHelper::OnTimerWriteLog " << e.what() << std::endl;
				}

				g_logInfoPool.returnObject(log);
			}


			QueryTaskInfo qti;
			boost::interprocess::message_queue::size_type recvd_size;
			unsigned int priority;

			while (m_run) {

				try {
					if (!m_messageQueueR->try_receive(&qti, sizeof(qti), recvd_size, priority)) {
						break;
					}

					Poco::Data::Statement stmt(*m_session);

					if (strcmp(qti.key,"AllLog") != 0) {
						stmt << "SELECT * FROM logs WHERE vType=? and vTime>=? and vTime<=?;", \
							Poco::Data::Keywords::useRef(qti.key),
							Poco::Data::Keywords::useRef(qti.beginTime),
							Poco::Data::Keywords::useRef(qti.endTime),
							Poco::Data::Keywords::now;
					}
					else {
						stmt << "SELECT * FROM logs WHERE (vType='Normal' or vType='Debug' or vType='Warning' or vType='Error' or vType='Exception') and vTime>=? and vTime<=?;", \
							Poco::Data::Keywords::useRef(qti.beginTime),
							Poco::Data::Keywords::useRef(qti.endTime),
							Poco::Data::Keywords::now;
					}

					Poco::Data::RecordSet rset(stmt);
					auto itEnd = rset.end();
					for (auto itBegin = rset.begin(); itBegin != itEnd; ++itBegin)
					{
						QueryTaskRes qtr = {'\0'};
						qtr.type = 1;

						String key = itBegin->get(0);
						String log = itBegin->get(1);

						if (key.size() <= 64) {
							strncpy(qtr.key, key.c_str(), key.size());
						}

						if (key.size() <= 128) {
							strncpy(qtr.log, log.c_str(), log.size());
						}

						qtr.time = itBegin->get(2);

						if (!m_messageQueueW->try_send(&qtr, sizeof(qtr), 0)) {
							std::cerr << "LogHelper::OnLogQuery try_send == false!" << std::endl;
							continue;
						}
					}

					QueryTaskRes qtr;
					qtr.type = 0;

					if (!m_messageQueueW->try_send(&qtr, sizeof(qtr), 0)) {
						std::cerr << "LogHelper::OnLogQuery try_send == false!" << std::endl;
						return;
					}

				}
				catch (std::exception &e) {
					std::cerr << "LogHelper::OnLogQuery " << e.what() << std::endl;
				}
			}
		}

		LogHelper() 
		{
			Poco::Data::SQLite::Connector::registerConnector();

			m_run = true;

			m_timerMgr = std::make_shared<TimerManager>(false);
			m_timerMgrR = std::make_shared<TimerManager>(false);

			m_timerWriteLog = m_timerMgr->CreateTimer(std::bind(&LogHelper::run,this));
			m_timerWriteLog->Start(2000);

			try {
				String messageQueueNameW = "FastNet_MessageQueueW_S" + std::to_string(g_appId);
				String messageQueueNameR = "FastNet_MessageQueueR_S" + std::to_string(g_appId);

				boost::interprocess::message_queue::remove(messageQueueNameW.c_str());
				boost::interprocess::message_queue::remove(messageQueueNameR.c_str());

				m_messageQueueW = std::make_shared<boost::interprocess::message_queue>(
					boost::interprocess::create_only, messageQueueNameW.c_str(), 1000, sizeof(QueryTaskRes));

				m_messageQueueR = std::make_shared<boost::interprocess::message_queue>(
					boost::interprocess::create_only, messageQueueNameR.c_str(), 1000, sizeof(QueryTaskInfo));

				m_session = std::make_shared<Poco::Data::Session>(Poco::Data::SQLite::Connector::KEY, g_workPath + "/log.db");
				*m_session << "CREATE TABLE IF NOT EXISTS logs (vType VARCHAR(16), vLog VARCHAR, vTime INTEGER)", Poco::Data::Keywords::now;
			}
			catch (std::exception& e) {
				std::cerr << "LogHelper::OnTimerWriteLog " << e.what() << std::endl;
			}

		}

		~LogHelper() {
			m_run = false;
			m_timerWriteLog->Stop();
			m_timerWriteLog.reset();

			run();

			m_timerMgr->Stop();
			m_timerMgr.reset();

			m_timerMgrR->Stop();
			m_timerMgrR.reset();

			m_session.reset();

			m_messageQueueW.reset();
			m_messageQueueR.reset();

			Poco::Data::SQLite::Connector::unregisterConnector();
		}

		static void Write(const String& type, const std::string& v) {
			try {
				auto log = g_logInfoPool.borrowObject();
				if (!log) {
					std::cerr << "Log::Write() borrowObject == nullptr!" << std::endl;
					return;
				}

				log->log = v;
				log->type = type;
				log->time = Poco::DateTime();

				g_cacheLogs.push(log);
			}
			catch (std::exception& e) {
				std::cerr << "LogHelper::Write " << e.what() << std::endl;
			}
			
		}

		static void Write(const String& type, const char * format, va_list& args) {
			try {
				auto log = g_logInfoPool.borrowObject();
				if (!log) {
					std::cerr << "Log::Write() borrowObject == nullptr!" << std::endl;
					return;
				}

				log->log.resize(1024);

				int ret = vsnprintf(&log->log.at(0), 1024 - 3, format, args);
				if (ret < 0) {
					std::cerr << "Log::Write() vsnprintf ret < 0!" << std::endl;
					return;
				}

				log->log.resize(ret);
				log->type = type;
				log->time = Poco::DateTime();

				g_cacheLogs.push(log);

			}
			catch (std::exception& e) {
				std::cerr << "LogHelper::Write " << e.what() << std::endl;
			}
		}

		void AddLogQueryTask(const String& key, UInt32 beginTime, UInt32 endTime, UInt32 appId, const ObjectRef& session) {

			m_timerMgrR->GetIoService().post([this, key, beginTime, endTime, appId, session] () {
				auto sessionPtr = session.Get<Session>();
				if (sessionPtr == nullptr) {
					return;
				}

				if (key.length() >= 100) {
					std::cerr << "AddLogQueryTask key size:" << key.length() << " too long!" << std::endl;
					return;
				}

				QueryTaskInfo qti;
				memset(qti.key, '\0', 64);
				memcpy(qti.key, key.c_str(), key.length());
				qti.beginTime = beginTime;
				qti.endTime = endTime;

				String messageQueueNameW = "FastNet_MessageQueueR_S" + std::to_string(appId);
				String messageQueueNameR = "FastNet_MessageQueueW_S" + std::to_string(appId);

				boost::interprocess::message_queue messageQueueW(boost::interprocess::open_only, messageQueueNameW.c_str());
				boost::interprocess::message_queue messageQueueR(boost::interprocess::open_only, messageQueueNameR.c_str());

				QueryTaskRes qtr;
				boost::interprocess::message_queue::size_type recvd_size;
				unsigned int priority;

				while (messageQueueR.try_receive(&qtr, sizeof(QueryTaskRes), recvd_size, priority)) {

				}

				if (!messageQueueW.try_send(&qti, sizeof(qti), 0)) {
					std::cerr << "AddLogQueryTask try_send == false!" << std::endl;
					return;
				}

				boost::shared_ptr<pkt::protocols::LogQueryRes> logQueryRes;

				UInt32 sleepTime = 0;

				while (m_run)
				{
					if (sleepTime >= 30000) {
						break;
					}

					if (!messageQueueR.try_receive(&qtr, sizeof(QueryTaskRes), recvd_size, priority) || recvd_size != sizeof(QueryTaskRes)) {
						std::this_thread::sleep_for(std::chrono::milliseconds(100));
						sleepTime += 100;
						continue;
					}

					if (qtr.type == 0) {
						if (!logQueryRes) {
							logQueryRes = Message::Create<pkt::protocols::LogQueryRes>();
						}

						logQueryRes->isEnd = true;
						sessionPtr->SendMsg(logQueryRes);
						break;
					}
					else {
						if (!logQueryRes) {
							logQueryRes = Message::Create<pkt::protocols::LogQueryRes>();
							logQueryRes->logs.reserve(100);
							logQueryRes->isEnd = false;
						}
						

						logQueryRes->logs.emplace_back(pkt::protocols::LogInfo());
						auto& logInfo = logQueryRes->logs.back();

						logInfo.log = qtr.log;
						logInfo.key = qtr.key;
						logInfo.time = qtr.time;

						if (logQueryRes->logs.size() >= 100) {
							sessionPtr->SendMsg(logQueryRes);
							logQueryRes = nullptr;
						}
					}
				}
			});

		}


		void AddLogQueryTaskNotRun(const String& key, UInt32 beginTime, UInt32 endTime, UInt32 appId, const ObjectRef& session) {

			m_timerMgrR->GetIoService().post([this, key, beginTime, endTime, appId, session]() {
				auto sessionPtr = session.Get<Session>();
				if (sessionPtr == nullptr) {
					return;
				}

				if (key.length() >= 100) {
					std::cerr << "AddLogQueryTask key size:" << key.length() << " too long!" << std::endl;
					return;
				}

				try {
					Poco::Data::Session session(Poco::Data::SQLite::Connector::KEY, Poco::format("%s/childs/work/%?i/log.db", g_workPath, appId));

					
					Poco::Data::Statement stmt(session);
					
					if (key != "AllLog") {
						stmt << "SELECT * FROM logs WHERE vType=? and vTime>=? and vTime<=?;", \
							Poco::Data::Keywords::useRef(key),
							Poco::Data::Keywords::useRef(beginTime),
							Poco::Data::Keywords::useRef(endTime),
							Poco::Data::Keywords::now;
					}
					else {
						stmt << "SELECT * FROM logs WHERE (vType='Normal' or vType='Debug' or vType='Warning' or vType='Error' or vType='Exception') and vTime>=? and vTime<=?;", \
							Poco::Data::Keywords::useRef(beginTime),
							Poco::Data::Keywords::useRef(endTime),
							Poco::Data::Keywords::now;
					}

					Poco::Data::RecordSet rset(stmt);

					boost::shared_ptr<pkt::protocols::LogQueryRes> logQueryRes;
					auto itEnd = rset.end();
					for (auto itBegin = rset.begin(); itBegin != itEnd; ++itBegin)
					{
						if (!logQueryRes) {
							logQueryRes = Message::Create<pkt::protocols::LogQueryRes>();
							logQueryRes->logs.reserve(100);
							logQueryRes->isEnd = false;
						}

						logQueryRes->logs.emplace_back(pkt::protocols::LogInfo());
						auto& logInfo = logQueryRes->logs.back();

						logInfo.log = itBegin->get(1).convert<String>();
						logInfo.key = itBegin->get(0).convert<String>();
						logInfo.time = itBegin->get(2);

						if (logQueryRes->logs.size() >= 100) {
							sessionPtr->SendMsg(logQueryRes);
							logQueryRes = nullptr;
						}
					}

					if (!logQueryRes) {
						logQueryRes = Message::Create<pkt::protocols::LogQueryRes>();
					}

					logQueryRes->isEnd = true;
					sessionPtr->SendMsg(logQueryRes);

				}
				catch (std::exception& e) {
					std::cerr << "AddLogQueryTaskNotRun: " << e.what() << std::endl;
				}

			});

		}

	private:

		bool m_run = false;

		std::shared_ptr<TimerManager> m_timerMgrR;
		std::shared_ptr<TimerManager> m_timerMgr;
		TimerPtr m_timerWriteLog;

		std::shared_ptr<Poco::Data::Session> m_session;

		std::shared_ptr<boost::interprocess::message_queue> m_messageQueueW;
		std::shared_ptr<boost::interprocess::message_queue> m_messageQueueR;
	};


	std::unique_ptr<LogHelper> s_log;

	void FASTNET_API LogNormal(const char* log,...) {
		va_list args;
		va_start(args, log);
		LogHelper::Write("Normal", log, args);
		va_end(args);
	}

	void FASTNET_API LogDebug(const char* log, ...) {

#ifdef DEBUG
		va_list args;
		va_start(args, log);
		LogHelper::Write("Debug", log, args);
		va_end(args);
#endif
	}

	void FASTNET_API LogWarning(const char* log, ...) {
		va_list args;
		va_start(args, log);
		LogHelper::Write("Warning", log, args);
		va_end(args);
	}

	void FASTNET_API LogError(const char* log, ...) {
		va_list args;
		va_start(args, log);
		LogHelper::Write("Error", log, args);
		va_end(args);
	}

	void FASTNET_API LogException(const char* log, ...) {
		va_list args;
		va_start(args, log);
		LogHelper::Write("Exception", log, args);
		va_end(args);
	}

	void FASTNET_API LogEvent(const String& key,const char* fmt, ...) {
		va_list args;
		va_start(args, fmt);
		LogHelper::Write(key, fmt, args);
		va_end(args);
	}


	void FASTNET_API LogNormal(const std::string& log) {
		LogHelper::Write("Normal", log);
	}

	void FASTNET_API LogDebug(const std::string& log) {
#if defined(_DEBUG) || defined(DEBUG)
		LogHelper::Write("Debug", log);
#endif
	}

	void FASTNET_API LogWarning(const std::string& log) {
		LogHelper::Write("Warning", log);
	}

	void FASTNET_API LogError(const std::string& log) {
		LogHelper::Write("Error", log);
	}

	void FASTNET_API LogException(const std::string& log) {
		LogHelper::Write("Exception", log);
	}

	void FASTNET_API LogEvent(const String& key,const std::string& log) {
		s_log->Write(key, log);
	}

	void Initialize_Log() {
		s_log.reset(new LogHelper());
	}

	void Finalize_Log() {
		s_log.reset();
	}

	void AddLogQueryTask(const String& key,UInt32 beginTime,UInt32 endTime,UInt32 appId, SessionPtr session) {
		if (s_log) {
			s_log->AddLogQueryTask(key, beginTime, endTime, appId, session.get());
		}
	}

	void AddLogQueryTaskNotRun(const String& key, UInt32 beginTime, UInt32 endTime, UInt32 appId, SessionPtr session) {
		if (s_log) {
			s_log->AddLogQueryTaskNotRun(key, beginTime, endTime, appId, session.get());
		}
	}
}
