# -*- coding: utf-8 -*-
import sys, time, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"C:\swprojects\sw-skill-fork\scripts"); sys.path.insert(0, str(S))
import sw_connect, win32com.client as w32
sp = importlib.util.spec_from_file_location("swapi", S/"sw_api_sldworks.py")
sw = importlib.util.module_from_spec(sp); sys.modules["swapi"]=sw; sp.loader.exec_module(sw)
sw.get_com_member = sw_connect.get_com_member
P = r"D:\SOLIDWORKS Data\browser\GB\washers and rings\lock washers\lock washers external teeth gb.sldprt"
print("  零件存在:", Path(P).is_file(), Path(P).stat().st_size, "bytes")
app = w32.dynamic.Dispatch("SldWorks.Application")
for _ in range(40):
    try: _ = app.RevisionNumber; break
    except Exception: time.sleep(1)
try:
    app.CommandInProgress = True
    print()
    print("  ① OpenDoc6(path, 1=PART, 1=Silent, '')  —— 4 参（另 2 个是 by-ref 出参）")
    d = sw.call_index(app, "ISldWorks", "OpenDoc6", P, 1, 1, "")
    print("     返回:", repr(d))
    if d is not None:
        print("     Title:", sw.call_index(d, "IModelDoc2", "GetTitle"))
        print("     配置:", sw.call_index(d, "IModelDoc2", "GetConfigurationNames"))
        print("     Path:", sw.call_index(d, "IModelDoc2", "GetPathName"))
        try:
            errs = sw.call_index(d, "IModelDocExtension", "GetMassProperties", 0)
            print("     质量属性(可读=文件完整):", type(errs).__name__)
        except Exception as e:
            print("     质量属性读不到:", str(e)[:50])
    print()
    print("  ② 若上面失败，试 swOpenDocOptions_ReadOnly=2 / RapidDraft=8")
    for opt, tag in ((2,"ReadOnly"), (8,"RapidDraft"), (0,"无选项")):
        try:
            d2 = sw.call_index(app, "ISldWorks", "OpenDoc6", P, 1, opt, "")
            print("     %-10s -> %s" % (tag, repr(d2)[:40]))
            if d2 is not None: break
        except Exception as e:
            print("     %-10s ERR %s" % (tag, str(e)[:44]))
finally:
    try: app.CommandInProgress = False
    except Exception: pass
    try: app.ExitApp()
    except Exception: pass