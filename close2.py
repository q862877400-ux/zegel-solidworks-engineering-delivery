# -*- coding: utf-8 -*-
"""关弹窗：先给焦点再回车（点击不生效时的可靠路径）。"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import ctl
import modal
import win32api
import win32con
import win32gui

hwnd, win = ctl.connect()


def dialogs():
    return modal.modal_report(hwnd)["dialogs"]


print("初始对话框:", len(dialogs()), flush=True)
for attempt in range(1, 6):
    ds = dialogs()
    if not ds:
        print("✅ 已关闭（第 %d 轮确认）" % (attempt - 1), flush=True)
        break
    d = ds[0]
    dh = d["hwnd"]
    print("  轮 %d: 弹窗 hwnd=%d rect=%s" % (attempt, dh, d["rect"]), flush=True)

    # 方法1：给弹窗自己置前台
    try:
        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
        time.sleep(0.1)
        win32gui.SetForegroundWindow(dh)
        time.sleep(0.25)
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        print("     已置前=%s" % (win32gui.GetForegroundWindow() == dh), flush=True)
    except Exception as e:
        print("     置前失败:", str(e)[:40], flush=True)

    # 方法2：直接给弹窗发 WM_COMMAND(确定=IDOK=1)
    win32gui.PostMessage(dh, win32con.WM_COMMAND, 1, 0)
    time.sleep(0.6)

    # 方法3：回车
    win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
    time.sleep(0.08)
    win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.6)

    # 方法4：Esc
    win32api.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
    time.sleep(0.08)
    win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.6)
else:
    print("❌ 五轮都没关掉", flush=True)

modal.screen_png(r"D:\AI\SW\shots\after_close.png")
print("整屏截图: after_close.png", flush=True)
