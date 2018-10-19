using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Collections;
using UnityEngine;
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
    using System.Security.Cryptography;

    [XLua.LuaCallCSharp]
    public enum Event
    {
        kConnectSucceed,
        kConnectFailure,
        kConnectClosed,
        kReConnecting,
        kReConnectFailure,
        kErrorMessage,
        kCheckUpdate,
        kUpdateBegin,
        kUpdateing,
        kUpdateEnd,
    };

    [XLua.LuaCallCSharp]
    public class Client
    {
        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Ansi, Pack = 1)]
        private struct MessageHead
        {
            public UInt32 size;
            public UInt32 id;
            public UInt32 signatureId;
        }

        private class MessageInfo
        {
            public UInt32 roomId = 0;
            public String roleId;
            public Message message;
        }

        [XLua.BlackList]
        public static readonly int MessageHeadSize = Marshal.SizeOf(typeof(MessageHead));

        private enum Status
        {
            NoConnect = 1,
            UserClosed,
            Connecting,
            ConnectSucceed,
            ConnectFailure,
            ConnectClosed,
            ReConnecting,
            ReConnectFailure
        };



        private TcpClient m_client = null;
        private Thread m_thread = null;
        private Bool m_run = false;
        private Queue<Message> m_sendMessages = new Queue<Message>();
        private Queue<MessageInfo> m_recvMessages = new Queue<MessageInfo>();
        private Status m_status = Status.NoConnect;
        private Int32 m_timerHeartbeat = -1;
        private Int32 m_timerSendHeartbeat = -1;
        private Int32 m_timerReconnect = -1;

        private String m_server = "";
        private UInt16 m_port = 0;
        private UInt32 m_reconnectTime = 0;
        private UInt32 m_reconnectCount = 0;
        private UInt32 m_currentReconnectCount = 0;
        private UInt64 m_sessionId = 0;
        private UInt32 m_serverId = 0;
        private String m_deviceId = "";
        private String m_token = "";
        private String m_roleId = "";

        private MessageHead m_sendHead = new MessageHead();
        private MessageHead m_recvHead = new MessageHead();

        private IntPtr m_sendHeadBuffer = IntPtr.Zero;
        private IntPtr m_recvHeadBuffer = IntPtr.Zero;

        private Dictionary<UInt32, KeyValuePair<UInt32, ConstructorInfo>> m_messages = null;
        private Dictionary<UInt32, MessageLua> m_luaMessages = null;


        private class DownloadFile
        {
            public UInt32 size;
            public FileStream fs;

            public DownloadFile(String path,UInt32 v)
            {
                size = v;
                fs = new FileStream(path, FileMode.OpenOrCreate);
            }

            ~DownloadFile()
            {
                fs.Close();
            }
        }


        private Dictionary<String, DownloadFile> m_downloadFiles = new Dictionary<String, DownloadFile>();
        private UInt32 m_totalDownloadSize = 0;
        private UInt32 m_curDownloadSize = 0;
        private Dictionary<String, String> m_localMd5Values = new Dictionary<String, String>();
        private Dictionary<String, String> m_needUpdateFiles = new Dictionary<String, String>();

        private String m_md5Values = "";

        public Client()
        {
            m_messages = new Dictionary<UInt32, KeyValuePair<UInt32, ConstructorInfo>>(App.Messages);
            m_luaMessages = new Dictionary<UInt32, MessageLua>(App.LuaMessages);


            m_sendHeadBuffer = Marshal.AllocHGlobal(MessageHeadSize);
            m_recvHeadBuffer = Marshal.AllocHGlobal(MessageHeadSize);

            m_thread = new Thread(new ThreadStart(Run));
            m_run = true;
            m_thread.Start();


            m_deviceId = UnityEngine.SystemInfo.deviceUniqueIdentifier;
            m_deviceId += UnityEngine.SystemInfo.deviceModel;
            m_deviceId += UnityEngine.SystemInfo.deviceName;
            m_deviceId += UnityEngine.SystemInfo.deviceType.ToString();
            m_deviceId += UnityEngine.SystemInfo.graphicsDeviceID.ToString();
            m_deviceId += UnityEngine.SystemInfo.operatingSystem;
            m_deviceId += UnityEngine.SystemInfo.processorCount.ToString();
            m_deviceId += UnityEngine.SystemInfo.systemMemorySize.ToString();
            m_deviceId += UnityEngine.SystemInfo.graphicsMemorySize.ToString();

            byte[] buff;
            using (var md5 = new System.Security.Cryptography.MD5CryptoServiceProvider())
            {
                buff = md5.ComputeHash(Encoding.UTF8.GetBytes(m_deviceId));
            }
            var builder = new System.Text.StringBuilder();
            foreach (var item in buff)
            {
                builder.Append(item.ToString("x2").ToLower());
            }
            m_deviceId = builder.ToString();
        }



        ~Client()
        {
            if (m_thread.IsAlive)
            {
                m_run = false;
                m_thread.Join();
            }

            Marshal.FreeHGlobal(m_sendHeadBuffer);
            Marshal.FreeHGlobal(m_recvHeadBuffer);
        }


        public UInt32 ServerId
        {
            get
            {
                return m_serverId;
            }
        }

        public UInt64 SessionId
        {
            get
            {
                return m_sessionId;
            }
        }


        public void AccountVerify(String channel, String jsonData)
        {
            var accountVerifyReq = new pkt.protocols.AccountVerifyReq();
            accountVerifyReq.channel = channel;
            accountVerifyReq.jsonData = jsonData;
            this.SendMessage(accountVerifyReq);
        }

        public void RoleLogin(String roleId)
        {
            var roleLoginReq = new pkt.protocols.RoleLoginReq();
            roleLoginReq.roleId = roleId;
            this.SendMessage(roleLoginReq);
        }

        private void Run()
        {
            while (m_run)
            {
                Thread.Sleep(10);

                if (m_timerSendHeartbeat > 0)
                {
                    m_timerSendHeartbeat -= 10;
                    if (m_timerSendHeartbeat <= 0)
                    {
                        m_timerSendHeartbeat = 3000;
                        OnTimerSendHeartbeat();
                    }
                }

                if (m_timerHeartbeat > 0)
                {
                    m_timerHeartbeat -= 10;
                    if (m_timerHeartbeat <= 0)
                    {
                        OnTimerHeartbeat();
                    }
                }

                if (m_timerReconnect > 0)
                {
                    m_timerReconnect -= 10;
                    if (m_timerReconnect <= 0)
                    {
                        OnTimerReconnect();
                    }
                }

                switch (m_status)
                {
                    case Status.Connecting:
                        DoConnect(false);
                        break;
                    case Status.UserClosed:
                        DoClose("user close", false);
                        break;
                    case Status.ConnectSucceed:
                        {
                            Message message = null;

                            DoRecvMessage();

                            lock (m_sendMessages)
                            {
                                if (m_sendMessages.Count > 0)
                                {
                                    message = m_sendMessages.Dequeue();
                                }
                            }

                            if (message != null)
                            {
                                DoSendMessage(message);
                            }
                        }
                        break;
                }
            }
        }

        private void DoRecvMessage()
        {
            try
            {
                if (m_client.Available >= MessageHeadSize)
                {
                    var buffer = new byte[MessageHeadSize];
                    var stream = m_client.GetStream();
                    if (stream.Read(buffer, 0, MessageHeadSize) == MessageHeadSize)
                    {
                        Marshal.Copy(buffer, 0, m_recvHeadBuffer, MessageHeadSize);
                        m_recvHead = (MessageHead)Marshal.PtrToStructure(m_recvHeadBuffer, typeof(MessageHead));


                        KeyValuePair<UInt32, ConstructorInfo> ret;

                        MessageLua ret_lua = null;

                        if (m_messages.TryGetValue(m_recvHead.id, out ret) == false &&
                            m_luaMessages.TryGetValue(m_recvHead.id, out ret_lua) == false)
                        {
                            DispatchSocketEvent(Event.kErrorMessage, "no find message id:" + m_recvHead.id);
                            return;
                        }

                        Message message = null;
                        if (ret_lua != null)
                        {
                            if (ret_lua.SignId != m_recvHead.signatureId)
                            {
                                DispatchSocketEvent(Event.kErrorMessage, "signId check error,message id:" + m_recvHead.id);
                                return;
                            }

                            message = new FastNet.LocalMessage(ret_lua.Create());
                        }
                        else if (ret.Value != null)
                        {
                            if (ret.Key != m_recvHead.signatureId)
                            {
                                DispatchSocketEvent(Event.kErrorMessage, "signId check error,message id:" + m_recvHead.id);
                                return;
                            }


                            message = ret.Value.Invoke(new object[] { }) as Message;
                        }


                        if (m_recvHead.size > 0)
                        {
                            buffer = new byte[m_recvHead.size];
                            if (stream.Read(buffer, 0, (int)m_recvHead.size) != m_recvHead.size)
                            {
                                DoClose("recv size error,message id:" + m_recvHead.id, true);
                                return;
                            }

                            var memoryStream = new MemoryStream(buffer);
                            var binaryReader = new BinaryReader(memoryStream);
                            message.Deserialize(binaryReader);

                            binaryReader.Close();
                            memoryStream.Close();
                        }

                        if (message != null && message.ClsId != pkt.protocols.SocketHeartbeat.sClsId)
                        {
                            if (message.ClsId == pkt.protocols.RoomMessageRes.sClsId)
                            {

                                var roomMessageRes = (pkt.protocols.RoomMessageRes)message;
                                KeyValuePair<UInt32, ConstructorInfo> ret_roomMessage;
                                MessageLua ret_luaRoomMessage = null;

                                if (false == m_messages.TryGetValue(roomMessageRes.clsId, out ret_roomMessage) &&
                                    m_luaMessages.TryGetValue(roomMessageRes.clsId, out ret_luaRoomMessage) == false)
                                {
                                    DispatchSocketEvent(Event.kErrorMessage, "no find room message id:" + roomMessageRes.clsId);
                                }
                                else
                                {
                                    Message roomMessage = null;
                                    if (ret_lua != null)
                                    {
                                        if (ret_lua.SignId != m_recvHead.signatureId)
                                        {
                                            DispatchSocketEvent(Event.kErrorMessage, "signId check error,room message id:" + roomMessageRes.clsId);
                                            return;
                                        }

                                        roomMessage = new FastNet.LocalMessage(ret_luaRoomMessage.Create());
                                    }
                                    else if (ret.Value != null)
                                    {
                                        if (ret.Key != m_recvHead.signatureId)
                                        {
                                            DispatchSocketEvent(Event.kErrorMessage, "signId check error,room message id:" + roomMessageRes.clsId);
                                            return;
                                        }

                                        roomMessage = ret_roomMessage.Value.Invoke(new object[] { }) as Message;
                                    }

                                    if (roomMessageRes.data.Length > 0)
                                    {
                                        byte[] byteArray = System.Text.Encoding.Default.GetBytes(roomMessageRes.data);
                                        var memoryStream = new MemoryStream(byteArray);
                                        var binaryReader = new BinaryReader(memoryStream);
                                        message.Deserialize(binaryReader);
                                        binaryReader.Close();
                                        memoryStream.Close();
                                    }

                                    lock (m_recvMessages)
                                    {
                                        var mi = new MessageInfo();
                                        mi.message = roomMessage;
                                        mi.roleId = roomMessageRes.roleId;
                                        mi.roomId = roomMessageRes.roomId;
                                        m_recvMessages.Enqueue(mi);
                                    }

                                }
                            }
                            else if (message.ClsId == pkt.protocols.SocketConnect.sClsId)
                            {
                                var socketConnect = (pkt.protocols.SocketConnect)message;
                                m_serverId = socketConnect.serverId;
                                m_sessionId = socketConnect.sessionId;

                                lock (m_md5Values)
                                {
                                    m_md5Values = socketConnect.md5Values;
                                }
                                DispatchSocketEvent(Event.kCheckUpdate, "");
                            }
                            else
                            {
                                lock (m_recvMessages)
                                {
                                    var mi = new MessageInfo();
                                    mi.message = message;
                                    m_recvMessages.Enqueue(mi);
                                }
                            }
                        }

                        m_timerHeartbeat = 10000;
                    }
                }
            }
            catch (Exception e)
            {
                DoClose(e.ToString(), true);
            }
        }

        private void DoClose(String msg, bool reconnect)
        {
            if (m_client != null)
            {
                if (m_client.Connected)
                {
                    DoSendMessage(new pkt.protocols.SocketClose());
                }

                m_client.Close();
            }

            m_timerHeartbeat = -1;
            m_timerSendHeartbeat = -1;

            m_roleId = "";
            m_token = "";

            if (reconnect && m_reconnectCount > 0)
            {
                if (m_currentReconnectCount >= m_reconnectCount)
                {
                    m_status = Status.ReConnectFailure;
                    DispatchSocketEvent(Event.kReConnectFailure, msg);
                }
                else
                {
                    m_timerReconnect = (Int32)m_reconnectTime;

                    m_currentReconnectCount++;

                    m_reconnectTime += 2000;
                    if (m_reconnectTime > 45000)
                    {
                        m_reconnectTime = 45000;
                    }

                    m_status = Status.ReConnecting;
                    DispatchSocketEvent(Event.kReConnecting, msg);
                }
            }
            else
            {
                m_timerReconnect = -1;
                m_status = Status.ConnectClosed;
                DispatchSocketEvent(Event.kConnectClosed, msg);
            }
        }


        private void DoSendMessage(Message message)
        {
            try
            {
                var memoryStream = new System.IO.MemoryStream();
                var binaryWriter = new System.IO.BinaryWriter(memoryStream, Encoding.ASCII);

                if (message.ClsId == FastNet.LocalMessage.sClsId)
                {
                    var localMessage = (FastNet.LocalMessage)message;
                    m_sendHead.id = localMessage.luaTable.Get<String, UInt32>("ClsId");
                    m_sendHead.signatureId = localMessage.luaTable.Get<String, UInt32>("SignId");
                }
                else
                {
                    m_sendHead.id = message.ClsId;
                    m_sendHead.signatureId = message.SignId;
                }

                message.Serialize(binaryWriter);

                binaryWriter.Flush();
                memoryStream.Flush();

                memoryStream.Position = 0;

                m_sendHead.size = (UInt32)memoryStream.Length;

                var buffer = new byte[MessageHeadSize + memoryStream.Length];

                memoryStream.Read(buffer, MessageHeadSize, (int)memoryStream.Length);

                binaryWriter.Close();
                memoryStream.Close();

                Marshal.StructureToPtr(m_sendHead, m_sendHeadBuffer, false);
                Marshal.Copy(m_sendHeadBuffer, buffer, 0, MessageHeadSize);
                m_client.GetStream().Write(buffer, 0, buffer.Length);
            }
            catch (Exception e)
            {
                if ((message is pkt.protocols.SocketClose) == false)
                {
                    DoClose(e.ToString(), true);
                }
            }
        }

        public bool IsConnect
        {
            get
            {
                if (m_status == Status.ConnectSucceed)
                {
                    return true;
                }

                return false;
            }
        }

        [XLua.BlackList]
        public void SendMessage(Message message)
        {
            if (!this.IsConnect)
            {
                UnityEngine.Debug.LogError("SendMessage this.IsConnect == False");
                return;
            }

            lock (m_sendMessages)
            {
                m_sendMessages.Enqueue(message);
            }
        }

        public void SendMessage(XLua.LuaTable message)
        {
            if (!this.IsConnect)
            {
                UnityEngine.Debug.LogError("SendMessage this.IsConnect == False");
                return;
            }

            lock (m_sendMessages)
            {
                var luaMessage = new FastNet.LocalMessage(message);
                m_sendMessages.Enqueue(luaMessage);
            }
        }

        [XLua.BlackList]
        public void SendRoomMessage(UInt32 roomId, String roleId, Message message)
        {
            if (!this.IsConnect)
            {
                UnityEngine.Debug.LogError("SendRoomMessage this.IsConnect == False");
                return;
            }

            if (m_roleId.Length == 0)
            {
                UnityEngine.Debug.LogError("SendRoomMessage message:" + message.ClsName + " m_roleId == empty");
                return;
            }

            var roomMessageReq = new pkt.protocols.RoomMessageReq();
            roomMessageReq.clsId = message.ClsId;
            roomMessageReq.roomId = roomId;
            roomMessageReq.roleId = roleId;
            roomMessageReq.signId = message.SignId;

            try
            {
                var memoryStream = new System.IO.MemoryStream();
                var binaryWriter = new System.IO.BinaryWriter(memoryStream, Encoding.ASCII);
                message.Serialize(binaryWriter);
                binaryWriter.Flush();

                roomMessageReq.data = System.Text.Encoding.ASCII.GetString(memoryStream.ToArray());

                binaryWriter.Close();
                memoryStream.Close();

                lock (m_sendMessages)
                {
                    m_sendMessages.Enqueue(roomMessageReq);
                }
            }
            catch (Exception e)
            {
                UnityEngine.Debug.LogException(e);
            }
        }

        public void SendRoomMessage(UInt32 roomId, String roleId, XLua.LuaTable message)
        {
            if (!this.IsConnect)
            {
                UnityEngine.Debug.LogError("SendRoomMessage this.IsConnect == False");
                return;
            }
            var luaMessage = new FastNet.LocalMessage(message);
            var roomMessageReq = new pkt.protocols.RoomMessageReq();
            roomMessageReq.clsId = luaMessage.luaTable.Get<String, UInt32>("ClsId");
            roomMessageReq.roomId = roomId;
            roomMessageReq.roleId = roleId;
            roomMessageReq.signId = luaMessage.luaTable.Get<String, UInt32>("SignId");

            try
            {
                var memoryStream = new System.IO.MemoryStream();
                var binaryWriter = new System.IO.BinaryWriter(memoryStream, Encoding.ASCII);
                luaMessage.Serialize(binaryWriter);
                binaryWriter.Flush();

                roomMessageReq.data = Encoding.ASCII.GetString(memoryStream.ToArray());

                binaryWriter.Close();
                memoryStream.Close();

                lock (m_sendMessages)
                {
                    m_sendMessages.Enqueue(roomMessageReq);
                }
            }
            catch (Exception e)
            {
                UnityEngine.Debug.LogException(e);
            }
        }

        public void Update(){
            MessageInfo mi = null;
            lock (m_recvMessages){
                if (m_recvMessages.Count > 0){
                    mi = m_recvMessages.Dequeue();
                }
            }

            if (mi != null)
            {
                if (mi.roomId == 0)
                {
                    if (mi.message.ClsId == pkt.protocols.LocalSocketEvent.sClsId)
                    {
                        var localSocketEvent = (pkt.protocols.LocalSocketEvent)mi.message;

                        _OnEvent((Event)localSocketEvent.evt, localSocketEvent.info);
                    }
                    else if (mi.message.ClsId == LocalMessage.sClsId)
                    {
                        if (OnLuaMessage != null)
                        {
                            var luaMessage = (LocalMessage)mi.message;
                            OnLuaMessage(luaMessage.luaTable);
                        }
                    }
                    else
                    {
                        _OnMessage(mi.message);
                    }
                }
                else
                {
                    if (mi.message.ClsId == LocalMessage.sClsId)
                    {
                        if (OnLuaRoomMessage != null)
                        {
                            var luaMessage = (LocalMessage)mi.message;
                            OnLuaRoomMessage(mi.roomId, mi.roleId,luaMessage.luaTable);
                        }
                    }
                    else
                    {
                        if (OnRoomMessage != null)
                        {
                            OnRoomMessage(mi.roomId, mi.roleId, mi.message);
                        }
                    }
                }  
            }
        }


        private void _OnMessage(Message message)
        {
            if (message.ClsId == pkt.protocols.RoleLoginRes.sClsId)
            {
                var roleLoginRes = (pkt.protocols.RoleLoginRes)message;
                m_roleId = roleLoginRes.roleId;
                m_token = roleLoginRes.token;
            }
            else if (message.ClsId == pkt.protocols.DownloadFileListRes.sClsId)
            {
                var downloadFileListRes = (pkt.protocols.DownloadFileListRes)message;
                m_downloadFiles.Clear();
                m_totalDownloadSize = 0;
                m_curDownloadSize = 0;

                foreach (var v in downloadFileListRes.files)
                {
                    var file = Path.Combine(App.WorkPath, v.Key);
                    var path = Path.GetDirectoryName(file);

                    if (Directory.Exists(path) == false)
                    {
                        Directory.CreateDirectory(path);
                    }

                    m_downloadFiles.Add(v.Key, new DownloadFile(file, v.Value));
                    m_totalDownloadSize += v.Value;
                }

                DispatchSocketEvent(Event.kUpdateBegin, "");
            }   
            else if (message.ClsId == pkt.protocols.DownloadFileRes.sClsId)
            {
                var downloadFileRes = (pkt.protocols.DownloadFileRes)message;

                m_curDownloadSize += (UInt32)downloadFileRes.data.Count;

                DownloadFile df;
                if (m_downloadFiles.TryGetValue(downloadFileRes.file,out df))
                {
                    df.fs.Write(downloadFileRes.data.ToArray<UInt8>(), (int)downloadFileRes.indexPart, downloadFileRes.data.Count);
                    if (df.size == downloadFileRes.indexPart + downloadFileRes.data.Count)
                    {
                        df.fs.Close();
                        m_downloadFiles.Remove(downloadFileRes.file);

                        String md5Value;
                        if (m_needUpdateFiles.TryGetValue(downloadFileRes.file,out md5Value))
                        {
                            m_localMd5Values[downloadFileRes.file] = md5Value;
                        }
                    }
                }

                if (m_totalDownloadSize > 0)
                {
                    var updateProgress = ((Double)m_curDownloadSize / (Double)m_totalDownloadSize) * 100;
                    DispatchSocketEvent(Event.kUpdateing, updateProgress.ToString("#.#"));
                }

                if (m_downloadFiles.Count < 1)
                {
                    try
                    {
                        var fileVersion = Path.Combine(App.WorkPath, "version.bytes");
                        FileStream fs = new FileStream(fileVersion, FileMode.OpenOrCreate);
                        var jsonString = MiniJSON.MiniJSON.jsonEncode(m_localMd5Values);
                        fs.Write(Encoding.ASCII.GetBytes(jsonString.ToCharArray()), 0, jsonString.Length);
                        fs.Close();
                    }
                    catch (Exception e)
                    {
                        Debug.LogException(e);
                    }

                    App.reload();

                    DispatchSocketEvent(Event.kUpdateEnd, "");
                    DispatchSocketEvent(Event.kConnectSucceed, "connect succeed!");
                }
            } 

            if (OnMessage != null)
            {
                OnMessage(message);
            }
        }


        private void _OnEvent(Event evt, String msg)
        {
            if (evt == Event.kCheckUpdate)
            {
                String md5ValueStr = "";
                lock (m_md5Values)
                {
                    md5ValueStr = m_md5Values;
                }

                try
                {
                    if (md5ValueStr.Length > 0)
                    {
                        var jsonObjects = MiniJSON.MiniJSON.jsonDecode(md5ValueStr) as Hashtable;

                        m_localMd5Values = App.cacheMd5Values;

                        foreach (String v in jsonObjects.Keys)
                        {
                            var md5Value = (String)jsonObjects[v];

                            String v1;
                            if (m_localMd5Values.TryGetValue(v, out v1) && v1.Equals(md5Value))
                            {
                                continue;
                            }

                            m_needUpdateFiles.Add(v, md5Value);
                        }


                        var removeKeys = new List<String>();

                        foreach (String v in m_localMd5Values.Keys)
                        {
                            if (!jsonObjects.ContainsKey(v))
                            {
                                var file = Path.Combine(FastNet.App.WorkPath, v);
                                if (File.Exists(file))
                                {
                                    File.Delete(file);
                                }

                                removeKeys.Add(v);
                            }
                        }

                        foreach (var v in removeKeys)
                        {
                            m_localMd5Values.Remove(v);
                        }

                        if (m_needUpdateFiles.Count > 0)
                        {
                            var downloadFileListReq = new pkt.protocols.DownloadFileListReq();
                            foreach (var v in m_needUpdateFiles)
                            {
                                downloadFileListReq.files.Add(v.Key);
                            }
                            SendMessage(downloadFileListReq);
                            return;
                        }
                    }

                    
                }
                catch (Exception e)
                {
                    UnityEngine.Debug.LogException(e);
                }

                DispatchSocketEvent(Event.kConnectSucceed, "connect succeed!");
            }

            if (OnEvent != null)
            {
                OnEvent((Event)evt, msg);
            }

            if (OnLuaEvent != null)
            {
                OnLuaEvent((Event)evt, msg);
            }
        }


        private void OnTimerHeartbeat()
        {
            DoClose("heartbeat timeout!", true);
        }

        private void OnTimerSendHeartbeat()
        {
            DoSendMessage(new pkt.protocols.SocketHeartbeat());
        }

        private void OnTimerReconnect()
        {
            DoConnect(true);
        }

        private void DispatchSocketEvent(Event e, String msg)
        {
            lock (m_recvMessages)
            {
                var message = new pkt.protocols.LocalSocketEvent();
                message.evt = (UInt8)e;
                message.info = msg;
                var mi = new MessageInfo();
                mi.message = message;
                m_recvMessages.Enqueue(mi);
            }
        }

        public void Close()
        {
            m_status = Status.UserClosed;
        }

        [XLua.BlackList]
        public delegate void DelegateEvent(Event se, String msg);

        [XLua.BlackList]
        public delegate void DelegateMessage(Message message);

        [XLua.BlackList]
        public delegate void DelegateRoomMessage(UInt32 roomId, String roleId, Message message);

        [XLua.CSharpCallLua]
        public delegate void DelegateEventLua(Event se, String msg);

        [XLua.CSharpCallLua]
        public delegate void DelegateMessageLua(XLua.LuaTable message);

        [XLua.CSharpCallLua]
        public delegate void DelegateRoomMessageLua(UInt32 roomId, String roleId, XLua.LuaTable message);

        [XLua.BlackList]
        public DelegateEvent OnEvent;

        [XLua.BlackList]
        public DelegateMessage OnMessage;

        [XLua.BlackList]
        public DelegateRoomMessage OnRoomMessage;

        public DelegateEventLua OnLuaEvent;
        public DelegateMessageLua OnLuaMessage;
        public DelegateRoomMessageLua OnLuaRoomMessage;

        private void DoConnect(bool reconnect)
        {
            try
            {
                m_client = new TcpClient();
                //m_client.Connect(m_server, m_port);

                IAsyncResult result = m_client.BeginConnect(m_server, m_port, null, null);
                var success = result.AsyncWaitHandle.WaitOne(TimeSpan.FromMilliseconds(10000));
                if (success)
                {
                    m_client.ReceiveTimeout = 10000;
                    m_client.SendTimeout = 10000;

                    m_currentReconnectCount = 0;

                    m_timerHeartbeat = 10000;
                    m_timerSendHeartbeat = 3000;
                    m_timerReconnect = -1;

                    m_currentReconnectCount = 0;
                    m_reconnectTime = 800;

                    m_status = Status.ConnectSucceed;

                    var socketConnectReq = new pkt.protocols.SocketConnectReq();
                    socketConnectReq.deviceId = m_deviceId;
                    //socketConnectReq.reconnect = reconnect;
                    //socketConnectReq.token = m_token;
                    SendMessage(socketConnectReq);
                }
                else
                {
                    DoClose("connect failure!", true);
                }
            }
            catch (Exception e)
            {
                DoClose(e.ToString(), true);
                return;
            }
        }

        public void Connect(String server, UInt16 port)
        {
            if (m_status == Status.NoConnect ||
                m_status == Status.ConnectFailure ||
                m_status == Status.ReConnectFailure)
            {

                m_status = Status.Connecting;
                m_server = server;
                m_port = port;

                m_reconnectCount = 0;

                m_currentReconnectCount = 0;
                m_reconnectTime = 800;
            }
        }


    }
}
