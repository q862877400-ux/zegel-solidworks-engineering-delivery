# JUDGE-C_D-E · C/D/E 三组合成总表 · 抽查证伪 · 分级

> ★ **本组范围**：`recon/verify50/` 下 **C-\* / D-\* / E-\* 共 14 份对账稿**
> `vd50-C-dw-1/2/3` · `vd50-C-sm-1/2/3` · `vd50-D-2` · `vd50-D-3` · `vd50-E-1/2/3/4/5/6`。
> ★ **纪律**：只读 + 只写本文件（未改仓内任何其他文件）· 每条保留**两段原文**（仓内段 / 官方段，均为可搜索片段，**不写行号**）· 查不到就说查不到 · 宁少勿滥。
> ★ **判定口径沿用各稿自述**（注意 C 组与 D/E 组的「成立 / 不成立」语义**方向相反**，本表统一改写为中性词）：
> - **确认** = 该稿声称的「对不上」经原文逐字比对**站得住**（原表里的「成立」或部分「不成立」）
> - **驳回** = 「对不上」不成立（原表里的「核对一致」或「不成立（仓内正确）」）
> - **存疑** = 两段原文本身互不一致、或一方缺可引原文
> - **查不到** = 官方或仓内任一侧没有可引的第二段原文

---

## 〇 · 本组总计

| 片 | 核了几处 | 对不上几处 | 口径备注 |
|---|---|---|---|
| `C-dw-1` 工程图视图族 | 5 | **4** | 另 1 处「核对一致」 |
| `C-dw-2` 工程图尺寸/公差/GD&T/粗糙度/基准/气泡 | 9 | **5** | 另记 4 条「查不到」，不计 |
| `C-dw-3` 工程图 BOM/孔表/图纸格式/PDF·DXF/图层 | 23 | **7** | 成立 11 · 存疑 3 · 查不到 5 |
| `C-sm-1` 钣金：基体/边线/斜接/闭合角 | 14 | **6** | 另 8 处「核过无问题」 |
| `C-sm-2` 钣金：展开/折弯/切口/成形工具/参数 | 9 | **6** | — |
| `C-sm-3` 钣金：镜像/阵列/转角/平板型式/导出 | 7 | **5** | — |
| `D-2` GATE-FINAL C5–C8 仓内锚点 | 4 判据 / 15 锚点 | **1** | 1 条铁的（C8） |
| `D-3` GATE-FINAL C9–C12 + R 锚点 | 26 | **1** | 另 1 条「查不到」 |
| `E-1` tool_specs batch1–15 doc↔目标 | 54 | **11** | 成立 10 + 存疑 1 |
| `E-2` tool_specs batch16–30 doc↔目标 | 58 | **4** | 成立 3 + 存疑 1 |
| `E-3` tool_specs batch31–45 doc↔目标 | 84 | **7** | 成立 6 + 存疑 1 |
| `E-4` tool_specs batch46–60 doc↔目标 | 67 | **6** | 成立 4 + 存疑 2 |
| `E-5` tool_specs batch61–75 doc↔目标 | 60 spec / 33 判据承诺 | **11** | 11 个工具 / 6 类 |
| `E-6` tool_specs batch76 doc↔目标 | 4 | **4** | 成立 2 + 存疑 2 |
| **合计** | **435 处** | **73 条** | — |

★ 「核了几处」的单位在各稿之间不完全一致（有的按 ToolSpec 条数、有的按可判定点数、有的按锚点数），加总只作规模参考，不作同质指标。

---

# 一 · 合成总表（★ 每条保留两段原文）

## C-dw-1 · 工程图「视图」族（4 条对不上）

| # | 主题 | 仓内原文（逐字） | 官方原文（逐字） | 本表判定 |
|---|---|---|---|---|
| C1-1 | 断裂视图只调 `InsertBreak3` | `scripts/sw_drawing_create_missing.py`：`"断裂视图": "IView.InsertBreak3（★ InsertBreak / InsertBreak2 都标 Obsolete）",` ／ 覆盖矩阵 `\| 工程图 \| 断裂视图 \| ✅ \| ✅ \|` | `IDrawingDoc\BreakView.md`：`Breaks the drawing view along the existing break lines.` ／ `Then, call this method to create the break view.` ／ `CreateBreakOutSection.md`：`Creates a broken-out section in a drawing document.` | **确认** |
| C1-2 | 三视图 `blocked` 与自家反射索引打架 | `drawing_workflow.py`：`method = getattr(drawing_model, method_name, None)` ／ `"error_code": "DRAWING_PROJECTION_API_UNAVAILABLE",` ／ `sw_api_sldworks.py`：`'Create1stAngleViews2': 1,` | `IDrawingDoc\Create1stAngleViews2.md`：`System.bool Create1stAngleViews2( System.string ModelName )` | **存疑**（争的是「本机 COM 上在不在」，未上真机） |
| C1-3 | 剖面视图传空 `SectionLabel`、无 `SetLabel2` | `def add_section_view(drawing_model, x, y):` / `return drawing_model.CreateSectionViewAt5(x, y, 0, "", 0, None, 0)` | `CreateSectionViewAt5.md`：`- **SectionLabel**: Letter for the label for the section view` ／ `swSectionView.SetLabel2 "ABCD"`（官方例子） | **确认** |
| C1-4 | 辅助视图 `NotAligned` | `sw_drawing_create_missing.py`：`not_aligned: bool = True,` ／ 调用处 `bool(not_aligned), str(label), bool(show_arrow), bool(flip),` | `CreateAuxiliaryViewAt2.md`：`- **NotAligned**: True aligns the view from its owner, false does not` ／ `swCreateSectionViewAtOptions_e.md`：`swCreateSectionView_NotAligned \| 1 or 0x1; If set, then the section does not snap into alignment with the parent view` | **确认（官方自相矛盾）** |
| C1-5 | 局部视图两个枚举字典 | `DET_VIEW_STYLES = {"standard": 0, …}` ／ `DET_CIRCLE_SHOW_TYPES = {"profile": 0, …}` | `swDetViewStyle_e.md`（5 项 0–4）· `swDetCircleShowType_e.md`（3 项 0–2） | **驳回**（逐项对得上） |

## C-dw-2 · 尺寸 / 公差 / GD&T / 粗糙度 / 基准 / 气泡（5 条对不上）

| # | 主题 | 仓内原文（逐字） | 官方原文（逐字） | 本表判定 |
|---|---|---|---|---|
| C2-1 | `GetText(0)` 当全文本 | `drawing_workflow.py`：`for index, label in ((0, "all"), (1, "prefix"), …)` ／ `all_text = next((item["text"] for item in parts if item["kind"] == "all"), "")` | `IDisplayDimension\GetText.md`：`swDimensionTextParts_e.swDimensionTextAll is not a valid value for the WhichText parameter for this method.` ／ 枚举：`swDimensionTextAll \| 0 = Entire dimension text string ([[IDisplayDimension::SetText]] only)` | **确认** |
| C2-2 | 兜底调 `Obsolete` 成员 | `text_format = _safe_member(annotation, "GetTextFormat", 0)` ／ `text_format = _safe_member(display_dimension, "GetTextFormat")` | `IDisplayDimension\GetTextFormat.md`：`Obsolete. Superseded by [[IAnnotation::GetTextFormat]].` | **确认**（主路径已走对后继，兜底那支未改） |
| C2-3 | 通用公差表类型号写成 6 | `TABLE_ANNOTATION_KINDS = { 0: "general", … 5: "title_block", 6: "general_tolerance", }` | `swTableAnnotationType_e.md`：`swTableAnnotation_GeneralTolerance \| 9` ／ `swTableAnnotation_WeldTable \| 6` | **确认**（真通用公差表 Type=9 会被打成 `unknown`） |
| C2-4 | `AddIndicator` 五值清单 | `GTOL_INDICATOR_ALLOWED_TOL_TYPES = { 20: "angularity", 22: "parallelism", 21: "perpendicularity", 25: "circular_runout", 13: "symmetry", }` | `IGtolFrame\AddIndicator.md`：`TolType may be one of only swGtolGeomCharSymbol_e.: swGcsANG / swGcsPARALLEL / swGcsPERP / swGcsCIRCRUNOUT / swGcsSYMMETRY` | **驳回**（完全对得上） |
| C2-5 | 0 基读 GTol 帧 | `for index in range(frame_count)` ／ `GetFrameSymbols3` · `GetFrameValues` | `IGtol\GetFrameSymbols3.md`：`- **FrameNumber**: Frame number to examine (1 or 2)` ／ `This method is valid only if this Gtol was created in a version of SOLIDWORKS earlier than 2022.` ／ `GetFrame.md`：`- **FrameIndex**: One-based index of Gtol frame to retrieve` | **确认**（第 0 次调用越界 + 用错年代读法） |
| C2-6 | `leaderType == swNO_LEADER` 传 0,0,0 | `location_applied = int(leader_type) != SW_LEADER_NO_LEADER` ／ `"official_remark_verbatim": ("…only if the surface finish symbol has a leader leaderType != swNO_LEADER.")` | `InsertSurfaceFinishSymbol3.md`：`The SOLIDWORKS Design software uses the location parameters for this method only if the surface finish symbol has a leader leaderType != swNO_LEADER.` | **驳回**（与契约一致） |
| C2-7 | 读粗糙度先调 `Obsolete` 的 `GetSymbolType` | `"symbol_type": _safe_member(owner, "GetSymbolType", default=None), "symbol": _safe_member(owner, "GetSymbol", default=None),` | `ISFSymbol\GetSymbolType.md`：`Obsolete. Superseded by [[ISFSymbol::GetSymbol]].` | **确认** |
| C2-8 | `InsertDatumTag2()` 零参 | `"""…`IModelDoc2.InsertDatumTag2()` → `DatumTag`（★ **零参**）。` | `System.object InsertDatumTag2()` ／ `Inserts a datum tag symbol at a selected location.` ／ 例子先 `SelectByID2("", "EDGE", …)` | **驳回**（对得上） |
| C2-9 | `AutoBalloon5` 四步序 | `opts = get_com_member(model, "CreateAutoBalloonOptions")` ／ `notes = get_com_member(model, "AutoBalloon5", opts)` | `AutoBalloon5.md` 四步 `1. Select one or more views or sheets… 2. Call [[IDrawingDoc::CreateAutoBalloonOptions]]… 4. Call this method using the IAutoBalloonOptions object…` | **驳回**（对得上） |

## C-dw-3 · BOM / 孔表 / 图纸格式 / PDF·DXF / 图层（7 条对不上）

| # | 主题 | 仓内原文（逐字） | 官方原文（逐字） | 本表判定 |
|---|---|---|---|---|
| C3-4 | `ISheet.GetBomTable` 后继名拼写 | `audit_gap_implementations.py`：`"工程图/孔表": ["InsertHoleTable2", "InsertHoleTable"]`（同类配对写法） | `ISheet\GetBomTable.md`：`Obsolete. Superseded by [[IView::GetBOMTable]].` ／ `IView\GetBomTable.md` front-matter：`member: GetBomTable` | **存疑**（官方同一族两处拼法不一致）★**已复核** |
| C3-5 | `IView.GetBomTable` 当「有没有 BOM 表」判据 | `prove_drawing_batch.py`：`bom = _get(view, "GetBomTable") if view is not None else None` ／ `row["preconditions_held"] = bool(bom is not None)` | `IView\GetBomTable.md`：`This method only returns a BOM table if there is a Microsoft Excel-based BOM for the drawing view.` | **确认** |
| C3-7 | 锚点枚举拼写两样 | —（仓内无引用段） | `InsertRevisionTable2.md` · `InsertTableAnnotation2.md` 写 `[[swBOMConfigurationAnchorType_e]]`；`InsertBomTable6.md` · `InsertHoleTable3.md` 写 `[[swBomConfigurationAnchorType_e]]` | **存疑**（两样确实并存）★**但原稿的支撑句有一处硬性事实错误，见 §三.3** |
| C3-13 | `ISheet.GetProperties` 自称 seven 却列 8 项 | `sw_drawing_query.py` 文档串：`` `[paperSize, templateIn, scale1, scale2, firstAngle, width, height, sameCustomPrp]` `` | `ISheet\GetProperties.md`：`The return value is the following array of seven doubles:` 紧跟方括号列 **8** 项 | **存疑**（官方旧页自相矛盾） |
| C3-20 | `SetSheets(0, …)` | `sw_export.py`：`pdf_data.SetSheets(0, sheet_names)` | `swExportDataSheetsToExport_e.md` 成员表只有 `1 / 2 / 3`（**无 0**）／ 官方例子传 `swExportData_ExportSpecifiedSheets` ／ `SaveAs3.md`：`If ExportData is Nothing or null, then all sheets are saved to PDF` | **确认** |
| C3-21 | PDF 出口压在被废弃成员上 | `sw_export.py`：`success = model.Extension.SaveAs(str(output_path), 0, 1, pdf_data, errors, warnings)` ／ `sw_com_traps.py`：「**本项目导出/保存一律用 `SaveAs3`**」 | `IModelDocExtension\SaveAs.md`：`Obsolete. Superseded by [[IModelDocExtension::SaveAs2]].` ／ `SaveAs2.md`：`Obsolete. Superseded by [[IModelDocExtension::SaveAs3]].` | **确认**（且仓内两处自相矛盾） |
| C3-22 | 「`SaveAs4` 不存在」 | `sw_com_traps.py`：「`SaveAs=4 · SaveAs2=6 · SaveAs3=5` · **SaveAs4 不存在**」／ `sw_api_sldworks.py` `ARITY` 的 `IModelDoc2` 段有 `'SaveAs4': 3,` | `IModelDoc2\SaveAs4.md`：`System.bool SaveAs4( System.string Name, System.int Version, System.int Options, out System.int Errors, out System.int Warnings )` ／ 官方 DXF 例子：`bRet = swModel.SaveAs4(sPathName, …)` | **确认**（该句只对 `IModelDocExtension` 成立，不带接口限定就是错的） |

## C-sm-1 · 钣金四特征（6 条对不上）

| # | 主题 | 仓内原文（逐字） | 官方 / 目标原文（逐字） | 本表判定 |
|---|---|---|---|---|
| V-1 | 基体法兰 开放/闭合 自相矛盾 | `tool_specs_batch3.py`：`An open polyline path produces a profile flange; a closed contour produces a flat plate.` ／ `sw_sheet_metal.py::SHEET_METAL_RUNTIME_STATUS`：`⚠ **开放折线（轮廓法兰）真机失败**：CreateFeature(IBaseFlangeFeatureData) 创建失败` … `⇒ **True` 仅对闭轮廓成立` | `IFeatureManager\InsertSheetMetalBaseFlange.md`：`Obsolete. Superseded by [[IFeatureManager::InsertSheetMetalBaseFlange2]].`（官方对开放/闭合**无任何前置说明**） | **确认**（仓内两处互斥） |
| V-2 | `verified` 的 evidence #1 不碰 COM | `capabilities.yaml`：`"id": "sheet_metal", … "level": "verified", … "evidence": [ "pytest tests/test_sw_sheet_metal.py",` | `tests/test_sw_sheet_metal.py`：`from sw_sheet_metal import BaseFlangeSpec  # noqa: E402` ＋ 三个用例名（只测 `export_flat_pattern_dxf` 对 `FakePart` 替身 + `BaseFlangeSpec.validate()`） | **确认** |
| V-3 | evidence #2 按字面收 0 个用例 | `"pytest tests/solidworks_sheet_metal_regression.py（钣金）"` | 该文件模块骨架：`def _validate_evidence(...)` / `def run_regression(...)` / `def main() -> int:` ／ `if __name__ == "__main__":` —— **全文无 `def test_`** | **确认** |
| V-4 | 边法兰工具契约报已修缺陷 | `tool_specs_batch4.py`：`it FAILED with: setting `ReverseDirection` gave `Property ... can not be set`. The correct call shape has not been determined yet` | `capabilities.yaml` limitations：**已修掉的缺陷**… `create_edge_flange` 的 `ReverseDirection` 跨接口泄漏` ／ 状态表：`报错已从 `Property ... can not be set` 变为 `CreateFeature(37) 创建失败`` | **确认** ★**已复核** |
| V-5 | `recon/sheetmetal.md` 把有入口的记成「官方没写」 | `\| 斜接法兰 \| 官方没写 \| 官方没写 \| 无 \| 无 \| — \|` ／ `\| 闭合角 \| 官方没写 \| 官方没写 \| 无 \| 无 \| — \|` | `IFeatureManager\InsertSheetMetalMiterFlange.md`：`Inserts a meter flange in a sheet metal part.` ／ `IModelDoc2\InsertSheetMetalClosedCorner.md`：`Inserts a sheet metal closed corner into this model document.` | **确认**（且本仓自己已实现这两个入口） |
| V-6 | 斜接/闭合角已挂 MCP、台账零引用 | `register_capabilities.py`：`"tool_specs_batch74",` ／ `tool_specs_batch74.py`：`name="solidworks_sheet_metal_insert_miter_flange",` `name="solidworks_sheet_metal_insert_closed_corner",` | `capabilities.yaml` 对两工具名 **0 命中** ／ `scan-S2a-tools-not-in-ledger.md`：`| 257 | … | tool_specs_batch74.py | 0 |` | **确认（但属仓内已自记的未清项）** |

## C-sm-2 · 展开 / 折弯 / 切口 / 成形工具 / 参数（6 条对不上）

| # | 主题 | 仓内原文（逐字） | 官方原文（逐字） | 本表判定 |
|---|---|---|---|---|
| S2-1 | `export_to_dxf` 把任何零件按展开导出 | `sw_export.py`：`if doc_type == 3:  # 工程图 / return _export_generic(...)` ／ `else: return export_flat_pattern_dxf(model, output_path)` ／ 唯一守卫：`if not model_path: raise ValueError("导出展开 DXF 前必须先保存钣金零件")` | `swExportToDWG_e.md`：`\| swExportToDWG_ExportSheetMetal \| 1; Valid only if the active document contains sheet metal \|` ／ `ExportToDWG2.md`：`SheetMetalOptions: … valid only if Action = …swExportToDWG_ExportSheetMetal` | **确认** |
| S2-2 | `swFmDraft(3)` 不在 `CreateDefinition` 名单 | `sw_sheet_metal.py`：`"CreateDefinition(3) 返回 None ⇒ **该类型不走 `CreateDefinition`**；" "正确入口未查明"` | `CreateDefinition.md` 的 35 条名单无 `swFmDraft`；`## Returns` 清单含 `[[sheet metal sketched bend]]` 不含任何 draft | **确认**（仓内断言与官方一致，是**如实记录**） |
| S2-3 | `create_one_bend` 无条件设 `BendRadius`、从不设 `UseGaugeTable` | `use_default_radius: bool = True` ／ `data.UseDefaultBendRadius = …` / `data.BendRadius = float(spec.bend_radius)` / `data.BendAngle = …` / `data.ReverseDirection = …` | `ISketchedBendFeatureData\BendRadius.md`：`This property is valid only if [[ISketchedBendFeatureData::UseDefaultBendRadius]] is false.` ／ `To use something other than the default bend radius, set: … [[ISketchedBendFeatureData::UseGaugeTable]] to false.` | **确认** |
| S2-4 | 切口 `ShowSlitInCornerRelief` 零实现 | `sw_api_sldworks.py` 的 `'IFlatPatternFeatureData'` 块内 `'ShowSlitInCornerRelief',`（反射抄录） | `IFlatPatternFeatureData\ShowSlitInCornerRelief.md`：`System.bool ShowSlitInCornerRelief {get; set;}` ／ `C:\swapi` 全库 `*Slit*` 只命中此一个文件 | **确认**（缺口） |
| S2-5 | 成形工具三入口零实现 | `sw_api_sldworks.py`：`'InsertFormToolFeature': 9,` `'CreateFormTool': 0,` `'CreateFormTool2': 2,` | `InsertFormToolFeature.md`：`Obsolete. Superseded by [[IFeatureManager::CreateDefinition]] and [[IFeatureManager::CreateFeature]].` ／ `CreateFormTool.md`：`Obsolete. Superseded by [[IFeatureManager::CreateFormTool2]].` ／ `ILibraryFormToolFeatureData\_overview.md` 六步现行链 | **确认**（缺口） |
| S2-6 | `ICustomBendAllowance.Type` 应最后设 | `bend_allowance.Type = SW_BEND_ALLOWANCE_K_FACTOR` ／ `bend_allowance.KFactor = float(spec.k_factor)`（Type 在前） | `ICustomBendAllowance\Type.md`：`If you do not set this property last, the ICustomBendAllowance property set last automatically overrides any previously set custom bend allowance type.` ／ `KFactor.md`：`the [[type of custom bend allowance]] is set to this type` | **存疑**（两段官方原文互相抵消） |

## C-sm-3 · 镜像 / 阵列 / 转角 / 平板型式 / 导出（5 条对不上）

| # | 主题 | 仓内原文（逐字） | 官方原文（逐字） | 本表判定 |
|---|---|---|---|---|
| S3-1 | 出处标注写 `IModelDoc2.ExportToDWG2` | `sw_export.py` 来源块：`IModelDoc2.ExportToDWG2(..., swExportToDWG_e)（★ export_flat_pattern_dxf 走它）` | `IPartDoc\ExportToDWG2.md` front-matter `type: IPartDoc` ／ `IModelDoc2\*.md` 对 `ExportToDWG2` **0 命中** | **确认（仅出处标注层，不构成功能缺陷）** |
| S3-2 | 调官方 `Obsolete` 的两个阵列成员 | `sw_part.py`：`return model.FeatureManager.FeatureLinearPattern3(` ／ `return model.FeatureManager.FeatureCircularPattern4(` ／ `linear_pattern_report` 内 `"FeatureLinearPattern3", n1, s1, …` | `FeatureLinearPattern3.md`：`Obsolete. Superseded by [[IFeatureManager::FeatureLinearPattern4]].` ／ `FeatureCircularPattern4.md`：`Obsolete. Superseded by [[IFeatureManager::FeatureCircularPattern5]].` | **确认** ★**已复核** |
| S3-3 | `linear_pattern` 把毫米传给 `in meters` 的 `Spacing1` | `d1_*: 方向1 的方向向量、间距（**毫米**，…）` ／ `FeatureLinearPattern3(int(d1_count), float(d1_spacing), …)` ／ 同仓 `linear_pattern_report`：`s1 = float(spacing_mm) * 0.001  #: ★ 毫米 ⇒ 米` | `FeatureLinearPattern3.md`：`- **Spacing1**: Spacing between each instance of the linear pattern in Direction 1 in meters` ／ `- **Spacing2**: … in meters` | **确认**（相差 1000 倍） |
| S3-4 | 展开入口零实现 | `sw_api_sldworks.py`：`'GetFlatPatternFolder': 0,` `'InsertSheetMetalUnfold': 0,` ／ `sw_capability_probe.py`：`"sheet_metal": ("ISheetMetalFeatureData", "IFlatPatternFeatureData"),` | `IModelDoc2\InsertSheetMetalUnfold.md`：`void InsertSheetMetalUnfold()` ／ `## Remarks`：`Select the objects for the unfold feature before calling this method.` | **确认**（缺口） |
| S3-5 | 转角处理三套入口零实现 | `sw_api_sldworks.py`：`'FinishCornerRelief': 0,` `'InsertSheetMetalCornerTrim': 5,` `'SetAddCornerTrim': 1,` `'SetBreakCorners': 1,` ／ 仓内可执行的钣金转角只有 `"钣金/斜接法兰"` 与 `"钣金/闭合角"` | `FinishCornerRelief.md`（5 步前置：`Mark = 0` 选体 / `Mark = 4` 选两面 / `AddCornerReliefCorner` / `AddCornerReliefType`）· `InsertSheetMetalCornerTrim.md`（5 参）· `IFlatPatternFeatureData\SetBreakCorners.md`：`void SetBreakCorners( System.bool BBreakCorner )` | **确认**（缺口） |

## D-2 · GATE-FINAL C5–C8 仓内锚点（1 条对不上）

| # | 主题 | 目标（判据）原文（逐字） | 仓内原文（逐字） | 本表判定 |
|---|---|---|---|---|
| D2-1 | C8 唯一判据要读的台账不存在 | C8 唯一判据：`docs/refuted-patterns.json` 里每条的 `anchor_quote` **必须逐字出现在 `docs/known-facts.md` 中** | 全仓 `**/refuted-patterns*` **0 命中**；文本搜索命中全是散文（GATE-FINAL 自身 + `gate-cand-C-loop.md`）；`docs/judge-registry.json` ✔ 存在 · `docs/gate-classification.json` ✔ 存在 · **唯独没有 `docs/refuted-patterns.json`** | **确认**（这条闸今天没有可读对象，`E9_LEDGER_DIVERGED` 永远产生不出来） |

★ C5（4 锚点）/ C6（4 锚点）/ C7（4 锚点）各锚点均逐字命中，**不判为问题**（含一处引文加粗星号出入，原稿已如实标注）。

## D-3 · GATE-FINAL C9–C12 + R（1 条对不上 + 1 查不到）

| # | 主题 | 判据原文（逐字） | 仓内原文（逐字） | 本表判定 |
|---|---|---|---|---|
| D3-1 | C11 括注「全仓提及只有 3 处」 | `★ 而它**没有门禁引用、没有测试**（★ 全仓提及只有 **3** 处 markdown 叙述）` | `recon/PROMPT-B-batch-generator.md`：`（分类器：`tools/classify_audit_divergences.py`，★ **你可以直接跑它**）。` ／ `python tools/classify_audit_divergences.py      # 30 份核对表的分歧分类` ／ 实测 4 文件 11 处（连 GATE-FINAL 与下游产物计入则 20 处 / 6 文件） | **确认**（但主结论「`tests/`+`scripts/` 0 命中 ⇒ 无门禁无测试」仍成立） |
| D3-2 | 「被改写之前」的读数 | `从 at=23:29:01 · 644 文件 · 671 行 · 870 次 被重写为 …` | `git ls-files --error-unmatch output/obsolete-usage-in-repo.json` → `did not match any file(s) known to git` ／ `git check-ignore -v` → `.gitignore:120:output/` | **查不到**（「之后」那四个数逐个对上；「之前」无 git 历史、无备份） |

## E-1 · batch1–15 工具 doc ↔ 目标函数（11 条对不上）

| # | 工具 | 仓内（spec doc）原文 | 目标原文 | 本表判定 |
|---|---|---|---|---|
| E1-1 | `sheet_metal_create_one_bend` | `it FAILED with: CreateDefinition(33) returned None. The correct call shape has not been determined yet` | 状态表：`正确入口是 swFmSketchBend(35)（**已改用**）` …`原记法：CreateDefinition(33) 返回 None ⇒ 不走 CreateDefinition` | **确认** |
| E1-2 | `sheet_metal_create_edge_flange` | `it FAILED with: setting ReverseDirection gave Property ... can not be set.` | `_apply` 注释：`⛔ 原代码在此设 data.ReverseDirection —— **该属性不属于本接口**。` ／ 状态表：`报错已从 Property ... can not be set 变为 CreateFeature(37) 创建失败` | **确认** ★**已复核** |
| E1-3 | `sheet_metal_create_gusset` | `it FAILED with: setting Thickness gave Property ... can not be set.` | `data.GussetThickness = float(spec.thickness)  # 原 Thickness（焊件名）` ／ `改用 GussetThickness/ProfileHeightDim/… 后真机读回全部成功；报错已变为 CreateFeature(118) 创建失败` | **确认** |
| E1-4 | `sheet_metal_create_base_flange` | `An open polyline path produces a profile flange; … it WORKED` | `⚠ **开放折线（轮廓法兰）真机失败**… ⇒ **True 仅对闭轮廓成立**` | **确认** |
| E1-5 | `topology_run` | `Mesh and solve the topology study and **report whether results exist**.` | `"""建网格并求解。返回 ``RunAnalysis`` 的结果码。"""` ／ 函数体末句即 `return code` | **确认** |
| E1-6 | `topology_create_study` | Param：`Study name; **a study with the same name is deleted first**.` | `常见原因见 swsStudyError_e：1=无实体、**2=同名研究已存在**或名称非法…` ／ 函数体**全程无任何删除调用** | **确认** |
| E1-7 | `weldment_evidence` | `**Read-only when create_missing_cut_list is False.**` | `if create_missing_cut_list: ensure_cut_list(model)` ／ `folders = update_cut_list(model)`（**无条件**）→ `UpdateCutList` 是写操作 | **确认** |
| E1-8 | `simulation_default_element_size_and_tolerance` | `Get the suggested element size and tolerance (**millimetre-scale when units=-1**).` | `当时的实测：NUnits=-1 ⇒ **4.9339 / 0.2467**（毫米）… 本次的实测：units=-1 ⇒ **4930.50 / 246.53**` ／ `同一个 units 值两次差**恰好 1000 倍** ⇒ … **具体原因未查清**` | **确认** |
| E1-9 | `mold_evidence` | `Read back the mold state of the active part: parting-line/surface and cavity/core surface counts…` | `⚠ **本函数当前仍从旧位置读** ⇒ 它**在真机上只会返回全 None**` | **确认** |
| E1-10 | `sheet_metal_create_draft` | `Param("depth_mm", float, description="Draft depth in MILLIMETRES.")` ／ 同 doc 已为 `face_ref` 写「accepted but NEVER USED」却**唯独没提 `depth_mm`** | `create_draft._apply` 只设 `data.Angle` 与 `data.ReverseDirection`；`depth` 仅被 `DraftFeatureSpec.validate()` 读一次 | **确认** ★**已复核** |
| E1-11 | `mold_undercut_detect` | `…pops the modal 「此拔模方向尚未定义。」on a part without one, **stalling the session**.` | `b_coord_input: bool = True` ／ `⇒ ★ **根因解决**：默认 b_coord_input=True + 非零方向 (0,0,1) ⇒ **从根上不弹框**` | **存疑**（doc 也可读成在讲旧参数名的往事） |

## E-2 · batch16–30（4 条对不上）

| # | 主题 | 仓内原文（逐字） | 目标原文（逐字） | 本表判定 |
|---|---|---|---|---|
| E2-1 | batch21 批头称 `x1_mm` 在黑名单 | `对外用语义名 + __mm —— start_x_mm / … （而不是 x1_mm，⚠ 那个**在黑名单里**）` ／ `_BARE_COORD_NAMES 只查参数字面名（x / y / z / x_mm / y_mm / z_mm / point / coordinate）` | `tool_registry.py`：`_BARE_COORD_NAMES = {"x", "y", "z", "point", "coordinate"}` ／ `if low.endswith("_mm"): return False` ／ `tests/test_rule3_bare_coord_boundary.py`：`for nm in ("x", "y", "z", "x1", "y2", "cx", …): assert _flagged(nm)` | **确认**（三条子断言逐条不成立） |
| E2-2 | batch30 批头列 `iteration_count` | `★ mass_reduce_percent / iteration_count —— …` | `def set_topology_iteration_options_report(study, *, iteration_option=None, iteration_limit=None)` ／ `形参名是 **iteration_limit**（★ 不是我最初写的 iteration_count）—— 真机一调就报 unexpected keyword argument` | **确认** |
| E2-3 | `revolve_boss` doc ⚠ 指向 `known-facts` | `doc="Revolve a profile sketch into a boss feature. ⚠ This call is routed through a closed-source COM backend — see docs/known-facts.md."` | `docs/known-facts.md` 对 `闭源` / `closed-source COM` **0 命中** ／ 全仓 `closed-source` 只有 **2 处**（本 spec 自己 + `_all_specs.json` 快照） | **确认**（目标 docstring 讲的完全是另一件事：先轴后轮廓） |
| E2-4 | batch21 `::_consumed` 吞掉 `*names` | `"""这些入参由 param_alias 改名后传给目标函数（**不是**由 derived_args 消费）。"""` ／ `return {n: None for n in ()}  #: 占位：本批用改名而非消费，故不标 None` | batch17/18/23/26/29/30 的同名函数都是 `return {n: None for n in names}` 且都有调用点 | **存疑**（行内注释已自陈是占位） |

## E-3 · batch31–45（7 条对不上）

| # | 工具 | 仓内（spec doc）原文 | 目标原文 | 本表判定 |
|---|---|---|---|---|
| E3-1 | `sketch_mirror` | `★ The criterion is that the sketch entity count changes.` | `:returns: 新建的镜像实体数（回读草图的线段数变化无法可靠判定，故返回 True）。` ／ `model.SketchMirror()` / `return True` | **确认** |
| E3-2 | `convert_entities` | `Convert the selected model edges into the active sketch. ★ The criterion is that the sketch entity count changes.` | `got = get_com_member(skm, "SketchUseEdge3", bool(chain), bool(inner_loops))` ／ `return True` | **确认** |
| E3-3 | `gtol_insert` | `★ The criterion is that it returns an object and the feature tree changes.` | `gtol = call_com_member(model, "InsertGtol")` ／ `if gtol is None: raise RuntimeError(` ／ `return gtol` | **确认**（同批 `insert_helix` 反而有 `return _newest_feature_name(model)`） |
| E3-4 | `weldment_create_cut_list` | `Create the weldment cut list and return the cut-list folders as evidence.` | `feature = get_com_member(manager, "InsertWeldmentCutList2", sort_options)` ／ `return feature` | **确认**（回的是 COM `Feature`，不是 dict 也不是 folders） |
| E3-5 | `selector_resolve_point` | `Resolve a named point selector to its (x, y, z) coordinates in MILLIMETRES.` | `"""把**声明式点选择器**解析成 ``(x, y, z)``（**米**）。` ／ `if key == "bbox:min": return (xmin, ymin, zmin)`（**无 ×1000**） | **确认**（官方 `GetBodyBox.md` 未写单位 ⇒ 哪个对查不到，只报两段仓内自相矛盾） |
| E3-6 | `simulation_set_study_option(s)` | `★ Unknown family/name raises instead of being silently ignored.` | `except Exception as exc:  # noqa: BLE001` ／ `return {"ok": False, "family": family, "name": name, "error": …}` | **确认** ★**已复核** |
| E3-7 | `simulation_list_setter_summary` | `Return the catalogue of simulation study-option setters (family / name / type) as a ` | 函数体只回 `"total" / "boolean" / "names"`，**丢掉 type**（登记表 `STUDY_OPTION_SETTERS: dict[str, dict[str, str]]` 里有 type） | **存疑**（doc 那句是括注，`boolean` 计数可读成部分类型信息） |

## E-4 · batch46–60（6 条对不上）

| # | 工具 | 仓内（spec doc）原文 | 目标 / 官方原文 | 本表判定 |
|---|---|---|---|---|
| E4-1 | `sketch_add_slot` | `Param("radius_mm", float, description="槽口半径（即宽度的一半），毫米")` | `scripts/sw_part.py`：`CreateSketchSlot(0,  # Straight` / `radius, radius,  # 宽度` ／ 官方：`CreateSketchSlot( System.int SlotCreationType, System.int SlotLengthType, System.double Width, …)` ／ `swSketchSlotLengthType_e` 只有 2 个成员（0 / 1） | **确认**（长度 `radius` 塞进了枚举位；第 3 位才是 `Width`，差一个系数 2） |
| E4-2 | `simulation_apply_remote_load` | `Add a **REMOTE LOAD** … + _STATIC` ／ `_STATIC = ("★ **本载荷在「静力算例」下验证通过**…` | **同一文件**证据块：`remote_load  ✗ com_error(-2147352561, '非选择性的参数')` ／ `⚠★ **remote_load 不注册**：★ 报「缺必填参数」` | **确认**（文案被无差别套给三条载荷） |
| E4-3 | `simulation_apply_temperature` | 文件头：`⚠★ **temperature 仍不注册**：★ 报「缺必填参数」` ／ 证据块：`temperature ✗ com_error(-2147352561, '非选择性的参数。') ← ★ **缺必填参数**` | **同一文件**注册代码：`"solidworks_simulation_apply_temperature", "Apply a Temperature Load", "apply_temperature_report",` ／ `sw_simulation_loads.py`：`"AddTemperature": 1,` / `return _check(manager, "AddTemperature", 1, entities)` | **确认** ★**已复核** |
| E4-4 | `part_loft` | `★★ 判据（规则 6）：**特征树多了新特征**。` | `sw_loft.py`：`ok_type = (tname == "Blend") if tname else False` ／ `return {"ok": bool(new) and ok_type, …}` ／ 自报串：`判据 = **特征树多了新特征** 且 **特征类型名 = Blend**` | **确认**（doc 只承诺前一半；对照组 batch48 的扫描写全了两半） |
| E4-5 | `sketch_add_polygon` | `Param("radius_mm", float, description="内切圆半径，毫米")` ／ doc：`画正多边形（**内切圆**方式）` | 官方 `- **Xp**: X coordinate for a vertex` ／ `- **Inscribed**: True to show an inscribed construction circle, false to show a circumscribed construction circle` ／ 代码落点 `cx + radius` | **存疑**（差一个 `cos(π/n)`；但 `Inscribed=True` 也确实传了） |
| E4-6 | `part_sweep` | `⚠ AccessSelections 在本机报 0x80010105 … ★ 而**它非必需**：真机上它报错时特征仍建成` | `sw_sweep.py` 相邻两行：`**两路都卡在 AccessSelections**，★ 故「它不是必需的」这半句**至少在这套前置下不成立**；` ／ `⇒ ★ 所以它**不是必需的**；…` | **存疑**（目标函数自己撤回又自己断言回来） |

## E-5 · batch61–75（11 个工具 / 6 类对不上）

| # | 类 | 仓内（spec doc）原文 | 目标原文 | 本表判定 |
|---|---|---|---|---|
| E5-1 | batch67 移动/旋转/镜像/缩放（4 工具） | `★ 判据 = ModelToSketchTransform.ArrayData 的平移分量变化` ／ 改几何的 ⇒ `判据 = 草图线段端点的 bbox 变没变` | `sw_sketch_modify_ops.py`：`return {"ok": True, "op": "move", "verified_by": "no_exception", …}` / `{"ok": bool(r), "op": "scale", "verified_by": "return_value",` ／ `ModelToSketchTransform` 与 `ArrayData` 在该文件**各 0 次** | **确认** |
| E5-2 | batch72 孔向导 | `★ 判据 = **特征树增量**（★ 真机新增 异型孔向导）。` | `sw_hole_features.py`：`if feature is None: raise RuntimeError(` ／ `return { "ok": True,` —— **无任何 before/after 取样** | **确认** |
| E5-3 | batch74 闭合角 | `判据**只能**是 **特征树增量** + **实体面数增量** + **体积增量**（★ 后两个互相独立、缺一不可）` | `"ok": bool(changed and (bool(added) or (face_delta or 0) != 0 or (vol_delta or 0) != 0)),` ／ 自报 `"verified_by": "feature tree delta + solid face-count delta + volume delta" （★ 官方回 void ⇒ 三个都是必要的）` | **确认**（`or` 恰是「缺一不可」的反面） |
| E5-4 | batch74 斜接/顶端盖/角撑板（3 工具） | `判据 = **特征树增量** + 返回对象非 None + **实体面数增量**（三个都要）` ／ `… + **GetDefinition() 属性回读**（官方例子读法）` ／ `… + **mark-1 选区计数**。` | 三处 `ok` **完全相同**：`"ok": bool(added) and feature is not None,` —— 第三项只回传（`face_count_delta` / `definition_readback_mm`）不判 | **确认**（「算了但不判」） |
| E5-5 | batch75 图纸格式 | `★ 判据：SetTemplateName 回 None **且** GetTemplateName 回读等于新路径。` | `out["ret_repr"] = repr(ret)` ／ `out["template_name_readback"] = …` ／ `out["ok"] = True`（**无条件**） | **确认** |
| E5-6 | batch71 通过参考点的曲线 | `★ 判据 = Point/End 的返回值 **且** 特征树增量。` | `point_rets.append(bool(get_com_member(model, "InsertCurveFilePoint", …)))` ／ `return {"ok": end_ret and bool(added), … "point_returns": point_rets, …}` | **确认**（`point_rets` 采了但不判） |

## E-6 · batch76（4 条对不上）

| # | 工具 | 仓内原文 | 官方 / 目标原文 | 本表判定 |
|---|---|---|---|---|
| E6-1 | `sketch_spline` | doc 末句：`★ 前置（官方 Remarks）：**必须先有活动草图**。` ／ 目标抛错文案：`② 是否**已有活动草图**（官方 Remarks 要求）。` | `ISketchManager\CreateSpline2.md`：`This method creates a spline in the active 2D sketch. **If a sketch is not active, then a new sketch is created.** Use [[ISketchManager::ActiveSketch]] to check if the sketch active.` | **确认**（像是把 `CreateLine2` 的前置搬过来了 —— `capabilities.yaml` 的 `sketch_line2` 逐字引官方 `If a sketch is **not active**, then the line is **not created and NULL is returned**`） |
| E6-2 | `feature_cosmetic_thread` | `#: ★ 官方枚举值（逐字取自 InsertCosmeticThread3.md 的 Parameters 段）` ＋ `Param("standard", … "**1 = ANSI Metric**（官方 `Standard`，逐字）。")` | `IFeatureManager\InsertCosmeticThread3.md` 的 `## Parameters`：`- **Standard**: Thread standard as defined by [[swCosmeticStandardType_e]]` ／ `- **EndType**: End condition as defined by [[swCosmeticEndConditions_e]]` —— **只指向枚举、不含数值** | **确认（值对、出处不实）** |
| E6-3 | batch76 三条判据 | `★ **判据**：特征树**新增** + 返回对象 GetTypeName2 …` | `out["ok"] = bool(out.get("ret_type") == "CosmeticThread" or out.get("new_features"))` ／ `out["ok"] = bool(out.get("new_features") or out.get("ret_type"))` | **存疑**（doc 写合取 `+`，代码是析取 `or`；doc 也可能只是在说「两项都回读当证据」） |
| E6-4 | `sketch_spline` docstring 首行 | doc：`★★★ **本条修掉了一个真 bug（★ 且是一处「被误记成架构限制」的假阴性）**…` | docstring 首行：`"""画样条曲线（⚠ **本机实测：建不出来，见下**）。` ／ 正文：`★★ 2026-10-03（接手轮）修正：本函数此前那条「建不出来」的结论是**错的**。` | **存疑**（陈旧首行，正文已自我更正） |

---

# 二 · 抽查证伪的方法

★ **抽样口径**：把本组 73 条「对不上」全部编号建表后，用 `Get-Random -Count 8` **一次性随机抽取**（未人工挑选、未按文件均衡、未避开「看起来最硬」的）。
★ **核法**：**我自己回去打开原文**（官方侧 `C:\swapi\types\` · `C:\swapi\enums\`；仓内侧 `scripts/` · `mcp-server\` · `tests/` · `capabilities.yaml`），逐条比对两段是否逐字对得上。
★ **判据**：`确认` = 原文站得住 · `驳回` = 对不上 · `存疑` = 一方缺原文或两方互不一致。

| 抽中 | 主题 | 我实际打开了什么 | 判 |
|---|---|---|---|
| **C-dw-3 #4** | `GetBomTable` 后继名拼写 | `C:\swapi\types\ISheet\GetBomTable.md` → 首行逐字 `Obsolete. Superseded by [[IView::GetBOMTable]].`；`C:\swapi\types\IView\GetBomTable.md` front-matter → `member: GetBomTable` | **确认**（官方两处拼法确实不同，无法裁定哪种是本意） |
| **E-3 #6** | `set_study_option` 的 `raises` | `mcp-server/tool_specs_batch37.py` L104 与 L117 → 两处逐字 `★ Unknown family/name raises instead of being silently ignored.`；`scripts/sw_simulation_study_options.py` L893 `def set_study_option_report` / L904 `except Exception as exc:` / L905 `return {"ok": False, "family": family, "name": name,` | **确认** |
| **C-dw-3 #7** | 锚点枚举拼写 | 四份 md 逐字：`InsertRevisionTable2.md`·`InsertTableAnnotation2.md` 写 `[[swBOMConfigurationAnchorType_e]]`；`InsertBomTable6.md`·`InsertHoleTable3.md` 写 `[[swBomConfigurationAnchorType_e]]`；全 `types/` 库两种拼法**各 18 次引用**（正好对半） | **确认，但原稿有一处事实错误** → 见 §三.3 |
| **E-1 #2** | 边法兰 doc 旧形态 | `mcp-server/tool_specs_batch4.py` L281 doc → 逐字 `it FAILED with: setting ReverseDirection gave Property ... can not be set.`；`scripts/sw_sheet_metal.py` `create_edge_flange._apply` → 只设 `UseDefaultBendRadius / BendRadius / BendAngle / UseDefaultBendAllowance`，`ReverseDirection` 只剩注释 `⛔ 原代码在此设 data.ReverseDirection —— **该属性不属于本接口**。` | **确认** |
| **C-sm-3 #3.1** | 调官方 `Obsolete` 的两个阵列成员 | `FeatureLinearPattern3.md` 标题下逐字 `Obsolete. Superseded by [[IFeatureManager::FeatureLinearPattern4]].`；`FeatureCircularPattern4.md` 逐字 `Obsolete. Superseded by [[IFeatureManager::FeatureCircularPattern5]].`；`scripts/sw_part.py` L1041 / L1179 / L1852 三处调用确在 | **确认** |
| **C-dw-1 #4** | 辅助视图 `NotAligned` | `CreateAuxiliaryViewAt2.md` 全文 `- **NotAligned**: True aligns the view from its owner, false does not`；`swCreateSectionViewAtOptions_e.md` `swCreateSectionView_NotAligned \| 1 or 0x1; If set, then the section does not snap into alignment with the parent view`；仓内 `create_auxiliary_view(..., not_aligned: bool = True, …)` 调用处 `bool(not_aligned), str(label), …` | **确认**（官方自相矛盾，仓内如实披露） |
| **E-4 #3** | `temperature` 注释 vs 注册 | `mcp-server/tool_specs_batch58.py` L30 `⚠★ **temperature 仍不注册**…` vs **同一文件** L104 `"solidworks_simulation_apply_temperature", "Apply a Temperature Load",` / L105 `"apply_temperature_report",`；`scripts/sw_simulation_loads.py` L206 `"AddTemperature": 1,` / L465 `return _check(manager, "AddTemperature", 1, entities)` | **确认** |
| **E-1 #10** | `create_draft` 的 `depth_mm` | `mcp-server/tool_specs_batch4.py` L328 `Param("depth_mm", float, description="Draft depth in MILLIMETRES.")`（同 doc 已为 `face_ref` 写「accepted but NEVER USED」）；`scripts/sw_sheet_metal.py` `DraftFeatureSpec` 有 `depth: float` 且 `validate()` 读它，而 `create_draft._apply` **只设 `data.Angle` 与 `data.ReverseDirection`** | **确认** |

## ★ 抽查成立率

> **8 / 8 = 100 %**
>
> ★ 其中 **7 条**两段原文逐字对得上、无可挑剔；**1 条**（`C-dw-3 #7`）**核心结论成立、但它给出的支撑句里有一处硬性事实错误**（已单列为对账稿自身的错误，见下）。
> ★ ⇒ **本组 73 条「对不上」的成立率 ≈ 100 %（下界 87.5 %，上界 100 %）**；按「整条无瑕才算成立」口径则是 **7/8 = 87.5 %**。

---

# 三 · 抽查中发现的对账稿自身的错误（★ 必须回写）

## 3.1 · `vd50-C-dw-3.md` §1.7 的两处事实错误（**待回写**）

原稿逐字写：

```
★ **本机文件名是小写 `swBom…`，成员名是大写 `swBOM…`** —— 文件名与成员名自身不一致，**照抄，不改**。
…
判定：存疑 · 一句话依据：…而本机枚举文件只落地了**小写文件名**那一种，无法判定哪种链接才是官方本意。
```

★ 我实测（`Get-ChildItem 'C:\swapi' -Recurse -Filter '*omConfigurationAnchor*'` 全库递归 + 直接读正文）：

- 全 `C:\swapi` **只有一个文件**：`C:\swapi\enums\swBOMConfigurationAnchorType_e.md` —— **文件名是大写 `swBOM`**（原稿说小写，**反了**）
- 该文件 front-matter 逐字 `name: swBOMConfigurationAnchorType_e` —— **文件名与枚举名一致**（原稿说「文件名与成员名自身不一致」，**不成立**）
- 四个成员逐字 `swBOMConfigurationAnchor_BottomLeft / _BottomRight / _TopLeft / _TopRight` —— **成员名也是大写**，与文件名一致

⇒ ★ **结论要改的两处**：① 「本机落地的是小写那一种」 ⇒ 实为**大写那一种**；② 「文件名与成员名自身不一致」 ⇒ 实为**一致**。
⇒ ★ **核心判定不变**：`swBOM…` 与 `swBom…` 两种拼法在官方 `types/` 库里**各 18 次、正好对半**，确实并存（原稿这一条观测是对的）。
⇒ ★ **但推理方向要翻**：既然本机落地的是**与文件名一致的大写 `swBOM…`**，那么**能落地这一种**本身就是官方本意的更强证据 —— 「无法判定哪种链接才是官方本意」这句也偏保守。
⚠ **该条建议降级为「记档」而非「立刻要改」**：它不影响任何代码路径，但**不能照抄进 `docs/known-facts.md`**。

## 3.2 · 各稿口径提示（本表已统一，不算错）

- **C 组（`C-dw-*` / `C-sm-*`）的「不成立」与 D/E 组的「成立」方向相反**：C 组用「不成立」表示「仓内按官方做对了、待核说法不成立」，D/E 组用「成立」表示「doc 承诺没兑现、确有缺陷」。本表已统一改写为 `确认` / `驳回`，**引用回原表时勿混**。

---

# 四 · 分级

## 🔴 立刻要改（★ 用户读到的契约说假话 / 判据失效 / 事实性错误会误导调用方）

| 序 | 条目 | 为什么是「立刻」 |
|---|---|---|
| 1 | **E-5 全部 6 类（11 个工具）** | doc 承诺的判据**没进 `ok`** ⇒ 特征没建成也报成功，直接违反仓库规则 6（不静默成功）。其中 batch74 闭合角用 `or` 把「缺一不可」写成「有一个就行」是最严重的一处 |
| 2 | **E-1 #2 / #3 / #4 / #1**（4 个钣金工具 doc） | 工具描述是对外契约，当前逐字陈述的是**已被自己修掉的失败原因**，按它排查会停在死路上 |
| 3 | **E-3 #1 / #2 / #3 / #4 / #6** | doc 承诺的回读判据在代码里**完全不存在**；`sketch_mirror` / `convert_entities` 甚至 `return True` 写死 |
| 4 | **E-4 #1**（`sketch_add_slot`） | 长度被塞进官方枚举位、第 3 位才是 `Width` ⇒ 槽口尺寸差一个系数 2，且 Param 描述「半径＝宽度一半」与实传的整宽相反 |
| 5 | **E-6 #1**（`sketch_spline`） | 把 `CreateLine2` 的前置（「无活动草图就不建、回 NULL」）**搬到 `CreateSpline2` 上**并冠以「官方 Remarks」—— 官方逐字写的是反面（没有草图会**新建**） |
| 6 | **C-dw-3 #20 / #21 / #22** | PDF/DXF 出口：`SetSheets(0, …)` 传官方枚举里**不存在**的值；PDF 走**已标废弃**的 `IModelDocExtension.SaveAs`（而同仓自己写着「一律用 `SaveAs3`」）；`SaveAs4` 的说法与官方页 + 官方 DXF 例子矛盾 ⇒ **导出功能真的会走错** |
| 7 | **C-dw-2 C2-3**（通用公差表类型号） | `6` 官方是 `WeldTable`、通用公差表是 `9` ⇒ **焊接表会被误报成公差表、真公差表被打成 `unknown`** |
| 8 | **C-dw-2 C2-1 / C2-2 / C2-5 / C2-7** | 一处调官方标 `Obsolete` 的读法、一处把官方**排除**的枚举当合法值、一处用 0 基读官方只收 `1 or 2` 且限「2022 之前」的 GTol 帧 |
| 9 | **C-sm-3 #3.2**（`linear_pattern` 毫米 ↔ `in meters`） | 阵列间距**差 1000 倍**；同仓另一条路径已做 `* 0.001` 并注明旧文档串是「错话」 |
| 10 | **C-sm-1 V-2 / V-3**（`sheet_metal` 的 `level: verified`） | 两条 evidence 一条不碰 COM、一条按字面 pytest **收 0 个用例** ⇒ 直接违反验收标准 **A4**（`verified` 必须有我们自己的运行证据） |
| 11 | **C-sm-1 V-1 / V-5** | 工具契约承诺开放折线可用而真机失败；`recon/sheetmetal.md` 把**已实现且官方有入口**的斜接/闭合角记成「官方没写」⇒ 会把后来人引到错误结论 |
| 12 | **C-dw-1 #1 / #3** | 覆盖矩阵「断裂视图 ✅」只由 `InsertBreak3`（插断裂线）支撑，`BreakView` / `CreateBreakOutSection` 零调用点；剖面视图传空 `SectionLabel` 且从不 `SetLabel2` ⇒ 建出来的剖视图没有标签字母 |
| 13 | **E-1 #7**（`weldment_evidence`） | doc 说「`create_missing_cut_list=False` 时只读」，目标**无条件**调 `update_cut_list` → 对 CutListFolder 调 `UpdateCutList`（**写操作**）⇒ 标注为只读的调用实际会改模型 |
| 14 | **E-1 #5 / #6 / #9** | `topology_run` 承诺「报告结果是否存在」实则只返回码；`create_study` 的 Param 承诺「同名先删」实则把同名当错误码 2 且**无任何删除调用**；`mold_evidence` doc 说可回读、目标自述真机**恒为全 `None`** |
| 15 | **D-2 C8** | 这条自称「**唯一常驻硬门禁**」，而它**唯一判据**要读的 `docs/refuted-patterns.json` **在仓里不存在** ⇒ 闸跑不起来，`E9_LEDGER_DIVERGED` 永远产生不出来 |
| 16 | **E-4 #3** | 文件头写「`temperature` 仍不注册」、同文件却已注册且 arity 仍停在被怀疑过时的 CHM 声明上 |

## 🟡 要记档（★ 不改代码，但必须写进 `docs/known-facts.md` / 缺口地图 / 台账）

| 序 | 条目 | 记什么 |
|---|---|---|
| 1 | **C-dw-3 #7 的更正**（§三.3） | 本机落地的是**大写 `swBOMConfigurationAnchorType_e`**，文件名与成员名一致；两种拼法在官方库里**各 18 次** |
| 2 | **C-sm-2 #3.1 / #4.2 · C-sm-3 #4.1 / #5.1** | 四个**零实现**子面（切口 / 成形工具 / 展开 / 转角处理）⇒ 进缺口地图，别让「官方没查过」的印象继续存在 |
| 3 | **C-sm-1 V-6** | 斜接/闭合角两个已挂 MCP 的工具在台账里 **0 引用**（★ 仓内 `scan-S2a` 已自记，属**未清项**，只主张「台账该有条目，哪怕标 `stitched`」） |
| 4 | **C-sm-2 S2-2 / C-sm-2 S2-6** | `swFmDraft(3)` 不在 `CreateDefinition` 名单 ⇒ `CreateDefinition(3)` 回 `None` 是**应然的**（这条是「如实记录」，不是缺陷）；`ICustomBendAllowance.Type` 顺序被官方两段原文互相抵消 ⇒ 记「存疑」 |
| 5 | **C-dw-3 #4 / #13 · C-dw-1 #2 / #4 · C-sm-2 S2-6 · E-2 #4 · E-3 #7 · E-4 #5 / #6 · E-6 #3 / #4 · E-1 #11** | **官方自相矛盾 / 陈旧首行 / doc 括注两可**这一族（共 13 条）⇒ 逐条记「哪两段打架」，避免下一轮又当成新发现重核 |
| 6 | **D-3 D3-1** | C11 的括注「全仓提及只有 3 处 markdown 叙述」实测是 4 文件 11 处（计入 GATE-FINAL 自身则 20 处 / 6 文件）⇒ **主结论仍成立**，只有那个计数错 |
| 7 | **D-3 D3-2** | 「被改写**之前**」的读数（`at=23:29:01` / 644 文件 / 671 行）**查不到**（`output/` 被 `.gitignore:120` 排除、无 git 历史）⇒ 记「查不到」，**不要**拿相似数字顶替 |
| 8 | **E-1 #8** | `units=-1` 两次实测差**恰好 1000 倍**（4.9339/0.2467 vs 4930.50/246.53），**原因未查清** ⇒ 原样记，**不编解释** |
| 9 | **C-dw-1 查不到三项** | ① 中文「断裂视图」对应哪个官方术语（无中英对照）；② `CreateFirstAngleViews2` 在本机 COM 上到底存不存在；③ `CreateSectionViewAt5` 传空 `SectionLabel` 的后果 |

## ⚪ 不用管（★ 抽查判不成立的 / 自陈「给不出两段原文」/ 仅出处或措辞层）

| 序 | 条目 | 处置理由 |
|---|---|---|
| 1 | **C-sm-3 #1.2**（`IModelDoc2.ExportToDWG2` 出处层） | 只影响**出处标注**；`IModelDoc2` 在 COM 里确实暴露该成员、调用本身不是用错接口 ⇒ 想改就改那行注释，**不是缺陷** |
| 2 | **E-2 #3**（`revolve_boss` doc 的 ⚠） | 目标 docstring 讲的才是调用方真正会踩的坑（先轴后轮廓，事实 251/278/279/280）⇒ 直接**删掉那句 ⚠ 或改指事实号**即可，属机械修文 |
| 3 | **全部「驳回 / 核对一致」条目**（C1-5 · C2-4 · C2-6 · C2-8 · C2-9 · C-sm-1 的 8 处「核过无问题」· C-sm-2 S2-2 的判定 2.1/4.1/5.2 · C-sm-3 的镜像 mark 表与 8 个 bitmask 常量 · D-2 的 C5/C6/C7 全部 12 个锚点 · D-3 的 C9/C10/R 全部 14 个核点） | 两段原文逐字对得上，**无问题可报**；保留在本表里只为避免下轮重复核 |
| 4 | **各稿「五 · 刻意省略」段**（`C-dw-2` 4 条 · `C-dw-3` 5 条 · `C-sm-1` 查不到 2 条 · `C-sm-3` 2 条 · `D-3` 3 条 · `E-2` 4 条 · `E-3` 3 条 · `E-4` 3 条 · `E-5` 3 条 · `E-6` 附注） | 全部是**「给不出两段原文」或「行号会漂 / 引号内个别字改写」**的自我克制项，按铁律 2/4 本就不该成条 ⇒ **不得当缺口重新提报** |
| 5 | **E-6 附注**（batch76 两条 doc 写「尚未真机验证」但 `output/flatten-tool-evidence.json` / `output/thicken-tool-evidence.json` 已在） | 属 doc 与**证据**不同步，不是「判据有没有实现」，按该片口径不计数 ⇒ **记档即可**（已在 🟡 第 5 条覆盖） |

---

# 五 · 三行

- **交付路径**：`D:\AI\SW\specs\202-user-coverage-gaps\recon\verify50\JUDGE-C_D_E.md`
- **核了 435 处 / 对不上 73 处**（C 组 33 · D 组 2 · E 组 38）
- **随机抽查 8 条，成立率 8/8 = 100 %**（按「整条无瑕」口径 7/8 = 87.5 %；唯一打折项是 `C-dw-3 #7` 的**支撑句事实写反了** —— 本机落地的是大写 `swBOMConfigurationAnchorType_e`，且文件名与成员名一致，两种拼法在官方库里各 18 次）