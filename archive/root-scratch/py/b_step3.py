# -*- coding: utf-8 -*-
"""B 第三步：钻进 Task Pane Tabs Wnd，列出标签（只读）。"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
import win32gui
import uiautomation as auto
sys.path.insert(0, r"D:\AI\SW")
import shot

hwnd = int(open(r"D:\AI\SW\_sw_hwnd.txt").read().strip())
print("  窗口:", repr(win32gui.GetWindowText(hwnd)[:56]))
root = auto.ControlFromHandle(hwnd)
root.SetActive()
time.sleep(0.6)


def find(node, pred, depth=0, maxd=9):
    if depth > maxd:
        return None
    for c in node.GetChildren():
        try:
            if pred(c):
                return c
        except Exception:
            continue
        r = find(c, pred, depth + 1, maxd)
        if r is not None:
            return r
    return None


tabs = find(root, lambda c: (c.Name or "") == "Task Pane Tabs Wnd")
if tabs is None:
    print("  ✗ 找不到 Task Pane Tabs Wnd")
    raise SystemExit(1)
print("  找到标签容器:", tabs.BoundingRectangle)

# 向上找它所在的右栏，看有没有更完整的兄弟节点
print()
print("  ★ Task Pane Tabs Wnd 的完整子树")
n = 0


def dump(node, d=0, cap=200):
    global n
    if n > cap:
        return
    for c in node.GetChildren():
        n += 1
        try:
            print("   %s%-18s %-34s %s" % ("  " * d, c.ControlTypeName[:16],
                                            (c.Name or "")[:32], c.BoundingRectangle))
        except Exception:
            continue
        dump(c, d + 1, cap)


dump(tabs)

print()
print("  ★ 截图取证")
img, ok, w, h = shot.capture(hwnd, r"D:\AI\SW\shots\b_tabs.png")
print("    存 D:\\AI\\SW\\shots\\b_tabs.png  PrintWindow=%s" % ok)
# 裁右侧任务窗格区域放大
r = tabs.BoundingRectangle
crop = img.crop((r.left - 6, r.top - 40, min(w, r.right + 8), min(h, r.bottom + 6)))
crop = crop.resize((crop.width * 3, crop.height * 3), 3)
crop.save(r"D:\AI\SW\shots\b_tabs_zoom.png")
print("    放大图 b_tabs_zoom.png  %s" % (crop.size,))
