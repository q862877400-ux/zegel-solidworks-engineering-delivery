# PATTERNS —— audit-vs-official 三路分歧的**唯一总表**

> **本文件是 `patterns-shard-1.md` / `-2.md` / `-3.md` 三份分片的合成总表**，按用户口径给出：全量表 · 复核结果 · 可批量性结论 · 每类建议动作。
> **生成方式**：`output/gen_patterns_table.py` 机械解析三份 shard 的分歧表并做统一类映射；脚本内置 `assert len(rows) == 104`，**「一条不丢」是可复跑的断言，不是承诺**。
> **纪律**：★ 只读；★ 未运行 SolidWorks；★ 未运行 pytest；★ 未改动仓内任何其它文件。分类与批量的判断依据一律回 `audit-*.md` 原文，引用给到可 grep 的片段。

## §0. 三路的类名统一

三份分片各自造了一套类名，彼此不兼容（这是分片的必然结果，不是分歧）。本总表把 **23 个原始类名收敛成 14 个统一类**，映射规则如下（★ 收敛只做**并集**与**按因果链归并**，不新造事实）：

| 统一类 | 名称 | 来自哪些原始类 | 条数 |
|---|---|---|---|
| **D1** | 废弃成员（代际落后） | S1 `E` · S2 `O` · S3 `C4` | **34** |
| **D2** | 取值不在官方合法域（枚举 / 区间） | S1 `N`（除 S1-11）· S2 `E`（除 S2-32）· S3 `C5`+`C11` | **10** |
| **D3** | 前置没做（官方前置缺失） | S1 `P` · S2 `P` · S3 `C1` | **31** |
| **D4** | 文档性分歧（注释声称官方没给） | S1 `Ns` · S2 `D` · S3 `C2` | **6** |
| **D5** | 实参量纲不符（mm↔米 · 度↔弧度） | S1 `U` | **3** |
| **D6** | 参数顺序不符 | S1 `O` | **2** |
| **D7** | 参数个数不符（含 by-ref 出参漏补） | S3 `C3` | **1** |
| **D8** | 调用序 / 事务层级错 | S1 `Sq` · S3 `C6` | **3** |
| **D9** | 类型 / 形状不符 | S1 `T` · S2 `T` | **3** |
| **D10** | 实参语义喂错（形参要数组 / 对象） | S1 `Us` | **2** |
| **D11** | 前置门槛方向错（过严 / 语义当硬约束） | S1 `Ps` · S3 `C8` | **2** |
| **D12** | 取错了成员（语义错位 / 成员名错 / 成员缺席） | S1 `M` · S2 `W` · S3 `C7` | **3** |
| **D13** | 对官方原文的转述失真 | S3 `C9` | **1** |
| **D14** | 官方源冲突（两源打架，不可判定） | S3 `C10` + ★**复核新增 S1-11 · S2-32** | **3** |
| | **合计** | | **104** |

★ **两处被复核「改判」的**（见 §2）：`S1-11` 从 D2 → **D14**，`S2-32` 从 D2 → **D14**。
⇒ ★ **D14 是本次复核唯一的净产出类**：两路的判据都落在 D2（"取值不在合法域"），但原文都写明**官方两源本身矛盾**，「照表换值」这个修法会把另一条调用路径改坏。

### §0.1 域 / 核对面覆盖

| 域 | A 面 | B 面 | C 面 | 小计 |
|---|---|---|---|---|
| 01-surface | 4 | 4 | 3 | 11 |
| 02-sheetmetal | 4 | 4 | 3 | 11 |
| 03-weldment | 2 | 3 | 4 | 9 |
| 04-assembly | 1 | 4 | 8 | 13 |
| 05-drawing | 1 | 7 | 4 | 12 |
| 06-features | 1 | 6 | 9 | 16 |
| 07-sketch | 0 | 0 | 5 | 5 |
| 08-mold-costing | 1 | 3 | 2 | 6 |
| 09-simulation | 0 | 5 | 0 | 5 |
| 10-misc | 0 | 6 | 10 | 16 |
| **合计** | **11** | **40** | **53** | **104** |

★ 横向规律（三路各自独立看到、此处合并后更清楚）：**A 面（签名）11 条 · B 面（前置/mark）40 条 · C 面（废弃/枚举）53 条。**
⇒ **分歧重心不在「签名写错」，而在「调用前的状态不对」+「调的是废弃入口」**，两者合计 **93 / 104 = 89%**。

### §0.2 ★ 范围限制（必读）

1. ★★ **三份 shard 冻结之后，又有 3 份 audit 出现了**：`audit-07-sketch-A.md`、`audit-07-sketch-B.md`、`audit-09-simulation-A.md`。
   shard-2 §0 明写「`audit-07-sketch-A/B` 在本仓不存在」，shard-3 §0 明写「`audit-09-A/C` 仍不存在」—— **它们是并发写的，比分片晚到**。
   ⇒ **104 条 = 三路并集的全量**，但**不是当前 audit 集合的全量**。这 3 份的 13 条新分歧单列在 **§4 附录**。
2. ★ 域 `08-mold-costing` 三份 audit **只核了 `sw_mold.py` 与 `sw_measure.py`**，`sw_costing.py` 与 `sw_api_sldcostingapi.py` **A/B/C 三面都没核过** —— Costing（三大护城河之一）在本核对里是**空白**（shard-3 §5.1 已记，本表沿用）。
3. ★ 置信度一栏**沿用各 audit 原文的自评**，本表未重新评级；低置信**不等于我们错**，多因官方自己没给出可判的原文。
## §1. 全量分歧表（三路并集，**104 条**，一条不丢）

编号：`S1-xx` = shard-1 第 xx 行 · `S2-xx` = shard-2 的 `S2-xx` 行 · `S3-xx` = shard-3 第 xx 行。
「找」= 一个静态脚本能不能把这一类找全；「改」= 能不能用**同一形态共用的一个修法**改完。
★「严格可批量」= 找 **高** 且 改 **高** —— 这才是用户口径的「一类一修」。

| # | 分片行号 | 文件 | 面 | 统一类 | 我们的锚点（可 grep） | 官方锚点（可 grep） | 置信 | 找 | 改 | 严格可批量 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `S1-01` | ``audit-01-surface-A.md`` | A | **D6** 参数顺序不符 | `sw_surface.py` | `CreateConicalSurface.md` | 高 | 低 | 低 | 否 |
| 2 | `S1-02` | ``audit-01-surface-A.md`` | A | **D6** 参数顺序不符 | `sw_surface.py` | `CreateBsplineSurface.md` | 高 | 低 | 低 | 否 |
| 3 | `S1-03` | ``audit-01-surface-A.md`` | A | **D9** 类型 / 形状不符 | `sw_surface.py` | `CreateSheetFromSurface.md` | 中 | 高 | 低 | 否 |
| 4 | `S1-04` | ``audit-01-surface-A.md`` | A | **D9** 类型 / 形状不符 | `sw_surface_ref_ops.py` | `InsertLoftRefSurface2.md` | 中 | 高 | 低 | 否 |
| 5 | `S1-05` | ``audit-01-surface-B.md`` | B | **D8** 调用序 / 事务层级错 | `sw_surface_features.py` | `PostTrimSurface.md` | 高 | 低 | 低 | 否 |
| 6 | `S1-06` | ``audit-01-surface-B.md`` | B | **D3** 前置没做（官方前置缺失） | `sw_surface_features.py` | `FeatureExtruRefSurface3.md` | 高 | 中 | 低 | 否 |
| 7 | `S1-07` | ``audit-01-surface-B.md`` | B | **D3** 前置没做（官方前置缺失） | `sw_surface_features.py` | `FeatureBossThicken.md` | 高 | 中 | 低 | 否 |
| 8 | `S1-08` | ``audit-01-surface-B.md`` | B | **D3** 前置没做（官方前置缺失） | `sw_surface_features.py` | `InsertExtendSurface.md` | 中 | 中 | 低 | 否 |
| 9 | `S1-09` | ``audit-01-surface-C.md`` | C | **D1** 废弃成员（代际落后） | `sw_surface.py` | `CreatePlanarSurface.md` | 高 | 高 | 低 | 否 |
| 10 | `S1-10` | ``audit-01-surface-C.md`` | C | **D2** 取值不在官方合法域（枚举 / 区间） | `sw_surface_features.py` | `InsertExtendSurface.md` | 0` / `UpToPoint \ | 高 | 高 | ★ 是 |
| 11 | `S1-11` | ``audit-01-surface-C.md`` | C | **D14** 官方源冲突（两源打架，不可判定） | `sw_surface_edit_ops.py` | `swRuledSurfaceType_e.md` | 1` … `swRuledSurfaceType_Sweep \ | 高 | 低 | 否 |
| 12 | `S1-12` | ``audit-02-sheetmetal-A.md`` | A | **D5** 实参量纲不符（mm↔米 · 度↔弧度） | `sw_sheet_metal.py` | `ISketchedBendFeatureData/BendAngle.md` | 高 | 高 | 中 | 否 |
| 13 | `S1-13` | ``audit-02-sheetmetal-A.md`` | A | **D5** 实参量纲不符（mm↔米 · 度↔弧度） | `sw_sheet_metal.py` | `IEdgeFlangeFeatureData/BendAngle.md` | 高 | 高 | 中 | 否 |
| 14 | `S1-14` | ``audit-02-sheetmetal-A.md`` | A | **D5** 实参量纲不符（mm↔米 · 度↔弧度） | `sw_sheet_metal.py` | `IDraftFeatureData2/Angle.md` | 高 | 高 | 中 | 否 |
| 15 | `S1-15` | ``audit-02-sheetmetal-A.md`（附录）` | C | **D1** 废弃成员（代际落后） | `sw_sheet_metal.py` | `IFeature/GetErrorCode.md` | 高 | 高 | 低 | 否 |
| 16 | `S1-16` | ``audit-02-sheetmetal-B.md`` | B | **D3** 前置没做（官方前置缺失） | `sw_sheet_metal.py` | `IEdgeFlangeFeatureData/AddEdges.md` | 高 | 中 | 低 | 否 |
| 17 | `S1-17` | ``audit-02-sheetmetal-B.md`` | B | **D3** 前置没做（官方前置缺失） | `sw_sheet_metal_weld_entry.py` | `Create_and_Modify_Closed_Corner_Feature_Example_VBNET.md` | 高 | 中 | 低 | 否 |
| 18 | `S1-18` | ``audit-02-sheetmetal-B.md`` | B | **D11** 前置门槛方向错（过严 / 语义当硬约束） | `sw_sheet_metal_weld_entry.py` | `InsertMidSurface.md` | 中 | 低 | 低 | 否 |
| 19 | `S1-19` | ``audit-02-sheetmetal-B.md`` | B | **D3** 前置没做（官方前置缺失） | `sw_sheet_metal.py` | `IDraftFeatureData2/FacesToDraft.md` | 中 | 中 | 低 | 否 |
| 20 | `S1-20` | ``audit-02-sheetmetal-C.md`` | C | **D1** 废弃成员（代际落后） | `sw_sheet_metal.py` | `IFeature/GetErrorCode.md` | 高 | 高 | 低 | 否 |
| 21 | `S1-21` | ``audit-02-sheetmetal-C.md`` | C | **D2** 取值不在官方合法域（枚举 / 区间） | `sw_sheet_metal.py` | `IBaseFlangeFeatureData/D1EndConditionType.md` | 1` … `swFlangeOffsetUptoEdgeAndMerge \ | 高 | 高 | ★ 是 |
| 22 | `S1-22` | ``audit-02-sheetmetal-C.md`` | C | **D2** 取值不在官方合法域（枚举 / 区间） | `sw_sheet_metal_weld_entry.py` | `InsertSheetMetalMiterFlange.md` | 中 | 高 | 中 | 否 |
| 23 | `S1-23` | ``audit-03-weldment-A.md`` | A | **D10** 实参语义喂错（形参要数组 / 对象） | `sw_weldment.py` | `InsertWeldmentCutList2.md` | 高 | 低 | 低 | 否 |
| 24 | `S1-24` | ``audit-03-weldment-A.md`` | A | **D10** 实参语义喂错（形参要数组 / 对象） | `sw_weldment.py` | `InsertSubWeldFolder2.md` | 高 | 低 | 低 | 否 |
| 25 | `S1-25` | ``audit-03-weldment-B.md`` | B | **D3** 前置没做（官方前置缺失） | `sw_weldment.py` | `InsertSubWeldFolder2.md` | 高 | 中 | 低 | 否 |
| 26 | `S1-26` | ``audit-03-weldment-B.md`` | B | **D3** 前置没做（官方前置缺失） | `sw_weldment.py` | `Insert_Weldment_Cut_List2_Example_VB.htm` | 高 | 中 | 低 | 否 |
| 27 | `S1-27` | ``audit-03-weldment-B.md`` | B | **D3** 前置没做（官方前置缺失） | `sw_weldment.py` | `IBodyFolder/UpdateCutList.md` | 中 | 中 | 低 | 否 |
| 28 | `S1-28` | ``audit-03-weldment-C.md`` | C | **D1** 废弃成员（代际落后） | `sw_weldment.py` | `IFeature/GetErrorCode.md` | 高 | 高 | 低 | 否 |
| 29 | `S1-29` | ``audit-03-weldment-C.md`` | C | **D2** 取值不在官方合法域（枚举 / 区间） | `sw_weldment.py` | `IProfileCenterMateFeatureData/MateAlignment.md` | 0` · `swMateAlignANTI_ALIGNED \ | 高 | 高 | ★ 是 |
| 30 | `S1-30` | ``audit-03-weldment-C.md`` | C | **D2** 取值不在官方合法域（枚举 / 区间） | `sw_weldment.py` | `IFeatureManager/CreateDefinition.md` | swFmMateProfileCenter \ | 高 | 中 | 否 |
| 31 | `S1-31` | ``audit-03-weldment-C.md`` | C | **D4** 文档性分歧（注释声称官方没给） | `sw_weldment.py` | `swFeatureNameID_e.md` | 中 | 中 | 高 | 否 |
| 32 | `S1-32` | ``audit-04-assembly-A.md`` | A | **D12** 取错了成员（语义错位 / 成员名错 / 成员缺席） | `sw_assembly.py` | `IMate2` | 高 | 中 | 低 | 否 |
| 33 | `S1-33` | ``audit-04-assembly-B.md`` | B | **D8** 调用序 / 事务层级错 | `sw_assembly.py` | `IInterferenceDetectionMgr/Done.md` | 高 | 低 | 低 | 否 |
| 34 | `S1-34` | ``audit-04-assembly-B.md`` | B | **D3** 前置没做（官方前置缺失） | `sw_assembly.py` | `Run_Interference_Detection_Example_VB.md` | 中 | 中 | 低 | 否 |
| 35 | `S1-35` | ``audit-04-assembly-B.md`` | B | **D3** 前置没做（官方前置缺失） | `sw_assembly.py` | `IAssemblyDoc/AddComponent5.md` | 中 | 中 | 低 | 否 |
| 36 | `S1-36` | ``audit-04-assembly-B.md`` | B | **D3** 前置没做（官方前置缺失） | `sw_assembly.py` | `IAssemblyDoc/AddMate5.md` | 中 | 中 | 低 | 否 |
| 37 | `S1-37` | ``audit-04-assembly-C.md`` | C | **D1** 废弃成员（代际落后） | `sw_assembly.py` | `IAssemblyDoc/AddComponent4.md` | 高 | 高 | 低 | 否 |
| 38 | `S1-38` | ``audit-04-assembly-C.md`` | C | **D1** 废弃成员（代际落后） | `sw_assembly.py` | `IAssemblyDoc/AddMate5.md` | 高 | 高 | 低 | 否 |
| 39 | `S1-39` | ``audit-04-assembly-C.md`` | C | **D1** 废弃成员（代际落后） | `sw_assembly.py` | `IEntity/Select2.md` | 高 | 高 | 低 | 否 |
| 40 | `S1-40` | ``audit-04-assembly-C.md`` | C | **D1** 废弃成员（代际落后） | `sw_assembly.py` | `IComponent2/SetTransformAndSolve2.md` | 高 | 高 | 低 | 否 |
| 41 | `S1-41` | ``audit-04-assembly-C.md`` | C | **D1** 废弃成员（代际落后） | `sw_assembly.py` | `IModelDoc2/EditSuppress.md` | 高 | 高 | 低 | 否 |
| 42 | `S1-42` | ``audit-04-assembly-C.md`` | C | **D1** 废弃成员（代际落后） | `sw_assembly.py` | `IModelDoc2/EditUnsuppress.md` | 高 | 高 | 低 | 否 |
| 43 | `S1-43` | ``audit-04-assembly-C.md`` | C | **D1** 废弃成员（代际落后） | `sw_assembly.py` | `IMateEntity2/ReferenceType.md` | 高 | 高 | 低 | 否 |
| 44 | `S1-44` | ``audit-04-assembly-C.md`` | C | **D1** 废弃成员（代际落后） | `sw_assembly.py` | `ISldWorks/ActivateDoc2.md` | 中 | 高 | 高 | ★ 是 |
| 45 | `S2-01` | `audit-05-drawing-A.md` | A | **D12** 取错了成员（语义错位 / 成员名错 / 成员缺席） | `scripts/sw_drawing_expose.py` | `ISelectionMgr\GetSelectedObjectType3.md` | 高 | 中 | 低 | 否 |
| 46 | `S2-02` | `audit-05-drawing-B.md` | B | **D3** 前置没做（官方前置缺失） | `ret = C.get_com_member(sheet, "SetTemplateName", str(fo...` | `ISheet\SetTemplateName.md` | 高 | 中 | 低 | 否 |
| 47 | `S2-03` | `audit-05-drawing-B.md` | B | **D4** 文档性分歧（注释声称官方没给） | `★ 官方 Remarks 逐字：调完要 ForceRebuild3 才刷新第一角/第三角投影；★ 这里顺带做掉。` | `ISheet\SetTemplateName.md` | 高 | 中 | 高 | 否 |
| 48 | `S2-04` | `audit-05-drawing-B.md` | B | **D3** 前置没做（官方前置缺失） | `pre = _selection_count(drawing_model)` | `IDrawingDoc\CreateSectionViewAt5.md` | 高 | 中 | 低 | 否 |
| 49 | `S2-05` | `audit-05-drawing-B.md` | B | **D3** 前置没做（官方前置缺失） | `res = D.add_detail_view(drawing_model, _mm(x_mm), _mm(y...` | `examples\Create_Detail_Circle_and_Detail_View_Example_V...` | 高 | 中 | 低 | 否 |
| 50 | `S2-06` | `audit-05-drawing-B.md` | B | **D3** 前置没做（官方前置缺失） | `sel = _selection_count(model)` | `IDrawingDoc\CreateAuxiliaryViewAt2.md` | 中 | 中 | 低 | 否 |
| 51 | `S2-07` | `audit-05-drawing-B.md` | B | **D3** 前置没做（官方前置缺失） | `sel = _selection_count(model)` | `IDrawingDoc\AutoBalloon5.md` | 中 | 中 | 低 | 否 |
| 52 | `S2-08` | `audit-05-drawing-B.md` | B | **D3** 前置没做（官方前置缺失） | `res = D.auto_insert_center_marks(drawing_model, require...` | `IView\AutoInsertCenterMarks2.md` | 中 | 中 | 低 | 否 |
| 53 | `S2-09` | `audit-05-drawing-C.md` | C | **D1** 废弃成员（代际落后） | `scripts/sw_drawing_expose.py` | `IView\Name.md` | 高 | 高 | 高 | ★ 是 |
| 54 | `S2-10` | `audit-05-drawing-C.md` | C | **D1** 废弃成员（代际落后） | `scripts/sw_drawing_create_missing.py` | `IView\Name.md` | 高 | 高 | 高 | ★ 是 |
| 55 | `S2-11` | `audit-05-drawing-C.md` | C | **D2** 取值不在官方合法域（枚举 / 区间） | `scripts/sw_drawing_expose.py` | `enums\swRevisionTableSymbolShape_e.md` | 1` / `_SquareSymbol \ | 高 | 高 | ★ 是 |
| 56 | `S2-12` | `audit-05-drawing-C.md` | C | **D2** 取值不在官方合法域（枚举 / 区间） | `scripts/sw_drawing_expose.py` | `IDrawingDoc\CreateDetailViewAt4.md` | 高 | 高 | 高 | ★ 是 |
| 57 | `S2-13` | `audit-06-features-A.md` | A | **D9** 类型 / 形状不符 | `scripts/sw_part.py` | `ISketchManager\CreateSketchSlot.md` | 高 | 高 | 低 | 否 |
| 58 | `S2-14` | `audit-06-features-B.md` | B | **D3** 前置没做（官方前置缺失） | `sw_part.py` | `IFeatureManager\FeatureRevolve2.md` | 高 | 中 | 低 | 否 |
| 59 | `S2-15` | `audit-06-features-B.md` | B | **D3** 前置没做（官方前置缺失） | `sw_part.py` | `IFeatureManager\FeatureLinearPattern3.md` | 高 | 中 | 低 | 否 |
| 60 | `S2-16` | `audit-06-features-B.md` | B | **D3** 前置没做（官方前置缺失） | `sw_part.py` | `FeatureLinearPattern3.md` | 高 | 中 | 低 | 否 |
| 61 | `S2-17` | `audit-06-features-B.md` | B | **D3** 前置没做（官方前置缺失） | `sw_part.py` | `ISketch\AutoDimension2.md` | 高 | 中 | 低 | 否 |
| 62 | `S2-18` | `audit-06-features-B.md` | B | **D3** 前置没做（官方前置缺失） | `sw_part.py` | `IFeatureManager\FeatureFillet.md` | 中 | 中 | 低 | 否 |
| 63 | `S2-19` | `audit-06-features-B.md` | B | **D3** 前置没做（官方前置缺失） | `sw_part.py` | `IModelDoc2\InsertFeatureShell.md` | 中 | 中 | 低 | 否 |
| 64 | `S2-20` | `audit-06-features-C.md` | C | **D1** 废弃成员（代际落后） | `sw_part.py` | `IFeatureManager\FeatureFillet.md` | 高 | 高 | 低 | 否 |
| 65 | `S2-21` | `audit-06-features-C.md` | C | **D1** 废弃成员（代际落后） | `sw_part.py` | `FeatureLinearPattern3.md` | 高 | 高 | 低 | 否 |
| 66 | `S2-22` | `audit-06-features-C.md` | C | **D1** 废弃成员（代际落后） | `sw_part.py` | `FeatureCircularPattern4.md` | 高 | 高 | 低 | 否 |
| 67 | `S2-23` | `audit-06-features-C.md` | C | **D1** 废弃成员（代际落后） | `sw_part.py` | `ISketchManager\CreateSpline2.md` | 高 | 高 | 低 | 否 |
| 68 | `S2-24` | `audit-06-features-C.md` | C | **D1** 废弃成员（代际落后） | `sw_part.py` | `ISketch\AutoDimension2.md` | 高 | 高 | 低 | 否 |
| 69 | `S2-25` | `audit-06-features-C.md` | C | **D1** 废弃成员（代际落后） | `sw_part.py` | `IModelDoc2\GraphicsRedraw2.md` | 高 | 高 | 低 | 否 |
| 70 | `S2-26` | `audit-06-features-C.md` | C | **D1** 废弃成员（代际落后） | `sw_part.py` | `IModelDoc2\GetActiveSketch2.md` | 高 | 高 | 高 | ★ 是 |
| 71 | `S2-27` | `audit-06-features-C.md` | C | **D1** 废弃成员（代际落后） | `sw_part.py` | `ISketchSegment\Select3.md` | 高 | 高 | 高 | ★ 是 |
| 72 | `S2-28` | `audit-06-features-C.md` | C | **D1** 废弃成员（代际落后） | `sw_part.py` | `ISketchSegment\Select2.md` | 中 | 高 | 高 | ★ 是 |
| 73 | `S2-29` | `audit-07-sketch-C.md` | C | **D1** 废弃成员（代际落后） | `scripts/sw_sketch_modify_ops.py` | `IModelDoc2\GetActiveSketch2.md` | 高 | 高 | 低 | 否 |
| 74 | `S2-30` | `audit-07-sketch-C.md` | C | **D1** 废弃成员（代际落后） | `scripts/sw_sketch_edit.py` | `同上（我们是**先调 Obsolete、再回退后继**）` | 高 | 高 | 低 | 否 |
| 75 | `S2-31` | `audit-07-sketch-C.md` | C | **D4** 文档性分歧（注释声称官方没给） | `scripts/sw_sketch_modify_ops.py` | `IModelDoc2\SketchModifyFlip.md` | 高 | 中 | 高 | 否 |
| 76 | `S2-32` | `audit-07-sketch-C.md` | C | **D14** 官方源冲突（两源打架，不可判定） | `scripts/sw_sketch_edit.py` | `enums\swSketchChamferType_e.md` | swSketchChamfer_DistanceAngle \ | 高 | 低 | 否 |
| 77 | `S2-33` | `audit-07-sketch-C.md` | C | **D4** 文档性分歧（注释声称官方没给） | `scripts/sw_sketch.py` | `enums\swCrossHatchFilter_e.md` | swCrossHatchAndExplodeOnly \ | 中 | 高 | 否 |
| 78 | `S3-01` | `audit-08-mold-costing-A.md` | A | **D7** 参数个数不符（含 by-ref 出参漏补） | `scripts/sw_measure.py` | `C:\swapi\types\IMeasure\Calculate.md` | 高 | 高 | 高 | ★ 是 |
| 79 | `S3-02` | `audit-08-mold-costing-B.md` | B | **D3** 前置没做（官方前置缺失） | `scripts/sw_mold.py` | `IFeatureManager\InsertMoldPartingLine.md` | 高 | 中 | 低 | 否 |
| 80 | `S3-03` | `audit-08-mold-costing-B.md` | B | **D3** 前置没做（官方前置缺失） | `"InsertMoldPartingSurface 返回 None —— 常见原因：未先建分型线，或未选面"` | `InsertMoldPartingSurface.md` | 中 | 中 | 低 | 否 |
| 81 | `S3-04` | `audit-08-mold-costing-B.md` | B | **D4** 文档性分歧（注释声称官方没给） | `sw_mold.py` | `InsertMoldCoreCavitySolids.md` | 高 | 中 | 高 | 否 |
| 82 | `S3-05` | `audit-08-mold-costing-C.md` | C | **D1** 废弃成员（代际落后） | `return get_com_member(fm, "MoldUndercutDetect",` | `MoldUndercutDetect.md` | 高 | 高 | 低 | 否 |
| 83 | `S3-06` | `audit-08-mold-costing-C.md` | C | **D2** 取值不在官方合法域（枚举 / 区间） | `int(option),            # 6 Int32 未查证` | `InsertMoldPartingSurface.md` | 1 \ | 高 | 高 | ★ 是 |
| 84 | `S3-07` | `audit-09-simulation-B.md` | B | **D3** 前置没做（官方前置缺失） | `scripts/sw_topology.py` | `Create_Topology_Study_Example_VBA.txt` | 高 | 中 | 低 | 否 |
| 85 | `S3-08` | `audit-09-simulation-B.md` | B | **D3** 前置没做（官方前置缺失） | `create_symmetry_control` | `CWTopoSymmetryControlObj.SelectSymmetryType 0` | 高 | 中 | 低 | 否 |
| 86 | `S3-09` | `audit-09-simulation-B.md` | B | **D3** 前置没做（官方前置缺失） | `create_demold_control` | `CWTopoDemoldControlObj.SelectDemoldDirection 0` | 高 | 中 | 低 | 否 |
| 87 | `S3-10` | `audit-09-simulation-B.md` | B | **D8** 调用序 / 事务层级错 | `create_*` | `CWTopologyStudyManagerObj.BeginEdit` | 高 | 低 | 低 | 否 |
| 88 | `S3-11` | `audit-09-simulation-B.md` | B | **D12** 取错了成员（语义错位 / 成员名错 / 成员缺席） | `sw_simulation.py` | `Analyze_Part_Example_VB.htm` | 中 | 中 | 低 | 否 |
| 89 | `S3-12` | `audit-10-misc-B.md` | B | **D4** 文档性分歧（注释声称官方没给） | `scripts/sw_ref_geometry.py` | `IFeatureManager\InsertRefPlane.md` | 高 | 中 | 高 | 否 |
| 90 | `S3-13` | `audit-10-misc-B.md` | B | **D3** 前置没做（官方前置缺失） | `scripts/sw_loft.py` | `InsertProtrusionBlend2.md` | 高 | 中 | 低 | 否 |
| 91 | `S3-14` | `audit-10-misc-B.md` | B | **D11** 前置门槛方向错（过严 / 语义当硬约束） | `create_loft_report` | `InsertProtrusionBlend2.md` | 高 | 低 | 低 | 否 |
| 92 | `S3-15` | `audit-10-misc-B.md` | B | **D3** 前置没做（官方前置缺失） | `sw_review.py` | `IModelDoc2\ShowNamedView2.md` | 中 | 中 | 低 | 否 |
| 93 | `S3-16` | `audit-10-misc-B.md` | B | **D13** 对官方原文的转述失真 | `sw_helix.py` | `C:\swapi\examples\Create_Spiral_Example_VB.md` | 中 | 低 | 低 | 否 |
| 94 | `S3-17` | `audit-10-misc-B.md` | B | **D14** 官方源冲突（两源打架，不可判定） | `sw_export.py` | `IPartDoc\ExportToDWG2.md` | 中 | 高 | 低 | 否 |
| 95 | `S3-18` | `audit-10-misc-C.md` | C | **D1** 废弃成员（代际落后） | `sw_export.py` | `IModelDocExtension\SaveAs.md` | 高 | 高 | 低 | 否 |
| 96 | `S3-19` | `audit-10-misc-C.md` | C | **D1** 废弃成员（代际落后） | `sw_export.py` | `IModelDoc2\SetUserPreferenceIntegerValue.md` | 高 | 高 | 低 | 否 |
| 97 | `S3-20` | `audit-10-misc-C.md` | C | **D1** 废弃成员（代际落后） | `sw_export.py` | `IModelDocExtension\GetMassProperties.md` | 高 | 高 | 低 | 否 |
| 98 | `S3-21` | `audit-10-misc-C.md` | C | **D1** 废弃成员（代际落后） | `sw_export.py` | `ISldWorks\ActivateDoc2.md` | 高 | 高 | 高 | ★ 是 |
| 99 | `S3-22` | `audit-10-misc-C.md` | C | **D2** 取值不在官方合法域（枚举 / 区间） | `sw_export.py` | `swSTLQuality_e.md` | 1 \ | 高 | 高 | ★ 是 |
| 100 | `S3-23` | `audit-10-misc-C.md` | C | **D1** 废弃成员（代际落后） | `sw_review.py` | `IModelDoc2\GraphicsRedraw2.md` | 高 | 高 | 低 | 否 |
| 101 | `S3-24` | `audit-10-misc-C.md` | C | **D1** 废弃成员（代际落后） | `sw_review.py` | `ISldWorks\ActivateDoc2.md` | 高 | 高 | 高 | ★ 是 |
| 102 | `S3-25` | `audit-10-misc-C.md` | C | **D1** 废弃成员（代际落后） | `sw_document_data.py` | `IDimension\GetSystemValue2.md` | 高 | 高 | 低 | 否 |
| 103 | `S3-26` | `audit-10-misc-C.md` | C | **D1** 废弃成员（代际落后） | `sw_document_data.py` | `IDimension\SystemValue.md` | 高 | 高 | 低 | 否 |
| 104 | `S3-27` | `audit-10-misc-C.md` | C | **D2** 取值不在官方合法域（枚举 / 区间） | `sw_wrap.py` | `InsertWrapFeature2.md` | 高 | 高 | 高 | ★ 是 |

## §2. ★★ 复核：跨三路抽 10 条，回 audit 原文逐条对

抽样覆盖三个分片 × 三种判据形态（A 面签名 / B 面前置 / C 面废弃枚举），并**刻意各抽一条各分片评得最"乐观"的**（批量可行性 高），因为那是最容易出错的地方。

| # | 抽到的行 | 所属类 | 回到的 audit 原文 | 根因类判得对不对 | 批量估得对不对 | 处置 |
|---|---|---|---|---|---|---|
| 1 | `S1-01` `CreateConicalSurface` 实参序 | D6 | `audit-01-surface-A.md` #1：官方第 3 位 `Radius`、第 4 位 `SemiAngle`，我们第 3 传 `half_angle`、第 4 传 `radius`；原文自评「个数与类型都对得上，错的是两个量的先后」 | ✅ 对 | ✅ 对（低）。原文自证**对调双方同为 `System.double`** ⇒ AST / 反射都分不出，只有官方形参名能判 | 维持 |
| 2 | `S1-09` `CreatePlanarSurface` 等 4 个 Obsolete | D1 | `audit-01-surface-C.md` #1：四页**各**有 `Obsolete. Superseded by [[IModeler::…2]]`；同文件 `SURFACE_CREATION_METHODS` **已登记** `…2` 却无任何封装调它 | ✅ 对 | ⚠️ **类级评高了**，见 §3.3（本条单看 OK，是整类"改"评高了） | 维持类归属 |
| 3 | **`S1-11`** `RULED_TYPE_MEANINGS = {0..4}` | **D2→D14** | `audit-01-surface-C.md` #3：官方 `swRuledSurfaceType_e` 是 **1..5**（无 0）；★ **原文附注逐字**：「`InsertRuledSurfaceFromEdge2.md` 的参数表确实是 0-based（0 = Tangent…4 = Sweep），但该页**没有**把 `Type` 指向 `swRuledSurfaceType_e`；同仓 `sw_surface_features.py` 已在用 1..5 口径，与本模块相反」 | ❌ **判漏了关键事实** | ❌ **估高了** | ★★ **改判 D2 → D14**。依据：audit 原文自记「**两源不一致，不判谁对**」，而 shard-1 把整段附注丢了，还给了「高」并配了「照 `enums/*.md` 生成常量表」这个修法 ⇒ **该修法会把 0-based 的调用路径改坏**。批量可行性 高 → **低** |
| 4 | `S1-22` `SW_RELIEF_NONE = 4` 等 | D2 | `audit-02-sheetmetal-C.md` #3：`InsertSheetMetalMiterFlange.md` 的 **valid selections 只列 3 条**，我们域里 5~6 个；原文自评**中** | ✅ 对 | ✅ 对（中）。判据落在**成员页的 Parameters** 而非 `enums/*.md` ⇒ 与 D2 其余条判据不同源，只能逐条 | 维持 |
| 5 | `S1-32` `mate.Name = name` | D12 | `audit-04-assembly-A.md`：**三源一致缺席**（`C:/swapi` IMate2 成员表 40 行 / CHM Public Properties 16 行 / 反射 `## IMate2` 段 34 行，均无 `Name`），原文自评「属成员缺席，不是个数/顺序/类型不符」 | ✅ 对（且原文的归类理由与我们把 M / W / C7 收敛成 D12 一致） | ✅ 对（中） | 维持 |
| 6 | `S2-13` `CreateSketchSlot` 第 2 参 | D9 | `audit-06-features-A.md`：官方三处一致声明第 2 形参是 `System.int`（枚举），我们把同一个浮点 `radius` 同时喂给第 2 位与第 3 位；原文自评「实参个数 14 = 形参个数 14，**不符点在类型不在个数**」 | ✅ 对 | ✅ 对（低）。原文明确排除了 D7（个数），排在我们把它放 D9 是对的 | 维持 |
| 7 | `S2-17` `auto_dimension_sketch` 缺一个基准 | D3 | `audit-06-features-B.md` #4：官方「**It is an error to supply just one datum**」；我们 `if segment is None: continue` 之后仍无条件调 `AutoDimension2` | ⚠️ 归类可接受，**措辞不准** | ✅ 对（中） | ★ **精化**：这不是「这一步根本没做」，而是**前置判据过弱**（缺一个基准仍往下走）。与 `S2-18` / `S2-19`（形参收了不用）同属 D3 的**「死形参 / 判据过弱」子档**，可由**纯 AST 规则**一次筛出。批量可行性 **中 → 找=高** |
| 8 | `S2-31` `sketch_flip` 的 AxisFlag | D4 | `audit-07-sketch-C.md` #3：官方 `SketchModifyFlip.md` **给了** `X = 1` / `Y = 2`，我们却断言「官方 swapi 与 CHM 均未给取值表」并把该断言写进了**对外返回值** | ✅ 对（单列 D4 是对的，shard-2 §4.2 的理由成立） | ✅ 对（低：找不出候选） | 维持。★ 注意这条在 `audit-07-sketch-A.md` #6 **被第二个核对面又报了一次** ⇒ 见 §4 附录的去重 |
| 9 | `S3-01` `IMeasure.Calculate` | D7 | `audit-08-mold-costing-A.md`：官方**四处一致**给 1 个形参 `Entities`，两个官方例子都显式传 `null`/`Nothing`，出厂反射同；我们 `_get(m, "Calculate")` **0 实参** | ✅ 对 | ✅ 对（高）。判据 = 我们实参个数 × 官方 `**Signature**` 形参个数，纯 AST + 文本 | 维持。★ 另 25 个 `_check(...)` 调用点与 cosworks CHM 逐个并排过，**全对** |
| 10 | **`S3-22`** `quality_map = {"coarse": 1, "fine": 0}` | D2 | `audit-10-misc-C.md` #5：`swSTLQuality_e` 成员只有 `Coarse 1 / Fine 2 / Custom 3`，我们给 `"fine"` 映射 **0**；原文自评高，并逐条列出 26 个「合法、未报」的枚举 | ✅ 对 | ✅ 对（高） | 维持。★ 这条的原文还给了**反面价值**：同页 #10 `sw_wrap.py` 的 `WRAP_MESH_FACTOR_DEFAULT = 0` 是**区间**越界（1–10）而非枚举 ⇒ D2 里「枚举表」与「成员页区间」两种判据必须**分开写检测器** |
| 11 | **`S3-17`** `ExportToDWG2` 前置 | D14 | `audit-10-misc-B.md` #6：`ExportToDWG2.md` 的 Remarks 写「You must select multi-body sheet-metal features」，而官方 VB.NET 例子对**同一 Action**（`swExportToDWG_ExportSheetMetal`）**无任何** `SelectByID2`；原文逐字「★ **官方两源不一致** … 判不了谁对」 | ✅ 对（shard-3 单开 C10 是对的 —— 这正是 Lead 那套关键词表的盲区） | ✅ 对（低） | 维持。★ 它与第 3 条同属 D14，**共同证明 D14 必须单列**：两条都被评过「高」或「中」，但**两源都在上、修不了** |

### §2.1 复核结论

| 口径 | 数字 |
|---|---|
| 抽样 | **11 条**（跨 3 分片 · 跨 3 核对面 · 覆盖各分片评得最乐观与最保守的两端） |
| 根因类判对 | **9 / 11** |
| 根因类判漏（★ 改判） | **1**（`S1-11`：D2 → **D14**） |
| 根因类措辞需精化 | **1**（`S2-17`：不是「没做」是「判据过弱」） |
| 批量可行性判对 | **10 / 11** |
| 批量可行性需下调 | **1**（`S1-11`：高 → 低） |
| 批量可行性需上调 | **1**（`S2-17`：中 → 找=高） |

★★ **最值得记的一条横向结论**：
> ★ **「官方两源不一致」这条线，三路共出现 5 处**（`audit-01-surface-C` #3 · `audit-02-sheetmetal-B` 的 Gusset · `audit-07-sketch-C` #4 · `audit-08-mold-costing-A` 记 0 条 · `audit-10-misc-B` #6），**但只有 shard-3 单开了类**，另外两路各把它**吞进了「枚举取值」或「前置没做」**。
> ⇒ ★ 这不是分类风格差异，是**真实风险**：一旦按「照官方枚举表换值」批量改，会把 `sw_surface_edit_ops.py`（0-based 调用路径）改成与官方 `swRuledSurfaceType_e` 一致 —— 而原文明说**该成员页并没有把 `Type` 指向那个枚举**。
> ⇒ ★ **任何 D2 批量脚本动手前，必须先跑一遍「该枚举是否存在第二源冲突」的过滤**（`enums/*.md` × 出厂反射 `enum_values_sldworks.txt` × 成员页 Parameters），命中的转人工。

@@SECTION3@@

@@SECTION4@@
