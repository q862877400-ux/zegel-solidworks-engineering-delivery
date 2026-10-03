# S2-b · A 表「能不能挂成 MCP 工具」逐条判定 —— **surface_\* 与 feature_\* 路**

**性质**：只读判定。**未运行 SolidWorks**、**未运行 pytest**、**未改动任何既有文件**。
**唯一新建文件**：本文件。

**口径**：只判 `specs/202-user-coverage-gaps/recon/scan-S2b-ledger-vs-tools.md` §二 A 表里
**id 首段为 `surface_` 与 `feature_` 的全部 15 条**（曲面 10 + 特征 5）；别的路不碰。

**判类三分**（沿用任务书口径）：
- **A 类·可直接挂** —— 首参是宿主对象（`model` / `sw`）且**其余形参全是** `str/float/int/bool/list/dict`。
- **B 类·要加转接层** —— 实现里必须**按序号 / 按名字把实体（边 / 面 / 环）解析成 COM 对象**再选中，
  或实现只存在于「自建文档的探针」里、函数签名与 MCP 的 `inject="model"` 契约不一致。
- **C 类·挂不了** —— 形参里有**接口指针**（`AccessSelections` 族）/ **SafeArray 的 out**，
  或**台账 `limitations` 自己写明**真机到不了 / 自己声明不挂。⇒ 逐字引用依据。

**★ 读法提示**：A 表的判据是「**台账没在 `mcp_tools` 里声明**」，**不等于**「工具面上没有这个工具」。
本表逐条顺手核了工具面（`mcp-server/tool_specs_batch*.py` + `server.py` + `register_capabilities.py` 的 `BATCH_MODULES`），
凡**已经挂了**的都在「建议工具名」列注明 ⇒ **真正缺的只有 4 条**（见 §三）。

---

## 一、主表

| id | 实现文件 | 目标函数 | 首参 | 其余形参形态 | 判类(A/B/C) | 依据（文件 + 可搜索的原文片段） | 若可挂：建议工具名 |
|---|---|---|---|---|---|---|---|
| `surface_modeling` | `scripts/advanced_surface_ocp.py`（另 `scripts/advanced_geometry.py` 是同一族的计划校验层） | `execute_advanced_surface` | **无宿主 COM 对象**（headless OCP；首参是请求体） | `value: str \| Path \| dict`、`output_dir: str \| Path` ⇒ 全是标量/字典 | **A** | `scripts/advanced_surface_ocp.py`：`def execute_advanced_surface(value: str \| Path \| dict[str, Any], output_dir: str \| Path) -> dict[str, Any]:` + docstring 逐字「**执行一个白名单高级曲面操作并返回稳定证据**」；内部四分支 `if request["operation"] == "smooth_loft":` / `elif request["operation"] == "sweep":` / `elif request["operation"] == "knit":` / `else: shape, extra = _thicken(request)`（⇒ 放样 / 扫描 / 缝合 / 加厚四族 + `collect_surface_continuity_evidence` 的 G1/G2 采样，全在这一棵树上） | **已挂**：`cadstudio_create_ocp_surface` + `cadstudio_create_ocp_loft`（`mcp-server/server.py`：`from scripts.advanced_surface_ocp import execute_advanced_surface`）。若另拆一个只查连续性的：`cadstudio_surface_continuity_check`（★ 见 §四 注意：覆盖率表**没有**「连续性」这一行 ⇒ 不增计数） |
| `surface_edit_ops` | `scripts/sw_surface_edit_ops.py` | 五个：`insert_planar_surface` · `insert_offset_surface` · `insert_ruled_surface` · `insert_delete_face` · `insert_replace_face` | `model` | 零参 / `thickness_mm: float, reverse: bool` / `ruled_type: int, length_mm: float, flip_pull_dir: bool, flip_dir: bool, trim_and_sew: bool, angle_deg: float, coord_input: bool, x_mm: float, y_mm: float, z_mm: float, b_connect_surface: bool` / `option: int` / 零参 ⇒ **全标量** | **A** | `scripts/sw_surface_edit_ops.py`：`def insert_planar_surface(model) -> dict:`、`def insert_offset_surface(model, thickness_mm: float, reverse: bool = False) -> dict:`、`def insert_ruled_surface(model, ruled_type: int, length_mm: float = 0.0,` …… `def insert_delete_face(model, option: int = 0) -> dict:`、`def insert_replace_face(model) -> dict:` | **已挂**（5 个全在）：`solidworks_insert_planar_surface` · `solidworks_insert_offset_surface` · `solidworks_insert_ruled_surface` · `solidworks_insert_delete_face` · `solidworks_insert_replace_face`（`mcp-server/tool_specs_batch68.py`：`module="sw_surface_edit_ops", function="insert_planar_surface"` 等） |
| `surface_ref_ops` | `scripts/sw_surface_ref_ops.py` | `insert_lofted_ref_surface`（放样曲面）；同文件 `insert_revolved_ref_surface`（旋转曲面，**已另立台账条目 `surface_revolve`**） | `model` | `closed: bool, keep_tangency: bool, force_non_rational: bool, tess_tolerance_factor: float, start_matching_type: int, end_matching_type: int` ⇒ **全标量** | **A** | `scripts/sw_surface_ref_ops.py`：`def insert_lofted_ref_surface(model, closed: bool = False, keep_tangency: bool = True,` … `end_matching_type: int = 0) -> dict:` | **已挂**：`solidworks_insert_lofted_ref_surface`（`mcp-server/tool_specs_batch69.py`：`module="sw_surface_ref_ops", function="insert_lofted_ref_surface"`）★ 该条目的另两族（**扫描曲面 / 边界曲面**）台账 `limitations` 逐字写「**两个源都没给出**」/「**但那是推断、不是查到的** ⇒ 不假装做到」⇒ 本路**不补**这两族 |
| `surface_thicken_silent_noop` | `scripts/sw_surface_features.py` | `thicken_surface_report` | `model` | `thickness_mm: float, *, direction: int = 0, fill_volume: bool = True, merge: bool = True, use_feat_scope: bool = False, use_auto_select: bool = True` ⇒ **全标量（形状是 A）** | **C** | 台账 `limitations[0]` 逐字：「★★ **实现层已按三源立好**（`sw_surface_features.thicken_surface_report` + `_solid_body_count` / `_surface_body_count`），★ 而**真机静默不成**（★ 11 组 · 两条入口 · 前置完美）⇒ ★ **按 A4 不登记成工具、不写 `verified`** —— **不假装做到**。」<br>函数体 docstring 同样逐字：「★ 按 A4 不登记成工具、不写 `verified`** —— ★ **不假装做到**」 | —（**挂不了**）★ 但工具面**已经有一个同名能力的工具** `solidworks_thicken`（`mcp-server/tool_specs_batch76.py`：`module="sw_feature_entry_ops", function="thicken_surface"`），其 doc 逐字自述「⚠ **尚未真机验证**」⇒ **台账与工具面现状不一致，见 §四** |
| `surface_offset` | `scripts/sw_surface_features.py`（★ 同能力另有一份实现 `scripts/sw_surface_edit_ops.insert_offset_surface`，**已挂**） | `insert_offset_surface_report` | `model` | `thickness_mm: float, *, reverse: bool = False` ⇒ **全标量** | **A** | `scripts/sw_surface_features.py`：`def insert_offset_surface_report(model, thickness_mm: float, *, reverse: bool = False) -> dict:` + docstring 逐字「**等距曲面**（`IModelDoc2.InsertOffsetSurface` —— ★ **旧式方法**）」 | **已挂**（走 `sw_surface_edit_ops` 那一份）：`solidworks_insert_offset_surface`。`sw_surface_features` 这份是**同能力重复实现** ⇒ 建议**不要**再挂第二个同名工具，改为在台账 `mcp_tools` 里认领已有那个 |
| `surface_planar_region` | `scripts/sw_surface_features.py`（★ 同能力另有一份实现 `scripts/sw_surface_edit_ops.insert_planar_surface`，**已挂**） | `insert_planar_ref_surface_report` | `model` | `*, sketch_name: str = ""` ⇒ **全标量** | **A** | `scripts/sw_surface_features.py`：`def insert_planar_ref_surface_report(model, *, sketch_name: str = "") -> dict:` + docstring 逐字「★ 轮 517 改试**草图**（一个闭合轮廓草图 · mark=1）⇒ **`返回值 True` · 建成 `曲面-基准面1`** ✓」 | **已挂**（走 `sw_surface_edit_ops` 那一份）：`solidworks_insert_planar_surface`。同上：**重复实现**，建议认领而非新增 |
| `surface_revolve` | `scripts/sw_surface_ref_ops.py` | `insert_revolved_ref_surface` | `model` | `angle_deg: float, rev_type: int = 0, reverse_dir: bool = False, angle2_deg: float = 0.0` ⇒ **全标量** | **A** | `scripts/sw_surface_ref_ops.py`：`def insert_revolved_ref_surface(model, angle_deg: float, rev_type: int = 0,` … `reverse_dir: bool = False, angle2_deg: float = 0.0) -> dict:` | **已挂**：`solidworks_create_revolved_surface`（`mcp-server/tool_specs_batch72.py`：`module="sw_surface_ref_ops", function="insert_revolved_ref_surface"`）<br>⚠ 覆盖率脚本 `gen_user_feature_coverage.py` 的备注行仍写「能力 `surface_revolve` 是 `verified`，但**未暴露成 MCP 工具**」⇒ **该备注已过期**（工具名含 `revolved_surface`，命中「曲面/旋转曲面」行） |
| `surface_flatten` | 台账指 `tools/prove_flatten_with_anchor.py`（**探针**）；★ 能力层已另立为 `scripts/sw_feature_entry_ops.py`（**已挂**） | 探针 `_one`；能力层 `create_flatten_surface` | 探针：`sw`；能力层：`model` | 探针 `_one(sw, tag, want_vertex, want_edge)`；能力层 `create_flatten_surface(model, *, accuracy_factor: int = 4, should_use_tears: bool = False, body_type: str = "surface")` ⇒ **全标量** | **A** | `scripts/sw_feature_entry_ops.py`：`def create_flatten_surface(model, *, accuracy_factor: int = 4, should_use_tears: bool = False,` … `body_type: str = "surface") -> dict:` + docstring 逐字「★ 本函数**自己选**（★ 调用方不必先选）：取**曲面体的第一张面**按 `mark=1`，再取**该体第一条边的一个顶点**按 `mark=16`（★ 与那次建成的探针同一手法）」<br>（探针侧：`tools/prove_flatten_with_anchor.py` 的 `_one(sw, tag, want_vertex, want_edge)` 内部 `doc = C.new_document(sw, "part")` ⇒ **不是**可直接挂的形状） | **已挂**：`solidworks_flatten_surface`（`mcp-server/tool_specs_batch76.py`：`module="sw_feature_entry_ops", function="create_flatten_surface"`；关键词 `flatten_surface` 命中「曲面/曲面展平」） |
| `surface_untrim` | **只有探针**：`tools/prove_untrim_matrix.py`（★ `scripts/` 下**没有**包装） | `_one` | `sw`（且函数内 `C.new_document(sw, "part")` **自建文档**、末尾 `finally` 里 `CloseDoc`） | `tag, pick, face_type, edge_type, b_trim` ⇒ 全标量；**但真正要的是对象**：`_sel(e, append=..., mark=0)` 按**对象**选**边** | **B** | `tools/prove_untrim_matrix.py`：`def _one(sw, tag, pick, face_type, edge_type, b_trim):` + `doc = C.new_document(sw, "part")` + `for e in list(_g(b, "GetEdges") or [])[:2]:` / `if _sel(e, append=(picked > 0), mark=0):` + `ret = _g(fm, "InsertUntrimSurface2", int(face_type), int(edge_type),` …<br>台账 `limitations` 逐字：「★★ **前置两层**：① 得先有一张**真被剪裁过**的曲面（★ `PreTrimSurface` + `PostTrimSurface` 可造，面数 8→7）；② 选的是**边**。」 | 新建议：`solidworks_untrim_surface`<br>转接层要做：`body_index` / `edge_index` → `IBody2.GetEdges()[i]` → `_select_com_object(..., mark=0)`（先例：`scripts/sw_drawing_expose.py` 的 `create_midsurface` 按 `body_index` 解析）<br>⚠ **覆盖率脚本的子串匹配会误计**：`gen_user_feature_coverage.py` 的 `_hit` 逐字是 `any(p in n for p in pats)` ⇒ `"trim_surface" in "solidworks_untrim_surface"` 为真 ⇒ 会被算进「曲面/剪裁曲面」，而**它其实是「解除剪裁」**。真要计数得先给该行加一个 `untrim_surface` 关键词 |
| `surface_delete_hole` | **只有探针**：`tools/prove_planar_region_then_delete_hole.py`（★ `scripts/` 下**没有**包装） | `_one` | `sw`（同样 `doc = C.new_document(sw, "part")` 自建文档） | `tag, then_delete_hole` ⇒ 全标量；**但真正要的是对象**：遍历 `GetFaces()` → `GetLoops()` → `GetEdges()` 挑「边数 ≤ 1 的那个环」 | **B** | `tools/prove_planar_region_then_delete_hole.py`：`def _one(sw, tag, then_delete_hole):` + `for lp in list(_g(f, "GetLoops") or []):` … `es = list(_g(lp, "GetEdges") or [])` + `if len(es) <= 1:` + `if _sel(e, append=(picked > 0), mark=0):` + `ret2 = _g(_g(doc, "FeatureManager"), "InsertDeleteHoleForSurface")`<br>台账 `limitations` 逐字：「★★ **三层前置**：① 用**继任者**（第一代已废弃）；② 得是**真正的带孔平面**（★ 用平面区域造；★ **拉伸得到的是 5 面 / 6 环、不行**）；③ 只选**孔那圈边**。」 | 新建议：`solidworks_delete_hole_surface`<br>转接层要做：`body_index` + `face_index` + `loop_index` → 逐层解析出环边对象 → `mark=0` 选中；并**先按台账前提造一张带孔平面**（可复用已挂的 `solidworks_insert_planar_surface`）<br>⚠ 覆盖率表**没有**「删除孔」这一行 ⇒ 该工具名**不增计数** |
| `feature_readback_criterion` | `scripts/sw_feature_readback.py` | `feature_readback`（另有 `feature_names` / `feature_present` / `whats_wrong` 三个只读兄弟） | `model` | `feature_name: str, *, do_rebuild: bool = True` ⇒ **签名形状是 A** | **C**（台账自述豁免，★ 不是因为形参） | 台账 `limitations[0]` 逐字：「★★ 2026-10-01（轮 290）**本条不挂工具 —— 理由写明**：★ 它是**规则 6 的通用助手**\n（建特征后回读判据），★ 即**内部判据库**而非用户操作 ⇒ ★★ 它被**别的工具内部调用**，\n★ 而**不暴露为工具**。」<br>`scripts/sw_feature_readback.py` 佐证：`def feature_readback(model, feature_name: str, *, do_rebuild: bool = True) -> dict[str, Any]:` | —（**台账自己说不挂**）★ 若 Lead 判定「已实现未暴露」该补齐，它是**四条里最容易补的一条**：形状已是 A，可挂只读诊断工具 `solidworks_feature_readback_criterion`（含关键词 `feature` + `readback`；⚠ 覆盖率表**没有**「回读」行 ⇒ 不增计数） |
| `feature_revolve_cut` | `scripts/sw_part.py` | `revolve_cut` | `model` | `sketch_name, angle_rad, axis_sketch_name=None` ⇒ **全标量**（⚠ `angle_rad` 是**弧度**，形参名违反五统一的角度约定，接工具时须改收 `angle_deg`） | **A** | `scripts/sw_part.py`：`def revolve_cut(model, sketch_name, angle_rad, axis_sketch_name=None):` + docstring 逐字「★ **旋转切除** —— `IFeatureManager.FeatureRevolve2(..., IsCut=True, ...)`」+ 函数体逐字「`#: ★★★ **这一行就是"切除"** —— `IsCut=True`」 | 新建议：`solidworks_revolve_cut`（关键词 `revolve` ⇒ 命中「特征/旋转」，★ **该行已由 `solidworks_revolve_boss` 覆盖 ⇒ 不增计数**；价值在于补上「切/不切」的对称面） |
| `feature_loft_cut` | `scripts/sw_loft.py` | `create_loft_cut_report` | `model` | `closed: bool = False, use_selected_profiles: bool = True` ⇒ **全标量** | **A** | `scripts/sw_loft.py`：`def create_loft_cut_report(model, closed: bool = False, use_selected_profiles: bool = True) -> dict:` + docstring 逐字「★ **用选中的草图轮廓放样切除**（★ 走 `InsertCutBlend`，官方 **12 参**）」；台账 `evidence` 逐字「★★ **而与「事实 429」**（旋转切除用 `IsCut=True`）**同一族**：★ **"切"会换类型名** 。」 | 新建议：`solidworks_loft_cut`（关键词 `loft` ⇒ 命中「特征/放样」，★ 已由 `solidworks_part_loft` 覆盖 ⇒ 不增计数）<br>⚠ 建议做成与 `solidworks_part_loft` 同形的 `cut` 布尔，而不是另起一个工具名（★ 那样覆盖面 +1、工具数不 +1） |
| `feature_cosmetic_thread` | 台账指 `tools/prove_cosmetic_thread.py`（**探针**）；★ 能力层已另立为 `scripts/sw_feature_entry_ops.py`（**已挂**） | 能力层 `insert_cosmetic_thread` | `model` | `*, standard: int, standard_type: str, size: str, diameter_mm: float, end_type: int, depth_mm: float, note: str` ⇒ **全标量** | **A** | `scripts/sw_feature_entry_ops.py`：`def insert_cosmetic_thread(model, *, standard: int = STD_ANSI_METRIC, standard_type: str = "",` … `size: str = "", diameter_mm: float = 8.0,` … `end_type: int = END_TYPE_THROUGH, depth_mm: float = 0.0, note: str = "") -> dict:` + docstring 逐字「★ 本函数**自己找**：先用 `ISurface.IsCylinder()` 找圆柱面，再取它的**第一条边**并按 `mark=0` 选中 ⇒ ★ 调用方**不必**先选」 | **已挂**：`solidworks_feature_cosmetic_thread`（`mcp-server/tool_specs_batch76.py`：`module="sw_feature_entry_ops", function="insert_cosmetic_thread"`；关键词 `thread` ⇒ 命中「特征/螺纹」） |
| `feature_hole_wizard5` | `scripts/sw_hole_features.py`（包装层；底探针 `tools/prove_hole_wizard5_build.py` 已并入本包装） | `create_hole_wizard_at_selection_report` | `model` | `selection: str, size: str, *, diameter_mm: float, depth_mm: float, through: bool, fastener_index: int, standard_index: int, generic_type: int, ray_dir=(0.0, 0.0, -1.0), plane_offset_mm: float, name: str` ⇒ **全标量 / 元组** | **A** | `scripts/sw_hole_features.py`：`def create_hole_wizard_at_selection_report(` … `selection: str, size: str, *,` … `ray_dir=(0.0, 0.0, -1.0), plane_offset_mm: float = 50.0, name: str = "") -> dict:` + docstring 逐字「:param size: **规格串**（如 "M8"）—— 而不是空串 / 纯数字（真机：那些全 None）」 | **已挂**：`solidworks_hole_wizard`（`mcp-server/tool_specs_batch72.py`：`module="sw_hole_features", function="create_hole_wizard_at_selection_report"`；关键词 `hole_wizard` ⇒ 命中「特征/孔向导」） |

---

## 二、统计

| 判类 | 条数 | id |
|---|---|---|
| **A 类·可直接挂** | **11** | `surface_modeling` · `surface_edit_ops` · `surface_ref_ops` · `surface_offset` · `surface_planar_region` · `surface_revolve` · `surface_flatten` · `feature_revolve_cut` · `feature_loft_cut` · `feature_cosmetic_thread` · `feature_hole_wizard5` |
| **B 类·要加转接层** | **2** | `surface_untrim` · `surface_delete_hole` |
| **C 类·挂不了** | **2** | `surface_thicken_silent_noop`（台账逐字「真机静默不成 ⇒ 不登记成工具」）· `feature_readback_criterion`（台账逐字「本条不挂工具 —— 理由写明」） |
| **合计** | **15** | ✔ 与 A 表里 `surface_*` 10 + `feature_*` 5 相符 |

---

## 三、把 A 类再切一刀：**真正缺的只有 4 条**

A 类的 11 条里，**7 条工具面上已经存在**（只是台账 `mcp_tools` 没认领）：

| 已挂（台账漏认领） | 工具 | 挂它的批次 |
|---|---|---|
| `surface_modeling` | `cadstudio_create_ocp_surface` · `cadstudio_create_ocp_loft` | `server.py`（L2 装饰器路） |
| `surface_edit_ops` | `solidworks_insert_planar_surface` · `solidworks_insert_offset_surface` · `solidworks_insert_ruled_surface` · `solidworks_insert_delete_face` · `solidworks_insert_replace_face` | `tool_specs_batch68.py` |
| `surface_ref_ops` | `solidworks_insert_lofted_ref_surface` | `tool_specs_batch69.py` |
| `surface_revolve` | `solidworks_create_revolved_surface` | `tool_specs_batch72.py` |
| `feature_hole_wizard5` | `solidworks_hole_wizard` | `tool_specs_batch72.py` |
| `feature_cosmetic_thread` | `solidworks_feature_cosmetic_thread` | `tool_specs_batch76.py` |
| `surface_flatten` | `solidworks_flatten_surface` | `tool_specs_batch76.py` |

⇒ ★ **真正要新写的只有 4 条**：

| # | id | 判类 | 要做的活 | 建议工具名 |
|---|---|---|---|---|
| 1 | `feature_revolve_cut` | A | 照 `sw_part.revolve_cut` 写一条 ToolSpec（★ 角改收 `_deg`） | `solidworks_revolve_cut` |
| 2 | `feature_loft_cut` | A | 建议并进 `solidworks_part_loft` 加 `cut` 布尔（★ 与旋转切除同族） | `solidworks_loft_cut` |
| 3 | `surface_untrim` | **B** | 先写「按序号取边 + `mark=0` 选中」转接层 | `solidworks_untrim_surface` |
| 4 | `surface_delete_hole` | **B** | 先写「按序号取环边 + `mark=0` 选中」转接层（且要能造出带孔平面） | `solidworks_delete_hole_surface` |

★ **覆盖率计数的实话**：上表 4 条里，`revolve` / `loft` 两个关键词**已经被 `solidworks_revolve_boss` / `solidworks_part_loft` 覆盖** ⇒ **新增工具数 4、覆盖率增量 0**。
`surface_untrim` / `surface_delete_hole` 对应的功能行（「曲面/剪裁曲面」与一条**不存在的**「删除孔」行）也各有缺口 ⇒ **增量至多 1**（且 `untrim` 那条是**子串误计**）。
⇒ ★ **这一路对覆盖率的净贡献接近 0**；真正该做的是把 A 表结论回写进 `capabilities.yaml` 的 `mcp_tools`，让「台账 ↔ 工具面」对齐。

---

## 四、拿不准处 / 需 Lead 拍板的 4 点

1. **`feature_readback_criterion` 我判了 C，但依据是「台账自述」而非「形参不可挂」。**
   它的签名 `feature_readback(model, feature_name: str, *, do_rebuild: bool = True)` **完全是 A 形** ⇒ 若任务书的 C 类只认「接口指针 / SafeArray out / 真机不可达」三种，这一条严格说该归 A。
   我按「台账 limitations 逐字写了『本条不挂工具 —— 理由写明』」归 C（与任务书里对 `requirements_planning` 的处理同口径）⇒ **这是判断，不是硬判据**。

2. **`surface_untrim` / `surface_delete_hole` 的「B」带着判断成分。**
   它们的唯一实现 `_one(sw, tag, ...)` **字面上**也是「首参宿主对象 + 其余全标量」⇒ 按三分法的字面定义属 A。
   我判 B 的理由有二：① 函数内 `doc = C.new_document(sw, "part")` **自建并自销文档**，与 MCP 的 `inject="model"` 契约**语义不同**（工具应操作用户的活动文档，不是自建一个）；② 它们真正要的是**边 / 环的 COM 对象**，靠 `GetEdges()` / `GetLoops()` 逐层解析 ⇒ 正是 B 类「按序号解析成对象」的定义。

3. **`surface_modeling` 的 A 类判定也不完全贴合字面定义。**
   它**没有宿主 COM 对象**（headless OCP，首参是请求 JSON）⇒ 「首参是宿主对象」这条不成立；我按「其余形参全是 `str/dict`」归 A。
   另外它的台账 `limitations[2]` 逐字写「⚠ **2026-10-01 实测（轮 77）：本机没有 `OCP`** …⇒ 本条 limitations 里涉及 **headless-occt** 的声明**在当前这台机器上无法复现**」⇒ ★ **能挂 ≠ 在本机跑得通**，若 Lead 要按 A4 口径核，这条的运行证据不在本机。

4. **★ 台账与工具面现在互相矛盾的一处（不在我这一路的判类里，但必须报）：**
   `surface_thicken_silent_noop` 的台账 `limitations` 逐字「★ **按 A4 不登记成工具、不写 `verified`**」，
   而 `mcp-server/tool_specs_batch76.py` 里**已经有** `name="solidworks_thicken"`（挂 `sw_feature_entry_ops.thicken_surface`），其 doc 逐字自述「⚠ **尚未真机验证**（★ 由 `tools/probe_thicken_tool.py` 单独验）⇒ ★ 在那之前不许把它写成 `verified`」。
   ⇒ ★ **台账说「不登记成工具」、工具面已经登了** —— 需要有人拍板：是把工具撤掉，还是把台账改成「已登记、未验证」。

---

## 五、本路**没有**做 / 查不到的事（铁律 5）

| # | 事项 |
|---|---|
| 1 | **未运行 SolidWorks、未运行 pytest** ⇒ 表里「已挂 / 未挂」的依据全部来自**静态读源码**（`mcp-server/tool_specs_batch*.py`、`server.py`、`register_capabilities.py` 的 `BATCH_MODULES`），**不是**运行时 `rc.all_specs()` 的读数。 |
| 2 | **未核「已挂」那 7 条经工具层的端到端读数** —— batch76 自己逐字写着「⚠ 经**本工具**的端到端读数**尚未跑** ⇒ ★ 在那之前不许把它写成「经工具层已验证」」。 |
| 3 | `surface_ref_ops` 的**扫描曲面 / 边界曲面**两族**未判**（台账逐字「两个源都没给出」「查不到」）⇒ 不在本路可挂清单内。 |
| 4 | 未查覆盖率脚本里「曲面/扫描曲面」「曲面/边界曲面」两行的当前状态（★ 与我这一路的 15 条不重叠，属别的路）。 |
