# C4 的两类致命冲突：`unit_diff`(15) + `mark_diff`(10) —— 逐条表

> **生成物** —— 由 `tools/t4_extract_unit_mark_conflicts.py` 产出，**不要手改**。
> 输入：`specs/204-bunny-moat-batches/recon/c4-merged.json`（另一个对话的 C4 产出，**只读复用**）。

## 一 · 为什么先做这两类

★ C4 共报 598 条冲突（过引文闸 544），分类：`precondition_diff` 324 · `other_conflict` 174 ·
`return_shape_diff` 75 · **`unit_diff` 15** · **`mark_diff` 10**。
★★ 本表只取**后两类** —— 因为**单位写错、选择 mark 写错**会**直接让工具算错或选错**，
★ 而前几类多半是「详略差异」（★ 另一对话的 V1 抽检：12 条里只 4 条真互斥 ⇒ 真冲突约 220–270）✓

★★ **本表「不算什么」**：
- ★ **不等于**「官方文档错了就一定是示例错」—— 本表只记**两侧不能同时成立**，谁对要逐条判；
- ★ **不构成**任何「我们的实现是错的」结论 —— 要先看我们**实际怎么调**（另一步）；
- ★ 来源全程 `conditional_pass`（该规格 REPORT §七 自陈 C4 只覆盖 91% 箱、丢箱偏向尾部）
  ⇒ ★★ **候选队列，逐条过闸才采纳** ✓

## 二 · 逐条（25 条）

| # | 成员 | 类 | ★ `Remarks` 说 | ★ 示例写 | 示例文件 | 判读 |
|---:|---|---|---|---|---|---|
| 1 | `AutoDimension2` | mark_diff | Select and mark a unique vertical edge, vertex, sketch point, or vertical sketch line as the datum for the horizontal dimensioning scheme, using swAutodimMarkHorizontalDa | bRet = swSketchSegVert.Select4(True, Nothing) | `Autodimension_All_Sketches_Example_VB.md` | 备注要求基准必须打 swAutodimMark* 标记；示例用没有 mark 形参的 Select4 选基准却声明成功。 |
| 2 | `ConeParams` | unit_diff | The half angle, origin, and radius parameters are in meters. | " & vCone(7) * 57.3 & " deg" | `Locate_Apex_of_Conical_Face_Example_VB.md` | Remarks 说 half angle 以米计；示例把 vCone(7) 当弧度，乘 57.3（度/弧度）后打印 deg，紧邻上一行还注明 1 radian = 57.3º。同一个元素不能既是米又是弧度。 |
| 3 | `EditMate3` | mark_diff | The two mated items must be selected with a selection mark of 1. |         '   IAssemblyDoc::EditMate3 requires that mate entities         '   be selected with mark of 1 except for:         '       swMateCAMFOLLOWER         '           c | `Edit_Mate_Example_VB.md` | Remarks 把 mark=1 写成无条件硬要求；示例明写 cam follower face 用 8、symmetry plane 用 4，两者不可同时成立。 |
| 4 | `FeatureCircularPattern4` | unit_diff | Spacing between each instance of the circular pattern; total angle in radians if EqualSpacing is true | myModel.FeatureManager.FeatureCircularPattern4 3, 1.25663706143592, True, "NULL", False, False, False | `Get_Cosmetic_Threads_in_a_Part_Document_Example_VB.md` | 成员页把弧度口径限定在 EqualSpacing=true；示例 EqualSpacing=False 仍传 1.25663706143592（=72°弧度），两侧不能同时成立 |
| 5 | `FeatureExtruRefSurface2` | mark_diff | Sketch; call [[IModelDocExtension::SelectByID2]] with selection mark 0. | boolstatus = swModelDocExt.SelectByID2("Sketch1", "SKETCH", 0, 0, 0, false, 4, null, 0); | `Create_Surface_Knit_Feature_Example_CSharp.md` | Remarks 规定「Sketch」只用 mark 0，mark 4 仅属「Sketch segments」；示例实体类型正是 SKETCH 却用 mark 4，两条规则不能同时为真。 |
| 6 | `FeatureExtruRefSurface2` | mark_diff | Sketch; call [[IModelDocExtension::SelectByID2]] with selection mark 0. | status = swModelDocExt.SelectByID2("Sketch1", "SKETCH", 0, 0, 0, false, 4, null, 0); | `Create_Temporary_Bodies_by_Offsetting_Surface_Body_Example_CSharp.md` | 第二份官方示例独立复现同一写法：整草图按名称选中、mark 仍为 4，与 Remarks 给「Sketch」的 mark 0 直接矛盾。 |
| 7 | `FeatureLinearPattern4` | unit_diff | - **Offset1**: Offset in meters from a selected reference in Direction 1 (see **Remarks**); valid only if HasOffset1 is true | * 0.l9 (Offset1; furthest instance in Direction 1 is offset by 190 mm | `Create_Linear_Pattern_Example_VB.md` | 页面写 Offset1 以米计、示例注释把同一个 0.19 说成 190 mm；同一行的 Spacing2 同样：页面「in meters」对示例「* 0.02 (Spacing2 in mm)」。 |
| 8 | `FeatureLinearPattern4` | mark_diff | - 8388608 to mark a seed instance reference when FromCentroid1 or FromCentroid2 is false | status = swModelDocExt.SelectByID2("Boss-Extrude2", "SOLIDBODY", 0, 0, 0, True, 256, Nothing, 0) | `Change_Linear_Pattern_Example_VB.md` | F4 的 mark 表只有特征/组件两行（1/2/4/2097152/8388608），无 256；示例用 256 选实体，256 只出现在 F5 页「256 to mark the solid bodies to pattern」。 |
| 9 | `FieldOfViewAngle` | unit_diff | Camera's horizontal angle of the field of view in radians | swCamera.FieldOfViewAngle * 1000.0 + " mm" | `Insert_Camera_Example_CSharp.md` | 成员页写明该量是弧度；示例却对它做 ×1000 的米→毫米换算并标 mm。弧度不是长度、不能换算成毫米，两侧不能同时成立。 |
| 10 | `FieldOfViewAngle` | unit_diff | Camera's horizontal angle of the field of view in radians | swCamera.FieldOfViewAngle * 1000# & " mm" | `Insert_Camera_Example_VB.md` | 同上：VBA 示例对同一量做 ×1000 并标 mm，与成员页的弧度口径冲突。 |
| 11 | `FieldOfViewAngle` | unit_diff | Camera's horizontal angle of the field of view in radians | swCamera.FieldOfViewAngle * 1000.0# & " mm" | `Insert_Camera_Example_VBNET.md` | 同上：VB.NET 示例对同一量做 ×1000 并标 mm，与成员页的弧度口径冲突。 |
| 12 | `GetEnvironment` | unit_diff | All numeric values returned from the IEnvironment object are relative to a unit text height of 1.0.; i.e., if a symbol has a text height of 0.15, then multiply the numeri |         Debug.Print ("        " & lineSymbols(i)) | `Analyze_Text_and_Geometry_in_GTol_Flat_Symbol_Example_VB.md` | Remarks 说所有数值按字高 1.0 归一、须再乘实际字高；示例把 GetSymLines 原值直接当坐标打印，未做任何缩放。 |
| 13 | `GetMergeDistance` | unit_diff | By default, points within 0.001mm are merged. | Debug.Print " Merge distance: " & (importData.GetMergeDistance("") * 1000#) & " mm" | `Import_DXF_File_into_Part_Sketch_Example_VB.md` | Remarks 唯一的量级线索用 mm，示例却必须先 *1000 才得到 mm，说明返回是米制；照 Remarks 读成 mm 会差 1000 倍，两侧口径不能同时成立。 |
| 14 | `GetRowHeight` | unit_diff | Height of the specified row in meters | RowHeight = swTableAnn.GetRowHeight(J); | `C:\swapi\examples\Get_Components_in_Each_BOM_Table_Row_Example_CSharp.md` | 本成员页写米；示例该调用绑在 TableAnnotation 声明上，同名 ITableAnnotation.GetRowHeight 的 Returns 写 in system units，两套口径不能同时成立。 |
| 15 | `InsertCutSwept5` | mark_diff | - 1 = Sketch profile or tool body | status = swModelDocExt.SelectByID2("", "EDGE", -0.0372983839416747, 0.0393904284381961, 0.0495042874504179, true, 4, null, 0); | `Create_Cut-sweep_Feature_Using_Circular_Profile_Example_CSharp.md` | Remarks 把 mark 1（草图轮廓/工具体）列为无条件前置；CircularProfile=true 的三份示例只选 mark 4 一条边，mark 1 一次都没用。 |
| 16 | `InsertCutSwept5` | mark_diff | - 2 = Guide curve, if provided  - 4 = Sweep path | status = swModelDocExt.SelectByID2("Boss-Extrude1", "SOLIDBODY", 0, 0, 0, true, 2048, null, 0); | `Create_Cut-sweep_Feature_Using_Tool_Body_Example_CSharp.md` | Remarks 只枚举 1/2/4 三个 mark；工具体示例在 mark 1 与 4 之外，还用 mark 2048 选了第三个实体。 |
| 17 | `InsertMoveCopyBody2` | mark_diff | Rotation edge, vertex, coordinate system  2 | status = swModelDocExt.SelectByID2("", "VERTEX", -0.085, 0, 0.065, True, 4, Nothing, 0) status = swModelDocExt.SelectByID2("", "VERTEX", -0.085, -0.09, 0.065, True, 8, No | `Copy_and_Rotate_Body_using_Edge_Example_VB.md` | Remarks 把旋转参考实体定为 mark 2；示例这一次调用传的是旋转原点（RotPoint）却只用 mark 4/8（平移 mark），旋转的 2 从未出现。 |
| 18 | `InsertProtrusionBlend2` | mark_diff | - 2 = guide curve selections | status = swModelDocExt.SelectByID2("Sketch3", "SKETCH", 0, 0, 0, true, 4098, null, 0); | `Get_Guide_Curves_in_Loft_Feature_Example_CSharp.md` | Remarks 只列 mark=2 作引导曲线；示例传 4098（=4096+2），4096 位在官方 mark 表与 swSelectOption_e（仅 0/1）中无出处。 |
| 19 | `InsertSewRefSurface` | unit_diff | A knit tolerance's:  - lower limit is 0.0001 mm  - upper limit is 0.1 mm | Debug.Print("  Knit tolerance: " + swSurfaceKnitFeature.KnitTolerance * 1000 + " mm"); | `Create_Surface_Knit_Feature_Example_CSharp.md` | 示例回读后要 ×1000 才标 mm，说明裸值单位是米；0.0001 裸值即 0.1 mm，与 Remarks「下限 0.0001 mm」不能同时成立。 |
| 20 | `InsertSewRefSurface` | unit_diff | A knit tolerance's:  - lower limit is 0.0001 mm  - upper limit is 0.1 mm | swNewFeatMgr.InsertSewRefSurface(true, false, false, 3.001639406912E-05, 0.0001); | `Fill_Holes_in_Part_Example_CSharp.md` | KnitTolerance 传 3.001639406912E-05；按 Remarks 的 mm 口径它低于 0.0001 mm 下限，按米口径才等于 0.03 mm 落在区间内。 |
| 21 | `InsertWeldmentTrimFeature2` | mark_diff | - 1 = Body or bodies to trim  - 2 = Trimming boundaries (body or face) | = Part.Extension.SelectByID2("Structural Member1[2]", "SOLIDBODY", 0, 0, 0, true, 2, null, 0); boolstatus = Part.Extension.SelectByID2("Structural Member1[1]", "SOLIDBODY | `Insert_Weldment_Features_Example_CSharp.md` | 先选者标 mark2 落 v1=BodiesToTrim，后选标 mark1 落 v2=BodiesOrFaces，与 Remarks 的 1=待裁、2=裁边正好相反。 |
| 22 | `IsTolerant` | unit_diff | Tolerance: Edge tolerance or gap in meters | Gap size (or tolerance) in mm of each edge or vertex. | `Get_Maximum_Edge_and_Vertex_Gaps_Example_VB.md` | 成员页说 out 参数是米，示例说同一间隙是 mm 且直接比较打印；差 1000 倍，不能同时成立。 |
| 23 | `MaxValueForGapRange` | unit_diff | Maximum gap should be in the range of [[ISurfaceKnitFeatureData::KnitTolerance]] to 1 mm. |             Debug.Print("  Maximum value for gap range: " + swSurfaceKnitFeature.MaxValueForGapRange * 1000 + " mm"); | `Create_Surface_Knit_Feature_Example_CSharp.md` | Remarks 把该值范围直接写成 mm（Returns 另写 0.01 mm~1 mm）；示例读回后 ×1000 再拼 ' mm'，即按米读同一数值 ⇒ 单位口径不能同时成立。 |
| 24 | `SetSystemValue3` | unit_diff | Sets the value of this dimension in system units (meters) in the specified configuration. | ' Change D3 of LocalCirPattern1 from 360 degrees to 270 degrees (4.72 radians) | `Change_Dimension_Example_VB.md` | 成员页称该入参一律以米计（Parameters 亦写 NewValue: Dimension value in meters），示例却把同一入参当弧度用（4.72 rad=270°，把 360° 改为 270°）；两者不能同时成立。 |
| 25 | `SetupSheet6` | unit_diff | Multiplying ZoneRow by ZoneCol equals the total number of zones in the zone area of this drawing sheet. The zone area is specified by ZoneLeftMargin, ZoneRightMargin, Zon | 0.2794, 0.2159, "Default", False, 0.5, 0.5, 0.5, 0.5, 3, 3) | `Create_Drawing_Sheet_Zones_Example_VB.md` | 同一次调用里 Width/Height 用米（0.2794/0.2159），四个 Zone 边距却是 0.5；同一单位下边距大于整张图，成员页又未标边距单位。 |

## 三 · 成员分布

- `FieldOfViewAngle` × 3
- `FeatureExtruRefSurface2` × 2
- `FeatureLinearPattern4` × 2
- `InsertCutSwept5` × 2
- `InsertSewRefSurface` × 2
- `AutoDimension2` × 1
- `ConeParams` × 1
- `EditMate3` × 1
- `FeatureCircularPattern4` × 1
- `GetEnvironment` × 1
- `GetMergeDistance` × 1
- `GetRowHeight` × 1
- `InsertMoveCopyBody2` × 1
- `InsertProtrusionBlend2` × 1
- `InsertWeldmentTrimFeature2` × 1
- `IsTolerant` × 1
- `MaxValueForGapRange` × 1
- `SetSystemValue3` × 1
- `SetupSheet6` × 1

## 四 · 下一步（T4-1 的「逐条核」）

★ 对每条判三态：**成立**（我们照示例写会错）/ **不成立**（我们没照示例写）/ **查不到**；
★ 成立的 ⇒ 核**我们实际怎么调**（`scripts/` 里对应实现），有证据才改 ✓
