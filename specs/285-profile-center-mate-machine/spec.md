# Spec — `create_profile_center_mate` **首次真机验证**：★ `CreateMateData` 通、★ `CreateMate` **静默回 `None`**

**Feature**: `specs/285-profile-center-mate-machine/`
**日期**: 2026-10-10
**上游**: ★ ② 段第 3 条（★ 最后一条：「`create_profile_center_mate` 真机验证」）
**授权**: ★ 业主**已授权**（`GOAL.md` §三 **C · 高危/写盘**）
**本轮只做一件事**：★ **首次真机跑** `create_profile_center_mate`，★ **逐层量**。

---

## 一、★★★ 真机读数（SW **34.4.1** · ★ 走 `sw_guard` · ★ 夹具 = 换刀主轴装配（11 零件 · 92 面 / 31 圆柱面））

| # | 层 | ★ 读数 |
|---|---|---|
| ① | `IAssemblyDoc::CreateMateData(24)` | ★★ **回对象**（`CDispatch`）✓ |
| ② | `EntitiesToMate` = **随便两个面** | 设得上 ⇒ ★ `CreateMate` **`None`** ✗ |
| ② | `EntitiesToMate` = **两个圆柱面** | 设得上 ⇒ ★ `CreateMate` **`None`** ✗ |
| ② | `EntitiesToMate` = **另一对圆柱面** | 设得上 ⇒ ★ `CreateMate` **`None`** ✗ |
| ③ | ★ 消息栈 | ★★ **`n = 0`（空）** ⇒ ★★★ **读不到任何原因** |
| ④ | 「预选 + Mark 1」那条臂 | ★ **选中 0 个** ⇒ ★★ **该臂不成立**（★ 装配里选面**没选上**） |

⇒ ★★★ **两条结论**：
1. ★★ **`CreateMateData(24)` 通** ⇒ ★ **不是** 280/281 那种「`AccessSelections` 结构性不可调用」⇒ ★ **不同因**。
2. ★★★ **`CreateMate` 回 `None` 且**消息栈空**** ⇒ ★ **静默失败**（★ 与 **263** 同族）。

---

## 二、★★★ 官方**两句话不完全一致**（★ 两条路都试了）

| 来源 | ★ 逐字 |
|---|---|
| `IProfileCenterMateFeatureData/_overview.md` | ★ 创建三步 · ★ 第 2 步：「Specify **`EntitiesToMate`** **or** use `SelectByID2` to **pre-select** the entities using **Mark = 1**」 |
| `IAssemblyDoc::CreateMate.md` | ★ 「an **asterisk** indicates that **pre-selection** of mate entities during mate creation is supported」 |
| ★ `IProfileCenterMateFeatureData` | ★★ **无星号** ⇒ ★ **官方自己说本类型不支持预选** |

⇒ ★★ **两句**不完全一致**** ⇒ ★ 本轮**两条路都试**（★ 其中预选那条**没选上** ⇒ ★ **不成立**，★ 如实标注）。

---

## 三、需求

### FR-001 ★★★ `CreateMateData` **通**（★ 与 280/281 不同因）
- **验收场景**：`test_create_mate_data_returns_an_object` 通过。

### FR-002 ★★★ 三条实体臂**全失败**
- **验收场景**：`test_all_entity_arms_fail` 通过。

### FR-003 ★★★ **静默失败**（★ 消息栈空）
- **验收场景**：`test_the_failure_is_silent` 通过。

### FR-004 ★★ 预选臂**不成立**要如实标
- **验收场景**：`test_the_preselect_arm_is_marked_as_inconclusive` 通过。

### FR-005 ★★★ 官方两句话**要一起引**
- **验收场景**：`test_both_official_statements_are_quoted` 通过。

### FR-006 ★★★ 回源码核：★ 源码**仍走官方路**
- **验收场景**：`test_source_still_follows_the_official_path` 通过。

### FR-007 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过（★ 七组负例）。

---

## 四、非目标

- ★★ **不改** `create_profile_center_mate` 的实现（★ 官方三步逐条照做 ⇒ ★ **不是代码错**）。
- ★ **不查**「`CreateMate` 为什么静默回 None」（★ 消息栈空 ⇒ ★ 本机**读不出原因** ⇒ ★ 另开切片）。

## 五、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | `CreateMateData` 不通 / 某实体臂成功 / 栈非空 / 预选臂读数不对 / 星号结论错 / 结论不对 / 源码不走官方路 ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_profile_center_mate_machine.py` **7/7 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 生成器链已跑 | 7 步全 `exit 0`（★ 改了 `scripts/`） |
| SC-5 | ★ 真机无残留 | 护栏预检「读到文档 0 个」 |

## 六、未过门（本轮不做，如实登记）

- ★★★ **`CreateMate` 为什么静默回 `None`** 未查（★ **消息栈空** ⇒ ★ 本机**读不出** ⇒ ★ 需要**别的**诊断手段）。
- ★★ **预选那条路没选上**（★ 装配里选面的正确姿势未查明）⇒ ★ 若查明，★ 可再试一次。
- ★ 12 条 `arity` 接线 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 B1–B5 · 未提交未部署。
