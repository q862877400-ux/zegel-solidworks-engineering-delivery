import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\030-sketch-getters-successors")
S.mkdir(parents=True, exist_ok=True)

spec = """# 030 · 把 `sw_sketch.py` 的 6 个废弃取法换到后继

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
"""

plan = """# 030 · Plan

## 步骤
1. 从 `029` 的台账取 6 条 `sw_sketch.py` 的候选
2. ★ **先查后继的形状**（不猜）：反射里逐个比 ⇒ **5 个零参直接换，1 个带参**
3. 取 `swCrossHatchFilter_e` 的值（**两源**，确认无冲突）
4. 改 `SKETCH_GETTERS`（后继排前、旧名保留）+ 6 个便捷取法 + 新常量
5. ★ 改测试：原「必须零参」的判据**被我的改动故意打破** ⇒
   改成「存在性 + 零参的仍须零参」，并**单列一条**钉住那个参数
6. ★ **复跑探针**验证这 6 条已消失
7. 更新台账 + 重生成 + 门禁 + 回归

## 风险与对策
| 风险 | 对策 |
|---|---|
| 换名但**形状变了** ⇒ 运行期炸 | ★ **先查反射**：发现 `GetLines2` 多一个参数 ⇒ 显式补上并测试 |
| 顺手把「必须零参」的判据删掉了事 | ★ 改成**更精确**的判据（存在性 + 例外显式登记），**不是**放宽 |
| 把"换了入口"说成"修好了" | 台账与 converge 都写明「**未在真机上验过**」|
| 一次改太多 | 本轮**只改这 6 条**；`AddMate5` / `GetBodies2` 留台账 |
"""

tasks = """# 030 · Tasks（全部完成，轮 111）

- [x] T-2601 从台账取 6 条候选
- [x] T-2602 ★ 查后继形状 ⇒ **5 个零参 + `GetLines2` 带参**
- [x] T-2603 取 `swCrossHatchFilter_e`（两源，确认无冲突）
- [x] T-2604 改 `sw_sketch.py`（登记表 + 6 个取法 + 新常量）
- [x] T-2605 同步测试 `tests/test_sw_sketch_contract.py`（**12 passed**）
  `→ 验收:` `python -m pytest tests/test_sw_sketch_contract.py -q`
- [x] T-2606 ★ **复跑探针**验证这 6 条已消失
  `→ 验收:` `python tools/probe_obsolete_members.py`
- [x] T-2607 更新台账（标为已处置 + 写明"仍未真机验过"）
- [x] T-2608 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 030 · Converge

**Converged**: 2026-10-01（轮 111）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-2601 6 个取法都改用后继 | ✅ 测试逐条断住 |
| SC-2602 `get_lines` 传 `include=0` | ✅ 单列一条测试 |
| SC-2603 判据改成「存在性 + 零参例外显式登记」 | ✅ **不是放宽，是更精确** |
| SC-2604 复跑探针 | ✅ **这 6 条已不在候选里** |
| SC-2605 台账标已处置 | ✅ 含「仍未真机验过」声明 |
| SC-2606 门禁 + 回归 | ✅ `release_check` exit 0 · **1085 passed** |

## 二、★ 换名之前先量了「形状有没有变」
```
GetLines  → GetLines2(Int16)   ⚠ 多一个参数
其余 5 个 → 零参，直接可换
```
★ **如果只看名字就换**，`get_lines` 会在运行期炸（少传一个参数）。
⇒ **查反射只多花一步，省掉一次运行期故障。**

## 三、★ 测试判据是被"故意打破"后**改精确**的，不是删掉的
```
原判据：所有登记取法**必须零参**                —— 我的改动让 `GetLines2` 破例
改后：  **在反射里存在** + 零参的仍须零参 + 例外**显式登记**（NON_ZERO_ARG_OK）
```
★ 关键区别：**放宽判据**会让 `GetLines2` 这种"有意带参"和"写错了"混在一起；
**显式登记例外**则两者仍可区分。⇒ 遇到判据被打破时，先问「**能不能改成更精确的**」，
而不是「**能不能不管它**」。

## 四、⚠ 这一轮**只处理了 8 条里的 6 条**
台账里 `AddMate5`（`IAssemblyDoc`）与 `GetBodies2`（`IComponent2`）**未改** ——
⚠ **未查**它们的后继形状（`CreateMate` / `GetBodies3` 的参数可能与旧的不同）。
⇒ 与 `023`/`024`/`028` 的教训一致：**换入口前必须先比形状。**

## 五、未查证
* **换完仍未在真机上验过**（等级 `stitched`）—— 换的是**入口名**，不是"测过了"；
* ⚠ 官方**未说明** `GetLines2(swCrossHatchInclude)` 是否**等价于**旧 `GetLines()` ——
  这是**语义推断**，已写进源码注释；
* `AddMate5` / `GetBodies2` 的后继形状**未查**；
* 台账里 **20 条未逐条核**的候选**仍未核**。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
