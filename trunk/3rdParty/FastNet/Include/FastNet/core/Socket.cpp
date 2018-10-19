#include "Socket.h"


namespace FastNet {

	Socket::Socket(boost::asio::io_service& ioService) {
		m_enableSSL = false;
		m_socket = (void*)new boost::asio::ip::tcp::socket(ioService);
	}

	Socket::Socket(boost::asio::io_service& ioService, boost::asio::ssl::context& c) {
		m_enableSSL = true;
		m_socket = (void*)new boost::asio::ssl::stream<boost::asio::ip::tcp::socket>(ioService,c);
	}

	Socket::~Socket() {
		if (m_enableSSL) {
			delete this->GetSocketSSL();
		}else{
			delete this->GetSocket();
		}
		m_socket = nullptr;
	}

	boost::asio::ip::tcp::socket* Socket::GetSocket() {
		return (boost::asio::ip::tcp::socket*)m_socket;
	}

	boost::asio::ssl::stream<boost::asio::ip::tcp::socket>* Socket::GetSocketSSL() {
		return (boost::asio::ssl::stream<boost::asio::ip::tcp::socket>*)m_socket;
	}

}