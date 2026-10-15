import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           377 🎯 **Spec Kit `060`：用****同样的强判据****查其余取法 —— 查出「通例」与一个****静默空操作******（轮 141）——
               起因：`059` 的限度里写着「⚠ `get_arcs` / `get_ellipses` 是否也是数值数组，**未测**」
               ——「**同样的疑问需要同样的强判据才能证**」⇒ 本轮**就去做那一格**。
            378 ★★ **结果 ①：是通例，不是孤例**（真机，画 N=1/2 个）：
               | 取法 | 画 1 个 | 画 2 个 | 每个占几个 `float` |
               |---|---|---|---|
               | `get_lines` | 12 | 24 | **12** |
               | `get_arcs` | 16 | 32 | **16** |
               | `get_ellipses` | 22 | 44 | **22** |
               ⇒ `get_*` 系列**全都返回数值数组**（元素 `float`）⇒ 已把三个 docstring 写明形状。
            379 ★★★ **结果 ②：`sketch_spline` 是「静默空操作」**：
               ```
               ① CreateSpline2              ⇒ 返回 **None** ⇒ get_sketch_segments = **0**（不抛异常）
               ② **重绘**（GraphicsRedraw）后 ⇒ **仍是 0**  ⇒ ★ **排除**官方 Remarks 那句
                                                「always adds directly to the database / 必须重绘才看得见」
               ③ CreateSpline（1 参旧版）    ⇒ **迟到绑定里没有这个成员**
               ④ 对照·同流程画直线           ⇒ **1** ⇒ 流程本身没问题
               ```
               ★ 根因：`CreateSpline2` 已 **Obsolete**，后继 `CreateSpline3(…, Object&)` 末参是
                 **BYREF** ⇒ **事实 47/68 的架构限制**。
               ⇒ 处置照 `sw_surface._invoke`（**事实 40**）：**让失败可见** —— 返回 `None` 即抛。
            380 ★★ **本轮形状：把上一轮"未测"的那一格补上，补出一个通例 + 一个静默空操作** ——
               ★ 与 `051`（补 `ellipse` ⇒ 顺带量出整模块单位写错）**同一个形状**：
                 **为了补一格而去看，看到的往往不止那一格。**
               ★ 「静默空操作」是**事实 40 那一族的第三次**（`Create*Surface` 不可靠 ⇒ 抛 ·
                 `CreateSpline2` 返回 None ⇒ 抛）—— 处置都是**让它可见**，不是"修好它"
                 （根因在架构）。
            381 ⚠ **一次我自己的判据错**（如实记）：第一次测"重绘"时把 `ActiveView` **当方法调**
               （它是**属性**）⇒ EXC ⇒ **那次重绘根本没发生** ⇒ 若就此收工，
               `sketch_spline` 的结论就**缺一环**（"是不是只是没重绘？"没被排除）⇒ 修对后重绘
               真的发生 ⇒ **重绘后仍是 0** ⇒ 结论才站得住。
               ★ 本会话**第三次**「先核对量的是不是那个东西」（`048` 爬错层 · `057` 注错名字 · 本轮调错形态）。
               ⚑ **未查证**：12/16/22 个 `float` 的**具体含义未逐位核**；
                 `get_splines` / `get_polylines` / `get_sketch_points` 等**其余取法形状未测**
                 （`get_splines` 量到 0 是**因为样条画不出来**）；`CreateSpline3` 的 BYREF 末参**没再试**。
               已知事实 **82** 入库 · 回归 **1199 passed**。
               下轮候选：① 把剩下几个取法的形状也量了（`get_polylines` / `get_sketch_points` 等）；
               ② 继续补「真缺」；③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+377 ", before, re.M):
    print("  游标 377 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+381 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 381 行已存在 ✓")
