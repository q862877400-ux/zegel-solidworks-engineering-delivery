# 能力前置覆盖缺口清单（★ 给主线的决策输入 · 本文件**不改** `capabilities.yaml`）

> **生成物** —— 由 `tools/t2_write_precondition_gaps.py` 产出，**不要手改**。
> 输入：`specs/204-bunny-moat-batches/recon/c3-merged.json`（另一个对话的 C3 对账，**只读复用**，其 `conditional_pass` 状态见该规格的 REPORT.md §七）。

## 一 · 口径（★ 与数字一起读）

| 项 | 值 |
|---|---|
| 能力条目 | **98**（另一个对话判完的；`capabilities.yaml` 当期共 112 条能力）|
| 有前置条目的 | 91 |
| 前置条目总数 | **534** |
| —— `not_covered`（未覆盖）| ★ **322** |
| —— 其中 ★ **可机检**（提到会话/文档/选择/保存态）| ★ **102** |
| —— 不可机检 | 220（7 条外部工具链/人工操作 + 213 条没提会话状态）|

★★ **本清单「不算什么」**：

- ★ **不等于**「这 98 条能力是坏的」—— 它只说**运行证据没覆盖官方示例揭示的前置**；
- ★★ **不是** `level` 的依据（★ 改 level 是主线的决定，D-5）；
- ★ **不可机检的 220 条不算缺陷** —— 它们是环境/工具链要求（如「先建 VS 工程」），本仓不该为此写断言；
- ★ 来源是**另一个对话的判读**且全程 `conditional_pass`（★ 其 REPORT §七 自陈：C3 的更正**未再被门禁复核**）⇒
  ★ **本清单是候选队列**，采纳前需逐条过闸 ✓

## 二 · ★ 可机检前置最多的能力（**这 51 条值得先补断言**）

| 能力 | level | 前置总数 | 未覆盖 | ★ 其中可机检 |
|---|---|---:|---:|---:|
| `selection_helpers` | verified | 13 | 10 | **8** |
| `declarative_hole_creation` | verified | 10 | 8 | **6** |
| `preview_and_review_report` | verified | 6 | 6 | **4** |
| `holes_and_finishing` | verified | 9 | 6 | **3** |
| `geometry_and_delivery_review` | verified | 5 | 5 | **3** |
| `simulation_study_create` | verified | 10 | 8 | **3** |
| `config_and_export` | verified | 11 | 9 | **3** |
| `surface_features` | verified | 7 | 5 | **3** |
| `loft_and_sweep` | verified | 7 | 5 | **3** |
| `sketch_primitives_b1` | verified | 11 | 6 | **3** |
| `sketch_edit_ops_b3` | verified | 8 | 6 | **3** |
| `sketch_modify_ops` | verified | 6 | 5 | **3** |
| `ref_geometry` | verified | 8 | 4 | **3** |
| `sketch_rotate_or_copy_3d` | verified | 5 | 4 | **3** |
| `part_and_features` | verified | 14 | 9 | **2** |
| `external_spur_gear_geometry` | verified | 3 | 2 | **2** |
| `sheet_metal` | verified | 6 | 4 | **2** |
| `sketch_edit_ops` | verified | 4 | 2 | **2** |
| `gtol_insert` | verified | 6 | 4 | **2** |
| `drawing_current_sheet_query` | verified | 7 | 5 | **2** |
| `topology_constraints_and_controls` | verified | 13 | 13 | **2** |
| `render_material_library` | verified | 7 | 4 | **2** |
| `weldment_profile_and_curve` | verified | 5 | 4 | **2** |
| `surface_offset` | verified | 4 | 3 | **2** |
| `sketch_slot_types` | verified | 3 | 3 | **2** |
| `feature_loft_cut` | verified | 6 | 4 | **2** |
| `sketch_spline3_2d` | verified | 5 | 4 | **2** |
| `sketch_equation_curve` | verified | 8 | 4 | **2** |
| `solidworks_addin_host` | verified | 9 | 8 | **1** |
| `custom_properties_and_bom` | verified | 6 | 5 | **1** |
| `pack_and_go` | verified | 5 | 5 | **1** |
| `drawings_and_bom` | verified | 3 | 2 | **1** |
| `weldments` | verified | 11 | 7 | **1** |
| `chamfer_fillet_on_selection` | verified | 4 | 1 | **1** |
| `mass_property_read` | verified | 3 | 2 | **1** |
| `simulation_loads_wiring` | verified | 6 | 3 | **1** |
| `mesh_size_sanity_gate` | verified | 4 | 3 | **1** |
| `modeling_feature_readback_tools` | verified | 11 | 6 | **1** |
| `render_materials_and_appearance` | verified | 5 | 4 | **1** |
| `motion_validation_and_preconditions` | verified | 9 | 9 | **1** |
| `drawing_views_and_summary` | verified | 6 | 3 | **1** |
| `costing_templates_and_defaults` | verified | 4 | 2 | **1** |
| `pattern_and_mirror` | verified | 6 | 2 | **1** |
| `drawing_view_operations` | verified | 7 | 4 | **1** |
| `reference_axis` | verified | 3 | 2 | **1** |
| `curve_and_split` | verified | 9 | 5 | **1** |
| `sketch_dimension_horizontal` | verified | 4 | 1 | **1** |
| `feature_revolve_cut` | verified | 7 | 5 | **1** |
| `surface_flatten` | verified | 4 | 2 | **1** |
| `surface_delete_hole` | verified | 2 | 1 | **1** |
| `sketch_offset_on_surface` | verified | 5 | 3 | **1** |

## 三 · ★ 可机检的前置逐条（按能力分组 · 前 40 条）

> ★ 每条都是**官方示例文件里写的前置**，而本仓的运行证据没覆盖它。
> 格式：`[能力] 前置文本` —— ★ 括号里是该前置出自哪个示例文件。

### `selection_helpers`（8 条）

- SelectByID2 选面建抽壳后，示例须 ActivateDoc2 并取 ActiveDoc 才用 SelectionManager  <sub>（`Access_and_Release_Access_to_Edges_Example_VB.md`）</sub>
- 读特征数据的边前须先 AccessSelections(swModel, Nothing)，Select4 作用在其返回的实体上  <sub>（`Access_and_Release_Access_to_Edges_Example_VB.md`）</sub>
- 读实体前须 ClearSelection2(True) 清空选区（示例中用于释放选择访问）  <sub>（`Access_and_Release_Access_to_Edges_Example_VB.md`）</sub>
- GetSelectedObjectCount2 前置：Verify that the specified part template and library feature exist.  <sub>（`Create_Library_Feature_With_References_Example_VB.md`）</sub>
- GetBodies2 前置：Open a part or assembly.（须先打开零件或装配）  <sub>（`Select_Bodies_Example_VB.md`）</sub>
- GetEdges 前置：Open a part document.  <sub>（`Check_Edges_for_Faults_Example_VB.md`）</sub>
- GetVertices 前置：Open public_documents\samples\tutorial\assemblymates\head.sldprt  <sub>（`Get_Maximum_Edge_and_Vertex_Gaps_Example_VB.md`）</sub>
- GetSelectedObject6 前置：打开含两个特征的模型，并在特征树里选中它们  <sub>（`Get_Selection_Specification_Example_VB.md`）</sub>

### `declarative_hole_creation`（6 条）

- FeatureCut4 前置：须先 SelectByRay 选中一个面 → CreateCircle 画圆，调用后须 ClearSelection2(true)  <sub>（`Create_Cut_Extrude_in_Sheet_Metal_Part_Example_CSharp.md`）</sub>
- InsertFeatureChamfer 前置：须先用 SelectByID2 空名+坐标选中两条 EDGE（mark 0/1）再调用  <sub>（`Get_Edge_Chamfer_Distances_Example_VB.md`）</sub>
- GetCurve/CircleParams 前置：先打开含装饰螺纹的模型工程图并选中一个视图  <sub>（`Get_Entities_Attached_To_Cosmetic_Thread_Example_VB.md`）</sub>
- SelectByID2 前置："Front Plane" must be selected before InsertSketch(true)  <sub>（`Insert_and_Resize_Sketch_Slot_Example_CSharp.md`）</sub>
- GetSelectionPoint2 前置：Open a part or assembly and select a face（选区须是面）  <sub>（`Create_Drag_Arrow_Manipulator_Example_VB.md`）</sub>
- Select4/ClearSelection2 前置：取边前须 AccessSelections(swModel, Nothing)，实体须来自活动文档  <sub>（`Access_and_Release_Access_to_Edges_Example_VB.md`）</sub>

### `preview_and_review_report`（4 条）

- 「Preconditions: Model document is open.」—— ShowNamedView2/ViewZoomtofit2 前须有已打开的模型文档  <sub>（`Change_to_Isometric_and_Zoom_to_Fit_View_Mode_Example_VB.md`）</sub>
- 「Preconditions: Open a part or assembly.」—— 取 ActiveView 并用其成员前须已打开零件或装配  <sub>（`Roll_Model_View_Example_VB.md`）</sub>
- 「Preconditions: 1. Open a part.」；遍历须由 FirstFeature 起、GetNextFeature 回 Nothing 收尾  <sub>（`Get_Error_Codes_for_Features_Example_VB.md`）</sub>
- 「Preconditions: 1. Open: …cstick.sldprt 2. Run macro.」—— SaveBMP 前须有已打开文档  <sub>（`Save_Model_as_Bitmap_Example_CSharp.md`）</sub>

### `holes_and_finishing`（3 条）

- 建草图槽前须已打开新零件文档并进入草图：SelectByID2 选 Front Plane → InsertSketch(true) → CreateSketchSlot  <sub>（`Get_Sketch_Slot_Using_Sketch_Point_and_Segment_Example_CSharp.md`）</sub>
- 调 InsertFeatureChamfer 前须先选中要倒角的边（示例两次 SelectByID2 EDGE，第二次 append=true）  <sub>（`Get_Edge_Chamfer_Distances_Example_CSharp.md`）</sub>
- 加几何关系前须存在草图、活动文档须是零件文档、目标图元须已选中（示例三处 SendMsgToUser2 检查）  <sub>（`Constrain_Sketch_Example_CSharp.md`）</sub>

### `geometry_and_delivery_review`（3 条）

- SaveBMP 前置：模型文档须已打开（示例打开 cstick.sldprt，并从 swApp.ActiveDoc 取模型）  <sub>（`Save_Model_as_Bitmap_Example_CSharp.md`）</sub>
- GetPartBox 前置逐字：' Preconditions: Part is open.'（零件须处于打开状态）  <sub>（`Get_Part_Bounding_Box_Example_VB.md`）</sub>
- 遍历 FirstFeature/GetNextFeature 前置逐字：' Preconditions: Open a new part document.'  <sub>（`Select_Plane_Example_VBNET.md`）</sub>

### `simulation_study_create`（3 条）

- Open public_documents\samples\Simulation Examples\tutor1.sldprt.  <sub>（`Create_Topology_Study_Example_VBA.txt`）</sub>
- 1. Open a part.  <sub>（`Get_and_Set_Material_Visual_Properties_Example_VB.md`）</sub>
- 1. Open a part.  <sub>（`Set_Material_Property_Name_Example_VB.md`）</sub>

### `config_and_export`（3 条）

- Open a part document.（示例经 GetActiveConfiguration 取 CustomPropertyManager）  <sub>（`Get_Custom_Properties_for_Configuration_Example_VB.md`）</sub>
- Open a part or assembly.（配置族读写的最小前置）  <sub>（`Add_Derived_Configurations_Example_VB.md`）</sub>
- 改尺寸前须 SelectByID2 选中特征，再 GetSelectedObject6(1,-1).Parameter("D3") 取尺寸对象。  <sub>（`Change_Dimension_Example_VB.md`）</sub>

### `surface_features`（3 条）

- 调用 FeatureExtruRefSurface3 前须用 SelectByID2 选中草图：SelectByID2("Sketch1","SKETCH",0,0,0,False,0,...)  <sub>（`Insert_Extruded_Reference_Surface_Example_VB.md`）</sub>
- 缝合前须先把要缝的曲面按 mark = 1 选中（示例：Surface-Extrude1 mark 1 + Surface-Plane1 mark 1；Fill_Holes 另用 Select2(True,1)）  <sub>（`Create_Surface_Knit_Feature_Example_VB6.md`）</sub>
- 选曲面之前须先 swSelectionManager.EnableContourSelection = False  <sub>（`Create_Surface_Knit_Feature_Example_VB6.md`）</sub>

### `loft_and_sweep`（3 条）

- 放样：轮廓选中顺序即语义（示例 Sketch1 先、Sketch2 append）；引导线另给 4098 等 mark  <sub>（`Insert_Protrusion_Blend_Example_CSharp.md`）</sub>
- 放样：各轮廓草图须先建好并 InsertSketch(true) 关闭草图，之后才能被选中  <sub>（`Get_Guide_Curves_in_Loft_Feature_Example_CSharp.md`）</sub>
- 扫描：官方 CreateDefinition→CreateFeature 路线在 CreateFeature 之前不调用 AccessSelections  <sub>（`Insert_Swept-boss_Feature_Example_VB.md`）</sub>

### `sketch_primitives_b1`（3 条）

- 官方示例先 CreateLine 建一条线段并 ClearSelection2(true)，才调 CreateTangentArc（弧需有可相切的既有段）  <sub>（`Create_Tangent_Arc_Example_CSharp.md`）</sub>
- 示例调用序：InsertSketch(true)→SelectByID2 选基准面→ClearSelection2(true)→Create3PointArc  <sub>（`Create_3_Point_Arc_Example_CSharp.md`）</sub>
- CreateParabola 示例断言活动文档须为零件（GetType==swDocPART），且须先选中一个 RefPlane 才 InsertSketch  <sub>（`Translate_Sketch_Example_CSharp.md`）</sub>

### `sketch_edit_ops_b3`（3 条）

- Trim 示例：先用 SelectByID2 以 SKETCHSEGMENT 选中两条线，才调 SketchTrim(swSketchTrimCorner,0,0,0)  <sub>（`Trim_Sketch_Entities_Example_CSharp.md`）</sub>

★ 其余见 `output/t2-preconditions-checkable.json` 的 `checkable` 数组。
