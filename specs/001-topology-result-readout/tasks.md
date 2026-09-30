# Tasks: 拓扑优化结果读取

**Input**: [spec.md](spec.md) · [plan.md](plan.md)

**格式**：`[ID] [P?] [Story] 描述` —— `[P]` 表示可并行；**每个任务必须带 `→ 验收:`**

**⚠ 唯一阻塞点**：Phase 2 的 T-002（真机跑通一次优化）。它不通，US1 的交付就降级为
「静态三源已查、运行期未验」，且必须在 limitations 里**明说未验**。

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
  **✅ 2026-10-01 逐段打通**（每一步都先撞错误码、再查枚举、再修）：
  | 步骤 | 撞到的 | 真因（枚举真源 `enum_cosworks.txt`） | 修法 |
  |---|---|---|---|
  | 建研究 | `类型不匹配 (arg 4)` | `Int32&` 出参 | `out_i4()` = `VARIANT(VT_BYREF\|VT_I4, 0)` |
  | 设目标+约束 | `EndEdit = 7` | `swsTopoErrCode_OnlyOneMassConstraintCanBeDefined` | **`CreateGoal(0/1)` 自带质量约束 ⇒ 改它，不要新建** |
  | 施夹具 | 返回 None（不抛异常） | 第 2 参 `DispArray` 传了 `None` | 传 `GetSelectedObject6(i,-1)` 的**对象列表** |
  | 施载荷 | 返回 None | 同上 + 力类型须为 `swsForceTypeNormal = 1` | 同上 |
  | 写属性 | `<unknown>.set_ForceType` | 迟到绑定的写形态 | **`set_com_member`（属性赋值）** |
  | `CreateMesh` | 返回 **5** | `swsStudyErrorSpecifyPositiveValue` | 尺寸/tol **必须为正** |
  | `RunAnalysis` | 返回 **19** | `swsRunAnalysisErrorMaterialNotDefined` | **先赋材料** `SetFavLibraryMaterialToSelectedEntities` |
  `→ 验收:` `python D:\AI\SW\probe_run_and_read_results.py` 打印
  `study.Results 非空 = True`

- [ ] **T-003** [P] 若 T-002 跑不通 ⇒ 记录**卡在哪一步**（错误码 + 现象），
  并把「运行期未验」作为已知缺口写进 spec 与 limitations
  `→ 验收:` `grep -c "运行期未验" D:\AI\SW\specs\001-topology-result-readout\*.md` ≥ 1

---

## Phase 3: User Story 1 —— 判定有没有 API（P1，MVP）

**Goal**: 对六个候选名逐个给出「存在 / 不存在 + 原文报错」
**Independent Test**: 重跑 `probe_results_api_surface.py`（**在 T-002 成功的研究上**）

- [ ] **T-004** [US1] 在 `ICWResults` 上试探六个候选名
  （`ExportSmoothedMesh` / `GetSmoothedMesh` / `ExportSmoothedMesh2` /
  `ViewConvergenceData` / `MaterialMass` / `GetMaterialMassPlot`）
  `→ 验收:` 每个名字打印「✓ 存在（含返回类型）」或「✗ 名字不存在（原文）」
- [ ] **T-005** [US1] 扩展试探：把 `ICWResults` 的 107 个成员里含
  `Export` / `Smooth` / `Conv` / `Mass` 的**全部**列出来（不只六个）
  `→ 验收:` 打印命中的成员名与签名；无命中则打印「0 命中」
- [ ] **T-006** [US1] 结论写进 `capabilities.yaml` 的 `topology_optimization.limitations`
  —— **必须含证据来源与可重跑命令**，禁用「试过了不行」
  `→ 验收:` `python scripts\check_union_conventions.py` exit 0，且 limitations 里每条都带命令

---

## Phase 4: User Story 2 —— 读出能读的（P2）

**Goal**: `collect_topology_numbers(study)` 返回可追溯的读数
**Independent Test**: 在 T-002 的研究上返回非空；在**未跑过**的研究上明确报「无结果」

- [ ] **T-007** [US2] 实现 `collect_topology_numbers(study)`（扩 `scripts/sw_topology.py`）
  - 用 `ICWResults` 的 `GetMinMaxDisplacement` / `GetMinMaxStress` /
    `GetMinMaxFactorOfSafety` / `GetTimeOrFrequencyAtEachStep`
  - **每个返回值附带来源成员名**（可复查）
  - 未跑过 ⇒ 返回 `{"status": "no_results", ...}`，**不抛未捕获异常、不静默空 dict**
  `→ 验收:` 真机调用两次（有结果 / 无结果），输出符合上述两种形态
- [ ] **T-008** [US2] 契约测试：扩 `tests/test_sw_topology_contract.py`
  —— 断言出参形态（`out_i4()`）与「无结果」的返回结构
  `→ 验收:` `python -m pytest tests\test_sw_topology_contract.py -q` 全绿
- [ ] **T-009** [P] [US2] `collect_topology_numbers` 加来源块（`check_provenance` 要求）
  `→ 验收:` `python scripts\check_provenance.py` → `[PASS]`

---

## Phase 5: User Story 3 —— 替代路径评估（P3）

- [ ] **T-010** [US3] 评估三条替代路径并各给依据：
  ① `ICWResults.savePlotsAseDrawings` ② `ICWStudy.ExportSimulationStudy`
  ③ UI 自动化（computer-use / 宏）
  `→ 验收:` 三条各一行「能/不能 + 依据（命令或源码位置）」

---

## Phase 6: Polish

- [ ] **T-011** 回写 `D:\AI\SW\docs\ROADMAP.md` §一 游标 + §四 调整记录（若 P1 降级则记原因）
  `→ 验收:` `Select-String ROADMAP.md -Pattern '^下一步'` 指向新阶段
- [ ] **T-012** 两仓库各自 commit（工作区 / 代码副本分开）
  `→ 验收:` 两个 `git status --porcelain` 都为空
- [ ] **T-013** [P] 全量回归：`python -m pytest tests -q`
  `→ 验收:` 失败列表与基线（6 failed / 749 passed / 15 skipped）**逐条相同**
