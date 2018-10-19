#pragma once

#include "FastNet/room/Room.h"
#include "FastNet/core/Singleton.h"
#include "boost/lockfree/queue.hpp"
#include "FastNet/timer/Timer.h"

namespace FastNet {

	class FASTNET_API RoomManager final: public Singleton<RoomManager>{
	public:

		RoomManager();

		virtual ~RoomManager();

		void RegisterRoom(const String& name,boost::python::object cls);

		std::vector<RoomPtr> GetRooms();
		boost::python::list GetRooms_Python();

		RoomPtr GetRoom(UInt32 id);
		RoomPtr CreateRoom(const String& name);
		void DeleteRoom(UInt32 id);

		void OnCreate();
		void OnDestory();

	private:
		friend class Session;
		void OnRoomMessage(UInt32 roomId,const String& roleId,const MessagePtr& message);
	private:
		std::unordered_map<String, boost::python::object> m_roomCls;
		std::map<UInt32,RoomPtr> m_rooms;

		struct RoomMsg {
			UInt32 roomId;
			String roleId;
			MessagePtr message;
		};

		boost::lockfree::queue<RoomMsg*> m_msgs;
		TimerPtr m_timerRoomMessage;
	};

}
