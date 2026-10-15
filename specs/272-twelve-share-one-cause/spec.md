# Spec — **12 条 `arity` 是同一病因**（★ 271 的「real-gap」其实是**约定**）

**Feature**: `specs/272-twelve-share-one-cause/`
**日期**: 2026-10-10
**上游**: `specs/271-real-gap-visible-again/`（★ 判 2 条为 `real-gap`，★ 说「下一轮修它们」）
**本轮只做一件事**：★ **先量**那 2 条的**表侧值** —— ★ 然后发现它们是**另一回事**。

---

## 一、★★★ 先量（★ 271 的教训：动手前先量）

| 成员 | ★ **表侧值**（`MESH_ARITY`） | ★ **官方形参数** | ★ 差 |
|---|---|---|---|
| `GetNodeLocation` | ★ **1** | **4**（`Int32, Double&, Double&, Double&`） | **−3** |
| `GetElementLocation` | ★ **1** | **4**（同上） | **−3** |

★ 逐字：★ `scripts/sw_simulation_results.py:128-129` ⇒ `"GetNodeLocation": 1` · `"GetElementLocation": 1`。
★ 而同文件 `:229-230` 的注释逐字写着官方签名是 **4 参**（★ 后 3 个是 `Double&`）。

---

## 二、★★★ 关键：★ `table + byref_out == official`

| 成员 | 表侧 | by-ref 出参数 | 官方 | 自洽？ |
|---|---|---|---|---|
| `GetNodeLocation` | **1** | **3** | **4** | ✓ |
| `GetElementLocation` | **1** | **3** | **4** | ✓ |
| `CreatePlot`（★ 10 条 `byref-tail` 之一） | **4** | **1** | **5** | ✓ |
| `GetBOMStartNumber`（★ 同上） | **0** | **1** | **1** | ✓ |

⇒ ★★★ **表侧一律「不含 by-ref 出参」** —— ★ 这正是 253 的 **`byref=excluded` 约定**
⇒ ★★ **那 2 条 `real-gap` 与那 10 条 `byref-tail` 是**同一条约定****，★ **不是两种病因**。

---

## 三、★★★ 纠正 271 的定性

★ 271 按**差的个数**分桶（★ −1 vs −3）⇒ ★ 判 2 条为 `real-gap`。
★★ 272 按**病因**看：★ **12 条**（10 + 2）**都是**「★ **封装未接 by-ref 出参**」
—— ★ 差的个数不同（1 vs 3）只是**出参有几个**，★ **不是两种病**。

★★★ **为什么这条要紧**：★ 不纠正 ⇒ ★ 下一轮会把那 2 条当**独立缺陷**修
（★ 而它们与另 10 条**同一处改法**：★ 接上 by-ref 出参）。

---

## 四、★★ `_checked` 的护栏会**先拦**

★ `scripts/sw_simulation_results.py:142-152` 逐字：

```python
expected = table.get(member)
if expected is not None and expected != len(args):
    raise ValueError(f"{member} 官方签名是 {expected} 个实参（不含末尾 by-ref 出参）…")
```

⇒ ★★ **想补出参就得**先改表**（★ 否则护栏先抛）—— ★ 这是下一轮动手前必须知道的。
★ 而那句错误提示**自己**就写着「**不含末尾 by-ref 出参**」⇒ ★ **约定写在代码里**。

---

## 五、需求

### FR-001 ★★★ 表侧一律「不含 by-ref 出参」（★ 4 条都自洽）
- **规则**：`table + byref_out == official` 对**每一条**成立。
- **验收场景**：`test_table_side_excludes_byref_out` 通过。

### FR-002 ★★★ 12 条**同一病因**
- **规则**：★ `10 + 2 == 12` · ★ 病因 = 「**封装未接 by-ref 出参**」。
- **验收场景**：`test_twelve_entries_share_one_cause` 通过；
  ★★ **能红的判据**：★ 同类条数 ≠ 12 ⇒ 当场红。

### FR-003 ★★ `_checked` 的护栏会拒多传的出参
- **验收场景**：`test_checked_guard_rejects_extra_args` 通过。

### FR-004 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过。

---

## 六、非目标

- ★★ **不改表**（★ 改表要动 `MESH_ARITY` 的 12 处 + 接出参 ⇒ ★ **另开切片**，★ 且**需真机验** `Double&` 的 VARIANT 写法）。
- **不**改 `scripts/` ⇒ ★ **不跑生成器链**。

## 七、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 表侧不自洽 / `real-gap` 桶 ≠ 2 / 同类条数不对 ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_twelve_share_one_cause.py` **4/4 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 未改 `scripts/` | mtime 核 |

## 八、未过门（本轮不做，如实登记）

- ★★★ **12 条本体的改法未做** —— ★ **改法已明确**：★ ① 改表（`MESH_ARITY` 等 12 处）★ ② 接 by-ref 出参
  （★ `Double&` ⇒ `VT_BYREF | VT_R8`）★ ③ **真机验**（★ 因为出参写法要试）⇒ ★ **另开切片**。
- ★ **1 条 `all-byref`**（`GetWhatsWrong`）仍未修（★ 266 判「不值」）。
- `create_base_flange` 族现象 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 8 条既有红 · 未提交未部署。
