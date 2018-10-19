using System;
using System.IO;
using System.Collections.Generic;


namespace cfg{
namespace Message{

using UInt8 = Byte;
using Int8 = SByte;
using Float = Single;
using Bool = Boolean;
	public class ErrorCode : FastNet.Cfg<ErrorCode,String> {
		public static UInt32 sClsId{
			get{
				return 1760467203;
			}
		}
		public override UInt32 ClsId{
			get{
				return 1760467203;
			}
		}
		public override String ClsName{
			get{
				return "cfg.Message.ErrorCode";
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

		public String msg="";
		public String key="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref msg);
			doDeserialize (stream,ref key);
		}

		public static void Init() {
			ErrorCode.Load(FastNet.App.WorkPath + "/cfg/Message/ErrorCode.bytes",true);
		}
	}
} //end namespace Message
} //end namespace cfg
