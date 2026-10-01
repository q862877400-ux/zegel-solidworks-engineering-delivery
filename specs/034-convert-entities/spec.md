# 034 · 从「真缺」再补一条：转换实体引用

**Status**: Implemented（轮 115）

## 背景
`023`/`024`/`028` 已从「真缺」档补了螺旋线 / 草图倒角镜像 / 方程式。本轮接着补
**`convert_entities`**（`022` 的核样确认它确实没有实现）。
⚠ 它**与已有的 `sw_sketch_edit.py` 同类**（都是草图编辑）⇒ **并进那个模块**，
**不新开文件**（"不重造"）。

## 选哪个入口（**先查废弃，再选**）
```
IModelDoc2.SketchUseEdge2(Boolean)      ⇒ 官方 md 明写 **Obsolete**
                                          （Superseded by ISketchManager::SketchUseEdge）
ISketchManager.ConvertEntities()        ⇒ **零参，未废弃**，也能用
ISketchManager.SketchUseEdge3(Boolean Chain, Boolean InnerLoops)  ⇒ **未废弃**
```
⇒ 取 **`SketchUseEdge3`**：两个参数**都有官方说明**（`Chain` 连整条链 / `InnerLoops` 带内环），
语义比零参的 `ConvertEntities()` 明确。⚠ 这一点**已写进来源块与 capability 的 limitations**。

## 判据
| ID | 判据 |
|---|---|
| SC-3001 | ★ 走 **`SketchUseEdge3`**，**不走**已废弃的 `SketchUseEdge2`（测试断言实现段里不出现后者）|
| SC-3002 | 参数按官方顺序 `(Chain, InnerLoops)`；默认 `True` / `False` |
| SC-3003 | ★ 官方返回 `False` ⇒ **抛带原因的错**（`False` 是假值，很容易被吞掉）|
| SC-3004 | 拿不到 `SketchManager` 时抛带原因的错 |
| SC-3005 | 扩 `sketch_edit_ops` 能力条目（34 条不变，**是扩不是新增**）|
| SC-3006 | 门禁 + 回归不退化（回归 **1091 passed**）|

## ⚠ 明确记下的限度
* **等级仍是 `stitched`** —— 只有静态证据，**本机从未做过转换实体引用**；
* **前置条件不代选**：官方写明投影的是「**selected** edges/loops/faces/curves/external contours」
  ⇒ 调用方要先选中并进入草图；
* 另有零参的 `ConvertEntities()`（未废弃）**未采用** —— 不是不能用，是语义更含糊；
* 本轮**主动不做真机测试**（轮 98 的模态框教训）。
