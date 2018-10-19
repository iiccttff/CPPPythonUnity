#include "RoomManager.h"
#include "FastNet/core/Log.h"
#include "FastNet/core/App.h"

namespace FastNet {

	RoomManager::RoomManager():m_msgs(16384) {

	}

	RoomManager::~RoomManager() {

	}

	void RoomManager::RegisterRoom(const String& name, boost::python::object cls) {
		if (!m_roomCls.emplace(name, cls).second) {
			LogError("RoomManager::RegisterRoom %s already exist!",name.c_str());
		}
	}


	std::vector<RoomPtr> RoomManager::GetRooms() {
		std::vector<RoomPtr> l;
		for (auto v : m_rooms) {
			l.emplace_back(v.second);
		}
		return l;
	}

	boost::python::list RoomManager::GetRooms_Python() {
		boost::python::list l;
		for (auto v : m_rooms) {
			l.append(v.second);
		}
		return l;
	}

	RoomPtr RoomManager::GetRoom(UInt32 id) {
		auto itRoom = m_rooms.find(id);
		if (m_rooms.end() == itRoom) {
			return nullptr;
		}
		else {
			return itRoom->second;
		}
	}

	RoomPtr RoomManager::CreateRoom(const String& name) {
		auto itRoomCls = m_roomCls.find(name);
		if (m_roomCls.end() != itRoomCls) {
			boost::python::object room = itRoomCls->second(name);
			RoomPtr roomPtr = boost::python::extract<RoomPtr>(room.ptr());
			m_rooms.emplace(roomPtr->Id(),roomPtr);

			roomPtr->OnCreate();

			return roomPtr;
		}else {
			return nullptr;
		}
	}

	void RoomManager::DeleteRoom(UInt32 id) {
		auto itRoom = m_rooms.find(id);
		if (m_rooms.end() != itRoom) {
			itRoom->second->OnDestory();
			m_rooms.erase(itRoom);
		}
	}

	void RoomManager::OnRoomMessage(UInt32 roomId, const String& roleId, const MessagePtr& message) {
		auto msg = new RoomMsg();
		msg->message = message;
		msg->roleId = roleId;
		msg->roomId = roomId;
		m_msgs.push(msg);
	}

	void RoomManager::OnCreate() {
		m_timerRoomMessage = App::Instance().CreateTimer([this]() {
			RoomMsg* qr;
			while (m_msgs.pop(qr)) {
				auto room = GetRoom(qr->roomId);
				if (room) {
					room->RecvMsg(qr->message,qr->roleId);
				}
				else {
					LogError("RoomManager::OnRoomMessage no find roomId:%d", qr->roomId);
				}

				delete qr;

			}
		});

		m_timerRoomMessage->Start(30);
	}

	void RoomManager::OnDestory() {

		m_timerRoomMessage->Stop();
		m_timerRoomMessage = nullptr;
	}
}