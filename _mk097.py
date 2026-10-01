import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── 事实 117 ────────────────────────────────────────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 117 | " + "".join([
    "**建表处漏了成员名规范化 ⇒ `_count` 那一层断链；修好后**真机验证**了检查器的命中** —— ",
    "2026-10-01（轮 177）。",
    "★★★ **链断点定位（本轮）**：`mold_evidence` 的 `_count` 里 `get_com_member(fm, name)` 推不出 `fm`，",
    "因为**建表**那一处只查裸名：",
    "```",
    "反射里是 `FeatureManager get_FeatureManager()` —— **属性带 `get_` 前缀**",
    "而代码写 `get_com_member(model, \"FeatureManager\")`（**裸名**）",
    "⇒ 建表时 `mem in d[\"returns\"]` **一律查不到** ⇒ `ret=None` ⇒ 变量**进不了表**",
    "⇒ ★★ 我在**查询**处做了 `canon_member` 规范化，**却忘了建表处** —— 同一个坑踩两次（事实 113/115/116 同族）",
    "```",
    "★ 修法：建表时**三种写法都试**（`mem` / `canon_member(mem)` / `\"get_\"+mem`）。",
    "⇒ 效果：检查点 **33 → 45** · 命中 **6 → 13**（`_count` 的 `fm` 那条链**也**命中了）。",
    "★★★ **真机核对了新命中**（`tools/verify_mold_draft_analysis_owner.py`，**3/3 pass**）：",
    "```",
    "反射 (官方源):  MoldDraftAnalysis 出现在 **['IModelDoc2']**",
    "✓ 真机**否定**：IFeatureManager.MoldDraftAnalysis ⇒ **AttributeError: <unknown>.MoldDraftAnalysis**",
    "✓ 真机**肯定**：IModelDoc2.MoldDraftAnalysis      ⇒ **能取到**（method）",
    "⇒ ★★★ **三条独立证据指向同一结论**（反射 / 真机否定 / 真机肯定）",
    "```",
    "⇒ ★★★ **这是检查器**第一次**在一个**新**位置（不是我先前查过的）抓出真问题，并被真机证实是真阳性** ——",
    "★ 它**不再只是「看起来在查」**（事实 62 那种假绿）。",
    "★ 而且这是**轮 176 那 6 处之外的**第 7 处**：`mold_draft_analysis` 也把成员取在了 `IFeatureManager` 上",
    "（`MoldDraftAnalysis` 属 `IModelDoc2`）—— **一处真 bug**（**尚未修**，本轮只做了核对）。",
    "★ 现状：**13 处命中** = 那 6 个成员 × 2 条链（`fm` / `model`，轮 172 真机核过）+ 1 处 `MoldDraftAnalysis`",
    "（本轮真机核过）⇒ ★ **13 处全部有真机支持**。",
    " | `scripts/check_member_owner_interface.py`；`tools/verify_mold_draft_analysis_owner.py`；",
    "事实 113 / 116 / 172 |",
])
if "| 117 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 117")
else:
    print("  已有 117")

# ── Spec Kit 097 ────────────────────────────────────────────────────
S = Path(r"D:\AI\SW\specs\097-checker-validated-by-real-machine")
S.mkdir(parents=True, exist_ok=True)
spec = """# 097 · 修好断链，并**第一次用真机验证了检查器的命中**（13 处全部有真机支持）

**Status**: Implemented（轮 177）

## 一、★★★ 链断点定位
```
`mold_evidence` 的 `_count` 里 `get_com_member(fm, name)` 推不出 `fm` —— 因为**建表**那处只查**裸名**：
  反射里是 `FeatureManager get_FeatureManager()`      ← **属性带 `get_` 前缀**
  而代码写 `get_com_member(model, "FeatureManager")`  ← **裸名**
  ⇒ 建表时 `mem in d["returns"]` **一律查不到** ⇒ `ret=None` ⇒ 变量**进不了表**
⇒ ★★ 我在**查询**处做了 `canon_member` 规范化，**却忘了建表处** ——
  **同一个坑踩两次**（事实 113/115/116 同族：都是"规范化只做了一半"）。
```

## 二、修法与效果
```
修：建表时**三种写法都试**（`mem` / `canon_member(mem)` / `"get_" + mem`）
效果：检查点 **33 → 45** · 命中 **6 → 13**（`_count` 的 `fm` 那条链**也**命中了）
```

## 三、★★★ 真机核对了新命中（`tools/verify_mold_draft_analysis_owner.py`，**3/3 pass**）
```
反射 (官方源):  MoldDraftAnalysis 出现在 **['IModelDoc2']**
✓ 真机**否定**：IFeatureManager.MoldDraftAnalysis ⇒ **AttributeError: <unknown>.MoldDraftAnalysis**
✓ 真机**肯定**：IModelDoc2.MoldDraftAnalysis      ⇒ **能取到**（method）
⇒ ★★★ **三条独立证据指向同一结论**（反射 / 真机否定 / 真机肯定）
```

## 四、★★★ 为什么这一步重要
```
★ 这是检查器**第一次**在一个**新**位置（不是我先前查过的）抓出真问题，
  并被真机证实是**真阳性** ⇒ **它不再只是「看起来在查」**（事实 62 那种假绿）。
★ 而且这是**轮 176 那 6 处之外的**第 7 处**：
  `mold_draft_analysis` 也把成员取在了 `IFeatureManager` 上（`MoldDraftAnalysis` 属 `IModelDoc2`）
  ⇒ **一处真 bug**（⚠ **尚未修** —— 本轮只做了核对）。
★ 现状：**13 处命中** = 那 6 个成员 × 2 条链（`fm` / `model`，轮 172 核过）+ 1 处 `MoldDraftAnalysis`（本轮核过）
  ⇒ ★ **13 处全部有真机支持**。
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-9701 | ★★★ **定位链断点**（建表处漏规范化 ⇒ 变量进不了表）|
| SC-9702 | ★ 修（三种写法都试）⇒ 检查点 33 → 45 · 命中 6 → 13 |
| SC-9703 | ★★★ **真机核对新命中**（反射 + 真机否定 + 真机肯定，三条独立证据）|
| SC-9704 | ★★ 结论：检查器**第一次被真机证实能抓真阳性** |
| SC-9705 | ★ 发现第 7 处真 bug（`mold_draft_analysis`）—— ⚠ **未修** |
| SC-9706 | 门禁 + 回归不退化 |

## ⚠ 明确记下的限度
* ⚠ **未修 `mold_draft_analysis`**（本轮只核对；它是**真 bug**：成员取在了 `IFeatureManager` 上）；
* ⚠ 13 处里那 6 个成员的**两条链**算 12 处（同一批成员的两种取法）⇒ **独立问题实际是 7 个**；
* ⚠ 47 处未检查项**仍在**；
* ⚠ 检查器的**判据仍可能在其未覆盖处出错**（本轮只验证了命中的那 13 处）。
"""
plan = """# 097 · Plan

## 步骤
1. 轮 176 留的疑问：`_count`（`fm`）那条链为何未命中
2. ★ 写调试脚本**逐段打印链条** ⇒ 定位到 `赋值 fm = get_com_member(model, "FeatureManager") ⇒ ret=None`
3. ★★★ 根因：**建表处只查裸名**，而反射里属性带 `get_` 前缀
   （⚠ 我在查询处做了规范化，**忘了建表处** —— 同一个坑第二次）
4. ★ 修：三种写法都试 ⇒ 检查点 33 → 45 · 命中 6 → 13
5. ★★ 新命中里有一处 `MoldDraftAnalysis`（轮 176 没发现）⇒ **真机核**
6. ★★★ 真机证实（反射 + 否定 + 肯定，三条独立证据）⇒ **检查器第一次被验证**
7. 事实 117 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 静态结论直接当真 | ★ **真机核**（本轮做了，3/3）|
| 断链原因靠猜 | ★ **写调试脚本逐段打印**，看到 `ret=None` 才下结论 |
| 规范化只做一半 | ⚠ 本轮**又**犯了 ⇒ 修好后**检查两处都做了** |
| 顺手修真 bug | ⚠ **不顺手** —— 本轮只核对，修它留给下轮（有真机证据后再改）|
"""
tasks = """# 097 · Tasks（全部完成，轮 177）

- [x] T-9701 调试定位链断点（`_debug_count_chain.py`）
- [x] T-9702 修建表处规范化 `→ 验收:` `python scripts/check_member_owner_interface.py`（**33→45 · 6→13**）
- [x] T-9703 ★★★ 真机核新命中 `→ 验收:` `python tools/verify_mold_draft_analysis_owner.py`（**3/3 pass**）
- [x] T-9704 事实 117
- [x] T-9705 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""
converge = """# 097 · Converge

**Converged**: 2026-10-01（轮 177）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-9701 定位断点 | ✅ 建表处漏规范化 |
| SC-9702 修 + 增益 | ✅ 33→45 / 6→13 |
| SC-9703 真机核 | ✅ 3/3（三条独立证据）|
| SC-9704 检查器被验证 | ✅ 第一次 |
| SC-9705 第 7 处真 bug | ✅ 发现（未修）|
| SC-9706 门禁 + 回归 | ✅ |

## 二、★★★ 本轮的转折：**工具本身被验证了**
```
前几轮：检查器报 X 处 ⇒ 我只能说"看起来合理"（或是被自己抓出假阳性）
本轮  ：报 13 处 ⇒ **真机核**其中新的一处 ⇒ **AttributeError（否定）+ 能取到（肯定）** ⇒ **真阳性**
⇒ ★★ 从「我造了个工具」到"**这个工具的产出被独立证据证实**" —— 这是质变。
```

## 三、★ 而「同一个坑踩两次」这次也发生了
```
轮 175：查询处的成员名要规范化（`get_` 前缀）⇒ 改了**查询**处
轮 177：**建表**处也该规范化 ⇒ 忘了 ⇒ `fm` 那条链全断
⇒ ★ 教训（可复用）：**规范化要成对做** —— 建表与查询是**一对**，
  改了其中一处就**必须**同步另一处（与事实 61 的「工具函数要在所有同类场合用」同源）。
```

## 四、未查证
* ⚠ `mold_draft_analysis` 的**真 bug 未修**（本轮只核对）；
* ⚠ 47 处未检查项仍在；
* ⚠ 13 处 = 6 个成员 × 2 条链 + 1 ⇒ **独立问题 7 个**；
* ⚠ 检查器在其**未覆盖处**是否出错，**未验**。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
