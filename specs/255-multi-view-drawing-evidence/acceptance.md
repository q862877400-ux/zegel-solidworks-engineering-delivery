# Acceptance — 造出多视图工程图，把 `IView::Name` == `GetName2` 的证据升到真实模型视图

**Feature**: `specs/255-multi-view-drawing-evidence/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 5/5 绿 · 红基线成立 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: 造出真实工程图，**4 个视图**（含 **3 个真实模型视图**）上 `Name` == `GetName2` ⇒ **等价**。
★ **但门槛是 views ≥ 5，本轮 4** ⇒ ★ **仍不改代码**。

---

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | 多视图逐对相等 | `test_multi_view_equivalence_reading` | ✅ **同 4 · 异 0** |
| FR-002 | ★★★ 样本必须**真的**含模型视图 | `test_sample_has_real_model_views` | ✅ **3 个** `工程图视图N` |
| FR-003 | ★★ 门槛未达必须**显式**记录 | `test_routing_threshold_is_not_yet_met` | ✅ **4 < 5** |
| FR-004 | 真机坑进判据 | `test_pitfalls_are_recorded` | ✅ 三条关键词 |
| FR-005 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 三组负例全红 |
| FR-006 | ★ 不改代码 | mtime 核（§三） | ✅ |

---

## 二、★★ 红基线

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | 0 条 | ✅ `0` |
| `diff=1` | 「不能换路由」 | ✅ `['有 1 处 \`Name\` != \`GetName2\` ⇒ **不能换路由**']` |
| `real_model_views=0` | 「证据仍弱」 | ✅ `['**真实模型视图** 0 < 下界 3 ⇒ 证据仍弱']` |
| 逐对读数不全 | 报错 | ✅ |

---

## 三、★ 未改动证明（★ 用 mtime）

| 文件 | mtime | 早于 00:20？ |
|---|---|---|
| `scripts/sw_drawing_query.py` | `10-04 08:26` | ✅ |
| `scripts/sw_drawing_view.py` | `10-09 13:45` | ✅ |
| `scripts/sw_review.py` | `10-04 00:40` | ✅ |

★ **本切片改过**：`tests/test_multi_view_drawing_evidence.py`（新）· `output/_probe255_make_drawing.py` / `.txt`（新）·
`output/_probe255_views.SLDDRW`（★ 造出来的图纸）· `specs/255-*/`（新）· `docs/ROADMAP.md` · memory · `AUTO_HANDOFF.md` · `.specify/feature.json`。

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

## 五、★★★ 真机读数

★ 走护栏（预检「读到文档 **0** 个」）· SW **rev 34.4.1** · 零件 `output/fixtures/刀柄_Holder.sldprt`（**只读**打开）
· 工程图模板 `gb_a4.drwdot` · ★ **零件与图纸用完都已关闭**。

| # | `Name` | `GetName2` | 判 |
|---|---|---|---|
| 1 | `图纸1` | `图纸1` | 同 |
| 2 | `工程图视图1` | `工程图视图1` | 同 |
| 3 | `工程图视图2` | `工程图视图2` | 同 |
| 4 | `工程图视图3` | `工程图视图3` | 同 |

⇒ ★ **同 4 · 异 0** ⇒ ★ **等价**。★ 图纸已存 `output/_probe255_views.SLDDRW`（★ 可复用）。

---

## 六、★★★ 真机踩的三个坑

| # | 坑 | 正解 |
|---|---|---|
| 1 | ★★ `GetUserPreferenceStringValue(9)` 是**装配**模板 ⇒ 建出来的是**装配**、**没有** `Create3rdAngleViews2` | ★ **10** 才是工程图模板 |
| 2 | `win32com.VARIANT` **不存在** | ★ `from win32com.client import VARIANT` |
| 3 | ★ `IView::GetName2` 是**属性**不是方法 | ★ 不加括号 |

---

## 七、未过门（如实登记）

1. **换路由仍未做** —— ★ **门槛 = views ≥ 5**，★ 本轮 **4**（★ 差 1）。
   ★ **触发条件** = 造出第 5 个视图（★ 例如再要一个等轴测/剖视图，或换更复杂的零件）。
2. **`sw_review.py:637` 的 `av` 站点**仍未覆盖（★ 需零件/装配文档的 `ActiveView`）。
3. **10 条 `byref-tail` 真机验证**（★ 253）。
4. **门禁 R8 每日跨天假红**（★ 253 发现）。
5. **223 的 8 条既有红**；**未提交 / 未部署**；**未删任何文件**。
