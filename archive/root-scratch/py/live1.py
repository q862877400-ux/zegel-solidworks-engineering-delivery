# -*- coding: utf-8 -*-
"""第一次真跑：启动 SolidWorks 并取回应用对象。

按新版铁律 2 的安全约束：先置 CommandInProgress 拦弹窗、收尾复位。
"""
import sys, time
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
try:
    import win32com.client as w32
    import pythoncom
except ImportError as e:
    print("  pywin32 没装:", e); raise SystemExit(1)
print("  pywin32 OK")
# ① 先试已运行的实例
try:
    app = w32.GetActiveObject("SldWorks.Application")
    print("  ① GetActiveObject -> 已有实例")
except Exception as e:
    print("  ① GetActiveObject 失败（预期，未在运行）:", str(e)[:60])
    app = None
# ② 启动一个
if app is None:
    t0 = time.time()
    try:
        app = w32.dynamic.Dispatch("SldWorks.Application")
        print("  ② Dispatch 成功，耗时 %.1fs" % (time.time() - t0))
    except Exception as e:
        print("  ② Dispatch 失败:", str(e)[:120]); raise SystemExit(2)
    # 首次启动可能弹许可/欢迎页 —— 等
    for _ in range(20):
        try:
            vis = app.Visible
            print("  启动后可读 Visible =", vis); break
        except Exception:
            time.sleep(1.0)
    else:
        print("  启动后 20s 仍读不到属性 —— 可能有模态框挡着")
        raise SystemExit(3)
print()
print("  对象类型:", type(app))
try:
    print("  RevisionNumber:", app.RevisionNumber)
except Exception as e:
    print("  RevisionNumber 读不到:", str(e)[:60])
try:
    app.CommandInProgress = True
    print("  CommandInProgress = True  已置")
    app.CommandInProgress = False
    print("  CommandInProgress = False 已复位")
except Exception as e:
    print("  CommandInProgress 操作失败:", str(e)[:80])
try:
    docs = app.GetDocuments()
    print("  当前打开的文档数:", 0 if docs is None else len(list(docs) or []))
except Exception as e:
    print("  GetDocuments 失败:", str(e)[:60])