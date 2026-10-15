# Spec — **改表前先量：12 处的 by-ref 出参只有 3 种类型**

**Feature**: `specs/273-out-params-three-types/`
**日期**: 2026-10-10
**上游**: `specs/272-twelve-share-one-cause/`（★ 判 **12 条同一病因** = 「封装未接 by-ref 出参」，★ 说「下一轮改表 + 接出参」）
**本轮只做一件事**：★ **先量那 12 处的出参** —— ★ 量出「**要写几种 VARIANT**」。

---

## 一、★★★ 为什么要先量（★ 272 的教训：动手前先量）

★ 272 的下一动作写的是「★ ① 改表（12 处）★ ② 接 by-ref 出参 ★ ③ **真机验**」。
★★ **但「接 by-ref 出参」要写 `VARIANT`** —— ★ **类型数决定要写几种**：
★ 若 12 处出参有 8 种类型 ⇒ 要写 8 种写法；★ 若只有 3 种 ⇒ **只需 3 种**。
★★★ **不先量就会**：★ 要么**多写**（把 3 种写成 12 种、逐条查官方）★ 要么**少写**（漏掉一种 ⇒ 真机 `DISP_E_TYPEMISMATCH`）。

---

## 二、★★★ 量出的结果

| 出参类型 | 个数 | ★ **VARIANT 写法** |
|---|---|---|
| `Int32&` | **9** | `VT_BYREF \| VT_I4` |
| `Double&` | **6** | `VT_BYREF \| VT_R8` |
| `SwDmTableError&` | **1** | `VT_BYREF \| VT_I4`（★ **枚举 ⇒ 整数**） |
| **合计** | **16** | ★ **只有 3 种** |

★★ **逐成员**（12 条 · 16 个出参）：

| # | 成员 | 出参 |
|---|---|---|
| 1 | `GetBOMStartNumber` | `SwDmTableError&` |
| 2 | `CreatePlot` | `Int32&` |
| 3 | `CreateDeformedBody` | `Int32&` |
| 4 | `GetDisplacementAtPoints` | `Int32&` |
| 5 | `GetBucklingLoadFactors` | `Int32&` |
| 6 | `GetNodeLocation` | `Double&, Double&, Double&` |
| 7 | `GetElementLocation` | `Double&, Double&, Double&` |
| 8 | `CreateNewStudy` | `Int32&` |
| 9 | `CreateNewStudy2` | `Int32&` |
| 10 | `CreateNewStudy3` | `Int32&` |
| 11 | `DuplicateStudy` | `Int32&` |
| 12 | `ConvertStudy` | `Int32&` |

★ 9 + 6 + 1 = **16** ✓。

---

## 三、★★★ `GetWhatsWrong` **不在** 12 条里

★ `GetWhatsWrong` 的出参**为空**（★ `com = 3` = 形参 **3**）⇒ ★ 它是 **`all-byref` 桶**（★ 253/266 的命名）
⇒ ★ **它差 0** ⇒ ★ **不该混进这 12 条**（★ 混进来 ⇒ 改表时**多改一处**）。

★★ 为什么单列这一条：★ 它是 266 判「**改口径能救**」的那一条 —— ★ 与这 12 条**不是同一处改法**。

---

## 四、需求

### FR-001 ★★★ 出参**只有 3 种类型**
- **规则**：12 处的 by-ref 出参集合 == `{Int32&, Double&, SwDmTableError&}`。
- **验收场景**：`test_only_three_out_param_types` 通过。

### FR-002 ★★ 每种类型**都有** VARIANT 写法
- **规则**：3 种类型**各有**对应的 `VT_BYREF` 组合（★ 改表时**照着抄**）。
- **验收场景**：`test_every_type_has_a_variant_form` 通过。

### FR-003 ★★ `GetWhatsWrong` **不在** 12 条里
- **规则**：★ 逐成员表里**没有** `GetWhatsWrong`；★ 出参总数 == **16**。
- **验收场景**：`test_all_byref_is_not_in_the_twelve` 通过。

### FR-004 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过（★ 三组负例）。

---

## 五、非目标

- ★★ **不改表**（★ 改 12 处 `MESH_ARITY` 等 + 接出参 ⇒ ★ **另开切片**，★ 且**需真机验**）。
- **不**改 `scripts/` ⇒ ★ **不跑生成器链**。

## 六、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 多一种类型 / 逐成员总数不符 / 混进 `GetWhatsWrong` ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_out_params_three_types.py` **4/4 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 未改 `scripts/` | mtime 核 |

## 七、未过门（本轮不做，如实登记）

- ★★★ **12 条本体的改法未做** —— ★ **改法已明确且已量清**：★ ① 改表（12 处）★ ② 接 by-ref 出参
  （★ **只需 3 种 VARIANT 写法**）★ ③ **真机验**（★ 因为出参写法要试）⇒ ★ **另开切片**。
- ★ 1 条 `all-byref`（`GetWhatsWrong`）仍未修（★ 266 判「不值」）。
- `create_base_flange` 族现象 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 8 条既有红 · 未提交未部署。
