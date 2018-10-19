#pragma once

#include "FastNet/core/Message.h"
#include "FastNet/core/Object.h"
#include "FastNet/role/Role.h"


namespace FastNet {

	class FASTNET_API Room : public Object {
	public:
		Room(PyObject* obj);

		virtual ~Room() = default;

		UInt32 Id() const;

		void Start();
		void Stop();

		virtual void OnCreate() {}
		virtual void OnDestory() {}

		bool IsStoped() { return m_stoped; }
		bool IsAllReady();

		virtual void OnJoin(const RolePtr& role) {}
		virtual void OnReady(const RolePtr& role) {}
		virtual void OnLeave(const RolePtr& role) {}
		virtual void OnMessage(MessagePtr message, const RolePtr& role) {}

		virtual void OnStart() {}
		virtual void OnStop() {}
	private:
		friend class Role;
		friend class RoomManager;

		void Join(const RolePtr& role);
		void Ready(const String& roleId);
		void Leave(const String& roleId);
		void SendMsg(MessagePtr, const String& sender);

		void RecvMsg(MessagePtr, const String& roleId);
	private:
		UInt32 m_id;
		bool m_stoped;

		std::unordered_map<String,std::pair<RolePtr,bool> > m_members;
	};

	typedef boost::shared_ptr<Room> RoomPtr;
}