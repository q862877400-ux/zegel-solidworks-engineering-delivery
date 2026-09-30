r"""@brief 决定性实验：`Get*Constraint(name, &err)` 在约束**不存在**时会不会**创建**一个？

背景（2026-10-01 真机 + 反射）：
- 错误码真源找到了：`swsTopologyStudyError_e`
  `swsTopoErrCode_OnlyOneMassConstraintCanBeDefined = 7` ← 我在多处撞到的 7
- 我的 `_clear()` 用 `Get*Constraint(默认名, out_i4())` 探测「有没有」，探到就 `RemoveConstraint`。
  若 `Get*` **本身会创建**，则 `_clear` 制造了第一个约束、随后的 `Create*` 制造第二个
  ⇒ 提交时两个 ⇒ **错误 7**。本脚本判定这个假设。

三个对照实验，全部在**全新研究**上（每个实验一个新研究，互不污染）：
  A. 只调 `GetMassConstraint(默认名, out_i4())`，事务提交后看约束**在不在**
  B. 只建一个质量约束，然后连续调两次 `GetMassConstraint`，看第二次是否报错/是否多出约束
  C. 目标 0（MaximizeStiffness）+ 质量约束（应当合法）vs 目标 1（MinimizeMaxDisplacement）
     + 质量约束（怀疑非法，因为目标 1 自带质量约束语义）

# ── 来源 ──
# 仓库:   本项目自身（真机判定实验）
# 文件:   D:\AI\SW\probe_get_creates_constraint.py
# 定位:   AGENTS.md 铁律 4「三源互证」：反射给了错误码枚举（`enum_cosworks.txt` 的
#         `swsTopologyStudyError_e`），本机实测判定**成因**；两者合起来才结论。
#         本轮修正了上一轮「错误码 7 语义查不到」的错误结论 —— 它在枚举文件里，只是没搜到。
# 官方签名依据: ICWTopologyStudyManager.GetMassConstraint(String, Int32&) /
#         RemoveConstraint(String) / CreateMassConstraint(Int32&)；
#         D:\AI\SW\_raw\topo-reflect\enum_cosworks.txt 的 swsTopologyStudyError_e
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；不保存任何文档。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import time

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import (  # noqa: E402
    connect_solidworks,
    get_com_member,
    new_document,
    out_i4,
)
from scripts import sw_part  # noqa: E402

MASS_NAME = "质量约束 1"


def new_study(mgr, tag):
    n = "%s_%d" % (tag, int(time.time()))
    get_com_member(mgr, "DeleteStudy", n)
    return get_com_member(mgr, "CreateNewStudy3", n, 13, 0, out_i4()), n


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=15, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        sw_part.extrude_boss(model, sk, 0.02)
        doc = get_com_member(get_com_member(sw.GetAddInObject("SldWorks.Simulation"),
                                            "CosmosWorks"), "ActiveDoc")
        mgr = get_com_member(doc, "StudyManager")

        # ── 实验 A：只 Get，看它会不会创建 ──
        print("=== A · 全新研究，只调 GetMassConstraint（不做任何 Create）===")
        s, _n = new_study(mgr, "GETONLY")
        tsm = get_com_member(s, "TopologyStudyManager")
        try:
            got = get_com_member(tsm, "GetMassConstraint", MASS_NAME, out_i4())
            print("  GetMassConstraint(%r) → %r" % (MASS_NAME, got is not None))
        except Exception as e:
            print("  GetMassConstraint 抛异常: %s" % str(e)[:70])
        # 提交一个空事务，看错误码（若 Get 造了约束，这里不会报；但下面 B 会暴露）
        print("  空事务 tsm: BeginEdit→EndEdit = %r" % (
            (get_com_member(tsm, "BeginEdit"), get_com_member(tsm, "EndEdit"))[1],))
        # 现在再建一个质量约束：若 Get 造过一个 ⇒ 这里应当报 7
        get_com_member(tsm, "BeginEdit")
        mc = get_com_member(tsm, "CreateMassConstraint", out_i4())
        print("  再 CreateMassConstraint → %r" % (mc is not None))
        print("  ★ tsm.EndEdit → %r   （7 = OnlyOneMassConstraintCanBeDefined ⇒ 证明 Get 造了一个）"
              % (get_com_member(tsm, "EndEdit"),))
        print()

        # ── 实验 B：先正常建一个，再 Get 两次 ──
        print("=== B · 全新研究，正常建一个质量约束，再 Get 两次 ===")
        s, _n = new_study(mgr, "GETTWICE")
        tsm = get_com_member(s, "TopologyStudyManager")
        get_com_member(tsm, "BeginEdit")
        mc = get_com_member(tsm, "CreateMassConstraint", out_i4())
        get_com_member(mc, "BeginEdit")
        get_com_member(mc, "SetMassPreference", 1)
        get_com_member(mc, "SetValue", 75.0)
        get_com_member(mc, "EndEdit")
        print("  第一次 CreateMassConstraint → %r  tsm.EndEdit = %r"
              % (mc is not None, get_com_member(tsm, "EndEdit")))
        for k in (1, 2):
            try:
                g = get_com_member(tsm, "GetMassConstraint", MASS_NAME, out_i4())
                print("  Get 第 %d 次 → %r" % (k, g is not None))
            except Exception as e:
                print("  Get 第 %d 次 抛异常: %s" % (k, str(e)[:60]))
        get_com_member(tsm, "BeginEdit")
        mc2 = get_com_member(tsm, "CreateMassConstraint", out_i4())
        print("  Get 之后再 Create → %r  ★ tsm.EndEdit = %r"
              % (mc2 is not None, get_com_member(tsm, "EndEdit")))
        print()

        # ── 实验 C：目标 0 vs 目标 1，各配质量约束 ──
        print("=== C · 目标 0(MaximizeStiffness) + 质量约束  vs  目标 1(MinimizeMaxDisp) + 质量约束 ===")
        for goal, label in ((0, "目标0 MaximizeStiffness"), (1, "目标1 MinimizeMaxDisplacement")):
            s, _n = new_study(mgr, "GOAL%d" % goal)
            tsm = get_com_member(s, "TopologyStudyManager")
            get_com_member(tsm, "BeginEdit")
            g = get_com_member(tsm, "CreateGoal", goal)
            get_com_member(tsm, "EndEdit")
            get_com_member(tsm, "BeginEdit")
            mc = get_com_member(tsm, "CreateMassConstraint", out_i4())
            if mc is not None:
                get_com_member(mc, "BeginEdit")
                get_com_member(mc, "SetValue", 75.0)
                get_com_member(mc, "EndEdit")
            code = get_com_member(tsm, "EndEdit")
            verdict = {0: "Success", 7: "OnlyOneMassConstraintCanBeDefined",
                       4: "MinimizeMassGoalHasNotBeenSet"}.get(code, "?")
            print("  %-34s CreateGoal=%r  质量约束=%r  ★ tsm.EndEdit=%r (%s)"
                  % (label, g, mc is not None, code, verdict))
        return 0
    finally:
        try:
            if title:
                sw.CloseDoc(title)
        except Exception:
            pass
        try:
            sw.CommandInProgress = False
        except Exception:
            pass
        print("收尾完成（文档未保存）")


if __name__ == "__main__":
    raise SystemExit(main())
