# -*- coding: utf-8 -*-
"""下拉已展开 -> 按坐标点选项（本轮实测唯一可行路径）。"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import ctl
import sw_gui_modal as M
from tap import tap_label
import win32api
import win32con

warnings.filterwarnings("ignore")


def combo_of(win, name):
    for c in win.descendants():
        try:
            if c.element_info.control_type == "ComboBox" and \
                    c.window_text().strip() == name:
                return c
        except Exception:
            continue
    return None


def pick(hwnd, name, row):
    """展开下拉并点第 ``row`` 个选项（0=第一个）。"""
    M.close_modals(hwnd)
    hwnd, win = ctl.connect()
    tap_label(win, hwnd, name)                       # 点标签取焦点
    hwnd, win = ctl.connect()
    cb = combo_of(win, name)
    r = cb.rectangle()
    cb.click_input()                                  # 展开
    time.sleep(0.9)
    # 列表在控件正下方，每行约 30px；第一行 = 「请选择」
    item_y = r.bottom + 14 + row * 30
    item_x = (r.left + r.right) // 2
    print("   点选项 row=%d at (%d,%d)" % (row, item_x, item_y), flush=True)
    win32api.SetCursorPos((int(item_x), int(item_y)))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.06)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.7)
    hwnd, win = ctl.connect()
    cb = combo_of(win, name)
    if cb is None:
        # ⚠ 点完选项后控件可能因重排而重建 —— 重试一次再判定
        time.sleep(1.2)
        hwnd, win = ctl.connect()
        cb = combo_of(win, name)
        val = "(控件重建,已不在本屏)" if cb is None else cb.selected_text().strip()
    else:
        val = cb.selected_text().strip()
    return hwnd, win, val


if __name__ == "__main__":
    import re
    hwnd, win = ctl.connect()
    for nm, row in (("滑块类型", 1), ("滑块固定方式", 1), ("滑块数量", 1),
                    ("防尘配件", 1), ("预压", 1), ("精度等级", 1)):
        hwnd, win, val = pick(hwnd, nm, row)
        txt = []
        for c in win.descendants():
            try:
                if c.element_info.control_type == "Text" and c.window_text():
                    txt.append(c.window_text().strip())
            except Exception:
                continue
        m = re.search(r"(\d+)%", " ".join(txt))
        print("  %-10s -> %-10r  进度 %s%%"
              % (nm, val, m.group(1) if m else "?"), flush=True)
    M.screen_png(r"D:\AI\SW\shots\after_all.png")
    print("整屏: after_all.png", flush=True)
