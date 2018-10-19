using System;
using System.IO;
using System.Collections.Generic;


namespace pkt{
namespace common{

using UInt8 = Byte;
using Int8 = SByte;
using Float = Single;
using Bool = Boolean;
	public class AccountVerifySucceedRes : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 3008152104;
			}
		}
		public override UInt32 ClsId{
			get{
				return 3008152104;
			}
		}
		public override String ClsName{
			get{
				return "pkt.common.AccountVerifySucceedRes";
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
	public class AnyReq : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 1862303533;
			}
		}
		public override UInt32 ClsId{
			get{
				return 1862303533;
			}
		}
		public override String ClsName{
			get{
				return "pkt.common.AnyReq";
			}
		}
		public override UInt32 SignId{
			get{
				return 201825498;
			}
		}
		public static UInt32 sSignId{
			get{
				return 201825498;
			}
		}

		public UInt32 classId=0;
		public String data="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref classId);
			doDeserialize (stream,ref data);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,classId);
			doSerialize (stream,data);
		}
	}
	public class AnyRes : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 2165186049;
			}
		}
		public override UInt32 ClsId{
			get{
				return 2165186049;
			}
		}
		public override String ClsName{
			get{
				return "pkt.common.AnyRes";
			}
		}
		public override UInt32 SignId{
			get{
				return 201825498;
			}
		}
		public static UInt32 sSignId{
			get{
				return 201825498;
			}
		}

		public UInt32 classId=0;
		public String data="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref classId);
			doDeserialize (stream,ref data);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,classId);
			doSerialize (stream,data);
		}
	}
	public class AnyForwardRes : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 4233942935;
			}
		}
		public override UInt32 ClsId{
			get{
				return 4233942935;
			}
		}
		public override String ClsName{
			get{
				return "pkt.common.AnyForwardRes";
			}
		}
		public override UInt32 SignId{
			get{
				return 287502520;
			}
		}
		public static UInt32 sSignId{
			get{
				return 287502520;
			}
		}

		public UInt32 classId=0;
		public UInt64 sessionId=0;
		public UInt32 serverId=0;
		public String data="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref classId);
			doDeserialize (stream,ref sessionId);
			doDeserialize (stream,ref serverId);
			doDeserialize (stream,ref data);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,classId);
			doSerialize (stream,sessionId);
			doSerialize (stream,serverId);
			doSerialize (stream,data);
		}
	}
	public class AnyForwardReq : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 307410619;
			}
		}
		public override UInt32 ClsId{
			get{
				return 307410619;
			}
		}
		public override String ClsName{
			get{
				return "pkt.common.AnyForwardReq";
			}
		}
		public override UInt32 SignId{
			get{
				return 287502520;
			}
		}
		public static UInt32 sSignId{
			get{
				return 287502520;
			}
		}

		public UInt32 classId=0;
		public UInt64 sessionId=0;
		public UInt32 serverId=0;
		public String data="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref classId);
			doDeserialize (stream,ref sessionId);
			doDeserialize (stream,ref serverId);
			doDeserialize (stream,ref data);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,classId);
			doSerialize (stream,sessionId);
			doSerialize (stream,serverId);
			doSerialize (stream,data);
		}
	}
} //end namespace common
} //end namespace pkt
