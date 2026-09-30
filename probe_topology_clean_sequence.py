r"""@brief 干净序列测试：每种拓扑约束**单独**建，读 `EndEdit()` 的错误码。

背景（2026-10-01 真机）：
- 同一研究里连续建 目标 → 质量约束 → FOS 约束，第二个 `tsm.EndEdit()` 返回 **7**（非 0）
- `CreateFactorOfSafetyConstraint` 返回 None
- 之后再调本项目的 `set_topology_goal` 也返回 None（因为质量约束已存在）

官方示例的前置（`D:\AI\SW\_raw\cworksapi\Create_Topology_Study_Example_VBA.txt`）：

    ErrorCodeObj = CWTopologyStudyManagerObj.RemoveConstraint("Stress Constraint 1")
    Set CWTopoFOSConstraintObj = CWTopologyStudyManagerObj.CreateFactorOfSafetyConstraint(ErrorCodeObj)
    sFOSConstraintName = CWTopoFOSConstraintObj.GetName
    Set CWTopoFOSConstraintObj = CWTopologyStudyManagerObj.GetFactorOfSafetyConstraint(sFOSConstraintName, ErrorCodeObj)

⇒ 假设：**同类约束已存在时 `Create*` 返回 None**，必须先 `RemoveConstraint`。
本脚本用**每个约束一个全新研究**来隔离，逐个读错误码，验证假设。

# ── 来源 ──
# 仓库:   本项目自身（真机隔离实验）+ SolidWorks 官方示例（cworksapi.chm）
# 文件:   D:\AI\SW\probe_topology_clean_sequence.py
# 定位:   AGENTS.md 铁律 5「查不到就说查不到」的对应动作：错误码枚举页在 CHM 里**不存在**，
#         故不猜 7 的语义，改用「每个约束一个新研究」的隔离法把机制试出来。
# 官方签名依据: C:\cworks_en\api\Create_Topology_Study_Example_VB.htm
# 许可:   官方文档示例代码用于接口选型（非移植）；本仓库 MIT。
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


def make_study(mgr, tag):
    name = "%s_%d" % (tag, int(time.time()))
    get_com_member(mgr, "DeleteStudy", name)
    return get_com_member(mgr, "CreateNewStudy3", name, 13, 0, out_i4()), name


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
        print("  零件 %r；实体验证单实体" % title)
        print()

        # ── 实验 1：全新研究里，只建质量约束 ──
        print("=== 实验 1 · 全新研究，只建质量约束 ===")
        s, n1 = make_study(mgr, "CLN_MASS")
        tsm = get_com_member(s, "TopologyStudyManager")
        get_com_member(tsm, "BeginEdit")
        mc = get_com_member(tsm, "CreateMassConstraint", out_i4())
        print("  CreateMassConstraint → %r" % (mc is not None))
        if mc is not None:
            get_com_member(mc, "BeginEdit")
            get_com_member(mc, "SetMassPreference", 1)
            get_com_member(mc, "SetValue", 75.0)
            print("  mc.EndEdit → %r" % (get_com_member(mc, "EndEdit"),))
            print("  mc.GetName → %r" % (get_com_member(mc, "GetName"),))
        print("  ★ tsm.EndEdit → %r   （0 = 成功）" % (get_com_member(tsm, "EndEdit"),))
        print()

        # ── 实验 2：全新研究里，只建 FOS 约束（不先建质量约束）──
        print("=== 实验 2 · 全新研究，只建 FOS 约束 ===")
        s, n2 = make_study(mgr, "CLN_FOS")
        tsm = get_com_member(s, "TopologyStudyManager")
        get_com_member(tsm, "BeginEdit")
        fos = get_com_member(tsm, "CreateFactorOfSafetyConstraint", out_i4())
        print("  CreateFactorOfSafetyConstraint → %r" % (fos is not None))
        if fos is not None:
            print("  fos.GetName → %r" % (get_com_member(fos, "GetName"),))
            get_com_member(fos, "BeginEdit")
            get_com_member(fos, "SetValue", 80.0)
            print("  fos.EndEdit → %r" % (get_com_member(fos, "EndEdit"),))
        print("  ★ tsm.EndEdit → %r" % (get_com_member(tsm, "EndEdit"),))
        print()

        # ── 实验 3：先建质量约束，再 RemoveConstraint，再建 FOS ──
        print("=== 实验 3 · 建质量约束 → RemoveConstraint → 再建 FOS ===")
        s, n3 = make_study(mgr, "CLN_RM")
        tsm = get_com_member(s, "TopologyStudyManager")
        get_com_member(tsm, "BeginEdit")
        mc = get_com_member(tsm, "CreateMassConstraint", out_i4())
        nm = get_com_member(mc, "GetName") if mc is not None else None
        print("  第一个质量约束名 → %r" % (nm,))
        print("  tsm.EndEdit → %r" % (get_com_member(tsm, "EndEdit"),))
        # 再开一个事务，先删掉它
        get_com_member(tsm, "BeginEdit")
        print("  RemoveConstraint(%r) → %r" % (nm, get_com_member(tsm, "RemoveConstraint", nm)))
        print("  tsm.EndEdit → %r" % (get_com_member(tsm, "EndEdit"),))
        get_com_member(tsm, "BeginEdit")
        mc2 = get_com_member(tsm, "CreateMassConstraint", out_i4())
        print("  删后再建 → %r   （非 None 说明「已存在就返回 None」假设成立）" % (mc2 is not None))
        print("  tsm.EndEdit → %r" % (get_com_member(tsm, "EndEdit"),))
        print()

        # ── 实验 4：全新研究，目标 + 一个约束（官方示例的最小组合）──
        print("=== 实验 4 · 全新研究，目标(1) + 质量约束 ===")
        s, n4 = make_study(mgr, "CLN_MIN")
        tsm = get_com_member(s, "TopologyStudyManager")
        get_com_member(tsm, "BeginEdit")
        print("  CreateGoal(1) → %r" % (get_com_member(tsm, "CreateGoal", 1),))
        print("  tsm.EndEdit → %r" % (get_com_member(tsm, "EndEdit"),))
        get_com_member(tsm, "BeginEdit")
        mc = get_com_member(tsm, "CreateMassConstraint", out_i4())
        print("  CreateMassConstraint → %r" % (mc is not None))
        if mc is not None:
            get_com_member(mc, "BeginEdit")
            get_com_member(mc, "SetValue", 75.0)
            get_com_member(mc, "EndEdit")
        print("  ★ tsm.EndEdit → %r" % (get_com_member(tsm, "EndEdit"),))
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
