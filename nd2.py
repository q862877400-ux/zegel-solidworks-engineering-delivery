# -*- coding: utf-8 -*-
"""排查 NewDocument 返回 None。"""
import sys, time, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"C:\swprojects\sw-skill-fork\scripts"); sys.path.insert(0, str(S))
import sw_connect, win32com.client as w32
sp = importlib.util.spec_from_file_location("swapi", S/"sw_api_sldworks.py")
sw = importlib.util.module_from_spec(sp); sys.modules["swapi"]=sw; sp.loader.exec_module(sw)
sw.get_com_member = sw_connect.get_com_member
try:
    app = w32.GetActiveObject("SldWorks.Application"); print("  复用实例")
except Exception:
    app = w32.dynamic.Dispatch("SldWorks.Application"); print("  新启动")
    for _ in range(40):
        try: _ = app.RevisionNumber; break
        except Exception: time.sleep(1)
print("  版本:", app.RevisionNumber)
try:
    print()
    print("  ① 裸 dynamic 直接调（不经护栏）:")
    raw = app.NewDocument("", 2, 0.0, 0.0)
    print("     返回:", repr(raw), type(raw).__name__ if raw is not None else "None")
    print("  ② 裸 getattr 再调:")
    m = getattr(app, "NewDocument"); print("     callable:", callable(m))
    try:
        r2 = m("", 2, 0.0, 0.0); print("     返回:", repr(r2))
    except Exception as e: print("     调失败:", str(e)[:70])
    print("  ③ 用 ISldWorks 强制转换（DumbDispatch）:")
    try:
        d = w32.dynamic.DumbDispatch(app._oleobj_, "SldWorks.Application")
        r3 = d.NewDocument("", 2, 0.0, 0.0)
        print("     返回:", repr(r3), type(r3).__name__ if r3 is not None else "None")
        if r3 is not None:
            print("     Title:", end=" ")
            try: print(r3.GetTitle())
            except Exception as e: print("读不到:", str(e)[:40])
    except Exception as e:
        print("     失败:", str(e)[:70])
    print("  ④ 走 call_index:")
    r4 = sw.call_index(app, "ISldWorks", "NewDocument", "", 2, 0.0, 0.0)
    print("     返回:", repr(r4))
finally:
    try:
        docs = app.GetDocuments() or app.GetDocuments
        print("  打开的文档数:", len(list(docs) or []))
    except Exception: pass
    try: app.CommandInProgress = False
    except Exception: pass
    try: app.ExitApp()
    except Exception: pass