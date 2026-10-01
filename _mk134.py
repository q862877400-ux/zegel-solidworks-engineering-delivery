import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(r"D:\AI\SW")
S = W / "specs" / "134-static-simulation-reverified"
S.mkdir(parents=True, exist_ok=True)

(S / "spec.md").write_text("""# Feature Specification: 静力学仿真整链**真机复验**

**Feature Branch**: `134-static-simulation-reverified` · **Created**: 2026-10-01 · **Status**: Implemented

**Input**: 队列 B1（`docs/backlog-8h.md`）—— 把 `simulation_and_fea` 的真机验收重跑一遍。

## 来源（§I / §IV）
| 需求 | 来源 | license |
|---|---|---|
| 重跑既有验收脚本 `tools/capture_simulation_evidence.py` | **本项目自身**（既有真机证据脚本，非新写）| 本仓库 **MIT** |
| 加载项可达性 | 事实 141 / 142 的修复（`ensure_simulation_addin`）| 本项目 **MIT** |

## User Scenarios & Testing

### User Story 1 - 确认静力学那条链也能跑绿（Priority: P1）
拓扑那条已在 `122` 复验 pass；静力学是**另一条链**（`ICWStudy` + 夹具/载荷 + 求解 + 4 张图），
需要单独确认 —— ★ 不能因为"同一根因"就推断它也通（**别用邻接关系代替证据**，事实 143）。

**Independent Test**: 单独跑 `python tools/capture_simulation_evidence.py`，看它自己的 `verdict`。

**Acceptance Scenarios**:
1. **Given** SW 2026 SP4.1 已连、加载项已由 `ensure_simulation_addin` 装上，
   **When** 跑该脚本，**Then** `verdict == "pass"` 且 JSON 里六步全 `ok`
2. **Given** 求解完成，**When** 读 `plot_names`，**Then** 含 `应力*` / `位移*` / `应变*`（而不是只有"品质"）
3. **Given** 该 JSON，**When** 看 `run_analysis_return_is_trustworthy`，**Then** 为 **`false`**
   —— ★ 即：**成功判据不是返回码**

## 明确不做
| 不做 | 理由 |
|---|---|
| 改这条链的任何代码 | 它本来就工作；本轮**只复跑取证据** |
| 声称"求解器不收敛"问题已解决 | ★ 那是另一件事（事实 142 已记：**成因仍未定**）|
""", encoding="utf-8")

(S / "plan.md").write_text("""# Implementation Plan: 静力学真机复验

**Branch**: `134-static-simulation-reverified` | **Date**: 2026-10-01 | **Spec**: 同目录 `spec.md`

## Technical Context
**Language/Version**: Python 3.14.7 · **Testing**: 该脚本**不在 pytest 里跑**（需许可，单次约秒级）
**Target Platform**: 本机 SW 2026 SP4.1（34.4.1）· 单实例 COM

## ★ 官方源与裁决顺序（§II）
| 源 | 用途 | 本次 |
|---|---|---|
| `C:\\swapi\\types\\ICWStudy\\*` 等 | 成员语义 | **不引入新 COM 成员**（只复跑既有脚本）⇒ 不适用 |
| 出厂反射 `reflect/enum_cosworks.txt` | 若要看枚举 | 本次未涉及 |

**裁决顺序**：出厂类型库/反射 > `C:\\swapi` markdown。★ 本次无冲突（无新调用）。

## Constitution Check（§I–§V）
| 条 | 判据 | 本次 |
|---|---|---|
| §I 来源 | 每条需求有来源 | ✅ |
| §II 官方源 | 列源 + 裁决序 | ✅（说明"不适用"的理由）|
| §III 查不到 | 附核查命令 | ✅ 见下（本特性**没有**"应该有"式断言）|
| §IV license | 来源行带 license | ✅ |
| §V 可跑验收 | 每条任务带 `→ 验收:` | ✅ |

## Project Structure
```
无代码改动 —— 本特性只跑既有脚本 + 落证据（output/simulation-evidence.json，gitignore 的产物目录）
```
""", encoding="utf-8")

(S / "tasks.md").write_text("""# Tasks: 静力学真机复验

- [x] T-13401 确认只有一个 SolidWorks 实例（事实 24）
  `→ 验收:` `Get-Process -Name SLDWORKS | Select-Object Id`（**恰好 1 个**）
- [x] T-13402 ★ 跑静力学真机验收
  `→ 验收:` `python tools/capture_simulation_evidence.py`（**exit 0 · `verdict: pass`**）
- [x] T-13403 复核判据是**回读**而不是返回码
  `→ 验收:` `python -c "import json;from pathlib import Path;d=json.loads(Path('output/simulation-evidence.json').read_text(encoding='utf-8'));print(d['verdict'], d['steps']['solve']['plot_names'], d['steps']['solve']['run_analysis_return_is_trustworthy'])"`
  （期望 `pass ['品质1','应力1','位移1','应变1'] False`）
- [x] T-13404 全链 + 回归
  `→ 验收:` `python scripts/release_check.py`（exit 0）· `python -m pytest tests -q`（0 failed）
""", encoding="utf-8")

(S / "checklist.md").write_text("""# Checklist: 静力学真机复验

- [x] **单实例** COM（事实 24）
- [x] 收尾：`CommandInProgress=False` + 点掉残留弹窗 + 脚本自建文档自行关闭
- [x] ★ **成功判据是 `Results` 非空 + 图数**，不是 `RunAnalysis` 返回码（该 JSON 自标 `false`）
- [x] ★ **不声称**"求解器不收敛"已解决（那是另一件事）
- [x] 不改任何代码（本特性只取证据）
- [x] 特性目录写完**不再改**（Flow-forward）
""", encoding="utf-8")

(S / "converge.md").write_text("""# Converge: 静力学真机复验

## 结果
| 判据 | 结论 |
|---|---|
| 单实例 | ✅ |
| `verdict` | ✅ **`pass`** |
| 网格 | ✅ 7,310 单元 · 1.6 s |
| 求解 | ✅ Results 非空 · **图数 4** · 0.8 s |
| 图名含应力/位移/应变 | ✅ `['品质1','应力1','位移1','应变1']` |
| 返回码可信性 | ✅ JSON 自标 **不可信** ⇒ 判据是回读 |

## ★ 未查证（逐条）
* ⚠ **"求解器不收敛"那四次（20–25 GB / 1000–3000 s）的成因仍未定** ——
  本轮的 pass **不推翻**它们，也**没解释**它们（网格/参数不同）；
* ⚠ 本特性**没有**改任何代码 ⇒ 它的价值是"**取到一份当前的、可复跑的绿证据**"，
  而不是修好了什么；
* ⚠ 只跑了**板**这个最简工况（100×60×20 单实体）⇒ 复杂几何未验。
""", encoding="utf-8")

FACT = """| 145 | **静力学仿真整链真机复验也 `pass`** —— 与拓扑**同一根因治好**，而两条链**各自独立取证** —— 2026-10-01（轮 205 / Spec Kit `134`）。

★★ **实测（`python tools/capture_simulation_evidence.py`，SW 2026 SP4.1 / 34.4.1）**：
```
[1] 零件 '零件2' 100×60×20 ✓   [2] 材料 'solidworks materials|AISI 1020|2' ✓   [3] 静力学研究 = True ✓
[4] 夹具选区=1 载荷选区=1 Count=2 ✓
[5] CreateMesh=0 · 单元 **7,310** · 1.6 s ✓
[6] RunAnalysis=0（★ JSON 自标 `run_analysis_return_is_trustworthy: false`）·
    Results 非空 · **图数 4** = ['品质1','应力1','位移1','应变1'] ✓
⇒ **verdict: pass** · 求解 **0.8 秒** · 证据 output/simulation-evidence.json
```
★★★ **为什么两条链要**各自**取证**：拓扑（`122`）与静力学（本特性）**不是同一条链** ——
前者走 `ICWTopology*` + 目标/约束，后者走 `ICWStudy` + 夹具/载荷 + 4 张图。
★ 虽然根因（加载项没启用，事实 141）相同，**但"同一根因"不等于"结果必然相同"** ——
这正是事实 143 那条教训的另一面：**别用邻接关系代替证据**（这次是反过来用它去要求取证）。

★ 判据仍是**回读**而不是返回码：脚本自己在 JSON 里标了 `run_analysis_return_is_trustworthy: false`，
而成功判据是 `Results` 非空 + 图数 > 0 ⇒ ★ **判据声明自己不可信**（正面样板，同事实 142）。

⚠ **限度**：⚠ **"求解器不收敛"那四次（20–25 GB / 1000–3000 s）的成因仍未定** ——
本轮 pass **不推翻**它们、也**没解释**它们（网格/参数不同）·
⚠ 本特性**没改任何代码**（价值是"取到当前可复跑的绿证据"）·
⚠ 只跑了**最简工况**（100×60×20 单实体板）⇒ 复杂几何未验。

**依据**：`output/simulation-evidence.json` · `tools/capture_simulation_evidence.py` · `specs/134-static-simulation-reverified/` · 事实 141 / 142 / 143
"""

K = W / "docs" / "known-facts.md"
tk = K.read_text(encoding="utf-8")
if "| 145 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT, encoding="utf-8")
    print("  ok known-facts 已加 145")

R = W / "docs" / "ROADMAP.md"
B = """           686 🎯 **Spec Kit `134`：静力学仿真整链真机复验也 `pass`**（轮 205）—— 与拓扑**同一根因治好**，而两条链**各自独立取证**。
               ```
               [1] 零件 100×60×20 ✓  [2] 材料 AISI 1020 ✓  [3] 静力学研究 ✓  [4] 夹具/载荷 Count=2 ✓
               [5] CreateMesh=0 · 单元 **7,310** · 1.6 s ✓
               [6] RunAnalysis=0（★ JSON 自标 `run_analysis_return_is_trustworthy: false`）·
                   Results 非空 · **图数 4** = ['品质1','应力1','位移1','应变1'] ✓
               ⇒ **verdict: pass** · 求解 **0.8 秒** · 证据 output/simulation-evidence.json
               ```
            687 ★★★ **为什么两条链要**各自**取证**：拓扑（`122`）与静力学（本特性）**不是同一条链** ——
               前者走 `ICWTopology*` + 目标/约束，后者走 `ICWStudy` + 夹具/载荷 + 4 张图。
               ★ 虽然根因（加载项没启用，事实 141）相同，**但"同一根因"不等于"结果必然相同"** ——
               这是事实 143 那条教训的**另一面**：**别用邻接关系代替证据**（这次是反过来用它去要求取证）。
            688 ★ 判据仍是**回读**不是返回码：脚本自己标了 `run_analysis_return_is_trustworthy: false`，
               而成功判据是 `Results` 非空 + 图数 > 0 ⇒ ★ **判据声明自己不可信**（正面样板）。
            689 ⚑ **限度**：⚠ **"求解器不收敛"那四次（20–25 GB / 1000–3000 s）的成因仍未定** ——
               本轮 pass **不推翻**它们、也**没解释**它们（网格/参数不同）·
               ⚠ 本特性**没改任何代码**（价值是"取到当前可复跑的绿证据"）·
               ⚠ 只跑了**最简工况**（100×60×20 单实体板）⇒ 复杂几何未验。
               门禁 + `release_check` exit 0 · 全量回归绿。
            690 ▶ **队列续作**（`docs/backlog-8h.md`）：下一项 = **A2**（`sw_simulation_study` 族：`generate_report` /
               `create_mesh_for_control` / `default_element_size_and_tolerance` —— ★ 注意最后一个实际在
               `scripts/sw_simulation.py` 而非 `_study`，**归属按实测改正**）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None
before = "".join(lines)
if re.search(r"^\s+686 ", before, re.M):
    print("  游标 686 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+690 ", R.read_text(encoding="utf-8"), re.M)
    print("  复核: 690 行已存在 ✓")
