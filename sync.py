import sys, time, re, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import ctl, sw_gui_modal as M
warnings.filterwarnings("ignore")
hwnd, win = ctl.connect()
M.close_modals(hwnd)
for i in range(8):
    hwnd, win = ctl.connect()
    txt = []
    for c in win.descendants():
        try:
            if c.element_info.control_type in ("Text","Pane"):
                t=(c.window_text() or "").strip()
                if t: txt.append(t)
        except Exception: continue
    j=" | ".join(txt)
    m = re.search(r"(\d+)/(\d+)", j)
    has_search = any("商品型号" in t or "全部商品" in t for t in txt)
    print("  %d轮: 同步=%s  有首页元素=%s" % (i+1, m.group(0) if m else "无", has_search))
    if not m:
        print("      同步已结束")
        break
    time.sleep(12)