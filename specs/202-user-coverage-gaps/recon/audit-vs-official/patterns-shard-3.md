# patterns-shard-3 —— 分歧根因分类与「批量可行性」判断（域 08-mold-costing / 09-simulation / 10-misc）

**分片范围**：audit-08 ～ audit-10（模具+Costing · 仿真 · 其余）
**纪律**：★ 只读核对；★ 未运行 SolidWorks；★ 未运行 pytest；★ 未改动仓内任何文件（只新建本文件）。
**方法**：逐份逐行抽「分歧表」每一行，**一行一条，不合并、不丢弃**；每条给可搜索原文片段（文件名 + 片段，**不写行号**）。

---

## 〇、本分片实际读到的文件（6 份）

| 文件 | 核对面 | 核了几处 | 报了几条 |
|---|---|---|---|
| `audit-08-mold-costing-A.md` | A · 签名一致性 | 38 成员 / 45 调用站点 | 1 |
| `audit-08-mold-costing-B.md` | B · 前置与 mark | 35 处（`sw_mold.py` 12 · `sw_measure.py` 23） | 3 |
| `audit-08-mold-costing-C.md` | C · 废弃链与枚举取值 | 43 处 | 2 |
| `audit-09-simulation-B.md` | B · 前置与 mark | 59 处 | 5 |
| `audit-10-misc-B.md` | B · 前置与 mark | 20 处 | 6 |
| `audit-10-misc-C.md` | C · 废弃链与枚举取值 | 108 处 | 10 |
| **合计** | | | **27 条** |

> ★★ **须知**：`audit-08-A.md` / `audit-09-B.md` / `audit-10-B.md` / `audit-10-C.md` 是**在本轮我开始工作之后才出现**的（并发写的）。本分片在收尾时重列目录，`audit-09-A/C`、`audit-10-A/C` 仍不存在 ⇒ **本分片不是 08～10 的全量**，结论按此限定读。

---

## 一、全量分歧表（27 条，一行一条）

> 「批量可行性」判据两条：**(a) 能不能用一个静态脚本把它全找出来**；(b) 能不能用一个共用修法把它全改掉。取值 高 / 中 / 低，理由见第二节。

| # | 文件 | 核对面 | 根因类（本文切法） | 我们的原文（可搜索片段） | 官方的原文（可搜索片段） | 置信度 | 批量可行性 |
|---|---|---|---|---|---|---|---|
| 1 | audit-08-mold-costing-A | A | **C3 参数个数不符** | `scripts/sw_measure.py`：`ok_calc = _get(m, "Calculate")` | `C:\swapi\types\IMeasure\Calculate.md`：**Signature**: `System.bool Calculate( System.object Entities )`；`C:\swapi\examples\Measure_Selected_Entities_Example_CSharp.md`：`status = swMeasure.Calculate(null);` | 高 | **高** |
| 2 | audit-08-mold-costing-B | B | **C1 前置没做（先选）** | `scripts/sw_mold.py`：`调用前须由调用方选好**拔模方向参考**（边线/基准面/轴）——` ／ `"InsertMoldPartingLine 返回 None —— 常见原因：未选拔模方向参考"` | `IFeatureManager\InsertMoldPartingLine.md`：`you must select the direction of pull and the edges for the parting line by calling SelectByID2 with the following Marks:` ／ 表 `Direction of pull` / `1` ／ `Parting line edges` / `4` | 高 | 中 |
| 3 | audit-08-mold-costing-B | B | **C1 前置没做（先选）** | `"InsertMoldPartingSurface 返回 None —— 常见原因：未先建分型线，或未选面"` | `InsertMoldPartingSurface.md`：`a face (direction of pull) has a mark of 1 and edges (parting lines) a mark of 4.` | 中 | 中 |
| 4 | audit-08-mold-costing-B | B | **C2 官方源覆盖误判** | `sw_mold.py` 模块 docstring：`⚠ **多个参数语义查不到**（CHM 无这些方法的独立说明页、\`C:\swapi\` 未收录、来源也未提供）` ／ `"InsertMoldCoreCavitySolids 返回 None —— 常见原因：未先建分型面"` | `InsertMoldCoreCavitySolids.md`：`## Remarks` ／ `To use this method:` ／ `- The Parting Line feature must exist.` ／ `- A sketch describing the outline of the mold block must exist. The sketch must be perpendicular to the pull direction.` | 高 | **高** |
| 5 | audit-08-mold-costing-C | C | **C4 用了废弃成员** | `return get_com_member(fm, "MoldUndercutDetect",` ／ `int(col_undercut), int(col_base), bool(b_coord_input), float(dx), float(dy), float(dz))` | `MoldUndercutDetect.md`：`Obsolete. Superseded by MoldUndercutDetect2.` ／ 后继页 `void MoldUndercutDetect2( System.int ColUndercut1, System.int ColUndercut2, System.int ColOccluded, System.int ColStraddle, System.int ColBase, System.bool BCoordInput, System.double Dx, System.double Dy, System.double Dz )` | 高 | 中 |
| 6 | audit-08-mold-costing-C | C | **C5 枚举取值不是合法成员** | `int(option),            # 6 Int32 未查证`（docstring 亦写 `⚠ **8 个参数里只有 3 个的语义可推断**`） | `InsertMoldPartingSurface.md`：`- **Smooth**: Smooth mold parting surface as defined by swPartingSurfaceSmoothingType_e`（第 6 形参即 `System.int Smooth`）／ `swPartingSurfaceSmoothingType_e.md`：`enum_member_count: 2`，成员表只有 `swPartingSurfaceSharp \| 1 \|`、`swPartingSurfaceSmooth \| 2 \|` | 高 | **高** |
| 7 | audit-09-simulation-B | B | **C1 前置没做（先选）** | `scripts/sw_topology.py` · `create_preserved_region`：`get_com_member(control, "SetIncludeRegionDepth2", True)` —— 函数体既不读选区、也不传面 | `Create_Topology_Study_Example_VBA.txt`：`CWTopoPreservedRegionObj.SelectFaces((DispArrayForPreservedRegion))` | 高 | 中 |
| 8 | audit-09-simulation-B | B | **C1 前置没做（先选）** | `create_symmetry_control`：`get_com_member(control, "SelectSymmetryType", int(symmetry_type))` | `CWTopoSymmetryControlObj.SelectSymmetryType 0` ／ `CWTopoSymmetryControlObj.SelectFirstSymmetryPlane sDispObjPlane1` | 高 | 中 |
| 9 | audit-09-simulation-B | B | **C1 前置没做（先选）** | `create_demold_control`：`get_com_member(control, "SelectDemoldDirection", int(direction))` | `CWTopoDemoldControlObj.SelectDemoldDirection 0` ／ `CWTopoDemoldControlObj.SelectPlaneForDirection sDispObjPlane`（另一形态 `SelectEdgeForPullDirection sDispObjEdge`） | 高 | 中 |
| 10 | audit-09-simulation-B | B | **C6 事务/调用序层级错** | 7 个 `create_*` 只在**约束对象**上开事务：`return _edit(constraint, _configure)`；同模块 `set_topology_goal` 却走 `_edit(manager, _build)` | `CWTopologyStudyManagerObj.BeginEdit` → `CWTopologyStudyManagerObj.CreateStressConstraint(ErrorCodeObj)` → `ErrorCodeObj = CWTopologyStudyManagerObj.EndEdit()` | 高 | 中 |
| 11 | audit-09-simulation-B | B | **C7 成员名不符（大小写/别名）** | `sw_simulation.py` · `get_cosmosworks`：`cosmos = get_com_member(addin, "CosmosWorks")` | `Analyze_Part_Example_VB.htm`：`Set COSMOSWORKS = CWObject. COSMOSWORKS` ／ `Create_Topology_Study_Example_VBA.txt`：`Set COSMOSWORKS = CWAddinCallBack.COSMOSWORKS` | 中 | 中 |
| 12 | audit-10-misc-B | B | **C2 官方源覆盖误判** | `scripts/sw_ref_geometry.py`：`"selection_mark": "★ 官方 Remarks 只说「these marks」、**未给取值表** ⇒ 不假定"`；★ 调用前**无任何选择动作** | `IFeatureManager\InsertRefPlane.md`：「Before calling this method, you must have selected the reference entities using these marks with SelectByID2:」／「- 0 = First reference entity」「- 1 = Second」「- 2 = Third」 | 高 | **高** |
| 13 | audit-10-misc-B | B | **C1 前置没做（先选）** | `scripts/sw_loft.py`（`_blend_args` / `_cut_blend_args` 各一处）：`False,                   # UseAutoSelect` | `InsertProtrusionBlend2.md` / `InsertCutBlend.md`：「When UseAutoSelect is false, the user must select the bodies that the feature will affect.」 | 高 | 中 |
| 14 | audit-10-misc-B | B | **C8 前置过严（误加门禁）** | `create_loft_report`：`if use_selected_profiles and sel_n < 2:` ／ `"error": "放样至少要选 **2 个轮廓**（★ mark=1 —— 官方 Remarks）；"` | `InsertProtrusionBlend2.md`：「You can use any number of profiles; however, if you select only one profile, then any selected guide curves must be closed curves.」 | 高 | 中 |
| 15 | audit-10-misc-B | B | **C1 前置没做（先选）** | `sw_review.py` · `set_standard_view`：`model.ShowNamedView2(str(view_name), -1)`（函数内无任何选择步骤，也不区分文档类型） | `IModelDoc2\ShowNamedView2.md`：「To set a named view to the active view in a drawing, the drawing view that contains the named view must be selected.」 | 中 | 中 |
| 16 | audit-10-misc-B | B | **C9 对官方原文的转述失真** | `sw_helix.py` docstring：「官方示例显示要先**选中一个圆**（`SelectByID2` + `CreateCircle`）」 ／ 报错 `"最常见原因：**没有选中定义直径的圆**（官方示例先 SelectByID2 选圆再调）。"` | `C:\swapi\examples\Create_Spiral_Example_VB.md`：`SelectByID2("Front Plane", "PLANE", …, 0, Nothing, 0)` ／ `swModel.ClearSelection2 True` ／ `CreateCircle(0#, 0#, 0#, 0.021866, 0.001156, 0#)` | 中 | 低 |
| 17 | audit-10-misc-B | B | **C10 官方源冲突（不可判定）** | `sw_export.py` · `export_flat_pattern_dxf`：`return bool(model.ExportToDWG2(` … `options, None,))`（函数内无任何选择动作） | `IPartDoc\ExportToDWG2.md`：「You must select multi-body sheet-metal features (i.e., multiple flat-pattern features) before calling this method.」**但** `examples\Export_Part_To_DWG_Example_VBNET.md`：`swPart.ExportToDWG2(…, swExportToDWG_e.swExportToDWG_ExportSheetMetal, True, varAlignment, False, False, …)` —— 同一 Action 下**无任何** SelectByID2 | 中 | 低 |
| 18 | audit-10-misc-C | C | **C4 用了废弃成员** | `sw_export.py`（`_export_generic` / `export_to_pdf`）：`success = model.Extension.SaveAs(` | `IModelDocExtension\SaveAs.md`：`Obsolete. Superseded by IModelDocExtension::SaveAs2.` | 高 | 中 |
| 19 | audit-10-misc-C | C | **C4 用了废弃成员** | `sw_export.py` · `export_to_stl`：`model.SetUserPreferenceIntegerValue(78, quality_map[quality])  # swSTLQuality` | `IModelDoc2\SetUserPreferenceIntegerValue.md`：`Obsolete. Superseded by IModelDocExtension::SetUserPreferenceInteger.`（★ **后继在另一个接口上**） | 高 | 中 |
| 20 | audit-10-misc-C | C | **C4 用了废弃成员** | `sw_export.py` · `get_mass_property_override_options`：`get_com_member(extension, "GetMassProperties", float(accuracy))` | `IModelDocExtension\GetMassProperties.md`：`Obsolete. Superseded by IModelDocExtension::GetMassProperties2.` | 高 | 中 |
| 21 | audit-10-misc-C | C | **C4 用了废弃成员** | `sw_export.py` · `_activate_source_document` except 分支：`sw.ActivateDoc2(title, False, errors)` | `ISldWorks\ActivateDoc2.md`：`Obsolete. Superseded by ISldWorks::ActivateDoc3.` | 高 | 中 |
| 22 | audit-10-misc-C | C | **C5 枚举取值不是合法成员** | `sw_export.py` · `export_to_stl`：`quality_map = {"coarse": 1, "fine": 0}` | `swSTLQuality_e.md`：`swSTLQuality_Coarse \| 1 \|` ／ `swSTLQuality_Custom \| 3 \|` ／ `swSTLQuality_Fine \| 2 \|` ⇒ **0 不是任何成员**（`"coarse": 1` 与官方一致） | 高 | **高** |
| 23 | audit-10-misc-C | C | **C4 用了废弃成员** | `sw_review.py`（`zoom_to_fit` / `clear_selection_for_preview`）：`get_com_member(model, "GraphicsRedraw2")` | `IModelDoc2\GraphicsRedraw2.md`：`Obsolete. Superseded by IModelView::GraphicsRedraw and IModelView::IGraphicsRedraw.`（★ **后继在另一个接口上**） | 高 | 中 |
| 24 | audit-10-misc-C | C | **C4 用了废弃成员** | `sw_review.py` · `activate_model_for_preview` except 分支：`sw.ActivateDoc2(title, False, errors)` | `ISldWorks\ActivateDoc2.md`：`Obsolete. Superseded by ISldWorks::ActivateDoc3.`（同 #21 的成员，换文件） | 高 | 中 |
| 25 | audit-10-misc-C | C | **C4 用了废弃成员** | `sw_document_data.py` · `_dimension_value_mm`：`return float(dimension.GetSystemValue2(configuration_name)) * 1000.0` | `IDimension\GetSystemValue2.md`：`Obsolete. See IDimension::GetSystemValue3 and IDimension::IGetSystemValue3.` | 高 | 中 |
| 26 | audit-10-misc-C | C | **C4 用了废弃成员** | `sw_document_data.py` · `_dimension_value_mm`：`return float(get_com_member(dimension, "SystemValue")) * 1000.0`（★ **属性**取法） | `IDimension\SystemValue.md`：`Obsolete. Superseded by IDimension::GetSystemValue3, …, and IDimension::ISetSystemValue3.`（★ **属性 → 方法**） | 高 | 中 |
| 27 | audit-10-misc-C | C | **C11 取值范围越界** | `sw_wrap.py`：`WRAP_MESH_FACTOR_DEFAULT = 0`（作第 5 实参传给 `InsertWrapFeature2`） | `InsertWrapFeature2.md`：`- **MeshFactor**: Accuracy of flattened triangle mesh; 1 (lowest) - 10 (highest)` | 高 | **高** |

---

## 二、按根因类汇总

| 类 | 条数 | 占比 | 分布（核对面 / 域） | 批量可行性 | 一句话理由 |
|---|---|---|---|---|---|
| **C1 前置没做（先选：mark / DispArray 喂给对象）** | 7 | 25.9% | B 面 7 条：`sw_mold.py` 2（模具）· `sw_topology.py` 3（仿真）· `sw_loft.py` 1 · `sw_review.py` 1 | **中** | ★ **发现要有三个不同匹配器**（官方 mark 表 / 官方例子的调用序 / Remarks 散文 `must select`）才抓得全；修法形态统一（读选区 → 交给对象）但**每次要选什么、走哪个成员是逐条的**。 |
| **C4 用了废弃成员** | 9 | 33.3% | C 面 9 条：`sw_export.py` 4 · `sw_review.py` 3 · `sw_document_data.py` 2（域 10-misc） | **中** | ★ **发现 100% 可脚本化**（grep 官方首行 `Obsolete.` → 名单 → 与我们的调用点取交）；★ 但**换后继不是同名同位**：本片见到 4 种形态 —— `6→9` 形参（#5）、**后继在别的接口上**（#19 `#23`）、**属性→方法**（#26）、**降级分支直接删**（#21 `#24`），逐条判定。 |
| **C2 官方源覆盖误判（有据当「查不到」）** | 2 | 7.4% | B 面 2 条：`sw_mold.py` 1 · `sw_ref_geometry.py` 1 | **高** | ★ 纯仓内自检：扫我们 docstring 里的「查不到 / 未收录 / 未给取值表 / 不假定」，把提到的成员名拿去对 `C:\swapi\types\` —— **有页即为误判**。发现与「先改正误判文案」两步都是共用改法。 |
| **C5 枚举取值不是合法成员** | 2 | 7.4% | C 面 2 条：`sw_mold.py` 1 · `sw_export.py` 1 | **高** | ★ 我们的 int 字面量 × `C:\swapi\enums\*.md` 的成员表 = 纯集合差；修法是**照表换值**。⚠ 检测器需给 `[Bitmask]` 枚举开豁免（见下）。 |
| **C3 参数个数不符** | 1 | 3.7% | A 面 1 条：`sw_measure.py` | **高** | ★ 我们调用点实参个数 × 官方 `**Signature**` 形参个数，**纯 AST + 文本**（audit-08-A 自己已经手搭过这张表）；本条的修法还是一条共用约定：`System.object` 形参按官方例子传 `null`/`Nothing`。 |
| **C6 事务/调用序层级错** | 1 | 3.7% | B 面 1 条：`sw_topology.py`（7 个 `create_*` 同形） | **中** | ★ 少开了一层 `BeginEdit … EndEdit`（管理器层）；**同模块 `set_topology_goal` 已有正确写法** ⇒ 照邻居抄即可，但「哪一层该开事务」是领域知识，脚本抓不到。 |
| **C7 成员名不符（大小写/别名）** | 1 | 3.7% | B 面 1 条：`sw_simulation.py` | **中** | ★ 名称集合差可脚本化；★ 但本条**官方两例写 `COSMOSWORKS`、我们的来源块引反射写 `get_CosmosWorks`** ⇒ COM 后期绑定大小写不敏感，是否真错**要真机探针才能定**，不能批量改。 |
| **C8 前置过严（误加门禁）** | 1 | 3.7% | B 面 1 条：`sw_loft.py` | **中** | ★ 与 C1 **方向相反**（我们多做了官方没要求的限制）；找它要逐个把我们自己的 `raise`/guard 对上官方那句「any number of profiles」，没有集合差可做。 |
| **C9 对官方原文的转述失真** | 1 | 3.7% | B 面 1 条：`sw_helix.py` | **低** | ★ 我们声称「官方示例先选圆」，官方例子其实选的是 `"Front Plane"`；**「修」= 知道真相**，真相只能逐条回官方例子读。 |
| **C10 官方源冲突（不可判定）** | 1 | 3.7% | B 面 1 条：`sw_export.py` | **低** | ★ 官方 Remarks 与官方 VB.NET 例子对同一 Action 的前置**互相矛盾**；发现容易（两段本地文本对撞），**修不了** —— 要么真机探针（本轮不许），要么立一条「冲突时以 Remarks 为准」的政策。 |
| **C11 取值范围越界** | 1 | 3.7% | C 面 1 条：`sw_wrap.py` | **高** | ★ 与 C5 **同族**（都是「我们的字面量 vs 官方定义域」），只是官方域写在参数 Remarks 的区间里（`1 (lowest) - 10 (highest)`）而非枚举成员表；抽区间 + 比大小即可。 |
| **合计** | **27** | 100% | A 面 1 · B 面 16 · C 面 10 | | |

---

## 三、★★ 结论：**能不能「一类一修」？**

### 3.1 一句话答案

> ★★ **不能「一类一修到底」—— 但可以拆成三层，而且真正该投资的是「检测器」不是「通用修法」。**
> ★ 在我这片 27 条里：**3 类（12 条 / 44%）能真正一类一修** · **3 类（16 条 / 59%）能一类一查、但必须逐条改** · **4 类（4 条 / 15%）既不好查也不好改**。

### 3.2 三层拆分

**第 1 层 · 能一类一修（发现 + 修法都共用）—— 3 类 12 条**

| 类 | 为什么能 |
|---|---|
| **C3 参数个数不符**（1 条） | 发现 = 我们调用点的实参个数 × 官方 `Signature` 形参个数；修法 = `System.object` 形参按官方例子的 `null` / `Nothing` 传。**判据与改法都是机械的。** |
| **C5 枚举非法值**（2 条） | 发现 = 我们的 int 字面量 × `enums/*.md` 成员表；修法 = 照表换值。 |
| **C11 取值范围越界**（1 条） | 与 C5 同一骨架：抽官方给的值域，和我们的字面量比大小。 |
| **C2 官方源覆盖误判**（2 条） | 发现 = 扫我们自己的「查不到」措辞 + 对 `C:\swapi\types\` 验页存在；改法 = 改文案 + 补前置。**这一类甚至不需要碰 COM。** |

⇒ 这三类的共同点：**分歧的两端都是「一张表」和「一个值」**，所以查找与修改都能写成脚本。

**第 2 层 · 能一类一查、修法逐条 —— 3 类 16 条**

| 类 | 为什么只到「查」 |
|---|---|
| **C1 前置没做**（7 条，最大类之一） | ★ **可脚本化**：官方 `types/*.md` 里 `with the following Marks` / `has a mark of N` / `must select` 三种句式都能 grep；官方例子的调用序也能 diff 出「官方喂了几何给对象、我们没有」。★ **但改法只到「形态」共用**（读选区 → 交给对象），**「选什么、走哪个成员」逐条不同**：`SelectFaces` / `SelectFirstSymmetryPlane` / `SelectPlaneForDirection` / `mark=1 面 + mark=4 边` / `UseAutoSelect=False 时用户选 body` / 工程图要先选 drawing view。 |
| **C4 用了废弃成员**（9 条，最大类之一） | ★ **可脚本化**：官方首行 `Obsolete.` 全文 grep 出名单，与我们的 `get_com_member(x,"Name")` / `obj.Method(...)` 取交 ⇒ 这 9 条 audit-10-C 已手工做过一遍（逐页读 82 处）。★ **但后继不是同名同位**，本片就有 4 种改法：`6→9` 形参 · 后继在**别的接口**上 · **属性→方法** · 降级分支**直接删**。 |
| **C7 成员名不符**（1 条） | 名字集合差可脚本化；★ 但结论要真机探针（大小写敏感性），本轮不许跑 ⇒ 只能「标出来，不能批量改」。 |

**第 3 层 · 既不好查也不好改 —— 4 类 4 条**

`C6 事务层级`（脚本抓不到「该开哪一层事务」）· `C8 前置过严`（要把我们的 guard 逐条对上官方那句散文）· `C9 转述失真`（修 = 知道真相）· `C10 官方源冲突`（**按定义不可批量**，要政策或真机）。

### 3.3 ★★ 三条比「类」本身更重要的判断

1. ★ **发现成本 ≫ 修复成本，而发现恰恰是能批量的。**
   11/11 类都能写出检测器（哪怕 C8/C9 要半手工），但改法只有 3 类共用。
   ⇒ ★★ **结论不是「写一个万能修法」，而是「先把 11 个检测器写出来，把无界的人工通读变成有限的待改清单」** —— 这正是本任务要的「一类一修」的真实形态：**一类一查**已经可行，**一类一改**只对 3 类可行。

2. ★ **C4（用了废弃成员）在本片是 9 条 / 33.3%，而它是全片最接近「真能一类一修」的大类。**
   audit-10-C 的做法本身就是证据：★ 「官方 COM 成员页 **82** 处（逐页读首行 `Obsolete.` 横幅）」—— 这**就是**一个静态脚本该干的事。
   ⇒ 若要挑一个先动，**挑 C4**：检测器最干净、条数最多、且其中 #21 #24 两条是「同函数的另一个分支已经用了 `ActivateDoc3`」⇒ **纯删除**。

3. ★ **C2（官方源覆盖误判）虽然只有 2 条，但它的危害最大，且最便宜。**
   两条都是我们在 docstring 里写下「**查不到 / 未收录 / 未给取值表 ⇒ 不假定**」，而 audit 转头就在官方页里找到了那一条。
   ⇒ ★★ 这些话会一路渗进 MCP 工具描述（工具 docstring 明写 `unverified`），**让下游把「我们不知道」当成事实**。修它**不需要真机、不需要碰 SolidWorks**，只要一个「有页即为误判」的 grep 门禁。

---

## 四、我为什么没沿用 Lead 的那套类名（★ 独立判断，非照抄）

★ Lead 的分类器（`tools/classify_audit_divergences.py`）是**关键词 first-match**。★ 我**用它自己的 `PATTERNS` 表跑了一遍**我这片 27 行，结果与我的判断 **14/27 不一致**，其中 **4 条直接落进「（未能归类）」**、**4 条落进了语义相反或明显错的类**。Lead 标签分布 vs 我的：

| | Lead 关键词表（我这片 27 条） | 我的切法（27 条） |
|---|---|---|
| 最大类 | 用了废弃成员 8 | **用了废弃成员 9** |
| 次大类 | mark 6 | **前置没做 7** |
| 第三 | 未能归类 4 · 枚举非法值 3 · 前置没做 3 | 官方源覆盖误判 2 · 枚举非法值 2 |
| 尾 | 参数个数 1 · 类型不符 1 · 返回值/出参 1 | 其余 7 类各 1 |

**四条实证的错标（可复核）**：

| 行 | Lead 标签 | 为什么错 | 我的类 |
|---|---|---|---|
| #5 `MoldUndercutDetect` | **类型不符** | 匹配规则含关键词 `double`，而官方签名单元格里写着 `System.double` ⇒ **任何带 double 的官方签名都会误命中「类型不符」** | C4 用了废弃成员 |
| #8 `SelectSymmetryPlane` 缺失 | **返回值/出参** | 官方例子里没有返回/出参；真因是漏喂平面 | C1 前置没做 |
| #14 轮廓 `< 2` 门禁 | **前置没做** | ★ **方向相反**：官方写「any number of profiles」，是我们**多做**了限制 | C8 前置过严 |
| #17 `ExportToDWG2` | **mark** | ★ 根因是**官方 Remarks 与官方例子自相矛盾** ⇒ 判不了谁对 | C10 官方源冲突 |

**另外两处我主动合并/新开**：

- ★ **合并**：「mark 值不对/没给」与「前置没做」在本片**不是两类** —— Lead 把我这 9 条拆成 6 + 3，可这 9 条里**没有一条是「mark 给了但值给错」**；它们全都是**整步没做**（我们从没把选区交给对象）。而且那 6 条「mark」里有 2 条（#4 #12）**根本不是 mark 问题，是「把有据当查不到」**。⇒ mark 在本片是**机制**，不是**根因**。
  ⚠ ★ **这是本片结论，不能外推**：Lead 全量 60 条里的 mark 类**可能**真含「值给错」的形态（那不在 08～10 的范围里）。分片结论只对本片成立。
- ★ **新开**：`C6 事务层级` / `C7 成员名` / `C8 前置过严` / `C9 转述失真` / `C10 官方源冲突` / `C11 取值范围越界` —— 这 6 类 Lead 的 10 个类名里没有，而它们的**修法各不相同**，混进现有类里会掩盖「哪些能批量」的差别。

---

## 五、本分片的覆盖缺口与限制（★ 读得到的都写在这，别当全量）

1. ★ **域 08 名为 `mold-costing`，但三份 audit 只核了 `scripts/sw_mold.py` 与 `scripts/sw_measure.py`** —— 仓里**存在** `scripts/sw_costing.py` 与 `scripts/sw_api_sldcostingapi.py`，**A/B/C 三面都没有核过它们**。
   ⇒ Costing（业主定的**三大护城河之一**）在本核对里**实际是空白**。
2. ★ **域 09 / 10 目前只有 B 面（前置与 mark）**（09 只有 B、10 有 B+C）⇒ `audit-09-A/C`、`audit-10-A` 尚不存在。
   ⇒ 若它们后来出现，本片会以**更多 A 面（签名）与 C 面（废弃/枚举）**为主，而那两面恰好是我结论里**批量可行性最高**的两类 ⇒ **本片的占比会向「可批量」方向移动**。
3. ★ **本片 27 条 vs Lead 60 条 / 17 片** —— **占比不可跨片比较**，第三节的三层拆分只对 08～10 成立。
4. ★ 本轮**未跑真机**，所以 #11（`CosmosWorks` 大小写）与 #17（官方两源冲突）只能**标记**、不能判定；本片所有「置信度」都沿用各 audit 原文的自评，未被我重新评级。
