using System;
using System.Collections.Generic;
using XLua;
using System.Xml;
using UnityEngine;
using MiniJSON;
using System.Collections;

namespace FastNet
{
    using UInt8 = Byte;
    using Int8 = SByte;
    using Float = Single;
    using Bool = Boolean;
    using System.Net;
    using System.Net.Sockets;
    using System.Threading;
    using System.Runtime.InteropServices;
    using System.Reflection;
    using System.IO;
    using System.Text;

    using LuaAPI = XLua.LuaDLL.Lua;

    
    public class Message: Struct
    {
        
    }

    public class MessageLua : Struct
    {
        private UInt32 _clsId = 0;
        private String _clsName = "";
        private UInt32 _signId = 0;
        private String _type = "";
        private List<Attr> _attrs = new List<Attr>();
        private XLua.LuaEnv _luaEnv = null;
        private XLua.LuaTable _luaTable = null;

        public class Attr
        {
            public String name;
            public String type;
            public String defVal;
            public object objDefVal = null;
        }

        
        private delegate XLua.LuaTable DelegateCreate();
        private delegate XLua.LuaTable DelegateGetItem(object key);

        public MessageLua(XLua.LuaEnv luaEnv, UInt32 clsId, String clsName, UInt32 signId, String type, List<Attr> attrs)
        {
            _luaEnv = luaEnv;
            _luaTable = _luaEnv.NewTable();
            _type = type;
            _luaTable.Set(s_sSelf, this);

            if (_type.Equals(s_sEnum))
            {
                foreach (var v in attrs)
                {
                    _luaTable.Set(v.name,Int32.Parse(v.defVal));
                }
            }
            else
            {
                _clsId = clsId;
                _clsName = clsName;
                _signId = signId;
                _attrs = attrs;

                _luaTable.Set("ClsName", _clsName);
                _luaTable.Set("ClsId", _clsId);
                _luaTable.Set("SignId", _signId);

                _luaTable.Set<String, DelegateCreate>("Create", this.Create);
            }
        }


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
                    if (((String)v["type"]).Equals("Enum"))
                    {
                        var attrs = new List<MessageLua.Attr>();
                        foreach (Hashtable c in (ArrayList)v["attrs"])
                        {
                            var attr = new MessageLua.Attr();
                            attr.name = (String)c["name"];
                            attr.defVal = (String)c["value"];
                            attrs.Add(attr);
                        }

                        var message = new MessageLua(luaEnv, 0, (String)v["clsName"], 0, (String)v["type"], attrs);
                        App.SetTable((String)v["clsName"], message.GetLuaTable());
                    }
                    else
                    {
                        var attrs = new List<MessageLua.Attr>();
                        foreach (Hashtable c in (ArrayList)v["attrs"])
                        {
                            var attr = new MessageLua.Attr();
                            attr.name = (String)c["name"];
                            attr.type = (String)c["type"];
                            attr.defVal = (String)c["value"];
                            attrs.Add(attr);
                        }

                        var message = new MessageLua(luaEnv, (UInt32)(Double)v["clsId"], (String)v["clsName"], (UInt32)(Double)v["signId"], (String)v["type"], attrs);
                        App.SetTable((String)v["clsName"], message.GetLuaTable());
                        App.RegisterMessage(message, true);
                    }
                }
            }
            catch (Exception e)
            {
                UnityEngine.Debug.LogException(e);
            }
        }

        public XLua.LuaTable GetLuaTable()
        {
            return _luaTable;
        }

        public XLua.LuaTable Create()
        {
            var t = _luaEnv.NewTable();
            t.Set("ClsName", _clsName);
            t.Set("ClsId", _clsId);
            t.Set("SignId", _signId);
            t.Set(s_sSelf, this);

            object objDefVal = null;
            
            foreach (var v in _attrs)
            {
                if (v.objDefVal == null)
                {
                    try
                    {
                        if (v.type.Equals(s_sString))
                        {
                            v.objDefVal = v.defVal;
                        }
                        else if (v.type.Equals(s_sInt32))
                        {
                            v.objDefVal = 0;
                            v.objDefVal = Int32.Parse(v.defVal);
                        }
                        else if (v.type.Equals(s_sUint32))
                        {
                            v.objDefVal = 0;
                            v.objDefVal = UInt32.Parse(v.defVal);
                        }
                        else if (v.type.Equals(s_sEnum))
                        {
                            v.objDefVal = false;
                            v.objDefVal = Int32.Parse(v.defVal);
                        }
                        else if (v.type.Equals(s_sUint8))
                        {
                            v.objDefVal = 0;
                            v.objDefVal = Byte.Parse(v.defVal);
                        }
                        else if (v.type.Equals(s_sUint16))
                        {
                            v.objDefVal = 0;
                            v.objDefVal = UInt16.Parse(v.defVal);
                        }
                        
                        else if (v.type.Equals(s_sUint64))
                        {
                            v.objDefVal = 0;
                            v.objDefVal = UInt64.Parse(v.defVal);
                        }
                        else if (v.type.Equals(s_sInt8))
                        {
                            v.objDefVal = 0;
                            v.objDefVal = SByte.Parse(v.defVal);
                        }
                        else if (v.type.Equals(s_sInt16))
                        {
                            v.objDefVal = 0;
                            v.objDefVal = Int16.Parse(v.defVal);
                        }
                        
                        else if (v.type.Equals(s_sInt64))
                        {
                            v.objDefVal = 0;
                            v.objDefVal = Int64.Parse(v.defVal);
                        }
                        else if (v.type.Equals(s_sDouble))
                        {
                            v.objDefVal = 0.0;
                            v.objDefVal = Double.Parse(v.defVal);
                        }
                        else if (v.type.Equals(s_sFloat))
                        {
                            v.objDefVal = 0.0;
                            v.objDefVal = Single.Parse(v.defVal);
                        }
                        else if (v.type.Equals(s_sBool))
                        {
                            v.objDefVal = false;
                            v.objDefVal = Boolean.Parse(v.defVal);
                        } 
                        else
                        {
                            var m = _luaEnv.Global.GetInPath<XLua.LuaTable>(v.type);
                            MessageLua self = m.Get<String, MessageLua>(s_sSelf);
                            objDefVal = self.Create();
                        }
                    }
                    catch (Exception e)
                    {
                        UnityEngine.Debug.LogException(e);
                    }
                }

                if (v.objDefVal != null)
                {
                    t.Set(v.name, v.objDefVal);
                }
                else if (objDefVal != null)
                {
                    t.Set(v.name, objDefVal);
                }
                
            }
            return t;
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

        public void Decode(XLua.LuaTable luaTable, BinaryReader stream)
        {
            var dictionary = new Dictionary<String, object>();
            foreach (var v in _attrs)
            {
                try
                {
                    if (v.type.Equals(s_sString))
                    {
                        String value = "";
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name,value);
                    }
                    else if (v.type.Equals(s_sInt32))
                    {
                        Int32 value = 0;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name,value);
                    }
                    else if (v.type.Equals(s_sUint32))
                    {
                        UInt32 value = 0;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name,value);
                    }
                    else if (v.type.Equals(s_sEnum))
                    {
                        Int32 value = 0;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name,value);
                    }
                    else if (v.type.Equals(s_sUint8))
                    {
                        UInt8 value = 0;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name,value);
                    }
                    else if (v.type.Equals(s_sUint16))
                    {
                        UInt16 value = 0;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name,value);
                    }
                    
                    else if (v.type.Equals(s_sUint64))
                    {
                        UInt64 value = 0;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name,value);
                    }
                    else if (v.type.Equals(s_sInt8))
                    {
                        Int8 value = 0;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name,value);
                    }
                    else if (v.type.Equals(s_sInt16))
                    {
                        Int16 value = 0;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name,value);
                    }
                    
                    else if (v.type.Equals(s_sInt64))
                    {
                        Int64 value = 0;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name,value);
                    }
                    else if (v.type.Equals(s_sDouble))
                    {
                        Double value = 0.0f;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name,value);
                    }
                    else if (v.type.Equals(s_sFloat))
                    {
                        Float value = 0.0f;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name,value);
                    }
                    else if (v.type.Equals(s_sBool))
                    {
                        Bool value = false;
                        doDeserialize(stream, ref value);
                        dictionary.Add(v.name,value);
                    }
                    else
                    {
                        var table = _luaEnv.Global.Get<XLua.LuaTable>(v.name);
                        var ml = table.Get<String, MessageLua>(s_sSelf);
                        ml.Decode(table, stream);
                    }
                }
                catch (Exception e)
                {
                    UnityEngine.Debug.LogException(e);
                }
            }

            luaTable.Set(dictionary);
        }

        public void Encode(XLua.LuaTable luaTable,BinaryWriter stream)
        {
            var dictionary = luaTable.Cast<Dictionary<String, object>>();
            foreach (var v in _attrs)
            {
                try
                {
                    if (v.type.Equals(s_sString))
                    {
                        doSerialize(stream,(String)dictionary[v.name]);
                    }
                    else if (v.type.Equals(s_sInt32))
                    {
                        doSerialize(stream, Convert.ToInt32(dictionary[v.name]));
                    }
                    else if (v.type.Equals(s_sUint32))
                    {
                        doSerialize(stream, Convert.ToUInt32(dictionary[v.name]));
                    }
                    else if (v.type.Equals(s_sEnum))
                    {
                        doSerialize(stream, Convert.ToInt32(dictionary[v.name]));
                    }
                    else if (v.type.Equals(s_sUint8))
                    {
                        doSerialize(stream, Convert.ToByte(dictionary[v.name]));
                    }
                    else if (v.type.Equals(s_sUint16))
                    {
                        doSerialize(stream, Convert.ToUInt16(dictionary[v.name]));
                    }
                    else if (v.type.Equals(s_sUint64))
                    {
                        doSerialize(stream, Convert.ToUInt64(dictionary[v.name]));
                    }
                    else if (v.type.Equals(s_sInt8))
                    {
                        doSerialize(stream, Convert.ToSByte(dictionary[v.name]));
                    }
                    else if (v.type.Equals(s_sInt16))
                    {
                        doSerialize(stream, Convert.ToInt16(dictionary[v.name]));
                    }
                    else if (v.type.Equals(s_sInt64))
                    {
                        doSerialize(stream, Convert.ToInt64(dictionary[v.name]));
                    }
                    else if (v.type.Equals(s_sDouble))
                    {
                        doSerialize(stream, Convert.ToDouble(dictionary[v.name]));
                    }
                    else if (v.type.Equals(s_sFloat))
                    {
                        doSerialize(stream, Convert.ToSingle(dictionary[v.name]));
                    }
                    else if (v.type.Equals(s_sBool))
                    {
                        doSerialize(stream, Convert.ToBoolean(dictionary[v.name]));
                    }
                    else
                    {
                        XLua.LuaTable table = (XLua.LuaTable)dictionary[v.name];
                        table.Get<String, MessageLua>(s_sSelf).Encode(table, stream);
                    }
                }
                catch (Exception e)
                {
                    UnityEngine.Debug.LogException(e);
                }
            }
        }
    }

    public class LocalMessage : Message
    {
        public XLua.LuaTable luaTable = null;

        public LocalMessage(XLua.LuaTable t)
        {
            luaTable = t;
        }

        public static UInt32 sClsId
        {
            get
            {
                return 394874348;
            }
        }
        public override UInt32 ClsId
        {
            get
            {
                return 394874348;
            }
        }
        public override String ClsName
        {
            get
            {
                return "FastNet.LocalMessage";
            }
        }
        public override UInt32 SignId
        {
            get
            {
                return 0;
            }
        }
        public static UInt32 sSignId
        {
            get
            {
                return 0;
            }
        }

        public override void Deserialize(BinaryReader stream)
        {
            var messageLua = luaTable.Get<MessageLua>(s_sSelf);
            messageLua.Decode(luaTable, stream);
        }

        public override void Serialize(BinaryWriter stream)
        {
            var messageLua = luaTable.Get<MessageLua>(s_sSelf);
            messageLua.Encode(luaTable, stream);
        }
    }
}
