# 草图完全定义 · **官方依据汇编**（★ 第 0 步的产物）

**用途**：★ 这是 `sketch-definition-protocol.md` 的**依据层** ——
本文件只收**官方原文**与**本仓真机读数**，★ 不掺我的推断。
**扫过的范围**：`AI Solidworks/官方文档/SWhelp/` **29697 个文件** ⇒
★ 命中「完全定义/草图关系/约束」**49 个**。

---

## §1 ★★ 官方**有**「自动完全定义」的 API —— 这改变主路

### `ISketchManager::FullyDefineSketch`（**10 参**）

**官方签名逐字**（`sldworksapivb6/SldWorks~SketchManager~FullyDefineSketch.html`）：

```vb
Public Function FullyDefineSketch( _
    ByVal EntitiesToFullyDefine As Boolean, _
    ByVal UseRelations As Boolean, _
    ByVal RelationsToApply As Long, _
    ByVal UseDimensions As Boolean, _
    ByVal HorizontalDimScheme As Long, _
    ByVal HorizontalDatumDisp As Object, _
    ByVal VerticalDimScheme As Long, _
    ByVal VerticalDatumDisp As Object, _
    ByVal HorizontalDimPlacement As Long, _
    ByVal VerticalDimPlacement As Long _
) As Long
```

**★ 官方示例的调用序**（`Fully_Define_Underdefined_Sketch_Example_VB.htm` 逐字摘）：

```vb
lMarkHorizontal = 2
lMarkVertical = 4
' 找第一个 ProfileFeature（草图）并选中
bValue = swFeature.Select2(False, 0)
swSketchManager.InsertSketch False
' ★★ 关键：把 vertical 与 horizontal 的 mark **或**起来选原点
'    ★ 官方注释逐字：「You cannot select the same point twice with different marks」
bValue = swModelExtension.SelectByID2("Point1@Origin", "EXTSKETCHPOINT", _
                                      0, 0, 0, False, lMarkHorizontal Or lMarkVertical, Nothing, 0)
lStatus = swSketchManager.FullyDefineSketch( _
    True, True, _
    swSketchFullyDefineRelationType_Vertical Or swSketchFullyDefineRelationType_Horizontal, _
    True, 1, Nothing, 1, Nothing, 1, 1)
swSketchManager.InsertSketch True
```

**★★ 本仓已有包装**：`scripts/sw_sketch_dimensions.py::fully_define_sketch`
（★ 且**已按 pywin32 的实际要求**把两个 `DatumDisp` 落成**空 Dispatch**）。

---

## §2 ★★ 本仓的真机读数（`sw_part.py` 的来源块，逐字）

| 形态 | 结果 |
|---|---|
| `FullyDefineSketch(…, **None**, …, **None**, …)` | ★★ **`类型不匹配`（位置 6）** ✗ |
| 同上但两个 `DatumDisp` 传**空 Dispatch** | ★★★ **回 `4` · 零错误** ✓ |
| ★ **官方调用序**（选 `Point1@Origin` + mark 6） | ★★★ **回 `4` · 零错误** ✓ |
| 不选原点（对照） | ★★ **也回 `4`** ⇒ ★ **那个返回码分不出"选了没选"** |

**⇒ 三条结论**：
1. ★ 官方说的 "if Nothing or null" 在 pywin32 上要落成**空 `Dispatch`**
   （★ `VARIANT(VT_DISPATCH, None)` —— ★ 与**事实 12**同族）
2. ★★ **返回码 `4` 不可解释** —— ★ 官方 `## Returns` 写的是「**Not currently defined**」，
   ★ 且实测**分不出选了没选** ⇒ ★ **不能拿 `4` 当"成功"**
3. ★★★ 当时的处置是「**暂不换**」，理由是**判据立不起来**：
   ★ `GetDimensionCount` 与 `GetSketchDimensions` **两种读法都量不到**（回 `-1`）

**★★★★ 那条记录里已写好的可复用判据（逐字）**：

> **"后继能调"与"后继能替"是两件事** ——
> 前者只要**不报错**、后者要**一个能证明产出存在的读数**。

---

## §3 `swSketchFullyDefineRelationType_e`（**Bitmask**，官方全表）

**逐字**（`swconst/…swSketchFullyDefineRelationType_e.html`）：

| 成员 | 值 |
|---|---|
| `Equal` | 1 (0x1) |
| `Horizontal` | 2 (0x2) |
| `Vertical` | 4 (0x4) |
| `Tangent` | 8 (0x8) |
| `Perpendicular` | 16 (0x10) |
| `Colinear` | 32 (0x20) |
| `Concentric` | 64 (0x40) |
| `Parallel` | 128 (0x80) |
| `Midpoint` | 256 (0x100) |
| `Coincident` | 512 (0x200) |

**★★ 这就是 `RelationsToApply` 的取值表** ——
★ 而本仓的 `fully_define_sketch` docstring 写着「**取值表两套离线源都没查到**」。
**⇒ ★ 那句话现在是错的**（★ 取值表就在这个文件里）—— ★ **要改**。

---

## §4 `swConstraintType_e`（★ 手加关系用的**全表 24 个**）

**逐字**（`Get_All_Sketch_Relations_and_Their_Types_Example_VB.htm`）：

| 值 | 成员 | | 值 | 成员 |
|---|---|---|---|---|
| 0 | `INVALIDCTYPE` | | 12 | `ATMIDDLE` |
| 1 | `DISTANCE` | | 13 | `ATINTERSECT` |
| 2 | `ANGLE` | | 14 | `SAMELENGTH` |
| 3 | `RADIUS` | | 15 | `DIAMETER` |
| 4 | `HORIZONTAL` | | 16 | `OFFSETEDGE` |
| 5 | `VERTICAL` | | 17 | `FIXED` |
| 6 | `TANGENT` | | 18 | `ARCANG90` |
| 7 | `PARALLEL` | | 19 | `ARCANG180` |
| 8 | `PERPENDICULAR` | | 20 | `ARCANG270` |
| 9 | `COINCIDENT` | | 21 | `ARCANGTOP` |
| 10 | `CONCENTRIC` | | 22 | `ARCANGBOTTOM` |
| 11 | `SYMMETRIC` | | 23 | `ARCANGLEFT` |

**★★ 本仓的 `sw_sketch_relations.RELATION_TYPES` 只有 9 个** ⇒
★ 缺 `DISTANCE` / `ANGLE` / `RADIUS` / `DIAMETER` / `ATINTERSECT` /
`OFFSETEDGE` / `ARCANG*`（★ 8 个 ARCANG 变体）。
**★ 而这些恰恰是"把圆弧定死"用的** —— ★ 我的生成器**生成不出来**。

---

## §5 ★ `GetConstrainedStatus` 的取值（★ 官方**没给**）

- ★ 官方 `ISketch::GetConstrainedStatus()` 页**没有 `## Remarks`、也没有取值表**
- ★★ **本仓真机两轮**：欠定义矩形回 **2** · 四段全加 `sgFIXED` 后回 **3**
- ⇒ ★ **只实测了 2 与 3** ⇒ ★ 不把它解释成"欠定义/完全定义"（★ 铁律 5）

**★ 而官方帮助页（非 API）给了颜色口径**（★ 见 `sketch-definition-protocol.md` §1）：
★ 蓝 = 欠定义 · 黑 = 完全定义 · 红 = 过定义。

---

## §6 ★★ 这次查证的**净收获**

| # | 收获 | 影响 |
|---|---|---|
| **1** | ★★ 官方**有** `FullyDefineSketch` ⇒ **主路该换成它** | ★ 我的生成器**降为备选**（★ 用于"预先规划"） |
| **2** | ★ `RelationsToApply` 的**取值表找到了**（10 个 bitmask） | ★ 改掉「查不到」那句话 |
| **3** | ★ `swConstraintType_e` **全表 24 个**（本仓只有 9 个） | ★ 补 15 个（★ 含 8 个 ARCANG） |
| **4** | ★★ 「后继能调 ≠ 后继能替」 | ★ 换主路**要等一个能证明产出的读数** |
| **5** | ★ 返回码 `4` **不可解释** | ★ 判据**不能**落在它上面 |

---

## §7 ★ 还缺什么（★ 这才是真缺口）

| # | 缺口 | 谁能补 |
|---|---|---|
| **1** | ★★ **"尺寸真的建出来了"的可核读数** | ★ 我要再找（★ `GetDimensionCount` 两种读法都回 -1） |
| **2** | ★ `HorizontalDimScheme` / `*DimPlacement` 的**取值表** | ★ 官方源里**仍没找到**（★ 只找到 `RelationsToApply`） |
| **3** | ★★ **"该不该这么画"**（★ 工程惯例：什么时候用旋转代替拉伸、倒角该多大） | ★★ **官方文档不给** —— ★ **这正是业主视频能补的** |

**★★ 第 3 条是关键**：★ 官方文档给的是「**有什么 API**」，
★ **不给**「**一个定位销该先画圆还是先画旋转**」这种**做法判断**。
⇒ ★ 业主的「扒教学视频」思路**填的正是这个洞**。
