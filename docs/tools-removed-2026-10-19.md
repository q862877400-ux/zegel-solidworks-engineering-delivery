# 已删除的开发工具（2026-10-19 清理）

> ★ 业主判据：「只保留那种新 Agent 不用就会出事、和项目紧密结合的工具」。
> 本表记录**删了什么、它当时是干什么的**，便于将来判断要不要重建。

**删除判据（两条，均为硬判据）**：

1. **零引用**：在 2,371 份文档（`docs/` `specs/` `output/`）+ `known-facts.md`
   + `capabilities.yaml` + `dead-ends.md` 里**一次都没出现**（实测：扫 `docs/*.md`
   `docs/recon/*.md` `specs/**/*.md` `output/*.md` `output/**/*.md`，共 2,371 份）；
2. **按轮次命名**：`t1_*` / `t2_*` / `t4_*` / `w3_*` / `w6_*` / `s206_*` ——
   这些不是「一种用途」，是「某一轮的临时活」（正则 `^(?:t\d+|w\d+|s\d+)_`）。

**排除掉的（保留）**：

- **测试硬依赖**（`tests/` 里 `import` 它们，删了测试会断 —— 实测：扫 `tests/*.py` 的 import 语句，命中 6 个）：
  `probe_drawing_annotations_recheck` / `probe_loft_params_recheck` /
  `probe_sweep_units_recheck` / `probe_sweep_wall_units_recheck` /
  `probe_sweep_wall_units_via_hook` / `t2_intersect_past_errors`
- **实测叙述密集**（其结论可能只存在于该文件、未进 `known-facts.md` —— 实测 6 个）：
  `probe_gear_true_curves_full` / `probe_all_parametric_closure` /
  `probe_revolve_wall_units_recheck` / `probe_gear_closed_profile` /
  `probe_overlap_closure` / `probe_gear_coincident`

**共删 68 个 / 352 KB**（实测：`sum(文件字节)`，见下表「字节」列求和）。

> ⚠ **下表「当时是干什么的」列是各文件的**原始首句逐字**，其中出现的数字
> （如「534 条」「3709 条」）是**那些脚本自己当时的读数**，不是本次清理的统计。
> 本表不做二次核实 —— 文件已删，那些读数只作「当时它想干什么」的线索。

| 文件 | 字节 | 当时是干什么的（首句） |
|---|---|---|
| probe_batch81_tools.py | 6343 | ★ 批 81 工具的**真机抽查**（★ 按 `ToolSpec` 的契约调，不手调内部实现 —— AGENTS.md 的纪律）。（原文引述，文件已删） |
| probe_equation_rotation.py | 7004 | ★ 真机：★ `CreateEquationSpline2` 的 `RotationAngle` 与 `XOffset/YOffset` 可不可用。（原文引述，文件已删） |
| probe_equation_unit_factor.py | 5906 | ★ 真机：★ **方程式曲线参数式的单位** —— 读回端点，与解析值比。（原文引述，文件已删） |
| probe_gear_endpoints.py | 8730 | ★ 真机：★ **读回草图点的真实坐标** —— 判 6 条曲线是否**首尾重合**。（原文引述，文件已删） |
| probe_gear_lock_flags.py | 10203 | ★ 真机：★ **闭合齿廓的过定义根因** —— `LockStart`/`LockEnd` 是嫌疑。（原文引述，文件已删） |
| probe_gear_merge_points.py | 8338 | ★ 真机：★ **用 `ISketch::MergePoints` 合并亚微米缝** ⇒ 让真曲线齿廓闭合可拉伸。（原文引述，文件已删） |
| probe_gear_nolock.py | 6541 | ★ 真机：★ 闭合齿廓**不用** LockStart/LockEnd 能不能建（★ 只测这一格）。（原文引述，文件已删） |
| probe_gear_relation_closure.py | 10550 | ★ 真机：★ **用 `AddRelation(COINCIDENT=9)` 闭合真曲线齿廓**（★ 官方推荐路）。（原文引述，文件已删） |
| probe_gear_sketch_diagnosis.py | 11757 | ★ 真机：★ 诊断「真曲线齿轮草图为什么拉不出来」（★ 轮廓闭合性）。（原文引述，文件已删） |
| probe_gear_true_curves.py | 8962 | ★ 真机：★ **用真渐开线 + 真摆线齿根建直齿轮**（★ 替掉 12 段折线那个野路子）。（原文引述，文件已删） |
| probe_lens_retriever_replica.py | 7585 | ★ 复刻 `dsh-mcp-lens` 的检索器，并在**我们的目录**上跑 —— ★ 用来核「1000 个工具都能精准找回」。（原文引述，文件已删） |
| probe_mesh_profile_matrix.py | 9231 | ★ 有界的**网格档位对照**：同一零件、四种设置各建一次网格，看谁成、谁卡、吃多少内存。（原文引述，文件已删） |
| probe_rib_dome_params_recheck.py | 9936 | ★ 真机：★ 建**筋**与**圆顶**，★ 再用 `rib_params` / `dome_params` 读回 ⇒ ★ 量三个量。（原文引述，文件已删） |
| probe_rib_polyline_recheck.py | 7667 | ★ 真机：★ 用**折线**轮廓建筋（★ 照官方示例的 `CreateLine ×3`）⇒ 读回 ⇒ 量口径。（原文引述，文件已删） |
| probe_sketch_units_after_fix.py | 5658 | ★ 验证：草图族修好没有（★ 真机 + 包围盒判据）。（原文引述，文件已删） |
| probe_spec209_unfold_contract.py | 5438 | ★ 真机：unfold 的**选择契约**（固定面 mark 1 + 折弯 mark 4）—— 判据是**逐条回读 mark**。（原文引述，文件已删） |
| probe_spec211_external_members.py | 9531 | ★ 探针：那三个"从没查过"的参数式成员**到底存不存在** —— ★ 真机反射直调。（原文引述，文件已删） |
| probe_spec211_section_area_units.py | 6059 | ★ 探针：`GetSectionProperties2` 的**面积单位**（★ 用 `Face.GetArea()` 做基准回读）。（原文引述，文件已删） |
| probe_spec211_weldsymbol_forms.py | 9253 | ★ 探针：焊接符号的**第二个成因**（★ `Symbol` 形态 × 开关位）—— ★ 每组都回读。（原文引述，文件已删） |
| probe_spec220_bead.py | 3489 | ★ 探针：圆角焊缝（`InsertFilletBeadFeature2`）的真机建成与回读。（原文引述，文件已删） |
| probe_spec220_cosmetic_bead.py | 3950 | ★ 探针：装饰焊缝（`InsertCosmeticWeldBead`）的真机建成与回读。（原文引述，文件已删） |
| probe_spec220_member_shape.py | 5156 | ★ 探针：只读问清 `GetBodies2` / `GetFaces` / `GetBox` / `GetFeatureCount` 的形态。（原文引述，文件已删） |
| probe_sweep_params_recheck.py | 9744 | ★ 真机：★ 建一个**扫描**特征 ⇒ 用 `sweep_params` 读回 ⇒ 量两个长度量的口径。（原文引述，文件已删） |
| probe_tool_official_term_alignment.py | 4973 | ★ 检验一个假设（业主 2026-10-04）：「我们的英文词与官方文档没对应，对应上准确率就好了」。（原文引述，文件已删） |
| probe_unit_decisive.py | 7041 | ★ 决定性实验：同文档、同会话、单变量 —— 把 COM 侧单位钉死。（原文引述，文件已删） |
| probe_unit_suspects.py | 7553 | ★ 单位实测：用「包围盒/体积」回读判据，验证 4 个可疑函数到底是毫米还是米。（原文引述，文件已删） |
| s206_handoff_r39.py | 5346 | 第 39 轮：给 tasks.md 追加交接增补（只追加，不改已有内容；且全程不写 ASCII 引号）。（原文引述，文件已删） |
| s206_handoff_update.py | 4438 | ★ 第 17 轮增补：把 tasks.md 的交接节更新到最新状态（★ 只追加，不重写）。（原文引述，文件已删） |
| s206_number_selfcheck.py | 4151 | ★ 自查：我这一线的产出物之间，**共享数字**是否一致（★ SC-5 的落点：口径不许漂）。（原文引述，文件已删） |
| t1_apply_aliases_to_doc.py | 5970 | ★ T1-4：把采纳的别名按 D-2 **只追加**一行进那 10 个工具的 `doc`（不动 schema 契约、可回退）。（原文引述，文件已删） |
| t1_build_alias_table.py | 6173 | ★ T1-3：生成别名表 `docs/tool-aliases.md` + 裁判输入（★ 带诚实口径）。（原文引述，文件已删） |
| t1_close_out.py | 6280 | ★ T1 收口：修正 `docs/tool-aliases.md`（采纳 10 → 5）+ 写事实 520 的正文。（原文引述，文件已删） |
| t1_filter_alias_candidates.py | 4837 | ★ T1-1：从 C5 手核数据里**机械筛**出可信的「别名 → 工具」候选对。（原文引述，文件已删） |
| t1_joint_gain.py | 2605 | ★ T1-5b：量**联合**（十个别名同时装）下的逐工具增益 —— ★ 平均值不足以决定去留。（原文引述，文件已删） |
| t1_measure_alias_gain.py | 4903 | ★ T1-2：别名候选的**增益测量** —— 别名必须「挣到它的字节」。（原文引述，文件已删） |
| t1_remeasure_sc1.py | 6091 | ★ T1-5：带口径的复测（SC-1）—— ★ 两面都测，避免只报有利的那一面。（原文引述，文件已删） |
| t1_revert_nonearning_aliases.py | 2963 | ★ T1-6：按 D-2 判据收口 —— 留下**真提升**的 5 个别名，回退其余 5 个。（原文引述，文件已删） |
| t1_tally_alias_gate.py | 6396 | ★ T1-4：把裁判判定并进别名表 —— ★ 只采纳 `same`，其余标待复核/弃用。（原文引述，文件已删） |
| t2_filter_checkable_preconditions.py | 3035 | ★ T2-1/T2-2：从 534 条前置里**机械分出可机检的那些**（★ 会话/文档/选择/保存态）。（原文引述，文件已删） |
| t2_sample_vs_checkable.py | 4056 | ★ T2-4 缺口量化：我写的 3 个样板，在不在这 102 条「可机检前置」清单里？（原文引述，文件已删） |
| t2_write_precondition_gaps.py | 4565 | ★ T2-5：产出「哪些能力的前置未覆盖」清单给主线（★ D-5：只出清单，不改 level）。（原文引述，文件已删） |
| t3_2_spelling_pairs.py | 6833 | ★ T3-2：把已核验的错拼名逐个配对到本机真名（编辑距离），出「错拼 → 正确名」表。（原文引述，文件已删） |
| t4_2_more_specific.py | 5119 | ★ T4-2 机械复核：3709 条 example_more_specific 分类 + 与我们真调用交叉。（原文引述，文件已删） |
| t4_2_more_specific_b.py | 4772 | ★ T4-2 机械复核（单遍版）：3709 条 example_more_specific 分类 + 与我们真调用交叉。（原文引述，文件已删） |
| t4_2_sample20.py | 4656 | ★ T4-2 抽样表：258 个「与我们有关」的成员里，取条目最多的 20 个，抽齐判读材料。（原文引述，文件已删） |
| t4_3_build_lookup.py | 5919 | ★ T4-3：建「写码前必查表」+ 量 AGENTS.md 的指令预算余量（★ 超预算会静默截断）。（原文引述，文件已删） |
| t4_extract_unit_mark_conflicts.py | 4586 | ★ T4-1：从 C4 的 2.6 MB 产出里抽出 `unit_diff`(15) + `mark_diff`(10) 共 25 条，出逐条表。（原文引述，文件已删） |
| t4_fix_used_criterion.py | 6016 | ★ T4-1 修正：用 `ast` 精确区分「真调用」与「注释/文档里的提及」—— 修正上一轮的高估。（原文引述，文件已删） |
| t4_judge_materials.py | 4697 | ★ T4-1 第三步（机械抽取）：把那 8 个「我们用到」的成员的判读材料抽到一处。（原文引述，文件已删） |
| t4_mark_audit.py | 5446 | ★ T4-1 机械判读：mark_diff 冲突下，我们的调用点是否用了「能带 mark 的选择 API」。（原文引述，文件已删） |
| t4_member_crosscheck.py | 3877 | ★ T4-1 逐条核（机械部分）：25 条冲突涉及的成员，我们的代码用没用到、用在哪。（原文引述，文件已删） |
| t4_unit_audit.py | 5608 | ★ T4-1 机械判读（unit_diff）：我们的调用点附近有没有单位换算，换算方向是什么。（原文引述，文件已删） |
| t5_3_register_recon.py | 4808 | ★ T5-3：登记两个 recon 目录的原始 JSON 为**只读数据集**（★ 建议稿，不替主线做决定）。（原文引述，文件已删） |
| w2_candidates.py | 3146 | W2 候选筛选：工程图族里**已实现、首参可注入、且没挂**的函数。（原文引述，文件已删） |
| w2_gap_check.py | 3620 | W2：把 ⑪工程图 的 49 个缺口名逐个核「我们是否已有实现」。（原文引述，文件已删） |
| w3_deep.py | 2043 | import inspect（原文引述，文件已删） |
| w3_gap.py | 1289 | import json（原文引述，文件已删） |
| w3_have.py | 1855 | import re（原文引述，文件已删） |
| w3_props.py | 2065 | import inspect（原文引述，文件已删） |
| w4_cand.py | 2113 | import inspect（原文引述，文件已删） |
| w4_semantics.py | 740 | import inspect（原文引述，文件已删） |
| w4_sketch.py | 1584 | import inspect（原文引述，文件已删） |
| w5_feature.py | 658 | import inspect（原文引述，文件已删） |
| w6_cand.py | 1860 | import inspect（原文引述，文件已删） |
| w6_cand2.py | 2170 | import inspect（原文引述，文件已删） |
| w6_gap.py | 2562 | import inspect（原文引述，文件已删） |
| w6_shapes.py | 734 | import inspect（原文引述，文件已删） |
| w7_sim.py | 3733 | W7 前置：① 先查四家有没有**仿真载荷**的判据（用户纪律 §5.0）；② 核能力层现状。（原文引述，文件已删） |
