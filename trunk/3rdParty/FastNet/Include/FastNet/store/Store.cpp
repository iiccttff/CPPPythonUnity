

#include "StoreManager.h"

#include "Poco/MemoryStream.h"

#include "FastNet/core/ClassFactory.h"

#include "FastNet/core/Message.h"
#include "FastNet/core/Stream.h"
#include "FastNet/core/App.h"
namespace FastNet {

	StoreRead::StoreRead(bsoncxx::stdx::optional<bsoncxx::document::value>& doc):m_doc(doc){

	}

	String StoreRead::ReadString(const String& name, const String& defaultVal) {

		if (m_doc) {
			auto itDoc = m_doc->view().find(name);
			if (itDoc == m_doc->view().end()) {
				return defaultVal;
			}

			return itDoc->get_utf8().value.data();
		}
		else {
			return defaultVal;
		}
	}

	UInt32 StoreRead::ReadUInt32(const String& name, UInt32 defaultVal) {

		if (m_doc) {
			auto itDoc = m_doc->view().find(name);
			if (itDoc == m_doc->view().end()) {
				return defaultVal;
			}

			return (UInt32)itDoc->get_int32().value;
		}
		else {
			return defaultVal;
		}
	}

	UInt64 StoreRead::ReadUInt64(const String& name, UInt64 defaultVal) {

		if (m_doc) {
			auto itDoc = m_doc->view().find(name);
			if (itDoc == m_doc->view().end()) {
				return defaultVal;
			}

			return (UInt64)itDoc->get_int64().value;
		}
		else {
			return defaultVal;
		}
	}

	Int32 StoreRead::ReadInt32(const String& name, Int32 defaultVal) {

		if (m_doc) {
			auto itDoc = m_doc->view().find(name);
			if (itDoc == m_doc->view().end()) {
				return defaultVal;
			}

			return itDoc->get_int32().value;
		}
		else {
			return defaultVal;
		}
	}

	Int64 StoreRead::ReadInt64(const String& name, Int64 defaultVal) {

		if (m_doc) {
			auto itDoc = m_doc->view().find(name);
			if (itDoc == m_doc->view().end()) {
				return defaultVal;
			}

			return itDoc->get_int64().value;
		}
		else {
			return defaultVal;
		}
	}

	Double StoreRead::ReadDouble(const String& name, Double defaultVal) {

		if (m_doc) {
			auto itDoc = m_doc->view().find(name);
			if (itDoc == m_doc->view().end()) {
				return defaultVal;
			}

			return itDoc->get_double().value;
		}
		else {
			return defaultVal;
		}
	}

	Bool StoreRead::ReadBool(const String& name, Bool defaultVal) {

		if (m_doc) {
			auto itDoc = m_doc->view().find(name);
			if (itDoc == m_doc->view().end()) {
				return defaultVal;
			}

			return itDoc->get_bool().value;
		}
		else {
			return defaultVal;
		}
	}

	/*MessagePtr StoreRead::ReadMessage(const String& name, MessagePtr defaultVal) {

		if (m_doc) {
			auto itDoc = m_doc->view().find(name);
			if (itDoc == m_doc->view().end()) {
				return defaultVal;
			}

			bsoncxx::document::view messageDoc = itDoc->get_document().value;
			auto itClsId = messageDoc.find("ClsId");
			if (itClsId != messageDoc.end()) {
				UInt32 clsId = (UInt32)itClsId->get_int32().value;
				MessagePtr message = ClassFactory::Instance()->Create(clsId);
				BsonRead br(messageDoc);
				message->DeserializeFromBson(br);
				return message;
			}else {
				return defaultVal;
			}
		}
		else {
			return defaultVal;
		}
	}*/

	boost::python::object StoreRead::ReadList(const String& name, boost::python::object defaultVal) {
		if (m_doc) {
			auto itDoc = m_doc->view().find(name);
			if (itDoc == m_doc->view().end()) {
				return defaultVal;
			}

			return App::Instance().LoadJson(itDoc->get_utf8().value.to_string());
		}
		else {
			return defaultVal;
		}
	}

	boost::python::object StoreRead::ReadDict(const String& name, boost::python::object defaultVal) {
		return ReadList(name, defaultVal);
	}

	using bsoncxx::builder::stream::open_document;
	using bsoncxx::builder::stream::close_document;
	using bsoncxx::builder::basic::kvp;

	StoreWrite::StoreWrite(bsoncxx::builder::stream::document& doc) :m_doc(doc) {

	}


	void StoreWrite::WriteString(const String& name, const String& value) {
		m_doc << name << bsoncxx::types::b_utf8{ value };
	}

	void StoreWrite::WriteUInt32(const String& name, UInt32 value) {
		m_doc << name << bsoncxx::types::b_int32{ (Int32)value };
	}

	void StoreWrite::WriteUInt64(const String& name, UInt64 value){
		m_doc << name << bsoncxx::types::b_int64{ (Int64)value };
	}

	void StoreWrite::WriteInt32(const String& name, Int32 value) {
		m_doc << name << bsoncxx::types::b_int32{ value };
	}

	void StoreWrite::WriteInt64(const String& name, Int64 value) {
		m_doc << name << bsoncxx::types::b_int64{ value };
	}

	void StoreWrite::WriteDouble(const String& name, Double value) {
		m_doc << name << bsoncxx::types::b_double{ value };
	}

	void StoreWrite::WriteBool(const String& name, Bool value) {
		m_doc << name << bsoncxx::types::b_bool{ value };
	}

	/*void StoreWrite::WriteMessage(const String& name, MessagePtr value) {
		BsonWrite bw(m_doc);

		m_doc << name << open_document;
		value->SerializeToBson(bw);
		m_doc << close_document;
	}*/

	void StoreWrite::WriteList(const String& name, boost::python::object value) {
		String s = boost::python::extract<String>(App::Instance().DumpJson(value));
		m_doc << name << bsoncxx::types::b_utf8{ s };
	}

	void StoreWrite::WriteDict(const String& name, boost::python::object value) {
		WriteList(name, value);
	}

	Store::Store(PyObject* obj, const String& collName, const String& id)
		: Object(obj), m_collName(collName), m_id(id)
	{
		m_expireTime = std::time(nullptr) + 3600 + std::rand() % 3200;
	}

	Store::~Store() {
		
	}

	void Store::Save() {
		m_expireTime = 0;
	}

	void Store::SetExpireTime(UInt32 t) {
		m_expireTime = t;
	}

	UInt32 Store::GetExpireTime() {
		return m_expireTime;
	}

	const String Store::CollName() {
		return m_collName;
	}

	const String Store::Id() {
		return m_id;
	}

	bsoncxx::stdx::optional<bsoncxx::document::value> Store::GetColl() {
		using bsoncxx::builder::basic::kvp;
		using bsoncxx::builder::basic::make_document;

		auto db = StoreManager::Instance()->GetDatabase();
		return db[m_collName].find_one(make_document(kvp("id", m_id)));
	}

	/*
	void Store::Cache(bsoncxx::document::value& doc) {
		try {
			bsoncxx::stdx::optional<bsoncxx::document::value> docValue(doc);
			StoreRead sr(docValue);
			this->OnCache(sr);
			boost::python::call_method<void>(m_obj, "OnCache", sr);
		}
		PythonCallbackException
	}

	void Store::Flush(bsoncxx::builder::stream::document& doc) {
		try {
			StoreWrite sw(doc);
			this->OnFlush(sw);
			boost::python::call_method<void>(m_obj, "OnFlush", sw);
		}
		PythonCallbackException
	}*/
}