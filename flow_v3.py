# -*- coding: utf-8 -*-
"""全流程 v3：焦点守卫 + 断点续跑 + 每步自检留证。"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")

import sw_jlcfa_cards as C
import sw_jlcfa_locate as L
import sw_jlcfa_steps as S

warnings.filterwarnings("ignore")


def click_named(w, name):
    r = L.rect_of(w, name)
    if r is None:
        S.log("      读不到「%s」" % name)
        return
    S.click((r.left + r.right) // 2, (r.top + r.bottom) // 2, 0.6)


def click_card(w, name):
    r = C.locate_category(w, name)
    if r is None:
        S.log("      分类卡里没有「%s」" % name)
        return
    S.click((r.left + r.right) // 2, (r.top + r.bottom) // 2, 0.9)


STEPS = [
    ("HOME", "回首页", lambda h, w: click_named(w, "返回")),
    ("CATEGORY", "点「直线运动零件」", lambda h, w: click_named(w, "直线运动零件")),
    ("RESULT", "点分类卡「直线导轨」", lambda h, w: click_card(w, "直线导轨")),
]


def main():
    h, w = L.connect()
    if L._modal().modal_report(h)["count"]:
        L._modal().close_modals(h, rounds=2)
        h, w = L.connect()
    st = S.read_state(w)
    S.log("容器宽 %d  当前 %s  进度 %s  代码卡 %d"
          % (st["container"].right - st["container"].left,
             S.page_kind(st), st["pct"], len(st["codes"])))

    # ★ 从当前页续跑，不是从首页
    idx, name, act = S.resume(h, w, STEPS)
    for i in range(idx, len(STEPS)):
        kind, sname, sa = STEPS[i]
        def act_wrapped(hh, ww, _s=sa):
            if S.ensure_front(hh):
                _s(hh, ww)
            else:
                S.log("      焦点不在 SolidWorks，跳过本步")
        h, w = S.run_step(sname, act_wrapped, kind, h, w, timeout=35, tries=2)
        st = S.read_state(w)
        S.log("   状态: %s  进度 %s  代码卡 %d  分类卡 %d"
              % (S.page_kind(st), st["pct"], len(st["codes"]), len(st["categories"])))
        if i == len(STEPS) - 1:
            S.log("到达 %s" % kind)
            S.evidence("reached_" + kind, h, w, st, note="流程到达目标页")


if __name__ == "__main__":
    try:
        main()
    except S.StepFailed as exc:
        S.log("✗ 中止: %s" % exc)
        S.log("  现场: D:\\AI\\SW\\evidence\\")
