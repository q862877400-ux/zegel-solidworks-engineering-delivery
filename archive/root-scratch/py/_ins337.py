import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           337 🎯 **Spec Kit `052`：给「脚本层的单位声明」装守卫 —— **试了，做不成，而且原理不成立****（轮 133）——
               起因（`051` 留的尾巴）：脚本层单位**无人守**（工具层有规则 2，脚本层不受它约束）⇒ 去试装一个。
            338 ★ **判法（有界、可复核）**：显式**长度词表**（radius/depth/width/dx…）→ 公开函数**形参名**命中
               → 看源码里有没有**单位声明**。结果：**已声明 10 个 · 一处都没声明 4 个**。
            339 ★★ **那 4 个逐条人工看 —— 4/4 全是假阳性**：
               | 模块 | 命中词 | 真相 |
               |---|---|---|
               | `sw_costing.set_lot_size(lot_size)` | `lot_size` | **批量大小**（件数）|
               | `sw_jlcfa_gui.drag(x1,y1,x2,y2)` | `x1 y1 x2 y2` | **屏幕坐标** |
               | `sw_jlcfa_gui.find_node(depth)` | `depth` | **树的深度** |
               | `sw_jlcfa_select.crop_region(dx,dy,…)` | `dx dy` | **像素** |
               | `sw_view.set_view_frame(width,height)` | `width height` | **窗口几何**（像素）|
               | `sw_view.translate_view(dx,dy)` | `dx dy` | **像素** |
               ⇒ 假阳性率 **4/4 = 100%**（此前 `029` 26% · `032` 50% · `037` 59%）。
            340 ★★ **这次是"根本做不成"，不是"假阳性多"**：
               ```
               `size`/`depth`/`width`/`dx` 在**非几何**语境里同样常用
               ⇒ ★ 「长度词表」**无法区分「几何长度」与「同名的非几何量」** —— 那是**语义**判断
               ⇒ 缩小词表则覆盖面太小，**漏的比抓的多**
               ```
               ★ 反向价值：这也解释了 `051` 那个错**为什么活那么久** ——
                 **不是"没人管"，而是"管不了"**。⇒ 两种解释导向**完全不同的对策**：
                 不是"加个门禁"，而是"**用实测校正**"（`051` 就是这么做的）。
            341 ⚑ **处置**：**不做门禁**（假阳性 100%）· 探针保留供**人工**扫 ·
               ★ **探针源码里写明结论**（免得下一个人拿它当判据）·
               ★ **唯一可靠的办法是实测**。
               ⚠ **本轮没有产出任何守卫** —— 产出的是「**这个守卫做不成**」的证据 + **为什么**。
               ⚠ 限度：词表是人为选的（换一份会得到不同清单，**但结论不变**）；
                 `051` 那 14 处修好之后，**同类错误仍可能再犯** —— 靠人、靠实测。
               ★ 第 4 次强调同一族事，而这次的结论最强：
                 **凡"按名字判语义属性"的检查，失败不是调参问题，是类别问题。**
               已知事实 **74** 入库 · 回归 **1166 passed**。
               下轮候选：① 继续补「真缺」；② 给剩下 3 条 `stitched` 冒烟；
               ③ 把 `048` 的协议层检查接进常规回归（已可跑、不碰 COM）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+337 ", before, re.M):
    print("  游标 337 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+341 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 341 行已存在 ✓")
