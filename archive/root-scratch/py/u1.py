import sys, time, ctypes
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui, jlc_auto as J
ctypes.windll.user32.SetProcessDPIAware()
hwnd = J.sw_window()
r = J.ensure_window(hwnd)
J.log("窗口 %s 尺寸 %dx%d 标题 %r" % (r, r[2]-r[0], r[3]-r[1],
                                     win32gui.GetWindowText(hwnd)[:44]))
_root, rect = J.tab_column(hwnd)
J.log("标签列 %s" % (rect,))
# 截整个面板（不裁窄），看全貌
J.snap("u1_panel_full", box=(rect.right-4, rect.top-16, r[2], r[3]))
J.log("完成")