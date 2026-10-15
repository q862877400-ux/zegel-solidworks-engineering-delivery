# -*- coding: utf-8 -*-
"""实测：属性/方法二义在真实 SolidWorks 上的影响面。"""
import sys
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
import win32com.client as w32
app = w32.GetActiveObject("SldWorks.Application")
print("  SW", app.RevisionNumber)
def probe(obj, name, args=()):
    """先按方法调，失败再按属性读 —— 复刻 sw_connect.get_com_member 的逻辑。"""
    try:
        m = getattr(obj, name)
    except Exception as e:
        return "MISSING", str(e)[:40]
    if args:
        try: return "CALL", m(*args)
        except Exception as e: return "CALL-FAIL", str(e)[:40]
    try:
        if callable(m):
            try: return "METHOD", m()
            except Exception as e:
                return "METHOD-ERR", str(e)[:40]
        return "PROP", m
    except Exception as e:
        return "ERR", str(e)[:40]
print()
print("  成员            形态        结果")
print("  " + "-"*56)
for n in ("GetDocuments","GetFirstDocument","ActiveDoc","FrameState",
          "EnableFileMenu","CommandInProgress","GetUserPreferenceToggle"):
    kind, val = probe(app, n)
    print("  %-16s %-11s %s" % (n, kind, str(val)[:26]))