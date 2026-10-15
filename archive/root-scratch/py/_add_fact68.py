import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"D:\AI\SW\docs\known-facts.md")
t = P.read_text(encoding="utf-8")
ADD = """

| # | 事实 | 依据 |
|---|---|---|
| 68 | **`Object&` 出参「也是必填的」（与 `Int32&` 同类），正确传法是 `VARIANT(VT_BYREF\\|VT_VARIANT, None)`** —— 2026-10-01（轮 123）真机四形态实验：对 `IHoleStandardsData.GetHoleStandards(Object& Standards, Object& Types)`（官方 arity = **2**）—— **A 不传出参 ⇒ `com_error -2147352561`「非选择性的参数」**（= `DISP_E_PARAMNOTOPTIONAL`，**决定性**）；B `VT_BYREF\\|VT_DISPATCH` ⇒ 「类型不匹配」；C 裸 `None` ⇒ 「类型不匹配」；**D `VT_BYREF\\|VT_VARIANT` ⇒ 返回 `True`** ✓。★ 这**推翻了「两边」**：`audit_call_arity.py` 旧规则「`Object&` 一律排除」**错**；`sw_hole_features.py` 传了但**传的是裸值**也**错**。⇒ 按铁律 4 改为「**arity = 出厂反射的参数个数**」（`count = len(_params)`），负例仍全抓住（**不是把门禁调松**）。⚠ 只证了这一个成员；但「以反射为准」**不需要外推** | `tools/probe_outparam_object_byref.py`；`tools/arity_negative_case.py`（固化的负例）；`tests/test_arity_audit_negative.py`；`docs/signature-audit.md` 同名小节 |
"""
if "「也是必填的」" not in t:
    P.write_text(t.rstrip() + ADD, encoding="utf-8")
    print("  ok known-facts 已加 68")
else:
    print("  已有 68")
