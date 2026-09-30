# -*- coding: utf-8 -*-
"""验证：侧边栏宽度变了，定位层是否仍然有效。"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import loc
import win32api
import win32con

warnings.filterwarnings("ignore")

KEYS = ["返回", "直线运动零件", "机床防护罩", "传动零部件", "轴承附件"]


def snap(tag):
    hwnd, win = loc.connect()
    cont = loc.find_container(win)
    s = loc.scan(win)
    print()
    print("  === %s ===" % tag)
    print("    容器: %s" % (cont[2] if cont else "无"))
    out = {}
    for k in KEYS:
        if k in s:
            ct, r = s[k]
            out[k] = r
            print("    %-12s (%d,%d,%d,%d) %dx%d"
                  % (k, r.left, r.top, r.right, r.bottom, r.width(), r.height()))
        else:
            print("    %-12s 缺失" % k)
    return cont[2] if cont else None, out


def drag(x1, y1, x2, y2, steps=16):
    win32api.SetCursorPos((int(x1), int(y1)))
    time.sleep(0.15)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    for i in range(1, steps + 1):
        win32api.SetCursorPos((int(x1 + (x2 - x1) * i / steps),
                              int(y1 + (y2 - y1) * i / steps)))
        time.sleep(0.03)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(1.2)


c1, o1 = snap("宽度 A（当前）")

# 标签列左边那条分隔条
hwnd, win = loc.connect()
tabs = None
for c in win.descendants():
    try:
        if (c.window_text() or "").strip() == "Task Pane Tabs Wnd":
            tabs = c.rectangle()
            break
    except Exception:
        continue
if tabs is None:
    print("找不到标签列，无法拖")
    raise SystemExit(1)

print()
print("  ★ 侧边栏当前宽 %d px，拉窄 260 px…" % (c1.right - c1.left))
xe = tabs.left - 4
drag(xe, tabs.top + 120, xe - 260, tabs.top + 120)
time.sleep(2.5)
c2, o2 = snap("宽度 B（窄 260px）")

print()
print("  ★ 自适应判定")
if c1 and c2:
    print("    容器宽 %d -> %d  （%s）"
          % (c1.right - c1.left, c2.right - c2.left,
             "已改变" if c1.right != c2.right else "未变"))
ok = True
for k in KEYS:
    if k in o1 and k in o2:
        r1, r2 = o1[k], o2[k]
        moved = (r1.left != r2.left) or (r1.width() != r2.width())
        print("    %-12s 左边 %d->%d 宽 %d->%d  %s"
              % (k, r1.left, r2.left, r1.width(), r2.width(),
                 "坐标已跟随" if moved else "无变化"))
    else:
        ok = False
        print("    %-12s ✗ 两次没都拿到" % k)
print()
print("  结论: %s" % ("✓ 宽度变了仍能按名字定位" if ok and c1.right != c2.right
                      else "（宽度未变，需再测）" if ok else "✗ 有控件丢失"))
loc.M.screen_png(r"D:\AI\SW\shots\width_B.png")
print("  截图: width_B.png")
