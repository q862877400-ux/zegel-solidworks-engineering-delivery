"""把「拓扑优化被许可证挡住」这个定论写进 capabilities.yaml。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植）
# 文件:   D:\\AI\\SW\\update_capabilities_license.py
# 定位:   AGENTS.md 停止条件 3「需要用户提供授权或接受缺口 ⇒ 停下报告」的落地：
#         把定论写进清单，使 `topology_optimization` 的 `stitched` 有**可复核的理由**，
#         而不是含糊的「未跑通」。
# 官方签名依据: 不适用（只改清单，不做 COM 调用）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本脚本改的是清单数据；许可是用户侧事项，本脚本不碰注册表、不改许可。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CAPS = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")

REASON = (
    "⛔ **2026-10-01 定论：拓扑优化的求解被**许可证**挡住**，不是代码问题。"
    "真机现象：整链**每一步都通**（见下），但求解时 Simulation 弹「**拓扑算例未获许可。**」"
    "（用户截图确认），`study.Results` 为空。"
    "而 `RunAnalysis` **仍返回 0**（本项目记录的**第四个**「返回码撒谎」）。"
)

LICENSE_FACTS = (
    "许可证依据（只读核查，未改任何注册表）："
    "`HKCU:\\Software\\SolidWorks\\Licenses\\2026` 下只有 "
    "`DriveWorksXpress` / `DFMXpress` / `SimulationXpress` / `FloXpress` "
    "—— **全是各家的 Xpress 简化版**，没有 `SOLIDWORKS Simulation Professional/Premium`；"
    "**而拓扑优化是 Professional/Premium 才有的功能**。"
    "拓扑模块的**文件是装了的**（`Simulation\\Topology\\code\\bin\\abqsmabas*.dll` 等），"
    "**缺的是许可**。"
)

CHAIN_EVIDENCE = (
    "⚑ 2026-10-01 闭环里**除求解外每一步都真机通过**（探针 `probe_topology_loop.py`）："
    "① 单实体板 100×60×20 mm；② 材料 `'solidworks materials|AISI 1020|2'` ✓；"
    "③ `CreateNewStudy3(name, 13, 0, out_i4())` 建拓扑研究、`AnalysisType == 13` ✓"
    "（入口 `CreateNewStudy3`，未走降级）；"
    "④ 目标与约束 `{goal: True, mass_constraint: True, mass_constraint_reused: True}` ✓"
    "（**复用了目标自带的质量约束**，避开 `EndEdit` 错误 7）；"
    "⑤ 夹具 选区=1 ✓；⑥ 载荷 选区=1、`LoadsAndRestraintsManager.Count = 2` ✓；"
    "⑦ `CreateMesh = 0`、**85,748 个单元**、1 秒 ✓；"
    "⑧ `RunAnalysis = 0`、39 秒（**返回码不可信**）；"
    "⑨ `study.Results` 非空 = **False** ⇒ 因「未获许可」。"
)

NEED = (
    "✅ **需要用户提供的东西**：`SOLIDWORKS Simulation Professional` 或 `Premium` 许可"
    "（或单独含拓扑优化的许可）。**在此之前，本能力无法在本机升到 `verified`**，"
    "且这不影响 `stitched` 之下的**每一段已分别真机验证**这一事实。"
)


def main() -> int:
    data = json.loads(CAPS.read_text(encoding="utf-8"))
    hit = False
    for cap in data["capabilities"]:
        if cap["id"] != "topology_optimization":
            continue
        hit = True
        cap["level"] = "stitched"
        cap["verified_versions"] = []
        lim = cap.setdefault("limitations", [])
        lim[:] = [x for x in lim if "未获许可" not in x and "许可证" not in x]
        cap["limitations"] = [REASON, LICENSE_FACTS, CHAIN_EVIDENCE, NEED] + lim
        dep = cap.setdefault("dependencies", [])
        for d in ("SOLIDWORKS Simulation Professional/Premium 许可（拓扑优化所需）",):
            if d not in dep:
                dep.append(d)
        print("  %s: level=%s  limitations=%d 条  dependencies=%d 条"
              % (cap["id"], cap["level"], len(cap["limitations"]), len(dep)))
    if not hit:
        print("  ⚠ 未找到 topology_optimization 条目")
        return 1
    CAPS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
