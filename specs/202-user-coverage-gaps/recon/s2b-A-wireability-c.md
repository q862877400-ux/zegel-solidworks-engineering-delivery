# S2-b · A 表「能否挂成 MCP 工具」逐条判定 —— **本路负责的 12 条**

**性质**：只读扫描 + 本文件一个新写。**未改动任何既有文件**；**未运行 SolidWorks**；**未运行 pytest**；未 `import` 任何项目模块（工具名靠正则静态抽，不进注册器）。

**本路范围**：`autocad_*`(3) · `animation_*`(1) · `coverage_*`(1) · `drawing_*`(1) · `geometric_*`(1) · `ref_*`(1) · `render_*`(1) · `replace_*`(1) · `requirements_*`(1) · `select_*`(1) = **12 条**。
（`sketch_*` / `surface_*` / `feature_*` / `curve_*` 共 29 条**不属本路**，未碰。）

**判定口径（本轮定的，逐条可复算）**
- **A 类·可直接挂** —— 首参是宿主对象（`model` / `sw` / `asm_model` / `drawing_model` / `cost_manager` / `study`）**且**其余形参都是 `str/float/int/bool/list/dict`（含 `**kwargs` 外的标量、可经 `derived_args` 造出的 dataclass）。
- **B 类·要加转接层** —— 形参里有 **COM 对象**（`IBody2` / `IModelDoc2` / `IView` / `ISheet` / `IGtol` / `IMotionStudy` / `IRenderMaterial` …）。
- **C 类·挂不了** —— 形参里有**接口指针**（`AccessSelections` 族）/ **SafeArray 的 out**，或台账 `limitations` **已写明真机不可达 / 形态不可挂**。

**两条必须先说的全局事实（否则下表会被误读）**

1. ★★★ **`mcp_tools` 字段缺失 ≠ 「工具不存在」。** 本轮对**已注册批次**（`register_capabilities.py` 的 `BATCH_MODULES` 76 项）+ `server.py` 做静态抽名，得 **322** 个工具名。★ **下表里有 3 条（`coverage_gap_batch1` / `ref_geometry` / `replace_face`）的能力其实早就挂好了** —— 判 A，**动作是补台账字段，不是写 ToolSpec**。
   证据：`mcp-server/register_capabilities.py` 的 `BATCH_MODULES` 段落注释逐字「★ **候选先变成"可复现的全量清单"再选**」与 `mcp-server/tool_registry.py` 的 `mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])`。
2. ★★★ **注册器只从 `scripts/` 取模块**，且 `inject` **必须等于目标函数首参名**、且**必须是 `RESOLVERS` 的键**。
   证据：`mcp-server/register_capabilities.py` 逐字「★ **规范（本表的设计意图，逐字见下面 `manager` 那条注释）是：**`inject` 必须等于目标函数的首参名**。」+「★ 依据（逐字核过源码）：`tool_registry.py:507` 是 `kwargs[inject_as or inj] = resolver(params)`」+ `RESOLVERS` 现有 **8** 个键：`model` / `sw_app` / `study` / `asm_model` / `manager` / `drawing_model` / `sw` / `cost_manager`。

---

## 一 · 主表

| id | 实现文件 | 目标函数 | 首参 | 其余形参形态 | 判类 | 依据（文件 + 原文片段） | 若可挂：建议工具名 |
|---|---|---|---|---|---|---|---|
| `autocad_basic_drafting` | `subskills/autocad-automation/scripts/acad_draw.py` | `run` | `brief: Dict[str, Any]` —— **不是宿主对象**；宿主 `AutoCADSession` 是函数内部 `session = AutoCADSession(create_if_missing=True, visible=True).connect()` 新建的 | `output: str \| Path \| None` · `new_document: bool` · `source: str \| Path \| None` · `fast_mode: bool` · `step_delay_s: float`（标量，但两个 `Path \| None`） | **C** | ① 台账 `limitations[0]` 逐字：「AutoCAD 2024 ActiveX 当前真机回归被阻塞：Documents、Layers、SelectionSets 代理不稳定；**不得宣称原生 DWG 绘图已完成**」；`level` 逐字 `not_implemented`（全清单唯一 1 条）。② `acad_draw.py` 原文：`def run(\n    brief: Dict[str, Any],\n    output: str \| Path \| None,\n    new_document: bool,\n    source: str \| Path \| None,\n    fast_mode: bool,\n    step_delay_s: float,\n) -> Dict[str, Any]:`。③ 通路阻断：`tool_registry.py` 逐字 `mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])` —— AutoCAD 实现住在**父目录名带连字符**的 `subskills/autocad-automation/scripts/`，而 `scripts/` 下**没有**任何 `acad*` 再导出（实测 `Get-ChildItem scripts -Filter '*acad*'` 命中 **0**）；工程图那条 `spec_from_file_location` 桥（`scripts/sw_drawing.py`）**是工程图专用的手工活**，AutoCAD 侧没有。 | ✗ 不建议挂<br>（硬要：`cadstudio_autocad_draw_brief`） |
| `autocad_script_backend` | `subskills/autocad-automation/scripts/acad_session.py` | `run_whitelisted_script_command` | `session: AutoCADSession` —— **自建会话对象，非 `RESOLVERS` 键** | `command_id: str` —— 纯标量 | **B** | ① 原文：`def run_whitelisted_script_command(session: AutoCADSession, command_id: str) -> dict[str, Any]:` + docstring `"""@brief 执行固定白名单 AutoCAD 命令，禁止传入任意脚本文本。"""` + 函数体 `if command_id not in SCRIPT_COMMANDS:`。② **要的东西已全是文本协议**（白名单 `command_id`），★ **缺的只是「把 `session` 解析出来」** —— `RESOLVERS` 现有 8 个键里没有 AutoCAD 会话。③ 另受上面的 `__import__("scripts.%s")` 限制 ⇒ 需先照 `scripts/sw_drawing.py` 的 `spec_from_file_location` 加一条加载桥。④ 台账 `limitations[0]` 逐字「★★ 按并入规范，headless / 非 SolidWorks 路线用 **`cadstudio_*`** 前缀 ⇒ ★ **而当前的工具表里没有对应的 `cadstudio_*`**（★ 13 个里没有）⇒ ★ **所以它的工具真缺**」—— 本轮复核 `cadstudio_*` 仍是 **13** 个（`server.py` + `tool_registry.py` docstring 两处声明），★ 该 limitation **仍然成立**。 | `cadstudio_acad_script_run_command` |
| `autocad_dotnet_backend` | `subskills/autocad-automation/scripts/acad_dotnet_preflight.py` | `run_preflight` | **无位置形参**：`def run_preflight(*, install_sdk: bool = False, evidence_path: Path \| None = None) -> dict[str, Any]:` | `install_sdk: bool` ✓ · `evidence_path: Path \| None` —— `pathlib.Path` **不是**文本协议（工具面收 `str` 再转，不算对象形参） | **B**（比上一条更轻：只需 `str → Path` 转换 + 加载桥，**无对象形参**） | ① 原文：`def run_preflight(*, install_sdk: bool = False, evidence_path: Path \| None = None) -> dict[str, Any]:` + docstring `"""@brief 返回四类 AutoCAD 后端的统一前置报告。"""`。② 台账 `limitations[0]` 逐字：「★ 而 `cadstudio_resolve_backend` 的 docstring 里**提到过 "AutoCAD .NET"** ⇒ ★ 说明**那条线在能力层里是有位置的**，只是**工具层没有对应工具**。」—— 本轮复核 `cadstudio_resolve_backend` 确实在册，它覆盖的是**后端解析**那一半，`run_preflight` 的四类预检报告仍未挂。③ 同样受 `subskills/autocad-automation/` 那个连字符目录阻断（见上一行依据③）。 | `cadstudio_acad_dotnet_preflight` |
| `animation_export` | `scripts/sw_motion.py` | `create_avi_parameter` / `configure_avi_parameter` / `export_motion_study_avi`（三件一组） | **三个都不是宿主对象**：`manager`（`IMotionStudyManager`）· `avi_parameter`（`IAVIParameter`）· `motion_study`（`IMotionStudy`） | `export_motion_study_avi` 的 `file_path`（str）✓ + `avi_parameter=None`（**对象**）；`configure_avi_parameter(avi_parameter, **options)` 是 `**kwargs` —— 注册器按值传参，`check_param_binding.py` 判不出显式形参名 | **B** | ① 三条原文：`def create_avi_parameter(manager):` / `def configure_avi_parameter(avi_parameter, **options):` / `def export_motion_study_avi(motion_study, file_path, avi_parameter=None):`。② ★★ **`manager` 这个 `inject` 键已被占、且指向别的对象**：`register_capabilities.py` 的 `RESOLVERS` 里逐字 `"manager": resolve_manager,`，而 `resolve_manager` 的 docstring 逐字「解析的是 **`ICWStudy.LoadsAndRestraintsManager`**（★ **Simulation 的**载荷与夹具管理器）」⇒ ★ 直接写 `inject="manager"` **会注错对象**；同仓已有同类教训（`resolve_cost_manager` docstring 逐字「★ **与 Costing 毫无关系** —— 那 8 条 Costing 工具**即便键名对上，也会注错对象**」）。③ ★ **不是 C**：台账 `limitations[0]` 逐字「★ **AVI 导出整条链已逐环走过** —— 类型库 ✅ · 建算例 ✅ · 找圆柱面 ✅（★ 独立探针）· 建马达 ✅（★ 3 种算例）· 导出 ✅（★ 三环）」⇒ 三个函数本身**跑得通**，卡的是 e2e 那条「组件未解析」。 | `solidworks_motion_export_avi` |
| `coverage_gap_batch1` | `scripts/sw_surface.py` · `scripts/sw_hole_features.py` · `scripts/sw_sketch_status.py` | `create_revolved_surface` · `HoleWizard5` 入口 · `get_constrained_status` | 三个都是宿主对象（`model` / `model` / 走当前草图） | 全是 `int` / `float` / `bool` 枚举与量纲 | **A**<br>★★★ **已挂 · 台账漏登** | ① 能力 `source_evidence` **自己**列的三份官方页：`C:\swapi\types\IFeatureManager\InsertRevolvedRefSurface.md` · `…\HoleWizard5.md` · `C:\swapi\types\ISketch\GetConstrainedStatus.md`。② 本轮静态抽名，三个入口**都有工具**：`solidworks_create_revolved_surface` · `solidworks_hole_wizard` · `solidworks_sketch_fully_defined_status`（后者在 `mcp-server/tool_specs_batch72.py`，来源块逐字「\| 草图/完全定义检查 \| `ISketch.GetConstrainedStatus` \| `sw_sketch_status.get_constrained_status` \| ✅ \| `fully_defined` \|」）。③ 规格原文在 `specs/202-user-coverage-gaps/tasks.md`：逐字「- [x] **T201** ★ **把已 `verified` 而未挂工具的能力补上入口**（旋转曲面等）」与「- [x] **T401** 移动实体 `IModelDoc2.SketchModifyTranslate`」⇒ `solidworks_sketch_move_entities` 也在册。★ **动作 = 往 `capabilities.yaml` 的 `mcp_tools` 补这 4 个名字，不是写 ToolSpec。** | 无需新增<br>（已有 `solidworks_create_revolved_surface` / `solidworks_hole_wizard` / `solidworks_sketch_fully_defined_status` / `solidworks_sketch_move_entities`） |
| `drawing_dimension_insertion` | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py` | `insert_dimensions` | `drawing_model` —— ★ **正好是 `RESOLVERS` 的键**（逐字 `"drawing_model": resolve_model,`，其注释逐字「★★ **工程图 subskill 里的函数首参叫 `drawing_model`**」·「★ 工程图文档同样是 `IModelDoc2` ⇒ ★ **复用 `resolve_model`**」） | `view=None` —— ★ **对象形参（`IView`）** ⇒ B；但 `None` 时函数自己 `views = _as_sequence(_safe_member(sheet, "GetViews", default=[]))` 遍历全部视图 ⇒ ★ **B 里最便宜的一档：`omitted_params=("view",)` 即可** | **B** | ① 原文：`def insert_dimensions(drawing_model, view=None):` + docstring「自动标注尺寸（模型项目）… `view: 目标视图对象，None 则标注所有视图`」。② 可达性原文 —— `scripts/sw_drawing.py`：`__all__ = list(getattr(_MODULE, "__all__", ()))` / `if not __all__:` / `__all__ = [name for name in vars(_MODULE) if not name.startswith("_")]` / `for _name in __all__:` / `globals()[_name] = getattr(_MODULE, _name)`，而 `drawing_workflow.py` **没有** `__all__` ⇒ ⇒ `insert_dimensions` 已在 `scripts.sw_drawing` 的导出面上 ⇒ `module="sw_drawing"` 可用。③ ⚠★ **台账 `limitations[0]` 与代码不符**：它逐字写「★★ 2026-10-01（轮 290）**核了实现在哪 —— 结论是"实现层没有对应函数"**：★ 全仓搜 `InsertModelDimensions` ⇒ ★ **只在 `scripts/sw_api_sldworks.py` 里**（★ 那是**签名索引**，不是实现）」—— ★ 本轮复核：该能力实际走的是 **`InsertModelAnnotations4`**，其注释在 `drawing_workflow.py` 里逐字「★ SolidWorks 2024 新增 InsertModelAnnotations4，返回实际插入的 IAnnotation 数组；旧版/动态代理仍可能只有 InsertModelAnnotations3。优先使用 4，再回退到 3，避免把"方法返回 True"误当成已经插入尺寸。」⇒ ★ **`InsertModelDimensions` 确实只出现在签名索引里这条观察是对的，但由此推出的「实现层没有对应函数」已被推翻**（找错了成员名）⇒ ★ **该 limitation 的判据应改**。 | `solidworks_drawing_dimension_insert` |
| `geometric_tolerance` | `scripts/sw_gtol.py` | `insert_gtol`（已挂）· `ensure_gtol_frame` / `add_gtol_indicator`（挂不了） | `insert_gtol(model)` → 宿主对象 ✓；`ensure_gtol_frame(gtol, frame: int = FIRST_FRAME)` 与 `add_gtol_indicator(gtol, *, tol_type, datum, border_type, frame)` → `gtol` 是 **`IGtol` 对象** | `tol_type` / `border_type` / `frame`（int）· `datum: str` —— 全是标量 | **C**（未挂的那半） | ① `limitations[0]` 逐字：「★★★ **2026-10-01（轮 166）穷尽式结论**：`IGtolFrame.AddIndicator` 那半 —— `tools/probe_gtol_indicator_matrix.py` 把 `BorderType`(0..3) × `TolType`（官方 Remarks 允许的 **5 个**：20/22/21/25/13）= **20 组全试**，而**每一组的帧都拿到了**（`GetFrame(1)` 非 NULL）⇒ **20 组全返回 `False`**。⇒ ★ 不是「取值不对」…而是**这条后端到不了这一个成员**（与事实 47 那族同类）。★ 所以拆出 `gtol_insert`（**verified**，覆盖「新建 GTol + 帧路径」）；本条目**仍为 `stitched`**（含「加指示符」那半，它在**本机到不了**）。」② `add_gtol_indicator` 的 docstring 也逐字「⚠⚠ **本函数当前「不可用」（2026-10-01 轮 120 真机实测）** … ★ 保留本函数是为了**留下可复算的证据**，不是为了「应该能用」。」③ 已挂的那半：`solidworks_gtol_insert`（在册）。 | ✗ 不建议新增<br>（已挂 `solidworks_gtol_insert`；剩余半**挂不了**） |
| `ref_geometry` | `scripts/sw_ref_geometry.py` | `insert_ref_plane` / `insert_coordinate_system` / `insert_reference_point` / `insert_center_of_mass` / `insert_global_bounding_box` | **五个全是** `model`（宿主对象，`RESOLVERS` 键） | 全是 `int` / `float` / `bool` —— ★ **没有一个对象形参** | **A**<br>★★★ **已全部挂 · 台账漏登** | ① 五条形参原文：`def insert_ref_plane(model, first_constraint: int, first_angle_or_dist: float = 0.0, second_constraint: int = 0, second_angle_or_dist: float = 0.0, third_constraint: int = 0, third_angle_or_dist: float = 0.0) -> dict:` · `def insert_coordinate_system(model, x_flipped: bool = False, y_flipped: bool = False, z_flipped: bool = False) -> dict:` · `def insert_reference_point(model, ref_point_type: int, along_curve_type: int = 0, distance_or_percent: float = 0.0, number_of_ref_points: int = 1) -> dict:` · `def insert_center_of_mass(model) -> dict:` · `def insert_global_bounding_box(model, bbox_type: int = 1, lwta_direction_type: int = 0, …`。② ★ 「先选后调」的 mark 前置**不是形参问题** —— 官方入口是 `selection` 声明式选择器，`pre_call` 机制就是为此存在的（`tool_registry.py` 逐字「`:param pre_call: **调用前的副作用钩子** … 用途：那些**实现里明写「调用前必须先选好」**的函数」）。③ 已在册工具 5 个：`solidworks_insert_ref_plane` / `solidworks_insert_coordinate_system` / `solidworks_insert_reference_point` / `solidworks_insert_center_of_mass` / `solidworks_insert_global_bounding_box`。④ 与 `limitations[3]` 一致（`solidworks_insert_global_bounding_box` 的来源块逐字「★ **边界框用的是 `InsertGlobalBoundingBox2`**，而**不是**台账 T701 给的 `Create3DBoundingBox`」）。 | 无需新增<br>（5 个已在册） |
| `render_material_library` | `scripts/sw_render_material.py` | `create_render_material` / `add_render_material` / `delete_render_material`（未挂）· `list_render_materials` / `refresh_scene_graph` / `collect_appearance_evidence`（已挂） | 前三个**全是** `model`（宿主对象） | `create_render_material(model, name: str, spec: RenderMaterialSpec)` —— `spec` 是 `@dataclass` 实例（★ 非文本协议，但**有现成解法**，见下）· ★ `add_render_material(model, material) -> bool` 的 **`material` 是 `IRenderMaterial` 对象** ⇒ B · `delete_render_material(model, index: int, cascade: bool = False) -> bool` —— **纯 A 且未挂** | **B** | ① 原文：`def create_render_material(model, name: str, spec: RenderMaterialSpec):` / `def add_render_material(model, material) -> bool:`（docstring 逐字「"""把外观对象应用到文档，并刷新场景图。返回 AddRenderMaterial 的原始返回值。"""」，函数体逐字 `result = get_com_member(extension, "AddRenderMaterial", material, out_i4())`）/ `def delete_render_material(model, index: int, cascade: bool = False) -> bool:` / `def list_render_materials(model) -> list[Any]:` / `def refresh_scene_graph(model, update: bool = True):` / `def collect_appearance_evidence(model) -> dict[str, Any]:`。② `spec` 不是障碍 —— `tool_registry.py` 的 `derived_args` 文档逐字「**从已声明的标量入参派生额外实参**，形如 ``lambda params: {"spec": BaseFlangeSpec(...)}``」（★ 钣金 `BaseFlangeSpec` 就是同一手法）。③ `add_render_material` 的 `material` **是**障碍：要么一个工具内「建→用」两段（`extra_op` 或同函数体内串联），要么加一个解析器。④ `limitations[4]` 逐字「★ 本族只验了「建外观 → 绑 `.p2m` → 挂实体 → 加到显示状态 → 读清单」这一条链；★ **删除**（`DeleteDisplayStateSpecificRenderMaterial`）与**改属性回读**未单独真机验。」⇒ 挂 `delete` 时判据只能靠返回值（`DeleteRenderMaterial(Int32, Boolean)` 无出参 ⇒ 可用；★ 而 `AddRenderMaterial` 末位是 `Int32&`，该文件自己写明「pywin32 迟到绑定下不保证回写，故本模块**不以它作成败判据**」）。 | `solidworks_render_material_create`<br>`solidworks_render_material_delete` |
| `replace_face` | `scripts/sw_surface_features.py` | `insert_replace_face_report` | `model`（宿主对象，`RESOLVERS` 键） | ★ **零个** | **A**<br>★★★ **已挂 · 台账漏登** | ① 原文：`def insert_replace_face_report(model) -> dict:` + docstring 逐字「★ 前置：★ **两张面**（★ 一张曲面面 = mark 1 · ★ 一张实体面 = mark 2）。★ 判据（规则 6）：★ **特征树多了新特征**。」+ 函数体 `selected = _select_two_faces_for_replace(model)`。② `limitations[2]` 逐字「⚠ **未查**：① 选具体哪一张面（★ 本包装取各体**第一张**）；② 多对面；③ 两个曲面之间替换。」⇒ ★ **这三条是「挂上去之后的使用限制」，不是不可挂的理由**（工具的 docstring 应如实抄进去）。③ 已在册工具 `solidworks_insert_replace_face`。 | 无需新增<br>（已挂 `solidworks_insert_replace_face`） |
| `requirements_planning` | `apps/desktop/cad_workbench/engineering_orchestrator.py` | 编排层（不是 COM 封装） | — | — | **C** | ① `limitations[0]` 逐字：「★★ 2026-10-01（轮 290）**本条不挂工具 —— 理由写明**：★ 它是**需求分析与工程规划**（★ 一个**流程能力**，不是 COM 操作）⇒ ★ 它的实现在**编排层**（★ 证据 `pytest tests/test_engineering_orchestrator.py`），★ **不是 `scripts/sw_*.py` 里的 COM 封装** ⇒ ★★ 所以**没有"工具"这种形态可挂**。」② 该条 `backends` 逐字 `local-agent`（★ 其余 11 条全是 `*-com` 系列）⇒ 与 `tool_registry.py` 的 `scripts.*` 通路无关。③ 落点也在铁律 3 之外（能力实现进 `scripts/`，而它在 `apps/`）。 | ✗ 不建议挂（台账自豁免） |
| `select_by_ray` | `tools/prove_hole_wizard5.py` | `_ray_select` | `doc` —— ★ **就是 `model`**（同一类 `IModelDoc2`，`RESOLVERS` 有 `model` 键） | `x` / `y` / `z_from` / `radius` 标量 ✓ · `vec=(0.0, 0.0, -1.0)`（**3 元组** —— 工具面拆 3 个 float 再 pack）· `type_wanted` / `mark`（int）✓ · `append`（bool）✓ ⇒ ★ **无 COM 对象形参** | **A**<br>（附两个机械前置） | ① 原文：`def _ray_select(doc, x, y, z_from=0.05, vec=(0.0, 0.0, -1.0), radius=1e-4, type_wanted=SW_SEL_FACES, mark=0, append=False):` + docstring「★ 从 `(x, y, z_from)` 沿 `vec` 发一条射线（★ 官方：圆柱形区域、无限长）。」+ 函数体 `return C.get_com_member(ext, "SelectByRay", float(x), float(y), float(z_from), float(vec[0]), float(vec[1]), float(vec[2]), float(radius), int(type_wanted), bool(append), int(mark), 0)`。② 来源块逐字「`IModelDocExtension.SelectByRay.md`（★ 未废弃，**11 参**）：`bool SelectByRay(double WorldX, WorldY, WorldZ, double RayVecX, RayVecY, RayVecZ, double RayRadius, int TypeWanted, bool Append, int Mark, int Option)`」⇒ ★ **11 个实参全是标量，无 out / 无 SafeArray / 无接口指针 ⇒ 明确不是 C**。③ ★ 两个机械前置：**(a) 模块路径** —— 注册器逐字 `mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])`，它现在在 `tools/` 且名字带 `_` 前缀 ⇒ 要先搬进 `scripts/` 并去下划线；**(b) `vec`** 在工具面拆成 `ray_vec_x/y/z: float`。④ `limitations[3]` 逐字「⚠ 本包装未接进 MCP 工具层；⚠ 本轮只验了 **命中面**（faces）一种。」⑤ `limitations[1]` 逐字「★ **只选** faces / edges / vertices（官方）；★ **不支持** 草图实体 / 轴 / 中心标记 / 中心线 / 剖面线。」⑥ `limitations[2]` 逐字「★ `RayRadius` **<= 2.9 m**；★ 而 `TypeWanted` 取 `swSelectType_e`。」 | `solidworks_select_by_ray` |

---

## 二 · 统计

| 判类 | 条数 | 逐条 |
|---|---|---|
| **A 类·可直接挂** | **4** | `coverage_gap_batch1` ★已挂 · `ref_geometry` ★已挂 · `replace_face` ★已挂 · `select_by_ray`（待搬模块） |
| **B 类·要加转接层** | **5** | `autocad_script_backend` · `autocad_dotnet_backend` · `animation_export` · `drawing_dimension_insertion` · `render_material_library` |
| **C 类·挂不了** | **3** | `autocad_basic_drafting` · `geometric_tolerance` · `requirements_planning` |
| **合计** | **12** | |

★ **A 类 4 条里有 3 条其实已经挂好了** ⇒ **真正「要写 ToolSpec」的只有 A 类 1 条（`select_by_ray`）+ B 类 5 条 = 6 条**；另 3 条是**纯台账补字段**、3 条是**挂不了/不值得挂**。

**B 类里最便宜的（按工作量排序）**
1. `drawing_dimension_insertion` —— `omitted_params=("view",)` 即可（`view` 默认 `None`，函数自己遍历全部视图）。
2. `render_material_library` —— `create` 走 `derived_args`（照钣金 `BaseFlangeSpec` 手法）；`delete` 是纯 A 可单独挂。
3. `autocad_dotnet_backend` —— 只差 `str → Path` + 加载桥。
4. `autocad_script_backend` —— 差一个 `AutoCADSession` 解析器 + 加载桥。
5. `animation_export` —— ★ 最贵：三个对象各要一个解析器，且 ★ **`manager` 这个 `inject` 键已被 Simulation 的 `resolve_manager` 占着**（照 `resolve_cost_manager` 的先例要另起一个键）。

---

## 三 · 建议工具名 → 覆盖率脚本能否吃到

`D:\SW-coverage-tool\gen_user_feature_coverage.py` 的 `CHECKLIST` 逐字「★ 关键词是**子串**匹配，作用在**原始工具名**上（不剥前缀，避免误伤）」。逐条对照：

| 建议工具名 | 命中的 CHECKLIST 行 | 净增 |
|---|---|---|
| `solidworks_select_by_ray` | ★ **无对应行**（清单里没有「按射线选择」这一项） | **0 格**（但它是 `solidworks_hole_wizard` 的官方前置，挂上后孔向导路径才闭合） |
| `solidworks_drawing_dimension_insert` | `("工程图", "尺寸标注", ("drawing_dimension", "add_dimension", "auto_dimension_view"))` | **0 格**（已由 `solidworks_add_dimension` / `solidworks_auto_dimension_sketch` 命中） |
| `solidworks_render_material_create` / `…_delete` | `("其他", "外观/渲染", ("appearance", "render_material"))` | **0 格**（已由 `solidworks_list_render_materials` 命中） |
| `solidworks_motion_export_avi` | `("仿真", "运动算例/马达", ("motion", "motor"))` | **0 格**（已由 `solidworks_motion_create_study` 命中） |
| `cadstudio_acad_script_run_command` / `cadstudio_acad_dotnet_preflight` / `cadstudio_autocad_draw_brief` | ★ **CHECKLIST 里没有 AutoCAD 行** | **0 格** |

⇒ ★ **净增覆盖率格 = 0**。★ 这与 §一 的结论不矛盾：那 6 条的收益是**「能力面 → 工具面」的可核对性**与**孔向导/工程图标注两条链闭合**，★ 不是覆盖率表上的数字。★ 按铁律 5，★ 「CHECKLIST 里为什么没有 AutoCAD 行 / 射线选择行」**本路查不到** —— ★ 那个表是 145 项功能的人工清单，★ 要加行是**覆盖脚本那个仓库**的事，★ 不在本仓。

---

## 四 · 复算方法（每行可独立重算，全程只读）

```
① 台账：json.loads(capabilities.yaml)["capabilities"]           → 110 条
   ★ 该文件内容是 JSON（首字符 `{`，`schema_version = "2.0"`），扩展名 `.yaml` 是历史遗留
② 工具名（静态抽，★ 不 import 任何模块 ⇒ 不碰 COM）：
   register_capabilities.py 的 BATCH_MODULES  → 76 个已注册批次
   对每个 tool_specs_batch*.py 取 name="(solidworks|cadstudio)_…" 与 _spec("…") → 322 个
   server.py 取 @mcp.tool(name="(solidworks|cadstudio)_…")
③ 实现：读上面各文件的 def 形参表 + capabilities.yaml 的 source_evidence / limitations
```

★ **两处必须写明的口径差异**（不要拿本轮的 322 去对 S2-b 的 313）：
- 本轮用**正则**抽名，比 S2-b 的 **AST** 抽名**更宽**（会吃掉 `docs`/注释里出现的同形字符串）⇒ **322 ≥ 313 是正常的**。
- ★ 本轮**额外**核了「**能力已挂但台账 `mcp_tools` 漏登**」这一维度 —— ★ S2-b 的判据是 `not (cap.get("mcp_tools") or [])`，★ 那只能判「台账**声明过**没有」，★ **判不出「台账没声明、但工具其实存在」** ⇒ ★ §一 开头那条全局事实就是本轮补的这个维度。

---

## 五 · 本表明确**查不到**的（铁律 5）

| # | 查不到的 | 实测依据 |
|---|---|---|
| 1 | `CHECKLIST` 里为什么没有 AutoCAD 行 / 「按射线选择」行 | `D:\SW-coverage-tool\gen_user_feature_coverage.py` 的 `CHECKLIST` 是硬编码 145 项人工清单；★ 本仓无该表的生成规则 |
| 2 | `subskills/autocad-automation/` 那条加载桥**要不要修** | `scripts/sw_drawing.py` 的 `spec_from_file_location` 是**工程图专用**的手工桥；★ 全仓**没有**「通用子技能加载器」，★ 也查不到「打算做」的记录 |
| 3 | `autocad_basic_drafting` 的 `not_implemented` 何时能升 | 台账只写「AutoCAD 2024 ActiveX 当前真机回归被阻塞」；★ 无复跑脚本登记（★ `tools/verify_*.py` 一族里没有 AutoCAD 项） |
| 4 | `drawing_dimension_insertion` 那条**过期 limitation** 该改成什么措辞 | ★ 本路只判「实现存在（`InsertModelAnnotations4`）」；★ 台账措辞属另一路的写权限，★ 本表不代改 |