# api-01 · 曲面域 · 官方契约抄录

**抄录员**：契约抄录员（只读源、只写本文件）
**范围**：① `C:\swapi\types\IFeatureManager\` 下名字含 Sweep / Boundary / Trim / Knit / Extend / Thicken / Untrim / Fill / Loft 的成员；
② `C:\swapi\types\IModeler\` 下 `Create*Surface` 全族（含标 Obsolete 的与它们的 `*2` 后继）；
③ 这些名字在 `C:\swapi\examples\*.md` 与 CHM 解包 `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\` 里出现的例子与 Remarks。

**纪律**：只写亲手读到的；每条给**文件名 + 可搜索原文片段**（★ 不写行号）；查不到就写「查不到」；不给建议、不下结论。

---

## 〇 · 本路的源覆盖事实（先说清楚，避免下游误读）

| 事实 | 依据 |
|---|---|
| ★ `C:\swapi\types\IModeler\` 下 **`Create*Surface` 全族共 17 个**（含 4 个 Obsolete + 4 个 `*2` 后继），本文件逐条抄完。 | 目录列举 `C:\swapi\types\IModeler\*.md` |
| ★ **CHM 解包里查不到 `IModeler` 接口页** —— 对 `sldworksapi\*.html` / `*.htm` 搜 `IModeler Interface`、`CreateToroidalSurface`、`CreateSweptSurface` 均 0 命中；目录里 8729 个 `.html` 无一个文件名含 `Modeler`。⇒ **IModeler 族的 CHM 侧 = 查不到**；本文件对 IModeler 成员只抄 `C:\swapi\types\IModeler\*.md` + `C:\swapi\examples\*.md` 两源。 | 在 `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\` 做的文件名列举与内容 grep |
| ★ `IFeatureManager` 侧 CHM 页存在，且与 `C:\swapi\types\*.md` **逐字一致**（我核对了 `InsertSweepSurface3` / `InsertUntrimSurface2` / `FeatureCutThicken` / `GetPreTrimmedBodies` 四页的 Remarks）。 | CHM 页 `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~<Member>.html` 的 `remarksSection` 段 |
| ★ `IFeatureManager` 目录里**没有任何名字含 `Knit` 的成员**（grep `Knit` 命中的全是**形参名** `KnitResult` / `KnitFlag` / `KnitTolerance` / `BKnit`）。**曲面 knit 特征的实际入口是 `InsertSewRefSurface`**（返回类型接口写的是 `ISurfaceKnitFeatureData Interface`）⇒ 本文件把它按「Knit 域」收进来抄。 | `C:\swapi\types\IFeatureManager\*.md` grep `Knit`；`InsertSewRefSurface.md` 的 See Also |
| ★ `InsertUntrimSurface2` 的**内嵌 VBA 官方例子只存在于 CHM 页**，`C:\swapi\types\IFeatureManager\InsertUntrimSurface2.md` 的 Examples 段是**空的** ⇒ 这是本文件唯一一处「例子只在 CHM」。 | CHM 页 `...~InsertUntrimSurface2.html` 的 `exampleSection` 段 |
| `swGuideCurveInfluence_e` / `swSurfaceTrimType_e` 不出现在**任何一条本文件成员的签名里**（只出现在例子的代码里）⇒ 按抄录纪律，它们不是「签名里出现的枚举」，只在相关例子里点名引用。 | 例 `Insert_Fill-surface_Feature_Example_VB.md` / `Create_Trimmed_Surface_Feature_Example_VB.md` |

**枚举全表（本次抄到的）**

| 枚举 | 成员与数值 | 源文件 |
|---|---|---|
| `swTwistControlType_e` | `swTwistControlFollowPath`=0 · `swTwistControlKeepNormalConstant`=1 · `swTwistControlFollowPathFirstGuideCurve`=2 · `swTwistControlFollowFirstSecondGuideCurves`=3 · `swTwistControlConstantTwistAlongPath`=8 · `swTwistControlNormalConstantTwistAlongPath`=9（共 6） | `C:\swapi\enums\swTwistControlType_e.md` |
| `swTangencyType_e` | `swTangencyNone`=0 · `swTangencyNormalToProfile`=1 · `swTangencyDirectionVector`=2 · `swTangencyAllFaces`=3 · `swMinimumTwist`=10（共 5） | `C:\swapi\enums\swTangencyType_e.md` |
| `swSweepDirection_e` | `swSweepDirection1`=0 · `swSweepBidirectional`=1 · `swSweepDirection2`=2（共 3） | `C:\swapi\enums\swSweepDirection_e.md` |
| `swFaceUntrimType_e` | `swFaceUntrimTypeAllEdges`=0 · `swFaceUntrimTypeInternalEdges`=1 · `swFaceUntrimTypeExternalEdges`=2（共 3） | `C:\swapi\enums\swFaceUntrimType_e.md` |
| `swEdgeUntrimType_e` | `swEdgeUntrimTypeConnectEndPoints`=1 · `swEdgeUntrimTypeExtendEdges`=2（共 2） | `C:\swapi\enums\swEdgeUntrimType_e.md` |
| `swThickenThicknessType_e` | `swThickenSideOne`=0 · `swThickenSideTwo`=1 · `swThickenSideBoth`=2（共 3） | `C:\swapi\enums\swThickenThicknessType_e.md` |
| `swThickenDirection_e` | `swThickenDirection_Side1`=0 · `swThickenDirection_Side2`=1 · `swThickenDirection_Both`=2（共 3） | `C:\swapi\enums\swThickenDirection_e.md` |
| `swFeatureFillSurfaceOptions_e` | Bitmask：`swOptimizeSurface`=1 或 0x1 · `swTryToFormSolid`=2 或 0x2 · `swMergeResult`=4 或 0x4 · `swReverseDirection`=8 或 0x8 · `swReverseSurface`=16 或 0x10（共 5） | `C:\swapi\enums\swFeatureFillSurfaceOptions_e.md` |
| `swContactType_e` | `swContact`=0 · `swTangent`=1 · `swCurvature`=2（共 3） | `C:\swapi\enums\swContactType_e.md` |

---

# 一 · `IFeatureManager`

## 1. `IFeatureManager.InsertSweepSurface`

**1) 精确签名（7 个参数）** —— `C:\swapi\types\IFeatureManager\InsertSweepSurface.md`
```
Feature InsertSweepSurface( System.bool Propagate, System.short TwistCtrlOption, System.bool KeepTangency, System.bool ForceNonRational, System.short StartMatchingType, System.short EndMatchingType, System.short PathAlign )
```
逐参数在该页写的是 `Propagate: No description` · `TwistCtrlOption: No description` · `KeepTangency: No description` · `ForceNonRational: No description` · `StartMatchingType: No description` · `EndMatchingType: No description` · `PathAlign: No description`。

**2) `## Remarks` 逐字摘录** —— **查不到**。该 md 全文只有 front matter、`Obsolete. Superseded by [[IFeatureManager::InsertSweepSurface2]].` 一行、签名、参数表、See Also，**没有 `## Remarks` 段**；CHM 页 `...~InsertSweepSurface.html` 也没有 `remarksSection`。★ 该页也**没有 `## Examples` 段**。

**3) 官方例子的调用序** —— **查不到**（该页无 Examples；`C:\swapi\examples\` 里只有 `InsertSweepSurface3` 的例子，见第 3 节）。

**4) 枚举**：签名里 `TwistCtrlOption` / `StartMatchingType` / `EndMatchingType` 在本页**没有点名任何枚举**（写的是 `No description`）⇒ 该成员自身点名的枚举 = 查不到（`*2` / `*3` 才点名，见下）。

**5) 废弃链**：**Obsolete. Superseded by `[[IFeatureManager::InsertSweepSurface2]]`**（逐字，原文首段）。后继 `InsertSweepSurface2` 有签名 + 完整 Remarks。

**前置一句话**：查不到（该页无 Remarks，只写了 Obsolete 与 `Superseded by`）。
**配方一句话**：查不到（该页无 Examples）。

---

## 2. `IFeatureManager.InsertSweepSurface2`

**1) 精确签名（11 个参数）** —— `C:\swapi\types\IFeatureManager\InsertSweepSurface2.md`
```
Feature InsertSweepSurface2( System.bool Propagate, System.short TwistCtrlOption, System.bool KeepTangency, System.bool BAdvancedSmoothing, System.short StartMatchingType, System.short EndMatchingType, System.short PathAlign, System.bool UseFeatScope, System.bool UseAutoSelect, System.double TwistAngle, System.bool BMergeSmoothFaces )
```
逐参数原文要点：`Propagate` = "True propagates the sweep to the next edge, false causes the sweep to occur only on the selected edge; to propagate to the next edge, the next edge must be tangent to the current edge"；`TwistCtrlOption` = "Twist control option as defined in [[swTwistControlType_e]]"；`StartMatchingType` / `EndMatchingType` = "Tangency type as defined in [[swTangencyType_e]]"；`PathAlign` = "Align path type (see **Remarks**)"；`TwistAngle` = "If TwistCtrlOption set to swTwistControlType_e.swTwistControlConstantTwistAlongPath, then specify end twist angle"。

**2) `## Remarks` 逐字摘录**（整段）——
> Because you are creating a surface, the sections can be open.
>
> Use [[IModelDocExtension::SelectByID2]] to select the profile and sweep curves. The mark for:
>
> - 1 = Profile selection
> - 2 = Guide curve selection, if provided
> - 4 = Sweep path
>
> The PathAlign argument is available when TwistCtrlOption is set to swTwistControlType_e.swTwistControlFollowPath and can take one of these values:
>
> - 0 = None; no correction (default)
> - 2 = Direction vector; a plane, planar face, or line defines the path
> - 3 = All faces; includes neighboring faces
>
> When UseAutoSelect is false, the user must select the bodies that the feature will affect.

★ 与第 3 节 `InsertSweepSurface3` 逐字比对：**第 1 个 mark 的措辞不同** —— `*2` 写 "1 = Profile selection"，`*3` 写 "1 = **Sketch** profile"。

**3) 官方例子的调用序** —— **查不到**（该页无 `## Examples` 段；CHM 页 `...~InsertSweepSurface2.html` 的 `exampleSection` 为空）。

**4) 枚举**：`swTwistControlType_e`（见本文件开头全表）· `swTangencyType_e`（`StartMatchingType` / `EndMatchingType`）· 另有 `PathAlign` 的**内联取值表** `0 / 2 / 3`（官方没给这个参数的枚举名 ⇒ 枚举名 = 查不到，只有 Remarks 里的字面数值）。

**5) 废弃链**：**Obsolete. Superseded by `[[IFeatureManager::InsertSweepSurface3]]`**（逐字）。

**前置一句话**：用 `SelectByID2` 先选轮廓与扫掠曲线，**mark 1 = 轮廓 · 2 = 引导线（可选）· 4 = 扫掠路径**；`UseAutoSelect=false` 时用户还必须自己选体。
**配方一句话**：查不到（该页无 Examples）。

---

## 3. `IFeatureManager.InsertSweepSurface3`

**1) 精确签名（14 个参数）** —— `C:\swapi\types\IFeatureManager\InsertSweepSurface3.md`
```
Feature InsertSweepSurface3( System.bool Propagate, System.int TwistCtrlOption, System.bool KeepTangency, System.bool BAdvancedSmoothing, System.int StartMatchingType, System.int EndMatchingType, System.int PathAlign, System.bool UseFeatScope, System.bool UseAutoSelect, System.double TwistAngle, System.bool BMergeSmoothFaces, System.bool CircularProfile, System.double CircularProfileDiameter, System.int Direction )
```
★ 与 `*2` 的类型差：`TwistCtrlOption` / `StartMatchingType` / `EndMatchingType` / `PathAlign` 由 **`System.short` 变 `System.int`**；`*3` 多 3 个参数 `CircularProfile` / `CircularProfileDiameter` / `Direction`。

**2) `## Remarks` 逐字摘录**（整段）——
> SOLIDWORKS 2018 introduces a new sweep architecture, making this method obsolete. See [Sweep Features and SweepFeatureData Objects] to create this sweep surface.
>
> Because you are creating a surface, the sections can be open.
>
> Use [[IModelDocExtension::SelectByID2]] to select the sketch profile and sweep curves. Specify these marks:
>
> - 1 = Sketch profile
> - 2 = Guide curve, if provided
> - 4 = Sweep path
>
> The PathAlign argument is available when TwistCtrlOption is set to swTwistControlType_e.swTwistControlFollowPath and can take one of these values:
>
> - 0 = None; no correction (default)
> - 2 = Direction vector; a plane, planar face, or line defines the path
> - 3 = All faces; includes neighboring faces
>
> When UseAutoSelect is false, the user must select the bodies that the feature will affect.
>
> Direction only applies to sketch profiles and only when the sketch profile is not coincident with an end of the path.

★ CHM 页 `...~InsertSweepSurface3.html` 的 `remarksSection` 与此**逐字相同**（含 "1 = Sketch profile"）。

**3) 官方例子的调用序** —— 例文件名 **`C:\swapi\examples\Create_Surface-sweep_Feature_Example_VB.md`**（另有 `_VBNET.md` / `_CSharp.md` 同名三份）。该页 `Examples` 段逐字列：
`Create Surface-sweep Feature (C#)` · `Create Surface-sweep Feature (VB.NET)` · `Create Surface-sweep Feature (VBA)`。

调用序（逐字抄 `Create_Surface-sweep_Feature_Example_VB.md` 的代码块，先选什么 + 实参）：
```vbnet
'Create another sketch
status = swModelDocExt.SelectByID2("Right Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0)
swSketchManager.InsertSketch True
Set swSketchSegment = swSketchManager.CreateLine(-0#, 0#, 0#, 0.021042, 0.091756, 0#)
...
swModel.ClearSelection2 True
swSketchManager.InsertSketch True
'Insert surface sweep
status = swModelDocExt.SelectByID2("Sketch2", "SKETCH", 0, 0, 0, False, 1, Nothing, 0)
status = swModelDocExt.SelectByID2("Sketch1", "SKETCH", 0, 0, 0, True, 4, Nothing, 0)
Set swFeatureManager = swModel.FeatureManager
Set swFeature = swFeatureManager.InsertSweepSurface3(False, 0, False, False, 0, 0, 0, True, True, 0, True, False, 0, 0)
```
★ 实参对位（14 个，与签名同序）：`Propagate=False, TwistCtrlOption=0, KeepTangency=False, BAdvancedSmoothing=False, StartMatchingType=0, EndMatchingType=0, PathAlign=0, UseFeatScope=True, UseAutoSelect=True, TwistAngle=0, BMergeSmoothFaces=True, CircularProfile=False, CircularProfileDiameter=0, Direction=0`。
★ 先选什么：`SelectByID2("Sketch2","SKETCH",…, mark=1)`，再 `SelectByID2("Sketch1","SKETCH",…, Append=True, mark=4)`。

**4) 枚举**：`swTwistControlType_e` · `swTangencyType_e`（`StartMatchingType` / `EndMatchingType`）· `swSweepDirection_e`（`Direction` = "Direction as defined in [[swSweepDirection_e]]"）。三者成员与数值见本文件开头全表。

**5) 废弃链**：本页首段逐字 **"Obsolete. See **Remarks**."** —— ★ **没有点名任何后继方法名**。Remarks 点名的是文档章节 `Sweep Features and SweepFeatureData Objects`；同页 See Also 点名接口 `[[ISweepFeatureData Interface]]`。
⇒ **「后继方法」= 查不到**（官方只给了接口族，没给方法名）。

**前置一句话**：用 `SelectByID2` 先选草图轮廓与扫掠曲线，**mark 1 = 草图轮廓 · 2 = 引导线（可选）· 4 = 扫掠路径**；`UseAutoSelect=false` 时用户还必须自己选体。
**配方一句话**：先 `SelectByID2("Sketch2","SKETCH",0,0,0,False,1,Nothing,0)` 再 `SelectByID2("Sketch1","SKETCH",0,0,0,True,4,Nothing,0)`，然后 `InsertSweepSurface3(False, 0, False, False, 0, 0, 0, True, True, 0, True, False, 0, 0)`（例 `Create_Surface-sweep_Feature_Example_VB.md`）。

---

## 4. `IFeatureManager.InsertUntrimSurface`

**1) 精确签名（4 个参数）** —— `C:\swapi\types\IFeatureManager\InsertUntrimSurface.md`
```
Feature InsertUntrimSurface( System.int FaceUntrimType, System.int EdgeUntrimType, System.double Distance, System.bool BMerge )
```
逐参数原文：`FaceUntrimType`: "Untrim face as defined in [[swFaceUntrimType_e]]"；`EdgeUntrimType`: "Untrim edge as defined in [[swEdgeUntrimType_e]]"；`Distance`: "Distance by which to untrim surface"；`BMerge`: "True to create a surface extension that merges with the original surface, false to create a new, separate surface body"。

**2) `## Remarks` 逐字摘录**（整段，只有两句）——
> You must preselect the face or the edges you want to untrim.

**3) 官方例子的调用序** —— **查不到**（该页无 `## Examples` 段；CHM 页 `...~InsertUntrimSurface.html` 的 `exampleSection` 为空）。

**4) 枚举**：`swFaceUntrimType_e`（`swFaceUntrimTypeAllEdges`=0 / `swFaceUntrimTypeInternalEdges`=1 / `swFaceUntrimTypeExternalEdges`=2）· `swEdgeUntrimType_e`（`swEdgeUntrimTypeConnectEndPoints`=1 / `swEdgeUntrimTypeExtendEdges`=2）。

**5) 废弃链**：**Obsolete. Superseded by `[[IFeatureManager::InsertUntrimSurface2]]`**（逐字）。

**前置一句话**：必须**预选**要取消裁剪的面或边（"You must preselect the face or the edges you want to untrim."）。
**配方一句话**：查不到（该页无 Examples）。

---

## 5. `IFeatureManager.InsertUntrimSurface2`

**1) 精确签名（5 个参数）** —— `C:\swapi\types\IFeatureManager\InsertUntrimSurface2.md`
```
Feature InsertUntrimSurface2( System.int FaceUntrimType, System.int EdgeUntrimType, System.double Distance, System.bool BMerge, System.bool BTrimOppositeSide )
```
逐参数原文：`FaceUntrimType` = "Untrim face edge type as defined by [[swFaceUntrimType_e]]; **valid only if a face is selected**"；`EdgeUntrimType` = "Connect endpoints or extend edges as defined by [[swEdgeUntrimType_e]]; **valid only of one or more edges are selected**"；`BTrimOppositeSide` = "True to remove the surface outside the selected surface edges or interior surface holes, false to not; **valid only if BMerge is false**"。

**2) `## Remarks` 逐字摘录**（整段）——
> This method:
>
> - is valid only for surface parts.
> - requires preselection of the face or edges you want to untrim.
>
> For learn more about Untrim Surfaces, see the **SOLIDWORKS Help > Parts and Features > Features > Surfaces > Surface Controls > Untrim Surface** topic.

★ CHM 页 `...~InsertUntrimSurface2.html` 的 `remarksSection` 逐字相同（"is valid only for surface parts." / "requires preselection of the face or edges you want to untrim."）。
★ CHM 页 `Availability` 段逐字：**"SOLIDWORKS 2024 FCS, Revision Number 32"**。

**3) 官方例子的调用序** —— ★ **`C:\swapi\types\IFeatureManager\InsertUntrimSurface2.md` 的 Examples 段是空的**；例子**只在 CHM 页** `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~InsertUntrimSurface2.html` 的 `exampleSection` 段内（原文标注 `'VBA`）。逐字抄调用序尾部：
```vb
Part.SelectionManager.EnableContourSelection = True
boolstatus = Part.Extension.SelectByID2("Sketch1", "SKETCHREGION", 2.26345552080154E-02, -0.013184045043844, 0, True, 1, Nothing, 0)
boolstatus = Part.InsertPlanarRefSurface()
Part.ClearSelection2 True
boolstatus = Part.Extension.SelectByRay(-4.08355377464196E-02, 1.83176555033939E-02, 0, 0, 0, -1, 7.93376161930438E-04, 2, True, 0, 0)
Part.FeatureManager.InsertUntrimSurface2 0, 2, 0, False, True
Part.SelectionManager.EnableContourSelection = False
```
★ 先选什么：先用 `SelectByID2("Sketch1","SKETCHREGION",…, mark=1)` 建 `Surface-Plane1`，`ClearSelection2` 之后用 **`SelectByRay(...)`** 打射线做那笔「预选」，紧接着调用。
★ 实参对位（5 个，与签名同序）：`FaceUntrimType=0, EdgeUntrimType=2, Distance=0, BMerge=False, BTrimOppositeSide=True`。

**4) 枚举**：`swFaceUntrimType_e`（=0 即 `swFaceUntrimTypeAllEdges`）· `swEdgeUntrimType_e`（=2 即 `swEdgeUntrimTypeExtendEdges`）· `swContactType_e` **不在这条签名里**（查不到）。

**5) 废弃链**：**本页首段没有 `Obsolete` 字样** ⇒ 不是 Obsolete；CHM 页也无 `Obsolete`（我逐页 grep 过 `Obsolete`）。它本身是 `*1` 的后继。

**前置一句话**：只对**曲面零件**有效，且**必须预选**要取消裁剪的面或边（`FaceUntrimType` 仅当选了面有效、`EdgeUntrimType` 仅当选了一条以上边有效、`BTrimOppositeSide` 仅当 `BMerge=false` 有效）。
**配方一句话**：`SelectByRay(...)` 预选之后 `Part.FeatureManager.InsertUntrimSurface2 0, 2, 0, False, True`（例只在 CHM 页 `...~InsertUntrimSurface2.html`）。

---

## 6. `IFeatureManager.InsertFillSurface`

**1) 精确签名（1 个参数）** —— `C:\swapi\types\IFeatureManager\InsertFillSurface.md`
```
Feature InsertFillSurface( System.int Resolution )
```
逐参数原文：`Resolution`: `No description`。★ 该页**没有 `## Returns` 段**。

**2) `## Remarks` 逐字摘录** —— **查不到**（该页无 `## Remarks` 段；CHM 页 `...~InsertFillSurface.html` 无 `remarksSection`）。

**3) 官方例子的调用序** —— **查不到**（该页无 `## Examples` 段；CHM 页 `exampleSection` 为空）。

**4) 枚举**：**查不到**（签名只出现 `System.int Resolution`，该页没点名任何枚举，也没写取值）。

**5) 废弃链**：**Obsolete. Superseded by `[[IFeatureManager::InsertFillSurface2]]`**（逐字）。

**前置一句话**：查不到。
**配方一句话**：查不到。

---

## 7. `IFeatureManager.InsertFillSurface2`

**1) 精确签名（6 个参数）** —— `C:\swapi\types\IFeatureManager\InsertFillSurface2.md`
```
Feature InsertFillSurface2( System.int Resolutions, System.int Options, System.object VPatchBoundaries, System.object VCurvatureControlType, System.object VFaces, System.object VConstraintCurves )
```
逐参数原文：`Resolutions` = "Controls the resolution or quality of the surface (see **Remarks**)"；`Options` = "Options as defined in [[swFeatureFillSurfaceOptions_e]]"；`VPatchBoundaries` = "Array of [[edges]] or [[sketches]] for the patch boundaries"；`VCurvatureControlType` = "Array of curve control methods as defined in [[swContactType_e]]"；`VFaces` = "Array of [[faces]] to use for direction"；`VConstraintCurves` = "Array of constraint curves ([[edges]] or [[sketches]])"。

**2) `## Remarks` 逐字摘录**（整段）——
> You must use [[IModelDocExtension::SelectByID2]] and the following Mark values to select edges that bound the surface to be filled:
>
> - Boundary curves = 1
> - Boundary with contact curvature control = 257
> - Boundary with tangent curvature control = 513
> - Constraint curves or internal curves = 4
>
> The resolution argument can be set to 1, 2, or 3. The higher the value, the better the resolution.
>
> Use the [[IBody2::Diagnose]] and the [[IDiagnoseResult]] APIs to get the gaps to fill.

★ CHM 页 `...~InsertFillSurface2.html` 的 `exampleSection` 存在（737 字符），与 md 的 Examples 段一致。

**3) 官方例子的调用序** —— 例文件名 **`C:\swapi\examples\Insert_Fill-surface_Feature_Example_VB.md`**（另有 `_VBNET.md` / `_CSharp.md`；md 的 Examples 段另列 `Get_and_Fill_Gaps_in_Body` 三份）。

调用序（先选什么 + 实参）：
```vbnet
'Get the sketch for the fill-surface feature
status = swModelDocExt.SelectByID2("Sketch2", "SKETCH", -3.09259362651374E-02, -1.50632202505945E-02, 2.65529245975468E-02, True, 257, Nothing, swSelectOptionDefault)
Set swSelMgr = swModel.SelectionManager
Set selObj = swSelMgr.GetSelectedObject6(1, 257)
'Insert the fill-surface feature
Set swFeat = swFeatMgr.InsertFillSurface2(2, swOptimizeSurface, selObj, swContact, Nothing, Nothing)
```
★ 实参对位（6 个）：`Resolutions=2, Options=swOptimizeSurface, VPatchBoundaries=selObj, VCurvatureControlType=swContact, VFaces=Nothing, VConstraintCurves=Nothing`。
★ 先选什么：`SelectByID2("Sketch2","SKETCH",…, mark=257)`（= Remarks 里的 "Boundary with contact curvature control"），再 `GetSelectedObject6(1, 257)` 取对象。

另一例 **`C:\swapi\examples\Get_and_Fill_Gaps_in_Body_Example_VB.md`**（走 `IBody2::Diagnose` 路线）：
```vbnet
swSelData.Mark = 257
nNumGap = swDiagnose.GetGapsCount
...
vCoEdgeArr = swDiagnose.GetCoEdgesAtGap(i - 1)
For Each vCoEdge In vCoEdgeArr
    Set swCoEdge = vCoEdge
    Set swEdge = swCoEdge.GetEdge
    Set swEnt = swEdge
    bRet = swEnt.Select4(True, swSelData)
Next vCoEdge
Set swFeat = swFeatMgr.InsertFillSurface2(3, swOptimizeSurface, swSelData, swContact, Nothing, Nothing)
```
★ 这里第 3 个实参传的是 **`swSelData`（SelectData 对象）** 而不是取出来的实体对象，`Resolutions=3`。

**4) 枚举**：`swFeatureFillSurfaceOptions_e`（Bitmask，例子用 `swOptimizeSurface`=1 或 0x1）· `swContactType_e`（例子用 `swContact`=0）。全表见本文件开头。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样**（CHM 页亦无）⇒ 不是 Obsolete；它是 `InsertFillSurface` 的后继。

**前置一句话**：用 `SelectByID2` 选界定要填充曲面的边，**mark 1 = 边界曲线 · 257 = 带接触曲率控制的边界 · 513 = 带切向曲率控制的边界 · 4 = 约束曲线/内部曲线**。
**配方一句话**：`SelectByID2("Sketch2","SKETCH",…,True,257,Nothing,…)` → `GetSelectedObject6(1,257)` → `InsertFillSurface2(2, swOptimizeSurface, selObj, swContact, Nothing, Nothing)`（例 `Insert_Fill-surface_Feature_Example_VB.md`）。

---

## 8. `IFeatureManager.PreTrimSurface`

**1) 精确签名（4 个参数）** —— `C:\swapi\types\IFeatureManager\PreTrimSurface.md`
```
System.bool PreTrimSurface( System.bool BMutualTrimIn, System.bool BSplitSystemIn, System.bool BSplitLinearIn, System.bool BRemovePickedIn )
```
逐参数原文：`BMutualTrimIn` = "True to use the selected intersecting surfaces as the trimming surfaces (mutual), false to use the selected surface, plane, or sketch as the trim tool (standard)"；`BSplitSystemIn` = "True to let the SOLIDWORKS Design application determine which surfaces to trim, false to trim all possible surfaces"；`BSplitLinearIn` = "False to naturally extend any trims along the intersecting surfaces, true to extend any trims linearly along the intersecting surfaces"；`BRemovePickedIn` = "True to remove the selected surfaces, false to keep the selected surfaces"。`## Returns` = "True if successful, false if not"。

**2) `## Remarks` 逐字摘录**（整段）——
> After calling this method:
>
> 1. Select the trimming surfaces or trim tool.
> 2. Optionally, call [[IFeatureManager::SolidForTrim]].
> 3. Call [[IFeatureManager::PostTrimSurface]].

**3) 官方例子的调用序** —— 例文件名 **`C:\swapi\examples\Create_Trimmed_Surface_Feature_Example_VB.md`** 与 **`C:\swapi\examples\Create_Solid_Body_Surface_Trim_Feature_Example_VB.md`**（各另有 `_VBNET` / `_CSharp`）。

`Create_Trimmed_Surface_Feature_Example_VB.md` 逐字：
```vbnet
' Set the trimming options
status = swFeatureMgr.PreTrimSurface(False, True, False, False)
' Trim the surface
status = swModelDocExt.SelectByID2("", "SURFACEBODY", 2.89416986472588E-02, 7.81827749557351E-03, 2.90635845400971E-02, True, 0, Nothing, 0)
Set swFeat = swFeatureMgr.PostTrimSurface(True)
```
★ 实参对位：`BMutualTrimIn=False, BSplitSystemIn=True, BSplitLinearIn=False, BRemovePickedIn=False`。
★ **注意调用序**：这里 `PreTrimSurface` **先调用**，然后才 `SelectByID2(... "SURFACEBODY" ...)` 选裁剪体 —— 与 Remarks 第 1 步「After calling this method: 1. Select the trimming surfaces」一致。

`Create_Solid_Body_Surface_Trim_Feature_Example_VB.md` 逐字（不同的一路：先选面，再 `PreTrimSurface(True,…)`，中间切 `SolidForTrim`）：
```vbnet
' Select surface features
status = swModelDocExt.SelectByID2("", "SURFACEBODY", -4.46486526100784E-02, 2.18350174377093E-02, 1.23754341749418E-02, True, 0, Nothing, 0)
status = swModelDocExt.SelectByID2("", "SURFACEBODY", -8.15686270678384E-03, 4.15839719953865E-02, 2.42402652081068E-02, True, 0, Nothing, 0)
' Select trimming surfaces to create solid body surface trim feature
status = swFeatureManager.PreTrimSurface(True, True, False, True)
status = swModelDocExt.SelectByID2("", "SURFACEBODY", 5.9504253577245E-03, 4.13800871671199E-02, 2.48740287174201E-02, True, 0, Nothing, 0)
...
Debug.Print "Solid body surface trim feature? " & swFeatureManager.SolidForTrim
swFeatureManager.SolidForTrim = True
Debug.Print "Solid body surface trim feature? " & swFeatureManager.SolidForTrim
Set swFeature = swFeatureManager.PostTrimSurface(True)
```
★ 实参对位：`BMutualTrimIn=True, BSplitSystemIn=True, BSplitLinearIn=False, BRemovePickedIn=True`。全部 `SelectByID2` 的 mark 都是 **0**。

**4) 枚举**：**查不到**（4 个形参全是 `System.bool`，该页没点名任何枚举）。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete，无后继链。

**前置一句话**：调完它**之后**才选裁剪面/裁剪工具（可选地夹在中间设 `SolidForTrim`），最后必须调 `PostTrimSurface`。
**配方一句话**：`PreTrimSurface(False, True, False, False)` → `SelectByID2("", "SURFACEBODY", x,y,z, True, 0, Nothing, 0)` → `PostTrimSurface(True)`（例 `Create_Trimmed_Surface_Feature_Example_VB.md`）。

---

## 9. `IFeatureManager.PostTrimSurface`

**1) 精确签名（1 个参数）** —— `C:\swapi\types\IFeatureManager\PostTrimSurface.md`
```
Feature PostTrimSurface( System.bool BSewSurfaceIn )
```
逐参数原文：`BSewSurfaceIn`: "True to sew the resulting trimmed surfaces, false to not"。`## Returns`: `[[Feature]]`。

**2) `## Remarks` 逐字摘录**（整段）——
> Before calling this method:
>
> 1. Call [[IFeatureManager::PreTrimSurface]].
> 2. Select the trimming surfaces or trim tool.
> 3. Optionally, call [[IFeatureManager::SolidForTrim]].

**3) 官方例子的调用序** —— 同 `PreTrimSurface` 的两例（`Create_Trimmed_Surface_Feature_Example_VB.md` / `Create_Solid_Body_Surface_Trim_Feature_Example_VB.md`）。前者逐字：
```vbnet
status = swFeatureMgr.PreTrimSurface(False, True, False, False)
status = swModelDocExt.SelectByID2("", "SURFACEBODY", 2.89416986472588E-02, 7.81827749557351E-03, 2.90635845400971E-02, True, 0, Nothing, 0)
Set swFeat = swFeatureMgr.PostTrimSurface(True)
swModel.ClearSelection2 True
```
★ 实参：`BSewSurfaceIn=True`。后者：`swFeatureManager.PostTrimSurface(True)`，在设完 `SolidForTrim = True` 之后。

**4) 枚举**：**查不到**（唯一形参是 `System.bool`）。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。

**前置一句话**：必须**先** `PreTrimSurface`、**再**选裁剪面/工具、（可选）`SolidForTrim`，最后才是它。
**配方一句话**：`PreTrimSurface(...)` → `SelectByID2("", "SURFACEBODY", …)` →（可选 `SolidForTrim=True`）→ `PostTrimSurface(True)`（例 `Create_Trimmed_Surface_Feature_Example_VB.md`）。

---

## 10. `IFeatureManager.SolidForTrim`

**1) 精确签名（属性，0 个参数）** —— `C:\swapi\types\IFeatureManager\SolidForTrim.md`（`kind: property`）
```
System.bool SolidForTrim {get; set;}
```
`## Returns`: "True if a solid body, false if a surface body (see **Remarks**)"。

**2) `## Remarks` 逐字摘录**（整段）——
> This property is only available when creating a surface trim feature. Call this property:
>
> - after calling [[IFeatureManager::PreTrimSurface]]
> - before calling [[IFeatureManager::PostTrimSurface]].

**3) 官方例子的调用序** —— 例文件名 **`C:\swapi\examples\Create_Solid_Body_Surface_Trim_Feature_Example_VB.md`**。逐字：
```vbnet
Debug.Print "Solid body surface trim feature? " & swFeatureManager.SolidForTrim
swFeatureManager.SolidForTrim = True
Debug.Print "Solid body surface trim feature? " & swFeatureManager.SolidForTrim
Set swFeature = swFeatureManager.PostTrimSurface(True)
```
★ 例子里是**先读回、再写 True、再读回**（两行 `Debug.Print`）。

**4) 枚举**：**查不到**（属性类型是 `System.bool`）。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。

**前置一句话**：只在**建曲面裁剪特征期间**可用，且必须在 `PreTrimSurface` **之后**、`PostTrimSurface` **之前**读/写。
**配方一句话**：`swFeatureManager.SolidForTrim = True`（夹在 `PreTrimSurface` 与 `PostTrimSurface(True)` 之间，例 `Create_Solid_Body_Surface_Trim_Feature_Example_VB.md`）。

---

## 11. `IFeatureManager.GetPreTrimmedBodies`

**1) 精确签名（1 个参数）** —— `C:\swapi\types\IFeatureManager\GetPreTrimmedBodies.md`
```
System.object GetPreTrimmedBodies( Body2 TargetSurface )
```
逐参数原文：`TargetSurface`: "Target sheet [[body]]"。`## Returns`: "Array of temporary trimmed bodies"。

**2) `## Remarks` 逐字摘录** —— **查不到**。md 页**无 `## Remarks` 段**；CHM 页 `...~GetPreTrimmedBodies.html` **也没有 `remarksSection` 段**（只有 syntax / Parameters / Return Value / See Also / Availability）。★ CHM 页 `Availability` 段逐字：**"SOLIDWORKS 2008 FCS, Revision Number 16.0"**。
★ 该页描述句（不是 Remarks 段，是首段摘要）逐字："Gets the temporary trimmed bodies using the specified target sheet (surface) body according to the trim tools previously defined by [[IFeatureManager::PreTrimSurface]]."

**3) 官方例子的调用序** —— **查不到**（该页无 `## Examples` 段；CHM 页 `exampleSection` 为空）。

**4) 枚举**：**查不到**。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样**；See Also 点名 `[[IFeatureManager::PostTrimSurface Method]]`（这是「相关成员」，**不是**后继声明）。

**前置一句话**：查不到（官方没写前置；只说「按 `PreTrimSurface` 先前定义过的裁剪工具」）。
**配方一句话**：查不到。

---

## 12. `IFeatureManager.SetFreeformBoundaryContinuity`

**1) 精确签名（2 个参数）** —— `C:\swapi\types\IFeatureManager\SetFreeformBoundaryContinuity.md`
```
void SetFreeformBoundaryContinuity( System.short BoundaryIndex, System.short Continuity )
```
逐参数原文：`BoundaryIndex` = "0-based index of the boundary to modify (i.e., a value ranging from 0 to (Number of face boundaries-1))"；`Continuity` 逐字取值表 **"-1 = Movaeable · 0 = Contact · 1 = Tangenet · 2= Curvature"**（★ 拼写 `Movaeable` / `Tangenet` 是官方原文照抄，不是笔误修正）。

**2) `## Remarks` 逐字摘录**（整段）——
> The SOLIDWORKS API Freeform-related methods are intended to journal the actions performed by an interactive user while creating the feature. Because user interaction is required to create a Freeform feature, fully automating the creation of it is not possible using the SOLIDWORKS API.
>
> The typical steps performed by an interactive user to create a Freeform feature are:
>
> 1. Select the face to form.
> 2. Add curves on the selected face. Corresponds to [[IFeatureManager::SetFreeformCurveData]].
> 3. Add points on the curves. Corresponds to [[IFeatureManager::SetFreeformPointData]].
> 4. Specify boundary continuity. Corresponds to IFeatureManager::SetFreeformBoundaryContinuity.
>
>    Interactively pull or push the points to change the shape of the selected face.
>
> 5. Insert the Freeform feature. Corresponds to this method, [[IFeatureManager::InsertFreeform2]].
>
> Record a macro while interactively creating a Freeform feature, then examine the macro to see the order in which the Freeform-related methods are recorded.

**3) 官方例子的调用序** —— **查不到**（该页无 `## Examples` 段；CHM 页 `...~SetFreeformBoundaryContinuity.html` 的 `exampleSection` 为空）。★ `C:\swapi\examples\` 全目录 grep `SetFreeformBoundaryContinuity` = 0 命中。

**4) 枚举**：**查不到**（`Continuity` 的 `-1/0/1/2` 是该页给的**内联数值表**，官方没给枚举名）。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。

**前置一句话**：它是 `Freeform` 宏录制序列里的第 4 步（先 `SetFreeformCurveData`、再 `SetFreeformPointData`），且官方明写「**完全自动化创建 Freeform 是不可能的**」。
**配方一句话**：查不到（官方只给录制序，无代码例子）。

---

## 13. `IFeatureManager.FeatureBossThicken`

**1) 精确签名（7 个参数）** —— `C:\swapi\types\IFeatureManager\FeatureBossThicken.md`
```
Feature FeatureBossThicken( System.double Thickness, System.int Direction, System.int FaceIndex, System.bool FillVolume, System.bool Merge, System.bool UseFeatScope, System.bool UseAutoSelect )
```
逐参数原文：`Thickness` = "Wall thickness"；`Direction` = "Direction as defined in [[swThickenThicknessType_e]]"；★ `FaceIndex` = "**Not used**"；`FillVolume` = "True if you want to make a solid from the knitted surface, false if not (see **Remarks**)"；`Merge` = "True if you want to merge the results in a multibody part, false if not"；`UseFeatScope` = "True if the feature only affects selected bodies, false if the feature affects all bodies"；`UseAutoSelect` = "True to automatically select all bodies and have the feature affect those bodies, false to select the bodies the feature affects (see **Remarks**)"。`## Returns`: "Pointer to the [[IFeature]] object"。

**2) `## Remarks` 逐字摘录**（整段）——
> This method generates a boss feature by thickening a selected reference surface.  The surface must be selected with a mark of 1. See [[IModelDocExtension::SelectByID2]] for details.
>
> If FillVolume is true, other arguments are ignored. A closed surface is required when FillVolume is true.
>
> If UseAutoSelect is false, the user must select the bodies that the feature will affect.

★ **唯一写明 mark 的是这一条**：`The surface must be selected with a mark of 1.`

**3) 官方例子的调用序** —— 三个例子。

**(a) `C:\swapi\examples\Create_Thicken_Feature_Example_VB.md`**：
```vbnet
status = swModelDocExt.SelectByID2("Extrude1", "BODYFEATURE", 0, 0, 0, False, 0, Nothing, 0)
status = swModelDocExt.SelectByID2("Surface-Offset1[1]", "SURFACEBODY", 3.19724221122328E-02, -9.99999999999091E-03, -1.04277742429417E-02, False, 1, Nothing, 0)
' Thicken the selected reference surface and then generate a boss
Set swFeatureThicken = swFeatureMgr.FeatureBossThicken(0.01, 0, 96, False, True, False, True)
```
★ 先选什么：先选 `Extrude1`（mark 0），再选 `Surface-Offset1[1]` **（`"SURFACEBODY"`，mark = 1）**。
★ 实参对位（7 个）：`Thickness=0.01, Direction=0, FaceIndex=96, FillVolume=False, Merge=True, UseFeatScope=False, UseAutoSelect=True`。

**(b) `C:\swapi\examples\Thicken_Surface_and_Generate_Boss_Example_VB.md`**：
```vb
bRet = swSelMgr.SetSelectedObjectMark(1, 1, swSelectionMarkSet)
Set swFeat = swFeatMgr.FeatureBossThicken(0.001, swThickenSideOne, 0, False, True, True, True)
```
★ 这条例子**不用 `SelectByID2`**，而是直接 `swSelMgr.SetSelectedObjectMark(1, 1, swSelectionMarkSet)` 把当前选中项的 mark 设成 1 —— 与 Remarks 的 "must be selected with a mark of 1" 对得上。
★ 实参对位：`Thickness=0.001, Direction=swThickenSideOne, FaceIndex=0, FillVolume=False, Merge=True, UseFeatScope=True, UseAutoSelect=True`（★ 注意与 (a) 的 `UseFeatScope` 不同：(a)=`False`、(b)=`True`）。

**(c) `C:\swapi\examples\Fill_Holes_in_Part_Example_VB.md`**（先缝合再增厚）：
```vb
bRet = swKnitFeat.Select2(False, 1)
Set swThickFeat = swNewFeatMgr.FeatureBossThicken(0.00254, 0, 7471215, False, True, True, True)
```
★ 先选什么：前面先把所有临时 sheet 逐个 `swFeat(i).Select2(True, 1)`、`swNewFeatMgr.InsertSewRefSurface True, False, False, 3.001639406912E-05, 0.0001` 缝合，再 `swKnitFeat.Select2(False, 1)` 选回 knit 特征。
★ `FaceIndex` 在三例里被填的是 `96` / `0` / `7471215` —— 官方参数表对它写的是 `Not used`。

**4) 枚举**：`swThickenThicknessType_e`（`swThickenSideOne`=0 / `swThickenSideTwo`=1 / `swThickenSideBoth`=2）。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。见 See Also 点名 `[[IFeatureManager::FeatureCutThicken Method]]`（是相关成员，非后继声明）。

**前置一句话**：必须先把**参考曲面用 mark = 1 选中**（`SelectByID2(..., mark=1)` 或 `SelectionMgr.SetSelectedObjectMark(1, 1, swSelectionMarkSet)`）；`UseAutoSelect=false` 时用户还必须自己选体；`FillVolume=true` 时其余参数被忽略且要求封闭曲面。
**配方一句话**：`FeatureBossThicken(0.001, swThickenSideOne, 0, False, True, True, True)`（例 `Thicken_Surface_and_Generate_Boss_Example_VB.md`）。

---

## 14. `IFeatureManager.FeatureCutThicken`

**1) 精确签名（6 个参数）** —— `C:\swapi\types\IFeatureManager\FeatureCutThicken.md`
```
Feature FeatureCutThicken( System.double Thickness, System.int Direction, System.int FaceIndex, System.bool FillVolume, System.bool UseFeatScope, System.bool UseAutoSelect )
```
逐参数原文：`Thickness` = "Wall thickness"；★ `Direction` **内联取值表**（该页没点名枚举）：`0 = Thicken side 1` · `1 = Thicken side 2` · `2 = Thicken both sides`；★ `FaceIndex` = "**Not currently used**"；其余三个 `bool` 与 `FeatureBossThicken` 同义。`## Returns`: "Pointer to the [[IFeature]] object"。

**2) `## Remarks` 逐字摘录**（整段）——
> This method creates a cut feature by thickening a selected reference surface. If FillVolume is True, other arguments are ignored. A closed surface is required when FillVolume is True.
>
> When UseAutoSelect is false, the user must select the bodies that the feature will affect.
>
> When using cut or cavity features that result in multiple bodies, you cannot select to keep all of the resulting bodies or one or more selected bodies.

★ CHM 页 `...~FeatureCutThicken.html` 的 `remarksSection` 与 md 逐字相同；该页 `Availability` 逐字 **"SOLIDWORKS 2003 FCS, Revision Number 11.0"**。
★ **这条的 Remarks 没有写 mark** —— 与 `FeatureBossThicken`（写了 "must be selected with a mark of 1"）不同。★ mark = **查不到**。

**3) 官方例子的调用序** —— **查不到**。md 页**无 `## Examples` 段**；CHM 页 `...~FeatureCutThicken.html` 的 `exampleSection` 为空；`C:\swapi\examples\` 全目录 grep `FeatureCutThicken` = 0 命中。

**4) 枚举**：**查不到**（`Direction` 的 0/1/2 是该页内联数值，官方没点枚举名）。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。见 See Also 点名 `FeatureCut2` / `FeatureCutThin` / `FeatureBossThicken`（相关成员，非后继）。

**前置一句话**：只写了「要先选中参考曲面」（**没写 mark**）与「`UseAutoSelect=false` 时用户必须自己选体」；mark 取值 = 查不到。
**配方一句话**：查不到（无例子）。

---

## 15. `IFeatureManager.InsertSewRefSurface`（曲面 **Knit** 入口）

> ★ 收录理由：`IFeatureManager` 目录里没有名字含 `Knit` 的成员；这一条的 `## Returns` 是 `[[Feature]]`、See Also 是 `[[ISurfaceKnitFeatureData Interface]]`、官方例子名是 `Create Surface Knit Feature` ⇒ 它就是曲面 knit 特征。

**1) 精确签名（5 个参数）** —— `C:\swapi\types\IFeatureManager\InsertSewRefSurface.md`
```
Feature InsertSewRefSurface( System.bool UseGapFilters, System.bool TryToFormSolid, System.bool MergeEntities, System.double KnitTolerance, System.double MaxValueForGapRange )
```
逐参数原文：`UseGapFilters` = "True to use gap filters, false to not"；`TryToFormSolid` = "True to form a solid body, false to no"（★ "false to no" 是原文照抄）；`MergeEntities` = "True to merge edges and faces by removing redundant vertices and edges, false to not"；`KnitTolerance` = "Knit tolerance (see **Remarks**)"；`MaxValueForGapRange` = "Maximum value of gap range for gap filters"。`## Returns`: `[[Feature]]`。

**2) `## Remarks` 逐字摘录**（整段）——
> Make selections using [[IModelDocExtension::SelectByID2]] with a mark number of 1. See the SOLIDWORKS Help for information about what entities are valid for selection.
>
> A knit tolerance's:
>
> - lower limit is 0.0001 mm
> - upper limit is 0.1 mm
>
> The knit tolerance value should be in a gap range such that:
>
> (Minimum gap) <= (Knit tolerance) <= MIN(0.1 mm, Maximum gap)

**3) 官方例子的调用序** —— 例文件名 **`C:\swapi\examples\Create_Surface_Knit_Feature_Example_VB6.md`**（md 的 Examples 段另列 `_VBNET.md` / `_CSharp.md`）。逐字：
```vb
' Select both surfaces and create surface knit feature
boolstatus = swModelDocExt.SelectByID2("Surface-Extrude1", "BODYFEATURE", 0, 0, 0, False, 1, Nothing, 0)
boolstatus = swModelDocExt.SelectByID2("Surface-Plane1", "SURFACEBODY", 0, 0, 0, True, 1, Nothing, 0)
Set swFeature = swFeatureManager.InsertSewRefSurface(True, False, False, 0.0001, 0.0001)
' Get some surface knit feature data
Set swSurfaceKnitFeature = swFeature.GetDefinition
Debug.Print " Knit tolerance: " & swSurfaceKnitFeature.KnitTolerance * 1000 & " mm"
```
★ 先选什么：两个曲面都用 **mark = 1**（一个 `BODYFEATURE` 一个 `SURFACEBODY`），第二个 `Append=True`。
★ 实参对位（5 个）：`UseGapFilters=True, TryToFormSolid=False, MergeEntities=False, KnitTolerance=0.0001, MaxValueForGapRange=0.0001`。

**4) 枚举**：**查不到**（5 个形参全是非枚举类型；`KnitTolerance` 的范围是 Remarks 里的文字）。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。`C:\swapi\types\IFeatureManager\` 目录下**没有 `InsertSewRefSurface2`**（目录列举只有 `InsertSewRefSurface.md`）⇒ 无 `*2` 后继。

**前置一句话**：用 `SelectByID2` 以 **mark number of 1** 选要缝合的曲面（多个都要），缝合容差必须落在 `0.0001 mm ~ 0.1 mm` 且满足 `(Minimum gap) <= (Knit tolerance) <= MIN(0.1 mm, Maximum gap)`。
**配方一句话**：`SelectByID2("Surface-Extrude1","BODYFEATURE",…,1,…)` + `SelectByID2("Surface-Plane1","SURFACEBODY",…,True,1,…)` → `InsertSewRefSurface(True, False, False, 0.0001, 0.0001)`（例 `Create_Surface_Knit_Feature_Example_VB6.md`）。

---

# 二 · `IModeler` · `Create*Surface` 全族

> ★ 本节全部成员：**CHM 解包里 `IModeler` 接口页查不到**（见本文件第〇节的覆盖事实）⇒ 签名 / Remarks / Examples 三样只来自 `C:\swapi\types\IModeler\<成员>.md` 与 `C:\swapi\examples\<例子>.md`。

## 16. `IModeler.CreateBsplineSurface`

**1) 精确签名（4 个参数）** —— `C:\swapi\types\IModeler\CreateBsplineSurface.md`
```
System.object CreateBsplineSurface( System.object Props, System.object UKnots, System.object VKnots, System.object CtrlPtCoords )
```
逐参数原文：`Props` = "Array containing 8 integers packed as 4 double elements (see **Remarks**)"；`UKnots` = "Array of numUKnots (see **Remarks**)"；`VKnots` = "Array of numVKnots (see **Remarks**)"；`CtrlPtCoords` = "Array of numCtrlPtCoord (see **Remarks**)"。`## Returns`: "B-spline [[surface]]"。

**2) `## Remarks` 逐字摘录**（整段，含官方那张对照表）——
> The Props array contains the following elements. These are integers packed into a double array in the Dispatch version.
>
> - Uorder, Vorder
> - numV_CtrlPoints, numU_CtrlPoints
> - Uperiodicity, Vperiodicity
> - DimensionControlPoints, UNUSED ( set =0 )
>
> **Number of elements in this array...**
>
> **Given by...**
>
> UKnots
>
> numUKnots = numU_CtrlPoints + Uorder
>
> VKnots
>
> numVKnots = numV_CtrlPoints + Vorder
>
> CtrlPtCoords
>
> numCtrlPtCoord =( NumV_CtrlPoints * NumU_CtrlPoints * DimensionControlPoints )
>
> **NOTE:** The order of the UV control points are reversed if you used [[ISurface::GetBSurfParams3]] or [[ISurface::IGetBSurfParams]] to get the data. You do not need to reverse the UV control points; instead, you can switch the UV knots and related parameters.
>
> For periodics, the first knot must have multiplicity = 1 and all excess multiplicity must be imposed on the last knot. Therefore, a valid periodic knot vector would be { 0, 1, 2, 3, 3, 3 } for a cubic curve. The control point on the seam of the closed curve cannot be replicated at both ends; it should occur only at the beginning.
>
> To convert from a clamped periodic curve (numKnots = numCtrlPts + Order, ctrlPts replicated, knot multiplicity = order at each end) to a SOLIDWORKS periodic curve, remove all but one of the knots at the beginning of the vector and remove one at the end. Also remove the last control point to avoid the point replication.

**3) 官方例子的调用序** —— **查不到**（该页无 `## Examples` 段；`C:\swapi\examples\` grep `CreateBsplineSurface` = 0 命中）。

**4) 枚举**：**查不到**（4 个形参全是 `System.object`，该页没点名任何枚举；`Props` 里的 8 个元素是**位置约定**不是枚举）。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。

**前置一句话**：`Props` 必须装 8 个整型（打包进 4 个 double 元素），且**元素个数**分别满足 `numUKnots = numU_CtrlPoints + Uorder`、`numVKnots = numV_CtrlPoints + Vorder`、`numCtrlPtCoord = NumV_CtrlPoints * NumU_CtrlPoints * DimensionControlPoints`。
**配方一句话**：查不到（无例子）。

---

## 17. `IModeler.CreateConicalSurface`（Obsolete）

**1) 精确签名（4 个参数）** —— `C:\swapi\types\IModeler\CreateConicalSurface.md`
```
System.object CreateConicalSurface( System.object Center, System.object Direction, System.double Radius, System.double SemiAngle )
```
★ 四个形参在该页**全写 `No description`**；该页**没有 `## Returns` 段**、**没有 `## Remarks` 段**、**没有 `## Examples` 段**。

**2) `## Remarks` 逐字摘录** —— **查不到**（无该段）。

**3) 官方例子的调用序** —— **查不到**（无该段；`C:\swapi\examples\` grep `CreateConicalSurface` = 0 命中）。

**4) 枚举**：**查不到**。

**5) 废弃链**：**Obsolete. Superseded by `[[IModeler::CreateConicalSurface2]]`**（逐字）。后继 `CreateConicalSurface2` 有签名 + Remarks（见下节）。

**前置一句话**：查不到。
**配方一句话**：查不到。

---

## 18. `IModeler.CreateConicalSurface2`

**1) 精确签名（5 个参数）** —— `C:\swapi\types\IModeler\CreateConicalSurface2.md`
```
System.object CreateConicalSurface2( System.object Center, System.object Direction, System.object RefDirection, System.double Radius, System.double SemiAngle )
```
逐参数原文：`Center` = "Array containing 3 doubles (see **Remarks**)"；`Direction` = "Array containing 3 doubles (see **Remarks**)"；`RefDirection` = "Array containing 3 doubles (see **Remarks**)"；`Radius` = "See **Remarks**"；★ `SemiAngle` = "**e Remarks**"（该页原文如此，疑为排版丢失，不改写）。`## Returns`: `[[Surface]]`。

**2) `## Remarks` 逐字摘录**（整段，含官方那张 Argument/Description 表）——
> Input arguments:
>
> **Argument** — **Description**
> Center — "XYZ location which represents the center of the bottom"
> Direction — "XYZ direction of the axis of the conical surface"
> Radius — "Radius at the center"
> SemiAngle — "Half angle of the cone **in radians**"
>
> You can trim the resulting surface to generate a sheet body (for example, using [[ISurface::CreateTrimmedSheet]]).

★ 官方那张表**没有 `RefDirection` 这一行** ⇒ `RefDirection` 的语义 = **查不到**。

**3) 官方例子的调用序** —— **查不到**（该页无 `## Examples` 段；grep `CreateConicalSurface` 在 examples 目录 = 0 命中）。

**4) 枚举**：**查不到**。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete；它是 `CreateConicalSurface` 的后继。

**前置一句话**：三个数组形参各是 3 个 double；`SemiAngle` 的单位官方明写是**弧度（in radians）**。
**配方一句话**：查不到（无例子）。

---

## 19. `IModeler.CreateCoonsBSurface`

**1) 精确签名（5 个参数）** —— `C:\swapi\types\IModeler\CreateCoonsBSurface.md`
```
Surface CreateCoonsBSurface( Curve UCurve0, Curve UCurve1, Curve VCurve0, Curve VCurve1, System.bool IgnoreClosureReqt )
```
★ **返回类型是 `Surface`（不是 `System.object`）** —— 本族里唯一直接返 `Surface` 的一条。逐参数原文：`UCurve0` = "First curve of u direction"；`UCurve1` = "Second curve of u direction"；`VCurve0` = "First curve of v direction"；`VCurve1` = "Second curve of v direction"；`IgnoreClosureReqt` = "True to ignore closure request, false to not"。`## Returns`: `[[B-surface]]`。

**2) `## Remarks` 逐字摘录**（整段，只有一句）——
> By default, IgnoreClosureReqt is not ignored.

**3) 官方例子的调用序** —— **查不到**（该页无 `## Examples` 段；grep `CreateCoonsBSurface` 在 examples 目录 = 0 命中）。

**4) 枚举**：**查不到**。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。

**前置一句话**：要 4 条边界曲线（u 向 2 条 + v 向 2 条）；`IgnoreClosureReqt` **默认不被忽略**。
**配方一句话**：查不到（无例子）。

---

## 20. `IModeler.CreateCylindricalSurface`（Obsolete）

**1) 精确签名（3 个参数）** —— `C:\swapi\types\IModeler\CreateCylindricalSurface.md`
```
System.object CreateCylindricalSurface( System.object Center, System.object Direction, System.double Radius )
```
★ 三个形参在该页**全写 `No description`**；该页**没有 `## Returns` 段**、**没有 `## Remarks` 段**、**没有 `## Examples` 段**。

**2) `## Remarks` 逐字摘录** —— **查不到**。

**3) 官方例子的调用序** —— **查不到**（无该段；grep `CreateCylindricalSurface` 在 examples 目录 = 0 命中）。

**4) 枚举**：**查不到**。

**5) 废弃链**：**Obsolete. Superseded by `[[IModeler::CreateCylindricalSurface2]]`**（逐字）。后继见下节。

**前置一句话**：查不到。
**配方一句话**：查不到。

---

## 21. `IModeler.CreateCylindricalSurface2`

**1) 精确签名（4 个参数）** —— `C:\swapi\types\IModeler\CreateCylindricalSurface2.md`
```
System.object CreateCylindricalSurface2( System.object Center, System.object Direction, System.object RefDirection, System.double Radius )
```
逐参数原文：`Center` = "Array containing 3 doubles for XYZ location of  the center of the bottom"（★ "of  the" 是原文双空格）；`Direction` = "Array containing 3 doubles for XYZ direction of the axis of the cylindrical surface"；★ `RefDirection` = "**Array containing 3 doubles for XYZ direction of the axis of the cylindrical surface**"（★ 官方原文与 `Direction` 的描述**完全相同** ⇒ `RefDirection` 的真实语义 = **查不到**）；`Radius` = "Radius at the center"。`## Returns`: `[[Surface]]`。

**2) `## Remarks` 逐字摘录**（整段，只有一句）——
> You can trim the resulting surface to generate a sheet body, for example, using [[ISurface::CreateTrimmedSheet]].

**3) 官方例子的调用序** —— 该页 `## Examples` 段逐字列：
`Create Spherical Surface, Trimmed Sheet, and Feature from Body (VBA)`。
例文件名 **`C:\swapi\examples\Create_Spherical_Surface_Trimmed_Sheet_and_Feature_From_Body_Example_VB.md`** —— ★ 但**这个例子的正文只调 `CreateSphericalSurface2`，没有调 `CreateCylindricalSurface2`**（我读了全文 62 行，见第 30 节）。⇒ **`CreateCylindricalSurface2` 的实际调用序 = 查不到**。

**4) 枚举**：**查不到**。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete；它是 `CreateCylindricalSurface` 的后继。

**前置一句话**：`Center` / `Direction` / `RefDirection` 各是 3 个 double 的数组，`Radius` 是中心处半径；结果是**未裁剪**曲面，要 sheet body 得再 `ISurface::CreateTrimmedSheet`。
**配方一句话**：查不到（唯一挂在本页 Examples 下的例子调的是 `CreateSphericalSurface2`，不是本条）。

---

## 22. `IModeler.CreateExtrusionSurface`

**1) 精确签名（2 个参数）** —— `C:\swapi\types\IModeler\CreateExtrusionSurface.md`
```
System.object CreateExtrusionSurface( System.object ProfileCurve, System.object AxisDirection )
```
逐参数原文：`ProfileCurve` = "Profile [[curve]]"；`AxisDirection` = "Array of 3 doubles (x,y,z)"。`## Returns`: "Extruded [[surface]]"。

**2) `## Remarks` 逐字摘录**（整段）——
> You can use this method with:
>
> - A set of related functions that construct a body from trimmed surfaces. The profile curve is extruded along the direction vector of axis direction, the new surface being the envelope of the curve. **The profile curve must be of type line, circle, or b-spline curve.**
>
> - Trimming curve creation routines (for example, [[ISurface::AddTrimmingLoop2]] or [[ISurface::IAddTrimmingLoop2]]) to construct a trimmed tabulated cylinder.

**3) 官方例子的调用序** —— 例文件名 **`C:\swapi\examples\Create_Imported_Surface_Body_from_Sketch_Example_CSharp.md`**。逐字（该例走的是 **`IBody2.ICreateExtrusionSurface`**，不是 `IModeler` 那一路 —— ★ 这一点必须照抄，不能当成 `IModeler` 的例子）：
```csharp
double []extruAxis = new double[3];
extruAxis[0] = 0.0;
extruAxis[1] = 0.0;
extruAxis[2] = 1.0;
ProfileSegs.Add(curSeg);
swSurface = swBody.ICreateExtrusionSurface((SldWorks.Curve)swCurve, extruAxis);
//Create a trimming loop for the surface
int nCurves = 4;
int []Order = {2, 2, 2, 2};
int []Dim = {2, 2, 2, 2};
int []Periodic = {0, 0, 0, 0};
int []nKnots = {4, 4, 4, 4};
int []nCtrlPts = {2, 2, 2, 2};
double []Knots = {0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1};
...
swSurface.AddTrimmingLoop(nCurves, Order, Dim, Periodic, nKnots, nCtrlPts, Knots, CtrlPts);
bRetval = swBody.CreateTrimmedSurface();
bRetval = swBody.CreateBodyFromSurfaces();
```
★ 调用序：先由草图段造曲线（`IAddProfileLine` / `IAddProfileArc`）→ 给 3 分量拉伸轴 → 造拉伸曲面 → **加裁剪环** → `CreateTrimmedSurface` → `CreateBodyFromSurfaces`。

**4) 枚举**：**查不到**。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。见 See Also 点名 `[[IBody2::CreateExtrusionSurface Method]]` 与 `[[IBody2::ICreateExtrusionSurface Method]]`（**不同接口**，不是后继）。

**前置一句话**：`ProfileCurve` 只能是 **line / circle / b-spline curve** 三种类型之一（Remarks 明写）。
**配方一句话**：造曲线 → 给 3 分量轴 → `ICreateExtrusionSurface` → `AddTrimmingLoop(...)` → `CreateTrimmedSurface()` → `CreateBodyFromSurfaces()`（例 `Create_Imported_Surface_Body_from_Sketch_Example_CSharp.md`，★ 该例走 `IBody2` 而非 `IModeler`）。

---

## 23. `IModeler.CreateLoftSurface`

**1) 精确签名（18 个参数）** —— `C:\swapi\types\IModeler\CreateLoftSurface.md`
```
System.object CreateLoftSurface( System.object CurveArray, System.bool BBlendClosed, System.bool BForceCubic, System.object GuideCrvArray, System.int StartMatchingType, System.int EndMatchingType, System.object NormalAtStartSection, System.object NormalAtEndSection, System.object StartMatchingFaceList, System.object EndMatchingFaceList, System.bool DegeneratedStart, System.bool DegeneratedEnd, System.object StartPointOfStartSection, System.object StartPointOfEndSection, System.int SectionIndexStart, System.int SectionIndexEnd, System.int GuideIndexStart, System.int GuideIndexEnd )
```
逐参数原文（要点）：`CurveArray` = "Array of b-spline [[curves]]"；`BBlendClosed` = "True if blend closed, false if not"；`BForceCubic` = "True if force surface is cubic, false if not"；`GuideCrvArray` = "Array of guide [[curves]]"；
★ `StartMatchingType` 与 `EndMatchingType` 各带**内联取值表**：`0 = MATCH_NONE (default)` · `1 = MATCH_NORMAL` · `2 = MATCH_VECTOR` · `3 = MATCH_ALL_FACES or MATCH_FACE_G1` · `4 = MATCH_FACE_G2`；
`NormalAtStartSection` = "when StartMatchingType is MATCH_NORMAL or MATCH_VECTOR; otherwise, can be Nothing"；`NormalAtEndSection` = "when EndMatchingType is MATCH_NORMAL or MATCH_VECTOR; otherwise, can be Nothing"；`StartMatchingFaceList` / `EndMatchingFaceList` = "Array of matching [[faces]] … when startMatchingType is MATCH_ALL_FACES, MATCH_FACE_G1, or MATCH_FACE_G2; otherwise, can be Nothing"；
`DegeneratedStart` / `DegeneratedEnd` = "True to degenerate at start/end, false to not"；`StartPointOfStartSection` / `StartPointOfEndSection` = "[[Start point]] of start/end section"；`SectionIndexStart` / `SectionIndexEnd` / `GuideIndexStart` / `GuideIndexEnd` = "Index of …; **default is -1**"。`## Returns`: "Newly created loft [[surface]]"。

**2) `## Remarks` 逐字摘录** —— **查不到**（该页**没有 `## Remarks` 段**；参数表里那些 "see" 全指向各自的参数说明，不是 Remarks）。

**3) 官方例子的调用序** —— **查不到**（该页无 `## Examples` 段；`C:\swapi\examples\` grep `CreateLoftSurface` = 0 命中）。★ 同目录的 `Create_Loft_Body_Example_*.md` 走的是 `CreateLoftBody` / `CreateLoftBody2`（**不是** `CreateLoftSurface`）。

**4) 枚举**：**查不到**（`MATCH_*` 是该页给的**内联数值**，官方没点枚举名）。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。

**前置一句话**：`CurveArray` 必须是 **b-spline 曲线**数组；四个 `*Index*` 形参的默认值官方写的是 **-1**；`Normal*` / `*MatchingFaceList` 在对应 `*MatchingType` 不为 `MATCH_NORMAL` / `MATCH_VECTOR` / `MATCH_ALL_FACES` 时**可以传 Nothing**。
**配方一句话**：查不到（无例子）。

---

## 24. `IModeler.CreateOffsetSurface`

**1) 精确签名（2 个参数）** —— `C:\swapi\types\IModeler\CreateOffsetSurface.md`
```
System.object CreateOffsetSurface( System.object SurfaceIn, System.double Distance )
```
逐参数原文：`SurfaceIn` = "Offset [[surface]]"；`Distance` = "Offset distance"。`## Returns`: "Newly created [[surface]]"。

**2) `## Remarks` 逐字摘录** —— **查不到**（该页**没有 `## Remarks` 段**）。

**3) 官方例子的调用序** —— **查不到**（该页无 `## Examples` 段；grep `CreateOffsetSurface` 在 examples 目录 = 0 命中）。★ `C:\swapi\examples\Create_Thicken_Feature_Example_VB.md` 里建偏移面走的是 `swModel.InsertOffsetSurface 0.01, False`（**`IModelDoc2` 那一路**，不是 `IModeler`）。

**4) 枚举**：**查不到**（`Distance` 是 `System.double`）。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。见 See Also 点名 `[[IBody2::CreateOffsetSurface Method]]`（不同接口，非后继）。

**前置一句话**：查不到（官方没写前置）。
**配方一句话**：查不到（无例子）。

---

## 25. `IModeler.CreatePlanarSurface`（Obsolete）

**1) 精确签名（2 个参数）** —— `C:\swapi\types\IModeler\CreatePlanarSurface.md`
```
System.object CreatePlanarSurface( System.object VRootPoint, System.object VNormal )
```
★ 两个形参在该页**全写 `No description`**；该页**没有 `## Returns` 段**、**没有 `## Remarks` 段**、**没有 `## Examples` 段**。

**2) `## Remarks` 逐字摘录** —— **查不到**。

**3) 官方例子的调用序** —— **查不到**（本条无 Examples；grep `CreatePlanarSurface` 在 examples 命中的三族例子见第 26、27 节，都是 `*2` 或 `IBody2` 那一路）。

**4) 枚举**：**查不到**。

**5) 废弃链**：**Obsolete. Superseded by `[[IModeler::CreatePlanarSurface2]]`**（逐字）。后继见下节。

**前置一句话**：查不到。
**配方一句话**：查不到。

---

## 26. `IModeler.CreatePlanarSurface2`

**1) 精确签名（3 个参数）** —— `C:\swapi\types\IModeler\CreatePlanarSurface2.md`
```
System.object CreatePlanarSurface2( System.object VRootPoint, System.object VNormal, System.object VRef )
```
逐参数原文：`VRootPoint` = "Array of 3 doubles (x,y,z) representing the root point of the VNormal and VRef vectors"；`VNormal` = "Array of 3 doubles (x,y,z) defining a vector with root point, VRootPoint; **this vector must be perpendicular to VRef**"；`VRef` = "Array of 3 doubles (x,y,z) defining the x-axis on the planar surface with root point, VRootPoint; **this vector must be perpendicular to VNormal**"。`## Returns`: "Newly created planar [[surface]]"。

**2) `## Remarks` 逐字摘录**（整段）——
> You can use this method with:
>
> - A set of related functions designed to construct a body from trimmed surfaces. It can also be used with trimming curve creation routines to construct a trimmed planar surface.
>
> - Trimming curve creation routines such as [[ISurface::AddTrimmingLoop2]] or [[ISurface::IAddTrimmingLoop2]] to construct a trimmed surface.
>
> See [[IBody2::CreatePlanarTrimSurfaceDLL]] or [[IBody2::ICreatePlanarTrimSurfaceDLL]], which allows you to create a planar trimmed surface directly from the vertex points.

**3) 官方例子的调用序** —— 该页 `## Examples` 段逐字列 5 个例子：
`Create Infinite Plane (VBA)` · `Cut Body in Half Using Macro Feature (VBA)` · `Create Temporary Extruded Body (C#)` · `Create Temporary Extruded Body (VB.NET)` · `Create Temporary Extruded Body (VBA)`。

★ 最直接的调用序来自 **`C:\swapi\examples\Create_Infinite_Plane_Example_VB.md`**（逐字）：
```vb
BasePt(0) = 0#: BasePt(1) = 0#: BasePt(2) = 0#
vBasePt = BasePt
Normal(0) = 0#: Normal(1) = 0#: Normal(2) = 1#
vNormal = Normal
Xvect(0) = 1#: Xvect(1) = 0#: Xvect(2) = 0#
vXvect = Xvect
Set swSurf = swModeller.CreatePlanarSurface2((vBasePt), (vNormal), (vXvect))
Debug.Assert Not swSurf Is Nothing
Debug.Assert swSurf.IsPlane
vPlane = swSurf.PlaneParams
Debug.Print " normal = (" & vPlane(0) & ", " & vPlane(1) & ", " & vPlane(2) & ")"
Debug.Print " root = (" & vPlane(3) * 1000# & ", " & vPlane(4) * 1000# & ", " & vPlane(5) * 1000# & ") mm"
```
★ 实参对位：`VRootPoint=(0,0,0)`, `VNormal=(0,0,1)`, `VRef=(1,0,0)`。★ 该例还演示 `PlaneParams` 读回的 0..2 是法向、3..5 是根点（乘 1000 转 mm）。

**4) 枚举**：**查不到**（3 个数组形参，官方没点枚举）。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete；它是 `CreatePlanarSurface` 的后继。

**前置一句话**：`VNormal` 与 `VRef` **必须互相垂直**（Remarks 的参数表明写两条），`VRootPoint` 是这两个向量的公共根点。
**配方一句话**：`CreatePlanarSurface2((vBasePt), (vNormal), (vXvect))`，例中取值 `(0,0,0) / (0,0,1) / (1,0,0)`（例 `Create_Infinite_Plane_Example_VB.md`）。

---

## 27. `IModeler.CreateRuledSurface`

**1) 精确签名（3 个参数）** —— `C:\swapi\types\IModeler\CreateRuledSurface.md`
```
System.object CreateRuledSurface( System.object Curve1In, System.object Curve2In, System.object Apex )
```
逐参数原文：`Curve1In` = "First [[curve]]"；`Curve2In` = "Second [[curve]]"；`Apex` = "Array of 3 doubles, (x, y, z), the apex point"。`## Returns`: "Newly created ruled [[surface]]"。

**2) `## Remarks` 逐字摘录**（整段，只有一句）——
> Valid input curves are b-curves.

**3) 官方例子的调用序** —— 例文件名 **`C:\swapi\examples\Create_Ruled_Surface_Example_VB.md`**。逐字：
```vb
Set swEdge(0) = swSelMgr.GetSelectedObject5(1)
Set swCurve(0) = swEdge(0).GetCurve
Debug.Print "Is b-curve? " & swCurve(0).IsBcurve
Set swEdge(1) = swSelMgr.GetSelectedObject5(2)
Set swCurve(1) = swEdge(1).GetCurve
Debug.Print "Is b-curve? " & swCurve(1).IsBcurve
nApex(0) = 0#: nApex(1) = 0#: nApex(2) = 0#
vApex = nApex
Set swSurf = swModeler.CreateRuledSurface(swCurve(0), swCurve(1), (vApex))
Debug.Print "Type of surface? " & swSurf.Identity
Debug.Print "Is parametric? " & swSurf.IsParametric
```
★ 先选什么：例子的 Preconditions 逐字是 "Open a part that has two edges created using b-curves. / Select those two edges."；代码用 `swSelMgr.GetSelectedObject5(1)` 与 `(2)` 取两条边 → `.GetCurve()` → 先 `Debug.Print` 验 `IsBcurve` 再调用。
★ 实参对位：`Curve1In=swCurve(0)`, `Curve2In=swCurve(1)`, `Apex=(0,0,0)`。

**4) 枚举**：**查不到**。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。见 See Also 点名 `[[IModeler::CreateRuledSurfaceFromEdge Method]]`（不同方法，不是后继；同页 See Also 也点 `[[IFeatureManager::InsertRuledSurfaceFromEdge2 Method]]`）。

**前置一句话**：两条输入曲线**必须是 b-curves**（"Valid input curves are b-curves."）。
**配方一句话**：`swModeler.CreateRuledSurface(swCurve(0), swCurve(1), (vApex))`，例中 `vApex=(0,0,0)`（例 `Create_Ruled_Surface_Example_VB.md`）。

---

## 28. `IModeler.CreateRuledSurfaceFromEdge`

**1) 精确签名（14 个形参 = 13 个入参 + 1 个 out）** —— `C:\swapi\types\IModeler\CreateRuledSurfaceFromEdge.md`
```
System.int CreateRuledSurfaceFromEdge( ModelDoc2 ModDoc, System.object Edges, System.int Type, System.double Length, System.bool FlipPullDir, System.bool FlipDir, System.bool TrimAndSew, System.double Angle, System.bool CoordInput, System.double X, System.double Y, System.double Z, System.bool BConnectSurface, out System.object RuledSurface )
```
逐参数原文（★ `Type` 是**内联取值表**，官方没点枚举名）：
- `ModDoc`: "[[Model document]] in which to create surface body"
- `Edges`: "Array of edges on which to create ruled surface" ★ **"NOTE: Currently only a single edge is supported."**
- `Type`: `0 = Tangent to Surface` · `1 = Normal to Surface` · `2 = Tapered to Vector` · `3 = Perpendicular to Vector` · `4 = Sweep`
- `Length`: "Distance at which to create the surface; valid for Tangent to Surface, Tapered to Vector, Perpendicular to Vector, and Sweep types only"
- `FlipPullDir`: "True to flip the pull direction, false to not; **valid for Normal to Surface and Tapered to Vector types only**"
- `FlipDir`: "True to flip the direction, false to not; **valid for Perpendicular to Vector type only**"
- `TrimAndSew`: "True to trim and knit the surface, false to not"
- `Angle`: "Angle for Tapered to Vector type only"
- `CoordInput`: "True to enable coordinate input, false if not; **for Sweep type only**"
- `X` / `Y` / `Z`: "x / y / z coordinate"
- `BConnectSurface`: "True to remove any connecting surfaces, false to not"
- `RuledSurface`（out）: "Ruled surface [[body]]"

`## Returns`: "0 if ruled surface body created, -1 if not"。

**2) `## Remarks` 逐字摘录**（整段）——
> This method returns a surface body, unlike [[IFeatureManager::InsertRuledSurfaceFromEdge2]], which returns a feature.
>
> **If you [[select]] an edge with a selection mark of 4, the default face is used.  If you select an edge with a selection mark of 6, the alternate face is used.**

**3) 官方例子的调用序** —— 例文件名 **`C:\swapi\examples\Create_Ruled_Surface_From_Edge_Example_VB.md`**。逐字：
```vb
Set swSelMgr = swDoc.SelectionManager
Set swEdge(0) = swSelMgr.GetSelectedObject6(1, -1)
swEdgeList = swEdge
Dim error As Long
error = swModel.CreateRuledSurfaceFromEdge(swDoc, swEdgeList, 1, 0.02, True, False, True, 0#, False, 1#, 0#, 0#, False, swRuledBody)
Dim typeBody As Long
typeBody = swRuledBody.GetType()
```
★ 先选什么：例子的 Preconditions 逐字是 "Model document is open and **an edge is selected** on the model."；代码 `swSelMgr.GetSelectedObject6(1, -1)` 取那条边装进 `swEdgeList`。
★ 实参对位（13 个入参 + 1 个 out）：`ModDoc=swDoc, Edges=swEdgeList, Type=1, Length=0.02, FlipPullDir=True, FlipDir=False, TrimAndSew=True, Angle=0#, CoordInput=False, X=1#, Y=0#, Z=0#, BConnectSurface=False, out RuledSurface=swRuledBody`。
★ 例中用的是 `Type=1`（Normal to Surface），而 `Length` 官方写「valid for Tangent to Surface, Tapered to Vector, Perpendicular to Vector, and Sweep types only」—— ★ 这是**官方例子本身**的实参，不是我改的。

**4) 枚举**：**查不到**（`Type` 的 0..4 是该页内联数值表，官方没点枚举名）。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。见 See Also 点名 `[[IFeatureManager::InsertRuledSurfaceFromEdge2 Method]]`，但 Remarks 明确二者**是不同物**（本条返 surface body，那条返 feature）⇒ **不是后继**。

**前置一句话**：先**选中一条边**（官方写 "Currently only a single edge is supported"）；**selection mark = 4 用默认面、mark = 6 用备用面**。
**配方一句话**：`swModel.CreateRuledSurfaceFromEdge(swDoc, swEdgeList, 1, 0.02, True, False, True, 0#, False, 1#, 0#, 0#, False, swRuledBody)`（例 `Create_Ruled_Surface_From_Edge_Example_VB.md`）。

---

## 29. `IModeler.CreateSphericalSurface`（Obsolete）

**1) 精确签名（2 个参数）** —— `C:\swapi\types\IModeler\CreateSphericalSurface.md`
```
System.object CreateSphericalSurface( System.object Center, System.double Radius )
```
★ 两个形参在该页**全写 `No description`**；该页**没有 `## Returns` 段**、**没有 `## Remarks` 段**、**没有 `## Examples` 段**。

**2) `## Remarks` 逐字摘录** —— **查不到**。

**3) 官方例子的调用序** —— **查不到**（无该段；grep `CreateSphericalSurface` 在 examples 命中的只有 `*2` 那一路，见下节）。

**4) 枚举**：**查不到**。

**5) 废弃链**：**Obsolete. Superseded by `[[IModeler::CreateSphericalSurface2]]`**（逐字）。后继见下节。

**前置一句话**：查不到。
**配方一句话**：查不到。

---

## 30. `IModeler.CreateSphericalSurface2`

**1) 精确签名（4 个参数）** —— `C:\swapi\types\IModeler\CreateSphericalSurface2.md`
```
System.object CreateSphericalSurface2( System.object Center, System.object Axis, System.object RefDir, System.double Radius )
```
逐参数原文：`Center` = "Array containing 3 doubles for XYZ location of the center of the spherical surface"；`Axis` = "Array containing 3 doubles"；★ `RefDir` = "**rray containing 3 doubles**"（该页原文如此，开头字母缺失，不改写）；`Radius` = "Radius at the center"。`## Returns`: "Untrimmed spherical [[surface]]"。

**2) `## Remarks` 逐字摘录**（整段）——
> The axis argument is the axis of the sphere; the refDir argument is perpendicular to the axis and through the center of the sphere and defines the origin of the UV space.
>
> You can trim the resulting surface to generate a sheet body, for example, using [[ISurface::CreateTrimmedSheet]].

**3) 官方例子的调用序** —— 例文件名 **`C:\swapi\examples\Create_Spherical_Surface_Trimmed_Sheet_and_Feature_From_Body_Example_VB.md`**。★ 该 md 的正文不是代码块、且行被折断，逐字可读的部分：
```vb
Const RADIUS As Double = 0.01
...
dCenter(0) = 0: dCenter(1) = 0: dCenter(2) = 0
Dim dAxis(2) As Double
dAxis(0) = 0: dAxis(1) = 0: dAxis(2) = 1
Dim dRef(2) As Double
dRef(0) = 1: dRef(1) = 0: dRef(2) = 0
Set swSurf = swModeler.CreateSphericalSurface2(dCenter, dAxis, dRef, RADIUS)
' No trimming curves are required, so pass one Nothing in the Curves parameter array of ISurface::CreateTrimmedSheet5
Dim ZeroTrimmingCurves(0 To 0) As SldWorks.Curve
Set ZeroTrimmingCurves(0) = Nothing
Set swBody = swSurf.CreateTrimmedSheet5(ZeroTrimmingCurves, True, 0.00001)
swBody.Display3 swPart, RGB(255, 255, 0), swTempBodySelectOptions_e.swTempBodySelectable
Stop
Set swFeat = swPart.CreateFeatureFromBody3(swBody, False, swCreateFeatureBodyOpts_e.swCreateFeatureBodyCheck + swCreateFeatureBodyOpts_e.swCreateFeatureBodySimplify)
```
★ 实参对位：`Center=(0,0,0)`, `Axis=(0,0,1)`, `RefDir=(1,0,0)`, `Radius=0.01`。
★ 调用序：`CreateSphericalSurface2` → `CreateTrimmedSheet5(ZeroTrimmingCurves, True, 0.00001)`（数组里塞一个 `Nothing` 表示无需裁剪曲线）→ `Display3` → `Stop`（人工介入）→ `PartDoc.CreateFeatureFromBody3` 把临时体变成特征。
★ 该例同时被 **`CreateCylindricalSurface2.md`** 的 Examples 段引用（同一份例子）—— ★ 但例中没调 `CreateCylindricalSurface2`。

**4) 枚举**：**查不到**（`swTempBodySelectOptions_e` / `swCreateFeatureBodyOpts_e` 出现在**例子的后续调用**里，不在本条签名里）。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete；它是 `CreateSphericalSurface` 的后继。

**前置一句话**：`Axis` 是球轴；`RefDir` 必须**垂直于 Axis 且过球心**，并定义 UV 空间原点（Remarks 明写）。
**配方一句话**：`swModeler.CreateSphericalSurface2(dCenter, dAxis, dRef, 0.01)` → `CreateTrimmedSheet5(ZeroTrimmingCurves, True, 0.00001)`（例 `Create_Spherical_Surface_Trimmed_Sheet_and_Feature_From_Body_Example_VB.md`）。

---

## 31. `IModeler.CreateSweptSurface`

**1) 精确签名（2 个参数）** —— `C:\swapi\types\IModeler\CreateSweptSurface.md`
```
System.object CreateSweptSurface( System.object CurveIn, System.object Dir )
```
逐参数原文：`CurveIn` = "[[Curve]] to use to create the swept surface"；`Dir` = "3 doubles describing the direction vector to sweep the curve along (see **Remarks**)"。`## Returns`: "Newly created [[surface]]"。

**2) `## Remarks` 逐字摘录**（整段）——
> This method creates an infinite surface. To create a trimmed surface, add a trimming loop with [[ISurface::AddTrimmingLoop2]] or [[ISurface::IAddTrimmingLoop2]].
>
> The Dir array is:
>
> - Dir[0] = X component of the direction vector
> - Dir[1] = Y component of the direction vector
> - Dir[2] = Z component of the direction vector

**3) 官方例子的调用序** —— **查不到**（该页无 `## Examples` 段；`C:\swapi\examples\` grep `CreateSweptSurface` = 0 命中）。
★ 唯一在别处点名它的是 `C:\swapi\types\IFeatureManager\InsertSweepSurface3.md` 的 See Also（`[[IModeler::CreateSweptSurface Method]]` / `[[IModeler::ICreateSweptSurface Method]]`）—— 那是交叉引用，不是例子。

**4) 枚举**：**查不到**。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。

**前置一句话**：它造的是**无限曲面**；要裁剪曲面必须再用 `ISurface::AddTrimmingLoop2` / `IAddTrimmingLoop2` 加裁剪环。
**配方一句话**：查不到（无例子）。

---

## 32. `IModeler.CreateToroidalSurface`

**1) 精确签名（5 个参数）** —— `C:\swapi\types\IModeler\CreateToroidalSurface.md`
```
System.object CreateToroidalSurface( System.object Center, System.object Axis, System.object RefDirection, System.double MajorRadius, System.double MinorRadius )
```
逐参数原文：`Center` = "Array containing 3 doubles (see **Remarks**)"；`Axis` = "Array containing 3 doubles (see **Remarks**)"；`RefDirection` = "Array containing 3 doubles (see **Remarks**)"；`MajorRadius` = "See **Remarks**"；`MinorRadius` = "See **Remarks**"。`## Returns`: "Untrimmed toroidal [[surface]]"。

**2) `## Remarks` 逐字摘录**（整段）——
> Input arguments:
>
> - Center "XYZ location that represents the center of the **spherical** surface."（★ 原文写的是 spherical，不是 toroidal —— 照抄不改）
> - Axis "XYZ direction of the axis of the **spherical** surface."（★ 同上）
> - RefDirection "XYZ direction of the reference axis of the **spherical** surface; **it must be perpendicular to the axis**."
> - MajorRadius "major radius of the toroidal surface."
> - MinorRadius "minor radius of the toroidal surface."
>
> The resulting surface can be trimmed using a method like [[ISurface::CreateTrimmedSheet]] to generate a sheet body.

**3) 官方例子的调用序** —— **查不到**（该页无 `## Examples` 段；`C:\swapi\examples\` grep `CreateToroidalSurface` = 0 命中）。

**4) 枚举**：**查不到**。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。见 See Also 点名 `[[ISurface::IsTorus Method]]` 与 `[[ISurface::TorusParams Property]]`。

**前置一句话**：`RefDirection` **必须垂直于 Axis**（Remarks 明写）；结果是**未裁剪**曲面，sheet body 要靠 `ISurface::CreateTrimmedSheet`。
**配方一句话**：查不到（无例子）。

---

# 三 · 相邻成员（名字不含指定关键词，但属同一曲面域；已按五样抄完，列出以免漏）

## 33. `IModeler.ThickenSheet`

**1) 精确签名（3 个参数）** —— `C:\swapi\types\IModeler\ThickenSheet.md`
```
Body2 ThickenSheet( Body2 Sheet, System.double Thickness, System.int Direction )
```
★ 返回类型是 `Body2`（本族里直接返 `Body2` 的一条）。逐参数原文：`Sheet` = "Sheet body that defines the profile for the temporary thickened [[body]]"；`Thickness` = "Thickness of the temporary thickened body"；`Direction` = "Direction in which to thicken the sheet body as defined in [[swThickenDirection_e]]"。`## Returns`: "Temporary thickened [[body]]"。

**2) `## Remarks` 逐字摘录**（整段，只有一句）——
> If you set Direction to swThickenDirection_Both, then the value set for Thickness is used in both directions.

**3) 官方例子的调用序** —— 例文件名 **`C:\swapi\examples\Thicken_Sheet_Body_Example_VB.md`**。逐字：
```vb
' Thickness
dThickness = 0.01
...
' Get the modeler
Set swModeler = swApp.GetModeler
Debug.Assert Not swModeler Is Nothing
' Get active document
Set swModel = swApp.ActiveDoc
' Cast down to part
Set swPart = swModel
' Get the selected sheet body
Set swBody = swModel.SelectionManager.GetSelectedObject6(1, -1)
' Make a copy, so you can later sew together with other sheets
Set swOriginalSheetBody = swBody.Copy
Set swThickenedbody = swModeler.ThickenSheet(swOriginalSheetBody, dThickness, swThickenDirection_Side1)
Debug.Assert (Not (swThickenedbody Is Nothing))
Debug.Assert (swThickenedbody.GetType = swBodyType_e.swSolidBody)
Set aBodies(0) = swThickenedbody
vBodies = aBodies
' Turn temporary body into a feature
Set swFeature = swPart.CreateFeatureFromBody3(vBodies(0), False, swCreateFeatureBodyOpts_e.swCreateFeatureBodyCheck)
swModel.EditRebuild3
```
★ 先选什么：例子的 Preconditions 逐字是 "Open a part that contains a sheet body. / **Select the sheet body in the Surface Bodies folder.**"；代码 `swModel.SelectionManager.GetSelectedObject6(1, -1)` 取它，**先 `.Copy()` 再传进去**（注释逐字："Make a copy, so you can later sew together with other sheets"）。
★ 实参对位：`Sheet=swOriginalSheetBody`, `Thickness=0.01`, `Direction=swThickenDirection_Side1`。
★ mark = **查不到**（该页与该例都没写 mark）。

**4) 枚举**：`swThickenDirection_e`（`swThickenDirection_Side1`=0 / `swThickenDirection_Side2`=1 / `swThickenDirection_Both`=2）。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。

**前置一句话**：要在 Surface Bodies 文件夹里**选中一个 sheet body**（例用 `GetSelectedObject6(1,-1)`），并**先 `.Copy()` 一份**再传进去。
**配方一句话**：`swModeler.ThickenSheet(swOriginalSheetBody, 0.01, swThickenDirection_Side1)` → `CreateFeatureFromBody3(...)` → `EditRebuild3`（例 `Thicken_Sheet_Body_Example_VB.md`）。

---

## 34. `IModeler.GetInitKnitGapWidth`

**1) 精确签名（0 个参数）** —— `C:\swapi\types\IModeler\GetInitKnitGapWidth.md`
```
System.double GetInitKnitGapWidth()
```
`## Returns`: "Initial knitting gap width used for body sewing"。

**2) `## Remarks` 逐字摘录**（整段，只有一句）——
> This value is 0 until a call to knit a body is made.

**3) 官方例子的调用序** —— **查不到**（该页无 `## Examples` 段；`C:\swapi\examples\` grep `GetInitKnitGapWidth` = 0 命中）。

**4) 枚举**：**查不到**。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。

**前置一句话**：零参读数；**调过一次 knit 之前它恒为 0**。
**配方一句话**：查不到。

---

## 35. `IModeler.SetInitKnitGapWidth`

**1) 精确签名（1 个参数）** —— `C:\swapi\types\IModeler\SetInitKnitGapWidth.md`
```
System.bool SetInitKnitGapWidth( System.double InitGapWidth )
```
逐参数原文：`InitGapWidth` = "Desired knitting gap width for body knitting; **valid range is from 1e-8 to 0.1 meters**"。`## Returns`: "True if successfully set, false if not"。

**2) `## Remarks` 逐字摘录**（整段）——
> This initial gap width bound is adjusted during the knitting operation in an attempt to successfully knit a body. Upon completion of the knitting operation, the value is reset to the default value.

★ 首段摘要（非 Remarks 段，但同为官方文字）逐字："Sets the initial gap bound width for sewing a body. **Call this method before calling any calls that attempt to knit a body**; for example, [[IBody2::CreateBodyFromSurfaces]]."

**3) 官方例子的调用序** —— **查不到**（该页无 `## Examples` 段；grep `SetInitKnitGapWidth` 在 examples 目录 = 0 命中）。

**4) 枚举**：**查不到**。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。

**前置一句话**：**必须在任何 knit 类调用之前**设（官方举例是 `IBody2::CreateBodyFromSurfaces`）；取值范围 `1e-8 ~ 0.1` **米**。
**配方一句话**：查不到（无例子）。

---

## 36. `IModeler.MakeManifoldBodies`

**1) 精确签名（1 个参数）** —— `C:\swapi\types\IModeler\MakeManifoldBodies.md`
```
System.object MakeManifoldBodies( Body2 NonManifoldIn )
```
逐参数原文：`NonManifoldIn`: "Non-manifold [[bodies]]"。`## Returns`: `[[Manifold bodies]]`。★ 该页**没有 `## Remarks` 段**。

**2) `## Remarks` 逐字摘录** —— **查不到**。

**3) 官方例子的调用序** —— 该页 `## Examples` 段逐字列：
`Create and Convert Non-manifold Bodies (C#)` · `Create and Convert Non-manifold Bodies (VB.NET)` · `Create and Convert Non-manifold Bodies (VBA)`。
例文件名 **`C:\swapi\examples\Create_and_Convert_Non-manifold_Bodies_Example_VB.md`**（★ 我在 examples 目录里 grep `MakeManifoldBodies` 命中这三份；★ **但我没有读那三份例子的正文** ⇒ 只抄到它的 `Examples` 指针，**实参 = 查不到**）。

**4) 枚举**：**查不到**。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。

**前置一句话**：查不到。
**配方一句话**：查不到（只有例子名，例子的实参我没读，见上方说明）。

---

## 37. `IModeler.ReplaceSurfaces`

**1) 精确签名（5 个参数）** —— `C:\swapi\types\IModeler\ReplaceSurfaces.md`
```
System.bool ReplaceSurfaces( System.int NFaces, System.object FaceArray, System.object NewSurfArray, System.object SenseArray, System.double Tolerance )
```
逐参数原文：`NFaces` = "Number of faces to have surfaces replaced"；`FaceArray` = "Array of [[faces]] to have the surfaces replaced"；`NewSurfArray` = "Array of [[surfaces]] to be replaced in these faces"；`SenseArray` = "Array of the senses of each surface in NewSurfArray"；`Tolerance` = "Tolerance"。`## Returns`: "True if operation is successful, false if not"。★ 该页**没有 `## Remarks` 段**、**没有 `## Examples` 段**。

**2) `## Remarks` 逐字摘录** —— **查不到**。

**3) 官方例子的调用序** —— **查不到**（无该段；grep `ReplaceSurfaces` 在 examples 目录 = 0 命中）。

**4) 枚举**：**查不到**。

**5) 废弃链**：本页首段**没有 `Obsolete` 字样** ⇒ 不是 Obsolete。见 See Also 点名 `[[IModeler::IReplaceSurfaces2 Method]]` —— ★ 注意 `IReplaceSurfaces2.md` 在 `C:\swapi\types\IModeler\` 里**单独存在**，但 See Also 写的是 `IReplaceSurfaces2`，**官方没有写「Superseded by」** ⇒ **`ReplaceSurfaces` 本身的废弃链 = 查不到**（它没标 Obsolete）。

**前置一句话**：查不到。
**配方一句话**：查不到。

---

# 四 · 本路的「查不到」清单（逐条，供下游按铁律 5 处理）

| 成员 / 内容 | 查不到的是什么 |
|---|---|
| `IFeatureManager.InsertSweepSurface` | 全部 7 个形参的说明（页面写 `No description`）· `## Remarks` · `## Examples` |
| `IFeatureManager.InsertSweepSurface2` | `## Examples` |
| `IFeatureManager.InsertSweepSurface3` | **后继方法名**（官方只写 "Obsolete. See **Remarks**."，Remarks 只指向文档章节 `Sweep Features and SweepFeatureData Objects`，See Also 只给接口 `ISweepFeatureData Interface`） |
| `IFeatureManager.InsertUntrimSurface` | `## Examples` |
| `IFeatureManager.InsertUntrimSurface2` | `C:\swapi\types\*.md` 侧的 `## Examples`（例子只在 CHM） |
| `IFeatureManager.InsertFillSurface` | `Resolution` 的说明与取值 · `## Remarks` · `## Examples` |
| `IFeatureManager.GetPreTrimmedBodies` | `## Remarks`（md 与 CHM 都没有该段）· `## Examples` |
| `IFeatureManager.SetFreeformBoundaryContinuity` | `## Examples`（examples 全目录 0 命中）· `Continuity` 的枚举名（只有内联 −1/0/1/2） |
| `IFeatureManager.FeatureCutThicken` | **mark 取值**（Remarks 未写，与 `FeatureBossThicken` 写了 "mark of 1" 不同）· `## Examples`（examples 全目录 0 命中） |
| `IFeatureManager.InsertSewRefSurface` | `## Remarks` 之外的枚举（5 个形参全非枚举） |
| `IModeler.CreateConicalSurface` / `CreateCylindricalSurface` / `CreatePlanarSurface` / `CreateSphericalSurface` | 4 个形参说明（`No description`）· `## Returns` · `## Remarks` · `## Examples` |
| `IModeler.CreateBsplineSurface` | `## Examples`（examples 全目录 0 命中） |
| `IModeler.CreateCoonsBSurface` | `## Examples`（0 命中） |
| `IModeler.CreateCylindricalSurface2` | **本条自己的调用序** —— 唯一挂在它 Examples 下的例子调的是 `CreateSphericalSurface2` |
| `IModeler.CreateExtrusionSurface` | **`IModeler` 版的实参** —— 唯一命中的例子走的是 `IBody2.ICreateExtrusionSurface` |
| `IModeler.CreateLoftSurface` | `## Remarks` · `## Examples`（0 命中）· `MATCH_*` 的枚举名 |
| `IModeler.CreateOffsetSurface` | `## Remarks` · `## Examples`（0 命中） |
| `IModeler.CreateRuledSurfaceFromEdge` | `Type` 的枚举名（只有内联 0..4） |
| `IModeler.CreateSweptSurface` | `## Examples`（0 命中） |
| `IModeler.CreateToroidalSurface` | `## Examples`（0 命中） |
| `IModeler.MakeManifoldBodies` | `## Remarks` · 例子的实参（只抄到例子名） |
| `IModeler.ReplaceSurfaces` | `## Remarks` · `## Examples`（0 命中）· 官方没写 `IReplaceSurfaces2` 是它的后继 |
| **整个 `IModeler` 接口的 CHM 侧** | CHM 解包里**没有 `IModeler` 任何一页**（文件名与内容双向确认） |
| `IFeatureManager` 目录整体 | **没有名字含 `Knit` 的成员**（Knit 只以形参名出现）；Knit 特征入口是 `InsertSewRefSurface` |

---

# 五 · 抄录计数

| 组 | 成员数 |
|---|---|
| `IFeatureManager`（Sweep / Boundary / Trim / Knit / Thicken / Untrim / Fill） | **15**（`InsertSweepSurface` · `InsertSweepSurface2` · `InsertSweepSurface3` · `InsertUntrimSurface` · `InsertUntrimSurface2` · `InsertFillSurface` · `InsertFillSurface2` · `PreTrimSurface` · `PostTrimSurface` · `SolidForTrim` · `GetPreTrimmedBodies` · `SetFreeformBoundaryContinuity` · `FeatureBossThicken` · `FeatureCutThicken` · `InsertSewRefSurface`） |
| `IModeler` · `Create*Surface` 全族 | **17**（`CreateBsplineSurface` · `CreateConicalSurface` · `CreateConicalSurface2` · `CreateCoonsBSurface` · `CreateCylindricalSurface` · `CreateCylindricalSurface2` · `CreateExtrusionSurface` · `CreateLoftSurface` · `CreateOffsetSurface` · `CreatePlanarSurface` · `CreatePlanarSurface2` · `CreateRuledSurface` · `CreateRuledSurfaceFromEdge` · `CreateSphericalSurface` · `CreateSphericalSurface2` · `CreateSweptSurface` · `CreateToroidalSurface`）—— 其中 **4 个标 Obsolete**：`CreateConicalSurface` / `CreateCylindricalSurface` / `CreatePlanarSurface` / `CreateSphericalSurface`，**四个都点名了 `*2` 后继** |
| 相邻（曲面域、名字不含指定关键词） | **5**（`ThickenSheet` · `GetInitKnitGapWidth` · `SetInitKnitGapWidth` · `MakeManifoldBodies` · `ReplaceSurfaces`） |
| **合计** | **37 个成员** |
| 抄到的枚举 | **9 个**（见第〇节全表） |
| 抄到的官方例子调用序 | **15 份**（`Create_Surface-sweep_Feature_Example_VB` · `Create_Trimmed_Surface_Feature_Example_VB` · `Create_Solid_Body_Surface_Trim_Feature_Example_VB` · `Insert_Fill-surface_Feature_Example_VB` · `Get_and_Fill_Gaps_in_Body_Example_VB` · `Create_Thicken_Feature_Example_VB` · `Thicken_Surface_and_Generate_Boss_Example_VB` · `Fill_Holes_in_Part_Example_VB` · `Create_Surface_Knit_Feature_Example_VB6` · `Create_Infinite_Plane_Example_VB` · `Create_Ruled_Surface_Example_VB` · `Create_Ruled_Surface_From_Edge_Example_VB` · `Create_Imported_Surface_Body_from_Sketch_Example_CSharp` · `Create_Spherical_Surface_Trimmed_Sheet_and_Feature_From_Body_Example_VB` · `Thicken_Sheet_Body_Example_VB` —— 15 份） |
| Obsolete 链 | **8 条有名后继**（`InsertSweepSurface→2` · `InsertSweepSurface2→3` · `InsertUntrimSurface→2` · `InsertFillSurface→2` · `CreateConicalSurface→2` · `CreateCylindricalSurface→2` · `CreatePlanarSurface→2` · `CreateSphericalSurface→2`）+ **1 条无后继名**（`InsertSweepSurface3` → **查不到**） |
