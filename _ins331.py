import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           331 🎯 **Spec Kit `051`：补 `ellipse` —— 顺带量准一件更大的事：长度单位是毫米，而 docstring 写的是米**（轮 132）——
               挑它的理由：它在「真缺」档里，且**有现成的验证手段** —— 轮 117 已验过
               `sw_sketch.get_ellipses`（当时返回 **0**，因为没画椭圆）⇒ 本轮可以**造一个再读回来**。
            332 ★ **走的是**现行入口**（官方有**两级废弃链**）**：
               ```
               IModelDoc2.CreateEllipse(Object×3)  ⇒ Obsolete ⇒ IModelDoc2::CreateEllipse2
               IModelDoc2.CreateEllipse2(Double×9) ⇒ Obsolete ⇒ ISketchManager::CreateEllipse
               ⇒ 现行 = ISketchManager.CreateEllipse(9 个 double)，返回 SketchSegment（两源一致）
               ```
            333 ★★ **顺带量准的一件更大的事**：
               ```
               冒烟第 ① 段：sketch_circle(model, 0, 0, **25**)（**未做任何换算**）+ 拉伸 10
                          ⇒ get_bounding_box 得跨度 **[10, 50, 50]**（**毫米**）
               ⇒ ★ **传进去的就是毫米** —— 而 sw_part 的 docstring 有 **14 处**写「单位: 米」！
               ```
               ⚠ 而且**没有任何门禁会检查它** —— 工具层有规则 2（`_mm` 后缀）守着，
                 但 `sw_part` 是**脚本层**，**不受那条规则约束**。
               ⇒ 已**逐条校正为毫米**并在模块头写明是**实测校正**（已知事实 **73**）。
               ★ 与已知事实 71（`GetBodyBox` 返回毫米）是**同一台机器上互相印证**的两条。
            334 ★ **真机冒烟 11/11**：量单位那一步 + `sketch_ellipse` 建成 +
               **★ 往返：`get_ellipses` 读回 22 个**（轮 117 时是 0 —— 那时没画）。
            335 ★★ **本轮的形状：为了写一个小功能，量出了一件全局的事**：
               ```
               目标：补 ellipse（一个"真缺"条目）
               过程：写冒烟时决定**顺手量一下单位**（因为 docstring 说"米"，而轮 127 的观察像毫米）
               ⇒ ★ 结果量出：**整个 sw_part 的 14 处 docstring 都写错了单位**
               ⇒ ★ 一个条目 vs 一整模块的文档正确性 —— **顺手那一下更值钱。**
               ```
               ★ 与 `040`（验螺旋线时抓到 `FirstFeature` 缺陷）**同一个形状**：
                 **验证一个具体东西时，顺手核一个更基础的假设。**
            336 ⚠ **「覆盖范围」问题第三次出现**（前两次：124/125、126）：
               改 14 行 ⇒ 它们变成"新增行" ⇒ 需要来源块覆盖 ⇒ 但**遗留函数从来没人改过**
               ⇒ **覆盖缺口一直存在、只是没暴露**。补一块**不够** —— 中间还有两块
               （指向 `_raw\\reflect_sldworks\\…`）⇒ ★ 正解：**先把 `_source_blocks` 的实际区间
               打印出来**，再决定在哪补。★ 新认识：**"覆盖缺口"可以是既有的，改动只是把它照亮。**
               ⚑ **未查证**：椭圆的**长短半轴数值**未逐一核（只证建成 + 读得回来）；
                 `sketch_circle` 一类改动后**未重跑**既有冒烟；`d1_*` 方向向量**归一化与否未测**。
               回归 **1166 passed**。
               下轮候选：① 继续补「真缺」；② 给剩下 3 条 `stitched` 冒烟；
               ③ 把"脚本层的单位声明"也纳入某个机器检查（本轮证明它**无人守**）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+331 ", before, re.M):
    print("  游标 331 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+336 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 336 行已存在 ✓")
