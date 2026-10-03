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

## §3. ★★ 总的可批量性结论（业主要的那个答案）

### §3.1 先把口径钉死（这是三路分歧的根源）

三份分片各自给的「可批量」比例是 **48%**（shard-1：B1+B2+B4 覆盖 21/44）、**33%**（shard-2：11/33「两类都成立」）、**44%**（shard-3：12/27「能一类一修」）。
★ **三个数都对，但它们数的是不同的东西**：

| 口径 | 含义 | 覆盖率 |
|---|---|---|
| 「一类一查」 | 一个静态脚本能把这一类**找全** | **54 / 104 = 52%** |
| 「一类一修」 | 再加一个**共用修法**能**全改完** | **17 / 104 = 16%** |

shard-2 §3.3 已经点破这个区分（「**找得全与改得动是两个独立的轴**」），shard-3 §3.3 也说了（「**发现成本 ≫ 修复成本，而发现恰恰是能批量的**」）；shard-1 的 B1 把「批量**报** + 逐条判是否该换」整批记成了覆盖。
⇒ ★★ **本总表一律按用户口径（一个脚本找全 **且** 一个共用修法改全）计，判据是「找=高 且 改=高」。**

### §3.2 ★ 可以「一类一修」的三档 —— 共 **17 条（16.3%）**

| 档 | 类 · 形态 | 条数 | 一个脚本怎么找全 | 共用修法是什么 |
|---|---|---|---|---|
| **①** | **D2 取值不在合法域 · 「我们的取值域 = 官方取值域 ∖ k」档** | **8** | AST 抽所有传给枚举形参的整数字面量 / `SW_*` 常量 / 白名单元组 × `C:\swapi\enums\*.md` 的成员表 **∪** 成员页 `## Parameters` 里的区间句式（`valid range is 1 … to 5`） | **以官方成员表为真源重生成我们的取值域/常量表**（不是逐条补值）。三路中 shard-1 §3.4 已独立得出同一结论 |
| **②** | **D1 废弃成员 · 「只出现在兜底 / 回退分支」档** | **8** | AST 抽调用点 →（官方 `types/*.md` 首行 `Obsolete.` 名单 + CHM 二源）→ 对每个命中查「**同函数内是否已存在官方后继的调用**」 | **删掉那个冗余分支**（或把后继提到首位）。一条规则、零歧义 |
| **③** | **D7 参数个数不符 ·「`System.object` 形参漏传」** | **1** | 我们调用点实参个数 × 官方 `**Signature**` 形参个数（纯 AST + 文本） | 按官方例子把 `System.object` 形参传 `null` / `Nothing` |
| | **合计** | **17** | | |

★ 档 ② 的 8 条具体是：`S2-09` / `S2-10`（`IView.Name` 兜底，主路径已是 `GetName2`）· `S2-26`（`sw_part.py` 同文件另一处已用 `SketchManager.ActiveSketch`）· `S2-27`（下一行就是 `Select4`）· `S2-28`（`("Select2","Select4")` 里的 `Select2`）· `S1-44`（`except` 回退分支，同函数上一分支已用 `ActivateDoc3`）· `S3-21` / `S3-24`（两条 `ActivateDoc2` 的 `except` 分支）。
★ 这 8 条是三路里**最标准化的批量修复**：判据是一个布尔（"后继是否已在同函数被调过"），修法是一个动作（删）。

### §3.3 ★ 只能一条一条改的 —— 共 **87 条（83.7%）**

**按类的「找得全 / 改得动」矩阵**（★ 改判**不是**按"能不能改"判，是按"能不能**同一形态共用一个修法**"判）：

| 类 | 条数 | 找 | 改 | 为什么改不动（一句话） |
|---|---|---|---|---|
| **D1** 废弃成员 | **34** | **高** | 低 | ★ **一个 sed 打不掉**：三路实测出 **8 种改法** —— ① 同型同名（`Select2`→`Select4`）② 删兜底分支（8 条，已单列为档②）③ 首位换后继（`CreateSpline2`→3）④ **后继形参变了**（`MoldUndercutDetect` 6→9；`AddComponent4`→5 多配置名）⑤ **属性→方法**（`IDimension.SystemValue`→`GetSystemValue3`）⑥ **换宿主接口**（`IModelDoc2.GraphicsRedraw2`→`IModelView.GraphicsRedraw`；`IModelDoc2.SetUserPreferenceIntegerValue`→`IModelDocExtension.SetUserPreferenceInteger`）⑦ **链尾是 `CreateFeature` + `XxxFeatureData`**（`FeatureFillet`→2→3、`FeatureLinearPattern3`→4→5、`FeatureCircularPattern4`→5）⑧ **by-ref 出参新增**（`GetErrorCode`→`GetErrorCode2`）。★ 第 ⑧ 种还撞本仓**已知事实 47**（pywin32 迟到绑定不可调用指针接口）—— 代码注释逐字写着「**使用无歧义的 `GetErrorCode` 兼容 pywin32**」⇒ **明知故犯的防御，批量替换会把它换成已知会失败的调用** |
| **D3** 前置没做 | **31** | 中 | 低 | ★ 官方前置散在**三种载体**（`## Remarks` 散文 / 官方例子的**排列** / `Selections that Define Features.md` 专章），且 `audit-02-sheetmetal-B` 自证**官方页与官方例子相反**（Gusset 的 `CreateDefinition` 顺序）⇒ 静态脚本**判不了谁对**。改法上每条要补的「选什么 / mark 几 / 走哪个成员」逐条不同 |
| **D2** 取值不在合法域 | **10** | **高** | 高 **8** / 中 2 | ★ 档①之外的 2 条判据异源：`S1-22`（看**成员页的 valid selections** 而非 `enums/*.md`）· `S1-29` / `S1-30`（要**加白名单**、要换 `CreateDefinition` 常量，不是换值） |
| **D4** 文档性分歧 | **6** | 中 | 高 | ★ **改法统一**（把「官方没给」改成引用官方原文），**但找不出候选** —— 判据是「我们的注释与官方页做语义比对」，只有 grep「没给 / 查不到 / 未收录 / 原样透传」当粗筛 |
| **D5** 实参量纲 | **3** | **高** | 中 | ★ 「找」极规整（3/3 同形态：`data.BendAngle` / `data.BendAngle` / `data.Angle` = `float(spec.angle)`），一条规则全找；但改法要连带改 `validate()` 的值域（0..360 度 ⇒ 0.261799..1.5708 弧度），且 `ISMGussetFeatureData.ProfileAngleDim` **官方页没给单位**（audit-02-A 记「查不到」）⇒ 同形态里混着一个不能判的 |
| **D6** 参数顺序 | **2** | 低 | 低 | ★ 对调双方**类型完全相同**（`double`↔`double`、`object`↔`object`）⇒ 只有官方**形参名**能区分，而形参名不可靠时必误判 |
| **D8** 调用序 / 事务层级 | **3** | 低 | 低 | ★ 要跨成员做顺序推理（`PreTrimSurface`↔`PostTrimSurface`、`GetInterferences`↔`Done`），证据只在官方例子的**排列**里；事务层级（`sw_topology.py` 少开一层 `BeginEdit`）是领域知识 |
| **D9** 类型 / 形状 | **3** | **高** | 低 | ★ 「找」高（出厂反射 `iface_sldworks.txt` 有每个形参的 VT 类型，我们 `int()` / `float()` 包装是 AST 可见的）；「改」要逐条（包 `VARIANT(VT_ARRAY|VT_DISPATCH)` 还是换包装） |
| **D10** 实参语义喂错 | **2** | 低 | 低 | ★ 官方只说「`Object`」，真语义在 `- **Bodies**: Array of [[Body2]] objects`；改法三选（删参 / 换参 / 补 `GetBodies2`）。★ 但这 2 条与 D3 的 `S1-25` / `S1-26` **是同一处代码的两面** ⇒ **改一处解两条** |
| **D11** 前置门槛方向错 | **2** | 低 | 低 | ★ 与 D3 **方向相反**：一条是「把官方的 `null or Nothing` 当成硬约束」（`PBodyIn` / `PPartDocIn`），一条是「**多做**了官方没要求的限制」（放样 `< 2` 轮廓门禁 vs 官方「any number of profiles」） |
| **D12** 取错了成员 | **3** | 中 | 低 | ★ `GetSelectedObjectType3` 被当 mark 用（名字对、类型对、**用途错**）；`IMate2.Name` 三源缺席；`CosmosWorks` vs `COSMOSWORKS` 大小写 —— 最后一条**必须真机探针**才能定（COM 后期绑定大小写不敏感） |
| **D13** 转述失真 | **1** | 低 | 低 | ★ 我们称「官方示例先选圆」，官方例子其实 `SelectByID2("Front Plane","PLANE",…)` 后接 `ClearSelection2`。**修 = 知道真相**，真相只能逐条回官方例子读 |
| **D14** 官方源冲突 | **3** | **高** | 低 | ★ 按定义不可批量：要么真机探针，要么立一条「冲突时以 Remarks 为准」的政策 |
| **D7** 参数个数 | **1** | **高** | **高** | ★ 唯一的全绿档（档③）。★ 但只 1 条 —— **量太小是它的问题，不是它不该做**（见 §4 附录：同类已在 `audit-09-A` 增至 3 条） |

### §3.4 ★★ 一句话回答业主的问题

> **「如果先只做可批量那几类，一共能清掉多少条分歧？」—— 17 条，占 104 条的 16.3%。**
>
> ★ 具体是三档：**① 取值域对齐 8 条 · ② 废弃成员的兜底分支删除 8 条 · ③ `object` 形参漏传 1 条。**
>
> ★★ **但这三个数字本身不是重点，重点是下面三句：**
> 1. ★ **一次「一类一查」能覆盖 54 条（52%）**，把无界的人工通读变成有限的待改清单 —— shard-3 §3.3 的判断是对的：**该投资的是检测器，不是通用修法**。
> 2. ★ **★ 修完这 17 条之后，第二步的性价比立刻反转**：剩下 87 条里，**D3（31）+ D1 的非兜底档（26）= 57 条**占了大头，而它们各自的**找**已经很便宜了 —— 真正的成本是**逐条读官方原文**。
> 3. ★★ **17 这个数低估了可批量性，因为分片冻结时还有 3 份 audit 没到**。把 `audit-07-sketch-A` / `-B` / `audit-09-simulation-A` 计入（§4 附录），**D5「mm↔米」这一档从 3 条变成 7 条且 4 条共用一个修法（包 `mm()`）**，**D7 从 1 条变成 3 条且 2 条共用一个修法（往 `_ERRORCODE_MEMBERS` 表里加两个名字）** ⇒ **严格可批量从 17 条涨到 22 条 / 117 条 = 18.8%**，且新增的两档都是**一个门禁就能根治**的形态。

### §3.5 ★ 三条比"类"更重要的横向发现（合并三路后浮出来的）

**① 同一个根因被多个核对面各报一次 ⇒ 104 条 ≠ 104 个修复单元。**
`GetErrorCode` 的 Obsolete 在 `audit-02-A`（附录）· `audit-02-C` · `audit-03-C` 被**报了三次**（`S1-15` / `S1-20` / `S1-28`，实为 2 个文件 3 处）；`InsertSubWeldFolder2` 的实参错在 `audit-03-A`（`S1-24`）、前置错在 `audit-03-B`（`S1-25`）**各报一次**；`InsertWeldmentCutList2` 同理（`S1-23` / `S1-26`）；`ActivateDoc2` 的 2 个 except 分支（`S1-44` / `S3-21` / `S3-24`）实为 3 处 1 个成员。
⇒ ★ **按"代码位置"去重后，104 条可合并到约 96 个修复单元** ⇒ ★★ **修的分母比 104 小，且这一条对排期的影响（-8）比"多修一类"（+1）大得多。**

**② 一整类「无源常量」横跨全表，任何单片都发现不了。**
`audit-02-sheetmetal-C` 与 `audit-03-weldment-C` **各自独立**记下同一件事：`swFeatureNameID_e.md` 的 `enum_member_count: 130`，成员表「Value」列装的是**描述**（`\| swFmBaseFlange \| Base flange \|`）**而不是数值**。
⇒ 我们代码里的 `SW_FM_BASE_FLANGE=34` / `SW_FM_DRAFT=3` / `SW_FM_ONE_BEND=33` / `SW_FM_SKETCH_BEND=35` / `SW_FM_EDGE_FLANGE=37` / `SW_FM_SWEPT_FLANGE=117` / `SW_FM_SM_GUSSET=118` / `SW_FM_MATE_PROFILE_CENTER=101` / `SW_FM_PROFILE_FEATURE=65` / `SW_FM_WELD_MEMBER_FEAT=72`，再加 `sw_sweep.py` 的 `SW_FM_SWEEP=17` / `SW_FM_SWEEP_CUT=18` / `SW_FM_REF_SURFACE=62` —— **十三个数值全部无官方依据可核**（`audit-10-misc-C` 的「查不到」段独立记到后三个）。
⇒ ★★ **这不是"某一条分歧"，是一条一次普查可解的系统性问题。** 第三源是出厂反射 `D:\AI\SW\_raw\**\enum_values_sldworks.txt`（本仓已知事实 43 已用它解过 `swFeatureNameID_e` 的数值）。
⇒ ★ **它应当按"普查"推进，不该按"条"修** —— 而且它一旦解出来，D2 的常量档和 D3 的 `CreateDefinition` 白名单档（`S1-30`）会**同时受益**。

**③ 「改了会坏」的坑已经写在代码注释里，批量脚本必须带这道过滤。**
`S1-20` 的注释逐字：「`GetErrorCode2` 多一个 by-ref `isWarning` 参数；此处只需拒绝硬错误，**使用无歧义的 `GetErrorCode` 可兼容 pywin32 静态与动态代理**」⇒ 与本仓**已知事实 47**（`IAccessSelections` / `IAccessSelections2` 在 pywin32 下不可调用）**同族**。
⇒ ★★ **任何"废弃成员批量替换"脚本，第一步必须是「后继是否多出 by-ref / out 形参」过滤**，命中即转人工；否则会把"明知故犯的防御"换成"已知会失败的调用"。

## §4. 每类**建议动作** + 事后新增 audit 的附录

### §4.1 建议动作表（按「造门禁 / 挂共用 pre_call / 逐个改 / 只记档」四档）

| 类 | 条数 | 建议动作 | 动作的具体形态（可直接开工） |
|---|---|---|---|
| **D2** 取值不在合法域 | 10 | ★ **造门禁**（主）+ 档① **共用修法** | 门禁 `check_enum_domain.py`：AST 抽整数字面量 / `SW_*` 常量 / 白名单元组 → 比 `C:\swapi\enums\*.md` 成员表 **∪** 成员页 `## Parameters` 的区间句式 → 差集报错。★ **必须内建两条豁免**：① `[Bitmask]` 枚举（官方 `Bitmasks.md` 未定义 0，如 `swDraftAnalysisOptions_e`，audit-08-C 已判「查不到 → 不报」）；② **第二源冲突**（§2.1 的过滤器，命中即转人工）。★ 根治动作 = **从官方 enum 页生成常量表**，不是逐条补值 |
| **D1** 废弃成员 | 34 | ★ **造门禁（只报不换）** + 档② **共用修法** | 门禁 `check_obsolete_members.py`：AST 抽成员名 × `types/*.md` 首行 `Obsolete.` + CHM 二源 → 输出「调用点 / 旧成员 / 官方点名后继 / **后继是否多 by-ref**」四列表。★ **只报不换**；唯一允许批量动手的是档②那 8 条（判定式：**同函数内已存在后继调用 ⇒ 删旧分支**）。★ 非兜底的 26 条**逐条读后继页再改** |
| **D3** 前置没做 | 31 | ★ **挂共用 pre_call**（首选）+ 逐个改 | ★ 共用 `pre_call` 层做**三件事**：① 从官方页抽前置（`Before calling this method` + `with the following Marks` / `has a mark of N` / `must select` 三种句式，**这层要 LLM，不能只 grep**）；② **★ 挂纯 AST 门禁「死形参 / 判据过弱」**（形参在函数体内从未被使用、或从未赋给任何 FeatureData 属性）——它把 D3 的人工审阅量从 **31 降到 5**（`S1-06` / `S1-19` / `S1-26` / `S2-18` / `S2-19`）；③ 对「只判 `_selection_count(...) >= 1` 没判对象类型」的那 4 条（`S2-04` / `S2-06` / `S2-07` / `S2-08`）**换成同一形态的判据**。★ 其余**逐条按官方原文补 `SelectByID2` + mark** |
| **D4** 文档性分歧 | 6 | ★★ **造门禁（最便宜、危害最大，优先做）** | `check_source_coverage_claims.py`：扫我们 docstring / 注释里的「**查不到 / 未收录 / 未给取值表 / 不假定 / 原样透传**」措辞 → 把提到的成员名拿去对 `C:\swapi\types\` → **有页即为误判**。★ 这一类**不碰 COM、不碰真机**，6 条全是文案；★ 而它会让下游把"我们不知道"当成事实（工具 docstring 明写 `unverified`）⇒ **危害远大于条数** |
| **D5** 实参量纲 | 3 | ★ **造门禁 + 逐个改**（★ 附录后升为「共用修法」优先） | 门禁：AST 找 `data.X = float(spec.*angle*)` 且官方 `## Returns` 含 `radians` ⇒ 报错。★ **附录的 4 条 mm↔米 共用一个修法（包 `mm()`），应优先于这 3 条做** —— 同模块 `sw_sketch_edit.py` 调 `CreateChamfer` **已经**在用 `mm(float(distance_mm))`，**同文件邻居就是正确写法**，照抄即可 |
| **D6** 参数顺序 | 2 | **逐个改** | 对调双方同为 `double` / `object` ⇒ 只能靠官方**形参名**逐个对照。无门禁可挂 |
| **D7** 参数个数 | 1 | ★ **共用修法**（先做，附录后 3 条） | 门禁 `check_arity.py`：调用点实参个数 × 官方 `**Signature**` 形参个数。★ 附录的 2 条 cosworks 同根因（漏列 `_ERRORCODE_MEMBERS`）⇒ **往那张表加两个名字即修完两条** |
| **D8** 调用序 / 事务层级 | 3 | **逐个改** | 跨成员顺序推理 + 官方例子的排列；事务层级是领域知识 ⇒ 只能照同模块邻居抄（`sw_topology.py::set_topology_goal` 已有正确写法） |
| **D9** 类型 / 形状 | 3 | ★ **造门禁（只报）+ 逐个改** | 门禁：出厂反射 `iface_sldworks.txt` 的形参 VT 类型 × 我们实参的 AST 包装类型（`float()` 包过 ⇒ 一定不是数组）。改法逐条 |
| **D10** 实参语义喂错 | 2 | ★ **逐个改（但改一处解两条）** | 与 D3 的 `S1-25` / `S1-26` 同一处代码两面（`InsertSubWeldFolder2` / `InsertWeldmentCutList2` 的 `Object` 形参应喂 `Body2` 数组）⇒ **修 D3 那两条时顺手把这两条一起解** |
| **D11** 前置门槛方向错 | 2 | ★ **逐个改**（注意**方向相反**） | 一条要**放松**（放样 `< 2` 门禁 vs 官方「any number of profiles」）· 一条要**加分支**（`PBodyIn` / `PPartDocIn` 在零件上下文要传 `null or Nothing`）。★ 与 D3 相反，改的时候别顺手统一 |
| **D12** 取错了成员 | 3 | ★ **逐个改**（`CosmosWorks` 那条**只记档**） | `IMate2.Name` 三源缺席 ⇒ 走 `CreateMate` 的签名改（**与 D1 的 `S1-38` 同源，应合并处理**）；`GetSelectedObjectType3` → `GetSelectedObjectMark`；★ `CosmosWorks` / `COSMOSWORKS` **大小写**必须真机探针 ⇒ **本轮只记档，不判** |
| **D13** 转述失真 | 1 | **只记档** | 1 条，`sw_helix.py` 的报错文案。修 = 逐条回 `Create_Spiral_Example_VB.md` 读真相，**不值得造门禁** |
| **D14** 官方源冲突 | 3 | ★★ **只记档 + 立一条政策** | **不建议现在修**。★ 需要的是一条仓级政策：**「官方两源冲突时以 `## Remarks` 为准」还是「先真机探针裁决」**。`S1-11` / `S2-32` 在政策定下来之前**任何自动化都不许碰** |

### §4.2 排期建议（若只能做三件事）

| 序 | 做什么 | 覆盖条数 | 为什么排这个位置 |
|---|---|---|---|
| **1** | `check_source_coverage_claims.py`（D4 门禁） | **6** | ★ 最便宜（不碰 COM / 不碰真机）· 危害最大（污染 MCP 工具描述）· 6 条全文案 |
| **2** | `check_enum_domain.py`（D2 门禁 + 常量表生成器） | **10** | 条数第二 · 根治后 `SW_*` 无源常量问题（13 个）一起消 |
| **3** | **D3 的死形参 AST 门禁** | 0（筛子） | ★ 把 D3 的人工审阅量从 **31 降到 5**，是本总表**杠杆最大**的一件（不动任何模型代码） |

⇒ ★★ 这三件做完：**门禁覆盖 16 条 + 把 31 条的人工量砍到 5 条**，而**模型代码只需要动 3 处**（档①的取值域、档②的 8 个兜底分支、档③的 1 个漏传实参）。

### §4.3 ★ 附录：分片冻结之后才到的 3 份 audit（13 条新分歧）

★ shard-2 §0 写「`audit-07-sketch-A` / `-B` 在本仓不存在」、shard-3 §0 写「`audit-09-A/C` 仍不存在」—— **这 3 份是并发写的，比分片晚到**，因此不在 104 条里。**它们不改变上面的任何一条结论，但改变两个数字。**

| # | 文件 | 行 | 统一类 | 分歧 | 置信 | 找 | 改 |
|---|---|---|---|---|---|---|---|
| A-1 | `audit-07-sketch-A` | 1 | **D9** | `GetContourEdges(contour)` 官方形参是 `Xform`（16 个 double 的变换数组），我们传轮廓对象；官方给"按轮廓取边"的是 `ISketchContour::GetEdges` | 高 | 中 | 低 |
| A-2 | `audit-07-sketch-A` | 2 | **D5** | `CreateFillet(radius_mm)` 官方形参表 `Radius: Radius of the fillet in **meters**`、官方配方传 `0.01`（=10 mm），我们**原样传 mm** ⇒ 放大 1000 倍 | 高 | **高** | ★ **高** |
| A-3 | `audit-07-sketch-A` | 3 | **D5** | `SketchOffset2(offset_mm)` 同上（官方配方 `0.00254` = 2.54 mm 的米制值） | 高 | **高** | ★ **高** |
| A-4 | `audit-07-sketch-A` | 4 | **D5** | `CreateLinearSketchStepAndRepeat(spacing_x_mm/y_mm)` 同上（官方配方 `0.0254`） | 高 | **高** | ★ **高** |
| A-5 | `audit-07-sketch-A` | 5 | **D5** | `CreateCircularSketchStepAndRepeat(arc_radius_mm)` 同上（官方配方 `0.0318`）。★ 同行 `math.radians(...)` 的角度与官方配方**方向一致，不算分歧** | 高 | **高** | ★ **高** |
| — | `audit-07-sketch-A` | 6 | D4 | ★ **= `S2-31` 同一处分歧被第二个核对面再报一次**（A 面 vs C 面）⇒ **不另计** | 高 | — | — |
| B-1 | `audit-07-sketch-B` | 1 | **D3** | `SketchTrim` 官方前置点名 `SelectByID2` + **mark = 0** + 按 pick point；我们的路径是 `Select4`（无 mark、无 pick point） | 高 | 中 | 低 |
| B-2 | `audit-07-sketch-B` | 2 | **D3** | `SketchOffset2` 官方例子用 `SelectByID2(..., mark=1)`；我们的 `Select4` 路径没有 mark | 高 | 中 | 低 |
| B-3 | `audit-07-sketch-B` | 3 | **D11** | ★ **方向相反的一档**：官方例子里 `ClearSelection2(true)` → 建矩形 → 调阵列，**中间没有任何选中动作**；我们**无条件先选**一段草图段 | 中 | 低 | 低 |
| B-4 | `audit-07-sketch-B` | 4 | **D3** | `MergePoints` 官方前置是「草图里**只能有一个开放轮廓**」，我们未做该检查、注释里也没提 | 高 | 中 | 低 |
| B-5 | `audit-07-sketch-B` | 5 | **D3** | 官方例子在选中前有一步 `swModel.SetPickMode()`，我们没有 | 中 | 低 | 低 |
| C-1 | `audit-09-simulation-A` | 1 | **D7** | `GetLoadsAndRestraints` 官方三源一致是 **2 个形参**（`NIndex` + by-ref `ErrorCode`），我们只传 1 个 ⇒ **`_ERRORCODE_MEMBERS` frozenset 里漏了这个名字** | 高 | **高** | ★ **高** |
| C-2 | `audit-09-simulation-A` | 2 | **D7** | `GetEdgeWeldConnector` **同一根因**（同样漏列 `_ERRORCODE_MEMBERS`）⇒ ★★ **往那张表加两个名字 = 修完两条** | 高 | **高** | ★ **高** |
| C-3 | `audit-09-simulation-A` | 3 | **D12** | 对载荷对象调 `GetName` / `GetType`，官方**两源一致**是**属性** `Name` / `Type`（无 `Get*`）；同仓 `sw_simulation.py` 用的就是 `Name` / `Type` | 高 | 中 | 低 |

**计入后的两个数字变化：**

| 口径 | 三路并集（104） | ＋本附录 13 条（117） |
|---|---|---|
| **D5 实参量纲** | 3 条（找高 / 改**中**） | **7 条**（找高 / 改**高 ×4 + 中 ×3**）⇒ ★ **mm↔米 档成为真正的一类一修** |
| **D7 参数个数** | 1 条（可批量） | **3 条**（3 条全可批量，且 2 条共用"表里加两个名字"这一个修法） |
| **★ 严格可批量合计** | **17 条 / 16.3%** | **★ 22 条 / 18.8%** |

★ **A-2~A-5 的价值不在条数（4 条），在于它们推翻了一个结论**：
shard-1 §2 判 **U（量纲）** 是「本分片最规整的一类：3/3 同形态」，并说「不能一刀切，因为 `ProfileAngleDim` 官方页没给单位」。
⇒ ★★ **这个"不能一刀切"的结论对度↔弧度档成立、对 mm↔米档不成立** —— 后者 4/4 共用一个修法（包 `mm()`），而且**同模块 `sw_sketch_edit.py` 调 `CreateChamfer` 已经在用 `mm(float(distance_mm))`，正确写法就在隔壁**。
⇒ ★ **判定纪律**：**不要因为同一类里有一条判不了就否定整类** —— 应当拆到"形态档"再判。shard-1 §3.2 的 E 类（同理）已经用了这个思路，但没推广到 U 类。

### §4.4 结尾三行

- **总条数**：**104 条**（三路并集，`assert` 可复跑）· 追加 3 份晚到 audit 后为 **117 条**。
- **严格可批量（一个脚本找全 + 一个共用修法改全）**：**17 条（16.3%）** · 计入附录后 **22 条（18.8%）**。
- **只能逐条**：**87 条（83.7%）**，其中 **57 条**（D3 31 + D1 非兜底档 26）是修的大头，且**各自的"找"已足够便宜、成本全在逐条读官方原文**。
