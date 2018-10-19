using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using XLua;
using System;
using MiniJSON;
using System.IO;

[LuaCallCSharp]
public class Main : MonoBehaviour {

    

    [CSharpCallLua]
    public delegate void LuaAction();

    public TextAsset luaScript;

    public static LuaEnv s_luaEnv = new LuaEnv();
    public LuaTable m_mainScriptEnv = s_luaEnv.NewTable();

    internal static float lastGCTime = 0;
    internal const float GCInterval = 1;//1 second 

    public FastNet.Client m_client = null;

    private LuaAction m_luaStart = null;
    private LuaAction m_luaUpdate = null;
    private LuaAction m_luaOnDestroy = null;

    IEnumerator AccountVerify()
    {

        byte[] buff;
        using (var md5 = new System.Security.Cryptography.MD5CryptoServiceProvider())
        {
            buff = md5.ComputeHash(System.Text.Encoding.UTF8.GetBytes("123456"));
        }
        var builder = new System.Text.StringBuilder();
        foreach (var item in buff)
        {
            builder.Append(item.ToString("x2").ToLower());
        }

        var verifyParams = new Dictionary<String, String>();
        verifyParams["username"] = "admin";
        verifyParams["password"] = builder.ToString();
        verifyParams["type"] = "client";

        String postData = MiniJSON.MiniJSON.jsonEncode(verifyParams);

        var headers = new Dictionary<string, string>();
        headers.Add("Content-Type", "application/json");
        headers.Add("Content-Length", postData.Length.ToString());

        var byteArray = System.Text.Encoding.UTF8.GetBytes(postData);
        WWW www = new WWW("http://127.0.0.1:18083/AccountVerify", byteArray, headers);
        yield return www;
        if (www.error != null)
        {
            Debug.LogError(www.error);
        }
        else
        {
            try
            {
                var j = MiniJSON.MiniJSON.jsonDecode(www.text) as Dictionary<String, object>;
                if ((UInt32)j["status"] == 1)
                {
                    verifyParams.Clear();
                    verifyParams["token"] = (String)j["token"];
                    m_client.AccountVerify("000", MiniJSON.MiniJSON.jsonEncode(verifyParams));
                }
                else
                {
                    Debug.LogError("帐号验证出错!");
                }
            }
            catch (Exception e)
            {
                Debug.LogException(e);
            }
        }
    }

    void OnEvent(FastNet.Event se, String msg)
    {
        if (se == FastNet.Event.kConnectSucceed)
        {
            
        }
        else if (se == FastNet.Event.kUpdateBegin){
            Debug.Log(se);
        }
        else if (se == FastNet.Event.kUpdateing){
            Debug.Log(String.Format("{0} {1}", se.ToString(), msg));
        }
        else if (se == FastNet.Event.kUpdateEnd){
            Debug.Log(se);
        }
    }

    void OnMessage(FastNet.Message message)
    {
        if (message.ClsId == pkt.protocols.ErrorMessage.sClsId)
        {
            var errorMessage = message as pkt.protocols.ErrorMessage;
            Debug.Log("OnErrorMessage key:" + errorMessage.key + " msg:" + errorMessage.msg);
        }
        else if (message.ClsId == pkt.protocols.RoleLoginRes.sClsId)
        {
            var roleLoginRes = message as pkt.protocols.RoleLoginRes;
            Debug.Log("OnRoleLoginRes roleId:" + roleLoginRes.roleId);

            var anyReq = new pkt.common.AnyReq();
            anyReq.data = "234234";
            anyReq.classId = 6666;
            m_client.SendRoomMessage(1000, roleLoginRes.roleId, anyReq);
        }
        else if (message.ClsId == pkt.common.AccountVerifySucceedRes.sClsId)
        {
            var accountVerifySucceedRes = message as pkt.common.AccountVerifySucceedRes;
            m_client.RoleLogin(accountVerifySucceedRes.roleId);
            Debug.Log("OnAccountVerifySucceedRes roleId:" + accountVerifySucceedRes.roleId);
        }
    }

    void OnRoomMessage(UInt32 roomId,String roleId,FastNet.Message message)
    {
        Debug.Log("OnRoomMessage roomId:" + roomId + " roleId:" + roleId);
    }

    void Awake()
    {
        FastNet.App.initialize(s_luaEnv);

        m_client = new FastNet.Client();
        m_client.OnMessage = OnMessage;
        m_client.OnRoomMessage = OnRoomMessage;
        m_client.OnEvent = OnEvent;

        LuaTable meta = s_luaEnv.NewTable();
        meta.Set("__index", s_luaEnv.Global);
        m_mainScriptEnv.SetMetaTable(meta);
        meta.Dispose();

        m_mainScriptEnv.Set("self", this);

        s_luaEnv.DoString(luaScript.text, "Main", m_mainScriptEnv);

        var luaAwake = m_mainScriptEnv.Get<LuaAction>("awake");
        m_mainScriptEnv.Get("start", out m_luaStart);
        m_mainScriptEnv.Get("update", out m_luaUpdate);
        m_mainScriptEnv.Get("ondestroy", out m_luaOnDestroy);

        if (luaAwake != null)
        {
            luaAwake();
        }
    }


	// Use this for initialization
	void Start () 
    {
        if (m_luaStart != null)
        {
            m_luaStart();
        }
	}

    void OnDestroy()
    {
        if (m_luaOnDestroy != null)
        {
            m_luaOnDestroy();
        }

        m_client.Close();
        m_client.OnEvent = null;
        m_client.OnMessage = null;
        m_client.OnRoomMessage = null;
        m_client = null;

        FastNet.App.finalize();

        m_luaOnDestroy = null;
        m_luaUpdate = null;
        m_luaStart = null;
        m_mainScriptEnv.Dispose();
        m_mainScriptEnv = null;
    }
	
	// Update is called once per frame
	void Update () 
    {
        if (m_luaUpdate != null)
        {
            m_luaUpdate();
        }

        if (Time.time - Main.lastGCTime > GCInterval)
        {
            s_luaEnv.Tick();
            Main.lastGCTime = Time.time;
        }

        m_client.Update();
	}
}
