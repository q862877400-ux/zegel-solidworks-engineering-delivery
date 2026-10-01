# 051 · 补 `ellipse` —— 顺带量准一件更大的事：**长度单位是毫米，而 docstring 写的是米**

**Status**: Implemented（轮 132）

## 一、挑 `ellipse` 的理由
它在「真缺」档里，而且**有现成的验证手段**：轮 117 已验过 `sw_sketch.get_ellipses`
（当时返回 **0** —— 因为没画椭圆）⇒ ★ 本轮可以**造一个椭圆再读回来**。

## 二、★ 走的是**现行入口**（官方有**两级废弃链**）
```
IModelDoc2.CreateEllipse(Object,Object,Object)
  ⇒ Obsolete. Superseded by IModelDoc2::CreateEllipse2.
IModelDoc2.CreateEllipse2(Double ×9)
  ⇒ Obsolete. Superseded by ISketchManager::CreateEllipse.
⇒ 现行 = ISketchManager.CreateEllipse(XC,YC,Zc, XMajor,YMajor,ZMajor, XMinor,YMinor,ZMinor)
  （**9 个 double**，返回 `SketchSegment`；两源一致）
```

## 三、★★ 顺带量准的一件更大的事
```
冒烟第 ① 段：`sketch_circle(model, 0, 0, 25)`（**未做任何换算**）+ 拉伸 10
           ⇒ `get_bounding_box` 得跨度 **[10, 50, 50]`（**毫米**）
⇒ ★ **传进去的就是毫米** —— 而 `sw_part` 的 docstring 有 **14 处**写「单位: 米」！
```
⚠ **docstring 与实际不符**，而且**没有任何门禁会检查它** ——
因为 `sw_part` 是**脚本层**，不受工具命名规则（`_mm` 后缀那条）约束。
⇒ 已**逐条校正为毫米**，并在模块头写明这是**实测校正**（已知事实 73）。
★ 与已知事实 71（`GetBodyBox` 返回毫米）是**同一台机器上互相印证**的两条。

## 四、真机冒烟 **11/11**
```
✓ 新建临时零件 · start_sketch
✓ ★★ 半径 25 的圆 ⇒ 边界框跨度 50 ⇒ 输入单位是毫米     实测 size=[10.0, 50.0, 50.0]
✓ （新件）start_sketch
✓ ★ sketch_ellipse（长半轴 40 / 短半轴 20）            返回 CDispatch
✓ ★★ 往返：get_ellipses 读回**至少 1 个**椭圆          读回 22 个（轮 117 时是 0）
✓ end_sketch ×2 · 两个临时件都已关且不保存 · ★ 无残留模态框
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-4701 | ★★ 走**现行入口**，不走那两级已废弃的路（测试查**调用形态**）|
| SC-4702 | ★ 签名 9 个 double；返回 `None` 时**抛** |
| SC-4703 | ★★ **往返一致**：造椭圆 ⇒ `get_ellipses` 读得回来 |
| SC-4704 | ★★ **量准单位**（圆半径 25 ⇒ 跨度 50）并**逐条校正 14 处 docstring** |
| SC-4705 | ★ 模块头写明单位，且**测试钉住**不许再出现裸的「（单位: 米）」|
| SC-4706 | 已知事实 73 入库 |
| SC-4707 | 门禁 + 回归不退化（回归 **1166 passed**）|

## 六、⚠ 本轮踩的两处（都是"覆盖范围"，第三次同族）
```
① 改了 14 行 docstring ⇒ `check_provenance` 报它们"未被来源块覆盖"
   （此前它们**没被改过**，所以一直没暴露）
② 补了一块之后仍报 2 行 —— 因为**中间还有两块**（L786 / L879，指向 `_raw\reflect_sldworks\…`）
   我的块被截在 L785，那 2 行落在**缝里**
⇒ 两次都要**先看块的实际区间**（`_source_blocks` 打印出来），而不是猜
```
★ 与轮 124/125（`覆盖: 后续同级定义` 的语义）、轮 126（插在块上方）**同族**。

## ⚠ 明确记下的限度
* 椭圆的**长短半轴数值未逐一核**（只证建成 + 读得回来）；
* `sketch_circle` 一类**改动后未重跑**既有冒烟；
* `d1_*` 方向向量的**归一化与否未测**（已在 docstring 标注）。
