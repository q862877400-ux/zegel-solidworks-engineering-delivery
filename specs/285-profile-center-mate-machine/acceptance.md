# Acceptance — `create_profile_center_mate` 首次真机验证

**Feature**: `specs/285-profile-center-mate-machine/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 7/7 绿 · 红基线成立 · 生成器链 7/7 · 真机无残留 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★★ **本机建不出** —— ★ `CreateMateData(24)` **通**（★ 回对象），★ 而 `CreateMate` **静默回 `None`**（★ **消息栈空**）
⇒ ★★ **不是** 280/281 那种「`AccessSelections` 结构性不可调用」⇒ ★ **不同因**；★ 而**代码路线是对的**（★ 官方三步逐条照做）。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ `CreateMateData` 通 | `test_create_mate_data_returns_an_object` | ✅ 回对象 |
| FR-002 | ★★★ 三条实体臂全失败 | `test_all_entity_arms_fail` | ✅ 全 None |
| FR-003 | ★★★ 静默失败 | `test_the_failure_is_silent` | ✅ 栈 `n=0` |
| FR-004 | ★★ 预选臂不成立要如实标 | `test_the_preselect_arm_is_marked_as_inconclusive` | ✅ 选中 0 个 |
| FR-005 | ★★★ 官方两句话要一起引 | `test_both_official_statements_are_quoted` | ✅ |
| FR-006 | ★★★ 源码仍走官方路 | `test_source_still_follows_the_official_path` | ✅ 回源码核 |
| FR-007 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 七组负例全红 |

## 二、★★★ 逐层读数（SW **34.4.1** · ★ 走 `sw_guard` · ★ 夹具 = 换刀主轴装配 · 11 零件 · 92 面 / 31 圆柱面）

| # | 层 | ★ 读数 |
|---|---|---|
| ① | `IAssemblyDoc::CreateMateData(24)` | ★★ **回对象**（`CDispatch`）✓ |
| ② | `EntitiesToMate` = **随便两个面** | 设得上 ⇒ `CreateMate` **`None`** ✗ |
| ② | `EntitiesToMate` = **两个圆柱面** | 设得上 ⇒ `CreateMate` **`None`** ✗ |
| ② | `EntitiesToMate` = **另一对圆柱面** | 设得上 ⇒ `CreateMate` **`None`** ✗ |
| ③ | ★ 消息栈 | ★★ **`n = 0`（空）** ⇒ ★★★ **读不到任何原因** |
| ④ | 「预选 + Mark 1」那条臂 | ★ **选中 0 个** ⇒ ★★ **该臂不成立**（★ 如实标注） |

⇒ ★★★ **两条结论**：
1. ★★ **`CreateMateData(24)` 通** ⇒ ★ **不是** 280/281 那种「`AccessSelections` 结构性不可调用」⇒ ★ **不同因**。
2. ★★★ **`CreateMate` 回 `None` 且**消息栈空**** ⇒ ★ **静默失败**（★ 与 **263** 同族）。
★ 读数原文 `output/_probe285_mate.txt` · `_probe285_mate_cyl.txt` · `_probe285_mate_presel.txt`。

## 三、★★★ 官方**两句话不完全一致**（★ 两条路都试了）

| 来源 | ★ 逐字 |
|---|---|
| `IProfileCenterMateFeatureData/_overview.md` | ★ 创建三步 · ★ 第 2 步：「Specify **`EntitiesToMate`** **or** use `SelectByID2` to **pre-select** the entities using **Mark = 1**」 |
| `IAssemblyDoc/CreateMate.md` | ★ 「an **asterisk** indicates that **pre-selection** of mate entities during mate creation is supported」 |
| ★ `IProfileCenterMateFeatureData` | ★★ **无星号** ⇒ ★ **官方自己说本类型不支持预选** |

⇒ ★★ **两句**不完全一致**** ⇒ ★ 本轮**两条路都试**（★ 其中预选那条**没选上** ⇒ ★ **不成立**，★ 如实标注）。

## 四、★★★ 登记（★ `scripts/sw_weldment.py`）

| 位置 | 内容 |
|---|---|
| ★ `create_profile_center_mate` 的**来源块**（★ **注释**） | ★ 完整四层读数 + ★ 官方两句话 + ★ 处置 |
| ★ 该函数的**文档串** | ★ **一行**警示：「⚠★ **本机（SW 34.4.1）实测建不出**」 |

★ **行为未改** · ★ 长文本写**注释**（★ 吸取 **282** 的教训）。

## 五、★★ 红基线（★ 七组负例）

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ `[]` |
| `CreateMateData` 不通 | 报错 | ✅ `['★ `CreateMateData(24)` 应**回对象**']` |
| 某实体臂成功 | 报错 | ✅ `['★ 三条实体臂应**全失败**']` |
| 栈非空 | 报错 | ✅ `['★ 消息栈应为**空**（★ 那才是「静默」）']` |
| 预选臂读数不对 | 报错 | ✅ `['★ 预选臂应如实记「选中 0 个」']` |
| 星号结论错 | 报错 | ✅ `['★ `IProfileCenterMateFeatureData` **无**星号 ⇒ 这一格应是 `False`']` |
| 结论不对 | 报错 | ✅ `['★ 结论应是「本机建不出」']` |
| 源码不走官方路 | 报错 | ✅ `['★ 源码应仍走官方路（`CreateMateData` + `CreateMate`）']` |

## 六、生成器链（★ 改了 `scripts/`）

| 步骤 | 结果 |
|---|---|
| `release_check.py` → `gen_level_audit.py` → `gen_metrics.py` → `gen_harvest_digest.py` → `build_union_map.py` → `gen_dead_ends.py` → `release_check.py` | **7/7 `exit 0`** |

## 七、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| 日志 | `output/_gate285.log` |

★ 真机预检前后均「**读到文档 0 个**」⇒ **无残留**。

## 八、未过门（如实登记）

1. ★★★ **`CreateMate` 为什么静默回 `None`** 未查（★ **消息栈空** ⇒ ★ 本机**读不出** ⇒ ★ 需要**别的**诊断手段）。
2. ★★ **预选那条路没选上**（★ 装配里选面的正确姿势未查明）⇒ ★ 若查明，★ 可再试一次。
3. 12 条 `arity` 接线 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 B1–B5 · 未提交未部署。
