# -*- coding: utf-8 -*-
"""置前 SolidWorks -> 截整屏（能看到浮窗）-> 标注读不到名字的控件位置。"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import loc
import win32api
import win32con
import win32gui
from PIL import ImageGrab

warnings.filterwarnings("ignore")

# ① 置前 SolidWorks（按住 Alt 绕过前台锁）
hwnd, win = loc.connect()
win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
time.sleep(0.15)
try:
    win32gui.SetForegroundWindow(hwnd)
except Exception as e:
    print("置前异常:", str(e)[:40])
time.sleep(0.35)
win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
time.sleep(1.2)
print("前台 =", win32gui.GetForegroundWindow(), "目标 =", hwnd,
      "✓" if win32gui.GetForegroundWindow() == hwnd else "✗")

# ② 截整屏（现在 SolidWorks 在最上层，能看到浮窗）
full = ImageGrab.grab()
full.save(r"D:\AI\SW\shots\sw_front.png")
print("整屏截图 %s" % (full.size,))

# ③ 插件容器 + 里面读到的控件
cont = loc.find_container(win)
cr = cont[2]
print()
print("插件容器:", cr, " 宽 %d 高 %d" % (cr.right - cr.left, cr.bottom - cr.top))

# ④ 裁出插件区单独看
pane = full.crop((cr.left, cr.top, cr.right, cr.bottom))
pane = pane.resize((int(pane.width * 1.3), int(pane.height * 1.3)))
pane.save(r"D:\AI\SW\shots\pane_only.png")
print("插件区截图 %s -> pane_only.png" % (pane.size,))

# ⑤ 读不到的控件，用「相对容器的比例」定位兜底
s = loc.scan(win)
MISS = ["搜索", "全部商品分类", "首页", "同步数据"]
print()
print("读不到名字的控件 -> 它们的实际位置（相对容器比例）:")
known = {t: r for t, (_c, r) in s.items()}
# 参考锚点：用「返回」这类已知控件推算纵向比例
ref = known.get("返回")
print("  参考锚点「返回」: y=%.1f%% of 容器高"
      % (100.0 * (ref.top - cr.top) / (cr.bottom - cr.top)))
for name in ("返回", "直线运动零件", "机床防护罩"):
    if name in known:
        r = known[name]
        print("  %-12s 相对容器: x=%.1f%% y=%.1f%%  宽=%.1f%%"
              % (name, 100.0 * (r.left - cr.left) / (cr.right - cr.left),
                 100.0 * (r.top - cr.top) / (cr.bottom - cr.top),
                 100.0 * r.width() / (cr.right - cr.left)))
