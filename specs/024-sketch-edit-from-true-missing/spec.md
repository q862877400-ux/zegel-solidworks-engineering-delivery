# 024 · 从「真缺」再补两条：草图倒角 / 草图镜像

**Status**: Implemented（轮 105）

## 背景
`023` 从「真缺」档补了螺旋线。本轮接着补 **`sketch_chamfer`** 与 **`sketch_mirror`**
（`022` 的核样确认这两条确实没有实现）。

## ★★ 本轮最重要的发现：**枚举值两源冲突**（铁律 4 的活例）
```
swSketchChamferType_e
  成员                              C:\swapi 的 md    出厂反射（**采用**）
  swSketchChamfer_DistanceAngle          0               0
  swSketchChamfer_DistanceDistance     **-1**          **1**      ← 冲突
  swSketchChamfer_DistanceEqual          2               2
```
★ **铁律 4：冲突以出厂类型库为准** ⇒ 实现取 **1**。
⚠ 此前铁律 4 更像一条**预防性条款**；本轮它**第一次真正裁决了一次冲突**。
★ 契约测试把 **1** 独立抄一份 ⇒ 任何人改成 -1 都会红。

## 另一处：**走非废弃入口**
官方文档明写 `IModelDoc2.SketchChamfer` 是 **Obsolete**，被 `ISketchManager::CreateChamfer` 取代
⇒ 本模块用**后继**（`SketchSegment CreateChamfer(Int32, Double, Double)`，两源签名一致）。

## 判据
| ID | 判据 |
|---|---|
| SC-2001 | ★ 枚举**取出厂反射**（`distance_distance = 1`），不是 md 的 -1 |
| SC-2002 | ★ 走**非废弃**入口（`CreateChamfer`），来源块记下原因 |
| SC-2003 | 官方参数顺序与个数照抄（倒角 3 参；镜像**0 参**）|
| SC-2004 | 长度在**边界**换算（2.5 mm ⇒ 0.0025 m）|
| SC-2005 | 前置条件不满足时抛**带原因**的 `RuntimeError`（两条实体 / 草图编辑态 + 标记 1/2）|
| SC-2006 | 来源块写明等级 **`stitched`** 且**无本机运行证据** |
| SC-2007 | `capabilities.yaml` 新增 `sketch_edit_ops`（`stitched`），32 → **33** 条 |
| SC-2008 | 门禁 + 回归不退化（回归 **1064 passed**）|

## ⚠ 明确记下的限度
* **等级 `stitched`** —— 只有静态证据，**本机从未做过草图倒角/镜像**；
* **前置条件不代选**：倒角要两条实体、镜像要按官方标记（线段 1 / 中心线 2）选中；
* `CreateChamfer` 第三参 `AngleORdist` 的**单位随类型变，官方未写** ⇒ **不做换算**、原样传；
* 本轮**主动不做真机测试**（轮 98 的模态框教训）。
