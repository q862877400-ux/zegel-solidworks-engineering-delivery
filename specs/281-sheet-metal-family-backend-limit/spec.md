# Spec — 同族的 `AccessSelections` 逐个测：★★ **整族后端限制**（4 个 `CreateDefinition` 族成员同一个因）

**Feature**: `specs/281-sheet-metal-family-backend-limit/`
**日期**: 2026-10-10
**上游**: `specs/280-edge-flange-backend-limit/`（★ 只验了常量 37 ⇒ ★ 说「下一轮逐个测同族」）
**本轮只做一件事**：★ 把同族的**其余常量**逐个测 ⇒ ★ **看是不是整族同一个因**。

---

## 一、★★★ 真机读数（SW **34.4.1** · ★ 走 `sw_guard` · ★ 临时零件用完关闭不保存）

| 常量 | 成员 | 官方接口 | `hasattr(AccessSelections)` | ★ `AccessSelections(model, 空 Dispatch)` |
|---|---|---|---|---|
| **37** | `create_edge_flange` | `IEdgeFlangeFeatureData` | — | ✗ ★ **`-2147417851`** |
| **35** | `create_one_bend` | `ISketchedBendFeatureData` | **True** | ✗ ★ **`-2147417851`** |
| **118** | `create_gusset` | `ISMGussetFeatureData` | **True** | ✗ ★ **`-2147417851`** |
| **117** | `create_swept_flange` | `ISweptFlangeFeatureData` | **True** | ✗ ★ **`-2147417851`** |

★★★ **四个常量**同一个读数**** ⇒ ★★ **整族后端限制**（★ 不是「每个都要单独查」）。
★★★ **`-2147417851` = `0x80010105`** ⇒ ★★ 与**事实 47 / 67 / 126** 的 `IAccessSelections` 指针族**同族**。
★★ **`hasattr` = True** ⇒ ★ 方法**在**（★ 不是「没有这个方法」）⇒ ★ **不是路径错**，★ 是**调用时**失败。

---

## 二、★★★ **路径分层**（★ 本轮的结构性结论）

| 路径 | 成员 | ★ 是否受此限 |
|---|---|---|
| ★ **`CreateDefinition` + `CreateFeature`** | `create_one_bend` · `create_edge_flange` · `create_swept_flange` · `create_gusset` | ★★ **受限**（★ 四个常量同一个 `0x80010105`） |
| ★ **直接 `Insert*`** | `create_base_flange`（★ `CreateFeature` 但**不需要** AccessSelections · ★ **已建成**）· `create_hem`（★ `InsertSheetMetalHem2` · 16 形参）· `create_draft`（★ `InsertMultiFaceDraft`） | ★ **不在这一族** |

★★★ ⇒ ★★ **`create_hem` 的「五种形态全回 `None`」是**另一个**原因**（★ 它**不走**这条路 ⇒ ★ **不要混为一谈**）。

---

## 三、需求

### FR-001 ★★★ 四个常量**同一个** hresult
- **验收场景**：`test_all_four_constants_share_one_hresult` 通过。

### FR-002 ★★★ 那个 hresult **就是** `0x80010105`
- **验收场景**：`test_the_hresult_is_the_known_pointer_family` 通过。

### FR-003 ★★ 方法**在**（★ 不是「没有这个方法」）
- **验收场景**：`test_the_method_exists_but_cannot_be_called` 通过。

### FR-004 ★★★ **路径分层**
- **验收场景**：`test_the_two_paths_are_separated` 通过。

### FR-005 ★★★ 状态表**三条**都订正（★ 回源码核）
- **验收场景**：`test_status_table_entries_are_corrected` 通过。

### FR-006 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过（★ 六组负例）。

---

## 四、非目标

- ★★ **不改**任何 `create_*` 的**实现**（★ 后端限制，★ 不是写错）。
- ★ **不验** `create_hem` 的 5 形态（★ 它走**另一条路** ⇒ ★ 独立一件工作）。

## 五、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 常量数不对 / hresult 不齐 / 十六进制写错 / `hasattr` 有 False / 条目数不对 / 某块没理由 ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_sheet_metal_family_backend_limit.py` **6/6 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 生成器链已跑 | 7 步全 `exit 0`（★ 改了 `scripts/`） |
| SC-5 | ★ 真机无残留 | 护栏预检「读到文档 0 个」 |

## 六、未过门（本轮不做，如实登记）

- ★★★ **`create_hem` 的 5 形态 `None` 未查** —— ★ 它走 **`InsertSheetMetalHem2`**（★ 直接 `Insert*`）
  ⇒ ★★ **与 `CreateDefinition` 族**不同因**** ⇒ ★ **独立一件工作**。
- ★★ **`create_draft` 未真机跑**（★ 路径已改 `InsertMultiFaceDraft` · ★ 239 是**离线切片**）。
- ★ 12 条 `arity` 接线 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 B1–B5 · 未提交未部署。
