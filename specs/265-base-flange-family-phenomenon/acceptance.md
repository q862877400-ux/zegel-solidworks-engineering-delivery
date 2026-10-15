# Acceptance — `create_base_flange` 的失败属于一族已知现象

**Feature**: `specs/265-base-flange-family-phenomenon/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 5/5 绿 · 红基线成立 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★ **`CreateFeature` 回 `None` 是**一族现象**（★ 事实 34 记 4 个特征卡在同一层）**；
★ 平面**不是**因素 · ★ **换模板不可行**（★ 本机只有 1 个零件模板）。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 族现象 ≥5 条 | `test_it_is_a_family_phenomenon` | ✅ **5** 条 |
| FR-002 | ★★ 平面不是因素 | `test_plane_is_not_a_factor` | ✅ `Front Plane` 仍 `None` · `Top` 选不上 |
| FR-003 | ★★ 换模板不可行 | `test_template_switch_is_not_available` | ✅ 模板数 **1** |
| FR-004 | ★★ 不可用成员留档 | `test_unavailable_members_are_recorded` | ✅ 2 条 |
| FR-005 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 三组负例全红 |

## 二、★★ 红基线

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ |
| `Front Plane` 成功 | 报错 | ✅ `['`Front Plane` 竟然成功了 ⇒ ★ 结论要改']` |
| 模板数改成 2 | 报错 | ✅ |
| 族条数改成 3 | 报错 | ✅ `['族现象条数 3 ≠ 5 ⇒ 请同步']` |

## 三、★★★ 族现象（★ 事实 34）

| 特征 | 事实 34 的记法 |
|---|---|
| ★ **`create_base_flange`** | ★ **2026-10-01 成功** ⇒ 现在失败 = **回归** |
| `create_one_bend` | ★ 前推到 `CreateFeature(35) 创建失败` |
| `create_draft` | ★ `swFmDraft(3)` 不在 35 个常量里 |
| `create_edge_flange` | ★ 设 `ReverseDirection` 报 `can not be set` |
| `create_gusset` | ★ 属性层 8/8 过，`CreateFeature(118)` **仍 None** |

⇒ ★★ **5 个特征卡在同一层** ⇒ ★ **更像环境/许可/选项**（★ 不是单个 API 的用法）。

## 四、★★ 环境读数

| 项 | 读数 |
|---|---|
| 零件模板 | `gb_part.prtdot`（★ 唯一） |
| ★ 模板数 | **1** ⇒ ★ **换模板走不通** |
| ★ `GetAddInObject('SldWorks.SheetMetal')` | **`None`** |
| ★ 换 `Front Plane` | `CreateFeature` **仍 `None`** ⇒ ★ **平面不是因素** |
| `Top` 平面 | ★ **选不上** |

## 五、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gate_details` 条数 | **47** |

★ **生成器链未跑**（★ 没改 `scripts/`）。

## 六、未过门（如实登记）

1. ★★ **根因仍未定到可改的点** —— ★ 已排除：顺序 · 常量 · 选前 · 现代路的用法 · **平面** · **模板**。
   ★ **下一步线索**：① **查这一族的共同环境因素** · ② 查 SW **许可类型/席位** · ③ 查**系统选项**（钣金相关开关）。
2. `_read_k_factor` 仍未被真机走到（★ 阻塞 = 造不出件）。
3. 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 8 条既有红 · 未提交未部署。
