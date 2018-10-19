using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using UnityEngine;
using XLua;
using MiniJSON;
using System.Collections;

namespace FastNet
{

    using UInt8 = Byte;
    using Int8 = SByte;
    using Float = Single;
    using Bool = Boolean;
    using System.Reflection;
    using System.IO;
    using System.Text;
    

    public class Cfg<T, K>:FastNet.Struct
    {
        private static Type s_typeUInt8 = typeof(UInt8);
        private static Type s_typeUInt16 = typeof(UInt16);
        private static Type s_typeUInt32 = typeof(UInt32);
        private static Type s_typeUInt64 = typeof(UInt64);
        private static Type s_typeInt8 = typeof(Int8);
        private static Type s_typeInt16 = typeof(Int16);
        private static Type s_typeInt32 = typeof(Int32);
        private static Type s_typeInt64 = typeof(Int64);

        private static Type s_typeBool = typeof(Boolean);
        private static Type s_typeString = typeof(String);
        private static Type s_typeFloat = typeof(Float);
        private static Type s_typeDouble = typeof(Double);

        private static List<K> s_keys = new List<K>();
        private static List<T> s_items = new List<T>();

        protected static bool s_load = false;

        public static K ReadKey(BinaryReader stream)
        {
            K k = default(K);
            doDeserialize(stream,ref k);
            return k;
        }
        
        public static List<K> Keys
        {
            get
            {
                return s_keys;
            }
        }

        public static List<T> Items
        {
            get
            {
                return s_items;
            }
        }

        public static T GetItem(K k)
        {
            if (s_load == false)
            {
                var method = typeof(T).GetMethod("Init", BindingFlags.Public | BindingFlags.Static);
                method.Invoke(null, null);
            }

            for (var i = 0; i != s_keys.Count; i++)
            {
                if (s_keys[i].Equals(k))
                {
                    return s_items[i];
                }
            }
            return default(T);
        }

        protected static void Load(String cfgPath,bool force = false)
        {
            if (s_load == true && force == false)
            {
                return;
            }

            FileStream ifs = null;

            try
            {

                s_keys.Clear();
                s_items.Clear();

                ifs = new FileStream(cfgPath, FileMode.Open, FileAccess.Read);

                UInt32 cfgCodeVersion = 0;
                UInt32 cfgDataVersion = 0;

                var binaryReader = new BinaryReader(ifs);
                cfgCodeVersion = binaryReader.ReadUInt32();
                cfgDataVersion = binaryReader.ReadUInt32();

                var t = typeof(T);
                PropertyInfo sSignId = t.GetProperty("sSignId", BindingFlags.Public | BindingFlags.Static);
                var signId = (UInt32)sSignId.GetValue(null, null);

                if (signId != cfgCodeVersion)
                {
                    return;
                }

                UInt32 cfgCount = binaryReader.ReadUInt32();


                var k = typeof(K);

                for (var i = 0; i < cfgCount; i++)
                {
                    var kk = k.Assembly.CreateInstance(k.FullName);

                    if (s_typeString == k)
                    {
                        var len = binaryReader.ReadUInt32();
                        if (len > 0)
                        {
                            var bytes = new byte[len];
                            binaryReader.Read(bytes, 0, (int)len);
                            kk = (K)(object)Encoding.UTF8.GetString(bytes);
                        }
                        else
                        {
                            kk = (K)(object)String.Empty;
                        }
                    }
                    else if (s_typeUInt8 == k)
                    {
                        var value = binaryReader.ReadByte();
                        kk = (K)(object)value;
                    }
                    else if (s_typeUInt16 == k)
                    {
                        var value = binaryReader.ReadUInt16();
                        kk = (K)(object)value;
                    }
                    else if (s_typeUInt32 == k)
                    {
                        var value = binaryReader.ReadUInt32();
                        kk = (K)(object)value;
                    }
                    else if (s_typeUInt64 == k)
                    {
                        var value = binaryReader.ReadUInt64();
                        kk = (K)(object)value;
                    }
                    else if (s_typeInt8 == k)
                    {
                        var value = binaryReader.ReadSByte();
                        kk = (K)(object)value;
                    }
                    else if (s_typeInt16 == k)
                    {
                        var value = binaryReader.ReadInt16();
                        kk = (K)(object)value;
                    }
                    else if (s_typeInt32 == k)
                    {
                        var value = binaryReader.ReadInt32();
                        kk = (K)(object)value;
                    }
                    else if (s_typeInt64 == k)
                    {
                        var value = binaryReader.ReadInt64();
                        kk = (K)(object)value;
                    }
                    else if (s_typeBool == k)
                    {
                        var value = binaryReader.ReadBoolean();
                        kk = (K)(object)value;
                    }
                    else if (s_typeFloat == k)
                    {
                        var value = binaryReader.ReadSingle();
                        kk = (K)(object)value;
                    }
                    else if (s_typeDouble == k)
                    {
                        var value = binaryReader.ReadDouble();
                        kk = (K)(object)value;
                    }
                    else
                    {
                        var value = binaryReader.ReadInt32();
                        kk = (K)(object)value;
                    }

                    s_keys.Add((K)kk);
                }

                for (var i = 0; i < cfgCount; i++)
                {
                    Struct tt = (Struct)t.Assembly.CreateInstance(t.FullName);
                    tt.Deserialize(binaryReader);
                    s_items.Add((T)(object)tt);
                }
                s_load = true;
            }
            catch (Exception e)
            {
                System.Console.WriteLine(e.Message);
            }
            finally
            {
                if (ifs != null)
                {
                    ifs.Close();
                }
            }
        }
    }






    [LuaCallCSharp]
    public class CfgLua : Struct
    {
        private abstract class KeyTypeConvertBase 
        {
            public abstract object Convert(object k);
        }

        private class KeyTypeConvert<T> : KeyTypeConvertBase
        {
            public override object Convert(object k)
            {
                return System.Convert.ChangeType(k, typeof(T));
            }
        }


        private UInt32 _clsId = 0;
        private String _clsName = "";
        private UInt32 _signId = 0;
        private String _index = "";
        private String _cfgPath = "";
        private List<Attr> _attrs = new List<Attr>();
        private XLua.LuaEnv _luaEnv = null;
        private XLua.LuaTable _luaTable = null;
        private KeyTypeConvertBase _keyTypeConvert;

        private const String _sUint8 = "UInt8";
        private const String _sUint16 = "UInt16";
        private const String _sUint32 = "UInt32";
        private const String _sUint64 = "UInt64";
        private const String _sInt8 = "Int8";
        private const String _sInt16 = "Int16";
        private const String _sInt32 = "Int32";
        private const String _sInt64 = "Int64";
        private const String _sDouble = "Double";
        private const String _sFloat = "Float";
        private const String _sBool = "Bool";
        private const String _sString = "String";
        private const String _sEnum = "Enum";
        private const String _sSelf = "__self__";


        private bool m_isCfgLoad = false;

        [XLua.BlackList]
        public class Attr
        {
            public String name;
            public String type;
            public String defVal;
            public object objDefVal = null;
        }

        [XLua.BlackList]
        public String IndexType
        {
            get
            {
                return _index;
            }
        }

        private delegate XLua.LuaTable DelegateGetItem(object key);


        [XLua.BlackList]
        public CfgLua(XLua.LuaEnv luaEnv, UInt32 clsId, String clsName, UInt32 signId, List<Attr> attrs, String index = "", String cfgPath = "")
        {
            _luaEnv = luaEnv;
            _index = index;

            _cfgPath = cfgPath;
            _luaTable = _luaEnv.NewTable();
            _luaTable.Set(_sSelf, this);
       
            _clsId = clsId;
            _clsName = clsName;
            _signId = signId;
            _attrs = attrs;

            _luaTable.Set("ClsName", _clsName);
            _luaTable.Set("ClsId", _clsId);
            _luaTable.Set("SignId", _signId);
            
            _keys = new List<object>();
            _items = new List<LuaTable>();

            _luaTable.Set<String, List<object>>("Keys", this.Keys);
            _luaTable.Set<String, List<LuaTable>>("Items", this.Items);
            _luaTable.Set<String, DelegateGetItem>("GetItem", this.GetItem);

            if (index.Equals(_sString))
            {
                 _keyTypeConvert = new KeyTypeConvert<String>();
            }
            else if (index.Equals(_sInt32))
            {
                _keyTypeConvert = new KeyTypeConvert<Int32>();
            }
            else if (index.Equals(_sUint32))
            {
                _keyTypeConvert = new KeyTypeConvert<UInt32>();
            }
            else if (index.Equals(_sUint8))
            {
                _keyTypeConvert = new KeyTypeConvert<UInt8>();
            }
            else if (index.Equals(_sUint16))
            {
                _keyTypeConvert = new KeyTypeConvert<UInt16>();
            }
            else if (index.Equals(_sUint64))
            {
                _keyTypeConvert = new KeyTypeConvert<UInt64>();
            }
            else if (index.Equals(_sInt8))
            {
                _keyTypeConvert = new KeyTypeConvert<Int8>();
            }
            else if (index.Equals(_sInt16))
            {
                _keyTypeConvert = new KeyTypeConvert<Int16>();
            }

            else if (index.Equals(_sInt64))
            {
                _keyTypeConvert = new KeyTypeConvert<Int64>();
            }
            else if (index.Equals(_sDouble))
            {
                _keyTypeConvert = new KeyTypeConvert<Double>();
            }
            else if (index.Equals(_sFloat))
            {
                _keyTypeConvert = new KeyTypeConvert<Float>();
            }
            else if (index.Equals(_sBool))
            {
                _keyTypeConvert = new KeyTypeConvert<Bool>();
            }
        }


        private static object ReadValue(BinaryReader stream, String t)
        {
            if (t.Equals(_sString))
            {
                String value = "";
                doDeserialize(stream, ref value);
                return value;
            }
            else if (t.Equals(_sInt32))
            {
                Int32 value = 0;
                doDeserialize(stream, ref value);
                return value;
            }
            else if (t.Equals(_sUint32))
            {
                UInt32 value = 0;
                doDeserialize(stream, ref value);
                return value;
            }
            else if (t.Equals(_sEnum))
            {
                Int32 value = 0;
                doDeserialize(stream, ref value);
                return value;
            }
            else if (t.Equals(_sUint8))
            {
                UInt8 value = 0;
                doDeserialize(stream, ref value);
                return value;
            }
            else if (t.Equals(_sUint16))
            {
                UInt16 value = 0;
                doDeserialize(stream, ref value);
                return value;
            }
            else if (t.Equals(_sUint64))
            {
                UInt64 value = 0;
                doDeserialize(stream, ref value);
                return value;
            }
            else if (t.Equals(_sInt8))
            {
                Int8 value = 0;
                doDeserialize(stream, ref value);
                return value;
            }
            else if (t.Equals(_sInt16))
            {
                Int16 value = 0;
                doDeserialize(stream, ref value);
                return value;
            }

            else if (t.Equals(_sInt64))
            {
                Int64 value = 0;
                doDeserialize(stream, ref value);
                return value;
            }
            else if (t.Equals(_sDouble))
            {
                Double value = 0.0f;
                doDeserialize(stream, ref value);
                return value;
            }
            else if (t.Equals(_sFloat))
            {
                Float value = 0.0f;
                doDeserialize(stream, ref value);
                return value;
            }
            else if (t.Equals(_sBool))
            {
                Bool value = false;
                doDeserialize(stream, ref value);
                return value;
            }
            else
            {
                return null;
            }
        }

        private List<object> _keys;
        private List<LuaTable> _items;

        
        public LuaTable GetItem(object key)
        {
            var keyCopy = _keyTypeConvert.Convert(key);
            for (var i = 0; i != _keys.Count; i++)
            {
                if (_keys[i].Equals(keyCopy))
                {
                    return _items[i];
                }
            }
            return null;
        }

        public List<object> Keys
        {
            get
            {
                return _keys;
            }
        }

        public List<LuaTable> Items
        {
            get
            {
                return _items;
            }
        }

        [XLua.BlackList]
        public void LoadCfg()
        {
            if (m_isCfgLoad == true)
            {
                return;
            }

            FileStream ifs = null;

            try
            {
                _keys.Clear();
                _items.Clear();


                var cfgPath = App.WorkPath + _cfgPath;

                if (!File.Exists(cfgPath))
                {
                    UnityEngine.Debug.LogError(String.Format("{0} no exists", cfgPath));
                    return;
                }

                ifs = new FileStream(cfgPath, FileMode.Open, FileAccess.Read);

                UInt32 cfgCodeVersion = 0;
                UInt32 cfgDataVersion = 0;

                var binaryReader = new BinaryReader(ifs);
                cfgCodeVersion = binaryReader.ReadUInt32();
                cfgDataVersion = binaryReader.ReadUInt32();

                if (this.SignId != cfgCodeVersion)
                {
                    return;
                }

                UInt32 cfgCount = binaryReader.ReadUInt32();


                for (var i = 0; i < cfgCount; i++)
                {
                    _keys.Add(ReadValue(binaryReader, _index));
                }

                for (var i = 0; i < cfgCount; i++)
                {
                    var luaTable = _luaEnv.NewTable();
                    this.Decode(luaTable, binaryReader);
                    _items.Add(luaTable);
                }

                m_isCfgLoad = true;
            }
            catch (Exception e)
            {
                UnityEngine.Debug.LogException(e);
            }
            finally
            {
                if (ifs != null)
                {
                    ifs.Close();
                }
            }
        }

        [XLua.BlackList]
        public static void Load(String jsonPath, XLua.LuaEnv luaEnv)
        {
            try
            {
                if (!File.Exists(jsonPath))
                {
                    UnityEngine.Debug.LogError(String.Format("{0} no exists", jsonPath));
                    return;
                }

                StreamReader sr = File.OpenText(jsonPath);
                string input = sr.ReadToEnd();
                var jsonObjects = MiniJSON.MiniJSON.jsonDecode(input) as ArrayList;

                foreach (Hashtable v in jsonObjects)
                {
                    var attrs = new List<CfgLua.Attr>();
                    foreach (Hashtable c in (ArrayList)v["attrs"])
                    {
                        var attr = new CfgLua.Attr();
                        attr.name = (String)c["name"];
                        attr.type = (String)c["type"];
                        attr.defVal = (String)c["value"];
                        attrs.Add(attr);
                    }

                    var ttt = v["clsId"].GetType();
                    var clsId = (Double)v["clsId"];
                    var signId = (Double)v["signId"];
                    var message = new CfgLua(luaEnv,
                        (UInt32)clsId,
                        (String)v["clsName"],
                        (UInt32)signId, 
                        attrs, 
                        (String)v["index"],
                        (String)v["cfgPath"]);

                    App.SetTable((String)v["clsName"], message);
                }


                foreach (Hashtable v in jsonObjects)
                {
                    var cl = luaEnv.Global.GetInPath<CfgLua>((String)v["clsName"]);
                    cl.LoadCfg();
                }

            }
            catch (Exception e)
            {
                UnityEngine.Debug.LogException(e);
            }
        }


        public override UInt32 ClsId
        {
            get
            {
                return _clsId;
            }
        }

        public override UInt32 SignId
        {
            get
            {
                return _signId;
            }
        }

        public override String ClsName
        {
            get
            {
                return _clsName;
            }
        }

        [XLua.BlackList]
        public void Decode(XLua.LuaTable luaTable, BinaryReader stream)
        {
            var dictionary = new Dictionary<String, object>();
            foreach (var v in _attrs)
            {
                try
                {
                    if (v.type.Equals(_sString))
                    {
                        String value = "";
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name, value);
                    }
                    else if (v.type.Equals(_sInt32))
                    {
                        Int32 value = 0;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name, value);
                    }
                    else if (v.type.Equals(_sUint32))
                    {
                        UInt32 value = 0;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name, value);
                    }
                    else if (v.type.Equals(_sEnum))
                    {
                        Int32 value = 0;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name, value);
                    }
                    else if (v.type.Equals(_sUint8))
                    {
                        UInt8 value = 0;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name, value);
                    }
                    else if (v.type.Equals(_sUint16))
                    {
                        UInt16 value = 0;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name, value);
                    }

                    else if (v.type.Equals(_sUint64))
                    {
                        UInt64 value = 0;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name, value);
                    }
                    else if (v.type.Equals(_sInt8))
                    {
                        Int8 value = 0;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name, value);
                    }
                    else if (v.type.Equals(_sInt16))
                    {
                        Int16 value = 0;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name, value);
                    }

                    else if (v.type.Equals(_sInt64))
                    {
                        Int64 value = 0;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name, value);
                    }
                    else if (v.type.Equals(_sDouble))
                    {
                        Double value = 0.0f;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name, value);
                    }
                    else if (v.type.Equals(_sFloat))
                    {
                        Float value = 0.0f;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name, value);
                    }
                    else if (v.type.Equals(_sBool))
                    {
                        Bool value = false;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name, value);
                    }
                    else
                    {
                        //var table = _luaEnv.Global.GetInPath<CfgLua>(v.type);
                        //var ml = table.Get<String, CfgLua>(_sSelf);
                        var cl = _luaEnv.Global.GetInPath<CfgLua>(v.type);

                        cl.LoadCfg();

                        var indexValue = ReadValue(stream, cl.IndexType);
                        dictionary.Add(v.name, cl.GetItem(indexValue));
                        
                    }
                }
                catch (Exception e)
                {
                    UnityEngine.Debug.LogException(e);
                }
            }

            luaTable.Set(dictionary);
        }
    }



















}
