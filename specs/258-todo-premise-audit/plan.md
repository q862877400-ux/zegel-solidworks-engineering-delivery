# Plan — ② 段待办的前提核对

**Feature**: `specs/258-todo-premise-audit/`
**日期**: 2026-10-10

## 一、三源与冲突裁决顺序

| 序 | 源 | 用途 | 权威度 |
|---|---|---|---|
| 1 | ★★ **真树源码** `scripts/sw_sketch_edit_ops.py:148` | 宿主表达式（★ 事实） | ★★★ |
| 2 | **250 的宿主级表态表** `_HOST_EXPR_REVIEW` | 判 `SketchTrim` 是 `FALSE_HIT` | ★★★ |
| 3 | **交接单原文** `output/AUTO_HANDOFF.md` ② 段 | 被核的**断言** | ★ |

**冲突裁决顺序**：1 > 2 > 3（★ 交接单是**被核对象**，★ 不是依据）。

## 二、口径

| 口径 | 真源 | 怎么用 |
|---|---|---|
| `SketchTrim` 的表态 | `tests/test_obsolete_host_review_family._HOST_EXPR_REVIEW` | ★ **import** |
| ② 段待办数 | `tools/goal_gate.count_todos` | ★ **import** |
| 宿主接口 | 官方 `C:/swapi/types/ISketchManager/SketchTrim.md`（★ **非** Obsolete） | ★ 只读 |

## 三、实现步骤

1. **先量**：grep `SketchTrim` 在交接单的位置 + 读 `sw_sketch_edit_ops.py:148` 的实际写法。
2. **核 250 的表**：确认 `FALSE_HIT` + 宿主 `ISketchManager` + 站点 1。
3. **写判据** → 证明能红。
4. **核销**：改 `output/GOAL.md` §三 B（★ 删错的「×4」）+ 交接单 ② 段（★ 删伪待办 + 删 2 条「不是待办」+ 重编号）。
5. 门禁 + 回写四处。

## 四、改动面

`output/GOAL.md`（★ 订正错的 `SketchTrim ×4`）· `output/AUTO_HANDOFF.md`（★ ② 段 8 → **6**）·
`tests/test_handoff_todo_premises.py`（新）· `specs/258-*/`（新）· 四处状态。

★ **未改** `scripts/` ⇒ ★ **不跑生成器链**。

## 五、风险与对策

| 风险 | 对策 |
|---|---|
| ★★ 把「核销」当成「刷分」 | ★★ 核销的**每一条都要有依据**（★ 250 的表 / 纪律原文）；★ 判据 `test_sketchtrim_is_not_a_routing_target` 钉住 |
| ★ 改错编号 | ★ 改完**用 `count_todos` 复读**（★ 实测 6） |
