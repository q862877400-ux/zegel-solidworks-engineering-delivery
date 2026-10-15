import sys, re, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import ctl, sw_gui_modal as M
warnings.filterwarnings("ignore")
hwnd, win = ctl.connect()
M.close_modals(hwnd)
hwnd, win = ctl.connect()
t=[]
for c in win.descendants():
    try:
        if c.element_info.control_type in ("Text","Pane"):
            x=(c.window_text() or "").strip()
            if x and len(x)<50 and c.rectangle().left>1300: t.append(x)
    except Exception: continue
j=" | ".join(t)
print("SW:", win.window_text()[:50])
print("插件区:", j[:340])
m=re.search(r"(\d+)\s*/\s*(\d+)", j)
print()
print("同步页:", m.group(0) if m else "不在同步页")
print("有搜索框:", any(c.element_info.control_type=="Edit" and c.rectangle().top<300
                        and c.rectangle().left>1400 and c.rectangle().width()>200
                        for c in win.descendants() if True))