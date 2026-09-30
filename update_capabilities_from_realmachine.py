r"""@brief 按 2026-10-01 的真机结果更新 capabilities.yaml 的两个条目。

**只改事实，不抬等级**（AGENTS.md A7：全文不得把 source_verified / stitched 写成 verified）：
- `simulation_and_fea`：`level` 保持 `verified` —— 那个 `verified` 指的是 CalculiX/Elmer
  那条链（`verified_versions: ["CalculiX 2.23"]`，有 pytest 证据），**本次不碰它**；
  但它的 `solidworks-simulation-adapter` 后端此前是坏的，须如实记进 limitations。
- `topology_optimization`：`level` 保持 `stitched` —— 真机只走到「研究建成」，
  `set_topology_goal` 仍失败 ⇒ **整链未跑通，不得升 verified**（A7 与停止条件 6）。
  把真机证据与失败点如实写进 limitations / evidence。

# ── 来源 ──
# 仓库:   本项目自身（状态清单的事实回写）
# 文件:   D:\AI\SW\update_capabilities_from_realmachine.py
# 定位:   AGENTS.md 验收 A4/A7 的对应动作：`verified` 必须有我们自己的运行证据；
#         本次真机跑出「研究建成但目标设置失败」，故只更新证据、不动等级。
# 官方签名依据: 不适用（本脚本只改状态清单，不碰 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(r"C:\swprojects\sw-skill-fork")
YAML = REPO / "capabilities.yaml"

SIM_LIMITATION = (
    "⚠ 2026-10-01 真机发现的**潜伏缺陷（已修）**：本条目下的 `solidworks-simulation-adapter` 后端"
    "（`sw_simulation.create_static_study` / `apply_fixed_restraint` / `apply_normal_force`）"
    "此前把官方 `Int32&` 出参按裸值传入，在 SolidWorks 2026 SP4.1 上**必然抛类型不匹配** ⇒ "
    "该后端在修复前从未真正跑通过，而它当时已被本条目的 verified 覆盖 —— 声明跑在事实前面。"
    "修复后真机复验：`create_static_study` ✓ 返回 (study, 'CreateNewStudy3', 0)；"
    "`create_mesh` / `run_analysis` ✓。**尚有一步未通**：`apply_fixed_restraint` 在有效选区下仍返回 None"
    "（选区已由 `sw_part._select_by_id` 选好、计数为 1，故疑为语义问题而非类型问题）。"
    "⇒ 该后端的完整静力学链**尚未**端到端跑通，不得据本条目的 verified 推定它可用。"
)
SIM_EVIDENCE_NEW = (
    "2026-10-01 真机（SW 2026 SP4.1 / 34.4.1）：create_static_study + create_mesh + run_analysis 通过；"
    "apply_fixed_restraint 仍失败（见 limitations）"
)

TOPO_LIMITATION = (
    "⚠ 2026-10-01 真机首验（SW 2026 SP4.1 / 34.4.1）：**研究建成** ✓ "
    "`CreateNewStudy3(name, 13, 0, out_i4())` 返回对象、`AnalysisType == 13`；"
    "`get_topology_study_manager` / `get_topology_study_options` ✓；"
    "`list_topology_constraints_and_controls` / `collect_topology_evidence` ✓。"
    "**但整链未跑通**：`set_topology_goal` 里 `CreateFactorOfSafetyConstraint` 返回 None；"
    "`set_topology_iteration_options` 抛 `服务器出现意外情况 (0x80010105)`；"
    "且官方要求的「看结果（Material Mass 图 / View Convergence Data and Graph / Export Smoothed Mesh）」"
    "尚未实现。⇒ 维持 `stitched`：**不得升 verified**（A7 + 停止条件 6）。"
)
TOPO_EVIDENCE_NEW = (
    "2026-10-01 真机：CreateNewStudy3(13 型) ✓ / AnalysisType=13 ✓ / 管理器与选项可取 ✓ / "
    "证据采集函数 ✓；目标与迭代选项设置 ✗（见 limitations）"
)


def main() -> int:
    text = YAML.read_text(encoding="utf-8")
    data = json.loads(text)
    changed = 0
    for cap in data["capabilities"]:
        if cap["id"] == "simulation_and_fea":
            lims = cap.setdefault("limitations", [])
            if not any("潜伏缺陷（已修）" in x for x in lims):
                lims.append(SIM_LIMITATION)
            ev = cap.setdefault("evidence", [])
            if SIM_EVIDENCE_NEW not in ev:
                ev.append(SIM_EVIDENCE_NEW)
            changed += 1
        elif cap["id"] == "topology_optimization":
            lims = cap.setdefault("limitations", [])
            lims[:] = [x for x in lims if "未在本机实测" not in x]
            if not any("真机首验" in x for x in lims):
                lims.append(TOPO_LIMITATION)
            ev = cap.setdefault("evidence", [])
            if TOPO_EVIDENCE_NEW not in ev:
                ev.append(TOPO_EVIDENCE_NEW)
            changed += 1
    if changed:
        YAML.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  已更新 %d 个条目" % changed)
    for cap in data["capabilities"]:
        if cap["id"] in ("simulation_and_fea", "topology_optimization"):
            print("  %-24s level=%s  limitations=%d  evidence=%d"
                  % (cap["id"], cap["level"], len(cap.get("limitations", [])), len(cap.get("evidence", []))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
