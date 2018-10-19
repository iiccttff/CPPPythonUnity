#pragma once

#include <string>
#include <vector>

#include "Poco/Types.h"
#include "boost/smart_ptr/shared_ptr.hpp"

namespace FastNet {

/*
#if defined(_MSC_VER)
	//
	// Windows/Visual C++
	//
	typedef signed char            Int8;
	typedef unsigned char          UInt8;
	typedef signed short           Int16;
	typedef unsigned short         UInt16;
	typedef signed int             Int32;
	typedef unsigned int           UInt32;
	typedef signed __int64         Int64;
	typedef unsigned __int64       UInt64;

#elif defined(__GNUC__) || defined(__clang__)
	//
	// Unix/GCC/Clang
	//
	typedef signed char            Int8;
	typedef unsigned char          UInt8;
	typedef signed short           Int16;
	typedef unsigned short         UInt16;
	typedef signed int             Int32;
	typedef unsigned int           UInt32;

#if defined(__LP64__)
	typedef signed long        Int64;
	typedef unsigned long      UInt64;
#else
	typedef signed long long   Int64;
	typedef unsigned long long UInt64;
#endif

#endif

*/

	typedef int8_t				Int8;
	typedef uint8_t				UInt8;
	typedef int16_t				Int16;
	typedef uint16_t			UInt16;
	typedef int32_t             Int32;
	typedef uint32_t			UInt32;
	typedef int64_t				Int64;
	typedef uint64_t			UInt64;

	typedef std::string String;
	typedef double Double;
	typedef float Float;
	typedef bool Bool;

	typedef std::vector<UInt8> Buffer;
	typedef boost::shared_ptr<Buffer> BufferPtr;


	const static auto s_sizeUInt8(sizeof(UInt8));
	const static auto s_sizeUInt16(sizeof(UInt16));
	const static auto s_sizeUInt32(sizeof(UInt32));
	const static auto s_sizeUInt64(sizeof(UInt64));
	const static auto s_sizeInt8(sizeof(Int8));
	const static auto s_sizeInt16(sizeof(Int16));
	const static auto s_sizeInt32(sizeof(Int32));
	const static auto s_sizeInt64(sizeof(Int64));

	const static auto s_sizeBool(sizeof(Bool));
	const static auto s_sizeFloat(sizeof(Float));
	const static auto s_sizeDouble(sizeof(Double));

	const static std::type_info& s_tpyeUInt8(typeid(UInt8));
	const static std::type_info& s_tpyeInt8(typeid(Int8));
	const static std::type_info& s_tpyeUInt16(typeid(UInt8));
	const static std::type_info& s_tpyeInt16(typeid(Int8));
	const static std::type_info& s_tpyeUInt32(typeid(UInt8));
	const static std::type_info& s_tpyeInt32(typeid(Int8));
	const static std::type_info& s_tpyeUInt64(typeid(UInt8));
	const static std::type_info& s_tpyeInt64(typeid(Int8));

	const static std::type_info& s_tpyeBool(typeid(Bool));
	const static std::type_info& s_tpyeFloat(typeid(Float));
	const static std::type_info& s_tpyeDouble(typeid(Double));
	const static std::type_info& s_tpyeString(typeid(String));

} // namespace FastNet