# Acceptance — 枚举表盲区收口

**Feature**: `specs/224-enum-table-disposition/`
**收口轮**: 2026-10-09 01:08–01:20（自链任务 `3c1e4507` 首跑；接手被中断的 224 孤儿切片）
**解释器**: 判据 `C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B`；
门禁全套 `release_check` 必须用 **3.14.7**（见 §五）。
**结论**: ✅ **离线切片收口** —— 44 张盲区表全部表态、表态全部可核、未表态判红机制生效；
四件制品齐（本文件补齐第 4 件）。

---

## 一、判据与读数（每条真跑过）

| 任务 | 命令 | 期望 | 实测 | 结论 |
|---|---|---|---|---|
| T-001 | `test_enum_table_disposition.py` 存在 | 5 用例 | 实为 **8 用例**（见 §四·注 1） | ✅ |
| T-002 | 跑红基线 | FAILED N≥4 | 收口首跑 **FAILED (failures=1)**（见 §四·注 2） | ✅（见注 2） |
| T-003 | `check_enum_values_vs_reflection.py` | 扫描 189 · 表 101 · 覆盖 33 · 未覆盖 68 | 逐字一致 | ✅ |
| T-004 | 反射转储成员数 | `10664`（改前 `10588`） | **10664** | ✅ |
| T-005 | `DISPOSITION_CODES` / `NOT_ENUM_SUBS` | `enum/member/not-enum` · 5 子类 | 一致（`test_disposition_codes_are_closed` ok） | ✅ |
| T-006 | 未表态即红 | 未表态 44 ⇒ exit 1 | 机制生效：负例 `test_undeclared_..._red` ⇒ exit 1 ✓ | ✅ |
| T-007 | `parse_dispositions()` 条数 | `44` | **44**（enum 23 · member 11 · not-enum 10） | ✅ |
| T-008 | `find_int_tables()` 张数 | `101` | **101**（未漂移） | ✅ |
| **T-009** | `tests/test_enum_table_disposition.py` | `OK` | **Ran 8 tests · OK** | ✅ |
| **T-010** | `scripts/check_enum_values_vs_reflection.py` | 已表态 44 · 未表态 0 · exit 0 | 逐字一致 · `[PASS] 175 条` · **exit 0** | ✅ |
| **T-011** | `tests/test_gate_boundary_transparency.py`（223） | `OK`（7） | **7/7 passed** | ✅ |
| **T-012** | `test_relation_enum_alignment.py` + `test_pattern_enum_alignment.py`（222） | 都 `OK` | **18/18** + **12/12** | ✅ |
| **T-013** | 声明为纯插入 | 删除行 = 0 | 含 `#: enum-gate:` 的 hunk 中**同含删除行 = 0**（§二） | ✅ |
| **T-014** | `tests/test_bundled_skill_enum_freshness.py` | `OK` | 首跑 2/3 → 同步后 **3/3**（`pruned=[]`） | ✅ |
| 附加 | `scripts/release_check.py`（18 门禁，@3.14.7） | exit 0 | **exit 0** | ✅ |

★ 收口时**唯一**的红是 T-009 的负例（判红文案不含 spec 用语「未表态」）——已在门禁侧修正（见 §二）。

---

## 二、改动清单（本轮相对 HEAD 的 224 增量）

| 文件 | 改动 | 证据 |
|---|---|---|
| `scripts/check_enum_values_vs_reflection.py` | FR-001 `DUMP_ROW` 成员名 `sw\w+` → `[A-Za-z_]\w*`；FR-002 表级声明解析/校验；FR-003 未表态即红 | 成员 10588→**10664**（+76）；`ok/不符/查不到/冲突` 四读数不变 |
| `scripts/*.py` × 22 个文件 / **44 处** | 每张盲区表起始行正上方插一行 `#: enum-gate: …` | 44 行**全部纯插入**；`git diff -U0` 中与删除行**零共现** |
| `tests/test_enum_table_disposition.py` | 新判据（8 用例） | **8/8 OK** |
| `apps/workbench-ui/.../resources/skill/**` | 打包副本同步（23 文件） | `sync_bundled_skill` 461 文件 · **`pruned=[]`** |
| `docs/union-level-audit.md` | 重生成（R8 门禁要求） | `gen_level_audit` → 140 条能力 |
| `scripts/check_enum_values_vs_reflection.py:516` | **收口修正**：FAIL 文案加入 spec 用语「未表态」 | 使 T-009 负例转绿 |

★ **未提交、未部署、未打 tag**；未调 COM / 真机；未删任何文件。

---

## 三、44 条表态明细（逐张，机器可核）

分类合计：**enum 23 · member 11 · not-enum 10 = 44**（与 `find_uncovered_claimed_tables()` 张数相等）。

### enum 23
| 文件:行 | 表 | 声明 |
|---|---|---|
| sw_automation_knowledge.py:124 | DIALOG_SUPPRESSORS | enum swUserPreferenceToggle_e |
| sw_drawing_create_missing.py:898 | MODEL_ITEM_SOURCES | enum swImportModelItemsSource_e |
| sw_drawing_create_missing.py:908 | ANNOTATION_TYPE_BITS | enum swInsertAnnotation_e |
| sw_drawing_create_missing.py:1128 | VIEW_ENTITY_TYPES | enum swViewEntityType_e |
| sw_macro.py:34 | RUN_MACRO_ERRORS | enum swRunMacroError_e |
| sw_ref_geometry.py:104 | REF_POINT_TYPES | enum swRefPointType_e |
| sw_ref_geometry.py:111 | REF_POINT_ALONG_CURVE_TYPES | enum swRefPointAlongCurveType_e |
| sw_ref_geometry.py:115 | GLOBAL_BBOX_FIT_OPTIONS | enum swGlobalBoundingBoxFitOptions_e |
| sw_ref_geometry.py:119 | GLOBAL_BBOX_RESULT | enum swGlobalBoundingBoxResult_e |
| sw_sheet_metal.py:876 | HEM_TYPES | enum swHemTypes_e |
| sw_sheet_metal.py:893 | HEM_RELIEFS | enum swSheetMetalReliefTypes_e |
| sw_sheet_metal.py:896 | HEM_RELIEF_TEARS | enum swReliefTearTypes_e |
| sw_sheet_metal.py:907 | SELECTION_MARK_ACTION | enum swSelectionMarkAction_e |
| sw_simulation_results.py:85 | SWS_NODAL_STRESS_COMPONENTS | enum swsStaticResultNodalStressComponentTypes_e |
| sw_sketch_edit_ops.py:70 | TRIM_CHOICES | enum swSketchTrimChoice_e |
| sw_sketch_edit_ops.py:76 | OFFSET_CAPS | enum swSkOffsetCapEndType_e |
| sw_sketch_edit_ops.py:79 | OFFSET_CONSTRUCTION | enum swSkOffsetMakeConstructionType_e |
| **sw_sketch_relations.py:48** | RELATION_TYPES | enum swConstraintType_e（★ 本地语义键，仅值集包含校验） |
| sw_topology.py:135 | SWS_ANALYSIS_STUDY_TYPES | enum swsAnalysisStudyType_e |
| **sw_topology.py:146** | SWS_TOPOLOGY_GOAL_TYPES | enum **swsTopologyStudyGoalType_e**（★ 源码旧注释少 `Study`，按 S1 订正） |
| sw_topology.py:156 | SWS_TOPOLOGY_MASS_PREFERENCES | enum swsTopologyStudyMassConstraintOption_e |
| sw_topology.py:168 | SWS_TOPOLOGY_PRESERVED_REGION_OPTIONS | enum swsTopologyPreservedRegionOption_e |
| sw_topology.py:178 | SWS_TOPOLOGY_ITERATION_OPTIONS | enum swsTopologyIterationOption_e |

### member 11
| 文件:行 | 表 | 声明 |
|---|---|---|
| sw_body_ops.py:138 | BODY_MARKS | member InsertMoveCopyBody2 |
| sw_boolean_ops.py:70 | REGION_TYPES | member PreIntersect2 |
| sw_net_blend.py:40 | BLEND_TYPE | member InsertNetBlend |
| sw_net_blend.py:44 | INFLUENCE_TYPE | member SetNetBlendDirectionData |
| sw_sheet_metal.py:901 | UNFOLD_MARKS | member InsertSheetMetalFold |
| sw_sketch_edit.py:73 | SKETCH_MIRROR_MARK | member SketchMirror |
| sw_surface_features.py:1193 | SWEEP_MARKS | member InsertSweepSurface2 |
| sw_weld_bead.py:26 | BEAD_TYPE | member InsertFilletBeadFeature2 |
| sw_weld_bead.py:28 | PENETRATION_TYPE | member InsertFilletBeadFeature2 |
| sw_weld_bead.py:30 | FLAG | member InsertFilletBeadFeature2 |
| sw_weldment.py:144 | WELDMENT_TRIM_MARKS | member InsertWeldmentTrimFeature2 |

### not-enum 10
| 文件:行 | 表 | 子类 |
|---|---|---|
| sw_assembly_doc.py:90 | ASSEMBLY_DOC_ARITY | arity |
| sw_automation_knowledge.py:110 | DIALOG_AND_NOTIFY | arity |
| sw_body_ops.py:98 | AXIS_INDEX | index |
| sw_body_ops.py:100 | ROTATION_AXIS_MAP | derived |
| sw_hole_features.py:1132 | WZD_FASTENER_ANSI_METRIC_SIMPLE | observed |
| sw_mass_property.py:170 | SECTION_INDEX | index |
| sw_pattern.py:122 | PATTERN_MEMBER_ARITY | arity |
| sw_simulation_loads.py:191 | OFFICIAL_LOAD_SIGNATURES | arity |
| sw_simulation_results.py:113 | RESULTS_ARITY | arity |
| sw_simulation_study.py:150 | STUDY_MANAGER_ARITY | arity |

---

## 四、未过门 / 未完成

1. **真机未验**：44 条表态是**静态三源核对**的结论（S1 反射转储 + S2 官方页 + 源码注释），
   **无任何真机/COM 读数**；`enum` 声明只做了**值集包含**校验，未验键与官方成员名的对应。
2. **`sw_sketch_relations.RELATION_TYPES`**：键是本地语义键（`"COINCIDENT"` ≠ `swConstraintType_COINCIDENT`），
   故**只做值集包含、不做键名校验** —— 这是 spec FR-004 明写的裁决，不是遗漏。
3. **`member` 声明的强度**：只校验「该成员在 `C:\swapi\types\*\` 有页」，
   **不校验表内每个值确实出自该页**（页内 `Parameters`/`Remarks` 的语义映射需人读）。
4. **8 条 `HEAD` 即红的既有失败**（223 登记，见 223 acceptance §七）**本轮未修** —— 不属本切片范围、权属不明。
5. **D 类余下 42 张无标注但可溯源的整数表**：仍只做可见化，未逐张表态（它们**未自称官方**，不属 224 范围）。
6. **`--basetemp` 纪律**：本轮**未跑全量 pytest**（只跑聚焦判据），未触发该坑；纪律仍有效。

**注 1**：`tasks.md` T-001/T-009 写「5/6 用例」，实际文件是 **8 用例**（多出 `test_disposition_codes_are_closed`、
`test_declared_claimed_table_keeps_the_gate_green`、`test_wrong_value_is_caught_by_the_enum_disposition`）——
判据更严，非缺件。tasks.md 未改数字（避免制造"改判据凑数"的痕迹），在此如实记录。

**注 2**：**真正的「改实现前先红」基线**无法在本轮重现（被中断的 224 会话已先实现）。
本轮**实际观察到的红**是收口首跑的 `FAILED (failures=1)`（负例文案）；
而**机制本身的「能红」**由两条**永久负例**证明（均绿即通过）：
`test_undeclared_claimed_table_makes_the_gate_red`（未表态 ⇒ exit 1 且点名 `FAKE_TABLE`）·
`test_wrong_value_is_caught_by_the_enum_disposition`（值 77 ∉ {0,1} ⇒ exit 1）。
⇒ 表态机制**不是装饰品**（这正是 FR-003 要防的「空判据」）。

---

## 五、★ 本轮新发现的环境纪律（可复用）

> **`release_check.py` 必须用 3.14.7 跑，不能用受管的 3.13.12。**

- 现象：用 `.../python/versions/3.13.12/python.exe` 跑 `release_check.py`，
  其「参数绑定门禁」子进程导入 COM 依赖模块 ⇒ 打印
  `检测到当前 Python 环境缺少 comtypes / win32com 库，是否授权 AI 自动为您配置本地环境？[Y/N]`
  ⇒ 该提示文本被当成门禁输出 ⇒ **门禁假红**（`exit 1`，且无人值守下有挂死风险）。
- 根因：**3.13.12 受管解释器没装 `comtypes`/`win32com`**；**3.14.7 有**（实测 `import comtypes,win32com` OK）。
- 正解：判据用 3.13.12（它们桩掉 COM，不触发提示）；**门禁全套用 3.14.7**
  （`C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe`）。
- 与「已知环境坑」里 `sw_part.py` 交互式询问**同族**，但**触发者是 `release_check` 而非测试**——
  下一轮若见 `release_check` 假红，**先换 3.14.7 再查真因**。

### 附：`docs/union-level-audit.md` 陈旧（R8）
- `release_check` 首跑另一处红：`docs/union-level-audit.md 与最新数据不一致`（R8）。
- 该文件**不在 224 改动面内**（`git status` 未列它）⇒ 是**更早未提交切片**留下的陈旧产物。
- 按门禁指引 `python scripts/gen_level_audit.py` 重生成（140 条能力）后即绿 —— 属**正常的轮次生成器**，非 224 缺陷。

---

## 六、不做（重申 spec §三）

不给 44 张表逐行补 `# swXxx`（27/409 实测说明不适用本地语义键表）· 不改 `CLAIM` 正则 ·
不给「未覆盖但未自称官方」的 24 张表态 · 不修 223 的 8 条既有红 · 不碰真机/COM · 不提交/不部署/不打 tag。
