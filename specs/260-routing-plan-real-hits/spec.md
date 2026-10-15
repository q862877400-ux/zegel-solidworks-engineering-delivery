# Spec — 250 的 **6 名 · 7 处真命中的换路由**先量**

**Feature**: `specs/260-routing-plan-real-hits/`
**日期**: 2026-10-10
**上游**: `specs/258-todo-premise-audit/` · `specs/259-todo-premise-audit-full/`（★ 定出这是「最红的一项」）
**本轮只做一件事**：★ 把 7 处**逐处定后继 + 定改法 + 定难度**，★ 为真正换路由铺路。

---

## 一、★★★ 逐处计划（★ 后继**逐字**来自官方索引）

| # | 站点 | 现调（废弃） | 官方后继 | 改法 |
|---|---|---|---|---|
| 1 | `sw_render_material.py:345` | `IModelDocExtension::DeleteRenderMaterial` | `IModelDocExtension::DeleteDisplayStateSpecificRenderMaterial` | `adapt-args` |
| 2 | `sw_part.py:1536` | `IFeatureManager::FeatureLinearPattern5` | `IFeatureManager::CreateFeature` | ★ **`needs-feature-data`** |
| 3 | `sw_part.py:2544` | `IFeatureManager::FeatureLinearPattern5` | `IFeatureManager::CreateFeature` | ★ **`needs-feature-data`** |
| 4 | `sw_pattern.py:548` | `IFeatureManager::FeatureLocalCurveDrivenPattern` | `IFeatureManager::CreateFeature` | ★ **`needs-feature-data`** |
| 5 | `sw_sheet_metal.py:1440` | `IFeatureManager::InsertFormToolFeature` | `IFeatureManager::CreateDefinition` | ★ **`needs-feature-data`** |
| 6 | `sw_sheet_metal.py:311` | `IBendsFeatureData::KFactor` | `IBendsFeatureData::GetCustomBendAllowance` | `adapt-args` |
| 7 | `sw_simulation.py:803` | `IModelDoc2::MaterialIdName` | `IPartDoc::GetMaterialPropertyName2` | `adapt-args` |

⇒ ★ **难度分层：`needs-feature-data` 4 处 · `adapt-args` 3 处 · `rename` 0 处**。

★★★ **4 处要先造 `*FeatureData`** ⇒ ★ **工作量比「改名」大一个数量级** ⇒ ★ **不许当成改名**（★ 单独立判据钉住）。

---

## 二、★★★ 本轮的关键教训：**判废弃不能只 grep `obsolete`**

★ 我第一遍用 `grep -ci 'obsolete'` 查官方页，★ 结论是「5/6 是废弃、`DeleteRenderMaterial` **不是**」—— ★★ **错的**。

★ `IModelDocExtension::DeleteRenderMaterial` 的废弃句逐字是：

> **「Not supported in SOLIDWORKS 2011 and later. Superseded by [[…DeleteDisplayStateSpecificRenderMaterial]] and [[…IDeleteDisplayStateSpecificRenderMaterial]].」**

★★ **它不含 `Obsolete` 这个词** ⇒ ★ grep 必然漏。

★★★ **定则：判「是否废弃」必须查 `official-obsolete-index.json`** ——
★ 它由 `tools/build_obsolete_index.py` 按**多种形态**建成（★ 实测 `obsolete_count` **1671**）；
★ **grep 单个词只会给出假阴性**。

★ 废弃句的**已知形态**（★ 本轮实测三种）：
1. `Obsolete. Superseded by [[X]] and [[Y]].`
2. `Obsolete. See [[X]] and the Remarks in [[Y]].`
3. `Not supported in SOLIDWORKS 2011 and later. Superseded by [[X]] and [[Y]].`

---

## 三、★★ 另一条教训：查索引要用**被废弃成员所在的接口**

★ `IModelDoc2::MaterialIdName` 的后继是 **`IPartDoc::GetMaterialPropertyName2`** ——
★★ **接口变了**。★ 我第一次查索引用的是**后继的**接口（`IPartDoc`）⇒ ★ **查不到** ⇒ 判据当场红。
⇒ ★★ **定则：查索引的键 = `(源接口, 成员名)`，★ 不是 `(后继接口, 成员名)`。**

---

## 四、需求

### FR-001 ★★ 7 处逐处有计划（成员 · 源接口 · 后继 · 改法）
- **验收场景**：`test_every_real_hit_site_has_a_plan` 通过。

### FR-002 ★★★ 后继必须**逐字**来自官方索引（★ 不许手抄）
- **规则**：每处的后继必须**等于** `official-obsolete-index.json` 给的那个（★ 手抄 = 双盲，★ 本仓铁律 6）。
- **验收场景**：`test_successors_come_from_the_official_index` 通过；★ 改一个后继即红。

### FR-003 ★★★ 难度不许低估：`needs-feature-data` ≥ **4**
- **规则**：★ 4 处要先造 `*FeatureData`（★ **大改**），★ 不许降级成「改名」。
- **验收场景**：`test_difficulty_tiers_are_not_understated` 通过。

### FR-004 ★★ 6 名全部**是废弃成员**（★ 经索引确认）
- **规则**：6 名在索引里**都有后继**；★ 且「废弃句形态表」≥3 条。
- **验收场景**：`test_all_six_names_are_deprecated_via_the_index` 通过。

### FR-005 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过。

---

## 五、非目标

- **不**本轮换路由（★ 3 处 `adapt-args` 要先查后继的实参表；★ 4 处 `needs-feature-data` 要先造数据对象）。
- **不**改 `scripts/` ⇒ ★ **不跑生成器链**。

## 六、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 非法改法 ⇒ 报错；假站点 ⇒ 报错；难度降级 ⇒ 报错 |
| SC-2 | 判据**是绿的** | `tests/test_routing_plan_real_hits.py` **5/5 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 后继与索引一致 | 7/7 逐字相同 |

## 七、未过门（本轮不做，如实登记）

- **7 处换路由本体未做** —— ★ 分两批：★ 先做 3 处 `adapt-args`（★ 便宜），★ 再做 4 处 `needs-feature-data`（★ 大改）。
- **`KFactor` / `MaterialIdName` 是**读**（★ 只要 Get 侧后继）** —— ★ 但两者都**换了接口/返回形态**，★ 要真机验。
- 高危写盘 · `create_hem` 行为证据 · 223 的 8 条既有红 · 未提交未部署。
