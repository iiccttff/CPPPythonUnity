#pragma once



#include "FastNet/core/Log.h"
#include "FastNet/core/Message.h"

namespace FastNet {

	class Struct;

	/*
	class FASTNET_API BsonRead {
	public:
		BsonRead(const bsoncxx::document::view& doc)
			:m_doc(doc)
		{

		}

		~BsonRead() = default;

		void read(const char* name, Int8& value);
		void read(const char* name, Int16& value);
		void read(const char* name, Int32& value);
		void read(const char* name, Int64& value);
		void read(const char* name, UInt8& value);
		void read(const char* name, UInt16& value);
		void read(const char* name, UInt32& value);
		void read(const char* name, UInt64& value);
		void read(const char* name, Double& value);
		void read(const char* name, Float& value);
		void read(const char* name, Bool& value);
		void read(const char* name, String& value);
		void read(const char* name, Struct& value);


		template <typename T>
		void read(const char* name, std::vector<T>& value) {
			bsoncxx::document::element element = m_doc[name];
			bsoncxx::array::view subarray{ element.get_array().value };

			value.resize(subarray.length());

			int i = 0;
			for (const bsoncxx::array::element& v : subarray) {
				BsonRead br(v.get_document().value);
				br.read("v", value.at(i));
				i++;
			}
		}

		template <typename K, typename V>
		void read(const char* name, std::map<K, V>& value) {
			bsoncxx::document::element element = m_doc[name];

			for (auto& v : element.get_document().value) {
				auto kkk = K();
				auto vvv = V();

				BsonRead br(v.get_document().value);
				br.read("k", kkk);
				br.read("v", vvv);
				value.emplace(kkk, vvv);
			}
		}

	private:
		const bsoncxx::document::view& m_doc;
	};

	
	class FASTNET_API BsonWrite {
	public:
		BsonWrite(bsoncxx::builder::stream::document& doc);
		~BsonWrite() = default;

		void write(const String& name, Int8 value);
		void write(const String& name, Int16 value);
		void write(const String& name, Int32 value);
		void write(const String& name, Int64 value);
		void write(const String& name, UInt8 value);
		void write(const String& name, UInt16 value);
		void write(const String& name, UInt32 value);
		void write(const String& name, UInt64 value);
		void write(const String& name, Double value);
		void write(const String& name, Float value);
		void write(const String& name, Bool value);
		void write(const String& name, const String& value);
		void write(const String& name, Struct& value);

		template <typename T>
		void write(const char* name, std::vector<T>& value) {
			bsoncxx::builder::basic::sub_array sa;
			for (auto& v : value) {
				sa.append(v);
			}

			m_doc << bsoncxx::types::b_utf8{name} << sa;
		}

		template <typename K, typename V>
		void write(const char* name, std::map<K, V>& value) {
            using bsoncxx::builder::basic::kvp;

			bsoncxx::builder::basic::sub_document sd;
			for (auto& v : value) {
				sd.append(kvp('k', v.first), kvp('v', v.second));
			}

			m_doc << bsoncxx::types::b_utf8{name} << sd;
		}

	private:
		bsoncxx::builder::stream::document& m_doc;
	};*/









	class FASTNET_API StreamRead {

	public:
		StreamRead(std::istream& istream)
			:m_istream(istream)
		{

		}

		~StreamRead() = default;

		template <typename T>
		void read(boost::shared_ptr<T>& value) {
			auto key = T::GetKeyType();
			this->read(key);

			T::Reload();
			value = T::GetValue(key);

			if (!value) {
				throw std::runtime_error("StreamRead::read cfg ref == null!");
			}
		}

		template <typename T>
		void read(T& value) {
			if (std::is_base_of<Struct, T>::value) {
				auto s = (Struct*)&value;
				s->Deserialize(*this);
			}
			else {
				m_istream.read((char*)&value, sizeof(value));
			}
		}

		void read(String& value) {
			UInt32 len = 0;
			m_istream.read((char*)&len, s_sizeUInt32);

			if (len >= FastNet_MaxMessageLength) {
				throw std::runtime_error("StreamRead::readString buffer size too long!");
			}

			if (len > 0) {
				value.resize(len);
				m_istream.read((char*)value.c_str(), len);
			}
		}

		template <typename T>
		void read(std::vector<T>& value) {
			UInt32 len = 0;
			m_istream.read((char*)&len, s_sizeUInt32);

			UInt32 buffersize = sizeof(T)*len;
			if (buffersize >= FastNet_MaxMessageLength) {
				throw std::runtime_error("StreamRead::readVector buffer size too long!");
			}

			if (len > 0) {
				value.resize(len);

				if (Struct::IsBasicType<T>()) {
					m_istream.read((char*)&value.at(0), buffersize);
				}
				else {
					for (auto& t : value) {
						read(t);
					}
				}
			}
		}

		template <typename K, typename V>
		void read(std::map<K, V>& arg) {
			UInt32 len = 0;
			m_istream.read((char*)&len, s_sizeUInt32);

			UInt32 buffersize = (sizeof(K) + sizeof(K))*len;
			if (buffersize >= FastNet_MaxMessageLength) {
				throw std::runtime_error("StreamRead::readMap buffer size too long!");
			}
			arg.clear();
			for (UInt32 i = 0; i<len; i++) {
				K key;
				read(key);
				V & value = arg[std::move(key)];
				read(value);
			}
		}

	private:
		std::istream& m_istream;
	};


	class FASTNET_API StreamWrite {
	public:
		StreamWrite(std::ostream& ostream)
			:m_ostream(ostream)
		{

		}

		~StreamWrite() = default;

		template <typename T >
		void write(T& value) {
			if (std::is_base_of<Struct, T>::value) {
				auto s = (Struct*)&value;
				s->Serialize(*this);
			}
			else
			{
				m_ostream.write((char*)&value, sizeof(value));
			}
		}

		void write(String& value) {
			UInt32 len = value.length();
			if (len >= FastNet_MaxMessageLength) {
				throw std::runtime_error("StreamWrite::writeString buffer size too long!");
			}

			m_ostream.write((char*)&len, s_sizeUInt32);

			if (len > 0) {
				m_ostream.write(value.c_str(), len);
			}
		}

		template <typename T>
		void write(std::vector<T>& value) {
			UInt32 len = value.size();

			UInt32 buffersize = sizeof(T)*len;
			if (buffersize >= FastNet_MaxMessageLength) {
				throw std::runtime_error("StreamWrite::writeVector buffer size too long!");
			}

			m_ostream.write((char*)&len, s_sizeUInt32);
			if (!value.empty()) {

				if (Struct::IsBasicType<T>()) {
					m_ostream.write((char*)&value.at(0), sizeof(T)*value.size());
				}
				else {
					for (auto& t : value) {
						write(t);
					}
				}
			}
		}

		template <typename K, typename V>
		void write(std::map<K, V>& arg) {
			UInt32 len = arg.size();
			m_ostream.write((char*)&len, s_sizeUInt32);
			for (auto& t : arg) {
				write((K&)t.first);
				write(t.second);
			}
		}

	private:
		std::ostream& m_ostream;
	};







}
