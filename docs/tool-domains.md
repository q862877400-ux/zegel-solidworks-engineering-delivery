# 工具域目录（★ 由 `tools/gen_tool_domain_catalogue.py` 生成，**不要手改**）

> **为什么有这个文件**：工具数已达 **433** 个，**不可能**列进 `AGENTS.md`
> （该文件受 **65536 字节**指令预算限制，本仓已因此把 known-facts 拆到 `docs/`）。
> ★ 行业口径（MCP 官方 *client best practices* / Anthropic *advanced tool use*）是：
> **系统提示里只写「类别」，工具定义按需发现** ⇒ 本文件就是那份「类别目录」 ✓
> ★ 全量索引（每个工具一行）见 [`mcp-tools.md`](mcp-tools.md)。

| 域（`scripts/sw_*.py`） | 工具数 | 代表性能力 |
|---|---:|---|
| `part` | 33 | Get Part Bounding Box · Add Sketch Relation · Mirror Feature ★注入键: model |
| `view` | 24 | Get Active View · Activate Model View · Redraw Graphics Window ★注入键: model / view |
| `simulation` | 21 | Set Part Material · Get Simulation Default Element Size And Tolerance · Apply a Fixed Restraint (Fixture) to t ★注入键: model / study / sw_app |
| `costing` | 20 | Get Costing Manager · Collect the Costing Overview · Read the Whole Cost Analysis ★注入键: cost_analysis / cost_body / cost_manager / cost_part / defaults / model |
| `feature_readback` | 16 | Read Extrude Feature Depth · Read Extrude Feature Parameters · Read Linear Pattern Parameters ★注入键: model |
| `simulation_loads` | 16 | Apply a Pressure Load to the Selected Faces · Apply a Torque Load to the Selected Faces · Apply a Gravity Load ★注入键: manager |
| `topology` | 16 | Create SOLIDWORKS Topology Study · Collect SOLIDWORKS Topology Evidence · Run SOLIDWORKS Topology Study ★注入键: study / sw_app |
| `review` | 15 | Set Standard View · Activate Model For Preview · Clear Selection For Preview ★注入键: model |
| `assembly_doc` | 12 | Create an Exploded View (IAssemblyDoc.CreateExplodedView) · Automatically Explode the Assembly (IAssemblyDoc.A ★注入键: asm_model / component / doc |
| `weldment` | 12 | Collect Weldment Evidence · Ensure Weldment Cut List · Update Weldment Cut List ★注入键: manager / model |
| `drawing_query` | 11 | List Drawing Sheets · Get Current Drawing Sheet · List Drawing Views ★注入键: model |
| `hole_features` | 10 | List Hole Wizard Standards · List Hole Wizard Fastener Types · List Hole Wizard Fastener Table Types ★注入键: model / sw |
| `assembly` | 9 | List Assembly Components · List Assembly Mates · Check Assembly Interference ★注入键: asm_model / component / model |
| `drawing_expose` | 9 | Drawing Projected / Model View · Drawing Section View · Drawing Detail View ★注入键: drawing_model |
| `selection` | 9 | Clear All Selection Colors (ISelectionMgr.ClearSelectionColors) · Selection: Suspend Selection List · Set Sele ★注入键: selection |
| `selection_spec` | 9 | Current Selection · Clear Selection · List Entities On Body ★注入键: model |
| `sketch_primitives` | 9 | Add a 3-Point Corner Rectangle (any angle) · Add a 3-Point Center Rectangle (any angle) · Add a Parallelogram ★注入键: model |
| `motion` | 8 | Create a Motion Study on the Active Assembly · Collect the Motion Study Summary · Validate the Motion Studies  ★注入键: asm_model / motion_study |
| `simulation_study_options` | 8 | List Simulation Study Options · List Every Simulation Study-Option Setter · Configure the Static Solver Option ★注入键: options / study |
| `export` | 7 | Export the Active Part to STEP (read-back verified) · Export the Active Part to STL (read-back verified) · Exp ★注入键: model |
| `macro_guard` | 7 | Normalize a Model Name to a Prompt Family · Build the VBA-Generation Prompt for a Model Family · Extract the V |
| `mold` | 7 | Insert Mold Parting Line · Insert Mold Shut-off Surface · Run Mold Draft Analysis ★注入键: model |
| `sheet_metal` | 7 | Collect Sheet Metal Evidence · Create Sheet Metal Base Flange · Create Sheet Metal One Bend ★注入键: model |
| `sketch_edit_ops` | 7 | Trim Sketch Entities · Extend a Sketch Entity · Offset Sketch Entities (offset entities) ★注入键: model |
| `automation_knowledge` | 6 | Explain an HRESULT in Plain Words (repo's own table) · Suppress Modal Dialogs (CommandInProgress = True) · Rel ★注入键: sldworks |
| `document_data` | 6 | Inspect the Document's Configurations · Create (and optionally activate) a Configuration · Activate a Configur ★注入键: model |
| `ref_geometry` | 6 | Insert Center of Mass · Insert Global Bounding Box · Insert Coordinate System ★注入键: model |
| `simulation_results` | 6 | Collect the Mesh Quality Evidence Of The Injected Mesh · Activate Result Plot · Delete Result Plot ★注入键: mesh / results |
| `gui_modal` | 5 | Capture a Full-Screen PNG (Modal-Dialog Forensics) · Find Visible Top-Level Modals Owned by This Process · Mod |
| `sheet_metal_weld_entry` | 5 | Sheet Metal Miter Flange · Sheet Metal Closed Corner · Weldment End Cap ★注入键: model |
| `sketch_modify_ops` | 5 | Move Sketch Entities · Rotate Sketch Entities · Scale Sketch Entities ★注入键: model |
| `surface_edit_ops` | 5 | Insert Planar Surface · Insert Offset Surface · Insert Ruled Surface ★注入键: model |
| `surface_features` | 5 | Create Extruded Surface Feature · Knit Selected Surfaces · Extend Surface Feature ★注入键: model |
| `busy` | 4 | Is SolidWorks Busy Right Now? (attributable windows only) · Is SolidWorks STUCK? (not responding AND no solver |
| `custom_property` | 4 | Get One Custom Property · List All Custom Properties · Count the Custom Properties ★注入键: model |
| `delivery` | 4 | Collect Assembly BOM · Build a BOM Traceability Record · Build a Pack-and-Go Audit Matrix ★注入键: model |
| `drawing_create_missing` | 4 | Drawing Break Lines (Broken View) · Drawing Auxiliary View · Drawing Surface Finish Symbol ★注入键: model |
| `equation` | 4 | Add a Global Equation (read-back verified) · List the Global Equations (and their values) · Evaluate (Solve) t ★注入键: model |
| `geometry_selectors` | 4 | Available Point Selectors · Available Direction Selectors · Resolve a Direction Selector to a Vector ★注入键: model |
| `gui_focus` | 4 | 读当前前台窗口句柄（GUI 焦点前置关卡，非 SolidWorks API） · Read the Current Focus State · Bring a Window to the Foreground and V |
| `render_material` | 4 | List Render Materials · Collect Appearance Evidence · Refresh Scene Graph ★注入键: model |
| `simulation_study` | 4 | Generate Simulation Study Report · Create Simulation Mesh For Mesh Control · 取算例的载荷与夹具管理器 ★注入键: study |
| `sketch` | 4 | Count Sketch Lines · Count Sketch Arcs · Count Sketch Segments |
| `toolbox_index` | 4 | List the Toolbox Standards · Load the Toolbox Index · Search the Toolbox Index |
| `chamfer_geometry` | 3 | Volume Removed by a 45° Equal-Distance Chamfer on a Straight Edge · Volume Removed by a 45° Equal-Distance Cha |
| `drawing_view` | 3 | Get a Drawing View's Scale (by name) · Set a Drawing View's Scale (read-back verified) · Collect Every Drawing ★注入键: model |
| `feature_entry_ops` | 3 | Cosmetic Thread (insert by cylindrical edge) · Flatten Surface (face mark=1 + anchor mark=16) · Thicken / Thic ★注入键: model |
| `sketch_edit` | 3 | Create a Sketch Chamfer · Mirror the Selected Sketch Entities · Convert Entities into the Active Sketch ★注入键: model |
| `com_traps` | 2 | Which Member Should Replace This Deprecated One? · Find Where a Member Is REALLY Implemented (excludes reflect |
| `gear` | 2 | Calculate an External Spur Gear (pure geometry) · Create an External Spur Gear Body ★注入键: model |
| `import_mesh_reference` | 2 | 设置 OBJ/STL/VRML 网格导入偏好（全局系统偏好 + 记旧值） · 还原网格导入偏好（按 report 记下的旧值写回并逐条读回校验） ★注入键: sw |
| `surface` | 2 | Collect Surface Evidence · Is This IModeler Surface Method Usable on This Machine? ★注入键: sw_app |
| `surface_ref_ops` | 2 | Insert Lofted Reference Surface · Create Revolved Surface ★注入键: model |
| `curve_and_split` | 1 | Insert Curve Through Points ★注入键: model |
| `gtol` | 1 | Insert a GTol Annotation (gets the object back) ★注入键: model |
| `helix` | 1 | Insert a Helix / Spiral ★注入键: model |
| `loft` | 1 | Create Loft Feature ★注入键: model |
| `macro` | 1 | Run a Macro File (ISldWorks.RunMacro2) ★注入键: sw_app |
| `mass_property` | 1 | Read Part Mass Properties ★注入键: model |
| `measure` | 1 | Measure Selected Entities ★注入键: model |
| `misumi` | 1 | Suggest MISUMI Part Numbers |
| `preflight` | 1 | 检查 Python COM 依赖包（comtypes / pywin32）是否缺失 |
| `sensor` | 1 | Read Sensors ★注入键: model |
| `session` | 1 | Undo Actions ★注入键: model |
| `sketch_dimensions` | 1 | 尺寸链（链式标注） ★注入键: model |
| `sketch_status` | 1 | Sketch Fully-Defined Status ★注入键: model |
| `sweep` | 1 | Create Sweep Feature ★注入键: model |
| `units` | 1 | Read Document Units ★注入键: model |
| `wrap` | 1 | Create Wrap Feature ★注入键: model |

**合计 433 个工具 · 69 个域**

