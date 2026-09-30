import sys, re, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import ctl, sw_gui_modal as M
warnings.filterwarnings("ignore")
hwnd, win = ctl.connect()
txt = []
for c in win.descendants():
    try:
        if c.element_info.control_type == "Text" and c.window_text():
            txt.append(c.window_text().strip())
    except Exception:
        continue
j = " | ".join(txt)
print("界面文字:", j[:300])
m = re.search(r"(\d+)%", j)
print("进度:", m.group(1) if m else "?")
print()
print("所有 ComboBox:")
for c in win.descendants():
    try:
        if c.element_info.control_type == "ComboBox" and c.rectangle().height() >= 10:
            r = c.rectangle()
            print("   %-12s = %-12s y=%d" % (c.window_text().strip(),
                                             c.selected_text().strip(), r.top))
    except Exception:
        continue
M.screen_png(r"D:\AI\SW\shots\state91.png")
print()
print("整屏: state91.png")