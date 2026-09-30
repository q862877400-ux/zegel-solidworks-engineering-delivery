# -*- coding: utf-8 -*-
"""优化版主流程：填参数到 100% -> 生成。

优化点（相对之前的逐轮截图 + 固定 sleep）：
  ① 「界面变了没」用**小区域截图 + md5** 判定，不肉眼
  ② 等待用 wait_until_changed（状态驱动），不用固定 sleep 3 秒
  ③ 连续动作之间不截图，只在关键节点截
  ④ 参数区每一轮都从「顶部」重新量，避免滚��后坐标失效
"""
import ctypes
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")

import shot
import win32api
import win32con
import win32gui
import jlc_auto as gui
import sw_jlcfa_select as sel

ctypes.windll.user32.SetProcessDPIAware()
BF_DIR = None


def focus_app(hwnd):
    win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
    time.sleep(0.1)
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        pass
    time.sleep(0.3)
    win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.35)


def probe_progress():
    """只截进度条那一小块 —— 判定「变了没」用。"""
    hwnd = gui.sw_window()
    r = gui.ensure_window(hwnd)
    _root, rect = gui.tab_column(hwnd)
    img, _ok, _w, _h = shot.capture(hwnd)
    return sel.crop_region(img, rect, 30, 275, 200, 26)


def main():
    hwnd = gui.sw_window()
    focus_app(hwnd)
    gui.ensure_window(hwnd)
    _root, rect = gui.tab_column(hwnd)
    print("  标签列 %s" % (rect,), flush=True)

    base_fp = sel.md5_png(probe_progress())
    print("  起始指纹 %s" % base_fp, flush=True)

    # ★ 第一步：取焦点（用户口述的关键动作）
    print("  ① 点参数框内部空白处 %s" % sel.fill_blank(hwnd, rect, gui), flush=True)
    time.sleep(0.4)

    for round_no in range(1, 13):
        r = gui.ensure_window(hwnd)
        _root, rect = gui.tab_column(hwnd)
        # 每轮重新取标签列（滚动不改它，但保险）
        img, _ok, _w, _h = shot.capture(hwnd)
        pane = sel.crop_region(img, rect, -4, -16, 560, 760)
        p = sel.SP if False else r"D:\AI\SW\shots\loop_%02d.png" % round_no
        pane.save(p)

        # 数一数还有几个「请选择」（找下拉框的灰色占位文字太脆，
        # 改用「进度条指纹是否变化」作为是否前进的判据）
        fp_before = sel.md5_png(probe_progress())
        print("  轮 %2d 指纹=%s" % (round_no, fp_before), flush=True)

        # 点当前屏上第一个下拉（位置：从裁剪图量）
        # 「请选择」框中心约 x=315, y=344（第一屏）
        cx = rect.right - 4 + 315
        cy = rect.top - 16 + 344
        gui.click(cx, cy, pause=0.5)
        sel.pick_first(gui)
        time.sleep(0.3)
        fp_after = sel.md5_png(probe_progress())
        if fp_after == fp_before:
            # 这屏没有可填的下拉了 -> 往下翻
            print("     指纹未变 -> 翻页", flush=True)
            sel.fill_blank(hwnd, rect, gui)
            sel.scroll(gui, rect, -3)
            changed, _ = sel.wait_until_changed(gui, probe_progress, 6)
            if not changed:
                print("     翻页无响应 -> 收手（可能已到底）", flush=True)
                break
            continue
        print("     指纹变了 -> 填成功", flush=True)
        # 回到顶部继续填
        sel.fill_blank(hwnd, rect, gui)
        sel.scroll(gui, rect, 6)
        time.sleep(0.4)

    print("  收工，最终截图见 loop_*.png", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
