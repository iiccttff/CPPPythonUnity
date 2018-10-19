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
	public class GotoServerTokenRes : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 1234268567;
			}
		}
		public override UInt32 ClsId{
			get{
				return 1234268567;
			}
		}
		public override String ClsName{
			get{
				return "pkt.common.GotoServerTokenRes";
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

		public String toekn="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref toekn);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,toekn);
		}
	}
	public class RoleLoginSucceedRes : FastNet.Message {
		public static UInt32 sClsId{
			get{
				return 2771882275;
			}
		}
		public override UInt32 ClsId{
			get{
				return 2771882275;
			}
		}
		public override String ClsName{
			get{
				return "pkt.common.RoleLoginSucceedRes";
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

		public String roleId="";
		public String tabs="";
		public String name="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref roleId);
			doDeserialize (stream,ref tabs);
			doDeserialize (stream,ref name);
		}

		public override void Serialize(BinaryWriter stream) {
			doSerialize (stream,roleId);
			doSerialize (stream,tabs);
			doSerialize (stream,name);
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
				return 3742882662;
			}
		}
		public static UInt32 sSignId{
			get{
				return 3742882662;
			}
		}

		public String classId="";
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
				return 3742882662;
			}
		}
		public static UInt32 sSignId{
			get{
				return 3742882662;
			}
		}

		public String classId="";
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
} //end namespace common
} //end namespace pkt
