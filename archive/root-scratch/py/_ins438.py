import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           438 🎯 **Spec Kit `073`：判别实验 —— ****mark 到底落没落******（轮 154）——
               `072` 留了**两个候选**没分开：①「mark 没设上」②「`GetSelectedObjectCount2(mark)` 的读法不对」。
            439 ★★★ **手法：换一个已知能选中的对象**（棱 ⇒ **草图**），其余调用形态不变：
               ```
               mark=0 ⇒ GetSelectedObjectCount2:  -1:1  0:1  1:0  2:0
               mark=1 ⇒ GetSelectedObjectCount2:  -1:1  0:0  1:1  2:0     ★ 精确落在 mark=1
               mark=2 ⇒ GetSelectedObjectCount2:  -1:1  0:0  1:0  2:1     ★ 精确落在 mark=2
               ```
               ⇒ ★★★ **两个候选都不是原因**：**mark 能落上**、**读法也对**（`-1` = 全部）。
            440 ★★★ **真因是第三个：`SelectByID2` 返回 `True` 却什么都没选中** ——
               轮 153 那次 `SelectByID2("", "EDGE", …, mark=1, …)` **返回 True**，
               而 `GetSelectedObjectCount2(1)` = **0** ⇒ **`True` 与「选中了」是两件事**。
               ★ 与**事实 8**（`AddSelectionListObject` 的 bool 不可信，要回读计数）**同族** ——
                 而那条此前**只记在 `AddSelectionListObject` 名下**，这次把 **`SelectByID2` 也纳进来**
                 ⇒ **事实 94**。
            441 ★★ **三次同一纪律**：
               ```
               轮 152：查「我的量法对不对」          （FeatureByPositionReverse 滞后一格）
               轮 153：查「我以为前提满足了没有」      （发现 mark 计数 0）
               轮 154：查「**我读那个前提的方法对不对**」 ⇒ 判别实验 ⇒ 两者都证明了，真因是**第三个**
               ⇒ ★★ 三次都在把**「我的观测」本身当成待验对象**；
                 而三次的结论都是：**观测方法本身有问题**（滞后一格 / 前提没验 / bool 不可信）。
               ```
               ★ **可直接用的判据（事实 94）**：判「选上没有」**一律回读**
                 `GetSelectedObjectCount2(<mark>)`，**不要看 `SelectByID2` 的返回值**
                 （它只表示「找到了那个名字/位置」）。
               ⚑ **未查证**：⚠ `InsertCompositeCurve` **真因仍未查明**（但失败点更清楚了：
                 得先**真的**选中 2 条边）；⚠ 判别实验只在**草图**上做 ——
                 **棱为什么返回 True 却没选中，未查明**；⚠ `composite_curve` **不升级**。
               已知事实 **94** 入库（93 已就地更正）· 回归 **1232 passed** · `release_check` exit 0。
               下轮候选：① **回读着 mark 计数**把 2 条边真的选上，再试一次 `InsertCompositeCurve`；
               ② 回到「真缺」继续补；③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+438 ", before, re.M):
    print("  游标 438 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+441 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 441 行已存在 ✓")
