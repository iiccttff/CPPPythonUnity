#pragma once


#include "FastNet/core/Object.h"
#include "FastNet/store/Store.h"

namespace FastNet {

	class RoleModule;
	class Session;

	class FASTNET_API Role :public Store {
	public:

		enum class Status {
			Online = 1,
			Offline,
			WaitReconnect
		};

		Role(PyObject* obj, const String& id);
		virtual ~Role();

		virtual void OnLogin() {}
		virtual void OnLogout() {}

		virtual void OnDisconnect() {}
		virtual void OnReconnect() {}

		void Frozen(UInt32 time);
		bool IsFrozen() const ;
		UInt32 FrozenTime() const;

		const String UserId() const;
		const String ChannelId() const;
		UInt32 Level() const;
		void SetLevel(UInt32 level);

		UInt32 CreateTime() const ;

		Status GetStatus() const ;

		Session* GetSession();
		boost::python::object GetSession_Python();

		UInt32 LastLoginTime()const;
		UInt32 LastLogoutTime()const;


		boost::shared_ptr<RoleModule> Module(const String& name);
		const std::map<String, boost::shared_ptr<RoleModule> >& Modules();
		std::map<String, boost::shared_ptr<RoleModule> > Modules_Python();

		void JoinRoom(UInt32 id);
		void ReadyRoom(UInt32 id);
		void LeaveRoom(UInt32 id);
		void SendRoomMsg(UInt32 id, const MessagePtr& message);



	private:
		friend class RoleManager;

		void SetUserId(const String& uid);
		void SetChannelId(const String& channelId);

		virtual void Cache() final;
		virtual  std::shared_ptr<StoreInfo> Flush() final;
		
		void Login(Object* session);
		void Reconnect(Object* session);
		void Logout();
		void Disconnect();

		bool AddModule(const String& name,boost::shared_ptr<RoleModule> module);

		void Destory(bool del = false);

	private:
		std::map<String, boost::shared_ptr<RoleModule> > m_modules;

		std::atomic<Status> m_status;
		String m_uid;
		String m_channelId;
		UInt32 m_frozenTime = 0;
		UInt32 m_createTime = 0;
		UInt32 m_lastLoginTime = 0;
		UInt32 m_lastLogoutTime = 0;

		UInt32 m_level = 0;

		ObjectRef m_session;

		std::set<UInt32> m_roomIds;


	};

	typedef boost::shared_ptr<Role> RolePtr;

}