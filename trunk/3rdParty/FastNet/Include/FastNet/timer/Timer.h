#pragma once
#include "FastNet/core/Callback.h"
#include "FastNet/core/Message.h"
#include "boost/lockfree/queue.hpp"
#include "boost/lockfree/spsc_queue.hpp"
#include "boost/asio.hpp"

namespace FastNet {

	class FASTNET_API Timer : public boost::enable_shared_from_this<Timer>{
		friend class TimerManager;

	public:
		Timer(const std::function<void()>& callback, boost::asio::io_service& ioService);
		Timer(PyObject* obj, const std::string& methodName, boost::asio::io_service& ioService);

		~Timer() = default;

		Timer(const Timer&) = delete;
		Timer& operator= (const Timer&) = delete;

		void Start(UInt32 interval, Int32 repeat = -1);
		void Start(UInt32 interval, UInt32 preDelay, Int32 repeat);
		void Stop();
		void Update(UInt32 interval, Int32 repeat = -1);

	private:
		void OnTimer(const boost::system::error_code& ec);
		
		std::function<void()> m_callback;
		boost::asio::deadline_timer m_deadlineTimer;
		bool m_stop;

		boost::posix_time::milliseconds m_interval;
		Int32 m_repeat = -1;
	};

	typedef boost::shared_ptr<Timer> TimerPtr;

}
