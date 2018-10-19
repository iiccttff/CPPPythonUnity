#include "Room.h"
#include "Poco/UUIDGenerator.h"

#include "FastNet/core/Log.h"
#include "FastNet/pkt/protocols.h"
#include "Poco/MemoryStream.h"
#include "FastNet/core/Session.h"
#include "FastNet/role/RoleManager.h"

namespace FastNet {
	extern boost::python::object g_callMethod;

	Room::Room(PyObject* obj) :Object(obj){
		m_id = Poco::hash(Poco::UUIDGenerator::defaultGenerator().createOne().toString());
	}

	UInt32 Room::Id() const {
		return m_id;
	}

	void Room::Start() {
		if (m_stoped == true) {
			m_stoped = false;

			try {
				OnStart();

				g_callMethod(boost::python::borrowed(m_obj), "OnStart");
				//boost::python::call_method<void>(m_obj, "OnStart");
			}
			PythonCallbackException
		}
		else {
			LogError("Room::Start m_stoped == false");
		}
	}

	void Room::Stop() {
		if (m_stoped == false) {
			m_stoped = true;

			try {
				OnStop();
				boost::python::call_method<void>(m_obj, "OnStop");
			}
			PythonCallbackException
		}
		else {
			LogError("Room::Stop m_stoped == true");
		}
	}

	bool Room::IsAllReady() {
		for (auto& v : m_members) {
			if (!v.second.second) {
				return false;
			}
		}
		return true;
	}

	void Room::Join(const RolePtr& role) {

		auto ret = m_members.emplace(role->Id(), std::make_pair(role,false));
		if (!ret.second) {
			LogError("Room::Join roomId:%d,roleId:%s repeat join!", m_id, role->Id().c_str());
		}
		else {

			try {
				OnJoin(role);
				boost::python::call_method<void>(m_obj, "OnJoin", role);
			}
			PythonCallbackException
		}
		
	}

	void Room::Ready(const String& roleId) {
		auto itMember = m_members.find(roleId);
		if (m_members.end() == itMember) {
			LogError("Room::Ready roomId:%d,roleId:%s no find", m_id, roleId.c_str());
		}
		else {
			if (itMember->second.second) {
				LogError("Room::Ready roomId:%d,roleId:%s repeat ready!", m_id, roleId.c_str());
			}
			else {
				itMember->second.second = true;

				try {
					OnReady(itMember->second.first);
					boost::python::call_method<void>(m_obj, "OnReady", itMember->second.first);
				}
				PythonCallbackException
			}
		}
	}

	void Room::Leave(const String& roleId) {
		auto itMember = m_members.find(roleId);
		if (m_members.end() == itMember) {
			LogError("Room::Leave roomId:%d,roleId:%s no find", m_id, roleId.c_str());
		}
		else {

			try {
				OnLeave(itMember->second.first);
				boost::python::call_method<void>(m_obj, "OnLeave", itMember->second.first);
				m_members.erase(itMember);
			}
			PythonCallbackException
		}
	}

	void Room::SendMsg(MessagePtr message, const String& sender) {
		auto rmr = Message::Create<pkt::protocols::RoomMessageRes>();
		rmr->data.resize(message->SerializeSize());
		rmr->clsId = message->ClsId();
		rmr->signId = message->SignId();
		rmr->roleId = sender;
		rmr->roomId = m_id;

		if (!rmr->data.empty()) {
			try {
				Poco::MemoryOutputStream mos((char*)rmr->data.c_str(), rmr->data.size());
				FastNet::StreamWrite stream(mos);
				message->Serialize(stream);
			}
			catch (std::exception& e) {
				LogException("Room::SendMsg %s", e.what());
			}
		}

		for (auto& v : m_members) {

			if (v.second.first->GetStatus() == Role::Status::Online) {
				auto session = v.second.first->GetSession();
				if (session) {
					session->SendMsg(rmr);
				}
				else {
					LogError("Room::SendMsg message:%s,roleId:%s session == nullptr", message->ClsName(), v.first.c_str());
				}
			}
		}
	}

	void Room::RecvMsg(MessagePtr message, const String& roleId) {
		auto itMember = m_members.find(roleId);
		if (m_members.end() == itMember) {
			LogError("Room::RecvMsg roomId:%d,roleId:%s no find", m_id, roleId.c_str());
		}
		else {

			try {
				OnMessage(message,itMember->second.first);
				boost::python::call_method<void>(m_obj, "OnMessage", message, itMember->second.first);
			}
			PythonCallbackException
		}
	}
}