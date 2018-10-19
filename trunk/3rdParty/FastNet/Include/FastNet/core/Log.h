#pragma once

#include "FastNet/core/Defs.h"

namespace FastNet {

	extern void FASTNET_API LogNormal(const char* fmt,...);
	extern void FASTNET_API LogDebug(const char* fmt,...);
	extern void FASTNET_API LogWarning(const char* fmt,...);
	extern void FASTNET_API LogError(const char* fmt,...);
	extern void FASTNET_API LogException(const char* fmt, ...);
	extern void FASTNET_API LogEvent(const String& key, const char* fmt, ...);

	extern void FASTNET_API LogNormal(const std::string& log);
	extern void FASTNET_API LogDebug(const std::string& log);
	extern void FASTNET_API LogWarning(const std::string& log);
	extern void FASTNET_API LogError(const std::string& log);
	extern void FASTNET_API LogException(const std::string& log);
	extern void FASTNET_API LogEvent(const String& key, const std::string& log);
}
