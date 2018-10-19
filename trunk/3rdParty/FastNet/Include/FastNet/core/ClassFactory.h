#pragma once

#include "FastNet/core/Message.h"
#include "FastNet/core/Log.h"
#include "FastNet/core/Object.h"
#include "FastNet/core/Singleton.h"

namespace FastNet {

	template <class Base>
	class  AbstractInstantiator
	{
	public:
		AbstractInstantiator(const AbstractInstantiator&) = delete;
		AbstractInstantiator& operator = (const AbstractInstantiator&) = delete;

		AbstractInstantiator() = default;

		virtual ~AbstractInstantiator() = default;

        virtual Base* Create() const = 0;
	};


	template <class C, class Base>
	class Instantiator : public AbstractInstantiator<Base>
	{
	public:
		Instantiator() = default;

		virtual ~Instantiator() = default;

		Base* Create() const override
		{
            return (Base*)new C();
		}
	};


	class FASTNET_API ClassFactory final:public Singleton<ClassFactory>
	{
		ClassFactory& operator = (const ClassFactory&) = delete;
	public:
		typedef AbstractInstantiator<Message> AbstractFactory;

		ClassFactory(const ClassFactory& factory) = delete;
		ClassFactory();
		virtual ~ClassFactory();

		static boost::shared_ptr<ClassFactory> Instance();

		template <class C>
		void Register()
		{
			Register(C::sClsId(), boost::make_shared<Instantiator<C, Message> >());
		}

		void Register(const UInt32 classId, boost::shared_ptr<AbstractFactory> pAbstractFactory);

		void Unregister(const UInt32 classId);

		void UnregisterAll();

		bool IsClass(const UInt32 classId) const;

		MessagePtr Create(const UInt32 classId) const;
	protected:


	private:
		typedef std::map<UInt32, boost::shared_ptr<AbstractFactory> > FactoryMap;

		FactoryMap _map;
		mutable std::mutex m_mutex;
	};

}
