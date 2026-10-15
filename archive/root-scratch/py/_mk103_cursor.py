import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           579 🎯 **Spec Kit `103`：样条****从「建不出来」变成「能建」**** —— 修实参形态 + 成员名（而「建不出来」是****误判****）**（轮 183）——
               背景：轮 141/182 记着「样条建不出来（`CreateSpline2` 返回 None）」⇒ ★ 它**挡住了 `composite_curve`**。
            580 ★★★ **读官方 Remarks ⇒ 发现**实参形态**要求**：
               ```
               `CreateSpline` / `CreateSpline2` 的 Remarks：
                 "The PointData array is a set of, at least, **two X, Y, Z values**.
                  X 起点 = PointData[0]，Y = [1]，Z = [2]；下一点 X = [3] …"
               ⇒ ★ 即一个**扁平的一维数组** `[x0,y0,z0, x1,y1,z1, …]`，⚠ 而仓库传的是 **list of tuples**。
               ```
            581 ★★★ **真机逐形态判别**（`tools/probe_spline_forms.py`，**每次回读草图段数**）：
               ```
               ① 扁平 list                   ⇒ 段数 0 → 0（没变）· 返回 None
               ② 扁平 tuple                  ⇒ 段数 0 → 0（没变）· 返回 None
               ③ **VARIANT(VT_ARRAY|VT_R8)** ⇒ 段数 **0 → 1（变了 ✚）**   ★★★ **成了**
               ④ list of tuples（原写法）     ⇒ 段数 0 → 0（没变）· 返回 None
               ⇒ ★★ 与**事实 167**（`AddRelation` 必须包 `VARIANT(VT_ARRAY|VT_DISPATCH)`）**完全同一族**：
                 **数组实参必须包 VARIANT**，且**官方 Remarks 没说** ⇒ **只能实测出来**。
               ```
            582 ⚠⚠ **修的过程中查出第二处**：`getattr(sketch_manager, "CreateSpline")` ⇒ **None** ⇒
               在 `get_com_member` 里报 `TypeError: 'NoneType' object is not callable` ——
               ★ 而**官方 md 明写** `CreateSpline` 是 "**Obsolete. Superseded by CreateSpline2**"
               ⇒ ★★ **必须走 `CreateSpline2`**；⚠ 那个 `TypeError` **指不出真因**。
               ★ 修后**三种写法全部成功**（点对 / 扁平 / `simulate=True` ⇒ 段数**都 0 → 1**）。
            583 ★★★ **意义：这是一个「挡着不止一个能力」的上游** —— 它一修，
               `composite_curve` 的**前置从「不可达」变成「可达」**（⚠ 本轮**未**重跑它，留给下轮）。
               ★★★ **「样条建不出来」是**误判** —— 而它已写进事实表（轮 141/182）** ⇒
                 ★ 教训：**「返回 None」既可能是「做不到」，也可能是「喂的东西不对」** ——
                   而**官方 Remarks 里的形态要求**是区分它们的第一步。
               ★ **这是本会话第 4 次「数组实参必须包 VARIANT」**（`AddRelation` 轮 167 · `Select4` 的 Callout ·
                 `CreateSpline` 本轮 …）⇒ ★ 定则：**官方签名里是 `Object` 的数组实参，先按「要包 VARIANT」准备**。
               门禁 + `release_check` exit 0 · 回归 **1248 passed**（契约 `-k "spline or relation"` **5 passed / 1 skipped**）。
               ⚑ **未查证**：⚠ **`composite_curve` 本轮未重跑** —— 前置**可达**但它**是否真能建成** **未验**；
                 ⚠ Remarks **没说「要包 VARIANT」** ⇒ 该知识**只能来自实测**（不可从文档推出）；
                 ⚠ 只证「段数变了」⇒ **不证样条的几何形状**；
                 ⚠ `CreateSplineByEqnParams` 族（B 曲线）**未试**。
               下轮候选：① **重跑 `composite_curve`**（前置现在可达 ⇒ 看它是否也能建成）；
               ② 顺同一线索查其它「返回 None 其实是形态不对」的地方（事实 40 那族还有几处）；
               ③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+579 ", before, re.M):
    print("  游标 579 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+583 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 583 行已存在 ✓")
