# Tasks: S1 — E1–E7 的验收规范与坏样件

**Feature**: `349-e1-e7-acceptance`

**格式**：`[ID] [P?] [Story] 描述` —— `[P]` 表示可并行；**每个任务必须带 `→ 验收:`**

## Phase 1: 统一结果结构与接口

- [x] **T001** 建 `scripts/engineering/acceptance/` 子包，定义 `CheckResult`（11 个必填字段，见 FR-008）
  → 验收: `python -B -c "import sys; sys.path.insert(0,'scripts'); from engineering.acceptance.result import CheckResult; print(sorted(CheckResult.__dataclass_fields__))"`

- [x] **T002** 定义四值状态枚举，禁止把其他非空字符串当 true
  → 验收: `python -B -c "import sys; sys.path.insert(0,'scripts'); from engineering.acceptance.result import Status; print([s.value for s in Status])"`

- [x] **T003** 写 `collect_*` / `judge_*` 的接口契约测试（采集器不判断、判定器不取数）
  → 验收: `python -B -m pytest tests/test_ec03_compiler.py -q`

## Phase 2: 七对采集器与判定器（可并行）

- [x] **T004** [P] [US1] E1 草图全约束：采集器读求解状态与欠约束实体；判定器判 DOF 与设计意图
  → 验收: `python -B -m pytest tests/test_ec03_compiler.py -q -k e1`

- [x] **T005** [P] [US1] E2 参数化可重建：采集器读改参后的重建结果与下游；判定器判联动与重开
  → 验收: `python -B -m pytest tests/test_ec03_compiler.py -q -k e2`

- [x] **T006** [P] [US1] E3 特征树可编辑：采集器读特征类型/错误/引用；判定器判可编辑性
  → 验收: `python -B -m pytest tests/test_ec03_compiler.py -q -k e3`

- [x] **T007** [P] [US1] E4 装配自由度闭合：采集器读配合对象与剩余运动；判定器判目标 DOF/干涉/间隙
  → 验收: `python -B -m pytest tests/test_ec03_compiler.py -q -k e4`

- [x] **T008** [P] [US1] E5 图样合规：采集器读实际标注对象；判定器逐项绑定要求
  → 验收: `python -B -m pytest tests/test_ec03_compiler.py -q -k e5`

- [x] **T009** [P] [US1] E6 工艺可行：采集器读实际几何与工艺输入；判定器判适用项
  → 验收: `python -B -m pytest tests/test_ec03_compiler.py -q -k e6`

- [x] **T010** [P] [US1] E7 结论可溯源：采集器解析引用；判定器判原文/适用性/版本/绑定
  → 验收: `python -B -m pytest tests/test_ec03_compiler.py -q -k e7`

## Phase 3: 三态样件（每条 E 都要）

- [x] **T011** [US1] 为 E1–E7 各写「好输入通过」样件
  → 验收: `python -B -m pytest tests/test_ec03_compiler.py -q -k "good or pass"`

- [x] **T012** [US1] 为 E1–E7 各写「已知坏输入拒绝」样件
  → 验收: `python -B -m pytest tests/test_ec03_compiler.py -q -k "bad or reject"`

- [x] **T013** [US1] 为 E1–E7 各写「缺证据 unknown」样件，且 unknown 不等于 fail
  → 验收: `python -B -m pytest tests/test_ec03_compiler.py -q -k "unknown"`

## Phase 4: 四个已知伪造手法必须被拒绝 (P1)

- [x] **T014** [P] [US2] R-04 负例：同一条草图关系重复 8 次，E1 不得判 DOF = 0
  → 验收: `python -B -m pytest tests/test_ec03_compiler.py -q -k duplicate_relation`

- [x] **T015** [P] [US2] R-05 负例：同一对组件重复贴 6 次 coincident，E4 不得判 fully_constrained
  → 验收: `python -B -m pytest tests/test_ec03_compiler.py -q -k duplicate_mate`

- [x] **T016** [P] [US2] R-06 负例：图纸义务 evidence 为空串，E5 覆盖率不得为 1.0
  → 验收: `python -B -m pytest tests/test_ec03_compiler.py -q -k empty_evidence`

- [x] **T017** [P] [US2] R-09 负例：规则请求只带两个布尔，E7 不得返回 PASS
  → 验收: `python -B -m pytest tests/test_ec03_compiler.py -q -k boolean_only`

## Phase 5: 既有估算器降级为预检

- [x] **T018** 在 `part_loop.DofPlan.total_dof` / `assembly.ConstraintGraph.total_dof` / `drawing_obligations.coverage` / `rule_service.evaluate_rule` 四处加「预检用途，不得直接授权交付」标注
  → 验收: `python -B -c "import io,re; t=io.open('scripts/engineering/part_loop.py',encoding='utf-8').read(); print('预检' in t)"`

- [x] **T019** 写一份「要求 → 检查 → 原始证据」覆盖表
  → 验收: `python -B -c "import io; print(len(io.open('specs/349-e1-e7-acceptance/coverage.md',encoding='utf-8').read()))"`

## Phase 6: 收口

- [x] **T020** 全量验收测试绿，且确认只叫「离线判据成立」
  → 验收: `python -B -m pytest tests/test_ec03_compiler.py tests/test_stage2_rules.py tests/test_ec03_compiler.py -q`

- [ ] **T021** 发布门禁仍绿
  → 验收: `python -B scripts/release_check.py`

## Dependencies & Execution Order

- Phase 1 必须先做（接口未定则其余全部无从谈起）
- Phase 2 七条**互不依赖**，可并行
- Phase 3 依赖 Phase 2
- Phase 4 依赖 Phase 2（负例要用判定器）
- Phase 5 与 2–4 独立
- Phase 6 最后

## 明确不做

- 不改四个既有估算器的算法（决定 3）
- 不接真机采集器（留 S3/S4）
- 不杜撰任何 SolidWorks 成员名（留 S3 三源互证）
- 不声称 E1–E7 真机通过
