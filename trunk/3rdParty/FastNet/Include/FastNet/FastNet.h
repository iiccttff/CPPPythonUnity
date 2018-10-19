#pragma once

#include "FastNet/core/Defs.h"
#include "FastNet/core/Log.h"

#include "FastNet/core/Message.h"
#include "FastNet/core/Stream.h"

#include "FastNet/timer/TimerManager.h"

#include "FastNet/core/Client.h"
#include "FastNet/core/Session.h"
#include "FastNet/core/Server.h"

#include "FastNet/core/App.h"


namespace FastNet {

	void FASTNET_API Execute(int argc, char **argv);

	String FASTNET_API GetWorkPath();

	String FASTNET_API GetDataPath();

	String FASTNET_API GetVersion();

	bool FASTNET_API IsDebugMode();
}