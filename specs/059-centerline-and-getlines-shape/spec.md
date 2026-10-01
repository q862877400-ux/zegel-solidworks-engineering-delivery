# 059 · 补 `centerline` —— 顺带查清 `get_lines` **返回的根本不是线对象**

**Status**: Implemented（轮 140）

## 一、补 `centerline`（真缺档）
★ 走**现行入口** `ISketchManager.CreateCenterLine(6 doubles)` → `SketchSegment` ——
官方有**两级废弃链**：`IModelDoc2.CreateCenterLine(Object,Object)` ⇒（Superseded）⇒
`CreateCenterLineVB`（**Void** 返回的 VB 变体）⇒ **`ISketchManager.CreateCenterLine`**。
★ 官方 Remarks 另给一条路（`CreateLine` + `ConstructionGeometry`）——**本函数不走那条**。

## 二、★★ 冒烟 8/8 里冒出来的一件事
```
✓ sketch_centerline 建成（返回 CDispatch）
✓ ★★ 往返 A：`get_sketch_segments` 读回 **1 段**  ← 对
✓ ★  往返 B：`get_lines` 读回 **12 条**            ← ⚠ 只画了 1 条！
✓ ★★ **再测单位**：半径 25 的圆 ⇒ 边界框 50 ⇒ **毫米**（官方文档的「in meters」是错的）
```
⚠ **12 对 1** —— 数字对不上 ⇒ **要去看**（不是"算了"）。

## 三、★★★ 查清了：`get_lines` 返回的是**数值数组**，不是**线对象列表**
`tools/probe_getlines_count.py`（真机，画 N 条直线）：
| 画的条数 | `get_sketch_segments` | `get_lines` |
|---|---|---|
| 1 | 1 | **12** |
| 2 | 2 | **24** |
| 3 | 3 | **36** |

⇒ **完全线性：每条直线占 12 个 `float`**，且 `get_lines(...)[0]` 的类型是 **`float`**
（不是 `Dispatch`）⇒ **不能**当线对象用（没有 `.X` / `.GetStartPoint2`）。
⚠ **官方文档没写这个返回结构。**

### ⚠⚠ 而它为什么一直没被发现
```
`tools/verify_sketch_getters_smoke.py`（轮 117）的判据是「**非空**」⇒ **12 对 1 也照样绿**
⇒ ★ **判据太弱 ⇒ 真问题藏在绿里。**
```
⇒ **这正是本会话反复出现的那一类**：**"绿"不等于"对"**，判据的**强度**决定它能发现什么。

## 四、处置（四处）
1. **改写** `sw_sketch.get_lines` 的 docstring —— 写明「**数值数组**」+「每条 **12** 个 `float`」
   + 给出「**要几条线**用 `get_sketch_segments`」的替代；
2. **冒烟加定量判据**（从"非空"升级到"**= 条数 × 12**"）⇒ **18/18**；
3. **契约测试加 3 条**（pytest 风格，与本文件一致）：docstring 写明形状 · 仍是后继 `GetLines2` ·
   ★★ **仓库里不许有人把 `get_lines` 的结果当对象用**（正向判据：元素是 `float`）；
4. 能力条目 + 已知事实 81。

## 五、判据
| ID | 判据 |
|---|---|
| SC-5501 | ★★ `sketch_centerline` 走**现行入口**（不走两级废弃链）|
| SC-5502 | ★ 真机冒烟 **8/8**，含**往返**与**无残留模态框** |
| SC-5503 | ★★ **再测单位**（半径 25 ⇒ 边界框 50 ⇒ 毫米），印证官方文档那句「in meters」是错的 |
| SC-5504 | ★★★ **查清 `get_lines` 的返回形状**（12/24/36 三点线性）|
| SC-5505 | ★★ 指出**判据太弱**（「非空」）是这个语义长期没被写下的原因 |
| SC-5506 | ★ 处置四处（docstring / 冒烟定量 / 契约 3 条 / 事实 81）|
| SC-5507 | ★ 门禁 + 回归不退化（回归 **1196 passed**）|

## 六、★ 门禁尽职的一个实例
```
加完 `sketch_centerline` 后 `release_check` **exit=1**：
  [FAIL] 地图与来源同步
     常见原因①：**增删了 scripts/sw_*.py 里的公开函数** ⇒ 地图的「本仓库能力面」列计数变了
⇒ ★★ 门禁**自己把原因和命令写出来了**（跑 `tools/build_union_map.py` 再提交）
⇒ 跑完 1 行改动 ⇒ `release_check exit=0`。
```
★ 这与事实 55 那次（`sync_bundled_skill.py` 的报错**从"看不出怎么办"改成"给命令"**）同一路数：
**好门禁的报错要能直接执行。**

## ⚠ 明确记下的限度
* 那 12 个 `float` 的**具体含义**（哪几个是哪个端点、是否含额外字段）**未逐位核**；
* 中心线的**构造几何标记**是否自动置上**未测**；
* `get_arcs` / `get_ellipses` 是否也是「数值数组」**未测**（⚠ 同样的疑问，**同样的强判据**才能证）。
