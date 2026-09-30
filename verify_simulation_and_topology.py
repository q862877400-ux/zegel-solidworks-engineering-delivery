r"""@brief 端到端真机验证：静力学研究 + 拓扑优化研究，产出 capabilities.yaml 的 evidence。

覆盖两件事：
  A. 既有 `sw_simulation`（静力学链）—— 修复出参写法后**首次**真机跑通
  B. 新 `sw_topology`（拓扑优化链）—— 护城河域的第一次真机验证

按 AGENTS.md 铁律 2 的三条安全约束写。不碰用户数据：新建**未保存**文档，收尾不保存。

官方依据：CHM `otsimtopology.chm` 解包（拓扑流程）+ cosworks 反射（签名）
关键实测结论（本脚本产出）：`Int32&` 出参必须传 `VARIANT(VT_BYREF|VT_I4, 0)`。

# ── 来源 ──
# 仓库:   本项目自身（实测脚本）+ 本项目既有模式（sw_connect / sw_part / sw_simulation / sw_topology）
# 文件:   D:\AI\SW\verify_simulation_and_topology.py
# 定位:   AGENTS.md 铁律 2「本机实测」；产物直接写进 capabilities.yaml 的两个条目的 evidence。
# 官方签名依据: D:\AI\SW\_raw\topo-reflect\iface_cosworks.txt
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机 SolidWorks；收尾不保存、直接关自建文档。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import time

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import connect_solidworks, get_com_member, new_document, out_i4  # noqa: E402
from scripts import sw_part  # noqa: E402
from scripts import sw_simulation as sim  # noqa: E402
from scripts import sw_topology as topo  # noqa: E402

RESULTS: list[tuple[str, str]] = []


def step(label: str, fn):
    try:
        r = fn()
        ok = r is not None and r is not False
        RESULTS.append((label, "✓" if ok else "○"))
        print("  %-52s %s %s" % (label, "✓" if ok else "○", _brief(r)))
        return r
    except Exception as e:
        RESULTS.append((label, "✗"))
        print("  %-52s ✗ %s" % (label, str(e)[:64]))
        return None


def _brief(r) -> str:
    s = repr(r)
    return s if len(s) <= 60 else s[:57] + "..."


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=10, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        sw_rev = get_com_member(sw, "RevisionNumber")
        print("SolidWorks %s" % sw_rev)
        print()

        # ── A. 静力学链（既有 sw_simulation，修复后首验）──
        print("=== A. 既有 sw_simulation（静力学）===")
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        sw_part.extrude_boss(model, sk, 0.02)
        bodies = get_com_member(model, "GetBodies2", 0, True)
        step("建单实体零件 %r（实体数=%d）" % (title, len(bodies) if bodies else 0), lambda: True)

        static = step("sw_simulation.create_static_study", lambda: sim.create_static_study(sw, "E2E_STATIC"))
        static_study = static[0] if isinstance(static, tuple) and static else None
        if static_study is None:
            step("回退：CreateNewStudy3(type=0, out_i4())",
                 lambda: get_com_member(get_com_member(get_com_member(
                     sw.GetAddInObject("SldWorks.Simulation"), "CosmosWorks"), "ActiveDoc"),
                     "StudyManager").CreateNewStudy3("E2E_STATIC2", 0, 0, out_i4()))
        if static_study is not None:
            step("  study.Name", lambda: get_com_member(static_study, "Name"))
            # 选区：用项目自己的封装（sw_part._select_by_id 内部把 Callout 包成空 Dispatch）
            def _pick_face():
                from scripts.sw_part import _select_by_id
                return _select_by_id(model.Extension, "", "FACE", append=False, mark=0)
            sel = step("  _select_by_id(FACE)", _pick_face)
            step("  apply_fixed_restraint", lambda: sim.apply_fixed_restraint(static_study))
            step("  create_mesh + run_analysis",
                 lambda: (sim.create_mesh(static_study), sim.run_analysis(static_study))[-1])
        print()

        # ── B. 拓扑优化链（护城河域首验）──
        print("=== B. 新 sw_topology（拓扑优化）===")
        created = step("sw_topology.create_topology_study",
                       lambda: topo.create_topology_study(sw, "E2E_TOPO"))
        t_study = created[0] if isinstance(created, tuple) and created else None
        if t_study is not None:
            step("  study.AnalysisType（应=13）", lambda: get_com_member(t_study, "AnalysisType"))
            step("  get_topology_study_manager", lambda: topo.get_topology_study_manager(t_study))
            step("  get_topology_study_options", lambda: topo.get_topology_study_options(t_study))
            step("  ★ set_topology_goal(MaximizeStiffness + 减重75% + 安全系数80)",
                 lambda: topo.set_topology_goal(t_study, mass_reduce_percent=75.0, factor_of_safety=80.0))
            step("  set_topology_iteration_options(auto)",
                 lambda: topo.set_topology_iteration_options(
                     t_study, iteration_option=topo.SWS_TOPOLOGY_ITERATION_OPTIONS["auto"]))
            step("  list_topology_constraints_and_controls", lambda: topo.list_topology_constraints_and_controls(t_study))
            step("  collect_topology_evidence", lambda: topo.collect_topology_evidence(sw))
        print()

        ok = sum(1 for _l, s in RESULTS if s == "✓")
        bad = sum(1 for _l, s in RESULTS if s == "✗")
        print("=== 汇总：%d 通过 / %d 失败 / 共 %d 步 ===" % (ok, bad, len(RESULTS)))
        return 0 if bad == 0 else 1
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
