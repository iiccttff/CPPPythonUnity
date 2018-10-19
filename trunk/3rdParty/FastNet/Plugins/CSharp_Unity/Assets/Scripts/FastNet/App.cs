using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using UnityEngine;
using XLua;
using System.Collections;

namespace FastNet
{
    public class App
    {
        private static Dictionary<UInt32, KeyValuePair<UInt32, ConstructorInfo>> s_messages = new Dictionary<UInt32, KeyValuePair<UInt32, ConstructorInfo>>();
        private static Dictionary<UInt32, MessageLua> s_lua_messages = new Dictionary<UInt32, MessageLua>();

        private static XLua.LuaEnv s_luaEnv = null;
        private static String s_workPath = null;


        public static Dictionary<UInt32, MessageLua> LuaMessages
        {
            get {
                return s_lua_messages;
            }
        }

        public static Dictionary<UInt32, KeyValuePair<UInt32, ConstructorInfo>> Messages
        {
            get
            {
                return s_messages;
            }
        }

        public static String WorkPath
        {
            get
            {
                return s_workPath;
            }
        }


        public static void RegisterMessage(object o, bool enableLua)
        {
            if (enableLua == false)
            {
                var t = (Type)o;
                PropertyInfo sClsId = t.GetProperty("sClsId", BindingFlags.Public | BindingFlags.Static);
                var clsId = (UInt32)sClsId.GetValue(null, null);

                PropertyInfo sSignId = t.GetProperty("sSignId", BindingFlags.Public | BindingFlags.Static);
                var signId = (UInt32)sSignId.GetValue(null, null);
                var constructor = t.GetConstructor(new Type[] { });
                s_messages[clsId] = new KeyValuePair<UInt32, ConstructorInfo>(signId, constructor);
            }
            else
            {
                var message = (MessageLua)o;
                s_lua_messages[message.ClsId] = message;
            }
        }


        public static void SetTable<T>(String k, T v)
        {
            var t = s_luaEnv.Global;
            var names = new List<String>(k.Split('.'));
            var name = names.Last();
            names.RemoveAt(names.Count - 1);
            foreach (var s in names)
            {
                var tt = t.Get<String, XLua.LuaTable>(s);
                if (tt == null)
                {
                    tt = s_luaEnv.NewTable();
                    t.Set<String, XLua.LuaTable>(s,tt );
                }

                t = tt;
            }

            t.Set(name, v);
        }


        public static void initialize(XLua.LuaEnv luaEnv = null)
        {
            
            try
            {
                s_workPath = System.IO.Path.Combine(Application.persistentDataPath, "FastNet");

                if (Directory.Exists(s_workPath) == false)
                {
                    Directory.CreateDirectory(s_workPath);
                }

                s_luaEnv = luaEnv;
                var types = Assembly.GetAssembly(typeof(App)).GetTypes();

                foreach (var type in types)
                {
                    try
                    {
                        var baseType = type.BaseType;
                        if (baseType != null)
                        {
                            if ("FastNet.Cfg`2".Equals(baseType.Namespace + "." + baseType.Name))
                            {
                                var method = type.GetMethod("Init", BindingFlags.Public | BindingFlags.Static);
                                method.Invoke(null, null);
                            }
                            else if ("FastNet.Message".Equals(baseType.Namespace + "." + baseType.Name))
                            {
                                RegisterMessage(type, false);
                            }
                        }
                    }
                    catch (Exception e)
                    {
                        UnityEngine.Debug.LogException(e);
                    }
                }

                if (luaEnv != null)
                {
                    //pkt
                    MessageLua.Load(s_workPath + "/pkt_table.bytes", luaEnv);

                    //cfg
                    CfgLua.Load(s_workPath + "/cfg_table.bytes", luaEnv);
                }
            }
            catch (Exception e)
            {
                Debug.LogException(e);
            }
        }


        public static void reload()
        {
            var types = Assembly.GetAssembly(typeof(App)).GetTypes();

            foreach (var type in types)
            {
                try
                {
                    var baseType = type.BaseType;
                    if (baseType != null)
                    {
                        if ("FastNet.Cfg`2".Equals(baseType.Namespace + "." + baseType.Name))
                        {
                            var method = type.GetMethod("Init", BindingFlags.Public | BindingFlags.Static);
                            method.Invoke(null, null);
                        }
                    }
                }
                catch (Exception e)
                {
                    UnityEngine.Debug.LogException(e);
                }
            }


            if (s_luaEnv != null)
            {
                //pkt
                MessageLua.Load(s_workPath + "/pkt_table.bytes", s_luaEnv);

                //cfg
                CfgLua.Load(s_workPath + "/cfg_table.bytes", s_luaEnv);
            }
        }


        public static void finalize()
        {
            s_messages.Clear();
            s_lua_messages.Clear();
            s_messages = null;
            s_lua_messages = null;
            s_luaEnv = null;
        }

        public static Dictionary<String, String> cacheMd5Values
        {
            get{
                try
                {
                    var ret = new Dictionary<String, String>();

                    var file = Path.Combine(FastNet.App.WorkPath, "version.bytes");
                    if (File.Exists(file))
                    {
                        var sr = File.OpenText(file);
                        var input = sr.ReadToEnd();
                        var jsonObjects = MiniJSON.MiniJSON.jsonDecode(input) as Hashtable;
                        sr.Close();

                        foreach (String v in jsonObjects.Keys)
                        {
                            ret[v] = (String)jsonObjects[v];
                        }
                    }

                    /*file = Path.Combine(FastNet.App.WorkPath, "pkt_version.bytes");
                    if (File.Exists(file))
                    {
                        var sr = File.OpenText(file);
                        var input = sr.ReadToEnd();
                        var jsonObjects = MiniJSON.MiniJSON.jsonDecode(input) as Hashtable;

                        foreach (String v in jsonObjects.Keys)
                        {
                            ret[v] = (String)jsonObjects[v];
                        }
                    }*/
                    
                    return ret;
                }
                catch (Exception e)
                {
                    UnityEngine.Debug.LogException(e);
                    return null;
                }
            }
            
        }
        


    }
}
