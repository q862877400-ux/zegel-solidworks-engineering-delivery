# 030 · 把 `sw_sketch.py` 的 6 个废弃取法换到后继

**Status**: Implemented（轮 111）

## 背景
`029` 的废弃成员台账（`docs/obsolete-member-candidates.md`）查出我们仍在调 **8 条**
官方已标 `Obsolete` 的成员，其中最集中的一簇是 **`sw_sketch.py` 的 6 个 `ISketch` 取法**：
`GetLines` · `GetArcs` · `GetEllipses` · `GetParabolas` · `GetSketchPoints` · `GetUserPoints`。
★ 该模块 docstring 明写「**ISketch 完整封装**」⇒ 归属**没有疑问** ⇒ 本轮换掉。

## 换法：先查清"形状有没有变"（**不猜**）
| 旧名 | 后继 | 形状 |
|---|---|---|
| `GetLines` | `GetLines2(Int16)` | ⚠ **多一个参数**（`swCrossHatchFilter_e`）|
| `GetArcs` | `GetArcs2()` | **零参，直接可换** |
| `GetEllipses` | `GetEllipses3()` | **零参，直接可换** |
| `GetParabolas` | `GetParabolas2()` | **零参，直接可换** |
| `GetSketchPoints` | `GetSketchPoints2()` | **零参，直接可换** |
| `GetUserPoints` | `GetUserPoints2()` | **零参，直接可换** |

⇒ ★ **5 个是直接换，只有 `GetLines2` 要补一个参数。**
`swCrossHatchFilter_e` 的取值**两源一致**（反射 5 个成员；swapi 列了 3 个、值相同、无冲突）
⇒ 取 `swCrossHatchInclude = 0`（与旧 `GetLines()` 的「都取」语义一致）。

## 改动
1. `SKETCH_GETTERS` 的元组里**把后继排到前面**（**旧名保留**，便于对照与自取）；
2. 6 个便捷取法改用后继（`get_lines` 传 `swCrossHatchInclude`）；
3. 新增常量 `SKETCH_CROSS_HATCH`（注明两源与"swapi 只列 3 个"这一事实）；
4. 测试同步：原判据「**所有取法必须零参**」不再成立（`GetLines2` 有意带参）⇒
   改成「**在反射里存在**，且**零参的仍须零参**」，并**单列一条**钉住 `get_lines` 传的那个参数。

## 判据
| ID | 判据 |
|---|---|
| SC-2601 | 6 个便捷取法**都改用后继**（测试逐条断言，防止改回旧名）|
| SC-2602 | ★ `get_lines` 传的是 `swCrossHatchInclude = 0`（唯一带参的后继）|
| SC-2603 | ★ 登记表判据改为「**存在性** + 零参的仍须零参」，并**显式登记** `GetLines2` 这个例外 |
| SC-2604 | ★ **复跑 `029` 的探针**：这 6 个**不再出现在候选里** |
| SC-2605 | ★ 台账标为**已处置**（含「**换完仍未在真机上验过**」这句声明）|
| SC-2606 | 门禁 + 回归不退化（回归 **1085 passed**）|

## ⚠ 明确记下的限度
* **换完仍未在真机上验过** —— 换的是**入口名**，**不是"测过了"**；等级仍是 `stitched`；
* ⚠ 官方**未说明**「`GetLines2(swCrossHatchInclude)`」是否**等价于**旧 `GetLines()` ——
  本模块按**语义一致**取 `include`，这一点**是推断，已在源码注释里声明**；
* 台账里另两条真候选（`AddMate5` · `GetBodies2`）**本轮未改**。
