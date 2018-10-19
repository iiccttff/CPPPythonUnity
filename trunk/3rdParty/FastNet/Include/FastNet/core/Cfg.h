#pragma once
#include "FastNet/core/Stream.h"
#include "FastNet/core/Log.h"

namespace FastNet {

template <typename T, typename K = UInt32>
class Cfg {
private:

	static boost::shared_ptr<std::map<K, boost::shared_ptr<T> > > s_values;
	static boost::python::list* s_keys_py;
	static boost::python::list* s_values_py;

	static UInt32 s_cfgDataVersion;
	static std::string s_cfgBasePath;
	static std::string s_cfgRelativePath;
	static bool s_reloading;
public:
	static K GetKeyType() { return K(); }
	static boost::shared_ptr<std::map<K, boost::shared_ptr<T> > > GetValues() { return s_values; }
	
	static boost::python::list GetKeys_Python() {
		if (!s_keys_py) {
			return boost::python::list();
		}

		return *s_keys_py;
	}

	static boost::python::list GetValues_Python(){ 
		if (!s_values_py) {
			return boost::python::list();
		}

		return *s_values_py;
	}

	static boost::shared_ptr<T> GetValue(const K& k) {
		if (!s_values) {
			return nullptr;
		}

		auto itValue = s_values->find(k);
		if (s_values->end() == itValue) {
			return nullptr;
		}

		return itValue->second;
	}

	static void Reload() {

		if (s_reloading == true) {
			throw std::runtime_error(Poco::format("Cfg::Reload '%s' fail, cannot nested reference!", s_cfgRelativePath));
		}

		s_reloading = true;

		std::ifstream ifs(s_cfgBasePath + "/" + s_cfgRelativePath, std::ios::binary | std::ios::in);
		UInt32 cfgCodeVersion = 0;
		UInt32 cfgDataVersion = 0;

		ifs.read((char*)&cfgCodeVersion, sizeof(UInt32));
		ifs.read((char*)&cfgDataVersion, sizeof(UInt32));

		if (T::sSignId() != cfgCodeVersion) {
			s_reloading = false;
			FastNet::LogError(Poco::format("Cfg::Reload '%s' fail, sign error! %?i", s_cfgRelativePath, cfgCodeVersion));
			return;
		}

		if (s_cfgDataVersion == 0 || s_cfgDataVersion != cfgDataVersion) {
			s_cfgDataVersion = cfgDataVersion;

			UInt32 cfgCount = 0;
			ifs.read((char*)&cfgCount, sizeof(UInt32));

			std::vector<K> keys;
			//std::vector<boost::shared_ptr<T> > items;

			auto values = boost::make_shared<std::map<K, boost::shared_ptr<T> > >();

			StreamRead sr(ifs);
			for (auto i = 0;i < cfgCount;i++) {
				K k;
				sr.read(k);
				keys.emplace_back(k);
			}

			if (s_keys_py != nullptr) {
				delete s_keys_py;
			}

			if (s_values_py != nullptr) {
				delete s_values_py;
			}

			s_keys_py = new boost::python::list();
			s_values_py = new boost::python::list();

			for (auto i = 0;i < cfgCount;i++) {
				auto t = boost::make_shared<T>();
				try {
					t->Deserialize(sr);
				}
				catch (...) {

				}
				
				values->emplace(keys.at(i),t);
				s_keys_py->append(keys.at(i));
				s_values_py->append(t);
			}

			s_values = values;

			App::AddCfgCachePyObject(T::sClsId(), s_keys_py, s_values_py);

			LogDebug("Cfg::Reload '%s' succeed!", s_cfgRelativePath.c_str());
		}

		s_reloading = false;
	}

	static void Init(const std::string& path) {
		s_cfgDataVersion = 0;
		s_cfgBasePath = path;
		s_reloading = false;
	}

	template <typename C>
	static void ExportCfg(C& t, const std::string& cfgPath) {
		s_cfgRelativePath = cfgPath;

		auto mapName = Poco::format("Map%s%?i",String(typeid(K).name()), T::sClsId());
		//App::RegisterStlMap<std::map<K, boost::shared_ptr<T> > >(mapName.c_str());

		//t.def("GetValues", &Cfg::GetValues).staticmethod("GetValues");
		t.def("GetKeys", &Cfg::GetKeys_Python).staticmethod("GetKeys");
		t.def("GetValues", &Cfg::GetValues_Python).staticmethod("GetValues");
		t.def("GetValue", &Cfg::GetValue).staticmethod("GetValue");
	}
};

template<typename T, typename K>
boost::shared_ptr<std::map<K, boost::shared_ptr<T> > > Cfg<T, K>::s_values;


template<typename T, typename K>
boost::python::list* Cfg<T, K>::s_keys_py = nullptr;

template<typename T, typename K>
boost::python::list* Cfg<T, K>::s_values_py = nullptr;

template<typename T, typename K>
UInt32 Cfg<T, K>::s_cfgDataVersion = 0;

template<typename T, typename K>
std::string Cfg<T, K>::s_cfgBasePath;

template<typename T, typename K>
std::string Cfg<T, K>::s_cfgRelativePath;

template<typename T, typename K>
bool Cfg<T, K>::s_reloading;


}