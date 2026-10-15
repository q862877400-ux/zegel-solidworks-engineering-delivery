import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── 事实 118 ────────────────────────────────────────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 118 | " + "".join([
    "**`mold_draft_analysis` 有**两处**错（对象 + 返回类型），修好后**真机闭合**（4/4）—— 而且我中途下过一个**错的结论**** —— ",
    "2026-10-01（轮 178）。",
    "★★★ **两处错**（都由轮 177 的静态检查器抓出）：",
    "```",
    "① **对象错**：原实现 `fm = get_com_member(model, \"FeatureManager\")` 再取 `MoldDraftAnalysis`",
    "   ⇒ 真机 `IFeatureManager.MoldDraftAnalysis` = **AttributeError: <unknown>.MoldDraftAnalysis**",
    "   ★ 官方两源一致：它在 **`IModelDoc2`** 上",
    "     · 反射 `Void MoldDraftAnalysis(Double, Int32, Object, Int32)`（IModelDoc2 段）",
    "     · `C:/swapi/types/IModelDoc2/MoldDraftAnalysis.md`",
    "② **返回类型写反**：原 docstring 说「返回码为 `Int32`，**非 0 不一定是失败**」——",
    "   ★ 官方是 **`Void`** ⇒ **没有返回码** ⇒ 整句都错",
    "```",
    "★ 修法：直接从 `model` 取（`get_com_member(model, \"MoldDraftAnalysis\", …)`）+ 更正 docstring。",
    "★★★ **真机复验 4/4 pass**（`tools/verify_mold_draft_analysis_owner.py`）：",
    "```",
    "✓ ① IFeatureManager.MoldDraftAnalysis ⇒ **AttributeError**（否定）",
    "✓ ② IModelDoc2.MoldDraftAnalysis     ⇒ **能取到**（method，肯定）",
    "✓ ③ 改后 `mold_draft_analysis` 可调用（**不再 AttributeError**）⇒ 返回 **bool**",
    "✓ 收尾无残留",
    "```",
    "⚠⚠⚠ **本轮我下过一个**错的结论**并当场纠正（如实记）**：",
    "看到真机回 `bool` 而我 docstring 写 `None`，我一度推断「**这个函数从来没真正调用过**」——",
    "★ 依据是我自己写的**测试桩**：`_Model(..., MoldDraftAnalysis=md)` 把 `_Recorder` 的**实例**设成属性",
    "（**不可调用**）⇒ `get_com_member` 调用失败、静默返回成员本身 ⇒ 看起来「没调用」。",
    "★★ **真相**：`get_com_member` 的语义是「**取或调**」，**有实参 ⇒ 一定调用**（它自己的 docstring 明写）",
    "⇒ ★ **是我的测试桩错了，不是实现错了**。",
    "★ 教训（可复用）：**用桩下结论之前，先确认桩自己是对的** ——",
    "否则会把自己的**脚手架缺陷**当成**被测代码的缺陷**（★ 与事实 113~117 的「用猜填不知道」**不同**：",
    "这次是**用错误的观测**下结论）。",
    "★ 顺带更正一处细节：pywin32 对 **`Void`** 调用**往往回 `True`** ⇒ `:returns:` 写成 `None` **不精确** ⇒",
    "已改成「官方是 `Void`；pywin32 可能回 `True`/`None`；**不得当作成败**」。",
    "★ 效果：静态命中 **13 → 12**（`MoldDraftAnalysis` 那处真问题被**修掉**）。",
    " | `scripts/sw_mold.py` 的 `mold_draft_analysis`；`tools/verify_mold_draft_analysis_owner.py`；",
    "事实 117；`C:/swapi/types/IModelDoc2/MoldDraftAnalysis.md` |",
])
if "| 118 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 118")
else:
    print("  已有 118")

# ── Spec Kit 098 ────────────────────────────────────────────────────
S = Path(r"D:\AI\SW\specs\098-mold-draft-analysis-two-defects")
S.mkdir(parents=True, exist_ok=True)
spec = """# 098 · `mold_draft_analysis` 两处错（对象 + 返回类型）修好并**真机闭合**（4/4）

**Status**: Implemented（轮 178）

## 一、两处错（都由轮 177 的静态检查器抓出）
```
① **对象错**：原实现 `fm = get_com_member(model, "FeatureManager")` 再取 `MoldDraftAnalysis`
   ⇒ 真机 `IFeatureManager.MoldDraftAnalysis` = **AttributeError: <unknown>.MoldDraftAnalysis**
   ★ 官方两源一致：它在 **`IModelDoc2`** 上
     · 反射 `Void MoldDraftAnalysis(Double, Int32, Object, Int32)`（IModelDoc2 段）
     · `C:/swapi/types/IModelDoc2/MoldDraftAnalysis.md`
② **返回类型写反**：原 docstring 说「返回码为 `Int32`，非 0 不一定是失败」
   ★ 官方是 **`Void`** ⇒ **没有返回码** ⇒ 整句都错
```

## 二、真机复验 **4/4 pass**
```
✓ ① IFeatureManager.MoldDraftAnalysis ⇒ **AttributeError**（否定）
✓ ② IModelDoc2.MoldDraftAnalysis     ⇒ **能取到**（method，肯定）
✓ ③ 改后 `mold_draft_analysis` 可调用（**不再 AttributeError**）⇒ 返回 **bool**
✓ 收尾无残留
⇒ ★★★ **改前 AttributeError · 改后能调** ⇒ **真机闭合**
```

## 三、⚠⚠⚠ 本轮我下过一个**错的结论**并当场纠正
```
看到真机回 `bool` 而我 docstring 写 `None`，我一度推断「**这个函数从来没真正调用过**」
★ 依据是我**自己写的测试桩**：`_Model(..., MoldDraftAnalysis=md)` 把 `_Recorder` 的**实例**
  设成属性（**不可调用**）⇒ `get_com_member` 调用失败、静默返回成员本身 ⇒ **看起来「没调用」**
★★ **真相**：`get_com_member` 的语义是「**取或调**」，**有实参 ⇒ 一定调用**（它自己的 docstring 明写）
⇒ ★ **是我的测试桩错了，不是实现错了。**
```

> ★ **教训（可复用）**：**用桩下结论之前，先确认桩自己是对的** ——
> 否则会把自己的**脚手架缺陷**当成**被测代码的缺陷**。
> ⚠ 这与事实 113~117 的「**用猜填不知道**」**形状不同**：这次是「**用错误的观测下结论**」。

## 四、★ 顺带更正一处细节
```
pywin32 对 **`Void`** 调用**往往回 `True`** ⇒ `:returns:` 写成 `None` **不精确**
⇒ 已改成「官方是 `Void`；pywin32 可能回 `True`/`None`；**不得当作成败**」
★ 并让契约测试断言「**不是**被当成成败的整数返回码」（`True`/`None` 都可，数字不行）
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-9801 | ★★ 修**对象错**（从 `IModelDoc2` 取）|
| SC-9802 | ★★ 修**返回类型写反**（`Void` ⇒ 没有返回码）|
| SC-9803 | ★★★ **真机复验 4/4**（否定 + 肯定 + 改后能调 + 收尾）|
| SC-9804 | ★ 改契约测试（它钉着**两条错的**语义）⇒ **11 passed** |
| SC-9805 | ★★★ **如实记下我那个错的结论**（桩错 ≠ 实现错）|
| SC-9806 | 静态命中 13 → 12（那处真问题被修掉）· 门禁 + 回归不退化 |

## ⚠ 明确记下的限度
* ⚠ `MoldDraftAnalysis` 的**实际效果未验**（只证「调得到」+「不抛 AttributeError」）；
* ⚠ `swDraftAnalysisOptions_e` / `swDraftAnalysisShow_e` 的**枚举值未逐条查证**；
* ⚠ 它**仍可能弹模态框**（未定义拔模方向时）⇒ 调用方需配兜底（⚠ 本轮真机上**没弹**，但那不构成保证）；
* ⚠ 那 12 处命中里，**只有 1 处**（`MoldDraftAnalysis`）本轮被真机核过；其余 11 处（那 6 个成员的
  两条链）**在轮 172/177 核过** ⇒ ★ **独立问题实际是 6 个**。
"""
plan = """# 098 · Plan

## 步骤
1. 轮 177 的检查器报出 `MoldDraftAnalysis` 取错对象 ⇒ 本轮修它
2. ★ 查官方两源 ⇒ 确认在 `IModelDoc2` 上，且**返回 `Void`**
3. ★ 修实现（从 `model` 取）+ 更正 docstring（`Void`，没有返回码）
4. ⚠ 契约测试红了（它钉着**两条错的**语义）⇒ 改写它
5. ⚠⚠ 改写时我**用错了测试桩** ⇒ 据此得出**错的结论**（「从不调用」）
6. ★★ 读 `get_com_member` 的 docstring ⇒ **我自己错了**（有实参一定调用）⇒ 修桩
7. ★★★ 真机复验 **4/4 pass** ⇒ 修复闭合
8. 事实 118 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 只修"看得见"的那处 | ★ 两处都修（对象 + 返回类型）|
| 测试钉着旧语义 | ★ 改写 + **写明为什么旧断言是错的** |
| **用错误观测下结论** | ⚠ **本轮犯了** ⇒ 读实现 docstring ⇒ 纠正 ⇒ **记进事实表** |
| 把 `True` 当成功 | ★ docstring 明写「不得当作成败」|
"""
tasks = """# 098 · Tasks（全部完成，轮 178）

- [x] T-9801 修两处 `→ 验收:` `python -m pytest tests/test_sw_mold_contract.py -q`（**11 passed**）
- [x] T-9802 ★★★ 真机复验 `→ 验收:` `python tools/verify_mold_draft_analysis_owner.py`（**4/4 pass**）
- [x] T-9803 纠正我那个错的结论（桩错 ≠ 实现错）
- [x] T-9804 事实 118
- [x] T-9805 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""
converge = """# 098 · Converge

**Converged**: 2026-10-01（轮 178）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-9801 修对象错 | ✅ |
| SC-9802 修返回类型 | ✅ |
| SC-9803 真机 4/4 | ✅ |
| SC-9804 改契约测试 | ✅ 11 passed |
| SC-9805 记下错的结论 | ✅ |
| SC-9806 13 → 12 + 门禁 | ✅ |

## 二、★★★ 本轮的教训与 113~117 **形状不同**
```
113~117：**用「猜」填「不知道」**（兜底 IObject / 猜接口名 / 变量名猜接口 …）
118    ：**用「错误的观测」下结论** —— 我拿一个**自己写错的测试桩**当证据，
         得出「这个函数从来没调用过」，★ **而实现是对的**。
⇒ ★ 教训：**用桩下结论之前，先确认桩自己是对的。**
  否则会把自己的**脚手架缺陷**当成**被测代码的缺陷**（比「猜」更隐蔽，因为**看起来有证据**）。
```

## 三、★ 而修复本身是干净的
```
两处错（对象 / 返回类型）⇒ 都改 ⇒ 契约测试 11 passed ⇒ **真机 4/4** ⇒ 静态命中 13 → 12
⇒ ★ 从「检查器抓出一处真问题」到"**修好并被真机闭合**" —— 这是第 117 轮那条价值闭环的完成。
```

## 四、未查证
* ⚠ `mold_draft_analysis` 的**实际效果未验**（只证「调得到」）；
* ⚠ `swDraftAnalysisOptions_e` / `swDraftAnalysisShow_e` 枚举值未逐条查证；
* ⚠ 它**仍可能弹模态框**（本轮真机没弹，但不构成保证）；
* ⚠ 那 12 处命中里只有 1 处本轮核过（其余 11 处在轮 172/177 核过 ⇒ **独立问题 6 个**）。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
