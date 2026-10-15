# -*- coding: utf-8 -*-
"""实测：属性/方法二义在真实 SolidWorks 2026 上的真实影响面。

一次跑完：启动 -> 探测 -> 收尾关闭（不留常驻进程）。
"""
import sys, time
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
import win32com.client as w32
try:
    app = w32.GetActiveObject("SldWorks.Application")
    print("  复用已有实例")
except Exception:
    app = w32.dynamic.Dispatch("SldWorks.Application")
    print("  新启动 SolidWorks")
    for _ in range(30):
        try:
            _ = app.RevisionNumber; break
        except Exception: time.sleep(1)
print("  版本 RevisionNumber =", app.RevisionNumber)
print()
def probe(obj, name):
    try: m = getattr(obj, name)
    except Exception as e: return "MISSING", str(e)[:34]
    try:
        if callable(m):
            try: return "METHOD", m()
            except Exception as e: return "METH-ERR", str(e)[:34]
        return "PROPERTY", m
    except Exception as e: return "ERR", str(e)[:34]
print("  ISldWorks 成员实测形态")
print("  " + "-"*58)
rows = []
for n in ("GetDocuments","GetFirstDocument","ActiveDoc","FrameState",
          "EnableFileMenu","CommandInProgress","Visible",
          "GetCurrentLicenseType","GetProcessID","GetCurrentLanguage"):
    k, v = probe(app, n); rows.append((n,k,v))
    print("  %-24s %-9s %s" % (n, k, str(v)[:28]))
print()
print("  >>> 统计：%d 个成员里 PROPERTY %d / METHOD %d / 其余 %d" % (
    len(rows),
    sum(1 for _,k,_ in rows if k=="PROPERTY"),
    sum(1 for _,k,_ in rows if k=="METHOD"),
    sum(1 for _,k,_ in rows if k not in ("PROPERTY","METHOD"))))
# 收尾
try: app.CommandInProgress = False
except Exception: pass
try:
    app.ExitApp(); print("  已 ExitApp")
except Exception as e:
    print("  ExitApp 失败（进程留给用户手动关）:", str(e)[:50])