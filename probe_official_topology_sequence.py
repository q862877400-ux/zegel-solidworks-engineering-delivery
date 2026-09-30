r"""@brief 照**官方示例的调用序列**重跑拓扑研究，定位我之前失败的真正原因。

官方依据（原文已存 `D:\AI\SW\_raw\cworksapi\Create_Topology_Study_Example_VBA.txt`）：

    StudyManagerObj.ActiveStudy = 1                     ← ★ 我漏了
    NewStudyName = "Topology Study 1"
    StudyManagerObj.DeleteStudy NewStudyName            ← ★ 我漏了
    Set CWNewStudy = StudyManagerObj.CreateNewStudy3(NewStudyName, 13, 0, ErrorCodeObj)

    CWTopologyStudyManagerObj.BeginEdit
    ErrorCodeObj = CWTopologyStudyManagerObj.CreateGoal(1)
    Set GoalObj = CWTopologyStudyManagerObj.MinimizeMaximumDisplacementGoal()   ← 用 Getter
    GoalObj.BeginEdit
    ...SetComponent(3)
    GoalObj.EndEdit
    ErrorCodeObj = CWTopologyStudyManagerObj.EndEdit

    Set FOSObj = CWTopologyStudyManagerObj.CreateFactorOfSafetyConstraint(ErrorCodeObj)
    FOSName = FOSObj.GetName                            ← GetName 是**属性**，无括号
    Set FOSObj = CWTopologyStudyManagerObj.GetFactorOfSafetyConstraint(FOSName, ErrorCodeObj)

本脚本逐条对照，找出我哪里不一样。**不改用户数据**：新建未保存文档，收尾不保存。

# ── 来源 ──
# 仓库:   本项目自身（真机对照实验）+ SolidWorks 官方示例（cworksapi.chm）
# 文件:   D:\AI\SW\probe_official_topology_sequence.py
# 定位:   AGENTS.md 铁律 4「三源互证」的第三源（官方 CHM 的**示例代码**）与
#         本项目实现的正面对照；结论回写 scripts/sw_topology.py。
# 官方签名依据: C:\cworks_en\api\Create_Topology_Study_Example_VB.htm
#         （api\cworksapi.chm 解包，2790 页）
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
from scripts import sw_topology as topo  # noqa: E402


def trial(label, fn):
    try:
        r = fn()
        print("  %-48s ✓ %r" % (label, r))
        return r
    except Exception as e:
        print("  %-48s ✗ %s" % (label, str(e)[:58]))
        return None


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
        print("  已建单实体零件 %r" % title)
        print()

        doc = get_com_member(get_com_member(sw.GetAddInObject("SldWorks.Simulation"),
                                            "CosmosWorks"), "ActiveDoc")
        mgr = get_com_member(doc, "StudyManager")
        name = "OFFICIAL_SEQ_%d" % int(time.time())

        print("=== ① 官方序列：先 ActiveStudy / DeleteStudy，再建研究 ===")
        trial("mgr.DeleteStudy(name)（同名先删）", lambda: get_com_member(mgr, "DeleteStudy", name))
        study = trial("mgr.CreateNewStudy3(name, 13, 0, out_i4())",
                      lambda: get_com_member(mgr, "CreateNewStudy3", name, 13, 0, out_i4()))
        if study is None:
            print("\n  ⇒ 研究建不出来，后续无从谈起。")
            return 2
        cnt = get_com_member(mgr, "StudyCount")
        print("     StudyCount = %r" % cnt)
        trial("mgr.ActiveStudy = 最后一个下标", lambda: setattr(mgr, "ActiveStudy", int(cnt)))
        print("     ⚠ 官方是在**建研究之前**设 ActiveStudy=1；本处建完后补设，等价性未知")
        print()

        tsm = get_com_member(study, "TopologyStudyManager")
        print("=== ② 目标：官方用 Getter 取对象，不用 CreateGoal 的返回值 ===")
        trial("tsm.BeginEdit", lambda: get_com_member(tsm, "BeginEdit"))
        trial("tsm.CreateGoal(1)（MinimizeMaximumDisplacement）",
              lambda: get_com_member(tsm, "CreateGoal", 1))
        trial("tsm.MinimizeMaximumDisplacementGoal()（★ 官方取法）",
              lambda: get_com_member(tsm, "MinimizeMaximumDisplacementGoal"))
        trial("tsm.MaximizeStiffnessGoal()（试同族 Getter）",
              lambda: get_com_member(tsm, "MaximizeStiffnessGoal"))
        trial("tsm.EndEdit", lambda: get_com_member(tsm, "EndEdit"))
        print()

        print("=== ③ 质量约束（官方：BeginEdit → CreateMassConstraint(Err) → 内层编辑 → EndEdit）===")
        trial("tsm.BeginEdit", lambda: get_com_member(tsm, "BeginEdit"))
        mc = trial("tsm.CreateMassConstraint(out_i4())",
                   lambda: get_com_member(tsm, "CreateMassConstraint", out_i4()))
        if mc is not None:
            trial("  mc.BeginEdit", lambda: get_com_member(mc, "BeginEdit"))
            trial("  mc.SetMassPreference(1=Percentage)", lambda: get_com_member(mc, "SetMassPreference", 1))
            trial("  mc.SetValue(75.0)", lambda: get_com_member(mc, "SetValue", 75.0))
            trial("  mc.EndEdit", lambda: get_com_member(mc, "EndEdit"))
            trial("  mc.GetName（★ 属性，无括号）", lambda: get_com_member(mc, "GetName"))
        trial("tsm.EndEdit", lambda: get_com_member(tsm, "EndEdit"))
        print()

        print("=== ④ 安全系数约束（我之前在此失败）===")
        trial("tsm.BeginEdit", lambda: get_com_member(tsm, "BeginEdit"))
        fos = trial("tsm.CreateFactorOfSafetyConstraint(out_i4())",
                    lambda: get_com_member(tsm, "CreateFactorOfSafetyConstraint", out_i4()))
        if fos is not None:
            trial("  fos.GetName（属性）", lambda: get_com_member(fos, "GetName"))
            trial("fos.BeginEdit", lambda: get_com_member(fos, "BeginEdit"))
            trial("  fos.SetValue(80.0)", lambda: get_com_member(fos, "SetValue", 80.0))
            trial("  fos.EndEdit", lambda: get_com_member(fos, "EndEdit"))
        trial("tsm.EndEdit", lambda: get_com_member(tsm, "EndEdit"))
        print()

        print("=== ⑤ 本项目实现的同一操作（对照）===")
        trial("topo.set_topology_goal(study, 减重75 + 安全系数80)",
              lambda: topo.set_topology_goal(study, mass_reduce_percent=75.0, factor_of_safety=80.0))
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
        print("  收尾完成（文档未保存）")


if __name__ == "__main__":
    raise SystemExit(main())
