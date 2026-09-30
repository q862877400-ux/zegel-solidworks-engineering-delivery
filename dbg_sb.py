import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import loc
warnings.filterwarnings("ignore")
hwnd, win = loc.connect()
cr = loc.find_container(win)[2]
print("容器:", cr, "宽", cr.right-cr.left, "高", cr.bottom-cr.top)
print()
print("★ 插件区内所有 Edit 控件（找搜索框）：")
for c in win.descendants():
    try:
        if c.element_info.control_type != "Edit": continue
        r = c.rectangle()
    except Exception: continue
    ov = min(r.right, cr.right) - max(r.left, cr.left)
    inside = ov > min(r.width(), cr.right-cr.left)*0.5
    print("   %-14r (%d,%d,%d,%d) %dx%d  重叠=%s  容器内相对y=%.0f"
          % ((c.window_text() or "")[:12], r.left, r.top, r.right, r.bottom,
             r.width(), r.height(), inside, r.top - cr.top))