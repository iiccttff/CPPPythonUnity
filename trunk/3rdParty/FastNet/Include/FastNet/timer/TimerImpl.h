


class TimerImpl :public boost::enable_shared_from_this<TimerImpl> {
		friend class Timer;
	public:
		TimerImpl(const std::function<void()>& callback, boost::asio::io_service& ioService)
			: m_deadlineTimer(ioService)
			, m_interval(100)
		{
			m_stop = true;
			//m_exit = false;

			m_callback = callback;
		}

		TimerImpl(PyObject* obj, const std::string& methodName, boost::asio::io_service& ioService)
			: m_deadlineTimer(ioService)
			, m_interval(100)
		{
			//m_exit = false;
			m_stop = true;

			m_callback = [this, obj, methodName]() {

				try
				{
					boost::python::call_method<void>(obj, methodName.c_str());
				}
				PythonCallbackException
			};

		}

        ~TimerImpl() {

		}

		void OnCallbackTimer(const boost::system::error_code& ec) {

			if (m_stop) {
				return;
			}

			if (m_deadlineTimer.expires_at() <= boost::asio::deadline_timer::traits_type::now())
			{

				if (m_repeat > 0) {
					m_repeat--;
					m_deadlineTimer.async_wait(std::bind(&TimerImpl::OnCallbackTimer,shared_from_this(), std::placeholders::_1));
					m_deadlineTimer.expires_from_now(m_interval);
				}
				else if (m_repeat < 0) {
					m_deadlineTimer.async_wait(std::bind(&TimerImpl::OnCallbackTimer, shared_from_this(), std::placeholders::_1));
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
					LogException("TimerImpl::OnCallbackTimer %s", e.what());
				}
			}
			else
			{
				m_deadlineTimer.async_wait(std::bind(&TimerImpl::OnCallbackTimer, shared_from_this(), std::placeholders::_1));
			}
		}


		void Start(UInt32 interval, Int32 repeat) {

			if (m_stop) {
				m_stop = false;

				m_interval = boost::posix_time::milliseconds(interval);
				m_repeat = repeat;


				m_deadlineTimer.expires_from_now(m_interval);
				m_deadlineTimer.async_wait(std::bind(&TimerImpl::OnCallbackTimer, shared_from_this(), std::placeholders::_1));
			}
		}

		void Stop() {

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

		void Update(UInt32 interval, Int32 repeat) {

			if (!m_stop) {

				m_interval = boost::posix_time::milliseconds(interval);
				m_repeat = repeat;

				m_deadlineTimer.expires_from_now(m_interval);
			}
			else {
				Start(interval, repeat);
			}
		}


		friend class Timer;
		friend class TimerManager;
	private:

		std::function<void()> m_callback;
		boost::asio::deadline_timer m_deadlineTimer;
		bool m_stop;

		boost::posix_time::milliseconds m_interval;
		Int32 m_repeat = -1;
	};