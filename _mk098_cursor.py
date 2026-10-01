import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           556 🎯 **Spec Kit `098`：`mold_draft_analysis` 两处错（对象 + 返回类型）修好并****真机闭合****（4/4）**（轮 178）——
               两处错**都由轮 177 的静态检查器抓出**：
               ```
               ① **对象错**：原实现 `fm = get_com_member(model, "FeatureManager")` 再取 `MoldDraftAnalysis`
                  ⇒ 真机 `IFeatureManager.MoldDraftAnalysis` = **AttributeError: <unknown>.MoldDraftAnalysis**
                  ★ 官方两源一致：它在 **`IModelDoc2`** 上
                    · 反射 `Void MoldDraftAnalysis(Double, Int32, Object, Int32)`（IModelDoc2 段）
                    · `C:/swapi/types/IModelDoc2/MoldDraftAnalysis.md`
               ② **返回类型写反**：原 docstring 说「返回码为 `Int32`，非 0 不一定是失败」
                  ★ 官方是 **`Void`** ⇒ **没有返回码** ⇒ 整句都错
               ```
            557 ★★★ **真机复验 4/4 pass**（`tools/verify_mold_draft_analysis_owner.py`）：
               ```
               ✓ ① IFeatureManager.MoldDraftAnalysis ⇒ **AttributeError**（否定）
               ✓ ② IModelDoc2.MoldDraftAnalysis     ⇒ **能取到**（method，肯定）
               ✓ ③ 改后 `mold_draft_analysis` 可调用（**不再 AttributeError**）⇒ 返回 **bool**
               ✓ 收尾无残留
               ⇒ ★★★ **改前 AttributeError · 改后能调** ⇒ **真机闭合**
               ```
               ★ 静态命中 **13 → 12**（那处真问题被**修掉**）· 契约测试 **11 passed**。
            558 ⚠⚠⚠ **本轮我下过一个**错的结论**并当场纠正（如实记）**：
               看到真机回 `bool` 而我 docstring 写 `None`，我一度推断「**这个函数从来没真正调用过**」——
               ★ 依据是**我自己写的测试桩**：`_Model(..., MoldDraftAnalysis=md)` 把 `_Recorder` 的**实例**
               设成属性（**不可调用**）⇒ `get_com_member` 调用失败、静默返回成员本身 ⇒ 看起来「没调用」。
               ★★ **真相**：`get_com_member` 的语义是「**取或调**」，**有实参 ⇒ 一定调用**（它自己的 docstring 明写）
               ⇒ ★ **是我的测试桩错了，不是实现错了**。
               ⇒ ★ 教训：**用桩下结论之前，先确认桩自己是对的** —— 否则会把自己的**脚手架缺陷**
                 当成**被测代码的缺陷**。
               ⚠ 这与事实 113~117 的「**用「猜」填「不知道」**」**形状不同**：
                 这次是「**用错误的观测下结论**」—— **比"猜"更隐蔽，因为看起来有证据**。
            559 ★ **顺带更正一处细节**：pywin32 对 **`Void`** 调用**往往回 `True`** ⇒ `:returns:` 写成 `None`
               **不精确** ⇒ 已改成「官方是 `Void`；pywin32 可能回 `True`/`None`；**不得当作成败**」，
               并让契约测试断言「**不是**被当成成败的整数返回码」（`True`/`None` 都可，数字不行）。
               门禁 + `release_check` exit 0 · 回归 **1248 passed**。
               ⚑ **未查证**：⚠ `mold_draft_analysis` 的**实际效果未验**（只证「调得到」+「不抛 AttributeError」）；
                 ⚠ `swDraftAnalysisOptions_e` / `swDraftAnalysisShow_e` 的**枚举值未逐条查证**；
                 ⚠ 它**仍可能弹模态框**（本轮真机没弹，但**不构成保证**）；
                 ⚠ 那 12 处命中里**只有 1 处**本轮核过（其余 11 处在轮 172/177 核过 ⇒ **独立问题 6 个**）。
               下轮候选：① 逐条真机核那 6 个成员的两条链（把它们也变成"核过的真问题"）；
               ② 查那 47 处未检查项；③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+556 ", before, re.M):
    print("  游标 556 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+559 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 559 行已存在 ✓")
