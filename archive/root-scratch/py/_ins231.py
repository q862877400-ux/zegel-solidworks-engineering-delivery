import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           231 🎯 **Spec Kit `031`：另两条废弃候选 —— 查清了，决定「不换」**（轮 112）——
               `029` 查出 **8 条真候选**，`030` 换掉 6 条；剩这 2 条经查证后**保留旧名**。
            232 ★ **查证结果（两源）**：
               ```
               GetBodies2 → GetBodies3(Int32 BodyType, **out Object** BodiesInfo)
                 官方说新的**支持轻量化零部件**（确实更好），**但第二个参数是 out** ——
                 而本机后端对 Object& 类参数**已有两次失败记录**（**已知事实 47**：
                 ISketchedBendFeatureData 的 AccessSelections/SetFixedFace 在 20+ 种形态全败，
                 结论是"换 comtypes 或进程内 C++ 才可能解决"）⇒ **不换**
               AddMate5 → CreateMate(**Object MateData**)
                 旧的是 **~18 个位置参数**；新的是**收一个 IMateFeatureData 派生对象** ——
                 **这不是换名，是换调用范式**；本仓库**没有任何 IMateFeatureData 的构造代码**，
                 换了要新写一套且**没有安全真机验证手段** ⇒ **不换**
               ```
            233 ★★ **两轮合起来才是完整处置**：
               `030` 换 6 条 —— 因为后继**直接可换**；
               `031` 不换 2 条 —— 因为后继**不是同一个调用形态**。
               ⇒ **能换的换掉，不能换的把理由写下来** —— 而不是"要么全换、要么全不换"。
               台账里这一档（8 条）**已全部处置完毕**。
            234 ⚠ **本轮结论没有一条是实测出来的**：`GetBodies3` 在本机后端**能不能跑未试**；
               「BYREF 会失败」的依据是**已知事实 47**（另一族成员的失败），**不是**在它上面测的。
               ⇒ **这是判断**。★ 与 `023`~`030` 相比，本轮**没有新的运行证据，只有新的查证**。
            235 ⚑ **保留旧名 ⇒ 「官方说它废弃」这件事仍然成立** —— 它们是**已知的、有据可查的**
               技术债，不是"没问题了"。★ 与 `029` 一脉相承：「官方标了废弃」≠「会坏」；
               本轮补上第三件：**「知道它废弃」≠「换得起」**。
               ⚠ 未查证：台账里 **20 条未逐条核**的候选仍未核。回归 **1085 passed**。
               下轮候选：① 核那 20 条；② 继续补「真缺」；③ A5 的 2 条存疑。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+231 ", before, re.M):
    print("  游标 231 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+235 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 235 行已存在 ✓")
