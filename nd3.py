# -*- coding: utf-8 -*-
import sys, time, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"C:\swprojects\sw-skill-fork\scripts"); sys.path.insert(0, str(S))
import sw_connect, win32com.client as w32
sp = importlib.util.spec_from_file_location("swapi", S/"sw_api_sldworks.py")
sw = importlib.util.module_from_spec(sp); sys.modules["swapi"]=sw; sp.loader.exec_module(sw)
sw.get_com_member = sw_connect.get_com_member
app = w32.dynamic.Dispatch("SldWorks.Application")
for _ in range(40):
    try: _ = app.RevisionNumber; break
    except Exception: time.sleep(1)
print("  版本:", app.RevisionNumber)
TPL = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2026\templates\gb_assembly.asmdot"
print("  模板存在:", Path(TPL).is_file())
try:
    print()
    print("  ① 真模板路径:")
    r = app.NewDocument(TPL, 2, 0.0, 0.0)
    print("     返回:", repr(r))
    print("  ② 文档到底建没建（GetActiveDoc）:")
    ad = app.ActiveDoc
    print("     ActiveDoc:", repr(ad))
    print("     Title:", end=" ")
    try: print(ad.GetTitle())
    except Exception as e: print("读不到:", str(e)[:50])
    print("  ③ GetDocuments:")
    gd = app.GetDocuments()
    print("     ", repr(gd))
    try: print("     数量:", len(list(gd or [])))
    except Exception as e: print("     不可迭代:", str(e)[:40])
    if ad is not None:
        print()
        print("  ④ 往这个装配里插一个 Toolbox 零件:")
        P = r"D:\SOLIDWORKS Data\browser\GB\washers and rings\lock washers\lock washers external teeth gb.sldprt"
        n0 = len(list(ad.GetComponents2(True, True) or []))
        ok = ad.AddComponent5(P, 0, "", True, "", 0.0, 0.0, 0.0)
        n1 = len(list(ad.GetComponents2(True, True) or []))
        print("     AddComponent5 ->", ok, " 组件数 %d -> %d" % (n0, n1))
        for c in (ad.GetComponents2(True, True) or []):
            try: print("     组件:", c.Name2)
            except Exception: pass
finally:
    try: app.CommandInProgress = False
    except Exception: pass
    try: app.ExitApp()
    except Exception: pass