r"""@brief 终局判定：`CreateGoal(N)` 是否**本身就会创建**一个质量约束？

证据链（2026-10-01 真机，全部全新研究、互不污染）：
  A · 只 `GetMassConstraint`       → False（Get 不创建）；随后一个 `Create` → EndEdit=0
  B · 已有 1 个，再 `Create`        → EndEdit=**7**（OnlyOneMassConstraintCanBeDefined）
      ⇒ `CreateMassConstraint` **不查重，无条件新建**
  C · 全新研究 `CreateGoal(N)` 后 `Create` → EndEdit=**7**（目标 0 / 1 皆然）
      ⇒ 差别只在「有没有先建目标」⇒ 怀疑 `CreateGoal` 自带一个质量约束

本脚本直接读答案：建目标**之后**（不建任何约束）去看有没有质量约束。

# ── 来源 ──
# 仓库:   本项目自身（真机判定实验）
# 文件:   D:\AI\SW\probe_goal_creates_mass.py
# 定位:   AGENTS.md 铁律 4：反射给枚举、实测定成因。本脚本闭合最后一步，
#         结论回写 scripts/sw_topology.py::set_topology_goal 的调用顺序。
# 官方签名依据: ICWTopologyStudyManager.CreateGoal(Int32) /
#         GetMassConstraint(String, Int32&) / GetTopologyConstraintCount 一族；
#         swsTopologyStudyError_e（D:\AI\SW\_raw\topo-reflect\enum_cosworks.txt）
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


def has_mass(tsm):
    try:
        return get_com_member(tsm, "GetMassConstraint", MASS_NAME, out_i4()) is not None
    except Exception as exc:
        return "异常：%s" % str(exc)[:40]


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

        print("=== 每个目标类型：建目标【之前】与【之后】各有几个质量约束 ===")
        for goal in (0, 1, 2):
            s, _n = new_study(mgr, "GOALCHK%d" % goal)
            tsm = get_com_member(s, "TopologyStudyManager")
            before = has_mass(tsm)
            get_com_member(tsm, "BeginEdit")
            g = get_com_member(tsm, "CreateGoal", goal)
            code = get_com_member(tsm, "EndEdit")
            after = has_mass(tsm)
            names = {0: "MaximizeStiffness", 1: "MinimizeMaxDisplacement", 2: "MinimizeMass"}.get(goal, "?")
            print("  目标 %d %-26s 建前有质量约束=%-6r  CreateGoal=%r EndEdit=%r  建后=%r"
                  % (goal, names, before, g, code, after))
        print()

        print("=== 反证：不建目标，直接建质量约束，能否成功 ===")
        s, _n = new_study(mgr, "NOGOAL")
        tsm = get_com_member(s, "TopologyStudyManager")
        get_com_member(tsm, "BeginEdit")
        mc = get_com_member(tsm, "CreateMassConstraint", out_i4())
        if mc is not None:
            get_com_member(mc, "BeginEdit")
            get_com_member(mc, "SetMassPreference", 1)
            get_com_member(mc, "SetValue", 75.0)
            get_com_member(mc, "EndEdit")
        print("  无目标 + 质量约束 → CreateMassConstraint=%r  ★ EndEdit=%r" % (
            mc is not None, get_com_member(tsm, "EndEdit")))
        print()

        print("=== 官方示例的顺序复刻：先目标(1)提交，再在【新事务】里建质量约束 ===")
        s, _n = new_study(mgr, "SEQ")
        tsm = get_com_member(s, "TopologyStudyManager")
        get_com_member(tsm, "BeginEdit")
        get_com_member(tsm, "CreateGoal", 1)
        print("  第一个事务（只建目标）EndEdit=%r" % (get_com_member(tsm, "EndEdit"),))
        print("  此刻有质量约束吗：%r" % (has_mass(tsm),))
        get_com_member(tsm, "BeginEdit")
        mc = get_com_member(tsm, "CreateMassConstraint", out_i4())
        if mc is not None:
            get_com_member(mc, "BeginEdit")
            get_com_member(mc, "SetValue", 75.0)
            get_com_member(mc, "EndEdit")
        print("  第二个事务（建质量约束）→ %r  ★ EndEdit=%r" % (
            mc is not None, get_com_member(tsm, "EndEdit")))
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
