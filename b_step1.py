# -*- coding: utf-8 -*-
"""B 第一步：枚举 SolidWorks 当前 UI 树，找嘉立创插件入口。只读，不点击。"""
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui
import uiautomation as auto

OUT = Path(r"D:\AI\SW\shots")
OUT.mkdir(exist_ok=True)

hwnd = int(open(r"D:\AI\SW\_sw_hwnd.txt").read().strip())
title = win32gui.GetWindowText(hwnd)
print("  目标窗口: hwnd=%d  %r" % (hwnd, title))
if not title.upper().startswith("SOLIDWORKS"):
    print("  ✗ 标题不匹配，中止（不操作非目标窗口）")
    raise SystemExit(1)

root = auto.ControlFromHandle(hwnd)
root.SetActive()
time.sleep(0.8)

print()
print("  ★ 深度扫描，找插件入口")
found = []
seen = 0


def walk(node, depth):
    global seen
    if depth > 6 or seen > 900:
        return
    for c in node.GetChildren():
        seen += 1
        try:
            nm = c.Name or ""
            ct = c.ControlTypeName or ""
            r = c.BoundingRectangle
        except Exception:
            continue
        if nm and ("立创" in nm or "FA" in nm or "零件" in nm or "工具" in nm
                   or "add-in" in nm.lower() or "加载" in nm or "选项" in nm):
            found.append((depth, ct, nm, r))
        walk(c, depth + 1)


walk(root, 0)
print("  扫过 %d 个控件，命中 %d 个关键词" % (seen, len(found)))
for d, ct, nm, r in found[:20]:
    print("    d%d %-18s %-30s %s" % (d, ct[:16], nm[:28], r))

print()
print("  ★ 顶层工具栏（点击插件的入口通常在这）")
top = root.GetChildren()
for c in top[:10]:
    try:
        print("    %-18s %-32s %s" % (c.ControlTypeName[:16], (c.Name or "")[:30],
                                      c.BoundingRectangle))
        for g in c.GetChildren()[:8]:
            print("        └ %-14s %-26s %s" % (g.ControlTypeName[:12],
                                                (g.Name or "")[:24],
                                                g.BoundingRectangle))
    except Exception:
        pass
