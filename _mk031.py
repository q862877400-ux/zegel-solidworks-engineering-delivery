import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\031-obsolete-not-switching")
S.mkdir(parents=True, exist_ok=True)

spec = """# 031 · 另两条废弃候选：查清了，**决定不换**

**Status**: Implemented（轮 112）

## 背景
`029` 的台账查出 **8 条真候选**；`030` 换掉了 6 条（`sw_sketch.py` 的 `ISketch` 取法）。
剩下 **2 条**：`GetBodies2`（`IComponent2`）· `AddMate5`（`IAssemblyDoc`）。
本轮把它们的后继形状查清 —— **结论是不换**。

## 查证结果（**两源**：出厂反射 + `C:\\swapi` 文档）

### ① `GetBodies2` → `GetBodies3`
```
旧:  Object GetBodies2(Int32 BodyType)                              1 参
新:  Object GetBodies3(Int32 BodyType, **out Object** BodiesInfo)    2 参（**含 out**）
```
官方还说 `GetBodies3` **支持轻量化零部件**（旧的不支持）⇒ **它确实更好**。
⚠ **但第二个参数是 `out`**，而本机后端（pywin32 迟到绑定）对 `Object&` 类参数
**已有两次失败记录**（**已知事实 47**：`ISketchedBendFeatureData` 的
`AccessSelections` / `SetFixedFace` 在 **20+ 种形态**下全部失败，
且结论是「**换 `comtypes` 或进程内 C++ 后端才可能解决**」）。
⇒ **不换**。

### ② `AddMate5` → `CreateMate`
```
旧:  Mate2 AddMate5(Int32, Int32, Boolean, Double×8, Boolean, Boolean, …)   **~18 个位置参数**
新:  Object CreateMate(**Object MateData**)                                  **1 个数据对象**
```
官方：`MateData` 是 `IMateFeatureData` 的**派生接口对象**
（`ICoincidentMateFeatureData` / `IAngleMateFeatureData` / `ICamFollowerMateFeatureData` …）。
⇒ 这**不是换名，是换调用范式**。本仓库**目前没有任何 `IMateFeatureData` 的构造代码** ⇒
换了要**新写一套**，且**没有安全真机验证手段**（建配合会改装配体）。
⇒ **不换**。

## 判据
| ID | 判据 |
|---|---|
| SC-2701 | ★ 两条的**旧/新签名并排写出**（不是只写"不换"）|
| SC-2702 | ★ `GetBodies3` 的 `out` 参数**明确点出**，并**挂到已知事实 47** 上 |
| SC-2703 | ★ `CreateMate` 说明它是**换范式**（要造 `IMateFeatureData` 对象），不是换名 |
| SC-2704 | ★ **声明这是判断、不是实测**（「未实测」写清楚）|
| SC-2705 | 台账标为**已全部处置**（8 条：6 换 · 2 查清后不换）|
| SC-2706 | 门禁 + 回归不退化（回归 **1085 passed**）|

## ⚠ 明确记下的限度
* **两条都没有实测** —— 「不换」的依据是**签名形状** + **已知事实 47**，不是本轮跑出来的结论；
* `GetBodies3` **能不能在本机后端跑** —— **未试**（试它要能造出 `out` 参数，属另一个量级的验证）；
* `AddMate5` 保留旧名 ⇒ **官方说它废弃**这件事**仍然成立**，只是换了代价更大。
"""

plan = """# 031 · Plan

## 步骤
1. 从反射取两条的**旧/新签名**并排比
2. ★ 发现 `GetBodies3` **多一个 `out` 参数** ⇒ 挂到**已知事实 47**（BYREF 在后端失败）
3. ★ 发现 `CreateMate` 要**造数据对象** ⇒ 是**换范式**不是换名
4. 两源（swapi 文档）确认细节：`GetBodies3` 支持轻量化（更好）· `CreateMate` 收 `IMateFeatureData`
5. ⇒ **决定不换**，把理由逐条写进台账
6. 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 把"不换"写成一句结论（无依据）| ★ 旧/新签名**并排写**，并指出**为什么**不能直接换 |
| 把**判断**说成**实测** | ★ SC-2704 明确声明「未实测」|
| 留着旧名却不记它已废弃 | 台账里那两行**保留**，只是状态改成"查清后不换" |
| 顺手去试 `GetBodies3` | **不做** —— 那要先解决 BYREF，属另一个量级的验证 |
"""

tasks = """# 031 · Tasks（全部完成，轮 112）

- [x] T-2701 取两条的旧/新签名（反射）
- [x] T-2702 ★ 查 `GetBodies3` 的第二个参数 ⇒ **`out Object`** ⇒ 挂已知事实 47
- [x] T-2703 ★ 查 `CreateMate` 的参数 ⇒ **`IMateFeatureData` 对象** ⇒ 换范式
- [x] T-2704 两源确认细节（swapi 文档）
- [x] T-2705 台账追加「不换」的两条及理由，标为**已全部处置**
  `→ 验收:` `Select-String docs\\obsolete-member-candidates.md -Pattern '决定「不换」'`
- [x] T-2706 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 031 · Converge

**Converged**: 2026-10-01（轮 112）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-2701 旧/新签名并排写出 | ✅ 见台账 §〇之二 |
| SC-2702 点出 `out` 参数并挂事实 47 | ✅ |
| SC-2703 说明 `CreateMate` 是换范式 | ✅ |
| SC-2704 声明是判断不是实测 | ✅ |
| SC-2705 台账 8 条全部处置 | ✅ **6 换 · 2 查清后不换** |
| SC-2706 门禁 + 回归 | ✅ `release_check` exit 0 · **1085 passed** |

## 二、★ 本轮的产出是「**查清后决定不做**」
```
GetBodies3(Int32, out Object)   ⇒ 多一个 out ⇒ 挂**已知事实 47**（BYREF 在后端失败）
CreateMate(Object MateData)     ⇒ 要造 IMateFeatureData 对象 ⇒ **换范式**，不是换名
```
★ **「不换」必须有依据才站得住** —— 上一轮 `030` 换 6 条是因为**后继是直接可换的**；
这一轮不换是因为**后继不是同一个调用形态**。
★ **两轮合起来才是完整的处置**：**能换的换掉，不能换的把理由写下来** ——
而不是"要么全换、要么全不换"。

## 三、⚠ 这一轮的结论**没有一条是实测出来的**
* `GetBodies3` 在本机后端**能不能跑** —— **未试**；
* 「BYREF 会失败」的依据是**已知事实 47**（另一族成员的 20+ 次失败），
  **不是**在 `GetBodies3` 上测出来的。
⇒ **这是判断**。★ 与 `023`~`030` 相比，本轮**没有新的运行证据**，**只有新的查证**。
⚠ 台账里写明了这一点。

## 四、⚠ 保留旧名 ⇒ 「官方说它废弃」这件事**仍然成立**
```
AddMate5 / GetBodies2 仍是官方 **Obsolete**
⇒ 它们是**已知的、有据可查的**技术债 —— 不是"没问题了"
```
★ 与 `029` 的结论一脉相承：**「官方标了废弃」与「会坏」是两件事**；
本轮补上第三件：**「知道它废弃」与「换得起」也是两件事**。

## 五、未查证
* 两条**都没实测**；
* `GetBodies3` 的 `out` 参数在本机后端是否真的失败 —— **未试**；
* 台账里 **20 条未逐条核**的候选**仍未核**。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
