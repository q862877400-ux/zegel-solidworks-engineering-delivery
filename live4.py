# -*- coding: utf-8 -*-
"""实测：走真实的 call_index 路径，看它到底行不行。"""
import sys, time, importlib.util
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
import win32com.client as w32
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
try:
    app = w32.GetActiveObject("SldWorks.Application"); print("  复用实例")
except Exception:
    app = w32.dynamic.Dispatch("SldWorks.Application"); print("  新启动")
    for _ in range(30):
        try: _ = app.RevisionNumber; break
        except Exception: time.sleep(1)
print("  SW", app.RevisionNumber)
spec = importlib.util.spec_from_file_location("swapi", r"C:\swprojects\sw-skill-fork\scripts\sw_api_sldworks.py")
m = importlib.util.module_from_spec(spec); sys.modules["swapi"]=m; spec.loader.exec_module(m)
m.get_com_member = __import__("sw_connect").get_com_member
print()
print("  走 call_index 的真实结果：")
print("  " + "-"*56)
for fam, mem, args in (("ISldWorks","GetDocuments",()),
                       ("ISldWorks","GetFirstDocument",()),
                       ("ISldWorks","GetProcessID",()),
                       ("ISldWorks","GetCurrentLanguage",()),
                       ("ISldWorks","FrameState",()),
                       ("ISldWorks","GetCurrentLicenseType",())):
    try:
        v = m.call_index(app, fam, mem, *args)
        print("  %-22s %-14s OK  -> %r" % (fam, mem, v))
    except Exception as e:
        print("  %-22s %-14s ERR -> %s" % (fam, mem, str(e)[:44]))
# arity 护栏仍在？
print()
try:
    m.call_index(app, "ISldWorks", "GetProcessID", 1)
    print("  [FAIL] 错 arity 未被拦")
except ValueError as e:
    print("  [OK] 错 arity 被拦:", str(e)[:60])
try:
    m.call_index(app, "INotAFamily", "X")
    print("  [FAIL] 未登记族未拦")
except KeyError as e:
    print("  [OK] 未登记族被拦")
try: app.CommandInProgress = False
except Exception: pass
try: app.ExitApp()
except Exception: pass