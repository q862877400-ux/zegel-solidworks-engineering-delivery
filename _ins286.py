import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           286 🎯 **Spec Kit `042`：真机裁断 A5 里唯一悬着的那条 —— 结论推翻了「两边」**（轮 123）——
               悬案：`sw_hole_features.py` 的 4 处传了 `Object&` 出参，而 `audit_call_arity.py`
               的新规则把 `Object&` 排除 ⇒ ① 必填（规则错、代码对）还是 ② 不必传（规则对、代码多传）？
               当时**未做真机实验**，按铁律 5 记「不猜」。
            287 ★ **四形态实验**（`tools/probe_outparam_object_byref.py`，先拿 `IHoleStandardsData`）：
               ```
               A 不传出参                             ⇒ com_error -2147352561「**非选择性的参数**」← 决定性
               B VARIANT(VT_BYREF|VT_DISPATCH, None)  ⇒ com_error -2147352571「类型不匹配」
               C 两个裸 None                           ⇒ com_error -2147352571「类型不匹配」
               D VARIANT(VT_BYREF|VT_VARIANT, None)   ⇒ **返回 True** ✓
               ```
            288 ★★ **裁定：`Object&` 必填，传法是 `VT_BYREF|VT_VARIANT` —— 两边都错**：
               ```
               ① 工具的规则「Object& / Variant& / Dispatch& 一律排除」 ⇒ **错**（必填）
               ② sw_hole_features.py 虽然传了，但传的是**裸值**        ⇒ **传法也错**
               ```
               ★★ **悬案之所以悬，是因为两个选项都不对** —— 不是二选一，是**两边都要改**。
            289 ★ **修正按铁律 4**：arity **就是出厂反射的参数个数**（`count = len(_params)`），
               **不做类型特例**。**判据有效性检验**（事实 62）：
               ★ 负例**固化进仓库**（`tools/arity_negative_case.py`）——
                 ⚠ 批次 6/7 那份住在 `%TEMP%` 里、**不可复现**（写着的"检验"只能做一次）；
               修正后负例**仍全被抓住**（3 个）⇒ **不是把门禁调松**；新增测试 **5 条**。
               影响可量化：`sw_hole_features` **4 处存疑 → 0**，**25 通过**。
            290 ⚑ **未查证**：只证了 `GetHoleStandards` **一个**成员（但"以反射为准"不需外推）；
               ⚠ 那 4 个包装**在仓库里没有调用方**（孤儿）⇒ 正确传法**没有被在跑的功能用到**，
                 本轮**没有**去接调用方；`Variant&` / `Dispatch&` **未逐个实测**。
               ★ 一条分支收获：探针第一版用 `pythoncom.VARIANT`（**不存在**）⇒ 改
                 `win32com.client.VARIANT`；**若没修，B 形态会显示成"探针坏了"而不是"传法不对"**，
                 那会把一个真实的负面结论掩盖掉。
               已知事实 **68** 入库 · 回归 **1113 passed**。
               下轮候选：① 继续给剩下 3 条 `stitched` 冒烟；② 继续补「真缺」；
               ③ 把 `sw_hole_features` 那 4 个孤儿接上调用方（**新发现**）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+286 ", before, re.M):
    print("  游标 286 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+290 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 290 行已存在 ✓")
