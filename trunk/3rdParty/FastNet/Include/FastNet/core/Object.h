#pragma once

#include "FastNet/core/Defs.h"


namespace FastNet {


    class FASTNET_API Object{
	public:
        Object(PyObject* obj);

        virtual ~Object() = default;
        PyObject* GetObject() { return m_obj; }

        void Retain();
        void Release();

	private:
        std::atomic<Int32> m_cntRef;
	protected:
        PyObject* m_obj = nullptr;
	};


	class FASTNET_API ObjectRef {
	public:
        ObjectRef();
		ObjectRef(Object* obj);
		ObjectRef(const ObjectRef& ref);
		ObjectRef& operator = (const ObjectRef& ref);
		ObjectRef& operator = (Object* obj);
		~ObjectRef();

		template <typename T = Object>
		T* Get() const{
			return (T*)m_obj;
		}

	private:
		Object* m_obj = nullptr;
	};


	class FASTNET_API ObjectWeakRef {
	public:
		ObjectWeakRef();
		ObjectWeakRef(Object* obj);
		ObjectWeakRef(const ObjectWeakRef& ref);
		ObjectWeakRef& operator = (const ObjectWeakRef& ref);
		ObjectWeakRef& operator = (Object* obj);
		~ObjectWeakRef();

		template <typename T = Object>
		T* Get() {
			return boost::python::extract<T*>(m_weakRef());
		}

	private:
		boost::python::object m_weakRef;
	};

}
