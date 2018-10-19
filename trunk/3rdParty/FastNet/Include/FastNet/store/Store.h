#pragma once

#include "FastNet/core/Message.h"
#include "FastNet/core/Object.h"

namespace FastNet {

	class FASTNET_API StoreRead {
	public:
		StoreRead(bsoncxx::stdx::optional<bsoncxx::document::value>& doc);
		String ReadString(const String&, const String& defaultVal);
		UInt32 ReadUInt32(const String&, UInt32 defaultVal);
		UInt64 ReadUInt64(const String&, UInt64 defaultVal);
		Int32 ReadInt32(const String&, Int32 defaultVal);
		Int64 ReadInt64(const String&, Int64 defaultVal);
		Double ReadDouble(const String&, Double defaultVal);
		Bool ReadBool(const String&, Bool defaultVal);
		boost::python::object ReadList(const String&, boost::python::object defaultVal);
		boost::python::object ReadDict(const String&, boost::python::object defaultVal);
	private:
		bsoncxx::stdx::optional<bsoncxx::document::value>& m_doc;
	};

	typedef boost::shared_ptr<StoreRead> StoreReadPtr;

	class FASTNET_API StoreWrite {
	public:
		StoreWrite(bsoncxx::builder::stream::document& doc);

		void WriteString(const String&, const String&);
		void WriteUInt32(const String&, UInt32);
		void WriteUInt64(const String&, UInt64);
		void WriteInt32(const String&, Int32);
		void WriteInt64(const String&, Int64);
		void WriteDouble(const String&, Double);
		void WriteBool(const String&, Bool);
		void WriteList(const String&, boost::python::object);
		void WriteDict(const String&, boost::python::object);
	private:
		bsoncxx::builder::stream::document& m_doc;
	};

	typedef boost::shared_ptr<StoreWrite> StoreWritePtr;

	class FASTNET_API Store : public Object {
	public:
		Store(PyObject* obj, const String& collName,const String& keyName);
		virtual ~Store();

		void Save();

		struct StoreInfo {
			bsoncxx::builder::stream::document doc;
			String name;
			String id;
			bool del = false;
		};

		const String CollName();
		const String Id();

		bsoncxx::stdx::optional<bsoncxx::document::value> GetColl();

	protected:

		friend class StoreManager;

		virtual void Cache() {}
		virtual std::shared_ptr<StoreInfo> Flush() { return nullptr; }
		virtual void Delete() {}

		void SetExpireTime(UInt32 t);
		UInt32 GetExpireTime();

		virtual void OnCache(StoreReadPtr& sr) {}
		virtual void OnFlush(StoreWritePtr& sw) {}
		virtual void OnReloadCfg() {}
		virtual void OnDelete() {}

	protected:
		UInt32 m_expireTime = 0;
		const String m_collName;
		const String m_id;
	};

	typedef boost::shared_ptr<Store> StorePtr;
}