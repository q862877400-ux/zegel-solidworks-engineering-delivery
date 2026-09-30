# -*- coding: utf-8 -*-
"""自愈循环主程序 —— 型号 → 选型 → 生成预览，逐步自验自愈。

⚑ 全自动。每步自己截图判定，失败自愈重试，有预算上限。
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
from PIL import ImageGrab

warnings.filterwarnings("ignore")
SHOTS = Path(r"D:\AI\SW\shots\loop")
SHOTS.mkdir(parents=True, exist_ok=True)
REC = []


def fresh():
    hwnd, win = L.connect()
    return hwnd, win, H.observe(hwnd, win)


def shot(tag, hwnd, win):
    try:
        L.focus_solidworks(hwnd)
        cr = L.container_rect(win)
        if cr:
            img = ImageGrab.grab().crop((cr.left, cr.top, cr.right, cr.bottom))
            img.save(str(SHOTS / ("%s.png" % tag)))
    except Exception:
        pass


def shapes(hwnd, win):
    try:
        return D.locate_all(hwnd, win, log=lambda m: None)
    except Exception:
        return {}


def to_home(hwnd, win, st):
    """回首页：点「返回」，自验「搜索框出现」。"""
    pts = shapes(hwnd, win)
    if pts.get("search_box"):
        H.log("  已在首页（搜索框存在）")
        return True
    ret = L.locate(win, "返回", "Text")
    if ret is None:
        for c in L._controls(win):
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
        h2, w2, s2 = fresh()
        return bool(shapes(h2, w2).get("search_box"))

    ok = H.do_with_verify("点「返回」回首页", act, check,
                          heal=lambda: (fresh(), None), tries=3)
    h, w, s = fresh()
    shot("home" if ok else "home_fail", h, w)
    return ok


def search(hwnd, win, code):
    """搜索一个型号，自验「出现 N 个结果」。"""
    pts = shapes(hwnd, win)
    sb = pts.get("search_box")
    if sb is None:
        H.log("  ✗ 找不到搜索框")
        return False

    def act():
        H.click(sb[0], sb[1], 0.45)
        for _ in range(30):
            H.key(win32con_VK_BACK)
        win32api_mod_ctrl_a()
        H.typ(code)
        H.key(win32con_VK_RETURN)
        time.sleep(2.2)

    def check():
        h, w, s = fresh()
        return bool(s["has_result"]) or bool(s["has_model"])

    def win32api_mod_ctrl_a():
        import win32api
        import win32con
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord("A"), 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(ord("A"), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

    global win32con_VK_BACK, win32con_VK_RETURN, win32api_mod_ctrl_a
    import win32con
    win32con_VK_BACK = win32con.VK_BACK
    win32con_VK_RETURN = win32con.VK_RETURN
    win32api_mod_ctrl_a = win32api_mod_ctrl_a

    ok = H.do_with_verify("搜索 %s" % code, act, check, tries=2)
    h, w, s = fresh()
    shot("search_" + code, h, w)
    return ok


def main():
    hwnd, win, st = fresh()
    H.log("起点: 返回=%s 结果=%s 选型=%s" % (st["has_return"], st["has_result"],
                                          st["has_model"]))
    if not to_home(hwnd, win, st):
        H.log("✗ 回不了首页")
        return
    H.log("✓ 已在首页")
    hwnd, win, st = fresh()
    ok = search(hwnd, win, "EGW35SA")
    H.log("搜索 EGW35SA -> %s" % ("成功" if ok else "失败"))
    hwnd, win, st = fresh()
    H.log("结果页状态: 结果=%s 进度=%s 按钮=%s"
          % (st["has_result"], st["pct"], list(st["buttons"])[:8]))
    REC.append({"stage": "search", "code": "EGW35SA", "ok": ok, "state": {
        "has_result": st["has_result"], "pct": st["pct"]}})
    Path(r"D:\AI\SW\loop_rec.json").write_text(
        json.dumps(REC, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
