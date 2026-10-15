import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           537 🎯 **Spec Kit `094`：「从 docstring 推形参接口」这条退路****不成立**** —— 实测两处都推错，已回退**（轮 174）——
               动机（接轮 173）：检查器**抓不到它自己的动机**（`mold_evidence(model)` 的 owner 是**形参**）。
               ★ 试的退路：**没有 `:param` 段时**，若 ① 函数恰好 1 个形参 且 ② docstring 里出现的反射接口名恰好 1 个
                 ⇒ 采纳它。
            538 ⚠⚠⚠ **实测（`D:/AI/SW/_verify_param_infer.py`）两处都推错**：
               ```
               ① insert_parting_line / insert_parting_surface / insert_shut_off_surface /
                  insert_core_cavity_solids / mold_draft_analysis
                  ⇒ 推成 **`Feature`**  ← docstring 里的**散文词** `feature` 命中了**接口名 `Feature`**
                    ⇒ 于是报「`Feature . FeatureManager` 不在 `IFeature` 上」（**荒谬但「技术上成立」**）
               ② mold_undercut_detect ⇒ 推成 **`IFeatureManager`**
                  ← docstring 提到的是**成员全名** `IFeatureManager.MoldUndercutDetect`，**不是形参的类型**
               ```
            539 ★ **处置：回退** —— 命中数 20 → 36（含 6 处 `sw_mold` 假阳性）⇒ 回退后 **36 → 20**，
               `sw_mold` 假阳性**清零**；★ 并把「试过、不成立」**写进代码注释**（`+17/-0`，防下一个人再试一遍）。
            540 ★★ **定则（本轮最值钱的一句）**：
               ```
               **显式 = 有依据；推断 = 会错** —— 只认 `:param <名>: <接口名>` 这一种写法。
               ⇒ ★★ 这也**印证了事实 113 的教训**（「推不出」不许用兜底值代替）：
                 轮 173 的兜底是 **`IObject`**，轮 174 的兜底是 **「docstring 里恰好 1 个接口名」** ——
                 **两次都是「把不知道伪装成知道」，两次都被实测打回。**
               ```
            541 ⚠ **本轮的产出是**负结果**，而这正是它该有的样子**：
               试一条退路 ⇒ **实测两处都推错** ⇒ **回退** ⇒ 把「试过、不成立」写进代码。
               ★ 与「猜一个兜底值然后接进工具」相比，**负结果 + 代码注释**才是**可累积**的：
                 下一个人不会在同一个地方再试一遍。
               ⚠ 回退过程中我**两次写坏文件**（一次脚本语法错、一次 `return {}` 缩进错）⇒ 都靠 `git checkout --` 恢复；
                 **最终用 `edit` 工具加注释**（★ 事实 61 的定则**又**用上了）。
               门禁 + `release_check` exit 0 · 回归 **1248 passed**。
               ⚑ **未查证**：⚠ **没有解决问题** —— `mold_evidence` 那种「**散文 docstring + 形参 owner**」
                 **仍然抓不到**（而它是本工具的**动机**）；⚠ 从**调用点**推形参接口那条路**未做**（下一步）；
                 ⚠ 那 20 处命中仍是**静态**，**未真机核**。
               下轮候选：① 走**从调用点推**那条路（`mold_evidence(doc)` ⇒ `doc` 的接口）⇒ 才可能覆盖动机；
               ② 逐条真机核那 20 处（尤其 `GetBodies2` 那族，轮 161 已踩过一次）；
               ③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+537 ", before, re.M):
    print("  游标 537 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+541 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 541 行已存在 ✓")
