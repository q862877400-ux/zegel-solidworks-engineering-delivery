import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           276 🎯 **Spec Kit `040`：螺旋线真机冒烟 —— 抓到缺陷、修好、并升 `verified`**（轮 121）——
               写冒烟**之前复查源码**就发现一处可疑：`_newest_feature_name()` 读
               `model.FirstFeature` —— 那是**特征树的第一个**，**不是最新加的那个**。
               **真机先 9/10**：螺旋线**真的建成了**（树新增 `螺旋线/涡状线1`），
               但函数**返回 `'收藏'`**（树里的收藏夹）⇒ **缺陷确认**。
            277 ★★ **缺陷的性质：返回了一个看起来合理的字符串** ——
               ```
               它**不抛异常**、返回值**看着像个人名** ⇒ **静态测试一条都抓不到**
               ```
               ★ 与 `028`（方程式 `-1` 双重语义）、`034`（`SketchUseEdge3` 返回 `False`）
                 **同一族**：**失败信号长得像正常值**。
               ★★ 这是**真机冒烟第二次抓到我自己写的缺陷**（第一次是 `039` 的 GTol）。
            278 ★ **修复**：改查官方 `IModelDocExtension.GetLastFeatureAdded()`
               （原文「Gets the **last feature added** to the model」）⇒ 返回 `螺旋线/涡状线1` ✓。
            279 ★★★ **然后加了一条硬验证：把定义读回来**：
               ```
               传进去：height_mm=50 · pitch_mm=10 · revolution=5
               读回来：Height = **0.05 米** · Pitch = **0.01 米** · Revolution = **5.0**
               ⇒ ★★ 这同时**证明 mm→米 的换算是对的**（若换算错，读回的会是 50）
               ```
               ⇒ **13/13** ⇒ 等级 `stitched` → **`verified`**；`verified 29 → 30` · `stitched 6 → 5`。
            280 ★★ **连着两轮冒烟，各抓到一处我自己写的缺陷 —— 但性质不同**：
               ```
               039（GTol）：API **到不了** —— 不是我的错，是那条路径在本机不通
               040（螺旋线）：**我的实现写错了** —— 且它"看着像对的"
               ```
               ★ 并且「**什么算硬证据**」已攒出**同一档**的三个实例：
               `035` 方程式（写==读）· `036` 草图（画 2 样 ⇒ segments==2）· `040` 螺旋线（传 50mm ⇒ 读回 0.05）。
               ★★ **共同点：空操作满足不了它们**；而「没抛异常」**空操作能满足** ⇒ 不算证据。
               ⚠ 未查证：只验了 3 个参数，其余 6 个与 `helix_def` 的另 3 种取值未测；
                 **`TaperAngle` 的单位仍未验证**。回归 **1108 passed**。
               下轮候选：① 继续给剩下 4 条 `stitched` 冒烟（**连续两轮都有产出**）；
               ② 继续补「真缺」；③ A5 的 2 条存疑。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+276 ", before, re.M):
    print("  游标 276 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+280 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 280 行已存在 ✓")
