# vd50-B · sketch · 「置信度＝高」条目双段原文复核

**范围**：`recon/audit-vs-official/` 下与 **sketch** 有关的三个文件里，**置信度标「高」**的条目 ——
`audit-07-sketch-A.md`（第 1–6 条全高）· `audit-07-sketch-B.md`（第 1、2、4 条为高，第 3、5 条为「中」**未核**）· `audit-07-sketch-C.md`（第 1–5 条全高）。
**只读核验**（未改仓内任何文件）；本文件是唯一写入。
**核了 14 处，对不上 1 处。**

每条两问：**①「官方的原文」是否真的存在于 `C:\swapi\`**；**②「我们的原文」是否真的存在于 `D:\AI\SW\`**。两段均逐字给出，可直接 grep。

---

## 总表

| 条目 | 文件 | 官方原文在不在 | 我们的原文在不在 | 判定 |
|---|---|---|---|---|
| A-1 | `scripts/sw_sketch.py` | ✅ 在 | ✅ 在 | **成立** |
| A-2 | `scripts/sw_sketch_edit_ops.py` | ✅ 在 | ✅ 在 | **成立** |
| A-3 | `scripts/sw_sketch_edit_ops.py` | ✅ 在 | ✅ 在 | **成立** |
| A-4 | `scripts/sw_sketch_edit_ops.py` | ✅ 在 | ✅ 在 | **成立** |
| A-5 | `scripts/sw_sketch_edit_ops.py` | ✅ 在 | ✅ 在 | **成立** |
| A-6 / C-3 | `scripts/sw_sketch_modify_ops.py` | ✅ 在 | ✅ 在 | **成立**（同一条，两文件各记一次） |
| B-1 | `scripts/sw_sketch_edit_ops.py` | ✅ 在 | ✅ 在 | **成立** |
| B-2 | `scripts/sw_sketch_edit_ops.py` | ✅ 在 | ✅ 在 | **成立** |
| B-4 | `scripts/sw_sketch.py` | ✅ 在 | ✅ 在 | **成立** |
| C-1 | `scripts/sw_sketch_modify_ops.py` | ✅ 在 | ❌ **不在** | **不成立** |
| C-2 | `scripts/sw_sketch_edit.py` | ✅ 在 | ✅ 在 | **成立** |
| C-4 | `scripts/sw_sketch_edit.py` | ✅ 在 | ✅ 在 | **成立** |
| C-5 | `scripts/sw_sketch.py` | ✅ 在 | ✅ 在 | **成立** |

> A-6 与 C-3 是同一条分歧（`SketchModifyFlip` 的 AxisFlag 取值表）在两个核对文件里的重复记录，合并核一次，计数仍按两条记。

---

## A-1 · `GetContourEdges` 的形参被当成「轮廓对象」传

**判定：成立**（官方形参表与我们的实参类型确不一致）

**仓内那一段** —— `scripts/sw_sketch.py`，`get_contour_edges`：
```python
    """取某个轮廓的边。⚠ 官方是 **1 参**（Contour 对象）。"""
    ...
    return as_sequence(get_com_member(sketch, "GetContourEdges", contour))
```
同文件来源块那一行：
```python
#     Object GetContourEdges(Object Contour)                    ← **1 参**
```

**目标那一段** —— `C:\swapi\types\ISketch\GetContourEdges.md`：
> **Signature**: `System.object GetContourEdges( System.object Xform )`
> - **Xform**: Array of size 16 doubles representing the transform

**一句话依据**：官方形参名是 `Xform` 且明写「16 个 double 的变换数组」，仓内三段原文（docstring / 来源块 / 实参）逐字都在、且都按「轮廓对象」写 ⇒ 条目说的分歧真实存在。

---

## A-2 · `CreateFillet` 的 `Radius` 官方写明 **meters**，我们原样传 mm

**判定：成立**

**仓内那一段** —— `scripts/sw_sketch_edit_ops.py`，`sketch_fillet`：
```python
    seg = get_com_member(get_com_member(model, "SketchManager"), "CreateFillet",
                         float(radius_mm), int(constrained_corners))
```
同文件模块头：
```python
#  ⚠ **单位**：长度**毫米**、角度**度** —— 换算在工具层边界做一次（规则 2）。
```
（对照项：同族另一处 `scripts/sw_sketch_edit.py` 的 `CreateChamfer` 确实做了换算 —— `int(chamfer_type), mm(float(distance_mm)), float(angle_or_distance)`）

**目标那一段** —— `C:\swapi\types\ISketchManager\CreateFillet.md`：
> - **Radius**: Radius of the fillet in meters

`C:\swapi\examples\Edit_Radial_Dimension_Example_CSharp.md`：
> swSketchSegment = (SketchSegment)swSketchManager.CreateFillet(0.01, (int)swConstrainedCornerAction_e.swConstrainedCornerDeleteGeometry);

**一句话依据**：官方形参表明写 `in meters`、官方配方实参传 `0.01`（=10 mm），而仓内 `float(radius_mm)` 无 `/1000` 直传 ⇒ 量纲分歧成立。

---

## A-3 · `SketchOffset2` 首个实参 `Offset` 按官方配方应为米，我们原样传 mm

**判定：成立**（★ 量纲依据来自**官方配方实参**，官方形参表本身未写量纲 —— 与核对表的说明一致）

**仓内那一段** —— `scripts/sw_sketch_edit_ops.py`，`sketch_offset`：
```python
    return get_com_member(get_com_member(model, "SketchManager"), "SketchOffset2",
                          float(offset_mm), bool(both_directions), bool(chain),
                          OFFSET_CAPS[cap_ends], OFFSET_CONSTRUCTION[make_construction],
                          bool(add_dimensions))
```

**目标那一段** —— `C:\swapi\types\ISketchManager\SketchOffset2.md`（6 参、顺序与仓内逐位一致，形参表**未写量纲**）：
> **Signature**: `System.bool SketchOffset2( System.double Offset, System.bool BothDirections, System.bool Chain, System.int CapEnds, System.int MakeConstruction, System.bool AddDimensions )`

`C:\swapi\examples\Sketch_Offset_Example_VB.md`：
> status = swSketchManager.SketchOffset2(0.00254, True, True, swSkOffsetCapEndType_e.swSkOffsetArcCaps, swSkOffsetMakeConstructionType_e.swSkOffsetMakeBothConstruction, True)

**一句话依据**：官方 VB 配方对 2.54 mm 传 `0.00254`，仓内 `float(offset_mm)` 把 2.54 原样传 ⇒ 差 1000 倍；个数与顺序确实都对得上，只有量纲不对。

---

## A-4 · `CreateLinearSketchStepAndRepeat` 第 3、4 实参 `SpacingX/Y` 量纲

**判定：成立**

**仓内那一段** —— `scripts/sw_sketch_edit_ops.py`，`sketch_linear_pattern`（实参列表第 3、4 位）：
```python
                          int(num_x), int(num_y), float(spacing_x_mm), float(spacing_y_mm),
                          math.radians(float(angle_x_deg)), math.radians(float(angle_y_deg)),
```

**目标那一段** —— `C:\swapi\types\ISketchManager\CreateLinearSketchStepAndRepeat.md`：
> - **SpacingX**: Spacing between instances along the x axis

`C:\swapi\examples\Create_and_Edit_Linear_Sketch_Pattern_Example_CSharp.md`：
> boolstatus = swSketchMgr.CreateLinearSketchStepAndRepeat(2, 2, 0.0254, 0.0254, 0.296705972839, 1.134464013796, "", true, true, false, true, true);

**一句话依据**：官方配方 `SpacingX=SpacingY=0.0254`（米制），仓内 `float(spacing_x_mm)` / `float(spacing_y_mm)` 无换算直传；同行的 `math.radians` 与配方弧度一致，核对表判定「不算分歧」亦属实。

---

## A-5 · `CreateCircularSketchStepAndRepeat` 第 1 实参 `ArcRadius` 量纲

**判定：成立**

**仓内那一段** —— `scripts/sw_sketch_edit_ops.py`，`sketch_circular_pattern`（实参列表第 1 位）：
```python
                          float(arc_radius_mm), math.radians(float(arc_angle_deg)),
                          int(pattern_num), math.radians(float(pattern_spacing_deg)),
```

**目标那一段** —— `C:\swapi\types\ISketchManager\CreateCircularSketchStepAndRepeat.md`：
> - **ArcRadius**: Radius for the circular sketch pattern

`C:\swapi\examples\Create_and_Edit_Circular_Sketch_Pattern_Example_CSharp.md`：
> boolstatus = swSketchMgr.CreateCircularSketchStepAndRepeat(0.03184378021964, 4.732863934409, 4, 1.570796326795, true, "", true, true, true);

**一句话依据**：官方配方 `ArcRadius = 0.03184378021964`（米制），仓内 `float(arc_radius_mm)` 原样传；第 2、4 位的 `math.radians` 与配方 `4.7329` / `1.5708` 弧度一致，不构成分歧。

---

## A-6 / C-3 · `SketchModifyFlip` 的 `AxisFlag`：我们断言「官方没给取值表」，官方页给了

**判定：成立**

**仓内那一段** —— `scripts/sw_sketch_modify_ops.py`，`sketch_flip` 的 docstring 与返回值：
```python
    ⚠ `AxisFlag` 的**取值表官方两个源都没给** ⇒ ★ 按铁律 5 **原样透传 int，不猜语义**，
```
```python
            "axis_flag_semantics": "官方 swapi 与 CHM 均未给取值表 —— 原样透传"}
```

**目标那一段** —— `C:\swapi\types\IModelDoc2\SketchModifyFlip.md`：
> - **AxisFlag**: Axis about which to flip the sketch:
>
>   - X = 1
>
>   - Y = 2

**一句话依据**：官方 `swapi` 页的 `AxisFlag` 形参下**就带着取值表**（X=1 / Y=2），而仓内把「官方两源都没给取值表」这一断言既写进 docstring 又写进对外返回值 ⇒ 依据与原文不符，分歧成立（值本身我们仍原样透传，未判对错）。

---

## B-1 · `SketchTrim` 官方前置点名 `SelectByID2`，我们走 `Select4`

**判定：成立**

**仓内那一段** —— `scripts/sw_sketch_edit_ops.py`：
```python
    ok = get_com_member(seg, "Select4", bool(append), _empty_callout())
```
（`select_sketch_segment` 内）；`sketch_trim` 内：
```python
    _select_spec(model, selection)
```

**目标那一段** —— `C:\swapi\types\ISketchManager\SketchTrim.md` 的 `## Remarks`：
> Before calling this method, you must edit a sketch and select sketch segments to trim using [[IModelDocExtension::SelectByID2]].

同页 `swSketchTrimTwoEntities` 条：
> Two intersecting sketch segments; trims the first selected sketch segment to the second intersecting sketch segment. Use IModelDocExtension::SelectByID2 with Mark = 0 to select two sketch segments, specifying their pick points.

`C:\swapi\examples\Trim_Sketch_Entities_Example_CSharp.md`：
> status = swModelDocExt.SelectByID2("Line6", "SKETCHSEGMENT", 0.0391723509933775, -0.0466042594822396, 0, true, 0, null, 0);

**一句话依据**：官方前置点名具体入口 `SelectByID2`（TwoEntities 处还点名 mark = 0 与 pick point），仓内 `Select4` 的实参只有 `append` 与 callout，确无 mark、无 pick point ⇒ 成立。

---

## B-2 · `SketchOffset2` 官方例子第 7 实参 mark = 1，我们的 `Select4` 路径无 mark

**判定：成立**

**仓内那一段** —— `scripts/sw_sketch_edit_ops.py`：
```python
    ok = get_com_member(seg, "Select4", bool(append), _empty_callout())
```
（`select_sketch_segment` 内）；`sketch_offset` 内：
```python
    _select_spec(model, selection)
```
★ 附注（不影响判定）：`_select_spec` 的签名里虽有 `mark: int = 0`，但函数体内**从未把它传给任何 COM 调用**（`_select_spec` 只调 `select_sketch_segment(model, i, append=…)`），故「选择路径没有 mark」这一说法对**实际调用**仍准确。

**目标那一段** —— `C:\swapi\examples\Sketch_Offset_Example_CSharp.md`：
> status = swModelDocExt.SelectByID2("Line3", "SKETCHSEGMENT", 0, 0, 0, false, 1, null, 0);
> status = swSketchManager.SketchOffset2(0.00254, true, true, (int)swSkOffsetCapEndType_e.swSkOffsetArcCaps, (int)swSkOffsetMakeConstructionType_e.swSkOffsetMakeBothConstruction, true);

**一句话依据**：官方 C# 例子里 `SelectByID2` 的第 7 个实参是 `1`（mark），紧接才是 `SketchOffset2`，而仓内选择只走两参 `Select4` ⇒ 成立。

---

## B-4 · `MergePoints` 官方前置「只能有一个开放轮廓」，仓内未提

**判定：成立**

**仓内那一段** —— `scripts/sw_sketch.py`：
```python
def merge_points(sketch, tolerance: float) -> bool:
    """合并重合点。⚠ 容差单位官方无说明。"""
    if sketch is None:
        raise ValueError("sketch 为 None")
    return bool(get_com_member(sketch, "MergePoints", float(tolerance)))
```

**目标那一段** —— `C:\swapi\types\ISketch\MergePoints.md` 的 `## Remarks`：
> This method requires that only one open contour exists in the sketch. To specify a distance below which points are automatically merged while creating the segments, use [[ISketchRelationManager::AddRelation]] or [[ISketchRelationManager::IAddRelation]] and swConstraintType_COINCIDENT.

**一句话依据**：官方写明的前置是「草图里只能有一个开放轮廓」，而仓内 `merge_points` 全函数（docstring + 3 行体）只说「容差单位官方无说明」，既无该前置检查也无注释提及 ⇒ 成立。

---

## C-1 · `_active_sketch_name()` 只调 Obsolete 的 `GetActiveSketch2`、无后继回退 —— **对不上**

**判定：不成立**（★ 官方原文在，**但「我们的原文」在今天的仓里已不存在** —— 代码在核对之后已改走官方点名的后继入口）

**仓内那一段** —— `scripts/sw_sketch_modify_ops.py`，`_active_sketch_name()` 现在的函数体：
```python
def _active_sketch_name(model):
    """★ 旁证：当前活动草图的名字（★ 取不到就回 None，**不猜、不兜底**）。

    ★★★ 2026-10-03（接手轮）**换走后继入口** —— 原来是 `get_com_member(model, "GetActiveSketch2")`。
    """
    try:
        from sw_sketch import active_sketch as _active_sketch
        sk = _active_sketch(model)
```
★ 全文件对 `GetActiveSketch2` 的命中只剩**注释里那一句「原来是 …」**，已无任何调用。

**目标那一段** —— `C:\swapi\types\IModelDoc2\GetActiveSketch2.md`（官方原文确实在）：
> Obsolete. Superseded by [[SketchManager::ActiveSketch]].

**一句话依据**：核对表所引的那句调用 `sk = get_com_member(model, "GetActiveSketch2")` 在 `_active_sketch_name` 里已查不到 —— 该函数现在转调 `scripts/sw_sketch.py::active_sketch`，而后者正是官方点名的那条后继（`get_com_member(get_com_member(model, "SketchManager"), "ActiveSketch")`），故「只走 Obsolete、无回退」这一分歧**已不成立**（按铁律 3 记「查不到」，不用相似代码顶替）。

---

## C-2 · `create_sketch_chamfer._seg_count()` 先调 Obsolete 再回退后继

**判定：成立**

**仓内那一段** —— `scripts/sw_sketch_edit.py`：
```python
            sk = get_com_member(model, "GetActiveSketch2")
            if sk is None:
                sk = get_com_member(get_com_member(model, "SketchManager"), "ActiveSketch")
```

**目标那一段** —— `C:\swapi\types\IModelDoc2\GetActiveSketch2.md`：
> Obsolete. Superseded by [[SketchManager::ActiveSketch]].

**一句话依据**：核对表所引的两行逐字都在（先 Obsolete、`if sk is None` 再回退后继），与官方页标注的「后继是 `SketchManager::ActiveSketch`」一致 ⇒ 「先调 Obsolete、后继不在首位」这一描述与代码相符。

---

## C-4 · `SKETCH_CHAMFER_TYPE["distance_distance"] = 1`，官方枚举里该成员是 `-1`

**判定：成立**（★ 只判「字面量 1 不在官方枚举页的三个值里」，不判两源谁对）

**仓内那一段** —— `scripts/sw_sketch_edit.py`：
```python
    "distance_distance": 1,     # swSketchChamfer_DistanceDistance（⚠ md 写 -1，反射写 1，采用 1）
```

**目标那一段** —— `C:\swapi\enums\swSketchChamferType_e.md`：
> enum_member_count: 3
> | swSketchChamfer_DistanceAngle | 0 |
> | swSketchChamfer_DistanceDistance | -1 |
> | swSketchChamfer_DistanceEqual | 2 |

**一句话依据**：官方枚举页的三个值是 `0 / -1 / 2`，其中**没有 `1`**，而仓内把 `1` 作为该枚举的字面量传给 `ISketchManager.CreateChamfer` 的 `Type` ⇒ 成立；仓内注释自己已写明两源不一致且采用反射，按核对表口径不判谁对。

---

## C-5 · `SKETCH_CROSS_HATCH` 上方注释称「swapi 只列了其中 3 个」，官方枚举页列全 5 个

**判定：成立**

**仓内那一段** —— `scripts/sw_sketch.py`：
```python
#: ⚠ swapi 只列了其中 3 个（`Include/Exclude/AndExplodeOnly`），**值相同**，无冲突。
#: 反射里还有 `swCrossHatchOnly = 2` · `swSolidHatchOnly = 4`。
SKETCH_CROSS_HATCH = {
    "include": 0,               # swCrossHatchInclude（**本模块默认**）
    "exclude": 1,               # swCrossHatchExclude
    "only": 2,                  # swCrossHatchOnly
    "and_explode_only": 3,      # swCrossHatchAndExplodeOnly
    "solid_hatch_only": 4,      # swSolidHatchOnly
}
```

**目标那一段** —— `C:\swapi\enums\swCrossHatchFilter_e.md`：
> enum_member_count: 5
> | swCrossHatchAndExplodeOnly | 3 |
> | swCrossHatchExclude | 1 |
> | swCrossHatchInclude | 0 |
> | swCrossHatchOnly | 2 |
> | swSolidHatchOnly | 4 |

**一句话依据**：官方 swapi 枚举页**本身列全了 5 个**、且两值与仓内字面量一致（0/1/2/3/4），而仓内注释仍称「swapi 只列了 3 个、另两个仅见于出厂反射」⇒ 描述与原文不符，成立。

---

## 统计与边界

- **核了 14 处**（A 6 条 · B 3 条 · C 5 条；A-6 与 C-3 为同一分歧的两次记录，两份原文均已核）。
- **对不上 1 处** —— **C-1**：官方原文在，但**我们的原文在今天的仓里已不存在**（`_active_sketch_name` 已改走官方后继 `SketchManager::ActiveSketch`），故判**不成立**。
- **存疑 0 处**。
- B 文件里置信度为「中」的**第 3、5 条未核**（按任务口径不碰中/低）。
- 查不到的只有一处表述：A-1 里「CHM 解包目录下没有 `ISketch~GetContourEdges` 页」——CHM 目录不在本次两处检索路径内，**按铁律 5 不复述、不背书**，该条结论不依赖这一句。
