using System;
using System.IO;
using System.Collections.Generic;


namespace cfg{
namespace globals{
namespace modules{

using UInt8 = Byte;
using Int8 = SByte;
using Float = Single;
using Bool = Boolean;
	public class NoticeMgr : FastNet.Cfg<NoticeMgr,String> {
		public static UInt32 sClsId{
			get{
				return 692628191;
			}
		}
		public override UInt32 ClsId{
			get{
				return 692628191;
			}
		}
		public override String ClsName{
			get{
				return "cfg.globals.modules.NoticeMgr";
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

		public String name="";
		public String key="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref name);
			doDeserialize (stream,ref key);
		}

		public static void Init() {
			NoticeMgr.Load(FastNet.App.WorkPath + "/cfg/globals/modules/NoticeMgr.bytes",true);
		}
	}
	public class PlatformMgr : FastNet.Cfg<PlatformMgr,String> {
		public static UInt32 sClsId{
			get{
				return 1674269620;
			}
		}
		public override UInt32 ClsId{
			get{
				return 1674269620;
			}
		}
		public override String ClsName{
			get{
				return "cfg.globals.modules.PlatformMgr";
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

		public String name="";
		public String key="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref name);
			doDeserialize (stream,ref key);
		}

		public static void Init() {
			PlatformMgr.Load(FastNet.App.WorkPath + "/cfg/globals/modules/PlatformMgr.bytes",true);
		}
	}
	public class ServerMgr : FastNet.Cfg<ServerMgr,String> {
		public static UInt32 sClsId{
			get{
				return 920194243;
			}
		}
		public override UInt32 ClsId{
			get{
				return 920194243;
			}
		}
		public override String ClsName{
			get{
				return "cfg.globals.modules.ServerMgr";
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

		public String name="";
		public String key="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref name);
			doDeserialize (stream,ref key);
		}

		public static void Init() {
			ServerMgr.Load(FastNet.App.WorkPath + "/cfg/globals/modules/ServerMgr.bytes",true);
		}
	}
	public class UserMgr : FastNet.Cfg<UserMgr,String> {
		public static UInt32 sClsId{
			get{
				return 522108523;
			}
		}
		public override UInt32 ClsId{
			get{
				return 522108523;
			}
		}
		public override String ClsName{
			get{
				return "cfg.globals.modules.UserMgr";
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

		public String name="";
		public String key="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref name);
			doDeserialize (stream,ref key);
		}

		public static void Init() {
			UserMgr.Load(FastNet.App.WorkPath + "/cfg/globals/modules/UserMgr.bytes",true);
		}
	}
	public class DataQuery : FastNet.Cfg<DataQuery,String> {
		public static UInt32 sClsId{
			get{
				return 1484661923;
			}
		}
		public override UInt32 ClsId{
			get{
				return 1484661923;
			}
		}
		public override String ClsName{
			get{
				return "cfg.globals.modules.DataQuery";
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

		public String name="";
		public String key="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref name);
			doDeserialize (stream,ref key);
		}

		public static void Init() {
			DataQuery.Load(FastNet.App.WorkPath + "/cfg/globals/modules/DataQuery.bytes",true);
		}
	}
	public class MailMgr : FastNet.Cfg<MailMgr,String> {
		public static UInt32 sClsId{
			get{
				return 1879507711;
			}
		}
		public override UInt32 ClsId{
			get{
				return 1879507711;
			}
		}
		public override String ClsName{
			get{
				return "cfg.globals.modules.MailMgr";
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

		public String name="";
		public String key="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref name);
			doDeserialize (stream,ref key);
		}

		public static void Init() {
			MailMgr.Load(FastNet.App.WorkPath + "/cfg/globals/modules/MailMgr.bytes",true);
		}
	}
} //end namespace globals
} //end namespace modules
} //end namespace cfg
