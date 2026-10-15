r"""@brief 真机验证拓扑优化 API 全链，并产出 `topology_optimization` 的 evidence。

**用本项目自己的 helper，不裸写 win32com** —— 那些 helper 已经把
AGENTS.md §六 的已知事实封进去了（`get_com_member` 处理属性/方法二象性、
`sw_part.sketch` 处理基准面名随 UI 语言变、`create_empty_dispatch_variant` 处理空 Dispatch）。
裸写会重新踩已知事实 4 / 9 / 12 的坑（第一次跑就踩了两个）。

不碰用户数据：新建**未保存**的文档，收尾**不保存**直接关闭。

官方依据：CHM `otsimtopology.chm` 解包 —— 拓扑优化只能对**单实体零件**做；
官方教程的流程是「研究树 Goals and Constraints → Mass Constraint（减重百分比）」。
签名依据：cosworks 反射（ICWStudyManager / ICWStudy / ICWTopologyStudyManager）。

# ── 来源 ──
# 仓库:   本项目自身（实测脚本）+ 本项目既有模式（sw_connect / sw_part / sw_simulation）
# 文件:   D:\AI\SW\prove_topology_api.py
# 定位:   AGENTS.md 铁律 2「本机实测」；产物写进 capabilities.yaml 的 evidence。
# 官方签名依据: D:\AI\SW\_raw\topo-reflect\iface_cosworks.txt
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机 SolidWorks；收尾不保存、直接关闭自建文档。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402
from scripts import sw_part  # noqa: E402

SIMULATION_PROGID = "SldWorks.Simulation"
TOPOLOGY_STATIC = 13  # swsAnalysisStudyTypeTopology_Static
GOAL_MAXIMIZE_STIFFNESS = 0
MASS_PERCENTAGE = 1


def out(label: str, value: object) -> None:
    print("  %-48s %s" % (label, value))


def main() -> int:
    # return_metadata=True 时返回 (sw, model, metadata) —— 三个值
    sw, opened_model, meta = connect_solidworks(wait_seconds=10, return_metadata=True)
    created_title = None
    try:
        out("SolidWorks 版本", get_com_member(sw, "RevisionNumber"))
        out("启动元数据", meta)
        sw.CommandInProgress = True
        out("CommandInProgress=True", "✓")

        # ① 本项目自己的建零件入口（含模板解析）
        model = new_document(sw, doc_type="part")
        created_title = get_com_member(model, "GetTitle")
        out("新建零件", "✓ %r" % created_title)

        # ② 单实体：一块板（拓扑优化的硬要求）
        sk_name = sw_part.sketch(model, "Front Plane")
        out("建草图（含基准面名候选）", sk_name)
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        feat = sw_part.extrude_boss(model, sk_name, 0.02)
        out("拉伸成板", "✓" if feat else "✗")
        bodies = get_com_member(model, "GetBodies2", 0, True)
        out("实体数（拓扑要求 = 1）", len(bodies) if bodies else 0)

        # ③ Simulation → CWModelDoc（用 get_com_member，属性/方法自适应）
        addin = get_com_member(sw, "GetAddInObject", SIMULATION_PROGID)
        out("GetAddInObject(SldWorks.Simulation)", "✓" if addin else "✗")
        cosmos = get_com_member(addin, "CosmosWorks") if addin else None
        out("addin.CosmosWorks", "✓" if cosmos else "✗")
        doc = get_com_member(cosmos, "ActiveDoc") if cosmos else None
        out("cosmos.ActiveDoc（CWModelDoc）", "✓" if doc else "✗ None")
        if doc is None:
            print("\n  ⇒ Simulation 未识别该文档 —— 可能加载项未对本会话启用。")
            return 3

        # ④ ★ 建 13 型（拓扑优化）研究 —— 核心验证点
        mgr = get_com_member(doc, "StudyManager")
        out("doc.StudyManager", "✓" if mgr else "✗")
        before = get_com_member(mgr, "StudyCount")
        out("StudyCount（建之前）", before)
        name = "MCP_TOPO_VERIFY_%d" % int(time.time())
        study = get_com_member(mgr, "CreateNewStudy3", name, TOPOLOGY_STATIC, 0, 0)
        out("★ CreateNewStudy3(name, 13, 0, 0)", "✓ 建成" if study else "✗ 返回 None")
        if study is None:
            print("\n  ⇒ 13 型拓扑研究建不出来。")
            return 4
        out("study.Name", get_com_member(study, "Name"))
        out("study.AnalysisType（应 = 13）", get_com_member(study, "AnalysisType"))
        tsm = get_com_member(study, "TopologyStudyManager")
        out("★ study.TopologyStudyManager", "✓ 拿到" if tsm else "✗ None")
        tso = get_com_member(study, "TopologyStudyOptions")
        out("study.TopologyStudyOptions", "✓ 拿到" if tso else "✗ None")

        # ⑤ ★ 目标 + 质量约束（官方教程：MaximizeStiffness + 减重 75%）
        if tsm is not None:
            try:
                get_com_member(tsm, "BeginEdit")
                goal = get_com_member(tsm, "CreateGoal", GOAL_MAXIMIZE_STIFFNESS)
                out("CreateGoal(0=MaximizeStiffness)", goal)
                cm = get_com_member(tsm, "CreateMassConstraint", 0)
                out("CreateMassConstraint(0)", "✓" if cm else "✗ None")
                if cm is not None:
                    get_com_member(cm, "BeginEdit")
                    get_com_member(cm, "SetMassPreference", MASS_PERCENTAGE)
                    get_com_member(cm, "SetValue", 75.0)
                    code = get_com_member(cm, "EndEdit")
                    out("SetMassPreference(1)+SetValue(75.0)+EndEdit", "EndEdit=%r" % (code,))
                code2 = get_com_member(tsm, "EndEdit")
                out("tsm.EndEdit()", "EndEdit=%r" % (code2,))
            except Exception as exc:
                out("约束创建链抛异常", exc)

        out("StudyCount（建之后）", get_com_member(mgr, "StudyCount"))
        out("研究名（供清理）", name)
        print("\n  ⇒ 验证结束。研究随未保存文档一起丢弃。")
        return 0
    finally:
        try:
            if created_title:
                sw.CloseDoc(created_title)
                out("已关闭自建文档（未保存）", "✓")
        except Exception as exc:
            out("关文档失败（请手工关）", exc)
        try:
            sw.CommandInProgress = False
            out("CommandInProgress=False", "✓")
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
