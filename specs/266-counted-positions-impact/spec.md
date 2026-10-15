# Spec — **先量** `counted_positions` 口径缺陷的影响面（★ 结论：**只 1 条** ⇒ **降级**）

**Feature**: `specs/266-counted-positions-impact/`
**日期**: 2026-10-10
**上游**: `specs/253-arity-mismatch-triage/`（★ 16 条里 4 条假阳性）· `specs/260-routing-plan-real-hits/`（★ 说「改口径要先量」）
**本轮只做一件事**：★ **量**「改 `counted_positions` 口径」能移出几条。

---

## 一、★★★ 根因（★ 已读源码确认）

`scripts/audit_byref_args.py:123`：

```python
def counted_positions(plist):
    """⚠ 口径与 audit_call_arity.py 一致：`Int32&` **计入**，`Object&` 等**不计入**。"""
    for i, p in enumerate(plist):
        if PURE_OUT.match(p):      # ← ★ `PURE_OUT = ^(Object|Variant|Dispatch)&$`
            continue
        out.append((i, p))
```

★ 而 **253 的真机实测**证明：`IModelDocExtension::GetWhatsWrong(Object&, Object&, Object&)` **必须传 3 个 by-ref**
（★ 3 个 ⇒ `OK`；2 个 / 0 个 ⇒ `DISP_E_BADPARAMCOUNT`）⇒ ★ **「`Object&` 不计入」这个口径是错的**。

---

## 二、★★★ 先量读数（`output/_probe266_impact.py`）

★ 口径与门禁**逐字对齐**（★ `import` 门禁的函数，★ 不重写）。

| 口径 | `arity` 桶条数 |
|---|---|
| ★ **现行**（跳 `PURE_OUT`） | **16** |
| ★ **实验**（不跳 ⇒ `Object&` 也计入） | **15** |
| ★★ **移出 `arity` 桶的** | ★★ **1** —— `sw_feature_readback.py:133 GetWhatsWrong`（实参 3） |

★ `PURE_OUT` 实测**只跳过 `Object&`**（★ 正则里还有 `Variant`/`Dispatch`，★ 真树里没出现）。

---

## 三、★★★ 结论：**收益/成本比很差** ⇒ **降级**

★★ **253 说的「4 条假阳性」不是同一病因**：

| 病因 | 条数 | 改口径能救吗 |
|---|---|---|
| ★ `all-byref-false-positive` | **1**（`GetWhatsWrong`） | ★ **能** |
| ★ `starargs-false-positive` | **3**（`create_flatten_route` 等 · ★ 1 实参 vs 11/12/7 形参） | ★★ **不能**（★ **另一病因**：`*args` 透传） |

⇒ ★★ **改口径只解决 1 条**，★ 而改它要动**门禁本体**（★ 生成器链 + 下界同步 + 内容断言）
⇒ ★★★ **优先级应下调**（★ 不是「独立一件工作」那么值）。

---

## 四、需求

### FR-001 ★★★ 影响面**只 1 条**（★ 不是 4 条）
- **规则**：`old - new == moved_out == 1`。
- **验收场景**：`test_impact_is_only_one_entry` 通过；
  ★★ **能红的判据**：★ 移出数改成 4 ⇒ 当场红。

### FR-002 ★★★ 4 条假阳性**分两类病因**
- **规则**：`all-byref` **1** · `starargs` **3** · ★ 合计 **4**。
- **验收场景**：`test_the_four_false_positives_have_two_causes` 通过。

### FR-003 ★★ `PURE_OUT` 实测只跳 `Object&`
- **验收场景**：`test_pure_out_skips_only_object` 通过。

### FR-004 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过。

---

## 五、非目标

- ★★ **不**改 `counted_positions`（★ 量完发现**不值**）⇒ ★ **不跑生成器链**。
- **不**改 `scripts/` 任何一行。

## 六、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 移出数改 4 / 计数与移出数不符 / 两类之和 ≠ 4 ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_counted_positions_impact.py` **4/4 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 未改 `scripts/` | mtime 核 |

## 七、未过门（本轮不做，如实登记）

- ★★ **`counted_positions` 未改**（★ 量完判「不值」）—— ★ **触发条件** = 若将来 `arity` 桶里**同病因**的条目变多。
- ★ **3 条 `starargs` 假阳性未修** —— ★ **病因不同**（★ `*args` 透传 ⇒ 门禁只数到 1 个非 Starred 实参）⇒ ★ **另开切片**。
- `create_base_flange` 族现象 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 8 条既有红 · 未提交未部署。
