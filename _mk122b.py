import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(r"D:\AI\SW")

FACT = """| 142 | **拓扑优化整链真机复验通过（`verdict: pass`）** —— 而此前那句「原因在**环境**（需 Simulation 许可证）」是**错归因** —— 2026-10-01（轮 203）。

★★ **起因**：业主说「Simulate 的软件你做了没有，**我已经安装好许可了**」⇒ 去查为何轮 179 起验收是红的。
★★★ **归因链（三轮才到底）**：
```
轮 179 记账：「验收红 = 原因在**环境**」⇒ ★ 这个标签**看起来负责**（承认不是代码退化），
  实际**让人停止追问**：既然"环境/许可"，就等业主装 —— **而业主早就装好了**。
轮 202：查出 `LoadAddIn("SldWorks.Simulation")` 返回 **3**，而 `swLoadAddinError_e` 里
  **3 = swFileNotFound**、**7 = swLicenseError** ⇒ ★ **"需许可证"那半是错的**；
  真因是「**加载项没启用**」（不在 `SOFTWARE\\SolidWorks\\Addins` 下）。
轮 203：持久修复后**真跑整链** ⇒ **pass**。
```
★★★ **实测（`python tools/capture_topology_evidence.py`，SW 2026 SP4.1 / 34.4.1）**：
```
[1] 单实体板 100×60×20 ✓        [2] 材料 'solidworks materials|AISI 1020|2' ✓
[3] 拓扑研究 CreateNewStudy3 / AnalysisType=13 ✓（未走降级）
[4] EndEdit=0 · mass_constraint=True · reused=True · ★ **质量下降 75.0%** ✓
[5] 夹具/载荷选区各 1 · Count=2 ✓
[6] CreateMesh=0 · 单元 **85,748** · 1.6 s ✓
[7] RunAnalysis=0（★ JSON 自己标 `run_analysis_return_is_trustworthy: false`）· Results 非空 · 图数 **2** ✓
[8] ★★ **Material Mass 图 = ['材料质量1']** ✓
⇒ **verdict: pass** · 求解 **228.9 s** · 证据 output/topology-evidence.json
```
★★ **为什么这次的成功可信**：它不是靠"返回 0" —— 脚本自己写明
「**无拓扑许可时：会弹『拓扑算例未获许可』且 Results 为空，而返回码仍为 0**」，
⇒ 而本次拿到了 `Results` 非空 + 图数 2 + `材料质量1` ⇒ ★ **许可确实生效**（业主没装错），
★ 而且**判据自己声明了自己不可信**（`run_analysis_return_is_trustworthy: false`）—— **正面样板**。

⚠⚠ **限度（不夸大）**：
* ⚠ **只跑了拓扑那条** —— 静力学（`tools/capture_simulation_evidence.py`）**没跑**；
* ⚠ 求解 **228.9 s**（不是失败那四次的 20–25 GB / 1000–3000 s）⇒ ★ 本轮 pass **不推翻**那四次"不收敛"，
  也**没解释**它们（网格/参数不同）—— **成因仍未定**；
* ⚠ `LoadAddIn` 是**会话级**的 ⇒ 下次启动 SW 仍要再装一次；
* ⚠ 那份结论错的探针（`probe_simulation_addin_status.py`）**故意留在仓库里**（作"错法的记录"）。

★ **可复用教训**：**给一个问题贴上「环境」标签之前，先证明那个环境条件真的不满足** ——
否则标签本身就是一层"判据没覆盖"，而它与"没问题"长得一样。

**依据**：`output/topology-evidence.json` · `tools/capture_topology_evidence.py` ·
`scripts/sw_simulation.py` 的 `ensure_simulation_addin` · `C:\\swapi\\enums\\swLoadAddinError_e.md` · 事实 141
"""

K = W / "docs" / "known-facts.md"
tk = K.read_text(encoding="utf-8")
if "| 142 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT, encoding="utf-8")
    print("  ok known-facts 已加 142")
print("  校验:", K.read_text(encoding="utf-8").count("| 142 |"), "次")

R = W / "docs" / "ROADMAP.md"
B = """           671 🎯 **Spec Kit `122`：拓扑优化整链****真机复验通过（`verdict: pass`）****（轮 203）** ——
               而此前那句「原因在**环境**（需 Simulation 许可证）」是**错归因**。
               ★ 起因：业主说「Simulate 的软件你做了没有，**我已经安装好许可了**」⇒ 去查为何轮 179 起验收是红的。
            672 ★★★ **归因链（三轮才到底）**：
               ```
               轮 179 记账：「验收红 = 原因在**环境**」⇒ ★ 这个标签**看起来负责**（承认不是代码退化），
                 实际**让人停止追问**：既然"环境/许可"，就等业主装 —— **而业主早就装好了**。
               轮 202：`LoadAddIn("SldWorks.Simulation")` 返回 **3**，而 `swLoadAddinError_e` 里
                 **3 = swFileNotFound** · **7 = swLicenseError** ⇒ ★ **"需许可证"那半是错的**；
                 真因是「**加载项没启用**」（不在 `SOFTWARE\\SolidWorks\\Addins` 下）。
               轮 203：持久修复后**真跑整链** ⇒ **pass**。
               ```
            673 ★★★ **实测（`python tools/capture_topology_evidence.py`，SW 2026 SP4.1 / 34.4.1）**：
               ```
               [1] 单实体板 100×60×20 ✓   [2] 材料 'solidworks materials|AISI 1020|2' ✓
               [3] 拓扑研究 CreateNewStudy3 / AnalysisType=13 ✓（未走降级）
               [4] EndEdit=0 · mass_constraint=True · reused=True · ★ **质量下降 75.0%** ✓
               [5] 夹具/载荷选区各 1 · Count=2 ✓
               [6] CreateMesh=0 · 单元 **85,748** · 1.6 s ✓
               [7] RunAnalysis=0（★ JSON 自标 `run_analysis_return_is_trustworthy: false`）·
                   Results 非空 · 图数 **2** ✓
               [8] ★★ **Material Mass 图 = ['材料质量1']** ✓
               ⇒ **verdict: pass** · 求解 **228.9 s** · 证据 output/topology-evidence.json
               ```
            674 ★★ **为什么这次的成功可信**：不是靠"返回 0" —— 脚本自己写明
               「**无拓扑许可时：会弹『拓扑算例未获许可』且 Results 为空，而返回码仍为 0**」，
               而本次拿到 `Results` 非空 + 图数 2 + `材料质量1` ⇒ ★ **许可确实生效**（业主没装错），
               ★ 且**判据自己声明了自己不可信** —— **正面样板**。
            675 ★★ **可复用教训**：**给一个问题贴上「环境」标签之前，先证明那个环境条件真的不满足** ——
               否则标签本身就是一层"判据没覆盖"，而它与"没问题"长得一样。
               ⚑ **限度（不夸大）**：⚠ **只跑了拓扑那条**，静力学没跑；
                 ⚠ 求解 **228.9 s**（不是失败那四次的 20–25 GB / 1000–3000 s）⇒
                   本轮 pass **不推翻**那四次"不收敛"，也**没解释**它们（网格/参数不同）—— **成因仍未定**；
                 ⚠ `LoadAddIn` 是**会话级**的 ⇒ 下次启动 SW 仍要再装一次；
                 ⚠ 那份结论错的探针**故意留在仓库里**（作"错法的记录"）。
               门禁 + `release_check` exit 0 · 全量回归 **1260 passed / 17 skipped**。
               下轮候选：① ★ **挂柜台**（孤立能力 **302** 个；探针只印前 30 ⇒ **要先把全量清单做出来**）；
               ② 跑静力学那条（`tools/capture_simulation_evidence.py`）；
               ③ B 级并入本体（范围口径已清）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None
before = "".join(lines)
if re.search(r"^\s+671 ", before, re.M):
    print("  游标 671 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+675 ", R.read_text(encoding="utf-8"), re.M)
    print("  复核: 675 行已存在 ✓")
