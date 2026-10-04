# unit_diff 冲突的机械判读：我们的调用点附近有没有单位换算

> 生成物 —— 由 `tools/t4_unit_audit.py` 产出，不要手改。
> 输入：`c4-merged.json`（只读）+ 本仓 `scripts/` `mcp-server/` `tools/`。

## 一 · 口径（★ 先说判据）

| 项 | 值 |
|---|---|
| `unit_diff` 冲突 | **15** 条 |
| 涉及成员 | **12** 个 |
| ★ 判据 | 真调用点（`ast` 判）前后 **15 行**内出现的换算形态（度↔弧度 / 毫米↔米 / 毫米↔英寸）|

★★ **本表「不算什么」**（★ 缺了它会被误用）：

- ★ **不等于**「我们单位用错了」—— 它只说**窗口内有没有换算**；
  ★★ 而「有没有换算」与「换算对不对」是**两件事** ⇒ ★ 结论必须**逐条对照官方 Remarks 的单位**才能下；
- ★ **窗口内没有换算 ≠ 错** —— ★ 可能我们**本来就按官方要求的单位传**（那才是对的）；
- ★ **窗口 15 行是启发式** ⇒ 换算写在别处（如上游调用方）时会误判；
- ★ 只覆盖**我们真调用过**的成员 ✓

## 二 · 逐成员

### `ConeParams`（1 条冲突）

- ★ `Remarks`：The half angle, origin, and radius parameters are in meters.
- ★ 示例：`" & vCone(7) * 57.3 & " deg"`
- ★ 判读：Remarks 说 half angle 以米计；示例把 vCone(7) 当弧度，乘 57.3（度/弧度）后打印 deg，紧邻上一行还注明 1 radian = 57.3º。同一个元素不能既是米又是弧度。

★ **我们没真调用过** ⇒ 该冲突对我们当前无直接影响 ✓

### `FeatureCircularPattern4`（1 条冲突）

- ★ `Remarks`：Spacing between each instance of the circular pattern; total angle in radians if EqualSpacing is true
- ★ 示例：`myModel.FeatureManager.FeatureCircularPattern4 3, 1.25663706143592, True, "NULL", False, False, False`
- ★ 判读：成员页把弧度口径限定在 EqualSpacing=true；示例 EqualSpacing=False 仍传 1.25663706143592（=72°弧度），两侧不能同时成立

- 调用点 `scripts\sw_part.py:1441` ⇒ ★★ 窗口内**没有**换算（★ 可能本来就按官方单位传 ⇒ 不一定错）
- 调用点 `tools\probe_pattern5.py:114` ⇒ ★★ 窗口内**没有**换算（★ 可能本来就按官方单位传 ⇒ 不一定错）

### `FeatureLinearPattern4`（1 条冲突）

- ★ `Remarks`：- **Offset1**: Offset in meters from a selected reference in Direction 1 (see **Remarks**); valid only if HasOffset1 is true
- ★ 示例：`* 0.l9 (Offset1; furthest instance in Direction 1 is offset by 190 mm`
- ★ 判读：页面写 Offset1 以米计、示例注释把同一个 0.19 说成 190 mm；同一行的 Spacing2 同样：页面「in meters」对示例「* 0.02 (Spacing2 in mm)」。

- 调用点 `tools\probe_linear_pattern_baseline.py:115` ⇒ ★★ 窗口内**没有**换算（★ 可能本来就按官方单位传 ⇒ 不一定错）
- 调用点 `tools\prove_linear_pattern_generations.py:94` ⇒ ★★ 窗口内**没有**换算（★ 可能本来就按官方单位传 ⇒ 不一定错）

### `FieldOfViewAngle`（3 条冲突）

- ★ `Remarks`：Camera's horizontal angle of the field of view in radians
- ★ 示例：`swCamera.FieldOfViewAngle * 1000.0 + " mm"`
- ★ 判读：成员页写明该量是弧度；示例却对它做 ×1000 的米→毫米换算并标 mm。弧度不是长度、不能换算成毫米，两侧不能同时成立。
- ★ `Remarks`：Camera's horizontal angle of the field of view in radians
- ★ 示例：`swCamera.FieldOfViewAngle * 1000# & " mm"`
- ★ 判读：同上：VBA 示例对同一量做 ×1000 并标 mm，与成员页的弧度口径冲突。
- ★ `Remarks`：Camera's horizontal angle of the field of view in radians
- ★ 示例：`swCamera.FieldOfViewAngle * 1000.0# & " mm"`
- ★ 判读：同上：VB.NET 示例对同一量做 ×1000 并标 mm，与成员页的弧度口径冲突。

★ **我们没真调用过** ⇒ 该冲突对我们当前无直接影响 ✓

### `GetEnvironment`（1 条冲突）

- ★ `Remarks`：All numeric values returned from the IEnvironment object are relative to a unit text height of 1.0.; i.e., if a symbol has a text height of 0.15, then multiply the numeric values returned by 0.15.
- ★ 示例：`        Debug.Print ("        " & lineSymbols(i))`
- ★ 判读：Remarks 说所有数值按字高 1.0 归一、须再乘实际字高；示例把 GetSymLines 原值直接当坐标打印，未做任何缩放。

★ **我们没真调用过** ⇒ 该冲突对我们当前无直接影响 ✓

### `GetMergeDistance`（1 条冲突）

- ★ `Remarks`：By default, points within 0.001mm are merged.
- ★ 示例：`Debug.Print " Merge distance: " & (importData.GetMergeDistance("") * 1000#) & " mm"`
- ★ 判读：Remarks 唯一的量级线索用 mm，示例却必须先 *1000 才得到 mm，说明返回是米制；照 Remarks 读成 mm 会差 1000 倍，两侧口径不能同时成立。

★ **我们没真调用过** ⇒ 该冲突对我们当前无直接影响 ✓

### `GetRowHeight`（1 条冲突）

- ★ `Remarks`：Height of the specified row in meters
- ★ 示例：`RowHeight = swTableAnn.GetRowHeight(J);`
- ★ 判读：本成员页写米；示例该调用绑在 TableAnnotation 声明上，同名 ITableAnnotation.GetRowHeight 的 Returns 写 in system units，两套口径不能同时成立。

★ **我们没真调用过** ⇒ 该冲突对我们当前无直接影响 ✓

### `InsertSewRefSurface`（2 条冲突）

- ★ `Remarks`：A knit tolerance's:

- lower limit is 0.0001 mm

- upper limit is 0.1 mm
- ★ 示例：`Debug.Print("  Knit tolerance: " + swSurfaceKnitFeature.KnitTolerance * 1000 + " mm");`
- ★ 判读：示例回读后要 ×1000 才标 mm，说明裸值单位是米；0.0001 裸值即 0.1 mm，与 Remarks「下限 0.0001 mm」不能同时成立。
- ★ `Remarks`：A knit tolerance's:

- lower limit is 0.0001 mm

- upper limit is 0.1 mm
- ★ 示例：`swNewFeatMgr.InsertSewRefSurface(true, false, false, 3.001639406912E-05, 0.0001);`
- ★ 判读：KnitTolerance 传 3.001639406912E-05；按 Remarks 的 mm 口径它低于 0.0001 mm 下限，按米口径才等于 0.03 mm 落在区间内。

- 调用点 `scripts\sw_surface_features.py:263` ⇒ ★ 窗口内有换算: 毫米→米

### `IsTolerant`（1 条冲突）

- ★ `Remarks`：Tolerance: Edge tolerance or gap in meters
- ★ 示例：`Gap size (or tolerance) in mm of each edge or vertex.`
- ★ 判读：成员页说 out 参数是米，示例说同一间隙是 mm 且直接比较打印；差 1000 倍，不能同时成立。

★ **我们没真调用过** ⇒ 该冲突对我们当前无直接影响 ✓

### `MaxValueForGapRange`（1 条冲突）

- ★ `Remarks`：Maximum gap should be in the range of [[ISurfaceKnitFeatureData::KnitTolerance]] to 1 mm.
- ★ 示例：`            Debug.Print("  Maximum value for gap range: " + swSurfaceKnitFeature.MaxValueForGapRange * 1000 + " mm");`
- ★ 判读：Remarks 把该值范围直接写成 mm（Returns 另写 0.01 mm~1 mm）；示例读回后 ×1000 再拼 ' mm'，即按米读同一数值 ⇒ 单位口径不能同时成立。

★ **我们没真调用过** ⇒ 该冲突对我们当前无直接影响 ✓

### `SetSystemValue3`（1 条冲突）

- ★ `Remarks`：Sets the value of this dimension in system units (meters) in the specified configuration.
- ★ 示例：`' Change D3 of LocalCirPattern1 from 360 degrees to 270 degrees (4.72 radians)`
- ★ 判读：成员页称该入参一律以米计（Parameters 亦写 NewValue: Dimension value in meters），示例却把同一入参当弧度用（4.72 rad=270°，把 360° 改为 270°）；两者不能同时成立。

- 调用点 `scripts\sw_document_data.py:365` ⇒ ★★ 窗口内**没有**换算（★ 可能本来就按官方单位传 ⇒ 不一定错）

### `SetupSheet6`（1 条冲突）

- ★ `Remarks`：Multiplying ZoneRow by ZoneCol equals the total number of zones in the zone area of this drawing sheet. The zone area is specified by ZoneLeftMargin, ZoneRightMargin, ZoneTopMargin, and ZoneBottomMargin.
- ★ 示例：`0.2794, 0.2159, "Default", False, 0.5, 0.5, 0.5, 0.5, 3, 3)`
- ★ 判读：同一次调用里 Width/Height 用米（0.2794/0.2159），四个 Zone 边距却是 0.5；同一单位下边距大于整张图，成员页又未标边距单位。

★ **我们没真调用过** ⇒ 该冲突对我们当前无直接影响 ✓

## 三 · ★ 小结

★ 15 个 `unit_diff` 成员里 **4 个我们真调用过** ✓

★ **下一步（★ 仍需人读官方页）**：对每个调用点读官方 `## Remarks` 的**单位声明** ⇒
★ 判「我们传的值是不是那个单位」—— ★★ 本表只给「有没有换算」这个机械事实，**不判对错** ✓
★ 成立且有证据的才改；★ 按 D-3，改之前上真机一次一条 ✓

