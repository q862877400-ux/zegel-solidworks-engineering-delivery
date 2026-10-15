# -*- coding: utf-8 -*-
"""全流程：首页 -> 分类 -> 子分类 -> 型号 -> 选型填参 -> 生成预览。

⚑ 全部按**名字**定位（实测：容器 569px / 1495px 两种宽度都准）。
⚑ 不点「插入」/「保存」⇒ 不产生文件。
⚑ 每步后自己读状态验证，失败不往下走。
"""
import re
import sys
import time
import warnings
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")

import sw_jlcfa_cards as C
import sw_jlcfa_locate as L
import win32api
import win32con

warnings.filterwarnings("ignore")
T0 = time.time()
STEP = [0]


def log(m):
    print("[%6.1fs] %s" % (time.time() - T0, m), flush=True)


def fresh():
    h, w = L.connect()
    return h, w


def click(x, y, pause=0.8):
    win32api.SetCursorPos((int(x), int(y)))
    time.sleep(0.12)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.06)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(pause)


def click_named(w, name, tries=2, pause=1.5):
    """按名字点插件区里的控件。点不到返回 False。"""
    for t in range(tries):
        h, w = fresh()
        r = L.rect_of(w, name)
        if r is not None:
            click((r.left + r.right) // 2, (r.top + r.bottom) // 2, pause)
            log("   ✓ 点「%s」" % name)
            return True
        time.sleep(0.4)
    log("   ✗ 点不到「%s」" % name)
    return False


def state(w):
    cr = L.container_rect(w)
    codes = C.code_labels(w)
    combos = []
    for c in L._controls(w):
        try:
            if c.element_info.control_type == "ComboBox" and L._overlaps(c.rectangle(), cr):
                combos.append(c.window_text().strip())
        except Exception:
            continue
    txts = [c.window_text().strip() for c in L._controls(w)
            if (c.window_text() or "").strip()]
    j = " ".join(txts)
    m = re.search(r"(\d+)%", j)
    return {"n_codes": len(codes), "codes": [c for _, _, c, _ in codes[:4]],
            "n_combos": len(combos), "combos": combos[:6],
            "pct": int(m.group(1)) if m else None,
            "has_生成": L.locate(w, "生成预览", "Button") is not None,
            "cr": cr}


def main():
    h, w = fresh()
    if L._modal().modal_report(h)["count"]:
        L._modal().close_modals(h, rounds=2)
        h, w = fresh()
    st = state(w)
    log("起点: 容器宽 %d  代码卡 %d  ComboBox %d  进度 %s"
        % (st["cr"].right - st["cr"].left, st["n_codes"], st["n_combos"], st["pct"]))

    # ① 回首页
    if not click_named(w, "返回"):
        log("没有「返回」，按当前页继续")
    else:
        h, w = fresh()
        st = state(w)
        log("回首页后: 代码卡 %d  ComboBox %d" % (st["n_codes"], st["n_combos"]))

    # ② 首页 -> 直线运动零件
    log("① 点「直线运动零件」")
    if not click_named(w, "直线运动零件"):
        return
    h, w = fresh()
    st = state(w)
    log("   分类页: 代码卡 %d  ComboBox %d" % (st["n_codes"], st["n_combos"]))

    # ③ -> 直线导轨
    r = C.locate_category(w, "直线导轨")
    if r is None:
        log("✗ 分类卡里找不到「直线导轨」，当前卡: %s"
            % [t for t, _ in C.category_cards(w)][:10])
        return
    log("② 点分类卡「直线导轨」%s" % ((r.left, r.top, r.right, r.bottom),))
    click((r.left + r.right) // 2, (r.top + r.bottom) // 2, 2.0)
    h, w = fresh()
    st = state(w)
    log("   结果页: 代码卡 %d 个 %s  ComboBox %d" % (st["n_codes"], st["codes"], st["n_combos"]))


if __name__ == "__main__":
    main()
