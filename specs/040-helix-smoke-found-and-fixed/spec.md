# 040 · 螺旋线的真机冒烟 —— **抓到缺陷、修好、并升为 `verified`**

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
