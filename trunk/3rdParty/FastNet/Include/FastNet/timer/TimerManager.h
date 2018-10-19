#pragma once
#include "FastNet/timer/Timer.h"

namespace FastNet {

	class App;

	class FASTNET_API TimerManager :
        public Object {
	public:
        TimerManager(bool mainThread = true, PyObject* obj = nullptr);
		virtual ~TimerManager();

		boost::asio::io_service& GetIoService() { return m_ioService; }

		TimerPtr CreateTimer(const std::function<void(void)>& callback);
		TimerPtr CreateTimer_Python(PyObject* obj, const std::string& methodName);

		void Run();
		void Update();
		void Stop();

	private:

        bool m_stop = true;

		boost::asio::io_service m_ioService;
		std::shared_ptr<boost::asio::io_service::work> m_ioServiceWrok;
		std::shared_ptr<std::thread> m_thread;

		bool m_mainThread;
	};

    struct TMInfo {
		boost::shared_ptr<TimerManager> tm;

		//boost::lockfree::spsc_queue<Callback::Queue*, boost::lockfree::capacity<16384> > queueRecv;
        boost::lockfree::queue<Callback::Queue*, boost::lockfree::capacity<16384> > queueSend;

        //Poco::Thread threadRecv;
        TimerPtr timerSend;

        std::queue<BufferPtr> queueSendBuffer;
	};

}
