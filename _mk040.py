import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\040-helix-smoke-found-and-fixed")
S.mkdir(parents=True, exist_ok=True)

spec = """# 040 · 螺旋线的真机冒烟 —— **抓到缺陷、修好、并升为 `verified`**

**Status**: Implemented（轮 121）

## 一、为什么挑它
* `023`（轮 104）补了螺旋线，**只有静态证据**；
* ★ 写冒烟**之前复查源码**时发现一处可疑：`_newest_feature_name()` 读的是
  `model.FirstFeature` —— 那是**特征树的第一个**，**不是最新加的那个**。

## 二、真机冒烟：**先 9/10，修完 13/13**
```
✓ 新建临时零件 · start_sketch · sketch_circle · 取到线段 · 选中那个圆
✓ insert_helix(height=50mm, pitch=10mm, 5 圈)     → 真的建成（特征树新增 螺旋线/涡状线1）
✗ ★★ 返回的名字 == 新建的那个                      返回 '收藏'    ← **缺陷**
✓ end_sketch · 关件不保存 · ★ 无残留模态框
```

## 三、★★ 缺陷的性质：**返回了一个看起来合理的字符串**
```
`_newest_feature_name` 读 `model.FirstFeature` ⇒ 拿到 '收藏'（特征树里的收藏夹）
而真正新建的是 '螺旋线/涡状线1'
⇒ 它**不抛异常、返回值看着像个人名**——**静态测试一条都抓不到**。
```
★ 与 `028`（方程式的 `-1` 双重语义）、`034`（`SketchUseEdge3` 返回 `False`）
**同一族**：**失败信号长得像正常值**。
★★ 这是**真机冒烟第二次抓到我自己写的缺陷**（第一次是 `039` 的 GTol）。

## 四、修复
```
改查官方 `IModelDocExtension.GetLastFeatureAdded()`
（官方原文：「Gets the **last feature added** to the model」）
⇒ 修完返回 '螺旋线/涡状线1' ✓
```
⚠ 官方 Remarks 提醒：该方法**可能返回子特征**（配合、工程图视图等）—— 已写进 limitations。

## 五、★★★ 然后加了一条**硬验证**：把定义**读回来**
```
传进去：height_mm=50 · pitch_mm=10 · revolution=5
读回来：Height = **0.05 米** · Pitch = **0.01 米** · Revolution = **5.0**
⇒ ★★ 这同时**证明 mm→米 的换算是对的**（若换算错，读回的会是 50）
```
★ 这是 **"往返一致"** 档的证据（与 `035` 的方程式、`036` 的草图同档），
**不是"没报错"** —— 空操作/换算错都满足不了它。

## 六、结果：**13/13** ⇒ 等级 `stitched` → **`verified`**
能力分布：**`verified 29 → 30`** · `stitched 6 → 5`

## 七、判据
| ID | 判据 |
|---|---|
| SC-3601 | 真机冒烟**先如实报 9/10**（没改判据去迎合）|
| SC-3602 | ★★ **抓到并修掉** `FirstFeature` 那处缺陷 |
| SC-3603 | ★ 改后**返回的名字 == 新建的那个特征**（测试钉住不许用 `FirstFeature`）|
| SC-3604 | ★★★ **读回定义**：`Height=0.05` / `Pitch=0.01` / `Revolution=5` —— 证明换算对 |
| SC-3605 | 等级升为 **`verified`** + `evidence`；**测试钉住不许降级** |
| SC-3606 | `GetLastFeatureAdded` 可能返回子特征这一点写进 limitations |
| SC-3607 | 门禁 + 回归不退化（回归 **1108 passed**）|

## ⚠ 明确记下的限度
* 只验了 `height_mm` / `pitch_mm` / `revolution` 这一组；
  `reversed` / `clockwise` / `tapered` / `outward` / `taper_angle_deg` / `start_angle_deg`
  与 `helix_def` 的**其余三种取值**（height+pitch / height+revolution / spiral）**未测**；
* ★ `Pitch` 的单位推断**本轮已被证实**（读回 0.01 与传的 10 mm 相符）；
  **`TaperAngle` 的单位仍未验证**；
* 只覆盖**定距**；变距（`InsertVariablePitchHelix`）**未实现**；
* 前置**必须选中定义直径的圆**（本模块不代选）。
"""

plan = """# 040 · Plan

## 步骤
1. 写冒烟：新零件 → 进草图 → 画圆 → **选中它** → `insert_helix` → 退草图 → 关件
2. ★ 顺带核一处源码疑点：`_newest_feature_name` 读 `FirstFeature`
3. 跑 ⇒ **9/10**：建成了，但**返回 `'收藏'`** ⇒ **缺陷确认**
4. ★ 查官方"取最后加的特征"接口 ⇒ `IModelDocExtension.GetLastFeatureAdded()`
5. 修 ⇒ 复跑
6. ★★ **再加一条硬验证**：把定义读回来，核 `Height`/`Pitch`/`Revolution`
7. ⇒ **13/13** ⇒ 升 `verified`
8. 同步源码来源块 / 测试（含"不许降级"与"不许用 FirstFeature"）
9. 重生成 + 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| **返回错名字却不抛异常** | ★ 冒烟里**显式比对**「返回的名字 == 特征树新增的那个」|
| 只证"建成了"就收工 | ★ 加**读回定义**这一步（往返一致档）|
| 改了实现忘了同步测试桩 | 桩要加 `Extension.GetLastFeatureAdded`（本轮改了三轮才对）|
| 改判据迎合现状 | ★ 冒烟**如实报 9/10**，改的是**代码** |
"""

tasks = """# 040 · Tasks（全部完成，轮 121）

- [x] T-3601 写 `tools/verify_helix_smoke.py`
- [x] T-3602 ★ 冒烟 **9/10** ⇒ 抓到 `FirstFeature` 那处缺陷
  `→ 验收:` `python tools/verify_helix_smoke.py`
- [x] T-3603 ★ 查官方接口 ⇒ `IModelDocExtension.GetLastFeatureAdded()`
- [x] T-3604 修 `_newest_feature_name` 并复跑
- [x] T-3605 ★★ 加**读回定义**的硬验证（核 `Height`/`Pitch`/`Revolution`）
- [x] T-3606 ⇒ **13/13** ⇒ 升 `verified`（能力 + 源码来源块 + 测试）
  `→ 验收:` `python -m pytest tests/test_sw_helix_contract.py -q`（9 passed）
- [x] T-3607 重生成 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 040 · Converge

**Converged**: 2026-10-01（轮 121）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-3601 如实报 9/10 | ✅ 改的是**代码**，不是判据 |
| SC-3602 抓到并修掉缺陷 | ✅ `FirstFeature` → `GetLastFeatureAdded` |
| SC-3603 名字对得上（测试钉住） | ✅ |
| SC-3604 **读回定义** | ✅ `Height=0.05` / `Pitch=0.01` / `Revolution=5.0` |
| SC-3605 升 `verified` + 禁止降级 | ✅ 测试钉住 |
| SC-3606 子特征风险写进 limitations | ✅ |
| SC-3607 门禁 + 回归 | ✅ `release_check` exit 0 · **1108 passed** |

**能力分布**：**`verified 29 → 30`** · `stitched 6 → 5`（36 条不变）

## 二、★★ 连着两轮的冒烟，各抓到一处我自己写的缺陷 —— 但**性质不同**
```
039（GTol）：API **到不了** —— 不是我的错，是那个路径在本机不通
040（螺旋线）：**我的实现写错了** —— 返回值错，而它"看着像对的"
```
★ `040` 这处更危险：**它不抛异常**。
若我不做冒烟，这个函数会一直"返回一个名字"，
**用它的人会以为拿到了新建特征的名字**。

## 三、★★ 什么算硬证据 —— 本项目已经攒出**同一档**的三个实例
```
035  方程式：写进去的 == 读回来的（SMOKE_B = 2）
036  草图：  画了 2 样东西 ⇒ segments == 2
040  螺旋线：传 50mm/10mm/5圈 ⇒ 读回 0.05 米/0.01 米/5.0
```
★★ **共同点：空操作满足不了它们。** 而「没抛异常」空操作能满足 ⇒ **不算证据**。

## 四、★ 三处「失败信号长得像正常值」已经攒成一个族
```
028  方程式的 `-1`：既是"追加到末尾"的入参，又是"失败"的返回
034  `SketchUseEdge3` 返回 `False`：假值，最容易被 `if not got: pass` 吞掉
040  `FirstFeature` 返回 `'收藏'`：**一个看着完全合理的字符串**
```
⇒ ★ **这一类错比"抛异常"危险得多**，因为**它们不进日志、不进门禁、不引人注意**。

## 五、未查证
* 只验了 `height_mm` / `pitch_mm` / `revolution`；
  **其余 6 个参数**与 `helix_def` 的**其余三种取值**未测；
* ★ **`TaperAngle` 的单位仍未验证**（`Pitch` 的推断本轮已被证实）；
* 只覆盖**定距**；变距**未实现**；
* `GetLastFeatureAdded` **可能返回子特征**这一点未穷尽验证。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
