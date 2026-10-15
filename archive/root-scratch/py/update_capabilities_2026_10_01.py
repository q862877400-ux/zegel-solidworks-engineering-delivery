"""把 simulation_and_fea 与 topology_optimization 的等级与限制更新为 2026-10-01 实测结论。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植）
# 文件:   D:\\AI\\SW\\update_capabilities_2026_10_01.py
# 定位:   把 `docs/A9-solve-attempts.md` 里记录的真机结论写进 capabilities.yaml。
#         AGENTS.md 判据 A4：`verified` 必须有我们自己的运行证据。
# 官方签名依据: 不适用（只改清单，不做 COM 调用）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本脚本改的是清单数据，不是能力实现；它自己不产生运行证据。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CAPS = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
DB_NAME = '"SOLIDWORKS Materials"'
MAT_NAME = '"AISI 1020"'
FILE_NAME = '"solidworks materials"'

SIM_EVIDENCE = (
    "⚑ 2026-10-01 **整链真机跑通**（SW 2026 SP4.1 / 34.4.1，100×60×20 mm 单实体板）："
    "赋材料（`SetMaterialPropertyName2`，库名 " + DB_NAME + " + 材料 " + MAT_NAME + "）→ "
    "按面坐标选面（`SelectByID2('', 'FACE', x, y, z, …)`）→ 夹具 → 载荷（`Count = 2`）→ "
    "`CreateMesh`（**7,310 个单元**）→ `RunAnalysis` → **`study.Results` 非空、"
    "`GetPlotCount = 4`、`GetPlotNames = ('品质1','应力1','位移1','应变1')`**，全程 **1 秒**。"
    "证据与逐次尝试记录：工作区 `docs/A9-solve-attempts.md`；探针 `probe_full_chain.py`。"
)

SIM_LIMITS = [
    "⚠ **`RunAnalysis` 返回 0 不代表求解成功**（真机：夹具/载荷未定义时返回 0，"
    "而 Simulation 弹「未定义载荷或规定的位移」且研究显示失败）"
    "⇒ **判据必须是 `study.Results` 非空 + 图数**。",
    "⚠ **材料库名必须是 " + DB_NAME + "**（显示名），不是 `.sldmat` 文件名 " + FILE_NAME + "；"
    "且 **`\"Plain Carbon Steel\"` 不在该库里**（用了会静默失败）⇒ 判据是回读 `MaterialIdName`。",
    "⚠ 本期**只测了平面**用点定位选中；曲面/圆柱面的点定位行为未实测。",
]

TOPO_EVIDENCE = (
    "⚑ 2026-10-01 拓扑研究的**前段**真机跑通：`CreateNewStudy3(name, 13, 0, out_i4())` 建拓扑研究"
    "（`AnalysisType == 13`）、`CreateGoal(0/1)` 自带一个质量约束"
    "（故 `CreateMassConstraint` 会因重复而使 `EndEdit` 返回 7 = "
    "`swsTopoErrCode_OnlyOneMassConstraintCanBeDefined`）、夹具/载荷/网格/求解的"
    "**同一套调用形状已由静力学研究实测通过**（见 `simulation_and_fea` 的证据）。"
)

TOPO_LIMITS = [
    "⚑ 2026-10-01：**求解之前的全部 7 步**已真机打通（建研究 → 目标 → 约束 → 夹具 → 载荷 → "
    "网格 → 赋值），且网格参数的真因已定（`CreateMesh(NUnits, DElementSize, DTolerance)`，"
    "后两参单位是**毫米**；早期按 `(meshType, tolerance, size)` 传导致 1950 万单元 / 20–25 GB）。"
    "**⇒ 但拓扑研究的完整闭环（目标 + 约束 + 求解 + 看结果）仍未在一次连续运行里跑通。**",
]


def main() -> int:
    data = json.loads(CAPS.read_text(encoding="utf-8"))
    touched = []
    for cap in data["capabilities"]:
        if cap["id"] == "simulation_and_fea":
            cap["level"] = "verified"
            cap["verified_versions"] = ["2026"]
            lim = cap.setdefault("limitations", [])
            lim[:] = [x for x in lim if not x.startswith("⚑ 2026-10-01")]
            cap["limitations"] = [SIM_EVIDENCE] + SIM_LIMITS + lim
            touched.append((cap["id"], cap["level"], len(cap["limitations"])))
        elif cap["id"] == "topology_optimization":
            cap["level"] = "stitched"
            cap["verified_versions"] = []
            lim = cap.setdefault("limitations", [])
            lim[:] = [x for x in lim if not x.startswith("⚑ 2026-10-01")]
            cap["limitations"] = [TOPO_EVIDENCE] + TOPO_LIMITS + lim
            touched.append((cap["id"], cap["level"], len(cap["limitations"])))

    CAPS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for cid, lvl, n in touched:
        print("  %-24s level=%-14s limitations=%d 条" % (cid, lvl, n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
