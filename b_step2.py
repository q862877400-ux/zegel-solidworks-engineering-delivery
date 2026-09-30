# -*- coding: utf-8 -*-
"""B 第二步：建一个零件文档，让任务窗格插件有机会加载，然后重扫。"""
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import win32com.client as w32
import win32gui
import uiautomation as auto

TPL = r"C:\ProgramData\SolidWorks\SOLIDWORKS 2026\templates\gb_part.prtdot"
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_connect

sp = __import__("importlib.util", fromlist=["util"]).spec_from_file_location(
    "swapi", r"C:\swprojects\sw-skill-fork\scripts\sw_api_sldworks.py")
sw = __import__("importlib.util", fromlist=["util"]).module_from_spec(sp)
sys.modules["swapi"] = sw
sp.loader.exec_module(sw)
sw.get_com_member = sw_connect.get_com_member

if not Path(TPL).is_file():
    cands = sorted(Path(r"C:\ProgramData\SolidWorks\SOLIDWORKS 2026\templates").glob("*.prtdot"))
    TPL = str(cands[0]) if cands else TPL
print("  模板:", TPL)

app = w32.GetActiveObject("SldWorks.Application")
print("  复用实例:", app.RevisionNumber)
try:
    app.CommandInProgress = True
except Exception:
    pass

doc = None
try:
    # ★ NewDocument 4 参（模板名, 类型1=PART, X, Y）—— 护栏会校验
    doc = sw.call_index(app, "ISldWorks", "NewDocument", TPL, 1, 0.0, 0.0)
    print("  建文档:", sw.call_index(doc, "IModelDoc2", "GetTitle") if doc else None)
    time.sleep(4)

    hwnd = int(open(r"D:\AI\SW\_sw_hwnd.txt").read().strip())
    title = win32gui.GetWindowText(hwnd)
    print("  窗口:", repr(title[:56]))

    root = auto.ControlFromHandle(hwnd)
    root.SetActive()
    time.sleep(1.0)

    print()
    print("  ★ 重新扫描（文档打开后插件可能已挂上）")
    hits = []
    n = 0

    def walk(node, d):
        global n
        if d > 7 or n > 1500:
            return
        for c in node.GetChildren():
            n += 1
            try:
                nm = c.Name or ""
            except Exception:
                continue
            if nm and any(k in nm for k in ("立创", "FA", "零件库", "Forface",
                                             "嘉立创", "Add-Ins", "加载项")):
                hits.append((d, c.ControlTypeName, nm, c.BoundingRectangle))
            walk(c, d + 1)

    walk(root, 0)
    print("  扫过 %d 个控件，命中 %d" % (n, len(hits)))
    for h in hits[:20]:
        print("    d%d %-16s %-32s %s" % (h[0], h[1][:14], h[2][:30], h[3]))

    print()
    print("  ★ 右侧任务窗格区（插件通常挂这里）")
    tp = root.GetChildren()
    for c in tp:
        try:
            if c.Name and "草图" in c.Name:
                for g in c.GetChildren():
                    print("    %-16s %-30s %s" % (g.ControlTypeName[:14],
                                                    (g.Name or "")[:28],
                                                    g.BoundingRectangle))
                    for gg in g.GetChildren()[:10]:
                        print("        └ %-14s %-26s %s" % (gg.ControlTypeName[:12],
                                                            (gg.Name or "")[:24],
                                                            gg.BoundingRectangle))
        except Exception:
            pass
finally:
    try:
        app.CommandInProgress = False
    except Exception:
        pass
    # ⚠ 故意**不**关文档也不 ExitApp —— 让它留着给下一步
    print("\n  保持 SolidWorks 运行（供下一步），未关文档")
