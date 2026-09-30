# -*- coding: utf-8 -*-
"""第三步：结果列表里点型号卡 —— 按「产品名」定位（比型号代码稳）。

⚑ 定位依据（本机控件树实测）
# --------------------------------------------------
#   Text  「代码：HGH20HAZ0C」      y=596
#   Text  「上银(HIWIN) HGH系列…」   y=540   ← ★ 用这个，型号代码易看错
#          （HGH20HAZC vs HGH20HAZ0C —— 数字 0 和字母 O 会看错）
#   ScrollBar「垂直滚动条」          y=517   ← 用户圈出的滚动条
"""
import re
import sys
import time
import warnings
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")

import sw_jlcfa_locate as L
import win32api
import win32con
from PIL import ImageGrab

warnings.filterwarnings("ignore")
SHOTS = Path(r"D:\AI\SW\shots\flow")
T0 = time.time()


def log(m):
    print("[%6.1fs] %s" % (time.time() - T0, m), flush=True)


def click(x, y, pause=0.6):
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.08)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(pause)


def snap(tag):
    try:
        h, w = L.connect()
        L.focus_solidworks(h)
        h, w = L.connect()
        cr = L.container_rect(w)
        if cr:
            ImageGrab.grab().crop((cr.left, cr.top, cr.right, cr.bottom)).save(
                str(SHOTS / (tag + ".png")))
    except Exception:
        pass


def find_product(prefix):
    """按产品名前缀找结果卡（返回矩形）。找不到返回 None。"""
    h, w = L.connect()
    cr = L.container_rect(w)
    if cr is None:
        return None
    best = None
    for c in L._controls(w):
        try:
            t = (c.window_text() or "").strip()
            r = c.rectangle()
        except Exception:
            continue
        if not t or not t.startswith(prefix):
            continue
        if not L._overlaps(r, cr):
            continue
        if best is None or r.top < best.top:
            best = r
    return best


def state():
    h, w = L.connect()
    cr = L.container_rect(w)
    pct = None
    has_cfg = False
    txts = []
    if cr:
        for c in L._controls(w):
            try:
                t = (c.window_text() or "").strip()
                r = c.rectangle()
                ct = c.element_info.control_type
            except Exception:
                continue
            if not t or not L._overlaps(r, cr):
                continue
            txts.append(t)
            if ct == "ComboBox":
                has_cfg = True
    j = " ".join(txts)
    m = re.search(r"(\d+)%", j)
    if m:
        pct = int(m.group(1))
    return {"pct": pct, "has_cfg": has_cfg,
            "n_combo": sum(1 for t in txts if False), "sample": txts[:12]}


def main():
    r = find_product("上银(HIWIN) HGH系列")
    if r is None:
        log("✗ 找不到产品卡")
        return
    log("找到产品卡 %s" % (r,))
    click((r.left + r.right) // 2, (r.top + r.bottom) // 2, 2.5)
    log("已点，等 3 秒…")
    time.sleep(3)
    snap("04_after_card")
    st = state()
    log("点后状态: 进度=%s%% 有配置下拉=%s" % (st["pct"], st["has_cfg"]))
    log("可见文字: %s" % [t[:16] for t in st["sample"]])


if __name__ == "__main__":
    main()
