using System;
using System.IO;
using System.Collections.Generic;


namespace pkt{
namespace protocols{

using UInt8 = Byte;
using Int8 = SByte;
using Float = Single;
using Bool = Boolean;
	public class LogInfo : FastNet.Struct {
		public static UInt32 sClsId{
			get{
				return 956022818;
			}
		}
		public override UInt32 ClsId{
			get{
				return 956022818;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.LogInfo";
			}
		}
		public override UInt32 SignId{
			get{
				return 1733085687;
			}
		}
		public static UInt32 sSignId{
			get{
				return 1733085687;
			}
		}

		public String key="";
		public String log="";
		public UInt32 time=0;

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref key);
			doDeserialize (stream,ref log);
			doDeserialize (stream,ref time);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,key);
			doSerialize (stream,log);
			doSerialize (stream,time);
		}
	}
	public class ErrorMessage : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 3011211716;
			}
		}
		public override UInt32 ClsId{
			get{
				return 3011211716;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.ErrorMessage";
			}
		}
		public override UInt32 SignId{
			get{
				return 3742882662;
			}
		}
		public static UInt32 sSignId{
			get{
				return 3742882662;
			}
		}

		public String key="";
		public String msg="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref key);
			doDeserialize (stream,ref msg);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,key);
			doSerialize (stream,msg);
		}
	}
	public class AccountVerifyReq : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 2110615719;
			}
		}
		public override UInt32 ClsId{
			get{
				return 2110615719;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.AccountVerifyReq";
			}
		}
		public override UInt32 SignId{
			get{
				return 3742882662;
			}
		}
		public static UInt32 sSignId{
			get{
				return 3742882662;
			}
		}

		public String channel="";
		public String jsonData="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref channel);
			doDeserialize (stream,ref jsonData);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,channel);
			doSerialize (stream,jsonData);
		}
	}
	public class RoleLoginReq : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 27255320;
			}
		}
		public override UInt32 ClsId{
			get{
				return 27255320;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.RoleLoginReq";
			}
		}
		public override UInt32 SignId{
			get{
				return 2568140703;
			}
		}
		public static UInt32 sSignId{
			get{
				return 2568140703;
			}
		}

		public String roleId="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref roleId);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,roleId);
		}
	}
	public class RoleLoginRes : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 4019290932;
			}
		}
		public override UInt32 ClsId{
			get{
				return 4019290932;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.RoleLoginRes";
			}
		}
		public override UInt32 SignId{
			get{
				return 3742882662;
			}
		}
		public static UInt32 sSignId{
			get{
				return 3742882662;
			}
		}

		public String roleId="";
		public String token="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref roleId);
			doDeserialize (stream,ref token);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,roleId);
			doSerialize (stream,token);
		}
	}
	public class UpdateRoleTokenRes : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 2169161796;
			}
		}
		public override UInt32 ClsId{
			get{
				return 2169161796;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.UpdateRoleTokenRes";
			}
		}
		public override UInt32 SignId{
			get{
				return 2568140703;
			}
		}
		public static UInt32 sSignId{
			get{
				return 2568140703;
			}
		}

		public String token="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref token);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,token);
		}
	}
	public class RoleReconnectReq : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 589866478;
			}
		}
		public override UInt32 ClsId{
			get{
				return 589866478;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.RoleReconnectReq";
			}
		}
		public override UInt32 SignId{
			get{
				return 3742882662;
			}
		}
		public static UInt32 sSignId{
			get{
				return 3742882662;
			}
		}

		public String roleId="";
		public String token="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref roleId);
			doDeserialize (stream,ref token);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,roleId);
			doSerialize (stream,token);
		}
	}
	public class SocketHeartbeat : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 890548039;
			}
		}
		public override UInt32 ClsId{
			get{
				return 890548039;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.SocketHeartbeat";
			}
		}
		public override UInt32 SignId{
			get{
				return 215971539;
			}
		}
		public static UInt32 sSignId{
			get{
				return 215971539;
			}
		}

		public UInt32 time=0;

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref time);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,time);
		}
	}
	public class SocketClose : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 4256359424;
			}
		}
		public override UInt32 ClsId{
			get{
				return 4256359424;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.SocketClose";
			}
		}
		public override UInt32 SignId{
			get{
				return 0;
			}
		}
		public static UInt32 sSignId{
			get{
				return 0;
			}
		}


	}
	public class PublishReq : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 2355507917;
			}
		}
		public override UInt32 ClsId{
			get{
				return 2355507917;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.PublishReq";
			}
		}
		public override UInt32 SignId{
			get{
				return 752654989;
			}
		}
		public static UInt32 sSignId{
			get{
				return 752654989;
			}
		}

		public Bool isPublic=false;
		public String message="";
		public UInt32 id=0;

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref isPublic);
			doDeserialize (stream,ref message);
			doDeserialize (stream,ref id);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,isPublic);
			doSerialize (stream,message);
			doSerialize (stream,id);
		}
	}
	public class PublishRes : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 1651004385;
			}
		}
		public override UInt32 ClsId{
			get{
				return 1651004385;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.PublishRes";
			}
		}
		public override UInt32 SignId{
			get{
				return 752654989;
			}
		}
		public static UInt32 sSignId{
			get{
				return 752654989;
			}
		}

		public Bool isPublic=false;
		public String message="";
		public UInt32 id=0;

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref isPublic);
			doDeserialize (stream,ref message);
			doDeserialize (stream,ref id);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,isPublic);
			doSerialize (stream,message);
			doSerialize (stream,id);
		}
	}
	public class SubscribeReq : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 2884920292;
			}
		}
		public override UInt32 ClsId{
			get{
				return 2884920292;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.SubscribeReq";
			}
		}
		public override UInt32 SignId{
			get{
				return 215971539;
			}
		}
		public static UInt32 sSignId{
			get{
				return 215971539;
			}
		}

		public UInt32 id=0;

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref id);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,id);
		}
	}
	public class SubscribeRes : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 1174012616;
			}
		}
		public override UInt32 ClsId{
			get{
				return 1174012616;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.SubscribeRes";
			}
		}
		public override UInt32 SignId{
			get{
				return 215971539;
			}
		}
		public static UInt32 sSignId{
			get{
				return 215971539;
			}
		}

		public UInt32 id=0;

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref id);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,id);
		}
	}
	public class UnsubscribeReq : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 2796758889;
			}
		}
		public override UInt32 ClsId{
			get{
				return 2796758889;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.UnsubscribeReq";
			}
		}
		public override UInt32 SignId{
			get{
				return 215971539;
			}
		}
		public static UInt32 sSignId{
			get{
				return 215971539;
			}
		}

		public UInt32 id=0;

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref id);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,id);
		}
	}
	public class UnsubscribeRes : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 1220363845;
			}
		}
		public override UInt32 ClsId{
			get{
				return 1220363845;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.UnsubscribeRes";
			}
		}
		public override UInt32 SignId{
			get{
				return 215971539;
			}
		}
		public static UInt32 sSignId{
			get{
				return 215971539;
			}
		}

		public UInt32 id=0;

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref id);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,id);
		}
	}
	public class LocalSocketEvent : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 1714455482;
			}
		}
		public override UInt32 ClsId{
			get{
				return 1714455482;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.LocalSocketEvent";
			}
		}
		public override UInt32 SignId{
			get{
				return 2634531576;
			}
		}
		public static UInt32 sSignId{
			get{
				return 2634531576;
			}
		}

		public String info="";
		public UInt8 evt=0;

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref info);
			doDeserialize (stream,ref evt);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,info);
			doSerialize (stream,evt);
		}
	}
	public class SocketConnect : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 3867250737;
			}
		}
		public override UInt32 ClsId{
			get{
				return 3867250737;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.SocketConnect";
			}
		}
		public override UInt32 SignId{
			get{
				return 2040317094;
			}
		}
		public static UInt32 sSignId{
			get{
				return 2040317094;
			}
		}

		public UInt32 sessionId=0;
		public UInt32 serverId=0;
		public String md5Values="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref sessionId);
			doDeserialize (stream,ref serverId);
			doDeserialize (stream,ref md5Values);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,sessionId);
			doSerialize (stream,serverId);
			doSerialize (stream,md5Values);
		}
	}
	public class SocketConnectReq : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 1638288233;
			}
		}
		public override UInt32 ClsId{
			get{
				return 1638288233;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.SocketConnectReq";
			}
		}
		public override UInt32 SignId{
			get{
				return 4068542651;
			}
		}
		public static UInt32 sSignId{
			get{
				return 4068542651;
			}
		}

		public String deviceId="";
		public String subscribeKey="";
		public String token="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref deviceId);
			doDeserialize (stream,ref subscribeKey);
			doDeserialize (stream,ref token);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,deviceId);
			doSerialize (stream,subscribeKey);
			doSerialize (stream,token);
		}
	}
	public class RoomMessageReq : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 2621212155;
			}
		}
		public override UInt32 ClsId{
			get{
				return 2621212155;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.RoomMessageReq";
			}
		}
		public override UInt32 SignId{
			get{
				return 3516244101;
			}
		}
		public static UInt32 sSignId{
			get{
				return 3516244101;
			}
		}

		public UInt32 roomId=0;
		public String roleId="";
		public UInt32 clsId=0;
		public UInt32 signId=0;
		public String data="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref roomId);
			doDeserialize (stream,ref roleId);
			doDeserialize (stream,ref clsId);
			doDeserialize (stream,ref signId);
			doDeserialize (stream,ref data);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,roomId);
			doSerialize (stream,roleId);
			doSerialize (stream,clsId);
			doSerialize (stream,signId);
			doSerialize (stream,data);
		}
	}
	public class RoomMessageRes : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 1915938007;
			}
		}
		public override UInt32 ClsId{
			get{
				return 1915938007;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.RoomMessageRes";
			}
		}
		public override UInt32 SignId{
			get{
				return 3516244101;
			}
		}
		public static UInt32 sSignId{
			get{
				return 3516244101;
			}
		}

		public UInt32 roomId=0;
		public String roleId="";
		public UInt32 clsId=0;
		public UInt32 signId=0;
		public String data="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref roomId);
			doDeserialize (stream,ref roleId);
			doDeserialize (stream,ref clsId);
			doDeserialize (stream,ref signId);
			doDeserialize (stream,ref data);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,roomId);
			doSerialize (stream,roleId);
			doSerialize (stream,clsId);
			doSerialize (stream,signId);
			doSerialize (stream,data);
		}
	}
	public class DownloadFileListReq : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 3892002974;
			}
		}
		public override UInt32 ClsId{
			get{
				return 3892002974;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.DownloadFileListReq";
			}
		}
		public override UInt32 SignId{
			get{
				return 3204821990;
			}
		}
		public static UInt32 sSignId{
			get{
				return 3204821990;
			}
		}

		public List<String> files=new List<String>();

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref files);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,files);
		}
	}
	public class DownloadFileListRes : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 167059890;
			}
		}
		public override UInt32 ClsId{
			get{
				return 167059890;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.DownloadFileListRes";
			}
		}
		public override UInt32 SignId{
			get{
				return 2638689951;
			}
		}
		public static UInt32 sSignId{
			get{
				return 2638689951;
			}
		}

		public Dictionary<String,UInt32> files=new Dictionary<String,UInt32>();

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref files);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,files);
		}
	}
	public class DownloadFileRes : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 905004720;
			}
		}
		public override UInt32 ClsId{
			get{
				return 905004720;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.DownloadFileRes";
			}
		}
		public override UInt32 SignId{
			get{
				return 720761691;
			}
		}
		public static UInt32 sSignId{
			get{
				return 720761691;
			}
		}

		public String file="";
		public List<UInt8> data=new List<UInt8>();
		public UInt32 indexPart=0;

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref file);
			doDeserialize (stream,ref data);
			doDeserialize (stream,ref indexPart);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,file);
			doSerialize (stream,data);
			doSerialize (stream,indexPart);
		}
	}
	public class LogQueryRes : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 426821530;
			}
		}
		public override UInt32 ClsId{
			get{
				return 426821530;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.LogQueryRes";
			}
		}
		public override UInt32 SignId{
			get{
				return 3300748031;
			}
		}
		public static UInt32 sSignId{
			get{
				return 3300748031;
			}
		}

		public Bool isEnd=false;
		public List<LogInfo> logs=new List<LogInfo>();

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref isEnd);
			doDeserialize (stream,ref logs);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,isEnd);
			doSerialize (stream,logs);
		}
	}
	public class LogQueryReq : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 4152272566;
			}
		}
		public override UInt32 ClsId{
			get{
				return 4152272566;
			}
		}
		public override String ClsName{
			get{
				return "pkt.protocols.LogQueryReq";
			}
		}
		public override UInt32 SignId{
			get{
				return 605709401;
			}
		}
		public static UInt32 sSignId{
			get{
				return 605709401;
			}
		}

		public String key="";
		public UInt32 beginTime=0;
		public UInt32 endTime=0;
		public UInt32 appId=0;

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref key);
			doDeserialize (stream,ref beginTime);
			doDeserialize (stream,ref endTime);
			doDeserialize (stream,ref appId);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,key);
			doSerialize (stream,beginTime);
			doSerialize (stream,endTime);
			doSerialize (stream,appId);
		}
	}
} //end namespace protocols
} //end namespace pkt
