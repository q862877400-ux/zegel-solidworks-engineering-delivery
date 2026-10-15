# Spec — **先量**：「改 `STUDY_MANAGER_ARITY`」的**正确改动面**（★ 标注是 **per-table** ⇒ 改**整张表**）

**Feature**: `specs/288-study-arity-change-surface/`
**日期**: 2026-10-10
**上游**: `specs/287-double-out-cosworks-positive/`（★ 解除了 12 条的前置）
**本轮只做一件事**：★ **动手前先量** —— ★ 改一处表值**要连带改多少**。

---

## 一、★★★ 逐条量：`ICWStudyManager` 的 **15** 个成员

| 成员 | ★ 表值 | ★ 官方完整形参数 | ★ 差 | ★ 末位形参 |
|---|---|---|---|---|
| `CreateNewStudy` | 3 | **4** | ★ **−1** | `Int32&` |
| `CreateNewStudy2` | 2 | **3** | ★ **−1** | `Int32&` |
| `CreateNewStudy3` | 3 | **4** | ★ **−1** | `Int32&` |
| `DuplicateStudy` | 4 | **5** | ★ **−1** | `Int32&` |
| `DuplicateStudy2` | 6 | **7** | ★ **−1** | `Int32&` |
| `ConvertStudy` | 6 | **7** | ★ **−1** | `Int32&` |
| `ConvertStudy2` | 8 | **9** | ★ **−1** | `Int32&` |
| ★ `RunAllStudies` | **0** | **1** | ★ **−1** | `Int32&` |
| ★ `RunSpecifiedStudyByName` | **0** | **1** | ★ **−1** | `Int32&` |
| `GetStudy` | 1 | **1** | 0 | `Int32` |
| `DeleteStudy` | 1 | **1** | 0 | `String` |
| `RenameStudyFromID` | 2 | **2** | 0 | `String` |
| `RenameStudyFromName` | 2 | **2** | 0 | `String` |
| `SetDistributedSimulation` | 1 | **1** | 0 | `Int32` |
| `ManageDistributedSimulation` | 2 | **2** | 0 | `Object` |

★★★ **⇒ 9 处差 1（★ 末位**全是** `Int32&`）· ★ 6 处相等（★ 末位**不是** `Int32&`）** ⇒ ★ **完全自洽**
（★ 表侧一律「**不含**末位 `Int32&` 出参」）⇒ ★ 与 **272 的公式** `table + byref_out == official` **逐条成立** ✓

---

## 二、★★★ 关键约束：★ 标注是 **per-table** ⇒ 改**整张表**

★ `scripts/check_arity_tables_vs_reflection.py:54` 逐字：

```python
DECL = re.compile(r"^#:\s*arity-reflect:\s*byref=(?P<mode>included|excluded)\s*$")
```

★★★ **⇒ 标注**紧贴表定义上方**、★ 一表一约定** ⇒ ★ 想改**一条**的值 ⇒ ★ **整张表都要按同一约定写**。

★★★ **⇒ 最小正确改动面 = 那 **9 处****（★ **不是** 12 条里的那 **5** 处！）
—— ★★ 若只改 5 处 ⇒ ★ **表内混用两种约定** ⇒ ★ 本轮的判据**当场红**。

---

## 三、★★ 另发现 2 处（★ 272 的 12 条**不含**它们）

★ `RunAllStudies` / `RunSpecifiedStudyByName` 的**官方末位也是 `Int32&`**（★ 表值 0 · ★ 官方 1）
⇒ ★★ **它们同属「差 1」那一批** —— ★ 而 **272 的 12 条**（★ 按**调用点**归集）**不含**它们
⇒ ★★ **改表时要一起改**（★ 否则表内自相矛盾）。

---

## 四、★★ 4 类同步点（★ 漏一类就红）

| # | ★ 同步点 | ★ 内容 |
|---|---|---|
| ① | ★ **表值** | ★ 差 1 的 **9 处**（★ 全部 +1） |
| ② | ★ **调用点** | ★ 被调用的那几个要传 **`out_i4()`**（★ `out_i4` 的 docstring 逐字说它是**在本接口 `CreateNewStudy3` 上真机实测**的 ✓） |
| ③ | ★ **标注** | ★ `excluded` → **`included`** |
| ④ | ★ **contract 测试的手抄对照表** | ★ `tests/test_sw_simulation_study_contract.py` 的 `REFLECTED_MANAGER_ARITY`（★ **9 处**） |

---

## 五、需求

### FR-001 ★★★ 整张表**一个约定**（★ 不混用）
- **验收场景**：`test_the_table_uses_one_uniform_convention` 通过。

### FR-002 ★★★ 约定在整张表上**一致**
- **验收场景**：`test_the_convention_is_uniform_across_the_table` 通过（★ 「差 1」的处数只允许 **0 或 9**）。

### FR-003 ★★★ 标注是 **per-table**
- **验收场景**：`test_the_annotation_is_per_table` 通过。

### FR-004 ★★ 4 类同步点**一致**（★ 钉「一致」不钉「现状」）
- **验收场景**：`test_four_synchronisation_points` 通过。

### FR-005 ★★ 另发现 2 处**同属差 1 那一批**
- **验收场景**：`test_two_extra_entries_are_also_in_the_gap` 通过。

### FR-006 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过（★ 四组负例）。

---

## 六、非目标

- ★★★ **本轮**不改表**** —— ★ 只**量清改动面**（★ 改表**另开切片**）。
- ★ **不改** `scripts/` ⇒ ★ **不跑生成器链**。

## 七、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 混用约定 / 非 `Int32&` 末位的值不对 / 差 >1 / 标注缺一张 / 对照表不一致 ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_study_arity_change_surface.py` **6/6 通过** |
| SC-3 | ★★ **判据**不钉现状**** | ★ 改表后（★ 9 处 +1 + 标注 `included`）★ **本条仍绿**（★ 「差 1」的处数变成 0） |
| SC-4 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |

## 八、未过门（本轮不做，如实登记）

- ★★★ **改表本体未做** —— ★ **改动面已量清**：★ **9 处表值** + ★ **5 个调用点接 `out_i4()`** + ★ **1 处标注** + ★ **测试对照表 9 处**。
- ★★ **同族的另两张表**（`RESULTS_ARITY` 9 条 / `MESH_ARITY` 10 条 / `sw_pdm.py`）**未逐条量** ⇒ ★ 下一轮**同样先量**。
- ★ ② 段第 2 条（250 的 7 处换路由）· `create_draft` 的 `pre_call` · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 未提交未部署。
