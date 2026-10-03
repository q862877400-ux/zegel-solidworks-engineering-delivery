# api-06-features · IFeatureManager 特征域（高级）契约抄录

抄录员任务：只抄，不建议、不推断。每条给出**文件名 + 可搜索的原文片段**（不给行号）。

## 范围与来源

- **本轮范围**：`${SW}\types\IFeatureManager\` 下成员名（= 文件名）含
  `Boundary` / `CurveDriven` / `Combine` / `Intersect` / `Scale` / `FeatureRecogn` /
  `Dome` / `Rib` / `Wrap` / `Indent` / `Flex` / `Deform` 者；
  以及 `CreateDefinition.md` 里那张常量名单。
- **主源**：`C:\swapi\types\<接口>\<成员>.md`（签名与 Remarks）。
- **例子源**：`C:\swapi\examples\*.md`（只给调用序与实参）。
- **枚举源**：`C:\swapi\enums\*.md`。
- **数值补充源**：`D:\AI\SW\_raw\enum_values_sldworks.txt`
  （文件头自述：「来源: SolidWorks.Interop.swconst.dll · 方法: 对官方 interop 程序集的纯元数据读取（非实测）」）。
- **CHM 复核源**：`D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager_*.html`
  与 `…IFeatureManager~<成员>.html`。
- **筛选口径**：成员名 = `C:\swapi\types\IFeatureManager\` 下的**文件基名**。命中 **14** 个成员
  + `CreateDefinition`（名单另立一节）。

### ★ 三个关键词在本接口下「查不到」

`FeatureRecogn` / `Dome` / `Deform` 三组，在 `IFeatureManager` 下**查不到任何成员**。

- 证据 1 · `C:\swapi\types\IFeatureManager\` 目录清单：无 `*FeatureRecogn*`、无 `*Dome*`、无 `*Deform*` 文件
  （目录共 263 方法 + 23 属性，见 `_overview.md` 的 `method_count: 263` / `property_count: 23`）。
- 证据 2 · CHM `…IFeatureManager_members.html`：全文检索 `Dome` → 0 命中、`Recogn` → 0 命中、`Deform` → 0 命中。
- ⚠ 旁证（**不是** IFeatureManager 成员）：CHM 同目录下存在 `…IDomeFeatureData_members.html` 等
  ⇒ Dome 有**特征数据接口**，但 `IFeatureManager` 里**没有** Insert 类成员名。不做外推。

---

## 1. `IFeatureManager.InsertScale`

- **来源**：`C:\swapi\types\IFeatureManager\InsertScale.md`
- **1 · 精确签名**（★ **5 个参数**）：

  `Feature InsertScale( System.short Type, System.bool Uniform, System.double Xscale, System.double YScale, System.double ZScale )`

- **2 · `## Remarks` 逐字摘录**（原文）：

  > To scale a graphic body:
  >
  > 1. Select the graphic body in the Graphic Bodies folder of the FeatureManager design tree.
  >
  > 2. Call this method.
  >
  > This method scales the selected graphic body up in the graphics view, but no scale feature is created.
  >
  > **If Uniform is...** / **Then the scaling factor is...** / True → Xscale, applied in three directions. /
  > False → All three scaling factors (Xscale, YScale, and ZScale).
  >
  > Use [[IFeature::GetDefinition]] and [[IFeature::IGetDefinition]] and [[IFeature::ModifyDefinition]]
  > and [[IFeature::IModifyDefinition2]] to gain access to the [[IScaleFeatureData]] object.

  参数注记逐字：`Type`: Value as defined in [[swScaleType_e]]；`YScale`: Y direction scale factor;
  **valid only if Uniform is false**；`ZScale`: 同句 **valid only if Uniform is false**。
  返回（原文）：`[[IFeature]] if scaling the current model; Null or Nothing if scaling a selected graphic body`。
  CHM `…IFeatureManager~InsertScale.html` 复核：同一段 Remarks，尾部多一句
  `Availability SOLIDWORKS 2003 SP2, Revision Number 11.2`。
- **3 · 官方例子调用序** —— 文件 `C:\swapi\examples\Insert_Scale_Feature_Example_VB.md`
  （`## Examples` 里只有 VBA 这一个）：

  ```vbnet
  Set swFeatMgr = swModel.FeatureManager
  Set swScaleFeat = swFeatMgr.InsertScale(swScaleAboutOrigin, True, 3, 3, 3)
  If swScaleFeat Is Nothing Then Exit Sub
  Set swScale = swScaleFeat.GetDefinition
  Debug.Print " Scale = " & swScaleFeat.Name
  Debug.Print " Error (0 = no errors) = " & swScaleFeat.GetErrorCode
  ```

  例首 `Postconditions`：`1. Scales the part by a factor of 3.`
  ⇒ 实参：**Type = `swScaleAboutOrigin`（字面枚举名，非数字）· Uniform = True · 三个 factor 都给 3**
  ⇒ 调用序：**先无选择、只传参**（例子没做任何 SelectByID2）。
- **4 · 枚举**（`C:\swapi\enums\swScaleType_e.md`，`enum_member_count: 3`）：

  | Member | Value |
  | --- | --- |
  | swScaleAboutCentroid | 0 |
  | swScaleAboutCoordinateSystem | 2 |
  | swScaleAboutOrigin | 1 |

- **5 · 废弃链**：该成员**未标 Obsolete**（md 与 CHM 均无 `Obsolete` 字样）⇒ 不适用。
  CHM 只在尾部给 `Availability SOLIDWORKS 2003 SP2, Revision Number 11.2`。
- **前置一句话**：官方只写「缩放图形体时，须先在 FeatureManager 树的 Graphic Bodies 文件夹里选中那个图形体，再调用本方法」；缩放当前模型时官方没写任何选择前置。
- **配方一句话**：`InsertScale(swScaleAboutOrigin, True, 3, 3, 3)` —— 一个枚举名 + 一个 bool + 三个 double，然后 `GetDefinition()` 拿 `IScaleFeatureData`。

---

## 2. `IFeatureManager.InsertRib`

- **来源**：`C:\swapi\types\IFeatureManager\InsertRib.md`
- **1 · 精确签名**（★ **10 个参数**，返回 `void`）：

  `void InsertRib( System.bool Is2Sided, System.bool ReverseThicknessDir, System.double Thickness, System.int ReferenceEdgeIndex, System.bool ReverseMaterialDir, System.bool IsDrafted, System.bool DraftOutward, System.double DraftAngle, System.bool IsNormToSketch, System.bool IsDraftedFromWall )`

- **2 · `## Remarks` 逐字摘录**：**该 md 没有 `## Remarks` 节**（只有 `## Parameters` / `## Examples` / `## See Also`）；
  CHM `…IFeatureManager~InsertRib.html` 同样**没有 Remarks 节** ⇒ **前置文字查不到**。
  参数里唯一带前置语义的逐字句：
  `DraftOutward`: `True to draft the rib outward, false to not; only valid if IsDrafted is true`；
  `DraftAngle`: `Draft angle of the rib; only valid if IsDrafted is true`；
  `ReverseThicknessDir`: `True to thicken the opposite side of the sketch normal, false to not; only valid for single-sided ribs`。
- **3 · 官方例子调用序** —— 文件 `C:\swapi\examples\Get_Rib_Feature_Data_Example_CSharp.md`
  （另有 `_VB` / `_VBNET` 两份同题）：

  ```csharp
  boolstatus = Part.Extension.SelectByID2("Sketch2", "SKETCH", 0, 0, 0, false, 0, null, 0);
  Part.FeatureManager.InsertRib(true, false, 0.00254, 0, false, false, true, 0.0174532925199433, false, false);
  swSelMgr = (SelectionMgr)Part.SelectionManager;
  swFeat = (Feature)swSelMgr.GetSelectedObject6(1, -1);
  swRibFeat = (RibFeatureData2)swFeat.GetDefinition();
  ```

  ★ 选法：**`SelectByID2("Sketch2", "SKETCH", 0,0,0, append=false, mark=0)`** —— 选**草图**、**mark=0**。
  实参逐位：`Is2Sided=true · ReverseThicknessDir=false · Thickness=0.00254 · ReferenceEdgeIndex=0 · ReverseMaterialDir=false · IsDrafted=false · DraftOutward=true · DraftAngle=0.0174532925199433(≈1°) · IsNormToSketch=false · IsDraftedFromWall=false`。
  调用序：**先建草图 → 选草图(mark=0) → InsertRib → 从 SelectionManager 取特征 → GetDefinition()**。
  取特征那段例子原文：`swSelMgr = (SelectionMgr)Part.SelectionManager; swFeat = (Feature)swSelMgr.GetSelectedObject6(1, -1);`。
- **4 · 枚举**：签名里**没有**枚举型形参（全是 `bool`/`double`/`int`）⇒ 无枚举可抄。
  （`See Also` 指 `[[IRibFeatureData2 Interface]]`；例子里读的是 `swRibFeat.Type`，注释写
  `as defined in swRibType_e` —— 但 `swRibType_e` 不在本方法签名内，本节不抄。）
- **5 · 废弃链**：未标 Obsolete（md 无、CHM 无）⇒ 不适用。CHM 无 Availability 行。
- **前置一句话**：查不到（官方页没有 Remarks 节）；只能从例子读到「调用前先 `SelectByID2` 选中那张草图」。
- **配方一句话**：`SelectByID2("<草图名>", "SKETCH", 0,0,0, false, 0, null, 0)` → `InsertRib(true, false, <厚度>, 0, false, false, true, <拔模角>, false, false)` → `GetSelectedObject6(1,-1).GetDefinition()` 取 `RibFeatureData2`。

---

## 3. `IFeatureManager.InsertIndent`

- **来源**：`C:\swapi\types\IFeatureManager\InsertIndent.md`
- **1 · 精确签名**（★ **6 个参数**）：

  `Feature InsertIndent( System.double Thickness, System.double Clearance, System.bool Exclude, System.bool ClrDir, System.bool Cut, System.bool CutDir )`

- **2 · `## Remarks` 逐字摘录**（★ 这一句就是 mark 表）：

  > Prior to calling this method, you must have selected the target body and tool body regions, using these selection marks:
  >
  > - Target body = 1
  > - Tool body region = 4

  CHM `…IFeatureManager~InsertIndent.html` 逐字一致：`Target body = 1  Tool body region = 4`，
  尾部 `Availability SOLIDWORKS 2005 FCS, Revision Number 13.0`。
- **3 · 官方例子调用序** —— 文件 `C:\swapi\examples\Insert_Indent_Feature_Example_CSharp.md`：

  ```csharp
  status = swModelDocExt.SelectByID2("Boss-Extrude1", "SOLIDBODY", 0, 0, 0, false, 1, null, 0);
  status = swModelDocExt.SelectByID2("", "FACE", -0.0371343422566497, -0.0149999999999864, 0.0883053842352979, true, 4, null, 0);
  swFeatureMgr = (FeatureManager)swModel.FeatureManager;
  swFeature = (Feature)swFeatureMgr.InsertIndent(0.01, 0, true, true, false, false);
  ```

  ★ 选法两条**分两个 mark**：目标体 `"Boss-Extrude1"` / 类型 `"SOLIDBODY"` / **mark=1**；
  工具体区域 `""` / 类型 `"FACE"` / 给出点坐标 / **mark=4**。
  实参逐位：`Thickness=0.01 · Clearance=0 · Exclude=true · ClrDir=true · Cut=false · CutDir=false`。
  调用序：**先选目标体(mark 1) + 选工具面(mark 4) → 再调 InsertIndent → GetDefinition() → AccessSelections() → ModifyDefinition()**。
- **4 · 枚举**：签名里**无枚举型形参** ⇒ 无枚举可抄。
- **5 · 废弃链**：未标 Obsolete（md 与 CHM 均无）⇒ 不适用。
- **前置一句话**：调用前必须已选中目标体（mark = 1）与工具体区域（mark = 4）。
- **配方一句话**：`SelectByID2(<体名>,"SOLIDBODY",…,mark=1)` + `SelectByID2("","FACE",x,y,z,append=true,mark=4)` → `InsertIndent(0.01, 0, true, true, false, false)`。

---

## 4. `IFeatureManager.InsertFlexFeature`

- **来源**：`C:\swapi\types\IFeatureManager\InsertFlexFeature.md`
- **1 · 精确签名**（★ **17 个参数**）：

  `Feature InsertFlexFeature( System.double RotX, System.double RotY, System.double RotZ, System.double TanX, System.double TanY, System.double TanZ, System.double RadX, System.double RadY, System.double RadZ, System.double Angle, System.double PivotX, System.double PivotY, System.double PivotZ, System.int Type, System.double LeftTrim, System.double RightTrim, System.bool HardEdges )`

- **2 · `## Remarks` 逐字摘录**：**md 无 `## Remarks` 节**；CHM `…IFeatureManager~InsertFlexFeature.html`
  同样**没有 Remarks 节** ⇒ **前置文字查不到**。
  ★ 但 md 的一行描述句自带前置，逐字：`Inserts a Flex feature using the selected solid or surface body.`
  返回（原文）：`Pointer to the [[IFeature]] object`。
- **3 · 官方例子**：md 与 CHM 的 `## Examples` 段**都为空 / 缺**（CHM 该页 `Example` 处无条目）⇒ **查不到**。
- **4 · 枚举**：签名里的 `Type` 在 md 里是**内联整数表（不是 `[[…_e]]` 链接）**，逐字：

  | 值 | 原文 |
  | --- | --- |
  | -1 | None |
  | 0 | Bending |
  | 1 | Twisting |
  | 2 | Tapering |
  | 3 | Stretching |
  | 4 | Experimental |

  ⇒ md 未给该表起枚举名，也未在 `C:\swapi\enums\` 下提供对应 md ⇒ **枚举名查不到**。
- **5 · 废弃链**：未标 Obsolete（md 与 CHM 均无）⇒ 不适用。
- **前置一句话**：查不到（无 Remarks 节）；md 只在描述句里写「使用**已选中的**实体或曲面体」。
- **配方一句话**：查不到（官方没给这个成员的例子）。

---

## 5. `IFeatureManager.InsertWrapFeature`（Obsolete）

- **来源**：`C:\swapi\types\IFeatureManager\InsertWrapFeature.md`
- **1 · 精确签名**（★ **3 个参数**）：

  `Feature InsertWrapFeature( System.int Type, System.double Thickness, System.bool ReverseDir )`

- **2 · `## Remarks` 逐字摘录**（★ 整节就是 mark 表）：

  > Use [[IModelDocExtension::SelectByID2]] and these values to mark these selections:
  >
  > - 1 = Face on which to place the wrap feature
  > - 2 = Pull direction if Type is swWrapSketchType_e.swWrapSketchType_Emboss or swWrapSketchType_e.swWrapSketchType_Engrave
  > - 4 = 2D sketch of wrap feature; 3D sketches are invalid

  参数逐字：`Type`: Type of wrap as defined in [[swWrapSketchType_e]]；
  `Thickness`: **Thickness; 0.00001 (thinnest) - 10000 (thickest)**；`ReverseDir`: True to reverse …, false to not。
  返回（原文）：`Wrap [[feature]]`。CHM 复核一致 + `Availability SOLIDWORKS 2004 FCS, Revision Number 12.0`。
- **3 · 官方例子调用序** —— 文件 `C:\swapi\examples\Change_Wrap_Feature_Face_Example_CSharp.md`：

  ```csharp
  status = swModelDocExt.SelectByID2("Sketch11", "SKETCH", 0, 0, 0, false, 4, null, 0);
  status = swModelDocExt.SelectByID2("", "FACE", 3.03698880696047E-03, 0.036653462145523, -1.43855543627342E-03, true, 1, null, 0);
  swFeatureManager = (FeatureManager)swModel.FeatureManager;
  swFeature = (Feature)swFeatureManager.InsertWrapFeature(2, 0.001, false);
  swModel.ClearSelection2(true);
  ```

  ★ 选法：草图 **mark=4**（`"Sketch11"` / `"SKETCH"`）· 面 **mark=1**（`""` / `"FACE"` / 给点坐标）；
  ★ 本例 **不选 pull direction**（Type 走 `2`）。
  实参逐位：`Type=2`（裸整数，未加枚举名）· `Thickness=0.001` · `ReverseDir=false`。
  例子注释原文：`// Select the sketch of the rectangle and the // face where to scribe the sketch as a wrap feature`。
- **4 · 枚举**（`C:\swapi\enums\swWrapSketchType_e.md`，`enum_member_count: 3`；该 md 的 Value 列装的是**描述**）：

  | Member | Value（原文含描述） |
  | --- | --- |
  | swWrapSketchType_Emboss | `0 = Emboss creates a raised feature on the selected face or faces` |
  | swWrapSketchType_Engrave | `1 = Engrave, which appears as Deboss in the user interface, creates an indented feature on the selected face or faces` |
  | swWrapSketchType_Scribe | `2 = Scribe creates an imprint of the sketch contours on the selected face or faces` |

  ⇒ 例子里的 `Type=2` 即 `swWrapSketchType_Scribe`（对上表）。
- **5 · 废弃链**：md 首行逐字 `Obsolete. Superseded by [[IFeatureManager::InsertWrapFeature2]].`；
  CHM `…IFeatureManager~InsertWrapFeature.html` 逐字 `Obsolete. Superseded by IFeatureManager::InsertWrapFeature2 .`
  ⇒ ★ **官方点名的后继 = `IFeatureManager::InsertWrapFeature2`**。
- **前置一句话**：用 `SelectByID2` 按 mark 选 —— 面 = 1、pull 方向 = 2（仅 Emboss/Engrave）、2D 草图 = 4（3D 草图无效）。
- **配方一句话**：`SelectByID2(<草图>,"SKETCH",…,mark=4)` + `SelectByID2("","FACE",x,y,z,append=true,mark=1)` → `InsertWrapFeature(2, 0.001, false)`。

---

## 6. `IFeatureManager.InsertWrapFeature2`

- **来源**：`C:\swapi\types\IFeatureManager\InsertWrapFeature2.md`
- **1 · 精确签名**（★ **5 个参数**）：

  `Feature InsertWrapFeature2( System.int Type, System.double Thickness, System.bool ReverseDir, System.int Method, System.int MeshFactor )`

- **2 · `## Remarks` 逐字摘录**（★ mark 表 + 一条 NOTE）：

  > To select...
  > Use [[IModelDocExtension::SelectByID2]] or [[IModelDocExtension::SelectByRay]] and specify a Mark of...
  >
  > - One or more faces on which to place the wrap feature → **1**
  > - Pull direction entity if Type is: `swWrapSketchType_e.swWrapSketchType_Emboss` - or - `swWrapSketchType_e.swWrapSketchType_Engrave`
  >   → **2**
  >   （原文：`For a line or linear edge, the pull direction is the direction of the selected entity.
  >   For a plane, the pull direction is normal to the plane. To wrap the sketch normal to the sketch
  >   plane, do not select a pull direction entity.`）
  > - 2D sketch containing no open contours; 3D sketches are not supported → **4**
  >
  > **NOTE:** The difference between this method and the now obsolete [[IFeatureManager::InsertWrapFeature]]
  > is that IFeatureManager::InsertWrapFeature2 can create a wrap feature on one or more faces and
  > IFeatureManager::InsertWrapFeature creates a wrap feature on one face only.

  参数逐字：`Method`: Type of wrap method as defined in [[swWrapMethods_e]]；
  `MeshFactor`: **Accuracy of flattened triangle mesh; 1 (lowest) - 10 (highest)**。
  CHM 复核一致 + `Availability SOLIDWORKS 2017 FCS, Revision Number 25.0`。
- **3 · 官方例子调用序** —— 文件 `C:\swapi\examples\Create_Wrap_Feature_on_Multiple_Faces_Example_CSharp.md`：

  ```csharp
  status = swModelDocExt.SelectByID2("Sketch30", "SKETCH", 0, 0, 0, false, 4, null, 0);
  status = swModelDocExt.SelectByRay(-0.103709743982563, 0.00466186411857746, 0.0465727951450701, 1, 0, 0, 0.000421383417784414, 2, true, 1, 0);
  status = swModelDocExt.SelectByRay(-0.105251033879711, 0.0013155840361718, 0.0360382097004597, 1, 0, 0, 0.000421383417784414, 2, true, 1, 0);
  // …（同型 SelectByRay 共 6 行）
  swFeature = (Feature)swFeatureManager.InsertWrapFeature2((int)swWrapSketchType_e.swWrapSketchType_Scribe, 0.00254, false, (int)swWrapMethods_e.swWrapMethods_SplineSurface, 5);
  swModel.ClearSelection2(true);
  ```

  ★ 选法：草图 `SelectByID2("Sketch30","SKETCH",…, mark=4)`；
  ★ 6 个面用 **`SelectByRay`、每行倒数第二参 = `1`（mark）**（★ 与 `InsertWrapFeature` 的最大差别：
  这里**面用 mark 1 且可多个**）。例子注释原文：
  `//Select the sketch of the circle and the faces on which to wrap it //Because the type of wrap feature to create Scribe, no pull direction entity is selected`。
  实参逐位：`Type=(int)swWrapSketchType_e.swWrapSketchType_Scribe · Thickness=0.00254 · ReverseDir=false ·
  Method=(int)swWrapMethods_e.swWrapMethods_SplineSurface · MeshFactor=5`。
- **4 · 枚举**：
  - `C:\swapi\enums\swWrapSketchType_e.md`（同第 5 节表格，3 成员）**复用**。
  - `C:\swapi\enums\swWrapMethods_e.md`（`enum_member_count: 2`）：

    | Member | Value |
    | --- | --- |
    | swWrapMethods_Analytical | 0 |
    | swWrapMethods_SplineSurface | 1 |

    ⇒ 例子里的 `Method` 即 `swWrapMethods_SplineSurface`。
- **5 · 废弃链**：本成员**未标 Obsolete**（自身是 `InsertWrapFeature` 的后继，见第 5 节）⇒ 不适用。
- **前置一句话**：`SelectByID2` 或 `SelectByRay` 选 —— 一个或多个面 mark=1、pull 方向 mark=2（仅 Emboss/Engrave）、无开放轮廓的 2D 草图 mark=4。
- **配方一句话**：草图 mark=4 + 6 个 `SelectByRay(…, 1)` → `InsertWrapFeature2((int)swWrapSketchType_Scribe, 0.00254, false, (int)swWrapMethods_SplineSurface, 5)`。

---

## 7. `IFeatureManager.InsertCombineFeature`

- **来源**：`C:\swapi\types\IFeatureManager\InsertCombineFeature.md`
- **1 · 精确签名**（★ **3 个参数**）：

  `Feature InsertCombineFeature( System.int OperationType, Body2 MainBody, System.object ToolVar )`

- **2 · `## Remarks` 逐字摘录**（★ mark 表）：

  > You can either call this method, directly passing in the bodies with MainBody and ToolVar, or you can:
  >
  > 1. Select the bodies using [[IModelDocExtension::SelectByID2]] as follows:
  >
  >    | To select... | Use Mark... |
  >    | MainBody | 1 |
  >    | ToolVar bodies | 2 |
  >
  > 2. Call this method, setting MainBody to Nothing or null and ToolVar to an empty array.
  >
  > See the SOLIDWORKS Help for more information about the combine feature.

  `MainBody` 取值表逐字（`## Parameters` 内）：
  `swBodyOperationType_e.SWBODYADD` → `Nothing or null`；
  `swBodyOperationType_e.SWBODYCUT` → `Target [[body]]`；
  `swBodyOperationType_e.SWBODYINTERSECT` → `Nothing or null`；末尾 `(See **Remarks**)`。
  CHM 复核一致 + `Availability SOLIDWORKS 2003 FCS, Revision Number 11.0`。
- **3 · 官方例子调用序** —— 文件 `C:\swapi\examples\Combine_Bodies_Example_CSharp.md`：

  ```csharp
  status = swModelDocExt.SelectByID2("Extrude-Thin1", "SOLIDBODY", 0, 0, 0, true, 0, null, 0);
  status = swModelDocExt.SelectByID2("Boss-Extrude1", "SOLIDBODY", 0, 0, 0, true, 0, null, 0);
  swModel.ClearSelection2(true);
  status = swModelDocExt.SelectByID2("Extrude-Thin1", "SOLIDBODY", 0, 0, 0, false, 2, null, 0);
  status = swModelDocExt.SelectByID2("Boss-Extrude1", "SOLIDBODY", 0, 0, 0, true, 2, null, 0);
  swFeatureMgr = (FeatureManager)swModel.FeatureManager;
  swFeature = (Feature)swFeatureMgr.InsertCombineFeature((int)swBodyOperationType_e.SWBODYADD, null, null);
  swCombineBodiesFeatureData = (CombineBodiesFeatureData)swFeature.GetDefinition();
  status = swCombineBodiesFeatureData.AccessSelections(swModel, null);
  ```

  ★ 调用序要点（例子逐字）：**先 mark=0 试选一遍 → `ClearSelection2(true)` → 再按 mark=2 重选 →
  然后 `InsertCombineFeature((int)swBodyOperationType_e.SWBODYADD, null, null)`**（`MainBody` 与 `ToolVar` 都传 `null`）。
  ★ 例子注释里的另一套枚举值原文：
  `//swCombineBodiesOperationType_e: // swCombineBodiesOperationAdd = 0 // swCombineBodiesOperationCommon = 2 // swCombineBodiesOperationSubract = 1`。
- **4 · 枚举**（`C:\swapi\enums\swBodyOperationType_e.md`，`enum_member_count: 3`）：

  | Member | Value |
  | --- | --- |
  | SWBODYADD | 15903 |
  | SWBODYCUT | 15902 |
  | SWBODYINTERSECT | 15901 |

- **5 · 废弃链**：未标 Obsolete ⇒ 不适用。`See Also` 点名 `[[IFeatureManager::IInsertCombineFeature Method]]`（姊妹条，不是后继）。
- **前置一句话**：要么直接传 MainBody + ToolVar，要么先 `SelectByID2` 按 MainBody = mark 1、ToolVar bodies = mark 2 选中、再把 MainBody 传 Nothing/null 且 ToolVar 传空数组。
- **配方一句话**：先 mark=0 试选 → `ClearSelection2(true)` → mark=2 重选 → `InsertCombineFeature((int)swBodyOperationType_e.SWBODYADD, null, null)`。

---

## 8. `IFeatureManager.IInsertCombineFeature`

- **来源**：`C:\swapi\types\IFeatureManager\IInsertCombineFeature.md`
- **1 · 精确签名**（★ **4 个参数**，第三个是 `ref`）：

  `Feature IInsertCombineFeature( System.int OperationType, Body2 MainBody, System.int ToolsCount, ref Body2 ToolsArr )`

- **2 · `## Remarks` 逐字摘录**：与 `InsertCombineFeature` **同文**（MainBody = mark 1 / ToolVar bodies = mark 2 / 空数组），
  末尾一句 md 原文是 `See the SOLIDWORKS Help for more information about the **combined** feature.`
  （★ 注意这里写的是 *combined*，非第 7 节的 *combine* —— 两页原文不同，逐字照抄，不改）。
  ★ 本成员**独有**的可用性约束（`## Parameters` 内逐字）：

  > - **ToolsArr**:
  >   - in-process, unmanaged C++: Pointer to an array of [[bodies]] to combine of size ToolsCount (see **Remarks**)
  >   - VBA, VB.NET, C#, and C++/CLI: **Not supported**
  >
  >   See [In-process Methods](<../../docs/Programming with the SOLIDWORKS API/In-process Methods.md>) for details about this type of method.

  CHM `…IFeatureManager~IInsertCombineFeature.html` 同一段 `in-process, unmanaged C++: Pointer to an array of …`。
- **3 · 官方例子**：md 与 CHM **都没有 `## Examples` 节** ⇒ **查不到**（CHM 该页无 Example 条目）。
- **4 · 枚举**：`OperationType` 仍是 `[[swBodyOperationType_e]]`，成员与值同第 7 节（`SWBODYADD=15903` / `SWBODYCUT=15902` / `SWBODYINTERSECT=15901`）。
- **5 · 废弃链**：未标 Obsolete ⇒ 不适用。`See Also` 点名 `[[IFeatureManager::InsertCombineFeature Method]]`（姊妹条）。
- **前置一句话**：同 `InsertCombineFeature`（MainBody = mark 1、ToolVar bodies = mark 2）；另明写 `ToolsArr` 在 VBA/VB.NET/C#/C++/CLI 下 **Not supported**，仅 in-process 非托管 C++ 可用。
- **配方一句话**：查不到（官方没给这个成员的例子；且参数说明写明只有 in-process 非托管 C++ 能调）。

---

## 9. `IFeatureManager.PreIntersect`（Obsolete）

- **来源**：`C:\swapi\types\IFeatureManager\PreIntersect.md`
- **1 · 精确签名**（★ **1 个参数**）：

  `System.object PreIntersect( System.bool CapPlanar )`

- **2 · `## Remarks` 逐字摘录**（★ 两条前置/后置，逐字）：

  > Before calling this method, you must select the intersecting [[surfaces]], [[solids]], or [[planes]] that make up the intersect feature.
  >
  > After calling this method, call [[IFeatureManager::PostIntersect]] to create the intersect feature.

  参数逐字：`CapPlanar`: True to cap the flat openings of surfaces to define closed volumes, false to not。
  返回（原文）：`Array of intersect [[bodies]]`。
- **3 · 官方例子调用序** —— 文件 `C:\swapi\examples\Get_Intersect_Feature_Data_Example_VB.md`（另有 `_VBNET` / `_CSharp`）：

  ```vbnet
  vResultingBodies = swFeatMgr.PreIntersect(False) 'Do not cap planar surface openings of intersect feature
  swModel.ClearSelection2 True
  Set swFeat = swFeatMgr.PostIntersect(intToExclude, True, False)
  ```

  例首 `Preconditions` 逐字：`' 3. Multi-select Surface-Extrude1, Boss-Extrude3, and Boss-Extrude4 in the ' '    FeatureManager design tree and press F5.`
  ⇒ ★ 调用序：**在树上多选（例子没写 mark）→ PreIntersect(False) → ClearSelection2 True → PostIntersect(...)**。
- **4 · 枚举**：签名里无枚举型形参 ⇒ 无枚举可抄。
- **5 · 废弃链**：md 首行逐字 `Obsolete. Superseded by [[IFeatureManager::PreIntersect2]].`；
  CHM `…IFeatureManager~PreIntersect.html` 逐字 `Obsolete. Superseded by IFeatureManager::PreIntersect2 .`
  ⇒ ★ **官方点名的后继 = `IFeatureManager::PreIntersect2`**。
- **前置一句话**：调用前必须已选中构成相交特征的 [[surfaces]] / [[solids]] / [[planes]]；调用后必须接着调 `PostIntersect`。
- **配方一句话**：`PreIntersect(False)` → `ClearSelection2 True` → `PostIntersect(intToExclude, True, False)`。

---

## 10. `IFeatureManager.PreIntersect2`

- **来源**：`C:\swapi\types\IFeatureManager\PreIntersect2.md`
- **1 · 精确签名**（★ **2 个参数**）：

  `System.object PreIntersect2( System.bool CapPlanar, System.int RegionType )`

- **2 · `## Remarks` 逐字摘录**：

  > Before calling this method, you must select the intersecting [[surfaces]], [[solids]], or [[planes]] that make up the intersect feature.
  >
  > After calling this method, call [[IFeatureManager::PostIntersect]] to create the intersect feature.

  `RegionType` 内联整数表逐字：`0 = Intersecting regions` / `1 = Internal regions` / `2 = Intersecting and internal regions`。
  返回（原文）：`Array of intersecting [[bodies]]`。
  CHM 复核一致 + `Availability SOLIDWORKS 2016 FCS, Revision Number 24.0`。
- **3 · 官方例子调用序** —— 文件 `C:\swapi\examples\Create_Intersect_Feature_Example_CSharp.md`：

  ```csharp
  status = swModelDocExt.SelectByID2("Shell1", "SOLIDBODY", 0, 0, 0, true, 0, null, 0);
  status = swModelDocExt.SelectByID2("Plane6", "PLANE", 0, 0, 0, true, 0, null, 0);
  bodyArray = (object[])swFeatureMgr.PreIntersect2(false, 1);
  swModel.ClearSelection2(true);
  nbrBodies = bodyArray.GetUpperBound(0);
  bodyExcludeArray = new bool[nbrBodies + 1];
  excludeArray = bodyExcludeArray;
  swFeature = swFeatureMgr.PostIntersect(excludeArray, true, false);
  ```

  ★ 选法：`"Shell1"` / `"SOLIDBODY"` 与 `"Plane6"` / `"PLANE"`，两条都 **mark=0**、都 append=true。
  实参逐位：`CapPlanar=false · RegionType=1`（例子注释逐字：`// * Create internal regions`）。
  ★ 例子必须按 `GetUpperBound(0)` 把排除数组开到 `nbrBodies + 1`（逐字 `new bool[nbrBodies + 1]`）。
- **4 · 枚举**：签名里无 `[[…_e]]` 型形参；`RegionType` 是 md 内联整数表（见上）⇒ 无枚举 md 可抄。
- **5 · 废弃链**：未标 Obsolete（自身是 `PreIntersect` 的后继，见第 9 节）⇒ 不适用。
- **前置一句话**：调用前必须已选中相交的 surfaces/solids/planes；调用后必须接着调 `PostIntersect`。
- **配方一句话**：`SelectByID2(<体名>,"SOLIDBODY",…,mark=0)` + `SelectByID2("Plane6","PLANE",…,mark=0)` → `PreIntersect2(false, 1)` → `ClearSelection2(true)` → `PostIntersect(excludeArray, true, false)`。

---

## 11. `IFeatureManager.PostIntersect`

- **来源**：`C:\swapi\types\IFeatureManager\PostIntersect.md`
- **1 · 精确签名**（★ **3 个参数**）：

  `Feature PostIntersect( System.object IntersectionsToExclude, System.bool Merge, System.bool Consume )`

- **2 · `## Remarks` 逐字摘录**（★ 一条前置，逐字）：

  > Before calling this method, you must call [[IFeatureManager::PreIntersect]] to obtain the intersect bodies.

  参数逐字：`IntersectionsToExclude`: Array of booleans indicating which bodies returned by
  [[IFeatureManager::PreIntersect]] to exclude from this intersect feature；
  `Merge`: True to merge all intersect regions into one body, false to not；
  `Consume`: True to remove input surfaces from the FeatureManager design tree, false to not。
  ★ 注意：本方法名为 `PostIntersect`，但 md 的前置句**点名的是 `PreIntersect`**（不是 `PreIntersect2`）—— 逐字照抄。
- **3 · 官方例子调用序** —— 两个例子都调它，逐字并列：
  - `C:\swapi\examples\Get_Intersect_Feature_Data_Example_VB.md`：

    ```vbnet
    Dim boolArr(3) As Boolean
    boolArr(0) = False
    boolArr(1) = True 'Exclude region, vResultingBodies(2), from the intersect feature
    boolArr(2) = False
    boolArr(3) = False
    intToExclude = boolArr
    Set swFeat = swFeatMgr.PostIntersect(intToExclude, True, False)
    ```

  - `C:\swapi\examples\Create_Intersect_Feature_Example_CSharp.md`：

    ```csharp
    swFeature = swFeatureMgr.PostIntersect(excludeArray, true, false);
    ```

  ⇒ 实参逐位：`IntersectionsToExclude` = 长度 `n+1` 的 bool 数组（**例子里是 4 元素的 `boolArr(3)`**）· `Merge=True/true` · `Consume=False/false`。
- **4 · 枚举**：签名里无枚举型形参 ⇒ 无枚举可抄。
- **5 · 废弃链**：未标 Obsolete（md 与 CHM 均无）⇒ 不适用。
- **前置一句话**：调用前必须先调 `IFeatureManager::PreIntersect` 拿到相交体数组。
- **配方一句话**：`PostIntersect(intToExclude, True, False)` —— 第一个实参是与相交区域个数对齐的 bool 数组。

---

## 12. `IFeatureManager.InsertSplitLineIntersect`

- **来源**：`C:\swapi\types\IFeatureManager\InsertSplitLineIntersect.md`
- **1 · 精确签名**（★ **1 个参数**）：

  `Feature InsertSplitLineIntersect( System.int CompleteOption )`

- **2 · `## Remarks` 逐字摘录**：**md 无 `## Remarks` 节**；CHM `…IFeatureManager~InsertSplitLineIntersect.html`
  同样**没有 Remarks 节** ⇒ **前置文字查不到**。
  ★ 但 md 的一行描述句自带前置，逐字：
  `Creates split lines using the selected intersecting tool and target entities.`
  `CompleteOption` 内联整数表逐字：`1 = Linear` / `7 = Natural` / `9 = Split all and linear` / `15 = Split all and natural`。
  返回（原文）：`Pointer to the [[IFeature]] object`。
- **3 · 官方例子**：md 与 CHM **都没有 `## Examples` 节** ⇒ **查不到**。
  CHM `See Also` 只点名 `IFeatureManager Interface` / `IFeatureManager Members` / `ISplitLineFeatureData Interface` /
  `IModelDoc2::InsertSplitLineProject Method` / `IModelDoc2::InsertSplitLineSil Method`。
- **4 · 枚举**：签名里无 `[[…_e]]` 型形参；`CompleteOption` 是 md 内联整数表（见上）⇒ 无枚举 md 可抄。
- **5 · 废弃链**：未标 Obsolete（md 与 CHM 均无）⇒ 不适用。
- **前置一句话**：查不到（官方页没有 Remarks 节）；只有描述句写「用**已选中的**相交工具实体与目标实体」。
- **配方一句话**：查不到（官方没给这个成员的例子；`CompleteOption` 只在 md 里给了 1/7/9/15 四个裸值）。

---

## 13. `IFeatureManager.FeatureLocalCurveDrivenPattern`（Obsolete）

- **来源**：`C:\swapi\types\IFeatureManager\FeatureLocalCurveDrivenPattern.md`
- **1 · 精确签名**（★ **13 个参数**）：

  `Feature FeatureLocalCurveDrivenPattern( System.bool FlipDir1, System.int Num1, System.bool EqualSpacing1, System.double Spacing1, System.int ReferencePoint, System.int CurveMethod, System.int AlignMethod, System.bool Direction2, System.bool FlipDir2, System.int Num2, System.bool EqualSpacing2, System.double Spacing2, System.bool PatternSeedOnly )`

- **2 · `## Remarks` 逐字摘录**（★ mark 表，含一条 NOTE）：

  > **To select...** / **Use a mark of...**
  >
  > - Components to pattern → **1**
  > - Curve, edge, sketch, or sketch entity for Direction 1 → **2**
  > - Curve, edge, sketch, or sketch entity for Direction 2 → **4**
  > - Reference point for ReferencePoint → **32**
  >
  >   **NOTE:** If ReferencePoint is set to swLocalSketchPatternReferencePoint_e.swLocalSketchPatternSelectedPoint,
  >   then the selected reference point must be a vertex.
  >
  > - Face on which a 3D curve lies → **64**

  参数注记逐字：`Spacing1`: … **when EqualSpacing1 is set to false**；`Spacing2`: … **when EqualSpacing2 is set to false**。
  返回（原文）：`Local curve pattern [[feature]]`。
  ★ md 的 NOTE 里引用的是 **`swLocalSketchPatternReferencePoint_e`**，而形参 `ReferencePoint` 声明的枚举是
  `[[swLocalCurvePatternReferencePoint_e]]` —— ★ **两页原文不一致，逐字照抄，不替官方改**。
- **3 · 官方例子**：md **没有 `## Examples` 节**（只有 `## See Also`，且只列 `IFeatureManager Interface` /
  `IFeatureManager Members`）；CHM `…IFeatureManager~FeatureLocalCurveDrivenPattern.html` 同样无 Example ⇒ **查不到**。
- **4 · 枚举**（三份 md 都在 `C:\swapi\enums\`，且都在反射转储 `enum_values_sldworks.txt` 里逐值对上）：

  `swLocalCurvePatternReferencePoint_e`（`enum_member_count: 3`）

  | Member | Value（md） | Value（反射转储） |
  | --- | --- | --- |
  | swLocalCurvePatternSelectedPoint | 0 | `swLocalCurvePatternSelectedPoint = 0` |
  | swLocalCurvePatternBoundingBoxCenter | 1 | `swLocalCurvePatternBoundingBoxCenter = 1` |
  | swLocalCurvePatternComponentOrigin | 2 | `swLocalCurvePatternComponentOrigin = 2` |

  `swLocalCurvePatternCurveMethod_e`（`enum_member_count: 2`）

  | Member | Value（md） | Value（反射转储） |
  | --- | --- | --- |
  | swLocalCurvePatternTransformCurve | 0 | `swLocalCurvePatternTransformCurve = 0` |
  | swLocalCurvePatternOffsetCurve | 1 | `swLocalCurvePatternOffsetCurve = 1` |

  `swLocalCurvePatternAlignment_e`（`enum_member_count: 2`）

  | Member | Value（md） | Value（反射转储） |
  | --- | --- | --- |
  | swLocalCurvePatternTangentToCurve | 0 | `swLocalCurvePatternTangentToCurve = 0` |
  | swLocalCurvePatternAlignToSeed | 1 | `swLocalCurvePatternAlignToSeed = 1` |

- **5 · 废弃链**：md 首行逐字
  `Obsolete. See [[IFeatureManager::CreateFeature]] and the Remarks in [[ILocalCurvePatternFeatureData]].`；
  CHM 逐字 `Obsolete. See IFeatureManager::CreateFeature and the Remarks in ILocalCurvePatternFeatureData .`
  ⇒ ★ **官方点名的后继 = `IFeatureManager::CreateFeature`（并转向 `ILocalCurvePatternFeatureData` 的 Remarks）**。
- **前置一句话**：按 mark 选 —— 要阵列的组件 = 1、方向 1 的曲线/边/草图/草图实体 = 2、方向 2 的同类 = 4、参考点 = 32（若取 `swLocalSketchPatternSelectedPoint` 则必须选顶点）、3D 曲线所在面 = 64。
- **配方一句话**：查不到（官方没给这个成员的例子）；可用路径按官方 Obsolete 指向 `CreateFeature` + `ILocalCurvePatternFeatureData`。

---

## 14. `IFeatureManager.SetFreeformBoundaryContinuity`

- **来源**：`C:\swapi\types\IFeatureManager\SetFreeformBoundaryContinuity.md`
- **1 · 精确签名**（★ **2 个参数**，返回 `void`）：

  `void SetFreeformBoundaryContinuity( System.short BoundaryIndex, System.short Continuity )`

- **2 · `## Remarks` 逐字摘录**（★ 这段是**官方对 Freeform 全族的限制声明**，逐字）：

  > The SOLIDWORKS API Freeform-related methods are intended to journal the actions performed by an
  > interactive user while creating the feature. Because user interaction is required to create a Freeform
  > feature, **fully automating the creation of it is not possible using the SOLIDWORKS API.**
  >
  > The typical steps performed by an interactive user to create a Freeform feature are:
  >
  > 1. Select the face to form.
  > 2. Add curves on the selected face. Corresponds to [[IFeatureManager::SetFreeformCurveData]].
  > 3. Add points on the curves. Corresponds to [[IFeatureManager::SetFreeformPointData]].
  > 4. Specify boundary continuity. Corresponds to IFeatureManager::SetFreeformBoundaryContinuity.
  >    Interactively pull or push the points to change the shape of the selected face.
  > 5. Insert the Freeform feature. Corresponds to this method, [[IFeatureManager::InsertFreeform2]].
  >
  > Record a macro while interactively creating a Freeform feature, then examine the macro to see the
  > order in which the Freeform-related methods are recorded.

  参数逐字：`BoundaryIndex`: **0-based index of the boundary to modify (i.e., a value ranging from 0 to (Number of face boundaries-1))**；
  `Continuity` 内联整数表逐字（★ 官方拼写照抄，含错字）：

  | 值 | 原文 |
  | --- | --- |
  | -1 | `Movaeable` |
  | 0 | `Contact` |
  | 1 | `Tangenet` |
  | 2 | `Curvature` |

- **3 · 官方例子**：md 与 CHM **都没有 `## Examples` 节** ⇒ **查不到**；
  官方给的做法逐字是 `Record a macro while interactively creating a Freeform feature, then examine the macro…`。
- **4 · 枚举**：签名里无 `[[…_e]]` 型形参；`Continuity` 是 md 内联整数表（见上）⇒ 无枚举 md 可抄。
- **5 · 废弃链**：未标 Obsolete（md 与 CHM 均无）⇒ 不适用。
- **前置一句话**：官方明说 Freeform 族方法只是用来 journal 交互用户的动作，**用它完全自动化建 Freeform 特征是不可能的**。
- **配方一句话**：查不到（官方没给例子）；官方指定的顺序是 选面 → `SetFreeformCurveData` → `SetFreeformPointData` → **本方法** → `InsertFreeform2`，中间还需交互拉/推点。

---

## 15. `IFeatureManager.CreateDefinition` 的常量名单（★ 35 个）

- **来源**：`C:\swapi\types\IFeatureManager\CreateDefinition.md`
- **1 · 精确签名**（★ **1 个参数**）：

  `System.object CreateDefinition( System.int Type )`

  CHM `…IFeatureManager~CreateDefinition.html` 的 .NET Syntax 逐字一致：
  `System.object CreateDefinition( System.int Type )`（VB 侧逐字：
  `Function CreateDefinition( ByVal Type As System.Integer ) As System.Object`）。
- **2 · `## Remarks` 逐字摘录**（★ 三段全抄）：

  > This method initializes the feature data objects with default data for pattern, sweep, bounding box,
  > ground plane, mirror components, projection curve, sheet metal normal cut, sheet metal swept flange,
  > sheet metal gusset, sheet metal edge flange, tab/slot, library form tool, and belt/chain features.
  >
  > For sheet metal base flange, sheet metal corner relief, convert solid to sheet metal, library, simple
  > fillet, and thread features, you must initialize feature data objects using specific initialize methods.
  >
  > For mate controller features, you can either pre-select mates before calling this method or initialize
  > the feature data object returned by this method with default values.

  ★ CHM 同一段逐字一致（仅多 `&nbsp;` 空格与尾部 `Availability` 行，md 里没有）。
  返回（原文）：`… or pattern-specific feature data object (see **Remarks**); Nothing or null otherwise`。
- **3 · 官方例子调用序** —— 文件 `C:\swapi\examples\Create_a_Thread_Feature_Example_CSharp.md`
  （另有 `_VB` / `_VBNET`；CHM 三个 Example 条目同名）：

  ```csharp
  FeatMgr = swModel.FeatureManager;
  //Create and initialize a thread feature data object
  swThreadFeatData = (ThreadFeatureData)FeatMgr.CreateDefinition((int)swFeatureNameID_e.swFmSweepThread);
  swThreadFeatData.InitializeThreadData();
  //Specify the thread method type as extrude
  swThreadFeatData.ThreadMethod = 1;
  //Select the thread's starting edge
  boolstatus = swModel.Extension.SelectByRay(0.011047195612548, -0.0190800402080527, -0.000365739009737354, 0.164466301431523, -0.479983539625146, -0.861723063044243, 0.00160036844432164, 1, false, 1, 0);
  pEdge = (Edge)((SelectionMgr)(swModel.SelectionManager)).GetSelectedObject6(1, -1);
  swThreadFeatData.Edge = pEdge;
  swModel.ClearSelection2(true);
  //Create the thread feature
  swFeat = FeatMgr.CreateFeature(swThreadFeatData);
  ```

  ★ 调用序（逐字三步）：
  `CreateDefinition((int)swFeatureNameID_e.swFmSweepThread)` → **`InitializeThreadData()`**（★ 对应 Remarks 的
  「thread 特征必须用特定的 initialize 方法」）→ 选实体填进 data → `CreateFeature(data)`。
  ★ 两条 `SelectByRay` 的**倒数第一参 = 1**（mark），例子对 edge 用 mark=1、对 up-to reference 也用 mark=1。
- **4 · 枚举** ★ 就是本节主题 —— `[[swFeatureNameID_e]]` 的那 35 个常量。
  ⚠ `C:\swapi\enums\swFeatureNameID_e.md` 的 `Value` 列**装的是描述、不是数值**（该文件 `enum_member_count: 130`，
  表里 130 行都是英文描述）。
  ⇒ 下面「数值」列**取自** `D:\AI\SW\_raw\enum_values_sldworks.txt` 的 `## swFeatureNameID_e` 段
  （该文件头自述为「对官方 interop 程序集的纯元数据读取（非实测）」）。
  ⇒ 「括注」列逐字抄自 `CreateDefinition.md` 的 `## Parameters`，并与 CHM
  `…IFeatureManager~CreateDefinition.html` 的参数段**逐字比对一致**（两处都是同样 35 条、同样括注、同样顺序）。

  | # | 常量 | 括注（CreateDefinition.md 原文） | 数值（反射转储） |
  | --- | --- | --- | --- |
  | 1 | swFmBaseFlange | (sheet metal base flange) | `swFmBaseFlange = 34` |
  | 2 | swFmBeltAndChain | (belt/chain) | `swFmBeltAndChain = 119` |
  | 3 | swFmBoundingBox | (bounding box) | `swFmBoundingBox = 114` |
  | 4 | swFmCirPattern | (circular pattern) | `swFmCirPattern = 5` |
  | 5 | swFmCornerRelief | (sheet metal corner relief) | `swFmCornerRelief = 120` |
  | 6 | swFmCurvePattern | (curve-driven pattern) | `swFmCurvePattern = 103` |
  | 7 | swFmDerivedLPattern | (derived-driven pattern) | `swFmDerivedLPattern = 28` |
  | 8 | swFmDimPattern | (variable/dimension pattern) | `swFmDimPattern = 107` |
  | 9 | swFmEdgeFlange | (sheet metal edge flange) | `swFmEdgeFlange = 37` |
  | 10 | swFmFillet | (constant radius, face, full round fillet/chamfer) | `swFmFillet = 1` |
  | 11 | swFmFillPattern | (fill pattern) | `swFmFillPattern = 105` |
  | 12 | swFmFormToolInstance | (library form tool) | `swFmFormToolInstance = 73` |
  | 13 | swFmGroundPlane | (ground plane) | `swFmGroundPlane = 113` |
  | 14 | swFmLibraryFeature | (library) | `swFmLibraryFeature = 69` |
  | 15 | swFmLocalChainPattern | (chain component pattern) | `swFmLocalChainPattern = 112` |
  | 16 | swFmLocalCirPattern | (circular component pattern) | `swFmLocalCirPattern = 109` |
  | 17 | swFmLocalCurvePattern | (curve-driven component pattern) | `swFmLocalCurvePattern = 110` |
  | 18 | swFmLocalLPattern | (linear component pattern) | `swFmLocalLPattern = 108` |
  | 19 | swFmLocalSketchPattern | (sketch-driven component pattern) | `swFmLocalSketchPattern = 111` |
  | 20 | swFmLPattern | (linear pattern) | `swFmLPattern = 6` |
  | 21 | swFmMateController | (mate controller) | `swFmMateController = 127` |
  | 22 | swFmMirrorComponent | (mirror components) | `swFmMirrorComponent = 116` |
  | 23 | swFmNormalCut | (sheet metal normal cut) | `swFmNormalCut = 115` |
  | 24 | swFmRefCurve | (projection curve) | `swFmRefCurve = 14` |
  | 25 | swFmRefSurface | (surface sweep) | `swFmRefSurface = 62` |
  | 26 | swFmSketchBend | (sheet metal sketched bend) | `swFmSketchBend = 35` |
  | 27 | swFmSketchPattern | (sketch-driven pattern) | `swFmSketchPattern = 104` |
  | 28 | swFmSMGusset | (sheet metal gusset) | `swFmSMGusset = 118` |
  | 29 | swFmSolidToSheetMetal | (convert solid to sheet metal) | `swFmSolidToSheetMetal = 128` |
  | 30 | swFmSweep | (boss sweep) | `swFmSweep = 17` |
  | 31 | swFmSweepCut | (cut sweep) | `swFmSweepCut = 18` |
  | 32 | swFmSweepThread | (sweep thread) | `swFmSweepThread = 87` |
  | 33 | swFmSweptFlange | (sheet metal swept flange) | `swFmSweptFlange = 117` |
  | 34 | swFmTabAndSlot | (tab and slot) | `swFmTabAndSlot = 88` |
  | 35 | swFmTablePattern | (table pattern) | `swFmTablePattern = 106` |

  ★ 抄录时可核的三处交叉点（只作可核验陈述，不作建议）：
  - 名单里的 `swFmSweepThread = 87`、`swFmSketchBend = 35`、`swFmOneBend`（**不在名单里**，转储值 `swFmOneBend = 33`）。
  - `swFeatureNameID_e.md` 的描述列对这 35 条也一一可对上（如 `swFmSweep | Sweep boss`、
    `swFmNormalCut | Sheet metal normal cut`、`swFmTabAndSlot | Tab and Slot`）—— ★ 但它的「值」是描述，
    **不能当数值读**。
- **5 · 废弃链**：`CreateDefinition` 本身**未标 Obsolete** ⇒ 不适用。
  但它 `See Also` 点名的两个后继式条目（是「改用 initialize 方法」的指向，不是本方法的后继）：
  `ILibraryFeatureData::Initialize Method` · `IThreadFeatureData::InitializeThreadData Method` ·
  `ISimpleFilletFeatureData2::Initialize Method` · `IBaseFlangeFeatureData::Initialize Method ()` ·
  `ICornerReliefFeatureData::Initialize` · `IMateControllerFeatureData::Initialize Method ()` ·
  `IConvertSolidFeatureData::Initialize Method ()`；以及完成链 `IFeature::GetDefinition Method` /
  `IFeature::IGetDefinition Method` / `IFeatureManager::CreateFeature Method`。
- **前置一句话**：查不到（`## Remarks` 没有「Before calling」式的选择前置；它只区分「哪些常量需再调专属 initialize 方法」与「哪些返回默认数据」）。
- **配方一句话**：`CreateDefinition((int)swFeatureNameID_e.<常量>)` → 对 base flange / corner relief / solid-to-sheet-metal / library / simple fillet / thread 这六类**必须**再调各自的 `Initialize*`，再 `IFeatureManager::CreateFeature(data)`。

---

## 抄录过程中记下的「官方原文自相矛盾 / 拿不准」清单（只记，不判）

1. `IInsertCombineFeature.md` 的 `ToolsArr` 说明里 `ToolsCount` 是本成员自己的形参名，但 `## Remarks`
   整段却写 `setting MainBody to Nothing or null and **ToolVar** to an empty array` —— `ToolVar` 是
   姊妹成员 `InsertCombineFeature` 的形参名。CHM 同一页也是 `ToolVar`。⇒ 两页原文如此，未改。
2. `IInsertCombineFeature.md` 末句写 `combined feature`，`InsertCombineFeature.md` 写 `combine feature`。
3. `FeatureLocalCurveDrivenPattern.md` 的 NOTE 引用 `swLocalSketchPatternReferencePoint_e`，
   而形参声明的是 `swLocalCurvePatternReferencePoint_e`（两个不同枚举，前者另有
   `swLocalSketchPatternReferencePoint_e = 0 / BoundingBoxCenter = 1 / ComponentOrigin = 2`，见反射转储）。
4. `SetFreeformBoundaryContinuity.md` 的 `Continuity` 表里官方把 `Movaeable` / `Tangenet` 拼错了（照抄）。
5. `InsertFlexFeature.md` 的 `Type` 给了 6 个裸值但**没给枚举名**，`C:\swapi\enums\` 下也查不到对应 md。
6. `InsertRib` / `InsertFlexFeature` / `InsertSplitLineIntersect` / `FeatureLocalCurveDrivenPattern` /
   `SetFreeformBoundaryContinuity` / `IInsertCombineFeature` 六个成员**官方没给例子**（md 与 CHM 双侧都查不到）。
7. 关键词筛选口径：按**成员名**命中 14 个。若按「正文里出现该词」命中，还会多出
   `InsertNetBlend` / `InsertNetBlend2`（正文含 “boundary feature/boundary surface feature”）与
   `InsertCutSurface`（正文含 “intersect”）。这三个**不在本轮交付**，留给调用方定夺。