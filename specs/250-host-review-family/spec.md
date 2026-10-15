# Spec — 245 其余 **13 条**命中名的宿主表达式级表态

**Feature**: `specs/250-host-review-family/`
**日期**: 2026-10-09
**上游**: `specs/248-name-host-adjudication/`（★ 248 只把 `Name` 一个名做到宿主级；★ 本切片把**其余 13 个名**一次做完）
**本轮只做一件事**：把 245 的**名级**结论（13 条）升级为**宿主表达式级 + 机检自洽**的表态。

---

## 一、背景（245 的名级结论**没有机检**）

245 的 `_HOST_REVIEW` 每个命中名只登记 **1~2 个证据站点** + 一段**散文依据**：
「宿主 `extension` = `model.Extension` ⇒ IModelDocExtension」。

★ 问题有三：

| # | 问题 | 后果 |
|---|---|---|
| 1 | **散文依据不被机检** | ★ 写错了也没人报（★ 「一句话不是守卫」） |
| 2 | **证据只登记 1 处** | ★ 真树上有 2 处站点时，另 1 处**没进表**（`FeatureLinearPattern5`） |
| 3 | **没有「接口」字段** | ★ 无法机检「`real-hit` ⟺ 宿主接口 == 条目接口」这条**定义** |

★★ 更关键的：**一个命中名可以跨多个条目接口**（★ 实测）：

| 名 | 条目接口 |
|---|---|
| `GetMassProperties` | `IModelDoc2` · `ISldWorks` |
| `GetSplines` | `ISketchBlockDefinition` · `IView` |
| `KFactor` | `IBendsFeatureData` · `IOneBendFeatureData` · `ISheetMetalFeatureData` |

⇒ ★ 名级表态**说不清**「我们调的是哪一个接口的成员」—— ★ 必须把**接口**写进表里。

---

## 二、本轮实测（13 名 · 14 处站点）

| 名 | 宿主表达式 | 接口 | 表态 |
|---|---|---|---|
| `DeleteRenderMaterial` | `extension` | `IModelDocExtension` | ★ 真命中 |
| `FeatureLinearPattern5` | `model.FeatureManager` · `get_com_member(model,"FeatureManager")` | `IFeatureManager` | ★ 真命中（**2 处**） |
| `FeatureLocalCurveDrivenPattern` | `fm` | `IFeatureManager` | ★ 真命中 |
| `InsertFormToolFeature` | `_mgr` | `IFeatureManager` | ★ 真命中 |
| `KFactor` | `definition` | `IBendsFeatureData` | ★ 真命中（★ 落在 3 个条目接口之一） |
| `MaterialIdName` | `model` | `IModelDoc2` | ★ 真命中 |
| `GetArcs2` / `GetEllipses3` / `GetLines2` / `GetPolylines` / `GetSplines` | `sketch` | `ISketch` | 假命中（★ 条目是 `IView` / `ISketchBlockDefinition`） |
| `GetMassProperties` | `extension` | `IModelDocExtension` | 假命中（★ 条目是 `IModelDoc2` / `ISldWorks`；★ 我们调的正是**后继**） |
| `SketchTrim` | `get_com_member(model,"SketchManager")` | `ISketchManager` | 假命中（★ `ISketchManager::SketchTrim` **非废弃**） |

⇒ ★ **真命中 7 处 · 假命中 7 处** ⇒ ★ **245 的 13 条名级结论全部复核通过**（★ 无一处翻案）。

---

## 三、需求

### FR-001 每个**命中名**都要有宿主表达式级表态（★ 含接口字段）

- **来源**：248 的 `_NAME_HOST_REVIEW` 形态 + 245 的 `_HOST_REVIEW`。
- **规则**：`_HOST_EXPR_REVIEW` 覆盖 248 未做的**全部**命中名（≥ **13**），每条给 `code` + **宿主接口** + 依据 + **全部站点**。
- **验收场景**：`test_every_remaining_name_is_adjudicated` 通过；★ 少一个名即红。

### FR-002 ★★ 表态必须与**该名的全部条目接口**自洽

- **来源**：官方索引 —— 一个成员名可跨多接口（★ 见 §一 表）。
- **规则**：`code == real-hit` ⟺ **宿主接口 ∈ 该名的条目接口集合**（★ 集合，不是单个）。
- **验收场景**：同上（纯函数第 ③ 查项）；★★ **能红的判据**：把 `SketchTrim` 翻成 `real-hit` ⇒ 当场红。

### FR-003 ★★ 判据必须能红（合成负例）

- **来源**：本项目铁律（「不能红的判据等于空判据」；★ 且**首跑全绿 = 可疑信号**）。
- **规则**：三组负例必须被判出：① 冒出新名；② 表态与接口矛盾；③ 表里登记的名被删掉。
- **验收场景**：`test_criterion_is_red_able` 通过。

### FR-004 证据站点必须与重算结果**逐字相等**（★ 不是子集）

- **来源**：本项目纪律（「比对原始转储」）。
- **规则**：每个名的证据站点集合**等于**重算集合 —— ★ 因为本轮已把 **14 处全部**登记。
- **验收场景**：`test_every_remaining_name_is_adjudicated` 通过；★ 改任一行号即红。

### FR-005 下界（只增不减）

- **来源**：本项目纪律。
- **规则**：名 ≥ **13** · 站点 ≥ **14** · 真命中站点 ≥ **7** · 假命中站点 ≥ **7**。
- **验收场景**：`test_lower_bounds` 通过。

### FR-006 ★★ 与 245 的**名级**表态跨规格一致

- **来源**：245 的 `_HOST_REVIEW`（★ 本切片的复核对象）。
- **规则**：本表判「有名级真命中」⇒ 245 的 code ∈ {`real-hit`, `mixed`}；★ 全假 ⇒ 245 的 code == `false-hit`。
- **验收场景**：`test_consistent_with_245_name_level_verdict` 通过；★ 两表漂移即红。

### FR-007 调用口径与互锁测试**逐条一致**（防漂移）

- **来源**：本项目纪律（244 曾因口径凭印象写，读数差 4）。
- **验收场景**：`test_scan_parity_with_interlock` 通过。

### FR-008 ★ **不许**改索引生成器 / 靶子表 / `scripts/sw_*.py`

- **来源**：243/244/248/249 的既有裁决。
- **规则**：本轮**只写判据**，真树与表一行不改。
- **验收场景**：mtime 核（见 `acceptance.md` §三）。

---

## 四、非目标

- **不**改 245 的 `_HOST_REVIEW` —— ★ 本轮的价值是**独立复核**它（★ 改了它，复核就没意义了）。
- **不**换路由（★ 7 处真命中属「需 COM 授权」的待办）。
- **不**动 248 已做掉的 `Name`（★ `DONE_IN_248` 跳过集）。
- **不**改 `tools/build_obsolete_index.py` / `scripts/sw_com_traps.py`。

## 五、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 清空表 ⇒ **13 条**未表态；翻 `SketchTrim` / `GetArcs2` ⇒ 「表态与接口矛盾」 |
| SC-2 | 判据**是绿的** | `tests/test_obsolete_host_review_family.py` **6/6 通过** |
| SC-3 | 相关族回归不破 | 248 + 249 + 250 三文件 **18 passed** |
| SC-4 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-5 | 未改 `scripts/` 与 `tools/` | mtime 核 |

## 六、未过门（本轮不做，如实登记）

- **7 处真命中未换路由**（★ 需 COM 授权；★ `FeatureLinearPattern5` / `FeatureLocalCurveDrivenPattern` / `InsertFormToolFeature`
  都**不是 drop-in** —— 要先造 `I*FeatureData`）。
- **245 的名级表态未被改动** —— ★ 本轮是**独立复核**（★ 复核结论 = 13 条**全部通过**，无翻案）。
- **6 条索引错后继仍未修**。
- 真机未验；223 的 8 条既有红未修；未提交未部署。
