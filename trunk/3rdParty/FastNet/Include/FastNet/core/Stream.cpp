#include "Stream.h"
#include "FastNet/core/Message.h"

namespace FastNet {
	/*
	using bsoncxx::builder::basic::kvp;

	void BsonRead::read(const char* name, Int8& value) {
		value = (Int8)m_doc[name].get_int32().value;
	}

	void BsonRead::read(const char* name, Int16& value) {
		value = (Int16)m_doc[name].get_int32().value;
	}

	void BsonRead::read(const char* name, Int32& value) {
		value = (Int32)m_doc[name].get_int32().value;
	}

	void BsonRead::read(const char* name, Int64& value) {
		value = (Int64)m_doc[name].get_int64().value;
	}

	void BsonRead::read(const char* name, UInt8& value) {
		value = (UInt8)m_doc[name].get_int32().value;
	}

	void BsonRead::read(const char* name, UInt16& value) {
		value = (UInt16)m_doc[name].get_int32().value;
	}

	void BsonRead::read(const char* name, UInt32& value) {
		value = (UInt32)m_doc[name].get_int32().value;
	}

	void BsonRead::read(const char* name, UInt64& value) {
		value = (UInt64)m_doc[name].get_int64().value;
	}

	void BsonRead::read(const char* name, Double& value) {
		value = (Double)m_doc[name].get_double().value;
	}

	void BsonRead::read(const char* name, Float& value) {
		value = (Float)m_doc[name].get_double().value;
	}

	void BsonRead::read(const char* name, Bool& value) {
		value = m_doc[name].get_bool().value;
	}

	void BsonRead::read(const char* name, String& value) {
		value = m_doc[name].get_utf8().value.to_string();
	}


	using bsoncxx::builder::stream::open_document;
	using bsoncxx::builder::stream::close_document;

	BsonWrite::BsonWrite(bsoncxx::builder::stream::document& doc)
		:m_doc(doc)
	{

	}

	void BsonWrite::write(const String& name, Int8 value) {
		m_doc << name << bsoncxx::types::b_int32{ (Int32)value };
	}

	void BsonWrite::write(const String& name, Int16 value) {
		m_doc << name << bsoncxx::types::b_int32{ (Int32)value };
	}

	void BsonWrite::write(const String& name, Int32 value) {
		m_doc << name << bsoncxx::types::b_int32{ (Int32)value };
	}

	void BsonWrite::write(const String& name, Int64 value) {
		m_doc << name << bsoncxx::types::b_int64{ (Int64)value };
	}

	void BsonWrite::write(const String& name, UInt8 value) {
		m_doc << name << bsoncxx::types::b_int32{ (Int32)value };
	}

	void BsonWrite::write(const String& name, UInt16 value) {
		m_doc << name << bsoncxx::types::b_int32{ (Int32)value };
	}

	void BsonWrite::write(const String& name, UInt32 value) {
		m_doc << name << bsoncxx::types::b_int32{ (Int32)value };
	}

	void BsonWrite::write(const String& name, UInt64 value) {
		m_doc << name << bsoncxx::types::b_int64{ (Int64)value };
	}

	void BsonWrite::write(const String& name, Double value) {
		m_doc << name << bsoncxx::types::b_double{ value };
	}

	void BsonWrite::write(const String& name, Float value) {
		m_doc << name << bsoncxx::types::b_double{ value };
	}

	void BsonWrite::write(const String& name, Bool value) {
		m_doc << name << bsoncxx::types::b_bool{ value };
	}

	void BsonWrite::write(const String& name,const String& value) {
		m_doc << name << bsoncxx::types::b_utf8{ value };
	}

	*/

}