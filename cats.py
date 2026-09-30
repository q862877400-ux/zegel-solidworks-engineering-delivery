import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import ctl, sw_gui_modal as M
warnings.filterwarnings("ignore")
hwnd, win = ctl.connect()
M.close_modals(hwnd)
hwnd, win = ctl.connect()
print("当前页面上的分类/按钮:")
for c in win.descendants():
    try:
        ct = c.element_info.control_type
        t = (c.window_text() or "").strip()
        r = c.rectangle()
    except Exception:
        continue
    if t and ct in ("Text", "Button", "Pane") and r.left > 1350 and r.top < 800 and r.width() > 20:
        print("   %-8s %-26s (%d,%d,%d,%d)" % (ct, t[:24], r.left, r.top, r.right, r.bottom))
    if len([x for x in []]) > 100: break