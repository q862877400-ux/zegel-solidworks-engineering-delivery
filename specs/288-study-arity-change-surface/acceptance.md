# Acceptance — 先量：`STUDY_MANAGER_ARITY` 的改动面

**Feature**: `specs/288-study-arity-change-surface/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 6/6 绿 · 红基线成立 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★★★ **改动面不是 5 处，是 9 处** —— ★ 因为 `#: arity-reflect:` 标注是 **per-table**
⇒ ★ 改一条值就得**整张表按同一约定写**。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 整张表一个约定 | `test_the_table_uses_one_uniform_convention` | ✅ 15 条全自洽 |
| FR-002 | ★★★ 约定在整张表上一致 | `test_the_convention_is_uniform_across_the_table` | ✅ 差 1 处数 ∈ {0, 9} |
| FR-003 | ★★★ 标注是 per-table | `test_the_annotation_is_per_table` | ✅ 2 张表各一标注 |
| FR-004 | ★★ 4 类同步点一致 | `test_four_synchronisation_points` | ✅ |
| FR-005 | ★★ 另发现 2 处同属差 1 那一批 | `test_two_extra_entries_are_also_in_the_gap` | ✅ |
| FR-006 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 四组负例全红 |

## 二、★★★ 逐条量（★ 现场解析源码 + 反射转储）

★ `ICWStudyManager` **15 条**：

| ★ 差 1（9 处 · 末位全是 `Int32&`） | ★ 相等（6 处 · 末位不是 `Int32&`） |
|---|---|
| `CreateNewStudy` 3→4 · `CreateNewStudy2` 2→3 · `CreateNewStudy3` 3→4 · `DuplicateStudy` 4→5 · `DuplicateStudy2` 6→7 · `ConvertStudy` 6→7 · `ConvertStudy2` 8→9 · ★ `RunAllStudies` 0→1 · ★ `RunSpecifiedStudyByName` 0→1 | `GetStudy` 1 · `DeleteStudy` 1 · `RenameStudyFromID` 2 · `RenameStudyFromName` 2 · `SetDistributedSimulation` 1 · `ManageDistributedSimulation` 2 |

⇒ ★★★ **完全自洽** ✓（★ 与 **272 的公式** `table + byref_out == official` **逐条成立**）

## 三、★★★ 关键约束：★ 标注是 **per-table**

★ `scripts/check_arity_tables_vs_reflection.py:54` 逐字
`DECL = re.compile(r"^#:\s*arity-reflect:\s*byref=(?P<mode>included|excluded)\s*$")`
⇒ ★ 标注**紧贴表定义上方**、★ **一表一约定** ⇒ ★ **改一条值 ⇒ 整张表按同一约定写**
⇒ ★★ **最小正确改动面 = 那 9 处**（★ **不是** 12 条里的那 **5** 处！）
⇒ ★★ 只改 5 处 ⇒ ★ **表内混用** ⇒ ★ 本轮的判据**当场红**。

## 四、★★ 4 类同步点（★ 漏一类就红）

| # | ★ 同步点 | ★ 内容 |
|---|---|---|
| ① | ★ **表值** | ★ 差 1 的 **9 处**（★ 全部 +1） |
| ② | ★ **调用点** | ★ 传 **`out_i4()`**（★ `out_i4` 的 docstring 逐字说它是**在本接口 `CreateNewStudy3` 上真机实测**的 ✓） |
| ③ | ★ **标注** | ★ `excluded` → **`included`** |
| ④ | ★ **contract 测试的手抄对照表** | ★ `tests/test_sw_simulation_study_contract.py` 的 `REFLECTED_MANAGER_ARITY`（★ **9 处**） |

## 五、★★ 红基线（★ 四组负例）

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ `[]` |
| 非 `Int32&` 末位的值不对（`GetStudy`=99） | 报错 | ✅ `['GetStudy 末位非 Int32& ⇒ 必须相等', '对照表与模块表不一致']` |
| 差 >1（`CreateNewStudy`=9） | 报错 | ✅ `['CreateNewStudy 只允许 0 或 1', '差 1 处数只允许 0 或 9，实测 8', …]` |
| 标注缺一张 | 报错 | ✅ `['标注应 ≥2 张表']` |
| 对照表与模块表不一致 | 报错 | ✅ `['对照表与模块表不一致']` |

## 六、★★★ 判据**不钉现状**（★ 铁律 28）

★ 本轮的判据是 **invariant-based**：★ 钉「**整张表一个约定**」· ★ 「差 1 的处数 ∈ **{0, 9}**」
⇒ ★★ **改表后（★ 9 处 +1 + 标注 `included`）本条仍绿**（★ 「差 1」的处数变成 **0**）✓
★ 这是**铁律 28**（★ 改实现前先搜有没有测试钉住旧行为）的**正面应用**。

## 七、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| 日志 | `output/_gate288.log` |

★ **未改** `scripts/` ⇒ ★ **不跑生成器链**。

## 八、未过门（如实登记）

1. ★★★ **改表本体未做** —— ★ **改动面已量清**：★ **9 处表值** + ★ **5 个调用点接 `out_i4()`** + ★ **1 处标注** + ★ **测试对照表 9 处**。
2. ★★ **同族的另两张表**（`RESULTS_ARITY` 9 条 / `MESH_ARITY` 10 条 / `sw_pdm.py`）**未逐条量** ⇒ ★ 下一轮**同样先量**。
3. ★ ② 段第 2 条（250 的 7 处换路由）· `create_draft` 的 `pre_call` · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 未提交未部署。
