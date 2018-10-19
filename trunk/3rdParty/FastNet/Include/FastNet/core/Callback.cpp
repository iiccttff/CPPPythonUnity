#include "Callback.h"
#include "ClassFactory.h"

namespace FastNet {
	extern Poco::Thread::TID g_mainThreadId;

	std::atomic<UInt64> s_queueCount(0);

	Callback::Queue::Queue() {
		s_queueCount++;
	}

	Callback::Queue::~Queue() {
		s_queueCount--;
	}

	Callback::Callback() {
		
	}

	void Callback::BindMessage_Python(UInt32 id, const std::string& name) {
		poco_assert_msg(Poco::Thread::currentTid() == g_mainThreadId, "Callback::BindMessage_Python calls must be is main thread!");

		if (!ClassFactory::Instance()->IsClass(id)) {
			PyErr_SetString(PyExc_RuntimeError, "Callback::BindMessage_Python id no find!");
			return;
		}

		Info info;
		info.name = name;
		auto ret = m_callbacks.emplace(id, info);
		if (!ret.second) {
			PyErr_SetString(PyExc_RuntimeError, "Callback::BindMessage_Python id repeat!");
		}
	}

	void Callback::DoBindMessage(UInt32 id, const Func& f) {
		poco_assert_msg(Poco::Thread::currentTid() == g_mainThreadId, "Client::DoBindMessage calls must be is main thread!");

		if (!ClassFactory::Instance()->IsClass(id)) {
			PyErr_SetString(PyExc_RuntimeError, "Callback::DoBindMessage id no find!");
			return;
		}

		Info ci;
		ci.func = f;
		auto ret = m_callbacks.emplace(id, ci);
		if (!ret.second) {
			PyErr_SetString(PyExc_RuntimeError, "Callback::DoBindMessage id repeat!");
		}
	}
}