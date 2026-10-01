# Converge: 拓扑优化结果读取

**Feature**: `001-topology-result-readout` · **Spec**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md) · **Tasks**: [tasks.md](tasks.md)

**Converged**: 2026-10-01（轮 52）· **环境**: SW 2026 SP4.1 / `revision 34.4.1`

> **这一步做什么**：把 `spec.md` 的每条验收判据**与交付物的实测证据逐条对齐**，并**明确记下不符合项**。
> ⚠ 前置：本特性的 `tasks.md` 是 **13/13 全 `[x]`**，所以 `converge` 是它**最后一步**。
> ★ **本特性是三个特性里唯一一个「spec 的前提被实测推翻」的** —— 见 §一。

---

## 一、结论摘要

| 判据 | 结论 | 依据 |
|---|---|---|
| FR-001 在**真的跑过优化**的研究上完成运行期试探 | 🔴 **未达成** | §三.1（环境阻塞） |
| FR-002 覆盖至少那 6 个候选名 | ✅ 成立 | §二.1 |
| FR-003 结论写进 `limitations`，不用「试过了不行」 | ✅ 成立 | §二.2 |
| FR-004 实现读数函数，包出**确实可用**的入口 | ✅ 成立 | §二.3 |
| FR-005 每个断言有**可重跑的命令** | ✅ 成立 | 逐条见 §二 |
| FR-006 若结论是「无 API」须在 spec/capabilities 同时写明 | ⚪ **前提未触发** | §三.3（结论**不是**「无 API」） |
| SC-001 `probe_results_api_surface.py` 在已跑过优化的研究上跑完 | 🔴 **未达成**（两个原因） | §三.1 · §三.2 |
| SC-002 `capabilities.yaml` 条目含结论 | ✅ 成立 | §二.2 |
| SC-003 读数函数返回**非空且来源可追溯**的值 | ⚠ **一半成立** | §二.3（可追溯 ✅ / 真机 ❌） |
| SC-004 四源取证表可被**独立重跑**复核 | ⚠ **原表不可** | §三.4（converge 已补命令） |

**⇒ 净结果：6 条 FR 里 **4 成立 / 1 未达成 / 1 前提未触发**；4 条 SC 里 **1 成立 / 2 部分 / 1 未达成**。**

---

## 二、成立项的取证

### 1. FR-002 —— 6 个候选名逐个核过

```powershell
Select-String D:\AI\SW\_raw\reflect\iface_cosworks.txt -Pattern 'ExportSmoothedMesh'
```
⇒ `ExportSmoothedMesh` / `GetSmoothedMesh` / `ExportSmoothedMesh2` / `ViewConvergenceData` /
`MaterialMass` / `GetMaterialMassPlot` **六个全部 0 命中** ✓（`## ICWResults` 段 **107 个成员**里一个都没有）

### 2. FR-003 / SC-002 —— 结论进了清单

```powershell
python -c "import json;d=json.load(open('capabilities.yaml',encoding='utf-8'));c=[x for x in d['capabilities'] if x['id']=='topology_optimization'][0];print(len(c['limitations']));[print(' -',s[:80]) for s in c['limitations'] if '结果读取' in s]"
```
⇒ `limitations` **18 条**，其中提到「结果读取」的**有 2 条**：
新增的那条**按证据强度分成 5 类**（① 可读且已证 / ②③⑤ 反射里有未验 / ④ 真查不到），
**每条带来源位置与可重跑命令**；
⚠ 老的那条（`[13]`「…**未实现**：反射里**未核到对应成员**」）**与新的直接矛盾** ——
见 §三.5，**本轮已给它加过期标记**（原文保留）。✓

### ★ **核对数字这件事本身抓到了 §三.5** ——

写本节时我按规矩「**不给没验过的数**」去核 `含「结果读取」的条数`，
**核出来是 2 不是 1** ⇒ 顺着这条查下去，才发现 `[13]` 是**另一条陈旧记录**（§三.5）。
**⇒ 「报告计数要给枚举命令」这条纪律的价值就在这里：它不只防我编数，还能**顺藤摸出问题**。**

### 3. FR-004 / SC-003（**可追溯那一半**）—— 读数函数

```powershell
python -m pytest tests\test_sw_topology_contract.py -q     # ⇒ 14 passed
```
⇒ `collect_topology_numbers(study)` 返回体里 **`source_members` 逐项点名官方成员**
（`ICWStudy.Results` / `ICWResults.GetPlotCount` / `GetPlotNames` / `GetMaximumAvailableSteps`），
由契约测试 `test_collect_numbers_with_plots_reports_ok_and_source_members` **钉死** ✓

**★ 并且它**没有**包那 4 个参数语义查不到的成员** —— 那 6 个登记在 `TOPOLOGY_RESULTS_UNRESOLVED`，
**每条带「为什么没实现 + 要补什么」**，并由 `test_unresolved_members_are_documented_with_reasons` 守着。
**⇒ 这是 FR-004「包出**确实可用**的入口」的正确读法：可用的包，不可用的**登记**而不是猜。** ✓

---

## 三、不符合项

### 🔴 1. FR-001 / SC-001 —— **运行期试探没做成**（环境阻塞）

**spec 要求**：在**真的跑过拓扑优化**的研究上完成运行期试探。

**实际**：`python D:\AI\SW\probe_collect_numbers_noresults.py` ⇒
```
RuntimeError: GetAddInObject('SldWorks.Simulation') 返回 None
```
**只读诊断**（`D:\AI\SW\probe_addin_registration.py`）试了 **5 个候选 ProgID**，**全 None** ⇒
**本会话（PID 24252）的 Simulation 加载项没加载。**

⚠ ⚠ **关键点**：**003 的证据来自**另一个**加载了它的会话**（T-001 记 `GetAddInObject("SldWorks.Simulation") ✓`）。
⇒ **同一台机器、不同会话、环境不同** ⇒ **已知事实 57 的同族**
（「一直是绿的」可能只是**那次环境恰好满足**）。

**⇒ 处置（不猜、不硬做）**：
1. **不自行 `LoadAddIn`** —— 官方 [LoadAddIn.md] 要 **DLL 全路径**（不是 ProgID），
   且它会改**会话状态**；这与 003 那次「用户改许可后**重启**」的先例一致 ⇒ **该由用户决定**。
2. **不打勾、不写「已验证」**（铁律 2）。
3. **两条形态各有其证据，只是不在同一次真机运行里** —— **明说**：
   | 形态 | 证据 | 强度 |
   |---|---|---|
   | 有结果 | 003 的闭环（`output/topology-evidence.json`，`verdict=pass`，拿到「材料质量1」） | ✅ **真机** |
   | 无结果 | 本特性的契约测试（假对象，3 条） | ✅ **静态** |
   ⇒ **合起来覆盖了两条形态，但没有一次运行同时验过两者。**

### ⚠ 2. SC-001 点名的脚本 **不在仓库里**

```powershell
Test-Path C:\swprojects\sw-skill-fork\tools\probe_results_api_surface.py      # ⇒ False
Test-Path C:\swprojects\sw-skill-fork\scripts\probe_results_api_surface.py    # ⇒ False
Test-Path D:\AI\SW\probe_results_api_surface.py                               # ⇒ True
```

⇒ **它只存在于工作区根** ⇒ **换机器 / CI 跑不了** ⇒ **SC-001 连"能跑"这一半都不成立**。

### 🔴 3. **系统性问题：这是第 2 例**

| # | 脚本 | 点名它的地方 | 仓库里有吗 |
|---|---|---|---|
| 1 | `capability_gap.py` | `specs/002-merge-template/tasks.md` T-005 | ✗（只在 `D:\AI\SW\`） |
| 2 | `probe_results_api_surface.py` | `specs/001-topology-result-readout/spec.md` SC-001 | ✗（只在 `D:\AI\SW\`） |

**⇒ 两例都对「**验收必须是可跑的命令**」（本 spec 的 FR-005 与 ROADMAP 的三条纪律之三）造成缺口。**
**共同根因**：这些脚本是**探索期**在工作区根就地写的（AGENTS.md 工作区表本来就把工作区定位为
「放产物」），**被写进 spec 当了验收命令，却从没搬进仓库**。
**⇒ 建议（下轮做）**：把「验收命令必须指向**仓库内**路径」做成一条**可 grep 的检查**
（扫 `specs/**/*.md` 里的 `→ 验收:` 行，看提到的脚本是否 `git ls-files` 得到）。

### ⚠ 4. SC-004 —— spec 内的四源表**原表不可独立重跑**

spec §背景 的「已查的四源」表是 `| # | 源 | 查什么 | 结果 |` —— **没有命令列**
⇒ **读者无法独立复核**。**⇒ 本文件 §二.1 已补上第 1 源的命令**；
其余三源（DLL 反射 / CHM / 运行期 `GetIDsOfNames`）的入口见
`docs/A9-solve-attempts.md` 与 `capabilities.yaml` 的对应 `limitations` 条。
⚠ **本轮不改 spec 原表**（它记录的是当时的查证形态，有历史价值）⇒ 用本节补命令。

### 🔴 5. **清单自相矛盾（第 2 例同型问题）**：`limitations[13]` 与 `[18]` 结论相反

**现象**：`topology_optimization.limitations` 里**两条**都讲「结果读取」，但结论**相反**：
| 条 | 原文要点 | 与事实 |
|---|---|---|
| `[13]`（老） | 「结果读取…**未实现**：**反射里未核到对应成员**，按铁律 5 不编」 | 🔴 **被推翻** —— `GetPlotCount`/`GetPlotNames` **存在且运行期已用** |
| `[18]`（轮 50 新加） | 「① Material Mass 图 ✅ 可读且运行期已证；②③⑤ 反射里有未验；④ 真查不到」 | ✅ 正确 |

**`[13]` 另一半仍然成立**：**「Export Smoothed Mesh」确实不存在**（六源候选名全 0 命中）
⇒ **错的是把「没核到」当成了最终结论**，而不是「查了什么」。

**⇒ 处置**：给 `[13]` **加过期标记**（**不删** —— 「当时确实没核到」这个动作是真的），
并在标记里指向 `[18]`。`git diff --stat` = **`1 insertion(+), 1 deletion(-)`**（就那一行）。

**★ 与 003 的 `limitations[15]/[16]` 是**同一模式** —— 这已经是**第 2 例**：**
```
共同根因：**追加式记录不留过期标记**
         （新条目进来了、旧条目的结论被推翻，但没人回头标注旧的）
⇒ 一个读者只看旧条目会得出**相反结论**
⇒ **建议（下轮做）**：一条可 grep 的检查 ——
  清单里同一 `capabilities[]` 条目的 `limitations` 若出现**互相矛盾的结论词**
  （如「未实现」vs「已证」「存在」），应报出来人工核。
⚠ 不能全靠启发式（事实 53）：**只能报「值得看」，不能自动改**。
```

### ⚪ 6. FR-006 —— **前提未触发**（不是不符合，但要说清）

spec 写「**若**结论是『无 API』，必须在 spec / capabilities 里同时写明**查不到**」。
**实测结论**：**不是**「无 API」，而是**四种强度不同的结论**（1 可读且已证 / 2 反射里有未验 / 1 真查不到）。
⇒ **FR-006 的前提不成立**，但它要求的**诚实性**由 §二.2 的分级记录满足。
★ **这本身是本特性最有价值的产出**：**原假设（三件事可能都不存在）被实测细化成了四类**，
比原来的二值答案**更有用**。

---

## 四、对交付物的收敛改动（本步产出）

1. **本文件** —— 把 FR-001/SC-001 的环境阻塞、`probe_results_api_surface.py` 不在仓库、
   系统性问题（2 例）、SC-004 原表缺命令，全部写明
2. **`tasks.md`** —— 补齐 T-008 的完成标记（**我漏打了**）+ T-011/T-012/T-013 的证据；
   并把 **T-013 的陈旧基线**（`6 failed / 749 passed / 15 skipped` → `0 failed / 874 passed / 17 skipped`）
   **更新并记原因**（三处差别逐条给出依据）
3. **不动** spec / plan —— 它们记录的是**当时的真实判断**，有历史价值

---

## 五、这一步**没有**覆盖的

- **没有**重跑运行期试探（§三.1）⇒ 「本轮未验」而非「已验」
- **没有**验 `SavePlotsAseDrawings` / `ExportSimulationStudy`（只到「反射里有」这一层）
- **没有**把 `probe_results_api_surface.py` 搬进仓库（§三.2，独立改动）
- **没有**加 §三.3 建议的那条检查（下轮）
- **没有**验 `TOPOLOGY_RESULTS_UNRESOLVED` 里那 4 个成员的参数语义（那正是「未解决」的定义）
