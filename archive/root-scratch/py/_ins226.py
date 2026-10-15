import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           226 🎯 **Spec Kit `030`：把 `sw_sketch.py` 的 6 个废弃取法换到后继**（轮 111）——
               承接 `029` 的台账（8 条真候选），先处置最集中的一簇：
               `GetLines` / `GetArcs` / `GetEllipses` / `GetParabolas` /
               `GetSketchPoints` / `GetUserPoints`（该模块 docstring 明写「**ISketch 完整封装**」⇒ 归属无疑）。
            227 ★ **换名之前先量了「形状有没有变」**（这一步是关键）：
               ```
               GetLines  → GetLines2(Int16)   ⚠ **多一个参数**（swCrossHatchFilter_e）
               其余 5 个 → 零参，直接可换
               ```
               ★ **如果只看名字就换**，`get_lines` 会在运行期炸（少传一个参数）。
                 ⇒ **查反射只多花一步，省掉一次运行期故障。**
               取 `swCrossHatchInclude = 0`（两源一致；swapi 只列 3 个、值相同、无冲突）。
            228 ★ **测试判据是被"故意打破"后改精确的，不是删掉的**：
               ```
               原判据：所有登记取法**必须零参**          —— 我的改动让 GetLines2 破例
               改后：  **在反射里存在** + 零参的仍须零参 + 例外**显式登记**（NON_ZERO_ARG_OK）
               ```
               ★ 关键区别：**放宽判据**会让"有意带参"和"写错了"混在一起；
                 **显式登记例外**则两者仍可区分。
                 ⇒ 判据被打破时，先问「**能不能改成更精确的**」，而不是「**能不能不管它**」。
            229 ✅ **复跑 `029` 的探针**：这 6 条**已不再出现在候选里**。
               ⚠ 但**换完仍未在真机上验过**（等级仍 `stitched`）—— 换的是**入口名**，
                 **不是"测过了"**。⚠ 且官方**未说明** `GetLines2(swCrossHatchInclude)`
                 是否**等价于**旧 `GetLines()` —— 这是**语义推断**，已写进源码注释。
            230 ⚑ **未查证**：台账里另两条真候选（`AddMate5` · `GetBodies2`）**未改**，
               且**未查它们的后继形状**（`CreateMate` / `GetBodies3` 的参数可能与旧的不同）；
               台账里 **20 条未逐条核**的候选仍未核。回归 **1085 passed**。
               下轮候选：① 查 `CreateMate` / `GetBodies3` 的形状再决定换不换；
               ② 继续补「真缺」；③ A5 的 2 条存疑。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+226 ", before, re.M):
    print("  游标 226 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+230 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 230 行已存在 ✓")
