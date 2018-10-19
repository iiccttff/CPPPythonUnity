#pragma once

#include "FastNet/core/Message.h"
#include "FastNet/core/Object.h"

namespace FastNet {


	class FASTNET_API Callback {
	public:
		Callback();
        virtual ~Callback() = default;

		typedef std::function<void(Object*, const MessagePtr&)> Func;

		struct Info {
			std::string name;
			Func func;
		};

		struct Queue {
			Queue();
			~Queue();
            Info* info;
            ObjectRef ref;
            MessagePtr message;
		};

		void BindMessage_Python(UInt32 id, const std::string& name);

		template<typename C, typename T>
		void BindMessage(void (C::*f)(const boost::shared_ptr<T>&)) {
			this->DoBindMessage(T::sClsId(),std::bind(&Callback::callback<T>,(void (Object::*)(const boost::shared_ptr<T>&))f,std::placeholders::_1,std::placeholders::_2));
		}

		template<typename T>
		void BindMessage(const std::function<void(Object* obj,const boost::shared_ptr<T>&)>& f) {
			this->DoBindMessage(T::sClsId(), std::bind(&Callback::callback2<T>, f, std::placeholders::_1, std::placeholders::_2));
		}

	private:

		void DoBindMessage(UInt32 id, const Func& f);

		template<typename T>
		static void callback(void (Object::*f)(const boost::shared_ptr<T>&), Object* obj, const MessagePtr& message) {
			auto messageRef = boost::dynamic_pointer_cast<T>(message);
			(obj->*f)(messageRef);
		}

		template<typename T>
		static void callback2(const std::function<void(Object* obj, const boost::shared_ptr<T>&)>& f, Object* obj, const MessagePtr& message) {
			auto messageRef = boost::dynamic_pointer_cast<T>(message);
			f(obj,messageRef);
		}

	protected:
		std::map<UInt32, Info> m_callbacks;

		
	};
}



