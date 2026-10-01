"""给 `limitations[13]` 加**过期标记**（它的结论已被 [18] 推翻）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（清单收敛）
# 文件:   C:\\swprojects\\sw-skill-fork\\capabilities.yaml 的 `topology_optimization.limitations[13]`
#         依据：`specs/001-topology-result-readout/converge.md`（轮 52）
# 定位:   轮 52 写 001 的 converge 时**核对数字**，发现 `limitations` 里有**两条**提到「结果读取」：
#           · [18] 是轮 50 新加的分级结论（正确）
#           · **[13] 是老的那句「结果读取…**未实现**：反射里**未核到对应成员**，按铁律 5 不编」**
#         **⇒ [13] 与 [18]**直接矛盾****：[18] 证明 `GetPlotCount`/`GetPlotNames` 存在且**运行期已用**、
#         `SavePlotsAseDrawings`/`ExportSimulationStudy` 在反射里存在。
#         **⇒ 成因**：与 003 的 `limitations[15]/[16]` **同一模式** ——
#           **追加式记录不留过期标记**（新条目进来了，旧条目的结论没回头标注）。
#         **⇒ 处置**：[13] **加过期标记、保留原文**（它记录了当时「反射里未核到」这个**真实动作**），
#           并在标记里指向 [18]。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 先证明 JSON 往返逐字节相同；按**事实 61**：只加不删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
CAP = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")

RAW = CAP.read_text(encoding="utf-8")
d = json.loads(RAW)
assert json.dumps(d, ensure_ascii=False, indent=2) + "\n" == RAW, "⚠ 往返不是逐字节相同 ⇒ 停下"
print("  ✓ 往返逐字节相同（%d 字节）" % len(RAW))

caps = d["capabilities"] if isinstance(d.get("capabilities"), list) else list(d["capabilities"].values())
topo = next(c for c in caps if c.get("id") == "topology_optimization")
lim = topo["limitations"]

MARK = ("🕓 **本条已过期（2026-10-01，轮 52 标注）**：它的结论「**反射里未核到对应成员**」"
        "**已被实测推翻** —— 见下面那条「拓扑「结果读取」三件事的实测判定」："
        "`ICWResults.GetPlotCount()` / `GetPlotNames()` **存在且运行期已用**（003 靠它断言到「材料质量1」）、"
        "`SavePlotsAseDrawings` / `ExportSimulationStudy` **在反射里存在**（只是未运行期验）。"
        "**⚠ 但本条的「Export Smoothed Mesh」那一半仍然成立**（六源候选名确实全不存在）。"
        "**保留原文是因为「当时确实没核到」这个动作是真的** —— 错的是把它当成了最终结论。｜ 原文：")

n = 0
for i, s in enumerate(lim):
    if s.startswith("结果读取（Material Mass 图") and not s.startswith("🕓"):
        lim[i] = MARK + s
        n += 1
print("  ✓ 已给 %d 条加过期标记" % n)
if n != 1:
    print("  ✗ 预期 1 条 ⇒ **停下**（按事实 61）")
    raise SystemExit(1)

CAP.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
after = json.loads(CAP.read_text(encoding="utf-8"))
t2 = next(c for c in (after["capabilities"] if isinstance(after.get("capabilities"), list)
                      else after["capabilities"].values()) if c.get("id") == "topology_optimization")
print()
print("  ── 落盘核对 ──")
print("    limitations 条数 → %d" % len(t2["limitations"]))
print("    含过期标记的条数: %d（应 1）" % sum(1 for s in t2["limitations"] if s.startswith("🕓")))
print("    level 仍为: %r（不动）" % t2["level"])
