#pragma once

#include "FastNet/core/Defs.h"

namespace FastNet {

	template<typename T>
	class Singleton {
		static boost::shared_ptr<T> s_instance;
	public:
		static boost::shared_ptr<T> Instance() {
			return s_instance;
		}

		static void Create() {
			s_instance = boost::make_shared<T>();
			s_instance->OnCreate();
		}

		static void Destory() {
			if (s_instance) {
				s_instance->OnDestory();
				s_instance = nullptr;
			}
		}

		virtual void OnCreate() {}
		virtual void OnDestory() {}
	};

	template<typename T>
	boost::shared_ptr<T> Singleton<T>::s_instance;
}