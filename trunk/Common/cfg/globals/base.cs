using System;
using System.IO;
using System.Collections.Generic;


namespace cfg{
namespace globals{
namespace base{

using UInt8 = Byte;
using Int8 = SByte;
using Float = Single;
using Bool = Boolean;
	public class Language : FastNet.Cfg<Language,UInt32> {
		public static UInt32 sClsId{
			get{
				return 1162455557;
			}
		}
		public override UInt32 ClsId{
			get{
				return 1162455557;
			}
		}
		public override String ClsName{
			get{
				return "cfg.globals.base.Language";
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

		public UInt32 id=0;
		public String text="";

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref id);
			doDeserialize (stream,ref text);
		}

		public static void Init() {
			Language.Load(FastNet.App.WorkPath + "/cfg/globals/base/Language.bytes",true);
		}
	}
	public class ErrorCode : FastNet.Cfg<ErrorCode,String> {
		public static UInt32 sClsId{
			get{
				return 576514151;
			}
		}
		public override UInt32 ClsId{
			get{
				return 576514151;
			}
		}
		public override String ClsName{
			get{
				return "cfg.globals.base.ErrorCode";
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

		public static void Init() {
			ErrorCode.Load(FastNet.App.WorkPath + "/cfg/globals/base/ErrorCode.bytes",true);
		}
	}
	public class Items : FastNet.Cfg<Items,UInt32> {
		public static UInt32 sClsId{
			get{
				return 998444613;
			}
		}
		public override UInt32 ClsId{
			get{
				return 998444613;
			}
		}
		public override String ClsName{
			get{
				return "cfg.globals.base.Items";
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

		public UInt32 id=0;
		public Language name=null;

		public override void Deserialize(BinaryReader stream){
			doDeserialize (stream,ref id);
			name = Language.GetItem(Language.ReadKey(stream));
		}

		public static void Init() {
			Items.Load(FastNet.App.WorkPath + "/cfg/globals/base/Items.bytes",true);
		}
	}
} //end namespace globals
} //end namespace base
} //end namespace cfg
