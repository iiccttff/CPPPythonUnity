#pragma once

#include "bsoncxx/builder/basic/document.hpp"
#include "bsoncxx/builder/basic/kvp.hpp"

#include "bsoncxx/builder/stream/array.hpp"
#include "bsoncxx/builder/stream/document.hpp"
#include "bsoncxx/builder/stream/helpers.hpp"
#include "bsoncxx/types.hpp"

#include "bsoncxx/stdx/make_unique.hpp"
#include "bsoncxx/stdx/optional.hpp"
#include "bsoncxx/stdx/string_view.hpp"
#include "bsoncxx/json.hpp"
#include "mongocxx/instance.hpp"
#include "mongocxx/logger.hpp"
#include "mongocxx/pool.hpp"
#include "mongocxx/uri.hpp"
#include "mongocxx/client.hpp"
#include "mongocxx/database.hpp"

#include "boost/python.hpp"
#include "boost/smart_ptr/shared_ptr.hpp"
#include "boost/smart_ptr/make_shared.hpp"
#include "boost/smart_ptr/enable_shared_from_this.hpp"
#include "boost/interprocess/file_mapping.hpp"
#include "boost/interprocess/mapped_region.hpp"

#include <string>
#include <map>
#include <set>
#include <vector>
#include <queue>
#include <deque>
#include <tuple>
#include <list>
#include <algorithm>
#include <functional>
#include <memory>
#include <thread>
#include <mutex>
#include <atomic>
#include <fstream>
#include <unordered_map>
#include <unordered_set>

#include "Poco/Bugcheck.h"
#include "Poco/Format.h"
#include "Poco/File.h"
#include "Poco/Path.h"
#include "Poco/StreamCopier.h"
#include "Poco/Hash.h"
#include "Poco/Thread.h"
#include "Poco/FIFOBufferStream.h"
#include "Poco/Base64Decoder.h"
#include "Poco/Base64Encoder.h"
#include "Poco/RWLock.h"

#include "Poco/Net/HTTPServer.h"
#include "Poco/Net/HTTPServerParams.h"
#include "Poco/Net/AbstractHTTPRequestHandler.h"
#include "Poco/Net/HTTPRequestHandlerFactory.h"
#include "Poco/Net/HTTPClientSession.h"
#include "Poco/Net/HTTPRequest.h"
#include "Poco/Net/HTTPServerRequest.h"
#include "Poco/Net/HTTPResponse.h"
#include "Poco/Net/HTTPServerResponse.h"


#include "FastNet/core/Types.h"

#if defined(_WIN32)


#if defined(FASTNET_EXPORTS)
#define FASTNET_API __declspec(dllexport)
#else
#define FASTNET_API __declspec(dllimport)
#endif

#endif

#if !defined(FASTNET_API)

#if defined (__GNUC__) && (__GNUC__ >= 4)
#define FASTNET_API __attribute__ ((visibility ("default")))
#else
#define FASTNET_API
#endif

#endif


#define FastNet_MaxMessageLength 65535



namespace FastNet {

//#pragma pack(push)
//#pragma pack(1)

	struct MessageHead {
		UInt32 size = 0;
		UInt32 id = 0;
		UInt32 signatureId = 0;
	};

//#pragma pack(pop)

#define FastNet_MessageHeadSize sizeof(MessageHead)



	enum SocketEvent
	{
		kConnectSucceed,
		kConnectFailure,
		kConnectClosed,
		kReConnecting,
		kReConnectFailure,
		kErrorMessage,
	};


	struct SystemMemoryInfo {
		std::atomic<UInt64> total;
		std::atomic<UInt64> available;
		std::atomic<UInt32> percent;
		std::atomic<UInt64> used;
		std::atomic<UInt64> free;
	};


#define BoostLink_VS2015_Update3(cls)	\
	namespace boost	\
	{	\
		template <>	\
		static cls const volatile * get_pointer<class cls const volatile >(	\
			class cls const volatile *c)	\
		{	\
			return c;	\
		}	\
	}

	extern void PrintPythonError();

#define PythonCallbackException		\
	catch (boost::python::error_already_set) {	\
		if (PyErr_Occurred()) {	\
			PrintPythonError();	\
		}	\
		PyErr_Clear();	\
	}


	class NoopLogger : public mongocxx::logger {
	public:
		virtual void operator()(mongocxx::log_level,
			bsoncxx::stdx::string_view,
			bsoncxx::stdx::string_view) noexcept {}
	};


}

