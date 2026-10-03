# api-pre · 分域契约摘要总索引

**本文件是合并者+索引员对 8 份分域契约摘要的合并产物**：逐份读完后抽出每条成员的五元属性，
并把「Remarks 明写前置」「官方例子给了实参」「查不到」三段**单列**出来。
**它不含分域文件里的逐字长摘录** —— 那些留在各分域文件里，本索引只给定位与判定。

---

## 〇 · 源清单与一处缺口（先说清楚）

| # | 分域文件 | 成员数 | 状态 |
|---|---|---|---|
| | `api-01-surface.md` | 37 | ✅ 已读入 |
| | `api-03-weldment.md` | 32 | ✅ 已读入 |
| | `api-04-assembly.md` | 150 | ✅ 已读入 |
| | `api-06-features.md` | 15 | ✅ 已读入 |
| | `api-07-sketch.md` | 196 | ✅ 已读入 |
| | `api-08-mold-costing.md` | 173 | ✅ 已读入 |
| | `api-09-simulation.md` | 33 | ✅ 已读入 |
| | `api-10-routing-pdm-anim.md` | 55 | ✅ 已读入 |
| | `api-02-sheetmetal.md` | — | ⚠ **不存在** |
| | `api-05-drawing.md` | — | ⚠ **不存在** |

★ **本索引覆盖 8 份，不是 10 份。** `api-02-sheetmetal.md` 与 `api-05-drawing.md` 在
`recon\api-pre\` 下不存在（目录列举确认，全仓库 0 命中）。
⇒ **钣金域与工程图域没有任何分域契约摘要可供合并**，本索引在这两域上是空的。
⚠ 同级目录另有 `recon\sheetmetal.md` 与 `recon\api-arity-drawing.md`，但它们**不在本次指定的
`api-pre\` 路径下**，也不是分域契约摘要，**本索引未采信、未合并**。
⇒ 缺口是真实的：**要补钣金与工程图两域，需先补这两份摘要文件。**

---

## 一 · 总表（接口.成员 · 几个参数 · 有没有 Remarks 前置 · 有没有官方例子 · 是否 Obsolete（后继是谁）· 在哪份分域文件里）

★ 读法：`参数`= 官方签名形参个数（`?` = 签名本身查不到）· `前置` = Remarks 段是否明写调用前置 ·
`例子` = 官方例子是否给出实参/调用序 · `源` = 该条抄录自哪份分域文件。

### 源：`api-01-surface.md`（37 条）

| 接口.成员 | 参数 | 前置 | 例子 | Obsolete → 后继 | 源 |
|---|---|---|---|---|---|
| `IFeatureManager.FeatureBossThicken` | 7 | ✅ | ✅ | — | api-01-surface |
| `IFeatureManager.FeatureCutThicken` | 6 | ✅ | — | — | api-01-surface |
| `IFeatureManager.GetPreTrimmedBodies` | 1 | — | — | — | api-01-surface<br>↳ 另见 api-03-weldment |
| `IFeatureManager.InsertFillSurface` | 1 | — | — | ⚠ 是 → `InsertFillSurface2` | api-01-surface |
| `IFeatureManager.InsertFillSurface2` | 6 | ✅ | ✅ | — | api-01-surface |
| `IFeatureManager.InsertSewRefSurface` | 5 | ✅ | ✅ | — | api-01-surface |
| `IFeatureManager.InsertSweepSurface` | 7 | — | — | ⚠ 是 → `InsertSweepSurface2` | api-01-surface |
| `IFeatureManager.InsertSweepSurface2` | 11 | ✅ | — | ⚠ 是 → `InsertSweepSurface3` | api-01-surface |
| `IFeatureManager.InsertSweepSurface3` | 14 | ✅ | ✅ | ⚠ 是 → 后继查不到 | api-01-surface |
| `IFeatureManager.InsertUntrimSurface` | 4 | ✅ | — | ⚠ 是 → `InsertUntrimSurface2` | api-01-surface<br>↳ 另见 api-03-weldment |
| `IFeatureManager.InsertUntrimSurface2` | 5 | ✅ | ✅ | — | api-01-surface<br>↳ 另见 api-03-weldment |
| `IFeatureManager.PostTrimSurface` | 1 | ✅ | ✅ | — | api-01-surface<br>↳ 另见 api-03-weldment |
| `IFeatureManager.PreTrimSurface` | 4 | ✅ | ✅ | — | api-01-surface<br>↳ 另见 api-03-weldment |
| `IFeatureManager.SetFreeformBoundaryContinuity` | 2 | ✅ | — | — | api-01-surface<br>↳ 另见 api-06-features |
| `IFeatureManager.SolidForTrim` | 0 | ✅ | ✅ | — | api-01-surface<br>↳ 另见 api-03-weldment |
| `IModeler.CreateBsplineSurface` | 4 | ✅ | — | — | api-01-surface |
| `IModeler.CreateConicalSurface` | 4 | — | — | ⚠ 是 → `CreateConicalSurface2` | api-01-surface |
| `IModeler.CreateConicalSurface2` | 5 | ✅ | — | — | api-01-surface |
| `IModeler.CreateCoonsBSurface` | 5 | ✅ | — | — | api-01-surface |
| `IModeler.CreateCylindricalSurface` | 3 | — | — | ⚠ 是 → `CreateCylindricalSurface2` | api-01-surface |
| `IModeler.CreateCylindricalSurface2` | 4 | ✅ | — | — | api-01-surface |
| `IModeler.CreateExtrusionSurface` | 2 | ✅ | ✅ | — | api-01-surface |
| `IModeler.CreateLoftSurface` | 18 | — | — | — | api-01-surface |
| `IModeler.CreateOffsetSurface` | 2 | — | — | — | api-01-surface |
| `IModeler.CreatePlanarSurface` | 2 | — | — | ⚠ 是 → `CreatePlanarSurface2` | api-01-surface |
| `IModeler.CreatePlanarSurface2` | 3 | ✅ | ✅ | — | api-01-surface |
| `IModeler.CreateRuledSurface` | 3 | ✅ | ✅ | — | api-01-surface |
| `IModeler.CreateRuledSurfaceFromEdge` | 14 | ✅ | ✅ | — | api-01-surface |
| `IModeler.CreateSphericalSurface` | 2 | — | — | ⚠ 是 → `CreateSphericalSurface2` | api-01-surface |
| `IModeler.CreateSphericalSurface2` | 4 | ✅ | ✅ | — | api-01-surface |
| `IModeler.CreateSweptSurface` | 2 | ✅ | — | — | api-01-surface |
| `IModeler.CreateToroidalSurface` | 5 | ✅ | — | — | api-01-surface |
| `IModeler.GetInitKnitGapWidth` | 0 | ✅ | — | — | api-01-surface |
| `IModeler.MakeManifoldBodies` | 1 | — | — | — | api-01-surface |
| `IModeler.ReplaceSurfaces` | 5 | — | — | — | api-01-surface |
| `IModeler.SetInitKnitGapWidth` | 1 | ✅ | — | — | api-01-surface |
| `IModeler.ThickenSheet` | 3 | ✅ | ✅ | — | api-01-surface |

### 源：`api-03-weldment.md`（32 条）

| 接口.成员 | 参数 | 前置 | 例子 | Obsolete → 后继 | 源 |
|---|---|---|---|---|---|
| `IFeatureManager.CreateStructuralMemberGroup` | 0 | — | ✅ | — | api-03-weldment |
| `IFeatureManager.CutListFolderLocation` | 1 | ✅ | — | — | api-03-weldment |
| `IFeatureManager.GetPreTrimmedBodies` | 1 | — | — | — | api-03-weldment<br>↳ 另见 api-01-surface |
| `IFeatureManager.InsertCosmeticWeldBead` | 1 | ✅ | — | ⚠ 是 → `InsertCosmeticWeldBead2` | api-03-weldment |
| `IFeatureManager.InsertCosmeticWeldBead2` | 4 | ✅ | ✅ | — | api-03-weldment |
| `IFeatureManager.InsertEndCapFeature` | 6 | — | — | ⚠ 是 → `InsertEndCapFeature3` | api-03-weldment |
| `IFeatureManager.InsertEndCapFeature2` | 7 | ✅ | ✅ | — | api-03-weldment |
| `IFeatureManager.InsertEndCapFeature3` | 10 | ✅ | ✅ | — | api-03-weldment |
| `IFeatureManager.InsertFilletBeadFeature` | 12 | — | — | ⚠ 是 → `InsertFilletBeadFeature2` | api-03-weldment |
| `IFeatureManager.InsertFilletBeadFeature2` | 16 | — | — | — | api-03-weldment |
| `IFeatureManager.InsertFilletBeadFeature3` | 18 | ✅ | ✅ | — | api-03-weldment |
| `IFeatureManager.InsertGussetFeature` | 15 | — | — | ⚠ 是 → `InsertGussetFeature3` | api-03-weldment |
| `IFeatureManager.InsertGussetFeature2` | 16 | ✅ | ✅ | — | api-03-weldment |
| `IFeatureManager.InsertGussetFeature3` | 20 | ✅ | ✅ | — | api-03-weldment |
| `IFeatureManager.InsertSheetMetalCornerTrim` | 5 | — | — | — | api-03-weldment |
| `IFeatureManager.InsertStructuralWeldment` | 3 | — | — | ⚠ 是 → `InsertStructuralWeldment2` | api-03-weldment |
| `IFeatureManager.InsertStructuralWeldment2` | 4 | — | — | ⚠ 是 → `InsertStructuralWeldment3` | api-03-weldment |
| `IFeatureManager.InsertStructuralWeldment3` | 5 | ✅ | ✅ | ⚠ 是 → `InsertStructuralWeldment4` | api-03-weldment |
| `IFeatureManager.InsertStructuralWeldment4` | 4 | ✅ | ✅ | ⚠ 是 → `InsertStructuralWeldment5` | api-03-weldment |
| `IFeatureManager.InsertStructuralWeldment5` | 5 | ✅ | ✅ | — | api-03-weldment |
| `IFeatureManager.InsertSubWeldFolder` | 0 | ✅ | — | — | api-03-weldment |
| `IFeatureManager.InsertSubWeldFolder2` | 1 | — | ✅ | — | api-03-weldment |
| `IFeatureManager.InsertUntrimSurface` | 4 | ✅ | — | ⚠ 是 → `InsertUntrimSurface2` | api-03-weldment<br>↳ 另见 api-01-surface |
| `IFeatureManager.InsertUntrimSurface2` | 5 | ✅ | — | — | api-03-weldment<br>↳ 另见 api-01-surface |
| `IFeatureManager.InsertWeldmentCutList` | 0 | — | — | — | api-03-weldment |
| `IFeatureManager.InsertWeldmentCutList2` | 1 | — | ✅ | — | api-03-weldment |
| `IFeatureManager.InsertWeldmentFeature` | 0 | — | ✅ | — | api-03-weldment |
| `IFeatureManager.InsertWeldmentTrimFeature` | 1 | ✅ | — | — | api-03-weldment |
| `IFeatureManager.InsertWeldmentTrimFeature2` | 5 | ✅ | ✅ | — | api-03-weldment |
| `IFeatureManager.PostTrimSurface` | 1 | ✅ | — | — | api-03-weldment<br>↳ 另见 api-01-surface |
| `IFeatureManager.PreTrimSurface` | 4 | ✅ | — | — | api-03-weldment<br>↳ 另见 api-01-surface |
| `IFeatureManager.SolidForTrim` | 0 | ✅ | — | — | api-03-weldment<br>↳ 另见 api-01-surface |

### 源：`api-04-assembly.md`（150 条）

| 接口.成员 | 参数 | 前置 | 例子 | Obsolete → 后继 | 源 |
|---|---|---|---|---|---|
| `IAssemblyDoc.AddConcentricMateWithTolerance` | 5 | ✅ | — | — | api-04-assembly |
| `IAssemblyDoc.AddDistanceMate` | 8 | ✅ | — | — | api-04-assembly |
| `IAssemblyDoc.AddMate` | 5 | — | — | ⚠ 是 → `AddMate3` | api-04-assembly |
| `IAssemblyDoc.AddMate2` | 12 | — | — | ⚠ 是 → `AddMate3` | api-04-assembly |
| `IAssemblyDoc.AddMate3` | 13 | ✅ | — | ⚠ 是 → `AddMate4` | api-04-assembly |
| `IAssemblyDoc.AddMate4` | 14 | ✅ | — | ⚠ 是 → `AddMate5` | api-04-assembly |
| `IAssemblyDoc.AddMate5` | 15 | ✅ | — | ⚠ 是 → `CreateMate` | api-04-assembly |
| `IAssemblyDoc.AutoExplode` | 0 | ✅ | — | — | api-04-assembly |
| `IAssemblyDoc.AutoMateRepair` | 2 | ✅ | — | — | api-04-assembly |
| `IAssemblyDoc.ClearanceVerificationManager` | 0 | — | — | — | api-04-assembly |
| `IAssemblyDoc.CollectAllSupportiveMates` | 0 | ✅ | — | — | api-04-assembly |
| `IAssemblyDoc.CreateExplodedView` | 0 | ✅ | ✅ | — | api-04-assembly |
| `IAssemblyDoc.CreateMate` | 1 | ✅ | — | — | api-04-assembly |
| `IAssemblyDoc.CreateMateData` | 1 | ✅ | — | — | api-04-assembly |
| `IAssemblyDoc.DissolveComponentPattern` | 0 | — | — | — | api-04-assembly |
| `IAssemblyDoc.EditConcentricMate` | 5 | ✅ | — | — | api-04-assembly |
| `IAssemblyDoc.EditDistanceMate` | 8 | ✅ | — | — | api-04-assembly |
| `IAssemblyDoc.EditMate` | 5 | — | — | ⚠ 是 → `EditMate2` | api-04-assembly |
| `IAssemblyDoc.EditMate2` | 13 | ✅ | — | ⚠ 是 → `EditMate3` | api-04-assembly |
| `IAssemblyDoc.EditMate3` | 14 | ✅ | — | ⚠ 是 → `EditMate4` | api-04-assembly |
| `IAssemblyDoc.EditMate4` | 16 | ✅ | — | ⚠ 是 → `各标准/高级/机械配合的 feature data 接口的 Remarks（官方未点名单一成员）` | api-04-assembly |
| `IAssemblyDoc.GetExplodedViewConfigurationName` | 1 | — | — | — | api-04-assembly |
| `IAssemblyDoc.GetExplodedViewCount` | ? | — | ✅ | ⚠ 是 → `GetExplodedViewCount2` | api-04-assembly |
| `IAssemblyDoc.GetExplodedViewCount2` | 1 | — | — | — | api-04-assembly |
| `IAssemblyDoc.GetExplodedViewNames` | ? | — | ✅ | ⚠ 是 → `GetExplodedViewNames2` | api-04-assembly |
| `IAssemblyDoc.GetExplodedViewNames2` | 1 | — | — | — | api-04-assembly |
| `IAssemblyDoc.GetLightWeightComponentCount` | 0 | — | — | — | api-04-assembly |
| `IAssemblyDoc.GetUnloadedComponentNames` | 4 | ✅ | — | — | api-04-assembly |
| `IAssemblyDoc.HasUnloadedComponents` | 0 | — | — | — | api-04-assembly |
| `IAssemblyDoc.InsertDerivedPattern` | 0 | ✅ | — | ⚠ 是 → `IFeatureManager::CreateFeature + IDerivedPatternFeatureData（官方未点名单一成员）` | api-04-assembly |
| `IAssemblyDoc.InterferenceDetectionManager` | 0 | — | — | — | api-04-assembly |
| `IAssemblyDoc.IsSupportedMatesAvailable` | 0 | ✅ | — | — | api-04-assembly |
| `IAssemblyDoc.IToolsCheckInterference2` | 5 | — | — | ⚠ 是 → `IToolsCheckInterference3` | api-04-assembly |
| `IAssemblyDoc.IToolsCheckInterference3` | 5 | ✅ | — | ⚠ 是 → 后继查不到 | api-04-assembly |
| `IAssemblyDoc.LightweightAllResolved` | 0 | ✅ | — | — | api-04-assembly |
| `IAssemblyDoc.MakeLightWeight` | 0 | ✅ | — | — | api-04-assembly |
| `IAssemblyDoc.OpenCompFile` | 0 | — | — | ⚠ 是 → `ISldWorks::ActivateDoc2 + ISldWorks::OpenDoc6` | api-04-assembly |
| `IAssemblyDoc.ResolveAllLightweight` | 0 | ✅ | — | — | api-04-assembly |
| `IAssemblyDoc.ResolveAllLightWeightComponents` | 1 | ✅ | — | — | api-04-assembly |
| `IAssemblyDoc.ResolveOutOfDateLightWeightComponents` | 0 | ✅ | — | — | api-04-assembly |
| `IAssemblyDoc.ShowExploded` | ? | — | — | ⚠ 是 → `ShowExploded2` | api-04-assembly |
| `IAssemblyDoc.ShowExploded2` | 2 | — | ✅ | — | api-04-assembly |
| `IAssemblyDoc.ToolsCheckInterference` | 0 | ✅ | — | ⚠ 是 → `ToolsCheckInterference2` | api-04-assembly |
| `IAssemblyDoc.ToolsCheckInterference2` | 5 | ✅ | ✅ | — | api-04-assembly |
| `IAssemblyDoc.ViewCollapseAssembly` | 0 | ✅ | ✅ | — | api-04-assembly |
| `IAssemblyDoc.ViewExplodeAssembly` | 0 | ✅ | ✅ | — | api-04-assembly |
| `IComponent2.GetChildren` | 0 | ✅ | ✅ | — | api-04-assembly |
| `IComponent2.GetHiddenUnloadedChildrenCount` | 0 | ✅ | — | — | api-04-assembly |
| `IComponent2.GetMates` | 0 | ✅ | — | — | api-04-assembly |
| `IComponent2.GetSpecificTransform` | 1 | — | — | — | api-04-assembly |
| `IComponent2.GetSuppression` | 0 | ✅ | — | ⚠ 是 → `GetSuppression2` | api-04-assembly |
| `IComponent2.GetSuppression2` | 0 | ✅ | — | — | api-04-assembly |
| `IComponent2.GetTotalTransform` | 1 | — | — | — | api-04-assembly |
| `IComponent2.GetUnloadedComponentNames` | 4 | ✅ | — | — | api-04-assembly |
| `IComponent2.HasUnloadedComponents` | 0 | — | — | — | api-04-assembly |
| `IComponent2.IGetChildrenCount` | 0 | ✅ | — | — | api-04-assembly |
| `IComponent2.IsEnvelope` | 0 | ✅ | — | — | api-04-assembly |
| `IComponent2.IsGraphicsOnly` | 0 | — | — | — | api-04-assembly |
| `IComponent2.IsHidden` | 1 | ✅ | — | — | api-04-assembly |
| `IComponent2.IsLoaded` | 0 | — | — | — | api-04-assembly |
| `IComponent2.IsPatternInstance` | 0 | ✅ | — | — | api-04-assembly |
| `IComponent2.IsSuppressed` | 0 | ✅ | — | — | api-04-assembly |
| `IComponent2.IsVirtual` | 0 | ✅ | — | — | api-04-assembly |
| `IComponent2.Select4` | 3 | — | ✅ | — | api-04-assembly |
| `IComponent2.SetSuppression` | 1 | — | — | ⚠ 是 → `SetSuppression2` | api-04-assembly |
| `IComponent2.SetSuppression2` | 1 | ✅ | ✅ | — | api-04-assembly |
| `IComponent2.SetTransformAndSolve2` | 1 | — | — | ⚠ 是 → `SetTransformAndSolve3` | api-04-assembly |
| `IComponent2.SetTransformAndSolve3` | 2 | — | — | — | api-04-assembly |
| `IComponent2.SetVisibility` | 3 | — | — | — | api-04-assembly |
| `IComponent2.Transform2` | 0 | ✅ | — | — | api-04-assembly |
| `IComponent2.Visible` | 0 | ✅ | — | — | api-04-assembly |
| `IExplodeStep.AutoSpaceComponentsOnDrag` | 0 | ✅ | — | — | api-04-assembly |
| `IExplodeStep.DivergeDirection` | 0 | ✅ | — | — | api-04-assembly |
| `IExplodeStep.DivergeFromAxis` | 0 | ✅ | — | — | api-04-assembly |
| `IExplodeStep.ExplodeDistance` | 0 | — | — | — | api-04-assembly |
| `IExplodeStep.ExplodeStepType` | 0 | — | — | — | api-04-assembly |
| `IExplodeStep.GetComponent` | 1 | ✅ | — | — | api-04-assembly |
| `IExplodeStep.GetComponentName` | 1 | ✅ | — | — | api-04-assembly |
| `IExplodeStep.GetComponents` | 0 | — | — | — | api-04-assembly |
| `IExplodeStep.GetComponentXform` | 0 | — | — | — | api-04-assembly |
| `IExplodeStep.GetExplodeDirection` | 1 | ✅ | — | — | api-04-assembly |
| `IExplodeStep.GetNumOfComponents` | 0 | — | ✅ | — | api-04-assembly |
| `IExplodeStep.GetRotationAxis` | 1 | ✅ | — | — | api-04-assembly |
| `IExplodeStep.GetSpecificComponentXForm` | 1 | ✅ | — | — | api-04-assembly |
| `IExplodeStep.GetSubAssemblyExplodeSteps` | 0 | ✅ | — | — | api-04-assembly |
| `IExplodeStep.IGetComponent` | 1 | ✅ | — | — | api-04-assembly |
| `IExplodeStep.IGetComponentXform` | 0 | — | — | — | api-04-assembly |
| `IExplodeStep.IsSubAssemblyRigid` | 0 | ✅ | ✅ | — | api-04-assembly |
| `IExplodeStep.Name` | 0 | — | ✅ | — | api-04-assembly |
| `IExplodeStep.ReverseRotationDirection` | 0 | ✅ | — | — | api-04-assembly |
| `IExplodeStep.ReverseTranslationDirection` | 0 | ✅ | — | — | api-04-assembly |
| `IExplodeStep.RotateAboutEachComponentOrigin` | 0 | ✅ | — | — | api-04-assembly |
| `IExplodeStep.RotationAngle` | 0 | ✅ | — | — | api-04-assembly |
| `IExplodeStep.SetComponents` | 1 | ✅ | — | — | api-04-assembly |
| `IExplodeStep.SetExplodeDirection` | 2 | — | — | — | api-04-assembly |
| `IExplodeStep.SetRotationAxis` | 2 | — | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.CreateFastenersFolder` | 0 | ✅ | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.Done` | 0 | — | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.ExportResults` | 2 | ✅ | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.GetComponentsAndTransforms` | 2 | — | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.GetComponentsTransformInterference` | 3 | — | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.GetComponentsTransformInterferenceCount` | 3 | ✅ | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.GetInterferenceComponentCount` | 0 | ✅ | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.GetInterferenceComponents` | 0 | — | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.GetInterferenceCount` | 0 | ✅ | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.GetInterferences` | 0 | — | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.IGetComponentsTransformInterference` | ? | — | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.IGetInterferenceComponents` | ? | — | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.IGetInterferences` | ? | — | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.IgnoreHiddenBodies` | 0 | ✅ | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.IncludeMultibodyPartInterferences` | 0 | ✅ | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.MakeInterferingPartsTransparent` | 0 | ✅ | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.NonInterferingComponentDisplay` | 0 | — | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.SetComponentsAndTransforms` | 2 | ✅ | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.ShowIgnoredInterferences` | 0 | ✅ | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.TreatCoincidenceAsInterference` | 0 | ✅ | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.TreatSubAssembliesAsComponents` | 0 | ✅ | — | — | api-04-assembly |
| `IInterferenceDetectionMgr.UseTransform` | 0 | — | — | — | api-04-assembly |
| `IMate2.Alignment` | 0 | — | — | — | api-04-assembly |
| `IMate2.CanBeFlipped` | 0 | ✅ | — | — | api-04-assembly |
| `IMate2.DisplayDimension` | ? | — | — | ⚠ 是 → `DisplayDimension2` | api-04-assembly |
| `IMate2.DisplayDimension2` | ? | — | — | — | api-04-assembly |
| `IMate2.DistanceFirstArcCondition` | 0 | ✅ | — | — | api-04-assembly |
| `IMate2.DistanceSecondArcCondition` | 0 | ✅ | — | — | api-04-assembly |
| `IMate2.Flipped` | 0 | — | — | — | api-04-assembly |
| `IMate2.ForceMisalignment` | 0 | — | — | — | api-04-assembly |
| `IMate2.GetConcentricAlignmentType` | 0 | — | — | — | api-04-assembly |
| `IMate2.GetCurrentMisalignedDeviation` | 0 | ✅ | — | — | api-04-assembly |
| `IMate2.GetForce` | 1 | — | — | — | api-04-assembly |
| `IMate2.GetLinkedMate` | 0 | ✅ | — | — | api-04-assembly |
| `IMate2.GetMateEntityCount` | 0 | ✅ | — | — | api-04-assembly |
| `IMate2.GetMaximumMisalignedDeviation` | 0 | ✅ | — | — | api-04-assembly |
| `IMate2.GetSupplementalFaces` | 1 | — | — | — | api-04-assembly |
| `IMate2.GetTorque` | 1 | — | — | — | api-04-assembly |
| `IMate2.GetUseMisalignedDeviationDocumentProperty` | 0 | ✅ | — | — | api-04-assembly |
| `IMate2.HasLoadBearingFaces` | 0 | — | — | — | api-04-assembly |
| `IMate2.HasTreatInterferenceAsShrinkFit` | 0 | — | — | — | api-04-assembly |
| `IMate2.IsLoadBearingFacesBonded` | 0 | — | — | — | api-04-assembly |
| `IMate2.LockMagneticMate` | 0 | ✅ | — | — | api-04-assembly |
| `IMate2.MateEntity` | 1 | ✅ | — | — | api-04-assembly |
| `IMate2.MateLoadReference` | 0 | — | — | — | api-04-assembly |
| `IMate2.MaximumVariation` | 0 | ✅ | — | — | api-04-assembly |
| `IMate2.MinimumVariation` | 0 | ✅ | — | — | api-04-assembly |
| `IMate2.RemoveMisalignment` | 0 | ✅ | — | — | api-04-assembly |
| `IMate2.SetConcentricAlignmentType` | 1 | — | — | — | api-04-assembly |
| `IMate2.SetForce` | 2 | — | — | — | api-04-assembly |
| `IMate2.SetMaximumMisalignedDeviation` | 1 | ✅ | — | — | api-04-assembly |
| `IMate2.SetTorque` | 2 | — | — | — | api-04-assembly |
| `IMate2.SetUseMisalignedDeviationDocumentProperty` | 1 | ✅ | — | — | api-04-assembly |
| `IMate2.Type` | 0 | — | — | — | api-04-assembly |

### 源：`api-06-features.md`（15 条）

| 接口.成员 | 参数 | 前置 | 例子 | Obsolete → 后继 | 源 |
|---|---|---|---|---|---|
| `IFeatureManager.CreateDefinition` | 1 | — | ✅ | — | api-06-features |
| `IFeatureManager.FeatureLocalCurveDrivenPattern` | 13 | ✅ | — | ⚠ 是 → `CreateFeature` | api-06-features |
| `IFeatureManager.IInsertCombineFeature` | 4 | ✅ | — | — | api-06-features |
| `IFeatureManager.InsertCombineFeature` | 3 | ✅ | ✅ | — | api-06-features |
| `IFeatureManager.InsertFlexFeature` | 17 | — | — | — | api-06-features |
| `IFeatureManager.InsertIndent` | 6 | ✅ | ✅ | — | api-06-features |
| `IFeatureManager.InsertRib` | 10 | — | ✅ | — | api-06-features |
| `IFeatureManager.InsertScale` | 5 | ✅ | ✅ | — | api-06-features |
| `IFeatureManager.InsertSplitLineIntersect` | 1 | — | — | — | api-06-features |
| `IFeatureManager.InsertWrapFeature` | 3 | ✅ | ✅ | ⚠ 是 → `InsertWrapFeature2` | api-06-features |
| `IFeatureManager.InsertWrapFeature2` | 5 | ✅ | ✅ | — | api-06-features |
| `IFeatureManager.PostIntersect` | 3 | ✅ | ✅ | — | api-06-features |
| `IFeatureManager.PreIntersect` | 1 | ✅ | ✅ | ⚠ 是 → `PreIntersect2` | api-06-features |
| `IFeatureManager.PreIntersect2` | 2 | ✅ | ✅ | — | api-06-features |
| `IFeatureManager.SetFreeformBoundaryContinuity` | 2 | ✅ | — | — | api-06-features<br>↳ 另见 api-01-surface |

### 源：`api-07-sketch.md`（196 条）

| 接口.成员 | 参数 | 前置 | 例子 | Obsolete → 后继 | 源 |
|---|---|---|---|---|---|
| `ISketch.AutoDimension` | 5 | — | — | ⚠ 是 → `AutoDimension2` | api-07-sketch |
| `ISketch.AutoDimension2` | 5 | ✅ | ✅ | ⚠ 是 → `ISketchManager::FullyDefineSketch` | api-07-sketch |
| `ISketch.CheckFeatureUse` | 3 | ✅ | ✅ | — | api-07-sketch |
| `ISketch.ConstrainAll` | 0 | ✅ | — | — | api-07-sketch |
| `ISketch.GetArcCount` | 0 | ✅ | ✅ | — | api-07-sketch |
| `ISketch.GetArcs` | 0 | — | — | ⚠ 是 → `GetArcs2 and IGetArcs2` | api-07-sketch |
| `ISketch.GetArcs2` | 0 | ✅ | ✅ | — | api-07-sketch |
| `ISketch.GetAutomaticSolve` | 0 | — | — | — | api-07-sketch |
| `ISketch.GetConstrainedStatus` | 0 | — | — | — | api-07-sketch |
| `ISketch.GetContourEdgeCount` | 0 | ✅ | — | — | api-07-sketch |
| `ISketch.GetContourEdges` | 1 | ✅ | — | — | api-07-sketch |
| `ISketch.GetDetachSegmentOnDrag` | 0 | ✅ | — | — | api-07-sketch |
| `ISketch.GetEllipseCount` | 0 | ✅ | ✅ | — | api-07-sketch |
| `ISketch.GetEllipses` | 0 | — | — | ⚠ 是 → `GetEllipses3 and IGetEllipses3` | api-07-sketch |
| `ISketch.GetEllipses2` | 0 | — | — | ⚠ 是 → `GetEllipses3 and IGetEllipses3` | api-07-sketch |
| `ISketch.GetEllipses3` | 0 | ✅ | — | — | api-07-sketch |
| `ISketch.GetLineCount` | 0 | — | — | ⚠ 是 → `GetLineCount2` | api-07-sketch |
| `ISketch.GetLineCount2` | 1 | ✅ | ✅ | — | api-07-sketch |
| `ISketch.GetLines` | 0 | — | — | ⚠ 是 → `GetLines2 and IGetLines2` | api-07-sketch |
| `ISketch.GetLines2` | 1 | ✅ | ✅ | — | api-07-sketch |
| `ISketch.GetParabolaCount` | 0 | ✅ | ✅ | — | api-07-sketch |
| `ISketch.GetParabolas` | 0 | — | — | ⚠ 是 → `GetParabolas2 and IGetParabolas2` | api-07-sketch |
| `ISketch.GetParabolas2` | 0 | ✅ | — | — | api-07-sketch |
| `ISketch.GetPolyLineCount` | 1 | — | — | — | api-07-sketch |
| `ISketch.GetPolylines` | 0 | — | — | — | api-07-sketch |
| `ISketch.GetReferenceEntity` | 1 | ✅ | ✅ | — | api-07-sketch |
| `ISketch.GetSketchBlockInstanceCount` | 0 | ✅ | — | — | api-07-sketch |
| `ISketch.GetSketchBlockInstances` | 0 | — | — | — | api-07-sketch |
| `ISketch.GetSketchContourCount` | 0 | ✅ | — | — | api-07-sketch |
| `ISketch.GetSketchContours` | 0 | ✅ | — | — | api-07-sketch |
| `ISketch.GetSketchHatches` | 0 | — | — | — | api-07-sketch |
| `ISketch.GetSketchPathCount` | 0 | ✅ | — | — | api-07-sketch |
| `ISketch.GetSketchPaths` | 0 | ✅ | ✅ | — | api-07-sketch |
| `ISketch.GetSketchPictureCount` | 0 | ✅ | — | — | api-07-sketch |
| `ISketch.GetSketchPictures` | 0 | — | — | — | api-07-sketch |
| `ISketch.GetSketchPoints` | 0 | — | — | ⚠ 是 → `GetSketchPoints2, IGetSketchPoints2, IEnumSketchPoints` | api-07-sketch |
| `ISketch.GetSketchPoints2` | 0 | — | — | — | api-07-sketch |
| `ISketch.GetSketchPointsCount` | 0 | — | — | ⚠ 是 → `GetSketchPointsCount2` | api-07-sketch |
| `ISketch.GetSketchPointsCount2` | 0 | ✅ | ✅ | — | api-07-sketch |
| `ISketch.GetSketchRegionCount` | 0 | ✅ | — | — | api-07-sketch |
| `ISketch.GetSketchRegions` | 0 | — | — | — | api-07-sketch |
| `ISketch.GetSketchSegments` | 0 | ✅ | ✅ | — | api-07-sketch |
| `ISketch.GetSketchSlotCount` | 0 | ✅ | — | — | api-07-sketch |
| `ISketch.GetSketchSlots` | 0 | — | — | — | api-07-sketch |
| `ISketch.GetSketchTextSegments` | 0 | — | — | — | api-07-sketch |
| `ISketch.GetSplineCount` | 1 | ✅ | ✅ | — | api-07-sketch |
| `ISketch.GetSplineInterpolateCount` | 1 | ✅ | — | — | api-07-sketch |
| `ISketch.GetSplineParams` | 0 | — | — | ⚠ 是 → `GetSplineParams2 and IGetSplineParams2` | api-07-sketch |
| `ISketch.GetSplineParams2` | 0 | — | — | ⚠ 是 → `GetSplineParams3` | api-07-sketch |
| `ISketch.GetSplineParams3` | 1 | — | — | ⚠ 是 → `GetSplineParams4` | api-07-sketch |
| `ISketch.GetSplineParams4` | 1 | ✅ | ✅ | ⚠ 是 → `GetSplineParams5` | api-07-sketch |
| `ISketch.GetSplineParams5` | 2 | — | ✅ | — | api-07-sketch |
| `ISketch.GetSplineParamsCount` | 1 | — | — | ⚠ 是 → `GetSplineParamsCount2` | api-07-sketch |
| `ISketch.GetSplineParamsCount2` | 1 | — | — | ⚠ 是 → `GetSplineParamsCount3` | api-07-sketch |
| `ISketch.GetSplineParamsCount3` | 2 | — | — | — | api-07-sketch |
| `ISketch.GetSplines` | 0 | ✅ | — | — | api-07-sketch |
| `ISketch.GetSplinesInterpolate` | 0 | ✅ | ✅ | — | api-07-sketch |
| `ISketch.GetUserPoints` | 0 | — | — | ⚠ 是 → `GetUserPoints2 and IGetUserPoints2` | api-07-sketch |
| `ISketch.GetUserPoints2` | 0 | ✅ | — | — | api-07-sketch |
| `ISketch.GetUserPointsCount` | 0 | ✅ | ✅ | — | api-07-sketch |
| `ISketch.IEnumSketchHatches` | 0 | — | — | — | api-07-sketch |
| `ISketch.IEnumSketchPoints` | 0 | — | — | — | api-07-sketch |
| `ISketch.IEnumSketchSegments` | 0 | ✅ | ✅ | — | api-07-sketch |
| `ISketch.IEnumSketchTextSegments` | 0 | — | — | — | api-07-sketch |
| `ISketch.IGetArcs` | 0 | — | — | ⚠ 是 → `GetArcs2 and IGetArcs2` | api-07-sketch |
| `ISketch.IGetArcs2` | 1 | ✅ | — | — | api-07-sketch |
| `ISketch.IGetContourEdges` | 2 | ✅ | — | — | api-07-sketch |
| `ISketch.IGetEllipses` | 0 | — | — | ⚠ 是 → `GetEllipses3 and IGetEllipses3` | api-07-sketch |
| `ISketch.IGetEllipses2` | 0 | — | — | ⚠ 是 → `GetEllipses3 and IGetEllipses3` | api-07-sketch |
| `ISketch.IGetEllipses3` | 1 | ✅ | — | — | api-07-sketch |
| `ISketch.IGetLines` | 0 | — | — | ⚠ 是 → `GetLines2 and IGetLines2` | api-07-sketch |
| `ISketch.IGetLines2` | 2 | ✅ | — | — | api-07-sketch |
| `ISketch.IGetParabolas` | 0 | — | — | ⚠ 是 → `GetParabolas2 and IGetParabolas2` | api-07-sketch |
| `ISketch.IGetParabolas2` | 1 | ✅ | — | — | api-07-sketch |
| `ISketch.IGetPolylines` | 0 | — | — | — | api-07-sketch |
| `ISketch.IGetSketchBlockInstances` | 1 | ✅ | — | — | api-07-sketch |
| `ISketch.IGetSketchContours` | 1 | ✅ | — | — | api-07-sketch |
| `ISketch.IGetSketchPaths` | 1 | ✅ | — | — | api-07-sketch |
| `ISketch.IGetSketchPictures` | 1 | ✅ | — | — | api-07-sketch |
| `ISketch.IGetSketchPoints2` | 1 | ✅ | — | — | api-07-sketch |
| `ISketch.IGetSketchRegions` | 1 | ✅ | — | — | api-07-sketch |
| `ISketch.IGetSketchSlots` | 1 | ✅ | — | — | api-07-sketch |
| `ISketch.IGetSplineParams` | 0 | — | — | ⚠ 是 → `GetSplineParams2 and IGetSplineParams2` | api-07-sketch |
| `ISketch.IGetSplineParams2` | 0 | — | — | ⚠ 是 → `IGetSplineParameters3` | api-07-sketch |
| `ISketch.IGetSplineParams3` | 1 | — | — | ⚠ 是 → `GetSplineParams4` | api-07-sketch |
| `ISketch.IGetSplines` | 0 | ✅ | — | — | api-07-sketch |
| `ISketch.IGetSplinesInterpolate` | 0 | ✅ | — | — | api-07-sketch |
| `ISketch.IGetUserPoints` | 0 | — | — | ⚠ 是 → `GetUserPoints2 and IGetUserPoints2` | api-07-sketch |
| `ISketch.IGetUserPoints2` | 1 | ✅ | — | — | api-07-sketch |
| `ISketch.IModelToSketchXform` | 0 | — | — | ⚠ 是 → `ModelToSketchTransform` | api-07-sketch |
| `ISketch.InsertRouteLine` | 4 | ✅ | ✅ | — | api-07-sketch |
| `ISketch.Is3D` | 0 | — | — | — | api-07-sketch |
| `ISketch.IsBoundaryBoxSketch` | 0 | — | — | — | api-07-sketch |
| `ISketch.IsDerived` | 0 | — | — | — | api-07-sketch |
| `ISketch.IsShared` | 0 | — | — | — | api-07-sketch |
| `ISketch.IsSketchEditable` | 0 | — | — | — | api-07-sketch |
| `ISketch.MergePoints` | 1 | ✅ | — | — | api-07-sketch |
| `ISketch.ModelToSketchTransform` | 0 | — | — | — | api-07-sketch |
| `ISketch.ModelToSketchXform` | 0 | — | — | ⚠ 是 → `ModelToSketchTransform` | api-07-sketch |
| `ISketch.RelationManager` | 0 | — | — | — | api-07-sketch |
| `ISketch.SetAutomaticSolve` | 1 | ✅ | — | — | api-07-sketch |
| `ISketch.SetDetachSegmentOnDrag` | 1 | ✅ | — | — | api-07-sketch |
| `ISketch.SetSketchEditable` | 1 | — | — | — | api-07-sketch |
| `ISketch.SetWorkingPlaneOrientation` | 12 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.ActiveSketch` | 0 | — | ✅ | — | api-07-sketch |
| `ISketchManager.AddAlongXDimension` | 3 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.AddAlongYDimension` | 3 | ✅ | — | — | api-07-sketch |
| `ISketchManager.AddAlongZDimension` | 3 | ✅ | — | — | api-07-sketch |
| `ISketchManager.AddToDB` | 0 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.AutoInference` | 0 | — | — | ⚠ 是 → `ISldWorks::SetUserPreferenceToggle（swUserPreferenceToggle_e.swSketchInference）` | api-07-sketch |
| `ISketchManager.AutoSolve` | 0 | — | — | — | api-07-sketch |
| `ISketchManager.ConvertEntities` | 0 | — | — | — | api-07-sketch |
| `ISketchManager.Create3PointArc` | 9 | — | — | — | api-07-sketch |
| `ISketchManager.Create3PointCenterRectangle` | 9 | — | — | — | api-07-sketch |
| `ISketchManager.Create3PointCornerRectangle` | 9 | — | — | — | api-07-sketch |
| `ISketchManager.CreateArc` | 10 | ✅ | — | — | api-07-sketch |
| `ISketchManager.CreateBoundaryHatch` | 5 | ✅ | — | — | api-07-sketch |
| `ISketchManager.CreateCenterLine` | 6 | — | ✅ | — | api-07-sketch |
| `ISketchManager.CreateCenterRectangle` | 6 | — | — | — | api-07-sketch |
| `ISketchManager.CreateChamfer` | 3 | — | — | — | api-07-sketch |
| `ISketchManager.CreateCircle` | 6 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.CreateCircleByRadius` | 4 | ✅ | — | — | api-07-sketch |
| `ISketchManager.CreateCircularSketchStepAndRepeat` | 9 | — | ✅ | — | api-07-sketch |
| `ISketchManager.CreateConic` | 12 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.CreateConstructionGeometry` | 0 | ✅ | — | — | api-07-sketch |
| `ISketchManager.CreateCornerRectangle` | 6 | — | ✅ | — | api-07-sketch |
| `ISketchManager.CreateEllipse` | 9 | ✅ | — | — | api-07-sketch |
| `ISketchManager.CreateEllipticalArc` | 15 | ✅ | — | — | api-07-sketch |
| `ISketchManager.CreateEquationSpline` | 9 | — | — | ⚠ 是 → `CreateEquationSpline2` | api-07-sketch |
| `ISketchManager.CreateEquationSpline2` | 11 | — | ✅ | — | api-07-sketch |
| `ISketchManager.CreateFillet` | 2 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.CreateLine` | 6 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.CreateLinearSketchStepAndRepeat` | 12 | — | ✅ | — | api-07-sketch |
| `ISketchManager.CreateParabola` | 12 | — | — | — | api-07-sketch |
| `ISketchManager.CreateParallelogram` | 9 | — | — | — | api-07-sketch |
| `ISketchManager.CreatePoint` | 3 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.CreatePolygon` | 7 | — | — | — | api-07-sketch |
| `ISketchManager.CreateRegionHatch` | 8 | ✅ | — | — | api-07-sketch |
| `ISketchManager.CreateSketchBelt` | 15 | ✅ | — | — | api-07-sketch |
| `ISketchManager.CreateSketchPlane` | 3 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.CreateSketchSlot` | 13 | — | ✅ | — | api-07-sketch |
| `ISketchManager.CreateSpline` | 1 | ✅ | ✅ | ⚠ 是 → `CreateSpline2` | api-07-sketch |
| `ISketchManager.CreateSpline2` | 2 | ✅ | ✅ | ⚠ 是 → `CreateSpline3` | api-07-sketch |
| `ISketchManager.CreateSpline3` | 5 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.CreateSplineByEqnParams` | 1 | ✅ | — | — | api-07-sketch |
| `ISketchManager.CreateSplineParamData` | 0 | — | ✅ | — | api-07-sketch |
| `ISketchManager.CreateSplinesByEqnParams` | 1 | ✅ | — | ⚠ 是 → `CreateSplinesByEqnParams2` | api-07-sketch |
| `ISketchManager.CreateSplinesByEqnParams2` | 1 | — | ✅ | — | api-07-sketch |
| `ISketchManager.CreateTangentArc` | 7 | — | — | — | api-07-sketch |
| `ISketchManager.CurvatureDensity` | 0 | — | — | — | api-07-sketch |
| `ISketchManager.CurvatureScale` | 0 | — | — | — | api-07-sketch |
| `ISketchManager.DisplayWhenAdded` | 0 | ✅ | — | — | api-07-sketch |
| `ISketchManager.Document` | 0 | — | — | — | api-07-sketch |
| `ISketchManager.EditCircularSketchStepAndRepeat` | 10 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.EditLinearSketchStepAndRepeat` | 13 | — | ✅ | — | api-07-sketch |
| `ISketchManager.EditSketchBlock` | 0 | ✅ | — | — | api-07-sketch |
| `ISketchManager.EndEditSketchBlock` | 1 | ✅ | — | — | api-07-sketch |
| `ISketchManager.ExplodeSketchBlockInstance` | 1 | ✅ | — | — | api-07-sketch |
| `ISketchManager.FullyDefineSketch` | 10 | — | — | — | api-07-sketch |
| `ISketchManager.GetDynamicMirror` | 0 | — | — | — | api-07-sketch |
| `ISketchManager.GetSketchBlockDefinitionCount` | 0 | ✅ | — | — | api-07-sketch |
| `ISketchManager.GetSketchBlockDefinitions` | 0 | — | — | — | api-07-sketch |
| `ISketchManager.ICreateSpline` | 2 | ✅ | — | ⚠ 是 → `ICreateSpline2` | api-07-sketch |
| `ISketchManager.ICreateSpline2` | 3 | ✅ | — | — | api-07-sketch |
| `ISketchManager.ICreateSplineByEqnParams` | 5 | ✅ | — | — | api-07-sketch |
| `ISketchManager.ICreateSplinesByEqnParams` | 5 | ✅ | — | — | api-07-sketch |
| `ISketchManager.IGetSketchBlockDefinitions` | 1 | ✅ | — | — | api-07-sketch |
| `ISketchManager.InferenceMode` | 0 | ✅ | — | ⚠ 是 → `ISldWorks::SetUserPreferenceToggle（swUserPreferenceToggle_e.swSketchInference）` | api-07-sketch |
| `ISketchManager.Insert3DSketch` | 1 | — | ✅ | — | api-07-sketch |
| `ISketchManager.InsertExplodeLineSketch` | 0 | — | ✅ | — | api-07-sketch |
| `ISketchManager.InsertSketch` | 1 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.InsertSketchBlockInstance` | 4 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.InsertSketchPicture` | 1 | — | — | ⚠ 是 → `InsertSketchPicture2` | api-07-sketch |
| `ISketchManager.InsertSketchPicture2` | 2 | — | ✅ | — | api-07-sketch |
| `ISketchManager.IntersectCurves` | 0 | — | — | — | api-07-sketch |
| `ISketchManager.MakeSketchBlockFromFile` | 5 | ✅ | — | — | api-07-sketch |
| `ISketchManager.MakeSketchBlockFromSelected` | 1 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.MakeSketchBlockFromSketch` | 2 | — | — | — | api-07-sketch |
| `ISketchManager.MakeSketchChain` | 0 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.PerimeterCircle` | 6 | — | — | — | api-07-sketch |
| `ISketchManager.ReverseEndPointTangent` | 1 | — | — | — | api-07-sketch |
| `ISketchManager.RotateOrCopy3DAboutVector` | 10 | — | — | — | api-07-sketch |
| `ISketchManager.RotateOrCopy3DAboutXYZ` | 9 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.SetDynamicMirror` | 1 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.SetGridOptions` | 10 | ✅ | — | — | api-07-sketch |
| `ISketchManager.SketchExtend` | 3 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.SketchOffset` | 6 | — | — | ⚠ 是 → `SketchOffset2` | api-07-sketch |
| `ISketchManager.SketchOffset2` | 6 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.SketchReplace` | 1 | ✅ | — | ⚠ 是 → `SketchReplace2` | api-07-sketch |
| `ISketchManager.SketchReplace2` | 2 | ✅ | — | — | api-07-sketch |
| `ISketchManager.SketchTrim` | 4 | ✅ | — | — | api-07-sketch |
| `ISketchManager.SketchUseEdge` | 1 | — | — | ⚠ 是 → `SketchUseEdge2` | api-07-sketch |
| `ISketchManager.SketchUseEdge2` | 1 | — | — | ⚠ 是 → `SketchUseEdge3` | api-07-sketch |
| `ISketchManager.SketchUseEdge3` | 2 | — | — | — | api-07-sketch |
| `ISketchManager.SplitClosedSegment` | 6 | ✅ | ✅ | — | api-07-sketch |
| `ISketchManager.SplitOpenSegment` | 3 | ✅ | ✅ | — | api-07-sketch |

### 源：`api-08-mold-costing.md`（173 条）

| 接口.成员 | 参数 | 前置 | 例子 | Obsolete → 后继 | 源 |
|---|---|---|---|---|---|
| `IAssemblyDoc.InsertCavity` | 0 | — | — | ⚠ 是 → `InsertCavity4` | api-08-mold-costing |
| `IAssemblyDoc.InsertCavity2` | 2 | — | — | ⚠ 是 → `InsertCavity4` | api-08-mold-costing |
| `IAssemblyDoc.InsertCavity3` | 3 | — | — | ⚠ 是 → `InsertCavity4` | api-08-mold-costing |
| `IAssemblyDoc.InsertCavity4` | 6 | ✅ | — | — | api-08-mold-costing |
| `ICavityFeatureData.AccessSelections` | 2 | ✅ | ✅ | — | api-08-mold-costing |
| `ICavityFeatureData.Components` | 0 | ✅ | — | — | api-08-mold-costing |
| `ICavityFeatureData.GetComponentsCount` | 0 | ✅ | — | — | api-08-mold-costing |
| `ICavityFeatureData.GetScale` | 3 | — | ✅ | — | api-08-mold-costing |
| `ICavityFeatureData.IGetComponents` | 2 | ✅ | — | — | api-08-mold-costing |
| `ICavityFeatureData.ISetComponents` | 2 | ✅ | — | — | api-08-mold-costing |
| `ICavityFeatureData.ReleaseSelectionAccess` | 0 | ✅ | — | — | api-08-mold-costing |
| `ICavityFeatureData.ScaleType` | 0 | — | ✅ | — | api-08-mold-costing |
| `ICavityFeatureData.SetScale` | 3 | — | — | — | api-08-mold-costing |
| `ICavityFeatureData.UniformScale` | 0 | ✅ | ✅ | — | api-08-mold-costing |
| `ICavityFeatureData.UseUniformScale` | 0 | ✅ | ✅ | — | api-08-mold-costing |
| `ICoreFeatureData.AccessSelections` | 2 | ✅ | ✅ | — | api-08-mold-costing |
| `ICoreFeatureData.BoundingSketch` | 0 | ✅ | ✅ | — | api-08-mold-costing |
| `ICoreFeatureData.CapEnds` | 0 | — | ✅ | — | api-08-mold-costing |
| `ICoreFeatureData.Depth` | 1 | — | ✅ | — | api-08-mold-costing |
| `ICoreFeatureData.DraftAngle` | 0 | ✅ | ✅ | — | api-08-mold-costing |
| `ICoreFeatureData.DraftOutward` | 0 | ✅ | ✅ | — | api-08-mold-costing |
| `ICoreFeatureData.EndCondition` | 1 | ✅ | ✅ | — | api-08-mold-costing |
| `ICoreFeatureData.GetExtractionDirection` | 4 | ✅ | ✅ | — | api-08-mold-costing |
| `ICoreFeatureData.ReleaseSelectionAccess` | 0 | ✅ | ✅ | — | api-08-mold-costing |
| `ICoreFeatureData.ReverseDirection` | 0 | — | ✅ | — | api-08-mold-costing |
| `ICoreFeatureData.SetExtractionDirection` | 2 | ✅ | — | — | api-08-mold-costing |
| `ICoreFeatureData.TargetBody` | 0 | ✅ | — | — | api-08-mold-costing |
| `ICoreFeatureData.UseDraft` | 0 | — | ✅ | — | api-08-mold-costing |
| `IFeatureManager.InsertMoldCoreCavitySolids` | 4 | ✅ | — | — | api-08-mold-costing |
| `IFeatureManager.InsertMoldPartingLine` | 1 | ✅ | — | — | api-08-mold-costing |
| `IFeatureManager.InsertMoldPartingSurface` | 8 | ✅ | — | — | api-08-mold-costing |
| `IFeatureManager.InsertMoldShutOffSurface` | 0 | — | — | — | api-08-mold-costing |
| `IFeatureManager.MoldUndercutDetect` | 6 | — | — | ⚠ 是 → `MoldUndercutDetect2` | api-08-mold-costing |
| `IFeatureManager.MoldUndercutDetect2` | 9 | — | — | — | api-08-mold-costing |
| `IMassProperty2.AccuracyLevel` | 0 | — | — | — | api-08-mold-costing |
| `IMassProperty2.CenterOfMass` | 0 | ✅ | — | — | api-08-mold-costing |
| `IMassProperty2.Density` | 0 | ✅ | — | — | api-08-mold-costing |
| `IMassProperty2.GetMomentOfInertia` | 1 | ✅ | — | — | api-08-mold-costing |
| `IMassProperty2.GetOverrideOptions` | 0 | — | — | — | api-08-mold-costing |
| `IMassProperty2.IncludeHiddenBodiesOrComponents` | 0 | ✅ | — | — | api-08-mold-costing |
| `IMassProperty2.Mass` | 0 | ✅ | — | — | api-08-mold-costing |
| `IMassProperty2.PrincipalAxesOfInertia` | 1 | — | — | — | api-08-mold-costing |
| `IMassProperty2.PrincipalMomentsOfInertia` | 0 | ✅ | — | — | api-08-mold-costing |
| `IMassProperty2.Recalculate` | 0 | ✅ | — | — | api-08-mold-costing |
| `IMassProperty2.SelectedItems` | 0 | ✅ | — | — | api-08-mold-costing |
| `IMassProperty2.SetCoordinateSystem` | 1 | — | — | — | api-08-mold-costing |
| `IMassProperty2.SetOverrideOptions` | 3 | — | — | — | api-08-mold-costing |
| `IMassProperty2.ShowWeldBeadMass` | 0 | ✅ | — | — | api-08-mold-costing |
| `IMassProperty2.SurfaceArea` | 0 | ✅ | — | — | api-08-mold-costing |
| `IMassProperty2.UseSystemUnits` | 0 | ✅ | — | — | api-08-mold-costing |
| `IMassProperty2.Volume` | 0 | ✅ | — | — | api-08-mold-costing |
| `IMassProperty2.WeldBeadMass` | 0 | ✅ | — | — | api-08-mold-costing |
| `IMassPropertyOverrideOptions.GetOverrideCenterOfMassValue` | 1 | — | — | — | api-08-mold-costing |
| `IMassPropertyOverrideOptions.GetOverrideMassValue` | 0 | — | — | — | api-08-mold-costing |
| `IMassPropertyOverrideOptions.GetOverrideMomentsOfInertiaValue` | 2 | — | — | — | api-08-mold-costing |
| `IMassPropertyOverrideOptions.GetOverridePrincipalAxesOrientation` | 1 | — | — | — | api-08-mold-costing |
| `IMassPropertyOverrideOptions.GetOverridePrincipalMomentsOfInertia` | 0 | — | — | — | api-08-mold-costing |
| `IMassPropertyOverrideOptions.OverrideCenterOfMass` | 0 | ✅ | — | — | api-08-mold-costing |
| `IMassPropertyOverrideOptions.OverrideMass` | 0 | ✅ | — | — | api-08-mold-costing |
| `IMassPropertyOverrideOptions.OverrideMomentsOfInertia` | 0 | ✅ | — | — | api-08-mold-costing |
| `IMassPropertyOverrideOptions.SetOverrideCenterOfMassValue` | 2 | ✅ | — | — | api-08-mold-costing |
| `IMassPropertyOverrideOptions.SetOverrideMassValue` | 1 | ✅ | — | — | api-08-mold-costing |
| `IMassPropertyOverrideOptions.SetOverrideMomentsOfInertiaValue` | 3 | ✅ | — | — | api-08-mold-costing |
| `IMassPropertyOverrideOptions.SetOverridePrincipalAxesOrientation` | 3 | ✅ | — | — | api-08-mold-costing |
| `IMassPropertyOverrideOptions.SetOverridePrincipalMomentsOfInertia` | 1 | ✅ | — | — | api-08-mold-costing |
| `IMeasure.Angle` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.AngleDecimalPlaces` | 0 | — | — | — | api-08-mold-costing |
| `IMeasure.ArcLength` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.ArcOption` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.Area` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.Calculate` | 1 | ✅ | ✅ | — | api-08-mold-costing |
| `IMeasure.CenterDistance` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.ChordLength` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.DeltaX` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.DeltaY` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.DeltaZ` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.Diameter` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.Distance` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.IsConcentricSpheres` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.IsIntersect` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.IsParallel` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.IsPerpendicular` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.Length` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.LengthDecimalPlaces` | 0 | — | — | — | api-08-mold-costing |
| `IMeasure.Normal` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.NormalDistance` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.Perimeter` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.Projection` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.ProjectionOption` | 0 | — | — | — | api-08-mold-costing |
| `IMeasure.Radius` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.SetProjectionEntity` | 1 | ✅ | — | — | api-08-mold-costing |
| `IMeasure.SpericalCenterDistance` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.TotalArea` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.TotalLength` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.X` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.Y` | 0 | — | ✅ | — | api-08-mold-costing |
| `IMeasure.Z` | 0 | — | ✅ | — | api-08-mold-costing |
| `IModelDoc2.MoldDraftAnalysis` | 4 | — | — | — | api-08-mold-costing |
| `IModelDocExtension.CreateMeasure` | 0 | — | ✅ | — | api-08-mold-costing |
| `IModelDocExtension.GetCostingManager` | 0 | ✅ | ✅ | — | api-08-mold-costing |
| `IPartingLineFeatureData.AccessSelections` | 2 | ✅ | ✅ | — | api-08-mold-costing |
| `IPartingLineFeatureData.Angle` | 0 | — | ✅ | — | api-08-mold-costing |
| `IPartingLineFeatureData.CoreCavitySplit` | 0 | — | ✅ | — | api-08-mold-costing |
| `IPartingLineFeatureData.DraftAnalysis` | 1 | ✅ | — | — | api-08-mold-costing |
| `IPartingLineFeatureData.GetEntitiesToSplit` | 1 | ✅ | — | — | api-08-mold-costing |
| `IPartingLineFeatureData.GetEntitiesToSplitCount` | 0 | ✅ | ✅ | — | api-08-mold-costing |
| `IPartingLineFeatureData.GetFacesByType` | 1 | ✅ | — | — | api-08-mold-costing |
| `IPartingLineFeatureData.GetFacesByTypeCount` | 1 | ✅ | — | — | api-08-mold-costing |
| `IPartingLineFeatureData.GetPartingLinesCount` | 0 | ✅ | — | — | api-08-mold-costing |
| `IPartingLineFeatureData.IGetEntitiesToSplit` | 2 | ✅ | — | — | api-08-mold-costing |
| `IPartingLineFeatureData.IGetFacesByType` | 2 | ✅ | — | — | api-08-mold-costing |
| `IPartingLineFeatureData.IGetPartingLines` | 1 | ✅ | — | — | api-08-mold-costing |
| `IPartingLineFeatureData.ISetEntitiesToSplit` | 2 | ✅ | — | — | api-08-mold-costing |
| `IPartingLineFeatureData.ISetPartingLines` | 2 | ✅ | — | — | api-08-mold-costing |
| `IPartingLineFeatureData.PartingLines` | 0 | ✅ | — | — | api-08-mold-costing |
| `IPartingLineFeatureData.PullDirection` | 0 | — | ✅ | — | api-08-mold-costing |
| `IPartingLineFeatureData.PullDirectionBase` | 0 | — | — | — | api-08-mold-costing |
| `IPartingLineFeatureData.PullDirectionType` | 0 | — | ✅ | — | api-08-mold-costing |
| `IPartingLineFeatureData.ReleaseSelectionAccess` | 0 | ✅ | — | — | api-08-mold-costing |
| `IPartingLineFeatureData.SetEntitiesToSplit` | 1 | ✅ | — | — | api-08-mold-costing |
| `IPartingLineFeatureData.SplitFaces` | 0 | — | ✅ | — | api-08-mold-costing |
| `IPartingLineFeatureData.SplitFacesOption` | 0 | — | ✅ | — | api-08-mold-costing |
| `IPartingLineFeatureData.Status` | 0 | ✅ | ✅ | — | api-08-mold-costing |
| `IPartingSurfaceFeatureData.AccessSelections` | 2 | ✅ | ✅ | — | api-08-mold-costing |
| `IPartingSurfaceFeatureData.GetPartingLinesCount` | 0 | ✅ | ✅ | — | api-08-mold-costing |
| `IPartingSurfaceFeatureData.GetPartingLinesType` | 0 | — | ✅ | — | api-08-mold-costing |
| `IPartingSurfaceFeatureData.IGetPartingLines` | 1 | ✅ | — | — | api-08-mold-costing |
| `IPartingSurfaceFeatureData.ISetPartingLines` | 2 | ✅ | — | — | api-08-mold-costing |
| `IPartingSurfaceFeatureData.Knit` | 0 | — | ✅ | — | api-08-mold-costing |
| `IPartingSurfaceFeatureData.OffsetAngle` | 0 | ✅ | ✅ | — | api-08-mold-costing |
| `IPartingSurfaceFeatureData.OffsetDistance` | 0 | — | ✅ | — | api-08-mold-costing |
| `IPartingSurfaceFeatureData.PartingLines` | 0 | ✅ | — | — | api-08-mold-costing |
| `IPartingSurfaceFeatureData.PartingType` | 0 | ✅ | ✅ | — | api-08-mold-costing |
| `IPartingSurfaceFeatureData.PullDirectionBase` | 0 | ✅ | — | — | api-08-mold-costing |
| `IPartingSurfaceFeatureData.PullDirectionType` | 0 | — | — | — | api-08-mold-costing |
| `IPartingSurfaceFeatureData.ReleaseSelectionAccess` | 0 | ✅ | — | — | api-08-mold-costing |
| `IPartingSurfaceFeatureData.ReverseAlignment` | 0 | — | ✅ | — | api-08-mold-costing |
| `IPartingSurfaceFeatureData.ReverseOffsetDirection` | 0 | — | — | — | api-08-mold-costing |
| `IPartingSurfaceFeatureData.TransitionDistance` | 0 | ✅ | — | — | api-08-mold-costing |
| `IPartingSurfaceFeatureData.TransitionType` | 0 | — | ✅ | — | api-08-mold-costing |
| `IShutOffSurfaceFeatureData.AccessSelections` | 2 | ✅ | — | — | api-08-mold-costing |
| `IShutOffSurfaceFeatureData.Edges` | 0 | ✅ | — | — | api-08-mold-costing |
| `IShutOffSurfaceFeatureData.FlipFaceTangentTo` | 1 | ✅ | — | — | api-08-mold-costing |
| `IShutOffSurfaceFeatureData.GetEdgeCount` | 0 | ✅ | — | — | api-08-mold-costing |
| `IShutOffSurfaceFeatureData.GetFaceTangentTo` | 1 | ✅ | — | — | api-08-mold-costing |
| `IShutOffSurfaceFeatureData.GetLoopCount` | 0 | ✅ | — | — | api-08-mold-costing |
| `IShutOffSurfaceFeatureData.GetLoopEdgeCount` | 1 | ✅ | — | — | api-08-mold-costing |
| `IShutOffSurfaceFeatureData.IGetEdges` | 1 | ✅ | — | — | api-08-mold-costing |
| `IShutOffSurfaceFeatureData.IGetLoopEdges` | 2 | ✅ | — | — | api-08-mold-costing |
| `IShutOffSurfaceFeatureData.ISetEdges` | 2 | ✅ | — | — | api-08-mold-costing |
| `IShutOffSurfaceFeatureData.Knit` | 0 | — | — | — | api-08-mold-costing |
| `IShutOffSurfaceFeatureData.LoopEdges` | ? | — | — | — | api-08-mold-costing |
| `IShutOffSurfaceFeatureData.LoopPatchType` | ? | — | — | — | api-08-mold-costing |
| `IShutOffSurfaceFeatureData.ReleaseSelectionAccess` | 0 | ✅ | — | — | api-08-mold-costing |
| `IShutOffSurfaceFeatureData.SetAllPatchTypes` | 1 | — | — | — | api-08-mold-costing |
| `IShutOffSurfaceFeatureData.Status` | 0 | — | — | — | api-08-mold-costing |
| `IToolingSplitFeatureData.AccessSelections` | 2 | ✅ | — | — | api-08-mold-costing |
| `IToolingSplitFeatureData.Angle` | 0 | ✅ | — | — | api-08-mold-costing |
| `IToolingSplitFeatureData.CavitySurfaces` | 0 | ✅ | — | — | api-08-mold-costing |
| `IToolingSplitFeatureData.CoreSurfaces` | 0 | ✅ | — | — | api-08-mold-costing |
| `IToolingSplitFeatureData.Depth` | ? | — | — | — | api-08-mold-costing |
| `IToolingSplitFeatureData.GetCavitySurfacesCount` | 0 | ✅ | — | — | api-08-mold-costing |
| `IToolingSplitFeatureData.GetCoreSurfacesCount` | 0 | ✅ | — | — | api-08-mold-costing |
| `IToolingSplitFeatureData.GetPartingSurfacesCount` | 0 | ✅ | — | — | api-08-mold-costing |
| `IToolingSplitFeatureData.IGetCavitySurfaces` | 1 | ✅ | — | — | api-08-mold-costing |
| `IToolingSplitFeatureData.IGetCoreSurfaces` | 1 | ✅ | — | — | api-08-mold-costing |
| `IToolingSplitFeatureData.IGetPartingSurfaces` | 1 | ✅ | — | — | api-08-mold-costing |
| `IToolingSplitFeatureData.InterlockSurface` | 0 | ✅ | — | — | api-08-mold-costing |
| `IToolingSplitFeatureData.ISetCavitySurfaces` | 2 | ✅ | — | — | api-08-mold-costing |
| `IToolingSplitFeatureData.ISetCoreSurfaces` | 2 | ✅ | — | — | api-08-mold-costing |
| `IToolingSplitFeatureData.ISetPartingSurfaces` | 2 | ✅ | — | — | api-08-mold-costing |
| `IToolingSplitFeatureData.PartingSurfaces` | 0 | ✅ | — | — | api-08-mold-costing |
| `IToolingSplitFeatureData.ReleaseSelectionAccess` | 0 | ✅ | — | — | api-08-mold-costing |

### 源：`api-09-simulation.md`（33 条）

| 接口.成员 | 参数 | 前置 | 例子 | Obsolete → 后继 | 源 |
|---|---|---|---|---|---|
| `ICWLoadsAndRestraintsManager.AddBearingLoad` | 4 | ✅ | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddBoltConnector` | 4 | — | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddCentrifugalForce` | 2 | ✅ | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddConvection` | 2 | — | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddCyclicSymmetryRestraint` | 4 | ✅ | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddDistributedMass` | 4 | — | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddEdgeWeldConnector` | 5 | — | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddElasticConnector` | 2 | — | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddForce` | 4 | ✅ | — | ⚠ 是 → `AddForce2` | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddForce2` | 5 | ✅ | — | ⚠ 是 → `AddForce3` | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddForce3` | 21 | ✅ | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddGravity` | 2 | ✅ | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddHeatFlux` | 2 | — | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddHeatPower` | 2 | ✅ | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddInitialConditionForDynamicStudy` | 12 | — | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddLinkConnector` | 3 | — | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddPinConnector` | 3 | — | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddPrescribedDisplacement` | 5 | ✅ | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddPressure` | 4 | ✅ | ✅ | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddRadiation` | 3 | — | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddRemoteLoad` | 7 | — | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddRestraint` | 4 | — | ✅ | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddRigidConnector` | 3 | — | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddSelectedBaseExcitation` | 10 | ✅ | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddSpotWeldConnector` | 4 | — | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddSpringConnector` | 4 | — | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddTemperature` | 2 | ✅ | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.AddUniformBaseExcitation` | 10 | ✅ | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.CopyLoadsAndRestraintsToStudy` | 2 | ✅ | ✅ | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.Count` | 0 | ✅ | ✅ | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.DeleteLoadsAndRestraints` | 1 | — | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.GetEdgeWeldConnector` | 2 | ✅ | — | — | api-09-simulation |
| `ICWLoadsAndRestraintsManager.GetLoadsAndRestraints` | 2 | ✅ | ✅ | — | api-09-simulation |

### 源：`api-10-routing-pdm-anim.md`（55 条）

| 接口.成员 | 参数 | 前置 | 例子 | Obsolete → 后继 | 源 |
|---|---|---|---|---|---|
| `IApplication.PDMDocManager` | 0 | ✅ | ✅ | — | api-10-routing-pdm-anim |
| `IAssemblyDoc.GetRouteManager` | 0 | — | ✅ | — | api-10-routing-pdm-anim |
| `IAssemblyDoc.IsRouteAssembly` | 0 | — | — | — | api-10-routing-pdm-anim |
| `IAVIParameter.BlurLength` | 0 | — | ✅ | — | api-10-routing-pdm-anim |
| `IAVIParameter.BlurOffset` | 0 | — | ✅ | — | api-10-routing-pdm-anim |
| `IAVIParameter.FramePerSecond` | 0 | — | ✅ | — | api-10-routing-pdm-anim |
| `IAVIParameter.ImageSize` | 0 | — | — | — | api-10-routing-pdm-anim |
| `IAVIParameter.MotionBlur` | 0 | ✅ | ✅ | — | api-10-routing-pdm-anim |
| `IAVIParameter.OutputType` | 0 | — | ✅ | — | api-10-routing-pdm-anim |
| `IAVIParameter.RendererType` | 0 | ✅ | ✅ | — | api-10-routing-pdm-anim |
| `IAVIParameter.SaveEntireAnimation` | 0 | ✅ | ✅ | — | api-10-routing-pdm-anim |
| `IBomFeature.RoutingComponentGrouping` | 0 | — | ✅ | — | api-10-routing-pdm-anim |
| `IConnectionPointFeatureData.AccessSelections` | 2 | ✅ | — | — | api-10-routing-pdm-anim |
| `IConnectionPointFeatureData.Direction` | 0 | — | ✅ | — | api-10-routing-pdm-anim |
| `IConnectionPointFeatureData.ElectricalPinID` | 0 | — | ✅ | — | api-10-routing-pdm-anim |
| `IConnectionPointFeatureData.IAccessSelections` | 2 | ✅ | — | — | api-10-routing-pdm-anim |
| `IConnectionPointFeatureData.Location` | 0 | — | ✅ | — | api-10-routing-pdm-anim |
| `IConnectionPointFeatureData.Name2` | 0 | — | ✅ | — | api-10-routing-pdm-anim |
| `IConnectionPointFeatureData.PortID` | 0 | — | ✅ | — | api-10-routing-pdm-anim |
| `IConnectionPointFeatureData.ReleaseSelectionAccess` | 0 | ✅ | — | — | api-10-routing-pdm-anim |
| `IConnectionPointFeatureData.RouteDiameter` | 0 | — | ✅ | — | api-10-routing-pdm-anim |
| `IConnectionPointFeatureData.RouteSubType` | 0 | — | ✅ | — | api-10-routing-pdm-anim |
| `IConnectionPointFeatureData.RouteType` | 0 | — | ✅ | — | api-10-routing-pdm-anim |
| `IConnectionPointFeatureData.StubLength` | 0 | — | ✅ | — | api-10-routing-pdm-anim |
| `IFeatureManager.InsertConnectionPoint` | 14 | ✅ | — | — | api-10-routing-pdm-anim |
| `IModelDoc2.EditRoute` | 0 | — | — | — | api-10-routing-pdm-anim |
| `IModelDoc2.InsertRoutePoint` | 0 | ✅ | — | — | api-10-routing-pdm-anim |
| `IModelDocExtension.GetMotionStudyManager` | 0 | — | ✅ | — | api-10-routing-pdm-anim |
| `IModelDocExtension.GetRoutingComponentManager` | 0 | — | — | — | api-10-routing-pdm-anim |
| `IModelDocExtension.SaveAs3` | 7 | ✅ | — | — | api-10-routing-pdm-anim |
| `IMotionStudy.CreateByRotateModel` | 6 | ✅ | ✅ | — | api-10-routing-pdm-anim |
| `IMotionStudy.Play` | 0 | — | ✅ | — | api-10-routing-pdm-anim |
| `IMotionStudy.SaveToAVI` | 2 | — | ✅ | — | api-10-routing-pdm-anim |
| `IMotionStudyManager.CreateAVIParameter` | 0 | — | ✅ | — | api-10-routing-pdm-anim |
| `IPDMDocManager.SetCancelOperation` | 1 | ✅ | — | — | api-10-routing-pdm-anim |
| `IPDMDocManager.SetDocumentStatus` | 1 | ✅ | ✅ | — | api-10-routing-pdm-anim |
| `IPDMDocManager.SetManagedDocument` | 1 | ✅ | ✅ | — | api-10-routing-pdm-anim |
| `IPrimaryMemberPathSegmentFeatureData.GetPathSegments` | 0 | — | — | — | api-10-routing-pdm-anim |
| `IPrimaryMemberPathSegmentFeatureData.GetPathSegmentsTypes` | 0 | — | — | — | api-10-routing-pdm-anim |
| `IPrimaryMemberPathSegmentFeatureData.MergeTangentMembers` | 0 | ✅ | — | — | api-10-routing-pdm-anim |
| `IPrimaryMemberPathSegmentFeatureData.SetPathSegments` | 1 | ✅ | — | — | api-10-routing-pdm-anim |
| `IRoutingSettings.GetFromToListHeaderDefinitions` | 12 | — | — | — | api-10-routing-pdm-anim |
| `IRoutingSettings.GetRoutingUserPreferenceDoubleValue` | 1 | — | ✅ | — | api-10-routing-pdm-anim |
| `IRoutingSettings.GetRoutingUserPreferenceIntegerValue` | 1 | — | ✅ | — | api-10-routing-pdm-anim |
| `IRoutingSettings.GetRoutingUserPreferenceStringValue` | 2 | — | ✅ | — | api-10-routing-pdm-anim |
| `IRoutingSettings.GetRoutingUserPreferenceToggle` | 1 | — | ✅ | — | api-10-routing-pdm-anim |
| `IRoutingSettings.LoadDefaultRoutingSettings` | 0 | — | — | — | api-10-routing-pdm-anim |
| `IRoutingSettings.LoadRoutingSettingsFromFile` | 1 | — | — | — | api-10-routing-pdm-anim |
| `IRoutingSettings.SaveRoutingSettingsToFile` | 1 | — | ✅ | — | api-10-routing-pdm-anim |
| `IRoutingSettings.SetFromToListHeaderDefinitions` | 12 | — | — | — | api-10-routing-pdm-anim |
| `IRoutingSettings.SetRoutingUserPreferenceDoubleValue` | 2 | — | — | — | api-10-routing-pdm-anim |
| `IRoutingSettings.SetRoutingUserPreferenceIntegerValue` | 2 | — | — | — | api-10-routing-pdm-anim |
| `IRoutingSettings.SetRoutingUserPreferenceStringValue` | 2 | — | — | — | api-10-routing-pdm-anim |
| `IRoutingSettings.SetRoutingUserPreferenceToggle` | 2 | — | — | — | api-10-routing-pdm-anim |
| `ISldWorks.GetRoutingSettings` | 0 | — | ✅ | — | api-10-routing-pdm-anim |

---

## 二 · 单列三段（本索引最有用的部分）

### 2.1 「前置在 Remarks 里明写的」—— 照着做就不会错的那批

★ 共 **377** 条（占 54.6%）。**这几条的前置是官方逐字写的，可直接照做。**

| 接口.成员 | 源 | 前置（Remarks 明写） |
|---|---|---|
| `IApplication.PDMDocManager` | `api-10-routing-pdm-anim` | Remarks 逐字：只有装了 SOLIDWORKS Toolbox 才可用；[D] 给的顺序是先 ISldWorks::GetAddInObject 取 Toolbox Browser 的 TypeLib GUID {ED783340-D5DB-11d4-BD5A-00C04F019809}，再 cast 成 swbrowser.IApplication。 |
| `IAssemblyDoc.AddConcentricMateWithTolerance` | `api-04-assembly` | 逐字：调用前必须先选中两个待配合实体，且父级标准同心配合必须已存在（否则会先自动建一个标准同心配合）。 |
| `IAssemblyDoc.AddDistanceMate` | `api-04-assembly` | 五步序：SelectByRay + GetSelectedObject6 取实体（圆柱距离配合须两圆柱面或一圆柱面加一轴）→ ClearSelection2 → Select4 → 调本方法 → EditRebuild3。 |
| `IAssemblyDoc.AddMate3` | `api-04-assembly` | 同一 mark 表（8/16/1）：ClearSelection2 → SelectByID2 选实体 → 调本方法 → ClearSelection2；无预选则 ErrorStatus 报 IncorrectSelections。 |
| `IAssemblyDoc.AddMate4` | `api-04-assembly` | mark 表 8/16/1；前后各一次 ClearSelection2；无预选则 ErrorStatus=swAddMateError_IncorrectSelections。 |
| `IAssemblyDoc.AddMate5` | `api-04-assembly` | 先 ClearSelection2 选实体；mark 逐字：cam-follower→8、width→16、其他→1；调本方法后再 ClearSelection2；无预选时 ErrorStatus=IncorrectSelections。 |
| `IAssemblyDoc.AutoExplode` | `api-04-assembly` | 无显式前置；官方写明每个装配配置只能建一个爆炸视图，要多个须用 IAssemblyDoc::CreateExplodedView。 |
| `IAssemblyDoc.AutoMateRepair` | `api-04-assembly` | 两条硬前置：修复所需实体必须在装配中；必须选中 FeatureManager 设计树里的 Mates 文件夹。 |
| `IAssemblyDoc.CollectAllSupportiveMates` | `api-04-assembly` | 逐字：仅当 IsSupportedMatesAvailable 返回 true 时本方法才有效。 |
| `IAssemblyDoc.CreateExplodedView` | `api-04-assembly` | 零参数、无选区要求；须处在活动的装配配置上，官方注明完美爆炸视图常需用户交互。 |
| `IAssemblyDoc.CreateMate` | `api-04-assembly` | 五步序：CreateMateData 取 MateFeatureData → 设通用属性 → 转型为 mate-specific 对象 → 按该接口 Remarks 设属性并/或预选实体（只对带星号的 13 个接口）→ 调本方法传入该对象。 |
| `IAssemblyDoc.CreateMateData` | `api-04-assembly` | Type 必须是逐字列出的 18 个 swMateType_e 子集之一；另 7 个（COORDINATE/LOCKTOSKETCH/MAGNETIC/MAXMATES/PATH/SLIDER/UNKNOWN）本方法排除。 |
| `IAssemblyDoc.EditConcentricMate` | `api-04-assembly` | 调用前选两项：① 定义偏心同心配合的两个实体；② 偏心同心配合本身；调完后必须调 EditRebuild3。 |
| `IAssemblyDoc.EditDistanceMate` | `api-04-assembly` | 选区逐字：距离配合实体用 IEntity::Select4 且 Data=Nothing，配合特征用 IFeature::Select2 且 Mark=0；调完调 EditRebuild3。 |
| `IAssemblyDoc.EditMate2` | `api-04-assembly` | 与 EditMate3 同源：先两个待配合项（mark=1），配合特征必须最后选；不支持改 Inplace 配合。 |
| `IAssemblyDoc.EditMate3` | `api-04-assembly` | 选区顺序逐字：先两个待配合项（mark=1），配合特征必须最后选；不支持改 Inplace 配合。 |
| `IAssemblyDoc.EditMate4` | `api-04-assembly` | 修缺同一配合实体的所有配合时，选区顺序逐字为：先选要修的配合特征，再选两个待配合模型项（mark=1）；官方另注不支持改 Inplace 配合。 |
| `IAssemblyDoc.GetUnloadedComponentNames` | `api-04-assembly` | 典型场景是装配以 Quick View/Selective open 或 Do not load hidden components 方式打开；4 个 out 数组依次是路径名/引用配置名/卸载原因/文档类型。 |
| `IAssemblyDoc.InsertCavity4` | `api-08-mold-costing` | 必须在装配体文档的编辑上下文里执行，缩放因子按百分比传，范围 -20 ~ +20。 |
| `IAssemblyDoc.InsertDerivedPattern` | `api-04-assembly` | 逐字顺序与 mark：SelectByID2 先选种子组件 mark=1，再选阵列特征 mark=6，然后调本方法。 |
| `IAssemblyDoc.IsSupportedMatesAvailable` | `api-04-assembly` | 为 true 时才能用 CollectAllSupportiveMates 收集支撑配合；Mate Controller 不支持带 free 或 center-in-slot 约束的 path/width/slot 配合。 |
| `IAssemblyDoc.IToolsCheckInterference3` | `api-04-assembly` | 与 ToolsCheckInterference2 同口径（空面数组/组件数组）；ref 形参类型是 Component2 而非 Component。 |
| `IAssemblyDoc.LightweightAllResolved` | `api-04-assembly` | 没有选中组件时作用于整份装配文档；被抑制的组件被忽略。 |
| `IAssemblyDoc.MakeLightWeight` | `api-04-assembly` | 零参数、作用于当前选中的组件；官方声明目的只是支持录制宏，推荐改用 GetSuppression / SetSuppression2。 |
| `IAssemblyDoc.ResolveAllLightweight` | `api-04-assembly` | 未选组件时作用于整份装配文档；被抑制的组件被忽略。 |
| `IAssemblyDoc.ResolveAllLightWeightComponents` | `api-04-assembly` | 装配必须在自己的窗口里打开（ISldWorks::ActivateDoc2 或 IModelDoc2::Visible）；仅作参考打开时返回 swResolveNotPerformed。 |
| `IAssemblyDoc.ResolveOutOfDateLightWeightComponents` | `api-04-assembly` | 逐字：You must select a lightweight component before using this method；选区无效则返回 false。 |
| `IAssemblyDoc.ToolsCheckInterference` | `api-04-assembly` | 零参数；唯一作用是打开干涉检测 PropertyManager 对话框。 |
| `IAssemblyDoc.ToolsCheckInterference2` | `api-04-assembly` | 例子前置逐字「Select at least two interfering components」；组件数组由 GetSelectedObjectCount + GetSelectedObjectsComponent2(i+1) 组装。 |
| `IAssemblyDoc.ViewCollapseAssembly` | `api-04-assembly` | 零参数；须与 ViewExplodeAssembly 配对使用。 |
| `IAssemblyDoc.ViewExplodeAssembly` | `api-04-assembly` | 零参数；官方要求与 ViewCollapseAssembly 成对使用，以 toggle 爆炸装配视图的显示。 |
| `IAVIParameter.MotionBlur` | `api-10-routing-pdm-anim` | Remarks 逐字：必须有一个 ray-trace 渲染引擎处于 active，才能在保存动画时启用运动模糊（例子 Preconditions 第 2 条同义）。 |
| `IAVIParameter.RendererType` | `api-10-routing-pdm-anim` | Remarks 逐字：渲染器设为 Custom 时才能改画面高/宽、保留宽高比并把宽高比设为屏幕比或指定值（但枚举表里没有 Custom 这个成员，数值查不到）。 |
| `IAVIParameter.SaveEntireAnimation` | `api-10-routing-pdm-anim` | Remarks 逐字：设成 false 时必须同时指定要保存的时间段的 start time 与 end time。 |
| `ICavityFeatureData.AccessSelections` | `api-08-mold-costing` | 把模型置入回滚态后访问选择；改完用 ModifyDefinition 收尾，没改则用 ReleaseSelectionAccess。 |
| `ICavityFeatureData.Components` | `api-08-mold-costing` | 官方只指向 Accessing Selections that Define Features（回滚态内读写），未写其它前置。 |
| `ICavityFeatureData.GetComponentsCount` | `api-08-mold-costing` | 必须先于 IGetComponents 调用。 |
| `ICavityFeatureData.IGetComponents` | `api-08-mold-costing` | 必须先调 GetComponentsCount() 取 Count。 |
| `ICavityFeatureData.ISetComponents` | `api-08-mold-costing` | 官方只指向 Accessing Selections that Define Features（回滚态内），未写别的。 |
| `ICavityFeatureData.ReleaseSelectionAccess` | `api-08-mold-costing` | 没改特征才用它恢复回滚态；改过特征必须走 ModifyDefinition 或 IModifyDefinition2。 |
| `ICavityFeatureData.UniformScale` | `api-08-mold-costing` | 必须先用 UseUniformScale 置 true 开启各向同性缩放，UniformScale 才生效。 |
| `ICavityFeatureData.UseUniformScale` | `api-08-mold-costing` | 用它开启各向同性缩放，之后才用 UniformScale 写缩放值。 |
| `IComponent2.GetChildren` | `api-04-assembly` | 官方逐字：必须递归调用，因为只返回直接（一层）子件；返回顺序不保证稳定。 |
| `IComponent2.GetHiddenUnloadedChildrenCount` | `api-04-assembly` | 只统计隐藏未加载子件，不含抑制未加载子件（后者走 GetUnloadedComponentNames）。 |
| `IComponent2.GetMates` | `api-04-assembly` | 无显式前置；官方称它可避免遍历配合列表（列表长时性能受影响）。 |
| `IComponent2.GetSuppression` | `api-04-assembly` | 用于判定 suppressed / lightweight / fully resolved；官方强调轻化件与抑制件只含一小部分数据。 |
| `IComponent2.GetSuppression2` | `api-04-assembly` | 零参数；官方用它区分 suppressed / lightweight / fully resolved，并强调轻化件与抑制件只含一小部分数据。 |
| `IComponent2.GetUnloadedComponentNames` | `api-04-assembly` | 装配以 Quick View/Selective open 打开时有用；签名与 IAssemblyDoc 同名成员逐字一致。 |
| `IComponent2.IGetChildrenCount` | `api-04-assembly` | 只返回单层计数；GetChildren / IGetChildren 不递归子装配。 |
| `IComponent2.IsEnvelope` | `api-04-assembly` | 无调用前置；Remarks 逐字只写版本信息（FCS Rev 10.0）。 |
| `IComponent2.IsHidden` | `api-04-assembly` | 对轻化件逐字注明：ConsiderSuppressed 为 True 时 IsHidden 返回 True；另附 ConsiderSuppressed/Component 真值表。 |
| `IComponent2.IsPatternInstance` | `api-04-assembly` | 无前置；官方逐字：组件是阵列实例成员则 True。 |
| `IComponent2.IsSuppressed` | `api-04-assembly` | 官方提示抑制状态随活动配置变化，推荐改用 GetSuppression 取具体状态值。 |
| `IComponent2.IsVirtual` | `api-04-assembly` | 装配内上下文创建虚拟件时不会自动建 In-Place 配合，位置与约束需自行给定。 |
| `IComponent2.SetSuppression2` | `api-04-assembly` | 逐字：SOLIDWORKS 不允许在 PropertyManager 页打开时抑制组件。 |
| `IComponent2.Transform2` | `api-04-assembly` | 变换必须相对根组件指定（in-context 编辑时也一样）；官方注明本属性可破坏既有配合关系。 |
| `IComponent2.Visible` | `api-04-assembly` | 无调用前置；官方指出该功能也可用 IModelDoc2::HideComponent2 / ShowComponent2 实现。 |
| `IConnectionPointFeatureData.AccessSelections` | `api-10-routing-pdm-anim` | Remarks 逐字：零件文档传 IModelDoc2 且 Component 为 NULL；装配体传装配的 IModelDoc2 加待改特征所在的 IComponent2；调用后模型进入回滚状态。 |
| `IConnectionPointFeatureData.IAccessSelections` | `api-10-routing-pdm-anim` | Remarks 与 AccessSelections 逐字相同：零件传 IModelDoc2 + Component=NULL，装配传 IModelDoc2 + IComponent2，调用后进入回滚状态。 |
| `IConnectionPointFeatureData.ReleaseSelectionAccess` | `api-10-routing-pdm-anim` | Remarks 逐字：它是恢复 AccessSelections / IAccessSelections 造成的回滚状态的那一个 —— 没改特征时用它收尾，改过则用 IFeature::ModifyDefinition 或 IModifyDefinition2。 |
| `ICoreFeatureData.AccessSelections` | `api-08-mold-costing` | 先在树里选中核心特征，GetDefinition() 后 AccessSelections 进回滚态；收尾 ModifyDefinition 或 ReleaseSelectionAccess。 |
| `ICoreFeatureData.BoundingSketch` | `api-08-mold-costing` | 官方只指向 Accessing Selections that Define Features（回滚态内读写），未写其它前置。 |
| `ICoreFeatureData.DraftAngle` | `api-08-mold-costing` | 要写这个属性，UseDraft 必须为 true。 |
| `ICoreFeatureData.DraftOutward` | `api-08-mold-costing` | 要写这个属性，UseDraft 必须为 true。 |
| `ICoreFeatureData.EndCondition` | `api-08-mold-costing` | 只接受 swEndCondBlind / swEndCondThroughAll / swEndCondThroughNext 三种终止条件（CHM 逐字）。 |
| `ICoreFeatureData.GetExtractionDirection` | `api-08-mold-costing` | 定义拔模方向的实体只能是 Face / Plane / Edge / Vertex / Sketch line / Sketch point 六类之一，可给两个实体。 |
| `ICoreFeatureData.ReleaseSelectionAccess` | `api-08-mold-costing` | 没改特征才用它恢复回滚态；改过特征必须走 ModifyDefinition 或 IModifyDefinition2。 |
| `ICoreFeatureData.SetExtractionDirection` | `api-08-mold-costing` | 传入的实体只能是 Face / Plane / Edge / Vertex / Sketch line / Sketch point；给两个草图点即可定方向。 |
| `ICoreFeatureData.TargetBody` | `api-08-mold-costing` | 官方只指向 Accessing Selections that Define Features（回滚态内读写），未写其它前置。 |
| `ICWLoadsAndRestraintsManager.AddBearingLoad` | `api-09-simulation` | CoordinateSystem 的 Z 轴必须与 FirstFace 数组中各圆柱面或圆形壳边的轴线重合。 |
| `ICWLoadsAndRestraintsManager.AddCentrifugalForce` | `api-09-simulation` | 必须先指定材料的密度属性，否则离心载荷不生效。 |
| `ICWLoadsAndRestraintsManager.AddCyclicSymmetryRestraint` | `api-09-simulation` | 仅对静态与非线性算例有效；FirstFace 与 SecondFace 的夹角须能被 360 整除，截面无效时不能施加。 |
| `ICWLoadsAndRestraintsManager.AddForce` | `api-09-simulation` | 不使用参考几何时 RefGeom 必须传 null。 |
| `ICWLoadsAndRestraintsManager.AddForce2` | `api-09-simulation` | 不使用参考几何时 RefGeom 必须传 null。 |
| `ICWLoadsAndRestraintsManager.AddForce3` | `api-09-simulation` | Comps 必须传非空且元素非零的数组，Ucode 指定用其中哪些分量表示某方向的力或力矩。 |
| `ICWLoadsAndRestraintsManager.AddGravity` | `api-09-simulation` | 必须先定义质量密度，否则重力不生效。 |
| `ICWLoadsAndRestraintsManager.AddHeatPower` | `api-09-simulation` | 给定的值会施加到 DispArray 里的每一个实体上。 |
| `ICWLoadsAndRestraintsManager.AddPrescribedDisplacement` | `api-09-simulation` | Displacements 是 6 元数组：参考几何与平面面给长度、圆柱面与球面给转角，后 3 个是 0/1 开关。 |
| `ICWLoadsAndRestraintsManager.AddPressure` | `api-09-simulation` | 不用参考几何时 RegGeom 传 null 或 Nothing；传 Dispatch 指针会被忽略。 |
| `ICWLoadsAndRestraintsManager.AddSelectedBaseExcitation` | `api-09-simulation` | DVal1/2/3 取负值表示反向；随机振动动态算例下它们是该 NType 的功率谱密度。 |
| `ICWLoadsAndRestraintsManager.AddTemperature` | `api-09-simulation` | 温度载荷可用于静态、非线性、频率、屈曲与热五类算例。 |
| `ICWLoadsAndRestraintsManager.AddUniformBaseExcitation` | `api-09-simulation` | DVal1/2/3 取负值表示反向；随机振动动态算例下它们是该 NType 的功率谱密度。 |
| `ICWLoadsAndRestraintsManager.CopyLoadsAndRestraintsToStudy` | `api-09-simulation` | LRNames 须先由 GetLoadsAndRestraints 逐个取 .Name 填好；重名时官方会给复制件加前缀 Copy[1]。 |
| `ICWLoadsAndRestraintsManager.Count` | `api-09-simulation` | 官方明确要求先取 Count 再调 GetLoadsAndRestraints。 |
| `ICWLoadsAndRestraintsManager.GetEdgeWeldConnector` | `api-09-simulation` | NIndex 须由 Count 得出，且与算例树里的纵向位置不对应，须用 GetLoadsAndRestraints 建立映射。 |
| `ICWLoadsAndRestraintsManager.GetLoadsAndRestraints` | `api-09-simulation` | 先调 Count 取合法 NIndex；返回的是基类 CWLoadsAndRestraints，须转成具体载荷约束子类。 |
| `IExplodeStep.AutoSpaceComponentsOnDrag` | `api-04-assembly` | 编辑已有爆炸步时若把它从 true 改成 false，官方要求必须重设 RotateAboutEachComponentOrigin 与 RotationAngle。 |
| `IExplodeStep.DivergeDirection` | `api-04-assembly` | 三条件：ExplodeStepType=swAssemblyExplodeStepType_Radial；被选实体与爆炸方向成角度；设为有效值自动把 DivergeFromAxis 置 true，Nothing/null 则置 false。 |
| `IExplodeStep.DivergeFromAxis` | `api-04-assembly` | 逐字双向依赖：置 true 前必须先给 DivergeDirection 一个有效实体；置 false 会把 DivergeDirection 清空。 |
| `IExplodeStep.GetComponent` | `api-04-assembly` | 官方逐字：Before calling this method, call GetNumOfComponents to get a valid value for Index。 |
| `IExplodeStep.GetComponentName` | `api-04-assembly` | 与 GetComponent 同一条逐字前置：调用前先调 GetNumOfComponents 取合法 Index。 |
| `IExplodeStep.GetExplodeDirection` | `api-04-assembly` | 有效性限定逐字：This method is not valid for subassembly explode steps（子装配爆炸步不可用）。 |
| `IExplodeStep.GetRotationAxis` | `api-04-assembly` | 与 GetExplodeDirection 同一条逐字前置：not valid for subassembly explode steps。 |
| `IExplodeStep.GetSpecificComponentXForm` | `api-04-assembly` | 逐字：先调 GetNumOfComponents 取合法 Index；普通步取整步变换，径向步取单个径向组件的变换。 |
| `IExplodeStep.GetSubAssemblyExplodeSteps` | `api-04-assembly` | 步的来源逐字是 PropertyManager 上的 Reuse Subassembly Explode；有效性由 ExplodeStepType==swAssemblyExplodeStepType_SubAssembly 决定。 |
| `IExplodeStep.IGetComponent` | `api-04-assembly` | 逐字同句：调用前先用 GetNumOfComponents 取合法 Index。 |
| `IExplodeStep.IsSubAssemblyRigid` | `api-04-assembly` | 官方把柔性/刚性子装配的语义外链到 SOLIDWORKS Help，本机该页未查 ⇒ 这条前置查不到。 |
| `IExplodeStep.ReverseRotationDirection` | `api-04-assembly` | 单一有效性条件：ExplodeStepType == swAssemblyExplodeStepType_Translate。 |
| `IExplodeStep.ReverseTranslationDirection` | `api-04-assembly` | 同一条件：ExplodeStepType == swAssemblyExplodeStepType_Translate。 |
| `IExplodeStep.RotateAboutEachComponentOrigin` | `api-04-assembly` | 置 true 会自动填入旋转轴；AutoSpaceComponentsOnDrag 为 true 时本属性被自动置 false。 |
| `IExplodeStep.RotationAngle` | `api-04-assembly` | AutoSpaceComponentsOnDrag 为 true 时本属性被自动置 0.0；含义随 ExplodeStepType 在绕各自原点与绕旋转轴之间切换。 |
| `IExplodeStep.SetComponents` | `api-04-assembly` | 条件式前置：仅在编辑该 regular 爆炸步、且创建时未提供旋转轴时有效，否则会改动旋转轴。 |
| `IFeatureManager.CutListFolderLocation` | `api-03-weldment` | This method only works for 三类对象：Solid Bodies / cut list items、Feature / body folders、Sub-weldment folders；其他设计树对象用 FeatureFolderLocation。 |
| `IFeatureManager.FeatureBossThicken` | `api-01-surface` | 必须先把参考曲面用 mark=1 选中（SelectByID2(…,mark=1) 或 SelectionMgr.SetSelectedObjectMark(1,1,swSelectionMarkSet)）；UseAutoSelect=false 时用户须自己选体；FillVolume=true 时其余参数被忽略且要求封闭曲面。 |
| `IFeatureManager.FeatureCutThicken` | `api-01-surface` | 只写了须先选中参考曲面、以及 UseAutoSelect=false 时用户必须自己选体；官方未写 selection mark 取值（与 FeatureBossThicken 写了 mark of 1 不同）。 |
| `IFeatureManager.FeatureLocalCurveDrivenPattern` | `api-06-features` | 按 mark 选：要阵列的组件 = 1、方向 1 的曲线/边/草图/草图实体 = 2、方向 2 同类 = 4、参考点 = 32（取 swLocalSketchPatternSelectedPoint 时必须选顶点）、3D 曲线所在面 = 64。 |
| `IFeatureManager.IInsertCombineFeature` | `api-06-features` | 同 InsertCombineFeature（MainBody = mark 1、ToolVar bodies = mark 2）；另明写 ToolsArr 在 VBA/VB.NET/C#/C++/CLI 下 Not supported，仅进程内非托管 C++ 可用。 |
| `IFeatureManager.InsertCombineFeature` | `api-06-features` | 要么直接传 MainBody + ToolVar；要么先 SelectByID2 按 MainBody = mark 1、ToolVar bodies = mark 2 选中，再把 MainBody 传 Nothing/null 且 ToolVar 传空数组。 |
| `IFeatureManager.InsertConnectionPoint` | `api-10-routing-pdm-anim` | Remarks 逐字：必须先在 Tools > Add-Ins 里加载 SOLIDWORKS Routing，且当前只支持零件文档；用 IModelDocExtension::SelectByID2 打 mark=1 选路由起点（圆边/圆面/面或基准面+草图点或顶点），mark=2 选对齐线缆宽度的参考轴或边（仅带状电缆）。 |
| `IFeatureManager.InsertCosmeticWeldBead` | `api-03-weldment` | Before calling this method, select the contact faces for the weld bead.（官方未点名 mark 数字） |
| `IFeatureManager.InsertCosmeticWeldBead2` | `api-03-weldment` | Remarks 给 mark 表：WeldGeometry 模式 from 面 mark=4 / to 面 mark=8；WeldPath 模式 weld-from 用 mark=0 且 WeldToFaceOrEdgeSet 传 Nothing/null；同侧实体类型必须一致。 |
| `IFeatureManager.InsertEndCapFeature2` | `api-03-weldment` | 官方未写「Before calling…」也未点名 mark；想在图形区预先选面时叫你改用 InsertEndCapFeature3，本方法靠末位 Faces（Array of Face2）收面。 |
| `IFeatureManager.InsertEndCapFeature3` | `api-03-weldment` | 调用前必须在图形区选中一个或多个结构构件的端面；官方未点名 mark 数字（例子传的是 0）；不想预选可改把面数组传给 InsertEndCapFeature2。 |
| `IFeatureManager.InsertFilletBeadFeature3` | `api-03-weldment` | 官方只说给两组面数组、各组面之间的交线加焊道，未点名 mark 数字；面走 FaceSet1 / FaceSet2 两个数组实参。 |
| `IFeatureManager.InsertFillSurface2` | `api-01-surface` | 用 SelectByID2 选界定待填充曲面的边：mark 1=边界曲线、257=带接触曲率控制的边界、513=带切向曲率控制的边界、4=约束曲线或内部曲线；Resolutions 可取 1/2/3。 |
| `IFeatureManager.InsertGussetFeature2` | `api-03-weldment` | 官方无 mark 要求，靠末位 Faces（构成该角板基底的面数组）收面；想「在图形区先选两个支撑腿面」就改走 InsertGussetFeature3。 |
| `IFeatureManager.InsertGussetFeature3` | `api-03-weldment` | 必须先调 SelectByID2 选两个作为支撑腿的面，Mark of 1；官方说不想预选时可改把面数组传给 InsertGussetFeature2。 |
| `IFeatureManager.InsertIndent` | `api-06-features` | 调用前必须已选中目标体（mark = 1）与工具体区域（mark = 4），用 SelectByID2 带上这两个不同的 mark。 |
| `IFeatureManager.InsertMoldCoreCavitySolids` | `api-08-mold-costing` | 分型线特征须已存在、分型面须已生成、零件须已被分成 core 与 cavity 两个 sheet body，并须有垂直于拔模方向的模具块轮廓草图。 |
| `IFeatureManager.InsertMoldPartingLine` | `api-08-mold-costing` | 调用前必须先用 IModelDocExtension::SelectByID2 选好：拔模方向实体 mark=1、分型线边 mark=4。 |
| `IFeatureManager.InsertMoldPartingSurface` | `api-08-mold-costing` | 模型里还没有分型线特征时，调用前须先用 SelectByID2 选拔模方向面 mark=1 与分型线边 mark=4。 |
| `IFeatureManager.InsertScale` | `api-06-features` | 缩放图形体时须先在 FeatureManager 树的 Graphic Bodies 文件夹里选中那个图形体再调用；缩放当前模型时官方没写任何选择前置。 |
| `IFeatureManager.InsertSewRefSurface` | `api-01-surface` | 用 SelectByID2 以 mark=1 选要缝合的曲面（可多个）；缝合容差须在 0.0001~0.1 mm 内并满足 (Min gap) <= (Knit tolerance) <= MIN(0.1 mm, Max gap)。 |
| `IFeatureManager.InsertStructuralWeldment3` | `api-03-weldment` | 官方没写图形区预选；要求先用 CreateStructuralMemberGroup、IStructuralMemberFeatureData::Groups 或 IGetGroups 把 Groups 形参填出来。 |
| `IFeatureManager.InsertStructuralWeldment4` | `api-03-weldment` | Path 必须是 install_dir\<lang>\<lang>\weldment profiles 下的 .sldlfp 轮廓；Groups 要用 CreateStructuralMemberGroup 一类填。 |
| `IFeatureManager.InsertStructuralWeldment5` | `api-03-weldment` | 官方把 Path（出厂 vs 自定义 .sldlfp）与 ConfigurationName（出厂→空串 / 自定义→配置名）配成一对硬约束；Groups 仍须用 CreateStructuralMemberGroup 填。 |
| `IFeatureManager.InsertSubWeldFolder` | `api-03-weldment` | 零件里必须先含一个焊件文件夹（Solid Bodies 或 Cut List）才能建子焊件文件夹，见 InsertWeldmentFeature。 |
| `IFeatureManager.InsertSweepSurface2` | `api-01-surface` | 用 SelectByID2 先选轮廓与扫掠曲线：mark 1=轮廓、2=引导线（可选）、4=扫掠路径；UseAutoSelect=false 时用户必须自己选体。 |
| `IFeatureManager.InsertSweepSurface3` | `api-01-surface` | 用 SelectByID2 选草图轮廓与扫掠曲线：mark 1=草图轮廓、2=引导线（可选）、4=扫掠路径；UseAutoSelect=false 时用户须自己选体；Direction 只在草图轮廓且轮廓与路径端点不重合时生效。 |
| `IFeatureManager.InsertUntrimSurface` | `api-01-surface` | 必须先预选要取消裁剪的面或边（You must preselect the face or the edges you want to untrim.）。 |
| `IFeatureManager.InsertUntrimSurface` | `api-03-weldment` | You must preselect the face or the edges you want to untrim.（官方未点名 mark 数字） |
| `IFeatureManager.InsertUntrimSurface2` | `api-01-surface` | 仅对曲面零件有效，且必须预选要取消裁剪的面或边；FaceUntrimType 仅当选了面有效，EdgeUntrimType 仅当选了边有效，BTrimOppositeSide 仅当 BMerge=false 有效。 |
| `IFeatureManager.InsertUntrimSurface2` | `api-03-weldment` | 官方写死两条：is valid only for surface parts，且 requires preselection of the face or edges you want to untrim。 |
| `IFeatureManager.InsertWeldmentTrimFeature` | `api-03-weldment` | SelectByID2 用 mark 1 = 待剪的体、mark 2 = 修剪边界（体或面）。 |
| `IFeatureManager.InsertWeldmentTrimFeature2` | `api-03-weldment` | SelectByID2 用 mark 1 = 待剪体、mark 2 = 修剪边界；GapValue 只在 Options 含 WeldGap 时才被采用，否则取设计界面上次设定值。 |
| `IFeatureManager.InsertWrapFeature` | `api-06-features` | 用 SelectByID2 按 mark 选：面 = 1、pull 方向 = 2（仅 Type 为 Emboss/Engrave 时）、2D 草图 = 4；官方明写 3D 草图无效。 |
| `IFeatureManager.InsertWrapFeature2` | `api-06-features` | 用 SelectByID2 或 SelectByRay 选：一个或多个面 mark=1、pull 方向实体 mark=2（仅 Emboss/Engrave）、不含开放轮廓的 2D 草图 mark=4，3D 草图不支持。 |
| `IFeatureManager.PostIntersect` | `api-06-features` | 调用前必须先调 IFeatureManager::PreIntersect 取得相交体数组（官方前置句点名的是 PreIntersect，不是 PreIntersect2）。 |
| `IFeatureManager.PostTrimSurface` | `api-01-surface` | 必须先调 PreTrimSurface、再选裁剪面或裁剪工具、（可选）SolidForTrim，最后才调用它。 |
| `IFeatureManager.PostTrimSurface` | `api-03-weldment` | Before calling this method 三步：先调 PreTrimSurface → 选修剪面或修剪工具 → （可选）SolidForTrim。 |
| `IFeatureManager.PreIntersect` | `api-06-features` | 调用前必须已选中构成相交特征的 surfaces/solids/planes；调用后必须接着调 IFeatureManager::PostIntersect 建出相交特征。 |
| `IFeatureManager.PreIntersect2` | `api-06-features` | 调用前必须已选中相交的 surfaces/solids/planes；调用后必须接着调 IFeatureManager::PostIntersect 建出相交特征。 |
| `IFeatureManager.PreTrimSurface` | `api-03-weldment` | 官方给的是三步序：本方法调用后 → 选修剪面或修剪工具 → （可选）SolidForTrim → PostTrimSurface。 |
| `IFeatureManager.PreTrimSurface` | `api-01-surface` | 调用它之后才去选裁剪面/裁剪工具（可选夹在中间设 SolidForTrim），最后必须调用 PostTrimSurface。 |
| `IFeatureManager.SetFreeformBoundaryContinuity` | `api-06-features` | 官方明说 Freeform 族方法只用来 journal 交互用户的动作，因需交互，完全自动化创建 Freeform 特征不可能；顺序为选面→SetFreeformCurveData→SetFreeformPointData→本方法→InsertFreeform2。 |
| `IFeatureManager.SetFreeformBoundaryContinuity` | `api-01-surface` | 它是 Freeform 宏录制序列的第 4 步（先 SetFreeformCurveData、再 SetFreeformPointData）；官方明写用 API 无法完全自动化创建 Freeform。 |
| `IFeatureManager.SolidForTrim` | `api-03-weldment` | 该属性只在创建 surface trim feature 的窗口期可用：必须在 PreTrimSurface 之后、PostTrimSurface 之前读写。 |
| `IFeatureManager.SolidForTrim` | `api-01-surface` | 只在创建曲面裁剪特征期间可用；必须在 PreTrimSurface 之后、PostTrimSurface 之前读或写。 |
| `IInterferenceDetectionMgr.CreateFastenersFolder` | `api-04-assembly` | 共性前置：该值只在 InterferenceDetectionMgr 对象在作用域内存在，不跨设计会话、不跨下次界面干涉检测。 |
| `IInterferenceDetectionMgr.ExportResults` | `api-04-assembly` | Filename 必须是 Excel 或 .csv；IncludeThumbnail 仅对 Excel 有效，缩略图为 128x128、白底、等轴测方向。 |
| `IInterferenceDetectionMgr.GetComponentsTransformInterferenceCount` | `api-04-assembly` | 逐字：必须在调用 IGetComponentsTransformInterference 之前调用，以取该方法返回数组的长度。 |
| `IInterferenceDetectionMgr.GetInterferenceComponentCount` | `api-04-assembly` | 逐字：必须在调用 IGetInterferenceComponents 之前调用（官方原文把接口名拼成 IInterferenceDectectionMgr）。 |
| `IInterferenceDetectionMgr.GetInterferenceCount` | `api-04-assembly` | 逐字：必须在调用 IGetInterferences 之前调用，以确定干涉数组的大小。 |
| `IInterferenceDetectionMgr.IgnoreHiddenBodies` | `api-04-assembly` | 共性七行：该值只在对象在作用域内存在、不跨设计会话、不跨下次界面干涉检测。 |
| `IInterferenceDetectionMgr.IncludeMultibodyPartInterferences` | `api-04-assembly` | 共性七行：该值只在对象在作用域内存在、不跨设计会话、不跨下次界面干涉检测。 |
| `IInterferenceDetectionMgr.MakeInterferingPartsTransparent` | `api-04-assembly` | 共性七行：该值只在对象在作用域内存在、不跨设计会话、不跨下次界面干涉检测。 |
| `IInterferenceDetectionMgr.SetComponentsAndTransforms` | `api-04-assembly` | 必须传绝对变换；全部传 null/Nothing 判为非法输入（部分为 null 才是恒等增量）。 |
| `IInterferenceDetectionMgr.ShowIgnoredInterferences` | `api-04-assembly` | 共性七行：该值只在对象在作用域内存在、不跨设计会话、不跨下次界面干涉检测。 |
| `IInterferenceDetectionMgr.TreatCoincidenceAsInterference` | `api-04-assembly` | 共性七行：该值只在对象在作用域内存在、不跨设计会话、不跨下次界面干涉检测。 |
| `IInterferenceDetectionMgr.TreatSubAssembliesAsComponents` | `api-04-assembly` | 共性七行：该值只在对象在作用域内存在、不跨设计会话、不跨下次界面干涉检测。 |
| `IMassProperty2.CenterOfMass` | `api-08-mold-costing` | 若 OverrideCenterOfMass=true 或复位了 IncludeHiddenBodiesOrComponents，必须先调 Recalculate() 再用本属性。 |
| `IMassProperty2.Density` | `api-08-mold-costing` | 若复位了 IncludeHiddenBodiesOrComponents 须先 Recalculate()；密度随零件不同而异时按 Density = Mass / Volume 理解。 |
| `IMassProperty2.GetMomentOfInertia` | `api-08-mold-costing` | 返回 0 基的 9 元 double 数组，顺序固定为 Lxx, Lxy, Lxz, Lyx, Lyy, Lyz, Lzx, Lzy, Lzz。 |
| `IMassProperty2.IncludeHiddenBodiesOrComponents` | `api-08-mold-costing` | 设为 true 之后必须调 Recalculate() 才能用 IMassProperty2 的各属性。 |
| `IMassProperty2.Mass` | `api-08-mold-costing` | 若 OverrideMass=true 或复位了 IncludeHiddenBodiesOrComponents，须先调 Recalculate()。 |
| `IMassProperty2.PrincipalMomentsOfInertia` | `api-08-mold-costing` | 覆盖主惯性矩或复位 IncludeHiddenBodiesOrComponents 后须先 Recalculate()；该属性默认返回 metric 单位。 |
| `IMassProperty2.Recalculate` | `api-08-mold-costing` | 覆盖质心/质量/惯性矩/主轴方向/主惯性矩之后，或复位 IncludeHiddenBodiesOrComponents 之后调用。 |
| `IMassProperty2.SelectedItems` | `api-08-mold-costing` | 已预选的实体/组件会被算进返回数组。 |
| `IMassProperty2.ShowWeldBeadMass` | `api-08-mold-costing` | 置为 true 之后才能用 WeldBeadMass。 |
| `IMassProperty2.SurfaceArea` | `api-08-mold-costing` | 若复位了 IncludeHiddenBodiesOrComponents，须先调 Recalculate()。 |
| `IMassProperty2.UseSystemUnits` | `api-08-mold-costing` | 默认 true，即用系统单位（米、弧度、千克），所有返回值的属性随之换算。 |
| `IMassProperty2.Volume` | `api-08-mold-costing` | 若复位了 IncludeHiddenBodiesOrComponents，须先调 Recalculate()。 |
| `IMassProperty2.WeldBeadMass` | `api-08-mold-costing` | 只有 ShowWeldBeadMass=true 时本属性才有效。 |
| `IMassPropertyOverrideOptions.OverrideCenterOfMass` | `api-08-mold-costing` | 置 true 之后必须调 SetOverrideCenterOfMassValue。 |
| `IMassPropertyOverrideOptions.OverrideMass` | `api-08-mold-costing` | 置 true 之后必须调 SetOverrideMassValue。 |
| `IMassPropertyOverrideOptions.OverrideMomentsOfInertia` | `api-08-mold-costing` | 置 true 之后要调三个写侧方法：SetOverrideMomentsOfInertiaValue、SetOverridePrincipalAxesOrientation、SetOverridePrincipalMomentsOfInertia。 |
| `IMassPropertyOverrideOptions.SetOverrideCenterOfMassValue` | `api-08-mold-costing` | 只有 OverrideCenterOfMass=true 时本方法才有效。 |
| `IMassPropertyOverrideOptions.SetOverrideMassValue` | `api-08-mold-costing` | 只有 OverrideMass=true 时本方法才有效。 |
| `IMassPropertyOverrideOptions.SetOverrideMomentsOfInertiaValue` | `api-08-mold-costing` | 只有 OverrideMomentsOfInertia=true 时本方法才有效。 |
| `IMassPropertyOverrideOptions.SetOverridePrincipalAxesOrientation` | `api-08-mold-costing` | 只有 OverrideMomentsOfInertia=true 时本方法才有效。 |
| `IMassPropertyOverrideOptions.SetOverridePrincipalMomentsOfInertia` | `api-08-mold-costing` | 只有 OverrideMomentsOfInertia=true 时本方法才有效。 |
| `IMate2.CanBeFlipped` | `api-04-assembly` | 逐字：要先用 IMate2::Type 判定配合类型。 |
| `IMate2.DistanceFirstArcCondition` | `api-04-assembly` | 仅对两个圆柱面之间、或一个圆柱面与一条轴之间的距离配合有效。 |
| `IMate2.DistanceSecondArcCondition` | `api-04-assembly` | 同 DistanceFirstArcCondition：仅对两圆柱面或一圆柱面加一轴的距离配合有效。 |
| `IMate2.GetCurrentMisalignedDeviation` | `api-04-assembly` | 若当前偏差大于 GetMaximumMisalignedDeviation 则配合解不出。 |
| `IMate2.GetLinkedMate` | `api-04-assembly` | 逐字定义：本配合与它的 linked mate 是 Hole Set 里的兄弟，即同一对组件之间的两个同心配合。 |
| `IMate2.GetMateEntityCount` | `api-04-assembly` | 逐字：必须在调用 MateEntity 之前调用，以取该配合的实体数量。 |
| `IMate2.GetMaximumMisalignedDeviation` | `api-04-assembly` | 偏差在 Hole Set 的两个同心配合间是累加的，与最大值比较前先求和。 |
| `IMate2.GetUseMisalignedDeviationDocumentProperty` | `api-04-assembly` | 它是 SetMaximumMisalignedDeviation 的门闸：返回 false 时最大偏差才由 GetMaximumMisalignedDeviation 给出。 |
| `IMate2.LockMagneticMate` | `api-04-assembly` | 仅当 Type 为 swMateType_e.swMateMAGNETIC 时有效。 |
| `IMate2.MateEntity` | `api-04-assembly` | 逐字：要取实体数量须先调 GetMateEntityCount。 |
| `IMate2.MaximumVariation` | `api-04-assembly` | 仅对 Type 为 swMateANGLE 或 swMateDISTANCE 的配合有效；最大变化 = 最大值 − 尺寸值。 |
| `IMate2.MinimumVariation` | `api-04-assembly` | 仅对 Type 为 swMateANGLE 或 swMateDISTANCE 的配合有效；最小变化 = 最小值 − 尺寸值。 |
| `IMate2.RemoveMisalignment` | `api-04-assembly` | 官方警告：调完之后其中一个同心配合可能变成不可解（unsolvable）。 |
| `IMate2.SetMaximumMisalignedDeviation` | `api-04-assembly` | 仅当 GetUseMisalignedDeviationDocumentProperty 返回 false 时有效（须先把它设为 false）；当前偏差大于该值时配合解不出。 |
| `IMate2.SetUseMisalignedDeviationDocumentProperty` | `api-04-assembly` | 设为 false 才能使用 SetMaximumMisalignedDeviation；偏差累加段同前。 |
| `IMeasure.Calculate` | `api-08-mold-costing` | Entities 传 NULL 则量选中的实体；返回 True 才说明实体类型与组合有效，否则各量会拿到 -1。 |
| `IMeasure.SetProjectionEntity` | `api-08-mold-costing` | 参数只能是面或平面（CHM 逐字 Face or plane）；设置成功返回 True。 |
| `IModelDoc2.InsertRoutePoint` | `api-10-routing-pdm-anim` | Remarks 逐字：若选区不完整就会弹出「Insert Route Point」对话框；路由点是插入配合时与草图点对齐的那个点。 |
| `IModelDocExtension.GetCostingManager` | `api-08-mold-costing` | SOLIDWORKS Costing 及其 API 只在 Professional 与 Premium 版可用；须先引用 SolidWorks.Interop.sldcostingapi.dll。 |
| `IModelDocExtension.SaveAs3` | `api-10-routing-pdm-anim` | Remarks 逐字：要传 AdvancedSaveAsOptions 先调 GetAdvancedSaveAsOptions 建对象；转 IGES/STL/STEP 必须先 ActivateDoc3 把待转文档设为活动文档、再取 ActiveDoc；要导出整个模型必须先 ClearSelection2 清选区；形参 6/7 是 out int。 |
| `IModeler.CreateBsplineSurface` | `api-01-surface` | Props 须装 8 个整型（打包进 4 个 double），且 numUKnots=numU_CtrlPoints+Uorder、numVKnots=numV_CtrlPoints+Vorder、numCtrlPtCoord=NumV*NumU*DimensionControlPoints。 |
| `IModeler.CreateConicalSurface2` | `api-01-surface` | Center/Direction/RefDirection 各是 3 个 double 的数组；SemiAngle 的单位官方明写是弧度（in radians）。 |
| `IModeler.CreateCoonsBSurface` | `api-01-surface` | 要 4 条边界曲线（u 向 2 条 + v 向 2 条）；IgnoreClosureReqt 默认不被忽略。 |
| `IModeler.CreateCylindricalSurface2` | `api-01-surface` | Center/Direction/RefDirection 各是 3 个 double 的数组，Radius 是中心处半径；结果是未裁剪曲面，要 sheet body 需再调 ISurface::CreateTrimmedSheet。 |
| `IModeler.CreateExtrusionSurface` | `api-01-surface` | ProfileCurve 只能是 line / circle / b-spline curve 三种之一（Remarks 明写）。 |
| `IModeler.CreatePlanarSurface2` | `api-01-surface` | VNormal 与 VRef 必须互相垂直（Remarks 参数表明写两条），VRootPoint 是这两个向量的公共根点。 |
| `IModeler.CreateRuledSurface` | `api-01-surface` | 两条输入曲线必须是 b-curves（Valid input curves are b-curves.）。 |
| `IModeler.CreateRuledSurfaceFromEdge` | `api-01-surface` | 须先选中一条边（官方写 Currently only a single edge is supported）；selection mark=4 用默认面、mark=6 用备用面。 |
| `IModeler.CreateSphericalSurface2` | `api-01-surface` | Axis 是球轴；RefDir 必须垂直于 Axis 且过球心，并定义 UV 空间原点（Remarks 明写）。 |
| `IModeler.CreateSweptSurface` | `api-01-surface` | 它造的是无限曲面；要裁剪曲面必须再用 ISurface::AddTrimmingLoop2 / IAddTrimmingLoop2 加裁剪环。 |
| `IModeler.CreateToroidalSurface` | `api-01-surface` | RefDirection 必须垂直于 Axis（Remarks 明写）；结果是未裁剪曲面，sheet body 要靠 ISurface::CreateTrimmedSheet。 |
| `IModeler.GetInitKnitGapWidth` | `api-01-surface` | 零参读数；调过一次 knit 之前它恒为 0。 |
| `IModeler.SetInitKnitGapWidth` | `api-01-surface` | 必须在任何 knit 类调用之前设置（官方举例是 IBody2::CreateBodyFromSurfaces）；取值范围 1e-8 ~ 0.1 米。 |
| `IModeler.ThickenSheet` | `api-01-surface` | 要在 Surface Bodies 文件夹里选中一个 sheet body（例用 GetSelectedObject6(1,-1)），并先 .Copy() 一份再传进去。 |
| `IMotionStudy.CreateByRotateModel` | `api-10-routing-pdm-anim` | Remarks 逐字：已有动画序列时 StartTime 必须累计前面所有序列的总时长；新序列则设 0 立即开始（或填一个值延迟开始）。 |
| `IPartingLineFeatureData.AccessSelections` | `api-08-mold-costing` | 把模型置入回滚态后访问选择；零件传 Component=Nothing/null，装配体传目标 IComponent2；改过用 ModifyDefinition，没改用 ReleaseSelectionAccess 收尾。 |
| `IPartingLineFeatureData.DraftAnalysis` | `api-08-mold-costing` | 想换拔模方向须先用 PullDirectionBase 改方向；本方法一旦调用就只生成按正/负拔模分类的面信息。 |
| `IPartingLineFeatureData.GetEntitiesToSplit` | `api-08-mold-costing` | 须在 AccessSelections 回滚态内调用；给两个顶点时会在两者之间为分型线特征生成一条边。 |
| `IPartingLineFeatureData.GetEntitiesToSplitCount` | `api-08-mold-costing` | 必须先于 IGetEntitiesToSplit 调用，以取数组长度。 |
| `IPartingLineFeatureData.GetFacesByType` | `api-08-mold-costing` | 官方只指向 Accessing Selections that Define Features 文档，未写必须先做什么；Type 的枚举名也未点名。 |
| `IPartingLineFeatureData.GetFacesByTypeCount` | `api-08-mold-costing` | 必须先于 IGetFacesByType 调用。 |
| `IPartingLineFeatureData.GetPartingLinesCount` | `api-08-mold-costing` | 必须先于 IGetPartingLines 调用，以取数组长度。 |
| `IPartingLineFeatureData.IGetEntitiesToSplit` | `api-08-mold-costing` | 必须先调 GetEntitiesToSplitCount() 拿 Count。 |
| `IPartingLineFeatureData.IGetFacesByType` | `api-08-mold-costing` | 必须先调 GetFacesByTypeCount(Type) 拿 Count。 |
| `IPartingLineFeatureData.IGetPartingLines` | `api-08-mold-costing` | 必须先调 GetPartingLinesCount() 拿 Count。 |
| `IPartingLineFeatureData.ISetEntitiesToSplit` | `api-08-mold-costing` | 混用草图线段与顶点时顶点必须成对出现：segment1, vtx11, vtx12, segment2, vtx21, vtx22 …。 |
| `IPartingLineFeatureData.ISetPartingLines` | `api-08-mold-costing` | 官方只指向 Accessing Selections that Define Features（回滚态内），未写别的。 |
| `IPartingLineFeatureData.PartingLines` | `api-08-mold-costing` | 官方只指向 Accessing Selections that Define Features（回滚态内读写），未写其它前置。 |
| `IPartingLineFeatureData.ReleaseSelectionAccess` | `api-08-mold-costing` | 只在没改特征时用它恢复回滚态；改过特征必须走 IFeature::ModifyDefinition 或 IModifyDefinition2。 |
| `IPartingLineFeatureData.SetEntitiesToSplit` | `api-08-mold-costing` | 顶点必须成对出现：segment1, vtx11, vtx12, segment2, vtx21, vtx22 …；官方指向 Accessing Selections 文档。 |
| `IPartingLineFeatureData.Status` | `api-08-mold-costing` | 必须在设置完该特征的各项设置与选项之后才调用它来查状态。 |
| `IPartingSurfaceFeatureData.AccessSelections` | `api-08-mold-costing` | 把模型置入回滚态后访问选择；零件传 Component=null，装配体传要修改特征所在的 IComponent2；收尾 ModifyDefinition 或 ReleaseSelectionAccess。 |
| `IPartingSurfaceFeatureData.GetPartingLinesCount` | `api-08-mold-costing` | 必须先于 IGetPartingLines 调用。 |
| `IPartingSurfaceFeatureData.IGetPartingLines` | `api-08-mold-costing` | 必须先调 GetPartingLinesCount() 拿 Count。 |
| `IPartingSurfaceFeatureData.ISetPartingLines` | `api-08-mold-costing` | 官方只指向 Accessing Selections that Define Features（回滚态内），未写别的。 |
| `IPartingSurfaceFeatureData.OffsetAngle` | `api-08-mold-costing` | 只有 PartingType 设为 swPartingSurfaceMoldParmTangent 或 swPartingSurfaceMoldParmNormal 时该属性才生效。 |
| `IPartingSurfaceFeatureData.PartingLines` | `api-08-mold-costing` | 官方只指向 Accessing Selections that Define Features（回滚态内读写），未写其它前置。 |
| `IPartingSurfaceFeatureData.PartingType` | `api-08-mold-costing` | Tangent 类型对部分几何不可用（官方原话）；文档未写其它调用前置。 |
| `IPartingSurfaceFeatureData.PullDirectionBase` | `api-08-mold-costing` | 官方只指向 Accessing Selections that Define Features（回滚态内读写），未写其它前置。 |
| `IPartingSurfaceFeatureData.ReleaseSelectionAccess` | `api-08-mold-costing` | 没改特征才用它恢复回滚态；改过特征必须走 IFeature::ModifyDefinition 或 IModifyDefinition2。 |
| `IPartingSurfaceFeatureData.TransitionDistance` | `api-08-mold-costing` | 只有 TransitionType 设为 swPartingSurfaceSmooth(=2) 时该属性才可用。 |
| `IPDMDocManager.SetCancelOperation` | `api-10-routing-pdm-anim` | Remarks 逐字：只有装了 SOLIDWORKS Toolbox 才可用；cancelOp 为 True 表示取消当前操作、False 表示继续。 |
| `IPDMDocManager.SetDocumentStatus` | `api-10-routing-pdm-anim` | Remarks 逐字：只有装了 SOLIDWORKS Toolbox 才可用；[D] 逐字要求在 BeforeWritingToDocument 事件处理器里调用。 |
| `IPDMDocManager.SetManagedDocument` | `api-10-routing-pdm-anim` | Remarks 逐字：只有装了 SOLIDWORKS Toolbox 才可用；[D] 逐字要求在 PreInsertDocument 事件处理器里调用。 |
| `IPrimaryMemberPathSegmentFeatureData.MergeTangentMembers` | `api-10-routing-pdm-anim` | Remarks 逐字：该属性只有在创建结构系统路径段构件（structure system path segment member）时才有效。 |
| `IPrimaryMemberPathSegmentFeatureData.SetPathSegments` | `api-10-routing-pdm-anim` | Remarks 逐字：.NET 应用必须先把 PathSegments 数组 marshal 成 IDispatch 对象数组再调用本方法。 |
| `IShutOffSurfaceFeatureData.AccessSelections` | `api-08-mold-costing` | 把模型置入回滚态后访问选择；零件传 Component=NULL，装配体传目标 IComponent2；收尾 ModifyDefinition 或 ReleaseSelectionAccess。 |
| `IShutOffSurfaceFeatureData.Edges` | `api-08-mold-costing` | 官方只指向 Accessing Selections that Define Features（回滚态内读写），未写其它前置。 |
| `IShutOffSurfaceFeatureData.FlipFaceTangentTo` | `api-08-mold-costing` | 只有补片类型设为 swPatchTypeTangent 时本方法才可用（配合 LoopPatchType / SetAllPatchTypes 设置）。 |
| `IShutOffSurfaceFeatureData.GetEdgeCount` | `api-08-mold-costing` | 必须先于 IGetEdges 调用，以取该数组的长度。 |
| `IShutOffSurfaceFeatureData.GetFaceTangentTo` | `api-08-mold-costing` | 只有补片类型设为 swPatchTypeTangent 时本方法才可用。 |
| `IShutOffSurfaceFeatureData.GetLoopCount` | `api-08-mold-costing` | 必须先于 IGetEdges 调用，以取该数组的长度。 |
| `IShutOffSurfaceFeatureData.GetLoopEdgeCount` | `api-08-mold-costing` | 必须先于 IGetLoopEdges 调用，以取该 loop 的数组长度。 |
| `IShutOffSurfaceFeatureData.IGetEdges` | `api-08-mold-costing` | 必须先调 GetLoopCount() 取 Count。 |
| `IShutOffSurfaceFeatureData.IGetLoopEdges` | `api-08-mold-costing` | 必须先调 GetLoopEdgeCount(Index) 取 Count；设置 loop 边要用 Edges 或 ISetEdges。 |
| `IShutOffSurfaceFeatureData.ISetEdges` | `api-08-mold-costing` | 官方只指向 Accessing Selections that Define Features（回滚态内），未写别的。 |
| `IShutOffSurfaceFeatureData.ReleaseSelectionAccess` | `api-08-mold-costing` | 没改特征才用它恢复回滚态；改过特征必须走 IFeature::ModifyDefinition 或 IModifyDefinition2。 |
| `ISketch.AutoDimension2` | `api-07-sketch` | EntitiesToDimension=swAutodimEntitiesSelected 时须 SelectByID2 带 mark=swAutodimMarkEntities；两个 datum 的 mark 分别是 HorizontalDatum / VerticalDatum，只给一个是错误。 |
| `ISketch.CheckFeatureUse` | `api-07-sketch` | OpenCount / ClosedCount 是 out；返回非 OK 时两者都回 0；FeatureType 非法返回 UnknownError。 |
| `ISketch.ConstrainAll` | `api-07-sketch` | 草图已有约束时不会再添加（等价于界面按钮每张草图只能按一次）。 |
| `ISketch.GetArcCount` | `api-07-sketch` | 必须先调它给 IGetArcs2 / GetArcs2 拿数组大小。 |
| `ISketch.GetArcs2` | `api-07-sketch` | 先 GetArcCount 定数组大小。 |
| `ISketch.GetContourEdgeCount` | `api-07-sketch` | 轮廓不闭合或含内部非构造元素时返回 0；须先于 IGetContourEdges 调用。 |
| `ISketch.GetContourEdges` | `api-07-sketch` | 只支持单轮廓草图；要模型坐标系就把 xform 设为 ModelToSketchTransform 的逆。 |
| `ISketch.GetDetachSegmentOnDrag` | `api-07-sketch` | 进出草图时会被 SOLIDWORKS 重置为 false，只在草图活动期间有用。 |
| `ISketch.GetEllipseCount` | `api-07-sketch` | 须先于 GetEllipses3 调用以定数组大小。 |
| `ISketch.GetEllipses3` | `api-07-sketch` | 先 GetEllipseCount 定数组大小。 |
| `ISketch.GetLineCount2` | `api-07-sketch` | 必须先选中草图特征（GetSelectedObject6 → GetSpecificFeature2）。 |
| `ISketch.GetLines2` | `api-07-sketch` | 先 GetLineCount2 定线数。 |
| `ISketch.GetParabolaCount` | `api-07-sketch` | 须先于 IGetParabolas2 调用。 |
| `ISketch.GetParabolas2` | `api-07-sketch` | 先 GetParabolaCount 定数组大小。 |
| `ISketch.GetReferenceEntity` | `api-07-sketch` | 草图所在面被后续特征消耗时返回 NULL + swSelNOTHING；要拿到面须先 EditSketch。 |
| `ISketch.GetSketchBlockInstanceCount` | `api-07-sketch` | 须先于 IGetSketchBlockInstances 调用。 |
| `ISketch.GetSketchContourCount` | `api-07-sketch` | 须先于 IGetSketchContours 调用；草图被抑制时也可用。 |
| `ISketch.GetSketchContours` | `api-07-sketch` | 草图被抑制时也可用。 |
| `ISketch.GetSketchPathCount` | `api-07-sketch` | 须先于 IGetSketchPaths 调用。 |
| `ISketch.GetSketchPaths` | `api-07-sketch` | 必须先 MakeSketchChain。 |
| `ISketch.GetSketchPictureCount` | `api-07-sketch` | 须先于 IGetSketchPcitures（官方原文拼写）调用。 |
| `ISketch.GetSketchPointsCount2` | `api-07-sketch` | 须先于 IGetSketchPoints2 调用。 |
| `ISketch.GetSketchRegionCount` | `api-07-sketch` | 须先于 IGetSketchRegions 调用。 |
| `ISketch.GetSketchSegments` | `api-07-sketch` | 草图有错误时返回的草图段不完整。 |
| `ISketch.GetSketchSlotCount` | `api-07-sketch` | 须先于 IGetSketchSlots 调用。 |
| `ISketch.GetSplineCount` | `api-07-sketch` | 须先于 IGetSplines 调用；PointCount 是 ref 出参。 |
| `ISketch.GetSplineInterpolateCount` | `api-07-sketch` | 须先于 IGetSplinesInterpolate 调用。 |
| `ISketch.GetSplineParams4` | `api-07-sketch` | 先 SelectByID2("Sketch1","SKETCH",…) 取 Feature → GetSpecificFeature2 得 ISketch。 |
| `ISketch.GetSplines` | `api-07-sketch` | 返回的是按显示质量细分出的点，不是生成样条时用的那些点。 |
| `ISketch.GetSplinesInterpolate` | `api-07-sketch` | 返回的是生成样条时用的那些点（与 GetSplines 相反）。 |
| `ISketch.GetUserPoints2` | `api-07-sketch` | 先 GetUserPointsCount 定数组大小。 |
| `ISketch.GetUserPointsCount` | `api-07-sketch` | 须先于 IGetUserPoints2 调用。 |
| `ISketch.IEnumSketchSegments` | `api-07-sketch` | 例子先 IGetActiveSketch2，pSketch == NULL 即无活动草图；枚举器 Next 返回 S_OK 才继续。 |
| `ISketch.IGetArcs2` | `api-07-sketch` | 先 GetArcCount 定 ArraySize。 |
| `ISketch.IGetContourEdges` | `api-07-sketch` | 只支持单轮廓；Xform 是 ref System.double（单位变换矩阵），要模型坐标系须传逆。 |
| `ISketch.IGetEllipses3` | `api-07-sketch` | 先 GetEllipseCount。 |
| `ISketch.IGetLines2` | `api-07-sketch` | 先 GetLineCount2(CrossHatchOption)。 |
| `ISketch.IGetParabolas2` | `api-07-sketch` | 先 GetParabolaCount。 |
| `ISketch.IGetSketchBlockInstances` | `api-07-sketch` | 先 GetSketchBlockInstanceCount。 |
| `ISketch.IGetSketchContours` | `api-07-sketch` | 先 GetSketchContourCount；草图被抑制时也可用。 |
| `ISketch.IGetSketchPaths` | `api-07-sketch` | 先 GetSketchPathCount。 |
| `ISketch.IGetSketchPictures` | `api-07-sketch` | 先 GetSketchPictureCount。 |
| `ISketch.IGetSketchPoints2` | `api-07-sketch` | 先 GetSketchPointsCount2。 |
| `ISketch.IGetSketchRegions` | `api-07-sketch` | 先 GetSketchRegionCount。 |
| `ISketch.IGetSketchSlots` | `api-07-sketch` | 先 GetSketchSlotCount。 |
| `ISketch.IGetSplines` | `api-07-sketch` | 返回的是细分点，不是生成样条用的点。 |
| `ISketch.IGetSplinesInterpolate` | `api-07-sketch` | 先 GetSplineInterpolateCount 定返回数组大小。 |
| `ISketch.IGetUserPoints2` | `api-07-sketch` | 先 GetUserPointsCount。 |
| `ISketch.InsertRouteLine` | `api-07-sketch` | 必须在爆炸线草图里：先 InsertExplodeLineSketch 再取 GetActiveSketch2。 |
| `ISketch.MergePoints` | `api-07-sketch` | 草图中必须只有一个开放轮廓。 |
| `ISketch.SetAutomaticSolve` | `api-07-sketch` | 大批量改草图时可临时关闭；改完必须恢复，恢复值由 GetAutomaticSolve 先读出。 |
| `ISketch.SetDetachSegmentOnDrag` | `api-07-sketch` | 进出草图会被 SOLIDWORKS 重置为 false，只在草图活动期间有用。 |
| `ISketch.SetWorkingPlaneOrientation` | `api-07-sketch` | 必须先取到 ISketch（swSketchManager.ActiveSketch）；用于 3D 草图中新 2D/3D 几何的放置平面。 |
| `ISketchManager.AddAlongXDimension` | `api-07-sketch` | 只在编辑态的 3D 草图中有效，尺寸仅在草图编辑态可见。 |
| `ISketchManager.AddAlongYDimension` | `api-07-sketch` | 同 X 版：只在编辑态的 3D 草图中有效。 |
| `ISketchManager.AddAlongZDimension` | `api-07-sketch` | 同 X 版：只在编辑态的 3D 草图中有效。 |
| `ISketchManager.AddToDB` | `api-07-sketch` | DisplayWhenAdded 生效必须先置 true；置 true 后部分实体不可撤销，必须复位 false 恢复常规模式。 |
| `ISketchManager.CreateArc` | `api-07-sketch` | 无活动草图时会自动新建一个；画完必须 AddToDB(False) 恢复常规模式。 |
| `ISketchManager.CreateBoundaryHatch` | `api-07-sketch` | 调用前必须选中作为边界的闭合草图轮廓。 |
| `ISketchManager.CreateCircle` | `api-07-sketch` | 无活动草图会自动新建；例子显式 SelectByID2 选基准面后 ClearSelection2；建完须 AddToDB(False)。 |
| `ISketchManager.CreateCircleByRadius` | `api-07-sketch` | 无活动草图会自动新建一个草图。 |
| `ISketchManager.CreateConic` | `api-07-sketch` | 无活动草图会自动新建一个草图。 |
| `ISketchManager.CreateConstructionGeometry` | `api-07-sketch` | 支持所有文档类型；IDrawingDoc::CreateConstructionGeometry 只支持工程图文档。 |
| `ISketchManager.CreateEllipse` | `api-07-sketch` | 无活动草图会自动新建；画部分椭圆要改用 CreateEllipticalArc。 |
| `ISketchManager.CreateEllipticalArc` | `api-07-sketch` | 无活动草图会自动新建（官方原文写 full circle）。 |
| `ISketchManager.CreateFillet` | `api-07-sketch` | 先 SelectByID2 选草图 + EditSketch 进编辑态，再 SelectByID2 选中 SKETCHPOINT 角点。 |
| `ISketchManager.CreateLine` | `api-07-sketch` | 无活动草图则不建线并返回 NULL（与 CreateArc/CreateCircle 的自动新建不同）。 |
| `ISketchManager.CreatePoint` | `api-07-sketch` | 无活动草图则不建点并返回 NULL（用 ActiveSketch 检查）。 |
| `ISketchManager.CreateRegionHatch` | `api-07-sketch` | 不要求先选中轮廓：三点坐标要与所有草图轮廓比较，定位唯一包含它的区域。 |
| `ISketchManager.CreateSketchBelt` | `api-07-sketch` | Side1..Side12 的顺序对应选区里皮带轮的顺序，必须先按顺序选好皮带轮；最多 12 个。 |
| `ISketchManager.CreateSketchPlane` | `api-07-sketch` | 必须先在选区按顺序放好实体（例用 EXTSKETCHSEGMENT + EXTSKETCHPOINT）；不足三个只用前几个。 |
| `ISketchManager.CreateSpline` | `api-07-sketch` | 与 AddToDB/DisplayWhenAdded 不兼容：恒等价于 AddToDB(True) + DisplayWhenAdded(False)。 |
| `ISketchManager.CreateSpline2` | `api-07-sketch` | 与 AddToDB/DisplayWhenAdded 不兼容（Remarks 与 CreateSpline 逐字相同）。 |
| `ISketchManager.CreateSpline3` | `api-07-sketch` | 2D 须其余参数全 null/Nothing；曲面上样条须先建 3D 草图、先选面取 ISurface，收尾要 InsertSketch。 |
| `ISketchManager.CreateSplineByEqnParams` | `api-07-sketch` | 坐标须在草图空间（Z 解释为 0）；非 G1 连续会被拒绝不建；与 AddToDB/DisplayWhenAdded 不兼容。 |
| `ISketchManager.CreateSplinesByEqnParams` | `api-07-sketch` | 非 G1 连续时不拒绝，而是拆成多个 G1 连续段（与 CreateSplineByEqnParams 相反）。 |
| `ISketchManager.DisplayWhenAdded` | `api-07-sketch` | 必须先 AddToDB=true 才生效；程序结束前应复位为 TRUE（GraphicsRedraw 比 EditRebuild3 快得多）。 |
| `ISketchManager.EditCircularSketchStepAndRepeat` | `api-07-sketch` | 先 SelectByID2("Line1@Sketch1","EXTSKETCHSEGMENT",…, Mark=0) + swModel.EditSketch 进编辑态。 |
| `ISketchManager.EditSketchBlock` | `api-07-sketch` | 编辑完块定义后必须调 EndEditSketchBlock 收尾。 |
| `ISketchManager.EndEditSketchBlock` | `api-07-sketch` | 必须先用 EditSketchBlock 把块置入编辑模式。 |
| `ISketchManager.ExplodeSketchBlockInstance` | `api-07-sketch` | 炸开最后一个块实例时，实体复制到宿主草图且源块定义被销毁。 |
| `ISketchManager.GetSketchBlockDefinitionCount` | `api-07-sketch` | 必须先调它，再调 IGetSketchBlockDefinitions 取数组大小。 |
| `ISketchManager.ICreateSpline` | `api-07-sketch` | 与 AddToDB/DisplayWhenAdded 不兼容；2D 草图忽略 Z。 |
| `ISketchManager.ICreateSpline2` | `api-07-sketch` | 与 AddToDB/DisplayWhenAdded 不兼容（Remarks 与 ICreateSpline 逐字相同）。 |
| `ISketchManager.ICreateSplineByEqnParams` | `api-07-sketch` | 坐标须在草图空间；非 G1 连续会被拒绝、不建。 |
| `ISketchManager.ICreateSplinesByEqnParams` | `api-07-sketch` | 同上；非 G1 连续被拒绝。 |
| `ISketchManager.IGetSketchBlockDefinitions` | `api-07-sketch` | 必须先 GetSketchBlockDefinitionCount() 拿到 BlockDefCount。 |
| `ISketchManager.InferenceMode` | `api-07-sketch` | 受 AutoInference / AddToDB / IDrawingDoc::StartDrawing 等连带设置影响。 |
| `ISketchManager.InsertSketch` | `api-07-sketch` | 该方法不支持工程图文档。 |
| `ISketchManager.InsertSketchBlockInstance` | `api-07-sketch` | 必须先 MultiSelect2(…, True, Nothing) 选实体、再 MakeSketchBlockFromSelected(Nothing) 拿 BlockDef；同一块不要重复建定义。 |
| `ISketchManager.MakeSketchBlockFromFile` | `api-07-sketch` | InsertionPoint 必须是 z=0.0 的 2D 点。 |
| `ISketchManager.MakeSketchBlockFromSelected` | `api-07-sketch` | 必须先 MultiSelect2 把实体放进选区；InsertionPoint 官方例子传 Nothing。 |
| `ISketchManager.MakeSketchChain` | `api-07-sketch` | 除非草图在编辑态否则无效；对 3D 草图无效。 |
| `ISketchManager.RotateOrCopy3DAboutXYZ` | `api-07-sketch` | 先 SelectByID2 选 SKETCH + swModel.EditSketch 进编辑态，再 GetSketchSegments 逐个 Select4。 |
| `ISketchManager.SetDynamicMirror` | `api-07-sketch` | 草图须在编辑态，且调用前必须已选中一条线段或模型的线性边。 |
| `ISketchManager.SetGridOptions` | `api-07-sketch` | AlignToEdge 置 TRUE 时必须已选中一条边。 |
| `ISketchManager.SketchExtend` | `api-07-sketch` | 要多次调用才能把选中的线依次延伸到后续多个草图实体。 |
| `ISketchManager.SketchOffset2` | `api-07-sketch` | 先用 SelectByID2("Line3","SKETCHSEGMENT",…, Append=False, Mark=1) 选中要偏置的线。 |
| `ISketchManager.SketchReplace` | `api-07-sketch` | 必须 SelectByID2 且 Append=true 选两个实体（被替换的 + 替换用的，后者不得引用下游几何或草图外引用）；调完须 InsertSketch 重建。 |
| `ISketchManager.SketchReplace2` | `api-07-sketch` | 同 SketchReplace：SelectByID2 且 Append=true 选两个实体；调完 InsertSketch 重建。 |
| `ISketchManager.SketchTrim` | `api-07-sketch` | 须先编辑草图并用 SelectByID2 选好要裁剪的段；mark 因 Option 而异（TwoEntities=0、Entities=2）；X/Y/Z 只有 EntityPoint 传非零，其余全 0.0。 |
| `ISketchManager.SplitClosedSegment` | `api-07-sketch` | 必须先关捕捉：取消 System Options 的 Enable snapping，或 SetUserPreferenceToggle(swSketchInference, false)。 |
| `ISketchManager.SplitOpenSegment` | `api-07-sketch` | 同 SplitClosedSegment：必须先关 snapping。 |
| `IToolingSplitFeatureData.AccessSelections` | `api-08-mold-costing` | 把模型置入回滚态后访问选择；零件传 Component=NULL，装配体传目标 IComponent2；收尾 ModifyDefinition 或 ReleaseSelectionAccess。 |
| `IToolingSplitFeatureData.Angle` | `api-08-mold-costing` | 官方只指向 Accessing Selections that Define Features（回滚态内）；须 InterlockSurface=true 后才可设拔模角。 |
| `IToolingSplitFeatureData.CavitySurfaces` | `api-08-mold-costing` | 官方只指向 Accessing Selections that Define Features（回滚态内读写），未写其它前置。 |
| `IToolingSplitFeatureData.CoreSurfaces` | `api-08-mold-costing` | 官方只指向 Accessing Selections that Define Features（回滚态内读写），未写其它前置。 |
| `IToolingSplitFeatureData.GetCavitySurfacesCount` | `api-08-mold-costing` | 必须先于 IGetCavitySurfaces 调用，以取该数组的长度。 |
| `IToolingSplitFeatureData.GetCoreSurfacesCount` | `api-08-mold-costing` | 必须先于 IGetCoreSurfaces 调用，以取该数组的长度。 |
| `IToolingSplitFeatureData.GetPartingSurfacesCount` | `api-08-mold-costing` | 必须先于 IGetPartingSurfaces 调用，以取该数组的长度。 |
| `IToolingSplitFeatureData.IGetCavitySurfaces` | `api-08-mold-costing` | 必须先调 GetCavitySurfacesCount() 取 Count。 |
| `IToolingSplitFeatureData.IGetCoreSurfaces` | `api-08-mold-costing` | 必须先调 GetCoreSurfacesCount() 取 Count。 |
| `IToolingSplitFeatureData.IGetPartingSurfaces` | `api-08-mold-costing` | 必须先调 GetPartingSurfacesCount() 取 Count。 |
| `IToolingSplitFeatureData.InterlockSurface` | `api-08-mold-costing` | 置为 true 之后才能给 interlocking 面指定拔模角（即 Angle 属性）。 |
| `IToolingSplitFeatureData.ISetCavitySurfaces` | `api-08-mold-costing` | 官方只指向 Accessing Selections that Define Features（回滚态内），未写别的。 |
| `IToolingSplitFeatureData.ISetCoreSurfaces` | `api-08-mold-costing` | 官方只指向 Accessing Selections that Define Features（回滚态内），未写别的。 |
| `IToolingSplitFeatureData.ISetPartingSurfaces` | `api-08-mold-costing` | 官方只指向 Accessing Selections that Define Features（回滚态内），未写别的。 |
| `IToolingSplitFeatureData.PartingSurfaces` | `api-08-mold-costing` | 官方只指向 Accessing Selections that Define Features（回滚态内读写），未写其它前置。 |
| `IToolingSplitFeatureData.ReleaseSelectionAccess` | `api-08-mold-costing` | 没改特征才用它恢复回滚态；改过特征必须走 IFeature::ModifyDefinition 或 IModifyDefinition2。 |

### 2.2 「官方例子给了配方实参的」—— 抄一句「照着这个调」

★ 共 **207** 条（占 30%）。**这几条的调用序/实参来自官方例子，可直接抄。**

| 接口.成员 | 源 | 配方（官方例子实参/调用序） |
|---|---|---|
| `IApplication.PDMDocManager` | `api-10-routing-pdm-anim` | GetAddInObject("{ED783340-D5DB-11d4-BD5A-00C04F019809}", &pDisp) → cast 成 SOLIDWORKS.Interop.swbrowser.IApplication → 读 .PDMDocManager（swbrowser 命名空间）。 |
| `IAssemblyDoc.CreateExplodedView` | `api-04-assembly` | For i=0 To 4 循环调 CreateExplodedView → GetExplodedViewNames 取名 → ShowExploded2(True,name) → ViewExplodeAssembly / ViewCollapseAssembly。 |
| `IAssemblyDoc.GetExplodedViewCount` | `api-04-assembly` | swAssembly.GetExplodedViewCount —— 例子用它与字符串拼接打印「Number of exploded views created: 」。 |
| `IAssemblyDoc.GetExplodedViewNames` | `api-04-assembly` | vViewName = swAssembly.GetExplodedViewNames → For i = 0 To UBound(vViewName) → sViewName = vViewName(i)。 |
| `IAssemblyDoc.GetRouteManager` | `api-10-routing-pdm-anim` | GetRouteManager → rtRouteManager.EditRoute → GetAutoRoute → ShowGuidelines → 先选两个 SKETCHPOINT → CreatePointToPointAutoRoute(swOrthogonalMode) → ExitRoute → swTopLevelAssembly.EditAssembly；类型是 SWRoutingLib.RouteManager。 |
| `IAssemblyDoc.ShowExploded2` | `api-04-assembly` | 循环 For i = 0 To UBound(vViewName)：sViewName = vViewName(i) → Call swAssembly.ShowExploded2(True, sViewName)；隐藏时把 True 换成 False。 |
| `IAssemblyDoc.ToolsCheckInterference2` | `api-04-assembly` | GetSelectedObjectCount → GetSelectedObjectsComponent2(i+1) 装数组 → 调本方法 → IsEmpty 判空 → 面 Select4(True,swSelData)、组件 Select2(True,0)。 |
| `IAssemblyDoc.ViewCollapseAssembly` | `api-04-assembly` | swAssembly.ViewCollapseAssembly —— 官方例子的最后一行调用，紧接在 ViewExplodeAssembly 之后。 |
| `IAssemblyDoc.ViewExplodeAssembly` | `api-04-assembly` | swAssembly.ViewExplodeAssembly（其后紧跟一行 Stop），与 ViewCollapseAssembly 成对调用。 |
| `IAVIParameter.BlurLength` | `api-10-routing-pdm-anim` | swSaveAVIData.BlurLength = 10（Returns 段写取值域 0..100、默认 50）。 |
| `IAVIParameter.BlurOffset` | `api-10-routing-pdm-anim` | swSaveAVIData.BlurOffset = -100（0=居中当前帧、100=向前挪整帧、-100=向后挪整帧）。 |
| `IAVIParameter.FramePerSecond` | `api-10-routing-pdm-anim` | 两个官方例子都写 swSaveAVIData.FramePerSecond = 7.5（类型是 double）。 |
| `IAVIParameter.MotionBlur` | `api-10-routing-pdm-anim` | swSaveAVIData.MotionBlur = True。 |
| `IAVIParameter.OutputType` | `api-10-routing-pdm-anim` | swSaveAVIData.OutputType = swAnimationOutputType_e.swAnimationOutput_AVI（=1）；另一个官方例子直接写裸数字 1。 |
| `IAVIParameter.RendererType` | `api-10-routing-pdm-anim` | swSaveAVIData.RendererType = swRendererType_e.swRendererType_Solidworks_Screen（=0）。 |
| `IAVIParameter.SaveEntireAnimation` | `api-10-routing-pdm-anim` | 官方例子写 swSaveAVIData.SaveEntireAnimation = True；设 False 时 StartTime/EndTime 的具体写法本轮未读、抄不到。 |
| `IBomFeature.RoutingComponentGrouping` | `api-10-routing-pdm-anim` | 先 SelectByID2("Bill of Materials1","BOMFEATURE",...) 再 GetSelectedObject6(1,-1) 取 BOM 对象，写入 swRoutingComponentGroupingOption_e.swShowOnlyRoutingComponentsInBOM + .swDisplayUnitsInBOM。 |
| `ICavityFeatureData.AccessSelections` | `api-08-mold-costing` | SelectByID2("Cavity1@telephoneMoldBase-1@AssemInterim","BODYFEATURE",…) → GetSelectedObject6(1,-1) → GetDefinition() → AccessSelections(swModel, null) → 改 → ModifyDefinition。 |
| `ICavityFeatureData.GetScale` | `api-08-mold-costing` | swCavityFeatureData.GetScale(out xScale, out yScale, out zScale); 前后 Debug.Print 打印 Scale values 与 X / Y / Z。 |
| `ICavityFeatureData.ScaleType` | `api-08-mold-costing` | Debug.Print("Scale type: " + swCavityFeatureData.ScaleType);（取值为 swCavityScaleType_e） |
| `ICavityFeatureData.UniformScale` | `api-08-mold-costing` | swCavityFeatureData.UseUniformScale = true; → swCavityFeatureData.UniformScale = 2; → ModifyDefinition。 |
| `ICavityFeatureData.UseUniformScale` | `api-08-mold-costing` | Debug.Print("Scale uniformly value: " + swCavityFeatureData.UseUniformScale); 或直接 swCavityFeatureData.UseUniformScale = true; |
| `IComponent2.GetChildren` | `api-04-assembly` | ActiveConfiguration → GetRootComponent3(True) → vChildCompArr = swComp.GetChildren → For Each vChildComp 递归。 |
| `IComponent2.Select4` | `api-04-assembly` | swSelMgr.CreateSelectData → bRet = swEnt.Select4(True, swSelData)（官方干涉例逐字，第三参省略）。 |
| `IComponent2.SetSuppression2` | `api-04-assembly` | ActiveConfiguration → GetRootComponent3(True) → 关 FeatureTree → 递归 GetChildren 后调 SetSuppression2(Lightweight/FullyResolved) → 复原。 |
| `IConnectionPointFeatureData.Direction` | `api-10-routing-pdm-anim` | vDirection = cPointData.Direction 后按 (0)/(1)/(2) 下标拆 3 个 double（只读属性，无 set）。 |
| `IConnectionPointFeatureData.ElectricalPinID` | `api-10-routing-pdm-anim` | 例子写 cPointData.ElectricalPinID = "zxc"。 |
| `IConnectionPointFeatureData.Location` | `api-10-routing-pdm-anim` | vLocation = cPointData.Location 后按 vLocation(0)/(1)/(2) 下标拆成 x/y/z 打印（只读属性，无 set）。 |
| `IConnectionPointFeatureData.Name2` | `api-10-routing-pdm-anim` | 例子写 cPointData.Name2 = "myCPoint"；Postconditions 逐字：CPoint1 现在在特征树里叫 MyCPoint。 |
| `IConnectionPointFeatureData.PortID` | `api-10-routing-pdm-anim` | 例子写 cPointData.PortID = "newPortID"。 |
| `IConnectionPointFeatureData.RouteDiameter` | `api-10-routing-pdm-anim` | 例子写 cPointData.RouteDiameter = 0.011（原文米制值，未做单位换算）。 |
| `IConnectionPointFeatureData.RouteSubType` | `api-10-routing-pdm-anim` | 例子直接写 cPointData.RouteSubType = 3。 |
| `IConnectionPointFeatureData.RouteType` | `api-10-routing-pdm-anim` | 例子直接写 cPointData.RouteType = 2（对应 swModelRouteType_FabricatedPipe = 2），前后各 Debug.Print 一次读值。 |
| `IConnectionPointFeatureData.StubLength` | `api-10-routing-pdm-anim` | 例子写 cPointData.StubLength = 0.009。 |
| `ICoreFeatureData.AccessSelections` | `api-08-mold-costing` | GetSelectedObject6(1,-1) → swFeat.GetDefinition() → swCoreFeat.AccessSelections(swModel, null) → 读属性 → swCoreFeat.ReleaseSelectionAccess()。 |
| `ICoreFeatureData.BoundingSketch` | `api-08-mold-costing` | swFeat = swCoreFeat.BoundingSketch; nam = swFeat.Name; Debug.Print("Name of bounding sketch = " + nam); |
| `ICoreFeatureData.CapEnds` | `api-08-mold-costing` | cap = swCoreFeat.CapEnds; Debug.Print("Are ends capped? " + cap); |
| `ICoreFeatureData.Depth` | `api-08-mold-costing` | d1 = swCoreFeat.get_Depth(0); d2 = swCoreFeat.get_Depth(1); 分别打印沿/背离拔模方向的深度（索引属性）。 |
| `ICoreFeatureData.DraftAngle` | `api-08-mold-costing` | 官方把它放在 if (useDr) 分支里：ang = swCoreFeat.DraftAngle; Debug.Print("Angle of draft = " + ang); |
| `ICoreFeatureData.DraftOutward` | `api-08-mold-costing` | 官方放在 if (useDr) 分支里：Drout = swCoreFeat.DraftOutward; Debug.Print("Drafted outward? = " + Drout); |
| `ICoreFeatureData.EndCondition` | `api-08-mold-costing` | e1 = swCoreFeat.get_EndCondition(0); e2 = swCoreFeat.get_EndCondition(1); 分别打印沿/背离拔模方向的终止条件（索引属性）。 |
| `ICoreFeatureData.GetExtractionDirection` | `api-08-mold-costing` | ct = swCoreFeat.GetExtractionDirection(out typ1, out dir1, out typ2, out dir2); 打印定义方向的实体个数。 |
| `ICoreFeatureData.ReleaseSelectionAccess` | `api-08-mold-costing` | 官方例子在 //Roll forward 之后调用 swCoreFeat.ReleaseSelectionAccess(); |
| `ICoreFeatureData.ReverseDirection` | `api-08-mold-costing` | rev = swCoreFeat.ReverseDirection; Debug.Print("Direction of extraction reversed? " + rev); |
| `ICoreFeatureData.UseDraft` | `api-08-mold-costing` | useDr = swCoreFeat.UseDraft; Debug.Print("Drafted? " + useDr); 再用 if (useDr) 包住 DraftAngle / DraftOutward 的读取。 |
| `ICWLoadsAndRestraintsManager.AddPressure` | `api-09-simulation` | 先 LBCMgr.AddPressure(0, 面数组, Nothing, errCode) 建载荷，再 PressureBeginEdit → 设 Unit=1、Value=1000 → PressureEndEdit(errCode) 提交。 |
| `ICWLoadsAndRestraintsManager.AddRestraint` | `api-09-simulation` | LBCMgr.AddRestraint(0, Array(面1, 面2), Nothing, errCode) —— 官方例子建固定约束就传 0 + 面数组 + Nothing。 |
| `ICWLoadsAndRestraintsManager.CopyLoadsAndRestraintsToStudy` | `api-09-simulation` | 按 Count 循环 GetLoadsAndRestraints(i, errCode).Name 组数组，再 CopyLoadsAndRestraintsToStudy("Partial", fixtures)。 |
| `ICWLoadsAndRestraintsManager.Count` | `api-09-simulation` | 官方例子用 For i = 0 To (lrMngr.Count - 1) 递减循环取全部载荷与约束。 |
| `ICWLoadsAndRestraintsManager.GetLoadsAndRestraints` | `api-09-simulation` | Set Fixture = lrMngr.GetLoadsAndRestraints(i, errCode)，再取 Fixture.Name。 |
| `IExplodeStep.GetNumOfComponents` | `api-04-assembly` | Set swExplodeStep = swConfiguration.GetExplodeStep(0) → Debug.Print 打印 swExplodeStep.GetNumOfComponents 的组件数。 |
| `IExplodeStep.IsSubAssemblyRigid` | `api-04-assembly` | swConfiguration.GetExplodeStep(0) → Debug.Print 「Is the sub-assembly rigid? 」& swExplodeStep.IsSubAssemblyRigid。 |
| `IExplodeStep.Name` | `api-04-assembly` | swConfiguration.GetExplodeStep(0) → Debug.Print 「Name of explode step: 」& swExplodeStep.Name。 |
| `IFeatureManager.CreateDefinition` | `api-06-features` | CreateDefinition((int)swFeatureNameID_e.<常量>) → base flange / corner relief / solid-to-sheet-metal / library / simple fillet / thread 这六类必须再调各自 Initialize*，再 CreateFeature(data)。 |
| `IFeatureManager.CreateStructuralMemberGroup` | `api-03-weldment` | 无参建组 → 设 Segments、Angle（弧度）、ApplyCornerTreatment / CornerTreatmentType / MirrorProfile / MirrorProfileAxis / GapWithinGroup（米）→ 装一元素数组转 Variant。 |
| `IFeatureManager.FeatureBossThicken` | `api-01-surface` | SetSelectedObjectMark(1,1,swSelectionMarkSet) 之后调 FeatureBossThicken(0.001, swThickenSideOne, 0, False, True, True, True)。 |
| `IFeatureManager.InsertCombineFeature` | `api-06-features` | 先 mark=0 试选 → ClearSelection2(true) → mark=2 重选 → InsertCombineFeature((int)swBodyOperationType_e.SWBODYADD, null, null)，两个体参数都传 null。 |
| `IFeatureManager.InsertCosmeticWeldBead2` | `api-03-weldment` | from 面 SelectByID2 传 mark 4、to 面传 mark 8 → GetSelectedObject6(1,4)/(1,8) → 各装一元素数组转 Variant → 调 (0, weldFromArray, weldToArray, 15/1000)。 |
| `IFeatureManager.InsertEndCapFeature2` | `api-03-weldment` | SelectByID2 选 1 个面（mark 传 1）→ GetSelectedObject6(1,-1) → 装一元素数组 → 转 Variant y → 调 (0.005, False, True, 0.003, 0.5, 0.003, y)。 |
| `IFeatureManager.InsertEndCapFeature3` | `api-03-weldment` | 先 EditDelete 旧 End cap1 → 连续 2 次 SelectByID2 选面（mark 都 0）→ 直调 10 参 (0.005,False,False,0.003,0.6,0.003,True,0.002,False,2) → GetDefinition 读回。 |
| `IFeatureManager.InsertFilletBeadFeature3` | `api-03-weldment` | ClearSelection2 → 3 次 SelectByID2 选面、mark 依次 1/2/4 → 按 mark 取对象分组成 FaceSet1 与 FaceSet2 → fbEdges(0)=0 → 调 18 参末两位传 v1/v2。 |
| `IFeatureManager.InsertFillSurface2` | `api-01-surface` | SelectByID2(Sketch2,SKETCH,…,True,257,…) → GetSelectedObject6(1,257) → InsertFillSurface2(2, swOptimizeSurface, selObj, swContact, Nothing, Nothing)。 |
| `IFeatureManager.InsertGussetFeature2` | `api-03-weldment` | 选 2 面（mark 分别 1、2）→ GetSelectedObjectCount 回读=2 才继续 → 按 mark 取对象装数组转 Variant z → 调 16 参 (0.005,0,0,False,0.025,0.025,0.015,0.7854,0.015,True,0.005,0,False,False,False,z)。 |
| `IFeatureManager.InsertGussetFeature3` | `api-03-weldment` | 两次 SelectByID2 选面、mark 都传 1 → 直调 20 参；DirType=swGussetThicknessBothSides、LocType=swGussetProfileLocationCenter，末五位 0.0125/0.0125/0.785398163397452/True/False。 |
| `IFeatureManager.InsertIndent` | `api-06-features` | SelectByID2(体名, SOLIDBODY, …, mark=1) 加 SelectByID2(空名, FACE, x,y,z, append=true, mark=4) → InsertIndent(0.01, 0, true, true, false, false)。 |
| `IFeatureManager.InsertRib` | `api-06-features` | SelectByID2(草图名, SKETCH, 0,0,0, append=false, mark=0) → InsertRib(true, false, 厚度, 0, false, false, true, 拔模角, false, false) → GetSelectedObject6(1,-1).GetDefinition() 取 RibFeatureData2。 |
| `IFeatureManager.InsertScale` | `api-06-features` | 不做任何选择、只传参：InsertScale(swScaleAboutOrigin, True, 3, 3, 3)，随后 GetDefinition() 取 IScaleFeatureData。 |
| `IFeatureManager.InsertSewRefSurface` | `api-01-surface` | SelectByID2(Surface-Extrude1,BODYFEATURE,…,mark=1) 与 SelectByID2(Surface-Plane1,SURFACEBODY,…,Append=True,mark=1) → InsertSewRefSurface(True,False,False,0.0001,0.0001)。 |
| `IFeatureManager.InsertStructuralWeldment3` | `api-03-weldment` | ClearSelection2 → InsertSketch2 进草图 → CreateCornerRectangle → CreateStructuralMemberGroup + Segments= → 退草图 → 调 (profilePathName, swEndConditionButt1, 0#, False, (vGroups2))。 |
| `IFeatureManager.InsertStructuralWeldment4` | `api-03-weldment` | InsertWeldmentFeature → CreateStructuralMemberGroup → 选两条 EXTSKETCHSEGMENT（mark 都 0）→ GetSelectedObject6(1,0)/(2,0) → Segments= → 调 (…3 x 5.sldlfp, 1, False, (vGroups1))。 |
| `IFeatureManager.InsertStructuralWeldment5` | `api-03-weldment` | ★经复核改正：官方页确有 ## Examples，挂 3 个 Custom Weldment Profile 例子（C#/VB.NET/VBA，文件均存在）。分域文件原判「无例子」实为「未读出实参」。 |
| `IFeatureManager.InsertSubWeldFolder2` | `api-03-weldment` | SelectByID2 选 Gusset1(SOLIDBODY)（mark 0、Append=False）→ GetSelectedObject6(1,-1) → 装 obj(0) → 转 Variant v → 调 InsertSubWeldFolder2((v)) → ClearSelection2。 |
| `IFeatureManager.InsertSweepSurface3` | `api-01-surface` | SelectByID2(Sketch2,SKETCH,…,mark=1) → SelectByID2(Sketch1,SKETCH,…,Append=True,mark=4) → InsertSweepSurface3(False,0,False,False,0,0,0,True,True,0,True,False,0,0)。 |
| `IFeatureManager.InsertUntrimSurface2` | `api-01-surface` | SelectByRay(...) 做预选之后调用 Part.FeatureManager.InsertUntrimSurface2 0, 2, 0, False, True（该例子只存在于 CHM 页）。 |
| `IFeatureManager.InsertWeldmentCutList2` | `api-03-weldment` | v = Part.GetBodies2(0, True) 取体数组 → 转 Variant → 单参调 Part.FeatureManager.InsertWeldmentCutList2(v)。 |
| `IFeatureManager.InsertWeldmentFeature` | `api-03-weldment` | ClearSelection2 → 两次 CreateCornerRectangle → InsertSketch True → ViewZoomtofit2 → 无参调 Part.FeatureManager.InsertWeldmentFeature()，紧接着 CreateStructuralMemberGroup。 |
| `IFeatureManager.InsertWeldmentTrimFeature2` | `api-03-weldment` | 先选 mark=2 边界体再选 mark=1 待剪体 → Count=2 → 按序取对象转数组 → ClearSelection2 → 调 (1, 四项位或, 0.01, (v1), (v2))。 |
| `IFeatureManager.InsertWrapFeature` | `api-06-features` | SelectByID2(草图, SKETCH, …, mark=4) 加 SelectByID2(空名, FACE, x,y,z, append=true, mark=1) → InsertWrapFeature(2, 0.001, false)；本例不选 pull 方向。 |
| `IFeatureManager.InsertWrapFeature2` | `api-06-features` | 草图 SelectByID2(…, mark=4) 加 6 个 SelectByRay(…, mark=1) → InsertWrapFeature2((int)swWrapSketchType_Scribe, 0.00254, false, (int)swWrapMethods_SplineSurface, 5)。 |
| `IFeatureManager.PostIntersect` | `api-06-features` | PostIntersect(intToExclude, True, False)：第一实参是与相交区域数对齐的 bool 数组（例子为 4 元素 boolArr(3)），Merge=True、Consume=False。 |
| `IFeatureManager.PostTrimSurface` | `api-01-surface` | PreTrimSurface(...) → SelectByID2(…,SURFACEBODY,…) →（可选 SolidForTrim=True）→ PostTrimSurface(True)。 |
| `IFeatureManager.PreIntersect` | `api-06-features` | 在特征树上多选（例子没写 mark）→ PreIntersect(False) → ClearSelection2 True → PostIntersect(intToExclude, True, False)。 |
| `IFeatureManager.PreIntersect2` | `api-06-features` | SelectByID2(体名, SOLIDBODY, …, mark=0) 加 SelectByID2(Plane6, PLANE, …, mark=0) → PreIntersect2(false, 1) → ClearSelection2(true) → PostIntersect(excludeArray, true, false)。 |
| `IFeatureManager.PreTrimSurface` | `api-01-surface` | PreTrimSurface(False,True,False,False) → SelectByID2(…,SURFACEBODY,…,mark=0) → PostTrimSurface(True)。 |
| `IFeatureManager.SolidForTrim` | `api-01-surface` | swFeatureManager.SolidForTrim = True，夹在 PreTrimSurface 与 PostTrimSurface(True) 之间（例中先读回再写再读回）。 |
| `IMeasure.Angle` | `api-08-mold-costing` | if (!(swMeasure.Angle == -1)) { Debug.Print("Angle: " + swMeasure.Angle); } —— 先判 -1 再读。 |
| `IMeasure.ArcLength` | `api-08-mold-costing` | Debug.Print("Arc length: " + swMeasure.ArcLength); —— 官方先判 != -1 再打印。 |
| `IMeasure.ArcOption` | `api-08-mold-costing` | swMeasure.ArcOption = 0;（注释逐字 0=center to center、1=minimum distance、2=maximum distance）须在 Calculate 之前设。 |
| `IMeasure.Area` | `api-08-mold-costing` | Debug.Print("Area: " + swMeasure.Area); —— 官方先判 != -1 再打印。 |
| `IMeasure.Calculate` | `api-08-mold-costing` | status = swMeasure.Calculate(null); 返回真后逐项判 != -1 再 Debug.Print（Length / Area / …）。 |
| `IMeasure.CenterDistance` | `api-08-mold-costing` | Debug.Print("Center distance: " + swMeasure.CenterDistance); —— 官方先判 != -1 再打印。 |
| `IMeasure.ChordLength` | `api-08-mold-costing` | Debug.Print("Chord length: " + swMeasure.ChordLength); —— 官方先判 != -1 再打印。 |
| `IMeasure.DeltaX` | `api-08-mold-costing` | Debug.Print("DeltaX: " + swMeasure.DeltaX); —— 官方先判 != -1 再打印。 |
| `IMeasure.DeltaY` | `api-08-mold-costing` | Debug.Print("DeltaY: " + swMeasure.DeltaY); —— 官方先判 != -1 再打印。 |
| `IMeasure.DeltaZ` | `api-08-mold-costing` | Debug.Print("DeltaZ: " + swMeasure.DeltaZ); —— 官方先判 != -1 再打印。 |
| `IMeasure.Diameter` | `api-08-mold-costing` | Debug.Print("Diameter: " + swMeasure.Diameter); —— 官方先判 != -1 再打印。 |
| `IMeasure.Distance` | `api-08-mold-costing` | Debug.Print("Distance: " + swMeasure.Distance); —— 官方先判 != -1 再打印。 |
| `IMeasure.IsConcentricSpheres` | `api-08-mold-costing` | if ((swMeasure.IsConcentricSpheres)) { Debug.Print("Are concentric spheres: " + …); } |
| `IMeasure.IsIntersect` | `api-08-mold-costing` | if ((swMeasure.IsIntersect)) { Debug.Print("Is intersect: " + swMeasure.IsIntersect); } |
| `IMeasure.IsParallel` | `api-08-mold-costing` | if ((swMeasure.IsParallel)) { Debug.Print("Is parallel: " + swMeasure.IsParallel); } |
| `IMeasure.IsPerpendicular` | `api-08-mold-costing` | if ((swMeasure.IsPerpendicular)) { Debug.Print("Is perpendicular: " + swMeasure.IsPerpendicular); } |
| `IMeasure.Length` | `api-08-mold-costing` | if (!(swMeasure.Length == -1)) { Debug.Print("Length: " + swMeasure.Length); } |
| `IMeasure.Normal` | `api-08-mold-costing` | Debug.Print("Normal: " + swMeasure.Normal); —— 官方先判 != -1 再打印。 |
| `IMeasure.NormalDistance` | `api-08-mold-costing` | Debug.Print("Normal distance: " + swMeasure.NormalDistance); —— 官方先判 != -1 再打印。 |
| `IMeasure.Perimeter` | `api-08-mold-costing` | Debug.Print("Perimeter: " + swMeasure.Perimeter); —— 官方先判 != -1 再打印。 |
| `IMeasure.Projection` | `api-08-mold-costing` | Debug.Print("Projection: " + swMeasure.Projection); —— 官方先判 != -1 再打印；需先 SetProjectionEntity。 |
| `IMeasure.Radius` | `api-08-mold-costing` | Debug.Print("Radius: " + swMeasure.Radius); —— 官方先判 != -1 再打印。 |
| `IMeasure.SpericalCenterDistance` | `api-08-mold-costing` | Debug.Print("Spherical center distance: " + swMeasure.SpericalCenterDistance); —— 官方成员名拼作 Sperical（少一个 h）。 |
| `IMeasure.TotalArea` | `api-08-mold-costing` | Debug.Print("Total area: " + swMeasure.TotalArea); —— 官方先判 != -1 再打印。 |
| `IMeasure.TotalLength` | `api-08-mold-costing` | Debug.Print("Total length: " + swMeasure.TotalLength); —— 官方先判 != -1 再打印。 |
| `IMeasure.X` | `api-08-mold-costing` | Debug.Print("X coordinate: " + swMeasure.X); —— 官方先判 != -1 再打印。 |
| `IMeasure.Y` | `api-08-mold-costing` | Debug.Print("Y coordinate: " + swMeasure.Y); —— 官方先判 != -1 再打印。 |
| `IMeasure.Z` | `api-08-mold-costing` | Debug.Print("Z coordinate: " + swMeasure.Z); —— 官方先判 != -1 再打印。 |
| `IModelDocExtension.CreateMeasure` | `api-08-mold-costing` | SelectByID2 选面 → (Measure)swModelDocExt.CreateMeasure() → 设 ArcOption → Calculate(null) → 读各量 → ClearSelection2(true)。 |
| `IModelDocExtension.GetCostingManager` | `api-08-mold-costing` | (CostManager)swModelDocExt.GetCostingManager() → WaitForUIUpdate() → CostingModel → CostPart → CreateCostAnalysis(<.sldctc/.sldcts 模板路径>)。 |
| `IModelDocExtension.GetMotionStudyManager` | `api-10-routing-pdm-anim` | Set swModelDocExt = swModel.Extension → Set swMotionMgr = swModelDocExt.GetMotionStudyManager() → 判 Is Nothing → GetMotionStudy("Motion Study 1")。 |
| `IModeler.CreateExtrusionSurface` | `api-01-surface` | 造曲线 → 给 3 分量拉伸轴 → ICreateExtrusionSurface → AddTrimmingLoop(...) → CreateTrimmedSurface() → CreateBodyFromSurfaces()；注意该例走的是 IBody2 而非 IModeler。 |
| `IModeler.CreatePlanarSurface2` | `api-01-surface` | swModeller.CreatePlanarSurface2((vBasePt),(vNormal),(vXvect))，例中取值分别是 (0,0,0) / (0,0,1) / (1,0,0)。 |
| `IModeler.CreateRuledSurface` | `api-01-surface` | 选中两条 b 曲线边 → GetCurve() → swModeler.CreateRuledSurface(swCurve(0), swCurve(1), (vApex))，例中 vApex=(0,0,0)。 |
| `IModeler.CreateRuledSurfaceFromEdge` | `api-01-surface` | swModel.CreateRuledSurfaceFromEdge(swDoc, swEdgeList, 1, 0.02, True, False, True, 0#, False, 1#, 0#, 0#, False, swRuledBody)（14 个形参=13 入参+1 out）。 |
| `IModeler.CreateSphericalSurface2` | `api-01-surface` | swModeler.CreateSphericalSurface2(dCenter,dAxis,dRef,0.01) → CreateTrimmedSheet5(ZeroTrimmingCurves,True,0.00001) → CreateFeatureFromBody3。 |
| `IModeler.ThickenSheet` | `api-01-surface` | swModeler.ThickenSheet(swOriginalSheetBody, 0.01, swThickenDirection_Side1) → CreateFeatureFromBody3(...) → EditRebuild3。 |
| `IMotionStudy.CreateByRotateModel` | `api-10-routing-pdm-anim` | CreateByRotateModel(True, swAnimatorAxisOfRotation_e.swRotationAboutYAxis, 1, swAnimatorDirectionOfRotation_e.swRotationClockwise, 10, 0)；Remarks 自带代码还给了 GetMotionStudyManager → CreateMotionStudy → Play 的序。 |
| `IMotionStudy.Play` | `api-10-routing-pdm-anim` | 先 PlayMode = swAnimationPlayMode_e.swAnimationPlayModeLoop，再 SetTime 0，再 Play；停止用 Stop（起点是时间轴当前所在位置）。 |
| `IMotionStudy.SaveToAVI` | `api-10-routing-pdm-anim` | CreateAVIParameter() 建对象后设 7 项（FramePerSecond=7.5、SaveEntireAnimation=True、OutputType=swAnimationOutput_AVI、RendererType=swRendererType_Solidworks_Screen、MotionBlur=True、BlurLength=10、BlurOffset=-100），先 swMotionStudy1.Stop 再 SaveToAVI "C:\test\Anim1.avi", swSaveAVIData。 |
| `IMotionStudyManager.CreateAVIParameter` | `api-10-routing-pdm-anim` | Set swSaveAVIData = swMotionMgr.CreateAVIParameter()，返回类型写 AVIParameter（声明用 Dim swSaveAVIData As SwMotionStudy.AVIParameter），调用点在 Stop 之后、SaveToAVI 之前。 |
| `IPartingLineFeatureData.AccessSelections` | `api-08-mold-costing` | swFeat.GetDefinition() → swPartingLine.AccessSelections(swModel, Nothing) → 改 SplitFaces/CoreCavitySplit/SplitFacesOption → swFeat.ModifyDefinition(data, swModel, Nothing)。 |
| `IPartingLineFeatureData.Angle` | `api-08-mold-costing` | Debug.Print("    Draft angle: " + swPartingLineFeatureData.Angle);（官方例子在 AccessSelections 回滚态内读，与 Status() 一起打印） |
| `IPartingLineFeatureData.CoreCavitySplit` | `api-08-mold-costing` | Debug.Print " Core/cavity split = " & swPartingLine.CoreCavitySplit，然后 swPartingLine.CoreCavitySplit = True，再 ModifyDefinition。 |
| `IPartingLineFeatureData.GetEntitiesToSplitCount` | `api-08-mold-costing` | Debug.Print("    Number of entities to split: " + swPartingLineFeatureData.GetEntitiesToSplitCount()); |
| `IPartingLineFeatureData.PullDirection` | `api-08-mold-costing` | 先 Debug.Print 读 PullDirection；若为真则置 false，否则置 true（官方例子的读后取反写回序列）。 |
| `IPartingLineFeatureData.PullDirectionType` | `api-08-mold-costing` | Debug.Print("    Pull direction type as defined by swSelectType_e: " + swPartingLineFeatureData.PullDirectionType); |
| `IPartingLineFeatureData.SplitFaces` | `api-08-mold-costing` | AccessSelections 后 swPartingLine.SplitFaces = True，再 SplitFacesOption = swSplitFacesAtSpecifiedAngle，最后 ModifyDefinition。 |
| `IPartingLineFeatureData.SplitFacesOption` | `api-08-mold-costing` | 官方例子在 if (SplitFaces) 分支里 Debug.Print 该属性，并把它置为 swSplitFacesAtSpecifiedAngle(=1)。 |
| `IPartingLineFeatureData.Status` | `api-08-mold-costing` | Debug.Print("    Parting line status as defined by swPartingLineFeatureStatus_e: " + swPartingLineFeatureData.Status()); |
| `IPartingSurfaceFeatureData.AccessSelections` | `api-08-mold-costing` | GetSelectedObject6(1,-1) → swFeature.GetDefinition() → AccessSelections(swModel, null) → 改属性 → swFeature.ModifyDefinition(data, swModel, null)。 |
| `IPartingSurfaceFeatureData.GetPartingLinesCount` | `api-08-mold-costing` | Debug.Print("    Number of parting lines: " + swPartingSurfaceFeatureData.GetPartingLinesCount()); |
| `IPartingSurfaceFeatureData.GetPartingLinesType` | `api-08-mold-costing` | Debug.Print("    Parting line type (0 = parting line feature, 1 = edge): " + swPartingSurfaceFeatureData.GetPartingLinesType()); |
| `IPartingSurfaceFeatureData.Knit` | `api-08-mold-costing` | Debug.Print("    Knit all surfaces: " + swPartingSurfaceFeatureData.Knit); |
| `IPartingSurfaceFeatureData.OffsetAngle` | `api-08-mold-costing` | 官方例子按 PartingType 分支：为 Perpendicular 时打印不可用，否则打印 swPartingSurfaceFeatureData.OffsetAngle。 |
| `IPartingSurfaceFeatureData.OffsetDistance` | `api-08-mold-costing` | Debug.Print("    Distance this parting surface feature extends: " + swPartingSurfaceFeatureData.OffsetDistance); |
| `IPartingSurfaceFeatureData.PartingType` | `api-08-mold-costing` | Debug.Print("    Parting surface type as defined by swPartingSurfaceMoldParmType_e: " + swPartingSurfaceFeatureData.PartingType); |
| `IPartingSurfaceFeatureData.ReverseAlignment` | `api-08-mold-costing` | 官方例子读 ReverseAlignment 后取反写回（为 true 则置 false，否则置 true）。 |
| `IPartingSurfaceFeatureData.TransitionType` | `api-08-mold-costing` | Debug.Print("    Transition between adjacent edges as defined by swPartingSurfaceSmoothingType_e: " + ...TransitionType); |
| `IPDMDocManager.SetDocumentStatus` | `api-10-routing-pdm-anim` | 传 swPDMStatus_e.swPDMStatusKnownAndAvailable（=2）；[D] 原话：传别的状态值 Toolbox Browser 会报错并中止文件拖放。 |
| `IPDMDocManager.SetManagedDocument` | `api-10-routing-pdm-anim` | 传 PDM 受管版本文档的路径名；若该路径不可写，就改传一份 SolidWorks Toolbox Browser 可写的受管文档副本。 |
| `IRoutingSettings.GetRoutingUserPreferenceDoubleValue` | `api-10-routing-pdm-anim` | 传 swUserPreferenceRoutingDouble_e.swSlackPercentage 或 .swTextSizeForConnectionAndRoutePoints（成员与数值抄不到）。 |
| `IRoutingSettings.GetRoutingUserPreferenceIntegerValue` | `api-10-routing-pdm-anim` | 传 swUserPreferenceRoutingInteger_e.swComponentRotationIncrementDegrees 或 .swEnableMinimumBendRadiusChecks（枚举成员与数值抄不到）。 |
| `IRoutingSettings.GetRoutingUserPreferenceStringValue` | `api-10-routing-pdm-anim` | 例子对 10 个库路径项一律写成 (swUserPreferenceRoutingFileLocations_e.xxx, True)，第二个实参 UseDefaultVal 恒为 True。 |
| `IRoutingSettings.GetRoutingUserPreferenceToggle` | `api-10-routing-pdm-anim` | 例子逐个读 15 个 toggle 项，形如 GetRoutingUserPreferenceToggle(swUserPreferenceRoutingToggle_e.swEnableRouteErrorChecking)（枚举成员与数值抄不到）。 |
| `IRoutingSettings.SaveRoutingSettingsToFile` | `api-10-routing-pdm-anim` | 先 GetRoutingSettings，再 SaveRoutingSettingsToFile("c:\temp\routingSettings.sqy")；参数表写文件名扩展名必须是 .sqy，例子的 Preconditions 还要求 c:\temp 存在。 |
| `ISketch.AutoDimension2` | `api-07-sketch` | Select3(True, swAutodimMarkHorizontalDatum, Nothing) + Select3(True, swAutodimMarkVerticalDatum, Nothing) → AutoDimension2(swAutodimEntitiesAll, Baseline, Below, Baseline, Left)。 |
| `ISketch.CheckFeatureUse` | `api-07-sketch` | For i = 0 To 22: CheckFeatureUse(i, nOpenCount, nClosedCount)。 |
| `ISketch.GetArcCount` | `api-07-sketch` | NumArcs = swSketch.GetArcCount → vArcs = swSketch.GetArcs2（每弧 16 个 double）。 |
| `ISketch.GetArcs2` | `api-07-sketch` | NumArcs = GetArcCount → vArcs = GetArcs2 → Debug.Assert UBound(vArcs)+1 = 16*NumArcs。 |
| `ISketch.GetEllipseCount` | `api-07-sketch` | Write #1, " Number of ellipses = " & CStr(swSketch.GetEllipseCount())。 |
| `ISketch.GetLineCount2` | `api-07-sketch` | GetLineCount2(1)（1 = 排除剖面线）→ GetLines2(1)，每线 12 个 double。 |
| `ISketch.GetLines2` | `api-07-sketch` | NumLines = swSketch.GetLineCount2(1) → vLines = swSketch.GetLines2(1)。 |
| `ISketch.GetParabolaCount` | `api-07-sketch` | Write #1, " Number of parabolas = " & CStr(swSketch.GetParabolaCount())。 |
| `ISketch.GetReferenceEntity` | `api-07-sketch` | swFeat.GetParents 找 ProfileFeature → swSketch.GetReferenceEntity(longstatus)（VBA 传 ByRef 变量）。 |
| `ISketch.GetSketchPaths` | `api-07-sketch` | bRet = MakeSketchChain → ClearSelection2(True) → vSketchPath = GetSketchPaths。 |
| `ISketch.GetSketchPointsCount2` | `api-07-sketch` | pSwSketch->GetSketchPointsCount2(&nbrSketchPoints); long splineArraySize = 1 + (nbrSketchPoints * 3); |
| `ISketch.GetSketchSegments` | `api-07-sketch` | vSketchSeg = GetSketchSegments → 遍历数组逐个 Select4(True, swSelData)。 |
| `ISketch.GetSplineCount` | `api-07-sketch` | splineCount = swSketch.GetSplineCount(splinePointCount) → 逐条 GetSplineParams5(True, i - 1)。 |
| `ISketch.GetSplineParams4` | `api-07-sketch` | GetSplineParams4(True) 返回 SplineParamData，再逐属性读并 GetControlPoints / GetKnotPoints。 |
| `ISketch.GetSplineParams5` | `api-07-sketch` | 先 GetSplineCount 拿条数，再逐条 GetSplineParams5(True, i - 1)（Index 是 0-based）。 |
| `ISketch.GetSplinesInterpolate` | `api-07-sketch` | pSwSketch->GetSplinesInterpolate(&vSplines)；数组大小 = 1 + n * 3。 |
| `ISketch.GetUserPointsCount` | `api-07-sketch` | Write #1, " Number of points = " & CStr(swSketch.GetUserPointsCount())。 |
| `ISketch.IEnumSketchSegments` | `api-07-sketch` | IEnumSketchSegments → 循环 Next(1, &pSketchSegment, &skReturned) → pSketchSegment->Select(TRUE, &ok)。 |
| `ISketch.InsertRouteLine` | `api-07-sketch` | 按序 SelectByID2("","FACE",…) 取面放进 itemsToConnect(0..n-1)，另三个布尔数组逐项填 False，再 InsertRouteLine。 |
| `ISketch.SetWorkingPlaneOrientation` | `api-07-sketch` | SetWorkingPlaneOrientation(0,0,0, 0,1,0, 0,0,1, 1,0,0)（原点 + X 轴 + Y 轴 + 法向）。 |
| `ISketchManager.ActiveSketch` | `api-07-sketch` | CreateCenterLine 后取 swSketchManager.ActiveSketch，紧接着 SetWorkingPlaneOrientation(0,0,0,0,1,0,0,0,1,1,0,0)。 |
| `ISketchManager.AddAlongXDimension` | `api-07-sketch` | Insert3DSketch True → CreateCornerRectangle / CreateSpline2 → InsertSketch True → AddAlongXDimension(0.05, -0.091, 0.001)。 |
| `ISketchManager.AddToDB` | `api-07-sketch` | AddToDB=True → 造几何 → AddToDB=False → GraphicsRedraw2。 |
| `ISketchManager.CreateCenterLine` | `api-07-sketch` | 先 Insert3DSketch True 进 3D 草图，再 CreateCenterLine(-0.082642, 0.005659, 0#, -0.049926, 0.045073, 0#)。 |
| `ISketchManager.CreateCircle` | `api-07-sketch` | CreateCircle(0#, 0#, 0#, 0.045549, 0.013926, 0#)（圆心 + 圆上一点，6 个 double）。 |
| `ISketchManager.CreateCircularSketchStepAndRepeat` | `api-07-sketch` | 先 CreateCircle + CreateCornerRectangle 造实体，再调用 (0.03184378021964, 4.732863934409, 4, 1.570796326795, True, "", True, True, True)。 |
| `ISketchManager.CreateConic` | `api-07-sketch` | CreateConic(0.109436, 0.080614, 0#, 0.048742, 0.022907, 0#, -0.017812, 0#, 0#, -0.006092, -0.069601, 0#)。 |
| `ISketchManager.CreateCornerRectangle` | `api-07-sketch` | 传左上角 + 右下角两点，如 CreateCornerRectangle(-0.005867589431389, 0.03694408160504, 0, 0.004563680668858, 0.02673012963188, 0)。 |
| `ISketchManager.CreateEquationSpline2` | `api-07-sketch` | InsertSketch True → CreateEquationSpline2("", "sin(x)", "", "0", "6.28", False, 0, 0, 0, True, True) → InsertSketch True。 |
| `ISketchManager.CreateFillet` | `api-07-sketch` | CreateFillet(0.01, swConstrainedCornerAction_e.swConstrainedCornerDeleteGeometry)。 |
| `ISketchManager.CreateLine` | `api-07-sketch` | InsertSketch True → SelectByID2("Top Plane","PLANE",…) → ClearSelection2 True → CreateLine 两点坐标。 |
| `ISketchManager.CreateLinearSketchStepAndRepeat` | `api-07-sketch` | (2, 2, 0.0254, 0.0254, 0.296705972839, 1.134464013796, "", True, True, False, True, True)。 |
| `ISketchManager.CreatePoint` | `api-07-sketch` | AddToDB=True → CreatePoint(X,Y,Z) 建 4 个点 → AddToDB=False。 |
| `ISketchManager.CreateSketchPlane` | `api-07-sketch` | SelectByID2(…, Append=True, Mark=0) 选两个实体 → CreateSketchPlane(9, 9, 0)。 |
| `ISketchManager.CreateSketchSlot` | `api-07-sketch` | CreateSketchSlot(swSketchSlotCreationType_line, swSketchSlotLengthType_CenterCenter, 0.05, -0.05,0,0, 0.05,0,0, 0,0,0, 1, False)。 |
| `ISketchManager.CreateSpline` | `api-07-sketch` | Dim points(11) As Double（12 个 = 4 个 XYZ）→ pointArray = points → CreateSpline((pointArray))。 |
| `ISketchManager.CreateSpline2` | `api-07-sketch` | ReDim points(0 To 11) As Double → CreateSpline2((pointArray), True)。 |
| `ISketchManager.CreateSpline3` | `api-07-sketch` | SelectByRay 选面 → GetSurface → CreateSpline3((pointArray), surfs, Nothing, True, statuses) → InsertSketch True。 |
| `ISketchManager.CreateSplineParamData` | `api-07-sketch` | 设 Dimension=3 / Order=4 / Periodic=0 / ControlPointsCount=6 → SetControlPoints → SetKnotPoints → CreateSplinesByEqnParams2。 |
| `ISketchManager.CreateSplinesByEqnParams2` | `api-07-sketch` | CreateSplineParamData 造好 ParamData → CreateSplinesByEqnParams2(swSplineParaData) → InsertSketch (True)。 |
| `ISketchManager.EditCircularSketchStepAndRepeat` | `api-07-sketch` | EditCircularSketchStepAndRepeat(0.03184378021964, 4.732863934409, 3, 1.570796326795, True, "", True, True, True, "Line2_Line1_Line4_Line3_")。 |
| `ISketchManager.EditLinearSketchStepAndRepeat` | `api-07-sketch` | (3, 2, 0.0254, 0.0254, 0.296705972839, 1.134464013796, "", False, False, False, True, True, "Line2_Line1_Line4_")。 |
| `ISketchManager.Insert3DSketch` | `api-07-sketch` | 官方例子里既当开始（造几何之前 Insert3DSketch True）也当结束（SplitOpenSegment 之后）。 |
| `ISketchManager.InsertExplodeLineSketch` | `api-07-sketch` | AutoExplode → EditRebuild3 → InsertExplodeLineSketch（开）… 结尾再调一次（关）。 |
| `ISketchManager.InsertSketch` | `api-07-sketch` | 开头、结尾各一次 InsertSketch True；CreateSpline3 的 Remarks 明写调它 finalize 草图。 |
| `ISketchManager.InsertSketchBlockInstance` | `api-07-sketch` | Position 由 swMathUtil.CreatePoint 造 → InsertSketchBlockInstance(swSketchBlockDef, swMathPoint, 1, 0)。 |
| `ISketchManager.InsertSketchPicture2` | `api-07-sketch` | InsertSketch True → InsertSketchPicture2("c:\temp\image_file", False) → InsertSketch True。 |
| `ISketchManager.MakeSketchBlockFromSelected` | `api-07-sketch` | MultiSelect2(vSkSeg / vSkPt / vSkNote, True, Nothing) → MakeSketchBlockFromSelected(Nothing)。 |
| `ISketchManager.MakeSketchChain` | `api-07-sketch` | SelectByID2 选草图 → EditSketch → 各段 Select4 True, Nothing → MakeSketchChain。 |
| `ISketchManager.RotateOrCopy3DAboutXYZ` | `api-07-sketch` | (True, 1, True, -0.09925811702374, 0.004131001848179, 0, 1.5707963267949, 0, 0)。 |
| `ISketchManager.SetDynamicMirror` | `api-07-sketch` | SetDynamicMirror (True)。 |
| `ISketchManager.SketchExtend` | `api-07-sketch` | SketchExtend(0#, 0#, 0#)。 |
| `ISketchManager.SketchOffset2` | `api-07-sketch` | SketchOffset2(0.00254, True, True, swSkOffsetArcCaps, swSkOffsetMakeBothConstruction, True)。 |
| `ISketchManager.SplitClosedSegment` | `api-07-sketch` | InsertSketch True → CreateSpline((pointArray)) → SplitClosedSegment(两点坐标) → Insert3DSketch True。 |
| `ISketchManager.SplitOpenSegment` | `api-07-sketch` | InsertSketch True → CreateLine → SplitOpenSegment(0.02, 0.01, 0#)。 |
| `ISldWorks.GetRoutingSettings` | `api-10-routing-pdm-anim` | 例子：Set swApp = Application.SldWorks 后 Set routingSettings = swApp.GetRoutingSettings，紧接着用同一对象调 SaveRoutingSettingsToFile("c:\temp\routingSettings.sqy")；例子的 Preconditions 要求先在 Tools > Add-Ins 里选中 SOLIDWORKS Routing 并引用 Routing 类型库。 |

### 2.3 「查不到的」—— 别再去找了

★ 共 **748** 条「查不到」条目，涉及 **545** 个（源, 成员）组合。
★ 官方两套离线源都没有的，**再花时间也是 0 命中**，直接按查不到处理。

#### `api-01-surface.md`（69 条）

| 成员 | 查不到的是什么 |
|---|---|
| `IFeatureManager.FeatureCutThicken` | ## Examples 段与官方例子调用序（examples 全目录 0 命中） |
| `IFeatureManager.FeatureCutThicken` | Direction 的枚举名（只有内联 0/1/2） |
| `IFeatureManager.FeatureCutThicken` | selection mark 取值（Remarks 未写） |
| `IFeatureManager.GetPreTrimmedBodies` | ## Examples 段与官方例子调用序 |
| `IFeatureManager.GetPreTrimmedBodies` | ## Remarks 段（md 与 CHM 都没有） |
| `IFeatureManager.GetPreTrimmedBodies` | 该成员点名的枚举与官方写的前置 |
| `IFeatureManager.InsertFillSurface` | ## Examples 段与官方例子调用序 |
| `IFeatureManager.InsertFillSurface` | ## Remarks 段 |
| `IFeatureManager.InsertFillSurface` | 该成员点名的枚举（签名只有 System.int Resolution） |
| `IFeatureManager.InsertFillSurface` | Resolution 的说明与取值 |
| `IFeatureManager.InsertSewRefSurface` | 该成员点名的枚举（5 个形参全非枚举类型） |
| `IFeatureManager.InsertSweepSurface` | ## Examples 段与官方例子调用序 |
| `IFeatureManager.InsertSweepSurface` | ## Remarks 段（md 与 CHM 都没有） |
| `IFeatureManager.InsertSweepSurface` | 该成员自身点名的枚举 |
| `IFeatureManager.InsertSweepSurface` | 全部 7 个形参的说明（页面写 No description） |
| `IFeatureManager.InsertSweepSurface2` | ## Examples 段与官方例子调用序 |
| `IFeatureManager.InsertSweepSurface2` | PathAlign 的枚举名（只有 Remarks 内联取值 0/2/3） |
| `IFeatureManager.InsertSweepSurface3` | Obsolete 后的后继方法名（官方只给文档章节与 ISweepFeatureData 接口） |
| `IFeatureManager.InsertUntrimSurface` | ## Examples 段与官方例子调用序 |
| `IFeatureManager.InsertUntrimSurface2` | C:\swapi\types 侧的 ## Examples（例子只在 CHM 页） |
| `IFeatureManager.InsertUntrimSurface2` | swContactType_e 是否在这条签名里 |
| `IFeatureManager.PostTrimSurface` | 该成员点名的枚举（唯一形参是 bool） |
| `IFeatureManager.PreTrimSurface` | 该成员点名的枚举（4 个形参全是 bool） |
| `IFeatureManager.SetFreeformBoundaryContinuity` | ## Examples 段（examples 全目录 0 命中） |
| `IFeatureManager.SetFreeformBoundaryContinuity` | Continuity 的枚举名（只有内联 -1/0/1/2） |
| `IFeatureManager.SolidForTrim` | 该成员点名的枚举（属性类型是 bool） |
| `IFeatureManager（目录整体）` | 没有名字含 Knit 的成员；Knit 特征入口是 InsertSewRefSurface |
| `IModeler.CreateBsplineSurface` | ## Examples 段（examples 全目录 0 命中） |
| `IModeler.CreateBsplineSurface` | 该成员点名的枚举（4 个形参全是 object） |
| `IModeler.CreateConicalSurface` | ## Examples 段与官方例子调用序（examples 0 命中） |
| `IModeler.CreateConicalSurface` | ## Remarks 段 |
| `IModeler.CreateConicalSurface` | ## Returns 段 |
| `IModeler.CreateConicalSurface` | 全部 4 个形参的说明（页面写 No description） |
| `IModeler.CreateConicalSurface2` | ## Examples 段与官方例子调用序 |
| `IModeler.CreateConicalSurface2` | RefDirection 的语义（官方那张 Argument 表没有这一行） |
| `IModeler.CreateCoonsBSurface` | ## Examples 段（examples 0 命中） |
| `IModeler.CreateCylindricalSurface` | ## Examples 段与官方例子调用序（examples 0 命中） |
| `IModeler.CreateCylindricalSurface` | ## Remarks 段 |
| `IModeler.CreateCylindricalSurface` | ## Returns 段 |
| `IModeler.CreateCylindricalSurface` | 全部 3 个形参的说明（页面写 No description） |
| `IModeler.CreateCylindricalSurface2` | 本条自己的调用序（唯一挂在 Examples 下的例子调的是 CreateSphericalSurface2） |
| `IModeler.CreateCylindricalSurface2` | RefDirection 的真实语义（官方原文与 Direction 描述完全相同） |
| `IModeler.CreateExtrusionSurface` | IModeler 版的实参（唯一命中的例子走的是 IBody2.ICreateExtrusionSurface） |
| `IModeler.CreateLoftSurface` | ## Examples 段（examples 0 命中） |
| `IModeler.CreateLoftSurface` | ## Remarks 段 |
| `IModeler.CreateLoftSurface` | MATCH_* 的枚举名（只有内联 0..4） |
| `IModeler.CreateOffsetSurface` | ## Examples 段（examples 0 命中） |
| `IModeler.CreateOffsetSurface` | ## Remarks 段 |
| `IModeler.CreateOffsetSurface` | 官方写的前置 |
| `IModeler.CreatePlanarSurface` | ## Examples 段与官方例子调用序 |
| `IModeler.CreatePlanarSurface` | ## Remarks 段 |
| `IModeler.CreatePlanarSurface` | ## Returns 段 |
| `IModeler.CreatePlanarSurface` | 全部 2 个形参的说明（页面写 No description） |
| `IModeler.CreateRuledSurfaceFromEdge` | Type 的枚举名（只有内联 0..4） |
| `IModeler.CreateSphericalSurface` | ## Examples 段与官方例子调用序 |
| `IModeler.CreateSphericalSurface` | ## Remarks 段 |
| `IModeler.CreateSphericalSurface` | ## Returns 段 |
| `IModeler.CreateSphericalSurface` | 全部 2 个形参的说明（页面写 No description） |
| `IModeler.CreateSweptSurface` | ## Examples 段（examples 0 命中） |
| `IModeler.CreateToroidalSurface` | ## Examples 段（examples 0 命中） |
| `IModeler.GetInitKnitGapWidth` | ## Examples 段（examples 0 命中） |
| `IModeler.MakeManifoldBodies` | ## Remarks 段 |
| `IModeler.MakeManifoldBodies` | 官方例子的实参（只抄到例子名，未读正文） |
| `IModeler.ReplaceSurfaces` | ## Examples 段（examples 0 命中） |
| `IModeler.ReplaceSurfaces` | ## Remarks 段 |
| `IModeler.ReplaceSurfaces` | 官方没写 IReplaceSurfaces2 是它的后继（废弃链查不到） |
| `IModeler.SetInitKnitGapWidth` | ## Examples 段（examples 0 命中） |
| `IModeler.ThickenSheet` | selection mark 取值（该页与该例都没写 mark） |
| `IModeler（整个接口）` | CHM 解包里没有 IModeler 的任何一页（文件名与内容双向确认） |

#### `api-03-weldment.md`（58 条）

| 成员 | 查不到的是什么 |
|---|---|
| `CreateStructuralMemberGroup` | 例中出现的 swMirrorProfileOrAlignmentAxis_Vertical 数值查不到：其枚举文件本轮未读 |
| `CreateStructuralMemberGroup` | Remarks 段查不到：md 文件没有该段，chm-api 也没有 |
| `CutListFolderLocation` | 官方例子调用序查不到：md 没有 Examples 段 |
| `CutListFolderLocation` | 后继查不到：该成员未被标 Obsolete |
| `GetPreTrimmedBodies` | 官方例子调用序查不到：md 没有 Examples 段 |
| `GetPreTrimmedBodies` | 后继查不到：该成员未被标 Obsolete |
| `GetPreTrimmedBodies` | Remarks 段查不到：md 文件没有该段，chm-api 也没有 |
| `IFeatureManager.*WeldSymbol*` | IFeatureManager 下含 WeldSymbol 的成员名字缺席；swapi 全量文件名表里无 Symbol 子串 |
| `InsertCosmeticWeldBead` | 逐字调用序查不到：Examples 列的 3 个例子文件本轮未读 |
| `InsertCosmeticWeldBead2` | 后继查不到：该成员未被标 Obsolete |
| `InsertEndCapFeature` | 官方例子调用序查不到：md 没有 Examples 段 |
| `InsertEndCapFeature` | Remarks 段查不到：md 文件没有该段，chm-api 也没有 |
| `InsertEndCapFeature2` | 后继查不到：该成员未被标 Obsolete |
| `InsertEndCapFeature3` | 官方 Remarks 的 mark 数字查不到：只说在图形区 select one or more end faces，未点数字 |
| `InsertEndCapFeature3` | 后继查不到：该成员未被标 Obsolete |
| `InsertFilletBeadFeature` | 官方例子调用序查不到：md 没有 Examples 段 |
| `InsertFilletBeadFeature` | Remarks 段查不到：md 文件没有该段，chm-api 也没有 |
| `InsertFilletBeadFeature2` | 官方例子调用序查不到：md 没有 Examples 段 |
| `InsertFilletBeadFeature2` | 后继查不到：该成员未被标 Obsolete |
| `InsertFilletBeadFeature2` | Remarks 段查不到：md 文件没有该段，chm-api 也没有 |
| `InsertFilletBeadFeature3` | 后继查不到：该成员未被标 Obsolete |
| `InsertGussetFeature` | 官方例子调用序查不到：md 没有 Examples 段 |
| `InsertGussetFeature` | Remarks 段查不到：md 文件没有该段，chm-api 也没有 |
| `InsertGussetFeature2` | 后继查不到：该成员未被标 Obsolete |
| `InsertGussetFeature3` | 后继查不到：该成员未被标 Obsolete |
| `InsertSheetMetalCornerTrim` | 官方例子调用序查不到：md 没有 Examples 段 |
| `InsertSheetMetalCornerTrim` | 后继查不到：该成员未被标 Obsolete |
| `InsertSheetMetalCornerTrim` | Remarks 段查不到：md 文件没有该段 |
| `InsertStructuralWeldment` | 官方例子调用序查不到：md 没有 Examples 段 |
| `InsertStructuralWeldment` | 形参 EndCond 对应哪个枚举查不到：其 Parameters 三行全写 No description |
| `InsertStructuralWeldment` | Remarks 段查不到：md 文件没有该段，chm-api 也没有 |
| `InsertStructuralWeldment2` | 官方例子调用序查不到：md 没有 Examples 段 |
| `InsertStructuralWeldment2` | Remarks 段查不到：md 文件没有该段，chm-api 也没有 |
| `InsertStructuralWeldment3` | Parameters 里 EndCond 写成全大写枚举 swSOLIDWORKSWeldmentEndCondOptions_e，该拼法本机查不到 |
| `InsertStructuralWeldment5` | 后继查不到：该成员未被标 Obsolete |
| `InsertStructuralWeldment5` | 逐字调用序查不到：其 Examples 指向的 3 个 Custom-Profile 例子文件本轮未读 |
| `InsertSubWeldFolder` | 官方例子调用序查不到：md 没有 Examples 段 |
| `InsertSubWeldFolder` | 后继查不到：它本身没标 Obsolete（See Also 只指向 2） |
| `InsertSubWeldFolder2` | 后继查不到：该成员未被标 Obsolete |
| `InsertSubWeldFolder2` | Remarks 段查不到：md 文件没有该段 |
| `InsertUntrimSurface` | 官方例子调用序查不到：md 没有 Examples 段 |
| `InsertUntrimSurface2` | 官方例子调用序查不到：md 没有 Examples 段 |
| `InsertUntrimSurface2` | 后继查不到：该成员未被标 Obsolete |
| `InsertWeldmentCutList` | 官方例子调用序查不到：md 没有 Examples 段 |
| `InsertWeldmentCutList` | Remarks 段查不到：md 文件没有该段 |
| `InsertWeldmentCutList2` | 后继查不到：该成员未被标 Obsolete |
| `InsertWeldmentCutList2` | Remarks 段查不到：md 文件没有该段 |
| `InsertWeldmentFeature` | Remarks 段查不到：md 文件没有该段 |
| `InsertWeldmentTrimFeature` | 官方例子调用序查不到：md 没有 Examples 段 |
| `InsertWeldmentTrimFeature` | 后继查不到：该成员未被标 Obsolete |
| `InsertWeldmentTrimFeature2` | 后继查不到：该成员未被标 Obsolete |
| `PostTrimSurface` | 后继查不到：该成员未被标 Obsolete |
| `PostTrimSurface` | 逐字调用序查不到：其例子文件本轮未读 |
| `PreTrimSurface` | 后继查不到：该成员未被标 Obsolete |
| `PreTrimSurface` | 逐字调用序查不到：Examples 列的 6 个例子文件本轮未读 |
| `SolidForTrim` | 后继查不到：该成员未被标 Obsolete |
| `SolidForTrim` | 逐字调用序查不到：Examples 列的例子文件本轮未读 |
| `swSOLIDWORKSWeldmentEndCondOptions_e` | 全大写拼法的枚举文件查不到；本机只有 swSolidworksWeldmentEndCondOptions_e |

#### `api-04-assembly.md`（279 条）

| 成员 | 查不到的是什么 |
|---|---|
| `AddConcentricMateWithTolerance` | Add_and_Edit_Misaligned_Symmetric_Concentric_Mate_Example_VB.md 未逐字读 ⇒ 调用序查不到 |
| `AddConcentricMateWithTolerance` | swConcentricAlignmentType_e 的数值查不到（enums 无对应文件） |
| `AddDistanceMate` | Add_Distance_Mates / Create_Limit_Distance_Mate / Add_and_Edit_Distance_Mate 三个例子未逐字读 ⇒ 调用序查不到 |
| `AddMate` | ## Remarks 段为空，查不到 |
| `AddMate` | 本页未点名枚举 ⇒ 成员层面的 swMateType_e / swMateAlign_e 关联查不到 |
| `AddMate` | 官方例子调用序查不到 |
| `AddMate2` | ## Remarks 段为空，查不到 |
| `AddMate2` | 官方例子调用序查不到 |
| `AddMate2` | 枚举关联属形参名推断，本成员页面自身未在 Remarks 里点名枚举 |
| `AddMate3` | 官方例子调用序查不到 |
| `AddMate4` | 官方例子调用序查不到 |
| `AddMate5` | 官方例子目录有 Create_Standard_Mates / Create_Symmetric_Mate / Create_Width_Mate / Create_Limit_Angle_Mate / Rack_and_Pinion_Mate 等，本轮未逐字读 ⇒ 逐字调用序查不到 |
| `api-04-assembly 域 29 个例子文件（§9 第 9 条列举）` | 例子文件存在但本轮未逐字读其代码 ⇒ 调用序标查不到，而不是「该成员无例子」 |
| `api-04-assembly 域 88 个 IAssemblyDoc 成员（§9 第 10 条列举）` | 本轮未逐条抄，其 ②③④⑤ 一律查不到（签名只在本轮批量清单里见过名字） |
| `api-04-assembly 域多个成员（§9 第 8 条列举）` | 官方例子本轮逐字读过并确认不含该调用 ⇒ 其调用序查不到 |
| `api-04-assembly 域全部成员` | CHM 解包 sldworksapi 目录下 AddMate5_Method / IToolsCheckInterference3_Method / CreateExplodedView_Method / SetSuppression2_Method / ExplodeStep_Property 五个 .htm 全部不存在 ⇒ 说明与 See Also 查不到 |
| `AutoExplode` | 官方例子查不到：Create_Exploded_Views_Example_VB.md 全文只调 CreateExplodedView |
| `AutoExplode` | 枚举查不到（无枚举形参） |
| `AutoMateRepair` | Repair_Mates_Missing_Same_Mate_Entity_Example_VB.md 未逐字读 ⇒ 调用序查不到 |
| `AutoMateRepair` | swAutoMateRepairErrors_e 文件存在但本轮未逐字读数值 ⇒ 数值查不到 |
| `AutoSpaceComponentsOnDrag` | 官方例子调用序查不到 |
| `AutoSpaceComponentsOnDrag` | 枚举查不到 |
| `ClearanceVerificationManager` | ## Remarks 段为空，查不到 |
| `ClearanceVerificationManager` | 官方例子调用序查不到 |
| `ClearanceVerificationManager` | 签名只写 System.object、未给接口名 ⇒ 实际返回类型查不到 |
| `CollectAllSupportiveMates` | Create_Mate_Controller_Example_VB.md / _CSharp.md 未逐字读 ⇒ 调用序查不到 |
| `CreateExplodedView` | 签名无枚举形参；官方例子里的 GetExplodedViewCount / GetExplodedViewNames 均已 Obsolete，枚举口径查不到 |
| `CreateFastenersFolder` | CreateFastenersFolder_Example_VB.md 不存在 ⇒ 官方例子查不到 |
| `CreateMate` | 未逐字读 Create_Standard_Mates_Example_VB.md 等 ⇒ 官方例子调用序查不到 |
| `CreateMateData` | 官方例子调用序查不到 |
| `CreateMateData` | swMateType_e 的 7 个成员（COORDINATE / LOCKTOSKETCH / MAGNETIC / MAXMATES / PATH / SLIDER / UNKNOWN）在本方法里查不到 |
| `DissolveComponentPattern` | ## Remarks 段为空 ⇒ 选什么、mark 多少查不到 |
| `DissolveComponentPattern` | 本仓 examples 目录按 Pattern 过滤无阵列相关例子 ⇒ 调用序查不到 |
| `DissolveComponentPattern` | 枚举查不到 |
| `DivergeDirection` | 官方例子里没有出现 Diverge 字样 ⇒ 调用序查不到 |
| `DivergeDirection` | swAssemblyExplodeStepType_e.swAssemblyExplodeStepType_Radial 的数值查不到 |
| `DivergeFromAxis` | 官方例子调用序查不到 |
| `DivergeFromAxis` | swAssemblyExplodeStepType_e 的数值查不到 |
| `Done` | ## Remarks 为空，查不到 |
| `Done` | 官方例子查不到 |
| `EditConcentricMate` | Add_and_Edit_Misaligned_Symmetric_Concentric_Mate_Example_VB.md 未逐字读 ⇒ 调用序查不到 |
| `EditConcentricMate` | swConcentricAlignmentType_e 的数值查不到（枚举文件不存在） |
| `EditDistanceMate` | 官方例子调用序查不到 |
| `EditMate` | ## Remarks 段为空，查不到 |
| `EditMate` | 本页未点名枚举 ⇒ 成员层面关联查不到 |
| `EditMate` | 官方例子调用序查不到 |
| `EditMate2` | 官方例子调用序查不到 |
| `EditMate3` | 官方例子调用序查不到 |
| `EditMate4` | 官方 Obsolete 行未点名单一后继成员，只指向各配合 feature data 接口的 Remarks |
| `EditMate4` | Edit_Mate / Edit_Mate_Reference / Repair_Mates_Missing_Same_Mate_Entity 三个例子未逐字读 ⇒ 调用序查不到 |
| `ExplodeDistance` | ## Remarks 段为空，查不到 |
| `ExplodeDistance` | 枚举查不到 |
| `ExplodeDistance` | Get_Explode_Step_Example_VB.md 只打印 Name / GetNumOfComponents / IsSubAssemblyRigid，未读 ExplodeDistance ⇒ 调用序查不到 |
| `ExplodeStepType` | ## Remarks 段为空，查不到 |
| `ExplodeStepType` | 返回枚举 swAssemblyExplodeStepType_e 的数值查不到（enums 目录逐字 grep 零命中） |
| `ExplodeStepType` | 官方例子未读本属性 ⇒ 调用序查不到 |
| `ExportResults` | 官方例子调用序查不到 |
| `GetComponent` | 官方例子只调 GetNumOfComponents，未调 GetComponent ⇒ 调用序查不到 |
| `GetComponent` | 枚举查不到 |
| `GetComponentName` | 官方例子未调本成员 ⇒ 调用序查不到 |
| `GetComponentName` | 枚举查不到 |
| `GetComponents` | ## Remarks 段为空，查不到 |
| `GetComponents` | 官方例子调用序查不到 |
| `GetComponents` | 枚举查不到 |
| `GetComponentsAndTransforms` | ## Remarks 为空，查不到 |
| `GetComponentsAndTransforms` | 官方例子查不到 |
| `GetComponentsTransformInterference` | ## Remarks 为空，查不到 |
| `GetComponentsTransformInterference` | Detect_Interferences_Using_a_Transform_Example_VB.md 未逐字读 ⇒ 调用序查不到 |
| `GetComponentsTransformInterferenceCount` | 官方例子调用序查不到 |
| `GetComponentXform` | ## Remarks 段为空，查不到 |
| `GetComponentXform` | 官方例子未调本成员 ⇒ 调用序查不到 |
| `GetComponentXform` | 枚举查不到 |
| `GetExplodeDirection` | 官方例子调用序查不到 |
| `GetExplodedViewConfigurationName` | ## Remarks 段为空，查不到 |
| `GetExplodedViewConfigurationName` | 官方例子未调本成员，调用序查不到 |
| `GetExplodedViewConfigurationName` | 枚举查不到 |
| `GetExplodedViewCount` | 枚举查不到（未抄） |
| `GetExplodedViewCount` | 签名与 ## Remarks 本轮未逐字抄 ⇒ 查不到 |
| `GetExplodedViewCount2` | ## Remarks 段为空，查不到 |
| `GetExplodedViewCount2` | 带 2 的版本在官方例子中查不到（例子用的是旧名 GetExplodedViewCount） |
| `GetExplodedViewNames` | 枚举查不到（未抄） |
| `GetExplodedViewNames` | 签名与 ## Remarks 本轮未逐字抄 ⇒ 查不到 |
| `GetExplodedViewNames2` | ## Remarks 段为空，查不到 |
| `GetExplodedViewNames2` | 官方例子用的是旧名 GetExplodedViewNames，带 2 的调用序查不到 |
| `GetInterferenceComponentCount` | 官方例子调用序查不到 |
| `GetInterferenceComponents` | ## Remarks 为空，查不到 |
| `GetInterferenceComponents` | 官方例子查不到 |
| `GetInterferenceCount` | 官方例子调用序查不到 |
| `GetInterferences` | ## Remarks 为空，查不到 |
| `GetInterferences` | 官方例子查不到 |
| `GetLightWeightComponentCount` | ## Remarks 段为空，查不到 |
| `GetLightWeightComponentCount` | 官方例子调用序查不到 |
| `GetLightWeightComponentCount` | 枚举查不到 |
| `GetNumOfComponents` | ## Remarks 段为空，查不到 |
| `GetNumOfComponents` | 枚举查不到 |
| `GetRotationAxis` | 官方例子调用序查不到 |
| `GetRotationAxis` | out 形参 RotAxisIndex 对应的枚举名与数值查不到（enums 无对应文件） |
| `GetSpecificComponentXForm` | 官方例子调用序查不到 |
| `GetSpecificComponentXForm` | 枚举查不到 |
| `GetSubAssemblyExplodeSteps` | 官方例子调用序查不到 |
| `GetSubAssemblyExplodeSteps` | swAssemblyExplodeStepType_e.swAssemblyExplodeStepType_SubAssembly 的数值查不到 |
| `IAssemblyDoc.GetPhysicalSimulationComponents` | 官方 Obsolete 行写 Not superseded（无后继） |
| `IAssemblyDoc.GetSimulation` | 官方 Obsolete 行写 Not superseded（无后继） |
| `IAssemblyDoc.GetUnloadedComponentNames` | 4 个 out 数组（路径名/引用配置名/卸载原因/文档类型）的枚举口径查不到 |
| `IAssemblyDoc.GetUnloadedComponentNames` | 本轮未逐字读该例代码 ⇒ 调用序查不到 |
| `IAssemblyDoc.HasUnloadedComponents` | ## Remarks 段为空，查不到（仅由 GetUnloadedComponentNames 的 Remarks 反向点名） |
| `IAssemblyDoc.HasUnloadedComponents` | 两个相关例子文件名指向本主题但本轮未逐字读代码 ⇒ 调用序查不到 |
| `IAssemblyDoc.HasUnloadedComponents` | 枚举查不到 |
| `IComponent2.CustomPropertyManager` | 该文件无 **Signature** 行 ⇒ 签名查不到 |
| `IComponent2.GetHiddenUnloadedChildrenCount` | 官方例子调用序查不到 |
| `IComponent2.GetHiddenUnloadedChildrenCount` | 枚举查不到 |
| `IComponent2.GetMates` | Get_Mates_Example_VB.md 未逐字读 ⇒ 调用序查不到 |
| `IComponent2.GetSpecificTransform` | ## Remarks 为空，查不到 |
| `IComponent2.GetSpecificTransform` | 官方例子调用序查不到 |
| `IComponent2.GetSuppression` | 官方例子只调 SetSuppression2 ⇒ 调用序查不到 |
| `IComponent2.GetSuppression2` | 官方例子里没有读 GetSuppression2 的行 ⇒ 只读方向调用序查不到（例子只调 SetSuppression2） |
| `IComponent2.GetTotalTransform` | ## Remarks 为空，查不到 |
| `IComponent2.GetTotalTransform` | Get_Collapsed_Transform_of_Component_in_Exploded_View_Example_VB.md 未逐字读 ⇒ 调用序查不到 |
| `IComponent2.GetUnloadedComponentNames` | 官方例子调用序查不到 |
| `IComponent2.GetUnloadedComponentNames` | 枚举查不到 |
| `IComponent2.HasUnloadedComponents` | ## Remarks 为空，查不到 |
| `IComponent2.HasUnloadedComponents` | 官方例子调用序查不到 |
| `IComponent2.HasUnloadedComponents` | 枚举查不到 |
| `IComponent2.IGetChildrenCount` | 官方例子调用序查不到 |
| `IComponent2.IGetMaterialPropertyValuesForFace` | 出现在 §6.1 批量签名清单但本轮未单独核对其页面 ⇒ 未抄 |
| `IComponent2.IGetTemporaryBodyID` | 出现在 §6.1 批量签名清单但本轮未单独核对其页面 ⇒ 未抄 |
| `IComponent2.IsEnvelope` | 官方例子调用序查不到 |
| `IComponent2.IsGraphicsOnly` | ## Remarks 为空，查不到 |
| `IComponent2.IsGraphicsOnly` | 官方例子调用序查不到 |
| `IComponent2.IsGraphicsOnly` | 枚举查不到 |
| `IComponent2.IsHidden` | 官方例子调用序查不到 |
| `IComponent2.IsHidden` | 无枚举形参，取值含义只由真值表给出 ⇒ 枚举查不到 |
| `IComponent2.IsLoaded` | ## Remarks 为空，查不到 |
| `IComponent2.IsLoaded` | 枚举查不到 |
| `IComponent2.IsLoaded` | 未逐字读 Get_Whether_Components_Are_Loaded_Example_VB.md ⇒ 调用序查不到 |
| `IComponent2.IsPatternInstance` | 官方例子调用序查不到 |
| `IComponent2.IsSuppressed` | 官方例子调用序查不到 |
| `IComponent2.IsSuppressed` | 枚举查不到 |
| `IComponent2.IsVirtual` | 官方例子调用序查不到 |
| `IComponent2.SetSuppression` | ## Remarks 段为空，查不到 |
| `IComponent2.SetSuppression` | 官方例子只调 SetSuppression2 ⇒ 调用序查不到 |
| `IComponent2.SetTransformAndSolve2` | ## Remarks 为空，查不到 |
| `IComponent2.SetTransformAndSolve2` | 官方例子调用序查不到 |
| `IComponent2.SetTransformAndSolve3` | ## Remarks 为空，查不到 |
| `IComponent2.SetTransformAndSolve3` | 官方例子调用序查不到 |
| `IComponent2.SetVisibility` | ## Remarks 为空，查不到 |
| `IComponent2.SetVisibility` | 官方例子调用序查不到 |
| `IComponent2.SetVisibility` | State / Config_opt / Config_names 的枚举名与取值本页未点名 ⇒ 查不到 |
| `IComponent2.Transform2` | 官方例子调用序查不到 |
| `IComponent2.Visible` | 官方例子调用序查不到 |
| `IGetComponent` | 官方例子未调本成员 ⇒ 调用序查不到 |
| `IGetComponent` | 枚举查不到 |
| `IGetComponentsTransformInterference` | 签名行未逐字读、## Remarks 未读 ⇒ 签名与前置查不到（只被 GetComponentsTransformInterferenceCount 点名为先取长度的那一个） |
| `IGetComponentXform` | ## Remarks 段为空，查不到 |
| `IGetComponentXform` | 官方例子调用序查不到 |
| `IGetComponentXform` | 枚举查不到 |
| `IGetInterferenceComponents` | 签名行未逐字读、## Remarks 未读 ⇒ 签名与前置查不到 |
| `IGetInterferences` | 签名行未逐字读、## Remarks 未读 ⇒ 签名与前置查不到 |
| `IgnoreHiddenBodies` | 官方例子调用序查不到 |
| `IMate2.Alignment` | ## Remarks 为空，查不到 |
| `IMate2.Alignment` | 本页未点名 swMateAlign_e ⇒ 成员层面关联查不到 |
| `IMate2.Alignment` | 官方例子调用序查不到 |
| `IMate2.CanBeFlipped` | 官方例子调用序查不到 |
| `IMate2.DisplayDimension` | 枚举查不到（未抄） |
| `IMate2.DisplayDimension` | 签名与 ## Remarks 本轮未读 ⇒ 查不到（未抄） |
| `IMate2.DisplayDimension2` | 官方例子调用序查不到 |
| `IMate2.DisplayDimension2` | types 文件全文 10 行，只有 front-matter 与标题，无 Signature / Remarks / Examples ⇒ 签名与前置查不到（该文件是空壳） |
| `IMate2.DistanceFirstArcCondition` | 本页未点名 swDistanceMateArcConditions_e ⇒ 成员层面关联查不到（全局数值见 §8） |
| `IMate2.DistanceFirstArcCondition` | 官方例子调用序查不到 |
| `IMate2.DistanceSecondArcCondition` | 本页未点名 swDistanceMateArcConditions_e ⇒ 成员层面关联查不到 |
| `IMate2.DistanceSecondArcCondition` | 官方例子调用序查不到 |
| `IMate2.Flipped` | ## Remarks 为空，查不到 |
| `IMate2.Flipped` | 官方例子调用序查不到 |
| `IMate2.ForceMisalignment` | ## Remarks 为空，查不到 |
| `IMate2.ForceMisalignment` | 官方例子调用序查不到 |
| `IMate2.GetConcentricAlignmentType` | ## Remarks 为空，查不到 |
| `IMate2.GetConcentricAlignmentType` | 本页未点名 swConcentricAlignmentType_e ⇒ 成员层面关联查不到（名字只在 SetMaximumMisalignedDeviation 处读到） |
| `IMate2.GetCurrentMisalignedDeviation` | 官方例子调用序查不到 |
| `IMate2.GetForce` | ## Remarks 为空，查不到 |
| `IMate2.GetForce` | 官方例子调用序查不到 |
| `IMate2.GetLinkedMate` | 官方例子调用序查不到 |
| `IMate2.GetMateEntityCount` | Get_Mates_and_Mate_Entities_Example_VB.md 未逐字读 ⇒ 调用序查不到 |
| `IMate2.GetMaximumMisalignedDeviation` | 官方例子调用序查不到 |
| `IMate2.GetSupplementalFaces` | ## Remarks 为空，查不到 |
| `IMate2.GetSupplementalFaces` | 官方例子调用序查不到 |
| `IMate2.GetSupplementalFaces` | WhichOne 的取值枚举查不到 |
| `IMate2.GetTorque` | ## Remarks 为空，查不到 |
| `IMate2.GetTorque` | 官方例子调用序查不到 |
| `IMate2.GetUseMisalignedDeviationDocumentProperty` | 官方例子调用序查不到 |
| `IMate2.HasLoadBearingFaces` | ## Remarks 为空，查不到 |
| `IMate2.HasLoadBearingFaces` | 官方例子调用序查不到 |
| `IMate2.HasTreatInterferenceAsShrinkFit` | ## Remarks 为空，查不到 |
| `IMate2.HasTreatInterferenceAsShrinkFit` | 官方例子调用序查不到 |
| `IMate2.IsLoadBearingFacesBonded` | ## Remarks 为空，查不到 |
| `IMate2.IsLoadBearingFacesBonded` | 官方例子调用序查不到 |
| `IMate2.LockMagneticMate` | 官方例子调用序查不到 |
| `IMate2.MateEntity` | 官方例子调用序查不到 |
| `IMate2.MateLoadReference` | ## Remarks 为空，查不到 |
| `IMate2.MateLoadReference` | Insert_Mate_Load_Reference_Example_VB.md 未逐字读 ⇒ 调用序查不到 |
| `IMate2.MaximumVariation` | 官方例子调用序查不到 |
| `IMate2.MinimumVariation` | 官方例子调用序查不到 |
| `IMate2.RemoveMisalignment` | Add_and_Edit_Misaligned_Symmetric_Concentric_Mate_Example_VB.md 未逐字读 ⇒ 调用序查不到 |
| `IMate2.SetConcentricAlignmentType` | ## Remarks 为空，查不到 |
| `IMate2.SetConcentricAlignmentType` | PositionType 的枚举名与数值查不到（enums 无对应文件） |
| `IMate2.SetForce` | ## Remarks 为空，查不到 |
| `IMate2.SetForce` | 官方例子调用序查不到 |
| `IMate2.SetMaximumMisalignedDeviation` | 官方例子调用序查不到 |
| `IMate2.SetMaximumMisalignedDeviation` | swConcentricAlignmentType_e.swConcentricAlignSymmetric 的数值查不到（enums 无该文件） |
| `IMate2.SetTorque` | ## Remarks 为空，查不到 |
| `IMate2.SetTorque` | 官方例子调用序查不到 |
| `IMate2.SetUseMisalignedDeviationDocumentProperty` | 官方例子调用序查不到 |
| `IMate2.Type` | ## Remarks 为空，查不到 |
| `IMate2.Type` | 官方例子调用序查不到 |
| `IncludeMultibodyPartInterferences` | 官方例子调用序查不到 |
| `InsertDerivedPattern` | 官方 Obsolete 行未点名单一后继成员，只指向 IFeatureManager::CreateFeature 与 IDerivedPatternFeatureData |
| `InsertDerivedPattern` | 官方例子调用序查不到 |
| `InsertDerivedPattern` | 枚举查不到 |
| `InterferenceDetectionManager` | ## Remarks 段为空 ⇒ 取该对象的前置查不到 |
| `InterferenceDetectionManager` | Run_Interference_Detection_Example_VB.md 未逐字读 ⇒ 调用序查不到 |
| `IsSubAssemblyRigid` | 枚举查不到 |
| `IsSubAssemblyRigid` | 柔性/刚性子装配语义外链到 SOLIDWORKS Help，本机该页未查 ⇒ 查不到 |
| `IsSupportedMatesAvailable` | Create_Mate_Controller_Example_VB.md / _CSharp.md 未逐字读 ⇒ 调用序查不到 |
| `IToolsCheckInterference2` | ## Remarks 段为空，查不到 |
| `IToolsCheckInterference2` | 官方例子只调 ToolsCheckInterference2 ⇒ 调用序查不到 |
| `IToolsCheckInterference2` | 枚举查不到 |
| `IToolsCheckInterference3` | 官方 Obsolete 行只有「Obsolete.」，后继查不到 |
| `IToolsCheckInterference3` | 官方例子调用序查不到 |
| `IToolsCheckInterference3` | 枚举查不到 |
| `LightweightAllResolved` | 官方例子调用序查不到 |
| `LightweightAllResolved` | 枚举查不到 |
| `MakeInterferingPartsTransparent` | Set_Components_Transparent_Example_VB.md 未逐字读 ⇒ 调用序查不到 |
| `MakeLightWeight` | 官方轻化例子走的是 SetSuppression2，未调 MakeLightWeight ⇒ 调用序查不到 |
| `MakeLightWeight` | 枚举查不到（作用范围由当前选区决定） |
| `Name` | ## Remarks 段为空，查不到 |
| `Name` | 枚举查不到 |
| `NonInterferingComponentDisplay` | ## Remarks 为空，查不到 |
| `NonInterferingComponentDisplay` | 返回 System.int，enums 目录无对应枚举文件 ⇒ 取值口径查不到 |
| `NonInterferingComponentDisplay` | 官方例子查不到 |
| `OpenCompFile` | ## Remarks 段为空，查不到 |
| `OpenCompFile` | 官方例子调用序查不到 |
| `OpenCompFile` | 枚举查不到 |
| `ResolveAllLightweight` | 官方例子调用序查不到 |
| `ResolveAllLightweight` | 枚举查不到 |
| `ResolveAllLightWeightComponents` | 官方例子调用序查不到 |
| `ResolveOutOfDateLightWeightComponents` | 官方例子调用序查不到 |
| `ResolveOutOfDateLightWeightComponents` | 枚举查不到 |
| `ReverseRotationDirection` | 官方例子调用序查不到 |
| `ReverseRotationDirection` | swAssemblyExplodeStepType_e.swAssemblyExplodeStepType_Translate 的数值查不到 |
| `ReverseTranslationDirection` | 官方例子调用序查不到 |
| `ReverseTranslationDirection` | swAssemblyExplodeStepType_e.swAssemblyExplodeStepType_Translate 的数值查不到 |
| `RotateAboutEachComponentOrigin` | 官方例子调用序查不到 |
| `RotateAboutEachComponentOrigin` | swAssemblyExplodeStepType_e 的数值查不到 |
| `RotationAngle` | 官方例子调用序查不到 |
| `RotationAngle` | swAssemblyExplodeStepType_e（Radial / Translate）的数值查不到 |
| `SetComponents` | 官方例子目录内没有设爆炸步组件的例子 ⇒ 调用序查不到 |
| `SetComponents` | 枚举查不到 |
| `SetComponentsAndTransforms` | 例子文件存在但本轮未逐字读代码 ⇒ 调用序查不到 |
| `SetExplodeDirection` | ## Remarks 段为空，查不到 |
| `SetExplodeDirection` | 官方例子调用序查不到 |
| `SetRotationAxis` | ## Remarks 段为空，查不到 |
| `SetRotationAxis` | 官方例子调用序查不到 |
| `SetRotationAxis` | RotAxisIndex 的枚举名与数值查不到（无对应 enum 文件） |
| `ShowExploded` | 官方例子查不到：Create_Exploded_Views_Example_VB.md 只用 ShowExploded2 |
| `ShowExploded` | 枚举查不到（未抄） |
| `ShowExploded` | 签名与 ## Remarks 本轮只做了 Obsolete 行扫描、未逐字抄 ⇒ 查不到 |
| `ShowExploded2` | ShowExploded2.md 的 ## Remarks 段为空，调用前置查不到 |
| `ShowIgnoredInterferences` | 官方例子调用序查不到 |
| `swAssemblyExplodeStepType_e` | 爆炸步类型判定（Radial / Translate / SubAssembly）的全部数值：enums 目录逐字 grep 零命中，查不到 |
| `swAutoMateRepairErrors_e` | 枚举文件存在但本轮未逐字读数值 ⇒ 数值查不到 |
| `swCheckInterferenceOption_e` | 枚举文件存在但未与 IInterferenceDetectionMgr 任一成员对上、也未逐字读 ⇒ 数值查不到 |
| `swConcentricAlignmentType_e` | 被 AddConcentricMateWithTolerance / EditConcentricMate 的 ConcentricPositionType 语义与 IMate2 偏心 Remarks 引用，enums 无该文件 ⇒ 数值查不到 |
| `ToolsCheckInterference` | 官方例子用的是 ToolsCheckInterference2 ⇒ 本成员调用序查不到 |
| `ToolsCheckInterference` | 枚举查不到 |
| `TreatCoincidenceAsInterference` | 官方例子调用序查不到 |
| `TreatSubAssembliesAsComponents` | 官方例子调用序查不到 |
| `UseTransform` | ## Remarks 为空，查不到 |
| `UseTransform` | 官方例子查不到 |
| `ViewCollapseAssembly` | 枚举查不到（无枚举形参） |
| `ViewExplodeAssembly` | 枚举查不到（无枚举形参） |

#### `api-06-features.md`（13 条）

| 成员 | 查不到的是什么 |
|---|---|
| `CreateDefinition` | Remarks 没有 Before calling 式的选择前置，只区分哪些常量需再调专属 initialize 方法，选用式前置查不到 |
| `Deform` | IFeatureManager 下查不到任何成员：目录清单无 *Deform* 文件，CHM 成员表全文检索 Deform 0 命中 |
| `Dome` | IFeatureManager 下查不到任何成员：目录清单无 *Dome* 文件，CHM 成员表全文检索 Dome 0 命中（只有 IDomeFeatureData 等特征数据接口） |
| `FeatureLocalCurveDrivenPattern` | 官方例子查不到：md 只有 See Also，CHM 该页同样无 Example 条目 |
| `FeatureRecogn` | IFeatureManager 下查不到任何成员：目录清单无 *FeatureRecogn* 文件，CHM 成员表全文检索 Recogn 0 命中 |
| `IInsertCombineFeature` | 官方例子查不到：md 与 CHM 都没有 ## Examples 节 |
| `InsertFlexFeature` | 官方例子查不到：md 与 CHM 的 Examples 段都为空或缺 |
| `InsertFlexFeature` | md 与 CHM 都没有 ## Remarks 节，调用前置文字查不到 |
| `InsertFlexFeature` | Type 的内联整数表（-1..4）没给枚举名，enums 目录下也查不到对应 md |
| `InsertRib` | md 与 CHM 都没有 ## Remarks 节，调用前置文字查不到 |
| `InsertSplitLineIntersect` | 官方例子查不到：md 与 CHM 都没有 ## Examples 节 |
| `InsertSplitLineIntersect` | md 与 CHM 都没有 ## Remarks 节，调用前置文字查不到 |
| `SetFreeformBoundaryContinuity` | 官方例子查不到：md 与 CHM 都没有 ## Examples 节，官方只给了交互录制宏的做法 |

#### `api-07-sketch.md`（162 条）

| 成员 | 查不到的是什么 |
|---|---|
| `ISketch.AutoDimension` | ## Remarks 段与官方例子调用序；五个形参描述全是 No description |
| `ISketch.ConstrainAll` | 官方例子调用序 |
| `ISketch.GetArcs` | ## Remarks 段与官方例子调用序 |
| `ISketch.GetAutomaticSolve` | 调用前置（Remarks 只写可由 SetAutomaticSolve 控制）；官方例子调用序 |
| `ISketch.GetConstrainedStatus` | ## Remarks 段、取值表与官方例子调用序 |
| `ISketch.GetContourEdgeCount` | 官方例子调用序 |
| `ISketch.GetContourEdges` | 官方例子调用序 |
| `ISketch.GetDetachSegmentOnDrag` | 官方例子调用序 |
| `ISketch.GetEllipses` | ## Remarks 段与官方例子调用序 |
| `ISketch.GetEllipses2` | ## Remarks 段与官方例子调用序 |
| `ISketch.GetEllipses3` | 官方例子调用序 |
| `ISketch.GetLineCount` | ## Remarks 段与官方例子调用序 |
| `ISketch.GetLineCount2` | CrossHatchOption 形参点名的枚举 |
| `ISketch.GetLines` | ## Remarks 段与官方例子调用序 |
| `ISketch.GetParabolas` | ## Remarks 段与官方例子调用序 |
| `ISketch.GetParabolas2` | 官方例子调用序（.md 与 CHM 正文都只到 Option Explicit） |
| `ISketch.GetPolyLineCount` | ## Remarks 段与官方例子调用序 |
| `ISketch.GetPolylines` | ## Remarks 段；该页例子没有调本成员 |
| `ISketch.GetReferenceEntity` | swSelNOTHING 的数值（Remarks 只写了名字） |
| `ISketch.GetSketchBlockInstanceCount` | 官方例子调用序 |
| `ISketch.GetSketchBlockInstances` | 调用前置（只有 See 链接）与官方例子调用序 |
| `ISketch.GetSketchContourCount` | 官方例子调用序 |
| `ISketch.GetSketchContours` | 官方例子代码未逐行抄 |
| `ISketch.GetSketchHatches` | 调用前置（Remarks 只指路到 IView 一族）；官方例子代码未逐行抄 |
| `ISketch.GetSketchPathCount` | 官方例子调用序 |
| `ISketch.GetSketchPictureCount` | 官方例子调用序 |
| `ISketch.GetSketchPictures` | ## Remarks 段与官方例子调用序 |
| `ISketch.GetSketchPoints` | ## Remarks 段与官方例子调用序 |
| `ISketch.GetSketchPoints2` | 调用前置（Remarks 只写与旧版差异）；官方例子代码未逐行抄 |
| `ISketch.GetSketchPointsCount` | ## Remarks 段与官方例子调用序 |
| `ISketch.GetSketchRegionCount` | 官方例子调用序（Get_Sketch_Regions_Example 未逐行抄） |
| `ISketch.GetSketchRegions` | ## Remarks 段与官方例子调用序 |
| `ISketch.GetSketchSlotCount` | 官方例子调用序（Get_Sketch_Slot_Data_Example 未逐行抄） |
| `ISketch.GetSketchSlots` | ## Remarks 段与官方例子调用序 |
| `ISketch.GetSketchTextSegments` | ## Remarks 段与官方例子调用序 |
| `ISketch.GetSplineInterpolateCount` | 官方例子调用序 |
| `ISketch.GetSplineParams` | ## Remarks 段与官方例子调用序 |
| `ISketch.GetSplineParams2` | 调用前置（页内只给布局公式）；官方例子调用序 |
| `ISketch.GetSplineParams3` | 调用前置；本成员的调用序（挂的例子里调的是 GetSplineParams4） |
| `ISketch.GetSplineParams5` | ## Remarks 段（Index 是 0-based 只由例子实参推出） |
| `ISketch.GetSplineParamsCount` | ## Remarks 段与官方例子调用序 |
| `ISketch.GetSplineParamsCount2` | ## Remarks 段与官方例子调用序 |
| `ISketch.GetSplineParamsCount3` | ## Remarks 段；Size 语义只在 Parameters；官方例子调用序 |
| `ISketch.GetSplines` | 官方例子调用序（该页无 ## Examples 段） |
| `ISketch.GetUserPoints` | ## Remarks 段与官方例子调用序 |
| `ISketch.GetUserPoints2` | 官方例子调用序 |
| `ISketch.IEnumSketchHatches` | ## Remarks 段与官方例子调用序 |
| `ISketch.IEnumSketchPoints` | ## Remarks 段；本成员的调用序（那句话出现在 Select_All_Sketch_Segments 例子里） |
| `ISketch.IEnumSketchTextSegments` | ## Remarks 段与官方例子调用序 |
| `ISketch.IGetArcs` | ## Remarks 段与官方例子调用序 |
| `ISketch.IGetArcs2` | 官方例子调用序 |
| `ISketch.IGetContourEdges` | 官方例子调用序；Remarks 把 GetContourEdgesCount 写成了不存在的成员名 |
| `ISketch.IGetEllipses` | ## Remarks 段与官方例子调用序 |
| `ISketch.IGetEllipses2` | ## Remarks 段与官方例子调用序 |
| `ISketch.IGetEllipses3` | 官方例子调用序 |
| `ISketch.IGetLines` | ## Remarks 段与官方例子调用序 |
| `ISketch.IGetLines2` | 官方例子调用序 |
| `ISketch.IGetParabolas` | ## Remarks 段与官方例子调用序 |
| `ISketch.IGetParabolas2` | 官方例子调用序 |
| `ISketch.IGetPolylines` | ## Remarks 段与官方例子调用序 |
| `ISketch.IGetSketchBlockInstances` | 官方例子调用序 |
| `ISketch.IGetSketchContours` | 官方例子调用序 |
| `ISketch.IGetSketchPaths` | 官方例子调用序 |
| `ISketch.IGetSketchPictures` | 官方例子调用序 |
| `ISketch.IGetSketchPoints2` | 官方例子调用序 |
| `ISketch.IGetSketchRegions` | 官方例子调用序 |
| `ISketch.IGetSketchSlots` | 官方例子调用序 |
| `ISketch.IGetSplineParams` | ## Remarks 段与官方例子调用序 |
| `ISketch.IGetSplineParams2` | 调用前置（只有布局公式）；官方例子调用序 |
| `ISketch.IGetSplineParams2（废弃链）` | 官方写的后继名 IGetSplineParameters3 在本接口查不到（实际成员叫 IGetSplineParams3） |
| `ISketch.IGetSplineParams3` | 调用前置；官方例子调用序 |
| `ISketch.IGetSplines` | 官方例子调用序 |
| `ISketch.IGetSplinesInterpolate` | 官方例子调用序（CHM 那例调的是 GetSplinesInterpolate） |
| `ISketch.IGetUserPoints` | ## Remarks 段与官方例子调用序 |
| `ISketch.IModelToSketchXform` | ## Remarks 段与官方例子调用序 |
| `ISketch.Is3D` | ## Remarks 段与官方例子调用序 |
| `ISketch.IsBoundaryBoxSketch` | ## Remarks 段与官方例子调用序 |
| `ISketch.IsDerived` | ## Remarks 段与官方例子调用序 |
| `ISketch.IsShared` | ## Remarks 段与官方例子调用序 |
| `ISketch.IsSketchEditable` | ## Remarks 段与官方例子调用序 |
| `ISketch.MergePoints` | 官方例子调用序；swConstraintType_COINCIDENT 的数值 |
| `ISketch.ModelToSketchTransform` | ## Remarks 段与官方例子调用序 |
| `ISketch.ModelToSketchXform` | ## Remarks 段与官方例子调用序 |
| `ISketch.RelationManager` | ## Remarks 段与官方例子调用序 |
| `ISketch.SetAutomaticSolve` | 官方例子调用序 |
| `ISketch.SetSketchEditable` | ## Remarks 段与官方例子调用序 |
| `ISketch（整域）` | 官方未给 swConstrainedStatus_e 数值表，不要自行解释完全定义 |
| `ISketchManager.ActiveSketch` | ## Remarks 段（官方没写） |
| `ISketchManager.AutoInference` | 调用前置（Remarks 只描述推断模式的显示效果） |
| `ISketchManager.AutoSolve` | ## Remarks 段与官方例子调用序 |
| `ISketchManager.CircularSketchStepAndRepeat 调用前置` | CreateCircularSketchStepAndRepeat 页内只写了尺寸可被交互用户改，未写前置 |
| `ISketchManager.ConvertEntities` | ## Remarks 段与官方例子调用序 |
| `ISketchManager.Create_Sketch_Point_Example_VB` | 官方例子调用序（正文只有前置注释，无函数体） |
| `ISketchManager.Create3PointArc` | ## Remarks 段与官方例子调用序 |
| `ISketchManager.Create3PointCenterRectangle` | ## Remarks 段与官方例子调用序 |
| `ISketchManager.Create3PointCornerRectangle` | ## Remarks 段与官方例子调用序 |
| `ISketchManager.CreateArc` | 官方例子调用序（本轮未逐行抄 Get_Sketch_Arc_Data_Example） |
| `ISketchManager.CreateArc` | Direction 形参点名的枚举 |
| `ISketchManager.CreateBoundaryHatch` | 官方例子调用序（该页无 ## Examples 段） |
| `ISketchManager.CreateCenterLine` | 调用前置（Remarks 段只给了一个替代做法，没写前置） |
| `ISketchManager.CreateCenterRectangle` | ## Remarks 段与官方例子调用序 |
| `ISketchManager.CreateChamfer` | ## Remarks 段与官方例子调用序；AngleORdist 的取舍只在 Parameters |
| `ISketchManager.CreateCircleByRadius` | 官方例子调用序（该页无 ## Examples 段） |
| `ISketchManager.CreateConstructionGeometry` | 官方例子调用序 |
| `ISketchManager.CreateEllipse` | 官方例子调用序（CHM 与 .md 正文只到 Option Explicit，无函数体） |
| `ISketchManager.CreateEllipticalArc` | 官方例子调用序；Direction 形参点名的枚举 |
| `ISketchManager.CreateEquationSpline` | 本成员的调用序（挂的例子里调的是 CreateEquationSpline2） |
| `ISketchManager.CreateEquationSpline2` | 调用前置（Remarks 只讲各参数含义，没写前置） |
| `ISketchManager.CreateParabola` | ## Remarks 段与官方例子调用序 |
| `ISketchManager.CreateParallelogram` | ## Remarks 段与官方例子调用序 |
| `ISketchManager.CreatePolygon` | ## Remarks 段与官方例子调用序 |
| `ISketchManager.CreateRegionHatch` | 官方例子调用序 |
| `ISketchManager.CreateSketchBelt` | 官方例子调用序（无例子） |
| `ISketchManager.CreateSketchSlot` | ## Remarks 段（官方没写） |
| `ISketchManager.CreateSplineByEqnParams` | 官方例子调用序（该页无 ## Examples 段） |
| `ISketchManager.CreateSplineParamData` | ## Remarks 段（该页既无 Parameters 也无 Remarks） |
| `ISketchManager.CreateSplinesByEqnParams` | 官方例子调用序（该页无 ## Examples 段） |
| `ISketchManager.CreateSplinesByEqnParams2` | ## Parameters / ## Remarks 段（页面两段都空） |
| `ISketchManager.CreateTangentArc` | ## Remarks 段与官方例子调用序 |
| `ISketchManager.CurvatureDensity` | ## Remarks 段与官方例子调用序 |
| `ISketchManager.CurvatureScale` | ## Remarks 段与官方例子调用序 |
| `ISketchManager.DisplayWhenAdded` | 官方例子调用序（该页无 ## Examples 段） |
| `ISketchManager.Document` | ## Remarks 段与官方例子调用序 |
| `ISketchManager.EditLinearSketchStepAndRepeat` | 调用前置（页内没写；抄到的例子片段不含 SelectByID2） |
| `ISketchManager.EditSketchBlock` | 官方例子调用序（该页无 ## Examples 段） |
| `ISketchManager.EndEditSketchBlock` | 官方例子调用序 |
| `ISketchManager.ExplodeSketchBlockInstance` | 官方例子调用序 |
| `ISketchManager.Extend_Sketch_Entity_Example_VB` | 造线那段的调用序（正文只到 Option Explicit） |
| `ISketchManager.FullyDefineSketch` | ## Remarks 段与官方例子调用序；mark=6 规则只在 Parameters |
| `ISketchManager.GetDynamicMirror` | ## Remarks 段与官方例子调用序 |
| `ISketchManager.GetSketchBlockDefinitionCount` | 官方例子调用序 |
| `ISketchManager.GetSketchBlockDefinitions` | 调用前置（只给了 See 链接）；官方例子代码未逐行抄 |
| `ISketchManager.ICreateSpline` | 官方例子调用序 |
| `ISketchManager.ICreateSpline2` | 官方例子调用序 |
| `ISketchManager.ICreateSplineByEqnParams` | 官方例子调用序 |
| `ISketchManager.ICreateSplinesByEqnParams` | 官方例子调用序 |
| `ISketchManager.IGetSketchBlockDefinitions` | 官方例子调用序 |
| `ISketchManager.InferenceMode` | 官方例子调用序 |
| `ISketchManager.Insert3DSketch` | ## Remarks 段（官方没写） |
| `ISketchManager.InsertExplodeLineSketch` | ## Remarks 段（官方没写） |
| `ISketchManager.InsertSketchPicture` | 本成员的调用序（CHM 例子正文已改用 InsertSketchPicture2） |
| `ISketchManager.InsertSketchPicture2` | 调用前置（Remarks 只写了非工程图时 HighestResolution 默认 false） |
| `ISketchManager.IntersectCurves` | ## Remarks 段与官方例子调用序 |
| `ISketchManager.MakeSketchBlockFromFile` | 官方例子调用序（该页无 ## Examples 段） |
| `ISketchManager.MakeSketchBlockFromSketch` | 调用前置（Remarks 只有 See 链接）；官方例子调用序 |
| `ISketchManager.PerimeterCircle` | ## Remarks 段与官方例子调用序 |
| `ISketchManager.ReverseEndPointTangent` | ## Remarks 段与官方例子调用序 |
| `ISketchManager.RotateOrCopy3DAboutVector` | ## Remarks 段与调用前置；官方例子调的是 RotateOrCopy3DAboutXYZ |
| `ISketchManager.SetGridOptions` | 官方例子调用序 |
| `ISketchManager.SketchOffset` | 调用前置（页内只写了 Chain 语义）；官方例子调用序 |
| `ISketchManager.SketchReplace2` | 官方例子调用序（Replace_Sketch_Example 未逐行抄） |
| `ISketchManager.SketchTrim` | 官方例子调用序（.md 只剩空 Sub，CHM 三语种全部 ABSENT） |
| `ISketchManager.SketchUseEdge` | 调用前置（页内只写 Chain 语义）；官方例子未逐行抄 |
| `ISketchManager.SketchUseEdge2` | 调用前置；Convert_Faces_Edges_to_Sketch_Entities 例子正文只有前置注释 |
| `ISketchManager.SketchUseEdge3` | 调用前置；官方例子未逐行抄 |
| `ISketchManager.Split_Closed_Sketch_Segment_Example_VB` | CHM .htm 文件 ABSENT；VBNET/CSharp 版未逐行抄 |
| `ISketchManager（整个目录）` | 草图文字创建成员：对 93 个文件检索 Text → 0 命中 |
| `ISketchManager（整域）` | 官方参数原文用 in meters（CreateFillet / CreateTangentArc），本文件照抄不换算 |
| `ISketchText（目录）` | C:\swapi\types\ISketchText\ 不在本轮范围内，未读 |
| `swConstraintType_e` | 逐条数值查不到（CreateSketchPlane / MergePoints 两页都只点名枚举名） |
| `swEndCapThicknessDirection_e` | 在 ISketchManager / ISketch 的签名、Parameters、Remarks 里都查不到出处 |
| `swSketchCheckFeatureStatus_e` | C:\swapi\enums\ 下的枚举文件不存在（数值改抄自 CHM 例子正文） |

#### `api-08-mold-costing.md`（71 条）

| 成员 | 查不到的是什么 |
|---|---|
| `C:\swapi\types\ICosting*` | 没有任何 ICosting*/ICost* 目录；全仓按 CostManager/CostAnalysis/CostBody/CostPart/CostFeature 搜 .md 结果为空 |
| `C:\swapi\types\IMold*` | 566 个类型目录里没有任何以 IMold 开头的目录，模具成员不在独立接口里 |
| `CostAnalysis` | 签名与 Remarks 查不到（CHM 解包 *sldcostingapi* 文件数 = 0） |
| `CostAnalysisMachining` | 签名与 Remarks 查不到（CHM 解包 *sldcostingapi* 文件数 = 0） |
| `CostBody` | 签名与 Remarks 查不到（CHM 解包 *sldcostingapi* 文件数 = 0） |
| `CostFeature` | 签名与 Remarks 查不到（CHM 解包 *sldcostingapi* 文件数 = 0） |
| `CostPart` | 签名与 Remarks 查不到（CHM 解包 *sldcostingapi* 文件数 = 0） |
| `IAssemblyDoc.InsertCavity` | ## Remarks 段与 ## Examples 段（已 Obsolete，后继 InsertCavity4） |
| `IAssemblyDoc.InsertCavity2` | ## Remarks 段与 ## Examples 段（已 Obsolete，后继 InsertCavity4） |
| `IAssemblyDoc.InsertCavity2` | 形参 ScaleType 的枚举类型官方未在本文件点名 |
| `IAssemblyDoc.InsertCavity3` | ## Remarks 段与 ## Examples 段（已 Obsolete，后继 InsertCavity4） |
| `IAssemblyDoc.InsertCavity3` | 形参 ScaleType 的枚举类型官方未在本文件点名 |
| `IAssemblyDoc.InsertCavity4` | ## Examples 段与官方调用序（CHM 只给手工操作说明） |
| `IAssemblyDoc.InsertCavity4` | 形参 ScaleType 的枚举类型官方未在本文件点名 |
| `ICavityFeatureData.SetScale` | ## Examples 段：官方例子只用了 UniformScale，没有调 SetScale |
| `ICoreFeatureData.Depth` | swapi 的 Depth.md 没有签名行，签名抄自 CHM ICoreFeatureData~Depth.html |
| `ICoreFeatureData.EndCondition` | swapi 的 EndCondition.md 没有签名行，签名抄自 CHM 同源页 |
| `ICoreFeatureData.GetExtractionDirection` | out Type1/Type2 的实体类型枚举名（官方只给 6 个文字名） |
| `ICoreFeatureData.SetExtractionDirection` | ## Examples 段与官方例子 |
| `ICoreFeatureData.SetExtractionDirection` | 形参实体的类型枚举名（同 H8） |
| `ICostManager` | 签名、Remarks、枚举数值全部查不到；CHM 解包目录 *sldcostingapi* 文件数 = 0 |
| `IFeatureManager.InsertMoldCoreCavitySolids` | ## Examples 段与官方例子 |
| `IFeatureManager.InsertMoldPartingLine` | ## Examples 段与官方例子（examples 里 4 个分型线例子都不从建模入口起手） |
| `IFeatureManager.InsertMoldPartingSurface` | ## Examples 段与官方例子（只有 3 个取改特征数据的例子） |
| `IFeatureManager.InsertMoldShutOffSurface` | ## Examples 段与官方例子（examples 目录无 shut-off / 封油面例子） |
| `IFeatureManager.InsertMoldShutOffSurface` | ## Remarks 段（该文件与 CHM 同源页都没有） |
| `IFeatureManager.MoldUndercutDetect` | ## Examples 段与官方例子 |
| `IFeatureManager.MoldUndercutDetect` | ## Remarks 段；6 个形参说明逐字全部是 No description |
| `IFeatureManager.MoldUndercutDetect2` | ## Examples 段与官方例子 |
| `IFeatureManager.MoldUndercutDetect2` | ## Remarks 段（只有 9 个形参的逐字语义，没有调用前置） |
| `IMassProperty2.PrincipalAxesOfInertia` | swapi 无签名行，签名抄自 CHM IMassProperty2~PrincipalAxesOfInertia.html |
| `IMassProperty2.SetCoordinateSystem` | 形参 Coords 的类型官方未点名 |
| `IMassProperty2.SetOverrideOptions` | Config_option 的枚举与三个形参的取值域 |
| `IMassProperty2.UseSystemUnits` | 改成毫米/工程单位的改法细节（官方未在本地源里给出） |
| `IMassPropertyOverrideOptions.GetOverridePrincipalAxesOrientation` | 形参 Axis 的取值域 |
| `IMassPropertyOverrideOptions.SetOverrideMomentsOfInertiaValue` | 形参 ReferenceFrame 的枚举 |
| `IMassPropertyOverrideOptions.SetOverridePrincipalAxesOrientation` | 形参 Axis 的取值域 |
| `IMassPropertyOverrideOptions（全部 13 个成员）` | 官方例子：IMassPropertyOverrideOptions 各成员页均无 ## Examples 段 |
| `IMeasure.AngleDecimalPlaces` | 官方例子未出现该成员 |
| `IMeasure.LengthDecimalPlaces` | 官方例子未出现该成员 |
| `IMeasure.ProjectionOption` | 官方例子未出现该成员 |
| `IMeasure.SetProjectionEntity` | 官方例子没调用它（Measure_Selected_Entities_Example_CSharp.md 里没有这一句） |
| `IMeasure（K4–K33 共 30 个成员）` | 全部 30 个成员的 ## Remarks 段（实测 withRemarks=0） |
| `IModelDoc2.MoldDraftAnalysis` | ## Examples 段与官方例子 |
| `IModelDoc2.MoldDraftAnalysis` | ## Remarks 段（swapi 文件与 CHM 页都没有） |
| `IModelDoc2.MoldDraftAnalysis` | swDraftAnalysisFaceType_e 未被本成员签名引用（未作为本成员枚举抄） |
| `IPartingLineFeatureData.GetEntitiesToSplit` | out TypeArr 的取值类型枚举官方未在本文件点名 |
| `IPartingLineFeatureData.GetFacesByType` | 形参 Type 的枚举名（官方只给 negative/positive 等文字名） |
| `IPartingLineFeatureData.GetFacesByTypeCount` | 形参 Type 的枚举名（同 D7） |
| `IPartingLineFeatureData.IGetEntitiesToSplit` | out TypeArr 的元素枚举官方未点名 |
| `IPartingLineFeatureData.IGetFacesByType` | 形参 Type 的枚举名（同 D7） |
| `IPartingLineFeatureData.ISetEntitiesToSplit` | 形参 EntIn 的元素类型官方未点名 |
| `IPartingLineFeatureData.PullDirectionBase` | ## Examples 段与实参说明（官方无例子） |
| `IPartingSurfaceFeatureData.GetPartingLinesType` | 返回值的枚举名（官方只给 0/1 文字，未点名枚举） |
| `IPartingSurfaceFeatureData.PullDirectionType` | ## Examples 段与枚举（## Remarks 段也查不到） |
| `IPartingSurfaceFeatureData.ReverseOffsetDirection` | ## Remarks 段、## Examples 段与枚举（全部查不到） |
| `IShutOffSurfaceFeatureData.AccessSelections` | ## Examples 段（该文件无 Examples 段，examples 目录也无 shut-off 例子） |
| `IShutOffSurfaceFeatureData.FlipFaceTangentTo` | swPatchTypeTangent 的数值（enums 无 swPatchType*.md，CHM 0 命中） |
| `IShutOffSurfaceFeatureData.GetFaceTangentTo` | swPatchTypeTangent 的数值（同上） |
| `IShutOffSurfaceFeatureData.LoopEdges` | 签名：md 全文只有 frontmatter+标题，CHM 无该页（param_count 记 -1） |
| `IShutOffSurfaceFeatureData.LoopPatchType` | 签名：LoopPatchType.md 无签名行，CHM 无该页（param_count 记 -1） |
| `IShutOffSurfaceFeatureData.SetAllPatchTypes` | 形参 Type 的取值集合：swPatchType_e 枚举文件与 CHM 均 0 命中 |
| `IShutOffSurfaceFeatureData.Status` | 枚举语义与 ## Remarks 段（文件只有签名行，CHM 无该成员页） |
| `IToolingSplitFeatureData.AccessSelections` | ## Examples 段（examples 目录无 tooling split 例子） |
| `IToolingSplitFeatureData.Depth` | 签名：md 全文只有 frontmatter+标题，CHM 无该页（param_count 记 -1） |
| `swcBodyStatus_e` | 枚举成员与数值：C:\swapi\enums\ 无同名文件 |
| `swcBodyType_e` | 枚举成员与数值：C:\swapi\enums\ 无同名文件（swBodyType_e 存在但不是它） |
| `swcCostingType_e` | 枚举成员与数值：C:\swapi\enums\ 无同名文件 |
| `swMeasureArcCircleOption_e` | 与 IMeasure::ArcOption 的绑定关系：官方两套源都没有显式绑定，归属是按名称对应记的 |
| `swMeasureProjectOnOption_e` | 与 IMeasure::ProjectionOption 的绑定关系：官方两套源都没有显式绑定，归属是按名称对应记的 |
| `swPatchType_e / swPatchTypeTangent` | 数值查不到：C:\swapi\enums\ 无 swPatchType*.md，CHM *swPatchType* 0 命中 |

#### `api-09-simulation.md`（80 条）

| 成员 | 查不到的是什么 |
|---|---|
| `ActiveDoc` | 例子里出现该调用，成员页查不到 |
| `AddBearingConnector` | 成员页本机缺失，签名查不到 |
| `AddBearingLoad` | 官方例子文件本机没有，调用序与配方查不到 |
| `AddBearingLoad` | swsLoadsAndRestraintsManagerBearingLoadError_e 的成员与数值查不到 |
| `AddBoltConnector` | 调用前置页面没写，查不到 |
| `AddBoltConnector` | 官方例子本机查不到 |
| `AddBoltConnector` | swsBoltType_e 与 swsBoltConnectorError_e 的数值查不到 |
| `AddCable` | 成员页本机缺失，签名查不到 |
| `AddCentrifugalForce` | 官方例子本机查不到 |
| `AddConvection` | 官方例子本机查不到 |
| `AddCyclicSymmetryRestraint` | 官方例子本机查不到 |
| `AddDefaultStaticStudyPlot` | 例子实参有，成员页查不到 |
| `AddDistributedMass` | 调用前置页面没写，查不到 |
| `AddDistributedMass` | 官方例子本机查不到 |
| `AddEdgeWeldConnector` | 官方例子本机查不到 |
| `AddEdgeWeldConnector` | swsEdgeWeldConnectorTypes_e 只抄到 4 个成员名，数值查不到 |
| `AddElasticConnector` | 调用前置页面没写，查不到 |
| `AddElasticConnector` | 官方例子本机查不到 |
| `AddForce` | 本页 Example 段为空，官方例子查不到 |
| `AddForce2` | 本页 Example 段为空，官方例子查不到 |
| `AddForce3` | 三个官方例子页本机查不到 |
| `AddGeneralSpringConnector` | 成员页本机缺失，签名查不到 |
| `AddGravity` | 官方例子本机查不到 |
| `AddHeatFlux` | 官方例子本机查不到 |
| `AddHeatPower` | 官方例子本机查不到 |
| `AddInitialConditionForDynamicStudy` | 成员页标 Obsolete 而本页无该字样，是否废弃与后继查不到 |
| `AddInitialConditionForDynamicStudy` | 官方例子本机查不到 |
| `AddInitialConditionForDynamicStudy2` | 成员页本机缺失，签名查不到 |
| `AddLinkageRod` | 成员页本机缺失，签名查不到 |
| `AddLinkConnector` | Example 段只写「See the ICWLinkConnector examples」，具体例子查不到 |
| `AddPinConnector` | 官方例子本机查不到 |
| `AddPrescribedDisplacement` | 官方例子本机查不到 |
| `AddRadiation` | 官方例子本机查不到 |
| `AddRemoteLoad` | 官方例子本机查不到 |
| `AddRigidConnector` | 调用前置页面没写，查不到 |
| `AddRigidConnector` | 官方例子本机查不到 |
| `AddSelectedBaseExcitation` | 本页没有 Example 段，官方例子查不到 |
| `AddSelectedBaseExcitation` | 成员页标 Obsolete 而本页无该字样，是否废弃与后继查不到 |
| `AddSelectedBaseExcitation2` | 成员页本机缺失，签名查不到 |
| `AddSpotWeldConnector` | 官方例子本机查不到 |
| `AddSpringConnector` | 官方例子本机查不到 |
| `AddTemperature` | 官方例子本机查不到 |
| `AddUniformBaseExcitation` | 成员页标 Obsolete 而本页无该字样，是否废弃与后继查不到 |
| `AddUniformBaseExcitation` | 官方例子本机查不到 |
| `AddUniformBaseExcitation2` | 成员页本机缺失，签名查不到 |
| `COSMOSWORKS` | 例子里出现该属性，成员页查不到 |
| `cosworks CHM 目录` | 47 个文件里只有 ICWLoadsAndRestraintsManager 的成员页，其它接口页查不到 |
| `CreateMesh` | 成员页查不到；两篇例子的实参口径还不一致 |
| `CreateNewStudy3` | 例子实参有，成员页查不到 |
| `CWMesh` | 该接口成员页本机一律查不到 |
| `DeleteLoadsAndRestraints` | 本页没有 Example 段，官方例子查不到 |
| `GetAddInObject` | 例子实参 "SldWorks.Simulation" 有，成员页查不到 |
| `GetBearingConnector` | 成员页本机缺失，签名查不到 |
| `GetCable` | 成员页本机缺失，签名查不到 |
| `GetComponentAt` | 例子实参有，成员页查不到 |
| `GetDefaultElementSizeAndTolerance` | 例子实参有，成员页查不到 |
| `GetEdgeWeldConnector` | 官方例子本机查不到 |
| `GetGeneralSpringConnector` | 成员页本机缺失，签名查不到 |
| `GetLinkageRod` | 成员页本机缺失，签名查不到 |
| `GetMinMaxStress` | 例子实参有，成员页查不到 |
| `GetSolidBodyAt` | 例子实参有，成员页查不到 |
| `GetStrainForEntities3` | 例子给了 9 个实参，成员页查不到 |
| `GetStressForEntities3` | 例子给了 10 个实参，成员页查不到 |
| `ICosmosWorks` | C:\swapi\types\ICosmosWorks 不存在，CHM 里也无成员页 |
| `ICW* 接口族` | C:\swapi\types 下无任何以 ICW 开头的接口目录（计数为 0） |
| `ICWContactManager` | 该接口成员页本机一律查不到 |
| `ICWResults` | 该接口成员页本机一律查不到 |
| `ICWSolidManager` | 该接口成员页本机一律查不到 |
| `ICWStudy` | 该接口成员页本机一律查不到 |
| `ICWStudyManager` | 该接口成员页本机一律查不到 |
| `Mesh` | 例子实参有，成员页查不到 |
| `Quality` | 例子里 Quality = 1，成员页查不到 |
| `Results` | 例子调用序有，成员页查不到 |
| `RunAnalysis` | 例子调用序有，成员页查不到 |
| `ShowOrHideFixtures` | 例子实参有，成员页查不到 |
| `ShowOrHideForce` | 例子实参有，成员页查不到 |
| `Simulation 官方例子` | C:\swapi\examples 内没有 Simulation/CosmosWorks 例子文件 |
| `SolidManager` | 例子实参有，成员页查不到 |
| `StudyManager` | 例子实参有，成员页查不到 |
| `sws* 枚举` | C:\swapi\enums 下无 sws 开头的枚举文件，Simulation 枚举的成员与数值本机查不到 |

#### `api-10-routing-pdm-anim.md`（16 条）

| 成员 | 查不到的是什么 |
|---|---|
| `IEdm*` | 全 C:\swapi 递归 grep IEdm 零命中；CHM 四个目录（sldworksapi/sldworksapivb6/cosworks/swconst）无任何 IEdm* 页面 |
| `IFeatureManager.InsertConnectionPoint` | 实参调用序查不到：[E] Insert_Connection_Point_Example_VB.md 的 Code 段只有 Sub main()/End Sub |
| `IModelDocExtension.SaveAs3` | 其 ## Examples 段查不到（为空，[E] 目录里没有 SaveAs3 的例子文件） |
| `IMotionStudy.SaveToAVI` | 其 ## Remarks 段查不到（.md 只有 Description/Signature/Parameters/Returns/Examples/See Also，CHM 无 swmotionstudyapi 目录） |
| `IPrimaryMemberPathSegmentFeatureData` | 其例子的调用序查不到：Create_Path_Segment_SSMember 的 VB/C# 例子文件在 examples 目录下按名字搜不到 |
| `IRouteManager` | IRoute* 的接口成员查不到：types 下无 IRoute* 目录，CHM 只有 IAssemblyDoc~GetRouteManager.html 等方法页 |
| `IRoutingComponentManager` | 接口成员查不到：types 下无该目录，CHM 只有 IModelDocExtension~GetRoutingComponentManager.html 一页 |
| `swOrthogonalMode` | 该常量的归属与数值查不到：只在 CHM 例子代码里出现一次，enums 下无对应文件 |
| `swRendererType_e` | 成员表只有 Photoworks_Buffer 与 Solidworks_Screen 两项，Remarks 提到的 Custom 成员查不到 |
| `swRoutingComponentGroupOption_e` | [T] 里引用的这个拼法文件不存在，存在的是 swRoutingComponentGroupingOption_e.md |
| `swSaveAVIImageSize_e` | Test-Path C:\swapi\enums\swSaveAVIImageSize_e.md = False，全仓 grep 只命中引用 |
| `swSelectType_e` | swSelSKETCHES / swSelEDGES / swSelREFCURVES 的数值查不到（本轮未读该枚举文件） |
| `swUserPreferenceRoutingDouble_e` | 该枚举文件在 C:\swapi\enums\ 下不存在，成员与数值查不到 |
| `swUserPreferenceRoutingFileLocations_e` | 该枚举文件在 C:\swapi\enums\ 下不存在，成员与数值查不到 |
| `swUserPreferenceRoutingInteger_e` | 该枚举文件在 C:\swapi\enums\ 下不存在，成员与数值查不到 |
| `swUserPreferenceRoutingToggle_e` | 该枚举文件在 C:\swapi\enums\ 下不存在，成员与数值查不到 |

---

## 三 · 抽查纠错（随机抽 6 条，跨 6 份文件）

★ 判据：自己打开官方页，核对该成员的**签名形参个数**、**Remarks 前置是否存在**、**Obsolete 标记**。
★ 官方页来源：`C:\swapi\types\<接口>\<成员>.md`；仿真域例外（见本节末）。

| # | 抽查条目 | 源 | 索引记 | 官方页复核 | 结论 |
|---|---|---|---|---|---|
| 1 | `IFeatureManager.InsertSweepSurface3` | api-01 | 参数 14 · 前置✅ · 例子✅ · Obsolete | 签名逐参点数 = **14**；`## Remarks` 在；`## Examples` 在；首行 `Obsolete.` | ✅ 一致 |
| 2 | `IFeatureManager.InsertStructuralWeldment5` | api-03 | 参数 5 · 前置✅ · **例子❌** | 签名点数 = **5** ✅；`## Remarks` 在 ✅；★**`## Examples` 段确实存在**，挂 3 个 Custom Weldment Profile 例子，三个例子文件均存在（13017 / 10269 / 11195 字节） | ⚠ **改正 1** |
| 3 | `IFeatureManager.InsertFlexFeature` | api-06 | 参数 17 · 前置❌ · 例子❌ | 签名点数 = **17**；无 `## Remarks`；无 `## Examples` | ✅ 一致 |
| 4 | `ISketchManager.Create3PointCenterRectangle` | api-07 | 参数 9 · 前置❌ · 例子❌ | 签名点数 = **9**；无 `## Remarks`；无 `## Examples` | ✅ 一致 |
| 5 | `IRoutingSettings.GetFromToListHeaderDefinitions` | api-10 | 参数 12 · 前置❌ · **例子✅** | 签名点数 = **12** ✅；无 `## Remarks` ✅；★**整页无 `## Examples` 段**（只有 Parameters / Returns / See Also） | ⚠ **改正 2** |
| 6 | `ICWLoadsAndRestraintsManager.AddForce3` | api-09 | 参数 21 · 前置✅ | ★**官方页无法离线复核**（见下）；分域文件逐字 VBA 签名独立点数 = **21**（ForceType…ErrorCode），与索引一致 | ✅ 一致（附复核限制） |

### 经复核改正（2 条）

**改正 1 · `IFeatureManager.InsertStructuralWeldment5`（api-03）**
　原：**没有官方例子**。实为：**有**。
　依据：`C:\swapi\types\IFeatureManager\InsertStructuralWeldment5.md` 的 `## Examples` 段列出
　`Insert_Structural_Weldments_Using_Custom_Weldment_Profile_Example_{CSharp,VBNET,VB}.md`，
　三个文件在 `C:\swapi\examples\` 下**均存在**。
　性质：分域文件把「例子存在但本轮没读出实参」记成了「无例子」——**判定过严，不是官方没有**。
　⇒ 已在本索引 2.2 段补回，并标注「未读出实参」。

**改正 2 · `IRoutingSettings.GetFromToListHeaderDefinitions`（api-10）**
　原：**有官方例子**。实为：**没有**。
　依据：同上路径的官方页**通读全文只有 Parameters / Returns / See Also，无 `## Examples` 段**。
　性质：分域文件把**别处的例子指针误记到了本条**——**判定过松，是凭空多出来的**。
　⇒ 已在本索引 2.2 段移除，并回填到 2.1 段作警示。

### ⚠ 抽查 6 暴露的一个源覆盖限制（不属纠错，但是真事实）

`ICWLoadsAndRestraintsManager`（**仿真域全部 33 条**）**在两套离线源里的状态是**：

- `C:\swapi\types\ICW*` → **0 个**（该目录 566 个接口里没有）——api-09 自己已如实记录；
- CHM `SWhelp\cosworks\ICWLoadsAndRestraintsManager~*.html` → **页面存在但正文是 JS 空壳**
　（去标签后正文只有 `Loading JS...`，参数表与 Remarks 由脚本动态注入）⇒ **离线无法复核其签名形参个数**。

⇒ 抽查 6 的 21 只能核到「与分域文件逐字抄录自洽」，**核不到官方页**。
⇒ **仿真域 33 条的参数个数属「单源、未二次复核」**，用前请自行上机或开浏览器核。

---

## 四 · 统计

| 指标 | 数 |
|---|---|
| 抄到的成员条目（行） | **691** |
| 去重后唯一 `接口.成员` | **684**（7 条被 2 份文件各抄一遍） |
| ★ 有 Remarks 前置的 | **377** |
| ★ 有官方例子配方实参的 | **207** |
| ★ 标 Obsolete 的 | 88 |
| 签名本身查不到（参数记 `?`） | 11 |
| ★ 「查不到」条目 | **748**（涉及 545 个「源·成员」） |
| ★ 抽查条数 | **6**（跨 **6** 份文件：api-01 / 03 / 06 / 07 / 09 / 10） |
| ★ 抽查后改正条数 | **2** |

---

## 五 · 下游怎么用这份索引

1. **要调某个成员** → 先在 §一 总表定位，看它的 `前置` 与 `例子` 两列。
2. **两列都是 `—`** → 别猜，去 §2.3 确认它是不是「查不到」那一类；
　若是，照查不到处理（官方两套源都没有）。
3. **两列有 ✅** → 直接抄 §2.1 / §2.2 的那一行实参。
4. **要钣金 / 工程图** → ⚠ **本索引这两域是空的**，先补 `api-02-sheetmetal.md` 与 `api-05-drawing.md` 再合并。

