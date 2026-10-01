# 031 · 另两条废弃候选：查清了，**决定不换**

**Status**: Implemented（轮 112）

## 背景
`029` 的台账查出 **8 条真候选**；`030` 换掉了 6 条（`sw_sketch.py` 的 `ISketch` 取法）。
剩下 **2 条**：`GetBodies2`（`IComponent2`）· `AddMate5`（`IAssemblyDoc`）。
本轮把它们的后继形状查清 —— **结论是不换**。

## 查证结果（**两源**：出厂反射 + `C:\swapi` 文档）

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
