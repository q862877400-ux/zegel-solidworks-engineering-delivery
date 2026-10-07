# 规格 217 · 任务清单（tasks）

> ★ 每批独立收口：三件套（`all_specs()` 行 + `capabilities.yaml` 归属 + 契约测试）+ 门禁 + 提交。
> ★ 判据一律"可执行、可复算"：★ 新工具名逐个断言 · `release_check` 一轮即绿 · `git diff capabilities.yaml` **不出现 `level` 变更**。

## T-217-00 · 基线复核（★ 开工第一件事，不许跳过）

- ★ 重跑 `python tools/probe_unexposed_functions.py` 与 `tools/probe_expose_candidates.py`，**记录开工时的读数**（★ 清单有时效）
- ★ 记 `len(rc.all_specs())`、`git rev-parse --short HEAD`
- **验收**：★ 把三个读数写进 `goal-bar.md` 的基线行 ✓

## T-217-01 · B1 草图尺寸与约束（≈10 个）

- ★ 候选：`sw_sketch_dimensions`(7) · `sw_sketch.sketch_by_name` · `sw_sketch_edit_ops.sketch_intersect_curves` · `sw_selection_spec.entity_geometry`
- ★ 逐个按 spec §四 五条判据过一遍（★ 不中者写进"排除"并给理由）
- **验收**：★ 新工具在 `all_specs()` 里 · 契约测试过 · 门禁绿 · `level` 未变 ✓

## T-217-02 · B2 曲面（★ 只取 `*_report`）

- ★ 候选：`sw_surface_features` 的 `insert_offset_surface_report` · `insert_planar_ref_surface_report` · `insert_replace_face_report` · `insert_ruled_surface_report` · `thicken_surface_report` · `trim_surface_report`
- ★ ★ **明确不暴露裸 `sw_surface.create_*_surface`**（事实 40）
- **验收**：同 T-217-01 ✓

## T-217-03 · B3 工程图读侧

- ★ 候选：`sw_drawing_view.list_drawing_views_report`（★ 域 ⑪ 缺口最大 49，但本批候选仅 1）
- ★ 顺手核：该域是否还有**别的读侧**孤儿被本批漏掉（★ 重跑探针按模块过滤）✓
- **验收**：同 T-217-01 ✓

## T-217-04 · B4 读侧/参数/测量

- ★ 候选：`sw_mass_property.mass_property_object` · `sw_mass_property.section_area_crosscheck` · `sw_feature_readback.rib_params`
- ★ ★ 两个 `require_*` **不暴露**（已在 plan §四 登记）✓
- **验收**：同 T-217-01 ✓

## T-217-05 · B5 特征/阵列/曲线

- ★ 候选：`sw_part.linear_pattern_report` · `sw_loft.create_loft_cut_report` · `sw_sweep.create_sweep_surface_report` · `sw_curve_and_split.insert_mate_reference` · `sw_curve_and_split.insert_split_line_silhouette` · `sw_assembly.iter_feature_tree` · `sw_sheet_metal.iter_features`
- **验收**：同 T-217-01 ✓

## T-217-06 · B6 topology 读侧（护城河域）

- ★ 候选：`sw_topology` 的 `topology_constraints_report` · `topology_manager_report` · `topology_options_report` · `set_topology_goal_report` · `set_topology_iteration_options_report`
- ★ ★ **只暴露读侧**；★ 建侧已知回 `None`（族级边界，见规格 216 台账）⇒ **不碰**
- **验收**：同 T-217-01 ✓

## T-217-07 · 规格收口

- ★ 写最终账进 `goal-bar.md`：★ 开工/收工的工具数 · 暴露了多少 · 排除了多少（逐条理由）· 台账 `level` 是否未被抬高
- ★ ★ **明确声明**：★ 本规格**只增加暴露面**，**不宣称"功能覆盖完成"**（★ 规格 202 的立场）
- ★ 更新 `docs/ROADMAP.md` §一
- **验收**：★ `release_check` 一轮即绿 · 全量 pytest（★ 收口时才跑，见 `AGENTS.md` §十六）✓

## ★ 通用验收（每批都适用）

| # | 判据 | 命令 |
|---|---|---|
| G1 | 工具数增量 = 本批新增数 | `python -c "import register_capabilities as rc; print(len(rc.all_specs()))"` |
| G2 | 台账有归属 | `python scripts/check_union_conventions.py` ⇒ exit 0 |
| G3 | 参数绑定无裸坐标 | `python scripts/check_param_binding.py`（★ 由 release_check 内含）|
| G4 | 门禁全绿 | `pwsh tools/round_chain.ps1 -Tests <新测试>` ⇒ release_check 第 1 轮 OK |
| G5 | ★ `level` 未变 | `git diff capabilities.yaml` 里 grep `level` ⇒ **0 命中** |
| G6 | 不重名 | 新工具名与既有 `all_specs()` 名取交集 ⇒ **空** |
