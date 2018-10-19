#pragma once

#include "FastNet/core/Defs.h"
#include "boost/python/suite/indexing/vector_indexing_suite.hpp"
#include "boost/python/suite/indexing/map_indexing_suite.hpp"

namespace FastNet {

	class StreamWrite;
	class StreamRead;
	class BsonWrite;
	class BsonRead;

	class FASTNET_API Struct {
	public:
        Struct();
        virtual ~Struct();

		virtual void Serialize(FastNet::StreamWrite& stream) {}
		virtual void Deserialize(FastNet::StreamRead& stream) {}
		//virtual void SerializeToBson(FastNet::BsonWrite& bson) {}
		//virtual void DeserializeFromBson(FastNet::BsonRead& bson) {}

        virtual UInt32 SerializeSize();
        virtual void Reset();
		virtual UInt32 ClsId() const;
		virtual const char* ClsName() const;
		virtual UInt32 SignId() const;

        template <typename T>
        static bool IsBasicType(){
            const auto& type = typeid(T);
            if (type == s_tpyeUInt8 ||
                type == s_tpyeInt8 ||
                type == s_tpyeUInt16 ||
                type == s_tpyeInt16 ||
                type == s_tpyeUInt32 ||
                type == s_tpyeInt32 ||
                type == s_tpyeUInt64 ||
                type == s_tpyeInt64 ||
                type == s_tpyeDouble ||
                type == s_tpyeFloat ||
                type == s_tpyeBool) {
                return true;
            }else{
                return false;
            }
        }

        static void CalcSerializeSize(UInt32& size,String& value){
            size = size + s_sizeUInt32 + value.length();
        }

        template <typename T>
        static void CalcSerializeSize(UInt32& size,T& value){
            if (std::is_base_of<Struct, T>::value) {
                auto s = (Struct*)&value;
                size += s->SerializeSize();
            }
            else {
                size += sizeof(value);
            }
        }

        template <typename T>
        static void CalcSerializeSize(UInt32& size,std::vector<T>& value) {
            size += s_sizeUInt32;
            if (value.empty()){
                return;
            }

            if (Struct::IsBasicType<T>()) {
                size += sizeof(T)*value.size();
            }else{
                for (auto& t : value) {
                    CalcSerializeSize(size,t);
                }
            }
        }

        template <typename K, typename V>
        static void CalcSerializeSize(UInt32& size,std::map<K, V>& arg) {
            size += s_sizeUInt32;

            if (Struct::IsBasicType<K>()){
                size += sizeof(K) * arg.size();
            }else{
                for (auto& t : arg) {
                    CalcSerializeSize(size,t.first);
                }
            }

            if (Struct::IsBasicType<V>()){
                size += sizeof(V) * arg.size();
            }else{
                for (auto& t : arg) {
                    CalcSerializeSize(size,t.second);
                }
            }
        }

		boost::python::str ToArray_Python();
		void FromArray_Python(const std::vector<UInt8>&);

		bool isMainThread;
	};


	class FASTNET_API Message :public Struct {
	public:
		Message() = default;
		virtual ~Message() = default;

        static boost::shared_ptr<Message> Create_Python(UInt32 id);

        template <typename T>
        static boost::shared_ptr<T> Create(){
            return boost::dynamic_pointer_cast<T>(Create_Python(T::sClsId()));
        }
	};


	typedef boost::shared_ptr<Message> MessagePtr;

	typedef boost::shared_ptr<Message>(*FNMessageCreate)(void);


#define  DefStruct(cls,id,crc)  \
static const char* sClsName(){ \
return cls; \
}	\
virtual const char* ClsName()const override{ \
return cls; \
}	\
static FastNet::UInt32 sClsId(){  \
return id; \
}	\
virtual FastNet::UInt32 ClsId() const override{  \
return id; \
}	\
static FastNet::UInt32 sSignId(){ \
return crc; \
}	\
virtual FastNet::UInt32 SignId() const override {\
return crc; \
}

}
