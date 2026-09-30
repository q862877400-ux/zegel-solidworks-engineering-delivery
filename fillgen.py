# -*- coding: utf-8 -*-
"""填参数到 100% + 生成预览（已验证过的那套方法）。"""
import re
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")

import sw_jlcfa_cards as C
import sw_jlcfa_locate as L
import sw_jlcfa_steps as S
import win32api
import win32con

warnings.filterwarnings("ignore")


def params(w):
    """选型页的参数下拉（排除「代码」这种只读的）。"""
    allc = S.controls_cached(w)
    cr = S._container_from(allc)
    out = []
    for c in allc:
        try:
            t = (c.window_text() or "").strip()
            r = c.rectangle()
            if c.element_info.control_type != "ComboBox" or not t:
                continue
            if not L._overlaps(r, cr):
                continue
            if t in ("每页", "代码"):
                continue
            out.append((t, c, c.selected_text().strip(), r))
        except Exception:
            continue
    return out


def label_of(allc, cr, name):
    for c in allc:
        try:
            if (c.window_text() or "").strip() != name:
                continue
            if c.element_info.control_type not in ("Pane", "Text"):
                continue
            r = c.rectangle()
            if r.width() > 150 and L._overlaps(r, cr):
                return r
        except Exception:
            continue
    return None


def fill_one(h, w, name, cb, r):
    """点标签取焦点 -> 点开下拉 -> 点第一项。返回填后的值。"""
    allc = S.controls_cached(w)
    cr = S._container_from(allc)
    lab = label_of(allc, cr, name)
    if lab:
        S.click((lab.left + lab.right) // 2, (lab.top + lab.bottom) // 2, 0.3)
    cb.click_input()
    time.sleep(0.7)
    if L._modal().modal_report(h)["count"]:
        L._modal().close_modals(h, rounds=2)
        return None
    S.click((r.left + r.right) // 2, r.bottom + 14 + 30, 0.5)
    S.cache_drop()
    h2, w2 = L.connect()
    for t2, c2, v2, _r2 in params(w2):
        if t2 == name:
            return h2, w2, v2
    return h2, w2, None


def main():
    h, w = L.connect()
    st = S.read_state(w)
    S.log("起点 %s  进度 %s" % (S.page_kind(st), st["pct"]))
    for rnd in range(1, 10):
        st = S.read_state(w)
        if st["pct"] == 100:
            S.log("★★ 100%")
            break
        ps = params(w)
        empty = [(n, c, v, r) for n, c, v, r in ps if v == "请选择"]
        S.log("轮%d 进度=%s%%  待填=%s"
              % (rnd, st["pct"], [n for n, _, _, _ in empty]))
        if not empty:
            S.log("没有待填项，但没到 100%")
            break
        n, c, v, r = empty[0]
        S.log("   填「%s」" % n)
        if not S.ensure_front(h):
            S.log("   焦点不在，跳过")
            break
        h, w, new = fill_one(h, w, n, c, r)
        S.log("   -> %r  现在 %s%%" % (new, S.read_state(w)["pct"]))
    # 生成
    st = S.read_state(w)
    S.log("最终进度 %s%%" % st["pct"])
    if st["pct"] != 100:
        S.evidence("not100", h, w, st, note="未达 100%")
        return
    S.cache_drop()
    h, w = L.connect()
    btn = L.locate(w, "生成预览", "Button")
    if btn is None:
        S.log("✗ 找不到「生成预览」")
        S.evidence("no_gen_btn", h, w, S.read_state(w), note="无生成按钮")
        return
    S.ensure_front(h)
    r = btn.rectangle()
    S.log("点「生成预览」%s" % ((r.left, r.top, r.right, r.bottom),))
    S.click((r.left + r.right) // 2, (r.top + r.bottom) // 2, 1.0)
    time.sleep(6.0)
    S.cache_drop()
    h, w = L.connect()
    S.log("SolidWorks 标题: %s" % w.window_text()[:70])
    S.evidence("after_generate", h, w, S.read_state(w), note="生成预览后")


if __name__ == "__main__":
    main()
