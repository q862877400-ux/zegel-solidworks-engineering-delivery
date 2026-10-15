import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           531 🎯 **Spec Kit `093`：新检查器用出厂反射判「成员该在哪个接口」—— 命中 20 处，但****抓不到它自己的动机******（轮 173）——
               动机（接轮 172）：仓库**已有** `check_interface_member_ownership.py`，
               ⚠ 但它只覆盖「`data = CreateDefinition(<CONST>)` ⇒ `data.X`」**那一条路径**
               ⇒ ★★ **「从某个管理器直接取成员」这种形态它看不见** ⇒ 本轮补这个盲点。
            532 ★ **判据（可核验，零启发式）**：
               ```
               ① 反射 `_raw/reflect_sldworks/iface_sldworks.txt` 有 `## <Iface>` 分段
                  ⇒ 直接解析出 **接口名 → 成员名集合**（**1032 个接口 / 16732 个成员**）
               ② `X = get_com_member(<owner>, "<Member>")` ⇒ 由 `<owner>` 的接口查 `Member` 的
                  **返回类型** ⇒ 得到 `X` 的接口（★ 返回类型就在反射行首：`FeatureManager get_FeatureManager()`）
               ③ `get_com_member(X, "<Member2>")` ⇒ `Member2` **完全不在** `X` 接口的谱系里 ⇒ **报**
               ```
            533 ★★★ **我一个人在这一处**连踩两个假阳性**（如实记）**：
               ```
               第一版 **113** 处 —— 根因①：反射里**属性带 `get_` 前缀**，而代码写不带前缀
                                    ⇒ 属性读**全被误报**
               第二版 **47** 处  —— 根因②：推不出接口时我落到了 **`IObject` 兜底**
                                    ⇒ ★ **兜底值必然不在成员谱系里 ⇒ 必报**
               第三版 **20** 处  —— 去掉兜底（**推不出就留白、不检查**）
               ⇒ ★ 教训：**「推不出」不许用兜底值代替** —— 兜底会把「我不知道」变成「它有错」。
               ```
            534 ★★ **20 处高度可信（**独立于我的记忆**的两个佐证）**：
               ```
               `GetBodies2` 在 IModelDoc2 上 ⇒ 实际在 **IPartDoc / IComponent2**  ← ★ **轮 161 真机踩过**
               `GetSketchSegments2` ⇒ 反射里**没有**                        ← ★ **轮 162 真机踩过**
               `GetSheetNames` ⇒ IDrawingDoc · `AddMate5` ⇒ IAssemblyDoc · `GetTitle` ⇒ IModelDoc/IModelDoc2
               ```
               ★ 并**核实**了判据本身：`FeatureByName` **确实不在 IModelDoc2 上**（反射里只在
                 IAssemblyDoc / IComponent2 / IDrawingDoc / IPartDoc）⇒ **不是解析漏了**。
               ★★ **检查器独立复现了我的真机经验** —— 这比「看起来合理」强得多。
            535 ⚠⚠⚠ **关键局限：它抓不到它自己的动机**：
               ```
               `mold_evidence(model)` 的 owner 是**形参** ⇒ 静态推不出接口 ⇒ 被「留白」排除
               ⇒ ★★ **检查器抓不到 `mold_evidence`**（而那正是写它的起因）
               ```
               ★ 可补的两条路（**未做**）：① docstring 里的 `:param` 说明（本仓库 docstring 常写接口名）；
                 ② **从调用点推**（`mold_evidence(doc)` ⇒ `doc` 的接口）。
               ⚠ **定位：诊断工具，不接门禁** —— 判据还没证到能当门禁的程度（20 处里仍有需逐条真机核的，
                 如 `model` 到底是不是 `IModelDoc2`）⇒ ★ 与**事实 53 同族**（**证据进文档，不进工具**）。
            536 门禁 + `release_check` exit 0 · 回归 **1248 passed**。
               ⚑ **未查证**：⚠ **抓不到形参 owner**（**含动机本身**）；⚠ 20 处里需逐条真机核的；
                 ⚠ **没有真机验证那 20 处**（本轮**只做静态**）；⚠ **不接门禁**。
               下轮候选：① 给检查器补「**从 docstring / 调用点推形参接口**」⇒ 才能覆盖 `mold_evidence` 那类；
               ② 逐条真机核那 20 处（尤其 `GetBodies2` 那族，轮 161 已踩过一次）；
               ③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+531 ", before, re.M):
    print("  游标 531 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+536 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 536 行已存在 ✓")
