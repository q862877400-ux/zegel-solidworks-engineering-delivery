import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\signature-audit.md")
t = P.read_text(encoding="utf-8")

OLD_PREFIX = "### ⚠ 一条**未查证**的遗留（如实记，不猜）"
i = t.index(OLD_PREFIX)
j = t.index("### 本轮新增/改动的模块", i)
OLD_BLOCK = t[i:j]

NEW_BLOCK = """### ✅ 那条**未查证的遗留**：**已用真机实验裁断**（2026-10-01 轮 123）

**原悬案**：`sw_hole_features.py` 的 4 处传了 `Object&` 出参，而工具的新规则把 `Object&` 排除：
* ① `Object&` 与 `Int32&` 一样**必须传** ⇒ 规则对 `Object&` 也错，代码对
* ② `Object&` **不必传** ⇒ 代码多传了无用参数，规则对

**实验**（`tools/probe_outparam_object_byref.py`，SW 2026 SP4.1 / 34.4.1）：
先 `ISldWorks.GetHoleStandardsData(0)` 拿到 `IHoleStandardsData`，
再对 `Boolean GetHoleStandards(Object& Standards, Object& Types)` 试**四种形态**：

| 形态 | 结果 |
|---|---|
| **A 不传任何出参** | `com_error -2147352561`「**非选择性的参数**」（= `DISP_E_PARAMNOTOPTIONAL`）|
| B `VARIANT(VT_BYREF\\|VT_DISPATCH, None)` ×2 | `com_error -2147352571`「类型不匹配」|
| C 两个裸 `None` | `com_error -2147352571`「类型不匹配」|
| **D `VARIANT(VT_BYREF\\|VT_VARIANT, None)` ×2** | ★ **返回 `True`** ✓ |

**⇒ 裁定：`Object&` 出参是必填的**（A 的 `DISP_E_PARAMNOTOPTIONAL` 是决定性证据），
官方 arity = **2**；正确的传法是 **`VARIANT(VT_BYREF|VT_VARIANT, None)`**。

★★ **这个裁断同时推翻了"两边"**：
* 工具的新规则「`Object&` / `Variant&` / `Dispatch&` 一律排除」⇒ **错，必填**；
* `sw_hole_features.py` 虽然**传了**，但传的是**裸值** ⇒ **传法也错**（要 `VT_BYREF|VT_VARIANT`）。

**由此做的修正**（按铁律 4：arity 以**出厂反射的参数个数**为准，不做类型特例）：
```python
count = len(_params)          # 旧：排除 Object& / Variant& / Dispatch&
```
**判据有效性检验**（事实 62：负例是唯一的证明）：
* 负例已**固化进仓库**（`tools/arity_negative_case.py`）——
  ⚠ 批次 6/7 用的那份住在 `%TEMP%` 里、**不可复现**；
* 修正后负例**仍然全被抓住**：`CreateNewStudy3` 3 vs 4 · `InsertWeldmentFeature` 1 vs 0 ·
  `TotallyBogusMemberName` 查不到 ⇒ **不是把门禁调松**；
* 新增 `tests/test_arity_audit_negative.py`（**5 条**）钉住。

**影响**：`python scripts/audit_call_arity.py scripts\\sw_hole_features.py @refs`
⇒ **4 处存疑 → 0 存疑 / 25 通过**（**代码本来就是对的，错的是工具的规则**）。

⚠ **边界**：只证了 `GetHoleStandards` **一个**成员；
但「**arity 以出厂反射为准**」这条**不需要外推** —— 它本身就是本仓库的口径（铁律 4）。
⚠ 另一个**仍未查证**的点：`sw_hole_features.py` 那 4 个包装**在仓库里没有调用方**（孤儿），
所以「正确的传法」目前**没有任何在跑的功能依赖它** —— 本轮**没有**去接调用方。

"""

t = t[:i] + NEW_BLOCK + t[j:]
P.write_text(t, encoding="utf-8")
print("  ok signature-audit.md 已把悬案换成裁定")
print("  新长度 %d 字节" % len(t))
