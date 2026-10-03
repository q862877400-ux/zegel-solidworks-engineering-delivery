# JUDGE-A_B · A-* 与 B-* 两组对账稿的裁判稿

> **被裁的稿**：18 份 —— A 档 8 份（`capabilities.yaml` 的 `level` 与真机证据是否对得上）+ B 档 10 份（`audit-vs-official/` 的「高置信」条目两段原文是否名实相符）。
> **口径**：A 档与 B 档是**两件不同的事** —— A 档核「**台账条目**是否被自己的证据撑住」，B 档核「**核对表引的两段原文**是否名实相符」，B 档判「成立」＝「核对表说的分歧属实」＝「**代码与官方对不上**」。
> **纪律**：只读核验，未改动 18 份原稿与仓内任何其它文件；本文件是本次唯一写入；原文一律逐字片段、不写行号。

---

## 〇 · 计数（先把这几个数对齐，后面的分级都按它）

| 分档 | 稿件数 | 核了（自报口径） | 对不上 | 成立 | 存疑 | 不成立 |
|---|---|---|---|---|---|---|
| **A-assembly** | 1 | 4 条目 / 8 引用 | 3 | 3 | 0 | 0 |
| **A-drawing** | 1 | 5 条目 / 8 文件 | 5 | 3 | 2 | 0 |
| **A-features** | 1 | 13 条目 / 55 路径 | 4 | 1 | 3 | 0 |
| **A-moldcosting** | 1 | 5 处引用 | 3 | 3 | 0 | 0 |
| **A-sheetmetal** | 1 | 9 处 | 5 | 5 | 0 | 0 |
| **A-sketch** | 1 | 16 条目 / 29 引用 | **5**（自报 4） | 5 | 0 | 0 |
| **A-surface** | 1 | 12 条目 / 19 文件 | 4 | 3 | 1 | 0 |
| **A-weldment** | 1 | 10 处引用 | 4 | 4 | 0 | 0 |
| **B-assembly** | 1 | 9 处 | 0 | 9 | 0 | 0 |
| **B-drawing** | 1 | 9 处 | 0 | 9 | 0 | 0 |
| **B-features** | 1 | 13 处 | 2 | 11 | 0 | 2 |
| **B-misc** | 1 | 14 处 | 1 | 13 | 0 | 1 |
| **B-moldcosting** | 1 | 5 处 | 0 | 5 | 0 | 0 |
| **B-sheetmetal** | 1 | 8→7（去重） | 0 | 7 | 0 | 0 |
| **B-sketch** | 1 | 14 处 | 1 | 13 | 0 | 1 |
| **B-surface** | 1 | 8 处 | 1 | 7 | 1 | 0 |
| **B-simulation** | 1 | 8 处 | 0 | 8 | 0 | 0 |
| **B-weldment** | 1 | 6 处（去重 4） | 0 | 6 | 0 | 0 |
| **合计** | **18** | **A 94 处 · B 93 处 = 187 处** | **38** | **117** | **7** | **4** |

★ **两处需要点名的稿件自相矛盾**（不是我的数，是它们自己两处对不上）：
① **`vd50-A-sketch.md`** 抬头写「**对不上 4 处（F1–F4）**」，正文却逐条给了 **F1 / F2 / F3 / F4 / F5 五条**，且 §〇 的判定表里 `sketch_offset_on_surface` 行标的也是 **F5** ⇒ **按正文是 5 条，不是 4 条**。
② **`vd50-B-sheetmetal.md`** 抬头写「表内高置信条目 **8 处**」，同文结尾三行又写「核了 8 处 → 去重后 **7 处**」⇒ 一个数两个口径。
⇒ ★ 本裁判按**正文实际条目数**（A-sketch = 5）计，并把两处不一致原样记下。

---

## 一 · 总表 —— 38 条「对不上」（每条两段原文）

### A 侧 33 条

| # | 稿 · 编号 | 条目 | 判定 | 仓内那一段（逐字） | 目标/证据那一段（逐字） |
|---|---|---|---|---|---|
| 1 | A-assembly **F1** | `assembly_and_mates` | **成立** | `"id": "assembly_and_mates"` / `"label": "装配体与配合"` / `"level": "verified"` | `output/in-context-reference-smoke.json` → `"verdict": "fail"` · `"passed": 9, "total": 12` · `"★★ 判据①：GetRelationsCount N → N+1": {"ok": false, "detail": "0 → 0"}` |
| 2 | A-assembly **F2** | `motion_study` | **成立** | `"label": "旋转马达 Motion Study"` / evidence `"pytest tests/test_sw_motion_audit.py（旋转马达创建与结果审计）"` | `tests/test_sw_motion_audit.py` → `class FakeMotionFeature:` / `Name = "旋转马达"` / `GetTypeName2 = "AEMRotationalMotor"`；引的 `sw_motion` 符号只有 `collect_motion_study_summary` 与 `validate_motion_study_summary` |
| 3 | A-assembly **F3** | `assembly_read` | **成立** | `pytest tests（全量 0 failed；两个「钉死数量」守卫已同步：all_specs() 81 / 协议层 126）` | `tests/test_server_wiring.py` → `assert len(all_specs()) == 277`；`tests/test_mcp_protocol_layer.py` → `assert n == 322, (` |
| 4 | A-drawing **一** | `drawing_dimension_insertion` | **成立** | `tests/test_cad_reliability.py` → `assert index["drawing_dimension_insertion"]["level"] == "verified"` | 同文件顶部 → `# ⚠ 未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）。本次是清单形状与授权判据的迁移，` |
| 5 | A-drawing **二** | `drawing_current_sheet_query` | **成立** | 条目 → `负例(numerator=3 / -1:5 / 图纸名不存在)都显式拒绝` · `图纸名不存在 ⇒ 如实报"现有：[…]" ✓` | `output/sheet-scale-evidence.json` → `"passed": 5, "of": 5` · `numerator=3` · `"negative": {"ok": true, "error": "比例的两个数都必须 > 0…"}`（**只有 2 个负例，无「图纸名不存在」**） |
| 6 | A-drawing **三** | `drawing_views_and_summary` | **存疑** | 条目 → `current_sheet_info 真机回 paper_size / scale_num / scale_den / first_angle / height_mm。证据 output/drawing-views-evidence.json · sheets-summary-probe.json` | `output/drawing-views-evidence.json` → `"current_sheet_info": {"keys": ["first_angle","height_mm","paper_size","paper_size_code"]}`（无 `scale_num`/`scale_den`） |
| 7 | A-drawing **四** | `drawings_and_bom` | **成立** | evidence `["pytest tests/test_delivery_compare.py", "pytest tests/test_drawing_subskill.py（工程图与 BOM）"]` | `tests/test_delivery_compare.py` → `def test_compare_snapshots_detects_added_removed_changed_and_unchanged(tmp_path):` · `capabilities=["drawings_and_bom", "export_delivery", "drawings_and_bom"],`（**全是在字符串里，无一行工程图/BOM 断言**） |
| 8 | A-drawing **五** | `drawing_view_operations` | **存疑**（★ 我判**成立**，见 §二 #1） | 条目 → `有视图的图（3 视图）—— list/collect ok count=3` | `output/drawing-view-evidence.json` → `steps` 只有 `list_views` / `get_scale` / `set_scale`；全文 grep `collect` **0 命中** |
| 9 | A-features **F1** | `part_and_features` | **成立** | `对盒体 12 条边的两两共 66 对逐一试` · `（8/8，到上限就停）—— ★★ 含边 0 的组合都成` | `output/dimension-edge-pairs-evidence.json` → `"tried": 12,` · `{"pair": [0,5], … "created": false}` · `[0,6] [0,9] [0,10]` 全 `created: false` |
| 10 | A-features **F2** | `feature_readback_criterion` | **存疑** | `① 直接调 GetWhatsWrong2 ⇒ 取不到；② 改用 Extension.GetWhatsWrongCount ⇒ 取到（0 条错）` | `output/modeling-readback-evidence.json` → `"★": "规则 6：特征在树里 + EditRebuild3 真 + GetWhatsWrong2 数 0"`；`C:\swapi\types` 下只有 `GetWhatsWrong.md` / `GetWhatsWrongCount.md`，**无 `GetWhatsWrong2`** |
| 11 | A-features **F3** | `modeling_feature_readback_tools` | **存疑** | `单位判决 = 毫米（t=2 ⇒ 空腔 96×56×18；t=4 ⇒ 92×52×16）` | `output/shell-thickness-units.json` → `"verdict": { "drop_ratio": 0.791, "expected_ratio": 2.0, "★": "事先规定：…下降之比 ≈ 厚度之比 ⇒ 口径与传入值一致…"`（**文件里没有「毫米」二字，且首要判据未过**） |
| 12 | A-features **F4** | `holes_and_finishing` | **存疑** | limitations → `output/countersink-mm-probe.json · output/hole-units-fixed-evidence.json · output/countersink-diag-probe.json · **output/slot-direct-probe.json**（★ 对象失效）` | `D:/AI/SW` 全树 `slot-direct-probe*` 递归搜索 **0 命中**（同链另三个文件都在） |
| 13 | A-moldcosting **V-1** | `costing` | **成立** | `python tools/verify_costing_e2e.py（⇒ verdict: pass；证据 output/costing-evidence.json）` | `output/costing-evidence.json` → `"passed": 5, "of": 6, "verdict": "partial"` · `"list_templates": {"ok": false, … "AttributeError: <unknown>.GetTemplatePathnames"}` |
| 14 | A-moldcosting **V-2** | `costing` | **成立** | limitations → `完整闭环真机跑通 … **total_to_manufacture = 3.2714499345031918（USD）**。证据文件：D:\AI\SW\output\costing-evidence.json` | 该文件全部 6 个 `steps` 只有 `get_costing_manager`/`evidence`/`body_count`/`list_bodies`/`list_templates`/`read_analysis`；**无 `templates`/`defaults`/`cost_analysis` 键、无成本数字、无「普通碳钢」** |
| 15 | A-moldcosting **V-3** | `mold_analysis` | **成立** | `mcp_tools` 含 `solidworks_mold_undercut_detect`，`level: verified` | 同条目 limitations → `⚠ 仍未查证：MoldUndercutDetect 官方是 Void …「怎么把颜色读回来」仍是未知`；两份证据文件的 `steps`/`cases` **一个 `undercut` 字样都没有** |
| 16 | A-sheetmetal **V-1** | `sheet_metal` | **成立** | `"label": "钣金建模与展开"` / `"level": "verified"` / evidence `"pytest tests/test_sw_sheet_metal.py"` | 该测试 → `from sw_sheet_metal import BaseFlangeSpec` · `class FakePart:` · `def test_flat_pattern_export_uses_alignment_array_and_option_bitmask` —— **只导一个 dataclass、全程不碰 COM** |
| 17 | A-sheetmetal **V-2** | `sheet_metal` | **成立** | evidence `pytest tests/solidworks_sheet_metal_regression.py（钣金）` | 该文件 `def test_` 计数 **0**，只有 `def _validate_evidence` / `def run_regression` / `def main()` / `if __name__ == "__main__":`；实跑 `no tests collected  EXIT=5` |
| 18 | A-sheetmetal **V-3** | `sheet_metal` | **成立** | limitations 第 1 项 → `SW2026 SP01.1 已真机验证现代 BaseFlange FeatureData、**开放 U 型轮廓双折弯**、…` | `scripts/sw_sheet_metal.py::SHEET_METAL_RUNTIME_STATUS` → `**闭轮廓**真机建成` · `⚠ **开放折线（轮廓法兰）真机失败：CreateFeature(IBaseFlangeFeatureData) 创建失败**` · `⇒ **True 仅对闭轮廓成立**` |
| 19 | A-sheetmetal **V-4** | `sheet_metal` | **成立** | 同上 → `…板厚/半径/K 因子参数重开回读和**含折弯线 DXF**` | `output/flat-pattern-dxf-evidence.json` → `"export_flat_pattern_dxf": { "ok": false, … "exists": false, "size_bytes": 0, "error": "ValueError: 导出展开 DXF 前必须先保存钣金零件"` · `"verdict": "partial"` |
| 20 | A-sheetmetal **V-5** | `sheet_metal` | **成立** | 同上 → `板厚/半径/K 因子参数重开回读` | 唯一声称做重开的是 `tests/solidworks_sheet_metal_regression.py::run_regression`（`reopened = open_document(...)` + `raise RuntimeError(f"重开参数不一致: …")`），但其产物 `sheet_metal_regression_result.json` / `u_channel*` / `%TEMP%\solidworks_sheet_metal_regression` **三处 0 命中** |
| 21 | A-sketch **F1** | `sketch_modify_ops` | **成立** | `2026-10-03（轮 472）**走 MCP 契约的真机调用 5/5** …：python tools/prove_tools_by_contract.py **solidworks_sketch_**` | `output/tools-by-contract-evidence.json` → `"prefix": "solidworks_insert_"` · 5 个 `tool` 全是 `insert_planar/offset/ruled/delete_face/replace_face` · `"n_tools": 5, "passed": 1` |
| 22 | A-sketch **F2** | `sketch_spline` | **成立** | `★★ **三个条件缺一不可**` · `② ★ **第二个参数 = False**（SimulateNaturalEnds）` · `⇒ ★★ **四格里只有一格成**` | `output/spline-with-variant-evidence.json` 四格 → 成功格 `"tag": "前人原样：CreateSpline2(data, False)"`；另三格 `err` 逐字相同且点名 `'CreateSpline'`（不带 2）· `"passed": 1, "total": 4` ⇒ **没有一格传过 `True`** |
| 23 | A-sketch **F3** | `sketch_spline` | **成立** | `② ★ 数组形态 = VARIANT(VT_ARRAY|VT_R8, 扁平 list) （★ 而**扁平 list / list of tuples 都回 None**）` | `output/spline-with-variant-evidence.json` 对应两格 → `"form": "flat_list" … "err": "TypeError: get_com_member(CDispatch, 'CreateSpline', *1 args)：取回来的成员不可调用"` —— **是 `TypeError`，不是 `None`** |
| 24 | A-sketch **F4** | `sketch_query` | **成立** | `…逐个调取法 → 退草图 → 关件不保存，**17/17 通过**，证据落 output/sketch-getters-smoke-evidence.json` | 该文件 → `"passed": 18, "total": 18, "verdict": "pass"`，`checks` 逐条数得 **18** 项 |
| 25 | A-sketch **F5** | `sketch_offset_on_surface` | **成立** | `★★ **三步缺一不可**：① 按对象选边（Select4）；② 补设 Mark；③ 收尾 InsertSketch(True)` | `output/offset-on-surface-per-example-evidence.json` → 成功格 `"insert_sketch": true, "ok": true`，其 `sel` 块 `"marked": [false, false, false, false]`；三格 `sel` 逐字相同 ⇒ **唯一变量只有 `insert_sketch`** |
| 26 | A-surface **S1** | `surface_delete_hole` | **成立** | evidence → `★★ 2026-10-03（轮 564）**真机建成** … 名 删除孔1 · 型 DelHole · 环Δ = −1 ✓` · `★ **证据文件**：output/delete-hole-for-surface-evidence.json` | 该文件 → `"verdict": "successor_also_fails"` · `"passed": 0, "total": 3` · `{"tag": "★ **继任者** + 选孔的边", "entry": "InsertDeleteHoleForSurface", "ok": false}`；同族另两份同样 `"passed": 0` |
| 27 | A-surface **S2** | `surface_features` | **成立** | limitations → `⚠ **本条**只包装了已验证的那一个：其余（填充 / 缝合 / 裁剪 / 加厚）都要先选中面或边 —— 真机实测：InsertSewRefSurface **不抛但特征树不变**` | `output/surface-knit-evidence.json` → `"knit": { "ok": true, "new": ["曲面-缝合1"], "faces": 8, "bodies": "2->1" }` · `"verdict": "pass"` |
| 28 | A-surface **S3** | `surface_features` | **成立** | evidence 结尾 → `★ ⚠ 真机推翻了「不选面」当负例的假设 —— **不选面它也能成**（它自己会找面）` | `output/extend-surface-evidence.json` → `"note": "…★ **负例（不选面）必须失败** —— 那证明判据不是恒真。"` · 唯一的负例是 `"negative_zero_distance": {"ok": true, "returned_ok": false, …}`，**无 `faces_selected: 0` 对照格** |
| 29 | A-surface **S4** | `surface_revolve` | **存疑** | limitations → `★★ **前置：蓝图里必须有一条中心线**（官方原话的 centerline）—— ★ 本包装的 docstring 已明写这一点` | `scripts/sw_surface_ref_ops.py` 的 docstring → `★ 与实体版 sw_part.revolve_boss 同形` · `⚠ **调用前要选好轮廓**` —— **「前置」段里没有中心线** |
| 30 | A-weldment **V-1** | `weldment_cut_list` | **成立** | evidence → `而唯一没过的 set_cut_list_properties 真因是**本地化名** … （**out-cut-list-property-names-evidence.json** PASS）` | 全仓无此文件名；真实文件是 `tools/probe_cut_list_property_names.py` → `OUT = Path(r"D:\AI\SW\output\cut-list-property-names-evidence.json")`（**差一个 `out-` 前缀**） |
| 31 | A-weldment **V-2** | `weldments` | **成立** | evidence `pytest tests/test_cad_reliability.py（焊件）` | 该测试「焊件」全部内容 → `assert index["weldments"]["level"] == "verified"` · `assert index["weldments"]["verified_versions"] == ["2026"]` —— **只读台账字段、不碰焊件代码** |
| 32 | A-weldment **V-3** | `weldments` | **成立** | limitations → `⚠ **没挂的 4 个及原因**：… **create_structural_member（★ segment_groups 是嵌套结构）**…` | 同条目 `mcp_tools` → `"solidworks_weldment_create_structural_member"`；evidence → `真机 … ⇒ **建成 square-rods (1)** … 证据 output/structural-member-evidence.json` |
| 33 | A-weldment **V-4** | `weldments` | **成立** | `"level": "verified"` · `mcp_tools` 含 `solidworks_weldment_read_property_manager` 与 `solidworks_weldment_create_profile_center_mate` | 另两条条目逐字说这两个没验 → `weldment_cut_list`: `而 read_property_manager 那条本轮**未验**`；`weldment_profile_and_curve`: `⚠ **未验**：create_profile_center_mate（★ 需装配体 + 两个实体，本轮未准备）` |

### B 侧 5 条

| # | 稿 · 编号 | 条目 | 判定 | 我们的那一段（逐字） | 官方那一段（逐字） |
|---|---|---|---|---|---|
| 34 | B-features **C-6** | `GraphicsRedraw2` 已过时 | **不成立** | `scripts/sw_part.py` → `#: ★★★ 2026-10-03（接手轮）**换成后继入口** —— 原来是 model.GraphicsRedraw2()。` · 活代码 `get_com_member(_view, "GraphicsRedraw", None)` | `C:\swapi\types\IModelDoc2\GraphicsRedraw2.md` → `Obsolete. Superseded by [[IModelView::GraphicsRedraw]] and [[IModelView::IGraphicsRedraw]].` —— 官方行在，但**调用点已不存在** |
| 35 | B-features **C-7** | `GetActiveSketch2` 已过时＋文件不符 | **不成立** | 核对表点名 `scripts/sw_part.py`；全仓 `sk = get_com_member(model, "GetActiveSketch2")` **只命中 `sw_sketch_edit.py`**；`sw_part.py` 只剩注释 `原来是 get_com_member(model, "GetActiveSketch2")` | `C:\swapi\types\IModelDoc2\GetActiveSketch2.md` → `Obsolete. Superseded by [[SketchManager::ActiveSketch]].` —— 官方行在，但**被点名文件里没有这条调用** |
| 36 | B-misc **C#6** | `GraphicsRedraw2`（同一族） | **不成立** | 核对表称 `scripts/sw_review.py` 有两处 `get_com_member(model, "GraphicsRedraw2")`；全文只命中 **docstring 一处**，且该 docstring 是**引用官方 Obsolete 横幅作为「已换后继」的依据** | 同上 `GraphicsRedraw2.md` → `Obsolete. Superseded by [[IModelView::GraphicsRedraw]] …`；活代码是 `view = get_com_member(model, "ActiveView")` → `get_com_member(view, "GraphicsRedraw", None)` |
| 37 | B-sketch **C-1** | `_active_sketch_name()` 只调 Obsolete | **不成立** | `scripts/sw_sketch_modify_ops.py` 现在的函数体 → `★★★ 2026-10-03（接手轮）**换走后继入口** —— 原来是 get_com_member(model, "GetActiveSketch2")` · 活代码 `from sw_sketch import active_sketch as _active_sketch` / `sk = _active_sketch(model)` | `C:\swapi\types\IModelDoc2\GetActiveSketch2.md` → `Obsolete. Superseded by [[SketchManager::ActiveSketch]].` —— 官方行在，**但已改走后继** |
| 38 | B-surface **C-3** | `RULED_TYPE_MEANINGS` 0..4 | **存疑** | `scripts/sw_surface_edit_ops.py` → `#: ★ 官方给的 Type 取值表（★ 逐字来自 InsertRuledSurfaceFromEdge2.md 的 Parameters）` / `RULED_TYPE_MEANINGS = { 0: "Tangent to Surface", … 4: "Sweep", }` / `ruled_type 不在官方取值表 0..4 内` | **两源互斥**：`swRuledSurfaceType_e.md` → `enum_member_count: 5`，值 `1/2/3/4/5`、**无 0**；`InsertRuledSurfaceFromEdge2.md` 的 `## Parameters` → `- **Type**: 0 = Tangent to Surface … 4 = Sweep`，**通篇不链该枚举** |

### B 侧其余 88 条「成立」分歧（代码偏离官方，压缩记；两段原文各留一短片段）

| 稿 | 条目数 | 我们的那一段（短片段） | 官方那一段（短片段） |
|---|---|---|---|
| B-assembly | 9 | `mate.Name = name` · `interference.Done()` 排在 `GetInterferences` 之前 · `AddComponent4` · `AddMate5` · `Select2(False, mark)` · `SetTransformAndSolve2` · `EditSuppress()` · `EditUnsuppress()` · `ReferenceType` | `IMate2` 三源成员表**全无 `Name`** · `Done.md` → `Stops the interference detection.` · 8 页逐字 `Obsolete. Superseded by …` |
| B-drawing | 9 | `GetSelectedObjectType3` 当 mark 存 · `SetTemplateName` 前无 `SetProperties` · docstring 写「官方 Remarks 逐字」 · `pre > 0` · `add_detail_view` 无 ActivateView/CreateCircle · `get_com_member(view, "Name")` · `shape: int = 0` · `shape_intensity: int = 0` | `GetSelectedObjectType3.md` → `Type of object as defined in swSelectType_e` · `SetTemplateName.md` → `call ISheet::SetProperties … swDwgTemplateCustom` · `IView/Name.md` → `Obsolete. Superseded by GetName2/SetName2` · `swRevisionTableSymbolShape_e` → 成员 1/2/3/4 · `ShapeIntensity` → `valid range is 1 (most) to 5 (least)` |
| B-features | 11 | `CreateSketchSlot(0, radius, radius, …)` · `_select_revolve_axis` 后被 `ClearSelection2` 清空 · `linear_pattern` 只 `mark=4` · `linear_pattern_report` 空选区 · `AutoDimension2` 无条件调 · `FeatureFillet` · `FeatureLinearPattern3` ×2 · `FeatureCircularPattern4` · `CreateSpline2` · `AutoDimension2` · `Select3(…, mark, …)` | 第 2 位是 `System.int SlotLengthType` · `FeatureRevolve2.md` → `the axis of revolution, using Mark = 4 or 16` · `FeatureLinearPattern3.md` → `1 and 2 to mark the directions` · `AutoDimension2.md` → `It is an error to supply just one datum` · 8 页 `Obsolete.` |
| B-misc | 13 | `get_com_member(extension, "GetMassProperties", float(accuracy))` · `"官方 Remarks 只说「these marks」、**未给取值表** ⇒ 不假定"` · `False, # UseAutoSelect` ×2 · `if sel_n < 2` ×2 · `Extension.SaveAs` ×2 · `SetUserPreferenceIntegerValue(78, …)` · `sw.ActivateDoc2` ×3 · `quality_map = {"coarse": 1, "fine": 0}` · `GetSystemValue2` · `"SystemValue"` · `WRAP_MESH_FACTOR_DEFAULT = 0` | `GetMassProperties(Int32, Int32&)` 2 参 · `InsertRefPlane.md` → `- 0 = First reference entity` · `UseAutoSelect is false, the user must select the bodies` · `You can use any number of profiles` · `swSTLQuality_e` → 成员 1/2/3 · `MeshFactor: 1 (lowest) - 10 (highest)` |
| B-moldcosting | 5 | `_get(m, "Calculate")` 零实参 · sw_mold 只写「未选拔模方向参考」 · `多个参数语义查不到` · `MoldUndercutDetect(…, 6 参)` · `int(option), # 6 Int32 未查证` | `Calculate(System.object Entities)` 1 参 · `InsertMoldPartingLine.md` → `Direction of pull 1 / Parting line edges 4` · `InsertMoldCoreCavitySolids.md` → 四条成文前置 · `MoldUndercutDetect.md` → `Obsolete` + 后继 9 参 · `Smooth` → `swPartingSurfaceSmoothingType_e`（成员 1/2） |
| B-sheetmetal | 7 | `data.BendAngle = float(spec.angle)` ×2 · `data.Angle = float(spec.angle)` · `GetErrorCode` ×2 · 边法兰不调 `InsertSketchForEdgeFlange`/`AddEdges` · `InsertSheetMetalClosedCorner` 零参不选面 · `SW_END_COND_BLIND = 0` | `BendAngle` → `0.261799 … 1.5708`（弧度）· 边法兰 → `1.5707963267949 radians` · 拔模 → `Draft angle in radians` · `GetErrorCode.md` → `Obsolete` · `AddEdges.md` → `call InsertSketchForEdgeFlange` · `swFlangeOffsetTypes_e` → 6 成员值 1–6，**无 0** |
| B-sketch | 13 | `GetContourEdges(contour)` · `CreateFillet(float(radius_mm), …)` · `SketchOffset2(float(offset_mm), …)` · `CreateLinearSketchStepAndRepeat` 第 3/4 位 · `CreateCircularSketchStepAndRepeat` 第 1 位 · 「`AxisFlag` 取值表官方两个源都没给」 · `SketchTrim` 走 `Select4` · `merge_points` 无开放轮廓检查 · `GetActiveSketch2` 先调后回退 · `distance_distance: 1` · 「swapi 只列了其中 3 个」 | `GetContourEdges(System.object Xform)` = 16 double 变换数组 · `Radius in meters` · 官方例子 `SketchOffset2(0.00254, …)` · `AxisFlag: X = 1 / Y = 2` · `MergePoints.md` → `only one open contour exists` · `swSketchChamferType_e` → `0 / -1 / 2` · `swCrossHatchFilter_e` → `enum_member_count: 5` |
| B-simulation | 8 | `_check(manager, "GetLoadsAndRestraints", 1, int(index))` · `GetEdgeWeldConnector` 同 · `get_com_member(item, "GetName")` / `"GetType"` · `create_preserved_region` 无 `SelectFaces` · `create_symmetry_control` 无对称面 · `create_demold_control` 无方向几何 · 7 个工厂只在对象层 `BeginEdit` · `"AddForce"` ×3 | `GetLoadsAndRestraints(ByVal NIndex, **ByRef ErrorCode**)` · `CWLoadsAndRestraints` 成员只有 `Name`/`Type`（**无 GetName/GetType**）· 官方 VBA：`SelectFaces(DispArray)` → `SetIncludeRegionDepth2` · `SelectSymmetryType 0` 紧接 `SelectFirstSymmetryPlane` · `SelectDemoldDirection` 紧接 `SelectPlaneForDirection` · `CWTopologyStudyManagerObj.BeginEdit … CreateStressConstraint …` · `AddForce` → `Obsolete. Superseded by …AddForce2` |
| B-weldment | 6 | `InsertWeldmentCutList2", sort_options` · `InsertSubWeldFolder2", folder` · 同函数体只有 3 行、**不选实体** · `GetErrorCode` · `MateAlignment` 注释「枚举在两套官方源里查不到」 | `InsertWeldmentCutList2(System.object **Bodies**)` = Array of Body2 · `InsertSubWeldFolder2(System.object **BodyArray**)` · 官方例子 `SelectByID2("Gusset1","SOLIDBODY",…)` → `GetSelectedObject6` → 传入 · `GetErrorCode.md` → `Obsolete` · `MateAlignment.md` → `as defined in swMateAlign_e`（该页 `enum_member_count: 6`） |

---

## 二 · 抽查证伪（★ 本次最重要的数）

**抽法**：把 18 份稿里全部 **55 条候选项**（A 侧 33 条 + B 侧 22 条抽样候选）写进池子，用 `Get-Random -Count 8` 抽，**抽中记录在案**（不挑不拣）：

```
#1 A-drawing|5      #2 B-surface|C-3     #3 B-sheetmetal|C-2   #4 A-surface|S2
#5 B-simulation|C-1 #6 A-moldcosting|V-2  #7 A-features|F2      #8 B-assembly|C-1
```

**逐条我自己回去看原文**（不看原稿的结论，直接读 `capabilities.yaml` / 脚本 / 证据 JSON / 官方 md）：

| # | 条目 | 我核到的事实 | 原稿判 | **我判** |
|---|---|---|---|---|
| 1 | A-drawing 五 | `capabilities.yaml:3369` 逐字 `list/collect ok count=3 · … 证据 output/drawing-view-evidence.json`；该 JSON 的 `steps` 只有 `list_views`/`get_scale`/`set_scale`，全文 grep `collect` **0 命中** | 存疑 | **成立**（★ 升级：`collect` 被当成 ok 的证据，却没有任何一格） |
| 2 | B-surface C-3 | `sw_surface_edit_ops.py` 的 `RULED_TYPE_MEANINGS` 确为 `0..4`，注释逐字引 `InsertRuledSurfaceFromEdge2.md`；该页 `## Parameters` 逐字 `0 = Tangent to Surface … 4 = Swep`；而 `swRuledSurfaceType_e.md` 逐字 `enum_member_count: 5`、值 1–5、**无 0** ⇒ **官方两源互斥** | 存疑 | **存疑**（★ 维持：仓库引对了成员页，分歧判不了） |
| 3 | B-sheetmetal C-2 | `sw_sheet_metal.py:16` 逐字 `SW_END_COND_BLIND = 0`，`:210/:212` 赋给 `D1/D2EndConditionType`；`D1EndConditionType.md` → `End condition type as defined in swFlangeOffsetTypes_e`；该枚举 6 成员值为 1/2/3/4/5/6，**无 0**，`swFlangeOffsetBlind` 是 **1** | 成立 | **成立** |
| 4 | A-surface S2 | `output/surface-knit-evidence.json` 逐字 `"knit": {"ok": true, "new": ["曲面-缝合1"], "faces": 8, "bodies": "2->1"}` + `"verdict": "pass"`；`capabilities.yaml:3400` 同条目 limitations 逐字 `InsertSewRefSurface **不抛但特征树不变**` ⇒ 同一条目内部直接打架 | 成立 | **成立** |
| 5 | B-simulation C-1 | `sw_simulation_loads.py:390/:404` 与 `sw_simulation.py:564` 三处 COM 调用全打在 `"AddForce"`；`AddForce2`/`AddForce3` 只出现在 `:197-199 / :304-306 / :323-324` 的常量表，**没有任何 `get_com_member(…,"AddForce2"…)`**；官方页逐字 `Obsolete. Superseded by ICWLoadsAndRestraintsManager::AddForce2` | 成立 | **成立** |
| 6 | A-moldcosting V-2 | `output/costing-evidence.json` 全文只有 6 个**读数** step + `captured_at`；grep `3.27144` / `普通碳钢` / `total_to_manufacture` / `cost_analysis` / `defaults` **全 0 命中**；`verdict: partial` ⇒ 条目所列闭环四要素与那个 USD 数值在该文件里一个都没有 | 成立 | **成立** |
| 7 | A-features F2 | `output/modeling-readback-evidence.json` 4 处逐字 `"规则 6：特征在树里 + EditRebuild3 真 + GetWhatsWrong2 数 0"`；`capabilities.yaml:2557` 逐字 `② 改用 Extension.GetWhatsWrongCount ⇒ 取到`；`C:\swapi\types` 下只有 `GetWhatsWrong.md` / `GetWhatsWrongCount.md`，**全树无 `GetWhatsWrong2`**；而 `capabilities.yaml:2545` 自己已写明这条失真 ⇒ **命名残留，非能力虚标** | 存疑 | **存疑**（★ 维持） |
| 8 | B-assembly C-1 | `scripts/sw_assembly.py:138` 逐字 `return asm_model.AddComponent4(`；`:120-121` 显示它是 `AddComponent5` 失败后的回退路径；官方 `IAssemblyDoc/AddComponent4.md` 逐字 `Obsolete. Superseded by [[IAssemblyDoc::AddComponent5]].` | 成立 | **成立** |

### ★★ 成立率

| 口径 | 数 |
|---|---|
| 抽中 | **8** |
| 我判 **成立** | **6**（#3 #4 #5 #6 #8 —— 另 #1 由「存疑」上调为成立） |
| 我判 **存疑** | **2**（#2 #7） |
| 我判 **不成立**（被证伪） | **0** |
| **★ 成立率** | **6 / 8 = 75 %** |
| **★ 若把「存疑」按半权计** | **7 / 8 = 87.5 %** |
| **★ 证伪率（原稿结论被推翻的）** | **0 / 8 = 0 %**；唯二变动是 #1 由「存疑」→「成立」（**上调**，不是下调） |

⇒ **这组稿子的结论方向是可信的**：8 条里 0 条被证伪，1 条被上调，且**没有一条是「原稿说有、原文其实没有」**。
⇒ ★ 唯一的方法论风险在**计数**不在**定性**：稿件的「对不上 N 处」自报值与正文实际条目数对不上的已抓到 2 例（A-sketch 4 vs 5、B-sheetmetal 8 vs 7）⇒ ★ **凡按「对不上 N 处」取数的人，必须以正文条目为准。**

---

## 三 · 分级

### 🔴 立刻要改（13 条）—— 台账把「证据否定」写成肯定，或引的证据不含它自称的内容

| 条目 | 一句话 |
|---|---|
| A-sheetmetal **V-3** | 「开放 U 型轮廓双折弯已真机验证」与 `SHEET_METAL_RUNTIME_STATUS` 的「开放折线真机失败 / `True` 仅对闭轮廓成立」**逐字相反**；且**同一条目两条 limitations 互相打架**，README 也跟着写了同一句 |
| A-moldcosting **V-1** | 条目写 `verdict: pass`，文件是 `partial`（5/6）；**同仓另两条文字（`costing_readback` + ROADMAP）都写 partial** ⇒ 一个文件被写成两种结论 |
| A-weldment **V-4** | `verified` 条目挂出 `read_property_manager` / `create_profile_center_mate`，而**另两条条目逐字写「未验」** |
| A-surface **S1** | 条目唯一以「★ 证据文件」点名的三份**全是 `passed: 0`**，真正带「建成」的那份从未被点名 ⇒ 修法很小（换 evidence 指针） |
| A-assembly **F1** | 唯一真机证据顶层 `"verdict": "fail"`，条目仍 `verified` 且 label 含「配合」；**三个挂的工具全是只读**，全仓建配合函数 grep 0 命中 |
| A-assembly **F2** | evidence 自称「旋转马达创建」，实际马达是 `FakeMotionFeature`；**同域 `animation_export` 自己记着「真机 `ok: false`」** |
| A-features **F1** | 「66 对 / 8-8 / 含边 0 都成」vs 文件 `tried: 12` + 四格 `created: false`；★ **已原样扩散到 `mcp-server` 侧 `solidworks_add_dimension` 的工具描述** ⇒ 影响面超出台账 |
| A-sketch **F1** | 「`solidworks_sketch_` 前缀 MCP 契约真机 5/5」vs 文件 `prefix: solidworks_insert_` / `passed: 1 / n_tools: 5` |
| A-drawing **一** | `drawing_dimension_insertion` 的 evidence 唯一相关行是 `assert index[...]["level"] == "verified"` —— **循环自证**，测试文件自己写「未在本机实测」 |
| A-moldcosting **V-2** | 「完整闭环四要素 + `total_to_manufacture = 3.2714499345031918`」在该证据文件里**一个都没有**；且它点名的验收命令写不出这个文件的键形状 |
| A-surface **S2** | 同条目内「缝合不抛但特征树不变」与「建成 `曲面-缝合1` · body 2→1」并排 |
| A-sheetmetal **V-4** | 「含折弯线 DXF 已验证」vs 唯一在盘证据 `ok:false / exists:false / size_bytes:0`；知识库第 322 条已定性「**红线内验不了、保持不注册**」 |
| A-sheetmetal **V-1/V-2** | `verified` 挂的两条 evidence：一条全程不碰 COM（只 import 一个 dataclass），一条按字面跑 `no tests collected EXIT=5` ⇒ **该 level 在本域无可执行的 pytest 支撑** |

### 🟡 要记档（21 条）—— 不立刻改，但得留下口径

| 组 | 条目 | 性质 |
|---|---|---|
| 数字/表述偏差（6） | A-assembly F3（`81/126` → 现值 `277/322`）· A-sketch F4（`17/17` → 文件 `18/18`）· A-drawing 五（`collect` 无对照格）· A-features F3（判决是推出来的、首要判据未过）· A-surface S3（结论另处有据，但被点的文件不含那一格）· A-sketch F5（`marked` 四条全 false，且只有第 ③ 步被对照过） | 改数字或补一格，不涉及能力定性 |
| 结论强度超框（3） | A-sketch F2（「三个条件缺一不可」的第三条件从未对照）· A-sketch F3（挂在错文件名下）· A-drawing 二（「图纸名不存在」这一步在 JSON 里不存在） | 同一文件里两处同源同错，**必须一起改** |
| 条目内部矛盾（2） | A-weldment V-3（limitations 说没挂、mcp_tools 说已挂）· A-surface S4（limitations 说 docstring 写了中心线前置、docstring 没写） | 以 evidence 为准，删陈旧那半句 |
| 引用/文件问题（2） | A-weldment V-1（`out-cut-list-…` vs `cut-list-…`，**真文件在、只是名字差前缀**）· A-features F4（`slot-direct-probe.json` 全树 0 命中，但在 `limitations` 不在 `evidence`） | 改名 / 删引用 |
| 存疑（6） | A-drawing 三 · A-drawing 五 · A-features F2 · A-surface S4 · B-surface C-3（官方两源互斥）· A-features F3 | 按铁律 5 记「查不到」，**不顶替** |
| 覆盖缺口（1） | A-moldcosting V-3（`undercut_detect` 挂在 `verified` 下、证据零覆盖） | 实现在、没验 ⇒ 降级或补证据 |
| 「查不到落盘」类（1） | A-sheetmetal V-5（重开回读三处 0 命中） | ★ **不据此断言没跑过**，只记「无落盘证据」 |

★ 另：B 侧 88 条「成立」分歧（`Obsolete` 成员、量纲差 1000 倍、枚举缺值、mark 前置缺失…）**整体归「要记档」** —— 它们是**真实的实现偏离**，但绝大多数在回退分支里或已被实测兜住，不构成「台账虚标」，不按「立刻要改」处理。★ 其中三条值得单独立项：`sw_part.py` 的 `CreateFillet`/`SketchOffset2`/`CreateLinearSketchStepAndRepeat` 的**毫米直传**（量纲差 1000×）、`sw_sheet_metal.py` 的 `BendAngle` **度直传**（差 57×）、`sw_sheet_metal.py` 的 `SW_END_COND_BLIND = 0`（枚举无 0）。

### ⚪ 不用管（4 条）—— 原稿自己判「不成立」，我抽查复核支持

| 条目 | 复核 |
|---|---|
| B-features C-6 | 官方 `Obsolete` 行在，但 `sw_part.py` 里 `model.GraphicsRedraw2()` **只以注释「原来是…」残留**，活代码是 `IModelView.GraphicsRedraw` ⇒ 核对表过时 |
| B-features C-7 | 官方 `Obsolete` 行在，但**被点名文件 `sw_part.py` 里没有这条调用**（只命中 `sw_sketch_edit.py`，不在本核对声明范围）⇒ 文件不符 + 过时 |
| B-misc C#6 | 官方 `Obsolete` 行在，但 `sw_review.py` 里只有 **docstring 引用该横幅**当「已换后继」的依据，**无任何调用** ⇒ 核对表把引用当调用点 |
| B-sketch C-1 | 官方 `Obsolete` 行在，但 `_active_sketch_name()` 已改走 `sw_sketch.active_sketch`（即官方点名的后继）⇒ 已过时 |

⇒ ★ 这 4 条**不要去「修」** —— 去改会把已经改对的代码改回去。★ 建议把**核对表源文件** `audit-vs-official/` 里的这 4 条标成「已过时」，否则每轮复核都会重新报一遍。

---

## 四 · 三行

- **路径**：`D:/AI/SW/specs/202-user-coverage-gaps/recon/verify50/JUDGE-A_B.md`
- **核了**：18 份稿 · **A 侧 94 处 / B 侧 93 处 = 187 处**（条目 / evidence 引用 / 高置信核对条目，口径见 §〇）· **对不上 38 处**（成立 31 · 存疑 7 · 不成立 4 的等价分布见 §〇）
- **抽查 8 条的成立率**：**6/8 = 75 %**（存疑 2 · **被证伪 0**；含半权口径 87.5 %）