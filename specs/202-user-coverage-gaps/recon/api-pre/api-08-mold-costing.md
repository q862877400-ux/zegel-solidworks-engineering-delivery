# api-08 · 模具域 + Costing 域 + 评估（Measure / Quality）· 官方契约抄录

> 抄录员：契约抄录。本文件**只写亲手读到的原文**，每条给「文件名 + 可搜索的原文片段」，不给行号、不给建议、不下结论。
> 离线来源：`C:\swapi\types\<接口>\<成员>.md`（签名）· `C:\swapi\enums\*.md`（枚举）· `C:\swapi\examples\*.md`（官方例子的调用序）·
> `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\`（CHM 解包页）。

---

## 0. 范围核对：两处「查不到」必须先说清楚

| 派工里写的路径 | 本机实际情况（`Get-ChildItem C:\swapi\types\` 实读） |
| --- | --- |
| `C:\swapi\types\IMold*` | **查不到** —— 566 个类型目录里**没有任何**以 `IMold` 开头的目录；模具成员不在独立接口里 |
| `C:\swapi\types\ICosting*` | **查不到** —— 没有任何 `ICosting*` / `ICost*` 目录；`Get-ChildItem C:\swapi -Recurse -Filter *.md \| Where Name -match 'CostManager\|CostAnalysis\|CostBody\|CostPart\|CostFeature'` 结果**为空** |
| `C:\swapi\types\IMeasure` | **存在**，32 个成员 |
| `C:\swapi\types\IMassProperty*` | **存在**：`IMassProperty2`（18 个成员）· `IMassPropertyOverrideOptions`（13 个成员） |

⇒ 模具域实际落在 6 个 `category: Feature Interfaces/Mold Tools` 的接口
（`IPartingLineFeatureData` / `IPartingSurfaceFeatureData` / `IShutOffSurfaceFeatureData` /
`ICavityFeatureData` / `ICoreFeatureData` / `IToolingSplitFeatureData`）+ `IFeatureManager` 的 6 个模具方法 +
`IModelDoc2::MoldDraftAnalysis` + `IAssemblyDoc::InsertCavity..4`。
Costing 域本机**只查得到入口** `IModelDocExtension::GetCostingManager`，其返回类型 `ICostManager` 的**全部成员在本机两套离线源里都查不到**
（CHM 解包目录里 `*sldcostingapi*` 文件数 = **0**）。

`IDraftFeatureData2` 的 frontmatter 是 `category: Feature Interfaces/Others`（实测），**不在** Mold Tools 分类里 ⇒ 未纳入本文件的成员抄录。

---

# A 组 · `IFeatureManager` 模具方法（6 个）

## A1 `IFeatureManager::InsertMoldPartingLine`

- **签名（1 个参数）**：`Feature InsertMoldPartingLine( System.bool BFlipDir )`
  （源文件：`C:\swapi\types\IFeatureManager\InsertMoldPartingLine.md`，原文片段 `**Signature**: \`Feature InsertMoldPartingLine( System.bool BFlipDir )\``）
- **## Remarks（逐字）**：
  > "Before calling this method, you must select the direction of pull and the edges for the parting line by calling [[IModelDocExtension::SelectByID2]] with the following Marks:"
  > "Selection / Mark / Direction of pull / 1 / Parting line edges / 4"

  （CHM 同源：`…SWhelp\sldworksapi\SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~InsertMoldPartingLine.html`
  的 Remarks 段逐字为 "Before calling this method, you must select the direction of pull and the edges for the parting line by calling IModelDocExtension::SelectByID2 &nbsp;with the following Marks: Selection Mark Direction of pull 1 Parting line edges 4"；
  同页 Availability 写 "SOLIDWORKS 2004 FCS, Revision Number 12.0"）
- **官方例子的调用序**：**查不到** —— `InsertMoldPartingLine.md` 全文**没有 `## Examples` 段**；`C:\swapi\examples\` 里与分型线相关的只有
  `Get_and_Set_Parting_Line_Feature_Data_Example_CSharp.md` / `_VBNET` / `_VB` 与 `Set_Split_Faces_Option_for_Parting_Line_Example_VB.md`，这四个例子都**不从建模入口起手**。
- **枚举**：签名里无枚举参数（唯一形参是 `System.bool`）。
- **废弃链**：该成员**无 Obsolete 标记**（文件首行为 "Inserts a mold parting line feature."）。
- **前置一句话**：调用前必须先用 `SelectByID2` 按 mark 选好——拔模方向实体 mark=**1**、分型线边 mark=**4**。
- **配方一句话**：选方向(mark=1)+选分型线边(mark=4) → `InsertMoldPartingLine(False)` → 得 `IFeature`。

## A2 `IFeatureManager::InsertMoldPartingSurface`

- **签名（8 个参数）**：`Feature InsertMoldPartingSurface( System.int Radiate, System.bool ReverseAlignment, System.bool ReverseOffset, System.double OffsetDistance, System.double Angle, System.int Smooth, System.double SmoothDistance, System.bool Knit )`
  （源文件 `C:\swapi\types\IFeatureManager\InsertMoldPartingSurface.md`，原文片段 `**Signature**: \`Feature InsertMoldPartingSurface( System.int Radiate, … )\``）
- **## Remarks（逐字）**：
  > "f a parting line feature does not yet exist in the model, you must first select the direction of pull and the edges for the parting line using [[IModelDocExtension::SelectByID2]]. For example, a face (direction of pull) has a mark of 1 and edges (parting lines) a mark of 4."

  ⚠ 官方原文首字母缺字（"f a parting line feature"），此处逐字抄录，未改。
  ⚠ 参数说明里 `OffsetDistance` 的官方描述是**复制粘贴错误**，逐字为 "True to reverse offset direction, false to not"。
- **官方例子的调用序**：**查不到** —— 该文件**没有 `## Examples` 段**；仅有 `Get_and_Set_Parting_Surface_Feature_Data_Example_CSharp.md` 等 3 个"取改特征数据"例子。
- **枚举**（来自 `C:\swapi\enums\`）：
  - `swPartingSurfaceMoldParmType_e`（形参 `Radiate` 的类型）：`swPartingSurfaceMoldParmTangent = 0` / `swPartingSurfaceMoldParmNormal = 1` / `swPartingSurfaceMoldParmPerpendicular = 4`
  - `swPartingSurfaceSmoothingType_e`（形参 `Smooth` 的类型）：`swPartingSurfaceSharp = 1` / `swPartingSurfaceSmooth = 2`
  - 参数可用性（官方逐字）：`ReverseAlignment` "only available when radiate set to swPartingSurfaceMoldParmNormal and a parting line does not yet exist"；`Angle` "only available when radiate set to either swPartingSurfaceMoldParmTangent or swPartingSurfaceMoldParmNormal"；`SmoothDistance` "only available when smooth set to swPartingSurfaceSmooth"
- **废弃链**：**无 Obsolete 标记**。
- **前置一句话**：模型里还没有分型线特征时，调用前必须先用 `SelectByID2` 选拔模方向面（mark=1）与分型线边（mark=4）。
- **配方一句话**：`InsertMoldPartingSurface(Radiate=枚举值, ReverseAlignment, ReverseOffset, OffsetDistance, Angle, Smooth=枚举值, SmoothDistance, Knit)` → 得 `IFeature`。

## A3 `IFeatureManager::InsertMoldShutOffSurface`

- **签名（0 个参数）**：`Feature InsertMoldShutOffSurface()`
  （源文件 `C:\swapi\types\IFeatureManager\InsertMoldShutOffSurface.md`，原文片段 `**Signature**: \`Feature InsertMoldShutOffSurface()\``）
- **## Remarks**：**查不到** —— 该文件**没有 `## Remarks` 段**（CHM 同源页 `…IFeatureManager~InsertMoldShutOffSurface.html` 的 Remarks 段同样为空，只有 See Also 与 Availability "SOLIDWORKS 2004 FCS, Revision Number 12.0"）。
- **官方例子的调用序**：**查不到** —— 无 `## Examples` 段，`C:\swapi\examples\` 无 shut-off / 封油面 例子。
- **枚举**：无。
- **废弃链**：**无 Obsolete 标记**。
- **前置一句话**：**查不到** —— 官方在该成员上没写任何前置。
- **配方一句话**：无参调用 `InsertMoldShutOffSurface()` → 得 `IFeature`。

## A4 `IFeatureManager::InsertMoldCoreCavitySolids`

- **签名（4 个参数）**：`Feature InsertMoldCoreCavitySolids( System.double Dist1, System.double Dist2, System.bool Setback, System.double Angle )`
- **## Remarks（逐字）**：
  > "To use this method:
  > - The Parting Line feature must exist.
  > - The parting surface must be generated.
  > - The part must be separated into core and cavity (sheet bodies).
  > - A sketch describing the outline of the mold block must exist. The sketch must be perpendicular to the pull direction. Usually, the sketch is a rectangle that includes the part (core and cavity).
  > The location of the sketch plane specifies the parting plane in the setback surface option.
  > - Without the setback surface option, the parting surface must extend beyond the block sketch so that the parting surface is cut off by the block.
  > - With the setback surface option, the parting surface should be included within the block sketch. The parting plane (sketch plane) cannot intersect with the parting surface. Therefore, the parting plane must be either higher or lower than the parting surface. From the parting surface, a set of ruled surfaces is generated to be trimmed by the parting plane."
- **官方例子的调用序**：**查不到** —— 无 `## Examples` 段，`C:\swapi\examples\` 无此成员例子。
- **枚举**：无（4 个形参全是 `System.double` / `System.bool`）。
- **废弃链**：**无 Obsolete 标记**。
- **前置一句话**：分型线特征必须已存在、分型面必须已生成、零件必须已被分成 core 与 cavity 两个 sheet body、并须有一个垂直于拔模方向的模具块轮廓草图。
- **配方一句话**：`InsertMoldCoreCavitySolids(Dist1, Dist2, Setback, Angle)` → 得 `IFeature`。

## A5 `IFeatureManager::MoldUndercutDetect`

- **签名（6 个参数）**：`void MoldUndercutDetect( System.int ColUndercut, System.int ColBase, System.bool BCoordInput, System.double Dx, System.double Dy, System.double Dz )`
- **## Remarks**：**查不到** —— 文件首行即 "Obsolete. Superseded by [[IFeatureManager::MoldUndercutDetect2]]."；6 个形参的参数说明**逐字全部是 "No description"**，文件无 `## Remarks` 段。
- **官方例子的调用序**：**查不到**（无 `## Examples` 段）。
- **枚举**：无。
- **废弃链**：**有 Obsolete**，官方逐字点名后继 —— "Obsolete. Superseded by [[IFeatureManager::MoldUndercutDetect2]]."
- **前置一句话**：**查不到**（官方对这 6 个形参没有任何说明）。
- **配方一句话**：**查不到** —— 官方已把它标为 Obsolete 且未给替代配方，后继是 `MoldUndercutDetect2`。

## A6 `IFeatureManager::MoldUndercutDetect2`

- **签名（9 个参数）**：`void MoldUndercutDetect2( System.int ColUndercut1, System.int ColUndercut2, System.int ColOccluded, System.int ColStraddle, System.int ColBase, System.bool BCoordInput, System.double Dx, System.double Dy, System.double Dz )`
- **## Remarks**：**查不到** —— 文件**没有 `## Remarks` 段**；但 9 个形参逐字说明里带语义：
  `ColUndercut1` "Value (COLORREF type) that specifies the color for the faces invisible from one direction that form an undercut" ·
  `ColUndercut2` "…invisible from a second direction that form an undercut" ·
  `ColOccluded` "…invisible from both directions that form an undercut" ·
  `ColStraddle` "…faces with draft in both directions that form an undercut" ·
  `ColBase` "…faces that do not form undercuts; that is, all faces except the undercut faces" ·
  `BCoordInput` "True to enable coordinate input to control the direction of pull, false to not" ·
  `Dx`/`Dy`/`Dz` "x/y/z coordinate to control the direction of pull"
- **官方例子的调用序**：**查不到**（无 `## Examples` 段）。
- **枚举**：无（形参全是 `int` / `bool` / `double`）。
- **废弃链**：**无 Obsolete 标记**（首行 "Detects trapped, also called undercut, areas in a model that cannot be ejected from the mold."）。
- **前置一句话**：**查不到** —— 官方只说 `BCoordInput=true` 时用 `Dx/Dy/Dz` 控制拔模方向，没写必须先选什么。
- **配方一句话**：`MoldUndercutDetect2(5 个颜色, BCoordInput, Dx, Dy, Dz)`；官方例子未见，本仓无实参配方可抄。

---

# B 组 · 拔模分析（1 个）

## B1 `IModelDoc2::MoldDraftAnalysis`

- **签名（4 个参数）**：`void MoldDraftAnalysis( System.double Angle, System.int Options, System.object Colors, System.int Shows )`
  （源文件 `C:\swapi\types\IModelDoc2\MoldDraftAnalysis.md`）
- **## Remarks**：**查不到** —— 该文件与 CHM 页 `…IModelDoc2~MoldDraftAnalysis.html` **都没有 `## Remarks` 段**。
- **官方例子的调用序**：**查不到**（无 `## Examples` 段）。
- **枚举**（来自 `C:\swapi\enums\`）：
  - `swDraftAnalysisOptions_e`（`Options`，官方注明是 Bitmask）：`swDraftAnalysisFlipDir = 1 (0x1)` / `swDraftAnalysisFindSteep = 2 (0x2)`
  - `swDraftAnalysisShow_e`（`Shows`，Bitmask）：`swDraftAnalysisShowPositive = 1 (0x1)` / `swDraftAnalysisShowNegative = 2 (0x2)` / `swDraftAnalysisShowDraftRequired = 4 (0x4)` / `swDraftAnalysisShowStraddle = 8 (0x8)` / `swDraftAnalysisShowPositiveSteep = 16 (0x10)` / `swDraftAnalysisShowNegativeSteep = 32 (0x20)` / `swDraftAnalysisShowSurface = 64 (0x40)`
  - `Colors` 是 4 个颜色的数组，官方逐字："Array of 4 colors (positive draft, negative draft, no draft, straddled faces)"。
  - ⚠ `swDraftAnalysisFaceType_e`（`swDraftAnalysisFaceTypeNegative = 1` / `NoDraft = 2` / `Positive = 0` / `Straddle = 3`）在本仓 `C:\swapi\enums\` 存在，但**本成员签名里没有引用它** ⇒ 未作为本成员枚举抄。
- **废弃链**：**无 Obsolete 标记**（首行 "Performs a mold draft analysis."）。
- **前置一句话**：**查不到** —— 官方对该成员只写了 4 个形参的用途，没有任何"调用前必须…"。
- **配方一句话**：`MoldDraftAnalysis(参考拔模角, swDraftAnalysisOptions_e 位掩码, 长度 4 的颜色数组, swDraftAnalysisShow_e 位掩码)`；官方无例子可抄实参。

---

# C 组 · 型腔特征（`IAssemblyDoc`，4 个）

## C1 `IAssemblyDoc::InsertCavity`

- **签名（0 个参数）**：`void InsertCavity()`
- **## Remarks**：**查不到**（无 `## Remarks` 段）。
- **官方例子的调用序**：**查不到**（无 `## Examples` 段）。
- **枚举**：无。
- **废弃链**：**有 Obsolete**，逐字 "Obsolete. Superseded by [[IAssemblyDoc::InsertCavity4]]."（CHM 页同文："Obsolete. Superseded by IAssemblyDoc::InsertCavity4 ."）。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**（已废弃，官方点名后继 `InsertCavity4`）。

## C2 `IAssemblyDoc::InsertCavity2`

- **签名（2 个参数）**：`void InsertCavity2( System.double ScaleFactor, System.int ScaleType )`
- **## Remarks**：**查不到**（无 `## Remarks` 段）。
- **官方例子的调用序**：**查不到**（无 `## Examples` 段）。
- **枚举**：形参 `ScaleType` 的类型官方未在此文件点名（**查不到**）；同族 `ICavityFeatureData::ScaleType` 的类型是 `swCavityScaleType_e`（`swAboutCentroid = 0` / `swAboutOrigin = 1` / `swAboutMoldBaseOrigin = 2` / `swAboutCoordinateSystem = 3`）。
- **废弃链**：**有 Obsolete**，逐字 "Obsolete. Superseded by [[IAssemblyDoc::InsertCavity4]]."
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**（已废弃，后继 `InsertCavity4`）。

## C3 `IAssemblyDoc::InsertCavity3`

- **签名（3 个参数）**：`void InsertCavity3( System.double ScaleFactor, System.int ScaleType, System.int KeepPieceIndex )`
- **## Remarks**：**查不到**（无 `## Remarks` 段）。
- **官方例子的调用序**：**查不到**（无 `## Examples` 段）。
- **枚举**：同上，`ScaleType` 类型**查不到**（本文件未点名）。
- **废弃链**：**有 Obsolete**，逐字 "Obsolete. Superseded by [[IAssemblyDoc::InsertCavity4]]."
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**（已废弃，后继 `InsertCavity4`）。

## C4 `IAssemblyDoc::InsertCavity4`

- **签名（6 个参数）**：`void InsertCavity4( System.double ScaleFactor_x, System.double ScaleFactor_y, System.double ScaleFactor_z, System.bool IsUniform, System.int ScaleType, System.int KeepPieceIndex )`
- **## Remarks（逐字）**：
  > "This operation is performed in the context of an assembly document. The component being edited in the context of the assembly receives the new cavity feature."
  > "Set the scaleFactor argument as appropriate for your casting material. The scaling factor is expressed as a percentage (+/- 20%) of the size of the cavity part. Pass it in as a value within the range of -20 to +20."
  > "SOLIDWORKS uses the following formula to determine the size of the cavity:"
  > "cavitysize = partsize * (1 + scaleFactor/100)"
  > "When there is ambiguity in the result of a cut, SOLIDWORKS uses KeepPieceIndex to determine which result to use. You can set this parameter to -1 if there is no ambiguity; otherwise, you should use the index of the result, in the range between 0 and 1 less than the possible number of outcomes."
- **官方例子的调用序**：**查不到**（无 `## Examples` 段）。CHM 里与之相关的只有"手工操作"说明
  （`Create_and_Modify_Cavity_Feature_Example_CSharp.md` 的 Preconditions 逐字含 "click Cavity on the Mold Tools toolbar."）。
- **枚举**：`ScaleType` 的类型**查不到**（本文件未点名）。
- **废弃链**：**无 Obsolete 标记**。
- **前置一句话**：必须在**装配体文档**的编辑上下文里执行，缩放因子按百分比传（-20 ~ +20）。
- **配方一句话**：`InsertCavity4(Sx, Sy, Sz, IsUniform, ScaleType, KeepPieceIndex)`，`cavitysize = partsize * (1 + scaleFactor/100)`。

---

# D 组 · `IPartingLineFeatureData`（23 个成员）

接口 frontmatter：`category: Feature Interfaces/Mold Tools`。

## D1 `AccessSelections`

- **签名（2 个参数）**：`System.bool AccessSelections( ModelDoc2 TopDoc, Component2 Component )`
- **## Remarks（逐字）**：
  > "**To modify a feature in a...** **Then...**
  > Part | - TopDoc argument is the [[IModelDoc2]] for the part | - Component argument is Nothing or null
  > Assembly | - TopDoc is the IModelDoc2 object for the assembly | - Component argument is the [[IComponent2]] object in which the feature is to be modified
  > This method puts the model into a rollback state to allow access to the selections that define this feature. You must use either of the following methods to restore the rollback state:
  > - [[IFeature::ModifyDefinition]] or [[IFeature::IModifyDefinition2]] if you modified the feature
  > - [[IPartingLineFeatureData::ReleaseSelectionAccess]] if you did not"
- **官方例子的调用序**（逐字，`Set_Split_Faces_Option_for_Parting_Line_Example_VB.md`）：
  > `Set swPartingLine = swFeat.GetDefinition`
  > `bRet = swPartingLine.AccessSelections(swModel, Nothing): Debug.Assert bRet`
  > `swPartingLine.SplitFaces = True`
  > `swPartingLine.CoreCavitySplit = True`
  > `swPartingLine.SplitFacesOption = swSplitFacesAtSpecifiedAngle`
  > `bRet = swFeat.ModifyDefinition(swPartingLine, swModel, Nothing): Debug.Assert bRet`
- **枚举**：无。
- **废弃链**：无 Obsolete。
- **前置一句话**：取到 `IFeature` 后先 `GetDefinition` 得 `PartingLineFeatureData`，再 `AccessSelections(swModel, Nothing)` 进入回滚态，改完必须 `ModifyDefinition` 或 `ReleaseSelectionAccess` 收尾。
- **配方一句话**：`GetDefinition()` → `AccessSelections(TopDoc, Nothing|Component2)` → 改属性 → `IFeature::ModifyDefinition`。

## D2 `Angle`

- **签名**：`System.double Angle {get; set;}`（属性，0 参数）
- **## Remarks**：**查不到**（无 `## Remarks` 段）。
- **官方例子**：`Get_and_Set_Parting_Line_Feature_Data_Example_CSharp.md` 逐字 `Debug.Print("    Draft angle: " + swPartingLineFeatureData.Angle);`
- **枚举**：无。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：在 `AccessSelections` 回滚态内读 `Angle`（官方例子把它与 `Status()` 一起打印）。

## D3 `CoreCavitySplit`

- **签名**：`System.bool CoreCavitySplit {get; set;}`
- **## Remarks**：**查不到**。
- **官方例子**（`Set_Split_Faces_Option_for_Parting_Line_Example_VB.md` 逐字）：
  > `Debug.Print " Core/cavity split = " & swPartingLine.CoreCavitySplit`
  > `swPartingLine.CoreCavitySplit = True`
- **枚举**：无。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：`AccessSelections` 后置 `CoreCavitySplit = True`，再 `ModifyDefinition`。

## D4 `DraftAnalysis`

- **签名（1 个参数）**：`System.bool DraftAnalysis( System.double Angle )`
- **## Remarks（逐字）**：
  > "If you want a different pull direction, then use [[IPartingLineFeatureData::PullDirectionBase]] to change the direction. Once this method is called, only the information for different faces (negative, positive, and so on) is generated."
- **官方例子**：**查不到**（该文件无 `## Examples` 段）。
- **枚举**：无。
- **废弃链**：无 Obsolete。
- **前置一句话**：要换拔模方向得先用 `PullDirectionBase` 改方向；本方法一旦调用就只生成"按正/负拔模分类的面"信息。
- **配方一句话**：`DraftAnalysis(Angle)` 返回 bool；调用后读 `GetFacesByType*` 系列。

## D5 `GetEntitiesToSplit`

- **签名（1 个 out 形参）**：`System.object GetEntitiesToSplit( out System.object TypeArr )`
- **## Remarks（逐字）**：
  > "The resulting edges are added to the parting line feature."
  > "When two vertices are specified, then an edge is created between them for the parting line feature."
  > "See [Accessing Selections that Define Features](<../../docs/Programming with the SOLIDWORKS API/Selections that Define Features.md>) for additional details on using this method."
- **官方例子**：**查不到**（无 `## Examples` 段）。
- **枚举**：`out System.object TypeArr` 的取值类型官方**未在本文件点名** ⇒ **查不到**。
- **废弃链**：无 Obsolete。
- **前置一句话**：必须先在 `AccessSelections` 回滚态内调用；给两个顶点时会在两者之间为分型线特征生成一条边。
- **配方一句话**：`GetEntitiesToSplit(out TypeArr)` 取"要分割的实体"，结果边会被加进分型线特征。

## D6 `GetEntitiesToSplitCount`

- **签名（0 个参数）**：`System.int GetEntitiesToSplitCount()`
- **## Remarks（逐字）**："Call this method before calling [[IPartingLineFeatureData::IGetEntitiesToSplit]]."
- **官方例子**（`Get_and_Set_Parting_Line_Feature_Data_Example_CSharp.md` 逐字）：
  > `Debug.Print("    Number of entities to split: " + swPartingLineFeatureData.GetEntitiesToSplitCount());`
- **枚举**：无。
- **废弃链**：无 Obsolete。
- **前置一句话**：必须先于 `IGetEntitiesToSplit` 调用以取数组长度。
- **配方一句话**：`Count = GetEntitiesToSplitCount()` → `IGetEntitiesToSplit(Count, out TypeArr)`。

## D7 `GetFacesByType`

- **签名（1 个参数）**：`System.object GetFacesByType( System.int Type )`
- **## Remarks（逐字）**："See [Accessing Selections that Define Features](…) for additional details on using this method."
- **官方例子**：**查不到**（无 `## Examples` 段）。
- **枚举**：`Type` 的枚举官方**未在本文件点名** ⇒ **查不到**（同族 `IPartingLineFeatureData::DraftAnalysis` 提到 "negative, positive, and so on"，但没给枚举名）。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**（只说了参 `Type`，没写必须先做什么）。
- **配方一句话**：先 `GetFacesByTypeCount(Type)` 取个数 → 再 `IGetFacesByType(Type, Count)`（见 D9 的官方逐字前置）。

## D8 `GetFacesByTypeCount`

- **签名（1 个参数）**：`System.int GetFacesByTypeCount( System.int Type )`
- **## Remarks（逐字）**："Call this method before calling [[IPartingLineFeatureData::IGetFacesbyType]]."
- **官方例子**：**查不到**。
- **枚举**：同 D7，**查不到**。
- **废弃链**：无 Obsolete。
- **前置一句话**：必须先于 `IGetFacesByType` 调用。
- **配方一句话**：`GetFacesByTypeCount(Type)` → 把返回值当 `Count` 传给 `IGetFacesByType`。

## D9 `IGetFacesByType`

- **签名（2 个参数）**：`Face2 IGetFacesByType( System.int Type, System.int Count )`
- **## Remarks（逐字）**：
  > "Call [[IPartingLineFeatureData::GetFacesByTypeCount]] before calling this method."
  > "See [Accessing Selections that Define Features](…) for additional details on using this method."
- **官方例子**：**查不到**。
- **枚举**：同 D7，**查不到**。
- **废弃链**：无 Obsolete。
- **前置一句话**：必须先调 `GetFacesByTypeCount(Type)` 拿 `Count`。
- **配方一句话**：`Faces = IGetFacesByType(Type, Count)`。

## D10 `GetPartingLinesCount`

- **签名（0 个参数）**：`System.int GetPartingLinesCount()`
- **## Remarks（逐字）**："Call this method before calling [[IPartingLineFeatureData::IGetPartingLines]]."
- **官方例子**：**查不到**（无 `## Examples` 段）。
- **枚举**：无。
- **废弃链**：无 Obsolete。
- **前置一句话**：必须先于 `IGetPartingLines` 调用以取数组长度。
- **配方一句话**：`Count = GetPartingLinesCount()` → `IGetPartingLines(Count)`。

## D11 `IGetEntitiesToSplit`

- **签名（2 个参数）**：`System.object IGetEntitiesToSplit( System.int Count, out System.int TypeArr )`
- **## Remarks（逐字）**：
  > "The resulting edges are added to the parting line feature."
  > "Call [[IPartingLineFeatureData::GetEntitiesToSplitCount]] before this method."
  > "When two vertices are specified, then an edge is created between them for the parting line feature."
  > "See [Accessing Selections that Define Features](…) for additional details on using this method."
- **官方例子**：**查不到**。
- **枚举**：`out System.int TypeArr` 的枚举**查不到**。
- **废弃链**：无 Obsolete。
- **前置一句话**：必须先调 `GetEntitiesToSplitCount()` 拿 `Count`。
- **配方一句话**：`IGetEntitiesToSplit(Count, out TypeArr)` 取数组。

## D12 `IGetPartingLines`

- **签名（1 个参数）**：`Edge IGetPartingLines( System.int Count )`
- **## Remarks（逐字）**：
  > "Call [[IPartingLineFeatureData::GetPartingLinesCount]] before calling this method."
  > "See [Accessing Selections that Define Features](…) for additional details on using this method."
- **官方例子**：**查不到**。
- **枚举**：无。
- **废弃链**：无 Obsolete。
- **前置一句话**：必须先调 `GetPartingLinesCount()` 拿 `Count`。
- **配方一句话**：`IGetPartingLines(Count)` 取分型线边数组。

## D13 `ISetEntitiesToSplit`

- **签名（2 个参数）**：`void ISetEntitiesToSplit( System.int Count, ref System.object EntIn )`
- **## Remarks（逐字）**：
  > "If sketch segments and vertices are specified, then a pair of vertices appear together; for example, segment1, vtx11, vtx12, segment2, vtx21, vtx22, vtx31, vtx32, and so on."
  > "See [Accessing Selections that Define Features](…) for additional details on using this method."
- **官方例子**：**查不到**。
- **枚举**：`EntIn` 的元素类型**查不到**（与 `GetEntitiesToSplit` 的 `TypeArr` 对应）。
- **废弃链**：无 Obsolete。
- **前置一句话**：若混用草图线段与顶点，**顶点必须成对出现**（segment1, vtx11, vtx12, segment2, …）。
- **配方一句话**：`ISetEntitiesToSplit(Count, ref EntIn)`；写侧对应属性为 D21 `SetEntitiesToSplit`。

## D14 `ISetPartingLines`

- **签名（2 个参数）**：`void ISetPartingLines( System.int Count, ref Edge EntIn )`
- **## Remarks（逐字）**："See [Accessing Selections that Define Features](…) for additional details on using this method."
- **官方例子**：**查不到**。
- **枚举**：无。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**（除"在回滚态内"之外没写别的）。
- **配方一句话**：`ISetPartingLines(Count, ref EntIn)`，`Count` 与 `GetPartingLinesCount()` 一致。

## D15 `PartingLines`

- **签名**：`System.object PartingLines {get; set;}`
- **## Remarks（逐字）**："See [Accessing Selections that Define Features](…) for additional details on using this method."
- **官方例子**：**查不到**（无 `## Examples` 段）。
- **枚举**：无。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：用属性读写分型线边数组（数组侧等价物为 `IGetPartingLines` / `ISetPartingLines`）。

## D16 `PullDirection`

- **签名**：`System.bool PullDirection {get; set;}`
- **## Remarks**：**查不到**。
- **官方例子**（`Get_and_Set_Parting_Line_Feature_Data_Example_CSharp.md` 逐字）：
  > `Debug.Print("    Pull direction before reversing: " + swPartingLineFeatureData.PullDirection);`
  > `if (swPartingLineFeatureData.PullDirection) { swPartingLineFeatureData.PullDirection = false; } else { swPartingLineFeatureData.PullDirection = true; }`
- **枚举**：无。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：`PullDirection` 读后取反再写回（官方例子的动作序列）。

## D17 `PullDirectionBase`

- **签名**：`System.object PullDirectionBase {get; set;}`
- **## Remarks**：**查不到**（无 `## Remarks` 段）。
- **官方例子**：**查不到**。
- **枚举**：无。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**（但 `DraftAnalysis` 的 Remarks 说它是"换拔模方向"的入口）。
- **配方一句话**：**查不到** —— 官方无例子、无实参说明。

## D18 `PullDirectionType`

- **签名**：`System.int PullDirectionType {get;}`（只读，0 参数）
- **## Remarks**：**查不到**。
- **官方例子**（`Get_and_Set_Parting_Line_Feature_Data_Example_CSharp.md` 逐字）：
  > `Debug.Print("    Pull direction type as defined by swSelectType_e: " + swPartingLineFeatureData.PullDirectionType);`
- **枚举**：官方例子点名的枚举是 **`swSelectType_e`**（`C:\swapi\enums\swSelectType_e.md` 存在）；签名本身没有枚举类型标注。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：只读取，官方例子直接打印。

## D19 `ReleaseSelectionAccess`

- **签名（0 个参数）**：`void ReleaseSelectionAccess()`
- **## Remarks（逐字）**：
  > "[[IPartingLineFeatureData::AccessSelections]] puts the model in a rollback state to allow access to the selections that define the parting line feature."
  > "Use this method to restore the rollback state if you did not modify the feature, or use [[IFeature::ModifyDefinition]] or [[IFeature::IModifyDefinition2]] if you did modify the feature."
- **官方例子**：**查不到**（无 `## Examples` 段；`Get_and_Set_Parting_Line_Feature_Data_Example_CSharp.md` 走的是 `ModifyDefinition` 分支）。
- **枚举**：无。
- **废弃链**：无 Obsolete。
- **前置一句话**：只有"没改特征"时才能用它退出回滚态；改过就必须走 `ModifyDefinition`。
- **配方一句话**：`ReleaseSelectionAccess()` 收尾（或改用 `swFeature.ModifyDefinition(data, swModel, null)`）。

## D20 `SetEntitiesToSplit`

- **签名（1 个参数）**：`void SetEntitiesToSplit( System.object PVar )`
- **## Remarks（逐字）**：
  > "If sketch segments and vertices are specified, then a pair of vertices appear together; for example, segment1, vtx11, vtx12, segment2, vtx21, vtx22, vtx31, vtx32, and so on."
  > "See [Accessing Selections that Define Features](…) for additional details on using this method."
- **官方例子**：**查不到**。
- **枚举**：无。
- **废弃链**：无 Obsolete。
- **前置一句话**：顶点成对出现的规则同 D13。
- **配方一句话**：`SetEntitiesToSplit(PVar)`（IUnknown 变体入口；数组侧为 `ISetEntitiesToSplit`）。

## D21 `SplitFaces`

- **签名**：`System.bool SplitFaces {get; set;}`
- **## Remarks**：**查不到**。
- **官方例子**（`Set_Split_Faces_Option_for_Parting_Line_Example_VB.md` 逐字）：
  > `Debug.Print " Split faces = " & swPartingLine.SplitFaces`
  > `swPartingLine.SplitFaces = True`
- **枚举**：无（枚举在 `SplitFacesOption`）。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：`AccessSelections` 后 `SplitFaces = True`，再 `SplitFacesOption = swSplitFacesAtSpecifiedAngle`。

## D22 `SplitFacesOption`

- **签名**：`System.int SplitFacesOption {get; set;}`
- **## Remarks**：**查不到**。
- **官方例子**（`Get_and_Set_Parting_Line_Feature_Data_Example_CSharp.md` 逐字）：
  > `if (swPartingLineFeatureData.SplitFaces) { Debug.Print("    Split faces options as defined by swSplitFacesOption_e: " + swPartingLineFeatureData.SplitFacesOption); }`
- **枚举**：`swSplitFacesOption_e`（`C:\swapi\enums\swSplitFacesOption_e.md`）：
  `swSplitFacesAtPlusMinusDraftTransition = 0` / `swSplitFacesAtSpecifiedAngle = 1`
- **废弃链**：无 Obsolete。
- **前置一句话**：官方例子的读取写在 `if (SplitFaces)` 分支里（**官方例子如此，文档未写"必须先 SplitFaces=True"**）。
- **配方一句话**：`SplitFacesOption = swSplitFacesAtSpecifiedAngle`（VBA 例子实测值，见 D1 的调用序）。

## D23 `Status`

- **签名（0 个参数）**：`System.int Status()`
- **## Remarks（逐字）**："Call this method after specifying the settings and options for this feature to find out the status of the feature."
- **官方例子**（`Get_and_Set_Parting_Line_Feature_Data_Example_CSharp.md` 逐字）：
  > `Debug.Print("    Parting line status as defined by swPartingLineFeatureStatus_e: " + swPartingLineFeatureData.Status());`
- **枚举**：`swPartingLineFeatureStatus_e`（`C:\swapi\enums\swPartingLineFeatureStatus_e.md`，逐字）：
  `STATUS_MOLD_REDUNDANT_EDGES = 1`（"There are more than enough edges selected to form a parting line; remove any redundant edges or add edges to close gaps between disjoint edge chains"）·
  `STATUS_MOLD_PARTINGLINE_EDGES_OPEN = 2`（"Select edges that form a closed loop"）·
  `STATUS_MOLD_PARTINGLINE_SEPARABLE = 3`（"The parting line is complete; the mold can be separated into core and cavity"）·
  `STATUS_MOLD_PARTINGLINE_NON_SEPARABLE = 4`（"The parting line is complete, but the mold cannot be separated into core and cavity; you might need to create shut-off surfaces"）
- **废弃链**：无 Obsolete。
- **前置一句话**：必须在"设置完该特征的各项设置与选项之后"才调它。
- **配方一句话**：`AccessSelections` → 改设置 → `Status()` 读状态码（3 = 可分离，4 = 需封油面）。

---

# E 组 · `IPartingSurfaceFeatureData`（17 个成员）

## E1 `AccessSelections`

- **签名（2 个参数）**：`System.bool AccessSelections( ModelDoc2 TopDoc, Component2 Component )`
- **## Remarks（逐字）**：与 D1 同文，差异一处：末尾是 "[[IPartingSurfaceFeatureData::ReleaseSelectionAccess]] if you did not"；表格里 Part 行的 Component 描述同样是 "Component argument is Nothing or null"。
  （源文件 `C:\swapi\types\IPartingSurfaceFeatureData\AccessSelections.md`）
- **官方例子的调用序**（`Get_and_Set_Parting_Surface_Feature_Data_Example_CSharp.md` 逐字）：
  > `swFeature = (Feature)swSelectionMgr.GetSelectedObject6(1, -1);`
  > `swPartingSurfaceFeatureData = (PartingSurfaceFeatureData)swFeature.GetDefinition();`
  > `state = swPartingSurfaceFeatureData.AccessSelections(swModel, null);`
  > `swFeature.ModifyDefinition(swPartingSurfaceFeatureData, swModel, null);`
- **枚举**：无。
- **废弃链**：无 Obsolete。
- **前置一句话**：零件里 Component 传 `Nothing`/`null`；装配体里传要修改特征所在的 `IComponent2`。
- **配方一句话**：`GetDefinition()` → `AccessSelections(swModel, null)` → 改属性 → `ModifyDefinition`。

## E2 `GetPartingLinesCount`

- **签名（0 个参数）**：`System.int GetPartingLinesCount()`
- **## Remarks（逐字）**："Call this method before calling [[IPartingSurfaceFeatureData::IGetPartingLines]]."
- **官方例子**（`Get_and_Set_Parting_Surface_Feature_Data_Example_CSharp.md` 逐字）：
  > `Debug.Print("    Number of parting lines: " + swPartingSurfaceFeatureData.GetPartingLinesCount());`
- **枚举**：无。 **废弃链**：无 Obsolete。
- **前置一句话**：必须先于 `IGetPartingLines`。
- **配方一句话**：`Count = GetPartingLinesCount()` → `IGetPartingLines(Count)`。

## E3 `GetPartingLinesType`

- **签名（0 个参数）**：`System.int GetPartingLinesType()`
- **## Remarks**：**查不到**（无 `## Remarks` 段）。
- **官方例子**（逐字）：
  > `Debug.Print("    Parting line type (0 = parting line feature, 1 = edge): " + swPartingSurfaceFeatureData.GetPartingLinesType());`
- **枚举**：**查不到** —— 官方只给 "0 = parting line feature, 1 = edge" 的文字，未点名枚举。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：只读取并直接打印。

## E4 `IGetPartingLines`

- **签名（1 个参数）**：`System.object IGetPartingLines( System.int Count )`
- **## Remarks（逐字）**：
  > "Call [[IPartingSurfaceFeatureData::GetPartingLinesCount]] before calling this method to get the number of parting lines for this parting surface feature."
  > "See [Accessing Selections that Define Features](…) for additional details on using this method."
- **官方例子**：**查不到**。 **枚举**：无。 **废弃链**：无 Obsolete。
- **前置一句话**：必须先调 `GetPartingLinesCount()` 拿 `Count`。
- **配方一句话**：`IGetPartingLines(Count)`。

## E5 `ISetPartingLines`

- **签名（2 个参数）**：`void ISetPartingLines( System.int Count, ref System.object EntIn )`
- **## Remarks（逐字）**："See [Accessing Selections that Define Features](…) for additional details on using this method."
- **官方例子 / 枚举 / 废弃链**：**查不到 / 无 / 无 Obsolete**。
- **前置一句话**：**查不到**。
- **配方一句话**：`ISetPartingLines(Count, ref EntIn)`。

## E6 `Knit`

- **签名**：`System.bool Knit {get; set;}`
- **## Remarks**：**查不到**。
- **官方例子**（逐字）：`Debug.Print("    Knit all surfaces: " + swPartingSurfaceFeatureData.Knit);`
- **枚举**：无。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：读/写布尔（对应 `InsertMoldPartingSurface` 的第 8 个形参 `Knit`）。

## E7 `OffsetAngle`

- **签名**：`System.double OffsetAngle {get; set;}`
- **## Remarks（逐字）**："This property only applies if you set [[IPartingSurfaceFeatureData::PartingType]] to swPartingSurfaceMoldParmTangent or swPartingSurfceMoldParmNormal."
  ⚠ 官方原文里 `swPartingSurfceMoldParmNormal` 少了 "fa"（逐字抄录）。
- **官方例子**（逐字）：官方例子显式做了分支 —— `if (swPartingSurfaceFeatureData.PartingType == (int)swPartingSurfaceMoldParmType_e.swPartingSurfaceMoldParmPerpendicular) { Debug.Print("    Offset angle not available for this parting surface type."); } else { Debug.Print("    Offset angle: " + swPartingSurfaceFeatureData.OffsetAngle); }`
- **枚举**：`swPartingSurfaceMoldParmType_e`（`Tangent = 0` / `Normal = 1` / `Perpendicular = 4`）。
- **废弃链**：无 Obsolete。
- **前置一句话**：只有 `PartingType` 为 Tangent 或 Normal 时该属性才生效。
- **配方一句话**：按 `PartingType` 分支读 `OffsetAngle`（官方例子即此写法）。

## E8 `OffsetDistance`

- **签名**：`System.double OffsetDistance {get; set;}`
- **## Remarks**：**查不到**。
- **官方例子**（逐字）：`Debug.Print("    Distance this parting surface feature extends: " + swPartingSurfaceFeatureData.OffsetDistance);`
- **枚举**：无。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：只读取/写入（对应 `InsertMoldPartingSurface` 第 4 形参 `OffsetDistance`）。

## E9 `PartingLines`

- **签名**：`System.object PartingLines {get; set;}`
- **## Remarks（逐字）**："See [Accessing Selections that Define Features](…) for additional details on using this method."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：属性形式读写分型线数组（数组侧 `IGetPartingLines` / `ISetPartingLines`）。

## E10 `PartingType`

- **签名**：`System.int PartingType {get; set;}`
- **## Remarks（逐字）**："swPartingSurfaceMoldParmType_e.swPartingSurfaceMoldParmTangent is not available for some geometry."
- **官方例子**（逐字）：`Debug.Print("    Parting surface type as defined by swPartingSurfaceMoldParmType_e: " + swPartingSurfaceFeatureData.PartingType);`
- **枚举**：`swPartingSurfaceMoldParmType_e` = `swPartingSurfaceMoldParmTangent 0` / `swPartingSurfaceMoldParmNormal 1` / `swPartingSurfaceMoldParmPerpendicular 4`。
- **废弃链**：无 Obsolete。
- **前置一句话**：Tangent 类型对部分几何不可用（官方原话）。
- **配方一句话**：读出后与 `(int)swPartingSurfaceMoldParmType_e.swPartingSurfaceMoldParmPerpendicular` 比较以决定是否读 `OffsetAngle`。

## E11 `PullDirectionBase`

- **签名**：`System.object PullDirectionBase {get; set;}`
- **## Remarks（逐字）**："See [Accessing Selections that Define Features](…) for additional details on using this method."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到** —— 官方无例子。

## E12 `PullDirectionType`

- **签名**：`System.int PullDirectionType {get;}`
- **## Remarks / 官方例子 / 枚举**：**查不到**。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**。

## E13 `ReleaseSelectionAccess`

- **签名（0 个参数）**：`void ReleaseSelectionAccess()`
- **## Remarks（逐字）**：
  > "[[IPartingSurfaceFeatureData::AccessSelections]] puts the model in a rollback state to allow access to the selections that define the parting surface feature."
  > "Use this method to restore the rollback state if you did not modify the feature, or use [[IFeature::ModifyDefinition]] or [[IFeature::IModifyDefinition2]] if you did modify the feature."
- **官方例子**：**查不到**（官方例子走 `ModifyDefinition`）。 **枚举**：无。 **废弃链**：无 Obsolete。
- **前置一句话**：没改特征才用；改过必须 `ModifyDefinition`。
- **配方一句话**：`ReleaseSelectionAccess()`。

## E14 `ReverseAlignment`

- **签名**：`System.bool ReverseAlignment {get; set;}`
- **## Remarks**：**查不到**。
- **官方例子**（逐字）：
  > `if (swPartingSurfaceFeatureData.ReverseAlignment == true) { swPartingSurfaceFeatureData.ReverseAlignment = false; } else { swPartingSurfaceFeatureData.ReverseAlignment = true; }`
- **枚举**：无（可用性约束写在 `InsertMoldPartingSurface` 的形参说明里：仅当 radiate = `swPartingSurfaceMoldParmNormal` 且尚无分型线时可用）。
- **废弃链**：无 Obsolete。
- **前置一句话**：官方只把它约束在"radiate=Normal 且无分型线"的情形（写在 A2 的形参说明里，本成员页没写）。
- **配方一句话**：读布尔后取反写回（官方例子的动作序列）。

## E15 `ReverseOffsetDirection`

- **签名**：`System.bool ReverseOffsetDirection {get; set;}`
- **## Remarks / 官方例子 / 枚举**：**查不到**。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**。

## E16 `TransitionDistance`

- **签名**：`System.double TransitionDistance {get; set;}`
- **## Remarks（逐字）**："This property is only available when [[IPartingSurfaceFeatureData::TransitionType]] is set to swPartingSurfaceSmoothngType_e.swPartingSurfaceSmooth."
  ⚠ 官方原文枚举名拼作 `swPartingSurfaceSmoothngType_e`（少一个 i，逐字抄录）；`C:\swapi\enums\swPartingSurfaceSmoothingType_e.md` 里的正确名是 `swPartingSurfaceSmoothingType_e`。
- **官方例子 / 枚举**：**查不到 / `swPartingSurfaceSmooth = 2`、`swPartingSurfaceSharp = 1`**（`swPartingSurfaceSmoothingType_e`）。
- **废弃链**：无 Obsolete。
- **前置一句话**：只有 `TransitionType = swPartingSurfaceSmooth` 时该属性才可用。
- **配方一句话**：先置 `TransitionType`，再写 `TransitionDistance`。

## E17 `TransitionType`

- **签名**：`System.int TransitionType {get; set;}`
- **## Remarks**：**查不到**。
- **官方例子**（逐字）：`Debug.Print("    Transition between adjacent edges as defined by swPartingSurfaceSmoothingType_e: " + swPartingSurfaceFeatureData.TransitionType);`
- **枚举**：`swPartingSurfaceSmoothingType_e` = `swPartingSurfaceSharp = 1` / `swPartingSurfaceSmooth = 2`。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：写入枚举值（Sharp 或 Smooth），Smooth 时才可用 `TransitionDistance`。

---

# F 组 · `IShutOffSurfaceFeatureData`（16 个成员）

## F1 `AccessSelections`

- **签名（2 个参数）**：`System.bool AccessSelections( ModelDoc2 TopDoc, Component2 Component )`
- **## Remarks（逐字）**：与 D1/E1 同文，末尾是 "[[IShutOffSurfaceFeatureData::ReleaseSelectionAccess]] if you did not"；Part 行写 "Component argument is NULL"（本组用 NULL，另两组一处是 "Nothing or null"）。
- **官方例子**：**查不到**（该文件无 `## Examples` 段，`C:\swapi\examples\` 也无 shut-off 例子）。
- **枚举**：无。 **废弃链**：无 Obsolete。
- **前置一句话**：零件里 Component 传 NULL；装配体里传目标 `IComponent2`。
- **配方一句话**：`GetDefinition()` → `AccessSelections(TopDoc, NULL|IComponent2)` → 改 → `ModifyDefinition` / `ReleaseSelectionAccess`。

## F2 `Edges`

- **签名**：`System.object Edges {get; set;}`
- **## Remarks（逐字）**："See [Accessing Selections that Define Features](<../../docs/Programming with the SOLIDWORKS API/Selections that Define Features.md>) for additional details."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**（无例子）。

## F3 `FlipFaceTangentTo`

- **签名（1 个参数）**：`void FlipFaceTangentTo( System.int Index )`
- **## Remarks（逐字）**："This method is only available when the type of patch is set to swPatchTypeTangent. See [[IShutOffSurfaceFeatureData::LoopPatchType]] and [[IShutOffSurfaceFeatureData::SetAllPatchTypes]]."
- **官方例子**：**查不到**。 **枚举**：`swPatchTypeTangent` —— **查不到**（`C:\swapi\enums\` 下无 `swPatchType*.md`；CHM 解包目录里 `*swPatchType*` 文件数 = 0）。
- **废弃链**：无 Obsolete。
- **前置一句话**：补片类型必须是 `swPatchTypeTangent`（配合 `LoopPatchType` / `SetAllPatchTypes` 设置）。
- **配方一句话**：`FlipFaceTangentTo(Index)`；`swPatchTypeTangent` 的数值**查不到**。

## F4 `GetEdgeCount`

- **签名（0 个参数）**：`System.int GetEdgeCount()`
- **## Remarks（逐字）**："Call this method before calling [[IShutOffSurfaceFeatureData::IGetEdges]] to get the size of the array for that method."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：必须先于 `IGetEdges`。
- **配方一句话**：`Count = GetEdgeCount()` → `IGetEdges(Count)`。

## F5 `GetFaceTangentTo`

- **签名（1 个参数）**：`Face2 GetFaceTangentTo( System.int Index )`
- **## Remarks（逐字）**：
  > "This method is only available when the type of patch is set to swPatchTypeTangent. See [[IShutOffSurfaceFeatureData::LoopPatchType]] and [[IShutOffSurfaceFeatureData::SetAllPatchTypes]]."
  > "See [Accessing Selections that Define Features](…) for additional details."
- **官方例子 / 枚举**：**查不到 / `swPatchTypeTangent` 数值查不到**。 **废弃链**：无 Obsolete。
- **前置一句话**：补片类型必须是 `swPatchTypeTangent`。
- **配方一句话**：`Face = GetFaceTangentTo(Index)`。

## F6 `GetLoopCount`

- **签名（0 个参数）**：`System.int GetLoopCount()`
- **## Remarks（逐字）**："Call this method before calling [[IShutOffSurfaceFeatureData::IGetEdges]] to get the size of the array for that method."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：必须先于 `IGetEdges` 取 `Count`。
- **配方一句话**：`Count = GetLoopCount()`。

## F7 `GetLoopEdgeCount`

- **签名（1 个参数）**：`System.int GetLoopEdgeCount( System.int Index )`
- **## Remarks（逐字）**："Call this method before calling [[IShutOffSurfaceFeatureData::IGetLoopsEdges]] to get the size of the array for that method."
  ⚠ 官方原文把成员名拼作 `IGetLoopsEdges`（本接口实际成员是 `IGetLoopEdges`，逐字抄录）。
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：必须先于 `IGetLoopEdges` 取该 loop 的 `Count`。
- **配方一句话**：`N = GetLoopEdgeCount(Index)` → `IGetLoopEdges(Index, N)`。

## F8 `IGetEdges`

- **签名（1 个参数）**：`Edge IGetEdges( System.int Count )`
- **## Remarks（逐字）**：
  > "Call [[IShutOffSurfaceFeatureData::GetLoopCount]] before calling this method to get the value for Count."
  > "See [Accessing Selections that Define Features](…) for additional details on using this method."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：必须先调 `GetLoopCount()`。
- **配方一句话**：`Edges = IGetEdges(Count)`。

## F9 `IGetLoopEdges`

- **签名（2 个参数）**：`Edge IGetLoopEdges( System.int Index, System.int Count )`
- **## Remarks（逐字）**：
  > "Call [[IShutOffSurfaceFeatureData::GetLoopEdgeCount]] before calling this method to get the value of Count."
  > "Use [[IShutOffSurfaceFeatureData::Edges]] or [[IShutOffSurfaceFeatureData::ISetEdges]] to set the edges for the loops."
  > "See [Accessing Selections that Define Features](…) for additional details on using this method."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：必须先调 `GetLoopEdgeCount(Index)`；设置 loop 边要用 `Edges` 或 `ISetEdges`。
- **配方一句话**：`IGetLoopEdges(Index, Count)`。

## F10 `ISetEdges`

- **签名（2 个参数）**：`void ISetEdges( System.int Count, ref Edge EdgeArr )`
- **## Remarks（逐字）**："See [Accessing Selections that Define Features](…) for additional details on using this method."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：`ISetEdges(Count, ref EdgeArr)`。

## F11 `Knit`

- **签名**：`System.bool Knit {get; set;}`
- **## Remarks / 官方例子 / 枚举**：**查不到**。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**。

## F12 `LoopEdges`

- **签名**：**查不到** —— `C:\swapi\types\IShutOffSurfaceFeatureData\LoopEdges.md` **全文只有 frontmatter + 标题**，无 `**Signature**` 行、无 `## Remarks`；CHM 解包目录里**没有** `IShutOffSurfaceFeatureData~LoopEdges` 页（实测 NOT FOUND）。
- **官方例子 / 枚举**：**查不到**。 **废弃链**：无 Obsolete 标记（文件内无该字样）。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**。

## F13 `LoopPatchType`

- **签名**：**查不到** —— 同 F12（`LoopPatchType.md` 无签名行；CHM 无该页）。
- **## Remarks / 官方例子 / 枚举**：**查不到**（但 `FlipFaceTangentTo` 与 `GetFaceTangentTo` 的 Remarks 逐字点名 "See [[IShutOffSurfaceFeatureData::LoopPatchType]]"，且提到 `swPatchTypeTangent`）。
- **废弃链**：无 Obsolete 标记。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到** —— 官方只在别处把它当"设置补片类型"的入口点名。

## F14 `ReleaseSelectionAccess`

- **签名（0 个参数）**：`void ReleaseSelectionAccess()`
- **## Remarks（逐字）**：
  > "[[IShutOffSurfaceFeatureData::AccessSelections]] puts the model in a rollback state to allow access to the selections that define the feature."
  > "Use this method to restore the rollback state if you did not modify the feature, or use [[IFeature::ModifyDefinition]] or [[IFeature::IModifyDefinition2]] if you did modify the feature."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：没改特征才用；改过必须 `ModifyDefinition`。
- **配方一句话**：`ReleaseSelectionAccess()`。

## F15 `SetAllPatchTypes`

- **签名（1 个参数）**：`void SetAllPatchTypes( System.int Type )`
- **## Remarks**：**查不到**（无 `## Remarks` 段；CHM 无该成员页）。
- **官方例子**：**查不到**。 **枚举**：形参 `Type` 对应的 `swPatchType_e` **查不到**（`C:\swapi\enums\` 无该文件、CHM 0 命中）；只有 `FlipFaceTangentTo`/`GetFaceTangentTo` 的 Remarks 里出现过成员名 `swPatchTypeTangent`，**数值查不到**。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：`SetAllPatchTypes(Type)`；`Type` 的取值集合**查不到**。

## F16 `Status`

- **签名（0 个参数）**：`System.int Status()`
- **## Remarks / 官方例子 / 枚举**：**查不到 / 查不到 / 无**（文件只有签名行；CHM 无该成员页）。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**。

---

# G 组 · `ICavityFeatureData`（11 个成员）

## G1 `AccessSelections`

- **签名（2 个参数）**：`System.bool AccessSelections( ModelDoc2 TopDoc, Component2 Component )`
- **## Remarks（逐字）**：与 D1/E1 同文，末尾是 "[[ICavityFeatureData::ReleaseSelectionAccess]] if you did not"。
- **官方例子的调用序**（`Create_and_Modify_Cavity_Feature_Example_CSharp.md` 逐字）：
  > `status = swModelDocExt.SelectByID2("Cavity1@telephoneMoldBase-1@AssemInterim", "BODYFEATURE", 0, 0, 0, false, 0, null, 0);`
  > `swFeature = (Feature)swSelectionMgr.GetSelectedObject6(1, -1);`
  > `swCavityFeatureData = (CavityFeatureData)swFeature.GetDefinition();`
  > `status = swCavityFeatureData.AccessSelections(swModel, null);`
  > `status = swFeature.ModifyDefinition(swCavityFeatureData, swModel, null);`
- **枚举**：无。 **废弃链**：无 Obsolete。
- **前置一句话**：型腔特征位于**装配体里的零件**上，须先按特征全名 `"Cavity1@telephoneMoldBase-1@AssemInterim"` 用 `SelectByID2` 选中（type 传 `"BODYFEATURE"`）。
- **配方一句话**：`SelectByID2("Cavity1@<零件>-1@<装配体>", "BODYFEATURE", …)` → `GetDefinition()` → `AccessSelections(swModel, null)` → 改 → `ModifyDefinition`。

## G2 `Components`

- **签名**：`System.object Components {get; set;}`
- **## Remarks（逐字）**："See [Accessing Selections that Define Features](…) for additional details on using this property."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**（无例子）。

## G3 `GetComponentsCount`

- **签名（0 个参数）**：`System.int GetComponentsCount()`
- **## Remarks（逐字）**："Call this method before calling [[ICavityFeatureData::IGetComponents]]."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：必须先于 `IGetComponents`。
- **配方一句话**：`Count = GetComponentsCount()` → `IGetComponents(Count, out Comps)`。

## G4 `GetScale`

- **签名（3 个 out 形参）**：`void GetScale( out System.double Xscale, out System.double YScale, out System.double ZScale )`
  ⚠ 官方形参名大小写不一致（`Xscale` vs `YScale`/`ZScale`，逐字抄录）。
- **## Remarks**：**查不到**。
- **官方例子**（逐字）：`swCavityFeatureData.GetScale(out xScale, out yScale, out zScale);`（前后是 `Debug.Print("Scale values:"); Debug.Print("  X: " + xScale); …`）
- **枚举**：无。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**（官方例子里它紧跟在 `AccessSelections` 之后）。
- **配方一句话**：`GetScale(out X, out Y, out Z)` 三个方向的缩放值。

## G5 `IGetComponents`

- **签名（2 个参数）**：`void IGetComponents( System.int Count, out Component2 Comps )`
- **## Remarks（逐字）**：
  > "Call [[ICavityFeatureData::GetComponentsCount]] before calling this method."
  > "See [Accessing Selections that Define Features](…) for additional details on using this method."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：必须先调 `GetComponentsCount()`。
- **配方一句话**：`IGetComponents(Count, out Comps)`。

## G6 `ISetComponents`

- **签名（2 个参数）**：`void ISetComponents( System.int Count, ref Component2 Comps )`
- **## Remarks（逐字）**："See [Accessing Selections that Define Features](…) for additional details on using this method."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：`ISetComponents(Count, ref Comps)`。

## G7 `ReleaseSelectionAccess`

- **签名（0 个参数）**：`void ReleaseSelectionAccess()`
- **## Remarks（逐字）**：
  > "[[ICavityFeatureData::AccessSelections]] puts the model into a rollback state to allow access to the selections that define this feature."
  > "Use this method to restore the rollback state if you did not modify the feature or use [[IFeature::ModifyDefinition]] or [[IFeature::IModifyDefinition2]] if you did."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：没改才用；改过走 `ModifyDefinition`。
- **配方一句话**：`ReleaseSelectionAccess()`。

## G8 `ScaleType`

- **签名**：`System.int ScaleType {get; set;}`
- **## Remarks**：**查不到**。
- **官方例子**（逐字）：`Debug.Print("Scale type: " + swCavityFeatureData.ScaleType);`
- **枚举**：`swCavityScaleType_e`（`C:\swapi\enums\swCavityScaleType_e.md`）：`swAboutCentroid = 0` / `swAboutOrigin = 1` / `swAboutMoldBaseOrigin = 2` / `swAboutCoordinateSystem = 3`
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：只读取并打印（官方例子即如此）。

## G9 `SetScale`

- **签名（3 个参数）**：`void SetScale( System.double Xscale, System.double YScale, System.double ZScale )`
- **## Remarks / 官方例子 / 枚举**：**查不到**（无 `## Remarks` 段、无 `## Examples` 段；参数为 double，无枚举）。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**（官方例子只用了 `UniformScale`，没有调 `SetScale`）。

## G10 `UniformScale`

- **签名**：`System.double UniformScale {get; set;}`
- **## Remarks（逐字）**："Use [[ICavityFeatureData::UseUniformScale]] to enable uniform scaling of this cavity feature."
- **官方例子**（逐字）：
  > `Debug.Print("Value by which to scale this cavity feature in all directions: " + swCavityFeatureData.UniformScale);`
  > `swCavityFeatureData.UseUniformScale = true;`
  > `swCavityFeatureData.UniformScale = 2;`
- **枚举**：无。 **废弃链**：无 Obsolete。
- **前置一句话**：必须先把 `UseUniformScale` 置 `true`，`UniformScale` 才生效（官方例子的动作顺序就是这样）。
- **配方一句话**：`UseUniformScale = true` → `UniformScale = 2` → `ModifyDefinition`。

## G11 `UseUniformScale`

- **签名**：`System.bool UseUniformScale {get; set;}`
- **## Remarks（逐字）**："Use [[ICavityFeatureData::UniformScale]] to set the uniform scaling value for this cavity feature."
- **官方例子**（逐字）：`Debug.Print("Scale uniformly value: " + swCavityFeatureData.UseUniformScale);`
- **枚举**：无。 **废弃链**：无 Obsolete。
- **前置一句话**：用它来开启各向同性缩放，之后才用 `UniformScale` 写值。
- **配方一句话**：`UseUniformScale = true`。

---

# H 组 · `ICoreFeatureData`（13 个成员）

## H1 `AccessSelections`

- **签名（2 个参数）**：`System.bool AccessSelections( ModelDoc2 PTopDoc, Component2 PComponent )`
  ⚠ 本组形参名前缀是 `P`（`PTopDoc` / `PComponent`，其余组无此前缀），逐字抄录。
- **## Remarks（逐字）**：同 D1 结构，Part 行逐字是 "Component argument is NULL"，末尾是 "[[ICoreFeatureData::ReleaseSelectionAccess]] if you did not"。
- **官方例子的调用序**（`Get_Core_Feature_Example_CSharp.md` 逐字）：
  > `swFeat = (Feature)swSelMgr.GetSelectedObject6(1, -1);`
  > `swCoreFeat = (CoreFeatureData)swFeat.GetDefinition();`
  > `b = swCoreFeat.AccessSelections(swModel, null);`
  > `//Roll forward`
  > `swCoreFeat.ReleaseSelectionAccess();`
- **枚举**：无。 **废弃链**：无 Obsolete。
- **前置一句话**：核心特征要在树里先选中，再 `GetDefinition()` → `AccessSelections(swModel, null)`。
- **配方一句话**：`GetSelectedObject6(1,-1)` → `GetDefinition()` → `AccessSelections(swModel, null)` → 读属性 → `ReleaseSelectionAccess()`。

## H2 `BoundingSketch`

- **签名**：`Feature BoundingSketch {get; set;}`
- **## Remarks（逐字）**："See [Accessing Selections that Define Features](<../../docs/Programming with the SOLIDWORKS API/Selections that Define Features.md>) for additional details on using this property."
- **官方例子**（逐字）：`swFeat = swCoreFeat.BoundingSketch; nam = swFeat.Name; Debug.Print("Name of bounding sketch = " + nam);`
- **枚举**：无。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：读出 `IFeature` 后取 `.Name` 打印（官方例子）。

## H3 `CapEnds`

- **签名**：`System.bool CapEnds {get; set;}`
- **## Remarks / 枚举**：**查不到 / 无**。
- **官方例子**（逐字）：`cap = swCoreFeat.CapEnds; Debug.Print("Are ends capped? " + cap);`
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：只读取并打印。

## H4 `Depth`（索引属性）

- **签名（1 个参数，索引器）**：CHM 页 `…ICoreFeatureData~Depth.html` 逐字：`System.double Depth( System.int Index ) {get; set;}`
  ⚠ `C:\swapi\types\ICoreFeatureData\Depth.md` **全文只有 frontmatter + 标题，没有签名行** ⇒ 签名抄自 CHM。
  CHM 同页逐字参数说明："Index Direction to extract core as defined in swCoreFeatureDirection_e"。
- **## Remarks**：**查不到**（CHM 该页也无 Remarks 段）。
- **官方例子**（`Get_Core_Feature_Example_CSharp.md` 逐字）：
  > `d1 = swCoreFeat.get_Depth(0); Debug.Print("Depth along extraction direction = " + d1);`
  > `d2 = swCoreFeat.get_Depth(1); Debug.Print("Depth away from extraction direction = " + d2);`
- **枚举**：`swCoreFeatureDirection_e` = `swCoreAlongExtractionDirection = 0` / `swCoreAwayFromExtractionDirection = 1`
- **废弃链**：无 Obsolete 标记。
- **前置一句话**：`Index` 取 0 = 沿拔模方向、1 = 背离拔模方向。
- **配方一句话**：`get_Depth(0)` / `get_Depth(1)` 分别读两个方向的深度。

## H5 `DraftAngle`

- **签名**：`System.double DraftAngle {get; set;}`
- **## Remarks（逐字）**："To set this property, [[ICoreFeatureData::UseDraft]] must be true."
- **官方例子**（逐字）：官方包在 `if (useDr)` 里 —— `if (useDr) { ang = swCoreFeat.DraftAngle; Debug.Print("Angle of draft = " + ang); … }`
- **枚举**：无。 **废弃链**：无 Obsolete。
- **前置一句话**：要写它，`UseDraft` 必须为 `true`。
- **配方一句话**：先 `UseDraft = true`，再写 `DraftAngle`。

## H6 `DraftOutward`

- **签名**：`System.bool DraftOutward {get; set;}`
- **## Remarks（逐字）**："To set this property, [[ICoreFeatureData::UseDraft]] must be true."
- **官方例子**（逐字）：同样在 `if (useDr)` 分支内 —— `Drout = swCoreFeat.DraftOutward; Debug.Print("Drafted outward? = " + Drout);`
- **枚举**：无。 **废弃链**：无 Obsolete。
- **前置一句话**：要写它，`UseDraft` 必须为 `true`。
- **配方一句话**：`UseDraft = true` → 写 `DraftOutward`。

## H7 `EndCondition`（索引属性）

- **签名（1 个参数，索引器）**：CHM 页 `…ICoreFeatureData~EndCondition.html` 逐字：`System.int EndCondition( System.int Index ) {get; set;}`
  ⚠ `C:\swapi\types\ICoreFeatureData\EndCondition.md` 同样**只有 frontmatter + 标题，无签名行**。
  CHM 同页属性值逐字："Type of end conditions as defined in swEndConditions_e (see Remarks )"；参数 `Index` 逐字："Direction of end conditions as defined in swCoreFeatureDirection_e"。
- **## Remarks（逐字）**（CHM）："Valid end conditions are swEndConditions_e: swEndCondBlind swEndCondThroughAll swEndCondThroughNext"
- **官方例子**（逐字）：
  > `e1 = swCoreFeat.get_EndCondition(0); Debug.Print("End condition along extraction = " + e1);`
  > `e2 = swCoreFeat.get_EndCondition(1); Debug.Print("End condition away from extraction = " + e2);`
- **枚举**：
  - `swEndConditions_e`（CHM 只点名 3 个；完整 11 个取值见 `C:\swapi\enums\swEndConditions_e.md`）：
    `swEndCondBlind = 0` / `swEndCondThroughAll = 1` / `swEndCondThroughNext = 2` / `swEndCondUpToVertex = 3`（官方注 "Do not use; superseded by swEndCondUpToSelection"）/ `swEndCondUpToSurface = 4`（同上注）/ `swEndCondOffsetFromSurface = 5` / `swEndCondMidPlane = 6` / `swEndCondUpToBody = 7` / `swEndCondThroughAllBoth = 9` / `swEndCondUpToSelection = 10` / `swEndCondUpToNext = 11`
  - `swCoreFeatureDirection_e` = `swCoreAlongExtractionDirection = 0` / `swCoreAwayFromExtractionDirection = 1`
- **废弃链**：无 Obsolete。
- **前置一句话**：只接受 `swEndCondBlind` / `swEndCondThroughAll` / `swEndCondThroughNext` 三种（CHM Remarks 逐字）。
- **配方一句话**：`get_EndCondition(0)` / `get_EndCondition(1)` 读两个方向的终止条件。

## H8 `GetExtractionDirection`

- **签名（4 个形参，全部 out）**：`System.int GetExtractionDirection( out System.int Type1, out System.object PDir1, out System.int Type2, out System.object PDir2 )`
- **## Remarks（逐字）**：
  > "The types of entities that define the extraction direction are:
  > - Face
  > - Plane
  > - Edge
  > - Vertex
  > - Sketch line
  > - Sketch point
  > There can be two entities because two sketch points can specify a direction."
- **官方例子**（逐字）：`ct = swCoreFeat.GetExtractionDirection(out typ1, out dir1, out typ2, out dir2); Debug.Print("Number of entities that define extraction = " + ct);`
- **枚举**：`Type1` / `Type2` 的实体类型枚举**查不到**（官方只给上面 6 个文字名，没点名枚举）。
- **废弃链**：无 Obsolete。
- **前置一句话**：定义拔模方向的实体只能是 Face / Plane / Edge / Vertex / Sketch line / Sketch point 六类之一。
- **配方一句话**：`N = GetExtractionDirection(out T1, out D1, out T2, out D2)`，`N` 是定义方向的实体个数。

## H9 `ReleaseSelectionAccess`

- **签名（0 个参数）**：`void ReleaseSelectionAccess()`
- **## Remarks（逐字）**：
  > "[[ICoreFeatureData::AccessSelections]] puts the model into a rollback state to allow access to the selections that define this feature."
  > "Use this method to restore the rollback state if you did not modify the feature or use [[IFeature::ModifyDefinition]] or [[IFeature::IModifyDefinition2]] if you did."
- **官方例子**（逐字）：`//Roll forward` 之后 `swCoreFeat.ReleaseSelectionAccess();`
- **枚举**：无。 **废弃链**：无 Obsolete。
- **前置一句话**：官方例子用它收尾（只读场景）。
- **配方一句话**：`ReleaseSelectionAccess()`。

## H10 `ReverseDirection`

- **签名**：`System.bool ReverseDirection {get; set;}`
- **## Remarks / 枚举**：**查不到 / 无**。
- **官方例子**（逐字）：`rev = swCoreFeat.ReverseDirection; Debug.Print("Direction of extraction reversed? " + rev);`
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：只读取并打印。

## H11 `SetExtractionDirection`

- **签名（2 个参数）**：`System.bool SetExtractionDirection( System.object PDir1, System.object PDir2 )`
- **## Remarks（逐字）**：与 H8 同一段（"The types of entities that define the extraction direction are: Face / Plane / Edge / Vertex / Sketch line / Sketch point … There can be two entities because two sketch points can specify a direction."）。
- **官方例子**：**查不到**（该文件无 `## Examples` 段）。
- **枚举**：同 H8，**查不到**。 **废弃链**：无 Obsolete。
- **前置一句话**：传入的实体只能是那六类；给两个草图点即可定方向。
- **配方一句话**：`SetExtractionDirection(PDir1, PDir2)` 返回 bool。

## H12 `TargetBody`

- **签名**：`Body2 TargetBody {get; set;}`
- **## Remarks（逐字）**："See [Accessing Selections that Define Features](<../../docs/Programming with the SOLIDWORKS API/Selections that Define Features.md>) for additional details on using this property."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**。

## H13 `UseDraft`

- **签名**：`System.bool UseDraft {get; set;}`
- **## Remarks / 枚举**：**查不到 / 无**。
- **官方例子**（逐字）：`useDr = swCoreFeat.UseDraft; Debug.Print("Drafted? " + useDr); if (useDr) { ang = swCoreFeat.DraftAngle; … }`
- **废弃链**：无 Obsolete。
- **前置一句话**：官方例子把 `DraftAngle` / `DraftOutward` 的读取放在它的 `if` 分支里。
- **配方一句话**：`UseDraft = true` 后才能用 `DraftAngle` / `DraftOutward`。

---

# I 组 · `IToolingSplitFeatureData`（17 个成员）

## I1 `AccessSelections`

- **签名（2 个参数）**：`System.bool AccessSelections( ModelDoc2 TopDoc, Component2 Component )`
- **## Remarks（逐字）**：同 D1 结构，Part 行 "Component argument is NULL"，末尾 "[[IToolingSplitFeatureData::ReleaseSelectionAccess]] if you did not"。
- **官方例子**：**查不到**（无 `## Examples` 段；`C:\swapi\examples\` 无 tooling split 例子）。
- **枚举**：无。 **废弃链**：无 Obsolete。
- **前置一句话**：零件里 Component 传 NULL，装配体里传目标 `IComponent2`。
- **配方一句话**：`GetDefinition()` → `AccessSelections(TopDoc, NULL|IComponent2)` → 改 → 收尾。

## I2 `Angle`

- **签名**：`System.double Angle {get; set;}`
- **## Remarks（逐字）**："See [Accessing Selections that Define Features](…) for additional details."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**（但在 `InterlockSurface` 的 Remarks 里被提到，见 I14）。
- **配方一句话**：**查不到**。

## I3 `CavitySurfaces`

- **签名**：`System.object CavitySurfaces {get; set;}`
- **## Remarks（逐字）**："See [Accessing Selections that Define Features](…) for additional details."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**（数组侧为 `GetCavitySurfacesCount` + `IGetCavitySurfaces` / `ISetCavitySurfaces`）。

## I4 `CoreSurfaces`

- **签名**：`System.object CoreSurfaces {get; set;}`
- **## Remarks（逐字）**："See [Accessing Selections that Define Features](…) for additional details."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**。

## I5 `Depth`

- **签名**：**查不到** —— `C:\swapi\types\IToolingSplitFeatureData\Depth.md` 全文只有 frontmatter + 标题（无 `**Signature**` 行、无 `## Remarks`）；CHM 解包目录里**没有** `IToolingSplitFeatureData~Depth` 页（实测 NOT FOUND）。
- **官方例子 / 枚举**：**查不到**。 **废弃链**：无 Obsolete 标记。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**。

## I6 `GetCavitySurfacesCount`

- **签名（0 个参数）**：`System.int GetCavitySurfacesCount()`
- **## Remarks（逐字）**："Call this method before calling [[IToolingSplitFeatureData::IGetCavitySurfaces]] to get the size of the array for that method."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：必须先于 `IGetCavitySurfaces`。
- **配方一句话**：`Count = GetCavitySurfacesCount()`。

## I7 `GetCoreSurfacesCount`

- **签名（0 个参数）**：`System.int GetCoreSurfacesCount()`
- **## Remarks（逐字）**："Call this method before calling [[IToolingSplitFeatureData::IGetCoreSurfaces]] to get the size of the array for that method."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：必须先于 `IGetCoreSurfaces`。
- **配方一句话**：`Count = GetCoreSurfacesCount()`。

## I8 `GetPartingSurfacesCount`

- **签名（0 个参数）**：`System.int GetPartingSurfacesCount()`
- **## Remarks（逐字）**："Call this method before calling [[IToolingSplitFeatureData::IGetPartingSurfaces]] to get the size of the array for that method."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：必须先于 `IGetPartingSurfaces`。
- **配方一句话**：`Count = GetPartingSurfacesCount()`。

## I9 `IGetCavitySurfaces`

- **签名（1 个参数）**：`Body2 IGetCavitySurfaces( System.int Count )`
- **## Remarks（逐字）**："Call [[IToolingSplitFeatureData::GetCavitySurfacesCount]] before calling this method to get Count."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：必须先调 `GetCavitySurfacesCount()`。
- **配方一句话**：`IGetCavitySurfaces(Count)`。

## I10 `IGetCoreSurfaces`

- **签名（1 个参数）**：`Body2 IGetCoreSurfaces( System.int Count )`
- **## Remarks（逐字）**："Call [[IToolingSplitFeatureData::GetCoreSurfacesCount]] before calling this method to get Count."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：必须先调 `GetCoreSurfacesCount()`。
- **配方一句话**：`IGetCoreSurfaces(Count)`。

## I11 `IGetPartingSurfaces`

- **签名（1 个参数）**：`Body2 IGetPartingSurfaces( System.int Count )`
- **## Remarks（逐字）**："Call [[IToolingSplitFeatureData::GetPartingSurfacesCount]] before calling this method to get Count."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：必须先调 `GetPartingSurfacesCount()`。
- **配方一句话**：`IGetPartingSurfaces(Count)`。

## I12 `InterlockSurface`

- **签名**：`System.bool InterlockSurface {get; set;}`
- **## Remarks（逐字）**：
  > "If this property is set to true, then you can specify a [[draft angle]] for the interlock surface."
  > "See [Accessing Selections that Define Features](…) for additional details."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：置 `true` 之后才能给 interlocking 面指定拔模角（即 `Angle`）。
- **配方一句话**：`InterlockSurface = true` → 写 `Angle`。

## I13 `ISetCavitySurfaces`

- **签名（2 个参数）**：`void ISetCavitySurfaces( System.int Count, ref Body2 BodyArr )`
- **## Remarks（逐字）**："See [Accessing Selections that Define Features](…) for additional details."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：`ISetCavitySurfaces(Count, ref BodyArr)`。

## I14 `ISetCoreSurfaces`

- **签名（2 个参数）**：`void ISetCoreSurfaces( System.int Count, ref Body2 BodyArr )`
- **## Remarks（逐字）**："See [Accessing Selections that Define Features](…) for additional details."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：`ISetCoreSurfaces(Count, ref BodyArr)`。

## I15 `ISetPartingSurfaces`

- **签名（2 个参数）**：`void ISetPartingSurfaces( System.int Count, ref Body2 BodyArr )`
- **## Remarks（逐字）**："See [Accessing Selections that Define Features](…) for additional details."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：`ISetPartingSurfaces(Count, ref BodyArr)`。

## I16 `PartingSurfaces`

- **签名**：`System.object PartingSurfaces {get; set;}`
- **## Remarks（逐字）**："See [Accessing Selections that Define Features](…) for additional details."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**。

## I17 `ReleaseSelectionAccess`

- **签名（0 个参数）**：`void ReleaseSelectionAccess()`
- **## Remarks（逐字）**：
  > "[[IToolingSplitFeatureData::AccessSelections]] puts the model in a rollback state to allow access to the selections that define the feature."
  > "Use this method to restore the rollback state if you did not modify the feature, or use [[IFeature::ModifyDefinition]] or [[IFeature::IModifyDefinition2]] if you did modify the feature."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：没改特征才用。
- **配方一句话**：`ReleaseSelectionAccess()`。

---

# J 组 · Costing 域（1 个可抄成员 + 1 条结构性「查不到」）

## J1 `IModelDocExtension::GetCostingManager`

- **签名（0 个参数）**：`System.object GetCostingManager()`
  返回值原文逐字："[[ICostManager]]"
- **## Remarks（逐字）**："SOLIDWORKS Costing and its API are only available in SOLIDWORKS Professional and SOLIDWORKS Premium."
- **官方例子的调用序**（`C:\swapi\examples\Create_Machining_Costing_Analyses_Example_CSharp.md`，逐字）：
  > `// Add a reference to SolidWorks.Interop.sldcostingapi.dll.`（Preconditions 第 3 条）
  > `swCosting = (CostManager)swModelDocExt.GetCostingManager();`
  > `swCosting.WaitForUIUpdate();`
  > `nbrMachiningCostingTemplate = swCosting.GetTemplateCount((int)swcCostingType_e.swcCostingType_Machining);`
  > `machiningCostingTemplates = (object[])swCosting.GetTemplatePathnames((int)swcCostingType_e.swcCostingType_Machining);`
  > `swCostingModel = (object)swCosting.CostingModel;`
  > `swCostingPart = (CostPart)swCostingModel;`
  > `swCostingAnalysis = (CostAnalysis)swCostingPart.CreateCostAnalysis("c:\\program files\\solidworks corp\\solidworks\\lang\\english\\costing templates\\multibodytemplate_default(englishstandard).sldctc");`
  > `swCostingAnalysis = (CostAnalysis)swCostingBody.CreateCostAnalysis("c:\\program files\\solidworks corp\\solidworks\\lang\\english\\costing templates\\machiningtemplate_default(englishstandard).sldcts");`
  > `swCostingMachining = (CostAnalysisMachining)swCostingAnalysis.GetSpecificAnalysis();`
  ⚠ 该例子的 Preconditions 第 2 条逐字还要求："Verify that the Costing templates exist by clicking Tools > Options > System Options > File Locations and select Costing templates in Show folders for in SOLIDWORKS Design."
  ⚠ 同名 VB / VB.NET 例子另见 `Create_Machining_Costing_Analyses_Example_VB.md` / `_VBNET.md`；钣金版另见 `Create_Sheet_Metal_Costing_Analyses_Example_CSharp.md` / `_VBNET.md` / `_VB.md`。
- **枚举**：签名里无枚举。例子里出现的 `swcCostingType_e`、`swcBodyType_e`、`swcBodyStatus_e` 在 `C:\swapi\enums\` **查不到**
  （实测：无 `swcCostingType_e.md`、无 `swcBodyStatus_e.md`；`swBodyType_e.md` 存在但**不是**例子里那个 `swcBodyType_e`）⇒ 其成员与数值**查不到**。
- **废弃链**：**无 Obsolete 标记**。
- **前置一句话**：SOLIDWORKS Costing 及其 API 只在 Professional 与 Premium 版可用（官方逐字），且须先引用 `SolidWorks.Interop.sldcostingapi.dll`。
- **配方一句话**：`CostManager = (CostManager)swModelDocExt.GetCostingManager()` → `WaitForUIUpdate()` → `CostingModel` → `CostPart` → `CreateCostAnalysis(<.sldctc/.sldcts 模板路径>)`。

## J2 `ICostManager` 及其 Costing 家族成员 —— **查不到**

- 派工要求的 `C:\swapi\types\ICosting*`：**目录不存在**（`Get-ChildItem C:\swapi\types\` 实读 566 个目录无一匹配）。
- 全仓递归搜 `CostManager|CostAnalysis|CostBody|CostPart|CostFeature` 命名的 `.md`：**0 命中**。
- CHM 解包目录 `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\` 里 `*sldcostingapi*` 文件数：**0**。
- ⇒ **ICostManager / CostPart / CostBody / CostAnalysis / CostAnalysisMachining / CostFeature / swcCostingType_e / swcBodyType_e / swcBodyStatus_e 的签名、Remarks、枚举数值，在本机两套离线源里全部查不到。**
  本机唯一可抄的 Costing 契约就是 J1 那一条入口 + C 组里的官方例子原文。

---

# K 组 · `IMeasure`（32 个成员）

接口 frontmatter：`category: Utility Interfaces`。
**全部 32 个成员在 `C:\swapi\types\IMeasure\*.md` 里都没有 `## Remarks` 段**（实测 `withRemarks=0`）⇒ 逐条按"查不到"记。
官方例子三份同名同码：`Measure_Selected_Entities_Example_CSharp.md` / `_VBNET.md` / `_VB.md`（C# 版调用序见下）。

**共用例子骨架（逐字，`Create_Machining…` 之外的 `Measure_Selected_Entities_Example_CSharp.md`）**：
> `status = swModelDocExt.SelectByID2("", "FACE", -0.00382117299216134, -0.0032246917626253, -0.00153854043344381, false, 0, null, 0);`
> `status = swModelDocExt.SelectByID2("", "FACE", 0.00547600669648318, 0.00252191841298099, 0.0050000000000523, true, 0, null, 0);`
> `swMeasure = (Measure)swModelDocExt.CreateMeasure();`
> `swMeasure.ArcOption = 0;`
> `status = swMeasure.Calculate(null);`
> `if ((!(swMeasure.Length == -1))) { Debug.Print("Length: " + swMeasure.Length); }` …（逐个量值先判 `-1` 再打印）
> `Debug.Print("Invalid combination of selected entities.");`（`Calculate` 返回 false 的分支）
> `swModel.ClearSelection2(true);`

## K1 `IModelDocExtension::CreateMeasure`（**入口，不在 `IMeasure` 里，但例子必经**，抄录备查）

- **签名（0 个参数）**：CHM 页 `…IModelDocExtension~CreateMeasure.html` 逐字：`Measure CreateMeasure()`（返回 "Measure tool"）。
- **## Remarks**：**查不到**（CHM 该页无 Remarks 段）。
- **官方例子**：即上面骨架第 3 行。
- **枚举 / 废弃链**：无 / 无 Obsolete（Availability "SOLIDWORKS 2008 FCS, Revision Number 16.0"）。
- **前置一句话**：**查不到** —— 官方例子是"先 `SelectByID2` 选两个面，再 `CreateMeasure()`"。
- **配方一句话**：选实体 → `CreateMeasure()` → 设 `ArcOption` → `Calculate(null)` → 读各量。

## K2 `Calculate`

- **签名（1 个参数）**：`System.bool Calculate( System.object Entities )`
- **## Remarks**：swapi **查不到**；CHM 页 `…IMeasure~Calculate.html` 的参数与返回值逐字：
  > 参数 "Entities: Array of entities to measure; if NULL, then this method measures the selected entities"
  > 返回值 "True if the specified or selected entities are valid types and combination , false if not"
- **官方例子**（逐字）：`status = swMeasure.Calculate(null);` —— **传 null**，并用返回的 `status` 判断后再读所有量值。
- **枚举**：无。 **废弃链**：无 Obsolete（Availability "SOLIDWORKS 2008 FCS, Revision Number 16.0"）。
- **前置一句话**：要量的实体已经选中，或直接把它作为数组传进来（传 NULL 则量选中的）。
- **配方一句话**：`Calculate(null)` → 返回 `True` 才继续读 `Length/Area/…`。

## K3 `SetProjectionEntity`

- **签名（1 个参数）**：`System.bool SetProjectionEntity( System.object Entity )`
- **## Remarks**：swapi **查不到**；CHM 页逐字：参数 "Face or plane"，返回值 "True if Entity is set, false if not"，See Also 点名 `IMeasure::Projection` 与 `IMeasure::ProjectionOption`。
- **官方例子**：**查不到**（`Measure_Selected_Entities_Example_CSharp.md` 里没有这一句）。
- **枚举**：无。 **废弃链**：无 Obsolete（Availability "SOLIDWORKS 2008 FCS, Revision Number 16.0"）。
- **前置一句话**：参数只能是面或平面（CHM 逐字 "Face or plane"）。
- **配方一句话**：**查不到** —— 官方例子没调用它。

## K4–K32 · 其余 29 个成员（**全部无 `## Remarks`**）

以下逐条只抄**精确签名**（源文件均在 `C:\swapi\types\IMeasure\`），示例列的"官方例子"一律指上面那份共用骨架（该成员在骨架里出现的逐字形式已给出）。

| # | 成员 | 精确签名（0 参数的属性） | 官方例子中的逐字用法 | 前置一句话 | 配方一句话 |
| --- | --- | --- | --- | --- | --- |
| K4 | `Angle` | `System.double Angle {get;}` | `if ((!(swMeasure.Angle == -1))) { Debug.Print("Angle: " + swMeasure.Angle); }` | 查不到 | `Calculate` 成功后判 `-1` 再读 |
| K5 | `AngleDecimalPlaces` | `System.int AngleDecimalPlaces {get; set;}` | 例子未出现 | 查不到 | 查不到 |
| K6 | `ArcLength` | `System.double ArcLength {get;}` | `Debug.Print("Arc length: " + swMeasure.ArcLength);`（判 `-1`） | 查不到 | 同上 |
| K7 | `ArcOption` | `System.int ArcOption {get; set;}` | `swMeasure.ArcOption = 0;`，注释逐字 "Can set this to 0 // 0 = center to center // 1 = minimum distance // 2 = maximum distance" | 查不到 | 先设 `ArcOption` 再 `Calculate` |
| K8 | `Area` | `System.double Area {get;}` | `Debug.Print("Area: " + swMeasure.Area);`（判 `-1`） | 查不到 | 同上 |
| K9 | `CenterDistance` | `System.double CenterDistance {get;}` | `Debug.Print("Center distance: " + swMeasure.CenterDistance);`（判 `-1`） | 查不到 | 同上 |
| K10 | `ChordLength` | `System.double ChordLength {get;}` | `Debug.Print("Chord length: " + swMeasure.ChordLength);`（判 `-1`） | 查不到 | 同上 |
| K11 | `DeltaX` | `System.double DeltaX {get;}` | `Debug.Print("DeltaX: " + swMeasure.DeltaX);`（判 `-1`） | 查不到 | 同上 |
| K12 | `DeltaY` | `System.double DeltaY {get;}` | `Debug.Print("DeltaY: " + swMeasure.DeltaY);`（判 `-1`） | 查不到 | 同上 |
| K13 | `DeltaZ` | `System.double DeltaZ {get;}` | `Debug.Print("DeltaZ: " + swMeasure.DeltaZ);`（判 `-1`） | 查不到 | 同上 |
| K14 | `Diameter` | `System.double Diameter {get;}` | `Debug.Print("Diameter: " + swMeasure.Diameter);`（判 `-1`） | 查不到 | 同上 |
| K15 | `Distance` | `System.double Distance {get;}` | `Debug.Print("Distance: " + swMeasure.Distance);`（判 `-1`） | 查不到 | 同上 |
| K16 | `IsConcentricSpheres` | `System.bool IsConcentricSpheres {get;}` | `if ((swMeasure.IsConcentricSpheres)) { Debug.Print("Are concentric spheres: " + swMeasure.IsConcentricSpheres); }` | 查不到 | 布尔直读 |
| K17 | `IsIntersect` | `System.bool IsIntersect {get;}` | `if ((swMeasure.IsIntersect)) { Debug.Print("Is intersect: " + swMeasure.IsIntersect); }` | 查不到 | 布尔直读 |
| K18 | `IsParallel` | `System.bool IsParallel {get;}` | `if ((swMeasure.IsParallel)) { Debug.Print("Is parallel: " + swMeasure.IsParallel); }` | 查不到 | 布尔直读 |
| K19 | `IsPerpendicular` | `System.bool IsPerpendicular {get;}` | `if ((swMeasure.IsPerpendicular)) { Debug.Print("Is perpendicular: " + swMeasure.IsPerpendicular); }` | 查不到 | 布尔直读 |
| K20 | `Length` | `System.double Length {get;}` | `Debug.Print("Length: " + swMeasure.Length);`（判 `-1`） | 查不到 | 判 `-1` 再读 |
| K21 | `LengthDecimalPlaces` | `System.int LengthDecimalPlaces {get; set;}` | 例子未出现 | 查不到 | 查不到 |
| K22 | `Normal` | `System.double Normal {get;}` | `Debug.Print("Normal: " + swMeasure.Normal);`（判 `-1`） | 查不到 | 判 `-1` 再读 |
| K23 | `NormalDistance` | `System.double NormalDistance {get;}` | `Debug.Print("Normal distance: " + swMeasure.NormalDistance);`（判 `-1`） | 查不到 | 判 `-1` 再读 |
| K24 | `Perimeter` | `System.double Perimeter {get;}` | `Debug.Print("Perimeter: " + swMeasure.Perimeter);`（判 `-1`） | 查不到 | 判 `-1` 再读 |
| K25 | `Projection` | `System.double Projection {get;}` | `Debug.Print("Projection: " + swMeasure.Projection);`（判 `-1`） | 查不到 | 需先 `SetProjectionEntity`（CHM See Also 点名） |
| K26 | `ProjectionOption` | `System.int ProjectionOption {get; set;}` | 例子未出现 | 查不到 | 查不到（枚举见 K33） |
| K27 | `Radius` | `System.double Radius {get;}` | `Debug.Print("Radius: " + swMeasure.Radius);`（判 `-1`） | 查不到 | 判 `-1` 再读 |
| K28 | `SpericalCenterDistance` | `System.double SpericalCenterDistance {get;}` | `Debug.Print("Spherical center distance: " + swMeasure.SpericalCenterDistance);`（判 `-1`）⚠ 官方成员名拼作 `Sperical`（少一个 h，逐字抄录） | 查不到 | 判 `-1` 再读 |
| K29 | `TotalArea` | `System.double TotalArea {get;}` | `Debug.Print("Total area: " + swMeasure.TotalArea);`（判 `-1`） | 查不到 | 判 `-1` 再读 |
| K30 | `TotalLength` | `System.double TotalLength {get;}` | `Debug.Print("Total length: " + swMeasure.TotalLength);`（判 `-1`） | 查不到 | 判 `-1` 再读 |
| K31 | `X` | `System.double X {get;}` | `Debug.Print("X coordinate: " + swMeasure.X);`（判 `-1`） | 查不到 | 判 `-1` 再读 |
| K32 | `Y` | `System.double Y {get;}` | `Debug.Print("Y coordinate: " + swMeasure.Y);`（判 `-1`） | 查不到 | 判 `-1` 再读 |
| K33 | `Z` | `System.double Z {get;}` | `Debug.Print("Z coordinate: " + swMeasure.Z);`（判 `-1`） | 查不到 | 判 `-1` 再读 |

★ 上表每一行的"**枚举**"一栏统一为：**无**（这 29 个成员签名里都没有枚举形参）。
★ "**废弃链**"一栏统一为：**无 Obsolete 标记**（这 29 个文件里都没有 "Obsolete" 字样）。

## K34–K36 · `IMeasure` 相邻枚举（值抄自 `C:\swapi\enums\`）

- **`swMeasureArcCircleOption_e`**（对应 K7 `ArcOption` 的取值域）：`swMeasureArcCircle_CenterToCenter = 0` / `swMeasureArcCircle_MinimumDistance = 1` / `swMeasureArcCircle_MaximumDistance = 2` / `swMeasureArcCircle_CustomCenterToCenter = 3` / `swMeasureArcCircle_CustomMinimumToMinimum = 4` / `swMeasureArcCircle_CustomMaximumToMaximum = 5` / `swMeasureArcCircle_CustomCenterToMinimum = 6` / `swMeasureArcCircle_CustomCenterToMaximum = 7` / `swMeasureArcCircle_CustomMinimumToCenter = 8` / `swMeasureArcCircle_CustomMaximumToCenter = 9` / `swMeasureArcCircle_CustomMinimumToMaximum = 10` / `swMeasureArcCircle_CustomMaximumToMinimum = 11`
- **`swMeasureProjectOnOption_e`**（对应 K26 `ProjectionOption` 的取值域）：`swMeasureProjectOn_None = 0` / `swMeasureProjectOn_Screen = 1` / `swMeasureProjectOn_FaceOrPlane = 2`
- ⚠ 这两个枚举**在 `IMeasure` 各成员页里都没有被点名**（swapi 未把它们挂到成员上）⇒ 归属关系是按"名称对应"记的，**官方在本机两套源里没有把它们与 `ArcOption` / `ProjectionOption` 显式绑定**。

---

# L 组 · `IMassProperty2`（18 个成员）

接口 frontmatter：`category: Utility Interfaces`。
官方例子：`Get_Mass_Properties_Using_IMassProperty_Example_CSharp.md`（CHM 目录里同名 `.htm` 实读存在）。

## L1 `AccuracyLevel`

- **签名**：`System.int AccuracyLevel {get; set;}`
- **## Remarks**：**查不到**。 **官方例子**：**查不到**。 **枚举**：无。 **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**。

## L2 `CenterOfMass`

- **签名**：`System.object CenterOfMass {get;}`
- **## Remarks（逐字）**："If [[IMassPropertyOverrideOptions::OverrideCenterOfMass]] is true or [[IMassProperty2::IncludeHiddenBodiesOrComponents]] is reset, then call [[IMassProperty2::Recalculate]] before using this property."
- **官方例子**：**查不到**（该文件无 `## Examples` 段）。
- **枚举**：无。 **废弃链**：无 Obsolete。
- **前置一句话**：覆盖了质心（`OverrideCenterOfMass=true`）或复位了 `IncludeHiddenBodiesOrComponents` 之后，必须先 `Recalculate()`。
- **配方一句话**：改覆盖值或改 `IncludeHiddenBodiesOrComponents` → `Recalculate()` → 读 `CenterOfMass`。

## L3 `Density`

- **签名**：`System.double Density {get;}`
- **## Remarks（逐字）**：
  > "If the density varies across components in a model:
  > Density = ( Mass / Volume )
  > If [[IMassProperty2::IncludeHiddenBodiesOrComponents]] is reset, then call [[IMassProperty2::Recalculate]] before using this property."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：复位 `IncludeHiddenBodiesOrComponents` 之后先 `Recalculate()`；密度随零件不同而异时按 `Density = Mass / Volume` 理解。
- **配方一句话**：`Recalculate()` → 读 `Density`。

## L4 `GetMomentOfInertia`

- **签名（1 个参数）**：`System.object GetMomentOfInertia( System.int WhereTaken )`
- **## Remarks（逐字）**："The return value is a 0-based array of nine doubles: **[ Lxx, Lxy, Lxz, Lyx, Lyy, Lyz, Lzx, Lzy, Lzz ]**"
- **官方例子**：**查不到**。 **枚举**：形参 `WhereTaken` 的枚举**查不到**。
- **废弃链**：无 Obsolete。
- **前置一句话**：返回的是 0 基的 9 元 double 数组，顺序固定为 `Lxx, Lxy, Lxz, Lyx, Lyy, Lyz, Lzx, Lzy, Lzz`。
- **配方一句话**：`GetMomentOfInertia(WhereTaken)` → 拆 9 个分量。

## L5 `GetOverrideOptions`

- **签名（0 个参数）**：`System.object GetOverrideOptions()`
- **## Remarks / 官方例子 / 枚举**：**查不到**。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**（无 `## Examples` 段；与之配对的写侧是 `SetOverrideOptions`，见 L7）。

## L6 `IncludeHiddenBodiesOrComponents`

- **签名**：`System.bool IncludeHiddenBodiesOrComponents {get; set;}`
- **## Remarks（逐字）**："After setting this property to true, be sure to call [[IMassProperty2::Recalculate]] before using the IMassProperty2 properties."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：设为 `true` 之后必须 `Recalculate()` 才能用 `IMassProperty2` 的各属性。
- **配方一句话**：`IncludeHiddenBodiesOrComponents = true` → `Recalculate()` → 读 `Volume` / `Mass` / `SurfaceArea` 等。

## L7 `Mass`

- **签名**：`System.double Mass {get;}`
- **## Remarks（逐字）**："If [[IMassPropertyOverrideOptions::OverrideMass]] is true or [[IMassProperty2::IncludeHiddenBodiesOrComponents]] is reset, then call [[IMassProperty2::Recalculate]] before using this property."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：覆盖质量或复位隐藏体开关之后先 `Recalculate()`。
- **配方一句话**：`Recalculate()` → 读 `Mass`。

## L8 `PrincipalAxesOfInertia`

- **签名（1 个参数，索引器，只读）**：CHM 页 `…IMassProperty2~PrincipalAxesOfInertia.html` 逐字：`System.object PrincipalAxesOfInertia( System.int Axis ) {get;}`
  ⚠ `C:\swapi\types\IMassProperty2\PrincipalAxesOfInertia.md` **全文只有 frontmatter + 标题，无签名行** ⇒ 签名抄自 CHM。
  CHM 同页 `Axis` 参数逐字："0 =&nbsp;x axis 1 =&nbsp;y axis 2 =&nbsp;z axis"。
- **## Remarks**：**查不到**（CHM 该页亦无）。 **官方例子**：**查不到**。
- **枚举**：无（`Axis` 是 0/1/2 的整型索引，CHM 给了字面对应，不是枚举）。
- **废弃链**：无 Obsolete。
- **前置一句话**：`Axis` 取 0=x 轴、1=y 轴、2=z 轴。
- **配方一句话**：`PrincipalAxesOfInertia(0|1|2)` 取指定轴的主惯性轴向量。

## L9 `PrincipalMomentsOfInertia`

- **签名**：`System.object PrincipalMomentsOfInertia {get;}`
- **## Remarks（逐字）**：
  > "This property returns metric units unless explicitly specified otherwise."
  > "The return value is a 0-based array of doubles: **[ Px, Py, Pz ]**"
  > "If [[IMassPropertyOverrideOptions::OverrideMomentsOfInertia]] is true or [[IMassProperty2::IncludeHiddenBodiesOrComponents]] is reset, then call [[IMassProperty2::Recalculate]] before using this property."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：覆盖主惯性矩或复位隐藏体开关后先 `Recalculate()`；该属性**默认返回 metric 单位**。
- **配方一句话**：`Recalculate()` → 读 3 元数组 `[Px, Py, Pz]`。

## L10 `Recalculate`

- **签名（0 个参数）**：`System.bool Recalculate()`
- **## Remarks（逐字）**："Call this method after overriding mass properties (center of mass, mass, moments of inertia, principal axes orientation, or principal moments of inertia) or resetting [[IMassProperty2::IncludeHiddenBodiesOrComponents]]."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：覆盖质心/质量/惯性矩/主轴方向/主惯性矩之后，或复位 `IncludeHiddenBodiesOrComponents` 之后调用。
- **配方一句话**：改覆盖值 → `Recalculate()` → 读属性。

## L11 `SelectedItems`

- **签名**：`System.object SelectedItems {get; set;}`
- **## Remarks（逐字）**："Pre-selected bodies/components are included in the returned array."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：已预选的实体/组件会被算进返回数组。
- **配方一句话**：**查不到**（无例子）。

## L12 `SetCoordinateSystem`

- **签名（1 个参数）**：`System.bool SetCoordinateSystem( System.object Coords )`
- **## Remarks / 官方例子 / 枚举**：**查不到**。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**（无例子；`Coords` 的类型官方未点名）。

## L13 `SetOverrideOptions`

- **签名（3 个参数）**：`System.bool SetOverrideOptions( System.object Options, System.int Config_option, System.object Config_names )`
- **## Remarks / 官方例子 / 枚举**：**查不到**（`Config_option` 的枚举**查不到**）。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：`SetOverrideOptions(Options, Config_option, Config_names)`；参数取值域**查不到**。

## L14 `ShowWeldBeadMass`

- **签名**：`System.bool ShowWeldBeadMass {get; set;}`
- **## Remarks（逐字）**："After setting this property to true, you can use [[IMassProperty2::WeldBeadMass]]."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：置 `true` 之后才能用 `WeldBeadMass`。
- **配方一句话**：`ShowWeldBeadMass = true` → 读 `WeldBeadMass`。

## L15 `SurfaceArea`

- **签名**：`System.double SurfaceArea {get;}`
- **## Remarks（逐字）**："If [[IMassProperty2::IncludeHiddenBodiesOrComponents]] is reset, then call [[IMassProperty2::Recalculate]] before using this property."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：复位 `IncludeHiddenBodiesOrComponents` 之后先 `Recalculate()`。
- **配方一句话**：`Recalculate()` → 读 `SurfaceArea`。

## L16 `UseSystemUnits`

- **签名**：`System.bool UseSystemUnits {get; set;}`
- **## Remarks（逐字）**："The default value is true. Thus, system units (meters, radians, and kilograms) are used by default. All properties returning a value are adjusted accordingly."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：默认 `true`，即系统单位（米、弧度、千克），所有返回值的属性随之换算。
- **配方一句话**：不设它就按系统单位读；要毫米值须显式改它（**官方未在本地源里给出改法细节**）。

## L17 `Volume`

- **签名**：`System.double Volume {get;}`
- **## Remarks（逐字）**："If [[IMassProperty2::IncludeHiddenBodiesOrComponents]] is reset, then call [[IMassProperty2::Recalculate]] before using this property."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：复位 `IncludeHiddenBodiesOrComponents` 之后先 `Recalculate()`。
- **配方一句话**：`Recalculate()` → 读 `Volume`。

## L18 `WeldBeadMass`

- **签名**：`System.double WeldBeadMass {get;}`
- **## Remarks（逐字）**："This property is valid only if [[IMassProperty2::ShowWeldBeadMass]] is set to true."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：只有 `ShowWeldBeadMass = true` 时才有效（官方逐字 "valid only if"）。
- **配方一句话**：`ShowWeldBeadMass = true` → 读 `WeldBeadMass`。

---

# M 组 · `IMassPropertyOverrideOptions`（13 个成员）

## M1 `GetOverrideCenterOfMassValue`

- **签名（1 个 out）**：`System.object GetOverrideCenterOfMassValue( out System.string CoordinateSystemName )`
- **## Remarks / 官方例子 / 枚举**：**查不到**。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**（写侧 `SetOverrideCenterOfMassValue` 的 Remarks 说"必须在 `OverrideCenterOfMass=true` 时才有效"，但本成员页没写）。
- **配方一句话**：**查不到**。

## M2 `GetOverrideMassValue`

- **签名（0 个参数）**：`System.double GetOverrideMassValue()`
- **## Remarks / 官方例子 / 枚举**：**查不到**。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**。

## M3 `GetOverrideMomentsOfInertiaValue`

- **签名（2 个 out）**：`System.object GetOverrideMomentsOfInertiaValue( out System.bool IsReferenceFrameSet, out System.string CoordinateSystemName )`
- **## Remarks / 官方例子 / 枚举**：**查不到**。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**。

## M4 `GetOverridePrincipalAxesOrientation`

- **签名（1 个参数）**：`System.object GetOverridePrincipalAxesOrientation( System.int Axis )`
- **## Remarks / 官方例子 / 枚举**：**查不到**。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**（`Axis` 取值域**查不到**）。
- **配方一句话**：**查不到**。

## M5 `GetOverridePrincipalMomentsOfInertia`

- **签名（0 个参数）**：`System.object GetOverridePrincipalMomentsOfInertia()`
- **## Remarks / 官方例子 / 枚举**：**查不到**。
- **废弃链**：无 Obsolete。
- **前置一句话**：**查不到**。
- **配方一句话**：**查不到**。

## M6 `OverrideCenterOfMass`

- **签名**：`System.bool OverrideCenterOfMass {get; set;}`
- **## Remarks（逐字）**："After setting this property to true, call [[IMassPropertyOverrideOptions::SetOverrideCenterOfMassValue]]."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：置 `true` 之后必须调 `SetOverrideCenterOfMassValue`。
- **配方一句话**：`OverrideCenterOfMass = true` → `SetOverrideCenterOfMassValue(...)` →（回到 `IMassProperty2`）`Recalculate()`。

## M7 `OverrideMass`

- **签名**：`System.bool OverrideMass {get; set;}`
- **## Remarks（逐字）**："After setting this property to true, call [[IMassPropertyOverrideOptions::SetOverrideMassValue]]."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：置 `true` 之后必须调 `SetOverrideMassValue`。
- **配方一句话**：`OverrideMass = true` → `SetOverrideMassValue(值)`。

## M8 `OverrideMomentsOfInertia`

- **签名**：`System.bool OverrideMomentsOfInertia {get; set;}`
- **## Remarks（逐字）**：
  > "After setting this property to true, call:
  > - [[IMassPropertyOverrideOptions::SetOverrideMomentsOfInertiaValue]]
  > - [[IMassPropertyOverrideOptions::SetOverridePrincipalAxesOrientation]]
  > - [[IMassPropertyOverrideOptions::SetOverridePrincipalMomentsOfInertia]]"
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：置 `true` 之后要调**三个**写侧方法。
- **配方一句话**：`OverrideMomentsOfInertia = true` → `SetOverrideMomentsOfInertiaValue` + `SetOverridePrincipalAxesOrientation` + `SetOverridePrincipalMomentsOfInertia`。

## M9 `SetOverrideCenterOfMassValue`

- **签名（2 个参数）**：`System.bool SetOverrideCenterOfMassValue( System.object Value, System.string CoordinateSystemName )`
- **## Remarks（逐字）**："This method is valid only if [[IMassPropertyOverrideOptions::OverrideCenterOfMass]] is set to true."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：只有 `OverrideCenterOfMass = true` 时才有效。
- **配方一句话**：`SetOverrideCenterOfMassValue(Value, CoordinateSystemName)`。

## M10 `SetOverrideMassValue`

- **签名（1 个参数）**：`System.bool SetOverrideMassValue( System.double Value )`
- **## Remarks（逐字）**："This method is valid only if [[IMassPropertyOverrideOptions::OverrideMass]] is set to true."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：只有 `OverrideMass = true` 时才有效。
- **配方一句话**：`SetOverrideMassValue(Value)`。

## M11 `SetOverrideMomentsOfInertiaValue`

- **签名（3 个参数）**：`System.bool SetOverrideMomentsOfInertiaValue( System.int ReferenceFrame, System.object Value, System.string CoordinateSystemName )`
- **## Remarks（逐字）**："This method is valid only if [[IMassPropertyOverrideOptions::OverrideMomentsOfInertia]] is set to true."
- **官方例子 / 枚举**：**查不到**（`ReferenceFrame` 的枚举**查不到**）。
- **废弃链**：无 Obsolete。
- **前置一句话**：只有 `OverrideMomentsOfInertia = true` 时才有效。
- **配方一句话**：`SetOverrideMomentsOfInertiaValue(ReferenceFrame, Value, CoordinateSystemName)`。

## M12 `SetOverridePrincipalAxesOrientation`

- **签名（3 个参数）**：`System.bool SetOverridePrincipalAxesOrientation( System.int Axis, System.object Value, System.bool AutoCorrect )`
- **## Remarks（逐字）**："This method is valid only if [[IMassPropertyOverrideOptions::OverrideMomentsOfInertia]] is set to true."
- **官方例子 / 枚举**：**查不到**（`Axis` 取值域**查不到**）。
- **废弃链**：无 Obsolete。
- **前置一句话**：只有 `OverrideMomentsOfInertia = true` 时才有效。
- **配方一句话**：`SetOverridePrincipalAxesOrientation(Axis, Value, AutoCorrect)`。

## M13 `SetOverridePrincipalMomentsOfInertia`

- **签名（1 个参数）**：`System.bool SetOverridePrincipalMomentsOfInertia( System.object Value )`
- **## Remarks（逐字）**："This method is valid only if [[IMassPropertyOverrideOptions::OverrideMomentsOfInertia]] is set to true."
- **官方例子 / 枚举**：**查不到 / 无**。 **废弃链**：无 Obsolete。
- **前置一句话**：只有 `OverrideMomentsOfInertia = true` 时才有效。
- **配方一句话**：`SetOverridePrincipalMomentsOfInertia(Value)`。

---

## 附录 · 本次抄录里所有「查不到」的清单（便于复核）

| 编号 | 对象 | 查不到的原因（实测） |
| --- | --- | --- |
| 0-a | `C:\swapi\types\IMold*` 目录 | 566 个类型目录里 0 个匹配 |
| 0-b | `C:\swapi\types\ICosting*` 目录 | 0 个匹配；全仓无 `Cost*` 命名 `.md` |
| 0-c | `ICostManager` 等 Costing 家族全部成员 | CHM 解包目录 `*sldcostingapi*` 文件数 = 0 |
| 0-d | `swcCostingType_e` / `swcBodyType_e` / `swcBodyStatus_e` 枚举 | `C:\swapi\enums\` 无同名文件 |
| 0-e | `swPatchType_e`（`swPatchTypeTangent` 的数值） | `C:\swapi\enums\swPatchType*.md` 0 命中；CHM `*swPatchType*` 0 命中 |
| F12 | `IShutOffSurfaceFeatureData::LoopEdges` 签名 | md 只有 frontmatter+标题；CHM 无该页 |
| F13 | `IShutOffSurfaceFeatureData::LoopPatchType` 签名 | 同上 |
| F15 | `SetAllPatchTypes` 的 `Type` 取值域 | 同上 + 枚举 `swPatchType_e` 缺失 |
| F16 | `IShutOffSurfaceFeatureData::Status` 的枚举语义 | 文件只有签名行，无 Remarks、无 CHM 页 |
| I5 | `IToolingSplitFeatureData::Depth` 签名 | md 只有 frontmatter+标题；CHM 无该页 |
| D7/D8/D9 | `GetFacesByType*` 的 `Type` 枚举 | 官方只给文字名 "negative, positive, and so on"，未点名枚举 |
| D5/D11 | `GetEntitiesToSplit` / `IGetEntitiesToSplit` 的 `TypeArr` 元素枚举 | 未点名 |
| H8/H11 | `GetExtractionDirection` / `SetExtractionDirection` 的 `Type1/Type2` 实体类型枚举 | 只给 6 个文字名 |
| L8 | `IMassProperty2::PrincipalAxesOfInertia` | swapi 无签名行；CHM 有（已抄） |
| H4/H7 | `ICoreFeatureData::Depth` / `EndCondition` | swapi 无签名行；CHM 有（已抄） |
| A3/A6/B1 | `InsertMoldShutOffSurface` / `MoldUndercutDetect2` / `MoldDraftAnalysis` 的前置 | 官方三处都没有 `## Remarks` 段 |
| A1–A6 | 模具 Insert* 方法的官方例子 | `C:\swapi\examples\` 中 0 个对应例子文件 |