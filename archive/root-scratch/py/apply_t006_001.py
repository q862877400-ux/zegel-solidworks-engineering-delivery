"""T-006：把 001 的 T-004/T-005/T-010 结论按**证据强度**写进 `limitations`。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（清单收敛）
# 文件:   C:\\swprojects\\sw-skill-fork\\capabilities.yaml 的 `topology_optimization.limitations`
#         依据：`specs/001-topology-result-readout/tasks.md` 的 T-004/T-005/T-010
# 定位:   轮 50 把 001 的三个静态任务做完，结论是**推翻了 spec 的一个前提**：
#         spec 说「这三件事在公开 API 里**可能不存在**」，实际是：
#           ① Material Mass 图 —— **可读且运行期已证**（003 的 `GetPlotNames`）
#           ② 导出结果图为图片 —— **反射里存在** `ICWResults.SavePlotsAseDrawings(String,String,String)`
#           ③ 导出研究 —— **反射里存在** `ICWStudy.ExportSimulationStudy(...)`
#           ④ 导出**平滑网格** —— **确实不存在**（六个候选名全无）
#         ⚠ ②③ **只有一源（反射）** ⇒ 按**事实 28/30**（「反射里有」≠「运行期调用得到」）
#           **不能声称「可导出」**，只能记「反射里存在、运行期未验」。
#         ⚠ 原 `limitations` 里那句「**导出类结果** 四源均未查到」**把 ②③④ 混为一谈** ⇒ 分解修正。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 先证明 JSON 往返逐字节相同再改；按**事实 61**跑完看 `git diff --stat`。
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
assert json.dumps(d, ensure_ascii=False, indent=2) + "\n" == RAW, \
    "⚠ JSON 往返不是逐字节相同 ⇒ 停下"
print("  ✓ 往返逐字节相同（%d 字节）" % len(RAW))

caps = d["capabilities"] if isinstance(d.get("capabilities"), list) else list(d["capabilities"].values())
topo = next(c for c in caps if c.get("id") == "topology_optimization")
lim = topo["limitations"]

# ── ① 给旧的那句「导出类结果…四源均未查到」加**分解指向**（不删原文）
OLD_KEY = "**导出类结果**"
n = 0
for i, s in enumerate(lim):
    if OLD_KEY in s and "见下条分解" not in s and "🕓" not in s:
        lim[i] = (s.rstrip()
                  + " 🕓 **2026-10-01（轮 50）分解修正**：本条把三件事混成了一件 —— "
                    "**「导出结果图」与「导出研究」在反射里**存在**（见下面新增的那条），"
                    "只有「导出**平滑网格**」才是真查不到。**原文保留。**")
        n += 1
print("  ✓ ① 给 %d 条旧记录加了分解指向" % n)

# ── ② 追加 T-004/T-005/T-010 的结论（**按证据强度分级**）
NEW = (
    "🔎 **拓扑「结果读取」三件事的**实测判定****（2026-10-01 轮 50，"
    "做完 `specs/001-topology-result-readout/tasks.md` 的 T-004/T-005/T-010）——"
    "**按证据强度分级，不混为一谈**："
    "① **Material Mass 图：✅ 可读，且运行期已证**。入口是 `ICWResults.GetPlotCount()` / "
    "`GetPlotNames()` / `GetPlot(Int32&)`；003 的闭环正是靠它断言到 `材料质量1` "
    "（证据 `output/topology-evidence.json` 的 `steps.material_mass_plot`）。"
    "② **导出结果图为图片：⚠ 反射里存在、运行期未验**。"
    "`ICWResults.SavePlotsAseDrawings(String, String, String) → Int32`。"
    "**⚠ 只有一源（反射 `D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt` L2270），"
    "没有独立的 CHM/官方页** ⇒ 按已知事实 28/30（**「反射里有」≠「运行期调用得到」**）"
    "**不得声称「可导出」**，只能记「存在、未验」。"
    "③ **导出研究：⚠ 同上（反射里有、未验）**。"
    "`ICWStudy.ExportSimulationStudy(String, String, Int32×5) → Int32`（同源 L2539）。"
    "④ **导出平滑网格：✗ 确实查不到**。「六源候选名」（`ExportSmoothedMesh` / `GetSmoothedMesh` / "
    "`ExportSmoothedMesh2` / `ViewConvergenceData` / `MaterialMass` / `GetMaterialMassPlot`）"
    "在 `ICWResults` 的 **107 个成员**里**一个都没有** ⇒ 按铁律 5 记「查不到」。"
    "⑤ **收敛/步数数据：⚠ 反射里有、未验**。`ICWResults.GetMaximumAvailableSteps()` / "
    "`GetTimeOrFrequencyAtEachStep(Int32, Int32&)`（同源 L2214 / L2262）。"
    "**▶ 可重跑枚举命令**（本条的每条结论都由它得出）："
    "`python -c \"from pathlib import Path;"
    "L=Path(r'D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt').read_text(encoding='utf-8').splitlines();"
    "s=next(i for i,x in enumerate(L) if x.strip()=='## ICWResults');"
    "e=next(i for i,x in enumerate(L) if x.strip()=='## ICWResultsProbeManager');"
    "print(len([x for x in L[s:e] if x.strip() and not x.startswith('#')]))\"` "
    "（⇒ 打印 **107**，即 `ICWResults` 的成员数）。"
    "⚠ **本轮**没有**真机调用 ②③⑤** —— 它们需要一次完整求解（约 3 分钟 + 许可），"
    "**不打勾、不声称已验证**。"
)
if not any("拓扑「结果读取」三件事的" in s for s in lim):
    lim.append(NEW)
    print("  ✓ ② 已追加 T-004/T-005/T-010 的分级结论")
else:
    print("  ⚠ ② 该条已存在")

CAP.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
after = json.loads(CAP.read_text(encoding="utf-8"))
t2 = next(c for c in (after["capabilities"] if isinstance(after.get("capabilities"), list)
                      else after["capabilities"].values()) if c.get("id") == "topology_optimization")
print()
print("  ── 落盘核对 ──")
print("    limitations 条数 → %d" % len(t2["limitations"]))
print("    level 仍为: %r（**不动**）" % t2["level"])
print("    含分级结论: %s" % any("拓扑「结果读取」三件事的" in s for s in t2["limitations"]))
print("    含分解指向: %s" % any("分解修正" in s for s in t2["limitations"]))
