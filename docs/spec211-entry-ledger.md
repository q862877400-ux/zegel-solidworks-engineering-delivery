# 规格 211 · B0 官方入口台账（21 项）

> ★ 由 `tools/gen_spec211_ledger.py` 生成 —— ★ **不要手改**。
> ★★ 查**四处**：`C:\swapi\types` · `C:\swapi\enums` · **CHM 的 API 命名空间** · CHM 示例页。
> ⚠★ 实录：**只查 `C:\swapi` 会误判「边界凸台」为「查不到」**，而 CHM 里有 `IBoundaryBossFeatureData` ✗
> ★★ 故「不做」的两种依据：**四处都查不到**（官方无入口）· **要 `AccessSelections`**（事实 47）。
> ⚠ ★★ **这不是终判** —— ★ `AccessSelections` 信号是**关键词共现**、★ 太粗（★ 实录：「曲线驱动阵列」17 个候选，★ 只要**一个**提到就触发）；★ 「疑无入口」也可能是我**命名猜错**。
> ★★ **终判方式：逐项读那一页的三样**（签名 / Remarks / Example）⇒ ★ 见 `tasks.md` B0-2。
> ★ 依据**事实 53**：同一启发式已连续改 3 次 ⇒ ★ **停止调它**，改成「信号 + 人工终判」✓

★★ 合计 **21** 项（★ **人工终判**）：★ **可做 11** · **不做 9** · **已覆盖 1** · **待实测 0**

## 特征 · 边界凸台 ⇒ **不做**

· 初判：★★ **人工终判**：★ 入口 = `IBoundaryBossFeatureData`（CHM 有 `~AccessSelections`）⇒ 属性式**要 ACL** ⇒ **事实 47**（后端限制）· ★ `AutoSelect` 或可绕开但**不试**　（★ 自动台账原判：待核实）
· 该关键词命中的 CHM **示例页**：**0**
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IBoundaryBossFeatureData.html`  
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IBoundaryBossFeatureData_members.html`  ★ 要 AccessSelections
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IBoundaryBossFeatureData_methods.html`  ★ 要 AccessSelections
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IBoundaryBossFeatureData_properties.html`  
  · `[chm-api] (CHM)::SolidWorks.Interop.swconst~SolidWorks.Interop.swconst.swBoundaryBossAlignment_e.html`  
  · `[chm-api] (CHM)::SolidWorks.Interop.swconst~SolidWorks.Interop.swconst.swBoundaryBossCurveInfluenceType_e.html`  
  · …（共 8 个候选）

## 特征 · 曲线驱动阵列 ⇒ **不做**

· 初判：★★ **人工终判**：★★★★ **后端受限** —— ★★ **官方示例逐字**（`Create_and_Access_Curve-driven_Pattern_Feature_Example_VB.md`）走的是 **`CreateDefinition(swFmCurvePattern)` + `CreateFeature`** ✗ ⇒ ★ 那条路的 Data **`ICurveDrivenPatternFeatureData` 带 `AccessSelections`** ✗（逐文件核过）⇒ **事实 47 一挡就到不了建成** ✓ ★★ 而参数式 `FeatureLocalCurveDrivenPattern` 那条**真机两档有效读数皆不建** ⇒ ★ 一并记在此 ✓ ★⚠ **本项经历过一次错误的翻案**：★ 我曾按「参数式存在且无 ACL」改判可做 ✗ —— ★★ **漏了「官方示例不用那个入口」** ✓　（★ 自动台账原判：待核实）
· 该关键词命中的 CHM **示例页**：**0**
  · `[swapi] IFeatureManager::FeatureLocalCurveDrivenPattern` `Feature FeatureLocalCurveDrivenPattern( System.bool FlipDir1, System.int Num1, System.bool EqualSpacing1, Sys 
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.ICurveDrivenPatternFeatureData.html`  
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.ICurveDrivenPatternFeatureData_members.html`  ★ 要 AccessSelections
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.ICurveDrivenPatternFeatureData_methods.html`  ★ 要 AccessSelections
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.ICurveDrivenPatternFeatureData_properties.html`  
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~FeatureLocalCurveDrivenPattern.html`  
  · …（共 17 个候选）

## 特征 · 缩放/变形 ⇒ **可做**

· 初判：★★ **人工终判**：★ `IFeatureManager::InsertScale(short Type, …)`（**参数式、无 ACL**）
· 该关键词命中的 CHM **示例页**：**0**
  · `[swapi] IFeatureManager::InsertScale` `Feature InsertScale( System.short Type, System.bool Uniform, System.double Xscale, System.double YScale, Syst 
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~InsertScale.html`  

## 特征 · 特征识别/Instant3D ⇒ **不做**

· 初判：★★ **人工终判**：★ **四处零命中** ⇒ 官方无 API 入口（铁律 5）· ★ CHM 的 9 个 `Instant3D` 页是**用户手册**、★ 不在 API 命名空间　（★ 自动台账原判：疑无入口）
· 该关键词命中的 CHM **示例页**：**9**

## 曲面 · 扫描曲面 ⇒ **可做**

· 初判：★★ **人工终判**：★ `InsertSweepSurface2` / `InsertSweepSurface3`（**参数式、无 ACL**）
· 该关键词命中的 CHM **示例页**：**0**
  · `[swapi] IFeatureManager::InsertSweepSurface` `Feature InsertSweepSurface( System.bool Propagate, System.short TwistCtrlOption, System.bool KeepTangency, Sy 
  · `[swapi] IFeatureManager::InsertSweepSurface2` `Feature InsertSweepSurface2( System.bool Propagate, System.short TwistCtrlOption, System.bool KeepTangency, S 
  · `[swapi] IFeatureManager::InsertSweepSurface3` `Feature InsertSweepSurface3( System.bool Propagate, System.int TwistCtrlOption, System.bool KeepTangency, Sys 
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~InsertSweepSurface.html`  
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~InsertSweepSurface2.html`  
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~InsertSweepSurface3.html`  

## 曲面 · 边界曲面 ⇒ **不做**

· 初判：★★ **人工终判**：★★★ **查不到官方入口**（★ 铁律 5）—— ★ 全扫 `C:\swapi\types` 无 `*BoundarySurface*` 入口；★ 最接近的是 `SetFreeformBoundaryContinuity`（**自由形**边界连续性）与 `IFillSurfaceFeatureData::*Boundary*`（**填充曲面**边界）⇒ **都不是它** ✗ ★★ 且本仓 `docs/toolbar-ledger.md` 早就写着「边界曲面 | **待查**」✓ ★⚠ **纠一处混淆**：★ 我原判把它当成了 `CreateRuledSurface`/`InsertRuledSurfaceFromEdge2` ✗ —— ★ 那是**直纹曲面**（★ **仓里已有**、★ 且**不在本规格的项里** ✓）　（★ 自动台账原判：可做）
· 该关键词命中的 CHM **示例页**：**0**
  · `[swapi] IBody2::CreateRuledSurface` `System.object CreateRuledSurface( System.object Curve1, System.object Curve2, System.object ApexPoint )` 
  · `[swapi] IBody2::ICreateRuledSurface` `Surface ICreateRuledSurface( Curve Curve1, Curve Curve2, ref System.double ApexPoint )` 
  · `[swapi] IFeatureManager::InsertRuledSurfaceFromEdge` `Feature InsertRuledSurfaceFromEdge( System.int Type, System.double Length, System.bool FlipPullDir, System.bo 
  · `[swapi] IFeatureManager::InsertRuledSurfaceFromEdge2` `Feature InsertRuledSurfaceFromEdge2( System.int Type, System.double Length, System.bool FlipPullDir, System.b 
  · `[swapi] IModeler::CreateRuledSurfaceFromEdge` `System.int CreateRuledSurfaceFromEdge( ModelDoc2 ModDoc, System.object Edges, System.int Type, System.double  
  · `[swapi] IModeler::ICreateRuledSurfaceFromEdge` `System.int ICreateRuledSurfaceFromEdge( ModelDoc2 ModDoc, System.int NumOfEdges, ref Edge Edges, System.int T 
  · …（共 11 个候选）

## 曲面 · 剪裁曲面 ⇒ **不做**

· 初判：★★ **人工终判**：★★ **后端受限** —— ★ 依据**事实 419**：★「**照官方例子把前置完全对上**」**而特征仍不建**（★ 案例之一就是**剔裁曲面**）✗ ⇒ ★ **不做** ✓ ★（★ **「取消剪裁」是另一半** —— ★ B2-1 已补包装、`untrim_surface` = `stitched` ✓）　（★ 自动台账原判：可做）
· 该关键词命中的 CHM **示例页**：**0**
  · `[swapi] IFeatureManager::InsertUntrimSurface` `Feature InsertUntrimSurface( System.int FaceUntrimType, System.int EdgeUntrimType, System.double Distance, Sy 
  · `[swapi] IFeatureManager::InsertUntrimSurface2` `Feature InsertUntrimSurface2( System.int FaceUntrimType, System.int EdgeUntrimType, System.double Distance, S 
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~InsertUntrimSurface.html`  
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~InsertUntrimSurface2.html`  
  · `[swapi] IBody2::CreatePlanarTrimSurfaceDLL` `System.bool CreatePlanarTrimSurfaceDLL( System.object Points, System.object Normal )` 
  · `[swapi] IBody2::ICreatePlanarTrimSurfaceDLL` `void ICreatePlanarTrimSurfaceDLL( System.int VertexCount, ref System.double Points, ref System.double Normal  
  · …（共 12 个候选）

## 钣金 · 成形工具 ⇒ **可做**

· 初判：★★ **人工终判**：★ `CreateFormTool2` / `InsertFormToolFeature` / `CreateFormTool`（**参数式、无 ACL**）　（★ 自动台账原判：待核实）
· 该关键词命中的 CHM **示例页**：**0**
  · `[swapi] IFeatureManager::CreateFormTool` `Feature CreateFormTool()` 
  · `[swapi] IFeatureManager::CreateFormTool2` `Feature CreateFormTool2( System.double OriginX, System.double OriginY )` 
  · `[swapi] IFeatureManager::InsertFormToolFeature` `Feature InsertFormToolFeature( System.string Path, System.bool Flip, System.double RotAngle, System.string Co 
  · `[swapi] ILibraryFormToolFeatureData::FormToolConfiguration` `System.string FormToolConfiguration {get; set;}` 
  · `[swapi] ILibraryFormToolFeatureData::FormToolPath` `System.string FormToolPath {get; set;}` 
  · `[swapi] ILibraryFormToolFeatureData::LinkToFormTool` `System.bool LinkToFormTool {get; set;}` 
  · …（共 16 个候选）

## 钣金 · 展开/折叠 ⇒ **已覆盖**

· 初判：★★ **人工终判**：★★ **由 `specs/209` 收口**：B2-1 `create_unfold` 与 B4-4 `create_fold` **都已 `verified`**（真机建出 `展开1`/`折叠1`）⇒ ★ **核销，不重复建设** ✓　（★ 自动台账原判：可做）
· 该关键词命中的 CHM **示例页**：**3**
  · `[swapi] IModelDoc2::InsertSheetMetalUnfold` `void InsertSheetMetalUnfold()` 
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IModelDoc2~InsertSheetMetalUnfold.html`  
  · `[swapi] IModelDoc2::InsertSheetMetalFold` `void InsertSheetMetalFold()` 
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IModelDoc2~InsertSheetMetalFold.html`  
  · `[swapi] IDrawingDoc::CreateUnfoldedViewAt` `System.bool CreateUnfoldedViewAt( System.double X, System.double Y, System.double Z )` 
  · `[swapi] IDrawingDoc::CreateUnfoldedViewAt2` `System.bool CreateUnfoldedViewAt2( System.double X, System.double Y, System.double Z, System.bool NotAligned  
  · …（共 10 个候选）

## 钣金 · 平板型式/导出 DXF ⇒ **可做**

· 初判：★★ **人工终判**：★★★★★ **用户 2026-10-07 授权后真机建成**（★ 原话「★ **D 我允许你做**」✓）—— ★★ 实现：`scripts/sw_export.py` 的 `export_flat_pattern_dxf` 新增 `allow_temporary_save`（★ **默认 `False`** ⇒ ★ 行为与从前**完全一致** ✓）与 `temporary_save_dir` ✓；★★★ 判据**一正两负**（`tests/test_spec211_flat_pattern_save.py` **4 passed** + `tools/probe_spec211_flatsave.py`）⇒ ★ 回读 DXF **20219 字节** ✓ ★★ 授权是**场景性的**、★ **不是**全仓废止硬约束⑦ ✓　（★ 自动台账原判：待核实）
· 该关键词命中的 CHM **示例页**：**0**
  · `[swapi] IAnnotationView::FlatPatternView` `System.bool FlatPatternView {get;}` 
  · `[swapi] IDrawingDoc::ChangeRefConfigurationOfFlatPatternView` `System.bool ChangeRefConfigurationOfFlatPatternView( System.string ModelName, System.string ConfigName )` 
  · `[swapi] IDrawingDoc::CreateFlatPatternViewFromModelView` `System.bool CreateFlatPatternViewFromModelView( System.string ModelName, System.string ConfigName, System.dou 
  · `[swapi] IDrawingDoc::CreateFlatPatternViewFromModelView2` `System.bool CreateFlatPatternViewFromModelView2( System.string ModelName, System.string ConfigName, System.do 
  · `[swapi] IDrawingDoc::CreateFlatPatternViewFromModelView3` `View CreateFlatPatternViewFromModelView3( System.string ModelName, System.string ConfigName, System.double Lo 
  · `[swapi] IFeatureManager::GetFlatPatternFolder` `System.object GetFlatPatternFolder()` 
  · …（共 33 个候选）

## 焊件 · 裁剪/延伸焊件 ⇒ **可做**

· 初判：★★ **人工终判**：★ `InsertWeldmentTrimFeature2`（**参数式、无 ACL**）· 另 `InsertEndCapFeature` ✓
· 该关键词命中的 CHM **示例页**：**0**
  · `[swapi] IFeatureManager::InsertWeldmentTrimFeature` `Feature InsertWeldmentTrimFeature( System.int EndCond )` 
  · `[swapi] IFeatureManager::InsertWeldmentTrimFeature2` `Feature InsertWeldmentTrimFeature2( System.int EndCond, System.int Options, System.double GapValue, System.ob 
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~InsertWeldmentTrimFeature.html`  
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~InsertWeldmentTrimFeature2.html`  
  · `[chm-api] (CHM)::SolidWorks.Interop.swconst~SolidWorks.Interop.swconst.swWeldmentTrimExtendOptionType_e.html`  
  · `[swapi] IFeatureManager::InsertEndCapFeature` `Feature InsertEndCapFeature( System.double Depth, System.bool BIsGivenOffset, System.bool BIsChamfer, System. 
  · …（共 11 个候选）

## 焊件 · 角撑板（焊件） ⇒ **可做**

· 初判：★★ **人工终判**：★ `InsertGussetFeature3`（**参数式、无 ACL**）⇒ ★ **只走参数式**；★ 属性式 `IGussetFeatureData` 有 `AccessSelections` ⇒ **那条不走**（事实 47）　（★ 自动台账原判：待核实）
· 该关键词命中的 CHM **示例页**：**11**
  · `[swapi] IFeatureManager::InsertGussetFeature` `Feature InsertGussetFeature( System.double Depth, System.short DirType, System.short LocType, System.bool BIs 
  · `[swapi] IFeatureManager::InsertGussetFeature2` `Feature InsertGussetFeature2( System.double Depth, System.short DirType, System.short LocType, System.bool BI 
  · `[swapi] IFeatureManager::InsertGussetFeature3` `Feature InsertGussetFeature3( System.double Depth, System.short DirType, System.short LocType, System.bool BI 
  · `[swapi] IFeatureManager::InsertSheetMetalGussetFeature` `Feature InsertSheetMetalGussetFeature( System.bool BOffset, System.double DOffset, System.bool BFlipOffsetSid 
  · `[swapi] IFeatureManager::InsertSheetMetalGussetFeature2` `Feature InsertSheetMetalGussetFeature2( System.bool BOffset, System.double DOffset, System.bool BFlipOffsetSi 
  · `[swapi] IFeatureManager::InsertSheetMetalGussetFeature3` `Feature InsertSheetMetalGussetFeature3( System.bool BOffset, System.double DOffset, System.bool BFlipOffsetSi 
  · …（共 25 个候选）

## 焊件 · 圆角焊缝 ⇒ **可做**

· 初判：★★ **人工终判**：★ `InsertFilletBeadFeature3` / `InsertCosmeticWeldBead`（**参数式、无 ACL**）　（★ 自动台账原判：待核实）
· 该关键词命中的 CHM **示例页**：**0**
  · `[swapi] IFeatureManager::InsertFilletBeadFeature` `Feature InsertFilletBeadFeature( System.short Type1, System.double Size1, System.double Length1, System.doubl 
  · `[swapi] IFeatureManager::InsertFilletBeadFeature2` `Feature InsertFilletBeadFeature2( System.short Type1, System.double Size1, System.double Length1, System.shor 
  · `[swapi] IFeatureManager::InsertFilletBeadFeature3` `Feature InsertFilletBeadFeature3( System.short Type1, System.double Size1, System.double Length1, System.shor 
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~InsertFilletBeadFeature.html`  
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~InsertFilletBeadFeature2.html`  
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~InsertFilletBeadFeature3.html`  
  · …（共 31 个候选）

## 焊件 · 焊接符号 ⇒ **可做**

· 初判：★★ **人工终判**：★ `InsertWeldSymbol3` / `InsertWeldSymbol2`（★ 无 ACL）· 读回用 `GetFirstWeldSymbol` ✓
· 该关键词命中的 CHM **示例页**：**0**
  · `[swapi] ICosmeticWeldBeadFeatureData::WeldSymbol` `System.object WeldSymbol {get; set;}` 
  · `[swapi] IDrawingDoc::InsertWeldSymbol` `void InsertWeldSymbol( System.string Dim1, System.string Symbol, System.string Dim2, System.bool Symmetric, S 
  · `[swapi] IModelDoc2::IInsertWeldSymbol3` `WeldSymbol IInsertWeldSymbol3()` 
  · `[swapi] IModelDoc2::InsertWeldSymbol2` `void InsertWeldSymbol2( System.string Dim1, System.string Symbol, System.string Dim2, System.bool Symmetric,  
  · `[swapi] IModelDoc2::InsertWeldSymbol3` `System.object InsertWeldSymbol3()` 
  · `[swapi] IView::GetFirstWeldSymbol` `System.object GetFirstWeldSymbol()` 
  · …（共 19 个候选）

## 装配 · 爆炸直线 ⇒ **可做**

· 初判：★★ **人工终判**：★ `IAssemblyDoc::InsertExplodeLineSketch()`（**零参数、无 ACL**）· 配套 `AddExplodeStep2` 族 ✓
· 该关键词命中的 CHM **示例页**：**0**
  · `[swapi] ISketchManager::InsertExplodeLineSketch` `System.bool InsertExplodeLineSketch()` 
  · `[swapi] IConfiguration::AddExplodeStep` `System.object AddExplodeStep( System.double ExplDist, System.bool ReverseDir, System.bool RigidSubassembly, S 
  · `[swapi] IConfiguration::AddExplodeStep2` `System.object AddExplodeStep2( System.double ExplDist, System.int ExplDirIndex, System.bool ReverseDir, Syste 
  · `[swapi] IConfiguration::AddPartExplodeStep` `System.object AddPartExplodeStep( System.string ExplodeView, System.double ExplDist, System.int ExplDirIndex, 
  · `[swapi] IConfiguration::AddRadialExplodeStep` `System.object AddRadialExplodeStep( System.double ExplDist, System.double ExplAng, System.bool DivergeFromAxi 
  · `[swapi] IConfiguration::DeleteExplodeStep` `System.bool DeleteExplodeStep( System.string ExplodeStepName )` 
  · …（共 34 个候选）

## 装配 · 零部件阵列 ⇒ **不做**

· 初判：★★ **人工终判**：★★★★ **后端受限** —— ★★ **官方示例逐字**（`Create_Local_Curve-driven_Pattern_Example_CSharp.md`）走的是 **`CreateDefinition(swFmLocalCurvePattern)` + `CreateFeature`** ✗，★ 且其 `Postconditions` 逐字「**Selects the component and edge**」⇒ **装配语境** ✓ ⇒ ★ 那条路的 Data **`ILocalCurvePatternFeatureData` 带 `AccessSelections`** ✗（逐文件核过）⇒ **事实 47 一挡就到不了建成** ✓ ★ 旁证：★ **同族的 `ILocalSketchPatternFeatureData` 也带** ✗ —— ★ 即这一族的 Data 全都带 ✓ ★⚠ **本项与「曲线驱动阵列」同时经历过一次错误的翻案** ✓　（★ 自动台账原判：可做）
· 该关键词命中的 CHM **示例页**：**0**
  · `[swapi] IAssemblyDoc::DissolveComponentPattern` `System.bool DissolveComponentPattern()` 
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IAssemblyDoc~DissolveComponentPattern.html`  

## 装配 · SpeedPak ⇒ **可做**

· 初判：★★ **人工终判**：★ `IAssemblyDoc::CreateSpeedPak(int, …)` · `SetSpeedPakConfigurations` · `UpdateSpeedPak`（**参数式、无 ACL**）· 读回 `IsSpeedPak` ✓
· 该关键词命中的 CHM **示例页**：**12**
  · `[swapi] IAssemblyDoc::CreateSpeedPak` `System.bool CreateSpeedPak( System.int SpeedPakType )` 
  · `[swapi] IAssemblyDoc::SetSpeedPakConfigurations` `System.bool SetSpeedPakConfigurations( System.int Config_opt, System.object Config_names )` 
  · `[swapi] IAssemblyDoc::SetSpeedPakToParent` `System.bool SetSpeedPakToParent()` 
  · `[swapi] IAssemblyDoc::UpdateSpeedPak` `System.bool UpdateSpeedPak()` 
  · `[swapi] IAssemblyDoc::UseSpeedPak` `System.bool UseSpeedPak()` 
  · `[swapi] IComponent2::IsSpeedPak` `System.bool IsSpeedPak {get;}` 
  · …（共 21 个候选）

## 装配 · 序列 / 说明书（Assembly Visualization） ⇒ **不做**

· 初判：★★ **人工终判**：★ **四处零命中** ⇒ 官方无 API 入口（铁律 5）· ★ CHM 的 `Sequence` 只命中 **BOM 序号**与**族表序号**（与装配序列无关）　（★ 自动台账原判：疑无入口）
· 该关键词命中的 CHM **示例页**：**0**

## 装配 · 装配体性能分析 ⇒ **不做**

· 初判：★★ **人工终判**：★ **四处零命中** ⇒ 官方无 API 入口（铁律 5）· ★ CHM 的 `Performance` 只命中枚举 `swPerformanceFeedback_e` / `swSearchIndexingPerformance_e`（**不是分析功能**）　（★ 自动台账原判：疑无入口）
· 该关键词命中的 CHM **示例页**：**0**

## 评估 · 截面属性 ⇒ **可做**

· 初判：★★ **人工终判**：★ `IModelDocExtension::GetSectionProperties2`（System.object 返回、**无 ACL**）✓
· 该关键词命中的 CHM **示例页**：**0**
  · `[swapi] IModelDocExtension::GetSectionProperties` `System.object GetSectionProperties( System.object Sections )` 
  · `[swapi] IModelDocExtension::GetSectionProperties2` `System.object GetSectionProperties2( System.object Sections )` 
  · `[swapi] IModelDocExtension::IGetSectionProperties` `System.double IGetSectionProperties( System.int Count, ref System.object Sections )` 
  · `[swapi] IModelDocExtension::IGetSectionProperties2` `System.double IGetSectionProperties2( System.int Count, ref System.object Sections )` 
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IModelDocExtension~GetSectionProperties.html`  
  · `[chm-api] (CHM)::SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IModelDocExtension~GetSectionProperties2.html`  
  · …（共 8 个候选）

## 其他 · PDM ⇒ **不做**

· 初判：★★ **人工终判**：★ 自动台账只有 1 个候选 ⇒ ★ **需真机确认本机有没有装 PDM**（★ 不装不改系统层）✓　（★ 自动台账原判：可做）
· 该关键词命中的 CHM **示例页**：**0**
  · `[swapi] IApplication::PDMDocManager` `PDMDocManager PDMDocManager {get;}` 

