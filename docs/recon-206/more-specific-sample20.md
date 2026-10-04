# T4-2 抽样表：条目最多的 **20** 个「与我们有关」的成员

> 生成物 —— 由 `tools/t4_2_sample20.py` 产出，不要手改。
> ★ 用途：`example_more_specific` 共 **3806** 条 / **2242** 个成员，其中 **258** 个我们真调用过。
> ★★ 本表从那 258 里取**条目最多的 20 个**，把判读材料抽齐 ⇒ **判读变成小范围阅读** ✓

## 一 · 口径（★ 先说清楚）

| 项 | 值 |
|---|---|
| 全量 `example_more_specific` | **3806** 条（★ 目标写 3709，★ 实量以此为准）|
| 涉及成员 | **2242** |
| ★ 我们真调用过的 | **258** |
| ★★ 本表抽样 | **20**（★ 按条目数降序，与 D-1 的抽检量一致）|

★★ **本表「不算什么」**（★ 缺了它会被误用）：

- ★★ **不等于**「这 20 条是缺陷」—— 该字段语义是「**示例比 Remarks 更具体**」，
  ★ 那是**中性的** ⇒ ★ 判读要问的是**「示例多给的信息是否改变调用形状」** ✓；
- ★ 抽样**不随机**（★ 按条目数取头部）⇒ ★★ **不能**用它估计全量的缺陷率；
  ★ 要估率得**随机抽**（★ 那是另一件事）✓；
- ★ 判读材料来自另一个对话的 `conditional_pass` 产出 ⇒ ★ **采纳前须回查官方页** ✓

---

## 1 · `CreateSketchSlot`（4 条 · 我们的调用点 `scripts\sw_part.py:613`）

- **1)** {"what": "示例调用前先选前视基准面再 InsertSketch 进入草图编辑态；成员页整页无 Remarks，未写此前置。", "example_quote": "skManager.InsertSketch(true);", "example_file": "Insert_and_Resize_Sketch_Slot_Example_CSharp.md"}
- **2)** {"what": "示例固定用 line 型 + CenterCenter 长度型，且第三点 X3/Y3/Z3 全传 0；成员页未给推荐组合。", "example_quote": "swSketchSlot = swSketchManager.CreateSketchSlot(swSketchSlotCreationType_e.swSketchSlotCreationType_line, swSketchSlotLengthType_e.swSketchSlotLengthType_CenterCenter, 0.05, -0.05, 0, 0, 0.05, 0, 0, 0, 0, 0, 1, False)", "example_file": "Get_Sketch_Slot_Using_Sketch_Point_and_Segment_Example_VB.md"}
- **3)** {"what": "示例给出 Width=0.05、端点 X=-0.05 与 0.05 的实参组合；成员页参数表对 Width 与各坐标完全没写单位。", "example_quote": "0.05, -0.05, 0, 0, 0.05, 0, 0, 0, 0, 0, 1, false", "example_file": "Insert_and_Resize_Sketch_Slot_Example_CSharp.md"}
- **4)** {"what": "示例返回 SketchSlot 后立刻读 Length/Width/LengthType 并把 Width 改写为两倍；成员页 Returns 只写『Sketch slot』。", "example_quote": "swSketchSlot.Width = swSketchSlot.Width * 2.0;", "example_file": "Insert_and_Resize_Sketch_Slot_Example_CSharp.md"}

## 2 · `CreateSpline`（4 条 · 我们的调用点 `tools\prove_createline2_and_createspline.py:107`）

- **1)** {"what": "示例在调用前先 Insert3DSketch2(True) 进 3D 草图；成员页的『没活动草图就新建一个』只描述 2D 情形。", "example_quote": "swModel.Insert3DSketch2 True", "example_file": "Create_3D_Spline_Example_VB.md"}
- **2)** {"what": "示例用 Dim nPtData(11) As Double 再转 Variant 传入 12 个双精度（4 个点），属 Remarks 说的 OLE 自动定长度那条路。", "example_quote": "Dim nPtData(11) As Double", "example_file": "Create_3D_Spline_Example_VB.md"}
- **3)** {"what": "示例把 Z 依次取 0/0.1/0.2/0.3 递增值，说明 3D 草图下 Z 是真正被使用的。", "example_quote": "nPtData(6) = -0.03568716302953: nPtData(7) = 0.01004261874198: nPtData(8) = 0.2", "example_file": "Create_3D_Spline_Example_VB.md"}
- **4)** {"what": "示例对返回值只做 Debug.Assert 非空判断，没有再用 QueryInterface 取 ISketchSpline；成员页给了更细的取法说明。", "example_quote": "Debug.Assert Not swSketchSeg Is Nothing", "example_file": "Create_3D_Spline_Example_VB.md"}

## 3 · `CreateSpline2`（4 条 · 我们的调用点 `scripts\sketch_relations.py:284`）

- **1)** {"what": "示例固定把 SimulateNaturalEnds 传 True；成员页只解释 True/False 的含义，未给推荐默认值。", "example_quote": "Set skSegment = Part.SketchManager.CreateSpline2((pointArray), True)", "example_file": "Add_Along_X_Dimension_To_3D_Sketch_Example_VB.md"}
- **2)** {"what": "示例用 ReDim points(0 To 11) As Double 组 12 个双精度（4 个点）再转 Variant；成员页只写『至少两组 X,Y,Z』。", "example_quote": "ReDim points(0 To 11) As Double", "example_file": "Add_Along_X_Dimension_To_3D_Sketch_Example_VB.md"}
- **3)** {"what": "示例给 Z 填 0.046/0.005/-0.043/-0.094 等真值，说明 3D 草图下 Z 被采用而非忽略。", "example_quote": "points(2) = 0.04608246573503", "example_file": "Add_Along_X_Dimension_To_3D_Sketch_Example_VB.md"}
- **4)** {"what": "成员页 Examples 段只列了 Insert a Composite Curve 一族，这四份 Add_Along_* 示例并未被该页列出。", "example_quote": "skSegment = (SketchSegment)Part.SketchManager.CreateSpline2((pointArray), true);", "example_file": "Add_Along_Y_Dimension_To_3D_Sketch_Example_CSharp.md"}

## 4 · `CreateSpline3`（4 条 · 我们的调用点 `tools\probe_createspline3.py:69`）

- **1)** {"what": "页面只说 Direction 可为 Nothing or null；C#/VB.NET 示例须包成 DispatchWrapper，且只传单个 null（VBA 直接传 Nothing）。", "example_quote": "dirArray = new DispatchWrapper(null);", "example_file": "Create_On-surface_Spline_Example_CSharp.md"}
- **2)** {"what": "页面称 SimulateNaturalEnds \"valid only for 2D splines\"，on-surface 示例仍显式传 true。", "example_quote": "skSegment = (SketchSegment)Part.SketchManager.CreateSpline3((pointArray), dispArray, dirArray, true, out statuses);", "example_file": "Create_On-surface_Spline_Example_CSharp.md"}
- **3)** {"what": "示例给出 on-surface 路径的收尾动作：建完立即 InsertSketch(true)。", "example_quote": "Part.SketchManager.InsertSketch(true);", "example_file": "Create_On-surface_Spline_Example_CSharp.md"}
- **4)** {"what": "VBA 版把 Status 以 Variant 按引用传入并以 Set 接返回，页面未给调用序。", "example_quote": "Set skSegment = Part.SketchManager.CreateSpline3((pointArray), surfs, Nothing, True, statuses)", "example_file": "Create_On-surface_Spline_Example_VB.md"}

## 5 · `CylinderParams`（4 条 · 我们的调用点 `scripts\sw_review.py:877`）

- **1)** {"what": "示例补了前置：先选中圆柱面，再用 IsCylinder 守卫后才取参数（成员页无前置）", "example_quote": "If swSurf.IsCylinder Then", "example_file": "Get_Parameters_of_Cylindrical_Surface_Example_VB.md"}
- **2)** {"what": "前置更具体：注释第 2 条逐字要求「Select the cylindrical surface.」，且无草图/文档单位前提", "example_quote": "2. Select the cylindrical surface.", "example_file": "Get_Parameters_of_Cylindrical_Surface_Example_VB.md"}
- **3)** {"what": "示例给出第二条取用路径：不选面，经注释附着实体直接取 CylinderParams", "example_quote": "faceParams = attachedEntity.GetSurface.CylinderParams", "example_file": "Get_Entities_Attached_To_Cosmetic_Thread_Example_VB.md"}
- **4)** {"what": "示例把索引 3..5 原样当单位向量用、不换算，印证 axis 三个分量无量纲", "example_quote": "nVector(0) = vCylinder(3): nVector(1) = vCylinder(4): nVector(2) = vCylinder(5)", "example_file": "Get_Angle_of_Hole_Not_Normal_to_a_Face_Example_VB.md"}

## 6 · `InsertMidSurface`（4 条 · 我们的调用点 `scripts\sw_sheet_metal_weld_entry.py:817`）

- **1)** {"what": "零件场景示例先 SelectByID2 选两个面再传 null/Nothing，成员页的算法描述里没有这一步", "example_quote": "// 2. Selects two faces and inserts a midsurface feature.", "example_file": "Get_Areas_of_MidSurface_Faces_Example_CSharp.md"}
- **2)** {"what": "零件场景下 Body2 与 ModelDoc2 两参都传 null，印证「非装配体上下文」那条分支", "example_quote": "swFeatureManager.InsertMidSurface(null, null, 0.0, false);", "example_file": "Get_Areas_of_MidSurface_Faces_Example_CSharp.md"}
- **3)** {"what": "装配场景示例的 FeatureManager 取自装配文档，pBody/pPartDoc 才换成组件的，成员页未规定二者须同源", "example_quote": "featMgr = (FeatureManager)swModel.FeatureManager;", "example_file": "Insert_MidSurface_in_Component_Example_CSharp.md"}
- **4)** {"what": "组件分支用 Placement 0.5 且 KnitFlag=True，成员页只说范围 -1 到 1，未给缝合成单张的具体取值", "example_quote": "midSurf = (MidSurface3)featMgr.InsertMidSurface(pBody, swModel, 0.5, true);", "example_file": "Insert_MidSurface_in_Component_Example_CSharp.md"}

## 7 · `InsertMirrorFeature2`（4 条 · 我们的调用点 `scripts\sw_part.py:1498`）

- **1)** {"what": "示例先整批按 mark 0 选一遍，再 ClearSelection2 后按成员页那张 mark 表重选，给出完整调用序", "example_quote": "Must be preselected and marked with a value of...", "example_file": "Get_Mirror_Pattern_Feature_Data_Example_CSharp.md"}
- **2)** {"what": "作镜面的那个面是按坐标选出的 FACE、用 mark 2（Planes or planar faces 行），从未用到 Faces 行的 128", "example_quote": "status = swModelDocExt.SelectByID2(\"\", \"FACE\", 0.232539736404746, -0.0399999999999068, 0.0224388980993808, true, 2, null, 0);", "example_file": "Get_Mirror_Pattern_Feature_Data_Example_CSharp.md"}
- **3)** {"what": "实体分支同时用到 Planes 行(PLANE Top 标 2)与 Bodies 行(SOLIDBODY 标 256)，与成员页表逐行对上", "example_quote": "status = swModelDocExt.SelectByID2(\"Extrude-Thin1\", \"SOLIDBODY\", 0, 0, 0, True, 256, Nothing, 0)", "example_file": "Get_Mirror_Solid_Data_Example_VB.md"}
- **4)** {"what": "三份示例的 ScopeOptions 都固定传 swFeatureScope_AllBodies，成员页未给默认取值", "example_quote": "InsertMirrorFeature2(false, false, false, false, (int)swFeatureScope_e.swFeatureScope_AllBodies);", "example_file": "Get_Mirror_Pattern_Feature_Data_Example_CSharp.md"}

## 8 · `ActivateDoc2`（3 条 · 我们的调用点 `scripts\sw_assembly.py:113`）

- **1)** {"what": "Errors 是 out 形参，VBA 侧须先 Dim 声明 Long 变量再传", "example_quote": "Dim longstatus As Long, longwarnings As Long", "example_file": "Access_and_Release_Access_to_Edges_Example_VB.md"}
- **2)** {"what": "四份示例全部丢弃返回值，改读 swApp.ActiveDoc 取激活后的文档", "example_quote": "swModel = (ModelDoc2)swApp.ActiveDoc;", "example_file": "Access_and_Release_Access_to_Edges_Example_CSharp.md"}
- **3)** {"what": "Name 传不带扩展名的标题 box，正是 Remarks 点名的歧义场景", "example_quote": "swApp.ActivateDoc2(\"box\", false, ref longstatus);", "example_file": "Access_and_Release_Access_to_Edges_Example_CSharp.md"}

## 9 · `AddComponent4`（3 条 · 我们的调用点 `scripts\sw_assembly.py:138`）

- **1)** {"what": "示例先用 OpenDoc6 把零件载入内存再调用，印证 Remarks 的必须已载入这条前置不是空话。", "example_quote": "swApp->OpenDoc6(sCompName,", "example_file": "Add_Component_and_Mate_Example_CPlusPlus_COM.md"}
- **2)** {"what": "X/Y/Z 全传 -1 作哨兵；示例自己说该方法只适合粗定位。", "example_quote": "sDefaultConfiguration, -1, -1, -1, &swComponent);", "example_file": "Add_Component_and_Mate_Example_CPlusPlus_COM.md"}
- **3)** {"what": "Remarks 说精确定位用 IComponent2::Transform2；示例改用选两个基准面 + AddMate3 定位，全程不调 Transform2。", "example_quote": "swAssy->AddMate3(swMateCOINCIDENT,", "example_file": "Add_Component_and_Mate_Example_CPlusPlus_COM.md"}

## 10 · `AddDimension2`（3 条 · 我们的调用点 `scripts\sw_part.py:838`）

- **1)** {"what": "示例没有显式 SelectByID2，选中态直接来自上一句 SketchManager.CreateLine", "example_quote": "swModel.SketchManager.CreateLine 0.01, 0.01, 0, 0.01, 0.01 + Height, 0", "example_file": "Get_Annotations_Array_Example_VB.md"}
- **2)** {"what": "示例把 swInputDimValOnCreate 这个开关设在 ISldWorks（swApp）上，建完再置回 True，Remarks 未说归属对象", "example_quote": "swApp.SetUserPreferenceToggle swInputDimValOnCreate, True", "example_file": "Get_Annotations_Array_Example_VB.md"}
- **3)** {"what": "工程图示例按实体对象选（SelectEntity）而非按名或按坐标，与 Remarks 的「按位置别按名」不矛盾", "example_quote": "= swView.SelectEntity(swEnt, False)", "example_file": "Dimension_Edge_in_Drawing_Example_VB.md"}

## 11 · `AddVerticalDimension2`（3 条 · 我们的调用点 `scripts\sw_sketch_dimensions.py:74`）

- **1)** {"what": "示例每次调用前先用 SelectEntity 把模型那条边在当前视图里选中（逐视图重新选中），成员页未写这一前置", "example_quote": "= swView.SelectEntity(swEnt, False)", "example_file": "Dimension_Edge_in_Drawing_Example_VB.md"}
- **2)** {"what": "示例明确该视图里边转换不了就返回 NULL；成员页 Returns 只写「Newly created dimension」", "example_quote": "NULL if cannot convert edge in this view", "example_file": "Dimension_Edge_in_Drawing_Example_VB.md"}
- **3)** {"what": "示例先按视图坐标判断边是竖直还是水平再选 AddVerticalDimension2 / AddHorizontalDimension2，说明「Vertical」指视图方向", "example_quote": "Must be vertical", "example_file": "Dimension_Edge_in_Drawing_Example_VB.md"}

## 12 · `AutoDimension2`（3 条 · 我们的调用点 `scripts\sw_part.py:805`）

- **1)** {"what": "打基准 mark 的实际入口是 IEntity::Select3 的第二个形参；成员页只说「mark」，未指明 API。", "example_quote": "bRet = swSketchSegHoriz.Select3(True, swAutodimMarkHorizontalDatum, Nothing)", "example_file": "Autodimension_a_Sketch_Example_VB.md"}
- **2)** {"what": "示例指出进入草图编辑会清掉选区，必须重新选中基准；成员页未提。", "example_quote": "' Editing sketch clears selections", "example_file": "Autodimension_All_Sketches_Example_VB.md"}
- **3)** {"what": "示例注释确认「竖线作水平基准」，与成员页的基准对应关系相同。", "example_quote": "' Vertical line is for horizontal datum", "example_file": "Autodimension_All_Sketches_Example_VB.md"}

## 13 · `Component`（3 条 · 我们的调用点 `scripts\sw_assembly.py:924`）

- **1)** {"what": "示例注明底层模型以另一配置打开时本属性返回 NULL、必须判空；Remarks 与 Returns 都没提", "example_quote": "' Returns NULL if underlying model is open in a different configuration", "example_file": "Get_Components_in_Drawing_View_Example_VB.md"}
- **2)** {"what": "取法：View.RootDrawingComponent → GetChildren 遍历子 DrawingComponent 后才读本属性", "example_quote": "vDrawChildCompArr = swRootDrawComp.GetChildren", "example_file": "Get_Components_in_Drawing_View_Example_VB.md"}
- **3)** {"what": "读出后打印 Name2 与 ReferencedConfiguration，即 Remarks 所说的「与被引用配置属性一致」", "example_quote": "Debug.Print \" Configuration = \" & swComp.ReferencedConfiguration", "example_file": "Get_Components_in_Drawing_View_Example_VB.md"}

## 14 · `CreateEquationSpline2`（3 条 · 我们的调用点 `tools\prove_equation_driven_curve.py:69`）

- **1)** {"what": "示例把返回值先接进 SketchSegment 变量、再强转 SketchSpline；成员页 Returns 未说清落点类型", "example_quote": "\t            SketchSpline skSpline = default(SketchSpline);\n\t            skSpline = (SketchSpline)skSegment;", "example_file": "Create_Equation-driven_Curve_Example_CSharp.md"}
- **2)** {"what": "示例前置是先选基准面再 InsertSketch，本方法在草图打开期间调用；成员页未提草图前置", "example_quote": "    boolstatus = swExt.SelectByID2(\"Front Plane\", \"PLANE\", 0, 0, 0, False, 0, Nothing, 0)\n    swModel.SketchManager.InsertSketch True", "example_file": "Create_Equation-driven_Curve_Example_VB.md"}
- **3)** {"what": "RangeEnd 传纯十进制串 6.28（约 2π），未用 Remarks 举例的 pi；说明范围串可写普通数字", "example_quote": "    Set skSegment = swModel.SketchManager.CreateEquationSpline2(\"\", \"sin(x)\", \"\", \"0\", \"6.28\", False, 0, 0, 0, True, True)", "example_file": "Create_Equation-driven_Curve_Example_VB.md"}

## 15 · `CreateLine2`（3 条 · 我们的调用点 `tools\prove_createline2_and_createspline.py:96`）

- **1)** {"what": "页面只教怎么「检查」活动草图（GetActiveSketch2）；示例给出打开/关闭草图的具体两句，把前置落成可执行调用。", "example_quote": "swModel.Insert3DSketch2 False", "example_file": "Calculate_Closest_Distance_Between_Faces_Example_VB.md"}
- **2)** {"what": "两例把同一个 System.object 返回分别接成 SketchSegment 与 SketchLine，各对应页面「VB 自动解释指针」那半句。", "example_quote": "Set swSkLine = swModel.CreateLine2(vPt1(0), vPt1(1), vPt1(2), vPt2(0), vPt2(1), vPt2(2))", "example_file": "Calculate_Closest_Distance_Between_Model_Components_Example_VB.md"}
- **3)** {"what": "页面六个参数只写「X value」不给单位；示例证明这些坐标是 API 原样的米（同一 vPt 乘 1000 才打 mm）。", "example_quote": "Debug.Print \" 1 = (\" & vPt1(0) * 1000# & \", \" & vPt1(1) * 1000# & \", \" & vPt1(2) * 1000# & \") mm\"", "example_file": "Calculate_Closest_Distance_Between_Model_Components_Example_VB.md"}

## 16 · `CreateMassProperty`（3 条 · 我们的调用点 `tools\compare_geometry.py:98`）

- **1)** {"what": "页面对 Mass/Volume/Density 一律不给单位；示例按 MKS 直出，乘 1000 转 mm、体积乘 1e9、惯量 kg*m^2。", "example_quote": "Debug.Print \"Volume = \" & swMass.Volume * 1000000000# & \" mm^3\"", "example_file": "Get_Mass_Properties_of_Multibody_Assembly_Component_Example_VB.md"}
- **2)** {"what": "页面教用 IComponent2::GetBodies2 取体；示例实际调 GetBodies3，C#/VBNET 还要把结果包成 DispatchWrapper[] 再喂 AddBodies。", "example_quote": "vBodyArr = swComp.GetBodies3(swSolidBody, vBodyInfo)", "example_file": "Get_Mass_Properties_of_Multibody_Assembly_Component_Example_VB.md"}
- **3)** {"what": "页面写了「Not called [AddBodies] 则含文档全部体」这一支；示例演示不调 AddBodies 直接读质心与主惯性轴。", "example_quote": "vCofG = swMass.CenterOfMass", "example_file": "Insert_Coordinate_System_Feature_at_Center_of_Mass_Example_VB.md"}

## 17 · `CreateParabola`（3 条 · 我们的调用点 `scripts\sw_sketch_primitives.py:132`）

- **1)** {"what": "成员页参数只写「X coordinate for the focus」无单位；示例坐标是米，打印时才 ×1000 标 mm", "example_quote": "\"      Apex  Point   = (\" & pApex.X * 1000 & \", \" & pApex.Y * 1000 & \", \" & pApex.Z * 1000 & \") mm\"", "example_file": "Create_Parabola_Example_VB.md"}
- **2)** {"what": "示例要求草图必须是 2D（四点 Z 全为 0 否则退出），成员页无任何前置", "example_quote": "MsgBox \"Need a 2D sketch.\"", "example_file": "Create_Parabola_Example_VB.md"}
- **3)** {"what": "成员页 Returns 写「Sketch segment for the parabola」；示例收成 SketchParabola 再取四个点", "example_quote": "Set SkParabola = swModel.SketchManager.CreateParabola(pFocal.X, pFocal.Y, 0, pApex.X, pApex.Y, 0, pStart.X, pStart.Y, 0, pEnd.X, pEnd.Y, 0)", "example_file": "Create_Parabola_Example_VB.md"}

## 18 · `CreateStructureSystemMemberData`（3 条 · 我们的调用点 `tools\prove_structure_system.py:104`）

- **1)** {"what": "页面只有一句指路；示例给出返回值必须逐级向下转型才能用到具体成员接口。", "example_quote": "memPathSegDef = (PrimaryMemberPathSegmentFeatureData)PrimDef;", "example_file": "Access_Structure_System_Corner_Treatments__Example_CSharp.md"}
- **2)** {"what": "示例给出 MemberType 实参与成员种类的对应 3=FacePlaneIntersection，与官方枚举表一致。", "example_quote": "structMemDef = (StructureSystemMemberFeatureData)modDocExt.CreateStructureSystemMemberData(3);", "example_file": "Create_Face_Plane_Intersection_SSMember_Example_CSharp.md"}
- **3)** {"what": "示例把返回对象的 StructureSystemMemberType 标为 swStructureSystemMemberType_e，与页面 MemberType 所引枚举不同名。", "example_quote": "Debug.Print(\"Type of structure system member as defined by", "example_file": "Access_Structure_System_Corner_Treatments__Example_CSharp.md"}

## 19 · `Elliptical`（3 条 · 我们的调用点 `tools\verify_dome_smoke.py:201`）

- **1)** {"what": "示例前置比成员页多一步：改 Elliptical 前先 AccessSelections 回滚取访问权，Remarks 只提 ModifyDefinition。", "example_quote": "swDome.AccessSelections(swModel,", "example_file": "Change_Height_of_Dome_Feature_Example_VB.md"}
- **2)** {"what": "示例写出 ModifyDefinition 的三参调用形态，并对返回值做 Debug.Assert。", "example_quote": "swFeat.ModifyDefinition(swDome,", "example_file": "Change_Height_of_Dome_Feature_Example_VB.md"}
- **3)** {"what": "示例显式给出成员页没写的前置：圆顶特征须已被选中，再从选区对象取 GetDefinition。", "example_quote": "Dome feature for which a distance was", "example_file": "Change_Height_of_Dome_Feature_Example_VB.md"}

## 20 · `FeatureFillet3`（3 条 · 我们的调用点 `scripts\sw_part.py:1144`）

- **1)** {"what": "只选 1 条边却给 2 个 Radii 值：示例用起点/终点顶点回读，说明每条边占 2 个槽位", "example_quote": "AsyRadius1 = swFeatData.GetRadius2(ver1, True)", "example_file": "Create_Asymmetric_Elliptic_Fillets_Example_VB.md"}
- **2)** {"what": "示例回读 ConicTypeForCrossSectionProfile 并给出枚举名注释，Remarks 只列可选名不给读数", "example_quote": "Debug.Print \"Fillet profile type as defined in swFeatureFilletProfileType_e (0 = Elliptical): \" & Fillet_ProfileTyp", "example_file": "Create_Asymmetric_Elliptic_Fillets_Example_VB.md"}
- **3)** {"what": "示例给出含 CurvatureContinuous 的 Options 组合；Remarks 第 8 步只说未含它时另加 CornerType", "example_quote": "filletOptions = (int)swFeatureFilletOptions_e.swFeatureFilletCurvatureContinuous + (int)swFeatureFilletOptions_e.swFeatureFilletKeepFeatures + (int)swFeatureFilletOptions_e.swFeatureFilletPropagateFeatToParts;", "example_file": "Create_Curvature_Continuous_Variable_Fillet_Feature_Example_CSharp.md"}

## ★ 判读模板（★ 每条填一行；★ 只关心「是否改变调用形状」）

| 成员 | 条目数 | ★ 示例多给的信息**是否改变调用形状** | 结论 | 证据 |
|---|---:|---|---|---|
| `CreateSketchSlot` | 4 | （待填）| （待填）| （待填）|
| `CreateSpline` | 4 | （待填）| （待填）| （待填）|
| `CreateSpline2` | 4 | （待填）| （待填）| （待填）|
| `CreateSpline3` | 4 | （待填）| （待填）| （待填）|
| `CylinderParams` | 4 | （待填）| （待填）| （待填）|
| `InsertMidSurface` | 4 | （待填）| （待填）| （待填）|
| `InsertMirrorFeature2` | 4 | （待填）| （待填）| （待填）|
| `ActivateDoc2` | 3 | （待填）| （待填）| （待填）|
| `AddComponent4` | 3 | （待填）| （待填）| （待填）|
| `AddDimension2` | 3 | （待填）| （待填）| （待填）|
| `AddVerticalDimension2` | 3 | （待填）| （待填）| （待填）|
| `AutoDimension2` | 3 | （待填）| （待填）| （待填）|
| `Component` | 3 | （待填）| （待填）| （待填）|
| `CreateEquationSpline2` | 3 | （待填）| （待填）| （待填）|
| `CreateLine2` | 3 | （待填）| （待填）| （待填）|
| `CreateMassProperty` | 3 | （待填）| （待填）| （待填）|
| `CreateParabola` | 3 | （待填）| （待填）| （待填）|
| `CreateStructureSystemMemberData` | 3 | （待填）| （待填）| （待填）|
| `Elliptical` | 3 | （待填）| （待填）| （待填）|
| `FeatureFillet3` | 3 | （待填）| （待填）| （待填）|

★ **定案要求**（★ 沿用 T4-1 的经验）：★ 机械表只给材料，
★★ **必须读我们那一行代码才能定案**（事实 535：看着像缺陷的读完可能会反转）✓

