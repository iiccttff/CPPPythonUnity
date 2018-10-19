#include "Helper.h"
#include "Log.h"

#include "App.h"
#include "FastNet/store/StoreManager.h"

#include "boost/interprocess/mapped_region.hpp"
#include "boost/process.hpp"
#include "Poco/Process.h"
#include "boost/interprocess/ipc/message_queue.hpp"


#include "Poco/Net/HTTPClientSession.h"
#include "Poco/Net/HTTPRequest.h"
#include "Poco/MD5Engine.h"
#include "Poco/UUIDGenerator.h"


#if defined(POCO_OS_FAMILY_WINDOWS)
#undef max
#endif



namespace FastNet {
	extern std::string g_workPath;
	extern boost::python::object JsonConfigs;
	using namespace boost::interprocess;
	namespace bp = boost::process;

	using bsoncxx::builder::basic::kvp;
	using bsoncxx::builder::basic::make_document;
	using bsoncxx::builder::stream::open_document;
	using bsoncxx::builder::stream::close_document;

	extern std::string g_mongodbUri;
	extern std::string g_mongodbDB;

Helper::Helper() {

	m_run = true;
	m_msgThread.setName("Helper");
	m_msgThread.setPriority(Poco::Thread::Priority::PRIO_LOW);

	Poco::MD5Engine engine;
	engine.update(Poco::UUIDGenerator::defaultGenerator().createOne().toString());
	m_token = Poco::DigestEngine::digestToHex(engine.digest());
}

Helper::~Helper() {

}

void Helper::CheckProcess(boost::python::object& process) {
	
	boost::python::object moduleHelperProcess = boost::python::import("Helper");

	if (process.is_none() || true != (bool)boost::python::extract<bool>(moduleHelperProcess.attr("CheckProcess")(process))) {
		
		UInt16 port = 0;

		if (&process == &m_accountVerifyProcess) {
			port = m_httpPort2;
		}
		else {
			port = m_httpPort;
		}

		
		boost::python::object moduleOS = boost::python::import("os");

		Int32 currentPid = boost::python::extract<Int32>(moduleOS.attr("getpid")());

		bsoncxx::builder::stream::document startParams;

		startParams << "pid" << bsoncxx::types::b_int32{ currentPid };
		startParams << "mongodbUri" << bsoncxx::types::b_utf8{ g_mongodbUri };
		startParams << "mongodbDB" << bsoncxx::types::b_utf8{ g_mongodbDB };
		startParams << "workPath" << bsoncxx::types::b_utf8{ g_workPath };
		startParams << "token" << bsoncxx::types::b_utf8{ m_token };
		startParams << "port" << port;
		process = moduleHelperProcess.attr("RunProcess")(bsoncxx::to_json(startParams));

		if (&process == &m_helperProcess) {
			PutChannelCode("000", boost::python::extract<String>(moduleHelperProcess.attr("GetCode")(m_httpPort2)));
		}
	}
}

bool Helper::DeleteAccount(const String& account, const String& channel) {
	try {

		auto uid = StoreManager::AccountToUid(account, channel);

		if (!IsExistUserId(uid)) {
			return false;
		}
		else {
			auto db = m_mongocxxClient->database(g_mongodbDB);
			db["accounts"].delete_one(make_document(kvp("uid", uid)));
			return true;
		}
	}
	catch (std::exception& e) {
		LogException("Helper::DeleteAccount %s", e.what());
		return false;
	}
}

bool Helper::AddAccount(const String& account, const String& password,const String& channel) {


	try {

		auto uid = StoreManager::AccountToUid(account, channel);

		if (!IsExistUserId(uid)) {
			auto db = m_mongocxxClient->database(g_mongodbDB);
			Poco::MD5Engine engine;
			engine.update(password);

			db["accounts"].insert_one(
				make_document(
					kvp("channel", channel),
					kvp("account", account),
					kvp("uid", uid),
					kvp("password", Poco::DigestEngine::digestToHex(engine.digest())) )
			);
			return true;
		}
		else {
			return false;
		}
	}
	catch (std::exception& e) {
		LogException("Helper::AddAccount %s",e.what());
		return false;
	}
}

bool Helper::ModifyAccount(const String& account, const String& password, const String& channel) {
	try {

		auto uid = StoreManager::AccountToUid(account, channel);

		if (IsExistUserId(uid)) {
			auto db = m_mongocxxClient->database(g_mongodbDB);
			Poco::MD5Engine engine;
			engine.update(password);
			String encPassword = Poco::DigestEngine::digestToHex(engine.digest());

			mongocxx::options::update update;
			update.upsert(true);

			db["accounts"].update_one(
				make_document(kvp("uid", uid)),
				make_document(kvp("$set", make_document(kvp("password", encPassword)))),
				update
			);
			return true;
		}
		else {
			return false;
		}
	}
	catch (std::exception& e) {
		LogException("Helper::ModifyAccount %s", e.what());
		return false;
	}
}

bool Helper::IsExistUserId(const String& uid) {

	try {
		auto db = m_mongocxxClient->database(g_mongodbDB);
		auto role = db["accounts"].find_one(make_document(kvp("uid", uid)));
		if (!role) {
			return false;
		}
		else {
			return true;
		}
	}
	catch (...) {
		return false;
	}
}

void Helper::OnCreate() {
	
	m_run = true;

	auto cfgHelper = JsonConfigs["Helper"];


	m_httpPort = (UInt16)boost::python::extract<UInt16>(cfgHelper["httpPort"]);
	m_httpPort2 = (UInt16)boost::python::extract<UInt16>(cfgHelper["httpPort2"]);


	m_mongocxxClient = bsoncxx::stdx::make_unique<mongocxx::client>(mongocxx::uri(g_mongodbUri));

	
	using bsoncxx::builder::basic::kvp;
	using bsoncxx::builder::basic::make_document;
	try {
		auto db = m_mongocxxClient->database(g_mongodbDB);
		mongocxx::options::index index_options{};
		index_options.unique(true);

		db["accounts"].create_index(make_document(kvp("account", 1)), index_options);
		db["accounts"].create_index(make_document(kvp("uid", 1)), index_options);

		db["accountTokens"].create_index(make_document(kvp("token", 1)), index_options);
		db["accountTokens"].create_index(make_document(kvp("uid", 1)), index_options);
	}
	catch (...) {

	}

	AddAccount("admin", "123456", "000");

	m_msgThread.startFunc(std::bind(&Helper::runMsg,this, ""));

	m_event.tryWait(3000);

	m_timerUpdate = App::Instance().CreateTimer([this]() {

		std::unique_lock<std::mutex> ulResponse(m_mutexAccountVerifyRes);
		while (!m_accountVerifyRess.empty()) {
			auto response = m_accountVerifyRess.front();
			m_accountVerifyRess.pop();

			auto session = response->session.Get<Session>();
			if (response->uid.empty()) {
				session->SendErrorCode("AccountVerifyFail");
			}
			else {
				session->AccountVerifySucceed(response->uid, response->channel);
			}
		}
	});

	m_timerUpdate->Start(500);

	m_timerUpdateToken = App::Instance().CreateTimer([this]() {
		CheckProcess(m_accountVerifyProcess);
		CheckProcess(m_helperProcess);
	});

	m_timerUpdateToken->Start(5000,0,-1);
}

void Helper::OnDestory() {
	m_mongocxxClient.reset();

	m_timerUpdate->Stop();
	m_timerUpdate = nullptr;

	m_timerUpdateToken->Stop();
	m_timerUpdateToken = nullptr;

	m_run = false;
	if (m_msgThread.isRunning()) {
		m_msgThread.join();
	}

	m_helperProcess.attr("kill")();
	m_accountVerifyProcess.attr("kill")();
}



void Helper::AccountVerify(Session* session, const String& channel, const String& data) {
	std::unique_lock<std::mutex> ul(m_mutexAccountVerifyReq);

	auto accountVerifyInfo = std::make_shared<AccountVerifyReq>();
	accountVerifyInfo->channel = channel;
	accountVerifyInfo->data = data;
	accountVerifyInfo->session = session;
	m_accountVerifyReqs.emplace(accountVerifyInfo);
}

void Helper::PutChannelCode(const String& channel, const String& code) {

	std::ostringstream str;
	Poco::Base64Encoder encoder(str);
	encoder << code;
	encoder.close();

	bsoncxx::builder::stream::document doc;
	doc << "channel" << bsoncxx::types::b_utf8{ channel };
	doc << "code" << bsoncxx::types::b_utf8{ str.str() };
	doc << "token" << m_token;


	try {


		Poco::Net::HTTPClientSession c("127.0.0.1", m_httpPort);
		Poco::Net::HTTPRequest request(Poco::Net::HTTPRequest::HTTP_POST, "/PutChannelCode");
		
		String body = bsoncxx::to_json(doc);
		request.setContentLength(body.length());
		request.setContentType("application/json");

		c.sendRequest(request) << body;

		Poco::Net::HTTPResponse response;
		c.receiveResponse(response);
	}
	catch (Poco::Exception& e) {
		LogException("Helper::PutChannelCode %s",e.displayText().c_str());
	}
}


void Helper::runMsg(const String& jsonValue) {


	std::this_thread::sleep_for(std::chrono::milliseconds(30));
	m_event.set();

	auto mongocxxClient = bsoncxx::stdx::make_unique<mongocxx::client>(mongocxx::uri(g_mongodbUri));
	auto db = mongocxxClient->database(g_mongodbDB);

	while (m_run)
	{
		std::this_thread::sleep_for(std::chrono::milliseconds(100));

		std::unique_lock<std::mutex> ul(m_mutexAccountVerifyReq);
		if (!m_accountVerifyReqs.empty()) {
			auto queue(std::move(m_accountVerifyReqs));
			ul.unlock();

			while (!queue.empty())
			{
				try {
					auto f = queue.front();
					queue.pop();

					Poco::Net::HTTPClientSession c("127.0.0.1", m_httpPort);
					Poco::Net::HTTPRequest request(Poco::Net::HTTPRequest::HTTP_POST, "/AccountVerifyReq");

					bsoncxx::builder::stream::document doc;
					doc << "channel" << bsoncxx::types::b_utf8{ f->channel };
					doc << "data" << bsoncxx::types::b_utf8{ f->data };
					doc << "token" << m_token;

					String body = bsoncxx::to_json(doc);
					request.setContentLength(body.length());
					request.setContentType("application/json");
					c.sendRequest(request) << body;

					Poco::Net::HTTPResponse response;
					std::istream& rs = c.receiveResponse(response);
					auto contentLength = response.getContentLength();
					if (response.getStatus() == Poco::Net::HTTPResponse::HTTPStatus::HTTP_OK && contentLength > 0) {
						String jsonValue;
						Poco::StreamCopier::copyToString(rs, jsonValue);
						auto retDoc = bsoncxx::from_json(jsonValue);
						auto itStatus = retDoc.view().find("status");
						if (retDoc.view().end() != itStatus) {
							if (itStatus->get_int32().value == 1) {
								auto accountVerifyRes = std::make_shared<AccountVerifyRes>();
								accountVerifyRes->session = f->session;
								accountVerifyRes->uid = StoreManager::AccountToUid(retDoc.view()["uid"].get_utf8().value.to_string(), f->channel);
								accountVerifyRes->channel = f->channel;

								std::unique_lock<std::mutex> ulAccountVerifyRes(m_mutexAccountVerifyRes);
								m_accountVerifyRess.emplace(accountVerifyRes);
							}
							else {
								auto itMessage = retDoc.view().find("message");
								if (retDoc.view().end() != itMessage) {
									LogError("Helper::runMsg %s", itMessage->get_utf8().value.data());
								}
							}
						}
						else {
							LogError("Helper::runMsg retDoc.view() no find status!");
						}
					}

				}
				catch (Poco::Exception& e) {
					LogException("Helper::runMsg %s", e.displayText().c_str());
				}
			}
		}
	}


}

}
