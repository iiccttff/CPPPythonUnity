#include "Timer.h"
#include "FastNet/core/Log.h"

namespace FastNet {
	extern Poco::Thread::TID g_mainThreadId;
	extern boost::python::object g_callMethod;

	Timer::Timer(const std::function<void()>& callback, boost::asio::io_service& ioService)
		: m_deadlineTimer(ioService)
		, m_interval(100)
	{
		m_stop = true;
		m_callback = callback;
	}

	Timer::Timer(PyObject* obj, const std::string& methodName, boost::asio::io_service& ioService)
		: m_deadlineTimer(ioService)
		, m_interval(100)
	{
		m_stop = true;

		m_callback = [this, obj, methodName]() {

			try
			{
				
				g_callMethod(boost::python::borrowed(obj), methodName);
				//boost::python::call_method<void>(obj, methodName.c_str());
			}
			PythonCallbackException
		};

	}

	void Timer::OnTimer(const boost::system::error_code& ec) 
	{
		if (m_stop) {
			return;
		}

		if (m_deadlineTimer.expires_at() <= boost::asio::deadline_timer::traits_type::now())
		{

			if (m_repeat > 0) {
				m_repeat--;
				m_deadlineTimer.async_wait(std::bind(&Timer::OnTimer, shared_from_this(), std::placeholders::_1));
				m_deadlineTimer.expires_from_now(m_interval);
			}
			else if (m_repeat < 0) {
				m_deadlineTimer.async_wait(std::bind(&Timer::OnTimer, shared_from_this(), std::placeholders::_1));
				m_deadlineTimer.expires_from_now(m_interval);
			}
			else {
				m_stop = true;
				m_callback = nullptr;
				return;
			}

			try {

				if (m_callback) {
					m_callback();
				}
			}
			catch (std::exception& e) {
				LogException("Timer::OnCallbackTimer %s", e.what());
			}
		}
		else
		{
			m_deadlineTimer.async_wait(std::bind(&Timer::OnTimer, shared_from_this(), std::placeholders::_1));
		}
	}

	void Timer::Start(UInt32 interval,UInt32 preDelay, Int32 repeat) {

		if (m_stop) {
			m_stop = false;

			m_interval = boost::posix_time::milliseconds(interval);
			m_repeat = repeat;

			m_deadlineTimer.expires_from_now(boost::posix_time::milliseconds(preDelay));
			m_deadlineTimer.async_wait(std::bind(&Timer::OnTimer, shared_from_this(), std::placeholders::_1));
		}
	}

	void Timer::Start(UInt32 interval, Int32 repeat) {

		if (m_stop) {
			m_stop = false;

			m_interval = boost::posix_time::milliseconds(interval);
			m_repeat = repeat;

			m_deadlineTimer.expires_from_now(m_interval);
			m_deadlineTimer.async_wait(std::bind(&Timer::OnTimer, shared_from_this(), std::placeholders::_1));
		}
	}

	void Timer::Stop() {

		if (!m_stop) {

			m_stop = true;

			auto self = shared_from_this();
			m_deadlineTimer.get_io_service().dispatch([this, self]() {

				boost::system::error_code ignored_ec;
				m_deadlineTimer.expires_at(boost::posix_time::neg_infin);

				m_callback = nullptr;
			});
		}
	}

	void Timer::Update(UInt32 interval, Int32 repeat) {

		if (!m_stop) {

			m_interval = boost::posix_time::milliseconds(interval);
			m_repeat = repeat;

			m_deadlineTimer.expires_from_now(m_interval);
		}
		else {
			Start(interval, repeat);
		}
	}
}

