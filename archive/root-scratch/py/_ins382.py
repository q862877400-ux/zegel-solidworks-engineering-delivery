import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           382 🎯 **Spec Kit `061`：量剩下的取法 —— ****推翻我上一轮的一概而论******（轮 142）——
               `060` 收工时我写下「`get_*` 系列**全都返回数值数组**」⇒ 本轮把那一格补上 ⇒ ★ **那句话是错的**。
            383 ★★★ **结果**（真机 SW 2026 SP4.1，`tools/probe_slot_and_point_shapes.py`）：
               | 画了什么 | 个数 | 取法 | 元素数 | 元素类型 |
               |---|---|---|---|---|
               | 槽口 | 1 / 2 | `get_sketch_slots` | **1 / 2** | **`CDispatch`** |
               | 直线（端点即草图点）| 1 / 2 | `get_sketch_points` | **2 / 4** | **`CDispatch`** |
               ```
               返回「数值数组」的（**曲线类**）：get_lines 12 · get_arcs 16 · get_ellipses 22
               返回「对象列表」的（**点/实体类**）：get_sketch_slots 1/个 · get_sketch_points **2/线**
               ⇒ ★★ **两种形状都有** —— 轮 141 那句「全都」是**过度概括**。
               ```
               ★ 规律**候选**（⚠ **n=5，当假设不当定则**）：**曲线类 ⇒ 数值数组；点/实体类 ⇒ 对象列表**。
               ★ 一条巧办法：`get_sketch_points` **不用新函数** —— 一条直线的**两个端点**就是草图点。
            384 ★★ **更正做了 7 处，且日志不重写**：
               ① `capabilities.yaml` ×2 · ② `sw_sketch.py` 的「通例」说明 ×2 ·
               ③ 契约测试注释 · ④ **事实 82 就地更正**（不新开一条 —— 它就是同一条）·
               ⑤ ★ **ROADMAP 游标 378 不重写**（那是当天的日志），而是在当场加一条**指向更正的标记**
               ⇒ ★ 与「已提交的 release/session 数据不改写、纠正靠追加」**同一种态度**。
            385 ★★★ **本轮最可复用的一条，是写更正时踩到的：「引用」与「主张」**：
               ```
               要写一条「不许再一概而论」的判据 ⇒ **它第一版就红了**
               ⇒ 因为**更正文字本身引用了那句错话**（"此处原写「…」——那是错的"）
               ⇒ ★★ **禁词判据必须先能区分「引用」与「主张」** ——
                 否则它把"**记录错误**"当成"**犯错**" ⇒ **结果是没人敢写下自己的错。**
               ⇒ 修法：每一处出现，**必须在它前面 40 字内**有「原写」或「更正」。
               ```
               ★★ 这比本轮任何测量都值钱：**一个不区分"引用"与"主张"的检查，
                 会把"自我更正"这个好行为一起惩罚掉。**
               ⚑ **未查证**：规律只是**候选**（n=5）；`get_parabolas` / `get_sketch_hatches` /
                 `get_contour_edges` / `get_sketch_contours` / `get_sketch_pictures` /
                 `get_sketch_paths` / `get_sketch_block_instances` **未测**（**画不出来**，不是取法的问题）；
                 12/16/22 个 `float` 的**具体含义**仍未逐位核。
               已知事实 **83** 入库 · 回归 **1201 passed**。
               下轮候选：① 回到「真缺」档继续补条目；② 给剩下 3 条 `stitched` 冒烟；
               ③ 查 `sw_sketch` 里其余取法是否有同类"静默"问题。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+382 ", before, re.M):
    print("  游标 382 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+385 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 385 行已存在 ✓")
