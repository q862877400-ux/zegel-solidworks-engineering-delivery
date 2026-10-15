# Acceptance — 同族的 `AccessSelections` 逐个测：★★ 整族后端限制

**Feature**: `specs/281-sheet-metal-family-backend-limit/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 6/6 绿 · 红基线成立 · 生成器链 7/7 · 真机无残留 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★★★ **整族定案** —— ★ 走 `CreateDefinition` + `CreateFeature` 的 **4 个**钣金成员
（`create_one_bend` / `create_edge_flange` / `create_swept_flange` / `create_gusset`）**同一个因**：
★ **`AccessSelections` 族不可调用**（`0x80010105`）⇒ ★ **后端限制**。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 四个常量同一个 hresult | `test_all_four_constants_share_one_hresult` | ✅ `-2147417851` |
| FR-002 | ★★★ 就是 `0x80010105` | `test_the_hresult_is_the_known_pointer_family` | ✅ 同族 |
| FR-003 | ★★ 方法在（不是「没有」） | `test_the_method_exists_but_cannot_be_called` | ✅ `hasattr=True` |
| FR-004 | ★★★ 路径分层 | `test_the_two_paths_are_separated` | ✅ 两档 |
| FR-005 | ★★★ 状态表三条都订正 | `test_status_table_entries_are_corrected` | ✅ 3/3 |
| FR-006 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 六组负例全红 |

## 二、★★★ 真机读数（SW **34.4.1** · ★ 走 `sw_guard` · ★ 临时零件用完关闭不保存）

| 常量 | 成员 | 官方接口 | `hasattr(AccessSelections)` | ★ `AccessSelections(model, 空 Dispatch)` |
|---|---|---|---|---|
| **37** | `create_edge_flange` | `IEdgeFlangeFeatureData` | — | ✗ ★ **`-2147417851`** |
| **35** | `create_one_bend` | `ISketchedBendFeatureData` | **True** | ✗ ★ **`-2147417851`** |
| **118** | `create_gusset` | `ISMGussetFeatureData` | **True** | ✗ ★ **`-2147417851`** |
| **117** | `create_swept_flange` | `ISweptFlangeFeatureData` | **True** | ✗ ★ **`-2147417851`** |

⇒ ★★★ **四个常量**同一个读数**** ⇒ ★★ **整族后端限制**（★ 不是「每个都要单独查」）。
★ **`-2147417851` = `0x80010105`** ⇒ ★★ 与**事实 47 / 67 / 126** 的 `IAccessSelections` 指针族**同族**。
★★ **`hasattr = True`** ⇒ ★ 方法**在**（★ 不是「没有这个方法」）⇒ ★ **不是路径错**，★ 是**调用时**失败。
★ 读数原文 `output/_probe281_family_access.txt`。

## 三、★★★ 路径分层（★ 本轮的结构性结论）

| 路径 | 成员 | ★ 是否受此限 |
|---|---|---|
| ★ **`CreateDefinition` + `CreateFeature`** | `create_one_bend` · `create_edge_flange` · `create_swept_flange` · `create_gusset` | ★★ **受限**（★ 四个常量同一个 `0x80010105`） |
| ★ **直接 `Insert*`** | `create_base_flange`（★ **已建成**）· `create_hem`（★ `InsertSheetMetalHem2` · 16 形参）· `create_draft`（★ `InsertMultiFaceDraft`） | ★ **不在这一族** |

⇒ ★★ **`create_hem` 的「五种形态全回 `None`」是**另一个**原因**（★ 它**不走**这条路 ⇒ ★ **不要混为一谈**）。

## 四、★★★ 订正（★ `SHEET_METAL_RUNTIME_STATUS` 三条）

| 条目 | ★ 旧结论（留档） | ★ 订正 |
|---|---|---|
| `create_one_bend` | ★「仍缺『选中折弯线 / 固定面』这一步」 | ★★ **后端限制**（★ 常量 35 ⇒ `0x80010105`） |
| `create_gusset` | ★「缺的是『折弯的两个面』这个前置」 | ★★ **后端限制** —— ★ **即使那个前置满足了也过不了这一关** |
| `create_swept_flange` | ★「未在本机实测」 | ★★ **后端限制**（★ 常量 117 ⇒ `0x80010105`） |

★ 加上 280 已订正的 `create_edge_flange` ⇒ ★★ **族里 4 个 `CreateDefinition` 成员**全部**定案**。

## 五、★★ 红基线（★ 六组负例）

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ `[]` |
| 常量数不对 | 报错 | ✅ `['★ 应测 4 个常量，实测 1']` |
| hresult 不齐 | 报错 | ✅ `['★ 四个常量应回**同一个** hresult，实测 [-2147417851, -1]']` |
| 十六进制写错 | 报错 | ✅ `['★ `0x80010105` 写错了', '★ 十进制与十六进制**不自洽**']` |
| `hasattr` 有 False | 报错 | ✅ `['★ `hasattr` 应全为 True（★ 方法**在**）']` |
| 条目数不对 | 报错 | ✅ `['★ 要订正的条目应是 3 条']` |
| 某块没理由 | 报错 | ✅ `['★ 回源码核失败：create_gusset **没有**写「后端限制」的理由']` |

## 六、生成器链（★ 改了 `scripts/`）

| 步骤 | 结果 |
|---|---|
| `sync_bundled_skill.py` → `gen_level_audit.py` → `gen_metrics.py` → `gen_harvest_digest.py` → `build_union_map.py` → `gen_dead_ends.py` → `sync_bundled_skill.py` | **7/7 `exit 0`** |

## 七、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| 日志 | `output/_gate281.log` |

★ 真机预检前后均「**读到文档 0 个**」⇒ **无残留**。

## 八、未过门（如实登记）

1. ★★★ **`create_hem` 的 5 形态 `None` 未查** —— ★ 它走 **`InsertSheetMetalHem2`**（★ 直接 `Insert*`）
   ⇒ ★★ **与 `CreateDefinition` 族**不同因**** ⇒ ★ **独立一件工作**
   （★ 下一步：★ 用 **276 的报错入口** `ISldWorks::GetErrorMessages` ★ **逐个形态读栈** —— ★ 209 试过 5 形态但**没读栈**）。
2. ★★ **`create_draft` 未真机跑**（★ 路径已改 `InsertMultiFaceDraft` · ★ 239 是**离线切片**）。
3. 12 条 `arity` 接线 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 B1–B5 · 未提交未部署。
