# Acceptance — 250 的 6 名 7 处真命中的换路由先量

**Feature**: `specs/260-routing-plan-real-hits/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 5/5 绿 · 红基线成立 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★ 7 处**逐处定了后继与改法**；★★ **4 处要先造 `*FeatureData`**（★ 大改，★ 不许当改名）。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★ 7 处逐处有计划 | `test_every_real_hit_site_has_a_plan` | ✅ 7 处 |
| FR-002 | ★★★ 后继逐字来自索引 | `test_successors_come_from_the_official_index` | ✅ 7/7 相同 |
| FR-003 | ★★★ 难度不许低估 | `test_difficulty_tiers_are_not_understated` | ✅ `needs-feature-data` **4** 处 |
| FR-004 | ★★ 6 名全是废弃成员 | `test_all_six_names_are_deprecated_via_the_index` | ✅ 6/6 在索引里 |
| FR-005 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 三组负例全红 |

## 二、★★ 红基线

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常表 | `[]` | ✅ |
| 改法不在词表 | 报错 | ✅ `["sw_render_material.py:345 的改法 '随便改改' 不在封闭词表 ['adapt-args', 'needs-feature-data', 'rename']"]` |
| 塞一个假站点 | 报错 | ✅ `['x.py:1 不在 250 的真命中站点里', '站点数 8 ≠ 基线 7']` |
| 把一处 `needs-feature-data` 降级成 `rename` | `needs-feature-data` 降到 3 < 基线 4 ⇒ 红 | ✅ **3 处** |

★ **判据第一次跑就红了两条**（★ 源接口查错 + 无意义的 `startswith`）⇒ ★ **修的是判据，不是数据**。

## 三、★★★ 逐处计划

| # | 站点 | 废弃成员 | 官方后继 | 改法 |
|---|---|---|---|---|
| 1 | `sw_render_material.py:345` | `DeleteRenderMaterial` | `DeleteDisplayStateSpecificRenderMaterial` | `adapt-args` |
| 2 | `sw_part.py:1536` | `FeatureLinearPattern5` | `IFeatureManager::CreateFeature` | ★ `needs-feature-data` |
| 3 | `sw_part.py:2544` | `FeatureLinearPattern5` | `IFeatureManager::CreateFeature` | ★ `needs-feature-data` |
| 4 | `sw_pattern.py:548` | `FeatureLocalCurveDrivenPattern` | `IFeatureManager::CreateFeature` | ★ `needs-feature-data` |
| 5 | `sw_sheet_metal.py:1440` | `InsertFormToolFeature` | `IFeatureManager::CreateDefinition` | ★ `needs-feature-data` |
| 6 | `sw_sheet_metal.py:311` | `KFactor` | `GetCustomBendAllowance` | `adapt-args` |
| 7 | `sw_simulation.py:803` | `MaterialIdName` | `IPartDoc::GetMaterialPropertyName2` | `adapt-args` |

## 四、★★★ 两条关键教训

### 1. **判废弃不能只 grep `obsolete`**
★ `DeleteRenderMaterial` 的废弃句是 **「Not supported in SOLIDWORKS 2011 and later. Superseded by …」** —— ★ **不含 `Obsolete`**。
⇒ ★ **必须查索引**（★ `obsolete_count` **1671**）。

### 2. **查索引要用「被废弃成员所在的接口」**
★ `IModelDoc2::MaterialIdName` 的后继在 **`IPartDoc`** 上 ⇒ ★ 用后继的接口查**查不到**（★ 我第一次就错了）。

## 五、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gate_details` 条数 | **47** |

## 六、未过门（如实登记）

1. **7 处换路由本体未做** —— ★ 分两批：★ 先 3 处 `adapt-args`（★ 便宜），★ 再 4 处 `needs-feature-data`（★ 大改）。
2. **`KFactor` / `MaterialIdName` 都换了接口/返回形态** ⇒ ★ 要真机验。
3. 高危写盘 · `create_hem` 行为证据 · 223 的 8 条既有红 · 未提交未部署。
