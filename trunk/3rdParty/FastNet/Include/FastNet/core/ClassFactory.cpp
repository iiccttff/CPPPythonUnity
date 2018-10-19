#include "ClassFactory.h"


namespace FastNet {

	ClassFactory::ClassFactory(){

	}

	ClassFactory::~ClassFactory() {

	}

	boost::shared_ptr<ClassFactory> ClassFactory::Instance() {
		static boost::shared_ptr<ClassFactory> s_instance(new ClassFactory());
		return s_instance;
	}

	MessagePtr ClassFactory::Create(const UInt32 classId) const
	{
		std::unique_lock<std::mutex> lock(m_mutex);

		FactoryMap::const_iterator it = _map.find(classId);
		if (it != _map.end())
			return MessagePtr(it->second->Create());
		else
			return nullptr;
	}


	void ClassFactory::Register(const UInt32 classId, boost::shared_ptr<AbstractFactory> pAbstractFactory)
	{
		std::unique_lock<std::mutex> lock(m_mutex);

		FactoryMap::iterator it = _map.find(classId);
		if (it == _map.end())
			_map[classId] = pAbstractFactory;
		else
		{
			LogError("ClassFactory::RegisterClass classId:%lld is repetition", classId);
		}
	}

	void ClassFactory::Unregister(const UInt32 classId)
	{
		std::unique_lock<std::mutex> lock(m_mutex);
		FactoryMap::iterator it = _map.find(classId);
		if (it != _map.end())
		{
			_map.erase(it);
		}
		else {
			LogError("ClassFactory::UnregisterClass no find class:%lld", classId);
		}
	}

	void ClassFactory::UnregisterAll()
	{
		std::unique_lock<std::mutex> lock(m_mutex);
		_map.clear();
	}

	bool ClassFactory::IsClass(const UInt32 classId) const
	{
		std::unique_lock<std::mutex> lock(m_mutex);
		return _map.find(classId) != _map.end();
	}


}