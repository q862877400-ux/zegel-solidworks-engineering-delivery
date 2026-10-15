# Acceptance — `IView::Name` 换路由的真机等价性先量

**Feature**: `specs/254-iview-name-routing/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 5/5 绿 · 红基线成立 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: 真机上 `Name` == `GetName2`（★ **但样本只有 1 个伪视图 ⇒ 证据弱 ⇒ 本轮只量不改**）。

---

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | 4 处靶子与 248 一致 | `test_four_view_name_sites_are_the_248_ones` | ✅ 全部在 248 的 `Name` 证据里 |
| FR-002 | 真机读数「有样本且等价」 | `test_machine_equivalence_reading` | ✅ 同 1 · 异 0 · 失败 0 |
| FR-003 | ★★★ 弱证据必须**显式**标注 | `test_sample_is_explicitly_weak` | ✅ `sample` 含「伪视图」· `views < 5` |
| FR-004 | 真机坑留在判据里 | `test_machine_pitfalls_are_recorded` | ✅ 3 条 · 含三个关键词 |
| FR-005 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 样本 0 / 不等价 / 站点全缺 **全红** |
| FR-006 | ★ 不改代码 | mtime 核（§三） | ✅ |

---

## 二、★★ 红基线

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | 0 条 | ✅ `0` |
| 样本置 0 | 「证据不足」 | ✅ `['真机视图数 0 < 下界 1 ⇒ 证据不足']` |
| `diff=1` | 「不等价」 | ✅ `['真机上 Name 与 GetName2 **不等价** 1 处 ⇒ **不能换路由**']` |
| 站点全缺 | 报错 | ✅ |

---

## 三、★ 未改动证明（★ 用 mtime）

| 文件 | mtime | 早于 00:10？ |
|---|---|---|
| `scripts/sw_drawing_query.py` | 见 `ls` | ✅ |
| `scripts/sw_drawing_view.py` | 见 `ls` | ✅ |
| `scripts/sw_review.py` | 见 `ls` | ✅ |

★ **本切片改过**：`tests/test_iview_name_successor_machine.py`（新）· `output/_probe254_viewname.py` / `.txt`（新）·
`specs/254-*/`（新）· `tools/goal_gate.py`（★ 修 UTF-8 编码）· `docs/ROADMAP.md` · memory · `AUTO_HANDOFF.md` · `.specify/feature.json`。

---

## 四、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gate_details` 条数 | **47** |

★ **生成器链未跑**（★ 没改 `scripts/`）。

---

## 五、★★★ 真机读数（★ 唯一证据）

★ 走护栏（预检「读到文档 **0** 个」）· SW **rev 34.4.1** · 打开 `output/pdf-probe.SLDDRW`（**只读**）· **关闭且未保存**。

| 项 | 读数 |
|---|---|
| 视图数 | **1**（★ **「图纸本身」伪视图**） |
| `Name` / `GetName2` | `'图纸1'` / `'图纸1'` |
| 汇总 | **同 1 · 异 0 · 失败 0** |

★★ **样本弱** ⇒ ★ **不改代码**（★ 由 `test_sample_is_explicitly_weak` 钉住）。

---

## 六、★★★ 真机踩的三个坑

| # | 坑 | 正解 |
|---|---|---|
| 1 | `ISheet` 上**没有** `GetFirstView` | ★ `IModelDoc2::GetFirstView` + `IView::GetNextView` |
| 2 | **只读打开**时 `doc.GetCurrentSheet` 回 `None` | ★ 别从 `sheet` 入手 |
| 3 | ★★ **`IView::GetName2` 是属性不是方法** | ★ **不能加括号** |

★ 第 3 条反直觉：★ 名字带 `Get` 前缀，★ 但迟到绑定下**按属性返回**。

---

## 七、未过门（如实登记）

1. **4 处换路由未做** —— ★ 样本太弱；★ **触发条件** = 拿到 **≥5 个真实模型视图**的图纸。
2. **`sw_review.py:637` 的 `av` 站点未覆盖** —— ★ 它读 `model.ActiveView`，需**零件/装配**文档。
3. **10 条 `byref-tail` 的真机验证**（★ 253 的未过门）。
4. **门禁 R8 的每日跨天假红**（★ 253 的发现）。
5. **223 的 8 条既有红**；**未提交 / 未部署**；**未删任何文件**。
