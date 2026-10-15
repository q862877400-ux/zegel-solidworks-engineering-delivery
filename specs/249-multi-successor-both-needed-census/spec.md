# Spec — 「两个后继都要」的**宿主级**先量（结论：**0 靶子**）

**Feature**: `specs/249-multi-successor-both-needed-census/`
**日期**: 2026-10-09
**上游**: `specs/247-multi-successor-adjudication/`（★ 其 §五「未过门 1」= 「16 条 `Superseded by A and B` 表达不了两个后继」）
**本轮只做一件事**：**先量** —— 真树上有没有**任何一处**「写」站点落在「两个后继」的那个废弃条目的接口上。
★ 结论：**0** ⇒ ★ **本待办没有靶子** ⇒ **关闭**（★ 不为改表形态而改表形态）。

---

## 一、背景（为什么要先量）

247 的未过门 1 说：靶子表的值是**裸成员名** ⇒ 表达不了「`Superseded by A and B`」这种**两个后继**的情形，
★ 所以要把表升级为可表达多后继 —— ★★ **但升级会改公开 MCP 工具 `deprecated_successor()` 的签名/输出**。

⇒ ★ **动手前必须先问：真树上到底有没有一条**真的**需要两个后继？**

**「需要两个后继」的定义**：存在一处站点，它的 **`(宿主接口, 成员名)` == 该条目的 `(interface, member)`**，
★ **且是「写」**（`obj.Prop = v`）—— ★ 因为「两个后继」的形态就是 **Get 侧 + Set 侧**
（`IView::Name` → `GetName2` + `SetName2`；`KFactor` → `GetCustomBendAllowance` + `SetCustomBendAllowance`）。
★ 只读 ⇒ 只要 Get 侧 ⇒ **不需要两个后继**。

---

## 二、★★★ 先量的第一版**给出了 4 条假靶子**（★ 本轮踩的坑）

第一版探针（`output/_probe249_both_successors.py`）按**裸成员名**归集站点 ⇒ 报出 **4 条**「两个后继都要」：

| 裸名 | 条数 | 真象 |
|---|---|---|
| `KFactor` | **3** | 写站点宿主是 **`ICustomBendAllowance`**（`manager.CreateCustomBendAllowance()`），★ **不是** `IBendsFeatureData` / `IOneBendFeatureData` / `ISheetMetalFeatureData` |
| `Name` | **1** | 写站点宿主是 **`IMate2`** / **`IFeature`** / **`CWStudy`**，★ **不是** `IView` |

⇒ ★★ **这正是 245/248 两轮反复证明的那件事：按裸成员名归集会骗人。**
★ 本轮把它**冻成判据**（`test_bare_name_aggregation_would_give_false_targets`，下界 **4**）。

---

## 三、需求（每条带来源与验收场景）

### FR-001 先量：条目数与被检写站点数的下界

- **来源**：本项目纪律（「可见性边界必须被量出来并冻结下界」）。
- **规则**：索引里 `Obsolete. Superseded by [[A]] and [[B]]` 且成员名在真树被调的条目 ≥ **15**；
  真树上对这批成员名的**写**站点 ≥ **7**。
- **验收场景**：`test_census_sizes_are_frozen` 通过；★ 减少即红。

### FR-002 每个写站点都要表态（宿主接口 + 依据）

- **来源**：248 的 `_NAME_HOST_REVIEW` 形态（★ 宿主级表态）。
- **规则**：`_WRITE_SITE_REVIEW` 必须**双向**覆盖：真树上的写站点全在表里；表里的条目也全在真树上。
- **验收场景**：`test_every_write_site_is_adjudicated` 通过；★ 新增/删除写站点即红。

### FR-003 ★★ 核心：**没有任何写站点落在「两个后继」的废弃接口上**

- **来源**：247 的未过门 1 的**关闭条件**。
- **规则**：纯函数 `_both_needed_failures(entries, write_review)` **必须为空**
  —— 判据 = 写站点的 `(宿主接口, 成员名)` ∈ 条目的 `(interface, member)` 集合。
- **验收场景**：`test_no_write_site_targets_a_multi_successor_interface` 通过；
  ★★ **能红的判据**：把 `sw_sheet_metal.py:257` 的宿主接口改成 `IBendsFeatureData` ⇒ 当场红。

### FR-004 ★★ 判据必须能红（合成负例）

- **来源**：本项目铁律（「不能红的判据等于空判据」）。
- **规则**：`IView` 写 `Name` ⇒ 必须判出；`IFeature` 写 `Name` ⇒ **必须不判出**（★ 反向也要验，防判据过宽）。
- **验收场景**：`test_criterion_is_red_able` 通过。

### FR-005 ★★ 把「裸名归集会给出假靶子」冻成判据

- **来源**：本轮踩的坑（见 §二）。
- **规则**：裸名口径下的假靶子条目数 ≥ **4**；★ 且**宿主级判据必须仍然为空**（两口径的差 = 假靶子）。
- **验收场景**：`test_bare_name_aggregation_would_give_false_targets` 通过。

### FR-006 与 248 的表**跨规格一致**

- **来源**：248 的 `_NAME_HOST_REVIEW`（★ 重复出现的宿主必须同接口）。
- **规则**：`feature` / `study` 这两个宿主在两表里的接口必须一致。
- **验收场景**：`test_hosts_agree_with_spec_248` 通过。

### FR-007 ★ **不许**改索引生成器、**不许**改靶子表、**不许**改任何 `scripts/sw_*.py`

- **来源**：243/244 的既有裁决。
- **规则**：本轮**只量不改** —— `tools/build_obsolete_index.py` · `scripts/sw_com_traps.py` · `scripts/sw_*.py` 一行不改。
- **验收场景**：mtime 核（见 `acceptance.md` §三）。

---

## 四、非目标

- **不**把靶子表升级为可表达多后继 —— ★ **本轮先量的结论就是「没有靶子」，所以这次不做**。
  ★ 若将来真出现靶子（`test_no_write_site_targets_a_multi_successor_interface` 变红）⇒ ★ **那时才立项**。
- **不**改公开工具 `deprecated_successor()` 的签名。
- **不**动需 COM 的六项。
- **不**碰 `IView::Name` 的 4 处真命中（★ 那属 248 的未过门）。

## 五、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 变异（把 `bend_allowance` 的接口改成 `IBendsFeatureData`）⇒ **1 条**靶子 |
| SC-2 | 判据**是绿的** | `tests/test_multi_successor_both_needed_census.py` **6/6 通过** |
| SC-3 | 相关族回归不破 | 248 + 249 两文件 **12 passed** |
| SC-4 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-5 | 未改 `scripts/` 与 `tools/` | mtime 核 |

## 六、未过门（本轮不做，如实登记）

- **靶子表仍表达不了「两个后继」** —— ★ 但**本轮的结论是「真树上没有这种靶子」** ⇒ ★ 按「没有靶子的守卫不做」原则**暂不升级**；
  ★ 触发条件 = `test_no_write_site_targets_a_multi_successor_interface` 变红。
- **4 处 `IView::Name` 真命中未换路由**（★ 248 的未过门）。
- **`motor_feature` 的接口**（`sw_motion.py:238`）★ 按「马达特征对象」登记 ——
  ★ 未逐字核官方页（★ 但它**显然不是** 15 条里任何一个接口，故不影响结论）。
- 真机未验；223 的 8 条既有红未修；未提交未部署。
