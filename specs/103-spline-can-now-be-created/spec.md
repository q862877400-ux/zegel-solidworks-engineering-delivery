# 103 · 样条**从「建不出来」变成「能建」** —— 修实参形态 + 成员名（而「建不出来」是**误判**）

**Status**: Implemented（轮 183）

## 一、起因
轮 141/182 记着「样条建不出来（`CreateSpline2` 返回 None）」⇒ ★ 它**挡住了 `composite_curve`**。

## 二、★★★ 读官方 Remarks ⇒ 发现**实参形态**要求
```
`CreateSpline` / `CreateSpline2` 的 Remarks：
  "The PointData array is a set of, at least, **two X, Y, Z values**.
   X 起点 = PointData[0]，Y = [1]，Z = [2]；下一点 X = [3] …"
⇒ ★ 即一个**扁平的一维数组** `[x0,y0,z0, x1,y1,z1, …]`，⚠ 而仓库传的是 **list of tuples**。
```

## 三、★★★ 真机逐形态判别（`tools/probe_spline_forms.py`，**每次回读草图段数**）
```
① 扁平 list                   ⇒ 段数 0 → 0（没变）· 返回 None
② 扁平 tuple                  ⇒ 段数 0 → 0（没变）· 返回 None
③ **VARIANT(VT_ARRAY|VT_R8)** ⇒ 段数 **0 → 1（变了 ✚）**   ★★★ **成了**
④ list of tuples（原写法）     ⇒ 段数 0 → 0（没变）· 返回 None
⇒ ★★ 与**事实 167**（`AddRelation` 必须包 `VARIANT(VT_ARRAY|VT_DISPATCH)`）**完全同一族**：
  **数组实参必须包 VARIANT**，且**官方 Remarks 没说** ⇒ 只能实测出来。
```

## 四、⚠⚠ 修的过程中查出**第二处**
```
`getattr(sketch_manager, "CreateSpline")` ⇒ **None**
  ⇒ 在 `get_com_member` 里报 `TypeError: 'NoneType' object is not callable`
★ 而**官方 md 明写**：`CreateSpline` 是 "**Obsolete. Superseded by ISketchManager::CreateSpline2**"
⇒ ★★ **必须走 `CreateSpline2`**；
⚠ 那个 `TypeError` **指不出真因**（又是「报错看不出病因」那一族）。
```

## 五、修后
```
create_spline 现在：**自己摊平**（两种写法都收）+ 包 `VARIANT(VT_ARRAY|VT_R8)` + **走 `CreateSpline2`**
★ 真机：点对 / 扁平 / `simulate=True` ⇒ 段数**都 0 → 1** ✓
```

## 六、★★★ 意义
```
这是一个**「挡着不止一个能力」的上游** —— 它一修，
`composite_curve` 的**前置从「不可达」变成「可达」**
（⚠ 本轮**未**重跑它 —— 留给下轮，且要看它现在是否真的能建成）。
```

## 七、判据
| ID | 判据 |
|---|---|
| SC-10301 | ★★★ **读官方 Remarks** 得到实参形态（扁平 X,Y,Z 序列）|
| SC-10302 | ★★★ **逐形态真机判别**（每次回读段数）⇒ `VARIANT(VT_ARRAY\|VT_R8)` 唯一可行 |
| SC-10303 | ★★ **与事实 167 同族**（数组实参必须包 VARIANT）|
| SC-10304 | ★★ 查出第二处：`CreateSpline` 已 Obsolete ⇒ 走 `CreateSpline2` |
| SC-10305 | ★ 修后**三种写法全部成功**（段数 0 → 1）|
| SC-10306 | 门禁 + 回归不退化 |

## ⚠ 明确记下的限度
* ⚠ **`composite_curve` 本轮未重跑** —— 它的前置现在**可达**，但它**是否真能建成** **未验**；
* ⚠ 官方 Remarks **没说「要包 VARIANT」** ⇒ 这条知识**只能来自实测**（不可从文档推出）；
* ⚠ 只验了「段数变了」⇒ **不证样条的几何形状**；
* ⚠ `CreateSplineByEqnParams` 族（B 曲线：控制点 + 节点向量）**未试**。
