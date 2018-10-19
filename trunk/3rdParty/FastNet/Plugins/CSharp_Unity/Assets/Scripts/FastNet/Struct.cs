using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

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
    


    [System.Serializable]
    public class _PktAttr
    {
        public String name;
        public String type;
        public String value;
    }

    [System.Serializable]
    public class _PktStruct
    {
        public String clsName;
        public UInt32 clsId;
        public UInt32 signId;
        public String type;
        public String index;
        public _PktAttr[] attrs;
        public String cfgPath;
    }

    [System.Serializable]
    public class _PktStructList
    {
        public _PktStruct[] pkts;
    }



    public class Struct
    {
        public const String s_sUint8 = "UInt8";
        public const String s_sUint16 = "UInt16";
        public const String s_sUint32 = "UInt32";
        public const String s_sUint64 = "UInt64";
        public const String s_sInt8 = "Int8";
        public const String s_sInt16 = "Int16";
        public const String s_sInt32 = "Int32";
        public const String s_sInt64 = "Int64";
        public const String s_sDouble = "Double";
        public const String s_sFloat = "Float";
        public const String s_sBool = "Bool";
        public const String s_sString = "String";
        public const String s_sEnum = "Enum";
        public const String s_sSelf = "__self__";

        public virtual UInt32 ClsId
        {
            get
            {
                return 0;
            }
        }

        public virtual String ClsName
        {
            get
            {
                return "";
            }
        }

        public virtual UInt32 SignId
        {
            get
            {
                return 0;
            }
        }

        public virtual void Serialize(BinaryWriter stream)
        {

        }

        public virtual void Deserialize(BinaryReader stream)
        {

        }


        //List
        protected static void doSerialize<T>(BinaryWriter stream, List<T> arg)
        {
            UInt32 len = (UInt32)arg.Count;
            stream.Write(len);
            for (int i = 0; i < len; i++)
            {
                var t = arg[i];
                doSerialize(stream, t);
            }
        }

        protected static void doDeserialize(BinaryReader stream, ref List<String> arg)
        {
            var len = stream.ReadUInt32();
            arg.Capacity = (Int32)len;
            for (int i = 0; i < len; i++)
            {
                String s = "";
                doDeserialize(stream, ref s);
                arg.Add(s);
            }
        }

        protected static void doDeserialize<T>(BinaryReader stream, ref List<T> arg)
        {
            var len = stream.ReadUInt32();
            arg.Capacity = (Int32)len;
            for (int i = 0; i < len; i++)
            {
                T t = Activator.CreateInstance<T>();
                doDeserialize(stream, ref t);
                arg.Add(t);
            }
        }

        protected static void doDeserialize<T1, T2>(BinaryReader stream, ref Dictionary<T1, T2> arg)
        {
            bool t1IsStr = typeof(String) == typeof(T1);
            bool t2IsStr = typeof(String) == typeof(T2);

            var len = stream.ReadUInt32();
            for (int i = 0; i < len; i++)
            {
                var t1 = t1IsStr ? (T1)(object)String.Empty : Activator.CreateInstance<T1>();
                var t2 = t2IsStr ? (T2)(object)String.Empty : Activator.CreateInstance<T2>();

                doDeserialize(stream, ref t1);
                doDeserialize(stream, ref t2);
                arg.Add(t1, t2);
            }
        }

        protected static void doSerialize<T1, T2>(BinaryWriter stream, Dictionary<T1, T2> arg)
        {
            UInt32 len = (UInt32)arg.Count;
            stream.Write(len);
            foreach (var item in arg)
            {
                doSerialize(stream, item.Key);
                doSerialize(stream, item.Value);
            }
        }

        protected static void doSerialize<T>(BinaryWriter stream, T arg)
        {
            var tt = typeof(T);
            if (typeof(String) == tt)
            {
                var str = arg as String;
                var bytes = Encoding.UTF8.GetBytes(str);

                stream.Write((UInt32)bytes.Length);
                if (bytes.Length > 0)
                {
                    stream.Write(bytes);
                }

            }
            else if (tt.IsAssignableFrom(typeof(Struct)))
            {
                var message = arg as Struct;
                message.Serialize(stream);
            }
            else if (typeof(UInt8) == tt)
            {
                var value = (UInt8)(object)arg;
                stream.Write(value);
            }
            else if (typeof(UInt16) == tt)
            {
                var value = (UInt16)(object)arg;
                stream.Write(value);
            }
            else if (typeof(UInt32) == tt)
            {
                var value = (UInt32)(object)arg;
                stream.Write(value);
            }
            else if (typeof(UInt64) == tt)
            {
                var value = (UInt64)(object)arg;
                stream.Write(value);
            }
            else if (typeof(Int8) == tt)
            {
                var value = (Int8)(object)arg;
                stream.Write(value);
            }
            else if (typeof(Int16) == tt)
            {
                var value = (Int16)(object)arg;
                stream.Write(value);
            }
            else if (typeof(Int32) == tt)
            {
                var value = (Int32)(object)arg;
                stream.Write(value);
            }
            else if (typeof(Int64) == tt)
            {
                var value = (Int64)(object)arg;
                stream.Write(value);
            }
            else if (typeof(Boolean) == tt)
            {
                var value = (Bool)(object)arg;
                stream.Write(value);
            }
            else if (typeof(Float) == tt)
            {
                var value = (Float)(object)arg;
                stream.Write(value);
            }
            else if (typeof(Double) == tt)
            {
                var value = (Double)(object)arg;
                stream.Write(value);
            }
            else
            {
                var value = (Int32)(object)arg;
                stream.Write(value);
            }
        }


        protected static void doDeserialize<T>(BinaryReader stream, ref T arg)
        {
            var tt = typeof(T);

            if (typeof(String) == tt)
            {
                var len = stream.ReadUInt32();
                if (len > 0)
                {
                    var bytes = new byte[len];
                    stream.Read(bytes, 0, (int)len);
                    arg = (T)(object)Encoding.UTF8.GetString(bytes);
                }
                else
                {
                    arg = (T)(object)String.Empty;
                }
            }
            else if (tt.IsAssignableFrom(typeof(Struct)))
            {
                var message = arg as Struct;
                message.Deserialize(stream);
            }
            else if (typeof(UInt8) == tt)
            {
                var value = stream.ReadByte();
                arg = (T)(object)value;
            }
            else if (typeof(UInt16) == tt)
            {
                var value = stream.ReadUInt16();
                arg = (T)(object)value;
            }
            else if (typeof(UInt32) == tt)
            {
                var value = stream.ReadUInt32();
                arg = (T)(object)value;
            }
            else if (typeof(UInt64) == tt)
            {
                var value = stream.ReadUInt64();
                arg = (T)(object)value;
            }
            else if (typeof(Int8) == tt)
            {
                var value = stream.ReadSByte();
                arg = (T)(object)value;
            }
            else if (typeof(Int16) == tt)
            {
                var value = stream.ReadInt16();
                arg = (T)(object)value;
            }
            else if (typeof(Int32) == tt)
            {
                var value = stream.ReadInt32();
                arg = (T)(object)value;
            }
            else if (typeof(Int64) == tt)
            {
                var value = stream.ReadInt64();
                arg = (T)(object)value;
            }
            else if (typeof(Boolean) == tt)
            {
                var value = stream.ReadBoolean();
                arg = (T)(object)value;
            }
            else if (typeof(Float) == tt)
            {
                var value = stream.ReadSingle();
                arg = (T)(object)value;
            }
            else if (typeof(Double) == tt)
            {
                var value = stream.ReadDouble();
                arg = (T)(object)value;
            }
            else
            {
                var value = stream.ReadInt32();
                arg = (T)(object)value;
            }
        }
    }

}
