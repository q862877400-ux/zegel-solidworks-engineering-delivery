# Spec — ② 段待办的**前提核对**（★ 核出并核销 1 条**伪待办**）

**Feature**: `specs/258-todo-premise-audit/`
**日期**: 2026-10-10
**上游**: ★ 本仓纪律「**交接单自己的前提也要核**」（★ 227/232–240 已**连续九轮**核出错）
**本轮只做一件事**：核 `output/AUTO_HANDOFF.md` ② 段每条待办的**前提**，把**不存在的**核销掉。

---

## 一、★★★ 核出的伪待办

★ ② 段第 2 条的子条「**251 的 `SketchTrim` 4 处换路由**」—— ★★ **该待办不存在**：

| 项 | 实测 | 交接单原文 | 判 |
|---|---|---|---|
| 250 的表态 | ★ **`FALSE_HIT`** | （未提） | ★ 假命中 |
| 宿主接口 | ★ **`ISketchManager`** | — | ★ `ISketchManager::SketchTrim` **非废弃**（★ 它**就是**索引该给的真后继） |
| 真树站点数 | ★ **1 处**（`sw_sketch_edit_ops.py:148`） | 「**4 处**」 | ★ **数也错** |
| 被废弃的条目 | `IModelDoc2::SketchTrim` | — | ★ **与我们无关**（★ 我们调的是另一个接口的同名成员） |

★ 真树那处逐字（`sw_sketch_edit_ops.py:148`）：
```python
return get_com_member(_sketch(model) and get_com_member(model, "SketchManager"),
                      "SketchTrim", TRIM_CHOICES[key], float(x), float(y), 0.0)
```
⇒ ★ 宿主是 `get_com_member(model, "SketchManager")` ⇒ ★ **ISketchManager** ⇒ ★ **非废弃** ⇒ ★ **没有换路由的靶子**。

★★ **这个错是本会话自己引入的** —— 我在 GOAL.md §三 B 写了「`SketchTrim` ×4」，★ 而 250 早就判它是假命中。

---

## 二、★★★ 核销的「不是待办」

| # | 原文 | 为什么**不是待办** |
|---|---|---|
| 6 | 「`WZD_FASTENER_ANSI_METRIC_SIMPLE` / `ROTATION_AXIS_MAP` **不改不猜**」 | ★ 那是**纪律**（铁律 5），★ ③ 段已写 |
| 7 | 「`output/` 残留临时文件**不删**」 | ★ 那是**纪律**（禁删），★ ③ 段已写 |

★★ **为什么必须删号**：★ 它们占着编号 ⇒ ★ **终止条件（② 段待办清空）永远达不成**。
★ 这正是 `output/GOAL.md` §二 定的规矩：**做不了的标注理由并删号**。

---

## 三、★★★ 读数

| 项 | 改前 | 改后 |
|---|---|---|
| **② 段编号待办** | **8** | ★ **6** |

★ 新清单：① 只读真机复核 · ② 换路由（250 的 7 处）· ③ 高危写盘 · ④ `create_hem` 行为证据 · ⑤ 223 的 8 条既有红 · ⑥ 发版前打包副本。

---

## 四、需求

### FR-001 ★★★ `SketchTrim` 是**假命中**（★ 不是换路由靶子）

- **规则**：250 的表里 `SketchTrim` 必须是 `FALSE_HIT` · 宿主 `ISketchManager` · 站点 **1** 处。
- **验收场景**：`test_sketchtrim_is_not_a_routing_target` 通过；
  ★★ **能红的判据**：★ 若 250 哪天把它改判成 `REAL_HIT` ⇒ 当场红（★ 那时才真该换路由）。

### FR-002 ★★ 真命中靶子必须与 250 一致

- **规则**：`REAL_HITS` = **6 名 · 7 处**（`DeleteRenderMaterial` 1 · `FeatureLinearPattern5` 2 ·
  `FeatureLocalCurveDrivenPattern` 1 · `InsertFormToolFeature` 1 · `KFactor` 1 · `MaterialIdName` 1）。
- **验收场景**：`test_real_hits_match_the_250_table` 通过。

### FR-003 ★★ ② 段每条必须有**分类**（封闭词表）

- **规则**：分类 ∈ {`actionable` · `needs-owner` · **`not-a-todo`**}；★ `not-a-todo` ≥ **3**。
- **验收场景**：`test_every_todo_is_classified` 通过。

### FR-004 ★★ 判据必须能红

- **验收场景**：`test_pure_function_is_red_able` 通过（★ 三组负例）。

### FR-005 ★ ② 段计数必须**真的降下来**

- **规则**：★ 核销后 ② 段编号待办 **6**（★ 原 8）。
- **验收场景**：★ `tools/goal_gate.py` 读数 = **6**。

---

## 五、非目标

- **不**改 `scripts/`（★ 本轮只核前提、改文档）⇒ ★ **不跑生成器链**。
- **不**动 250 的表（★ 它是对的，★ 错的是我的交接单）。

## 六、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 翻 `SketchTrim` 成真命中 ⇒ 报错；宿主改错 ⇒ 报错 |
| SC-2 | 判据**是绿的** | `tests/test_handoff_todo_premises.py` **4/4 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ ② 段计数 | `tools/goal_gate.py` ⇒ **6** |

## 七、未过门（本轮不做，如实登记）

- **其余 5 条待办的**前提**未逐条核** —— ★ 本轮只核出并核销了 1 条（★ 其余按 250/253 的读数**暂信**）。
- **250 的 7 处真命中换路由**未做（★ 都要先造 `I*FeatureData`）。
- 高危写盘 · `create_hem` 行为证据 · 223 的 8 条既有红 · 未提交未部署。
