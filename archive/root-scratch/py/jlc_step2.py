# -*- coding: utf-8 -*-
"""步骤 2：点搜索框 → 输入型号 → 回车 → 截图。"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32api
import win32con
import win32gui
import shot
import jlc_auto as J


def type_text(s: str) -> None:
    """用 VkKeyScan 逐字符敲（对大小写字母与数字都可靠）。"""
    for ch in s:
        vk = win32api.VkKeyScan(ch)
        vkey = vk & 0xFF
        shift = (vk >> 8) & 1
        if shift:
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        win32api.keybd_event(vkey, 0, 0, 0)
        time.sleep(0.03)
        win32api.keybd_event(vkey, 0, win32con.KEYEVENTF_KEYUP, 0)
        if shift:
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.03)


def main() -> int:
    keyword = sys.argv[1] if len(sys.argv) > 1 else "HGR20"
    hwnd = J.sw_window()
    J.log("窗口: %r" % win32gui.GetWindowText(hwnd)[:52])
    _root, rect = J.tab_column(hwnd)
    if rect is None:
        J.log("✗ 没有标签列")
        return 2
    r = rect
    J.log("标签列: %s" % (r,))

    panel_left = r.right + 2
    img, ok, w, h = shot.capture(hwnd)
    J.log("整窗 %dx%d  面板内容区 x>=%d" % (w, h, panel_left))

    # 搜索框中心：上一张截图里它横跨面板顶部
    sx, sy = panel_left + 130, r.top + 28
    J.log("点搜索框 (%d,%d)" % (sx, sy))
    J.click(sx, sy, pause=0.7)

    J.log("输入: %s" % keyword)
    type_text(keyword)
    time.sleep(0.6)
    J.snap("s2_typed", box=(panel_left - 12, r.top - 12,
                            min(w, panel_left + 430), r.top + 90))

    J.log("按回车搜索")
    win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
    time.sleep(0.08)
    win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(4.5)

    J.snap("s3_result", box=(panel_left - 12, r.top - 12,
                            min(w, panel_left + 470), min(h, r.top + 700)))
    J.log("完成，截图在 D:\\AI\\SW\\shots\\")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
