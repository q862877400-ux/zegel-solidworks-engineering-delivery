# Acceptance — 加判别层（真缺口重新可见）

**Feature**: `specs/271-real-gap-visible-again/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 4/4 绿 · 红基线成立 · 生成器链 7 步 OK · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★ `arity` **11 → 13** ⇒ ★★ **2 条 `real-gap` 重新可见** · ★ `starred` **5 → 3** · ★ 门禁仍过。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ arity 11 → 13 | `test_real_gaps_are_visible_again` | ✅ **13 = 10 + 1 + 2** |
| FR-002 | ★★★ 两类 AST 同形 | `test_the_two_cases_are_ast_identical` | ✅ `slots`/`com` 相同 |
| FR-003 | ★★ 不丢覆盖 | `test_coverage_is_not_lost` | ✅ **316 ≥ 313** · 少 2（★ 正当） |
| FR-004 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 四组负例全红 |

## 二、★★ 红基线

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ |
| arity 没回升 | 报错 | ✅ `['`arity` 11 ≠ 13 ⇒ 判别层没生效']` |
| `real-gap` 桶 = 0 | 报错 | ✅ `['桶之和 11 ≠ 13']` |
| 掉到下界以下 | 报错 | ✅ |

## 三、★★★ 先量：两类 AST **完全同形**

| 成员 | `slots` | `com` |
|---|---|---|
| `CreateFlattenRoute` | `[('*args', None)]` | **1** |
| `GetNodeLocation` | `[('*args', None)]` | **1** |

⇒ ★ **AST 分不开** ⇒ ★ 269 / 270 的方向**都不够**。

## 四、★★★ 但形参表能分

| 成员 | 缺的形参 | 性质 |
|---|---|---|
| `CreateFlattenRoute`（11 参） | 10 个，**全是普通入参** | `*args` 该补 ⇒ `starred` |
| `GetNodeLocation(Int32, Double&, Double&, Double&)` | 3 个，**全是 by-ref 出参** | **真缺口** ⇒ 留 `arity` |

## 五、★★★ 读数

| 读数 | 268 | **271** |
|---|---|---|
| `arity` | **11** | ★ **13** |
| `starred` | 5 | ★ **3** |
| 可核分发口 | 21 | **21** ✓ |
| 已核调用点 | **318** | **316**（★ ≥ 下界 313）✓ |
| 门禁 | `exit 0` | **`exit 0`** ✓ |

★ 分桶：**10 `byref-tail` + 1 `all-byref` + 2 `real-gap`**（★ 真缺口**回来了**）。

## 六、生成器链 + 门禁

| 项 | 读数 |
|---|---|
| ★ **生成器链** | ★ **7/7 OK** |
| ★ **门禁本体单跑** | `arity 13` · `可核 21` · `已核 316` · `违规 0` · **`[PASS] · exit 0`** |
| **门禁全套** @3.14.7 | **`status pass` · `EXIT 0` · `missing []`** · `gate_details` **47** |

## 七、未过门（如实登记）

1. ★★ **2 条 `real-gap` 本体未修** —— ★ 它们**现在可见了**（★ 本切片的目标）；★ **修法** = 补 by-ref 出参 ⇒ 另开切片。
2. ★ 10 条 `byref-tail` 仍是约定 · 1 条 `all-byref` 未修（★ 266 判「不值」）。
3. `create_base_flange` 族现象 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 8 条既有红 · 未提交未部署。
