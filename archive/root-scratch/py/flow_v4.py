# -*- coding: utf-8 -*-
"""全流程 v4：焦点守卫 + 断点续跑 + 每步自检留证 + 控件缓存。"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")

import sw_jlcfa_cards as C
import sw_jlcfa_locate as L
import sw_jlcfa_steps as S

warnings.filterwarnings("ignore")


def named(w, name, card=False):
    """按名字取控件矩形（走缓存）。"""
    r = C.locate_category(w, name, S.controls_cached(w)) if card \
        else L.rect_of(w, name)
    if r is None:
        return None
    return (r.left + r.right) // 2, (r.top + r.bottom) // 2


STEPS = [
    ("HOME", "回首页", lambda w: named(w, "返回")),
    ("CATEGORY", "点「直线运动零件」", lambda w: named(w, "直线运动零件")),
    ("RESULT", "点分类卡「直线导轨」", lambda w: named(w, "直线导轨", card=True)),
]


def main():
    h, w = L.connect()
    if L._modal().modal_report(h)["count"]:
        L._modal().close_modals(h, rounds=2)
        h, w = L.connect()
    st = S.read_state(w)
    S.log("容器宽 %d  当前 %s" % (st["container"].right - st["container"].left,
                                 S.page_kind(st)))
    idx, _n, _a = S.resume(h, w, [(k, n, None) for k, n, _ in STEPS])
    for i in range(idx, len(STEPS)):
        kind, sname, getpt = STEPS[i]

        def act(hh, ww, _g=getpt):
            if not S.ensure_front(hh):
                S.log("      焦点不在 SolidWorks，跳过")
                return
            S.cache_drop()               # ★ 点击前重读，避免过期坐标
            hh2, ww2 = L.connect()
            pt = _g(ww2)
            if pt is None:
                S.log("      定位不到目标")
                return
            S.click(pt[0], pt[1], 1.0)

        h, w = S.run_step(sname, act, kind, h, w, timeout=30, tries=2)
        st = S.read_state(w)
        S.log("   状态 %s  型号 %d  分类卡 %d  ComboBox %d  进度 %s"
              % (S.page_kind(st), len(st["codes"]), len(st["categories"]),
                 len(st["combos"]), st["pct"]))
        S.cache_drop()
    st = S.read_state(w)
    S.log("★ 到达 %s，%d 个型号: %s"
          % (S.page_kind(st), len(st["codes"]), st["codes"][:6]))
    S.evidence("final_RESULT", h, w, st, note="全流程到达结果页")


if __name__ == "__main__":
    try:
        main()
    except S.StepFailed as exc:
        S.log("✗ 中止: %s" % exc)
        S.log("  现场: D:\\AI\\SW\\evidence\\")
