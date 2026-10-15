# Spec — **cosworks 的 `Double&` 正例找到了**（★ 274 缺的那一格，★ 一直在仓里）

**Feature**: `specs/287-double-out-cosworks-positive/`
**日期**: 2026-10-10
**上游**: `specs/274-double-out-param-form/`（★ 结论：★「`out_double` **只有类推、无 `Double&` 真机正例**」）
**本轮只做一件事**：★ 把 274 缺的那个 **cosworks `Double&` 正例**找出来（★ 273 说 12 条里有 **6 个 `Double&`**）。

---

## 一、★★★★ 正例**一直在仓里**

★ `scripts/sw_simulation.py` 的 `default_element_size_and_tolerance`：

```python
v_size = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_R8, 0.0)
v_tol  = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_R8, 0.0)
get_com_member(mesh, "GetDefaultElementSizeAndTolerance", int(units), v_size, v_tol)
return float(v_size.value), float(v_tol.value)
```

★ 而它的**来源块逐字**（★ 不是推断）：

```
# 定位:   ``Public Sub GetDefaultElementSizeAndTolerance( _
#             ByVal NUnits As Long, _      ' 与 CreateMesh 的第 1 参同义
#             ByRef DElementSize As Double, _
#             ByRef DTolerance As Double _ )``
# ⚠ 真机实测（2026-10-01）：传 ``NUnits=-1`` 返回**毫米级**（4.9339 / 0.2467）；
#   传 ``NUnits=2``（Metric）返回**米级**（0.0049339 / 0.0002467）—— 同一个建议值两种量纲。
```

★★★ **⇒ 官方签名 `ByRef … As Double`（★ cosworks）· ★ 形态 `VT_BYREF | VT_R8` · ★ 真机实测**取回了值**（★ 两条不同读数）**
⇒ ★★★ **cosworks 的 `Double&` 正例成立** ✓✓✓

---

## 二、★★★ 精炼后的模型：★ `Double&` **没有唯一形态 —— 它按「接口有没有类型信息」分**

| 接口族 | ★ 形态 | ★ 证据 |
|---|---|---|
| ★ **cosworks**（★ **无**类型信息） | ★ `VT_BYREF \| VT_R8` | ★ **本条**（★ `ICWMesh::GetDefaultElementSizeAndTolerance` · 2026-10-01 真机取回值） |
| ★ **sldworks.tlb**（★ **有**类型信息） | ★ **裸值 / 省略** | ★ 274（★ `IBody2::GetExtremePoint` · 传 by-ref VARIANT ⇒ `TypeError`） |

★★★ ⇒ **274 的「两表不同」结论仍然成立**，★ 而**两张表现在都有真机证据** ✓
⇒ ★★ **不再有「只有类推」的格子**（★ `out_bstr` 除外 —— 它仍无证据）。

---

## 三、★★★ **12 条接线的前置全部满足**

| 出参 | 个数 | ★ 正例 |
|---|---|---|
| `Int32&` | **9** | ★ `out_i4` ⇒ `VT_BYREF \| VT_I4`（★ 2026-10-01 逐形态实测） |
| ★ **`Double&`** | **6** | ★★ **`VT_BYREF \| VT_R8`**（★ **本条** · 2026-10-01 真机实测取回值） |
| `SwDmTableError&` | **1** | ★ 枚举 ⇒ `VT_BYREF \| VT_I4` |

⇒ ★★★ **三种出参**都有真机正例**** ⇒ ★★ **12 条接线的前置**解除****（★ 下一轮可动手改表 + 接出参）。

---

## 四、需求

### FR-001 ★★★ 仓里**有** cosworks `Double&` 的正例
- **验收场景**：`test_the_positive_example_exists_in_the_repo` 通过。

### FR-002 ★★★ 精炼：★ `Double&` **按接口族分**
- **验收场景**：`test_double_out_is_interface_dependent` 通过。

### FR-003 ★★★ 12 条接线的前置**全部满足**
- **验收场景**：`test_the_twelve_entries_are_now_unblocked` 通过。

### FR-004 ★★★ **回源码核**（★ 不靠手抄）
- **验收场景**：`test_source_check_proves_the_positive_example` 通过。

### FR-005 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过（★ 五组负例）。

---

## 五、非目标

- ★★ **不改** `scripts/`（★ 正例本来就在，★ 只是**没被引用**）⇒ ★ **不跑生成器链**。
- ★★ **不动手改那 12 条**（★ 那是**下一轮**的切片 —— ★ 本轮只**解除前置**）。

## 六、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 正例字段少 / 两条读数相同 / 形态不对 / 接口相关表不 2 档 / 前置不 3 条 ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_double_out_cosworks_positive.py` **5/5** · ★ **274 的判据同步更新后仍 5/5** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |

## 七、未过门（本轮不做，如实登记）

- ★★★ **12 条本体仍未改** —— ★ 但**前置已解除**（★ 三种出参都有真机正例）⇒ ★ **下一轮动手**。
- ★★ **`out_bstr` 仍无真机证据**（★ 它与本条无关 ⇒ ★ 如实标注）。
- ★ ② 段第 2 条（250 的 7 处换路由）· `create_draft` 的 `pre_call` · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 未提交未部署。
