

def Init():
    global _global_dict
    _global_dict = {}

def Uninit():
    global _global_dict
    _global_dict.clear()
    _global_dict = None

def SetValue(name, value):
    global _global_dict
    _global_dict[name] = value

def GetValue(name, defValue=None):
    try:
        global _global_dict
        return _global_dict[name]
    except KeyError:
        return defValue