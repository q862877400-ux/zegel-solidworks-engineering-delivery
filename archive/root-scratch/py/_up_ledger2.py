import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\obsolete-member-candidates.md")
t = P.read_text(encoding="utf-8")

ADD = """
---

## 〇之二、⚑ 另两条真候选：**查清了，决定「不换」**（2026-10-01 轮 112）

`029` 查出 8 条真候选，`030` 换掉 6 条。**剩下这 2 条经查证后决定保留旧名** ——
**不是因为懒，是因为后继不是"换个名字"。**

### ① `GetBodies2` → `GetBodies3`
```
旧:  Object GetBodies2(Int32 BodyType)                        1 参
新:  Object GetBodies3(Int32 BodyType, **out Object** BodiesInfo)  2 参（**含 out**）
```
官方还说 `GetBodies3` **支持轻量化零部件**（旧的不支持）—— 所以它**确实更好**。
⚠ **但它的第二个参数是 `out`**。而本机后端（pywin32 迟到绑定）对 `Object&` 类参数
**已有两次失败记录**（**已知事实 47**：`ISketchedBendFeatureData.AccessSelections` /
`SetFixedFace` 在 20+ 种形态下全部失败，且**换 `comtypes` 或进程内 C++ 才可能解决**）。
⇒ **不换**。⚠ **未实测** —— 这是**依据已知事实 47 的判断**，不是本轮跑出来的结论。

### ② `AddMate5` → `CreateMate`
```
旧:  Mate2 AddMate5(Int32, Int32, Boolean, Double×8, Boolean, Boolean, …)   **~18 个位置参数**
新:  Object CreateMate(**Object MateData**)                                  **1 个数据对象**
```
官方：`MateData` 是 `IMateFeatureData` 的**派生接口对象**
（`ICoincidentMateFeatureData` / `IAngleMateFeatureData` / `ICamFollowerMateFeatureData` …）。
⇒ 这**不是换名，是换调用范式**：从"传一串位置参数"变成"先造一个数据对象再传进去"。
⚠ 本仓库**目前没有任何 `IMateFeatureData` 的构造代码** ⇒ 换了要**新写一套**，
且**没有真机验证手段**（建配合会改装配体）。
⇒ **不换**。

### 结论
```
8 条真候选： 6 条**已换**（030）· 2 条**查清后决定不换**（032，理由如上）
⇒ 台账里这一档**已全部处置完毕**（不再是"待办"）
```
"""

if "另两条真候选：**查清了，决定「不换」**" not in t:
    t = t.rstrip() + ADD
    P.write_text(t, encoding="utf-8")
    print("  ok 台账已追加「不换」的两条及理由")
else:
    print("  已有")
