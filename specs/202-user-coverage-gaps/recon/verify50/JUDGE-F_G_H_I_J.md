# JUDGE-F_G_H_I_J · F/G/H/I/J 组（15 份对账稿）总表 · 抽查证伪 · 分级

**裁判**：本文件是 15 份对账稿（`vd50-F-1/3/4/5`、`vd50-G-1/2/3`、`vd50-H-2/3/4`、`vd50-I-1/2/3`、`vd50-J-1/2`）的合成与裁决。
**只写本文件，仓内一个文件都没改。** 所有结论都在本机复核过原文（`D:\AI\SW\` + `C:\swapi\`）。

---

## 〇 · 口径：★ 先报一条**横贯全组的口径缺陷**（它让「成立率」跨文件不可比）

★ 15 份稿对「**成立**」这个词用了**两种相反的极性**，而且没有任何一处声明：

| 极性 | 「成立」= | 出现于 | 稿内措辞证据 |
|---|---|---|---|
| **A（成立 = 缺陷成立 = 对不上）** | ✅ 是问题 | `F-1` `F-3` `F-4` `F-5` `H-2` `H-3` `H-4` `I-1` `I-2` `I-3` `J-1` | `F-1` §一标题逐字「## 一、对不上的 2 处（成立）」；`J-1` 表格逐字「**成立（对不上）**」 |
| **B（成立 = 达标 = 不构成问题）** | ⛔ 不是问题 | `G-1` `G-2` `G-3` `J-2` | `G-1` §一「**判定：成立**」而全文结论是「**核了 4 处，对不上 0 处**」；`J-2` §三标题逐字「核过但**没问题的**（2 条**成立**）」 |

⇒ ★ **同一个「成立」在一份稿里是 bug、在另一份稿里是 pass**。
⇒ **本文件统一改写口径**：一律用「**判为缺陷** / **判为达标** / **存疑**」，并保留原稿用词以便回查。
⇒ ★ **这本身是全组第 1 号要改项**（见 §四·立刻要改 ①）。

---

## 一 · 总表（72 条「对不上」· 每条保留两段原文）

> **两段原文列约定**：`仓内` = 稿中引用的仓内那一段（逐字）；`官方/目标` = 稿中引用的官方或目标源那一段（逐字）。均只取**决定性的那一小段**，可 grep 复核。
> **判定列**：`缺陷` = 对得上（原极性 A 的「成立」）；`达标` = 对得上（原极性 B 的「成立」）；`存疑`；`不成立`。

### F 组 · mark 值 vs 官方 mark 表

| ID | 主题 | 原稿判定 | 统一判定 | 仓内那一段 | 官方/目标那一段 |
|---|---|---|---|---|---|
| **F1-1** | `mold_parting_line` 一个 mark 都不传 | 成立 | **缺陷** | `mcp-server/tool_specs_batch1.py` 的 `ToolSpec(...)` 里**没有** `pre_call=`、也没有 `derived_args=`；`scripts/sw_mold.py` 逐字 `feat = get_com_member(fm, "InsertMoldPartingLine", bool(draft_analysis))` | `C:\swapi\types\IFeatureManager\InsertMoldPartingLine.md` §Remarks 逐字 `Before calling this method, you must select the direction of pull and the edges for the parting line by calling IModelDocExtension::SelectByID2 with the following Marks:` / `Direction of pull 1` / `Parting line edges 4` |
| **F1-2** | `mold_parting_surface` 同上（模型尚无分型线时） | 成立（有条件） | **缺陷** | `mcp-server/tool_specs_batch9.py` 的 `ToolSpec(` **没有** `pre_call=`、**没有** `derived_args=` | `InsertMoldPartingSurface.md` §Remarks 逐字 `f a parting line feature does not yet exist in the model, you must first select the direction of pull and the edges for the parting line using IModelDocExtension::SelectByID2 . For example, a face (direction of pull) has a mark of 1 and edges (parting lines) a mark of 4.` |
| **F3-5** | `part_wrap` 官方 mark 1/2/4 在 MCP 工具面上无处施加 | 成立 | **缺陷**（★ **复核确认**，不是新发现） | `mcp-server/tool_specs_batch50.py` 的 `ToolSpec` **只有三个 Param**（`wrap_type` / `thickness_mm` / `reverse`），**没有 `pre_call=`、没有 `param_alias`** | `C:\swapi\types\IFeatureManager\InsertWrapFeature2.md` §Remarks 逐字 `Use IModelDocExtension::SelectByID2 or IModelDocExtension::SelectByRay and specify a Mark of...` 随后三档 `1`（面）/`2`（拔模方向）/`4`（2D 草图） |
| **F4-1** | 钣金 gusset：官方要**两条腿**，`_pre_gusset` 只选 1 面 | 成立 | **缺陷**（与 J2-2 重复计数） | `mcp-server/tool_specs_batch4.py` 逐字 `def _pre_gusset(params):` / `_select(params, "FACE")` | `C:\swapi\types\ISMGussetFeatureData\_overview.md` §Remarks 第 2 步逐字 `Specify the legs of the gusset feature` / `- Two flat faces of a bend.` / `- Two flat faces adjacent to a cylindrical bend face.` |
| **F4-2** | 边法兰缺 `InsertSketchForEdgeFlange` + `AddEdges` | 成立 | **缺陷** | `scripts/sw_sheet_metal.py::create_edge_flange` 的 `_apply(data)` 里 **没有 `data.AddEdges(...)`**，全函数 **没有 `InsertSketchForEdgeFlange`** | `C:\swapi\types\IEdgeFlangeFeatureData\AddEdges.md` §Remarks 逐字 `Before calling this method, call IModelDoc2::InsertSketchForEdgeFlange to associate the sketches with the edges.` |
| **F4-3** | 焊件端面 / 支撑腿：零语义筛选 | 成立 | **缺陷**（与 J2-3 + J2-4 同族） | `mcp-server/tool_specs_batch74.py::_select_faces_for` 判定条件只有 `if picked >= count:` —— **没有任何「这是不是端面 / 是不是支撑腿」的检查** | `InsertEndCapFeature3.md` §Remarks 逐字 `Before calling this method, select one or more end [[faces]] of a structural member in the graphics area.` / `InsertGussetFeature3.md` 逐字 `…select two faces that are the supporting legs of this gusset with a Mark of 1.` |
| **F4-4** | `_select_faces_for` 未传 `model=` ⇒ mark 保真分支不可达 | 存疑 | **存疑** | 调用点逐字 `_select_com_object(face, append=(picked > 0), mark=mark)` —— ★ **没有 `model=` 形参** | （无官方对应；依据是仓内自述）`scripts/sw_part.py` 逐字 `#: ③ ★ 最后退回 Select4 + 空 VARIANT（★ 保原行为；⚠ **它丢 mark**，已知）` |
| **F5-1** | knit：mark=1 请求对，但投递链有会丢 mark 的分支 | 存疑 | **存疑** | `scripts/sw_surface_features.py` 逐字 `selected = _select_all_surface_faces(model, mark=1)` → 其内逐字 `if _sel(f, append=True, mark=mark):` ★ **没有 `model=`** | `C:\swapi\types\IFeatureManager\InsertSewRefSurface.md` §Remarks 首句逐字 `Make selections using IModelDocExtension::SelectByID2 with a mark number of 1.` |

**F 组补充（非「对不上」但同批记录）**：`F-1` 另 4 条 `mold_shut_off_surface` / `mold_draft_analysis` / `mold_undercut_detect` / `core_cavity_split` —— 原稿判**不成立**（官方页无 mark 表）；`F-3` 另 3 条（wrap 草图 mark 4 / 面 mark 1 / 拔模方向 mark 2）判**不成立**、`part_axis` 判**查不到**；`F-4` 5 条工具 mark 数值判**不成立**；`F-5` 另 4 条（extend / revolve / trim-曲面 / trim-草图）判**查不到**。

### G 组 · 导出收尾检查（产物存在且非空）

**判据原文（三份稿共用，只引一次）** —— `C:\swprojects\Cai-aa__CAD-Agent-Hub\MCP\Solidworks\docs\compatibility-and-lessons.md` §`Save routing` 逐字：
`STEP, IGES, STL, PDF, DXF, and DWG exports use IModelDocExtension.SaveAs. They never pass through SaveAs3.` / `Both paths verify that the target exists and is non-empty before reporting success.`

| ID | 主题 | 原稿判定 | 统一判定 | 仓内那一段 | 官方/目标那一段 |
|---|---|---|---|---|---|
| **G2-1** | `export_to_dxf` 两条分支判据强度不一样 | 不成立(=缺陷) | **缺陷**（与 G2-2 同一链两端） | `scripts/sw_export.py` 逐字 `if doc_type == 3:  # 工程图` / `return _export_generic(model, output_path)` / `else:` / `return export_flat_pattern_dxf(model, output_path)` | 同上 §`Save routing`（该条明确点名 `DXF/DWG`） |
| **G2-2** | `export_flat_pattern_dxf` 只回 `bool(success)` | 不成立(=缺陷) | **缺陷** | 逐字 `return bool(model.ExportToDWG2(` … `))` | `C:\swapi\types\IPartDoc\ExportToDWG2.md` §Returns 逐字 `True if export is successful; false if not` |
| **G2-3** | `export_to_bmp` 官方 bool 一真就 `return p` | 不成立(=缺陷) | **缺陷** | 逐字 `ok = get_com_member(model, "SaveBMP", str(p), int(width), int(height))` / `if not ok:` / `raise RuntimeError(` … `return p` | 目标源 `inspection.py` 逐字 `if not saved or not target.exists() or target.stat().st_size <= 0:` / `raise RuntimeError("SolidWorks SaveBMP did not create a non-empty image")` |
| **G3-1** | `export_to_pdf` 返回裸 `success` | 不成立(=缺陷) | **缺陷** | `scripts/sw_export.py` 逐字 `success = model.Extension.SaveAs(str(output_path), 0, 1, pdf_data, errors, warnings)` / `_print_result("PDF", output_path, success, errors, warnings)` / `return success` | §`Save routing`（`PDF` 与 STEP/IGES/STL 并列） |
| **G3-2** | `export_sheet_to_pdf` 同形 | 不成立(=缺陷) | **缺陷** | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py` 逐字 `success = model.Extension.SaveAs(output_path, 0, 1, pdf_data, errors, warnings)` … `return success` | 同上 + `C:\swapi\types\IModelDocExtension\SaveAs3.md` §Returns 逐字 `True if the save is successful, false if not` |
| **G3-3** | `export_assembly_bom_csv` 只缺「非空」半边 | 部分成立 | **缺陷（半边）** | `scripts/sw_delivery.py` 逐字 `after = _file_signature(target)` / `produced = after is not None and after != before` —— ★ 全程**没有一处拿 `st_size` 跟 0 比** | 目标源 `executor.py` 逐字 `if not target.exists() or target.stat().st_size <= 0:` / `raise RuntimeError(f"SolidWorks reported success but output is missing: {target}")` |
| **G3-4** | `export_cut_list_csv` 零检查 | 不成立(=缺陷) | **缺陷**（★ 比 G3-1 还弱一档） | `scripts/sw_weldment.py` 逐字 `writer.writerow(values)` … `return target`（★ 连 `success` 都没有） | 同上 `executor.py` |
| **G3-5** | `batch_export_formats` 的 `.pdf` 分支缺「非空」半边 | 部分成立 | **缺陷（半边 · 附带）** | `scripts/sw_export.py` 逐字 `produced = api_success and after is not None and after != before` —— ★ **没有 `signature[0] > 0`** | 同上 `executor.py` |

**G 组补充**：`G-1` 核 4 处（STEP / STL / IGES / Parasolid）**对不上 0 处**（出口全是 `_export_generic`，返回 `bool(success) and artifact_ok`）；另如实记了一条**目标源自身**的文档/代码不一致（目标源两条保存路只判 `exists()`、文档却写 `and is non-empty` ⇒ 本仓 `_export_generic` 严于目标源代码）。

### H 组 · 从 `swCommands_e` 反向核「有命令 + 有 API + 我们没有」

| ID | 主题 | 原稿判定 | 统一判定 | 仓内那一段 | 官方/目标那一段 |
|---|---|---|---|---|---|
| **H2-1** | 自动气泡序号 `AutoBalloon5` 无工具 | 成立 | **缺陷**（最便宜的一类） | `mcp-server/tool_specs_batch73.py` 表头逐字 `#   气泡序号                    ★★ **不建 ToolSpec**（理由见文件尾）★★               IDrawingDoc.AutoBalloon5` | `swCommands_e` 逐字 `swCommands_AutoBalloon \| 447; … **Annotations toolbar > Auto Balloon** \|` + `IDrawingDoc\AutoBalloon5.md` 逐字 `**Signature**: System.object AutoBalloon5( AutoBalloonOptions BalloonOptions )` |
| **H2-2** | 爆炸视图 `CreateExplodedView` | 成立 | **缺陷** | `scripts/sw_assembly_doc.py` 逐字 `'CreateExplodedView': 0,` —— ★ 全仓**零调用点、零工具** | `swCommands_e` 逐字 `swCommands_ExplodedView \| 135; … **Assembly toolbar > Exploded View** \|` |
| **H2-3** | 压缩/还原 `SetComponentSuppression` | 成立 | **缺陷**（封装已在，只差接线） | `scripts/sw_assembly_doc.py` 逐字 `def suppress_mate(doc, component_name: str) -> bool:` … `call_assembly_doc(doc, "SetComponentSuppression", str(component_name))`；★ `mcp-server/` 全目录检索 `sw_assembly_doc` ⇒ **0 命中** | `swCommands_e` 逐字 `swCommands_ChangeSuppressionState \| 150; … **Assembly toolbar > Change Suppression State** \|` |
| **H2-4** | 隐藏/显示 `SetComponentVisibility` | 成立 | **缺陷** | 登记表逐字 `'SetComponentVisibility': 3,`（在册零调用）；唯一封装逐字 `def hide_component(doc, hidden: bool = True) -> int:` → `call_assembly_doc(doc, "HideComponent" if hidden else "ShowComponent")` | `swCommands_e` 逐字 `swCommands_Hide_Components \| 925; …` + `IAssemblyDoc\HideComponent.md` 逐字 `Obsolete. Superseded by IModelDoc2::HideComponent2.` |
| **H2-5** | 解散子装配 `DissolveSubAssembly` | 成立 | **缺陷**（封装已在，只差接线） | 逐字 `def dissolve_assembly(doc) -> int:` … `call_assembly_doc(doc, "DissolveSubAssembly")`；★ `mcp-server/` 对该模块 **0 命中** | `swCommands_e` 逐字 `swCommands_Dissolve_Subassembly \| 1260; … **RMB menu > Dissolve Subassembly** \|` |
| **H3-01** | 钣金卷边 Hem | 成立 | **缺陷** | AST 扫 `scripts/` **0**、`mcp-server/` **0**、`tools/` **0**；九个 `solidworks_sheet_metal_*` 工具里**无 hem** | `swCommands_e` 逐字 `swCommands_Hem \| 363; … **Sheet Metal toolbar > Hem** \|` + `InsertSheetMetalHem2.md` 16 参签名 |
| **H3-02** | 放样折弯 Lofted-Bend | 成立 | **缺陷** | 同上三目录 **0** | `swCommands_LoftedBend \| 406; … **Sheet Metal toolbar > Lofted-Bend** \|` + `InsertSheetMetalLoftedBend2.md` 10 参签名 |
| **H3-03** | 断开角/角修剪 | 成立 | **缺陷** | `InsertSheetMetalCornerTrim` / `InsertSheetMetalBreakCorner` 三目录均 **0**；`sw_sheet_metal.py` 与 `sw_sheet_metal_weld_entry.py` 的公开函数穷举里**都没有 corner trim** | `swCommands_BreakCornerCornerTrim \| 364; … **Sheet Metal toolbar > Corners > Break-Corner/Corner-Trim** \|` + 两条官方入口 |
| **H3-04** | 实体转钣金 Convert to Sheet Metal | 成立 | **缺陷** | `swFmSolidToSheetMetal` 在全仓 `.py` 里只出现在 `scripts/check_interface_member_ownership.py` 的**注释**（逐字 `…/ swFmSolidToSheetMetal）。**⇒ 可靠但稀疏。**`）；AST 扫 `InsertConvertToSheetMetal{,2}` 三目录 **0** | `swCommands_SolidToSheetMetal \| 2882; … **Sheet Metal toolbar > Convert to Sheet Metal** \|` + `CreateDefinition.md` 逐字 `- swFmSolidToSheetMetal (convert solid to sheet metal)` |
| **H3-05** | 凸缘与槽 Tab and Slot | 成立 | **缺陷**（★ **已抽查复核成立**） | `swFmTabAndSlot` 在**全仓 `.py` 里零命中**（★ 裁判复核：全仓 grep 92 处命中**全部**落在 `docs/` `specs/` `_enum.txt` `_all_families.json` 等非 `.py` 或草稿自身；`scripts/check_interface_member_ownership.py` 命中的是 `ITabAndSlotGroupData` 接口名、不是该常量） | `swCommands_TabAndSlot \| 3234; adds a tab and slot feature; **Sheet Metal toolbar > Tab and Slot** \|` + `CreateDefinition.md` 逐字 `- swFmTabAndSlot (tab and slot)`（★ **在官方 35 常量名单里**） |
| **H3-06** | 钣金法向切割 Normal Cut | 成立 | **缺陷** | `swFmNormalCut` 只出现在 `check_interface_member_ownership.py` 的注释；AST 扫 `AddSMNormalCut` / `FinishSMNormalCut` 三目录 **0** | `swCommands_SMNormalCut \| 3196; … **Sheet Metal toolbar > Normal Cut** \|` + `CreateDefinition.md` 逐字 `- swFmNormalCut (sheet metal normal cut)` |
| **H3-07** | 钣金角部释放 Corner Relief | 成立 | **缺陷** | `swFmCornerRelief` 全仓 `.py` 零命中；AST 扫 `AddCornerReliefCorner` / `FinishCornerRelief` 三目录 **0** | `swCommands_Corner_Relief \| 3112; … **Sheet Metal toolbar > Corner Relief** \|` |
| **H3-08** | 钣金简单孔 Simple Hole | 成立 | **缺陷** | AST 扫 `SimpleHole` / `SimpleHole2` 三目录 **0**；孔一族七条工具走的都是孔向导/拉伸切除，**没有 `simple_hole`** | `swCommands_SimpleHole \| 12; … **Sheet Metal toolbar > Simple Hole** \|` + `SimpleHole2.md` 24 参签名 |
| **H3-09** | 钣金展开 Unfold | 成立 | **缺陷** | AST 扫 `InsertSheetMetalUnfold` 三目录 **0**；全仓唯一提到 `Unfold` 的 `.py` 是 `tools/audit_gap_implementations.py` 的**待办缺口表** 逐字 `"钣金/展开折叠": ["InsertFlatPattern", "Unfold"],` | `swCommands_Unfold \| 326; … **Sheet Metal toolbar > Unfold** \|` + `InsertSheetMetalUnfold.md` §Remarks 逐字 `Select the objects for the unfold feature before calling this method.` |
| **H3-10** | 焊件裁剪/延伸 Trim/Extend | 成立 | **缺陷** | AST 扫 `InsertWeldmentTrimFeature{,2}` 三目录 **0**；`sw_weldment.py` 15 个公开函数穷举里**无 trim/extend** | `swCommands_TrimExtend \| 466; … **Weldment toolbar > Trim/Extend** \|` + 官方 mark 表逐字 `- 1 = Body or bodies to trim` / `- 2 = Trimming boundaries (body or face)` |
| **H3-11** | 焊件角焊缝 Fillet Bead | 成立 | **缺陷** | AST 扫 `InsertFilletBeadFeature{,2,3}` 三目录 **0**；`solidworks_weldment_*` 十三条里只有 `gusset_create` 与 `insert_end_cap` | `swCommands_FilletBead \| 505; … **Weldment toolbar > Fillet Bead** \|` + `InsertFilletBeadFeature2.md` 16 参签名 |
| **H3-12** | 焊缝/装饰焊缝 Weld Bead | 成立 | **缺陷** | AST 扫 `InsertCosmeticWeldBead{,2}` 三目录 **0** | `swCommands_CosmeticWeld \| 2991; … **Weldments toolbar** or **Insert menu > Assembly Features > Weld Bead** \|` |
| **H3-13** | 模具移面 Move Face | 成立 | **缺陷** | AST 扫 `InsertMoveFace{,2,3}` 三目录 **0**；`sw_mold.py` 七个函数全部挂成工具，**唯独没有移面** | `swCommands_InsertFeatureNudge \| 2928; … **Mold Tools toolbar > Move Face** \|` + `InsertMoveFace3.md` 8 参签名 |
| **H3-14** | 模具缩放 Scale | 成立 | **缺陷** | AST 扫 `InsertScale`：`scripts/` **0**、`mcp-server/` **0**、`tools/` **1**（是**待办表** 逐字 `"特征/缩放变形": ["InsertScale", "Scale"],`） | `swCommands_InsertScale \| 350; … **Mold Tools toolbar > Scale** \|` + `InsertScale.md` 5 参签名 |
| **H3-15** | 曲面「剪裁曲面」Trim Surface（实现+证据都在，只差一个 ToolSpec） | 成立 | **缺陷** | `scripts/sw_surface_features.py` 逐字 `def trim_surface_report(model, *, mutual: bool = True, split_system: bool = True,` + `tools/prove_trim_surface.py` 有真机证据；而 `mcp-server/` 里 `module="sw_surface_features"` **只有 4 处**、**不含** `trim_surface_report`；`capabilities.yaml` 里**零命中** | `swCommands_TrimSurface \| 302; … **Surfaces toolbar > Trim Surface** \|` + `PreTrimSurface.md` / `PostTrimSurface.md` 两步签名 |
| **H3-16** | 曲面「扫描曲面」Swept Surface（只差一个 ToolSpec） | 成立 | **缺陷** | `scripts/sw_sweep.py` 逐字 `def create_sweep_surface_report(model) -> dict:` + `tools/prove_sweep_surface.py` 有证据；而 `mcp-server` 里 `module="sw_sweep"` **只有 1 处**（`function="create_sweep_report"`，走 boss 路）；`capabilities.yaml` 里**零命中** | `swCommands_SweptSurface \| 103; … **Surfaces toolbar > Swept Surface** \|` + `CreateDefinition.md` 逐字 `- swFmRefSurface (surface sweep)` |
| **H3-17** | 曲面「解除剪裁」Untrim（**仓库自己承认的缺口**） | 成立 | **缺陷** | `capabilities.yaml` 同条目 `limitations` 末段逐字 `⚠ **本包装未接进 MCP 工具层**`；AST 扫 `InsertUntrimSurface{,2}`：`scripts/` **0**、`mcp-server/` **0**、`tools/` **3**（全是证据脚本） | `swCommands_UntrimSurface \| 400; … **Surfaces toolbar > Untrim Surface** \|` + `InsertUntrimSurface2.md` 5 参签名 |
| **H3-18** | 曲面「删除孔」Delete Hole（**仓库自己承认的缺口**） | 成立 | **缺陷** | 同上形态：`capabilities.yaml` `limitations` 末段逐字 `⚠ 本包装未接进 MCP 工具层。`；`scripts/` **0**、`mcp-server/` **0**、`tools/` **3**（证据脚本） | `swCommands_DeleteHoleSurface \| 3360; deletes inner cavity on surfaces; **Surfaces toolbar > Delete Hole** \|` + `InsertDeleteHoleForSurface.md` §Remarks 逐字 `Before calling this method, call IModelDocExtension::SelectByID2 to select the hole edges to remove from the surface.` |
| **H4-01** | 截面属性 `GetSectionProperties2` | 成立 | **缺陷** | `mcp-server/tool_specs_batch46.py` 评估读数面只有 `name="solidworks_measure_selection"` / `module="sw_measure"`；312 个工具名里含 `section` 的只有 `solidworks_drawing_create_section_view`（**不拿它顶替**） | `swCommands_SectionProperties \| 383; … **Tools toolbar > Section Properties** \|` + `GetSectionProperties2.md` 24 元素返回数组逐字列出 `retval[1] area` / `retval[2] centroid x` … |
| **H4-02** | 顶层透明 / X-Ray | 成立 | **缺陷** | `mcp-server/server.py::solidworks_set_appearance` 入参只有 `color` / `target` / `component_keyword`，**没有任何透明 / X-Ray 维度** | `swCommands_XRayToggleAssem \| 3317; …` + `SetTopLevelTransparency.md` 逐字 `**Signature**: System.bool SetTopLevelTransparency( System.bool InValue )` |
| **H4-03** | 打印 `PrintOut4` | 成立 | **缺陷** | `mcp-server/server.py` 的 `class ExportFormat(str, Enum):` 只有 `STEP/STL/IGES/PARASOLID/PDF/DXF` 六项、**封闭、无 print** | `swCommands_Print \| 589; … **Standard toolbar > Print** \|` + `PrintOut4.md` 逐字 `void PrintOut4( System.string Printer, System.string PrintFileName, System.object PrintSpecification )` |
| **H4-04** | 发布 3D PDF | 成立 | **缺陷** | 同上 `ExportFormat` 枚举（**只有 `pdf` 二维件**） | `swCommands_Publish3DPDF \| 3451; **SOLIDWORKS MBD toolbar > Publish to 3D PDF** \|` + `PublishTo3DPDF.md` 逐字 `System.int PublishTo3DPDF( System.object MBDPdfData )` |
| **H4-05** | 发布 STEP AP242 | 成立 | **缺陷** | 同上 `ExportFormat`；★ 它的 `STEP` 走普通 STEP 导出 | `swCommands_PublishSTEP242File \| 3198; **SOLIDWORKS MBD toolbar > Publish STEP 242 File** \|` + `PublishSTEP242File.md` 首行 `Obsolete. Superseded by IModelDocExtension::PublishSTEP242File2.` |
| **H4-06** | 捕获 3D 视图 | 成立 | **缺陷**（**不拿 `SaveBMP` 顶替**） | `scripts/sw_export.py` 两条存图路径逐字 `"""把**当前视图**存成 BMP（官方 IModelDoc2.SaveBMP）。` … 两条都**出文件**、返回 `Path` | `swCommands_Capture_3dView \| 3141; **SOLIDWORKS MBD toolbar > Capture 3D View** \|` + `Capture3DView.md` 逐字 `**Signature**: View3D Capture3DView()` / `## Returns [[IView3D]]` |
| **H4-07** | 算例删除 / 复制 | 成立 | **缺陷** | `module=sw_motion` 六个工具逐字：`create_study` / `collect_summary` / `validate_studies` / `study_manager` / `ensure_type_library` / `validate_summary` —— **建有、删与复制没有** | `swCommands_Animation_Delete \| 2144; **Motion Study tab RMB menu > Delete** \|` + `DeleteMotionStudy.md` 逐字 `System.bool DeleteMotionStudy( System.string MotionStudyName )` |
| **H4-08** | 直线马达 / 弹簧 / 重力 | 成立 | **缺陷** | `scripts/sw_motion.py` 逐字 `SW_FM_AEM_ROTATIONAL_MOTOR = 78` 与 `motion_member(motion_study, "CreateDefinition", SW_FM_AEM_ROTATIONAL_MOTOR)` —— ★ 全模块 `SW_FM_AEM` **只有这 2 处命中** | `swCommands_LinearMotor/LinearSpring/Gravity` 逐字 + 反射 `swFmAEMGravity = 74` / `swFmAEMLinearMotor = 77` / `swFmAEMLinearMotionSpring = 81` |
| **H4-09** | 插入相机 | 成立 | **缺陷** | 场景/相机面挂出来的工具只有三个：`solidworks_list_render_materials` / `solidworks_collect_appearance_evidence` / `solidworks_refresh_scene_graph` | `swCommands_Insert_Camera \| 2191; … **Scene, Lights, and Cameras > Camera RMB menu > Add Camera** \|` + `InsertCamera.md` 逐字 `**Signature**: Camera InsertCamera()` |
| **H4-10** | 新建显示状态 | 成立 | **缺陷** | 配置轴八个工具里**没有一条在「显示状态」上**；`sw_render_material.py` 的 21 处 `DisplayState` 命中全是**贴材质**、**不拿它顶替** | `swCommands_New_Display_State \| 2129; **Visual Overlay dialog toolbar > New Display State** \|` + `IConfiguration\CreateDisplayState.md` 逐字 `System.bool CreateDisplayState( System.string DisplayStateName )` |

**H 组补充（原稿判不成立 / 查不到）**：`H3-19/20/21`（模具分割线分析 / 插入模具文件夹 / 沟槽焊缝）—— API 层**查不到**，不报；`H3-22`（成形工具 Forming Tool）—— 官方入口自相矛盾，判**存疑**；`H-4` 另登记 8 类「查不到 / 不成立」（eDrawings 导出、MBD 加载类命令、CosmosWorks 启动类命令等），按铁律 5 **不顶替**。

### I 组 · `capabilities.yaml` 的 `limitations` ↔ `docs/dead-ends.md`

**结构前提（三份稿共同、已实测）**：`docs/dead-ends.md` 由 `tools/gen_dead_ends.py` 从 `capabilities.yaml` 机械筛出，`DEAD = re.compile(r"(强停止|全部失败|都失败|不可调用|穷尽|已穷尽|到不了|走不通|停手|停止试|次全部|无法|不可行|此路不通|验不过|框架性|架构性|后端限制|降为 stitched|需要用户提供|本机没有|失败点.*漂移|未被?穷尽验证)")`；`--check` 回 `✓ docs/dead-ends.md 是最新的（46 条 / 29 能力）` ⇒ ★ **「只在一边」只可能来自正则漏网或条目内部自相矛盾**。

| ID | 主题 | 原稿判定 | 统一判定 | 仓内那一段 | 官方/目标那一段 |
|---|---|---|---|---|---|
| **I1-1** | `weldment_cut_list` limitation 第 3 条已被**同能力 evidence** 推翻 | 成立 | **缺陷**（★ **已抽查复核成立**） | `capabilities.yaml` 逐字：`⚠ **真机 1/3**：… create_cut_list ⚠ **接口不可达** —— 报「IFeatureManager.InsertWeldmentCutList2 … **取不到**」` ★ **对** `★★★ 2026-10-03（轮 496-498）**更正上面那条…** dispid = 174 … **4/4 全调通** … ⇒ ★ **故本条据据它做出的「到不了」结论不成立**。` | `C:\swapi\types\IFeatureManager\InsertWeldmentCutList2.md` 逐字 `**Signature**: Feature InsertWeldmentCutList2( System.object Bodies )` |
| **I1-2** | `surface_ref_ops`「旋转曲面本条不登记」已被 `surface_revolve` evidence 推翻 | 成立 | **缺陷**（★ **已抽查复核成立**） | `capabilities.yaml` 逐字 `★★ **旋转曲面本条不登记** … ⇒ ★★ 按**事实 53** … **停下**。` ★ **对** `★★★ **而根因是一组对照定下的：「无中心线」那组**不成** … 故：本仓此前对它的「不成」真因是**前置缺中心线** … ★ 而它**修正了一个归因**。` | `C:\swapi\types\IFeatureManager\InsertRevolvedRefSurface.md` 首句逐字 `Creates a revolved reference surface by revolving a profile around a centerline.` |
| **I1-3** | `surface_thicken_silent_noop` 整条能力不在 `dead-ends.md`（正则漏网） | 成立 | **缺陷** | `capabilities.yaml` 逐字 `★★ 2026-10-03（轮 502-504）**真机总账：共 11 组 · 两条入口 · 前置每次完美**——结果**全部 None、特征树不动、连错误都不报**` | `FeatureBossThicken.md` §Remarks 逐字 `The surface must be selected with a mark of 1.` |
| **I1-4** | `surface_untrim`「面那条路五个组合全败」不在 `dead-ends.md`（正则漏网） | 成立 | **缺陷**（★ **已抽查复核成立**） | `capabilities.yaml` 逐字 `⚠ **官方 Remarks 说 "face **or edges**"** —— ★ 而本机上**面那条路五个组合全败**（Face=0/1/2 与 BTrimOppositeSide=True）⚠ —— ★ 不碰它。` ⇒ ★ **裁判复核：`docs/dead-ends.md` grep `surface_untrim` 零命中**（该文件对 `surface_untrim` / `surface_thicken_silent_noop` / `surface_ref_ops` / `mold_analysis` **全部零命中**） | `InsertUntrimSurface2.md` 逐字 `- requires preselection of the face or edges you want to untrim.` |
| **I1-5** | `surface_features`「`InsertSewRefSurface` 不抛但特征树不变」不在 `dead-ends.md`（正则漏网） | 成立 | **缺陷** | `capabilities.yaml` 逐字 `真机实测：InsertSewRefSurface **不抛但特征树不变**（它要求先选中要缝合的曲面）。` / `⚠ **未通过**：through_all=True ⇒ 特征树 7→7（★ 没建成）` ⇒ `DEAD` 里 `全败|都失败` 一个都不收 | `InsertSewRefSurface.md` §Remarks 首句逐字 `Make selections using IModelDocExtension::SelectByID2 with a mark number of 1.` |
| **I1-6** | `sheet_metal` 两条 limitation 对「开放轮廓」说法相反 | **存疑** | **存疑**（★ **已抽查，同意存疑**） | `capabilities.yaml` 逐字：`SW2026 SP01.1 已真机验证现代 BaseFlange FeatureData、**开放 U 型轮廓双折弯**…` ★ **对** `**真机实测状态（2026-10-01，SW 2026 SP4.1）**：… ✓ create_base_flange（但**只对闭轮廓成立**，开放折线的轮廓法兰实测失败）` —— ★ **两处版本号不同（SP01.1 vs SP4.1），可被「版本间修复」调和，而仓内没有任何一处写出这条调和** | ★ **无** —— 官方侧**查不到**表述（`C:\swapi` 里 `swFmBaseFlange` / `IBaseFlangeFeatureData` 对该差异无记载） |
| **I2-1** | `topology_optimization` 收进死路表的那条已被同条目推翻且与自身 `verified` 矛盾 | 成立 | **缺陷** | `capabilities.yaml` 逐字 `⚑ 2026-10-01 **拓扑优化完整闭环真机跑通** … ⇒ **study.Results 非空、GetPlotCount == 2 …**` + `⚠ **需要许可**：… 2026-10-01 用户在 SolidNetWork License Manager 中调整并**重启 SolidWorks** 后解除` | `docs/dead-ends.md` §`### topology_optimization（verified）` 唯一一条逐字 `✅ **需要用户提供的东西**：… **在此之前，本能力无法在本机升到 verified**` ⇒ ★ 与自身标题 `（verified）` 矛盾、且**没标 🕓「本条已过期」** |
| **I2-2** | `mold_analysis` 两条真死路在死路表里**连分节都没有** | 成立 | **缺陷**（★ 与 I1-4 同批复核：`mold_analysis` 在 `dead-ends.md` **零命中**） | `capabilities.yaml` 逐字 `⚠ **仍未查证**：MoldUndercutDetect 官方是 Void … ★ **「怎么把颜色读回来」仍是未知**（铁律 5）。` + `⚠ **未验**：MoldDraftAnalysis 的**返回值语义** … ⇒ ★ 本模块**原样返回、不判定成败**。` | `C:\swapi\types\IFeatureManager\MoldUndercutDetect2.md` 逐字 `**Signature**: void MoldUndercutDetect2( System.int ColUndercut1, … )` / `全页**没有 ## Remarks**` |
| **I2-3** | `mold_tools` 死路表里唯一那一条**说的是另一件事** | 成立 | **缺陷** | `docs/dead-ends.md` §`### mold_tools（stitched）` 那一条逐字是 `⚠ **2026-10-01 实测（轮 77）：本机没有 OCP / cadquery / trimesh**…` —— ★ 该字符串被 **3 个能力逐字共用** | 同一条在 `dead-ends.md` 的 `surface_modeling` 与 `headless_open_format_writing` 两处**逐字重现**（与模具无关）⇒ ★ 而 `mold_tools` 真正的死路（`⚠ **新模块未在本机实测**`、`Col*` 结果读不回来、`InsertMoldPartingSurface` 5 参 + `InsertMoldCoreCavitySolids` 4 参语义**全部未查证**）**一条都没进表** |
| **I2-4** | `simulation_load_family_breadth` 10 条 limitations 零条入册，且 `temperature` 说法条目内相反 | 成立 | **缺陷** | `capabilities.yaml` 逐字（轮 408）`★ 另：**temperature 仍未注册** —— 报「缺必填参数」… ⇒ 按铁律 5 不猜` ★ **对**（轮 415）`**thermal** ⇐ convection / heat_flux / heat_power / **temperature** / radiation**；` + `mcp-server/tool_specs_batch58.py` 工具层**已注册** `_spec("solidworks_simulation_apply_temperature", …)` | `docs/dead-ends.md` grep `load_family` / `temperature` ⇒ **0 命中**（该能力**没有分节**） |
| **I2-5** | `simulation_loads_wiring` 说「建研究工具未挂」，工具层早已挂 | 成立 | **缺陷** | `capabilities.yaml` 末条 limitation 逐字 `⚠ **没有**「建研究」的工具 ⇒ … 建研究要用能力层 create_static_study（**未挂**）。` | `mcp-server/tool_specs_batch27.py` 逐字 `ToolSpec( name="solidworks_simulation_create_study", … module="sw_simulation", function="create_study_report", inject="sw_app",` + `capabilities.yaml::simulation_study_create` 已是 `level: verified` |
| **I3-1** | `drawing_view_operations` 表里留着已被同能力下一条推翻的「待查」 | 成立 | **缺陷**（★ **已抽查复核成立**） | `capabilities.yaml` 轮 293 条（即 `limitations[2]`）逐字 `get_view_scale_report("工程图视图1") ⇒ ★★ {ok: true, scale: 0.002 …} ✓（★ **即 ScaleRatio 确实取到了** —— 而 0.002 的**语义待查** … ★ **待核**）` + `⚠ set_view_scale_report ⇒ **仍 ok: false**（★ before/after/asked 全 null）⇒ ★ **待查**` ★ **对** 轮 294 条（即 `limitations[1]`）逐字 `① ★★ **ScaleRatio 回的是比例的两个数** —— 真机 (1.0, 500.0)（★ 即 1:500）… ⇒ ★ **所以 get_view_scale 回 0.002 是对的** ✓ ② … ⇒ ★ **正解是 set_com_member(obj, name, value)** … ★ 已改用。` | `docs/dead-ends.md` §`### drawing_view_operations（verified）` 只收进了**轮 293 那一条**（逐字含 `而 0.002 的**语义待查**`）⇒ ★ **答掉它们的轮 294 整条不在表里** |
| **I3-2** | 被筛掉的那条正是收进表里那条的**反证** | 成立 | **缺陷**（★ 含一处轮次不可考） | `capabilities.yaml` 逐字 `⚠ **未真机验证** —— 本批 4 个工具**尚未单独跑过**（★ 需要一个**有视图的工程图文档**，而本会话尚未造过一个）` ★ **对** 轮 293 条 `★★★★ **真机复验（有视图的图 · 3 个视图 工程图视图1/2/3）**` | `docs/dead-ends.md` grep `尚未造过一个` ⇒ **0 命中**；该段里**只有**轮 293 那一条 bullet |
| **I3-3** | `weldment_cut_list`「接口不可达」**只在 `capabilities.yaml` 一边** | 成立 | **缺陷**（**与 I1-1 同一条，正则漏网角度**） | `capabilities.yaml` 逐字 `create_cut_list ⚠ **接口不可达** … **取不到**` ⇒ ★ 掉出去的原因就在筛子里：正则列了 `到不了 / 不可调用 / 后端限制`，**没有 `不可达`，也没有 `取不到`** | `docs/dead-ends.md` grep `接口不可达` ⇒ **0 命中**；29 个能力标题里**没有 `weldment_cut_list`**；★ 佐证：`docs/known-facts.md` 事实 389 逐字 `★★ 结构系统（焊件切割清单）真机跑通了 —— 事实 382 的「到不了」**被推翻**` |
| **I3-4** | `sketch_edit_ops` 死路表里并排放两条互相否定的结论 | 成立 | **缺陷** | `capabilities.yaml` `limitations[0]` 逐字 `★★★ **2026-10-01（轮 164）更正轮 122 的定性**：… 轮 122 看到 type=2 报 com_error 0x80010105 就判它「**架构性限制、到不了**」并停手 —— **那是误判**。` | `docs/dead-ends.md` §`### sketch_edit_ops（stitched）` 的**第二条** bullet 逐字 `❌ **create_sketch_chamfer 到不了** … ★ 0x80010105 **正是已知事实 47 / 28 那个错误码** ⇒ 属「pywintypes 迟到绑定到不了需要真实指针的接口」这一**架构性限制** … ⚠ 按**事实 53** 停手。` ⇒ ★ **已被推翻的那条还在表里，且没有轮次标记** |
| **I3-5** | `sheet_metal_creation` 说「**三条**达不到」，下面列了**四个** | 成立 | **缺陷**（★ 纯文案错，零风险） | `capabilities.yaml` 逐字 `⚠⚠ **三条达不到**（★ 都在 known-facts 47/43 里记着）：create_one_bend（0x80010105 后端限制）· create_edge_flange（同族）· create_gusset（同族）· create_draft（CreateDefinition(3) 回 None）` —— ★ **冒号后面 4 个、标题说 3 个** | `dead-ends.md` 逐字搬的是**同一句**（故两处同错）；同域 `sheet_metal` 把这 4 个**分成两类**（前三个是 pywin32 指针限制、第四个是 `swFmDraft(3)` 不在 35 常量里）⇒ ★「三条」可能只指前一类，但那条 limitation 自己没这么写 |

**I 组补充（原稿判不成立）**：`I-1` / `I-3` 的 `F6`（公差 `geometric_tolerance` ↔ `gtol_insert`）判**不成立**（主从分工 + 显式互引）；`I-2` 另列 4 项「想过但**不报**」（结构上不可能 / 主语是某 backend 无法判定 / 相似名字顶替 / 属未完成而非已走死）。

### J 组 · selection 参数：官方要求什么 vs 我们给什么

| ID | 主题 | 原稿判定 | 统一判定 | 仓内那一段 | 官方/目标那一段 |
|---|---|---|---|---|---|
| **J1-1** | `surface_fill` 的 `selection` 从不按官方 Mark=1 选边 | 成立(对不上) | **缺陷** | `scripts/sw_surface_features.py` 逐字 `_declarative = bool(str(selection or "").strip())` + `for m, _e in ([] if _declarative else picked):` ⇒ ★ **该字符串只被当成布尔量、从不解析、从不选边** | `C:\swapi\types\IFeatureManager\InsertFillSurface2.md` §Remarks 逐字 `You must use IModelDocExtension::SelectByID2 and the following Mark values to select edges that bound the surface to be filled:` / `- Boundary curves = 1` |
| **J1-2** | `swept_flange` 的 `profile_selection` 解析器**根本不认 `"SKETCH"`** | 成立(对不上) | **缺陷** | `mcp-server/tool_specs_batch4.py` 逐字 `profile_ref = resolve_entity(model, p.profile_selection, "SKETCH")`；而 `scripts/sw_selection_spec.py` 逐字 `ENTITY_KINDS = ("EDGE", "FACE", "VERTEX")` + `if k not in ENTITY_KINDS: raise EntitySelectionError(` ⇒ ★ **`profile_selection="index:0"` 必抛** | `C:\swapi\examples\Create_Swept_Flange_Example_CSharp.md` 逐字 `boolstatus = Part.Extension.SelectByID2("Sketch6", "SKETCH", …, true, 0, null, 0); swProfileSketch = (Feature)((SelectionMgr)Part.SelectionManager).GetSelectedObject6(1, -1);` + `Edge[] swPathObj = new Edge[1];` |
| **J1-3** | `sketch_trim` 的 `selection` 给不出官方要的 pick point | 成立(对不上) | **缺陷** | `scripts/sw_sketch_edit_ops.py` 逐字 `ok = get_com_member(seg, "Select4", bool(append), _empty_callout())`；`_select_spec(model, selection, *, mark: int = 0)` 的 **`mark` 形参在函数体里没被使用** | `C:\swapi\types\ISketchManager\SketchTrim.md` §Remarks 逐字 `Two intersecting sketch segments; … Use IModelDocExtension::SelectByID2 with Mark = 0 to select two sketch segments, **specifying their pick points**.` |
| **J2-1** | `solidworks_fillet` Simple fillet 官方要 **Mark = 1**，我们一个 mark 都没给 | 成立(=缺陷) | **缺陷**（★ **已抽查复核成立**） | `scripts/sw_part.py::fillet` 逐字 `return model.FeatureManager.FeatureFillet( 195, radius, 0, 0, None, None, None )` ⇒ ★ 第 3 实参 `Ftyp = 0`；`scripts/sw_selection_spec.py::select_object` 逐字 `get_com_member(obj, "Select4", bool(append), _empty_callout())` ⇒ ★ **`Mark` 从未被写进去** | `C:\swapi\types\IFeatureManager\FeatureFillet.md` §Remarks 逐字 `Simple fillets` / `1. Call IModelDocExtension::SelectByID2 with Mark = 1 to select the edges to fillet.` / `2. Specify Ftyp with swFeatureFilletType_e.swFeatureFilletType_Simple.`；`C:\swapi\enums\swFeatureFilletType_e.md` 逐字 `swFeatureFilletType_Simple \| 0`；签名逐字 `FeatureFillet( System.int Options, System.double R1, System.int Ftyp, …)` |

**J 组补充（原稿判达标 / 查不到）**：`J-1` 另 11 条判**不成立**（`hole_wizard` / `edge_flange` / `gusset` / `draft` / `chamfer`+`fillet` / 草图五件 / 孔族五条 / `part_loft` / `part_sweep` / `surface_knit`）；仿真载荷族 17 条判**查不到**（`C:\swapi\types\` 无 `ICWLoadsAndRestraintsManager`）。
`J-2` 另 2 条判**达标**（`part_loft` mark=1 / `part_sweep` 轮廓 1 · 路径 4）、1 条**不成立**（`chamfer` 官方无选区前置）、9 条**查不到**。

---

## 二 · ★★ 抽查证伪（8 条）

**抽样口径**：把上表 72 条编成 72 元列表，**固定种子 `random.Random(202)`** 无放回抽 8 条（可复算）。
**抽中**：`F5-1` · `H3-05` · `I1-1` · `I1-2` · `I1-4` · `I1-6` · `I3-1` · `J2-1`。
**证伪法**：★ **每条都自己回到原文**（`D:\AI\SW\capabilities.yaml` / `docs\dead-ends.md` / `scripts\*.py` / `mcp-server\*.py` / `C:\swapi\**`），不采信稿里的转述。

| # | 条目 | 原稿判定 | **裁判判定** | 复核到的原文证据 | 结论 |
|---|---|---|---|---|---|
| 1 | **F5-1** knit mark 投递 | 存疑 | **存疑** | 读 `scripts/sw_surface_features.py:129/210`：`def _select_all_surface_faces(model, mark: int = 1)` → `selected = _select_all_surface_faces(model, mark=1)` → 函数体内逐字 `if _sel(f, append=True, mark=mark):` ★ **确无 `model=`**；读 `scripts/sw_part.py:294/331/352`：`def _select_com_object(obj, append=False, mark=0, model=None)` · `if model is not None:` · `#: ③ ★ 最后退回 Select4 + 空 VARIANT（★ 保原行为；⚠ **它丢 mark**，已知）` | ★ **机制成立**（保 mark 的分支结构上不可达）；但**最终 mark 是否真丢**取决于中间那条已标 Obsolete 的 `Select2` 是否成功 ⇒ **保持存疑，不升级** |
| 2 | **H3-05** Tab and Slot | 成立 | **成立** | 全仓 grep `swFmTabAndSlot\|TabAndSlot\|tab_and_slot` ⇒ **92 处命中逐条看过**：全部落在 `docs/`（`family-coverage.md` / `api-map.json` / `known-facts.md` 讲 `ITabAndSlotGroupData`）、`specs/`（含草稿自身与 `api-pre/api-06-features.md`）、`_enum.txt`（`swFmTabAndSlot = 88`）、`_all_families.json` / `makepy-property-direction.json` / `solidpilot-salvage` CSV ⇒ ★ **`scripts/` `mcp-server/` `tools/` 三个目录的 `.py` 里零命中**；`scripts/check_interface_member_ownership.py:232` 那处是**接口名**、不是该常量 | ★ **零实现属实**。附带确认：它**在官方 35 常量名单内**（`_enum.txt` 给出 `swFmTabAndSlot = 88`）⇒ 是可走通的活入口，缺口成立 |
| 3 | **I1-1** `weldment_cut_list` 旧结论 | 成立 | **成立** | `capabilities.yaml:2811` 逐字 `⚠ **真机 1/3**：… create_cut_list ⚠ **接口不可达** —— 报「IFeatureManager.InsertWeldmentCutList2 … **取不到**」`；`capabilities.yaml:2820`（**同一能力的 `evidence`**）逐字 `★★★ 2026-10-03（轮 496-498）**更正上面那条…** dispid = 174 … **4/4 全调通** … ⇒ ★ **故本条据据它做出的「到不了」结论不成立**。` | ★ **同一份清单里两句话对同一件事说了相反的话**，成立 |
| 4 | **I1-2** `surface_ref_ops` 旋转曲面旧结论 | 成立 | **成立** | `capabilities.yaml:3655`（`surface_ref_ops` 的 limitation）逐字 `★★ **旋转曲面本条不登记** … ⇒ ★★ 按**事实 53** … **停下**。`；`capabilities.yaml:3826/3841/3842`（`surface_revolve`）逐字 `label: 旋转曲面（★ **真机建成**·★★ 根因是"必须有中心线"）` · `★★ 2026-10-03（轮 529）**真机建成** … ⇒ **建成 曲面-旋转1**` · `★★★ **而根因是一组对照定下的：「无中心线」那组**不成** … 故：…真因是**前置缺中心线** … ★ 而它**修正了一个归因**。` | ★ 官方原话那个 `centerline` 正是后来定下的根因（`InsertRevolvedRefSurface.md` 逐字 `…around a centerline.`）⇒ **旧 limitation 停在「不登记/停下」** ⇒ 成立 |
| 5 | **I1-4** `surface_untrim` 正则漏网 | 成立 | **成立** | `docs/dead-ends.md` grep `surface_untrim\|surface_thicken_silent_noop\|surface_ref_ops\|topology_optimization\|mold_analysis` ⇒ **只命中 `topology_optimization`（第 139 行）**，★ **其余四个能力名全部零命中** ⇒ 而 `capabilities.yaml` 里 `surface_untrim` 逐字有 `…面那条路五个组合全败…★ 不碰它。` | ★ **「语义上是死路、字面不在 `DEAD` 白名单」**成立。★ **顺带实证**：同一次 grep 直接坐实了 `I1-3` / `I2-2` 两条 ⇒ **一次复核证三条** |
| 6 | **I1-6** `sheet_metal` 开放/闭轮廓 | 存疑 | **存疑** | `capabilities.yaml:1119` 逐字 `SW2026 SP01.1 已真机验证现代 BaseFlange FeatureData、**开放 U 型轮廓双折弯**…`；`capabilities.yaml:1120` 逐字 `**真机实测状态（2026-10-01，SW 2026 SP4.1）**：… ✓ create_base_flange（但**只对闭轮廓成立**，开放折线的轮廓法兰实测失败）` | ★ **两句确实相反**，但 ★ **版本号不同**（SP01.1 vs SP4.1）⇒ 可被「版本间修复」调和而仓内**没有任何一处写出这条调和**；且**官方侧查不到**该差异的表述 ⇒ **同意原稿判存疑，不升级为成立** |
| 7 | **I3-1** `drawing_view_operations` 待查被推翻 | 成立 | **成立** | `capabilities.yaml` 逐字：轮 294 条（= `limitations[1]`）`① ★★ **ScaleRatio 回的是比例的两个数** —— 真机 **(1.0, 500.0)**（★ 即 **1:500**）… ⇒ ★ **所以 get_view_scale 回 0.002 是对的** ✓ ② … **正解是 set_com_member(obj, name, value)** … ★ 已改用。`；轮 293 条（= `limitations[2]`）`…而 0.002 的**语义待查** … ★ **待核**）` + `⚠ set_view_scale_report ⇒ **仍 ok: false** … ★ **待查**`；`docs/dead-ends.md:41` §`drawing_view_operations（verified）` **只收进了轮 293 那一条** | ★ 死路表把读者交给两个「待查」开口，而**答掉它们的那一条不在表里** ⇒ 成立。★ 一处提醒：轮 294 ③ 另说「改用赋值后仍写不进」⇒ 原稿「已答掉」的措辞**略宽**，但核心指控（表里留着开口、答案不在表里）**准确** |
| 8 | **J2-1** `solidworks_fillet` 需 Mark=1 | 成立 | **成立** | `C:\swapi\types\IFeatureManager\FeatureFillet.md:44-48` 逐字 `Simple fillets` / `1. Call IModelDocExtension::SelectByID2 with Mark = 1 to select the edges to fillet.` / `2. Specify Ftyp with swFeatureFilletType_e.swFeatureFilletType_Simple.`；`:14` 签名逐字 `FeatureFillet( System.int Options, System.double R1, **System.int Ftyp**, … )`；`C:\swapi\enums\swFeatureFilletType_e.md:20` 逐字 `swFeatureFilletType_Simple \| 0`；`scripts/sw_part.py:989-991` 逐字 `return model.FeatureManager.FeatureFillet( 195, radius, 0, 0, None, None, None )` ⇒ ★ **第 3 实参正是 `Ftyp` 且 = 0 = Simple**；`scripts/sw_selection_spec.py:172-180` 逐字 `def select_object(model, obj, *, append=False) -> int:` / `get_com_member(obj, "Select4", bool(append), _empty_callout())` ⇒ ★ **无 mark 通道** | ★ 四段原文**逐字对齐**：官方对 Simple 分支要求 Mark=1、我们走的**正是** Simple 分支、选区 mark **恒未设** ⇒ **成立**（原标注的 `FeatureFillet` 已 Obsolete 属**附注不另计**，处理得当） |

### ★★ 抽查结论（本次最重要的数）

| 口径 | 数 |
|---|---|
| 抽查 | **8** |
| **判为成立** | **6** |
| 判为存疑 | **2**（`F5-1` · `I1-6` —— ★ **两条原稿自己就判了存疑，裁判复核后同意其存疑、不升级**） |
| **判为不成立** | **0** |
| **★ 成立率** | **6 / 8 = 75%**（★ 若把「原稿已自判存疑、复核后维持」也算对，则 **8/8 = 100% 判定正确，0 条证伪成功**） |

★ **诚实读法**：**8 条里没有一条被证伪成「不成立」** —— 这组对账稿的**判定口径可信度高**。
★ 但**成立率只有 75%**，因为 2 条停在「存疑」。★ 这两条的共性是**同一个根因**：`_select_com_object` 不传 `model=` ⇒ 保 mark 分支不可达（`F5-1` 静态可证、运行结果不可证）。
⇒ ★★ **换句话说：真正需要复核员下真机结论的，只有「mark 到底丢没丢」这一类**（本组 `F5-1` `F4-4` `J2-1` 同族），其余都能静态判死。
★ 另：**重复计数**未在抽查中暴露新的（`F4-1`≡`J2-2`、`I1-1`≡`I3-3` 属**同一条被两份稿各记一次**，见 §四）。

---

## 三 · 重复与去重（★ 72 条 ≠ 72 个独立缺口）

| 重复簇 | 涉及条目 | 独立缺口数 |
|---|---|---|
| 钣金 gusset 只选 1 面 | `F4-1` ≡ `J2-2` | 1（算 2 次） |
| 焊件端面 / 支撑腿无语义筛选 | `F4-3` ≡ `J2-3` + `J2-4` | 2（算 3 次） |
| `_select_com_object` 不传 `model=` ⇒ mark 投递链 | `F4-4` ∪ `F5-1` ∪ （`J2-1` 同族） | **1 个根因**（算 3+ 次） |
| `weldment_cut_list`「接口不可达」 | `I1-1` ≡ `I3-3`（前者判「内部自相矛盾」、后者判「正则漏网」，**其实是同一条的两个面**） | 1（算 2 次） |
| 曲面四件「写好了没挂工具」 | `H3-15/16/17/18` | 4（★ 不重复，且是全组最便宜的 4 条） |

⇒ ★ **实锤独立缺口 ≈ 72 − 5 = 67 条**（其中「重复」指**同一个修法能一次消掉**，不是指内容不真）。

---

## 四 · ★★★ 分级

### 立刻要改（4 条 · 全是**一处改动能一次消掉多条**的）

| # | 事项 | 依据 | 建议动作 |
|---|---|---|---|
| **①** | **★ 全组口径分裂：「成立」= bug 还是 = pass，15 份稿分成两派且无一处声明** | §〇 的极性表（F 派 vs G 派） | 在 15 份稿各加**一行图例**，或统一改写为「判为缺陷 / 判为达标 / 存疑」。★ **不做这一条，任何跨文件的「成立率」都不可比** —— 这也是本次抽查必须逐条判极性的原因 |
| **②** | **★ `tools/gen_dead_ends.py` 的 `DEAD` 正则是中文措辞白名单 ⇒ I 组 11 条里至少 7 条自动消解** | `I1-3` `I1-4` `I1-5` `I3-3`（实测漏抓：`静默不成` `全败` `不抛但特征树不变` `没建成` `不可达` `取不到` **全部不在白名单**）；`I2-2` `I2-3` `I2-4`（整节缺席） | ★ **本组投入产出比最高的一条**。给 `DEAD` 补上这 6 个词（≈6 处正则编辑）⇒ `dead-ends.md` 重新生成即覆盖 7 条。⚠ 补词前先确认它们**不**会把 `stitched` 的「未查」类条目也卷进来（`I-2` 已自己指出 `mold_parting_geometry` 属「未完成」而非「已走死」） |
| **③** | **`capabilities.yaml` 内部 4 处自我否定**（同一条目里两句话打架） | `I1-1`（接口不可达 vs dispid=174 4/4）· `I1-2`（旋转曲面不登记 vs 真机建成）· `I2-4`（temperature 未注册 vs 已注册已验）· `I2-5`（建研究工具未挂 vs 早已挂成 ToolSpec） | ★ **不要删旧句**（那是历史），★ 在旧 limitation 后补 `🕓 **本条已过期（YYYY-MM-DD，轮 N 标注）**` —— ★ **本仓已有这个约定**，`dead-ends.md` 里的 `topology_optimization` 同族就在用。四处各改一行 |
| **④** | **`sheet_metal_creation`「三条达不到」下面列了四个** | `I3-5`（`capabilities.yaml` 与 `dead-ends.md` **同错**，因后者是机械搬运） | 改一个数字（或把标题改成「四条」，或按同域 `sheet_metal` 的两类分法补一句「前三项受 pywin32 指针限制、`create_draft` 是常量不在白名单」）。★ **零风险** |

### 要记档（按「改动量 / 已有资产」排序）

| 优先 | 事项 | 条数 | 为什么这个顺序 |
|---|---|---|---|
| **①** | **曲面 4 件：实现 + 真机证据都在，只差一个 `ToolSpec`** | `H3-15/16/17/18` | ★ **全组最便宜的 4 条** —— 宪法 §I 缝合优先：不用从零写，`scripts/` 里的代码与 `tools/prove_*.py` 的证据现成，各加一个 `ToolSpec` 即可。★ 其中 `H3-17` `H3-18` **是仓库自己在 `limitations` 里写下的缺口** |
| **②** | **装配 3 件：能力层封装已写好，`mcp-server` 对 `sw_assembly_doc` 零引用** | `H2-3` `H2-5`（+ `H2-2` `H2-4` 只差 arity 登记→实现） | 同型：**挂上就行**。★ `H2-2` 与 `H2-4` 连封装都是零调用（登记表 ≠ 能力，`sw_assembly_doc.py` 文件头自己写着这句） |
| **③** | **G 组导出收尾 8 处** | `G2-1/2/3` `G3-1/2/3/4/5` | ⚠ ★ **必须先记一条限定**：三份稿自己都写明 —— ★ **从 MCP 工具层调用看不到这些缺口**（`solidworks_export_dxf/_bmp/_image` 都走 `*_report` 包装，`_export_report` 判据是 `err is None and exists and size > 0`）；★ **只有直接调 `scripts/sw_export.py` 的裸函数（脚本 / 探针 / 其它仓内代码）才暴露**。⇒ 优先级**不高**，但要在册，别让下一个人以为「导出收尾检查全覆盖了」 |
| **④** | **H 组真缺口 18 条**（钣金 9 / 焊件 3 / 模具 2 / 曲面 4） | `H3-01…14` | 全是真缺口（仓内零实现）；其中 `H3-04/05/06/07` 走 `swFm*` 常量的 `CreateDefinition` 路，与仓内现有 4 处调用**同构** ⇒ 改动量最小 |
| **⑤** | **H 组交付 / 仿真 / 外观 10 条** | `H4-01…10` | 全是真缺口；`H4-03`（打印）与 `H4-05`（AP242）都只需扩 `ExportFormat` 枚举 + 一个薄包装 |
| **⑥** | **F 组 mark / 前置 6 条** | `F1-1` `F1-2` `F3-5` `F4-1` `F4-2` `F4-3` | ★ `F1-1` 与 `F1-2` **共用同一个 `pre_call`**（官方两条 Remarks 的 mark 表逐字同形 1/4）⇒ **边际成本≈0**。⚠ `F3-5`（`part_wrap`）★ **`preselect-family-b.md` 已记录 ⇒ 是复核确认、不要重复修**；且同族 `part_sweep`/`part_loft` 已按 batch47/48 的修法补上 `pre_call` |
| **⑦** | **J 组 selection 4 条** | `J1-1` `J1-2` `J1-3` `J2-1` | `J1-2` 最硬（`resolve_entity` 拒绝 `"SKETCH"` ⇒ **必抛**，是死代码）；`J1-1` 的实际后果是「该参数只起强制回退作用」（返回带 `fallback_from_declarative`，**不静默**） |
| **⑧** | **`_select_com_object` 不传 `model=` 的全族** | `F5-1` `F4-4` `J2-1` 同族 | ★ **一个根因**：给调用点补 `model=` 即可让保 mark 分支可达。★ 但 `F5-1` 已判**存疑** ⇒ ★ **要改之前先跑一次真机**确认 mark 确实丢了（否则改了也看不出差别） |

### 不用管

| 事项 | 条数 | 理由 |
|---|---|---|
| **★ 本次抽查判「不成立」的** | **0 条** | ★ 8 条抽查**无一被证伪** ⇒ 没有需要「因证伪而不用管」的项。★ 报告成立率时不能写成「8 条都对、所以都对」—— **实数是 6 成立 / 2 存疑** |
| **原稿自己判「不成立 / 查不到」的全部条目** | ≈ **38 条** | F-1 的 4 条（官方页无 mark 表）· F-3 的 3+1（wrap 三档 mark 对得上 / `InsertAxis2` 官方无 mark 表）· F-4 的 5 条 mark 数值 · F-5 的 4 条（extend/revolve/trim-曲面/trim-草图官方没给 mark）· G-1 的 0 条 · H-3 的 3 条（模具分割线分析 / 插入模具文件夹 / 沟槽焊缝 —— API 层查不到）· H-4 的 8 类（eDrawings / MBD 加载类 / CosmosWorks 启动类等）· I 的 `F6`（公差主从互引）· J-1 的 11 条 + 仿真族 17 条（查不到）· J-2 的 1 条（chamfer 无前置）+ 9 条查不到。★ 这些按铁律 3/5 **不顶替、不硬报，处理得当** |
| **重复计数的 4 簇** | 5 条 | 见 §三。★ **不是「不用管」，是「修的时候按一处算」** —— 否则会把工作量估高 5 条 |
| **`H3-22` 成形工具（存疑）** | 1 条 | 官方文档自身矛盾（专用方法标废弃并指向 `CreateDefinition`，而 35 常量名单里只有 `swFmFormToolInstance`「library form tool」）⇒ ★ 原稿正确地**既不判成立也不判不成立** |

---

## 五 · 统计（交付口径）

| 口径 | 数 |
|---|---|
| 本组对账稿 | **15** 份（`F-1/3/4/5`、`G-1/2/3`、`H-2/3/4`、`I-1/2/3`、`J-1/2`） |
| **核了** | **383**（★ ⚠ **单位不统一**，必须随数报出：`F-1` 6 · `F-3` 5 · `F-4` 6 · `F-5` 6 · `G-1` 4 · `G-2` **8 个导出入口** · `G-3` 5 · `H-2` **16 处** · `H-3` **22 处** · `H-4` **132 条命令** · `I-1` **51 条 limitation** · `I-2` **12 个能力 / 86 条 limitation** · `I-3` 6 · `J-1` 15 · `J-2` 15） |
| **对不上** | **72** 条（与 15 份稿各自声明的对不上数**逐份相加完全吻合**，且与本文件总表行数一致） |
| ├ 原稿判「成立」（= 缺陷） | 55 |
| ├ 原稿判「不成立」（= 缺陷，极性 B） | 13（`G2-1/2/3`、`G3-1/2/4`、`J2-1…4`） |
| ├ 原稿判「部分成立」 | 2（`G3-3` `G3-5`） |
| └ 原稿判「存疑」 | 2（`F4-4` `F5-1`） |
| **抽查** | **8**（种子 202，无放回） |
| **★ 成立率** | **6 / 8 = 75%**（成立 6 · 存疑 2 · **不成立 0**） |
| 实锤独立缺口 | ≈ **67**（72 − 5 条重复） |
| 分级 | **立刻要改 4 · 要记档 8 组 · 不用管 0 条证伪项 + ≈38 条原稿自判不成立/查不到** |

★ **三句话**：
① **这组稿没有编造的条目** —— 8 条抽查**零证伪**，2 条停在存疑的都是原稿自己就标了存疑的。
② **最该马上动的是 `gen_dead_ends.py` 的正则**（一处改动消解 ≥7 条）和**口径图例**（不做则跨文件不可比）。
③ **最便宜的是曲面四件 + 装配三件** —— 代码和真机证据都在仓里，只差接线。