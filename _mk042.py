import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\042-outparam-object-byref-verdict")
S.mkdir(parents=True, exist_ok=True)

spec = """# 042 · 用真机实验裁断 A5 里唯一悬着的一条 —— **结论推翻了「两边」**

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
| B `VARIANT(VT_BYREF\\|VT_DISPATCH, None)` ×2 | `com_error -2147352571`「类型不匹配」|
| C 两个裸 `None` | `com_error -2147352571`「类型不匹配」|
| **D `VARIANT(VT_BYREF\\|VT_VARIANT, None)` ×2** | ★ **返回 `True`** ✓ |

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
"""

plan = """# 042 · Plan

## 步骤
1. 从 `docs/signature-audit.md` 找出那条**真正悬着**的遗留（不是已裁定的批次 6/7 旧账）
2. 找它的实验入口：`ISldWorks.GetHoleStandardsData(Int32)` → `IHoleStandardsData`
3. 照 `probe_outparam_convention.py` 的路子写四形态实验
4. 跑 ⇒ **A 报「非选择性的参数」** ⇒ **裁断：必填**
5. ★ B/C 都报「类型不匹配」⇒ **别停下**，按 `Int32&` 的已知good形态加 **D** ⇒ **返回 True**
6. 修正 `audit_call_arity.py` 的 arity 口径（按铁律 4：不做类型特例）
7. ★ **负例固化进仓库** + 负例仍全抓住（事实 62）
8. 更新审计文档 / 能力条目 / 已知事实 68 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 试到 A 就下结论 | ★ **四形态都试**（B/C 的"类型不匹配"说明传法也要查）|
| 把"必填"当成"这样传就行" | ★ D 才给出**正确传法** |
| 修正判据是把门禁调绿 | ★ 负例**仍全抓住** + 负例**固化进仓库** |
| 顺手去接调用方 | **不做**（本轮只裁断与修口径）|
"""

tasks = """# 042 · Tasks（全部完成，轮 123）

- [x] T-3801 定位真正悬着的 A5 遗留（批次 7 的「未查证的遗留」）
- [x] T-3802 写 `tools/probe_outparam_object_byref.py`（四形态）
  `→ 验收:` `python tools/probe_outparam_object_byref.py`（裁定 out-required）
- [x] T-3803 ★ 修探针自己的 bug（`pythoncom.VARIANT` 不存在 ⇒ `win32com.client.VARIANT`）
- [x] T-3804 ★ 加 D 形态 ⇒ **返回 True** ⇒ 拿到正确传法
- [x] T-3805 修 `audit_call_arity.py` 的 arity 口径（`count = len(_params)`）
- [x] T-3806 ★ 负例固化进仓库 `tools/arity_negative_case.py` + `tests/test_arity_audit_negative.py`
  `→ 验收:` `python -m pytest tests/test_arity_audit_negative.py -q`（**5 passed**）
- [x] T-3807 更新 `docs/signature-audit.md` + 已知事实 68
- [x] T-3808 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 042 · Converge

**Converged**: 2026-10-01（轮 123）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-3801 四形态都试 | ✅ A/B/C/D |
| SC-3802 A 报 `DISP_E_PARAMNOTOPTIONAL` | ✅ `-2147352561` |
| SC-3803 D 返回 `True` | ✅ 传法 = `VT_BYREF\\|VT_VARIANT` |
| SC-3804 裁定两边都错 | ✅ 规则错 + 传法错 |
| SC-3805 按铁律 4 修正 | ✅ `count = len(_params)` |
| SC-3806 负例固化 + 仍全抓住 | ✅ 3 个负例全中 |
| SC-3807 影响可量化 | ✅ `sw_hole_features` 4 存疑 → **0** / 25 通过 |
| SC-3808 事实 68 + 门禁 + 回归 | ✅ `release_check` exit 0 · **1113 passed** |

## 二、★★ 最值钱的一点：**悬案之所以悬，是因为两个选项都不对**
```
原作者把问题写成了二选一：
  ① Object& 必填 ⇒ 规则错，代码对
  ② Object& 不必传 ⇒ 代码多传，规则对
⇒ 真机裁断：**① 成立（必填），但"代码对"不成立** ——
  代码虽然传了，**传的是裸值**，正确的传法是 `VT_BYREF|VT_VARIANT`。
```
★ 这与 `032` 那次「**假阳性率 50%**」不同：那不是"两个都不对"，是"**问题本身没定义清楚**"。
★ 而这次是「**两个候选都不完整**」——
⇒ **教训：把悬案写成"A 还是 B"的时候，先问一句「会不会 A 和 B 都只对一半」。**

## 三、★ 修正判据的**正当性**是怎么证明的
```
① 修正有**真机证据**（A 的 DISP_E_PARAMNOTOPTIONAL），不是"看代码像"
② 修正后**负例仍全被抓住**（3 个）⇒ 不是把门禁调松
③ 负例**固化进仓库** —— 批次 6/7 那份住在 %TEMP% 里、**不可复现**
```
⚠ 第 ③ 条是**顺带发现的问题**：原文档写着「判据有效性检验（应抓出 2 存疑 + 1 查不到）」，
但那个输入文件**下一轮就没了** ⇒ 那种"检验"**只能做一次**。
★ 与事实 62 一脉相承：**负例是唯一的证明 —— 但负例必须能长期存在。**

## 四、★ 一条**分支上的收获**：探针自己也有 bug
```
第一版用 `pythoncom.VARIANT(...)` ⇒ **AttributeError: module 'pythoncom' has no attribute 'VARIANT'**
⇒ 改用 `win32com.client.VARIANT`
```
⚠ 而**如果没修**，B 形态就会显示成"探针坏了"而不是"传法不对"——
**那会把一个真实的负面结论掩盖掉**。

## 五、未查证
* 只证了 `GetHoleStandards` **一个**成员（但「以反射为准」不需外推）；
* `sw_hole_features.py` 那 4 个包装**没有调用方** ⇒ 正确传法**没有被在跑的功能用到**；
* `Variant&` / `Dispatch&` 等其它容器出参**未逐个实测**。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
