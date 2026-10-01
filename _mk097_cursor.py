import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           552 🎯 **Spec Kit `097`：修好断链，并****第一次用真机验证了检查器的命中****（13 处全部有真机支持）**（轮 177）——
               ★★★ **链断点定位**：`mold_evidence` 的 `_count` 里 `get_com_member(fm, name)` 推不出 `fm` ——
               因为**建表**那一处只查**裸名**：
               ```
               反射里是 `FeatureManager get_FeatureManager()`     ← **属性带 `get_` 前缀**
               而代码写 `get_com_member(model, "FeatureManager")`  ← **裸名**
               ⇒ 建表时 `mem in d["returns"]` **一律查不到** ⇒ `ret=None` ⇒ 变量**进不了表**
               ⇒ ★★ 我在**查询**处做了 `canon_member` 规范化，**却忘了建表处** —— 同一个坑踩两次
               ```
               ★ 修法：建表时**三种写法都试**（`mem` / `canon_member(mem)` / `"get_"+mem`）
               ⇒ 检查点 **33 → 45** · 命中 **6 → 13**（`_count` 的 `fm` 那条链**也**命中了）。
            553 ★★★ **真机核对了新命中**（`tools/verify_mold_draft_analysis_owner.py`，**3/3 pass**）：
               ```
               反射 (官方源):  MoldDraftAnalysis 出现在 **['IModelDoc2']**
               ✓ 真机**否定**：IFeatureManager.MoldDraftAnalysis ⇒ **AttributeError: <unknown>.MoldDraftAnalysis**
               ✓ 真机**肯定**：IModelDoc2.MoldDraftAnalysis      ⇒ **能取到**（method）
               ⇒ ★★★ **三条独立证据指向同一结论**（反射 / 真机否定 / 真机肯定）
               ```
            554 ★★★ **本轮的转折：工具本身被验证了** ——
               ```
               前几轮：检查器报 X 处 ⇒ 我只能说"看起来合理"（或是被自己抓出假阳性）
               本轮  ：报 13 处 ⇒ **真机核**其中新的一处 ⇒ **AttributeError（否定）+ 能取到（肯定）**
                       ⇒ **真阳性**
               ⇒ ★★ 从「我造了个工具」到「**这个工具的产出被独立证据证实**」—— 这是质变。
               ```
               ★ 而且这是**轮 176 那 6 处之外的**第 7 处**：`mold_draft_analysis` 也把成员取在了
                 `IFeatureManager` 上（`MoldDraftAnalysis` 属 `IModelDoc2`）⇒ **一处真 bug**（⚠ **尚未修**）。
            555 ★ **「同一个坑踩两次」这次也发生了**：轮 175 规范化了**查询**处，轮 177 才发现**建表**处也要
               ⇒ ★ 可复用教训：**规范化要成对做** —— **建表与查询是一对**，改了其中一处就**必须**同步另一处
                 （与事实 61 的「工具函数要在所有同类场合用」同源）。
               门禁 + `release_check` exit 0 · 回归 **1248 passed**。
               ⚑ **未查证**：⚠ **未修 `mold_draft_analysis`**（本轮只核对；它是**真 bug**）；
                 ⚠ 13 处 = 那 6 个成员的**两条链**（`fm`/`model`）+ 1 处 ⇒ **独立问题实际是 7 个**；
                 ⚠ 47 处未检查项**仍在**；⚠ 检查器在其**未覆盖处**是否出错，**未验**。
               下轮候选：① **修 `mold_draft_analysis`**（成员取在 `IModelDoc2` 上）并真机复验；
               ② 逐条真机核那 6 个成员的两条链；③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+552 ", before, re.M):
    print("  游标 552 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+555 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 555 行已存在 ✓")
