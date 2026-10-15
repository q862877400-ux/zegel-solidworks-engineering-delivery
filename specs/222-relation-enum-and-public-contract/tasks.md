---
description: "Task list for feature implementation"
---

# Tasks: 草图关系枚举正名与公开调用契约收敛

**Input**: `/specs/222-relation-enum-and-public-contract/`

**Prerequisites**: plan.md, spec.md

**Tests**: 本特性要求测试（spec FR-010 / SC-005 明写先红后绿），故测试任务为必需。

**⚠ 诚实性订正（2026-10-08）**：初版本文件 22 条**全部未勾**，而 `acceptance.md` 与 `ROADMAP` 已宣称完成 ⇒ **自相矛盾**（由独立核对 `w2-35-tasks-honesty.md` 抓出）。现已按实际完成情况补勾，并把**不自含**的验收命令（原文写「上述命令」「同上」）改为逐条可复制执行。

## Format: `[ID] [P?] [Story] Description`

## Path Conventions

单项目结构：`scripts/`、`mcp-server/`、`tests/`、`specs/` 均在仓库根。

**统一解释器**：`PY = "C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"`（本机无 pytest，一律标准库 `unittest`）。下文的 `→ 验收:` 命令均为**完整可复制**形式。

---

## Phase 1: Setup

- [x] T001 建立官方枚举基线：从三源抄出官方值写进 `tests/test_relation_enum_alignment.py` 的 `OFFICIAL_CONSTRAINT_TYPES` → 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -c "import ast;ast.parse(open(r'D:/AI/SW/tests/test_relation_enum_alignment.py',encoding='utf-8').read())"`
- [x] T002 记录 221 的 12 例为绿，作为本切片回归基线 → 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B "D:/AI/SW/tests/test_sw_sketch_relations_safety.py" -q`

---

## Phase 2: Foundational (Blocking Prerequisites)

- [x] T003 [P] [US1] 写判据：`RELATION_TYPES` 每键数值等于 `OFFICIAL_CONSTRAINT_TYPES` → 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B "D:/AI/SW/tests/test_relation_enum_alignment.py" -k relation_types_values_match_official_enum`
- [x] T004 [P] [US2] 写判据：`sw_part._SG_RELATIONS` 每项在官方 `SketchAddConstraints` 清单内 → 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B "D:/AI/SW/tests/test_relation_enum_alignment.py" -k sw_part_whitelist`
- [x] T005 [P] [US2] 写判据：公开工具参数描述不含非官方名 → 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B "D:/AI/SW/tests/test_relation_enum_alignment.py" -k tool_spec_description`
- [x] T006 [P] [US3] 写判据：数值未对齐的键必须在未决登记中 → 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B "D:/AI/SW/tests/test_relation_enum_alignment.py" -k unaligned_name_is_registered`

**Checkpoint**: 改动前实测 `Ran 8 tests` ⇒ **6 failures + 2 errors**（红基线成立）。

---

## Phase 3: User Story 1 - 关系名与官方枚举对齐 (Priority: P1) 🎯 MVP

- [x] T007 [US1] `RELATION_TYPES` 整表按官方重写（9 键数值 + 2 键改名） → 验收: `... -k relation_types_values_match_official_enum`
- [x] T008 [US1] 移除官方不存在的 `EQUAL`/`MIDPOINT`，改反别名指向 `SAMELENGTH`/`ATMIDDLE` → 验收: `... -k legacy_names_resolve_to_exact_official_members`
- [x] T009 [US1] 非法名拒绝信息补「官方对应名」提示 → 验收: `... -k string_entry_rejects_legacy_name_with_official_hint`
- [x] T010 [US1] 更新源码来源块（写明三源与为何是反别名） → 验收: `... -k relation_types_keys_are_complete`

**Checkpoint**: US1 独立可验；MVP 达成。

---

## Phase 4: User Story 2 - 公开工具与字符串入口收敛 (Priority: P1)

- [x] T011 [P] [US2] `sw_part._SG_RELATIONS` 去非官方名 → 验收: `... -k sw_part_whitelist_only_official_names`
- [x] T012 [US2] `add_sketch_relation` 加前置状态门（活动草图 + `status==2`，无旁路） → 验收: `... -k string_entry_refuses_when_sketch_not_underconstrained`
- [x] T013 [US2] 保证至多一次修改派发、异常不重放 → 验收: `... -k string_entry_dispatches_once_when_underconstrained`
- [x] T014 [P] [US2] 修正 `tool_specs_batch16.py` 的参数描述与模块 docstring → 验收: `... -k tool_spec_description_lists_only_official_names`

**Checkpoint**: US1 + US2 均独立可验。

---

## Phase 5: User Story 3 - 未决项登记 (Priority: P2)

- [x] T015 [US3] 增加 `UNDECIDED_CONSTRAINT_TYPES` + `is_undecided_constraint()`，且**不给数值**（登记项不得出现在表内） → 验收: `... -k unaligned_name_is_registered`
- [x] T016 [US3] `SKETCH_CONSTRAINT_TYPES` 19 项按「已对齐 / 别名 / 未决」归位 → 验收: `... -k relation_types_values_match_official_enum`（同族判据）+ 人工核对 `UNDECIDED_CONSTRAINT_TYPES` 内容
- [x] T017 [US3] 写明「为什么不能裁决」的具体候选冲突 → 验收: 读 `scripts/sketch_relations.py` 的 `UNDECIDED_CONSTRAINT_TYPES` 注释块

**Checkpoint**: US1–US3 全部独立可验。

---

## Phase 6: Polish & Cross-Cutting

- [x] T018 本切片判据 + 221 回归同时绿 → 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B "D:/AI/SW/tests/test_relation_enum_alignment.py"` ⇒ **Ran 16 tests / OK**；`... -B "D:/AI/SW/tests/test_sw_sketch_relations_safety.py"` ⇒ **Ran 12 tests / OK**
- [x] T019 AST 检查全部改动文件 → 验收: 对 `scripts/sw_sketch_relations.py`、`scripts/sw_part.py`、`scripts/sketch_relations.py`、`mcp-server/tool_specs_batch16.py` 逐个 `ast.parse`
- [x] T020 核对无 COM 导入、无依赖安装、无提交 → 验收: `git status --short`
      **⚠ 判据订正**：初版写「仅预期的 4 个文件变化」是**错的** —— 工作树**本来就有** 5 项遗留已跟踪改动（`AGENTS.md`、`docs/metrics.md`、`docs/union-coverage-matrix.md`、`output/costing-evidence.json`、`output/orphan-callability-census.json`，mtime 早于本会话）。**正确判据**是「本次新增的改动 ⊆ 222 的 9 个目标文件，且无暂存、无删除/重命名」。
- [x] T021 更新 `docs/ROADMAP.md` §一 游标与 `.specify/feature.json` → 验收: 读回两文件确认指向 `specs/222-...`
- [x] T022 写 `specs/222-.../acceptance.md` → 验收: 文件存在且含实际命令读数与未过门清单

---

## Dependencies & Execution Order

- **Setup (Phase 1)**：无依赖。
- **Foundational (Phase 2)**：依赖 Setup；**阻塞**所有 user story 的实现。
- **US1 (Phase 3)**：依赖 Phase 2；本切片 MVP。
- **US2 (Phase 4)**：依赖 Phase 2；与 US1 无代码文件重叠，可并行。
- **US3 (Phase 5)**：与 US1 同文件，**必须**在 US1 之后。
- **Polish (Phase 6)**：依赖全部 user story。

### 实际执行中的并发纪律

本切片的**核对**工作由 80 路 DeepSeek 成员并行完成（两波 × 40，报告在 `output/222-verify/`），
**实现**由主代理单独串行完成 —— 因为 T007/T008/T015 同在 `sw_sketch_relations.py`、
T011/T012 同在 `sw_part.py`，并行编辑会互相覆盖。

---

## 本切片的停止条件（实际触发过的）

- 任一判据无法转绿 ⇒ 停在 `in_progress`。**实际触发**：独立核对抓出两个真缺陷
  （`get_com_member` 实参误用致前置门恒失败；`_SG_LEGACY_ALIASES` 键大小写不一致致死代码），
  均已修复并补上**能抓到它们**的判据。
- 发现映射表存在新的生产消费者 ⇒ 重估。**实际触发**：确认 `sw_sketch_relations.py:364` 是生产消费者，
  已登记进 `spec.md` 的 Assumptions 段并据此认定本次**是行为变更**。

---

## Notes

- 全量 pytest 与收尾链（`tools/round_chain.ps1`）**不在本切片范围**：前者只在发布前/改门禁时跑，
  后者含 `git add` 与关闭 SW 副作用。
- 完成判据是「命令跑绿」，不是「我检查过了」。
- **本文件曾被独立核对判为「勾选与宣称矛盾」**（`output/222-verify/w2-35-tasks-honesty.md`），
  那次核对有效，已据此订正。
