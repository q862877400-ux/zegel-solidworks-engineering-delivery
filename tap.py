# -*- coding: utf-8 -*-
"""按用户教的取焦点方式：点参数标签（纯文本），不抢前台。
"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import ctl
import sw_gui_focus as F
import sw_gui_modal as M

warnings.filterwarnings("ignore")


def label_rect(win, name):
    """找参数标签（纯文本 Pane/Text），取它的坐标。"""
    best = None
    for c in win.descendants():
        try:
            if c.window_text().strip() != name:
                continue
            ct = c.element_info.control_type
            if ct not in ("Pane", "Text"):
                continue
            r = c.rectangle()
            if r.width() < 30:
                continue
            if best is None or r.width() > best.width():
                best = r
        except Exception:
            continue
    return best


def tap_label(win, hwnd, name):
    """★ 点标签纯文本 —— 焦点进插件窗格，但**不抢前台**。"""
    import win32api
    import win32con
    r = label_rect(win, name)
    if r is None:
        print("   [焦点] 找不到标签「%s」" % name, flush=True)
        return False
    x, y = (r.left + r.right) // 2, (r.top + r.bottom) // 2
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.08)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.25)
    print("   [焦点] 点标签「%s」(%d,%d) 前台=%d"
          % (name, x, y, F.foreground()), flush=True)
    return True


def combos(win):
    out = []
    for c in win.descendants():
        try:
            if c.element_info.control_type != "ComboBox":
                continue
            r = c.rectangle()
            if r.height() >= 10:
                out.append((c.window_text().strip(), c, r))
        except Exception:
            continue
    return out


if __name__ == "__main__":
    hwnd, win = ctl.connect()
    print("SolidWorks hwnd=%d 前台=%d" % (hwnd, F.foreground()), flush=True)
    M.close_modals(hwnd)
    print()
    print("参数标签定位测试:", flush=True)
    for nm in ("滑块固定方式", "滑块类型", "滑块数量", "预压", "精度等级"):
        r = label_rect(win, nm)
        print("   %-10s %s" % (nm, (r.left, r.top, r.right, r.bottom)
                                 if r else "**没找到**"), flush=True)
    print()
    print("试点「滑块类型」标签:", flush=True)
    tap_label(win, hwnd, "滑块类型")
    print("点完前台 =", F.foreground(), flush=True)
    print("（前台应仍是 SolidWorks，未抢到别的程序）", flush=True)
