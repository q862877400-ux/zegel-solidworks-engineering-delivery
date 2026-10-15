# -*- coding: utf-8 -*-
"""插件控件探索器 —— 逐个点击 + 每次前后截图 + 记录结果。

⚑ 目标（用户 2026-09-30 明确要求）
# --------------------------------------------------
#   「从首页开始，探索每个控件都是干啥的，每个字符每个图标你都点一点试试，
#     每次点击前后都截图，学习这个插件所有的用法」
#   「尤其注意进入具体选型页面后上下两部分都可以向下滚动」

⚑ 设计
# --------------------------------------------------
#   每步：截图前 -> 点 -> 截图后 -> 记录「控件名/坐标/前后差异」
#   回退：点完能回上一级就回（点「返回」），回不去就用 ESC
#   自愈：点完若出模态框，关掉再继续
#   不产生文件：不点「插入」/「保存」
"""
import json
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
OUT = Path(r"D:\AI\SW\explore")
OUT.mkdir(parents=True, exist_ok=True)
T0 = time.time()
N = [0]
LOG = []

#: 绝对不点的东西（会破坏状态或产生文件）
FORBIDDEN = ("保存", "插入", "下载", "购买", "去官网", "联系我们",
             "个人中心", "设置", "清除所有", "同步数据")


def log(m):
    print("[%6.1fs] %s" % (time.time() - T0, m), flush=True)


def click(x, y, pause=0.7):
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.06)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(pause)


def esc(pause=0.5):
    win32api.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
    time.sleep(0.06)
    win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(pause)


def snap(tag):
    N[0] += 1
    p = OUT / ("%03d_%s.png" % (N[0], tag))
    try:
        h, w = L.connect()
        L.focus_solidworks(h)
        h, w = L.connect()
        cr = L.container_rect(w)
        if cr:
            ImageGrab.grab().crop((cr.left, cr.top, cr.right, cr.bottom)).save(str(p))
            return p
    except Exception:
        pass
    return None


def controls(win):
    """插件区里所有可点的控件（Button / Text / ComboBox / Edit）。"""
    cr = L.container_rect(win)
    if cr is None:
        return []
    out = []
    for c in L._controls(win):
        try:
            t = (c.window_text() or "").strip()
            ct = c.element_info.control_type
            r = c.rectangle()
        except Exception:
            continue
        if not t or not L._overlaps(r, cr):
            continue
        if ct not in ("Button", "Text", "ComboBox", "Edit", "Pane"):
            continue
        if r.width() < 12 or r.height() < 8:
            continue
        out.append({"text": t, "type": ct, "rect": r})
    out.sort(key=lambda d: (d["rect"].top, d["rect"].left))
    return out


def page_state(win):
    """当前页面的特征（用于判断「点完之后变了没有」）。"""
    ctrls = controls(win)
    names = sorted({c["text"][:22] for c in ctrls})
    combos = [c["text"] for c in ctrls if c["type"] == "ComboBox"]
    return {"n": len(ctrls), "names": names[:30], "combos": combos,
            "fingerprint": "|".join(names)[:400]}


def go_back(win):
    """尽量回到上一级：先找「返回」，再 ESC。"""
    for c in L._controls(win):
        try:
            if (c.window_text() or "").strip() == "返回":
                c.click_input()
                time.sleep(1.6)
                return "返回"
        except Exception:
            continue
    esc()
    time.sleep(0.6)
    return "ESC"


def main():
    h, w = L.connect()
    if L._modal().modal_report(h)["count"]:
        L._modal().close_modals(h, rounds=2)
        h, w = L.connect()
    cr = L.container_rect(w)
    log("容器 %s 宽 %d" % (cr, cr.right - cr.left))
    snap("home_before")
    before = page_state(w)
    log("首页控件 %d 个" % before["n"])
    log("  按钮: %s" % sorted({c['text'] for c in controls(w)
                            if c['type'] == 'Button'}))
    log("  ComboBox: %s" % before["combos"][:10])
    Path(OUT / "home_controls.json").write_text(
        json.dumps([{"text": c["text"], "type": c["type"],
                     "rect": [c["rect"].left, c["rect"].top,
                              c["rect"].right, c["rect"].bottom]}
                    for c in controls(w)], ensure_ascii=False, indent=1),
        encoding="utf-8")
    log("首页控件清单已存 explore/home_controls.json")


if __name__ == "__main__":
    main()
