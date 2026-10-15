import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           434 🎯 **Spec Kit `072`：`InsertCompositeCurve` 换****边****再试 —— 四种选法全失败，按纪律停下**（轮 153）——
               动机：`071` 更正后「前提满足仍返回 False」，试那个最自然的候选 —— **选边**而不是
               「整个草图」（合成曲线的语义是「把**曲线**接起来」）。
            435 ★ **四种选法逐个试（50×50×20 方块，12 条边）**：
               ```
               ① **整个草图 × 2**（**官方示例的原样形态**，mark=1）      ⇒ False
               ② `IEntity.Select4(True, callout)` 选 2 条边（计数 2）    ⇒ False
                  ⚠ 它**没有 mark 参数**
               ③ **按面上的点 + mark=1** 选 2 条棱                       ⇒ False
                  命中 1 · 而 `GetSelectedObjectCount2(1)` = **0**
               ④ 按名字选边 ⇒ 计数 0（**事实 32 复现**，非新发现）
               ⇒ **全部返回 False** ⇒ 按**事实 53**（≥3 次就停）**停止试**。
               ```
            436 ★★ **本轮真正的收获：「前提已满足」这句话本身也没被证实**：
               ```
               `GetSelectedObjectCount2(-1)` = **2**  而  `GetSelectedObjectCount2(1)` = **0**
               ⇒ **「按点选边」那次并没有把 mark 设成 1**（或该接口的 mark 语义与预期不同）
               ⇒ ★★ 所以「前提已按官方要求满足」是个**未经证实的说法**
               ```
               ★★ 与轮 152**同一形状**：**在说「功能不行」之前，先证「前提真的满足了」** ——
                 而 mark 到底设上没有，要用**读回来的计数**判，**不是调用返回的 `True`**
                 （与事实 8 同族：`AddSelectionListObject` 的 bool 不可信，要回读计数）。
            437 ★★ **三句话放一起看（本会话最有价值的一组）**：
               ```
               ① 「一个不会失败的检查，等于没有检查」                    （事实 62/79/81/88）
               ② 「我量到了 X」与「X 是真的」之间，隔着「我的量法对不对」   （事实 91 → 轮 152）
               ③ 「我以为前提满足了」与「前提满足了」之间，隔着**一次回读** （事实 93 → 轮 153）
               ⇒ ★★ ②③ 是同一件事的**测量侧**与**准备侧**；① 是它们的**共同后果**。
               ```
               ⚑ **未查证**：⚠ **真因仍未查明**（已排除「整草图 vs 边」这个区分）；
                 ⚠ 「mark 没设上」的依据是**计数为 0**，而**该接口的 mark 语义**没验证；
                 ⚠ 选点坐标是**估算**的（命中 1/2）⇒ 未必落在棱上；
                 ⚠ `insert_composite_curve` **已写但未取证** ⇒ `composite_curve` **不升级**。
               已知事实 **93** 入库 · 回归 **1232 passed** · `release_check` exit 0。
               下轮候选：① **先把 mark 真的设上**（拿 `GetSelectedObjectCount2(1)` 回读为准）
                 再试一次 composite_curve；② 回到「真缺」继续补；③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+434 ", before, re.M):
    print("  游标 434 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+437 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 437 行已存在 ✓")
