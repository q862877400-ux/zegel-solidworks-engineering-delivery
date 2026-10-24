# Tasks: S0 — 恢复首件所需的正式通路

**Feature**: `348-s0-restore-official-path`

**格式**：`[ID] [P?] [Story] 描述` —— `[P]` 表示可并行；**每个任务必须带 `→ 验收:`**

## Phase 1: 基线与取证

- [ ] **T001** 记录三处阻断的当前红面基线（失败条数 + 错误分类），作为修复后的对照
  → 验收: `python -B -m pytest tests/test_ec03_compiler.py tests/test_stage2_rules.py tests/test_stage4_planner.py tests/test_stage7_housing.py -q --tb=line`

- [ ] **T002** 取证 `compiler.py:594` 的调用点与 `ApplicabilityMixin` 的实际接口
  → 验收: `python -B -c "import sys,inspect; sys.path.insert(0,'scripts'); from engineering._applicability import ApplicabilityMixin as A; print([m for m in dir(A) if not m.startswith('_')])"`

- [ ] **T003** 取证 `FinalDod.evaluate` 的历史实现
  → 验收: `git show a695ac62 -- scripts/engineering/housing.py`

## Phase 2: User Story 1 - 编译入口能跑通 (P1)

- [ ] **T004** [US1] 把 `compiler.py` 的 `spec.allows(k)` 改为 `spec.applies_to(k)`
  → 验收: `python -B -m pytest tests/test_ec03_compiler.py -q`

- [ ] **T005** [US1] 补一条负例：落在适用域外的设备类别必须被拒绝，不得静默通过
  → 验收: `python -B -m pytest tests/test_s0_official_path.py -q -k 越权`

## Phase 3: User Story 2 - 最终 DoD 入口能跑通 (P1)

- [ ] **T006** [US2] 从 `git show a695ac62` 恢复 `FinalDod.evaluate()` 到 `housing.py`
  → 验收: `python -B -m pytest tests/test_stage7_housing.py -q`

- [ ] **T007** [US2] 核对恢复后的字段与 322 验收记录里出现的判定名一致
  → 验收: `python -B -m pytest tests/test_s0_official_path.py -q -k finaldod`

## Phase 4: User Story 3 - 规划出口能跑通 (P1)

- [ ] **T008** [US3] `build_registry` 遇重名时报出**具体冲突对**（两个规范名 + 各自模块），不阻断构建
  → 验收: `python -B -m pytest tests/test_stage4_planner.py -q`

- [ ] **T009** [US3] 确认规划出口在四孔需求下返回 3–5 个可编译候选
  → 验收: `python -B -m pytest tests/test_s0_official_path.py -q -k 规划出口`

## Phase 5: 收尾链审计

- [ ] **T010** 给 `tools/round_chain.ps1` 加 `-DryRun`，打印将要执行的写操作与关闭动作
  → 验收: `Select-String -Path tools\round_chain.ps1 -Pattern DryRun`

- [ ] **T011** 确认 `round_chain.ps1` 的 `git add -A` 被替换为「只提交点名的路径」或显式告警
  → 验收: `Select-String -Path tools\round_chain.ps1 -Pattern "add -A"`

## Phase 6: 收口

- [ ] **T012** 四个工程层测试文件的合计失败数必须为 0
  → 验收: `python -B -m pytest tests/test_ec03_compiler.py tests/test_stage2_rules.py tests/test_stage4_planner.py tests/test_stage7_housing.py -q`

- [ ] **T013** 全仓发布门禁仍绿，且 ruff 不上升
  → 验收: `python -B scripts/release_check.py`

- [ ] **T014** 把收口读数写进 `acceptance.md`（含修复前后对照与证据）
  → 验收: `python -B -c "import io; print(len(io.open('specs/348-s0-restore-official-path/acceptance.md', encoding='utf-8').read()))"`

## Dependencies & Execution Order

- Phase 1 必须先做（无基线则无法证明修复有效）
- Phase 2 / 3 / 4 三处修复**互不依赖**，可并行
- Phase 5 独立
- Phase 6 必须最后做

## 明确不做

- 不放宽任何既有断言换绿（FR-004）
- 不重写 `FinalDod.evaluate`（决定 2）
- 不自动挑重名里的一份（决定 3）
- 不改 `round_chain.ps1` 的既有行为，只显式化（决定 4）
