# -*- coding: utf-8 -*-
"""关键验证：末位 by-ref 出参，调用时到底要不要传占位。"""
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

P = r"D:\SOLIDWORKS Data\browser\GB\washers and rings\lock washers\lock washers external teeth gb.sldprt"

app = w32.dynamic.Dispatch("SldWorks.Application")
for _ in range(40):
    try:
        _ = app.RevisionNumber
        break
    except Exception:
        time.sleep(1)
try:
    app.CommandInProgress = True
    print("  ★ by-ref 出参要不要传占位？")
    for n_extra, tag in ((0, "4 参（无占位）"), (1, "5 参"), (2, "6 参（2 占位）")):
        args = [P, 1, 1, ""] + [None] * n_extra
        try:
            d = app.OpenDoc6(*args)
            print("    %-16s -> %s" % (tag, repr(d)[:44]))
            if d is not None:
                print("       ★★ 成功  Title =", sw.call_index(d, "IModelDoc2", "GetTitle"))
                print("          配置 =", sw.call_index(d, "IModelDoc2", "GetConfigurationNames"))
                break
        except Exception as e:
            print("    %-16s ERR %s" % (tag, str(e)[:50]))
finally:
    try:
        app.CommandInProgress = False
    except Exception:
        pass
    try:
        app.ExitApp()
    except Exception:
        pass
