# 写码前必查表：这些官方成员的 `Remarks` 与官方示例**不能同时成立**

> 生成物 —— 由 `tools/t4_3_build_lookup.py` 产出，不要手改。
> 输入：`specs/204-bunny-moat-batches/recon/c4-merged.json`（另一个对话的 C4 产出，只读复用）。
> ★ 用法：**动手碰下表中任一成员之前，先看一眼它这一行** —— 它是官方文档内部的两侧对不上。

## 一 · 口径（★ 与数字一起读）

| 项 | 值 |
|---|---|
| 全量冲突 | **598** 条（另一对话的机械报出）|
| 过引文闸 | **544**（★ 其 `quote_ok`）|
| ★ 本表取的类 | `unit_diff` · `mark_diff` · `return_shape_diff` · `precondition_diff` |
| ★ 涉及成员 | **368** 个 · 条目 **424** 条 |

★★ **本表「不算什么」**（★ 缺了它，这张表会被误用）：

- ★ **不等于**「官方文档错了、示例对」—— 它只记**两侧不能同时成立**，★ **谁对要逐条判**；
- ★★ **不等于**「我们的实现错了」—— ★ 要用 `ast` 判**我们有没有真调用**（★ 事实 528：文本命中 ≠ 真调用）；
- ★ ★ 不取 `other_conflict`(174) —— ★ 另一对话的 V1 抽检：12 条里只 4 条真互斥，**其余是「详略差异」不是矛盾** ⇒ 真冲突约 220–270 ✓
- ★ 来源全程 `conditional_pass`（该规格 REPORT §七：C4 只覆盖 **91%** 箱、**丢箱系统偏向尾部**）；
  ★★ **且本表未回查官方页原文** ⇒ ★ **采纳前须回查** ✓

## 二 · 按类分列（★ 先看最危险的 `unit_diff` / `mark_diff`）

### `unit_diff`（15 条）

- **`ConeParams`**
  - ★ `Remarks`：The half angle, origin, and radius parameters are in meters.
  - ★ 示例：`" & vCone(7) * 57.3 & " deg"`（`Locate_Apex_of_Conical_Face_Example_VB.md`）
  - ★ 判读：Remarks 说 half angle 以米计；示例把 vCone(7) 当弧度，乘 57.3（度/弧度）后打印 deg，紧邻上一行还注明 1 radian = 57.3º。同一个元素不能既是米又是弧度。
- **`FeatureCircularPattern4`**
  - ★ `Remarks`：Spacing between each instance of the circular pattern; total angle in radians if EqualSpacing is true
  - ★ 示例：`myModel.FeatureManager.FeatureCircularPattern4 3, 1.25663706143592, True, "NULL", False, False, False`（`Get_Cosmetic_Threads_in_a_Part_Document_Example_VB.md`）
  - ★ 判读：成员页把弧度口径限定在 EqualSpacing=true；示例 EqualSpacing=False 仍传 1.25663706143592（=72°弧度），两侧不能同时成立
- **`FeatureLinearPattern4`**
  - ★ `Remarks`：- **Offset1**: Offset in meters from a selected reference in Direction 1 (see **Remarks**); valid only if HasOffset1 is true
  - ★ 示例：`* 0.l9 (Offset1; furthest instance in Direction 1 is offset by 190 mm`（`Create_Linear_Pattern_Example_VB.md`）
  - ★ 判读：页面写 Offset1 以米计、示例注释把同一个 0.19 说成 190 mm；同一行的 Spacing2 同样：页面「in meters」对示例「* 0.02 (Spacing2 in mm)」。
- **`FieldOfViewAngle`**
  - ★ `Remarks`：Camera's horizontal angle of the field of view in radians
  - ★ 示例：`swCamera.FieldOfViewAngle * 1000.0 + " mm"`（`Insert_Camera_Example_CSharp.md`）
  - ★ 判读：成员页写明该量是弧度；示例却对它做 ×1000 的米→毫米换算并标 mm。弧度不是长度、不能换算成毫米，两侧不能同时成立。
- **`FieldOfViewAngle`**
  - ★ `Remarks`：Camera's horizontal angle of the field of view in radians
  - ★ 示例：`swCamera.FieldOfViewAngle * 1000# & " mm"`（`Insert_Camera_Example_VB.md`）
  - ★ 判读：同上：VBA 示例对同一量做 ×1000 并标 mm，与成员页的弧度口径冲突。
- **`FieldOfViewAngle`**
  - ★ `Remarks`：Camera's horizontal angle of the field of view in radians
  - ★ 示例：`swCamera.FieldOfViewAngle * 1000.0# & " mm"`（`Insert_Camera_Example_VBNET.md`）
  - ★ 判读：同上：VB.NET 示例对同一量做 ×1000 并标 mm，与成员页的弧度口径冲突。
- **`GetEnvironment`**
  - ★ `Remarks`：All numeric values returned from the IEnvironment object are relative to a unit text height of 1.0.; i.e., if a symbol has a text height of 0.15, then multiply the numeric values returned by 0.15.
  - ★ 示例：`        Debug.Print ("        " & lineSymbols(i))`（`Analyze_Text_and_Geometry_in_GTol_Flat_Symbol_Example_VB.md`）
  - ★ 判读：Remarks 说所有数值按字高 1.0 归一、须再乘实际字高；示例把 GetSymLines 原值直接当坐标打印，未做任何缩放。
- **`GetMergeDistance`**
  - ★ `Remarks`：By default, points within 0.001mm are merged.
  - ★ 示例：`Debug.Print " Merge distance: " & (importData.GetMergeDistance("") * 1000#) & " mm"`（`Import_DXF_File_into_Part_Sketch_Example_VB.md`）
  - ★ 判读：Remarks 唯一的量级线索用 mm，示例却必须先 *1000 才得到 mm，说明返回是米制；照 Remarks 读成 mm 会差 1000 倍，两侧口径不能同时成立。
- **`GetRowHeight`**
  - ★ `Remarks`：Height of the specified row in meters
  - ★ 示例：`RowHeight = swTableAnn.GetRowHeight(J);`（`C:\swapi\examples\Get_Components_in_Each_BOM_Table_Row_Example_CSharp.`）
  - ★ 判读：本成员页写米；示例该调用绑在 TableAnnotation 声明上，同名 ITableAnnotation.GetRowHeight 的 Returns 写 in system units，两套口径不能同时成立。
- **`InsertSewRefSurface`**
  - ★ `Remarks`：A knit tolerance's:

- lower limit is 0.0001 mm

- upper limit is 0.1 mm
  - ★ 示例：`Debug.Print("  Knit tolerance: " + swSurfaceKnitFeature.KnitTolerance * 1000 + " mm");`（`Create_Surface_Knit_Feature_Example_CSharp.md`）
  - ★ 判读：示例回读后要 ×1000 才标 mm，说明裸值单位是米；0.0001 裸值即 0.1 mm，与 Remarks「下限 0.0001 mm」不能同时成立。
- **`InsertSewRefSurface`**
  - ★ `Remarks`：A knit tolerance's:

- lower limit is 0.0001 mm

- upper limit is 0.1 mm
  - ★ 示例：`swNewFeatMgr.InsertSewRefSurface(true, false, false, 3.001639406912E-05, 0.0001);`（`Fill_Holes_in_Part_Example_CSharp.md`）
  - ★ 判读：KnitTolerance 传 3.001639406912E-05；按 Remarks 的 mm 口径它低于 0.0001 mm 下限，按米口径才等于 0.03 mm 落在区间内。
- **`IsTolerant`**
  - ★ `Remarks`：Tolerance: Edge tolerance or gap in meters
  - ★ 示例：`Gap size (or tolerance) in mm of each edge or vertex.`（`Get_Maximum_Edge_and_Vertex_Gaps_Example_VB.md`）
  - ★ 判读：成员页说 out 参数是米，示例说同一间隙是 mm 且直接比较打印；差 1000 倍，不能同时成立。
- **`MaxValueForGapRange`**
  - ★ `Remarks`：Maximum gap should be in the range of [[ISurfaceKnitFeatureData::KnitTolerance]] to 1 mm.
  - ★ 示例：`            Debug.Print("  Maximum value for gap range: " + swSurfaceKnitFeature.MaxValueForGapRange * 1000 + " mm");`（`Create_Surface_Knit_Feature_Example_CSharp.md`）
  - ★ 判读：Remarks 把该值范围直接写成 mm（Returns 另写 0.01 mm~1 mm）；示例读回后 ×1000 再拼 ' mm'，即按米读同一数值 ⇒ 单位口径不能同时成立。
- **`SetSystemValue3`**
  - ★ `Remarks`：Sets the value of this dimension in system units (meters) in the specified configuration.
  - ★ 示例：`' Change D3 of LocalCirPattern1 from 360 degrees to 270 degrees (4.72 radians)`（`Change_Dimension_Example_VB.md`）
  - ★ 判读：成员页称该入参一律以米计（Parameters 亦写 NewValue: Dimension value in meters），示例却把同一入参当弧度用（4.72 rad=270°，把 360° 改为 270°）；两者不能同时成立。
- **`SetupSheet6`**
  - ★ `Remarks`：Multiplying ZoneRow by ZoneCol equals the total number of zones in the zone area of this drawing sheet. The zone area is specified by ZoneLeftMargin, ZoneRightMargin, ZoneTopMargin, and ZoneBottomMargin.
  - ★ 示例：`0.2794, 0.2159, "Default", False, 0.5, 0.5, 0.5, 0.5, 3, 3)`（`Create_Drawing_Sheet_Zones_Example_VB.md`）
  - ★ 判读：同一次调用里 Width/Height 用米（0.2794/0.2159），四个 Zone 边距却是 0.5；同一单位下边距大于整张图，成员页又未标边距单位。

### `mark_diff`（10 条）

- **`AutoDimension2`**
  - ★ `Remarks`：Select and mark a unique vertical edge, vertex, sketch point, or vertical sketch line as the datum for the horizontal dimensioning scheme, using swAutodimMarkHorizontalDatum as the mark value.
  - ★ 示例：`bRet = swSketchSegVert.Select4(True, Nothing)`（`Autodimension_All_Sketches_Example_VB.md`）
  - ★ 判读：备注要求基准必须打 swAutodimMark* 标记；示例用没有 mark 形参的 Select4 选基准却声明成功。
- **`EditMate3`**
  - ★ `Remarks`：The two mated items must be selected with a selection mark of 1.
  - ★ 示例：`        '   IAssemblyDoc::EditMate3 requires that mate entities
        '   be selected with mark of 1 except for:
        '       swMateCAMFOLLOWER
        '  `（`Edit_Mate_Example_VB.md`）
  - ★ 判读：Remarks 把 mark=1 写成无条件硬要求；示例明写 cam follower face 用 8、symmetry plane 用 4，两者不可同时成立。
- **`FeatureExtruRefSurface2`**
  - ★ `Remarks`：Sketch; call [[IModelDocExtension::SelectByID2]] with selection mark 0.
  - ★ 示例：`boolstatus = swModelDocExt.SelectByID2("Sketch1", "SKETCH", 0, 0, 0, false, 4, null, 0);`（`Create_Surface_Knit_Feature_Example_CSharp.md`）
  - ★ 判读：Remarks 规定「Sketch」只用 mark 0，mark 4 仅属「Sketch segments」；示例实体类型正是 SKETCH 却用 mark 4，两条规则不能同时为真。
- **`FeatureExtruRefSurface2`**
  - ★ `Remarks`：Sketch; call [[IModelDocExtension::SelectByID2]] with selection mark 0.
  - ★ 示例：`status = swModelDocExt.SelectByID2("Sketch1", "SKETCH", 0, 0, 0, false, 4, null, 0);`（`Create_Temporary_Bodies_by_Offsetting_Surface_Body_Example_CSharp.md`）
  - ★ 判读：第二份官方示例独立复现同一写法：整草图按名称选中、mark 仍为 4，与 Remarks 给「Sketch」的 mark 0 直接矛盾。
- **`FeatureLinearPattern4`**
  - ★ `Remarks`：- 8388608 to mark a seed instance reference when FromCentroid1 or FromCentroid2 is false
  - ★ 示例：`status = swModelDocExt.SelectByID2("Boss-Extrude2", "SOLIDBODY", 0, 0, 0, True, 256, Nothing, 0)`（`Change_Linear_Pattern_Example_VB.md`）
  - ★ 判读：F4 的 mark 表只有特征/组件两行（1/2/4/2097152/8388608），无 256；示例用 256 选实体，256 只出现在 F5 页「256 to mark the solid bodies to pattern」。
- **`InsertCutSwept5`**
  - ★ `Remarks`：- 1 = Sketch profile or tool body
  - ★ 示例：`status = swModelDocExt.SelectByID2("", "EDGE", -0.0372983839416747, 0.0393904284381961, 0.0495042874504179, true, 4, null, 0);`（`Create_Cut-sweep_Feature_Using_Circular_Profile_Example_CSharp.md`）
  - ★ 判读：Remarks 把 mark 1（草图轮廓/工具体）列为无条件前置；CircularProfile=true 的三份示例只选 mark 4 一条边，mark 1 一次都没用。
- **`InsertCutSwept5`**
  - ★ `Remarks`：- 2 = Guide curve, if provided

- 4 = Sweep path
  - ★ 示例：`status = swModelDocExt.SelectByID2("Boss-Extrude1", "SOLIDBODY", 0, 0, 0, true, 2048, null, 0);`（`Create_Cut-sweep_Feature_Using_Tool_Body_Example_CSharp.md`）
  - ★ 判读：Remarks 只枚举 1/2/4 三个 mark；工具体示例在 mark 1 与 4 之外，还用 mark 2048 选了第三个实体。
- **`InsertMoveCopyBody2`**
  - ★ `Remarks`：Rotation edge, vertex, coordinate system

2
  - ★ 示例：`status = swModelDocExt.SelectByID2("", "VERTEX", -0.085, 0, 0.065, True, 4, Nothing, 0)
status = swModelDocExt.SelectByID2("", "VERTEX", -0.085, -0.09, 0.065, T`（`Copy_and_Rotate_Body_using_Edge_Example_VB.md`）
  - ★ 判读：Remarks 把旋转参考实体定为 mark 2；示例这一次调用传的是旋转原点（RotPoint）却只用 mark 4/8（平移 mark），旋转的 2 从未出现。
- **`InsertProtrusionBlend2`**
  - ★ `Remarks`：- 2 = guide curve selections
  - ★ 示例：`status = swModelDocExt.SelectByID2("Sketch3", "SKETCH", 0, 0, 0, true, 4098, null, 0);`（`Get_Guide_Curves_in_Loft_Feature_Example_CSharp.md`）
  - ★ 判读：Remarks 只列 mark=2 作引导曲线；示例传 4098（=4096+2），4096 位在官方 mark 表与 swSelectOption_e（仅 0/1）中无出处。
- **`InsertWeldmentTrimFeature2`**
  - ★ `Remarks`：- 1 = Body or bodies to trim

- 2 = Trimming boundaries (body or face)
  - ★ 示例：`= Part.Extension.SelectByID2("Structural Member1[2]", "SOLIDBODY",
0, 0, 0, true, 2, null, 0);
boolstatus
= Part.Extension.SelectByID2("Structural Member1[1]", `（`Insert_Weldment_Features_Example_CSharp.md`）
  - ★ 判读：先选者标 mark2 落 v1=BodiesToTrim，后选标 mark1 落 v2=BodiesOrFaces，与 Remarks 的 1=待裁、2=裁边正好相反。

### `return_shape_diff`（75 条）

- **`AddToolbarCommand2`**
  - ★ `Remarks`：If ButtonEnableMethod returns...

**Then SOLIDWORKS Design...**

0

Deselects and disables the menu item

1

Deselects and enables the menu item; this is the default menu state if no update function is specified
  - ★ 示例：`    Function ButtonEnableMethod() As Boolean
        ' TODO: Add your implementation here
    End Function`（`Add_Toolbars_Example_VBNET.md`）
  - ★ 判读：Remarks 要求该方法返回 0 至 3 的整数状态；VB.NET 示例把它声明为 Boolean 且函数体只有 TODO，无返回值，永远给不出 2 或 3。
- **`CreateBodyFromBox`**
  - ★ `Remarks`：[[Body]]
  - ★ 示例：`swBoxBody = (Body2)swModeler.CreateBodyFromBox((vBoxArr));`（`Create_Solid_Bodies_using_Geometry_and_Topology_APIs_Example_CSharp.md`）
  - ★ 判读：页面 Returns 指向 Body，示例却把返回值转成 Body2 并调 Check3/Operations2；本地类型树只有 IBody2，无 IBody。
- **`EntityParams`**
  - ★ `Remarks`：To define the mate entity, the following information is returned based on the mate type.
  - ★ 示例：`Debug.Assert 7 = UBound(vEntParam)`（`Get_Mate_Definition_Example_VB.md`）
  - ★ 判读：Remarks 表里 swMatePoint 只返回 pointX/Y/Z 三个量（数组长 3）；示例对任意配合实体一律断言 UBound=7（长 8）并读满 0..7，两种返回长度不能同时成立。
- **`EnumDocuments2`**
  - ★ `Remarks`：The list of [[IModelDoc2]] objects contained in the [[IEnumDocuments2]] object contain any open IModelDoc2 pointer. This includes IModelDoc2 objects that may have been opened as file references, for example, from an assembly or drawing.
  - ★ 示例：`LPENUMDOCUMENTS pDocEnum
= NULL;
hres = TheApplication->m_pSldWorks->EnumDocuments2(&pDocEnum);`（`Traverse_All_Open_Documents_Example_CPlusPlus_COM.md`）
  - ★ 判读：Remarks 指返回 IEnumDocuments2 且元素是 IModelDoc2；示例取的是 LPENUMDOCUMENTS / LPMODELDOC 这一代旧接口，两者不是同一个返回对象。
- **`ExternalState`**
  - ★ `Remarks`：The return value for each event is a double that specifies the new force or torque magnitude.
  - ★ 示例：`return 1;`（`sldworksapi__Fire_Events_for_External_Output_Time_Step_Changes_Example`）
  - ★ 判读：Remarks 说返回值是 double 幅值；示例处理器声明为 int 并返回 1，幅值另写入 ref 参数数组。
- **`FirstPlane`**
  - ★ `Remarks`：[[Plane]] or [[planar face]]
  - ★ 示例：`p1 = (Feature)data.FirstPlane;`（`Get_Section_View_Data_Example_CSharp.md`）
  - ★ 判读：该句出自页面 Returns 段，说取值是 Plane 或 planar face；读取示例却强转 Feature 并调 Feature.Select2，写入侧 Create 示例也把 Feature 塞回去。
- **`FixedReference`**
  - ★ `Remarks`：Fixed reference entity (edge or face)
  - ★ 示例：`    Set swFixedFace = swSheetMetal.FixedReference
    If Not swFixedFace Is Nothing Then
        Debug.Print "A fixed face or fixed edge is selected."`（`Get_Template_Sheet_Metal_Feature_Data_Example_VB.md`）
  - ★ 判读：页面承诺返回值可能是边，示例却声明为 Face2 并直接赋值后又打印「fixed edge」；真返回边时该转换不成立。
- **`GetAttachedEntities2`**
  - ★ `Remarks`：COM applications can use QueryInterface to obtain the specific object from the LPUNKNOWN pointer.
  - ★ 示例：`swEntity = (Entity)attachedEntityArray[i];`（`Get_BOM_Balloon_Properties_Example_CSharp.md`）
  - ★ 判读：Remarks 说元素是 LPUNKNOWN、须经 QueryInterface 取具体对象；示例把元素直接硬转 Entity 并调 GetComponent()，与 Remarks 的 IFace2/IEdge/IVertex 表不能同时成立。
- **`GetAttachedEntities3`**
  - ★ `Remarks`：COM applications can use QueryInterface to obtain the specific object from the LPUNKNOWN pointer.
  - ★ 示例：`swEntity = (Entity)vAttEntArr[i];`（`Attach_Annotation_to_Entity_Example_CSharp.md`）
  - ★ 判读：Remarks 要求经 QueryInterface 取具体对象；示例把元素直接硬转 Entity 再调 Select4，与 Remarks 的对象类型表不能同时成立。
- **`GetCentermarks`**
  - ★ `Remarks`：This method returns an empty array for center marks that are annotations; thus, this method is only valid for center marks that are features.
  - ★ 示例：`Debug.Assert
Not IsEmpty(vCenterMarkArr)`（`List_Center_Marks_in_Drawing_Example_VB.md`）
  - ★ 判读：Remarks 称中心标记现已是注解且对注解返回空数组；示例前置只要求「有中心标记的工程图」，却断言返回数组非空，两说不能同时成立。
- **`GetConfigurationParamsCount`**
  - ★ `Remarks`：Number of parameters in this configuration
  - ★ 示例：`hr
= pCfgMgr->GetConfigurationParamsCount(sCfgName,
&NumParams);`（`Get_Configuration_Parameters_Example_CPlusPlus_COM.md`）
  - ★ 判读：页面 Returns 说返回参数个数(int)，示例却把返回值赋给 HRESULT hr，真正的个数改从第二个出参 NumParams 读。
- **`GetDependencies2`**
  - ★ `Remarks`：If AddReadOnlyInfo is set to True, then a string of True or false is added to the list of strings. If Part1 is read-only, then the resulting set of strings would be:
  - ★ 示例：`vDepend
= swModel.GetDependencies2(True,
True, True)
Debug.Print
swModel.GetPathName
For
i = 0 To (UBound(vDepend) - 1) / 2`（`Get_Active_Document_Dependents_Example_VB.md`）
  - ★ 判读：Remarks：AddReadOnlyInfo=True 时每个依赖多一个 True/false 串 ⇒ 每文档 3 个。示例正是用 True 调用，却按 (UBound-1)/2 与 2i/2i+1 按每文档 2 个配对。两说不能同时成立。
- **`GetDetailCircleCount2`**
  - ★ `Remarks`：Call this method before calling [[IView::GetDetailCircles]] to get the size of the array for that method.
  - ★ 示例：`vDetCirc
= swView.GetDetailCircleInfo2
nNumDetCirc
= swView.GetDetailCircleCount2(nSize)
Debug.Assert
nNumDetCirc = vDetCirc(0)
Debug.Assert
nSize = UBound(vDet`（`Get_Detail_Circle_Information_Example_VB.md`）
  - ★ 判读：Remarks 说 Size 是 GetDetailCircles 的数组尺寸，参数段说每局部圆一个 double；示例却断言 Size 等于 GetDetailCircleInfo2 全部 double 数（按其 Remarks 为 1+16n+9A）。两值一般不等。
- **`GetDisplayState`**
  - ★ `Remarks`：True if the setting specified is turned on, false if not
  - ★ 示例：`"  Sectioned = " & swModView.GetDisplayState(swIsViewSectioned)`（`Get_Display_State_Example_VB.md`）
  - ★ 判读：签名与 Returns 段给出 System.bool；示例把返回值用 & 拼进字符串，VBA 中 Boolean 作 & 操作数报 Type mismatch，两者不能同时成立。
- **`GetDistance`**
  - ★ `Remarks`：0 if success; -1 if failure
  - ★ 示例：`Debug.Print("IEquity::GetDistance return value (0 = success; 1 = failure) : " + retval);`（`Get_Distance_Between_Entities_Example_CSharp.md`）
  - ★ 判读：成员页写失败返回 -1；示例打印 0=成功、1=失败，失败码取值不同。
- **`GetExplodedViewNames`**
  - ★ `Remarks`：Array of strings of the names of the exploded views in the active configuration
  - ★ 示例：`vViewName = (object[])swAssembly.GetExplodedViewNames();`（`Create_Exploded_Views_Example_CSharp.md`）
  - ★ 判读：页面说返回字符串数组，C# 示例声明 object[]、接成 object[] 且逐元素 (string) 转换；而后继 Names2 的示例接成 string[]。
- **`GetFarSideElements`**
  - ★ `Remarks`：Array of far side hole elements
  - ★ 示例：`swCounterBoreFar = featdata.GetFarSideElements(0)`（`Create_Advanced_Hole_Example_VBNET.md`）
  - ★ 判读：成员页签名是零参、返回整组远端元素数组；VB/VB.NET 示例却按下标传参并把返回值当单个元素赋值，两者不能同时成立。
- **`GetFirstDocument`**
  - ★ `Remarks`：If the document first opened is an assembly, then this method returns the name of the first component document opened in that assembly.
  - ★ 示例：`ModelDoc2 modDoc = (ModelDoc2)iSwApp.GetFirstDocument();`（`Add_.NET_Controls_to_SOLIDWORKS_Using_an_Add-in_Example_CSharp.md`）
  - ★ 判读：Remarks 说装配体情形返回的是 name（名字/字符串），示例却无条件强转 ModelDoc2 并当文档对象遍历；两者不能同时成立。
- **`GetGuideCurvesType`**
  - ★ `Remarks`：See [Accessing Selections that Define Features](<../../docs/Programming with the SOLIDWORKS API/Selections that Define Features.md>) for additional details on using this method.
  - ★ 示例：`Debug.Print (" Type of feature: " & swLoftFeatureData.GetGuideCurvesType(i))`（`Get_Guide_Curves_in_Loft_Feature_Example_VB.md`）
  - ★ 判读：成员签名零参、返回类型数组；VBA/VB.NET 却传索引取单值，C# 则零参强转 int[]，两侧不能同时成立
- **`GetImportFileData`**
  - ★ `Remarks`：[[IGES import data]] or [[DXF/DWG import data]]
  - ★ 示例：`swImportStepData = (ImportStepData)swApp.GetImportFileData(stepFileName);`（`Import_STEP_File_Example_CSharp.md`）
  - ★ 判读：页面 Returns 只给 IGES / DXF-DWG 两种导入数据对象；示例把返回值强转成 ImportStepData 并用其 MapConfigurationData。
- **`GetLeaderPointsAtIndex`**
  - ★ `Remarks`：retval[0] = X-coordinate of first leader point
  - ★ 示例：`ReDim leaderPt(nNumPts) As Double`（`Get_Display_Dimensions,_Gtols,_and_Surface-Finish_Symbols_Example_VB.m`）
  - ★ 判读：Remarks 返回数组每点 3 分量（3 点即 retval[0..8]）；示例按点数 ReDim，定尺口径不同。
- **`GetMotionStudy`**
  - ★ `Remarks`：This method gets the names of both SOLIDWORKS Simulation and SOLIDWORKS Motion studies.
  - ★ 示例：`Set swMotionStudy1 = swMotionMgr.GetMotionStudy("PhysSim")`（`Get_Motion_Study_Example_VB.md`）
  - ★ 判读：Remarks 说本方法「取名字」；示例按名字取回的是 MotionStudy 对象，从不返回名字数组（取名字的是 GetMotionStudyNames）。两句不能同时成立。
- **`GetNamedEntitiesCount`**
  - ★ `Remarks`：**Signature**: `System.int GetNamedEntitiesCount()`
  - ★ 示例：`hr
= pPart->GetNamedEntitiesCount
(&nEntCount);`（`Get_Named_Entities_Example_CPlusPlus_COM.md`）
  - ★ 判读：成员页（Interop 形态）是一个无参返回 int；C++ 官方示例是填 long* 出参、回 HRESULT。同一次调用不可能同时是这两种形态。
- **`GetObjectByPersistReference3`**
  - ★ `Remarks`：Objects returned by IModelDocExtension::GetObjectByPersistReference3 are often features, including IConfiguration, IRefPlane, and IRefAxis objects. You must first obtain a reference to a feature, and then use IFeature::GetSpecificFeature2 to get the original o
  - ★ 示例：`Debug.Assert(swSelObj Is swObj)`（`Use_Persistent_Reference_Example_VB.md`）
  - ★ 判读：Remarks 说返回值是基类、原对象须再经 GetSpecificFeature2；示例却断言返回值与选中对象同一引用，且前置只写「Select an entity」未排除特征，两种身份判定不能同时成立。
- **`GetPMIData`**
  - ★ `Remarks`：[[IPMIDatumData]], [[IPMIDimensionData]], [[IPMIGtolData]]; null or Nothing if the model is a drawing or no PMI data is associated with this annotation (see **Remarks**)
  - ★ 示例：`swPMIDatumData = (PMIDatumData)swAnnotation.GetPMIData();
Debug.Print("PMI datum data");
if (swPMIDatumData.GetDatumType() == (int)swPMIDatumType_e.swPMIDatumTy`（`Get_PMI_Data_Example_CSharp.md`）
  - ★ 判读：Returns 明说可返回 null/Nothing；示例 datum 分支取回后立即解引用 GetDatumType() 而不判空，同文件另两分支却有 != null 判，两侧对同一返回形状不能同时成立。
- **`GetParent`**
  - ★ `Remarks`：If the component is the root component or a top-level component, then this method returns NULL.
  - ★ 示例：`Set swParentConfig = swConfig.GetParent`（`Display_Configuration_Description_in_Bill_of_Materials_Example_VB.md`）
  - ★ 判读：示例对 Configuration 调用，IConfiguration::GetParent 回 Configuration 且另有 Remarks；本页讲父组件，NULL 语义不适用。
- **`GetPartingLinesCount`**
  - ★ `Remarks`：Call this method before calling [[IDraftFeatureData2::IGetPartingLines]] to determine the size of the array for that method.
  - ★ 示例：`Debug.Print("    Number of parting lines: " + swPartingSurfaceFeatureData.GetPartingLinesCount());`（`Get_and_Set_Parting_Surface_Feature_Data_Example_CSharp.md`）
  - ★ 判读：示例对象是 PartingSurfaceFeatureData，其同名页签 System.int，本页签 System.short。
- **`GetPersistReferenceCount3`**
  - ★ `Remarks`：**Signature**: `System.int GetPersistReferenceCount3( System.object DispObj )`
  - ★ 示例：`long sizePersistIDs;
swDocExt->GetPersistReferenceCount3(disp, &sizePersistIDs);`（`Get_Object_s_Persistent_Reference_ID_Example_CPlusPlus_COM.md`）
  - ★ 判读：成员页为 1 参回 int；示例按 2 参调用（第二参 out long）并取其值。同一成员两种调用形态不能同时成立。
- **`GetRelatedTangentEdgeCount`**
  - ★ `Remarks`：Array of visible tangent edges for the specified bendline
  - ★ 示例：`nbrRelatedTangentEdges = swView.GetRelatedTangentEdgeCount(BendlinesArr(i))`（`Get_Tangent_Edges_of_Bendlines_Example_VB.md`）
  - ★ 判读：页面自身签名是 System.int、摘要也写 number，示例更把它当 Long 计数打印并与 >0 比较；Returns 却写 Array —— 计数与数组不能同时成立。
- **`GetSelectedObject6`**
  - ★ `Remarks`：ISelectionMgr object obtained from a part or assembly document

[[IComponent2]] object.
  - ★ 示例：`swFeat = (Feature)swSelMgr.GetSelectedObject6(1, -1);`（`Access_and_Release_Access_to_Edges_Example_CSharp.md`）
  - ★ 判读：Remarks 的条件只说 ISelectionMgr 取自哪种文档，没说要选中什么；此例 swSelMgr 来自 box.sldprt（零件），按 Remarks 该情形必返 IComponent2，实际返的是 Feature。两条不能同时成立。
- **`GetSelectedObject6`**
  - ★ `Remarks`：ISelectionMgr object obtained from a part or assembly document

[[IComponent2]] object.
  - ★ 示例：`Set segments(0) = swSelMgr.GetSelectedObject6(1, 0)`（`Access_Structure_System_Corner_Treatments_Example_VB.md`）
  - ★ 判读：同上：swSelMgr 取自 weldment_box.sldprt（零件），返回值被当作草图线段喂给 SetPathSegments。按 Remarks 此情形必须返回 IComponent2，与示例直接冲突（C# 版同型）。
- **`GetSelectionFilters`**
  - ★ `Remarks`：Array of long values representing the [[swSelectType_e]] enumeration
  - ★ 示例：`vFilters = (int[])swApp.GetSelectionFilters();`（`Inspect_Facets_Example_CSharp.md`）
  - ★ 判读：冲突出自 Returns 行：页称元素为 long，C# 例把它强转成 int[]；若真为 long[] 该强转会抛异常，两说不能同时成立。
- **`GetSolidHatchCount`**
  - ★ `Remarks`：- **ArraySize**: Number of solid-fill hatches

## Returns
Size of the array for the solid-fill hatches boundary data
  - ★ 示例：`nbrSolidFillHatches = swView.GetSolidHatchCount(out ArraySize);
                file.WriteLine(" Number of solid-fill hatches in this view: " + nbrSolidFillHatc`（`Get_Solid-fill_Hatch_Information_Example_CSharp.md`）
  - ★ 判读：成员页说返回值是数组长度、ArraySize 是孔数；三份示例都把返回值当孔数、ArraySize 当数组长度，二者对调。
- **`GetSplinesInterpolate`**
  - ★ `Remarks`：This complete set of data repeats itself for each spline found in the sketch. For each spline, the array returned contains the number of spline points in the spline, and the X,Y,Z value for each of those points.
  - ★ 示例：`long splineArraySize = 1
 + (nbrSketchPoints * 3);`（`Get_Spline_Points_Example_CPlusPlus_COM.md`）
  - ★ 判读：Remarks 说每条样条各重复一组 [N, x,y,z…]；示例按单一 1+N*3 定长取值。多样条草图时实际长度应为 Σ(1+3Ni)，与 1+3ΣNi 不能同时成立。
- **`GetSplinesInterpolate`**
  - ★ `Remarks`：The return value is an array of doubles formatted as:

[ [NumSplinePoints, [x, y, z] ], ]
  - ★ 示例：` //First value in vSplines array is the number of
//sketch (or spline) points, followed by the x, y, z
//coordinates of each point in the spline`（`Get_Spline_Points_Example_CPlusPlus_COM.md`）
  - ★ 判读：Remarks 说首元素是本条样条的 NumSplinePoints；示例首元素取自 GetSketchPointsCount2（整草图点数），两者只在单样条草图上巧合相等。
- **`GetSubAssemblyExplodeSteps`**
  - ★ `Remarks`：Array of [[IExplodeSteps]] in the subassembly explode view
  - ★ 示例：`Set nestedStep = steps(j)`（`Add_Explode_Step_Example_VB.md`）
  - ★ 判读：页面称元素为 IExplodeSteps（本机官方类型树无此接口）；示例把元素当 SldWorks.ExplodeStep 取并读 .Name。
- **`GetSuppression`**
  - ★ `Remarks`：Suppression state of this component instance as defined in [[swComponentSuppressionState_e]]
  - ★ 示例：`hres = swComponent->GetSuppression(&lComponentSuppressState);`（`Access_Assembly_Example_CPlusPlus_COM.md`）
  - ★ 判读：成员页签名是 `System.int GetSuppression()`，零参、状态即返回值；C++ 示例却传一个 long 出参、把返回值当 hres(HRESULT)，状态从参数取 —— 两种调用形状不能同时成立。
- **`GetSustainability`**
  - ★ `Remarks`：[[ISustainabilityApp]]
  - ★ 示例：`sustain = (swgsustainabilityApp)PDoc.Extension.GetSustainability();`（`Calculate_Environmental_Impact_of_Part_Example_CSharp.md`）
  - ★ 判读：成员页 Returns 写 ISustainabilityApp，示例强转到 swgsustainabilityApp，两个接口名不同。
- **`GetTessPts`**
  - ★ `Remarks`：The array returned contains the x, y, z location of the tessellation points:
  - ★ 示例：`For i = 0 To UBound(vTessPts) Step 6`（`Get_Intersecting_Faces_Example_VB.md`）
  - ★ 判读：页面是每点 3 个 double 的点表；本示例按 6 个一组取线段，另两份官方示例用 Step 3。两种步长不能同时为正解。
- **`GetUnloadedComponentNames`**
  - ★ `Remarks`：To get whether an assembly has hidden or suppressed unloaded components, call [[IAssemblyDoc::HasUnloadedComponents]].
  - ★ 示例：`if (Reasons[index] == 1)`（`Get_Hidden_Components_Filenames_Example_CSharp.md`）
  - ★ 判读：页面参数表说该数组按 swComponentLoadStatus_e 三值（Unknown/Hidden/Suppressed）返回；C# 示例只判 ==1、其余全当 suppressed，VBA 版更直接赋给 Boolean，两者都把 Unknown 与 Suppressed 混为一谈。
- **`GetUserPoints2`**
  - ★ `Remarks`：This set of data repeats for each user point in the sketch. The size of the array is (NumPts * 8).
  - ★ 示例：`For i = 0 To UBound(vSketchUserPt) / 3 - 1
        ' Coordinates in sketch space
        Debug.Print " User point (" & i & ") = (" & vSketchUserPt(3 * i + 0) * `（`Get_Sketch_Points_and_Their_Persistent_IDs_Example_VB.md`）
  - ★ 判读：Remarks：每点 8 个 double，前 5 槽是 Color/Line Font/Line Width/Layer ID/Layer Override，坐标在第 5–7 槽。示例按每点 3 个、偏移 3*i 直接当 x,y,z 读；按 8 槽布局，3*i 落在第 i 点的第 4 槽（i=0 时正是 Color）。两种数组布局不能同时成立。
- **`GroupCount`**
  - ★ `Remarks`：use this property to get a range of valid values for [[ICenterMark::GetExtendedLength]]'s and [[ICenterMark::SetExtendedLength]]'s GroupID parameter. You can use a value from 0 to the number of center marks in a center mark set for the GroupID parameter.
  - ★ 示例：`Debug.Print(" Number in set: " + (nbrInGroup - 1));`（`Get_and_Set_Center_Marks_Set_Example_CSharp.md`）
  - ★ 判读：Remarks：GroupCount 即 set 内个数、GroupID 可到 GroupCount；示例把 GroupCount-1 当 Number in set。差 1。
- **`IActivateDoc3`**
  - ★ `Remarks`：This file becomes the active document, and this method returns a pointer to that document object.
  - ★ 示例：`hres = swApp->IActivateDoc3(sActiveAssembly,
false, &lErrorActivatingDoc, &swModel);`（`Access_Assembly_Example_CPlusPlus_COM.md`）
  - ★ 判读：成员页写 3 形参、以返回值给出文档指针；示例传 4 实参、文档指针作末位 out，结果收在 hres。
- **`IActivateDoc3`**
  - ★ `Remarks`：This file becomes the active document, and this method returns a pointer to that document object.
  - ★ 示例：`swApp->IActivateDoc3(sAssemblyName,
true, &lErrors, &swModel);`（`Add_Component_and_Mate_Example_CPlusPlus_COM.md`）
  - ★ 判读：第二份官方示例同为 4 实参 + hres，且 errors 复用了 OpenDoc6 已用过的 lErrors。
- **`IAddComponents2`**
  - ★ `Remarks`：**Signature**: `Component2 IAddComponents2( ref System.int Count, ref System.string Names, ref System.double Transforms )`
  - ★ 示例：`= pAssy->IAddComponents2(&nNumComp,
sPartPath, dTransform, swCompArr);`（`Add_Components_and_Transforms_Example_CPlusPlus_COM.md`）
  - ★ 判读：成员页 3 形参、Returns 直接给出 IComponent2 数组指针；示例传 4 实参，数组作末位 out，函数回 HRESULT。
- **`IAddControl`**
  - ★ `Remarks`：**Signature**: `PropertyManagerPageControl IAddControl( System.int ID, System.short ControlType, System.string Caption, System.short LeftAlign, System.int Options, System.string Tip )`
  - ★ 示例：`hres = m_pSwGroup_1->IAddControl(id,
controlType, caption, alignment, options, tip, &m_pSwControl_1_2);`（`Set_Up_PropertyManager_Page_Slider_Control_Example_CPlusPlus_COM.md`）
  - ★ 判读：成员页 6 形参、以返回值给出控件；示例传 7 实参，控件指针作末位 out，函数回 HRESULT。
- **`IGetBCurveParams`**
  - ★ `Remarks`：Pointer to an array of doubles describing the parameters of the curve (see **Remarks**)
  - ★ 示例：`pCurve->IGetBCurveParams( dSplineParams);`（`Get_Curve_Spline_Points_Example_CPlusPlus_COM.md`）
  - ★ 判读：成员页是零参、返回数组指针；示例把调用方 new 出来的数组当输出参数传入，之后自己 delete[]。返回形状不一致。
- **`IGetBCurveParamsSize2`**
  - ★ `Remarks`：Size of the data set returned by [[ICurve::IGetBCurveParams]].
  - ★ 示例：`pCurve->IGetBCurveParamsSize2( FALSE, TRUE,
&nParamSize);`（`Get_Curve_Spline_Points_Example_CPlusPlus_COM.md`）
  - ★ 判读：成员页签名是 2 参回 System.int；示例是 3 参、第 3 个是 long* 输出参数。两个调用形状不能同时成立。
- **`IGetCurveParams2`**
  - ★ `Remarks`：The return value is the following array of 11 doubles:
  - ★ 示例：`edgeData[10]={NULL};`（`Get_Edge_Data_By_Name_Example_CPlusPlus_COM.md`）
  - ★ 判读：Remarks 说返回 11 个 double 且末位是 PackDouble3/SenseFlag；示例只声明 edgeData[10]、最大下标读到 9，SenseFlag 未取，两者不能同时成立。
- **`IGetSplinePts`**
  - ★ `Remarks`：The array returned contains the x, y, z location of the spline points
  - ★ 示例：`pCurve->IGetSplinePts( dSplinePts);`（`Get_Curve_Spline_Points_Example_CPlusPlus_COM.md`）
  - ★ 判读：页说方法“返回”一个数组；示例是调用方 new 出缓冲区再作为实参传入，方法不返回数组。
- **`IGetUnits`**
  - ★ `Remarks`：The format of the returned data is an array of shorts:
  - ★ 示例：`hres
= pModelDoc->IGetUnits(unitArray);`（`Get_and_Set_Units_Example_CPlusPlus_COM.md`）
  - ★ 判读：页说“返回”5 个 short 的数组；示例由调用方声明 short unitArray[5] 传入后从缓冲区读，不接返回值。
- **`IGetVersionHistoryCount`**
  - ★ `Remarks`：Size of array required for the version history
  - ★ 示例：`hres
= pModelDoc->IGetVersionHistoryCount(&versHistCount);`（`Document_Version_History_Example_CPlusPlus_COM.md`）
  - ★ 判读：成员页签名零参、返回 System.int 即数组长度；示例传入 &versHistCount 出参，并把返回值当 HRESULT 判 S_OK。两种出口形态不能同时成立。
- **`INewDocument2`**
  - ★ `Remarks`：Newly created [[document]] or NULL if the operation fails
  - ★ 示例：`hres = swApp->INewDocument2(sDrawingDocTemplate,
lPaperSize, dWidth, dHeight, &swNewModel);`（`Access_Assembly_Example_CPlusPlus_COM.md`）
  - ★ 判读：成员页签名 4 参、返回 ModelDoc2；示例传 5 个实参（第 5 个 &swNewModel 为出参），并把返回值赋给 hr 当状态判。新文档归谁返回，两侧不能同时成立。
- **`ISketchSplineByEqnParams`**
  - ★ `Remarks`：True if created successfully, false if not
  - ★ 示例：`hr
= pModel->ISketchSplineByEqnParams(pPropArray,
pKnotsArray, pCntrlPntCoordArray, &retval);`（`Insert_Spline_in_Drawing_Example_CPlusPlus_COM.md`）
  - ★ 判读：成员页 3 参、返回值即成败布尔；示例多传第 4 个出参 &retval，用 _ASSERT(retval) 判成败，而返回值被当成 hr。
- **`IVersionHistory`**
  - ★ `Remarks`：Array of strings showing the history of the document
  - ★ 示例：`hres
= pModelDoc->IVersionHistory(versionHistStrings);`（`Document_Version_History_Example_CPlusPlus_COM.md`）
  - ★ 判读：成员页签名零参、返回 System.string 即数组本身；示例由调用方 new BSTR[versHistCount] 后传入，并把返回值赋给 hr。数组归谁分配，两侧不能同时成立。
- **`InsertCoordinateSystem`**
  - ★ `Remarks`：Feature InsertCoordinateSystem( System.bool XFlippedIn, System.bool YFlippedIn, System.bool ZFlippedIn )
  - ★ 示例：`bRet = swModel.InsertCoordinateSystem(False, False, False): Debug.Assert bRet`（`Insert_Coordinate_System_at_Center_of_Mass_Example_VB.md`）
  - ★ 判读：同名成员一份示例当 Feature 收（Set swFeat / Is Nothing 判空），另一份当 Boolean 收并 Assert。
- **`InsertFeatureReplaceFace`**
  - ★ `Remarks`：True if the edges match, false if not
  - ★ 示例：`Part.InsertFeatureReplaceFace();`（`Replace_Face_Example_CSharp.md`）
  - ★ 判读：这句在本页 ## Returns 段（不在 ## Remarks）：它说回 True/False，但同一页签名是 void，示例也按无返回值语句调用。
- **`InsertReferencePoint`**
  - ★ `Remarks`：Pointer to the [[IFeature]] object
  - ★ 示例：`    vFeatArr = swFeatMgr.InsertReferencePoint(swRefPointAlongCurve, swRefPointAlongCurveEvenlyDistributed, 0#, 6)
    For Each vFeat In vFeatArr`（`Insert_Reference_Points_Example_VB.md`）
  - ★ 判读：成员页 Returns 说返回单个 IFeature 指针；示例把返回值当数组 For Each 逐个取特征。
- **`IsClosed`**
  - ★ `Remarks`：True if the sketch contour is open, false if closed
  - ★ 示例：`if ((closed == false))`（`Get_Sketch_Contours_Example_CSharp.md`）
  - ★ 判读：示例把 false 映射为 Open、else 映射为 Closed，与成员页「True = open」正好相反，二者不可同时成立
- **`IsClosed`**
  - ★ `Remarks`：True if the sketch contour is open, false if closed
  - ★ 示例：`Debug.Print("  Sketch contour " + i + " is closed? " + skcontour.IsClosed());`（`Create_Extrude_Feature_Using_Sketch_Contours_Example_CSharp.md`）
  - ★ 判读：示例把返回值直接标注为「是否闭合」（true 即闭合），成员页说 true 是 open，语义冲突
- ★ 其余 15 条见 `c4-merged.json` ✓

### `precondition_diff`（324 条）

- **`AddCommandTab`**
  - ★ `Remarks`：If another CommandManager tab exists with the same name, then another CommandManager tab is still created because CommandManager tab names are not unique.
  - ★ 示例：`If Not cmdTab Is Nothing And Not getDataResult Or ignorePrevious Then ' If tab exists, but the registry info is ignored, then re-create the tab; otherwise the I`（`Create_Flyouts_in_the_CommandManager_Example_VBNET.md`）
  - ★ 判读：Remarks 说同名标签照样再建一个、无害；示例说已存在同名标签会导致 ID 不匹配、标签空白，必须先 RemoveCommandTab。同一情形不能既无害又空白。
- **`AddCornerReliefCorner`**
  - ★ `Remarks`：1. Call [[IModelDocExtension::SelectByID2]] with Mark = 0 and Append = true to select the sheet metal body in which to create a corner relief feature.
  - ★ 示例：`swModel.ClearSelection2(true);`（`Create_Corner_Relief_Feature_Example_CSharp.md`）
  - ★ 判读：Remarks 第 1 步要求体以 Mark=0/Append 选中并保留、再由第 2 步追加两面；三份示例都在选完体后立刻 ClearSelection2，调用时选区里只剩两个 Mark=4 的面。
- **`AddDistanceMate`**
  - ★ `Remarks`：2. Call [[IModelDoc2::ClearSelection2]].
  - ★ 示例：`swEnt2.Select4 True, Nothing`（`Add_and_Edit_Distance_Mate_Example_VB.md`）
  - ★ 判读：页面规定取到实体后先 ClearSelection2 再 Select4；示例两次 SelectByRay 后直接 Select4，全程未调 ClearSelection2。
- **`AddExplodeStep2`**
  - ★ `Remarks`：2. Call [[IAssemblyDoc::ShowExploded2]] to activate an explode view.
  - ★ 示例：`Call swModel.AutoExplode`（`Add_Explode_Step_Example_VB.md`）
  - ★ 判读：页面把 ShowExploded2 列为调用前必须步骤；示例只用 AutoExplode 建视图，从未调 ShowExploded2 就调 AddExplodeStep2。
- **`AddFilletedCorners`**
  - ★ `Remarks`：This property is valid only if [[ISMCornerReliefData::ReliefType]] is set to [[swCornerReliefType_e]].swCornerRectangularRelief.
  - ★ 示例：`           cornerItr.AddFilletedCorners = True
           cornerItr.CornerFilletDiameter = 0.00025
           cornerItr.CenterOnBendLines = True
           corn`（`Create_SM_Corner_Relief_Feature_Example_VBNET.md`）
  - ★ 判读：示例第151行以 swCornerTearRelief 收集角，第156行即写 AddFilletedCorners=True，而 ReliefType 到第160行才改成 Rectangular ⇒ 写入时前提不成立。
- **`AddFrame`**
  - ★ `Remarks`：This method is valid only if this Gtol was created in SOLIDWORKS 2022 or later.
  - ★ 示例：`// Preconditions:
// 1. Open a drawing that contains a GTol created with
either SolidWorks 2021 or SolidWorks 2022/2022+.`（`Get_Gtol_Frame_Information_Example_CSharp.md`）
  - ★ 判读：示例前置明确允许 2021 年创建的 Gtol；ConvertFormat 仅在 CanConvertFormat 为真且格式为 GTOL_SW2021 时才尝试且可失败，AddFrame 前无 2022 守卫。
- **`AddMenuItem5`**
  - ★ `Remarks`：Text to show in the SOLIDWORKS Design status bar when the user moves the pointer over this menu item; if you specify HintString, then it must be preceded by a comma
  - ★ 示例：`menuId = iSwApp.AddMenuItem5((int)swDocumentTypes_e.swDocPART, addinID, "MyMenuItem@MyMenu", 0, "MyMenuCallback", "MyMenuEnableMethod", "My menu item", images);`（`Add_Menu_and_Menu_Item_Example_CSharp.md`）
  - ★ 判读：备注要求 HintString 必须以逗号开头；示例第 7 个实参 "My menu item" 无前导逗号。VB.NET 版同样。
- **`AddMenuItem5`**
  - ★ `Remarks`：Text to show in the SOLIDWORKS Design status bar when the user moves the pointer over this menu item; if you specify HintString, then it must be preceded by a comma
  - ★ 示例：`menuId = iSwApp.AddMenuItem5(swDocumentTypes_e.swDocPART, addinID, "MyMenuItem@MyMenu", 0, "MyMenuCallback", "MyMenuEnableMethod", "My menu item", images)`（`Add_Menu_and_Menu_Item_Example_VBNET.md`）
  - ★ 判读：同上：官方示例自身未遵守备注的逗号要求。
- **`AddToolbar5`**
  - ★ `Remarks`：When your add-in is unloaded, you must call [[ISldWorks::RemoveToolbar2]] to remove this toolbar.
  - ★ 示例：`        public bool DisconnectFromSW()
        {
            DetachEventHandlers();
            System.Runtime.InteropServices.Marshal.ReleaseComObject(iSwApp);`（`Add_Toolbars_Example_CSharp.md`）
  - ★ 判读：成员页把卸载时调 RemoveToolbar2 写成必须；C# 示例的卸载路径只解绑事件并释放 COM，没有该调用。
- **`AddToolbar5`**
  - ★ `Remarks`：When your add-in is unloaded, you must call [[ISldWorks::RemoveToolbar2]] to remove this toolbar.
  - ★ 示例：`    Function DisconnectFromSW() As Boolean Implements SolidWorks.Interop.swpublished.SwAddin.DisconnectFromSW
        DetachEventHandlers()
        System.Runti`（`Add_Toolbars_Example_VBNET.md`）
  - ★ 判读：同一条必须步骤；VB.NET 版卸载路径同样只有 DetachEventHandlers 与释放 COM，缺 RemoveToolbar2。
- **`AllowFlip`**
  - ★ `Remarks`：This property is valid only if [[IDragArrowManipulator::ShowOppositeDirection]] is false.
  - ★ 示例：`swDrag.ShowOppositeDirection = true;`（`Create_Drag_Arrow_Manipulator_Example_CSharp.md`）
  - ★ 判读：备注说 ShowOppositeDirection 为 false 时 AllowFlip 才有效；C# 示例设成 true，却又断言 AllowFlip 为 true 并生效，两条不能同时成立。
- **`AllowFlip`**
  - ★ `Remarks`：This property is valid only if [[IDragArrowManipulator::ShowOppositeDirection]] is false.
  - ★ 示例：`swDrag.ShowOppositeDirection = True`（`Create_Drag_Arrow_Manipulator_Example_VBNET.md`）
  - ★ 判读：同一前置在 VB.NET 示例里也被违反：ShowOppositeDirection 设为 True，而备注要求 false。
- **`AnnotationCount`**
  - ★ `Remarks`：Call this method before calling [[IAnnotationView::IGetAnnotations]] to get the size of the array for that method.
  - ★ 示例：`                annotations = (object[])swAnnView.GetAnnotations2(false, false);
                swFeat = (Feature)swAnnView;
                nbrAnnotations = s`（`Get_Where_Annotations_Can_Be_Shown_Example_CSharp.md`）
  - ★ 判读：Remarks 要求先读本属性再取数组，示例顺序相反：因 IGetAnnotations 已 Obsolete 且 C#/VBA 不支持，示例改用无计数字段的 GetAnnotations2
- **`ApplySavedSortScheme`**
  - ★ `Remarks`：1. Set [[IBomTableSortData::SaveCurrentSortParameters]] to true to indicate that the sort settings should be saved in the BOM table in the drawing.
  - ★ 示例：`sortSaved = swSortData.SaveCurrentSortParameters;`（`Sort_Table_Example_CSharp.md`）
  - ★ 判读：成员页要求置 true 才能把排序参数存进图里的 BOM；示例只读取该属性，全篇从未赋 true。
- **`ApplySavedSortScheme`**
  - ★ `Remarks`：3. [[IBomTableAnnotation::GetBomTableSortData]] to populate SortData.
  - ★ 示例：`BomTableSortData swSortData = swSpecTable.GetBomTableSortData();`（`Sort_Table_Example_CSharp.md`）
  - ★ 判读：成员页把取 SortData 列为第 3 步（在 Sort 之后）；示例先调用它，再配置排序参数、再 Sort。
- **`BackgroundImage`**
  - ★ `Remarks`：This property is valid only if [[ISwScene::BackgroundType]] is [[swSceneBackgroundType_e]].swBackgroundType_Image.
  - ★ 示例：`    Scene.BackgroundType = swSceneBackgroundType_e.swBackgroundType_UseEnvironment`（`Get_and_Set_Scene_Properties_Example_VB.md`）
  - ★ 判读：示例把 BackgroundType 设成 UseEnvironment，紧接着就读 Scene.BackgroundImage；Remarks 要求其为 Image 才有效。
- **`BehindSheet`**
  - ★ `Remarks`：This property places a note on the sheet format behind a drawing sheet, which allows you to display the note as watermark in a drawing. Before calling this property, you must call [[IDrawingDoc::EditTemplate]] and [[IDrawingDoc::EditSheet]].
  - ★ 示例：`swDrawing.EditSheet2`（`Place_Note_Behind_Drawing_Sheet_Example_VB.md`）
  - ★ 判读：Remarks 点名必须调 EditSheet；示例调的是 EditSheet2，而 EditSheet 官方页已标 Obsolete、由 EditSheet2 取代。
- **`BlindDepth`**
  - ★ `Remarks`：This property is valid only if [[IAdvancedHoleFeatureData::UseBaselineDimensions]] is set to false, [[IAdvancedHoleElementData::EndCondition]] is set to [[swEndConditions_e]].swEndCondBlind, and the hole element's corresponding override property is set to true
  - ★ 示例：`            swAdvHole_Near_3.Diameter = ConvFactorLength * 0.266;
            swAdvHole_Near_2.BlindDepth = 0.205 * ConvFactorLength;
            swAdvHole_Near`（`Create_Advanced_Hole_Example_CSharp.md`）
  - ★ 判读：示例把 BlindDepth 写到 swAdvHole_Near_2，而其 EndCondition 在第110行已设为 swEndCondUpToNext；本块的 EndCondition=Blind 只给了 Near_3。
- **`BlindDepth`**
  - ★ `Remarks`：This property is valid only if [[IAdvancedHoleFeatureData::UseBaselineDimensions]] is set to false, [[IAdvancedHoleElementData::EndCondition]] is set to [[swEndConditions_e]].swEndCondBlind, and the hole element's corresponding override property is set to true
  - ★ 示例：`swAdvHole_Far_2 = (AdvancedHoleElementData)swModel.Extension.CreateAdvancedHoleElementData((int)swAdvWzdGeneralHoleTypes_e.swAdvWzdStraight);`（`Create_Advanced_Hole_Example_CSharp.md`）
  - ★ 判读：Remarks 只列 Counterbore/Countersink/TaperedTap 三个 EndConditionOverride；IStraightElementData 无此属性，示例却给直孔元素写 BlindDepth。
- **`CalloutString`**
  - ★ `Remarks`：This property is valid only if [[IAdvancedHoleFeatureData::CustomizeCallout]] is set to true.
  - ★ 示例：`Set feat = swFeatureMgr.AdvancedHole2((advHoleNearArr), (advHoleFarArr), False, True, False, ResultArray)`（`Create_Advanced_Hole_Example_VB.md`）
  - ★ 判读：备注把开关挂在 AdvancedHoleFeatureData 的 CustomizeCallout 上；示例改用 AdvancedHole2 第4参，且赋值时特征尚未创建。
- **`Capture3DView`**
  - ★ `Remarks`：This method requires that the SOLDWORKS MBD add-in be loaded. ([[ISldWorks::LoadAddIn]])
  - ★ 示例：`' 1. Open a part or assembly.
' 2. Open an Immediate window.`（`Capture_3DView_Example_VB.md`）
  - ★ 判读：成员页把 MBD 加载项列为硬前置；三份示例的前置清单只有两条且代码从不调 LoadAddIn，两侧不能同时成立。
- **`CenterOnBendLines`**
  - ★ `Remarks`：- [[ISMCornerReliefData::ReliefType]] is set to [[swCornerReliefType_e]].:

  - swCornerCircularRelief

  - swCornerObroundRelief

  - swCornerRectangularRelief
  - ★ 示例：`               cornerItr.CenterOnBendLines = true;
               cornerItr.TangentToBend = true;
               cornerItr.ReliefType = (int)swCornerReliefTyp`（`Create_SM_Corner_Relief_Feature_Example_CSharp.md`）
  - ★ 判读：示例在 ReliefType 仍是 CollectAllCorners 给的 swCornerTearRelief 时就置 true，而 Remarks 三个允许值不含 Tear。
- **`CircularProfileDiameter`**
  - ★ `Remarks`：This property is valid only if [[ISweepFeatureData::CircularProfile]] is set to true.
  - ★ 示例：`swSweep.CircularProfileDiameter = 0#`（`Insert_Bidirectional_Swept-cut_Feature_Example_VB.md`）
  - ★ 判读：该示例上一行是 swSweep.CircularProfile = False，紧接着写直径；按 Remarks 前提此时该属性无效。
- **`ContourLineColor`**
  - ★ `Remarks`：This property is only available when [[IRayTraceRendererOptions::ContourCartoonRenderingEnabled]] is true.
  - ★ 示例：`Debug.Print("  Contour line color = " + swRayTraceRenderOptions.ContourLineColor);`（`Render_Model_Example_CSharp.md`）
  - ★ 判读：Remarks 把该属性的可用性挂在开关上；示例在「取当前值」段就读它，而 ContourCartoonRenderingEnabled = true 出现在同文件第 95 行、读之后。
- **`ContourLineThickness`**
  - ★ `Remarks`：This property is only available when [[IRayTraceRendererOptions::ContourCartoonRenderingEnabled]] is true.
  - ★ 示例：`Debug.Print("  Contour line thickness = " + swRayTraceRenderOptions.ContourLineThickness);`（`Render_Model_Example_CSharp.md`）
  - ★ 判读：Remarks 说仅在开关为 true 时可用；示例先在「取当前值」段读本属性，开关赋值 ContourCartoonRenderingEnabled = true 在其后第 95 行。
- **`CopyDocument`**
  - ★ `Remarks`：There can be no documents open when using this method.
  - ★ 示例：`Preconditions: Open an assembly document.`（`Copy_Document_and_Its_Dependencies_Example_VB.md`）
  - ★ 判读：成员页要求调用时无文档打开；示例前置却要求打开装配体，只靠代码里额外 CloseAllDocuments 才成立。
- **`CornerFilletDiameter`**
  - ★ `Remarks`：This property is valid only if:

- [[ISMCornerReliefData::AddFilletedCorners]] is true,

    - And -

- [[ISMCornerReliefData::ReliefType]] is set to [[swCornerReliefType_e]].swCornerRectangularRelief.
  - ★ 示例：`cornerItr.ReliefType = (int)swCornerReliefType_e.swCornerCircularRelief;`（`Create_SM_Corner_Relief_Feature_Example_CSharp.md`）
  - ★ 判读：示例在该分支随即调用 PrintReliefData，其内部 Debug.Print 读 CornerFilletDiameter；此时 ReliefType 已非 Rectangular，Remarks 的有效条件不成立。
- **`CounterDrillAngle`**
  - ★ `Remarks`：This property is relevant only for swCounterDrilled and swCounterDrilledDrilled holes.
  - ★ 示例：`swFeat = swFeatMgr.HoleWizard((int)swWzdGeneralHoleTypes_e.swWzdCounterBore,`（`Create_Holes_Using_Hole_Wizard_and_Sketch_Points_Example_CSharp.md`）
  - ★ 判读：Remarks 把适用孔型限定为 swCounterDrilled/swCounterDrilledDrilled，示例建的却是 swWzdCounterBore（两者都不是），却照样读取。
- **`CounterDrillDepth`**
  - ★ `Remarks`：This property is relevant only for swCounterDrilled and swCounterDrilledDrilled holes.
  - ★ 示例：`swFeat = swFeatMgr.HoleWizard((int)swWzdGeneralHoleTypes_e.swWzdCounterBore,`（`Create_Holes_Using_Hole_Wizard_and_Sketch_Points_Example_CSharp.md`）
  - ★ 判读：Remarks 把适用孔型限定为 swCounterDrilled/swCounterDrilledDrilled，示例建的却是 swWzdCounterBore（两者都不是），却照样读取。
- **`CounterDrillDiameter`**
  - ★ `Remarks`：This property is relevant only for swCounterDrilled and swCounterDrilledDrilled holes.
  - ★ 示例：`swFeat = swFeatMgr.HoleWizard((int)swWzdGeneralHoleTypes_e.swWzdCounterBore,`（`Create_Holes_Using_Hole_Wizard_and_Sketch_Points_Example_CSharp.md`）
  - ★ 判读：Remarks 把适用孔型限定为 swCounterDrilled/swCounterDrilledDrilled，示例建的却是 swWzdCounterBore（两者都不是），却照样读取。
- **`CounterSinkAngle`**
  - ★ `Remarks`：This property is relevant only for swCounterSunk and swCounterSunkDrilled holes.
  - ★ 示例：`swFeat = swFeatMgr.HoleWizard((int)swWzdGeneralHoleTypes_e.swWzdCounterBore,`（`Create_Holes_Using_Hole_Wizard_and_Sketch_Points_Example_CSharp.md`）
  - ★ 判读：Remarks 把适用孔型限定为 swCounterSunk/swCounterSunkDrilled，示例建的却是 swWzdCounterBore（两者都不是），却照样读取。
- **`CounterSinkDiameter`**
  - ★ `Remarks`：This property is relevant only for swCounterSunk and swCounterSunkDrilled holes.
  - ★ 示例：`swFeat = swFeatMgr.HoleWizard((int)swWzdGeneralHoleTypes_e.swWzdCounterBore,`（`Create_Holes_Using_Hole_Wizard_and_Sketch_Points_Example_CSharp.md`）
  - ★ 判读：Remarks 把适用孔型限定为 swCounterSunk/swCounterSunkDrilled，示例建的却是 swWzdCounterBore（两者都不是），却照样读取。
- **`CreateByExplode`**
  - ★ `Remarks`：' Precondition: Active document contains an exploded view of an assembly.
  - ★ 示例：`' MotionStudy 1 and a collapsed exploded view.`（`sldworksapi__Duplicate,_Delete,_and_Create_Motion_Study_Example_VB.md`）
  - ★ 判读：成员摘要说炸开的是 collapsed 视图，Remarks 前置却要求文档已含 exploded 视图；示例前置写的是 collapsed exploded view，两个状态不能同时成立。
- **`CreateExtrudedBody`**
  - ★ `Remarks`：3. Call [[ISurface::CreateTrimmedSheet4]] or [[ISurface::ICreateTrimmedSheet4]] to create the profile body, passing in either trimmed arcs and lines or untrimmed elliptical curves.
  - ★ 示例：`    Set profileBody = planeSurf.CreateTrimmedSheet((trimCurves))`（`Create_Temporary_Extruded_Body_Example_VB.md`）
  - ★ 判读：Remarks 第 3 步只许 CreateTrimmedSheet4/ICreateTrimmedSheet4；示例调的是无 4 的 CreateTrimmedSheet（官方另页标注 Obsolete）
- **`CreateFeatureMgrWindowFromHandlex64`**
  - ★ `Remarks`：Fully qualified path to the bitmap file that you want to use for the control
  - ★ 示例：`public_documents\\samples\\tutorial\\api\\addin\\pm_extruded_block.bmp`（`Add_.NET_Controls_to_SOLIDWORKS_Using_an_Add-in_Example_CSharp.md`）
  - ★ 判读：Remarks 要求全限定路径；C# 与 VB.NET 两份示例都传相对路径（无盘符），与该前置相反。
- **`CreateMassProperty2`**
  - ★ `Remarks`：A mass properties object with information about one or more components. Before calling this method, call [[IModelDocExtension::SelectByID2]] to pre-select the components.
  - ★ 示例：`MyMassProp = (MassProperty2)Extn.CreateMassProperty2();`（`Get_Mass_Properties_Using_IMassProperty_Example_CSharp.md`）
  - ★ 判读：示例打开的是 98food processor.sldasm（OpenDoc6 传 swDocASSEMBLY），却全程无 SelectByID2、无预选组件，随后直接读出 Mass/Volume/Density。
- **`CreateMate`**
  - ★ `Remarks`：[[IMateFeatureData]] is the base interface for the following mate-specific interfaces (an asterisk indicates that pre-selection of mate entities during mate creation is supported):

- [[IAngleMateFeatureData]]

- [[ICamFollowerMateFeatureData]] *
  - ★ 示例：`            boolstatus = swModel.Extension.SelectByRay(0.00868857956595548, 0.0414144214960288, 0.0633435410960033, -0.520148774728431, -0.59141018013918, -0.61`（`Create_Limit_Angle_Mate_Example_CSharp.md`）
  - ★ 判读：Remarks 只给带星号接口标注可预选实体，IAngleMateFeatureData 无星号；该示例却对角度配合先 SelectByRay 预选两面再赋给 EntitiesToMate。
- **`CreatePlotFeatureData`**
  - ★ `Remarks`：Set the entities for the x-axis and y-axis feature data objects.
  - ★ 示例：`            swSimPlotYAxisFeatureData[0].Entities = swEntityArray;
            swSimPlotYAxisFeatureData[1].Entities = swEntityArray;`（`sldworksapi__Create_Plots_and_Get_Values_Example_CSharp.md`）
  - ★ 判读：Remarks 第 8 步要求 x 轴与 y 轴都设 Entities；示例只给两个 y 轴对象赋 Entities，x 轴对象从头到尾没设，照样出图。
- **`CreatePlotXAxisFeatureData`**
  - ★ `Remarks`：Set the entities for the x-axis and y-axis feature data objects.
  - ★ 示例：`            swSimPlotYAxisFeatureData[0].Entities = swEntityArray;
            swSimPlotYAxisFeatureData[1].Entities = swEntityArray;`（`sldworksapi__Create_Plots_and_Get_Values_Example_CSharp.md`）
  - ★ 判读：Remarks 要求给 x 轴对象也设 Entities；示例建好 x 轴对象后只设 y 轴，x 轴的 Entities 与 Type 全程未赋，仍能出图。
- **`CreatePlotYAxisFeatureData`**
  - ★ `Remarks`：Set the entities for the x-axis and y-axis feature data objects.
  - ★ 示例：`            swSimPlotYAxisFeatureData[0].Entities = swEntityArray;
            swSimPlotYAxisFeatureData[1].Entities = swEntityArray;`（`sldworksapi__Create_Plots_and_Get_Values_Example_CSharp.md`）
  - ★ 判读：同一句 Remarks 同时管 x 轴与 y 轴；示例只落实了 y 轴那一半，x 轴对象从未设 Entities，两条不能同时成立。
- **`CreatePoint2`**
  - ★ `Remarks`：This method creates a point in the active 2D or 3D sketch. If a sketch is not active, the point is not created and NULL is returned.
  - ★ 示例：`    Set pSketchPoint1 = pDrawing.CreatePoint2(0.1, 0.14, 0)`（`Create_Sketch_Line_with_Visual_Properties_Example_VB.md`）
  - ★ 判读：该示例在新建工程图里直接调用，全文未插入任何草图（前置写 None），却把返回的点当作草图实体使用；与「无活动草图则不创建并返回 NULL」不能同时成立。
- **`CreateSectionViewAt5`**
  - ★ `Remarks`：Before calling this method, select the section line or lines to use as a section line.
  - ★ 示例：`    swModel.ClearSelection2 True
    ' Create section-view line
    Set swSketchMgr = swModel.SketchManager
    Set swSketchSegment = swSketchMgr.CreateLine(-1.`（`Create_Section_View_and_Get_Some_Data_Example_VB.md`）
  - ★ 判读：示例调用前显式 ClearSelection2，只用 SketchManager.CreateLine 生成剖切线，全程无 SelectByID2；与 Remarks 要求的“先选中剖切线”不能同时成立。
- **`CreateSeedCutPolygonSides`**
  - ★ `Remarks`：This property is valid only if both are true:

- [[IFillPatternFeatureData::FeaturesToPatternType]] = [[swFeaturesToPatternType_e]].swFeaturesToPatternCreateSeedCut

- [[IFillPatternFeatureData::CreateSeedCutType]] = [[swCreateSeedCutType_e]].swCreateSeedCutPo
  - ★ 示例：`		            swFeatData.CreateSeedCutPolygonSides = 0;
		            swFeatData.CreateSeedCutType = 0;
		            swFeatData.Diagonal = 0.008;
		           `（`Create_Fill_Pattern_Example_CSharp.md`）
  - ★ 判读：示例设 CreateSeedCutType=0（swCreateSeedCutNone）与 FeaturesToPatternType=0（swFeaturesToPatternSelectedFeatures），两个前提都不成立却仍赋该属性并 CreateFeature。
- **`CreateSpline`**
  - ★ `Remarks`：This method creates a spline in the active 2D sketch.
  - ★ 示例：`This example shows how to create a 3D spline.`（`Create_3D_Spline_Example_VB.md`）
  - ★ 判读：Remarks 限定建在活动的 2D 草图里；本页唯一示例却在 3D 草图(Insert3DSketch2)里建样条并给非零 Z，两侧说法不能同时成立。
- **`CreateSpline2`**
  - ★ `Remarks`：This method creates a spline in the active 2D sketch.
  - ★ 示例：`Part.SketchManager.Insert3DSketch True`（`Add_Along_X_Dimension_To_3D_Sketch_Example_VB.md`）
  - ★ 判读：Remarks 限定建在活动的 2D 草图里；四份示例都先 Insert3DSketch 进 3D 草图并给真 Z 值建样条，两侧说法不能同时成立。
- **`CreateTaskpaneView3`**
  - ★ `Remarks`：ImageList contains paths to PNG or BMP images in six pixel sizes:
  - ★ 示例：`string[] bitmap = new string[1];`（`Create_TaskPaneView_Add-in_Example_CSharp.md`）
  - ★ 判读：Remarks 要求六个尺寸的路径（20/32/40/64/96/128），该 Add-in 示例只放 1 个 bmp 路径，两者不能同时成立。
- **`CreateTrimmedSurface`**
  - ★ `Remarks`：Before you call this method, you must call one of the base-surface creation methods (such as [[IBody2::CreatePlanarSurface]] or [[IBody2::ICreatePlanarSurface]]) and the trimming-curve creation method [[ISurface::AddTrimmingLoop2]] or [[ISurface::IAddTrimmingL
  - ★ 示例：`swSurface.AddTrimmingLoop(nCurves,
Order, Dim, Periodic, nKnots, nCtrlPts, Knots, CtrlPts);`（`Create_Imported_Surface_Body_from_Sketch_Example_CSharp.md`）
  - ★ 判读：Remarks 点名只能用 AddTrimmingLoop2/IAddTrimmingLoops；该例调的是另一个成员 ISurface::AddTrimmingLoop（types 目录里两者各自独立成页），两侧不能同时成立。
- **`Curvature`**
  - ★ `Remarks`：Curvature control must be enabled for this property to have an effect. Use [[ISplineHandle::CurvatureControlled]] to see if curvature control is enabled or to set curvature control for this spline handle.
  - ★ 示例：`        Debug.Print " Curvature: " & swSplineHandle(i).Curvature`（`Get_and_Set_Spline_Handles_Example_VB.md`）
  - ★ 判读：Remarks 说必须先开曲率控制；三份示例里 CurvatureControlled 出现 0 次，仍把它当有效读数打印。
- **`D1Direction`**
  - ★ `Remarks`：Use this property only when editing the pattern feature.
  - ★ 示例：`patternDirection = swCurveDrivenPatternFeatureData.D1Direction;`（`Create_and_Access_Curve-driven_Pattern_Feature_Example_CSharp.md`）
  - ★ 判读：Remarks 把该属性限定为仅编辑时使用；示例全程不写它，只在 AccessSelections 之后读取。
- **`DefineAttribute`**
  - ★ `Remarks`：The Name argument used for this attribute definition must be unique and qualified among the attributes defined in the current session. To ensure this, the first three letters of the name must be an officially recognized third-party identifier.
  - ★ 示例：`swAttributeDef = (AttributeDef)swApp.DefineAttribute("TestPropagationOfAttribute");`（`Add_Attribute_to_Feature_and_Include_in_Library_Feature_Example_CSharp`）
  - ★ 判读：Remarks 要求名称前三字母是官方第三方标识（或 pub），示例用 Tes 前缀且声明成功。
- **`DeleteFrame`**
  - ★ `Remarks`：This method is valid only if this Gtol was created in SOLIDWORKS 2022 or later.
  - ★ 示例：`either SolidWorks 2021 or SolidWorks 2022/2022+.`（`Get_Gtol_Frame_Information_Example_CSharp.md`）
  - ★ 判读：备注限定只对 2022 及以后创建的 Gtol 有效，示例前置却明写允许 2021 创建的 Gtol，可用前提不同。
- **`DeleteOriginalFace`**
  - ★ `Remarks`：This property is only available if [[ISurfExtrudeFeatureData::BothDirections]] = false.
  - ★ 示例：`' Create a blind surface extrude
    ' in two directions from the selected sketch`（`Insert_Extruded_Reference_Surface_Example_VB.md`）
  - ★ 判读：示例建的是双向拉伸（首参 Sd=false，故 BothDirections=true），同一示例紧接着读 DeleteOriginalFace，与「仅 BothDirections=false 可用」不能同时成立。
- **`Diagonal`**
  - ★ `Remarks`：This property is valid only if both are true:

- [[IFillPatternFeatureData::FeaturesToPatternType]] = [[swFeaturesToPatternType_e]].swFeaturesToPatternCreateSeedCut

- [[IFillPatternFeatureData::CreateSeedCutType]] = [[swCreateSeedCutType_e]].swCreateSeedCutDi
  - ★ 示例：`swFeatData.CreateSeedCutType = 0;
swFeatData.Diagonal = 0.008;`（`Create_Fill_Pattern_Example_CSharp.md`）
  - ★ 判读：swCreateSeedCutType_e 枚举 0=None、3=Diamond；示例显式设 CreateSeedCutType=0 后立刻写 Diagonal，与 Remarks 要求的 Diamond(=3) 相反。
- **`Diagonal`**
  - ★ `Remarks`：- [[IFillPatternFeatureData::FeaturesToPatternType]] = [[swFeaturesToPatternType_e]].swFeaturesToPatternCreateSeedCut
  - ★ 示例：`swFeatData.FeaturesToPatternType = 0;`（`Create_Fill_Pattern_Example_CSharp.md`）
  - ★ 判读：枚举 0=swFeaturesToPatternSelectedFeatures、1=swFeaturesToPatternCreateSeedCut；示例最终设为 0，按 Remarks 此时 Diagonal 无效。
- **`Diameter`**
  - ★ `Remarks`：This property is valid only if [[IAdvancedHoleElementData::DiameterOverride]] is set to true.
  - ★ 示例：`swAdvHole_Near_1.Diameter = ConvFactorLength * 0.225;`（`Create_Advanced_Hole_Example_CSharp.md`）
  - ★ 判读：该元素（Near_1 沉头）在三份官方示例里都未写过 DiameterOverride，却先写 Diameter 再进 AdvancedHole2。
- **`Diameter`**
  - ★ `Remarks`：This property is valid only if [[IAdvancedHoleElementData::DiameterOverride]] is set to true.
  - ★ 示例：`swAdvHole_Near_2.Diameter = ConvFactorLength * 0.089;
swAdvHole_Near_2.EndCondition = (int)swEndConditions_e.swEndCondUpToNext;
swAdvHole_Near_2.DiameterOverrid`（`Create_Advanced_Hole_Example_CSharp.md`）
  - ★ 判读：示例次序是 Diameter 先写、DiameterOverride 后置 true，与 Remarks 要求的「先 Override 才有效」相反。
- **`Diameter`**
  - ★ `Remarks`：This property is valid only if [[IAdvancedHoleElementData::DiameterOverride]] is set to true.
  - ★ 示例：`Debug.Print("   Diameter in m: " + ((AdvancedHoleElementData)swCounterSinkNear).Diameter);`（`Create_Advanced_Hole_Example_CSharp.md`）
  - ★ 判读：读侧同样在 Near_1 未设 DiameterOverride 时读 .Diameter；Remarks 的前提没区分读写方向。
- **`Dimension`**
  - ★ `Remarks`：- [[IFillPatternFeatureData::FeaturesToPatternType]] = [[swFeaturesToPatternType_e]].swFeaturesToPatternCreateSeedCut
  - ★ 示例：`swFeatData.FeaturesToPatternType = 0;`（`Create_Fill_Pattern_Example_CSharp.md`）
  - ★ 判读：官方枚举页 swFeaturesToPatternType_e 载 CreateSeedCut=1、SelectedFeatures=0；示例写 0，Remarks 要求的前置不成立。
- **`Dimension`**
  - ★ `Remarks`：- [[IFillPatternFeatureData::CreateSeedCutType]] is set to one of the following:

  - [[swCreateSeedCutType_e]].swCreateSeedCutDiamond

  - swCreateSeedCutType_e.swCreateSeedCutSquare
  - ★ 示例：`swFeatData.CreateSeedCutType = 0;`（`Create_Fill_Pattern_Example_CSharp.md`）
  - ★ 判读：官方枚举页 swCreateSeedCutType_e 载 Diamond=3、Square=2、None=0；示例写 0 即 None，两个允许值都不是。
- **`DisplayAsOneItem`**
  - ★ `Remarks`：This property applies to top-level only BOM tables. Use [[IBomFeature::TableType]] to determine the BOM table type.
  - ★ 示例：`BomType = swBomType_Indented`（`Insert_and_Show_BOM_Table_and_BOM_Balloon_Example_VB.md`）
  - ★ 判读：Remarks 限定只适用于 top-level only 表（swBomType_TopLevelOnly=2），示例建的是 Indented（=3）BOM 却照读该属性，读数不在声明的适用域内。
- ★ 其余 264 条见 `c4-merged.json` ✓

## 三 · ★ 我们**真调用**过的成员（★ 优先查这批 —— 用 `ast` 判，事实 528）

★ 见 `docs/recon-206/conflicts-25-crosscheck.md` §五（真调用 7 个 / 只出现在文本里 1 个 / 没出现 11 个）✓

## 四 · ★ 怎么用（★ 接进哪一步）

★ 本表是「官方文档是第 0 步」那条链的**第 0.5 步**：
```
① 官方页（签名 + Remarks）→ ② ★★ **本表（先看这个成员有没有内部冲突）** →
③ docs/dead-ends.md → ④ 该能力的 limitations → ⑤ known-facts.md → ⑥ 动手
```
⚠ ★★ **本表暂不写进 `AGENTS.md`** —— 因为该文件的指令预算是 65536 字节、
当前已用 **76.3%**（余量 15534 字节），★ 加行有**静默截断最新条目**的风险
（★ 本仓自己记过这个坑）⇒ ★ **改由本文件自荐 + 交接节指向**，等 `AGENTS.md` 腾出空间再挂 ✓
