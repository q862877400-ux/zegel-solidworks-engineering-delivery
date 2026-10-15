# Spec — `IView::Name` ⇒ `GetName2` 换路由的**真机等价性先量**（★ 本轮只量不改）

**Feature**: `specs/254-iview-name-routing/`
**日期**: 2026-10-10
**上游**: `specs/248-name-host-adjudication/`（★ 判出 **4 处 `IView::Name` 真命中**）
**本轮只做一件事**：**先量** —— 后继 `GetName2` 与被废弃的 `Name` 在**真机**上是否等价。

---

## 一、背景

248 判出 `Name` 有 **4 处真命中**（宿主 `view` ×3 + 宿主 `av` ×1）：

| 站点 | 写法 |
|---|---|
| `sw_drawing_query.py:194` | `get_com_member(view, "GetName2")` **失败后的兜底** `get_com_member(view, "Name")` |
| `sw_drawing_query.py:264` | 同上 |
| `sw_drawing_view.py:436` | `return str(get_com_member(view, "Name") or "")` |
| `sw_review.py:637` | `get_com_member(av, "Name")`（`av = model.ActiveView`） |

★ 换路由（去掉对 `IView::Name` 的调用）的**前提** = 后继 `GetName2` **真机等价**。

---

## 二、★★★ 真机读数（`output/_probe254_viewname.py` · SW rev **34.4.1**）

★ 走护栏（预检「读到文档 0 个」）· 打开 `output/pdf-probe.SLDDRW`（**只读**）· **关闭且未保存**。

| 项 | 读数 |
|---|---|
| 视图数 | **1**（★ **是「图纸本身」那个伪视图**） |
| `Name` | `'图纸1'` |
| `GetName2` | `'图纸1'` |
| ★ 汇总 | **同 1 · 异 0 · 失败 0** |

⇒ ★ **两者在该样本上等价**。
★★ **但样本只有 1 个、且是伪视图** ⇒ ★★ **证据弱** ⇒ ★ **本轮不改代码**。

---

## 三、★★★ 真机踩的三个坑（★ 都已进判据）

| # | 坑 | 正解 |
|---|---|---|
| 1 | `ISheet` 上**没有** `GetFirstView`（`AttributeError`） | ★ 用 `IModelDoc2::GetFirstView` + `IView::GetNextView` |
| 2 | **只读打开**时 `doc.GetCurrentSheet` 回 **`None`** | ★ 别从 `sheet` 入手 |
| 3 | ★★ **`IView::GetName2` 在 COM 迟到绑定下是「属性」不是方法** | ★ **不能加括号**（`v.GetName2` ✓ / `v.GetName2()` ✗ ⇒ `'str' object is not callable`） |

★ 第 3 条尤其反直觉：★ 名字带 `Get` 前缀，★ 但 `IModelDoc2/GetName2` 这类成员在**迟到绑定**下**按属性返回**。
★ 真树现有写法（`get_com_member(view, "GetName2")` = 属性访问）**是对的**。

---

## 四、需求

### FR-001 4 处靶子必须与 248 的证据逐字一致

- **来源**：248 的 `_HOST_REVIEW["Name"]`（★ `real-hit` 站点）。
- **验收场景**：`test_four_view_name_sites_are_the_248_ones` 通过；★ 站点漂移即红。

### FR-002 ★★ 真机等价性读数必须「有样本、且等价」

- **来源**：本仓纪律（「声明要能被证据判定」）。
- **规则**：`views ≥ 1` · `diff == 0` · `fail == 0` · `Name == GetName2`。
- **验收场景**：`test_machine_equivalence_reading` 通过。

### FR-003 ★★★ **不许把弱证据当强证据**

- **来源**：★ 本轮实测 —— 「1 个伪视图」与「20 个模型视图」在**只看 same/diff/fail** 时**同形**。
- **规则**：样本必须被**显式**标注（`sample` 里要出现「伪视图」）；★ 且 `views < 5` ⇒ ★ **不得据此改代码**。
- **验收场景**：`test_sample_is_explicitly_weak` 通过。

### FR-004 ★★ 真机踩的坑必须留在判据里

- **来源**：本仓纪律（「踩过的坑要变成判据，不是散文」）。
- **规则**：`MACHINE_PITFALLS` ≥ 3 条，且必须含 `GetFirstView` / `GetCurrentSheet` / `属性` 三个关键词。
- **验收场景**：`test_machine_pitfalls_are_recorded` 通过。

### FR-005 ★★ 判据必须能红

- **验收场景**：`test_pure_function_is_red_able` 通过（★ 三组负例：样本 0 / 不等价 / 站点全缺）。

### FR-006 ★ **本轮不改代码**

- **来源**：★ 证据弱。
- **规则**：`scripts/sw_drawing_query.py` · `sw_drawing_view.py` · `sw_review.py` **一行不改**。
- **验收场景**：mtime 核。

---

## 五、非目标

- **不**换路由（★ 样本太弱）。
- **不**为了「凑证据」而去**造**一张有模型视图的图纸 —— ★ 那是**独立一件工作**（且要写盘）。
  ★ **触发条件**：★ 若下一轮能拿到 ≥5 个**真实模型视图**的图纸 ⇒ ★ 那时才换路由。

## 六、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 样本 0 ⇒ 「证据不足」· `diff=1` ⇒ 「不等价」· 站点全缺 ⇒ 报错 |
| SC-2 | 判据**是绿的** | `tests/test_iview_name_successor_machine.py` **5/5 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 真机只读 | 护栏预检「读到文档 0 个」· ★ 工程图**已关闭且未保存** |
| SC-5 | 未改 `scripts/` | mtime 核 |

## 七、未过门（本轮不做，如实登记）

- **4 处换路由未做** —— ★ **样本太弱**（1 个伪视图）⇒ ★ 需先拿到**有真实模型视图**的图纸。
- **`sw_review.py:637` 的 `av` 站点** —— ★ 本次探针**没覆盖**（它读的是 `model.ActiveView`，需要**零件/装配**文档）。
- **10 条 `byref-tail` 的真机验证**（★ 253 的未过门）。
- 223 的 8 条既有红；未提交未部署。
