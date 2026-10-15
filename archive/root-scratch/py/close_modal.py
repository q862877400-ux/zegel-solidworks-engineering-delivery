# -*- coding: utf-8 -*-
"""验证模态检测器：关掉那个挡路对话框。"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import ctl
import modal
import win32api
import win32con

hwnd, win = ctl.connect()
rep = modal.modal_report(hwnd)
print("操作前: 对话框 %d 个" % len(rep["dialogs"]), flush=True)

for d in rep["dialogs"]:
    r = d["rect"]
    print("  弹窗 hwnd=%d cls=%s rect=%s" % (d["hwnd"], d["cls"], r), flush=True)
    # 用 UIA 找它的「确定」按钮
    from pywinauto import Application
    app = Application(backend="uia").connect(handle=d["hwnd"])
    dlg = app.window(handle=d["hwnd"])
    print("  弹窗内容: %r" % dlg.window_text()[:60], flush=True)
    btns = []
    for c in dlg.descendants():
        try:
            if c.element_info.control_type == "Button":
                rr = c.rectangle()
                btns.append((c.window_text().strip(), rr))
        except Exception:
            continue
    print("  按钮: %s" % [(n, (r2.left, r2.top, r2.right, r2.bottom))
                          for n, r2 in btns], flush=True)
    target = None
    for n, r2 in btns:
        if n in ("确定", "OK", "&确定"):
            target = r2
            break
    if target is None and btns:
        target = btns[0][1]
    if target:
        x = (target.left + target.right) // 2
        y = (target.top + target.bottom) // 2
        print("  点「%s」(%d,%d)" % (btns[0][0] if not btns else "按钮", x, y), flush=True)
        win32api.SetCursorPos((int(x), int(y)))
        time.sleep(0.15)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.08)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(1.0)

time.sleep(0.8)
hwnd, win = ctl.connect()
rep2 = modal.modal_report(hwnd)
print("操作后: 对话框 %d 个  %s" % (len(rep2["dialogs"]),
                                  "✅ 弹窗已关" if not rep2["dialogs"] else "❌ 还在"), flush=True)
