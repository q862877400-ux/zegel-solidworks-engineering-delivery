# -*- coding: utf-8 -*-
"""自愈循环 —— 型号 → 选型 → 生成预览。逐步自验、自愈、自取证。

⚑ 全自动；每步自己截图判定；失败自愈重试；有预算上限不无限循环。
⚑ 「生成预览」不点「插入」/「保存」⇒ 不产生文件。
"""
import json
import sys
import time
import warnings
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")

import heal as H
import sw_jlcfa_locate as L
import draw_loc as D
import win32api
import win32con
from PIL import ImageGrab

warnings.filterwarnings("ignore")
SHOTS = Path(r"D:\AI\SW\shots\loop")
SHOTS.mkdir(parents=True, exist_ok=True)
REC = []


def fresh():
    h, w = L.connect()
    return h, w, H.observe(h, w)


def shot(tag, h, w):
    try:
        L.focus_solidworks(h)
        cr = L.container_rect(w)
        if cr:
            ImageGrab.grab().crop((cr.left, cr.top, cr.right, cr.bottom)).save(
                str(SHOTS / ("%s.png" % tag)))
    except Exception:
        pass


def shapes(h, w):
    try:
        return D.locate_all(h, w, log=lambda m: None)
    except Exception:
        return {}


def ctrl_a():
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(ord("A"), 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(ord("A"), 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.25)


def to_home():
    h, w, s = fresh()
    if shapes(h, w).get("search_box"):
        H.log("  已在首页")
        return True
    ret = None
    for c in L._controls(w):
        try:
            if (c.window_text() or "").strip() == "返回":
                ret = c
                break
        except Exception:
            continue
    if ret is None:
        H.log("  ✗ 找不到「返回」")
        return False

    def act():
        ret.click_input()
        time.sleep(1.8)

    def check():
        hh, ww, _ = fresh()
        return bool(shapes(hh, ww).get("search_box"))

    ok = H.do_with_verify("点「返回」回首页", act, check, tries=3)
    h, w, s = fresh()
    shot("home" if ok else "home_fail", h, w)
    return ok


def do_search(code):
    h, w, s = fresh()
    sb = shapes(h, w).get("search_box")
    if sb is None:
        H.log("  ✗ 找不到搜索框")
        return False

    def act():
        H.click(sb[0], sb[1], 0.45)
        ctrl_a()
        for _ in range(28):
            H.key(win32con.VK_BACK, 0.03)
        H.typ(code)
        H.key(win32con.VK_RETURN, 0.4)
        time.sleep(2.0)

    def check():
        hh, ww, ss = fresh()
        return bool(ss["has_result"]) or bool(ss["has_model"])

    ok = H.do_with_verify("搜索 %s" % code, act, check, tries=2)
    h, w, s = fresh()
    shot("search_" + code, h, w)
    return ok, s


def main():
    h, w, s = fresh()
    H.log("起点: 返回=%s 结果=%s 选型=%s" % (s["has_return"], s["has_result"],
                                          s["has_model"]))
    if not to_home():
        return
    H.log("✓ 首页就绪")
    ok, s = do_search("EGW35SA")
    H.log("结果页: 结果=%s 选型=%s 按钮=%s"
          % (s["has_result"], s["has_model"], list(s["buttons"])[:8]))
    REC.append({"stage": "search", "code": "EGW35SA", "ok": ok,
                "has_result": s["has_result"], "pct": s["pct"]})
    Path(r"D:\AI\SW\loop_rec.json").write_text(
        json.dumps(REC, ensure_ascii=False, indent=1), encoding="utf-8")
    H.log("记录已存 loop_rec.json")


if __name__ == "__main__":
    main()
