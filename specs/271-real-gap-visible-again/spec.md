# Spec — **加判别层** ⇒ `arity` **11 → 13**（★ 2 条 `real-gap` **重新可见**）

**Feature**: `specs/271-real-gap-visible-again/`
**日期**: 2026-10-10
**上游**: `specs/269-arity-retriage-new-rule/`（★ 核出 268 掩盖 2 条 `real-gap`）· `specs/270-starargs-move-back-noop/`（★ 空改动）
**本轮只做一件事**：★ 修 268 的窄规则 —— ★ **让 2 条真缺口重新可见**。

---

## 一、★★★ 先量：两类在 AST 上**完全同形**

★ 269 说「移回 `com_args`」· ★ 270 试了 ⇒ ★ **空改动** ⇒ ★ 271 **先量**：

| 成员 | `slots` | `com` |
|---|---|---|
| ★ `CreateFlattenRoute` | `[('*args', None)]` | **1** |
| ★ `GetNodeLocation` | `[('*args', None)]` | **1** |

★★★ **两者**一模一样** ⇒ ★ **AST 层分不开** ⇒ ★ 269 / 270 的方向**都不够**。

---

## 二、★★★ 但**形参表**能分

| 成员 | 反射签名 | 缺的形参 | 性质 |
|---|---|---|---|
| ★ `CreateFlattenRoute` | 11 参（`Int32, Int32, Double, …`） | 10 个，★ **全是普通入参** | ★ `*args` **该补** ⇒ `starred` |
| ★ `GetNodeLocation` | `(Int32, Double&, Double&, Double&)` | 3 个，★ **全是 by-ref 出参** | ★ **真缺口** ⇒ 留在 `arity` |

★★ **判别依据（★ 有物理意义）**：★ 缺的是 **by-ref 出参** ⇒ ★ 调用方**拿不到**它们 ⇒ ★ **真缺口**；
★ 缺的是**普通入参** ⇒ ★ 那是 `*args` **该补而没补**。

---

## 三、★★★ 判别层

★ 在 268 的窄规则上**再加一层**：

```python
if len(com) == 1 and min(len(counted_positions(v[1])) for v in variants) >= 2:
    missing_all_byref = all(
        all(p.strip().endswith("&") for _i, p in counted_positions(v[1])[len(com):])
        for v in variants)
    if not missing_all_byref:
        return "starred"
return "arity"
```

---

## 四、★★★ 读数

| 读数 | 268 | **271** |
|---|---|---|
| `arity` 不符 | **11** | ★ **13** |
| ★ `starred` | 5 | ★ **3**（★ 只剩 3 条 `starargs`） |
| 可核分发口 | 21 | **21** ✓ |
| ★ **已核调用点** | **318** | ★ **316**（★ **仍 ≥ 下界 313**）✓ |
| 门禁 | `exit 0` | **`exit 0`** ✓ |

### ★★★ 271 的分桶（★ 13 = 10 + 1 + 2）

| 桶 | 条数 |
|---|---|
| ★ `byref-tail-convention`（差 −1） | **10** |
| ★ `all-byref-false-positive`（差 0 · `GetWhatsWrong`） | **1** |
| ★★ **`real-arity-gap`（差 −3）** | ★★ **2**（`GetNodeLocation` / `GetElementLocation`）★ **回来了** |

★ 而且：★ **「缺的全 byref」对 13 条**全成立** ★ —— ★ 正是判别规则的依据。

★★ **已核调用点 318 → 316（−2）是**正当的**：★ 那 2 条 `real-gap` 从 `starred`（★ 算已核）
**回到了 `arity`**（★ 不算已核）⇒ ★ **它们本来就该在 `arity` 里**。

---

## 五、需求

### FR-001 ★★★ `arity` 11 → 13（★ 真缺口重新可见）
- **规则**：`arity == 13` · `starred == 3` · ★ 桶 = **10 + 1 + 2**。
- **验收场景**：`test_real_gaps_are_visible_again` 通过；
  ★★ **能红的判据**：★ `arity` 没回升 / `real-gap` 桶 ≠ 2 ⇒ 全红。

### FR-002 ★★★ 两类在 AST 上**完全同形**
- **规则**：`slots` 相同 · `com` 相同 · `missing_all_byref` 一真一假。
- **验收场景**：`test_the_two_cases_are_ast_identical` 通过。

### FR-003 ★★ 不丢覆盖（★ 267 的教训）
- **规则**：已核调用点 **≥ 313** · 可核分发口**不变** · ★ 少掉的**恰好 2**（★ 正当）。
- **验收场景**：`test_coverage_is_not_lost` 通过。

### FR-004 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过（★ 四组负例）。

---

## 六、非目标

- ★ **不**改 `counted_positions`（★ 266 判「不值」）。
- ★ **不**动那 10 条 `byref-tail`（★ 约定问题，★ 253 判过）。

## 七、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | arity 没回升 / `real-gap` 桶 ≠ 2 / 掉到下界以下 ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_real_gap_visible_again.py` **4/4 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 生成器链 | 7 步全 OK |
| SC-5 | ★ 门禁本体单跑 | `arity 13` · `可核 21` · `已核 316` · `违规 0` · **`[PASS]`** |

## 八、未过门（本轮不做，如实登记）

- ★ **10 条 `byref-tail`** 仍是**约定问题**（★ 253 判过）—— ★ **触发条件** = 若官方改了口径。
- ★ **1 条 `all-byref`**（`GetWhatsWrong`）仍未修 —— ★ 266 判「改动收益只 1 条 ⇒ 不值」。
- ★★ **2 条 `real-gap` 本体未修** —— ★ 它们**现在可见了**（★ 这才是本切片的目标）；
  ★ **修法** = 给 `GetNodeLocation` / `GetElementLocation` **补 by-ref 出参** ⇒ ★ 另开切片。
- `create_base_flange` 族现象 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 8 条既有红 · 未提交未部署。
