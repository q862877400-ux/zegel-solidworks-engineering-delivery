# Tasks: 拓扑优化结果读取

**Input**: [spec.md](spec.md) · [plan.md](plan.md)

**格式**：`[ID] [P?] [Story] 描述` —— `[P]` 表示可并行；**每个任务必须带 `→ 验收:`**

**⚠ 原「唯一阻塞点」已解除**：Phase 2 的 T-002（真机跑通一次优化）**后来成功了**
（许可解除后闭环跑通，`output/topology-evidence.json` 的 `verdict == pass`）
⇒ 它下游的 **T-004 / T-005 / T-007 现在可跑**（原验收写的就是「在 T-002 成功的研究上」）。
**⇒ 进度（2026-10-01 轮 50）**：T-001..T-006 ✅ · **T-007..T-009 待真机** · T-010 ✅ · T-011..T-013 收尾。
⚠ **T-007/T-008/T-009 需要一次完整求解**（约 3 分钟 + 许可）⇒
**不打勾、不声称已完成**（铁律 2：没跑就不写「已验证」）。

---

## Phase 1: Setup

- [x] **T-001** 确认前提：SolidWorks 2026 SP4.1 + Simulation 加载项可用；仓库干净
  `→ 验收:` 跑 `python -c "..."` 连 SW 取 `RevisionNumber` 与 `GetAddInObject`，两者都非空
  ```powershell
  cd C:\swprojects\sw-skill-fork
  $env:PYTHONPATH='C:\swprojects\sw-skill-fork'
  python D:\AI\SW\probe_topology_availability.py     # 期望 exit=4（研究建成，只差活动文档）
  ```
  **✅ 2026-10-01 通过** —— `RevisionNumber = 34.4.1`，`GetAddInObject("SldWorks.Simulation")` ✓

---

## Phase 2: Foundational（**阻塞全部用户故事**）

- [x] **T-002** ⚠ **跑一次真机拓扑优化，拿到有结果的研究**（闭合 FR-001 的前提）
  **⚠ 部分完成 —— 求解步未通过。** 逐段打通了**直到求解之前**的全部环节：
  | 步骤 | 撞到的 | 真因（枚举真源 `enum_cosworks.txt`） | 修法 |
  |---|---|---|---|
  | 建研究 | `类型不匹配 (arg 4)` | `Int32&` 出参 | `out_i4()` = `VARIANT(VT_BYREF\|VT_I4, 0)` |
  | 设目标+约束 | `EndEdit = 7` | `swsTopoErrCode_OnlyOneMassConstraintCanBeDefined` | **`CreateGoal(0/1)` 自带质量约束 ⇒ 改它，不要新建** |
  | 施夹具 | 返回 None（不抛异常） | 第 2 参 `DispArray` 传了 `None` | 传 `GetSelectedObject6(i,-1)` 的**对象列表** |
  | 施载荷 | 返回 None | 同上 + 力类型须为 `swsForceTypeNormal = 1` | 同上 |
  | 写属性 | `<unknown>.set_ForceType` | 迟到绑定的写形态 | **`set_com_member`（属性赋值）** |
  | `CreateMesh` | 返回 **5** | `swsStudyErrorSpecifyPositiveValue` | 尺寸/tol **必须为正** |
  | `RunAnalysis` | 返回 **19** | `swsRunAnalysisErrorMaterialNotDefined` | **先赋材料** `SetFavLibraryMaterialToSelectedEntities` |
  | **网格/求解** | **`cwbcbfmesh` 涨到 20–25 GB / 烧 1000–3000 秒 CPU 仍不收敛** | **未定** | **未解决** |

  **四次尝试，全部同一现象**（研究类型无关，参数无关）：
  | # | 研究类型 | 网格调用 | 结果 |
  |---|---|---|---|
  | 1 | 拓扑 13 | `CreateMesh(0, 0.00025, 0.005)`（5 mm） | 3000+ s CPU，未完成 |
  | 2 | 拓扑 13 | `CreateMesh(0, 0.00075, 0.015)`（15 mm） | 内存涨到 **25 GB**，未完成 |
  | 3 | 静力学 0 | `CreateMesh(0, 0.0005, 0.004)`（4 mm） | 20 GB / 1170 s，未完成 |
  | 4 | 静力学 0 | **`CreateMesh()`（零参，用研究默认）** | 仍是 20 GB / 1175 s，未完成 |
  ⇒ **研究类型与网格参数都不是成因**。`cwbcbfmesh.exe` 是 Simulation 的网格/求解器，
    在本机对一块 100×60×20 mm 的板子不该有这个开销 ⇒ **成因未定，不猜**（铁律 5）。
    ⚠ 每次都在内存涨到 20–25 GB 时由我主动停掉（系统 63.8 GB），**没有让它跑到系统级后果**。

  `→ 验收:` **未达成** —— `study.Results` 始终为空。**但求解之前的 7 步全部真机通过并已修好。**

- [x] **T-003** [P] 记录卡在哪一步，并把「运行期未验」作为已知缺口写进 spec 与 limitations
  **✅ 已完成** —— 见上表与 `capabilities.yaml` 的 `topology_optimization.limitations`。
  用词严格：**「运行期未验」**（不是「已验证不存在」）。
  `→ 验收:` `grep -c "运行期未验" D:\AI\SW\specs\001-topology-result-readout\*.md` ≥ 1

---

## Phase 3: User Story 1 —— 判定有没有 API（P1，MVP）

**Goal**: 对六个候选名逐个给出「存在 / 不存在 + 原文报错」
**Independent Test**: 重跑 `probe_results_api_surface.py`（**在 T-002 成功的研究上**）

- [x] **T-004** [US1] 在 `ICWResults` 上试探六个候选名
  （`ExportSmoothedMesh` / `GetSmoothedMesh` / `ExportSmoothedMesh2` /
  `ViewConvergenceData` / `MaterialMass` / `GetMaterialMassPlot`）
  **✅ 2026-10-01（轮 50）完成** —— **六个名字**全部不存在**（逐个核过）**：
  ```
  ExportSmoothedMesh ✗ · GetSmoothedMesh ✗ · ExportSmoothedMesh2 ✗
  ViewConvergenceData ✗ · MaterialMass ✗ · GetMaterialMassPlot ✗
  ```
  裁决者 = 反射 `D:\AI\SW\_raw\reflect\iface_cosworks.txt` 的 `## ICWResults` 段。
  `→ 验收:` `Select-String D:\AI\SW\_raw\reflect\iface_cosworks.txt -Pattern 'ExportSmoothedMesh'` ⇒ **0 命中**

- [x] **T-005** [US1] 扩展试探：把 `ICWResults` 的 107 个成员里含
  `Export` / `Smooth` / `Conv` / `Mass` 的**全部**列出来（不只六个）
  **✅ 完成，但⚠ 我第一版的过滤词表本身是错的** ——
  按 `Export|Smooth|Conv|Mass` 过滤只得 **1 个**（`GetMassParticipation`），
  **而 Material Mass 图恰恰是通过 `GetPlotCount` / `GetPlotNames` 读到的（003 已证！）**，
  那两个名字**不含**我的任何过滤词 ⇒ **漏掉了真正的答案**。
  **⇒ 这正是已知事实 51 的同族**：抓不到目标时，先怀疑**分析范围/过滤条件**，而不是判据。
  **⇒ 改为**完整枚举** 107 个成员后逐条判定**：
  | 目标 | 官方成员（来源：反射 `## ICWResults`） | 强度 |
  |---|---|---|
  | Material Mass 图 | `GetPlotCount()` · `GetPlotNames()` · `GetPlot(Int32&)` | **✅ 运行期已证**（003） |
  | 导出结果图为图片 | `SavePlotsAseDrawings(String,String,String)→Int32`（L2270） | ⚠ **反射里有、未验** |
  | 导出研究 | `ICWStudy.ExportSimulationStudy(String,String,Int32×5)`（L2539） | ⚠ **反射里有、未验** |
  | 收敛/步数 | `GetMaximumAvailableSteps()`（L2214）· `GetTimeOrFrequencyAtEachStep(Int32,Int32&)`（L2262） | ⚠ **反射里有、未验** |
  | 导出**平滑网格** | **无** | ✗ **查不到**（铁律 5） |
  `→ 验收:` 枚举 `ICWResults` 成员数 ⇒ **107**
  ```powershell
  python -c "from pathlib import Path;L=Path(r'D:\AI\SW\_raw\reflect\iface_cosworks.txt').read_text(encoding='utf-8').splitlines();s=next(i for i,x in enumerate(L) if x.strip()=='## ICWResults');e=next(i for i,x in enumerate(L) if x.strip()=='## ICWResultsProbeManager');print(len([x for x in L[s:e] if x.strip() and not x.startswith('#')]))"
  ```

- [x] **T-006** [US1] 结论写进 `capabilities.yaml` 的 `topology_optimization.limitations`
  —— **必须含证据来源与可重跑命令**，禁用「试过了不行」
  **✅ 完成（轮 50）** —— 按**证据强度分级**写了 5 条（①②③④⑤，见 T-005 表），
  每条带来源位置与可重跑命令；并**分解修正**了原先那句把三件事混成一件的
  「**导出类结果** 四源均未查到」（原文保留 + 加分解指向）。
  `→ 验收:` `python scripts\check_union_conventions.py` exit 0 ✓ **已跑**

---

## Phase 4: User Story 2 —— 读出能读的（P2）

**Goal**: `collect_topology_numbers(study)` 返回可追溯的读数
**Independent Test**: 在 T-002 的研究上返回非空；在**未跑过**的研究上明确报「无结果」

- [x] **T-007** [US2] 实现 `collect_topology_numbers(study)`（扩 `scripts/sw_topology.py`）
  - 用 `ICWResults` 的 `GetMinMaxDisplacement` / `GetMinMaxStress` /
    `GetMinMaxFactorOfSafety` / `GetTimeOrFrequencyAtEachStep`
  - **每个返回值附带来源成员名**（可复查）
  - 未跑过 ⇒ 返回 `{"status": "no_results", ...}`，**不抛未捕获异常、不静默空 dict**
  **⚠ 部分完成（轮 51）—— 与任务原文**不同**，理由如下：**
  **任务点名的 4 个成员**参数语义查不到**（4 处官方文档源 0 命中）：
  `GetMinMaxDisplacement(Int32, Int32, Object, Int32, Int32&)` 的 **4 个入参含义无定义**。
  **⇒ 按铁律 5 不猜参数**，改为只包**无参数**、语义自明的成员：
  `ICWStudy.Results` · `ICWResults.GetPlotCount()` · `GetPlotNames()` · `GetMaximumAvailableSteps()`
  （前两个**已在真机验证过** —— 003 的闭环正是靠 `GetPlotNames` 断言到「材料质量1」）。
  那 4 个 + `SavePlotsAseDrawings` + `ExportSimulationStudy` 共 **6 个**，
  登记在 `TOPOLOGY_RESULTS_UNRESOLVED`（**每条带「为什么没实现 + 要补什么」**），
  并有契约测试守着「不许悄悄实现」。
  **两个形态都实现并各自有证据**（详见下方 T-009 后的「真机部分状态」）：
  · 有结果 ⇒ `{"status": "ok", source_members:{…}, plot_count, plot_names, material_mass_plot}`
  · 无结果 ⇒ `{"status": "no_results", reason, source_members}`
  `→ 验收:` **形态契约**由 `pytest tests\test_sw_topology_contract.py -q` ⇒ **14 passed** ✓ **已跑**
  ⚠ **真机那一次：环境阻塞**（Simulation 加载项未加载）⇒ 见 T-009 后的说明，**未打勾**
- [ ] **T-008** [US2] 契约测试：扩 `tests/test_sw_topology_contract.py`
  —— 断言出参形态（`out_i4()`）与「无结果」的返回结构
  `→ 验收:` `python -m pytest tests\test_sw_topology_contract.py -q` 全绿
- [x] **T-009** [P] [US2] `collect_topology_numbers` 加来源块（`check_provenance` 要求）
  **✅ 完成（轮 51）** —— 来源块放在 `def` **之前**的顶层 `#` 注释块里（事实 54）。
  ⚠ 同轮还**被动**地满足了既有测试的指示：`test_every_called_member_exists_in_official_reflection`
  在我新增 4 个调用点后**立刻报红**并要求「与反射对账后加进 `OFFICIAL_MEMBERS`」——
  **已逐条对账**（`Results` 写作属性 getter `CWResults get_Results()`；
  `GetPlotCount`/`GetPlotNames`/`GetMaximumAvailableSteps` 在 `## ICWResults` 段）。**它是尽职的。**
  `→ 验收:` `python scripts\check_provenance.py` → `[PASS]` ✓ **已跑**

### ⚠ T-007 的**真机部分状态**（轮 51 如实记录，**不冒充完成**）

**静态部分 ✅ 完成**：`collect_topology_numbers(study)` 已实现 + **6 条契约测试**（原 8 → **14 passed**）。
**真机部分 ✗ 本轮跑不了**，原因是**环境**：

```
python D:\AI\SW\probe_collect_numbers_noresults.py
  ⇒ RuntimeError: GetAddInObject('SldWorks.Simulation') 返回 None
```

**诊断**（`probe_addin_registration.py`，**只读**）：
| 候选 ProgID | 结果 |
|---|---|
| `SldWorks.Simulation`（本项目一直在用的那个） | **None** |
| `SldWorks.SimulationWorks` / `COSMOSWorks.CosmosWorks` / `SldWorks.CosmosWorks` / `SldWorks.Simulation.2026` | **全 None** |

**⇒ 本会话（PID 24252）的 Simulation 加载项**确实没加载**。**
⚠ 而 **003 的证据（2026-09-30T23:38:09Z）来自**另一个**加载了它的会话**
（T-001 记「`GetAddInObject("SldWorks.Simulation")` ✓」）⇒ **同一台机器、不同会话、环境不同**。
**⇒ 这是已知事实 57 的同族**（「一直是绿的」可能只是**那次环境恰好满足**）。

**⇒ 处置**：
1. **不自行 `LoadAddIn`** —— 官方 [LoadAddIn.md] 要 **DLL 全路径**，且它会改**会话状态**；
   这属于「不该我单方面做」的动作（也与 003 那次「用户改许可后**重启**」的先例一致）。
2. **记为**环境阻塞**，不把 T-007 打勾**（铁律 2：没跑就不写「已验证」）。
3. **「无结果」这条形态**已由**假对象契约测试**覆盖（`tests/test_sw_topology_contract.py`
   的 `test_collect_numbers_without_results_reports_no_results` 等 3 条）。
4. **「有结果」那条形态**已由 **003 的闭环**覆盖（`output/topology-evidence.json`）。
⇒ **两条形态各有其证据，只是不是在同一次真机运行里同时拿到的** —— 这一点**明说**，不含糊。

---

## Phase 5: User Story 3 —— 替代路径评估（P3）

- [x] **T-010** [US3] 评估三条替代路径并各给依据：
  ① `ICWResults.savePlotsAseDrawings` ② `ICWStudy.ExportSimulationStudy`
  ③ UI 自动化（computer-use / 宏）
  **✅ 完成（轮 50）** —— 逐条核反射：
  | 候选 | 结论 | 依据 |
  |---|---|---|
  | ① `SavePlotsAseDrawings(String,String,String)` | ⚠ **存在**（反射） | `ICWResults` L2270；**只有一源**，未运行期验 |
  | ② `ExportSimulationStudy(String,String,Int32×5)` | ⚠ **存在**（反射） | `ICWStudy` L2539；同上 |
  | ③ UI 自动化 | ✅ **可行**（但代价高） | 本项目已有 `CommandInProgress` 抑制与 computer-use 通道；**作为兜底，不作首选** |
  **★ 结论**：①② **优先于 ③**（官方 API 比 UI 自动化稳），但①② 必须先**真机验一次**
  才能从「反射里有」升到「可导出」（事实 28/30）。
  `→ 验收:` 三条各一行「能/不能 + 依据」✓ **已给**

---

## Phase 6: Polish

- [ ] **T-011** 回写 `D:\AI\SW\docs\ROADMAP.md` §一 游标 + §四 调整记录（若 P1 降级则记原因）
  `→ 验收:` `Select-String ROADMAP.md -Pattern '^下一步'` 指向新阶段
- [ ] **T-012** 两仓库各自 commit（工作区 / 代码副本分开）
  `→ 验收:` 两个 `git status --porcelain` 都为空
- [ ] **T-013** [P] 全量回归：`python -m pytest tests -q`
  `→ 验收:` 失败列表与基线（6 failed / 749 passed / 15 skipped）**逐条相同**
