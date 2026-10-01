# 041 · 草图编辑的真机冒烟 —— **倒角到不了，而且是架构性限制**

**Status**: Implemented（轮 122）

## 一、为什么挑它
`024`（轮 105）补了草图倒角/镜像，**只有静态证据**。
★ 而且它的前置最具体：官方写「creates a chamfer **between two selected sketch entities**」
⇒ 正好能验「**选中两条实体**」这个前置到底成不成立。

## 二、真机冒烟：**8/10** —— 前置成立，倒角不通
```
✓ 新建临时零件 · start_sketch · 画直线 1 · 画直线 2
✓ 取到草图线段（2 条）
✓ ★ 同时选中**两条**草图实体                    选区计数 = **2**   ← **前置成立**
✗ ★ create_sketch_chamfer(distance=5mm)      RuntimeError: CreateChamfer 返回 None
✗ ★★ 倒角后线段数变了                           倒角前 2 → 倒角后 2
✓ end_sketch · 关件不保存 · ★ 无残留模态框
```

## 三、★ 定向探针量到的：**不是「参数没调对」，是架构限制**
```
新零件 → 进草图 → 两条相接直线 → 确认选区计数 = 2 → 调 CreateChamfer

type=2(distance_equal) dist=0.005 angle=0.0
  ⇒ **pywintypes.com_error: (-2147417851, '服务器出现意外情况')**
```
★ `0x80010105`（`-2147417851`）**正是已知事实 47（`ISketchedBendFeatureData.AccessSelections`）
与事实 28（`CreateBsplineSurface`）那个错误码** ——
即「**pywin32 迟到绑定到不了需要真实指针的接口**」这一族。
⚠ **按事实 53 停手**，不再试别的类型/参数组合（`distance_angle` / `distance_distance` 没意义了）。

## 四、处置：**如实分裂声明**
```
convert_entities       ⚠ 未实测（需要选中的边/环/面，本轮未造出前置）
create_sketch_chamfer  ❌ **到不了**（0x80010105）—— 保留作可复算的证据
sketch_mirror          ⚠ 未实测（需要中心线 mark=2 + 线段 mark=1 的选中标记）
```
能力的等级**仍是 `stitched`**（三条里只有前置被验过），
⚠ 但 **`limitations` 里逐条写清**哪条到不了、哪条没测。
**已知事实 67** 入库。

## 五、判据
| ID | 判据 |
|---|---|
| SC-3701 | 真机冒烟跑通并**如实报告 8/10**（不改判据去迎合）|
| SC-3702 | ★ **「同时选中两条」这个前置的成立被验证**（选区计数 = 2）|
| SC-3703 | ★★ 量到的是 **`0x80010105`** —— 指出它**与事实 47 / 28 同码** |
| SC-3704 | ★ 源码里**明写** `create_sketch_chamfer` 当前不可用 + 那三次失败形态 |
| SC-3705 | ★ 来源块**分开声明**三条的实测状态（一条到不了、两条未测）|
| SC-3706 | 能力条目 `evidence` 写 **8/10**、`limitations` 逐条写清 |
| SC-3707 | 已知事实 67 入库 |
| SC-3708 | 门禁 + 回归不退化（回归 **1108 passed**）|

## ⚠ 明确记下的限度
* `convert_entities` / `sketch_mirror` **未实测** —— **不得当成"验过了"**；
* 只证了「**在这台机器 + 这个后端**到不了」——
  ⚠ **未查证**换后端（`comtypes` / 进程内 C++）能否走通；
* ⚠ 枚举 `swSketchChamferType_e` **两源冲突**（`distance_distance`: 反射 1 vs md −1）
  ⇒ 按铁律 4 取了反射的 **1**；**本轮没能用真机裁决这一处**（因为在选型之前就报错了）。
