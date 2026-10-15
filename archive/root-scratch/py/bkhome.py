import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import ctl, sw_gui_modal as M
warnings.filterwarnings("ignore")
hwnd, win = ctl.connect()
M.close_modals(hwnd)
hwnd, win = ctl.connect()
print("当前页有「返回」:", any((c.window_text() or "").strip()=="返回"
                              for c in win.descendants()), flush=True)
# 点「返回」看能否回首页
ret = None
for c in win.descendants():
    try:
        if c.element_info.control_type=="Text" and (c.window_text() or "").strip()=="返回":
            ret = c; break
    except Exception: continue
if ret:
    ret.click_input(); time.sleep(2.5)
    print("已点返回", flush=True)
    hwnd, win = ctl.connect()
    txt=[]
    for c in win.descendants():
        try:
            if c.element_info.control_type in ("Text","Pane"):
                t=(c.window_text() or "").strip()
                if t and len(t)<40: txt.append(t)
        except Exception: continue
    print("返回后可见文字:", " | ".join(txt[:26]), flush=True)