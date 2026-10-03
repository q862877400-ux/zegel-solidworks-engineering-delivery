# patterns-shard-1 —— 分歧根因分类与「批量可行性」判断（**分片 1：audit-01 ~ audit-04**）

> **范围**：`specs/202-user-coverage-gaps/recon/audit-vs-official/` 下 **audit-01-surface / 02-sheetmetal / 03-weldment / 04-assembly** 的 A/B/C 三面，共 **12 份**、**44 条分歧行**。
> **方法**：逐份逐行读原文，一行一条，不合并不丢。
> **纪律**：只读；未运行 SolidWorks、未运行 pytest；**未改动仓内任何文件**；本文件是本次唯一写入。
> ★ **与 Lead 首轮分类的关系**：`tools/classify_audit_divergences.py` 的类名被**借用但重新判定**（见 §0.3 与 §2 的差异说明），**没有照抄它的结论**。

---

## §0. 读法与口径

### §0.1 抽了多少、怎么数的

| 文件 | 核对面 | 分歧行数 | 高 / 中 |
|---|---|---|---|
| `audit-01-surface-A.md` | A 签名一致性 | 4 | 2 / 2 |
| `audit-01-surface-B.md` | B 前置与 mark | 4 | 3 / 1 |
| `audit-01-surface-C.md` | C 废弃链与枚举 | 3 | 3 / 0 |
| `audit-02-sheetmetal-A.md` | A（+ 附录 1 条属 C 面） | 3 + 1 附录 | 4 / 0 |
| `audit-02-sheetmetal-B.md` | B | 4 | 2 / 2 |
| `audit-02-sheetmetal-C.md` | C | 3 | 2 / 1 |
| `audit-03-weldment-A.md` | A | 2 | 2 / 0 |
| `audit-03-weldment-B.md` | B | 3 | 2 / 1 |
| `audit-03-weldment-C.md` | C | 4 | 2 / 2 |
| `audit-04-assembly-A.md` | A | 1 | 1 / 0 |
| `audit-04-assembly-B.md` | B | 4 | 1 / 3 |
| `audit-04-assembly-C.md` | C | 8 | 7 / 1 |
| **合计** | **A 11 · B 15 · C 18** | **44** | **31 / 13** |

**域分布**：01-surface 11（25%）· 02-sheetmetal 11（25%）· 03-weldment 9（20%）· 04-assembly 13（30%）。

★ **一条横向规律（域序 vs 核对面）**：

| 域 | A 面（签名） | B 面（前置/mark） | C 面（废弃/枚举） |
|---|---|---|---|
| 01-surface | 4 | 4 | **3** |
| 02-sheetmetal | 4 | 4 | **3** |
| 03-weldment | 2 | 3 | **4** |
| 04-assembly | **1** | 4 | **8** |

⇒ **越晚写的域，签名越干净，但代际越落后**：A 面从 4 掉到 1，C 面从 3 涨到 8。`audit-04-assembly-C.md` 一片就占了全分片 C 面的 44%（8/18）、全分片的 18%。

### §0.2 引用格式

每条给 **文件名 + 可 grep 的原文片段**（不写行号）。

### §0.3 我为什么没有直接沿用 Lead 的类名

`tools/classify_audit_divergences.py` 的 `PATTERNS` 是一个**有序关键词表 + `break` 命中即停**，且搜索对象是 `what + theirs`（**含官方原文**）。三点后果，本分片里都能看到：

1. **匹配的是官方引文里的样板词，不是根因**。`audit-04-assembly-C.md` 全部 8 条的官方栏都有 `Obsolete. Superseded by …`，但同一份 `audit-04-assembly-B.md` 的 mark 表里官方也反复写 "mark" ⇒ 关键词命中的是**引文的措辞**。
2. **`mark` 排在第一位**，任何官方引文里出现 "Mark" 的行都会被吃进「mark 值不对/没给」，哪怕它的根因是「调用序反了」或「常量域收窄」。Lead 报的 **mark 类 20 条（33%）** 与本分片实测的「真·mark 语义分歧」条数并不吻合。
3. **`split("|")` 不识别转义竖线**。这些核对表的单元格里有大量 inline code 的 `\|`（例：`audit-07-sketch-C.md` 的 `\| swSketchChamfer_DistanceDistance \| -1 \|`）。`\|` 会被当成分隔符 ⇒ `cells[3]` 取到的不是「分歧点」列 ⇒ 分类输入被污染。

⇒ **本分片改用「按分歧点的因果链」归类**：判据是「**错在哪一层**」，不是「原文里出现了哪个词」。

---

## §1. 全量分歧表（44 条）

**根因类代号**（详见 §2）：`E`=废弃成员 · `P`=前置没做 · `Ps`=前置语义当成硬约束 · `O`=参数顺序 · `Sq`=调用序 · `U`=实参量纲 · `Us`=实参语义喂错 · `T`=类型/形状 · `N`=枚举域错 · `Ns`=枚举/成员表完整性断言 · `M`=成员缺席。

★ **批量可行性三档**：`高` = 静态脚本能全找 **且** 共用修法能全改 · `中` = 能全找但改法多样 / 需逐条核后继 · `低` = 只能逐条。

| # | 文件 | 面 | 类 | 我们的原文（可搜索） | 官方的原文（可搜索） | 置信度 | 批量可行性 |
|---|---|---|---|---|---|---|---|
| 1 | `audit-01-surface-A.md` | A | **O** | `sw_surface.py`：`get_modeler(sw_app), "CreateConicalSurface", origin, axis, float(half_angle), float(radius)` | `CreateConicalSurface.md`：`CreateConicalSurface( Center, Direction, System.double Radius, System.double SemiAngle )` | 高 | 低 |
| 2 | `audit-01-surface-A.md` | A | **O** | `sw_surface.py`：`get_modeler(sw_app), "CreateBsplineSurface", control_points, weights, knots, degree` | `CreateBsplineSurface.md`：`CreateBsplineSurface( Props, UKnots, VKnots, CtrlPtCoords )` | 高 | 低 |
| 3 | `audit-01-surface-A.md` | A | **T** | `sw_surface.py`：`"CreateSheetFromSurface", surface, float(tolerance)`（包装把第 2 参叫 `tolerance`） | `CreateSheetFromSurface.md`：`CreateSheetFromSurface( SurfaceIn, System.object UvRange )` ／ `- **UvRange**: Array of UV values for this surface` | 中 | 中 |
| 4 | `audit-01-surface-A.md` | A | **T** | `sw_surface_ref_ops.py`：`get_com_member(model, "InsertLoftRefSurface2", …, int(start_matching_type), int(end_matching_type))` | `InsertLoftRefSurface2.md`：`void InsertLoftRefSurface2( Closed, KeepTangency, ForceNonRational, TessToleranceFactor, System.short StartMatchingType, System.short EndMatchingType )` | 中 | 中 |
| 5 | `audit-01-surface-B.md` | B | **Sq** | `sw_surface_features.py`：`selected = _select_all_surface_faces(model, mark=0)` → `PreTrimSurface` → `PostTrimSurface`（两步之间**没有**任何再选择） | `PostTrimSurface.md`：「Before calling this method: 1. Call [[IFeatureManager::PreTrimSurface]]. 2. **Select the trimming surfaces or trim tool.**」 | 高 | 低 |
| 6 | `audit-01-surface-B.md` | B | **P** | `sw_surface_features.py`：`get_com_member(fm, "FeatureExtruRefSurface3", *args)`（函数体内没有任何 `SelectByID2`）；`"sketch_name": str(sketch_name)` 只出现在返回值里 | `FeatureExtruRefSurface3.md`：「Before calling this method, **select the entities for the extruded surface** using [[IModelDocExtension::SelectByID2]]」 | 高 | 低 |
| 7 | `audit-01-surface-B.md` | B | **P** | `sw_surface_features.py` docstring：`★ 前置：★ **文件里要有曲面体**`；调用处 `get_com_member(fm, "FeatureBossThicken",` 之前无任何选择动作 | `FeatureBossThicken.md`：「The surface must be selected with a mark of 1.」「If **UseAutoSelect** is false, the user must select the **bodies**」 | 高 | 低 |
| 8 | `audit-01-surface-B.md` | B | **P** | `sw_surface_features.py`：`if int(end_condition) not in (0, 1):` ＋ `_select_all_surface_faces(model, mark=0)`（先 `ClearSelection2(True)` 再只选面） | `InsertExtendSurface.md`：「**The selected point or surface to which to extend should be in the selection list.**」 | 中 | 低 |
| 9 | `audit-01-surface-C.md` | C | **E** | `sw_surface.py`：`"CreatePlanarSurface", point, normal` ／ `"CreateCylindricalSurface", origin, axis, float(radius)` ／ `"CreateSphericalSurface", center, float(radius)` ／ `"CreateConicalSurface"`（另有 `require_runtime_available("CreatePlanarSurface")` 等四处守卫） | `CreatePlanarSurface.md`／`CreateCylindricalSurface.md`／`CreateSphericalSurface.md`／`CreateConicalSurface.md` 四页**各**：`Obsolete. Superseded by [[IModeler::…2]].` | 高 | 高 |
| 10 | `audit-01-surface-C.md` | C | **N** | `sw_surface_features.py`：`if int(end_condition) not in (0, 1):` ／ `"end_condition 只支持 0（按距离）/ 1（到选定点）：%r"` | `InsertExtendSurface.md`：`- 2 - Extend surface up to a selected surface`；`swSurfaceExtendEndCond_e.md`：3 个成员 `Distance \| 0` / `UpToPoint \| 1` / `UpToSurface \| 2` | 高 | 高 |
| 11 | `audit-01-surface-C.md` | C | **N** | `sw_surface_edit_ops.py`：`RULED_TYPE_MEANINGS = { 0: "Tangent to Surface", … 4: "Sweep" }` | `swRuledSurfaceType_e.md`：`swRuledSurfaceType_TangentToSurface \| 1` … `swRuledSurfaceType_Sweep \| 5`（**没有 0**） | 高 | 高 |
| 12 | `audit-02-sheetmetal-A.md` | A | **U** | `sw_sheet_metal.py`：`data.BendAngle = float(spec.angle)`（`create_one_bend`）；`OneBendSpec.validate`：`raise ValueError("折弯角度必须位于 0 与 360 度之间")` | `ISketchedBendFeatureData/BendAngle.md`：`System.double BendAngle {get; set;}` ／ Returns「0.261799 <= … radians (15 degrees) <= 1.5708」 | 高 | 中 |
| 13 | `audit-02-sheetmetal-A.md` | A | **U** | `sw_sheet_metal.py`：`data.BendAngle = float(spec.angle)`（`create_edge_flange`）；`EdgeFlangeSpec` docstring `"""@brief 边法兰的可制造参数，长度单位为米，角度为度。"""`，默认 `angle: float = 90.0` | `IEdgeFlangeFeatureData/BendAngle.md`：Returns「Flange angle; default value is 1.5707963267949 radians」 | 高 | 中 |
| 14 | `audit-02-sheetmetal-A.md` | A | **U** | `sw_sheet_metal.py`：`data.Angle = float(spec.angle)`（`create_draft`）；`DraftFeatureSpec` docstring `"""@brief 拔模的可制造参数，角度为度、深度为米。"""` | `IDraftFeatureData2/Angle.md`：Returns「Draft angle in radians」 | 高 | 中 |
| 15 | `audit-02-sheetmetal-A.md`（附录） | C | **E** | `sw_sheet_metal.py` 两处：`error_code = int(get_com_member(feature, "GetErrorCode") or 0)` | `IFeature/GetErrorCode.md`：`Obsolete. Superseded by [[IFeature::GetErrorCode2]].` | 高 | 中 |
| 16 | `audit-02-sheetmetal-B.md` | B | **P** | `sw_sheet_metal.py`：`"""@brief 在已选中的边上创建原生边法兰。"""`；`_apply` 内只设 `UseDefaultBendRadius` / `BendRadius` / `BendAngle` / `UseDefaultBendAllowance`（**无** `AddEdges`、**无** `InsertSketchForEdgeFlange`） | `IEdgeFlangeFeatureData/AddEdges.md`：「Before calling this method, call [[IModelDoc2::InsertSketchForEdgeFlange]] to associate the sketches with the edges.」＋ 例子 `Call FeatData.AddEdges(vFlangeEdges, vSketchFeats)` | 高 | 低 |
| 17 | `audit-02-sheetmetal-B.md` | B | **P** | `sw_sheet_metal_weld_entry.py`：`get_com_member(model, "InsertSheetMetalClosedCorner")`；`"preconditions_held": None,` ／ `"precondition_note": "★★ **官方页无 \`## Remarks\` 段 ⇒ 前置查不到**"` | `Create_and_Modify_Closed_Corner_Feature_Example_VBNET.md`：两次 `SelectByID2("", "FACE", …, True, 1, Nothing, 0)` 紧接 `swModel.InsertSheetMetalClosedCorner()` | 高 | 低 |
| 18 | `audit-02-sheetmetal-B.md` | B | **Ps** | `sw_sheet_metal_weld_entry.py`：`if body is None: return {"ok": False, … "error": "body 为 None …"}` ／ `if part_doc is None: … "PPartDocIn 是对象形参"` ／ `"preconditions_held": bool(body is not None and part_doc is not None)` | `InsertMidSurface.md`：`- **PBodyIn**: [[Body]] in the context of an assembly; **otherwise, null or Nothing**` ／ `- **PPartDocIn**: … otherwise, null or Nothing` | 中 | 低 |
| 19 | `audit-02-sheetmetal-B.md` | B | **P** | `sw_sheet_metal.py`：`def create_draft(model, face_ref, spec: DraftFeatureSpec):` ／ `"""@brief 在已选中的面上创建原生拔模特征。"""`（**`face_ref` 在整个函数体内不再出现**） | `IDraftFeatureData2/FacesToDraft.md`：「Gets or sets the faces that define this draft feature.」＋ `Selections that Define Features.md`：「1. First, call the AccessSelections method …」 | 中 | 低 |
| 20 | `audit-02-sheetmetal-C.md` | C | **E** | `sw_sheet_metal.py`：`# 使用无歧义的 GetErrorCode 可兼容 pywin32 静态与动态代理。` ／ `error_code = int(get_com_member(feature, "GetErrorCode") or 0)`（两处逐字重复） | `IFeature/GetErrorCode.md`：`Obsolete. Superseded by [[IFeature::GetErrorCode2]].`；后继页 `GetErrorCode2( out System.bool IsWarning )` 且**无** Obsolete 行 | 高 | 中 |
| 21 | `audit-02-sheetmetal-C.md` | C | **N** | `sw_sheet_metal.py`：`SW_END_COND_BLIND = 0` ／ `data.D1EndConditionType = SW_END_COND_BLIND` ／ `data.D2EndConditionType = SW_END_COND_BLIND` | `IBaseFlangeFeatureData/D1EndConditionType.md`：「as defined in [[swFlangeOffsetTypes_e]]」；`swFlangeOffsetTypes_e.md` 六成员 `swFlangeOffsetBlind \| 1` … `swFlangeOffsetUptoEdgeAndMerge \| 6` —— **没有值为 0 的成员**；官方例子 `swBaseFlangeFeat.D1EndConditionType = 1` | 高 | 高 |
| 22 | `audit-02-sheetmetal-C.md` | C | **N** | `sw_sheet_metal_weld_entry.py`：`SW_RELIEF_NONE = 4` ／ `SW_RELIEF_TEAR_BEND = 5` ／ `SW_FLANGE_BEND_CENTER_LINE = 4` ／ `SW_FLANGE_BEND_SHARP = 5` ／ `SW_FLANGE_BEND_TANGENT = 6`；实参原样透传 `int(relief_type),` | `InsertSheetMetalMiterFlange.md`：`- **ReliefType**: … valid selections:` 逐条只列 `swSheetMetalRelievObround` / `swSheetMetalReliefRectangular` / `swSheetMetalReliefTear`；`- **FlangePos**: … valid selections:` 只列 3 条 | 中 | 中 |
| 23 | `audit-03-weldment-A.md` | A | **Us** | `sw_weldment.py` 来源块：`IFeatureManager.InsertWeldmentCutList2(Object SortOptions) -> Feature` ／ `⚠ InsertWeldmentCutList2 接受一个 Object 参数（排序选项），官方未标注其类型` ／ 调用 `get_com_member(manager, "InsertWeldmentCutList2", sort_options)` | `InsertWeldmentCutList2.md`：`Feature InsertWeldmentCutList2( System.object Bodies )` ／ `- **Bodies**: Array of [[Body2]] objects` | 高 | 低 |
| 24 | `audit-03-weldment-A.md` | A | **Us** | `sw_weldment.py` 来源块：`Feature InsertSubWeldFolder2(Object Folder)   ← 1 参` ／ `⚠ 官方未标注该 Object 参数的确切类型（预期为 IStructureSystemFolder），故只透传不校验` ／ `get_com_member(manager, "InsertSubWeldFolder2", folder)` | `InsertSubWeldFolder2.md`：`Feature InsertSubWeldFolder2( System.object BodyArray )` ／ `- **BodyArray**: Array of [[Body2]] objects` | 高 | 低 |
| 25 | `audit-03-weldment-B.md` | B | **P** | `sw_weldment.py`：`本函数走 2 参版以支持指定父文件夹；不传 folder 时传 None。` ／ `feature = get_com_member(manager, "InsertSubWeldFolder2", folder)`（全程无选实体/取 Body2） | `InsertSubWeldFolder2.md`：「Creates a sub weld folder feature containing the specified weldment bodies.」；`Insert_Weldment_Features_Example_VB.md`：`Set obj(0) = selMgr.GetSelectedObject6(1, -1)` ／ `fm.InsertSubWeldFolder2((v))` | 高 | 低 |
| 26 | `audit-03-weldment-B.md` | B | **P** | `sw_weldment.py`：`feature = get_com_member(manager, "InsertWeldmentCutList2", sort_options)` | `Insert_Weldment_Cut_List2_Example_VB.htm`：`v = Part.GetBodies2(0, True)` ／ `Set cutListFeature = Part.FeatureManager.InsertWeldmentCutList2(v)` | 高 | 低 |
| 27 | `audit-03-weldment-B.md` | B | **P** | `sw_weldment.py`：`update_ok = bool(call_com_member(body_folder, "UpdateCutList")) if body_folder else False` | `IBodyFolder/UpdateCutList.md`：「To find out if the part contains a weldment feature, use [[IPartDoc::IsWeldment]]. If it does, then use [[IBodyFolder::GetAutomaticCutList]]…」 | 中 | 低 |
| 28 | `audit-03-weldment-C.md` | C | **E** | `sw_weldment.py` docstring：`最后用 ``GetErrorCode`` 拒绝硬错误（与上游 ``create_base_flange`` 一致）。` ／ `error_code = int(get_com_member(feature, "GetErrorCode") or 0)`（注释通篇只谈「与上游同构」） | `IFeature/GetErrorCode.md` 首行：`Obsolete. Superseded by [[IFeature::GetErrorCode2]].` | 高 | 中 |
| 29 | `audit-03-weldment-C.md` | C | **N** | `sw_weldment.py` 来源块：`# ⚠ MateAlignment 的枚举在两套官方源里查不到（\`sw_know find MateAlignment\` 未命中可用的枚举定义），故本函数只做 int 透传` ／ `mate_alignment: int = 0,` ／ `set_com_member(data, "MateAlignment", int(mate_alignment))` | `IProfileCenterMateFeatureData/MateAlignment.md`：`## Returns`：`Mate alignment as defined in [[swMateAlign_e]]`；`swMateAlign_e.md`：`swMateAlignALIGNED \| 0` · `swMateAlignANTI_ALIGNED \| 1` · `swMateAlignCLOSEST \| 2` · 另 3 个成员逐字 `Obsolete. Do not use.` | 高 | 中 |
| 30 | `audit-03-weldment-C.md` | C | **N** | `sw_weldment.py`：`SW_FM_MATE_PROFILE_CENTER = 101  # swFmMateProfileCenter` ／ `return _create_from_definition(model, SW_FM_MATE_PROFILE_CENTER, _apply)` | `IFeatureManager/CreateDefinition.md`：`- **Type**: Feature name ID as defined in [[swFeatureNameID_e]]:` 之后逐条列 35 个 `swFm*`，**其中没有 `swFmMateProfileCenter`**；`swFeatureNameID_e.md` 确有 `\| swFmMateProfileCenter \| Profile center mate \|` | 中 | 中 |
| 31 | `audit-03-weldment-C.md` | C | **Ns** | `sw_weldment.py` 文件头：`# ⚠ 扫描 131 个条目确认：焊件相关的**只有这 3 个**，没有「下料表」或「构件分割」` | `swFeatureNameID_e.md` 另有 6 行：`swFmStrctSysCnrFeat` / `swFmStrctSysCnrGrpFeat` / `swFmStrctSysCnrMgmtFeat` / `swFmStrctSysFeat` / `swFmStrctSysGrpFeat` / `swFmStrctSysMbrFeat` | 中 | 低 |
| 32 | `audit-04-assembly-A.md` | A | **M** | `sw_assembly.py` `add_mate5_checked()`：紧接 `if name:` → `try:` → `mate.Name = name` | `IMate2` 成员表 40 行**无 `Name`**；CHM `IMate2_members.html` Public Properties 16 行**无 `Name`**；反射 `## IMate2` 段**无 `Name` / `set_Name`**（**三源一致缺席**） | 高 | 中 |
| 33 | `audit-04-assembly-B.md` | B | **Sq** | `sw_assembly.py`：`interference.Done()` 紧接着 `count = int(safe_get_com_member(interference, "GetInterferenceCount") or 0)`，再往后 `_got = call_com_member(interference, "GetInterferences")` | `IInterferenceDetectionMgr/Done.md`：「Stops the interference detection.」；`GetInterferences.md`：「Calculates and gets the interferences.」；两处官方例子把 `pIntMgr.Done` **注释掉并放在 `GetInterferences()` 之后** | 高 | 低 |
| 34 | `audit-04-assembly-B.md` | B | **P** | `sw_assembly.py`：`interference = asm_model.InterferenceDetectionManager`（本行之前没有任何调用） | `Run_Interference_Detection_Example_VB.md`：`swAssemblyDoc.ToolsCheckInterference` ／ `Set pIntMgr = swAssemblyDoc.InterferenceDetectionManager`（三行相邻）；`IAssemblyDoc/ToolsCheckInterference.md`：「Opens the Interference Detection PropertyManager.」 | 中 | 低 |
| 35 | `audit-04-assembly-B.md` | B | **P** | `sw_assembly.py`：`component = _add_component5(asm_model, component_path, config_name, x, y, z)` 是**首选路径**（此时只有 `if not os.path.exists(component_path):`） | `IAssemblyDoc/AddComponent5.md`：「The specified file must be **loaded in memory**.」；官方例子序：`OpenDoc6` → `ActivateDoc3` → `AddComponent5` | 中 | 低 |
| 36 | `audit-04-assembly-B.md` | B | **P** | `sw_assembly.py`：`if not entity1.Select2(False, mark):` ／ `if not entity2.Select2(True, mark):` | `IAssemblyDoc/AddMate5.md`：「1. Call [[IModelDoc2::ClearSelection2]] … 2. Call [[IModelDocExtension::SelectByID2]] to select each entity to mate.」 | 中 | 中 |
| 37 | `audit-04-assembly-C.md` | C | **E** | `sw_assembly.py`：`return asm_model.AddComponent4(` | `IAssemblyDoc/AddComponent4.md`：`Obsolete. Superseded by [[IAssemblyDoc::AddComponent5]].` | 高 | 高 |
| 38 | `audit-04-assembly-C.md` | C | **E** | `sw_assembly.py`：`mate = asm_model.AddMate5(` | `IAssemblyDoc/AddMate5.md`：`Obsolete. Superseded by [[IAssemblyDoc::CreateMate.]]` | 高 | 高 |
| 39 | `audit-04-assembly-C.md` | C | **E** | `sw_assembly.py`：`if not entity1.Select2(False, mark):` | `IEntity/Select2.md`：`Obsolete. Superseded by [[IEntity::Select4]].` | 高 | 高 |
| 40 | `audit-04-assembly-C.md` | C | **E** | `sw_assembly.py`：`if component.SetTransformAndSolve2(transform):` | `IComponent2/SetTransformAndSolve2.md`：`Obsolete. Superseded by [[IComponent2::SetTransformAndSolve3]].` | 高 | 高 |
| 41 | `audit-04-assembly-C.md` | C | **E** | `sw_assembly.py`：`asm_model.EditSuppress()` | `IModelDoc2/EditSuppress.md`：`Obsolete. Superseded [[IModelDoc2::EditSuppress2]].` | 高 | 高 |
| 42 | `audit-04-assembly-C.md` | C | **E** | `sw_assembly.py`：`asm_model.EditUnsuppress()` | `IModelDoc2/EditUnsuppress.md`：`Obsolete. Superseded by [[IModelDoc2::EditUnsuppress2]].` | 高 | 高 |
| 43 | `audit-04-assembly-C.md` | C | **E** | `sw_assembly.py`：`"reference_type": int(get_com_member(mate_entity, "ReferenceType") or -1),` | `IMateEntity2/ReferenceType.md`：`Obsolete. Superseded by [[IMate2Entity::Reference2]].` | 高 | 高 |
| 44 | `audit-04-assembly-C.md` | C | **E** | `sw_assembly.py`：`sw.ActivateDoc2(title, False, errors)`（except 回退分支） | `ISldWorks/ActivateDoc2.md`：`Obsolete. Superseded by [[ISldWorks::ActivateDoc3]].`（CHM 无该成员页 ⇒ **仅一源**） | 中 | 中 |

---

## §2. 按类汇总

| 类 | 名称 | 条数 | 占比 | 分布（域） | 分布（面） | **批量可行性** | 一句话理由 |
|---|---|---|---|---|---|---|---|
| **P** | 前置没做（官方要求的前置步骤缺失） | **12** | **27%** | 01:3 · 02:3 · 03:3 · 04:3 | 全部 B 面 | **低** | 官方「该先做什么」写在**三种不同载体**里（`## Remarks` 散文 / 官方例子调用序 / `Selections that Define Features.md` 专章），且 `audit-02-sheetmetal-B.md` 自证**官方页与官方例子两源相反**（`InsertGussetFeature3`）⇒ 静态脚本无从判谁对。 |
| **E** | 用了废弃成员（代际落后） | **12** | **27%** | 01:1 · 02:2 · 03:1 · 04:8 | 全在 C 面（+02-A 附录） | **高（找）/ 中（改）** | 官方 `Obsolete. Superseded by` 行就在每个成员页**首行**，CHM 是第二源 ⇒ 纯集合运算；但**后继签名逐个不同**（`GetErrorCode2` 多 `out bool`），且第 20 条注释写明**明知故犯**（pywin32 by-ref 限制）⇒ 只能「批量**报**」不能「批量**换**」。 |
| **N** | 枚举取值域错（收窄 / 偏移 / 认错枚举 / 白名单外） | **6** | **14%** | 01:2 · 02:2 · 03:2 | 全在 C 面 | **高（找）/ 中（改）** | `C:\swapi\enums\*.md` 每页 front matter 带 `enum_member_count`、成员表是 `名 \| 值` 两列 ⇒ 「我们的 `SW_XXX = <整数>` 是否在该集合里」是纯集合题；但第 22 条要看**成员页的 valid selections** 而非 enum 页，判据不同源。 |
| **U** | 实参量纲不符（度 vs 弧度） | **3** | **7%** | 02:3 | 全部 A 面 | **中** | **本分片最规整的一类：3/3 同形态**（`data.BendAngle` / `data.BendAngle` / `data.Angle` = `float(spec.angle)`），一条「扫 `data.X = float(spec.*angle*)` + 读官方 `## Returns` 找 `radians`」的规则能全找出来；但取值域校验要逐条改，且 `ISMGussetFeatureData.ProfileAngleDim` **官方页没给单位**（audit-02-A 记「查不到」）⇒ 不能一刀切。 |
| **O** | 参数顺序不符 | **2** | **5%** | 01:2 | A 面 | **低** | 第 1、#2 条的对调双方**都是 `System.double` / `System.object`**（`Radius`/`SemiAngle`、`Props`/`CtrlPtCoords`）⇒ AST 与反射都分不出谁是谁，只能靠官方 Parameters 段的**形参名**去匹配我们的**变量名**，形参名不可靠时必误判。 |
| **Sq** | 调用序不符（成员之间的先后） | **2** | **5%** | 01:1 · 04:1 | B 面 | **低** | 要跨成员做顺序推理（`Pre→选中→Post`、`Get→Done`），且证据只在官方例子的**排列**里；同一条往往同时是「O」或「P」，根因分层要人来判。 |
| **Us** | 实参语义喂错（形参是数组/对象，传了别的东西） | **2** | **5%** | 03:2 | A 面 | **低** | 判据是官方形参名 + `- **Bodies**: Array of [[Body2]] objects` 的**语义**；改法三选（删参 / 换参 / 补一次 `GetBodies2`），无法自动决定。 |
| **T** | 类型/形状不符（short vs int · 标量 vs 数组） | **2** | **5%** | 01:2 | A 面 | **中** | 「找」是高：出厂反射 `iface_sldworks.txt` 有每个形参的 VT 类型，我们代码里的 `int(...)` / `float(...)` 包装是 AST 可见的，`float()` 包过的实参**一定不是数组** ⇒ 一条规则全找；「改」要逐条（包 `VARIANT(VT_ARRAY\|VT_DISPATCH)` 还是换包装）。 |
| **Ps** | 前置语义被当成硬约束（与官方 `null or Nothing` 相反） | **1** | **2%** | 02:1 | B 面 | **低** | 1 条；改法不是「补一步」而是「**分叉装配体/零件两种上下文**」，与 `P` 完全不同。 |
| **Ns** | 枚举/成员表的完整性断言与官方不符 | **1** | **2%** | 03:1 | C 面 | **低** | 1 条，且分歧在**源码注释**里；改法是重写注释不是改代码，且「这 6 条算不算焊件相关」本身是口径问题。 |
| **M** | 成员缺席（官方没有这个成员） | **1** | **2%** | 04:1 | A 面 | **中** | 「找」是高（成员表集合运算，`audit-04-A` 已用三源证过）；「改」要看 `CreateMate` 的签名，而那正是 #38 的后继 ⇒ **与 E 类同源，应一起改**。 |

### §2.1 两个辅助视角

**按核对面 × 批量可行性**

| 面 | 条数 | 高 | 中 | 低 |
|---|---|---|---|---|
| A 签名一致性 | 11 | 0 | **4**（#3 #4 #12 #13 #14） | 7 |
| B 前置与 mark | 15 | 0 | **1**（#36） | 14 |
| C 废弃链与枚举 | 18 | **14**（#9 #10 #11 #21 #37…#44） | **4** | 0 |

★ **这是本次最硬的一条结论**：**全部「高」可行性都落在 C 面；B 面 15 条里 14 条是「低」。** 原因不是数量，而是**判据的性质** —— C 面的判据是**集合成员资格**（这行有没有 `Obsolete`？这个整数在不在枚举表里？），A/B 面的判据是**语义与顺序**（该先做什么、谁在前、这个实参是什么东西）。

**按置信度**：高 31（70%）· 中 13（30%）。★ **中置信的 13 条里有 11 条在 B/C 面的「官方两源不一致」地带**（`audit-02-B` 的 Gusset 两源相反、`audit-03-C` 的 swFeatureNameID_e 数值查不到、`audit-04-C#44` 的 CHM 成员页缺失）⇒ **低置信不等于我们错，而是官方自己没给出可判的原文**。

---

## §3. ★ 能不能「一类一修」

### §3.1 直接回答

**不能一刀切，但可以切成「3 类可批量 + 1 类只能逐条」的两层结构。** 按可批量程度排序：

| 层 | 类 | 条数 | 能「静态全找」吗 | 能「共用修法全改」吗 | 综合 |
|---|---|---|---|---|---|
| **① 批量报 + 批量改** | **E 废弃成员** | 12 | ✅ **能** | ⚠ **半能** | **高** |
| **② 批量报 + 批量改** | **N 枚举取值域** | 6 | ✅ **能** | ⚠ **分两形态** | **高** |
| **③ 批量报 + 半自动筛候选** | **P 前置没做** | 12 | ❌ 不能 | ❌ 不能 | **低**（但可筛到 ~4 条） |
| ④ 只能逐条 | O 2 · Sq 2 · Us 2 · Ps 1 · Ns 1 · M 1 · T 2 · U 3 | 14 | 混 | 混 | **低** |

### §3.2 为什么 E 类「找」是高的

判据是**纯集合运算**，三步、可完全静态：

1. 从代码里抽出所有成员名 —— `get_com_member(x, "Name"` / `call_com_member(x, "Name"` / `x.Member` —— ★ **这是 AST 可做的，仓里已有同类脚本**。
2. 从官方抽出 Obsolete 名单 —— `C:\swapi\types\<接口>\<成员>.md` 的**首行** `Obsolete. Superseded by [[...]]`；第二源 `AI Solidworks\官方文档\SWhelp\sldworksapi\*.html`。
3. 集合运算 + 输出「调用点 → 旧成员 → 官方点名后继」三列表。

★ **`audit-04-assembly-C.md` 已经把这条走通了**：它核了 52 处成员，报 8 条，**全部命中这一类、零枚举发现**。也就是说本分片里**最大的一块（12 条）已经有人验证过静态判据可行**。

★ 但有一处**必须写进脚本输出、不能自动替换**：`GetErrorCode → GetErrorCode2`（#15 #20 #28 三处）。`sw_sheet_metal.py` 的注释逐字写着「`GetErrorCode2` 多一个 by-ref `isWarning` 参数 … 用无歧义的 `GetErrorCode` 兼容 pywin32 静态与动态代理」⇒ 这是**针对本仓已知事实 47（pywin32 迟到绑定不可调用指针接口）的有意保留**。批量替换会把它改成已知会失败的形式。

⇒ **E 类的正确批量形态是「批量报 + 逐条判是否该换」，不是「批量替换」。** 判据：`后继是否多出 by-ref/out 形参` —— 是 ⇒ 需要走 pywin32 适配决策，不是 ⇒ 可换。

### §3.3 为什么 E 类「改」只能算「中」

12 条里，**后继签名逐条不同**，不存在同一个 sed：

| 后继 | 与旧版差在哪 | 来源 |
|---|---|---|
| `GetErrorCode2` | 多一个 `out bool IsWarning` | `audit-02-sheetmetal-C.md` / `audit-03-weldment-C.md` |
| `AddComponent5` | 比 `AddComponent4` 多一个配置名形参 | `audit-04-assembly-C.md` #1 |
| `CreateMate` | 取代 `AddMate5`，**形状完全换掉** | `audit-04-assembly-C.md` #2 |
| `Select4` | 与 `Select2` 同型（Append, Mark） | `audit-04-assembly-C.md` #3 |
| `EditSuppress2` / `EditUnsuppress2` | 官方只写了后继名，**形状未核** | `audit-04-assembly-C.md` #5 #6 |
| `IMate2Entity::Reference2` | ★ **后继接口 `IMate2Entity` 在 `C:\swapi\types\` 下没有对应目录** | `audit-04-assembly-C.md`「查不到」段 |

⇒ 前 4 条可批量、后 5 条要逐条核、1 条连后继页都查不到。

### §3.4 为什么 N 类的真正修法是「生成」而不是「改」

6 条里有 4 条（#10 #11 #21，以及 #30 的白名单形态）是**同一个根因**：

> **我们自己手写了一张常量表/取值域，而没有让官方 enum 页生成它。**
> `swSurfaceExtendEndCond_e` 有 3 个成员我们只认 2 个 · `swRuledSurfaceType_e` 是 1..5 我们写成 0..4 · `swFlangeOffsetTypes_e` 官方没有 0 我们写 `SW_END_COND_BLIND = 0` · `swMateAlign_e` 官方有 6 个成员我们判「查不到」。

⇒ **一类一修的真正形态不是逐条补值，而是：让 `SW_*` 常量表从 `C:\swapi\enums\<枚举>.md` 生成。** 那样这一整类**从根上消失**，且 `audit-03-C#29` 那种「官方有枚举、我方注释说查不到」的判断错误也一并消失。

剩下 2 条判据不同源：#22（`ReliefType` / `FlangePos` 的 `valid selections` 只有 3 条、我们域里 5~6 个）要看**成员页的 Parameters** 而不是 enum 页；#30（`swFmMateProfileCenter` 不在 `CreateDefinition` 逐条列出的 35 项里）判据是**白名单差集**。

### §3.5 P 类（12 条）为什么「低」，以及唯一能用的那一招

**低的三个理由**（都可在本分片找到直接证据）：

1. **官方前置散在三种载体**：`## Remarks` 的散文句、官方例子的**排列**、以及 `Selections that Define Features.md` 这类专章。`audit-02-sheetmetal-B.md` 的 `InsertSheetMetalClosedCorner` 就是**类型页没有 `## Remarks`、靠官方例子才补上**（#17）⇒ 只读 `## Remarks` 的脚本会漏。
2. **官方自己会打架**：`audit-02-sheetmetal-B.md` 明确记 `ISMGussetFeatureData` 的**官方页说「先 `CreateDefinition` 再选面」、官方例子做的是「先选面再 `CreateDefinition`」**，两源相反 ⇒ 静态脚本**无法判谁对**，必须人来判。
3. **缺的那一步在代码里长得一模一样**：`create_draft` 收了 `face_ref` 从不使用（#19）、`create_one_bend` 收了 `sketch_name` 只回显（#6）、`FeatureBossThicken` 的 docstring 把前置写成「文件里要有曲面体」（#7）—— **AST 看不出这三条的差别，只知道「形参收了没用」**。

★ **但 P 类有一条可自动化的强规则**：

> **「函数形参在函数体内从未被使用 / 从未被赋给任何 FeatureData 属性」是纯 AST 可查的。**

用它能把 12 条筛成候选：`create_draft` 的 `face_ref`（#19）· `FeatureExtruRefSurface3` 的 `sketch_name`（#6）· `create_cut_list` 的 `sort_options`（#26）· `create_sub_weld_folder` 的 `folder`（#25）—— **4 条**。人工只需审 4 条而不是 12 条。⇒ **这是本分片性价比最高的一招：一条 AST 规则把 P 类的审阅量从 12 降到 4。**

### §3.6 其余 14 条为什么只能逐条

| 类 | 为什么批不了 |
|---|---|
| **O 参数顺序**（#1 #2） | 对调双方**类型完全相同**（`double`↔`double`、`object`↔`object`）⇒ 只有官方**形参名**能区分 ⇒ 要维护一张「形参名 → 我们变量名」的映射，且形参名不可靠时必误判。 |
| **Sq 调用序**（#5 #33） | 证据只在官方例子的**排列**里，且跨两个成员（`PreTrimSurface`↔`PostTrimSurface`、`GetInterferences`↔`Done`）⇒ 静态脚本没有「跨成员序」的稳定判据。 |
| **Us 实参语义**（#23 #24） | 官方只说「`Object`」，真语义在 `- **Bodies**: Array of [[Body2]] objects`；改法三选（删参 / 换参 / 补 `GetBodies2`），**无法自动决定**。★ 但这两条与 #25 #26 **是同一处代码的两面**（A 面报「实参错」、B 面报「前置没做」）⇒ **改一处解两条**。 |
| **U 量纲**（#12 #13 #14） | 「找」是规整的（3/3 同形态，一条规则全找），但**改法要连带改 `validate()` 的取值域**（0..360 度 ⇒ 0.261799..1.5708 弧度），且 **`ProfileAngleDim` 官方页没给单位** ⇒ 同形态代码里混着一个不能判的，不能一刀切。 |
| **T 类型/形状**（#3 #4） | 「找」高（反射 VT + AST 包装）；「改」要逐条（包 `VARIANT` 还是换包装）。 |
| **M 成员缺席**（#32） | 找法高（三源集合运算），但**改法依赖 #38 的后继 `CreateMate` 的签名** ⇒ 与 E 类同源，**应合并处理**。 |
| **Ps 前置语义**（#18） | 改法是「分叉装配体 / 零件两种上下文」，不是补一步。 |
| **Ns 完整性断言**（#31） | 分歧在注释里，且「这 6 条算不算焊件相关」是口径问题，不是对错问题。 |

### §3.7 ★ 三条横向发现（比单条分类更重要）

**① 一整类「无源常量」横跨全分片，任何单片都发现不了。**
`audit-02-sheetmetal-C.md` 与 `audit-03-weldment-C.md` **各自独立**记下同一件事：`swFeatureNameID_e.md` 的 `enum_member_count: 130` 成员表里，「Value」列装的是**描述**（如 `| swFmBaseFlange | Base flange |`）**而不是数值**。
⇒ 我们代码里的 `SW_FM_BASE_FLANGE=34` / `SW_FM_DRAFT=3` / `SW_FM_ONE_BEND=33` / `SW_FM_SKETCH_BEND=35` / `SW_FM_EDGE_FLANGE=37` / `SW_FM_SWEPT_FLANGE=117` / `SW_FM_SM_GUSSET=118` / `SW_FM_MATE_PROFILE_CENTER=101` / `SW_FM_PROFILE_FEATURE=65` / `SW_FM_WELD_MEMBER_FEAT=72` —— **十个数值全部无官方依据可核**。
⇒ 这不是「某一条分歧」，是一条**一次普查可解**的系统性问题（`D:\AI\SW\_raw\**\enum_values_sldworks.txt` 是已知第三源）。**它应当按「普查」推进，不该按「条」修。**

**② 同一个根因被三个核对面各报一次 —— 说明核对面是「视角」不是「分类」。**
`GetErrorCode` 的 Obsolete 在 `audit-02-sheetmetal-A`（附录）· `audit-02-sheetmetal-C` · `audit-03-weldment-C` **被报了三次**；`InsertSubWeldFolder2` 的实参错在 `audit-03-A`（#24）与前置错在 `audit-03-B`（#25）**各报一次**；`InsertWeldmentCutList2` 同理（#23 / #26）。
⇒ **44 条 ≠ 44 个问题。** 按「代码位置」去重后，A 面+B 面+C 面的重叠处（`sw_weldment.py` 的两个 `Insert*` 调用、`GetErrorCode` 的三处）**至少可合并成 2 个修复单元**。⇒ **修的分母比 44 小。**

**③ 「改了会坏」的坑已经写在代码注释里，分类时不能只按「官方说 Obsolete」判。**
`#20` 的注释逐字：「`GetErrorCode2` 多一个 by-ref `isWarning` 参数；此处只需拒绝硬错误，**使用无歧义的 `GetErrorCode` 可兼容 pywin32 静态与动态代理**」。
⇒ 这与本仓已知事实 47（`IAccessSelections` / `IAccessSelections2` 在 pywin32 下不可调用）**同族**。⇒ **任何「废弃成员批量替换」脚本，都必须先跑一遍「后继是否多出 by-ref 形参」的过滤**，否则会把「明知故犯的防御」换成「已知会失败的调用」。

### §3.8 结论（可直接据以排期）

| 批次 | 内容 | 工具形态 | 覆盖条数 | 人工投入 |
|---|---|---|---|---|
| **B1** | **废弃成员普查** | 静态脚本：AST 抽成员名 × 双源 Obsolete 名单（`types/*.md` 首行 + CHM） | 12 | 逐条判「后继是否多 by-ref」+ 逐条核后继签名 |
| **B2** | **枚举常量表从官方 enum 页生成** | 生成器：读 `C:\swapi\enums\*.md` 的 `enum_member_count` + 成员表 | 6（根治） | 复核生成结果 + 处理 #22 #30 两种异源判据 |
| **B3** | **`SW_FM_*` 数值普查** | 反射 `enum_values_sldworks.txt` × 代码常量 | 0 条分歧，但覆盖 10 个无源常量 | 复核 |
| **B4** | **类型/形状/成员缺席静态查** | 反射 VT 类型 × AST 包装；成员名 × 成员表 | 3 | 逐条改 |
| **B5** | **死形参 AST 规则**（P 类的候选筛子） | 纯 AST：形参在函数体内未被使用 / 未赋给 FeatureData | 0（筛子） | **把 P 类的人工审阅量从 12 降到 4** |
| **B6** | **剩余逐条** | 人工 | **11**（O 2 · Sq 2 · Us 2 · U 3 · Ps 1 · Ns 1） | 全人工 |

⇒ **B1+B2+B4 覆盖 21 条（48%），且 3 个批次全是静态脚本；B6 剩 11 条必须逐条。B5 是把人工量砍掉三分之二的杠杆。**

★ **一句话回答业主的问题**：**「能不能一类一修」—— 能，但只有一类半。** 废弃成员（12 条）**能批**，因为官方逐字点名了后继，判据是集合运算；枚举域（6 条）**能批**，但正确的修法是「让常量表从官方生成」而不是逐条补值；前置/调用序/顺序这三类（16 条，占 36%）**只能逐条**，因为官方证据散在三种载体里、且官方自己会两源打架 —— 唯一能做的自动化是**用一条 AST 规则把 16 条筛成 4 条真候选**。