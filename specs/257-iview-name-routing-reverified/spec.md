# Spec — 换路由后的**真机复验**（`list_views` / `get_view_name`）

**Feature**: `specs/257-iview-name-routing-reverified/`
**日期**: 2026-10-10
**上游**: `specs/256-iview-name-routing-done/`（★ 改了路由但**没跑过改后的函数**）
**本轮只做一件事**：★ 在**真机**上跑改后的函数，回答「**删了兜底会不会丢名字**」。

---

## 一、背景（256 的未过门 1）

★ 256 把 4 处 `IView::Name` 换掉了，但**只在真机上验过「两个成员等价」**，
★ **没跑过改后的函数**。★ 本切片补上。

---

## 二、★★★ 真机读数（`output/_probe257_reverify.py` · SW rev **34.4.1**）

★ 走护栏（预检「读到文档 0 个」）· 图纸 `output/_probe255_views.SLDDRW`（★ 255 造的 4 视图图）**只读**打开、**未保存关闭**。

| 入口 | 读数 |
|---|---|
| ① `sw_drawing_query.list_views(doc)`（★ 含 :194 换路由点） | ★ **3 个视图**：`工程图视图1` / `工程图视图2` / `工程图视图3` |
| ② `sw_drawing_view.get_view_name(view)`（★ 含 :436 换路由点） | ★ **4 个全部拿到名字**：`图纸1` / `工程图视图1` / `工程图视图2` / `工程图视图3` |
| ③ `sw_drawing_view.list_drawing_views_report(doc)` | `ok=True` · `views=3` |
| ★ 异常数 | **0** |

⇒ ★★★ **换路由没有破坏任何功能** —— ★ 名字**照样取得到**。
★★ **为什么**：★ 兜底只在 `GetName2` **抛异常**时才走到；★ 真机上 `GetName2` **正常返回**。

---

## 三、★★★ 本轮**额外修**的一个缺陷：**docstring 与代码不符**

★ `sw_drawing_view.get_view_name` 的 docstring 原本逐字写着：

> ★★★★ **⇒ 统一成同一个写法** —— ★ **兜底不能删**：★ 老成员**可能仍可调**、★★ 而「两代都试」**最稳** ✓

★★ 而 256 把兜底**删了** ⇒ ★ **文档串直接和代码矛盾**。
★ 本仓原则逐字：**「文档串与代码不符比没有文档更糟」**（★ 那句话就写在同一个 docstring 里）。
★ **已订正**：docstring 改成「**只用现行的 `GetName2`**；★ 取不到就报空串」，
★ 并写明**行为变化**（★ `GetName2` 抛异常时**报空串**，★ 不再回落）与**依据落点**（254/255/256 三个规格）。

---

## 四、需求

### FR-001 ★★★ 换路由后功能正常（真机）

- **规则**：`list_views` ≥3 个视图 · `get_view_name` 4 个名字**全非空** · `report.ok=True` · **异常 0**。
- **验收场景**：`test_rerouted_functions_still_work_on_real_machine` 通过；★ 任一处坏即红。

### FR-002 ★★ 名字必须**非空**（★ 直接回答「会不会丢名字」）

- **规则**：4 个视图的名字**全部非空**；★ 且复验过程**无异常**（★ 否则结论不可用）。
- **验收场景**：`test_names_are_not_empty_after_removing_the_fallback` 通过。

### FR-003 ★★ 判据必须能红

- **验收场景**：`test_pure_function_is_red_able` 通过（★ 空名字 / 有异常 / 两入口数不一致）。

### FR-004 ★ docstring 必须与代码一致

- **规则**：`get_view_name` 的 docstring **不得**再写「兜底不能删」。
- **验收场景**：★ grep 复核（见 `tasks.md` T-003）。

### FR-005 ★★ 改了 `scripts/` ⇒ **必须跑生成器链**

- **验收场景**：7 步全 OK。

---

## 五、非目标

- **不**再改路由（★ 256 已定）。
- **不**动其它 `Name` 调用（★ 248 判过 47 处是假命中）。

## 六、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 空名字 ⇒ 「名字丢了」· 有异常 ⇒ 「破坏了功能」· 数不一致 ⇒ 报错 |
| SC-2 | 判据**是绿的** | `tests/test_iview_name_routing_reverified.py` **3/3 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 生成器链 | 7 步全 OK |
| SC-5 | ★ 真机只读 | 护栏预检「读到文档 0 个」· ★ 图纸**已关闭且未保存** |

## 七、未过门（本轮不做，如实登记）

- **250 的 7 处真命中**（`FeatureLinearPattern5` 等）仍未换路由。
- **251 的 `SketchTrim` 4 处**仍未换路由。
- **高危写盘**（`SaveAs3` · `create_draft` · `create_profile_center_mate`）。
- 10 条 `byref-tail` 真机验证 · 门禁 R8 每日跨天假红 · 223 的 8 条既有红 · 未提交未部署。
