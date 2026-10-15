---
description: "Task list for feature implementation"
---

# Tasks: 伪造枚举表裁决与门禁边界透明化

**Input**: `/specs/223-enum-fabrication-and-gate-boundaries/`

**Prerequisites**: plan.md, spec.md

**Tests**: 本特性要求测试（spec FR-001/FR-010/FR-011/FR-021 明写「改动前必须红」），故测试任务为必需。

## Format: `[ID] [P?] [Story] Description`

## Path Conventions

单项目结构：`scripts/`、`mcp-server/`、`tests/`、`specs/` 均在仓库根。

**统一解释器**：`PY = "C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"`（本机该解释器**无 pytest** ⇒ 新增判据一律标准库风格 + `_main()`）。下文的 `→ 验收:` 命令均为**完整可复制**形式。

---

## Phase 1: Setup

- [x] T001 建立官方枚举基线：从 S1/S2 抄出官方值写进 `tests/test_pattern_enum_alignment.py` 的 `OFFICIAL_PATTERN_ELEMENT_SELECTION` / `OFFICIAL_FEATURES_TO_PATTERN` → 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -c "import ast;ast.parse(open(r'D:/AI/SW/tests/test_pattern_enum_alignment.py',encoding='utf-8').read())"`
- [x] T002 记录既有回归基线为绿 → 验收: `"C:/Users/Zegel/AppData/Local/Microsoft/WindowsApps/python.exe" -m pytest tests/test_sw_pattern_contract.py -q -p no:cacheprovider` ⇒ **11 passed**

---

## Phase 2: Foundational (Blocking Prerequisites) —— **先写判据，确认能红**

- [x] T003 [P] [US1] 写判据：两张表 ⟺ 官方枚举（值/成员名/项数） → 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B "D:/AI/SW/tests/test_pattern_enum_alignment.py"`
      **改动前实测：5/8 passed ⇒ 3 FAIL**（元素表 7≠3 · 特性表 8≠2 · 来源块项数不符）
- [x] T004 [P] [US2] 写判据：`check_undefined_names.py` 输出须列出被跳过文件与原因 → 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B "D:/AI/SW/tests/test_gate_boundary_transparency.py"`
      **改动前实测：2/6 passed ⇒ 4 FAIL**（无「跳过」段 · 无覆盖清单 · 无扩面 · 两张表未覆盖）
- [x] T005 [P] [US2] 写判据：`check_enum_values_vs_reflection.py` 须打印覆盖清单（计数自洽） → 验收: 同上文件 `-k enum_gate_reports_coverage_inventory`
- [x] T006 [P] [US3] 写判据：打包副本无「非官方 sg 名当合法值」且与源一致 → 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B "D:/AI/SW/tests/test_bundled_skill_enum_freshness.py"`
      **改动前实测：0/2 passed**（副本含 `sgEQUAL` · 4 处漂移）

**Checkpoint**: 三份新测试各至少一红（读数见 `acceptance.md`）✓

---

## Phase 3: US1 —— 伪造枚举表裁决与修正 (Priority: P1) 🎯 MVP

- [x] T007 [US1] `SWS_PATTERN_ELEMENT_SELECTION` 按官方重写为 3 项 + `# swXxx` 注释 → 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B "D:/AI/SW/tests/test_pattern_enum_alignment.py" -k pattern_element_selection`
- [x] T008 [US1] `SWS_FEATURES_TO_PATTERN` 按官方重写为 2 项 + `# swXxx` 注释 → 验收: `... -k features_to_pattern`
- [x] T009 [US1] 订正两表的来源块（如实写官方项数 + 引用官方页路径 + 写明「自造抽象冒官方名」的裁决） → 验收: `... -k source_block_states_official_page`
- [x] T010 [US1] 登记 `_SG_RELATIONS` 为「官方 45 项的真子集（12 项）」判据（非伪造） → 验收: `... -k sg_relations_is_subset_of_official`
      依据: 官方 `SketchAddConstraints.md` 的 Remarks = **77 行 / 45 个不重复名**（分旧式 `sgHORIZONTAL` 与新式 `sgHORIZONTAL2D` 两子块）

**Checkpoint**: US1 独立可验；MVP 达成 ✓

---

## Phase 4: US2 —— 两道门禁的边界透明化 (Priority: P1)

- [x] T011 [US2] `check_undefined_names.py` 让「跳过」可见（文件 + 原因 + 计数），退出码不变 → 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B "D:/AI/SW/scripts/check_undefined_names.py"` ⇒ 打印 **7** 个跳过文件（含 `scripts/sw_part.py`）
- [x] T012 [US2] `check_enum_values_vs_reflection.py` 扫描面扩到 `scripts/**/*.py` + **键字符集放宽到驼峰** + 打印覆盖清单 → 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B "D:/AI/SW/scripts/check_enum_values_vs_reflection.py"` ⇒ 覆盖行 **122 → 177**，0 处值不符
- [x] T013 [US2] 保证门禁退出码不变（跳过/未覆盖**不判失败**） → 验收: 两条命令退出码均为 **0** ✓

**Checkpoint**: US1 + US2 均独立可验 ✓

---

## Phase 5: US4 —— 同类候选：门禁双盲的错值表 (Priority: P2)

> ★ 由**委派只读核对成员**的全仓扫描发现（报告 `output/223-verify/fabrication-candidates.md`），
> ★ **本代理逐条复核**后才动手。

- [x] T014 [US4] `REF_PLANE_CONSTRAINTS` 两个值按反射订正（1028→1024 · 2056→2048）+ 补注释 → 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B "D:/AI/SW/tests/test_pattern_enum_alignment.py" -k ref_plane`
- [x] T015 [US4] `HEM_POSITIONS` 按铁律 4 取反射（1/2 → 0/1）+ 补注释 + 写明两源冲突 → 验收: `... -k hem_positions`
- [x] T016 [US4] 同步耦合面：`tests/test_tool_specs_batch93.py` 与 `mcp-server/tool_specs_batch93.py` 的 `position` 描述 → 验收: `"C:/Users/Zegel/AppData/Local/Microsoft/WindowsApps/python.exe" -m pytest tests/test_tool_specs_batch93.py -q -p no:cacheprovider` ⇒ passed
- [x] T017 [US4] `references/part-modeling.md` 的清单行只许列官方名（222 漏掉的文档） → 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B "D:/AI/SW/tests/test_bundled_skill_enum_freshness.py" -k doc`
- [x] T018 [US4] 补**永久负例**（1028/2056 与 md 的 1/2 必须不通过） → 验收: `... -k negative_case`

**⚠ 诚实性说明**：T014–T018 的**值订正发生在判据之前**（先修后写）⇒ 未取得「改前红」的读数。
**补偿措施**：每条都配了**永久负例**（断言订正前的值**必须不通过**），★ 即判据**有牙**是可复现的，
而不是只靠一次历史读数。此偏差如实登记，不掩饰。

---

## Phase 6: US3 —— 打包副本同步 (Priority: P2)

- [x] T019 [US3] 先算待裁剪集（**须为空**）再执行 `sync_bundled_skill()` → 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -c "import sys;sys.path.insert(0,'.');from scripts.sync_bundled_skill import sync_bundled_skill;print(sync_bundled_skill()['pruned'])"` ⇒ `[]`（**未删任何文件**）✓
- [x] T020 [US3] 复算漂移 → 验收: `... -c "…find_bundled_skill_drift(…)"` ⇒ `[]` ✓（修前 **4 处内容不符 + 1 文件缺失**）

---

## Phase 7: Polish & Cross-Cutting

- [x] T021 三份新测试 + 既有相关测试同时绿 → 验收: 见 `acceptance.md` 的读数表
- [x] T022 AST 检查全部改动文件 → 验收: 对 `scripts/sw_pattern.py`、`scripts/sw_ref_geometry.py`、`scripts/sw_sheet_metal.py`、`scripts/check_undefined_names.py`、`scripts/check_enum_values_vs_reflection.py`、`mcp-server/tool_specs_batch93.py` 逐个 `ast.parse` ⇒ 全通过
- [x] T023 核对无 COM 导入、无依赖安装、无提交、无删除 → 验收: `git status --short`（判据：本次新增改动 ⊆ 目标文件；**无删除/重命名**）
- [x] T024 更新 `docs/ROADMAP.md` §一 游标与 `.specify/feature.json` → 验收: 读回两文件确认指向 `specs/223-...`
- [x] T025 写 `specs/223-.../acceptance.md` → 验收: 文件存在且含实际命令读数与未过门清单
- [x] T026 追加 `.workbuddy-ai/memory/2026-10-08.md` 与 `output/AUTO_RUN_<日期>-<时间>.md` → 验收: 两文件存在

---

## Dependencies & Execution Order

- **Setup (Phase 1)**：无依赖。
- **Foundational (Phase 2)**：依赖 Setup；**阻塞**所有实现（判据必须先红）。
- **US1 (Phase 3)**：依赖 Phase 2；MVP。
- **US2 (Phase 4)**：依赖 Phase 2；与 US1 无文件重叠，可并行。
- **US4 (Phase 5)**：依赖 US2（T012 的键放宽是 T014 的注释生效前提）。
- **US3 (Phase 6)**：依赖 US1/US4（副本要含修正后的值）。
- **Polish (Phase 7)**：依赖全部。

---

## 本切片的停止条件（实际触发过的）

- 任一判据**无法先红** ⇒ 停在 `in_progress`。**实际触发**：US4 的值订正在判据之前
  ⇒ 已按上面「诚实性说明」补**永久负例**，并把偏差如实登记（不掩饰）。
- 发现要删文件才能同步 ⇒ 停下交业主。**未触发**：待裁剪集实测为空 ⇒ 只复制、零删除 ✓
- 成员核对发现异常 ⇒ 立即停止。**未触发**：核对成员正常完成并落报告 ✓
