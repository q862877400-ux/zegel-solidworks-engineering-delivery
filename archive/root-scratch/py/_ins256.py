import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           256 🎯 **Spec Kit `036`：草图读回真机 17/17 —— 并**顺手补上一处 A1 覆盖缺口****（轮 117）——
               挑它的理由：轮 111（`030`）我把 **6 个官方已废弃的草图取法换成了后继**
               （其中 **`GetLines2` 还多带一个参数**）—— ⚠ 那次**只有静态证据**，
               签名若对不上**代码会在运行期炸**。⇒ **本轮专门验那一次替换。**
            257 ★ **冒烟 17/17**（程序化造前置，不靠人手）：
               ```
               start_sketch → sketch_line(1 条线) → sketch_arc(1 段弧) → 取 ActiveSketch
               ★ get_lines          list · **12** 个元素      ★ get_arcs   list · **16**
               ★ get_ellipses       list · 0                  ★ get_parabolas list · 0
               ★ get_sketch_points  list · **5**              ★ get_user_points list · 0
               ✓ get_sketch_segments（未换，对照） list · **2**  ← ★ **交叉验证：正好线+弧**
               end_sketch · 关件不保存 · ★ 收尾无残留模态框
               ```
            258 ★★ **拿到的是"能被空操作证伪"的证据**，不只是"没报错"：
               ```
               我们画了 1 条线 + 1 段弧
               ⇒ get_sketch_segments 返回 **2**  ← 与"画了两样东西"对得上
               ⇒ get_lines 返回 12 个浮点 · get_arcs 返回 16  ← 数据量与"一线一弧"相符
               ⇒ 没画椭圆/抛物线/用户点 ⇒ 它们返回 **0**  ← 合理
               ```
               ⚠ 与 `012` 对照：那时 `list_render_materials` 返回 **0 个材质**，
                 「没报错」**什么都没证明**。
            259 ★ **顺手查出一处 A1 覆盖缺口**：
               ```
               `sketch_edit_ops` 只管**草图编辑** ⇒ **`sw_sketch.py`（读回）根本没有能力条目**
               ⇒ A1「每域都有来源」在这一处**本来是空的**，而**没人注意到**
               ```
               ⇒ 本轮**新建 `sketch_query` 条目**并直接标 **`verified`**（真机证据已在手）。
               ★ 教训：**"能力有实现"与"能力有条目"是两件事** ——
                 `017` 发现过"有实现但没暴露"，本轮发现"**有实现但没登记**"。
            260 ⚑ **新问题（值得下轮做）**：`scripts/` 下有多少个 `sw_*.py`
               **没有对应的 capability 条目**？⇒ 本轮只**碰巧**发现一个，**未做系统核对**。
               ★ 这属于 A1/A4 的直接判据，**且可以机器化**（模块名 ↔ 条目名）。
               ⚠ 限度：只证"没抛异常 + 元素数合理"，**不证元素内容/顺序**；
                 只测了线+弧，其余几何未测。
               能力 **35 条**（新增 1）· `verified 29` · `stitched 5` · 回归 **1091 passed**。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+256 ", before, re.M):
    print("  游标 256 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+260 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 260 行已存在 ✓")
