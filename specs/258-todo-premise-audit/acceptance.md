# Acceptance — ② 段待办的前提核对

**Feature**: `specs/258-todo-premise-audit/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 4/4 绿 · 红基线成立 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★ 核出并核销 **1 条伪待办** + **2 条「不是待办」** ⇒ ★ **② 段编号待办 8 → 6**。

---

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ `SketchTrim` 是**假命中** | `test_sketchtrim_is_not_a_routing_target` | ✅ `FALSE_HIT` · `ISketchManager` · **1 处** |
| FR-002 | ★★ 真命中靶子与 250 一致 | `test_real_hits_match_the_250_table` | ✅ **6 名 · 7 处** |
| FR-003 | ★★ ② 段每条有分类 | `test_every_todo_is_classified` | ✅ `not-a-todo` **3** 条 |
| FR-004 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 三组负例全红 |
| FR-005 | ★ ② 段计数真的降 | `tools/goal_gate.count_todos` | ✅ **8 → 6** |

---

## 二、★★ 红基线

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常表 | `[]` | ✅ |
| 把 `SketchTrim` 翻成 `REAL_HIT` | 报错 | ✅ `["\`SketchTrim\` 的表态是 'real-hit'（★ 不是 'false-hit'）⇒ **它可能真有靶子**，请复核"]` |
| 宿主接口改成 `IModelDoc2` | 报错 | ✅ |
| 真命中表改掉 | 报错 | ✅ |

---

## 三、★★★ 核销的 3 条（★ 逐条有依据）

| # | 原文 | 依据 | 处置 |
|---|---|---|---|
| 1 | 「**251 的 `SketchTrim` 4 处换路由**」 | ★ 250 判 `FALSE_HIT`（宿主 `SketchManager` ⇒ **`ISketchManager::SketchTrim` 非废弃**）· ★ 真树**只有 1 处**（`sw_sketch_edit_ops.py:148`） | ★ **删号 + 写明理由** |
| 2 | 「`WZD_FASTENER` / `ROTATION_AXIS_MAP` **不改不猜**」 | ★ 那是**纪律**（铁律 5），★ ③ 段已写 | ★ **删号** |
| 3 | 「`output/` 残留临时文件**不删**」 | ★ 那是**纪律**（禁删），★ ③ 段已写 | ★ **删号** |

★ 真树那处逐字：
```python
return get_com_member(_sketch(model) and get_com_member(model, "SketchManager"),
                      "SketchTrim", TRIM_CHOICES[key], float(x), float(y), 0.0)
```
⇒ ★ 宿主是 `SketchManager` ⇒ ★ **非废弃** ⇒ ★ **没有换路由的靶子**。

★★ **这个错是本会话自己引入的** —— 我在 `GOAL.md` §三 B 写了「`SketchTrim` ×4」，★ 而 250 早就判它是假命中。
★ 已订正 `GOAL.md` §三 B。

---

## 四、★ 改动面

| 文件 | 动作 |
|---|---|
| `output/GOAL.md` | ★ 订正 §三 B 里错的「`SketchTrim` ×4」 |
| `output/AUTO_HANDOFF.md` | ★ ② 段 **8 → 6**（★ 删 1 伪待办 + 2 条「不是待办」+ 重编号） |
| `tests/test_handoff_todo_premises.py` | ★ **新增**（4 例） |
| `specs/258-todo-premise-audit/*.md` | ★ **新增**（四件齐） |
| `docs/ROADMAP.md` · memory · `AUTO_RUN_*.md` · `.specify/feature.json` | 回写 |

★ **未改** `scripts/` ⇒ ★ **不跑生成器链**。

---

## 五、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gate_details` 条数 | **47** |

---

## 六、未过门（如实登记）

1. **其余 5 条待办的**前提**未逐条核** —— ★ 本轮只核出并核销了 1 条（★ 其余按 250/253 的读数**暂信**）。
2. **250 的 7 处真命中换路由**未做（★ 都要先造 `I*FeatureData`）。
3. **高危写盘** · **`create_hem` 行为证据** · **223 的 8 条既有红**。
4. **未提交 / 未部署**；**未删任何文件**。
