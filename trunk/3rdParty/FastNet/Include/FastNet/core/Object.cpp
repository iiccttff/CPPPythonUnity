#include "Object.h"
#include "App.h"


namespace FastNet {
	extern Poco::Thread::TID g_mainThreadId;


    Object::Object(PyObject* obj):m_obj(obj){
        m_cntRef = 0;
        poco_assert_msg(Poco::Thread::currentTid() == g_mainThreadId, "Object::Object calls must be is main thread!");
    }

	void Object::Retain() { 

        if (m_obj == nullptr) {
            return;
        }

		if (m_cntRef == 0) {
			Py_INCREF(m_obj);
		}

		m_cntRef++; 
	}

	void Object::Release() {

		if (m_obj == nullptr) {
			return;
		}

        if (m_cntRef <= 0 ) {
            poco_assert_dbg(false);
            return;
        }

        m_cntRef--;
        if (m_cntRef == 0) {

			if (Poco::Thread::currentTid() == g_mainThreadId) {
				Py_DECREF(m_obj);
			}
			else {
				App::Instance().PushDestoryObject(m_obj);
			}
		}
    }

    ObjectRef::ObjectRef(){
    }

	ObjectRef::ObjectRef(Object* obj) :m_obj(obj) {

		if (m_obj) {
			m_obj->Retain();
		}
	}

	ObjectRef::ObjectRef(const ObjectRef& ref) {
        auto obj = m_obj;

		m_obj = ref.m_obj;
		if (m_obj) {
			m_obj->Retain();
		}

        if (obj) {
            obj->Release();
        }
	}

	ObjectRef& ObjectRef::operator = (const ObjectRef& ref) {

        auto obj = m_obj;
		m_obj = ref.m_obj;

		if (m_obj) {
			m_obj->Retain();
		}
		
        if (obj) {
            obj->Release();
        }

		return *this;
	}

    ObjectRef& ObjectRef::operator = (Object* ref) {
        auto obj = m_obj;

        m_obj = ref;

		if (m_obj) {
			m_obj->Retain();
		}

        if (obj) {
            obj->Release();
        }

		return *this;
	}

	ObjectRef::~ObjectRef() {
        if (m_obj) {
            m_obj->Release();
        }

	}






	ObjectWeakRef::ObjectWeakRef() {
	}

	ObjectWeakRef::ObjectWeakRef(Object* obj) {

		if (obj) {
			auto moduleWeakref = boost::python::import("weakref");
			m_weakRef = moduleWeakref.attr("ref")(boost::python::object(boost::python::detail::borrowed_reference(obj->GetObject())));
		}
	}

	ObjectWeakRef::ObjectWeakRef(const ObjectWeakRef& ref) {
		m_weakRef = ref.m_weakRef;
	}

	ObjectWeakRef& ObjectWeakRef::operator = (const ObjectWeakRef& ref) {

		m_weakRef = ref.m_weakRef;

		return *this;
	}

	ObjectWeakRef& ObjectWeakRef::operator = (Object* ref) {
		if (ref != nullptr) {
			auto moduleWeakref = boost::python::import("weakref");
			m_weakRef = moduleWeakref.attr("ref")(boost::python::object(boost::python::detail::borrowed_reference(ref->GetObject())));
		}
		return *this;
	}

	ObjectWeakRef::~ObjectWeakRef() {


	}

}
