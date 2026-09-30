# -*- coding: utf-8 -*-
"""用 sw_com_traps.byref_long() 给 by-ref 出参造 VARIANT，再开零件。"""
import sys
import time
import importlib.util
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, str(S))
import sw_connect
import win32com.client as w32

sp = importlib.util.spec_from_file_location("swapi", S / "sw_api_sldworks.py")
sw = importlib.util.module_from_spec(sp)
sys.modules["swapi"] = sw
sp.loader.exec_module(sw)
sw.get_com_member = sw_connect.get_com_member
ct = importlib.util.module_from_spec(
    importlib.util.spec_from_file_location("sw_com_traps", S / "sw_com_traps.py"))
sys.modules["sw_com_traps"] = ct
importlib.util.spec_from_file_location("sw_com_traps", S / "sw_com_traps.py").loader.exec_module(ct)

P = r"D:\SOLIDWORKS Data\browser\GB\washers and rings\lock washers\lock washers external teeth gb.sldprt"
e1, w1 = ct.byref_pair()
print("  byref_pair 造出:", type(e1).__name__, repr(e1), type(w1).__name__)

app = w32.dynamic.Dispatch("SldWorks.Application")
for _ in range(40):
    try:
        _ = app.RevisionNumber
        break
    except Exception:
        time.sleep(1)
try:
    app.CommandInProgress = True
    print()
    print("  ★ 用 byref VARIANT 传 errors/warnings：")
    d = app.OpenDoc6(P, 1, 1, "", e1, w1)
    print("     返回:", repr(d)[:50])
    if d is not None:
        print("     ★★ 成功！")
        print("        Title  :", sw.call_index(d, "IModelDoc2", "GetTitle"))
        print("        配置   :", sw.call_index(d, "IModelDoc2", "GetConfigurationNames"))
        print("        Path   :", sw.call_index(d, "IModelDoc2", "GetPathName"))
finally:
    try:
        app.CommandInProgress = False
    except Exception:
        pass
    try:
        app.ExitApp()
    except Exception:
        pass
