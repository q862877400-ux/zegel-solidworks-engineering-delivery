# Spec — `create_base_flange` 的失败**属于一族已知现象**（★ 合并，★ 免得一轮一个特征试参数）

**Feature**: `specs/265-base-flange-family-phenomenon/`
**日期**: 2026-10-10
**上游**: `specs/264-base-flange-two-paths/`（★ 判「失败在环境/前置」）
**本轮只做一件事**：★ 把**族现象**合并 + 查**具体环境因素**。

---

## 一、★★★ 族现象（★ 事实 34 早就记了）

★ `docs/known-facts.md` **事实 34**（**2026-10-01**）逐字：

> ✓ `create_base_flange`（真建出特征：特征树出现「钣金6 / 基体-法兰1 / 平展型式6」）…
> … 其余三条现在**卡在同一层** `CreateFeature(N)`

⇒ ★★★ **「`CreateFeature` 回 `None`」不是钣金独有，是**一族现象****：

| 特征 | 事实 34 的记法 |
|---|---|
| ★ **`create_base_flange`** | ★ **2026-10-01 成功** ⇒ 现在失败 = **回归** |
| `create_one_bend` | ★ 从 `CreateDefinition(33) 返回 None` **前推到** `CreateFeature(35) 创建失败` |
| `create_draft` | ★ `swFmDraft(3)` 不在 35 个常量里 |
| `create_edge_flange` | ★ 设 `ReverseDirection` 报 `Property ... can not be set` |
| `create_gusset` | ★ 属性层 8/8 过，`CreateFeature(118)` **仍 None** |

★★ **为什么合并值钱**：★ 不合并 ⇒ ★ 下一轮会**一个特征一个特征地试参数**；
★ 合并后 ⇒ ★ **方向转到「这一族的共同环境因素」**。

---

## 二、★★ 本轮真机环境读数（`output/_probe265_env.py` · SW rev **34.4.1**）

| 项 | 读数 |
|---|---|
| 默认**零件模板** | ★ `gb_part.prtdot`（★ 国标模板） |
| ★ **本机零件模板个数** | ★ **1**（★ 只有 `gb_part.prtdot`）⇒ ★ **「换模板」这条路走不通** |
| ★ `GetAddInObject('SldWorks.SheetMetal')` | ★ **`None`** |
| ★ 换 `Front Plane` | ★ `CreateFeature` **仍 `None`** ⇒ ★ **平面不是因素** |
| `Top` 平面 | ★ **选不上**（`无法选择基准面: Top`）⇒ ★ 官方示例那个平面**在本机不可用** |

---

## 三、★★ 迟到绑定下**不可用**的成员（★ 留档）

| 成员 | 结果 |
|---|---|
| `IsAddInRegistered` | ★ `AttributeError`（★ 迟到绑定下没有它） |
| `GetCommandManager(0).GetTabs` | ★ `GetCommandManager` 回 `None` ⇒ 链式取不到 |

---

## 四、需求

### FR-001 ★★★ 族现象（★ 5 个特征卡在同一层）
- **规则**：族里 **≥5** 条（★ 4 个既有 + `create_base_flange`），★ **每条要写出处**。
- **验收场景**：`test_it_is_a_family_phenomenon` 通过。

### FR-002 ★★ 平面不是因素
- **验收场景**：`test_plane_is_not_a_factor` 通过。

### FR-003 ★★ 换模板**不可行**（★ 本机只有 1 个零件模板）
- **验收场景**：`test_template_switch_is_not_available` 通过。

### FR-004 ★★ 不可用成员留档
- **验收场景**：`test_unavailable_members_are_recorded` 通过。

### FR-005 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过。

---

## 五、非目标

- **不**改 `scripts/`（★ 根因未定到可改的点）⇒ ★ **不跑生成器链**。
- **不**动 `docs/known-facts.md`（★ 那是**既有事实**，★ 本轮只**引用**）。

## 六、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | `Front Plane` 成功 / 模板多于 1 个 / 族条数不对 ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_base_flange_family_phenomenon.py` **5/5 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 真机 | 护栏预检「读到文档 0 个」· ★ 临时零件**已关闭** |

## 七、未过门（本轮不做，如实登记）

- ★★ **根因仍未定到可改的点** —— ★ 已排除：顺序 · 常量 · 选前 · **现代路的用法** · **平面** · **模板**（★ 只有 1 个，换不了）。
  ★ **下一步线索**：① **查这一族的共同环境因素**（★ 5 个特征卡在同一层 ⇒ ★ 更像**环境/许可/选项**）；
  ② 查 SW 的**许可类型/席位**；③ 查**系统选项**（★ 例如钣金相关开关）。
- `_read_k_factor` 仍未被真机走到（★ 阻塞 = 造不出件）。
- 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 8 条既有红 · 未提交未部署。
