# Acceptance — 换路由后的真机复验

**Feature**: `specs/257-iview-name-routing-reverified/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 3/3 绿 · 红基线成立 · 生成器链 7 步 OK · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★ **换路由没有破坏功能** —— 真机上 `list_views` 拿 3 个视图、`get_view_name` **4 个名字全非空**。
★ 并**顺手修掉**一个我自己引入的缺陷：**docstring 与代码不符**。

---

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 换路由后功能正常（真机） | `test_rerouted_functions_still_work_on_real_machine` | ✅ 3 视图 · 4 名字 · `ok=True` · **异常 0** |
| FR-002 | ★★ 名字必须**非空** | `test_names_are_not_empty_after_removing_the_fallback` | ✅ 4/4 非空 |
| FR-003 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 三组负例全红 |
| FR-004 | ★ docstring 与代码一致 | grep（§四） | ✅ 「兜底不能删」已无 |
| FR-005 | ★★ 生成器链 | 7 步 | ✅ 全 OK |

---

## 二、★★ 红基线

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ |
| 有空名字 | 「名字丢了」 | ✅ `['\`get_view_name\` 只拿到 2 个名字（< 4）', '\`get_view_name\` 回了**空串** ⇒ 名字丢了']` |
| 有异常 | 「破坏了功能」 | ✅ `['真机复验有 1 处异常 ⇒ 换路由**破坏了功能**']` |
| 两入口数不一致 | 报错 | ✅ |

---

## 三、★★★ 真机读数（★ 唯一证据）

★ 走护栏（预检「读到文档 **0** 个」）· SW **rev 34.4.1** · 图纸 `output/_probe255_views.SLDDRW`（★ 255 造的 4 视图图）**只读**打开、**未保存关闭**。

| 入口 | 读数 |
|---|---|
| ① `sw_drawing_query.list_views(doc)` | ★ **3 个视图**：`工程图视图1` / `工程图视图2` / `工程图视图3` |
| ② `sw_drawing_view.get_view_name(view)` | ★ **4 个全非空**：`图纸1` / `工程图视图1` / `工程图视图2` / `工程图视图3` |
| ③ `list_drawing_views_report(doc)` | `ok=True` · `views=3` |
| ★ 异常 | **0** |

⇒ ★★★ **换路由没有破坏功能**。★★ **为什么**：★ 兜底只在 `GetName2` **抛异常**时走到；★ 真机上 `GetName2` **正常返回**。

---

## 四、★★★ 本轮**额外修**：docstring 与代码不符

★ `sw_drawing_view.get_view_name` 的 docstring 原本逐字写着：

> ★★★★ **⇒ 统一成同一个写法** —— ★ **兜底不能删**：★ 老成员**可能仍可调**、★★ 而「两代都试」**最稳** ✓

★★ 而 256 把兜底**删了** ⇒ ★ **文档串直接和代码矛盾** ——
★ 而本仓原则逐字 **「文档串与代码不符比没有文档更糟」**（★ 那句话**就写在同一个 docstring 里**）。

★ **已订正**：docstring 改为「**只用现行的 `GetName2`**；★ 取不到就报空串」，
★ 并写明**行为变化**（★ 抛异常时报**空串**，不再回落）与**依据落点**（254/255/256 三个规格）。

★ 验收：`grep -n "兜底不能删" scripts/sw_drawing_view.py` ⇒ ★ **无输出** ✓

---

## 五、生成器链（★ 改了 `scripts/` ⇒ 必跑）

| 步骤 | 结果 |
|---|---|
| `scripts/release_check.py` → `gen_level_audit.py` → `tools/gen_metrics.py` → `gen_harvest_digest.py` → `build_union_map.py` → `gen_dead_ends.py` → `release_check.py` | ✅ **7/7 OK** |

---

## 六、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gate_details` 条数 | **47** |

---

## 七、未过门（如实登记）

1. **250 的 7 处真命中**（`FeatureLinearPattern5` / `FeatureLocalCurveDrivenPattern` / `InsertFormToolFeature`）仍未换路由。
2. **251 的 `SketchTrim` 4 处**仍未换路由。
3. **高危写盘**（`SaveAs3` · `create_draft` · `create_profile_center_mate`）。
4. **10 条 `byref-tail` 真机验证** · **门禁 R8 每日跨天假红** · **223 的 8 条既有红**。
5. **未提交 / 未部署**；**未删任何文件**。
