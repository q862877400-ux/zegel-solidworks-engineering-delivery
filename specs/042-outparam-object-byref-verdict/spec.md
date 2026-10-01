# 042 · 用真机实验裁断 A5 里唯一悬着的一条 —— **结论推翻了「两边」**

**Status**: Implemented（轮 123）

## 一、悬案（`docs/signature-audit.md` 批次 7 的「一条未查证的遗留」）
`sw_hole_features.py` 的 4 处传了 `Object&` 出参，而 `audit_call_arity.py` 的**新**规则把 `Object&` 排除：
* ① `Object&` 与 `Int32&` 一样**必须传** ⇒ **规则错，代码对**
* ② `Object&` **不必传** ⇒ **代码多传了无用参数，规则对**

⇒ 当时**未做真机实验**，按铁律 5 记「不猜」。

## 二、实验（`tools/probe_outparam_object_byref.py`）
先 `ISldWorks.GetHoleStandardsData(0)` 拿 `IHoleStandardsData`，
再对 `Boolean GetHoleStandards(Object& Standards, Object& Types)`（官方 arity = **2**）试**四形态**：

| 形态 | 结果 |
|---|---|
| **A 不传任何出参** | `com_error -2147352561`「**非选择性的参数**」（`DISP_E_PARAMNOTOPTIONAL`，**决定性**）|
| B `VARIANT(VT_BYREF\|VT_DISPATCH, None)` ×2 | `com_error -2147352571`「类型不匹配」|
| C 两个裸 `None` | `com_error -2147352571`「类型不匹配」|
| **D `VARIANT(VT_BYREF\|VT_VARIANT, None)` ×2** | ★ **返回 `True`** ✓ |

## 三、★★ 裁定：**`Object&` 必填，且传法是 `VT_BYREF|VT_VARIANT`** —— 两边都错
```
① 工具的规则「Object& / Variant& / Dispatch& 一律排除」  ⇒ **错**（必填）
② sw_hole_features.py 虽然传了，但传的是**裸值**          ⇒ **传法也错**
```
★ 这正是「**悬案之所以悬，是因为两个选项都不对**」——
它不是一个二选一，而是一个**两边都要改**的局面。

## 四、修正（按铁律 4：arity 以**出厂反射的参数个数**为准，不做类型特例）
```python
count = len(_params)      # 旧：排除 Object& / Variant& / Dispatch&
```

## 五、判据有效性检验（事实 62：负例是唯一的证明）
* ★ 负例**固化进仓库**（`tools/arity_negative_case.py`）——
  ⚠ 批次 6/7 用的那份住在 `%TEMP%` 里、**不可复现**；
* 修正后负例**仍全被抓住**：`CreateNewStudy3` 3 vs 4 · `InsertWeldmentFeature` 1 vs 0 ·
  `TotallyBogusMemberName` 查不到 ⇒ **不是把门禁调松**；
* 新增 `tests/test_arity_audit_negative.py`（**5 条**）钉住。

## 六、判据
| ID | 判据 |
|---|---|
| SC-3801 | ★ **四形态都试了**（A/B/C/D），不是"试一个就下结论" |
| SC-3802 | ★★ **A 报 `DISP_E_PARAMNOTOPTIONAL`** 作为"必填"的决定性证据 |
| SC-3803 | ★★ **D 返回 `True`** ⇒ 给出**正确的传法** |
| SC-3804 | ★★ 裁定指出**两边都错**（工具的规则 + 代码的传法）|
| SC-3805 | 修正按铁律 4（arity = 反射参数个数），**不做类型特例** |
| SC-3806 | ★ **负例固化进仓库**（不再住 `%TEMP%`）+ **仍全被抓住**（事实 62）|
| SC-3807 | 影响可量化：`sw_hole_features` **4 处存疑 → 0**，25 通过 |
| SC-3808 | 已知事实 68 入库；门禁 + 回归不退化（回归 **1113 passed**）|

## ⚠ 明确记下的限度
* 只证了 `GetHoleStandards` **一个**成员；但「**arity 以出厂反射为准**」
  **不需要外推** —— 它本身就是本仓库的口径（铁律 4）；
* ⚠ `sw_hole_features.py` 那 4 个包装**在仓库里没有调用方**（孤儿）⇒
  正确的传法目前**没有任何在跑的功能依赖它**；本轮**没有**去接调用方；
* ⚠ `Object&` 之外的其它容器出参类型（`Variant&` / `Dispatch&`）**未逐个实测**。
