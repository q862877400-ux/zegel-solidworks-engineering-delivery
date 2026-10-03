# audit-10 · 域 `10-misc` · 核对 A（签名一致性）

**范围**：域 `10-misc` ∩ 核对 A（实参个数 / 顺序 / 明显类型 与官方 Signature 形参表并排数）
**我方文件**：`scripts/sw_export.py` · `scripts/sw_review.py` · `scripts/sw_document_data.py` ·
`scripts/sw_ref_geometry.py` · `scripts/sw_helix.py` · `scripts/sw_loft.py` · `scripts/sw_sweep.py` ·
`scripts/sw_wrap.py` · `scripts/sw_gtol.py` —— ★ 九份**全部存在**，无替代、无缺档
**官方源**：`C:\swapi\types\<接口>\<成员>.md` 的 `**Signature**` 行 · `C:\swapi\examples\*.md` ·
`C:\swapi\enums\*.md` · 出厂类型库反射 `D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt` ·
CHM 解包 `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\*.html`
**纪律**：只报「两段原文对不上」；给不出两段的不写；不下结论、不给建议。

---

## 表

| # | 我们的原文（文件 + 片段） | 官方的原文（文件 + 片段） | 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | `scripts/sw_export.py`（`get_mass_property_override_options`）：<br>`        mass_property = get_com_member(extension, "GetMassProperties", float(accuracy))` | ① `C:\swapi\types\IModelDocExtension\GetMassProperties.md`：<br>`**Signature**: `System.object GetMassProperties( System.int Accuracy, out System.int Status )``<br>② 出厂类型库反射 `D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt`（`## IModelDocExtension` 段）：<br>`Object GetMassProperties(Int32, Int32&)`<br>③ `scripts/sw_connect.py`（`get_com_member`，证明 `*args` 原样透传、无补位）：<br>`        return member(*args)` | 两个官方源**一致**给出 **2 个形参**（`Int32 Accuracy` + `out Int32 Status`）；我方只给 **1 个**实参，且该实参是 `float(...)` 而形参声明为 `System.int`。⇒ 参数个数不符（1 vs 2）**且**第 1 实参类型不符（浮点 vs 整数）。<br>⚠ 同名成员的另一处声明：`## IBody` / `## IBody2` 段为 `Object GetMassProperties(Double)`（1 参、Double）；我方代码取的是 `model.Extension`（`IModelDocExtension`），不是 `IBody2`。 | 高 |

---

## 核对覆盖（逐点数的，不含「看起来没问题」的推断）

| 文件 | 核了的调用点数 | 其中 |
|---|---|---|
| `scripts/sw_export.py` | 29 | `SetUserPreferenceIntegerValue`(2/2) · `GetExportFileData`(1/1) · `GetSheetNames`(0/0) · `SetSheets`(2/2) · `Extension.SaveAs`(6/6，**两处**) · `ExportToDWG2`(9/9) · `GetType`/`GetPathName`/`GetTitle`/`ActiveDoc`(0/0) · `ActivateDoc3`(4/4，两处含 DumbDispatch) · `ActivateDoc2`(3/3，两处) · `GetOpenDocumentByName`(1/1) · `CloseDoc`(1/1) · `ClearSelection2`(1/1) · **`GetMassProperties`(1/2，✗ 见 #1)** · `GetOverrideOptions`(0/0) · `OverrideMass`/`OverrideCenterOfMass`/`OverrideMomentsOfInertia`(属性写) · `SetOverrideMassValue`(1/1) · `SetOverrideOptions`(3/3) · `SaveBMP`(3/3) · `SaveAs3`(7/7) |
| `scripts/sw_review.py` | 34 | `ViewZoomtofit2`(0/0，**CHM 页**) · `GraphicsRedraw2`(0/0，两处) · `ClearSelection2`(1/1，两处) · `GetSelectedObjectCount2`(1/1) · `ActivateDoc3`(4/4) · `ActivateDoc2`(3/3) · `ShowNamedView2`(2/2，两处) · `SaveBMP`(3/3) · `FirstFeature`/`GetNextFeature`/`GetTypeName2`/`GetTitle`/`GetPathName`/`GetType`/`ActiveView`/`Name`(0/0) · `GetPartBox`(1/1) · `GetBodies2`(2/2) · `GetFaces`/`GetSurface`/`IsCylinder`/`CylinderParams`/`FaceInSurfaceSense`/`GetArea`/`GetLoopCount`/`GetEdgeCount`(0/0) · `ForceRebuild3`(1/1) |
| `scripts/sw_document_data.py` | 16 | `GetConfigurationNames`(0/0) · `ConfigurationManager`/`ActiveConfiguration`/`Name`/`SystemValue`(属性) · `ShowConfiguration2`(1/1) · `EditRebuild3`(0/0，三处) · `AddConfiguration3`(4/4) · `Parameter`(1/1) · `GetSystemValue2`(1/1) · `SetSystemValue3`(3/3) · `CustomPropertyManager`(1/1，**见「查不到」**) · `Get6`(6/6) · `Add3`(4/4) |
| `scripts/sw_ref_geometry.py` | 12 | `InsertRefPlane`(6/6) · `InsertCoordinateSystem`(3/3) · `InsertReferencePoint`(4/4) · `InsertCenterOfMass`(0/0) · `Create3DBoundingBox`(0/0) · `InsertGlobalBoundingBox2`(5/5) · `FeatureManager`/`Extension`(属性) |
| `scripts/sw_helix.py` | 4 | `InsertHelix`(10/10) · `Extension`(属性) · `GetLastFeatureAdded`(0/0) · `Name`(属性) |
| `scripts/sw_loft.py` | 13 | `GetSelectedObjectCount2`(1/1，两处) · **`InsertProtrusionBlend2`(18/18)** · **`InsertCutBlend`(12/12)** · `FeatureByName`(1/1，两处) · `GetTypeName2`(0/0，两处) · `SelectionManager`/`FeatureManager`(属性) |
| `scripts/sw_sweep.py` | 18 | `CreateDefinition`(1/1，三处) · `AccessSelections`(2/2，两处) · `CreateFeature`(1/1，两处) · `GetSelectedObjectCount2`(1/1，两处各 3 个 mark) · `FeatureByName`(1/1) · `GetTypeName2`(0/0) · `SelectionManager`/`FeatureManager`(属性) |
| `scripts/sw_wrap.py` | 10 | `InsertWrapFeature2`(5/5) · `GetSelectedObjectCount2`(1/1，两个 mark) · `FeatureByName`(1/1) · `GetTypeName2`(0/0，两处) · `Name`(属性) · `SelectionManager`/`FeatureManager`(属性) |
| `scripts/sw_gtol.py` | 8 | `InsertGtol`(0/0) · `AddFrame`(0/0) · `CanConvertFormat`(0/0) · `ConvertFormat`(0/0) · `GetFrameCount`(0/0，两处) · `GetFrame`(1/1) · `AddIndicator`(3/3) |
| **合计** | **144** | — |

**位置逐位对齐的两处大参数表**（最易错，本轮逐位对过）：
- `_blend_args` 18 元组 ↔ `C:\swapi\types\IFeatureManager\InsertProtrusionBlend2.md`
  的 `System.bool Closed, System.bool KeepTangency, System.bool ForceNonRational, System.double TessToleranceFactor,
  System.short StartMatchingType, System.short EndMatchingType, System.double StartTangentLength,
  System.double EndTangentLength, System.bool StartTangentDir, System.bool EndTangentDir, System.bool IsThinBody,
  System.double Thickness1, System.double Thickness2, System.short ThinType, System.bool Merge,
  System.bool UseFeatScope, System.bool UseAutoSelect, System.int GuideCurveInfluence` —— **逐位一致**。
- `_cut_blend_args` 12 元组 ↔ `C:\swapi\types\IFeatureManager\InsertCutBlend.md` —— **逐位一致**（12 参 = 18 参去掉
  `Start/EndTangentLength`·`Start/EndTangentDir`·`Merge`·`GuideCurveInfluence` 六位，其余同位）。

---

## 「两源不一致」记录（本轮 0 条）

把域内 **25 个**带参成员同时对着 `C:\swapi\types\*.md` 的 `**Signature**` 与出厂类型库反射的**参数个数**数了一遍
（`InsertWrapFeature2` 5/5 · `InsertProtrusionBlend2` 18/18 · `InsertCutBlend` 12/12 · `InsertRefPlane` 6/6 ·
`InsertReferencePoint` 4/4 · `InsertGlobalBoundingBox2` 5/5 · `InsertHelix` 10/10 · `IGtolFrame::AddIndicator` 3/3 ·
`IDimension::SetSystemValue3` 3/3 · `ICustomPropertyManager::Get6` 6/6 · `Add3` 4/4 · `IPartDoc::ExportToDWG2` 9/9 ·
`IModelDocExtension::SaveAs` 6/6 · `SaveAs3` 7/7 · `IExportPdfData::SetSheets` 2/2 · `IModelDoc2::ShowConfiguration2` 1/1 ·
`AddConfiguration3` 4/4 · `IPartDoc::GetBodies2` 2/2 · `ISelectionMgr::GetSelectedObjectCount2` 1/1 ·
`ISweepFeatureData::AccessSelections` 2/2 · `CreateDefinition` 1/1 · `IMassProperty2::SetOverrideOptions` 3/3 · …）
⇒ **两源的个数全部相同**，本域未出现「文档 7 个 / 类型库 14 个」那类分歧；**唯一的例外是 #1 那一处，而那一处两源反而一致
（都是 2 个形参），与我方的 1 个实参不符。**

## 「查不到」记录

- `C:\swapi\types\IModelDocExtension\CustomPropertyManager.md` **全页只有 10 行**（front-matter + 标题 + 空行），
  **没有 `**Signature**` 行** ⇒ 我方 `model.Extension.CustomPropertyManager(configuration_name)` 的实参个数
  **在 md 源里查不到**。出厂反射 `## IModelDocExtension` 段有 `CustomPropertyManager get_CustomPropertyManager(String)`
  （1 参，与我方 1 实参一致）⇒ 因缺 md 侧原文，**不计入表内**。
- `C:\swapi\types\IModelDoc2\` 下**没有** `ViewZoomtofit2.md` ⇒ 改用 CHM 页
  `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IModelDoc2~ViewZoomtofit2.html`：
  `Sub ViewZoomtofit2()` / `C# void ViewZoomtofit2()` ⇒ 0 形参，与我方 0 实参一致，**不计入表内**。

## 「接口归属」事实记录（★ 属核对 C / 铁律 5 范畴，本轮不作判定、不入表）

- 我方在标注为 `IModelDoc2` 的对象上调用、而官方页把成员声明在**别的接口**下的，有 4 处（只陈述归属，不判对错）：
  `sw_export.py` 的 `model.ExportToDWG2(...)`（官方页 `type: IPartDoc` / `# IPartDoc.ExportToDWG2`）·
  `sw_review.py` 的 `get_com_member(model, "GetBodies2", 0, False)` 与 `get_com_member(model, "GetPartBox", True)`
  （官方页在 `IPartDoc\` 下）· `sw_export.py` 的 `get_com_member(model, "GetSheetNames")`（官方页在 `IDrawingDoc\` 下）。
  这 4 处的**形参个数与顺序均与官方一致**，分歧只在「声明在哪个接口」，不在 Signature 形参表 ⇒ 按核对 A 的口径不入表。

---

核了 **144** 处 · 报 **1** 条 · 置信度为高的是 **第 1 条**（`IModelDocExtension.GetMassProperties` 实参 1 个 / 形参 2 个，且第 1 实参 `float` 与形参 `System.int` 不符）。
