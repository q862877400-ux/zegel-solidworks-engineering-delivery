"""拓扑优化闭环达成 → 升 `verified`；两条 evidence 改为**可跑的命令**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（清单更新，非第三方移植）
# 文件:   D:\\AI\\SW\\upgrade_topology_verified.py
# 定位:   AGENTS.md 判据 A4「`verified` 必须有我们自己的运行证据」与 A9
#         「空白域护城河有可跑的工程实现」的落地。
# 官方签名依据: 不适用（只改清单，不做 COM 调用）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本脚本只改清单数据；证据由 `tools/capture_*_evidence.py` 真机产出。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CAPS = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")

TOPO_EVIDENCE = (
    "⚑ 2026-10-01 **拓扑优化完整闭环真机跑通**（SW 2026 SP4.1 / 34.4.1，100×60×20 mm 单实体板）："
    "建拓扑研究（`CreateNewStudy3(name, 13, 0, …)`，`AnalysisType == 13`，未走降级）→ "
    "目标+质量约束（复用目标自带约束，`EndEdit` = **0** 成功）→ 夹具（选区计数 1）→ "
    "载荷（选区计数 1，`LoadsAndRestraintsManager.Count == 2`）→ "
    "`CreateMesh`（**85,748 个单元**，1 秒）→ `RunAnalysis`（187 秒）→ "
    "**`study.Results` 非空、`GetPlotCount == 2`、"
    "`GetPlotNames == ('品质1', '材料质量1')`** —— **`材料质量1` 即 Material Mass 结果图**。"
    "证据文件（含逐步 JSON 与时间戳）：`output/topology-evidence.json`。"
)

TOPO_LIMITS = [
    "⚑ **验收命令**（可复跑；需含拓扑优化的 Simulation 许可）："
    "`python tools/capture_topology_evidence.py` ⇒ 期望 `verdict: pass`。",
    "⚠ **需要许可**：拓扑优化需 `SOLIDWORKS Simulation Professional/Premium`。"
    "本机原先只有 `SimulationXpress`，求解时弹「拓扑算例未获许可」、`Results` 为空，"
    "而 `RunAnalysis` **仍返回 0**；2026-10-01 用户在 SolidNetWork License Manager 中调整并"
    "**重启 SolidWorks** 后解除（许可在启动时签出，改设置后必须重启）。",
    "⚠ **`RunAnalysis` 返回 0 不代表成功**（本项目累计五处「返回码撒谎」之一）"
    "⇒ 判据必须是 `study.Results` 非空 + 图数。",
    "⚠ **不要用真假值判成功码**：`set_topology_goal` 的 `goal` 是 `EndEdit` 返回码、"
    "**成功为 `0`**，而 `bool(0)` 为 `False` ⇒ 曾把成功判成失败。"
    "判据一律显式比 `0` 或用 `is not None`。",
    "⚠ 本期只验了**单实体零件**（官方硬约束：拓扑优化只能对单实体零件做）。"
    "多实体零件/装配体需先另存为零件，未验。",
    "⚠ **导出类结果**（`Export Smoothed Mesh` / 收敛数据曲线）仍未实现 —— "
    "四源（接口清单 / DLL / CHM / 运行期 `GetIDsOfNames`）均未查到可调用的公开方法；"
    "官方只在界面流程里有说明。按铁律 5 记为查不到，不猜。",
]

SIM_EVIDENCE_NEW = (
    "pytest tests/test_fea_analysis.py（CalculiX / Elmer 求解链）",
    "**可跑的真机证据**：`python tools/capture_simulation_evidence.py` "
    "（2026-10-01 起；期望 `verdict: pass`，证据落 `output/simulation-evidence.json`）",
    "⚑ 2026-10-01 真机整链（SW 2026 SP4.1 / 34.4.1，100×60×20 mm 单实体板）："
    "赋材料 → 按**面坐标**选面 → 夹具 → 载荷（`Count == 2`）→ `CreateMesh`（**7,310 个单元**）→ "
    "`RunAnalysis`（1 秒）→ **`study.Results` 非空、`GetPlotCount == 4`、"
    "`GetPlotNames == ('品质1','应力1','位移1','应变1')`**。**已复现两次。**",
)


def main() -> int:
    data = json.loads(CAPS.read_text(encoding="utf-8"))
    done = []
    for cap in data["capabilities"]:
        if cap["id"] == "topology_optimization":
            cap["level"] = "verified"
            cap["verified_versions"] = ["2026"]
            lim = cap.setdefault("limitations", [])
            lim[:] = [x for x in lim if "未获许可" not in x
                      and not x.startswith("⛔ **2026-10-01 定论")
                      and "许可证依据" not in x]
            cap["limitations"] = [TOPO_EVIDENCE] + TOPO_LIMITS + lim
            cap["evidence"] = [
                "python tools/capture_topology_evidence.py（真机闭环，落 output/topology-evidence.json）",
                "pytest tests/test_sw_topology_contract.py（8 条契约测试，无 COM）",
            ]
            done.append(("topology_optimization", cap["level"], len(cap["limitations"])))
        elif cap["id"] == "simulation_and_fea":
            cap["evidence"] = list(SIM_EVIDENCE_NEW)
            done.append(("simulation_and_fea", cap["level"], len(cap.get("evidence") or [])))
    CAPS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for cid, lvl, n in done:
        print("  %-24s level=%-14s evidence/limitations 条数=%d" % (cid, lvl, n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
