# 官方示例的前置条件 × 本仓「真机运行证据」对账

> **这份文件回答**：`capabilities.yaml` 里标成 `verified` 的能力，
> 它们的运行证据**是否覆盖了官方示例揭示的前置条件**？
>
> **答案：98 条里 75（保守）/ 80（原始判读） 条有未覆盖的前置**（`all_covered` 只有 **3** 条）。
> ★ **数有两个口径**：原始判读 **80**；按 V1 审计者要求收窄（**只留「出自真实示例文件、且不是示例运行环境说明」的前置**）后是 **75** —— **保守值用 75**。
>
> **来源与口径**
> - **能力条目**：`capabilities.yaml` 的 **100** 条 `level: verified`（共 112 条能力 / 320 条 evidence）。
> - **前置条件的来源**：把每条能力的 `tools` 追到它调的 **COM 成员**，
>   再用 `docs/recon/member-to-example-index.md` + `specs/203-*/recon/b3-4-merged.json`
>   反查**哪些官方示例用到那些成员**，读那些示例（`C:\swapi\examples\`）里写的**前置条件**。
> - **判定**：每条前置给三态 `covered` / `not_covered` / `cannot_tell`；
>   ★ `covered` **必须附该条 evidence 里的逐字片段**。
> - **分工**：Bunny（`opencode-zen` / `space-bunny-free`）**50 箱**（每箱 2 条能力）。
> - ⚠ **本文件不含行号**。

## 一、统计

| 指标 | 数 |
|---|---|
| 送入判定的能力（`level: verified`） | **100** |
| 实际判完 | **98**（缺 1 箱 = 2 条未判） |
| 抽出的前置条目（原始） | **534** |
| —— ★ **其中 `from` 真的是示例文件的** | **约 459**（V1：120 条 `from` 不是 `C:\swapi\examples` 的文件；51 条自写「无示例」）⇒ **示例派生口径的分母 = 459** |
| —— `covered`（evidence 里确实提到） | **131** |
| —— `not_covered`（evidence 里没提） | **322** |
| —— `cannot_tell`（原始） | **81** |
| —— ★ **其中 28 条是 agent 的元陈述**（「无先例/零命中/无从判定」），**不是前置** | ⇒ **该口径下 ≈53** |
| 能力级：**`has_uncovered`** | **80** |
| 能力级：`all_covered` | **3** |
| 能力级：`cannot_tell` | **15** |

**★ 引文闸**：`covered` 那 131 条的 `evidence_quote` **逐字回查该条 evidence 数组** ——
**命中 131 · 不命中 0**。

## 二、★ 核心结论

> **98 条 `verified` 里，80 条（82%）至少有一条前置
> 是官方示例明确要求、而它们的运行证据里没提到的。**

★ **这不是说那 80 条「不 verified」** —— `verified` 的定义是「**有我们自己的运行证据**」（`AGENTS.md` A4），
本件**没有改任何 level**。它说的是：**那些证据的覆盖面**比官方示例揭示的前置**窄**。

### 2.1 我抽查了 4 条（**确认前置是真信息，不是噪声**）

| 能力 | 未覆盖的前置（逐字浓缩） | 我的判断 |
|---|---|---|
| `mass_property_read` | 「示例显式设 `UseSystemUnits=false`（注释 *Use document property units*）才按文档单位给读数」 | **真前置**，且是**单位口径**问题 |
| `sheet_metal` | 「边线法兰须先调 `FeatData.AddEdges(边数组, 草图数组)` 把边与草图喂进 FeatData」 | **真前置**，是**调用序**问题 |
| `export_delivery` | 「调用前须准备 **12 个双精度**的 3×4 对齐数组（示例 `dataAlignment(0..11)`）」 | **真前置**，是**实参准备**问题 |
| `chamfer_fillet_on_selection` | ★ **我原来写「全部 covered」是错的** —— 数据是 **3 covered + 1 not_covered**（V1 抓到）；那 1 条是 `block.sldprt` 文件前置 | 判定**基本正确，但我的抽查表写错了** |

⇒ ★ **抽查支持这个结论**：那些前置是官方示例写明的**具体要求**（单位开关 / 调用序 / 实参准备），
**不是**把无关示例硬凑进来的噪声。

## 三、`has_uncovered` 的 80 条（**这是给主线的清单**）

| # | 能力 | 前置 covered / 总 | note（agent 自述） |
|---|---|---|---|
| 1 | `solidworks_addin_host` | 0/9 | 工具 probe_addin_host 自身零 COM 调用（winreg/ctypes），COM 成员在进程内 C# Add-in；evidence 一句 pytest 未提 |
| 2 | `part_and_features` | 4/14 | 旋转、撤销、加尺寸三条前置被 evidence 逐字覆盖；包覆/镜像/圆形阵列的 mark 与调用序、旋转选序、单位与传感器的文档前置均未出现在 evidence 里（只在 l |
| 3 | `external_spur_gear_geometry` | 0/3 | 唯一 evidence 只有一行 pytest（tests/test_cad_reliability.py），未提任何官方前置；建模链的选面-建草图-选草图序列一条都没覆盖。 |
| 4 | `holes_and_finishing` | 3/9 | 证据只覆盖孔标准链与读点两处；槽、倒角、切除轮廓、草图关系的前置均未被证据提及。HoleWizard5 示例不计入（本族走画圆+FeatureCut4）。 |
| 5 | `parameter_updates` | 2/5 | 证据覆盖了单位换算疑点与精确尺寸名；GetSystemValue3 的数组形态、Empty 出参与 EditRebuild3 三项前置证据未提。 |
| 6 | `custom_properties_and_bom` | 0/6 | 两条 evidence 只证 set/read_custom_property 三条属性往返；未提活动配置、装配体文档类型、组件已加载。BOM 表前置不适用：本实现走 IAss |
| 7 | `pack_and_go` | 0/5 | 两条 evidence 皆为 pytest 名，未提源文档已存盘、目标目录存在，也未提 SetSaveToName 先于 Flatten 的调用序（本实现顺序相反）。 |
| 8 | `motion_study` | 0/7 | 实现读自 scripts/sw_motion.py（tool_specs_batch40 挂载）。evidence 只有一句 pytest 名称，未提任何示例前置。 |
| 9 | `drawings_and_bom` | 0/3 | 实现读自 scripts/sw_delivery.py。collect_assembly_bom 走 GetComponents 遍历组件，非 BOM 表；BOM 表官方示例用 |
| 10 | `export_delivery` | 3/5 | SaveBMP 与 ExportToDWG2 的示例前置已被 evidence 覆盖；ExportToDWG2 的 12 个对齐参数未见覆盖；SaveAs3 覆盖 5 个导出工 |
| 11 | `geometry_and_delivery_review` | 0/5 | 唯一 evidence 是一句 pytest 调用，不含任何官方示例前置字样，5 条前置全未覆盖。BMP 与包围盒两例都要求文档已打开。 |
| 12 | `configurations_and_design_tables` | 0/7 | evidence 只有一条 pytest，7 条前置里 6 条未被提及；官方属性示例走 config.CustomPropertyManager，本实现走 model.Exte |
| 13 | `sheet_metal` | 1/6 | 只有「闭轮廓」这条前置被 evidence 逐字点到；边线法兰的 AddEdges、加强筋的两个支撑面、放样折弯的先有基体法兰均未提；拔模无官方示例。 |
| 14 | `weldments` | 3/11 | 结构构件那半前置齐（轮廓文件、路径草图、选区）；切割清单/焊接文件夹/更新清单/读属性四族的前置未提。 |
| 15 | `topology_optimization` | 0/6 | evidence 三条只写了脚本名、证据文件缺失、契约测试；加载项、类型库、开文档、DeleteStudy 调用序一条都没提到。 |
| 16 | `costing` | 0/7 | evidence 只有一条（verify_costing_e2e.py 的 partial 5/6）；官方 Costing 示例的前置一条都没出现在里面。 |
| 17 | `sketch_edit_ops` | 1/4 | evidence 数组只写了 create_sketch_chamfer 那次冒烟（选中两条是草图线段、非模型边/面）；convert_entities 与 sketch_mi |
| 18 | `gtol_insert` | 2/6 | 两条官方示例都以「已存在的工程图 + 已存在的 GTol」为前提；本条证据是在「新零件」上现建对象，工程图与 GTol 来源前提未覆盖。 |
| 19 | `drawing_current_sheet_query` | 2/7 | 「必须是工程图」与「首个视图即图纸本身」两条已覆盖；多图纸、需按选择加载图纸、有视图、文档属性开关等前置只验过空图纸，均未覆盖。 |
| 20 | `file_custom_property_read` | 1/2 | Add_and_Get 那份是焊件【特征】级属性，与文件级不同，未计其前置；示例的 Open the Immediate window 属 VBA 脚手架未计入。 |
| 21 | `sketch_build` | 4/6 | 模板存在/Immediate window 属 VBA 脚手架未计入；CreateCenterLine 的官方示例只出现在 3D 草图与角度尺寸里，未计前置。 |
| 22 | `feature_build_extrude` | 2/4 | 起止面 mark=32/1 与轮廓选择属本工具未暴露的端条件，判 cannot_tell；唯一硬缺口是证据从未打开过任何零件文件。 |
| 23 | `chamfer_fillet_on_selection` | 3/4 | 官方用 SelectByID2 按点选边、本仓走 IEntity.Select4，机制不同但前置（先选中）已被证据覆盖；AccessSelections 属读数能力，未计入。 |
| 24 | `mass_property_read` | 1/3 | 「文档已存在并可读」被 evidence 覆盖；UseSystemUnits 单位开关与 AddBodies（组件级读数）两条官方示例前置在 evidence 里一字未提。 |
| 25 | `assembly_read` | 1/3 | 装配文档已打开这条被 evidence 覆盖；MateGroup/子特征下钻这条前置没被提到；ToolsCheckInterference 是否必须，两份官方示例互相矛盾。 |
| 26 | `simulation_loads_wiring` | 2/6 | 两份 recon 索引对 cosworks 成员零命中；该官方 Simulation 示例由实现自身来源块逐字指向，见 D:\AI\SW\_raw\cworksapi\。 |
| 27 | `simulation_study_create` | 1/10 | 材料两条前置来自 sldworks 侧示例（SetMaterialPropertyName2 同形调用），与仿真研究建链是否同源存疑；cosworks 侧索引覆盖为零。 |
| 28 | `simulation_load_family_breadth` | 5/10 | 只有 AddPressure 有官方示例（重载+参数形状已对上）；加载项、材料、DispArray 数组形状、压力值提交四项证据未提。 |
| 29 | `mesh_size_sanity_gate` | 0/4 | 该闸门只经 GetBodies2+GetBodyBox 量包围盒；四条 evidence 全是过数与静态门禁，没提零件已打开、GetBodies2 口径或近似值警告。 |
| 30 | `feature_readback_criterion` | 2/4 | 两条活动文档/打开零件前置有逐字证据；三参 GetWhatsWrong 的「count>0 才调」条件 evidence 未提；EditRebuild3 无对口示例。 |
| 31 | `modeling_feature_readback_tools` | 3/11 | shell/dome/包围盒的「先有文档」有逐字证据；选面 mark=1、筋的抽壳+折线+选草图、模板前置全未提；复合曲线前置 evidence 只说「前置成立」未指名。 |
| 32 | `config_and_export` | 0/11 | evidence 仅三行（脚本名 + 10/12 + 8/8 + 静态门禁），无一条提到示例前置；SaveAs3 导出侧官方无示例。 |
| 33 | `render_materials_and_appearance` | 0/5 | evidence 只有两行（脚本名 + 4/4 + 工具清单）；「须先建材质并赋到面」这条外观前置一字未提。 |
| 34 | `selection_helpers` | 2/13 | 13 工具共用选择族成员。evidence 只覆盖 GetSelectionPoint2/GetSelectionPoint 的「须选中面」；文档存在、AccessSelect |
| 35 | `declarative_hole_creation` | 1/10 | 5 个孔工具链为 SelectByID2 选面 → InsertSketch → CreateCircleByRadius → FeatureCut4。示例前置（先选面/先选两 |
| 36 | `weldment_cut_list` | 4/8 | 官方示例的 Solid Bodies>Show、Description 重命名、SetAutomaticCutList 三项前置，evidence 均未提及。 |
| 37 | `simulation_solver_options` | 0/2 | CosmosWorks 族无任何官方示例；唯一相关示例是通用加载项的 Load_and_Unload_Add-in，其 DLL 存在性前置 evidence 未提。 |
| 38 | `topology_constraints_and_controls` | 0/13 | 官方拓扑示例全文 881 行只此一份，13 条前置全来自它；evidence 仅一句「8 项过 7」+计数对照，一条都没写到。 |
| 39 | `topology_readback` | 2/9 | 2 条 covered 靠逐字片段；加载项/类型库/DeleteStudy/类型 13 等前置 evidence 均未提；求解与读结果无相关示例。 |
| 40 | `costing_readback` | 0/9 | 证据只有一句「5/6 · 四个读数真的读到数据」，模板位置、CostPart 转换、BodyStatus 已分析等示例前置一条未记。 |
| 41 | `render_material_library` | 3/7 | covered 的是 .p2m 绑定与 create→add_entity→add 次序；未提「先选面再 AddEntity」与「先建显示状态/传真实名字数组」。 |
| 42 | `preview_and_review_report` | 0/6 | 证据只有一行 PASS 读数（ok=true / 20 个特征 / 4 个非空 BMP / ActiveView 报 <unknown>），六条官方前置一条都没提到。 |
| 43 | `motion_validation_and_preconditions` | 0/9 | evidence 仅 1 句、不含任何前置文字；tlb 只出现在 limitations，故 9 项全 not_covered。 |
| 44 | `drawing_views_and_summary` | 3/6 | 多图纸、图纸页伪视图、先切页三项 evidence 未提；GetSheetFormatName 两索引零命中。 |
| 45 | `weldment_profile_and_curve` | 0/5 | evidence 只证 create_weldment_profile 建出 .sldlfp；配合的装配体/双实体前置与官方 CreateDefinition 入口均未提。 |
| 46 | `costing_templates_and_defaults` | 1/4 | 只覆盖「模板存在」一条；打开零件文档与 WaitForUIUpdate 调用序未提，GetTemplateName 无相关示例。 |
| 47 | `pattern_and_mirror` | 3/6 | 镜像两条 mark 前置有逐字证据；圆周阵列的种子特征 mark=4 与样件文档未提；InsertAxis2 示例属旋转域，不计入。Get_Mirror_Solid 例子走的是 |
| 48 | `drawing_view_operations` | 3/7 | 比例与 UseSheetScale 前置有逐字证据；选视图、EditRebuild3、首视图是图纸、可见件数断言均未提；Get_Annotations 例子宿主是 ModelD |
| 49 | `surface_features` | 1/7 | evidence 只覆盖 mark=1 边界边；草图 mark0 选中、缝合 mark=1、EnableContourSelection=False、VPatchBoundar |
| 50 | `geometry_measurement` | 1/3 | 只有「未选中 ⇒ 拒绝」被 evidence 提到；ArcOption 取值表与 Calculate(Nothing)/status 判读都没提。 |
| 51 | `loft_and_sweep` | 2/7 | evidence 只覆盖「必须选中→未选则显式拒绝」；mark 取值、轮廓顺序、草图关闭、AccessSelections 调用序均未出现在 evidence。 |
| 52 | `reference_axis` | 1/3 | 选区前置完全未进 evidence（limitations 提到「未验两点/两平面交线」，但按纪律只认 evidence）；仅入口层级被覆盖。 |
| 53 | `sketch_primitives_b1` | 0/11 | evidence 数组只有一个产物路径；示例揭示的前置（既有相切段、四点、2D 草图、零件文档）在 evidence 里无任何逐字提及。 |
| 54 | `sketch_edit_ops_b3` | 0/8 | evidence 数组只有产物路径；SketchOffset2 需 mark=1 选段、Trim 需两条段等官方前置在 evidence 里无逐字提及。 |
| 55 | `sketch_modify_ops` | 0/6 | 三个官方示例的前置（选基准面、活动/选中草图、零件文档）evidence 全未提；Stretch 无示例可对账。 |
| 56 | `surface_edit_ops` | 2/8 | Create_Ruled_Surface_From_Edge_Example_VB 调的是 IModeler.CreateRuledSurfaceFromEdge，非本条成员， |
| 57 | `ref_geometry` | 2/8 | 坐标系那条示例要求先按 mark 选 3 个草图实体，evidence 只写了 InsertCoordinateSystem 一句 ⇒ 未覆盖。Create_3D_Boundi |
| 58 | `curve_and_split` | 3/9 | 草图/面 mark 与三步式已被 evidence 逐字覆盖；模板存在、Boss-Extrude1 mark 0、配合参考 mark 1+2 未提；轮廓型无官方示例。 |
| 59 | `surface_offset` | 1/4 | evidence 只写到「先建一张曲面⇒4 张面选中」；多体零件前置、示例的 mark 0 逐张选法、建曲面那步的草图选中均未提。 |
| 60 | `surface_planar_region` | 4/6 | 选法两条（边 / 草图）与 mark=1 都已实测对照；唯官方前置「文档模板须存在」evidence 未提。 |
| 61 | `replace_face` | 4/6 | 两个 mark 的数值已被 evidence 覆盖；但官方示例 mark=2 选整个 SURFACEBODY 的选法 evidence 未提。 |
| 62 | `sketch_dimension_horizontal` | 1/4 | 唯一官方示例属工程图语境。实质前置「先选中实体」被 evidence 逐字覆盖；「零件或装配体已打开」evidence 未提 ⇒ not_covered；装配与图纸转换两条属该 |
| 63 | `sketch_dimension_vertical` | 2/3 | 官方唯一示例是工程图语境（尺寸加在视图里的边）；前置 2「装配体需完全解析」不适用于本条故未计。evidence 未提直线/朝向要求，且竖直尺寸加在水平线上也成。 |
| 64 | `feature_revolve_cut` | 2/7 | evidence 只覆盖「文档里已有轴+剖面」；mark 表、mark=32、同实体只选一次、选区顺序均未提。示例顺序与本仓「轴先于轮廓」相反。受影响体 mark=1 不适用（ |
| 65 | `sketch_slot_types` | 0/3 | 证据只给参数表与段数 0→5；官方示例三条前置（新建零件、选面进草图、传官方枚举）evidence 全未提。 |
| 66 | `surface_flatten` | 1/4 | 面(1)+锚点(16) 有逐字证据；打开零件、撕裂边 mark=8 未提，几何类型那条示例说不清。 |
| 67 | `surface_untrim` | 2/4 | 只覆盖「先造出真被剪裁曲面」这一步；InsertUntrimSurface2 自身前置（face or edges）无示例 ⇒ cannot_tell。 |
| 68 | `feature_loft_cut` | 1/6 | InsertCutBlend 无官方示例 ⇒ 自身前置只能 cannot_tell；证据只覆盖 mark=1 与顺序，引导线/中心线/参考基准面三项未提。 |
| 69 | `surface_delete_hole` | 0/2 | 核心成员官方无示例，前置无法对账；证据只写「真正的带孔平面」，未提平面区域的 mark=1 边界选择。 |
| 70 | `feature_cosmetic_thread` | 2/3 | 选边前置已被三格对照覆盖；但示例里螺纹线挂在孔的子特征下、须 GetFirstSubFeature 才找得到，证据未提。 |
| 71 | `sketch_spline` | 2/4 | 官方示例在 3D 草图内建样条且 SimulateNaturalEnds=true；证据用 start_sketch 的草图 + False，示例未就此写前置。 |
| 72 | `sketch_spline3_2d` | 1/5 | CreateSpline3 官方只有 on-surface 示例；探针只做 2D 两格对照，面选取/surfs 组装与示例文档前置均未在 evidence 提及。 |
| 73 | `sketch_rotate_or_copy_3d` | 1/5 | 示例强调「选中草图→EditSketch→全部图元 Select4」才调用；探针只 Insert3DSketch+CreateLine 后直接调，选区与进出草图序未在 evid |
| 74 | `sketch_equation_curve` | 3/8 | 证据只覆盖「先 start_sketch」与两种表达式形态（参数那格实测 0→0）；新零件文档、ClearSelection2、收尾 InsertSketch、改写表达式四项前 |
| 75 | `curve_through_xyz` | 1/6 | 证据只覆盖三步式顺序与特征树判据；模板存在、c:\temp 目录、坐标按米三项前置证据未提；InsertCurveFile 无官方示例故 cannot_tell。 |
| 76 | `select_by_ray` | 3/4 | 唯一相关示例是 Select_Face_Using_Intersecting_Ray；mates/wrap 等只是碰巧同名成员，已排除。唯一 not_covered 是 Imm |
| 77 | `feature_hole_wizard5` | 2/8 | SSize 规格串与 Mark=0 定位已逐字覆盖；未覆盖：-1 未用参数约定、FastenerType 与 Standard 配对、模板/文档必须存在、Immediate 窗 |
| 78 | `sketch_offset_on_surface` | 2/5 | tools 为空；实现是 tools/prove_offset_on_surface_per_example.py。UseFront 与 Geodesic 两条只写在 limi |
| 79 | `coverage_gap_batch1` | 2/8 | 三条成员分别落在 sw_surface_ref_ops、sw_hole_features、sw_sketch_status；证据只报「树增量/回 int」，未交代选位与取草图对 |
| 80 | `assembly_exploded_views` | 5/9 | 8 个成员有官方示例。未覆盖：Immediate 窗口；GetExplodedViewConfigurationName 实参应为**视图名**——示例给了答案，而本仓 lim |

## 四、`all_covered` 的 3 条（**证据覆盖完整**）

| 能力 | 前置数 |
|---|---|
| `helix_and_spiral` | 3 |
| `sketch_chamfer` | 5 |
| `sketch_line2` | 1 |

## 五、`cannot_tell` 的 15 条

| 能力 | note |
|---|---|
| `requirements_planning` | 实现是 apps/desktop 编排层纯 Python，零 COM 成员 ⇒ 无官方示例前置可核，不编前置。 |
| `headless_open_format_writing` | 实现是纯 Python/ezdxf/matplotlib/可选 OCP，不碰 COM；两份证据均为 pytest 且 OCP 后端被 monkeypatch，无官方示例前置可核。 |
| `dfm_checks` | cadstudio_check_dfm 走 scripts/dfm_review.write_dfm_report，load_automation=False，零 COM 成员，故无官方示例可 |
| `simulation_and_fea` | 8 个工具全落在 CosWorks ICWStudy/StudyOptions 成员上；索引与 2839 份示例 grep 零命中。 |
| `autocad_headless_preview` | 不调任何 COM 成员（load_automation=False），纯 Python + 第三方 ezdxf；两份 recon 索引 grep 工具名/ezdxf/PreviewScene  |
| `dxf_preview_scene` | 同一工具，同样 0 个 COM 成员；evidence 里的 tools/verify_dxf_preview_e2e.py 也只用 ezdxf+subprocess；recon 索引 0 命 |
| `autocad_script_backend` | AutoCAD ActiveX 实现；两索引对 SendCommand/ActiveDocument 等成员零命中，SaveAs 命中属 SolidWorks 同形异义，无官方示例前置可对账。 |
| `autocad_dotnet_backend` | 零 COM 调用，是文件系统+子进程预检，无 AutoCAD 成员可查；两索引对 AcMgd 零命中，AutoCAD 命中属 SolidWorks 样例路径，同串异义已排除。 |
| `standard_parts_toolbox` | 实现 scripts/sw_toolbox_index.py 全 97 行只 import json/pathlib/typing，无一处 get_com_member ⇒ COM 成员为空； |
| `mesh_create_readback` | 2839 篇官方示例与两索引对 CreateMesh/CreateMeshForMeshControl/GetDefaultElementSizeAndTolerance 全 0 命中；cos |
| `analysis_run_readback` | GetPlotCount 唯一命中的示例属 SwMotionStudy(Motion API)、非 ICWResults；RunAnalysis/GetPlotNames/ElementCou |
| `mold_analysis` | 成员读自 scripts/sw_mold.py。MoldDraftAnalysis 在 IModelDoc2，底切走后继 IFeatureManager.MoldUndercutDetect2 |
| `surface_ref_ops` | 两个成员在示例索引与 examples 目录均零命中（Insert_Extruded_Reference_Surface / Create_360-degree_Revolve 用的是别的成员 |
| `surface_revolve` | InsertRevolvedRefSurface 在两索引与官方页均 0 命中 ⇒ 示例侧前置无从取得；同族 InsertPlanar/Sew/ExtruRefSurface 示例属巧合，未计 |
| `macro_execution` | 8 个工具中只有 macro_run 碰 COM（RunMacro2）；另 7 个是 sw_macro_guard 纯文本函数（该文件无 COM 导入，已核）。无官方示例可对账 ⇒ 全条 ca |


## 六、★★ 三裁判门禁（**V2 找到 7 条反例**）

**V1 审计者（DeepSeek）** 抽检 12 条 · **9 条判据缺陷** · **不同意我 6 个数**
**V2 对抗者（Bunny）** 攻 86 条 · **反例 7 条**（其中 4 条硬反例）
**V3 复算者（Bunny）** 独立重算三态与 verdict · **零差异** · 引文闸独立复跑**一致**

### 6.1 V2 的反例（**含 3 个编造的示例文件名**）

| 能力 | 那条前置 | V2 指出 |
|---|---|---|
| `costing` | 必须先打开一个零件文档（machined_part.sldprt / sheet_metal_part.sldp | **被引示例只出现 machined_part.sldprt；sheet_metal_part.sldprt 全文 208 行零命中，属编造的第二个文件名。** |
| `chamfer_fillet_on_selection` | 零件 block.sldprt / block20.sldprt 必须存在并已打开 | **被引示例的前置只有 block.sldprt 一条；block20.sldprt 全文零命中，第二个文件名是编的。** |
| `pattern_and_mirror` | 官方前置：先打开含种子特征的零件文档（varyinstance.sldprt / holecube.sldprt | **被引示例 81 行只打开 varyInstance.sldprt；holecube.sldprt 零命中，第二个文件名是编的。** |
| `part_and_features` | 包覆用的草图必须是 2D，官方原话 3D sketches are invalid | **标成「官方原话」的那串字不在被引示例里：该示例全文只谈选基准面-画圆-选草图选面-InsertWrapFeature2，从未提 2D/3D。该原话出自 InsertWrapFeature2 的 Remarks。** |
| `parameter_updates` | SetSystemValue3 之后必须调 EditRebuild3 才生效（示例两处均在设值后重建） | **「两处」是编的计数：示例里 SetSystemValue3 与 EditRebuild3 各只出现 1 次。** |
| `costing_readback` | GetBodyCount() > 0 才有实体可列，否则官方示例打印 No bodies 后退出 | **示例的退出判据是 isBody（有没有「加工体」），由 GetBodyType()==Machined 分支里置位，与 GetBodyCount>0 是两个条件；有体但非加工体照样会走 No bodies 分支。** |
| `part_and_features` | 该示例另设两条：装配体须完全解算；边若无法转成工程图视图则不建尺寸 | **内容本身属实，但 from 字段是 GBK 乱码拼串、不是可解析路径；且串尾标「（1）」而这两条其实是示例的前置(2)与 NOTE，标注错位。** |

⇒ ★★ **最严重的是 3 处编造示例文件名**：`sheet_metal_part.sldprt` / `block20.sldprt` / `holecube.sldprt`
—— agent 把**另一个文件的名字**写进了被引示例的前置里，而该示例全文**零命中**。
★ 这正是本项目已知的 Bunny 失效模式（203 轮实测 0.15% 编造率），**这次出现在"前置的 from 字段"上**。

### 6.2 V2 指出：**6 条 `covered` 的引文其实不覆盖**

| 能力 | 引文 | 为什么不覆盖 |
|---|---|---|
| `sketch_chamfer` | 选中两条（选区计数 2） | 这条前置的主张是「该成员在两索引与 examples 内 0 份示例」——是关于示例语料「缺失」的事实；quote 只证明选了 2 条线，完全无法佐证缺失。且 from 本身是 API 文档页、不是示 |
| `weldments` | 工具不读选区也不依赖选中状态：它自己按草图名取线段 | 前置要求「须先 SelectByID2 选中再赋值」，而 quote 明说本工具不依赖选中状态。引用句是在否认该前置，不是覆盖它——按此证据该前置属未验证而非已覆盖。 |
| `export_delivery` | ★ 另记前置条件：零件路径要求「钣金件 + 必须先保存」 | quote 是把前置原样复述一遍（自述式），不是任何一次真机读数。用被检验的主张去证明自己，属循环取证，不构成覆盖。 |
| `weldments` | 下有 111 个 .sldlfp | 前置是两个合取项：轮廓库特征(.sldlfp) 存在 且 零件模板存在。quote 只覆盖前一半，对「零件模板」一字未提，合取项未整体覆盖。 |
| `export_delivery` | export_to_bmp(model, path, 800, 600) 建成 | 前置指名官方示例要先打开 cstick.sldprt 设为活动文档；quote 里的 model 是泛指、未指名任何文档，也未显示活动文档身份，只证明「导出成功」。 |
| `part_and_features` | 唯一差别是本轮每次选之前都 ClearSelection2(True) | 前置是「AddDimension2 调用前实体处于选中态」；quote 描述的是清空选区的做法差异，既没证明调用时刻有选中实体，也没证明那条线由 CreateLine 现画后直接标注。 |

★ 最典型的一类是**循环取证**：`export_delivery` 那条引文逐字是「★ 另记前置条件：零件路径要求…」——
**把被检验的主张原样复述一遍当证据**。

### 6.3 V2 指出：**5 组分类偏低** + **8 条 `from` 根本不是示例文件**

* `declarative_hole_creation`：**not_covered 实为 covered** —— 与 selection_helpers 完全同一条前置（GetSelectionPoint2 / Open a part or assembly and select a face / 同一个 from 文件 Create_Drag_Arr
* `selection_helpers`：**not_covered 实为 covered** —— 「GetBodies2 前置：Open a part or assembly.」（from=Select_Bodies_Example_VB.md）判 not_covered、quote 空；而 declarative_hole_creat
* `preview_and_review_report`：**not_covered 实为 covered（系统性）** —— 6 条 not_covered 里 6 条都是「须有已打开的模型文档」类（Model document is open / Open a part / Verify that the specified part exists），而本能力 
* `custom_properties_and_bom`：**cannot_tell 应为「不适用」** —— note 自述「BOM 表前置不适用：本实现走 IAssemblyDoc.GetComponents，不读 BOM 表，故记 cannot_tell」。既然实现根本不碰 BOM 表，这条前置不是「说不清」而是与本能力无关，混进 81 条 c
* `(数据面)`：**from 字段不可解析** —— not_covered 的 from 里有 8 个根本不是示例文件：6 个是 API 文档页（如 'IFeatureManager/HoleWizard5.md ## Remarks'、'IModelDocExtension/SketchO

### 6.4 V1 的 9 条判据缺陷（挑最关键的 5 条）

1. 把示例的 Preconditions 段等同于本能力的 API 前置：那段是「怎么跑这篇示例」（开哪个 .sldprt、开 Immediate 窗口、装加载项），对 Python COM 近零区分力，却全量计入 not_covered。
2. from 无类型约束：既装示例文件名，也装「（无示例）」/索引文件名/成员 .md 页/本仓源码路径（120/534）⇒ 单位口径不成立，无法机械判定是否出自官方示例。
3. 无「无示例 ⇒ 不产出前置」的兜底：51 条前置在 from 明写「无示例」时仍被产出（autocad_dotnet_backend 5 条读自本仓 subskills 源码）并计入分母。
4. covered 只判「引文字面出现在 evidence 里」，不判「evidence 证明了该前置」⇒ 蕴含式前置被判未覆盖（Part is open），无关引文被判覆盖（建草图→拉伸→读质量属性）。
5. 一条 text 常捆两件事（示例夹具＋真语义）却只有一个 state 位，只能二选一（Create a new drawing document.（GetProperties2 读的是当前图纸页））。

★ V1 对「80 是否高估」的原话：**「计数上不算高估：剔除样板句/非示例来源/元陈述后仍 79，
再要求『实质 API 前置』后 75。但『官方示例明确要求』这句高估 —— 322 条 `not_covered` 里
约 60 条是示例自身的运行环境要求，且至少 3 条是假阳性。保守可写的数：75/98。」**

## ⚠ 明确记下的限度

* ⚠ **没改任何 `level`** —— 本件只产出「覆盖情况」，改等级是主线的决定。
* ⚠ **前置的抽取依赖「能力 → 工具 → COM 成员 → 示例」这条链**，链条任一环断了就落在 `cannot_tell`
  （81 条前置 + 15 条能力级）。
* ⚠ **有 2 条能力未判**（1 箱未落盘：`idx=14`）。
* ✅ **三裁判已齐**：V3 **零差异**（三态/verdict/引文闸独立复跑一致）；V1 报 9 条判据缺陷、把可信数收窄到 **75/98**；**V2 找到 7 条反例**（含 3 个编造示例文件名、6 条循环取证的 covered）⇒ 头部数已改成 **75（保守）/ 80（原始）** 并全部留档在 §六。
* ⚠ **`covered` 只表示「evidence 里提到了这个前置」，不表示「真机验过这个前置」** ——
  两者的差别正是本件**不能**回答的（那要真机，属主线）。
* ⚠ 前置的**措辞是 agent 概括的**（不是官方原文逐字）；只有 `covered` 那 131 条
  的 `evidence_quote` 过了逐字闸。
