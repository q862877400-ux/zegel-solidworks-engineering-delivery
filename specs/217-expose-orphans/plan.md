# 规格 217 · 实施计划（plan）

## 一、技术路线（★ 复用本仓既有工法，不发明新结构）

```
① 清点（★ 已有工具，不另造）：
   python tools/probe_unexposed_functions.py        # 1262 公开 / 470 已暴露下界 / 263 孤立
   python tools/probe_expose_candidates.py          # 交叉口径：未暴露 + 被生产代码调用 + 签名兼容
   ⇒ 读 output/orphan-capabilities.json 取 first_param_is_injectable / has_bare_coord_param
② 判"该不该暴露"（★ 人的判断，本规格我把判据写死在 spec.md §四）
③ 成批暴露：新建下一号 tool_specs_batchNNN.py（先查现有最大号）+ 在 register_capabilities.py 里挂上
④ 台账归属：capabilities.yaml 对应条目的 mcp_tools 加名（★ 只加名，不动 level）
⑤ 契约测试：按本仓既有形态（如 tests/test_spec213_batch100_tools.py：清单 + 契约）
⑥ 门禁：pwsh tools/round_chain.ps1 -Tests <新测试> ⇒ release_check 一轮即绿
⑦ 提交：python tools/commit_mine.py -m <信息文件> <路径…>
```

## 二、★ 关键实现约束（每条都有既有依据）

| 约束 | 依据 |
|---|---|
| ★ `ToolSpec` 的 **inject** 只给 `model` / `sw_app` / `study` —— 与候选的 `first_param_is_injectable` 对应 | ★ `AGENTS.md` §十七「按 ToolSpec 的契约调」|
| ★ **工具不收裸坐标**：有裸坐标形参者要么**加声明式选择**（`selection`/`selection_kind`），要么**不暴露** | ★ 规则 3（`docs/union-conventions.md`）+ `scripts/check_union_conventions.py` |
| ★ 阈值/枚举**只从官方源抄**（`C:\swapi\enums\*` 或反射），不许凭记忆 | ★ 铁律 4 + 事实 43 的教训 |
| ★ 优先暴露 **`*_report`** 形态（自带回读判据），而不是裸动作 | ★ 事实 40（`Create*Surface` 返回值不可靠）|
| ★ 长字符串里**禁用 ASCII 双引号**，一律用「」 | ★ 事实 560（本仓踩 7 次）|
| ★ 新建 `.py`：**docstring 只一行**，来源块紧随其后 | ★ `AGENTS.md` §十八 + `scripts/check_python_syntax.py`（第 19 道）|

## 三、分批（★ 按域缺口 + 同模块成组，先窄后宽）

| 批 | 内容 | 模块 | 域（缺口） |
|---|---|---|---|
| **B1** | 草图尺寸与约束（尺寸/完全定义/关系计数） | `sw_sketch_dimensions`(7) · `sw_sketch`(1) · `sw_sketch_edit_ops`(1) · `sw_selection_spec.entity_geometry`(1) | ③ 草图 33 / ④ 尺寸 10 |
| **B2** | 曲面系列（★ **只取带 `_report` 判据的**）| `sw_surface_features`(6) | ⑥ 曲面 8 |
| **B3** | 工程图读侧 | `sw_drawing_view.list_drawing_views_report`(1) | ⑪ 工程图 **49** |
| **B4** | 读侧/参数/测量 | `sw_mass_property`(2) · `sw_feature_readback.rib_params`(1) | ⑫ 检查测量 16 |
| **B5** | 特征/阵列/曲线 | `sw_part.linear_pattern_report` · `sw_loft.create_loft_cut_report` · `sw_sweep.create_sweep_surface_report` · `sw_curve_and_split`(2) · `sw_assembly.iter_feature_tree` · `sw_sheet_metal.iter_features` | ⑤ 零件特征 24 |
| **B6** | topology **读侧**（护城河域，★ 只暴露读，不碰已知回 `None` 的建侧）| `sw_topology` 的 `*_report`(5) | ⑯ 高级/专项（我方独有 40）|

★ 每批**独立收口**（三件套 + 门禁 + 提交），★ 批与批之间不叠改动 ✓

## 四、★ 明确排除（★ 本规格判"不暴露"，理由逐条）

| 候选 | 为什么不暴露 |
|---|---|
| `sw_mass_property.require_mass_property_document` / `require_section_document` | `require_*` = **前置守卫**，内部件 |
| `sw_render_material.get_extension` · `sw_selection.get_selection_manager` · `sw_fingerprint.doc_kind_of` | **内部访问器 / 判定件**，暴露无意义 |
| `sw_surface.create_bspline/conical/extrusion/offset/revolution/ruled/swept_surface` | ★★ **踩事实 40**（`IModeler.Create*Surface` 返回值不可靠）⇒ 改暴露 `sw_surface_features` 的 `*_report` |
| `sw_topology.get_topology_study_manager` / `get_topology_study_options` | **内部入口**（已有 `*_report` 版读侧）|
| `sw_sketch_modify_ops.select_active_sketch_segments` | ★ 它是 **`sketch_stretch` 的助手**（★ 清单生成于当天 05:26，晚于它的出现 ⇒ ★ **清单有时效**）|
| `sw_part.add_dimension` · `sw_part.insert_scale_report` | ★ 含**裸坐标形参**（规则 3）⇒ 除非改成声明式，否则不暴露 |

## 五、风险与守则

1. ★★ **不许把"暴露成功"记成"能力已验证"** —— `level` 不动（★ A4 判据用来守它；★ 规格 204 的 P4–P6 就栽在这）
2. ★ **不许为凑数重复暴露**（★ 先查既有 459 个工具名与近名语义）
3. ★ **清单以源码为准**：发现旧清单与源码不符时，**先重跑探针**再据实修正 ✓
4. ★ 每批 ≤ 一轮能做完的体量（★ 宁可多批、不要一批里混两类判断）
5. ★ 若某候选**暴露后立刻需要真机验证**，★ 那属于下一规格（本条只做暴露 + 契约测试）；
   ★ 但**若契约测试需要真机**，则走 `tools/sw_guard.py` 并在批内说明 ✓
