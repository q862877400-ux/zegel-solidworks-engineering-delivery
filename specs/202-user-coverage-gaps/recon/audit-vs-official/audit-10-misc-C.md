# audit-10-misc-C —— 域 10-misc · 核对 C（废弃链与枚举取值）

**只读核对，未运行 SolidWorks，未运行 pytest，未改动仓内任何文件（只新建本文件）。**

## 范围

| 项 | 内容 |
|---|---|
| 域 | `10-misc` |
| 核对项 | **C · 废弃链与枚举取值**（① 官方标 Obsolete 的成员；② 字面量当枚举/取值传时，对 `enums/*.md` 查该值是否合法成员） |
| 我们这边读的文件（9 个，全部存在） | `scripts/sw_export.py` · `sw_review.py` · `sw_document_data.py` · `sw_ref_geometry.py` · `sw_helix.py` · `sw_loft.py` · `sw_sweep.py` · `sw_wrap.py` · `sw_gtol.py` |
| 官方源 | `C:\swapi\types\<接口>\<成员>.md`（首行有无 `Obsolete.` 横幅 + 形参表）· `C:\swapi\enums\*.md`（成员表 Value 列）· `C:\swapi\types\IFeatureManager\CreateDefinition.md`（合法常量清单）· `IPartDoc\ExportToDWG2.md` 的 Remarks 位掩码表 |

## 发现（10 条）

| # | 我们的原文（文件 + 片段） | 官方的原文（文件 + 片段） | 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | `scripts/sw_export.py`（`_export_generic`）：`success = model.Extension.SaveAs(`<br>`scripts/sw_export.py`（`export_to_pdf`）：`success = model.Extension.SaveAs(str(output_path), 0, 1, pdf_data, errors, warnings)` | `C:\swapi\types\IModelDocExtension\SaveAs.md`：`Obsolete. Superseded by [[IModelDocExtension::SaveAs2]].` | 我们两条导出路径（通用导出 + PDF 导出）都调 `IModelDocExtension.SaveAs`，官方该页正文第一行即标 `Obsolete` 并点名后继为 `SaveAs2`。 | 高 |
| 2 | `scripts/sw_export.py`（`export_to_stl`）：`model.SetUserPreferenceIntegerValue(78, quality_map[quality])  # swSTLQuality` | `C:\swapi\types\IModelDoc2\SetUserPreferenceIntegerValue.md`：`Obsolete. Superseded by [[IModelDocExtension::SetUserPreferenceInteger]].` | 我们调的是 `IModelDoc2` 上那个设置整数首选项的成员，官方标 `Obsolete`、后继在 `IModelDocExtension` 上。 | 高 |
| 3 | `scripts/sw_export.py`（`get_mass_property_override_options`）：`mass_property = get_com_member(extension, "GetMassProperties", float(accuracy))` | `C:\swapi\types\IModelDocExtension\GetMassProperties.md`：`Obsolete. Superseded by [[IModelDocExtension::GetMassProperties2]].` | 我们取的 `IMassProperty2` 对象来自官方标 `Obsolete` 的 `GetMassProperties`；同一函数 docstring 里已经点名后继是 `GetMassProperties2`，但调用仍走旧成员。 | 高 |
| 4 | `scripts/sw_export.py`（`_activate_source_document` 的 except 分支）：`sw.ActivateDoc2(title, False, errors)`<br>同函数内 DumbDispatch 分支：`dynamic_sw.ActivateDoc2(title, False, errors)` | `C:\swapi\types\ISldWorks\ActivateDoc2.md`：`Obsolete. Superseded by [[ISldWorks::ActivateDoc3]].` | 降级分支调用 `ISldWorks.ActivateDoc2`，官方标 `Obsolete`、后继为 `ActivateDoc3`（同函数第一分支已经在用 `ActivateDoc3`）。 | 高 |
| 5 | `scripts/sw_export.py`（`export_to_stl`）：`quality_map = {"coarse": 1, "fine": 0}` | `C:\swapi\enums\swSTLQuality_e.md`：<br>`\| swSTLQuality_Coarse \| 1 \|`<br>`\| swSTLQuality_Custom \| 3 \|`<br>`\| swSTLQuality_Fine \| 2 \|` | `swSTLQuality_e` 的成员只有 1 / 2 / 3；我们给 `"fine"` 映射的字面量 **0 不是该枚举的任何成员**（`"coarse": 1` 与官方一致）。 | 高 |
| 6 | `scripts/sw_review.py`（`zoom_to_fit`）：`get_com_member(model, "GraphicsRedraw2")`<br>`scripts/sw_review.py`（`clear_selection_for_preview` 收尾）：`get_com_member(model, "GraphicsRedraw2")` | `C:\swapi\types\IModelDoc2\GraphicsRedraw2.md`：`Obsolete. Superseded by [[IModelView::GraphicsRedraw]] and [[IModelView::IGraphicsRedraw]].` | 我们两处重绘都走 `IModelDoc2.GraphicsRedraw2`，官方标 `Obsolete`、后继改在 `IModelView` 上。 | 高 |
| 7 | `scripts/sw_review.py`（`activate_model_for_preview` 的 except 分支）：`sw.ActivateDoc2(title, False, errors)` | `C:\swapi\types\ISldWorks\ActivateDoc2.md`：`Obsolete. Superseded by [[ISldWorks::ActivateDoc3]].` | 同 #4 的成员，换了个文件：`sw_review.py` 的降级分支也调官方标 `Obsolete` 的 `ActivateDoc2`。 | 高 |
| 8 | `scripts/sw_document_data.py`（`_dimension_value_mm`）：`return float(dimension.GetSystemValue2(configuration_name)) * 1000.0` | `C:\swapi\types\IDimension\GetSystemValue2.md`：`Obsolete. See [[IDimension::GetSystemValue3]] and [[IDimension::IGetSystemValue3]].` | 取指定配置下的系统值走 `GetSystemValue2`，官方标 `Obsolete` 并指向 `GetSystemValue3`。 | 高 |
| 9 | `scripts/sw_document_data.py`（`_dimension_value_mm`）：`return float(get_com_member(dimension, "SystemValue")) * 1000.0` | `C:\swapi\types\IDimension\SystemValue.md`：`Obsolete. Superseded by [[IDimension::GetSystemValue3]], [[IDimension::IGetSystemValue3]], [[IDimension::SetSystemValue3]], and [[IDimension::ISetSystemValue3]].` | 读“当前配置”系统值走 `IDimension.SystemValue` 属性，官方标 `Obsolete`、后继是 `GetSystemValue3` 一族。 | 高 |
| 10 | `scripts/sw_wrap.py`：`WRAP_MESH_FACTOR_DEFAULT = 0`（作为第 5 个实参传给 `InsertWrapFeature2`：`WRAP_TYPES[key], thickness_m, bool(reverse),` / `WRAP_METHOD_DEFAULT, WRAP_MESH_FACTOR_DEFAULT)`） | `C:\swapi\types\IFeatureManager\InsertWrapFeature2.md`：`- **MeshFactor**: Accuracy of flattened triangle mesh; 1 (lowest) - 10 (highest)` | 官方把 `MeshFactor` 的合法取值范围写死为 **1–10**；我们传的字面量 **0 落在该范围之下**。（第 4 参 `Method` 我们传 `0`，官方 `C:\swapi\enums\swWrapMethods_e.md` 的 `\| swWrapMethods_Analytical \| 0 \|` 是合法成员，故不报。） | 高 |

## 查不到（按铁律 5 记「查不到」，不判定、不入表）

| 我们的写法 | 官方侧情况 | 处置 |
|---|---|---|
| `sw_export.py`：`SetUserPreferenceIntegerValue(78, …)` 里的 **78** | `C:\swapi\enums\swUserPreferenceIntegerValue_e.md` 的 Value 列写的是 `See [System Options and Document Properties.]`，**不是数值**；`C:\swapi\docs\Programming with the SOLIDWORKS API\System Options and Document Properties.md` 全文也查不到 `swSTLQuality` | 两套离线源都查不到 78 的出处 ⇒ 不判定（#5 只报同行的 `swSTLQuality_e` 取值，不涉及 78） |
| `sw_sweep.py`：`SW_FM_SWEEP = 17` · `SW_FM_SWEEP_CUT = 18` · `SW_FM_REF_SURFACE = 62` | `C:\swapi\enums\swFeatureNameID_e.md` 的 Value 列也是说明文字（`\| swFmRefSurface \| Reference or sweep surface \|`），无数值 | 数值查不到 ⇒ 不判定。只在 `C:\swapi\types\IFeatureManager\CreateDefinition.md` 的合法常量清单里核到**名字**存在：`swFmRefSurface (surface sweep)` · `swFmSweep (boss sweep)` · `swFmSweepCut (cut sweep)` |
| `sw_review.py`：`get_com_member(model, "ViewZoomtofit2")` | `C:\swapi\types\` 全目录按名递归检索 `ViewZoomtofit2` / `ViewZoomToFit2` ⇒ **一处都没有** | 名字查不到 ⇒ 不判定（属核对 A/B 的范围，本表不收） |
| `sw_wrap.py` 注释：`★ 官方那两个参数在本文件里**没有查到取值表** ⇒ ★ 按铁律 5 处理：**不猜**` | `C:\swapi\types\IFeatureManager\InsertWrapFeature2.md` 写明 `- **Method**: Type of wrap method as defined in [[swWrapMethods_e]]`，且 `C:\swapi\enums\swWrapMethods_e.md` 存在并有 2 个成员 | 这是**注释与官方页存在性**的文字出入（不是调用行为分歧）；传的 `0` 本身合法 ⇒ 不入表，仅记此备注 |

## 本轮核过、判定为**一致**的字面量/枚举（不报，仅留痕）

`swHelixDefinedBy_e` 0/1/2/3 · `swWrapSketchType_e` 0/1/2 · `swWrapMethods_e` 0 · `swRefPlaneReferenceConstraints_e`（1/4/8/16/128/256/512/**1028**/**2056**/8192）· `swRefPointType_e` 0–7 · `swRefPointAlongCurveType_e` 0/1/2 · `swGlobalBoundingBoxFitOptions_e` 1/2/3 · `swGlobalBBoxLWTADirectionType_e` 0 · `swGlobalBoundingBoxResult_e` 0/1/2 · `swExportToDWG_e` `ExportSheetMetal=1` · `ExportToDWG2` 14 位掩码（1/2/4/8/16/32/64/2048 与我们 8 个常量逐位一致）· `swExportDataFileType_e` `swExportPdfData=1` · `swSaveAsOptions_e` `Silent=1` · `swCustomInfoType_e` 3/5/11/30/64 · `swCustomPropertyAddOption_e` `ReplaceValue=2` · `swCustomInfoAddResult_e` `AddedOrChanged=0` · `swSetValueInConfiguration_e` 1/2/3 · `swSetValueReturnStatus_e` 0–5 · `swGtolIndicatorBorderType_e` 0–3 · `swGtolGeomCharSymbol_e` 12–30 · `swGuideCurveInfluence_e` 0 · `swStandardViews_e` 1–9 · `swBodyType_e` `swSolidBody=0` · `swDocumentTypes_e` `swDocDRAWING=3`。

## 三行收尾

- **都核了几处**：官方 COM 成员页 **82** 处（逐页读首行 `Obsolete.` 横幅）+ 官方枚举/位掩码页 **26** 处，合计 **108** 处；其中 4 处判为「查不到」已单列、不判定。
- **报了几条**：**10** 条（#1–#10，全部为「两段原文对不上」，无一条含推测）。
- **哪几条置信度为高**：**#1–#10 全部为高**（每条的两段原文都是逐字可搜的官方原文，无一处靠推断）。