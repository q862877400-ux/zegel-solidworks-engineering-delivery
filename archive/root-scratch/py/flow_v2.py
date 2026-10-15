# -*- coding: utf-8 -*-
"""全流程（带自检）：首页 -> 分类 -> 子分类 -> 型号 -> 填参 -> 生成预览。"""
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


def main():
    h, w = L.connect()
    if L._modal().modal_report(h)["count"]:
        L._modal().close_modals(h, rounds=2)
        h, w = L.connect()
    st = S.read_state(w)
    S.log("起点: %s  容器宽 %d  进度 %s  代码卡 %d"
          % (S.page_kind(st), st["container"].right - st["container"].left,
             st["pct"], len(st["codes"])))

    # ① 回首页
    def go_home(h, w):
        r = L.rect_of(w, "返回")
        if r:
            S.click((r.left + r.right) // 2, (r.top + r.bottom) // 2, 0.6)

    if S.page_kind(st) != "HOME":
        h, w = S.run_step("点返回回首页", go_home, "HOME", h, w, timeout=30,
                          heal=go_home, tries=2)

    # ② 首页 -> 分类页
    def to_cat(h, w):
        r = L.rect_of(w, "直线运动零件")
        if r:
            S.click((r.left + r.right) // 2, (r.top + r.bottom) // 2, 0.8)

    h, w = S.run_step("点「直线运动零件」", to_cat, "CATEGORY", h, w, timeout=30, tries=2)

    # ③ 分类页 -> 结果页
    def to_result(h, w):
        r = C.locate_category(w, "直线导轨")
        if r is None:
            cards = [t for t, _ in C.category_cards(w)][:12]
            S.log("      找不到「直线导轨」，现有卡: %s" % cards)
            return
        S.click((r.left + r.right) // 2, (r.top + r.bottom) // 2, 1.0)

    h, w = S.run_step("点分类卡「直线导轨」", to_result, "RESULT", h, w,
                      timeout=40, tries=2)

    st = S.read_state(w)
    S.log("结果页: %d 个型号 %s" % (len(st["codes"]), st["codes"][:5]))
    return h, w


if __name__ == "__main__":
    try:
        main()
    except S.StepFailed as exc:
        S.log("✗ 流程中止: %s" % exc)
        S.log("  现场已留在 D:\\AI\\SW\\evidence\\")
