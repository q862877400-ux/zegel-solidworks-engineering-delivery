import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           372 🎯 **Spec Kit `059`：补 `centerline` —— 顺带查清 `get_lines` ****返回的根本不是线对象******（轮 140）——
               ★ 走**现行入口** `ISketchManager.CreateCenterLine(6 doubles)` —— 官方有**两级废弃链**：
               `IModelDoc2.CreateCenterLine(Object,Object)` ⇒ `CreateCenterLineVB`（**Void** 的 VB 变体）
               ⇒ **`ISketchManager.CreateCenterLine`**。
            373 ★★ **冒烟 8/8 里冒出来的一件事**：
               ```
               ✓ sketch_centerline 建成 · ★★ 往返 A：get_sketch_segments 读回 **1 段** ← 对
               ✓ ★ 往返 B：get_lines 读回 **12 条** ← ⚠ **只画了 1 条！**
               ✓ ★★ **再测单位**：半径 25 的圆 ⇒ 边界框 50 ⇒ **毫米**（官方文档的「in meters」是错的）
               ```
               ⚠ **12 对 1** ⇒ **数字对不上就要去看**（本轮的核心动作）。
            374 ★★★ **查清了：`get_lines` 返回的是「数值数组」，不是「线对象列表」**：
               | 画的条数 | `get_sketch_segments` | `get_lines` |
               |---|---|---|
               | 1 | 1 | **12** |
               | 2 | 2 | **24** |
               | 3 | 3 | **36** |
               ⇒ **完全线性：每条直线占 12 个 `float`**（元素类型是 `float`，不是 `Dispatch`）
               ⇒ **不能**当线对象用。⚠ **官方文档没写这个返回结构。**
               ⚠⚠ **而它为什么一直没被发现**：既有冒烟的判据只是「**非空**」⇒ **12 对 1 也照样绿**
               ⇒ ★ **判据太弱 ⇒ 真问题藏在绿里。**
            375 ★ **处置（四处）**：① 改写 `get_lines` 的 docstring（「数值数组」+「每条 12 个」+
               「要几条线用 `get_sketch_segments`」）· ② 冒烟**加定量判据**（非空 → **= 条数 × 12**）⇒ **18/18** ·
               ③ 契约测试加 3 条（含「**仓库里不许有人把结果当对象用**」）⇒ **15 passed** · ④ 事实 81。
            376 ★ **门禁尽职的一个正面实例**：加完公开函数 ⇒ `release_check` **exit=1**：
               ```
               [FAIL] 地图与来源同步
                  常见原因①：**增删了 scripts/sw_*.py 里的公开函数** ⇒ 计数变了
                  诊断：跑 `tools/build_union_map.py` 后看 git diff
               ```
               ⇒ ★★ 门禁**自己把原因与命令写出来了** ⇒ 跑一遍（1 行改动）⇒ **exit=0**。
               ★ 与事实 55（把"看不出怎么办"改成"给命令"）同一路数：**好门禁的报错要能直接执行。**
               ★★ **与事实 57/62/79 同一族，合起来是一句**：
                 「**绿有很多种假象 —— 假的绿比红更难发现。**」
                 （57 环境恰好满足 · 62 门禁没在尽职 · 79 会 skip · 本轮 **判据太弱**）
               ⚑ **未查证**：那 12 个 `float` 的**具体含义**未逐位核；中心线的**构造几何标记**是否自动
                 置上**未测**；⚠ `get_arcs` / `get_ellipses` 是否也是「数值数组」**未测**
                 —— 同样的疑问需要**同样的强判据**才能证。
               已知事实 **81** 入库 · 回归 **1196 passed**。
               下轮候选：① 用**同样的强判据**去查 `get_arcs` / `get_ellipses` / `get_splines`；
               ② 继续补「真缺」；③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+372 ", before, re.M):
    print("  游标 372 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+376 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 376 行已存在 ✓")
