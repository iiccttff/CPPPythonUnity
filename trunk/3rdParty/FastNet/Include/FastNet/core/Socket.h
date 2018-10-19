#pragma once


#include "FastNet/core/Defs.h"

#include "boost/asio.hpp"
#include "boost/asio/ssl.hpp"

namespace FastNet {

	class FASTNET_API Socket {
	public:
		Socket(boost::asio::io_service& ioService);
		Socket(boost::asio::io_service& ioService, boost::asio::ssl::context& c);
		~Socket();

		boost::asio::ip::tcp::socket* GetSocket();
		boost::asio::ssl::stream<boost::asio::ip::tcp::socket>* GetSocketSSL();

		bool IsEnableSSL() const{ return m_enableSSL; }
	private:
		bool m_enableSSL;
		void* m_socket;
	};

}