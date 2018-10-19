#include "TimerManager.h"
#include "FastNet/core/Log.h"
#include "FastNet/core/Session.h"
#include "FastNet/core/Client.h"
#include "FastNet/core/App.h"


namespace FastNet {
	extern Poco::Thread::TID g_mainThreadId;

    TimerManager::TimerManager(bool mainThread, PyObject* obj)
        :Object(obj)
		, m_mainThread(mainThread)
	{
		m_ioServiceWrok.reset(new boost::asio::io_service::work(m_ioService));
		m_stop = false;

		if (!m_mainThread){
			m_thread.reset(new std::thread(std::bind(&TimerManager::Run,this)));
		}
	}

	TimerManager::~TimerManager()
	{
		this->Stop();
	}


	TimerPtr TimerManager::CreateTimer(const std::function<void(void)>& callback)
	{
        return boost::make_shared<Timer>(callback, m_ioService);
	}

	TimerPtr TimerManager::CreateTimer_Python(PyObject * obj, const std::string & methodName)
	{
		return boost::make_shared<Timer>(obj, methodName, m_ioService);
	}

	void TimerManager::Run()
	{
		while (!m_stop) {
			try {
				m_ioService.run();
			}
			catch (std::exception& e) {
				LogException("TimerManager::Run %s", e.what());

				m_ioService.reset();
			}
		}
	}

	void TimerManager::Update()
	{
		try {
			m_ioService.poll();
		}
		catch (std::exception& e) {
			LogException("TimerManager::Update %s", e.what());
		}
	}

	void TimerManager::Stop() {

        if (m_stop){
            return;
        }

        m_stop = true;

		m_ioServiceWrok.reset();


		if (!m_mainThread) {
			if (m_thread->joinable()) {
				m_thread->join();
			}

			m_thread.reset();
		}
	}

}

