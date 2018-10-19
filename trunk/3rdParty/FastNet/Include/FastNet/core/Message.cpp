#include "Message.h"

#include "Log.h"
#include "ClassFactory.h"

#include "boost/thread/tss.hpp"

#include "Poco/MemoryStream.h"
#include "Message.h"

#include "Stream.h"
namespace FastNet {

	extern Poco::Thread::TID g_mainThreadId;


    std::atomic<UInt32> s_structCount(0);

    Struct::Struct(){
		isMainThread = Poco::Thread::currentTid() == g_mainThreadId;
		s_structCount++;
    }

    Struct::~Struct(){
		s_structCount--;
    }


    UInt32 Struct::SerializeSize(){
        return 0;
    }

    void Struct::Reset(){

    }

	UInt32 Struct::SignId() const {
		return 0;
	}

	boost::python::str Struct::ToArray_Python() {
		auto size = this->SerializeSize();
		if (size > 0) {
			std::vector<UInt8> buffer(size);
			Poco::MemoryOutputStream mos((char*)&buffer.at(0), size);
			StreamWrite stream(mos);
			this->Serialize(stream);
			return boost::python::str((char*)&buffer.at(0), size);
		}
		else {
			return boost::python::str("");
		}
	}

	void Struct::FromArray_Python(const std::vector<UInt8>& l) {
		if (l.size() > 0) {
			Poco::MemoryInputStream mis((char*)&l.at(0), l.size());
			StreamRead stream(mis);
			this->Deserialize(stream);
		}
	}

	UInt32 Struct::ClsId()const {
		return Poco::hash(ClsName());
	}

	const char* Struct::ClsName()const {
		return "FastNet.Struct";
	}

    struct CacheMessage{
        std::map<UInt32,std::queue<MessagePtr> > cacheMessages;
        std::time_t time;
        std::list<MessagePtr> recoveryMessages;
    };

    MessagePtr Message::Create_Python(UInt32 id){
        static boost::thread_specific_ptr<CacheMessage> s_cacheMessages;

        auto p = s_cacheMessages.get();
        if (p == nullptr){
            p = new CacheMessage();
            p->time = std::time(nullptr) + std::rand() % 30;
            s_cacheMessages.reset(p);
        }

        auto now = std::time(nullptr);
        if (now > (p->time + 60)){
            p->time = now + std::rand() % 10;
            auto itBegin = p->recoveryMessages.begin();
            for (;itBegin != p->recoveryMessages.end();){
                if (itBegin->unique()){
                    p->cacheMessages[(*itBegin)->ClsId()].emplace(*itBegin);
                    itBegin = p->recoveryMessages.erase(itBegin);
                }else{
                    ++itBegin;
                }
            }
        }

        auto& queue = p->cacheMessages[id];
        if (!queue.empty()){
            auto result = queue.front();
            queue.pop();
			result->Reset();
            return result;
        }else{
            auto result = ClassFactory::Instance()->Create(id);
            p->recoveryMessages.emplace_back(result);
            return result;
        }
    }
	
}
