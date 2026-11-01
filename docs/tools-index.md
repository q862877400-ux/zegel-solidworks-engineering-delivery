# 开发工具索引（`tools/`）

> ★ **本文件由 `tools/gen_tools_index.py` 生成，不要手改。**
> 重生成：`python tools/gen_tools_index.py`

**为什么有这份索引**：`tools/` 有 697 个脚本，此前没有任何索引 —— 「你不知道有，所以你没找」是可发现性问题，已有门禁 `check_probe_reuse.py` 只拦「明明有你还重写」，拦不住这个。

**怎么用**：先按「我想干什么」找到分类，再在分类里按文件名扫一眼。★ 每条的第一句就是它的用途（**lean 口径：结论在 120 字内，模型才看得见**）。

---

## 我想… → 去哪一类

| 我想… | 分类 | 条数 | 目录内文件前缀 |
|---|---|---|---|
| 真机验证某个 API 到底能不能用 / 怎么调 | **探针** | 282 | `probe_*` |
| 把探针结论落成可复现的证据 | **取证** | 110 | `prove_*` |
| 验证某能力端到端仍然可用 | **冒烟/回归** | 34 | `verify_*` |
| 静态检查，违反即红（部分在 scripts/ 下） | **门禁** | 17 | `check_*` |
| 从真源生成文档/索引（跑完要提交生成物） | **生成器** | 25 | `gen_*` |
| 对账/查缺口，只读不改 | **审计** | 11 | `audit_*` |
| 真机跑一遍并把结果落盘成证据 | **证据采集** | 19 | `capture_*` |
| 量一个数（覆盖率/误报率/成本） | **度量** | 9 | `measure_*` |
| 从官方源建结构化索引 | **构建索引** | 16 | `build_*` |
| 全仓扫描找某种形态 | **扫描** | 13 | `scan_*` |
| 给条目分类/定处置 | **分诊** | 5 | `triage_*` |
| 生成给人看的报告 | **报告** | 2 | `report_*` |
| 按规格串多个阶段跑 | **编排运行** | 16 | `run_*` |
| 列出某类条目 | **清单** | 4 | `list_*` |
| 对某类数据做分析 | **分析** | 2 | `analyze_*` |
| 对候选做判定 | **裁判** | 6 | `judge_*` |
| 查某现象为什么发生（不改任何东西） | **诊断** | 12 | `diag_*` |
| 按已知根因批量改文件 | **修复** | 3 | `fix_*` |
| 从官方源或日志里抽出结构 | **提取** | 4 | `extract_*` |
| 抽几条核对 | **抽检** | 3 | `spotcheck_*` |
| 对别人的结论再核一遍 | **复核** | 2 | `recheck_*` |
| 统计判定结果 | **计票** | 2 | `tally_*` |
| 弹窗处置相关（配 sw_guard 用） | **弹窗** | 2 | `modal_*` |
| 直接连 SolidWorks 的执行器/护栏 | **真机运行器** | 7 | `sw_*` |
| （未归入上面任何一类） | 其他 | 90 | — |

## 探针（282 个）

> 用途：真机验证某个 API 到底能不能用 / 怎么调

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `probe_a4_custom_properties.py` | ★ 真机补 `custom_properties_and_bom` 的运行证据（★ A4 的待补项） |
| `probe_a4_runtime_evidence.py` | ★ 为 A4 的两个真缺口跑真机证据：`parameter_updates` + `custom_properties_and_bom` |
| `probe_acceptance_report.py` | ★ 用现有样件生成一份真实报告 —— 证明报告链路能跑通 |
| `probe_access_selections_matrix.py` | ★ 真机：**批量**测 `*FeatureData.AccessSelections` —— 给「指针族」画确定边界 |
| `probe_access_selections_on_featuredata.py` | ★ 真机：对"静默 `None`"那几条试 `*FeatureData.AccessSelections`（事实 424 给的新路） |
| `probe_access_selections_param2.py` | ★ 真机：`AccessSelections` 的**第 2 参**到底要什么 —— `None` 还是空 Dispatch？ |
| `probe_activesketch_successor.py` | ★ 真机验证 `GetActiveSketch2` 的后继 `ISketchManager.ActiveSketch`（★ 属性）能不能替代 |
| `probe_add_component_diagnose.py` | ★ 诊断：为什么 `AddComponent5` 回 None |
| `probe_add_component_three_paths.py` | ★ 真机验证：用**本仓自己那条三步路**（`sw_assembly.add_component`）能不能建成组件 |
| `probe_add_relation_forms.py` | @brief 探针：`ISketchRelationManager.AddRelation` 的**调用形态** —— 拿完整 traceback，不猜 |
| `probe_add_view_two_trials.py` | ★ 真机：`add_view` 的两个独立试验 —— ★「模型先打开 vs 只给路径」（事实 324：每格独立） |
| `probe_all_parametric_closure.py` | ★ 真机：★ **全参数式方程式曲线**构成的闭合轮廓（★ 不混直线）—— 决定性判据 |
| `probe_analysis_run_long_timeout.py` | ★ 给足超时 + 正确网格尺寸，验 `analysis_run_readback` 的「跑求解」能不能算出结果 |
| `probe_assembly_family_successors.py` | ★ 真机验证装配族的**五条后继**（★ 一次跑完，★ 逐条记"能不能调"） |
| `probe_autodimension_successor.py` | ★ 真机验证 `ISketch.AutoDimension2` → `ISketchManager.FullyDefineSketch` |
| `probe_base_flange_params_recheck.py` | ★ 真机验 `base_flange_params` 并**测出钣金族的单位口径**（★ 阶段 3 · 第 8 个能力） |
| `probe_batch88_return_types.py` | ★ 真机验证批 88 里那 4 个"返回可能是 COM 对象"的工具 —— ★ 判据是**能不能过 JSON 边界** |
| `probe_brep_evidence_contract.py` | @brief 探针：按 `_load_brep_evidence` 的**真形态**造 B-Rep 证据，验证「篡改必被拒」 |
| `probe_capability_coverage.py` | @brief 探针：**哪些 `scripts/sw_*.py` 模块没有任何能力条目提到它** |
| `probe_chamfer_forms.py` | @brief 探针：`ISketchManager.CreateChamfer` 的**可行参数组合** —— 回读线段数当判据 |
| `probe_checked_zero_skip.py` | @brief 探针：复现「反射转储在、但**本仓库模块一个都解析不出**」时， `check_signature_audit_freshness` 是 `SKIP` 还是 `FAIL` |
| `probe_close_our_docs.py` | ★ 处置探针：关掉**我方产物**文档 —— ★ 判据**严格限制**、★ 并逐条自证 |
| `probe_component_transform_successor.py` | ★ 真机验证 `SetTransformAndSolve2` → `SetTransformAndSolve3` 与 `AddComponent4` → `AddComponent5` |
| `probe_composite_curve_edges.py` | @brief 探针：`InsertCompositeCurve` 换**边**（而不是整个草图）能不能成 |
| `probe_composite_curve_segments.py` | @brief 探针：**回读着 mark 计数**去选 2 个草图实体，再试 `InsertCompositeCurve` |
| `probe_composite_curve_selection.py` | @brief 探针：`InsertCompositeCurve` 到底要选**实体（草图段）**还是**草图特征**？ ## 为什么（轮 184） 轮 183 修好样条后，`verify_composite_curve_smoke` 里** |
| `probe_createspline3.py` | ★ 真机验：`CreateSpline3`（★ 现行的那个）**到底能不能调**（★ 阶段 2 · T1 第 ② 步） |
| `probe_csys_params_recheck.py` | ★ 真机验 `csys_params`（★ 阶段 3 补能力 · 第 7 个 · 第 6 个族） |
| `probe_custom_property_reads.py` | @brief 探针：**读文件自定义属性**的三条路 —— 以及 pywin32 下 by-ref 出参到底回不回写 |
| `probe_cut_list_property_names.py` | ★ 真机：切割清单属性名要**中文（本地化）**还是英文？—— ★ 用 `update_cut_list` 报的**真实属性名**去写 |
| `probe_cut_surface_bodies.py` | ★ 真机：`InsertCutSurface` 的 **`Bodies` 形态矩阵**（★ 上轮错码链的推论） |
| `probe_cut_surface_real_bodies.py` | ★ 真机：`InsertCutSurface` 的 **`Bodies` 传"真的体数组"**（★ 而非空数组） |
| `probe_cut_surface_returned.py` | ★ 真机：`InsertCutSurface` **返回的那个对象是什么**（★ 上一轮留的"新观测"） |
| `probe_cut_surface_selection.py` | ★ 真机：`InsertCutSurface` 的**选区变体**（★ 上一轮留的"另一个变量"） |
| `probe_datum_tag_selfcontained.py` | ★ 真机：自足建图（新工程图 + 从**已在盘上**的零件加视图）⇒ 再验 `InsertDatumTag2()` |
| `probe_datum_tag_selfcontained2.py` | ★ 真机：**先上 A3 图框**再 `add_view` —— ★ 承事实 327 的具体下一步 |
| `probe_dead_guards.py` | @brief 探针：找「**定义了却没人用**」的门禁常量（**死守卫**的通用形态） |
| `probe_deps_bom_undercut.py` | ★ 真机验证三条：`ExcludeFromBOM` · `GetDependencies2` · `MoldUndercutDetect` |
| `probe_dialog_guard_selftest.py` | ★ 弹窗监控的自测：让 SolidWorks **自己弹一个真消息框**，看常驻监控能否点掉 |
| `probe_dialog_guard_visible.py` | 把 SolidWorks 设为可见，然后再弹一次消息框 —— 这次它应该真的出现在屏幕上 |
| `probe_dialog_watch_fixes.py` | ★ 验证第 46 轮两个修复：日志去重 + 报告器结束进程 |
| `probe_dimension_edge_pairs.py` | ★ 真机：`AddDimension2` 的**边对穷举表** —— 找出"哪一类边对能定义出尺寸" |
| `probe_dimension_unit.py` | ★ 核：「`GetSystemValue3` 的单位随文档单位变」—— ★ 上一轮真机顺带量到的可疑 ① |
| `probe_direct_member_access.py` | @brief 探针：扫**直接属性访问**形态的疑似不存在 COM 成员 —— ★ 先量**假阳性率** |
| `probe_doc_cap_live.py` | ★ 真机验证「文档数上限」：故意开 5 个我方文档，看它是否只留 1 个 |
| `probe_doc_count_crosscheck.py` | ★ 核对 `open_doc_count` 与已验证的 `probe_list_open_docs` 是否一致 |
| `probe_document_units.py` | @brief 探针：**文档的单位设置** —— 它是不是"两次 `units=-1` 差 1000 倍"的源头 |
| `probe_drawing_annotations_recheck.py` | ★ 真机：★ 建工程图 + 加注释 ⇒ 用 `view_annotations_report` 读回（★ 工程图读侧第一批） |
| `probe_drawing_datum_tag.py` | ★ 真机：工程图**标注的写操作**第一枪 —— `InsertDatumTag2()` + `GetDatumTagCount()` 回读 |
| `probe_drawing_datum_tag2.py` | ★ 真机：工程图标注第二枪 —— **先选中视图**再 `InsertDatumTag2()`（★ 穷举"调用前提"） |
| `probe_drawing_object_routes.py` | @brief 探针：**工程图对象怎么取** —— 三条读数路（图纸 / 当前图纸属性 / 视图链） |
| `probe_drawing_tools_e2e.py` | ★ 工具层端到端探针：8 条工程图工具**按 ToolSpec 契约**能否经注册器跑通 |
| `probe_dwg_magic.py` | @brief 探针：`.dwg` 导出来的**到底是 DWG 还是 DXF**？—— **读魔数说话** |
| `probe_e2_hole_dimension_link.py` | 给四个孔心建尺寸（孔心 → 右板边），然后改板宽、量位移 —— E2.rebuild 的最后一步 |
| `probe_e2_hole_sketch_survey.py` | 只读勘察：这块板的**孔位草图**与**板宽尺寸**分别是什么 |
| `probe_e4_add_component_via_wrapper.py` | ★ 重测 E4 的加组件：走**高层封装** `sw_assembly.add_component`（含兜底），不走裸成员 |
| `probe_e4_assembly.py` | E4 真机装配探针（**唯一一份**）：搭两组件 → 试配合 → 读干涉 |
| `probe_endcap_face_matrix.py` | ★ 逐面矩阵：顶端盖到底要**哪一张面**才建得出来（★ 单变量：一次只换选中的面） |
| `probe_endcap_feature2.py` | ★ 照**官方例子**走 `InsertEndCapFeature2`（★ 7 参 · 面**当参数传** · 不需要预选） |
| `probe_endcap_official_args.py` | ★ 按**官方例子的实参**重测 `InsertEndCapFeature3`（★ 铁律：例子给的是调用序与配方） |
| `probe_enum_assembly_coverage.py` | @brief 探针：我们代码里写的官方枚举成员，分别落在**哪个 interop 程序集**里 |
| `probe_equation_expression_power.py` | ★ 真机：★ `CreateEquationSpline2` 的**表达式能力**（★ 决定根过渡曲线能不能用真 trochoid） |
| `probe_equation_units.py` | ★ 真机：★ 方程式曲线的**单位**（★ 决定渐开线会不会又犯 1000× 的错） |
| `probe_explicit_reject_family.py` | ★ 真机取证：`solidworks_part_sweep` 等「显式拒」四条，**经工具层必然失败**（区无路可给） |
| `probe_export_magic_matrix.py` | @brief 探针：**导出格式矩阵** —— 逐个格式**读魔数**，判「名实相符」与否 |
| `probe_expose_candidates.py` | @brief 换口径找暴露候选：**「未暴露 + 被生产代码调用」** 比「孤立」更靠得住 |
| `probe_exposure_surface.py` | @brief 探针：量清「本仓库 MCP 暴露面」的**两个来源**，判断「缺 339」是否被低估 |
| `probe_extension_add_dimension.py` | ★ 试一条**没试过**的建尺寸路径：`IModelDocExtension.AddDimension` |
| `probe_extrude_depth_recheck.py` | ★ 真机验新能力 `extrude_depth`（★ 阶段 3 补能力 · 复查） |
| `probe_extrude_depth_unit.py` | ★ 定案：`extrude_boss(20.0)` 建出来的实体，★ **真实的 bounding box 是多少毫米** |
| `probe_extrude_equation_profile.py` | ★ 真机：★ **最小闭合轮廓能不能拉伸** —— 隔离「方程式曲线」与「拉伸」两件事 |
| `probe_extrude_params_recheck.py` | ★ 真机验 `extrude_params`（★ 阶段 3 补能力 · 第 2 个） |
| `probe_extrudefeaturedata_getdepth.py` | ★ 真机验 `IExtrudeFeatureData2.GetDepth` —— 阶段 3 补能力 · 查 × 特征格的第一个 |
| `probe_feature_edit_e2e.py` | ★ 真机验证 `sw_part.feature_delete`（★ 阶段 5 补的第二个 `改 × 特征` 能力） |
| `probe_feature_info_recheck.py` | ★ 真机验 `feature_info`（★ 阶段 3 补能力 · 第 5 个 · 第 4 个族） |
| `probe_feature_names_blindspot.py` | ★ 真机：**`FirstFeature` 全链 dump** —— 为什么 `feature_names` 看不见 `SurfCut` |
| `probe_feature_suppress_e2e.py` | ★ 真机验证新增能力 `sw_part.feature_suppress` / `feature_unsuppress`（★ 阶段 5 补的缺口） |
| `probe_featurefillet3.py` | ★ 真机验 `FeatureFillet3` 能不能替代 `FeatureFillet`（★ 阶段 2 · T1 第 ② 步） |
| `probe_fillet_generations.py` | ★ 决定性对照：`FeatureFillet`（7 参，旧）与 `FeatureFillet3`（15 参，新）**谁真能建成倒角** |
| `probe_fillet_params_recheck.py` | ★ 真机验 `fillet_params` 并**测出那一族的单位口径**（★ 阶段 3 · 第 6 个能力） |
| `probe_fillet_precall_e2e.py` | ★ 真机验证 `solidworks_fillet` 的 `pre_call`：★ 声明式 `selection` ⇒ 选上 ⇒ **建成** |
| `probe_fingerprint_sensitivity.py` | ★ 指纹灵敏度标定（真机）：逐类挑一个"已知会改它"的写操作，看指纹有没有动 |
| `probe_first_load_rule.py` | ★ 真机：**"第一个载荷"那条规律**的独立确认 —— 换一个载荷当"第一个"，看回读是否照样崩 |
| `probe_flatten_tool.py` | ★ 真机验证：新工具 `solidworks_flatten_surface` 能否**按工具层契约**建成曲面展平 |
| `probe_fr008_explode_macro.py` | ★ 规格 204 / SC-005：批 79 的真机验证 —— **FR-008 的两半**（爆炸视图 + 宏执行） |
| `probe_fullydefinesketch.py` | ★ 真机验 `FullyDefineSketch` 能不能替代 `AutoDimension2`（★ 阶段 2 · T1 第 ② 步） |
| `probe_fullydefinesketch2.py` | ★ 按**官方示例的调用序**真机跑 `FullyDefineSketch`（★ 阶段 2 · T1 第 ② 步 · 第二轮） |
| `probe_gear_closed_profile.py` | ★ 真机：★ **完整齿轮轮廓** —— 每条边都是**真曲线**（★ 无一处折线逼近） |
| `probe_gear_coincident.py` | ★ 真机：★ **用 `AddRelation(COINCIDENT)` 强制闭合** —— 比 `MergePoints` 更规范 |
| `probe_gear_curve_by_curve.py` | ★ 真机：★ 逐条曲线**后**数段数 —— 找出那 6 条里哪一条没进去 |
| `probe_gear_tooth_pattern.py` | ★ 真机：★ **规范做法建齿轮** —— 一个齿（真曲线闭合）⇒ 拉伸 ⇒ 圆周阵列 ×z ⇒ 加轮缘 |
| `probe_gear_tooth_pattern2.py` | ★ 真机：★ **一个齿（真曲线）⇒ 拉伸 ⇒ 圆周阵列 ×z**（★ 规范做法） |
| `probe_gear_true_curves_full.py` | ★ 真机：★ **用真曲线建完整齿轮并回读**（★ 体积/包围盒/特征树 · ★ 判据 3 件一起） |
| `probe_geterrorcode2.py` | ★ 真机试 `IFeature.GetErrorCode2(out bool IsWarning)` —— ★ 它到底调不调得动 |
| `probe_getlines_count.py` | @brief 探针：`get_lines` 对**1 条直线**到底读回几条？（轮 140 冒烟里 12 对 1 的疑问） ## 疑问的来源 `tools/verify_centerline_smoke.py`：草图里**只画了 1 条中心 |
| `probe_getsystemvalue_on_existing.py` | ★ 真机验证 `IDimension.GetSystemValue2` / `SystemValue` → `GetSystemValue3` |
| `probe_getsystemvalue_successor.py` | ★ 真机验证 `IDimension.GetSystemValue2` / `SystemValue` → `GetSystemValue3` |
| `probe_graphicsredraw_successor.py` | ★ 真机验证 `GraphicsRedraw2` 的后继路径能不能调（★ 改之前先证） |
| `probe_gtol_frame_order.py` | @brief 探针：`geometric_tolerance` 的**另一半**能不能通 —— 试**正确的顺序** |
| `probe_gtol_indicator_matrix.py` | @brief 探针：`IGtolFrame.AddIndicator` 的**可行组合矩阵**（border × tol 全试一遍） |
| `probe_gtol_symbol_xml.py` | @brief 探针：绕开不通的 `AddIndicator`，试 **`IGtolFrame.SetSymbolXml`（XML 路径）** |
| `probe_gtol_xml_schema.py` | @brief 探针：拿官方 `ISldWorks.GetGtolFrameXMLSchema()`，看它要求什么结构 |
| `probe_hole_params_recheck.py` | ★ 真机验 `hole_params` 并**测出那一族的单位口径**（★ 阶段 3 补能力 · 第 4 个） |
| `probe_holewizard_arity.py` | ★ 决定性测量：`HoleWizard5` 在 Depth 之后要 **13** 个 double 还是 **14** 个？ ## 已知 - 官方 27 参：`… EndType, Diameter, Depth, Length, Valu |
| `probe_hv_dimension_with_selection.py` | ★ 真机：水平/竖直尺寸 —— **选中实体后**再试（★ 事实 421 留的下一步） |
| `probe_imathutility_family.py` | ★ 真机：**`IMathUtility` 那一族的可达性** —— ★ 逐个试它的成员 |
| `probe_inject_key.py` | ★ 判定：注入键 `sw_app`/`manager` 与目标函数形参 `sw`/`cost_manager` 不符时，能不能调通 |
| `probe_involute_equation_curve.py` | ★ 真机：**用方程式驱动曲线画真正的渐开线**（★ 替掉「12 段直线逼近」那个野路子） |
| `probe_involute_phase.py` | ★ 真机：★ **带相位的渐开线**能不能用一个表达式表达（★ 20 个齿共用一个式子） |
| `probe_judge_alternatives.py` | ★ 真机：**换判据前先验判据** —— 在已知成功的场景上同时读「旧判据」与「新判据」 |
| `probe_judge_object_type.py` | ★ 真机：**验一个新判据** —— 它落在**载荷对象**上（读 `Type`），而不是落在管理器的 `Count` 上 |
| `probe_knit_then_thicken.py` | ★ 真机：**先缝合、再加厚**（★ 官方原话里的 "knitted surface" 直指这条路） |
| `probe_linear_pattern_access_recheck.py` | ★ 真机：**重跑** `ILinearPatternFeatureData.AccessSelections`（★ 目标点名第一族的决定性实验） |
| `probe_linear_pattern_baseline.py` | ★ 按**官方示例的调用序**把「线性阵列」建成（★ 阶段 2 · T1 · 补基线） |
| `probe_linear_pattern_production_recheck.py` | ★ 真机复验：★ 换代后**生产函数 `linear_pattern`** 还能不能建成（★ 阶段 2 · T1 · 改完必验） |
| `probe_linearpattern4.py` | ★ 真机试：`FeatureLinearPattern4`（20 参）在前置成立时能不能建成线性阵列 |
| `probe_list_open_docs.py` | ★ 只读探针：列出会话里打开的文档，★ **不关、不改、不建任何东西** |
| `probe_load_entity_kinds.py` | ★ 真机：**实体种类 × 载荷** 的穷举表（★ 官方文本说这族各自要求的实体种类不同） |
| `probe_load_entity_kinds_clean.py` | ★ 真机：**每格一个新算例**重搭"实体种类 × 载荷"表（★ 做法①，★ 治上一版的格子污染） |
| `probe_load_state.py` | @brief 探针：**载荷的「活动状态」**（`ICWLoadsAndRestraints.State` 与 `SuppressUnSuppress()`） |
| `probe_load_state_active.py` | @brief 决定性实验：**把载荷 `State` 设成"另一侧"，再跑 `RunAnalysis`，看框还弹不弹** |
| `probe_loads_count_studytype.py` | ★ 真机诊断：`ICWLoadsAndRestraintsManager.Count` 在**静力**与**热**算例上分别是什么 |
| `probe_loft_fixed_e2e.py` | ★ 真机验证 `part_loft` 的修复：★ 带 `profile_sketches` 走**契约** ⇒ 前置过不过、建不建得成 |
| `probe_loft_params_recheck.py` | ★ 真机：★ 建一个**放样**（★ 两个轮廓）⇒ 用 `loft_params` 读回 ⇒ 量那几个量的口径 |
| `probe_mark_semantics.py` | @brief 探针：**mark 到底落没落？** —— 用「已知能选中」的**草图**做判别 |
| `probe_mass_property_reads.py` | @brief 探针：**读质量属性** —— 怎么取 `IMassProperty2`、成员可达性、以及**单位** |
| `probe_mass_units_controlled.py` | @brief **D3 对照实验**：`IMassProperty2.Mass` 的物理单位 —— 用**已知密度材料**定死它 |
| `probe_mate5_vs_createmate.py` | ★ 决定性对照：`AddMate5` 与后继 `CreateMate(MateData)` **谁真能建成 mate** |
| `probe_mate_after_save.py` | 候选 12：**先把装配存盘**再 `CreateMate` |
| `probe_mate_pickpoints.py` | 候选 13（最后一个）：`ICoincidentMateFeatureData.PickPoints` 显式给坐标 |
| `probe_mcp_stdio_handshake.py` | ★ 探针：对我们自己的 MCP 服务器做一次**真 JSON-RPC 握手**（★ 不连 SolidWorks） |
| `probe_mesh_settings_readonly.py` | ★ 只读：造零件+算例，然后**只读**网格设置那组数（★ 不写一个字节）—— 用来定单位口径 |
| `probe_mesh_units.py` | @brief 探针：`default_element_size_and_tolerance` 的 **`units` 口径** —— 父进程 vs 子进程 |
| `probe_mold_evidence_readers.py` | @brief 探针：`mold_evidence` 在真机上**全 None** —— 是"空件没有"还是"**读法不对**"？ ## 为什么（轮 172） `sw_mold.mold_evidence()` 在**新零件**上返回**全  |
| `probe_obsolete_members.py` | @brief 探针：我们**调用**的 COM 成员里，有几个官方已标 **Obsolete** |
| `probe_outparam_object_byref.py` | @brief 裁决 A5 里那条悬案：**`Object&` 出参到底要不要传？** ## 悬案原文（`docs/signature-audit.md` 批次 7 的「一条未查证的遗留」） `sw_hole_features.py` 的 4 |
| `probe_overlap_closure.py` | ★ 真机：★ **让相邻真曲线轻微交叠** ⇒ 轮廓真闭合（★ 机械 CAD 的通行做法） |
| `probe_parametric_scale_law.py` | ★ 真机：★ **全参数式正方形的尺度律** —— 直接量出单位因子（★ 不猜） |
| `probe_pattern5.py` | ★ 真机验 `FeatureLinearPattern5` / `FeatureCircularPattern5` 能不能替代 `3` / `4` |
| `probe_pattern_dimension_units.py` | ★ 测单位：`FeatureLinearPattern3` 的间距与 `AddDimension2` 的坐标究竟是米还是毫米 |
| `probe_pattern_direction_marks.py` | ★ 真机：线性阵列按**官方 Remarks 的 mark 表**给方向 —— mark=1 是方向、mark=4 是要阵列的特征 |
| `probe_pattern_direction_marks2.py` | ★ 真机：逐条边算中点、用 `SelectByID2(..., mark=1)` 试选方向 —— ★ 又是穷举表 |
| `probe_pattern_generations.py` | ★ 决定性对照：`FeatureLinearPattern3` / `FeatureCircularPattern4`（旧）**真能建成阵列吗** |
| `probe_pattern_params_recheck.py` | ★ 真机验 `pattern_params`（★ 阶段 3 补能力 · 第 3 个 · ★ 换族） |
| `probe_pdf_on_drawing.py` | @brief 探针：**工程图**上 `pdf` / `dwg` 能不能出 —— 补上轮矩阵里唯一没验的那格 |
| `probe_pin_asm_component_faces.py` | ★ 真机：销钉连接件的**最后一个候选** —— ★ 装配体 + 「**组件上的面**」 |
| `probe_pin_wants_faces.py` | ★ 真机：销钉连接件到底要**组件**还是**面** —— ★ 用"多体零件 + 两个面"做分辨实验 |
| `probe_planar_replace_variants.py` | ★ 真机：T605 平面区域 / T609 替换面的**选法变体**（上一轮各只试了一种） |
| `probe_r3_tools.py` | ★ R3 四条（钣金/焊件）的**首次**真机探针：按 ToolSpec 的契约逐条调 + 如实记前置 |
| `probe_readback_blindspot_bounds.py` | ★ 真机：**界定**事实 406 那个「回读盲区」的边界（★ 哪些特征 `feature_names` 看得见） |
| `probe_registry_wiring.py` | @brief 探针：找「**文件在、却没被登记**」与「**登记了、文件却不在**」的表 |
| `probe_render_material_family.py` | ★ 真机对照：渲染材质族的**旧入口 vs 新入口**（★ 决定怎么改之前先跑） |
| `probe_resolver_mark_matrix.py` | ★ 决定性对照：**mark 不同**时，`RESOLVERS["model"]` 会不会清掉选区 |
| `probe_result_serializer.py` | ★ 真机取证：`sw_part.fillet` 的返回**过不了 `_result` 的 `json.dumps`**（MCP 层会误报 error） |
| `probe_results_api_surface.py` | @brief P1 终局判定：运行期枚举活对象的成员，查三个「看结果」入口是否真的不存在 |
| `probe_revolve_oldstyle.py` | ★ 真机：**旋转曲面**走 `IModelDoc2`（**旧式** 4 参）—— 本仓此前只试过 `IFeatureManager` 那个 |
| `probe_revolve_params_recheck.py` | ★ 真机：★ 建**旋转**特征（★ 已知角度 30°）⇒ 用 `revolve_params` 读回 ⇒ 判度/弧度 |
| `probe_revolve_wall_units_recheck.py` | ★ 真机：★ 建**薄壁旋转** ⇒ 用 `revolve_params` 读回 ⇒ 量 `GetWallThickness` 的口径 |
| `probe_rib_preconditions.py` | @brief 探针：`InsertRib` 的**前置形态** —— 三个变体一次试掉（`rib` 真机失败的收敛） |
| `probe_ruled_surface_on_feature.py` | ★ 真机：直纹曲面（T608）—— 官方原话里的「**on this feature**」该怎么落实 |
| `probe_ruled_whats_wrong.py` | ★ 真机：直纹曲面失败后读 **What's Wrong**（★ 上轮留的"换观测手段"） |
| `probe_s3_autodim_why_fully_defined.py` | ★ S3 测量：`AutoDimension2` 只加 1 个尺寸，草图凭什么变成「全约束」？ ## 为什么查这个 上一轮真机读到（`specs/350-first-part-delivery/s3-t008-dimension-drive |
| `probe_s3_dimension_units.py` | ★ S3 测量探针：把三个「未查明」量准，不猜 |
| `probe_s3_dimensions_exist.py` | ★ S3 T008 前置核查：交付的板件到底有没有**驱动尺寸** |
| `probe_s3_e1_real_machine.py` | ★ S3 第 3 条：先验证**检查器能看见真实坏样件** |
| `probe_s3_e3_feature_tree.py` | ★ S3 真机采集：E3 特征树可编辑 —— 回读类型/错误/父子 + 实际编辑前序并验证后续 |
| `probe_s3_e3_imported_solid_negative.py` | ★ S3 真机负例：导入死实体能不能被 E3 判出来 |
| `probe_s3_fully_define_sketch.py` | ★ S3 测量：`ISketchManager.FullyDefineSketch` 到底怎么调才能用 |
| `probe_s3_hole_center_diagnose.py` | ★ 诊断：交付件里每张草图的段，以及圆心能不能读出来 |
| `probe_s3_hole_dimension_point_to_point.py` | ★ S3 测量：孔心用**点-点尺寸**约束到板角（同行已验证的选法范围内） |
| `probe_s3_hole_linkage_construction_line.py` | ★ S3 测量：用**构造线单段长度**把孔位绑到板边，让孔随板宽联动 |
| `probe_s3_hole_linkage_fully_define.py` | ★ S3 测量：孔与板轮廓放**同一张草图** + `FullyDefineSketch`，孔会不会随板宽联动？ ## 为什么值得试 E2 的硬要求是「孔随板宽变化」（`ENGINEERING-PATH` 第四节 E2 的负例逐字） |
| `probe_s3_holewizard_four_holes.py` | ★ 验证：按指定坐标建 4 个异型孔向导孔，孔位与孔型都读得回 |
| `probe_s3_holewizard_single.py` | ★ 单点验证：异型孔向导建一个孔，`hole_params` 能否读到孔型 |
| `probe_s3_t008_dimension_driven.py` | ★ S3 T008：把板件做成尺寸驱动 —— 用**可行的**那两个入口 |
| `probe_s4_assembly_create_and_interference.py` | ★ S3/E4 真机：装配创建与干涉检测 —— `assembly_and_mates` 从 `stitched` 往前推 |
| `probe_safearray_comtypes.py` | @brief 探针：换 **comtypes 早绑定**后端，`ISafeArrayUtility` 能不能驱动（含 `out` 形参） |
| `probe_safearray_utility.py` | @brief 探针：`ISldWorks.GetSafeArrayUtility()` 在 pywin32 上**可达吗**，`out` 形参能不能驱动 |
| `probe_select4_mark_e2e.py` | ★ 真机验证 `_select_com_object` 的 **Select4 + ISelectData** 新路径：mark 真的写得进去吗 |
| `probe_select_by_ray_count.py` | ★ 真机：`SelectByRay` 之后选区里**到底有几个东西、分别是什么** |
| `probe_selected_object_entry.py` | ★ 真机：**按位置取选区对象**的正确入口 —— `GetSelectedObject5` / `4` vs `GetSelectedObject6` |
| `probe_selected_objects_face.py` | ★ 真机：`GetSelectedObjectsFace` —— ★ 名字直接对应需求（**一次拿到所有选中的面**） |
| `probe_selection_count_e2e.py` | ★ 验证 bunny 的洞察：★ 诊断型工具（`selection_count` 等）经工具层**永远报 0**（事实 503 的另一种受害者） |
| `probe_selection_marks_split.py` | ★ 真机：分辨「两个 mark 桶」还是「同一个桶里的两个」—— 量 `GetSelectedObjectCount2` 按 mark 的取值 |
| `probe_selection_readback_raw.py` | ★ 真机：直接按序号读选区对象 —— ★ 看第 2 个到底抛了什么（`safe_get_com_member` 会吞异常） |
| `probe_selectionmgr_component_members.py` | ★ 在**活的 `SelectionMgr`** 上逐个试官方候选成员，看**哪一个真的可达**（★ 不猜名字） |
| `probe_server_dispatch_wiring.py` | @brief 探针：`server.py` **声明的工具** vs **协议层实际给出的** —— 集合比对 |
| `probe_session_accumulation.py` | ★ 真机：看**本会话累积了多少东西** —— 因为轮 418 的失败与 B 组无关、与会话状态有关 |
| `probe_setsavetoname_successor.py` | ★ 真机验证 `IPackAndGo.SetSaveToName` → `SetSaveToName2`（★ 判据：签名相同 ⇒ 疑似纯改名，仍须真机） |
| `probe_shell_params_recheck.py` | ★ 真机：★ 建一个**抽壳**特征，★ 再用 `shell_params` 读回来 ⇒ ★ 量**第八族**的单位口径 |
| `probe_shell_thickness_units.py` | @brief 探针：`IModelDoc2.InsertFeatureShell` 的 **`Thickness` 单位**（官方说**米**，模块说**毫米**） |
| `probe_simulation_addin_by_clsid.py` | @brief 纯读探针：用 **CLSID 的 `{GUID}`** 取 Simulation 加载项对象（**不加载任何 DLL**） |
| `probe_simulation_addin_status.py` | @brief 探针：`SldWorks.Simulation` 加载项**为什么取不到** —— 是没加载，还是没许可？ ## 为什么（轮 179） `topology_optimization` 是 `verified`，它的验收命令 ` |
| `probe_simulation_loadaddin_by_path.py` | @brief 决定性探针：用**正确的参数形态**调 `LoadAddIn`，让返回码回答「是不是许可问题」 |
| `probe_simulation_study_shapes.py` | @brief 探针：`iter_studies` 与 `create_static_study` 的**真实形状**（Spec Kit `141` 的 T1） |
| `probe_sketch_edit_pending_evidence.py` | ★ 真机验 `sketch_edit_ops` 里**未取证**的两项 —— `convert_entities` 与 `sketch_mirror` |
| `probe_sketch_enumeration_lag.py` | @brief 探针：核「刚建的草图」到底建了几个 —— ★★ **三种数法对照，暴露位置枚举滞后一格** |
| `probe_sketch_getter_shapes.py` | @brief 探针：**所有**按类型取法的返回形状 —— 是「对象列表」还是「数值数组」？ ## 起因（2026-10-01 轮 140） `get_lines` 的 docstring 写「直线」，实测却是**数值数组**（每条直线 * |
| `probe_sketch_object_routes.py` | @brief 探针：**从 model 取「草图对象」的三条路**，以及关掉草图后哪条还活着 |
| `probe_skip_semantics.py` | @brief 探针：把「文档在、但逐模块表读不出来」当输入，看 `check_signature_audit_freshness` 怎么走 |
| `probe_slot_and_point_shapes.py` | @brief 探针：`get_sketch_slots` / `get_sketch_points` 的形状（轮 142） |
| `probe_spec209_b2.py` | ★ 真机：规格 209 · B4-2（idx 173 hem）+ B2-1（idx 336 unfold）—— 判据全是回读 |
| `probe_spec209_b2_balloon.py` | ★ 真机：规格 209 · B2-2（idx 34 balloon）—— ★★ 给"两家外部项目结论互相矛盾"**定案** |
| `probe_spec209_b2_blank_sketch.py` | ★ 真机：规格 209 · B2-4（idx 175 blank_sketch）—— ★ 判据 = `IFeature::Visible` 的前后读数 |
| `probe_spec209_b2_centerline.py` | ★ 真机：规格 209 · B2-3（idx 52 centerline）—— ★ 给「静默无效 vs 能用」定案 |
| `probe_spec209_b3_entities.py` | ★ 真机：规格 209 · B3-1（idx 115 edges + idx 145 faces 合并）—— ★ 判据 = 计数 + 欧拉公式 |
| `probe_spec209_b4_intersect.py` | ★ 真机：规格 209 · B4-3（idx 181 intersect）—— ★ 唯一要验的是布尔 SafeArray 的包装 |
| `probe_spec209_b4_macro_recording.py` | ★ 真机：规格 209 · B4-1（idx 211 native_macro_recording）—— ★★ **永不点 StopMacro(31)** |
| `probe_spec209_b4_model_annotations.py` | ★ 真机：规格 209 · B4-5（idx 205 model_annotations）—— 判据 = 视图标注数的前后回读 |
| `probe_spec209_hem_diag.py` | ★ 真机：hem 为什么回 None —— **假设驱动的诊断**（一次跑完，不是换着参数瞎试） |
| `probe_spec209_hem_units.py` | ★ 真机：钣金厚度的**单位**到底是不是米？—— 用"厚度棱的长度"直接量 |
| `probe_spec209_unfold_fold.py` | ★ 真机：unfold（idx 336）+ fold（idx 155）—— ★ 判据全是回读（树增量 / 平展型式 / 逐条 mark） |
| `probe_spec211_curvedriven.py` | ★ 探针：`FeatureLocalCurveDrivenPattern` —— ★ 一次试两项（曲线驱动阵列 / 零部件阵列） |
| `probe_spec211_curvedriven_pre.py` | ★ 探针：`FeatureLocalCurveDrivenPattern` **第二步** —— ★ 追第二处成因「档位」 |
| `probe_spec211_explodeline.py` | ★ 探针：`ISketchManager::InsertExplodeLineSketch` —— ★ 爆炸直线（★ 零参） |
| `probe_spec211_flatsave.py` | ★ 探针：D 项（临时另存 → 展开 DXF）—— ★ 一个正例 + 两个负例 |
| `probe_spec211_formtool.py` | ★ 探针：`InsertFormToolFeature` —— ★ 成形工具（★ 前置链**全在本机**） |
| `probe_spec211_pdm.py` | ★ 探针：PDM 的真机可达性 —— ★ 判据是**抛不抛 + 拿不拿得到**（★ 铁律 5 的现场） |
| `probe_spec211_scale.py` | ★ 探针：`InsertScale` 的建成 / 体积 `x³` 判据 / 官方必然失败负例 / 我方工程选择 |
| `probe_spec211_section_properties.py` | ★ 探针：`IModelDocExtension::GetSectionProperties2` 的建状态 / 正例 / 官方必然失败负例 / 副作用 |
| `probe_spec211_section_props_forms.py` | ★ 探针：`GetSectionProperties2` 的形态判定（★ 与事实 386 那类"后端造不出包装"是不是同一形态） |
| `probe_spec211_section_units_cube.py` | ★ 探针：用**正方体**坐实 `GetSectionProperties2` 的面积单位（★ 六面同面积 ⇒ 消除面序干扰） |
| `probe_spec211_speedpak.py` | ★ 探针：`IAssemblyDoc::CreateSpeedPak` —— ★ 前置 = **选中的子装配** |
| `probe_spec211_sweep.py` | ★ 探针：`InsertSweepSurface2`（★ **那条从没查过的路 B**）—— ★ 最小实验：先看它的"行为" |
| `probe_spec211_sweep_pre.py` | ★ 探针：`InsertSweepSurface2` —— ★★ **给它把前置完全对上**：轮廓 mark 1 · 路径 mark 4 |
| `probe_spec211_sweep_variants.py` | ★ 探针：`InsertSweepSurface2` 的**两个未试变体** —— ★ 带引导线（mark 2）· 闭合路径 |
| `probe_spec211_untrim.py` | ★ 探针：`InsertUntrimSurface2`（取消剪裁）—— ★ 三条**必然失败**的负例 + 官方前置的实证 |
| `probe_spec211_weld_misc.py` | ★ 探针：B3 余下两项的**参数式入口** —— ★ 角撑板（`InsertGussetFeature3`）· 圆角焊缝（`…Feature3`） |
| `probe_spec211_weldsymbol.py` | ★ 探针：`IDrawingDoc::InsertWeldSymbol` —— ★ 焊接符号（★ 前置链全在本机） |
| `probe_spec211_weldsymbol_real.py` | ★ 探针：焊接符号的**真 API** —— ★ `IModelDoc2::InsertWeldSymbol3`（零参）+ `IWeldSymbol` |
| `probe_spec211_weldtrim.py` | ★ 探针：`InsertWeldmentTrimFeature2` —— ★ 先"查行为" + ★★ 两个数组形参的**形态判定** |
| `probe_spec211_weldtrim_opt.py` | ★ 探针：`InsertWeldmentTrimFeature2` **第三步** —— ★ 用**正确档位** `swEndConditionTrim(4)` |
| `probe_spec211_weldtrim_pre.py` | ★ 探针：`InsertWeldmentTrimFeature2` **第二步** —— ★ 把前置完全对上，把「试死」与「大发现」分开 |
| `probe_spec213_b2_modules.py` | ★ 探针：验 `scripts/` 里**新缝的两个模块函数**（B2 的产出）—— ★ 不是重复验探针内部实现 |
| `probe_spec213_b2b_modules.py` | ★ 探针：验 `scripts/` 里**新缝的三个装配/阵列模块函数**（B2b 的产出）—— ★ 不是重跑探针实现 |
| `probe_spec220_append_arms.py` | ★ 探针：只读判别"两选面"的 Append 语义（SelectByID2 臂 与 Select4 臂） |
| `probe_spec220_boundary.py` | ★ 探针：边界特征（官方 `IFeatureManager::InsertNetBlend`）两个 Type 的建成与回读 |
| `probe_spec_glob_gate.py` | @brief 负例：`check_spec_acceptance_paths` 对 glob 的处理必须**两边都对** |
| `probe_spline_creation.py` | @brief 探针：`sw_part.sketch_spline` 到底建没建成？（轮 141 里 `segments=0` 的追问） ## 疑问 `tools/probe_sketch_getter_shapes.py`：画 1/2 条样 |
| `probe_spline_fix.py` | ★ 真机验证：修好后的 `sw_part.sketch_spline` + 新工具 `solidworks_sketch_spline` 能否建成 |
| `probe_spline_forms.py` | @brief 探针：`ISketchManager.CreateSpline` 的**实参形态**（官方要求**扁平一维 double 数组**） |
| `probe_spline_redraw.py` | @brief 探针：样条到底是"没建成"还是"建成了但没重绘"？（轮 141 的第二问） ## 官方的说法（`C:\swapi\types\ISketchManager\CreateSpline2.md`） > This method do |
| `probe_split_line.py` | ★ 真机：**分割线**（三条入口：轮廓 / 投影 / 交叉） |
| `probe_split_line_projection_per_example.py` | ★ 真机：投影型分割线**照官方例子重做** —— 草图 mark=4 · 面 mark=1 |
| `probe_split_line_returns.py` | ★ 真机：**分割线三条入口的返回值到底是什么**（★ 补记事实 406 那条教训下的缺口） |
| `probe_surface_control.py` | ★ 对照实验：跑**本仓成功过的曲面特征**（填充曲面）—— 判别"曲面特征能不能建" |
| `probe_surface_fill_fallback.py` | ★ 真机验证 `surface_fill` 的回退：**给了 `selection`** 时该回退并**建成** |
| `probe_surface_modify_vs_create.py` | ★ 验证假设：**"改动已有体"成、"新建体"不成**（跑缝合曲面作对照） |
| `probe_surface_scale.py` | ★ 真机核：★ `sw_surface_features` 的 `* 0.001` 到底对不对（★ 事实 517 §三的待核项） |
| `probe_surfcut_recursive.py` | ★ 真机：**递归遍历**（含子特征）找 `SurfCut` —— 上一轮留的下一步 |
| `probe_sweep_fixed_e2e.py` | ★ 真机验证 `part_sweep` 的修复：★ 带 `profile_sketch`/`path_sketch` 走**契约** ⇒ 建不建得成 |
| `probe_sweep_oldstyle.py` | ★ 真机：`IModelDoc2.InsertSweepRefSurface2`（**旧式扫描曲面**）—— 能否推翻「到不了」 |
| `probe_sweep_set_profile_path.py` | ★ 决定性验证：曲面扫描**设上 `Profile` / `Path` 属性**后再 `CreateFeature` |
| `probe_sweep_surface_dedicated.py` | ★ 真机：**扫描曲面**走它的**专用方法** `IFeatureManager.InsertSweepSurface2/3` |
| `probe_sweep_surface_skip_access.py` | ★ 真机：扫描曲面**跳过 `AccessSelections`** 直接 `CreateFeature`（★ 新假设） |
| `probe_sweep_units_recheck.py` | ★ 真机：★ 给扫描设**圆轮廓 + 已知直径** ⇒ 用**包围盒独立判**那个长度量的口径 |
| `probe_sweep_wall_units_recheck.py` | ★ 真机：★ 建**薄壁**扫描、写一个**已知壁厚** ⇒ 用**体积**独立判它的口径 |
| `probe_sweep_wall_units_via_hook.py` | ★ 真机：★ 用**新钩子**在 `CreateFeature` **之前**设薄壁 ⇒ 量 `GetWallThickness` 的口径 |
| `probe_swept_flange_evidence.py` | ★ 真机验 `sheet_metal_creation` 里**唯一未取证**的那一项 —— `create_swept_flange` |
| `probe_swept_flange_v6.py` | ★ 照**官方例子**的调用序重试 `create_swept_flange`（★ 第 6 版 —— ★ 换做法，不是再试参数） |
| `probe_t011_edit_delivered_plate.py` | ★ S3 T011：在**已交付件的副本**上改板宽 100→120，验证下游联动、保存重开 |
| `probe_t302_four_families.py` | ★ 真机预试 **T302 的四个「无 `IAccessSelections`」族** —— 判它们是「指针族」还是「能建」 |
| `probe_t302_four_families_v2.py` | ★ 真机预试 **T302 的四个「无 `IAccessSelections`」族** —— ★ 第二版（★ 按官方签名逐参） |
| `probe_testonly_candidates.py` | @brief 量第三个池子：**「未暴露 + 只被测试调用」** —— 前两个口径都漏了它 |
| `probe_thermal_loads.py` | ★ 真机：那 5 条热载荷在**热算例**（`study_type=3`）下能不能建成 —— ★ 穷举表：算例类型 × 载荷 |
| `probe_thicken2.py` | ★ 真机：`IModelDoc2.FeatureBossThicken2`（4 参）——「加厚」的一个**没试过的变体** |
| `probe_thicken_matrix.py` | ★ 真机：`FeatureBossThicken` 的**参数矩阵**（★ 上一轮单组参数回了 `None`） |
| `probe_thicken_obsolete_entry.py` | ★ 真机：试**废弃入口** `IModelDoc2.FeatureBossThicken`（3 参）—— 上轮留下的假设 |
| `probe_thicken_tool.py` | ★ 真机验证：新工具 `solidworks_thicken` 能否**按工具层契约**建成加厚 |
| `probe_tool_rag_cn_vs_en.py` | ★ 中/英检索对照实验（离线，不碰 SolidWorks、不改任何文件） |
| `probe_tool_rag_feasibility.py` | ★ 可行性实验：**在本仓 433 个工具上内建一个检索（BM25）**，用真实任务查询量命中率 |
| `probe_tool_surface_language_overlap.py` | ★ 量化「中文查询 vs 英文工具面」的词元重叠 —— ★ 这是检索失败的结构性成因（不是算法问题） |
| `probe_trim_surface_by_object.py` | ★ 真机：剪裁曲面 —— 照官方例子的**顺序**，而把 `SURFACEBODY` 改成**按对象选** |
| `probe_trim_surface_per_example.py` | ★ 真机：剪裁曲面**照官方例子重做** —— 顺序是 `PreTrimSurface` → 选 `SURFACEBODY` → `PostTrimSurface` |
| `probe_typelib_add_loads.py` | ★ 真机：直接读**出厂类型库**里 `AddTemperature` 的真实参数表（`ITypeInfo.GetFuncDesc`） |
| `probe_uncalled_helpers.py` | @brief 探针：找「**定义了却从没被调用**」的函数 —— 死守卫的**另一种形态** |
| `probe_unexposed_functions.py` | @brief 反向全景：`scripts/sw_*.py` 的公开函数里，有多少**没被暴露成 MCP 工具** |
| `probe_union_adopt_b1.py` | ★ 真机：规格 209 · B1 批的 4 件活逐个试（★ 判据按能力分：回读状态 / 回读属性 / 回读清单） |
| `probe_unit_declarations.py` | @brief 探针：`scripts/sw_*.py` 里**哪些模块带长度参数、却没声明单位** |
| `probe_weldment_cutlist_dispid.py` | ★ 回筛：结构系统的 `InsertWeldmentCutList{,2}` 到底能不能调（`dispid` 路径） |
| `probe_weldment_cutlist_recheck.py` | ★ 真机：核「结构系统（焊件）」那一族 —— `InsertWeldmentCutList2` 的**真实形态**是什么 |
| `probe_window_vs_graphics.py` | @brief 探针：`SaveBMP(0,0)` 与 `SaveAs3` 的宽度差，是不是「窗口 vs 绘图区」？ ## 待解的疑问（轮 146/147 留下的「未查明」） ``` 同一份文档、同一个时刻： SaveBMP(0,0) ⇒ ( |

## 取证（110 个）

> 用途：把探针结论落成可复现的证据

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `prove_absolute_criteria.py` | ★ objective④ 收口：把**绝对 mm 判据**在真机上用一次（正例 + 负例 + 落 evidence） |
| `prove_authorization_check.py` | @brief 判据有效性检验：R11 的静态检查必须能抓到迁移前那两处真实泄漏 |
| `prove_b1_sketch_primitives.py` | ★ 真机：B1 批那 9 个草图图元逐个建（★ 判据 = 草图实体段数增加） |
| `prove_b3_intersect_curves.py` | ★ 真机：交叉曲线 —— 补**官方前置**（3D 草图 + 两个相交面）再试 |
| `prove_b3_sketch_edit.py` | ★ 真机：B3 批草图编辑 7 个逐个试（★ 判据**分操作定**：计数增量 或 几何增量） |
| `prove_b4_sketch_modify.py` | ★ B4 真机探针：在真零件上逐条跑「移动 / 旋转 / 缩放 / 伸展 / 镜像」 |
| `prove_b5_sketch_dimensions.py` | ★ 真机：B5 批草图尺寸与关系（★ 判据 = 草图特征上的**尺寸计数** + **关系计数**） |
| `prove_b6a_surface_edit.py` | ★ B6-a 真机探针：平面区域 / 等距曲面 / 直纹曲面 / 删除面 / 替换面 |
| `prove_b6b_surface_ref.py` | ★ B6-b 真机探针：旋转曲面 / 放样曲面（另 2 条单列，见实现层模块尾） |
| `prove_b7a_curve_split.py` | ★ B7-a 真机探针：分割线（投影/轮廓）/ 通过参考点的曲线 / 配合参考 |
| `prove_b8_ref_geometry.py` | ★ B8 真机探针：基准面 / 坐标系 / 点 / 质心 / 边界框 |
| `prove_basic_features.py` | ★ 真机：**基础功能逐个过一遍**（★ 每个操作一行判据，不许"大概能"） |
| `prove_boundary_boss_same_api_as_loft.py` | ★ 真机：**边界凸台/基体** —— 验它与「放样凸台/基体」在 API 上是不是**同一个** |
| `prove_chamfer_geometry.py` | ★ 真机：**倒角到底建成没有** —— ★ 三条判据并列，不拿「树没涨」定性（事实 104 的教训） |
| `prove_composite_curve_entities.py` | ★ 真机：**复合曲线** —— 试**三种合法实体**（★ 事实 449 留的下一步） |
| `prove_composite_curve_per_example.py` | ★ 真机：**复合曲线** —— 照官方例子的形态（★ 两个各含一条样条的草图 + SelectByID2 按名选） |
| `prove_connectors_two.py` | ★ 真机：B 组开头两条（链接连接件 · 刚性连接件）—— ★ "把选区一分为二"那条形态 |
| `prove_cosmetic_thread.py` | ★ 真机：**螺纹线** `InsertCosmeticThread3`（★ 7 参 · 未废弃） |
| `prove_coverage_gap_batch1.py` | ★ 真机：覆盖面缺口批 1 —— 旋转曲面 / 孔向导 / 完全定义检查（★ 只测**能测的**） |
| `prove_createline2_and_createspline.py` | ★ 真机：两条草图图元的**继任者** —— `CreateLine2`（中点线）· `CreateSpline`（样条） |
| `prove_createspline3.py` | ★ 真机：**`CreateSpline3`** —— 2D 样条 · **曲面上的样条**（★ `CreateSpline2` 的继任者） |
| `prove_curve_through_xyz.py` | ★ 真机：**通过 XYZ 点的曲线** —— `IModelDoc2.InsertCurveFileBegin/Point/End`（三步式） |
| `prove_cut_list_chain.py` | ★ 真机：**焊件切割清单那条链** —— ★ 在一个「**真有结构构件**」的文档上验 |
| `prove_cut_surface.py` | ★ 真机：**曲面切除**（`IFeatureManager.InsertCutSurface`）—— 与"剪裁曲面"是**两件事** |
| `prove_delete_hole.py` | ★ 真机：**删除孔** `IModelDoc2.InsertDeleteHole()`（★ 0 参 · 回 void ⇒ 判据用几何量） |
| `prove_delete_hole_for_surface.py` | ★ 真机：**删除孔（曲面）** `InsertDeleteHoleForSurface` —— ★ 更正事实 439 的实证入口 |
| `prove_delete_hole_inner_loop.py` | ★ 真机：删除孔（曲面）—— ★ **只选内环那圈边**（★ 事实 441 留的下一步） |
| `prove_delete_hole_on_surface.py` | ★ 真机：**删除孔** —— 在**带内环（缺口）的曲面体**上试（★ 事实 438 留的下一步） |
| `prove_dimension_and_pattern.py` | ★ 真机验：段 3 收尾两条（`add_dimension_report` · `linear_pattern_report`） |
| `prove_dimension_pattern_retry.py` | ★ 真机重试：段 3 收尾两条（`add_dimension` · `linear_pattern`）—— ★ 这次**选区卫生**是对的 |
| `prove_drawing_batch.py` | ★ 真机：工程图 13 项（视图族 5 + 标注族 8）—— 每格先回读前置，再调用 |
| `prove_equation_driven_curve.py` | ★ 真机：**方程式驱动的曲线** —— `ISketchManager.CreateEquationSpline2`（11 参） |
| `prove_export_two.py` | ★ 真机验：段 6 导出（图片导出做正例 |
| `prove_extend_surface.py` | ★ 真机验：`insert_extend_surface_report`（objective② 的真缺之一 `extend_surface`） |
| `prove_face_selector.py` | ★ 真机：按**声明式选择器**选面（`select_face_by_selector`） |
| `prove_family_d_readback.py` | ★ 真机：族 D 那批「属性赋值 + return True」**到底有没有生效**（★ 逐个回读，不靠返回值） |
| `prove_feature_toolbar.py` | ★ 真机：特征工具条那 21 个按钮逐个试（★ 用真入口，每个全新零件） |
| `prove_fill_surface.py` | ★ 真机验：`insert_fill_surface_report`（objective② 的第二个真缺 `filled_surface`） |
| `prove_fill_surface_selection.py` | ★ 真机：填充曲面 —— ★ 验 `boundary_z` → `selection` 这次改动的**两条路** |
| `prove_flat_pattern_dxf.py` | ★ 真机：先造**钣金件**（按工具契约调 base flange），再导**展开 DXF** |
| `prove_flatten_surface2.py` | ★ 真机：**曲面展平** `InsertFlattenSurface2`（★ 官方给了 2 参与五个 mark） |
| `prove_flatten_with_anchor.py` | ★ 真机：曲面展平 —— **补 `mark = 16`（锚点）**（★ 事实 434 说缺的就是它） |
| `prove_freeform.py` | ★ 真机：**自由样式**（`InsertFreeform2`）—— ★ 按官方 Remarks 的五步链走一遍 |
| `prove_freeform_matrix.py` | ★ 真机：自由样式 —— ★ **参数矩阵**（★ 官方材料已穷尽后的"最后手段"） |
| `prove_hole_pattern.py` | ★ 真机验：段 4 孔族的 `hole_pattern_report`（按孔位批量建孔） |
| `prove_hole_wizard5.py` | ★ 真机：**高级孔** —— `SelectByRay` 定孔位 + `IFeatureManager.HoleWizard5`（27 参） |
| `prove_hole_wizard5_build.py` | ★ 真机：**高级孔** —— `SelectByRay` 定孔位 + `IFeatureManager.HoleWizard5`（27 参） |
| `prove_hole_wizard_wrapper.py` | ★ 真机：验 **`create_hole_wizard_at_selection_report`** 这个包装（★ A4 要的运行证据） |
| `prove_linear_pattern_generations.py` | ★ 真机：`FeatureLinearPattern*` 三代逐个试 —— ★ 逐字照搬 `circular_pattern` 那套，只换成员名 |
| `prove_linear_pattern_geometry.py` | ★ 真机：`linear_pattern` 的卡点 —— ★ 判据**三条都看**（特征树 · 特征数 · **几何**） |
| `prove_linear_pattern_newarch.py` | ★ 真机试：线性阵列的**新架构**（`CreateDefinition` + `ILinearPatternFeatureData`） |
| `prove_link_connector_twobody.py` | ★ 真机：`AddLinkConnector` —— ★ **两个体各取一个顶点**（★ 承事实 372 那个下一个维度） |
| `prove_link_connector_vertex.py` | ★ 真机：`AddLinkConnector` —— ★ 形参名是 `VertexPoint*` ⇒ 试**顶点**那几个形态 |
| `prove_link_tool_contract.py` | ★ 真机：用**本仓的包装** `add_link_connector` 走**已验场景**（★ 两个体各一个顶点） |
| `prove_link_wrapper_twobody.py` | ★ 真机：用**本仓的包装** `add_link_connector` 走**已验场景**（★ 两个体各一个顶点） |
| `prove_loads_groupa3.py` | ★ 真机：A 组收尾三条（分布质量 / 力 / 远程载荷）在**静力算例**下能不能建 |
| `prove_loads_simple6.py` | ★ 真机验：段 5 的 6 个简单载荷（对流/弹性连接/热流/热功率/温度/辐射） |
| `prove_loft_cut.py` | ★ 真机：**放样切除** `InsertCutBlend`（★ 12 参 · 未废弃） |
| `prove_member_availability.py` | ★ 真机普查：`IModelDocExtension` 的 396 个成员，**哪些这个对象真的能用** |
| `prove_mold_family_rest.py` | ★ 真机验：模具族的另三个（分型面 / 关断面 / 型芯型腔）—— 承接分型线已打通 |
| `prove_mold_parting_geometry.py` | ★ `mold_parting_geometry` 的**写入那半**真机探针：先"准备"（选好拔模方向）再插分型线 |
| `prove_mold_parting_line_marks.py` | ★ 用"中点 + mark"重试 `insert_parting_line`（轮 51 因"边线带不了 mark"而走死） |
| `prove_name_selection_readback.py` | ★ 真机：按**名字**选草图线段，★ 看 `GetSelectedObject6(i, 0)` 读不读得到**多实体** |
| `prove_offset_on_surface_per_example.py` | ★ 真机：**曲面上偏移** —— ★ 严格按官方 VB 例子的**调用序**重试 |
| `prove_part_read_and_dimension.py` | ★ 真机验：段 3 的 2 个工具（`current_sketch_name` · `auto_dimension_sketch`） |
| `prove_pattern_members.py` | ★ 真机：`IFeatureManager` 上那几个**阵列成员**取得取不到 —— ★ 拿 `CircularPattern4`（已验能用）当对照 |
| `prove_pending_verification_three.py` | ★ 真机：复验「待验证」那桶里的三条 —— **筋** · **复合曲线** · **交叉曲线** |
| `prove_pin_connector_asm.py` | ★ 真机：装配体上的**销钉连接件** —— ★ 同族里"只要两个零件"的那条 |
| `prove_planar_region_then_delete_hole.py` | ★ 真机：**平面区域**造「真正的带孔曲面」+ 在其上试**删除孔**（★ 事实 442 留的下一步） |
| `prove_projection_curve.py` | ★ 真机：**投影曲线**（★ 第三代：`CreateDefinition(swFmRefCurve=14)` + `IProjectionCurveFeatureData`） |
| `prove_render_material_sequence.py` | ★ 照**官方示例**完整复现「把外观加到指定显示状态」的七步序列，并逐步入账 |
| `prove_revolve_axis.py` | ★ **旋转轴的几何级判据**：用「非对称轮廓绕不同轴 ⇒ 体积不同」证明**轴真的生效** |
| `prove_revolve_cut.py` | ★ 真机：**旋转切除** —— 官方文档指的路（`FeatureRevolve2(IsCut=True)`） |
| `prove_revolve_reference_axis.py` | ★ **参考轴（reference axis）路径的旋转**：照官方示例用 `SelectByID2(Axis1, "AXIS")` + 几何判据 |
| `prove_rigid_by_objects.py` | ★ 真机：**按已知实体清单**加刚性连接件 —— ★ 事实 337 的正解（**不读选区**） |
| `prove_rigid_connector_by_point.py` | ★ 真机：刚性连接件 —— ★ **换维度**：用「按面上的点」那条**已验证的路**选两组面（而非按序号选实体） |
| `prove_rigid_twobody.py` | ★ 真机：**双体零件**上试刚性连接件 —— ★ 事实 338 那个"它要两个体"的假设 |
| `prove_rotate_or_copy_3d.py` | ★ 真机：**复制实体** —— ★ 入口是 `ISketchManager.RotateOrCopy3DAboutXYZ`（`Copy=True`） |
| `prove_ruled_surface.py` | ★ 真机：直纹曲面（`IFeatureManager.InsertRuledSurfaceFromEdge2`）—— B6/T608 |
| `prove_selection_base.py` | ★ 真机验：段 1 选择底座的 6 个工具（`sw_selection_spec`） |
| `prove_selection_by_marks.py` | ★ 真机：验「**分桶取数**」这条修法 —— 两次选择用不同 mark，逐个桶各取一个对象 |
| `prove_shut_off_surface.py` | ★ 真机验：`insert_shut_off_surface`（先打一个**通孔** —— 关断面就是盖住通孔） |
| `prove_sketch_offset_on_surface.py` | ★ 真机：**曲面上偏移** —— `IModelDocExtension.SketchOffsetOnSurface`（4 参） |
| `prove_sketch_primitives.py` | ★ 真机验：段 2 草图图元的 5 个工具（`sw_part` 的 arc/ellipse/polygon/slot/centerline） |
| `prove_sketch_slot_four_types.py` | ★ 真机：**槽口**四种 —— 一条方法 `CreateSketchSlot` + 一个枚举覆盖（官方 + 反射给全了） |
| `prove_sketch_use_edge3.py` | ★ 真机：**侧影实体 / `SketchUseEdge3`** —— ★ 按**已核过的官方调用序**试 |
| `prove_spline_with_variant.py` | ★ 真机：**样条曲线** —— 用**前人已证的第三种形态**（`VARIANT(VT_ARRAY\|VT_R8)`） |
| `prove_split_line_geometry_controls.py` | ★ 真机：投影型分割线的**正例复核 + 三个负例对照**（★ 证明几何条件才是承重的） |
| `prove_split_line_geometry_isolate.py` | ★ 真机：投影型分割线的**因果隔离** —— 到底是"几何"还是"选面的方式"让它成立的？ |
| `prove_split_line_geometry_per_example.py` | ★ 真机：投影型分割线 —— 照官方例子重建**几何**（★ 不只是 marks） |
| `prove_split_line_minimal_matrix.py` | ★ 真机：投影型分割线的**最小前置矩阵** —— 每个前置都先验明"真的选上了"再调 |
| `prove_split_line_silhouette_marks.py` | ★ 真机：**轮廓型分割线**（`InsertSplitLineSil`）—— ★ 照官方 mark 表（方向项 **2** · 面 **1**） |
| `prove_splitline_and_silhouette.py` | ★ 真机：核两条"**做了但没登记**"的 —— 投影分割线 · 侧影实体 |
| `prove_structural_member.py` | ★ 真机：**结构构件**（焊件族）—— ★ 判据是**特征树**（不是 `Count`） |
| `prove_structure_system.py` | ★ 真机：建**结构系统**（Structure System）—— ★ 走事实 358 那条官方序列 |
| `prove_surface_oldstyle_three.py` | ★ 真机：三条**旧式**曲面方法（`IModelDoc2.Insert{Offset,PlanarRef,FeatureReplaceFace}*`） |
| `prove_sweep_ab.py` | ★ A/B 对比：同一套选区下，**实体扫描（17）** vs **曲面扫描（62）** |
| `prove_sweep_surface.py` | ★ 真机试：**曲面扫描**（`CreateDefinition(swFmRefSurface = 62)`） |
| `prove_symmetric_angular_dimension.py` | ★ 真机：**对称线性直径尺寸** —— `IModelDocExtension.AddSymmetricDimension`（★ 照官方例子） |
| `prove_thicken_surface.py` | ★ 真机：加厚曲面（`IFeatureManager.FeatureBossThicken`）—— B6/T610 |
| `prove_tool_availability.py` | ★ 真机：把成员可用性普查扩到**我们工具真正用的接口**，并与已注册 function 名取交集 |
| `prove_tools_by_contract.py` | ★ 按 `ToolSpec` 的契约真机调一批工具（★ 不是手调内部实现） |
| `prove_trim_surface.py` | ★ 真机：**剪裁曲面**（`IFeatureManager.PreTrimSurface` + `PostTrimSurface` · 两段式）—— B6/T607 |
| `prove_undo.py` | ★ 真机验：`undo_report`（objective② 的真缺 `undo`） |
| `prove_untrim_matrix.py` | ★ 真机：解除剪裁 —— 把上一轮收窄的三个可能**一次试完** |
| `prove_untrim_surface2.py` | ★ 真机：**解除剪裁曲面** `InsertUntrimSurface2`（★ 官方给全了 5 参与两个枚举） |
| `prove_untrim_with_trimmed_surface.py` | ★ 真机：**解除剪裁曲面** —— 先造出它的前置（★ 一张**真被剪裁过**的曲面） |
| `prove_view_name_matrix.py` | ★ 单变量矩阵：`ViewName` 取自**模型自己给的名单**（`GetModelViewNames`）能否建成视图 |
| `prove_weldment_cut_list.py` | ★ 真机：`sw_weldment.ensure_cut_list`（★ 它早已实现 dispid 兜底，★ 而没被接进工具层） |
| `prove_weldment_tools_e2e.py` | ★ 真机：**按工具层契约**跑焊件切割清单那条链（`create → ensure → evidence → csv`） |

## 冒烟/回归（34 个）

> 用途：验证某能力端到端仍然可用

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `verify_batch10_smoke.py` | @brief 真机冒烟：**走「工具声明」这条路**调 batch10 的 4 个工具 |
| `verify_batch5_smoke.py` | @brief 真机冒烟：`tool_specs_batch5` 的 5 个新工具（轮 91，Spec Kit `012`） |
| `verify_batch6_smoke.py` | 真机冒烟：batch6 的 3 个工具（轮 93） |
| `verify_batch7_smoke.py` | 真机冒烟：batch7 的 3 个工具（轮 96） |
| `verify_batch8_smoke.py` | 真机冒烟：batch8 的 3 个工具（轮 97） |
| `verify_batch9_smoke.py` | batch9 的**前置条件感知**冒烟（轮 98/99） |
| `verify_bbox_smoke.py` | @brief 真机冒烟：`sw_part.get_bounding_box`（边界框） |
| `verify_bmp_smoke.py` | @brief 真机冒烟：`sw_export.export_to_bmp` —— ★★ **读 BMP 头核对尺寸（定量往返）** |
| `verify_centerline_smoke.py` | @brief 真机冒烟：`sw_part.sketch_centerline` + **再测一次长度单位** |
| `verify_component_units.py` | ★ 真机验证单位纪律：按**米**放组件，回读变换矩阵必须是对应的**毫米**数 |
| `verify_composite_curve_smoke.py` | @brief 真机冒烟：`sw_part.insert_composite_curve` —— ★★ **定量往返**（选 2 个 ⇒ 读回 2） |
| `verify_costing_e2e.py` | @brief 验收命令：`costing` 的端到端真机闭环（**A9 的可跑工程实现**） |
| `verify_dfm_e2e.py` | @brief 验收命令：`dfm_checks` 的**端到端**（离线，**不碰 SolidWorks / OCP**） |
| `verify_dome_smoke.py` | @brief 真机冒烟：`sw_part.insert_dome` —— ★★ **定量**验证 + **再量一次单位** |
| `verify_dxf_preview_e2e.py` | @brief 验收命令：`dxf_preview_scene` 的**端到端**（离线，**不碰 SolidWorks**） |
| `verify_ellipse_smoke.py` | @brief 真机冒烟：`sw_part.sketch_ellipse` + **顺带量准 sketch 助手的单位** |
| `verify_equation_smoke.py` | @brief 真机冒烟：`sw_equation`（把 `stitched` 往 `verified` 推一步） |
| `verify_gate_note_numbers.py` | ★ 核 B-6 里 C4 / C11 的两组数（★ 改前先核） |
| `verify_gtol_smoke.py` | @brief 真机冒烟：`sw_gtol` —— 验**上轮选的那条 2022 格式路径**能不能用 |
| `verify_helix_smoke.py` | @brief 真机冒烟：`sw_helix` —— 验 `insert_helix` 那条路 |
| `verify_hole_standards_smoke.py` | @brief 真机冒烟：`sw_hole_features.list_hole_standards`（把孤儿包装接成能用的 API） |
| `verify_in_context_reference_smoke.py` | @brief 真机冒烟：**在上下文编辑 + 外部参考** —— 验提案 §六 的前两条判据 |
| `verify_interference_smoke.py` | @brief 真机冒烟：`sw_assembly.get_interference_detection` —— ★★ **定量**（真造出干涉） |
| `verify_mcp_protocol_layer.py` | @brief 真机探针：**MCP 协议层** —— 起 server，发 `tools/list`，核对声明的 schema |
| `verify_modal_dialog_lifecycle.py` | @brief 端到端验证：**故意复现**模态框 ⇒ 验证「能发现」+「能点掉」，且**零硬编码** |
| `verify_modal_polling_catches_async_dialog.py` | @brief 证伪实验：证明**一次性**模态框检查**真的会漏**，而**轮询**能抓到 |
| `verify_mold_draft_analysis_owner.py` | @brief 真机核 `MoldDraftAnalysis` 到底在不在 `IFeatureManager` 上（检查器 L197 那条新命中） |
| `verify_mold_evidence_smoke.py` | @brief 真机冒烟：`sw_mold.py` 的**只读**函数（`mold_evidence` 等）—— 给 `mold_tools` 拆条目取证 |
| `verify_motion_avi_e2e.py` | @brief 验收命令：`animation_export` 的真机端到端 —— **导出出非零 AVI** |
| `verify_png_smoke.py` | @brief 真机冒烟：`sw_export.export_to_image`（png/jpg）—— 读**魔数 + IHDR 尺寸** |
| `verify_routing_e2e.py` | @brief 验收命令：`routing` 的**中性复核**端到端（离线，**不碰 SolidWorks**） |
| `verify_sketch_edit_smoke.py` | @brief 真机冒烟：`sw_sketch_edit.create_sketch_chamfer`（草图倒角） |
| `verify_sketch_getters_smoke.py` | @brief 真机冒烟：`sw_sketch` 的取法 —— 重点验**轮 111 换到后继的那 6 个** |
| `verify_union_349.py` | ★ 规格 207 · V7-1：核验 349 条记录的覆盖与合法性（SC-1 / SC-5） |

## 门禁（17 个）

> 用途：静态检查，违反即红（部分在 scripts/ 下）

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `check_bunny_toolspec_rows.py` | ★ Bunny 扇出的**门禁**：逐行核 Buny 交回的 ToolSpec 草稿 —— ★ 判据全部**从盘上重推**，不信它自述 |
| `check_com_write_form.py` | ★ 门禁：**写 COM 属性必须用 `set_com_member`**，不能用 `get_com_member`（它会去"调用"属性） |
| `check_convergence_numbers.py` | ★ 核对收敛报告里的数字**是否与生成物一致** —— ★ 报告自己也要被判据管 |
| `check_corpus.py` | ★ 语料自检门禁（规格 315）：校验 L1/L2/L3 的全部约束 |
| `check_inject_binding.py` | ★ 门禁：每个 ToolSpec 声明的注入，必须覆盖包装的**必需**对象形参 |
| `check_judge_preflight.py` | ★ 判据前置检查：凡"用某个回读去判某条能力"的判据，必须**先在已知成功场景上被验过** |
| `check_obsolete_heuristic.py` | ★ 官方页「废弃」判定的**精确判据**（★ 只报不动 · ★ 阶段 3 · 判据修正） |
| `check_output_units.py` | ★ 规格 212 · D：**返回侧（输出）单位门禁** —— 扫全部工具返回字典的顶层键名 |
| `check_same_parser.py` | ★ 审计：有没有**同一个文件被不同解析器读**的地方（★ 承事实 370 那条定则） |
| `check_server_side_tools.py` | ★ 核：`server.py` 用 `@mcp.tool` 声明的那些工具，**在不在 ToolSpec 门禁的射程内** |
| `check_spec207_sc.py` | ★ 规格 207 的 SC-1..SC-8 机器判据（能机检的机检，不能的如实标"待人/待 deep"） |
| `check_subagent_models.py` | ★ 门禁：核「我派出去的子代理**实际**跑在哪个模型上」—— ★ 防"派活写着 bunny、实际跑 DeepSeek" |
| `check_tool_capability_coverage.py` | @brief **门禁：每个工具都要有归属** —— ★ 一个 `solidworks_*` 工具必须至少被**一条能力条目**认领 |
| `check_tool_param_binding.py` | ★ 静态交叉核对：**每一条 ToolSpec 声明的参数名，是否都在其目标函数的形参里** |
| `check_typelib_tables.py` | ★ 把能力层里**手抄的成员表**对着**出厂类型库**逐条核 —— 用 PowerShell 读 .NET 元数据 |
| `check_unit_suffix_consistency.py` | ★ 规格 212 · C 改版：**名字后缀 ↔ 描述单位词** 的一致性检查（★ 只报不拦） |
| `check_unit_suffix_reverse.py` | ★ 规格 212 · C：规则 2 的**逆向一半**（描述声明单位 ⇒ 名字必须有对应后缀）—— **只报不拦** |

## 生成器（25 个）

> 用途：从真源生成文档/索引（跑完要提交生成物）

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `gen_api_map.py` | # ── 来源 ───────────────────────────────────────────────────────────── # 仓库: 本项目自身（本工具为原创 |
| `gen_com_member_index.py` | ★ 生成「COM 成员 → 本仓哪个函数封了它」索引（治「忘了我们有工具」） |
| `gen_dead_ends.py` | ★ 从 `capabilities.yaml` 生成 **`docs/dead-ends.md`** —— 「这条路已经走死」的清单 |
| `gen_dsh_sw_preset.py` | ★ 生成并**校验** DSH 新 preset「Lean 模式（SW工程师）」的配置块（★ 只写文件、不 apply） |
| `gen_effect_declarations.py` | ★ 生成效应表（规格 210 · B1）：从底层成员动词机械初判每个工具改哪几类状态，落成生成物 |
| `gen_family_coverage.py` | 接口族覆盖度量化：14 个域的官方接口族，本仓库实际触及了多少 |
| `gen_fingerprint_calibration.py` | ★ 把指纹标定结果落成**可提交的记录**（规格 210 · B2 的收口产物） |
| `gen_goal_evidence.py` | ★ 规格 205 / SC-001 的**达标证据**：一份可复核的报告（工具数 · 门禁 · 各批 · 提交） |
| `gen_harvest_digest.py` | @brief 生成 `docs/harvest-digest.md` —— **交付报告的状态摘要（生成段）** |
| `gen_iview_registry.py` | # ── 来源 ───────────────────────────────────────────────────────────── # 仓库: 本项目自身（本工具为原创 |
| `gen_member_kind_index.py` | ★ 建「成员种类」索引：官方类型库里每个成员是**方法还是属性**，属性**能不能设** |
| `gen_member_registry.py` | 通用「接口族成员登记表」生成器 |
| `gen_metrics.py` | 生成 `docs/metrics.md` —— 项目里**所有对外引用的数字**，逐条给「定义 / 口径 / 当前值 / 重算命令」 |
| `gen_observed_effects.py` | ★ 把存活普查的**实证**落成覆盖层（★ 实证优先于静态 —— 规格 210 · B3/B4） |
| `gen_precall_patch.py` | ★ **生成器原型**：把 bunny 的 `precall-cand-*.py` 自动翻成"该给哪条 spec 挂什么"的**补丁计划** |
| `gen_spec211_final_table.py` | ★ 规格 211 · B8 收口：自动生成**21 项逐项结论表**（★ 台账终判 × `capabilities.yaml` 的 level） |
| `gen_spec211_ledger.py` | ★ 规格 211 · B0 台账生成器：逐项查官方入口 + 判可做性（★ 只读，不碰真机） |
| `gen_study_options_registry.py` | 从 cosworks 反射清单里机械生成各 StudyOptions 族的 setter 登记表 |
| `gen_survival_diff.py` | ★ 把存活普查结果落成记录（规格 210 · B3 的产物） |
| `gen_sw_enums.py` | 从官方枚举文件生成 `scripts/sw_enums.py` |
| `gen_tool_domain_catalogue.py` | ★ 生成"工具域目录"（供 AGENTS.md 引用 + 独立索引文档）—— ★ 判据全从 `all_specs()` 重推 |
| `gen_tool_official_claims.py` | 生成「工具 → 官方 API 页」台账**草稿**（不填 claim 证据，留给核验人逐条读页） |
| `gen_tool_rewrite_briefs.py` | ★ 为「每条工具改写」生成**工作简报**：一个 JSON，一个执行者一份 |
| `gen_tools_index.py` | ★ 生成 `docs/tools-index.md`：709 个开发工具的**可检索索引**（按 lean 口径） |
| `gen_usage_guide.py` | 生成 docs/usage-guide.md —— 「某个功能该看哪个官方示例、对应本仓库哪个函数」 |

## 审计（11 个）

> 用途：对账/查缺口，只读不改

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `audit_bunny_routing.py` | ★ 机械检查：某批派活**实际**跑的是哪个模型（解压会话日志，不认 list_agents） |
| `audit_caller_asserted_bools.py` | ★ 枚举「采集器收布尔、判定器当结论用」的字段 —— 第 38 轮那类缺陷的全景 |
| `audit_gap_implementations.py` | ★ 静态审计：`user-feature-coverage.md` 的缺口项，**本仓到底有没有真实现**（AST 为准） |
| `audit_get_com_member_semantics.py` | @brief 审计：`get_com_member(x, "Name")`（**无实参**）的调用点里，哪些 `Name` 是**方法**？ ## 为什么要查（2026-10-01 轮 143 查出的机制） `sw_connect.get_ |
| `audit_inout_array_params.py` | @brief 审计：**数组类形参的 `[in,out]` 方向** —— 用**类型库方法表**（第 4 套签名源） |
| `audit_real_gaps.py` | @brief **真缺口审计（⚠ 提示性，不是判据）**：能力层公开函数里，**可能**还没有入口的那些 |
| `audit_runtime_reachability.py` | @brief 运行期可达性审计：`scripts/` 用到的 COM 成员，在**活着的对象**上取得到吗？ ## 为什么需要它（本项目已证实的盲区） **已知事实 28**：`IModeler` 的 14 个曲面创建入口，反射里**全都有 |
| `audit_session_model.py` | ★ 解压 DSH 会话日志（zstd）并数出**实际用的模型路由** |
| `audit_silent_pass_guards.py` | 扫描判定器里「守护式判据」：`if <真值>:` 体内 return FAIL，假分支直接落到 PASS |
| `audit_test_plan_claims.py` | @brief 核 `D:\AI\SW-transfer\test-plan-final.md` 里点名的**路径 / 模块 / 函数**是否真实存在 |
| `audit_unit_suffixes.py` | ★ 规格 211 · 单位体检：**全部工具**的"形参名后缀 × 描述声明"一致性审计（★ 只读） |

## 证据采集（19 个）

> 用途：真机跑一遍并把结果落盘成证据

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `capture_appearance_evidence.py` | @brief 真机证据：**渲染材质与外观域**（24h 段 5 的「方程 / 渲染材质」那一半） |
| `capture_assembly_evidence.py` | @brief 真机证据：**装配只读 3 个工具**（砌墙 W6 / Spec Kit `139` 的验收②） |
| `capture_chamfer_fillet_evidence.py` | @brief 真机证据：**倒角 / 圆角 2 个工具**（砌墙 W4 续 / Spec Kit `137` 的验收②） |
| `capture_config_export_evidence.py` | @brief 真机证据：**配置族 6 + 导出族 6**（24h 段 4 / Spec Kit `147` 的验收②） |
| `capture_custom_property_evidence.py` | @brief 真机证据：**读文件自定义属性 2 个工具**（砌墙 W3 / Spec Kit `133` 的验收②） |
| `capture_drawing_query_evidence.py` | @brief 真机证据：**当前活动工程图的轻量只读读数 3 个工具**（砌墙 W2 / Spec Kit `132` 的验收②） |
| `capture_feature_build_evidence.py` | @brief 真机证据：**拉伸族 3 个工具**（砌墙 W4 续 / Spec Kit `136` 的验收②） |
| `capture_loadfamily_evidence.py` | @brief 真机证据：**载荷族 4 个工具**（24h 段 2.1 / Spec Kit `143` 的验收②） |
| `capture_mass_property_evidence.py` | @brief 真机证据：**读质量属性 1 个工具**（砌墙 W5 / Spec Kit `138` 的验收②） |
| `capture_mesh_sane_evidence.py` | @brief 真机证据：**网格参数生效判据**（24h 段 5「修地基」/ Spec Kit `145`） |
| `capture_mesh_solve_evidence.py` | @brief 真机证据：**网格 / 求解 / 读数 4 个工具**（24h 段 1.2 / Spec Kit `142` 的验收②）—— ★ **经进程隔离执行** |
| `capture_modeling_readback_evidence.py` | @brief 真机证据：**建模闭环补全 4 个工具**（24h 段 3 / Spec Kit `146` 的验收②） |
| `capture_simulation_evidence.py` | @brief 真机证据采集：跑完整仿真链并把结果写成**可复核的 JSON 证据文件** |
| `capture_simulation_loads_evidence.py` | @brief 真机证据：**仿真载荷 2 个工具**（砌墙 W7 / Spec Kit `140` 的验收②） |
| `capture_simulation_study_evidence.py` | @brief 真机证据：**仿真研究族 3 个工具**（24h 计划 段 1.1 / Spec Kit `141` 的验收②） |
| `capture_sketch_build_evidence.py` | @brief 真机证据：**建草图 + 画几何 5 个工具**（砌墙 W4 / Spec Kit `135` 的验收②） |
| `capture_sketch_evidence.py` | @brief 真机证据：**草图只读族 4 个工具**（砌墙 W1 / Spec Kit `131` 的验收②） |
| `capture_topology_evidence.py` | @brief 真机证据采集：跑**拓扑优化闭环**并把结果写成可复核的 JSON |
| `capture_topology_readback_evidence.py` | @brief 真机证据：**拓扑读数与参数 6 个工具**（24h 段 2.2 / Spec Kit `144` 的验收②） |

## 度量（9 个）

> 用途：量一个数（覆盖率/误报率/成本）

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `measure_copyability.py` | 量一件事：我们**已经挂出去**的工具，四家外部项目**有没有对应物**（能抄的话在哪儿） |
| `measure_fact_single_home_fp.py` | ★ T5-1 的 D-1 合规实测：给 `check_fact_single_home` 造 20 例，量它的误报率 |
| `measure_four_merged.py` | 仓库: 本项目自身 |
| `measure_function_fate.py` | 量清 692 个公开函数的三种命运：**挂了 / 被别的函数调用 / 两者都没有** |
| `measure_lean_catalog.py` | ★ 量一量：504 个工具按 **lean-mode 的规则**渲染出来到底多大（★ 并揪出废话最多的） |
| `measure_official_defects_fp.py` | ★ D-1 合规实测（第 2 道门禁）：`check_official_source_defects` 的误报率与漏报率 |
| `measure_rag_cold_sample.py` | ★ 冷门样本上的三族检索对照（★ 分层统计）—— 等 49 路的查询落地后跑 |
| `measure_realmachine_members.py` | 量清楚一件事：**官方 15,466 个成员里，我们真机试过多少个？** 方法（2026-10-01 轮 214）： ① 官方成员名清单 = `C:\swapi\types\<接口>\*.md` 的**文件名**（一个成员一个文件） ⇒ 这 |
| `measure_simulation_moat.py` | 量护城河：① 先查四家有没有**仿真载荷**的判据（用户纪律 §5.0） |

## 构建索引（16 个）

> 用途：从官方源建结构化索引

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `build_capability_matrix.py` | ★ 画「操作 × 对象」矩阵并跑**三个预先写死的可数判据**（★ 业主 2026-10-03 批准） |
| `build_capability_matrix_v2.py` | ★ **第二版矩阵**：用**真实映射**（工具 → COM 成员）填充，★ 重跑三个预先写死的判据 |
| `build_enum_scale.py` | ★ 抽**官方枚举的规模** —— ★ 矩阵第三轴「种类」的官方来源（★ 不是猜的） |
| `build_first_part.py` | ★ 首件重建（**唯一**入口）：4 个 **GB** 孔（标准已修 |
| `build_judge_inputs.py` | ★ 组装**盲判**输入：把 48 路挑出来的工具，配上它**真实的 title/描述**，给独立裁判判「能不能做这件事」 |
| `build_members_index.py` | ★ 建**全量成员索引**（接口 × 成员），并统计"同名成员分布在几个接口上" |
| `build_obsolete_index.py` | ★ 建**官方废弃成员索引**：把 `C:\swapi\types\**\*.md` 里带 `Obsolete` 的都收进来 |
| `build_pick_test_tasks.py` | ★ 第 0 步实测的**组题**：把 Bunny 写的中文查询当作任务文本（★ 不让我再写）， 分层抽一批，写成"让真模型挑工具"的输入文件 |
| `build_refuted_patterns.py` | ★ 建 `docs/refuted-patterns.json` —— ★ 让 `GATE-FINAL` 的 **C8** 真有可读对象 |
| `build_t0_judge_inputs.py` | ★ 组 T0-3 的裁判输入：把我的头条数字 + 口径声明交给三个独立裁判挑毛病 |
| `build_toolbar_ledger.py` | ★ 台账核实：把 `docs/toolbar-ledger.json` 里每个 api 名对**官方离线源**逐条核，并生成 Markdown 台账 |
| `build_toolspec_batch_from_rows.py` | ★ 把**过了门禁**的 Bunny 行，转成真正的 `mcp-server/tool_specs_batchNN.py`（扇出的"最后一公里"） |
| `build_union_denominator.py` | ★ 建**并集分母**：UI 功能（145 项）∪ 纯 API 功能（774 族）—— ★ 业主定的口径 |
| `build_union_map.py` | 生成「并集广度地图」—— 域 × 来源 矩阵 + 缺口清单 |
| `build_union_sources.py` | 扫描外部 MCP 项目，产出去重后的「并集来源清单」 |
| `build_union_verify_349.py` | ★ 聚合 349 条逐条记录成一份**合法 JSON 且 < 256 KB** 的产物（规格 207 的 SC-1 / SC-5） |

## 扫描（13 个）

> 用途：全仓扫描找某种形态

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `scan_bare_array_args.py` | @brief 扫「**数组实参没包 VARIANT**」的调用点（事实 167/183 证过的形状） |
| `scan_blind_criteria.py` | ★ 扫描器：找「判据看不见真实状态」这一族问题（B5 崩溃事故的同族） |
| `scan_evidence_links.py` | ★ 扫 `capabilities.yaml` 里全部 `output/*.json` 引用 —— ★ 报出**死链**（★ 同类问题一次扫清） |
| `scan_hardcoded_ok.py` | ★ 扫「**`ok` 是不是被写死的**」—— ★ 一次找出全部同类（★ 而不是逐个工具人眼找） |
| `scan_mm_meter_conversions.py` | ★ 扫全仓「把毫米当米 / 把米当毫米」的硬编码换算 —— ★ 上一条真 bug 的**扩散检查** |
| `scan_mm_without_conversion.py` | ★ 扫描：哪些工具声明了 `*_mm` 参数**却没有换算**（本缺陷的普查） |
| `scan_nondict_returns.py` | ★ 扫「目标函数的返回**不是 dict**」的工具 —— 它们经 MCP 层会被 `json.dumps` 判死 |
| `scan_obsolete_safe.py` | ★ **任务 3 · 扫全仓"用了官方废弃成员"** —— ★ 判据用「所有接口都废弃」的**安全名字**（★ 事实 511） |
| `scan_obsolete_usage.py` | ★ 批量扫：**我们仓里用了多少官方废弃成员**（★ 拿官方索引去比，不靠人读） |
| `scan_param_kind_consistency.py` | ★ 用**正确的字段名 `kind`**（不是 `type`）重做判据 ⑥⑦ —— 上一版两个都是**空跑** |
| `scan_preselect_requiring_tools.py` | ★ 精确扫「**前置**依赖调用方选区」的工具族（★ 比 bunny 的"读到选区"精确） |
| `scan_silent_source_fallbacks.py` | @brief 扫「**缺源时静默返回假值**」的兜底 —— 把「我不知道」写成「它有错」的那一族 |
| `scan_verified_without_implementation.py` | ★ 扫全台账：`verified` 条目挂的 **MCP 工具** 有没有**对应的实现函数**（★ 阶段 1 第二句） |

## 分诊（5 个）

> 用途：给条目分类/定处置

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `triage_get_members.py` | ★ 官方 `*FeatureData` 族 `Get*` 成员的**分诊表** —— 下一阶段"按官方成员批量补"的施工队列 |
| `triage_known_facts.py` | ★ 批次①·处置：**批量规则分类** 557 条事实 + 人工复核「吸收」档 |
| `triage_mech_design.py` | ★ 批次⑰：给 `mech-design` **全部 86 篇**做逐篇处置清单（★ 收口） |
| `triage_real_gaps.py` | ★ 真缺口分诊：把 `audit_real_gaps.py` 那 101 条分成 ① 该挂 ② 内部件 ③ 不做（+原因） |
| `triage_union_gaps.py` | @brief 分诊：`union-coverage-matrix` 的「缺口操作」里，多少是**别名**（我们其实有），多少是**真缺** |

## 报告（2 个）

> 用途：生成给人看的报告

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `report_batch_capability_levels.py` | ★ SC-008：报"某批工具**背后的能力**里有多少条是 `verified`"（★ 规格 205 §7.2 要求） |
| `report_false_positive_rate.py` | ★ 规格 207 · V7-2：假阳性率报告 —— **分类器自述**与**逐条实测**必须并列（SC-2 / SC-4） |

## 编排运行（16 个）

> 用途：按规格串多个阶段跑

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `run_migrated_verify_smokes.py` | @brief 逐个真机跑被迁移过的 `verify_*` 冒烟 —— 上轮（轮 169）迁移后只抽样跑了 2 个 |
| `run_s323_catalog.py` | ★ 规格 323 验收入口：任务域 + 受控多标签 + 分面检索（Q4/Q6 的 N1~N10） |
| `run_s324_gates.py` | ★ 规格 324 验收入口：门禁清单四类 + 责任人 + 元门禁覆盖 tools/（Q16） |
| `run_s325_protocols.py` | ★ 规格 325 验收入口：四类协议 + check_ref + 三态决策（Q1/Q5 的 R1~R10） |
| `run_s326_boundaries.py` | ★ 规格 326 验收入口：问题持久化 + DoD 边界 + 止损关口 + 运行边界（S1~S19） |
| `run_s327_manifest.py` | ★ 规格 327 验收入口：发布清单 + 规则取证 + 落点持久化（Q12/Q13/Q14） |
| `run_s328_cloud.py` | ★ 规格 328 验收入口：云政策 + 离线承诺 + 降级顺序（Q7 的 U1~U7） |
| `run_s3_acceptance.py` | ★ S3 验收运行器：在真机上采 E1 / E2 / E3，生成 `acceptance.md` |
| `run_stage1_plate.py` | ★ 阶段 1 生产入口：经方法入口安全建成参数板（规格 316 的真机验收） |
| `run_stage2_plate.py` | ★ 阶段 2 生产入口：真实孔组 + 规则 + 工程图 + 参数变更（规格 317 的真机验收） |
| `run_stage3_recovery.py` | ★ 阶段 3 验收入口：三类崩溃窗口 × 3 次 = 9/9（规格 318 的 S3-A/S3-B） |
| `run_stage4_corpus.py` | ★ 阶段 4 验收入口：60 条语义语料评估（规格 319 的 S4-A / S4-B） |
| `run_stage5_vise.py` | ★ 阶段 5 验收入口：平口钳（规格 320 的 S5） |
| `run_stage6_linkage.py` | ★ 阶段 6 验收入口：可调连杆（规格 321 的 S6） |
| `run_stage7_final_dod.py` | ★ 阶段 7 验收入口：最终 DoD（规格 322 的 S7-A / S7-B） |
| `run_verified_acceptance_commands.py` | @brief 逐条跑 `verified` 条目声明的**真机验收命令** —— 「曾经绿」要重新确认为「现在绿」 |

## 清单（4 个）

> 用途：列出某类条目

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `list_adoptable.py` | ★ 规格 207 · V7-3：从 bunny 的 deep 档记录里出**采纳候选清单**（SC-3） |
| `list_gap_capabilities.py` | ★ 列出能力清单里**没真正可用**的条目（`not_implemented` / `stitched`） |
| `list_production_obsolete.py` | ★ 列出**生产（`scripts/`）**里剩下的废弃成员调用点 —— ★ 逐条核"是不是都已判过" |
| `list_uncovered_user_features.py` | ★ 从 145 项用户功能清单里抽出「本仓库未覆盖」的那些（★ 只读，不改产物） |

## 分析（2 个）

> 用途：对某类数据做分析

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `analyze_family_features.py` | 抽「接口族的结构特征」，用来回答一件事： **「我们认定值得做并做了的族」与「还没做的族」在结构上有什么可判别的差异？** ## 为什么这么做（2026-10-01 轮 212） 用户给的方法是对的：**别靠感觉判「该不该做」，先从已经确定 |
| `analyze_spec_constitution.py` | ★ 跨制品一致性检查：把 `.specify` 宪法的 §I–§V 判据**跑出来**（`speckit.analyze` 的可执行版） |

## 裁判（6 个）

> 用途：对候选做判定

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `judge_bunny_records.py` | ★ 容错抽取 bunny 记录（溢出文件的 JSON 坏了 ⇒ 按字段正则捞，不靠整体 json 解析） |
| `judge_bunny_tallies.py` | ★ 从（被截断的）workflow 返回体里榨出裁决口径：`verdict_tally` + `recommendation_tally` 分档 |
| `judge_candidates.py` | 把 51 个候选族逐个判一遍：**它对应什么用户动作？** 方法（2026-10-01 轮 213）： ① 官方**示例**的标题里往往直接写着"拿这个接口干什么" —— 例如 `Rotate_Assembly_Component_on_A |
| `judge_gap_candidates.py` | ★ 批量判「缺口操作」：**先从四家取描述，再在我们这边找实现**（objective② 的判据） |
| `judge_naked_batch2.py` | ★ objective② 批量判定：把 naked 清单里的条目按**两层证据**判「真缺 vs 已有」 |
| `judge_two_boundary_cases.py` | ★ 判 `check_official_source_defects` 那 2 处边界：哪个是误报、哪个是真漏 |

## 诊断（12 个）

> 用途：查某现象为什么发生（不改任何东西）

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `diag_display_select.py` | ★ 诊断：`display` 读数为什么回 None |
| `diag_getbodies.py` | ★ 诊断：`IPartDoc.GetBodies2` 到底怎么调才拿得到实体（★ 它一直读不到） |
| `diag_getdocuments.py` | ★ 诊断：`ISldWorks.GetDocuments` / `GetDocumentCount` 到底怎么调才拿得到值 |
| `diag_in_context_projection.py` | ★ 诊断探针：定位「SketchUseEdge3 返回 ok 但投影出 0 个实体」的真因 |
| `diag_in_context_sketch.py` | @brief 诊断：`convert_entities` 之后**到底哪个草图里有几个实体** —— 换读数法，不再改写法 |
| `diag_insert_dome.py` | @brief 诊断：`InsertDome` 到底该怎么调？（轮 143，第 3 次终于对了之前先诊断） ## 已知 * 官方签名 `void IModelDoc2.InsertDome(double Height, bool Revers |
| `diag_mate_face_owner.py` | 聚焦诊断：**一束一束**射线地看归属，并打印每束命中点的坐标 |
| `diag_mate_two_faces.py` | 补一步：**同时选中两个面**后再读归属 —— 隔离「两项选择」这个情形 |
| `diag_read_exits_sketch.py` | ★ 诊断：抓指纹会不会把「草图编辑态」弄没（★ 决定三条 sketch_* 能不能跑） |
| `diag_residual_selection.py` | ★ 诊断探针 2：查「开草图后 selection=1」那个残留选择是什么 |
| `diag_selection_lifetime.py` | ★ 单变量隔离：选区在 `_pick_faces` 之后、工具读取之前，**到底被哪一步清掉** |
| `diag_weldment_feature_kind.py` | ★ 确认那个体是不是**焊件特征** —— 用 `IModelDoc2.FirstFeature`（属性）+ `GetTypeName2` |

## 修复（3 个）

> 用途：按已知根因批量改文件

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `fix_cjk_quotes.py` | ★ 把 Python 源码里「中文散文中的 ASCII 双引号」批量换成「」（★ 事实 48 的自动修法） |
| `fix_com_write_form.py` | ★ 批量修：把「用 get_com_member 写**属性**」改成 `set_com_member`（★ 按 AST span，不用正则） |
| `fix_exemption_escapes.py` | ★ 定点修 JSON：把我刚写进豁免理由里的 `C:\swapi` 补上转义（★ 用 json.load 自证） |

## 提取（4 个）

> 用途：从官方源或日志里抽出结构

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `extract_cosworks_docs.py` | 从 CHM 解包出的 cosworks 官方文档页里提取正文 |
| `extract_exclusive_ops.py` | ★ 抽出四家的「独家操作」（只出现在**一家**的操作名）⇒ 带编号的清单文件 |
| `extract_operation_descriptions.py` | ★ 从四家仓库抽「操作名 → 描述」表，给分诊表里的"缺口操作"取**判据依据** |
| `extract_psr_shots.py` | 把 PSR 的 `.mht` / `.zip` 里的截图按步骤顺序拆成图片（用标准库 `email` 解析） |

## 抽检（3 个）

> 用途：抽几条核对

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `spotcheck_contract_summaries.py` | ★ 自动抽验验：从 bunny 的契约摘要里抽「签名断言」，★ 拿**官方原文**核 |
| `spotcheck_t003_l1.py` | ★ T003 抽查：把 `recon/bunny-L1-signature-transcribe.md` 的断言逐条拿**官方原文**核 |
| `spotcheck_t003_l2.py` | T003 抽查（第二份）：核 `recon/bunny-L2-official-member-calls.md` 的 143 个成员名 |

## 复核（2 个）

> 用途：对别人的结论再核一遍

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `recheck_bare_array_negative.py` | @brief **负例校验**：证明 `scan_bare_array_args.py` 的判据抓得到它要抓的那个形态 |
| `recheck_param_iface_inference.py` | @brief 复算：`check_member_owner_interface.py` 的**形参接口推断**推错了哪两处 |

## 计票（2 个）

> 用途：统计判定结果

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `tally_pick_test.py` | ★ 最终结算：**「模型挑出来的第一个工具，到底对不对」**（★ 不是"有没有命中我标的那个"） |
| `tally_t0_judges.py` | ★ 合并三裁判的发现（★ 同一条缺陷被多路报出 ⇒ 置信度更高） |

## 弹窗（2 个）

> 用途：弹窗处置相关（配 sw_guard 用）

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `modal_dialog_forensics.py` | ★ **弹窗取证**：发现弹窗 ⇒ 截图 + 抓结构 ⇒ 落盘 ⇒ **交给 LLM 判根因**（★ 不自动点） |
| `modal_dialog_safe.py` | ★ **不阻塞的弹窗检测**：在**有硬时限的子进程**里跑 `collect_dialogs`，超时也能报出"发现弹窗" |

## 真机运行器（7 个）

> 用途：直接连 SolidWorks 的执行器/护栏

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `sw_dialog_watch.py` | ★ 常驻弹窗监控：**本项目一启用就跟着起来**，一直盯着 SolidWorks 家族的弹窗 |
| `sw_dialog_watchdog.py` | @brief SolidWorks 系窗口**看门狗** —— ⚠⚠⚠ 【已被否决 —— 不是正解】（见 known-facts 176） ## ⚠⚠⚠ **用户 2026-10-01 明确否决了这个方案，它不是正解** ``` 用户原话： |
| `sw_grid.py` | ★ 打开 SolidWorks 的**网格显示**（标准视图下的背景标尺） |
| `sw_guard.py` | ★ **带弹窗哨兵的调用护栏**：真机调用从它走 ⇒ **弹窗被主动发现、主动点掉、内容随返回值上来** |
| `sw_scene_report.py` | ★ 场景报告：上色 + 三视图 + **人话描述**（人工验收阶段 2 的标准取证工具） |
| `sw_screenshot.py` | 把 SolidWorks 主窗口截成 PNG —— 用视觉看它**实际**显示了什么 |
| `sw_snapshot_loop.py` | 后台连拍：每隔几秒给 SolidWorks 窗口截一张 —— 录下用户人工操作的**过程** |

## 按轮次临时（1 个）

> 用途：按轮次/批次命名的临时活（t1_/t4_/w6_/s206_ 等），不是一种长期用途

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `t2_intersect_past_errors.py` | ★ T2-4 的交集法：把「102 条可机检前置」与「本仓自己的过去错误笔记」交叉，挑出下一批该写断言的 |

## 其他（90 个）

> 用途：未按前缀归类的脚本

| 脚本 | 用途（第一句，≤120 字） |
|---|---|
| `aggregate_audit_vs_official.py` | ★ 批量抽 bunny 那 30 路对比稿的**结构与计数**，找规律（★ 业主指令：等对比稿到齐后批量总结） |
| `annotate_obsolete_form.py` | ★ 给废弃命中补一维标注「方法 ↔ 属性」（★ 任务书阶段 2 要的那一类 · 轮 135 · 第二版） |
| `apply_dsh_sw_preset.py` | ★ 把生成好的 preset 块**安全地**追加进 DSH 活配置（★ 校验不过就自动回滚） |
| `apply_tool_official_claims.py` | 按批把「官方依据台账草稿」落成**台账记录**（自动核验档），并挑出需要人读的条目 |
| `arity_negative_case.py` | @brief **故意写错**的 arity 负例 —— 给 `scripts/audit_call_arity.py` 当"应该抓住"的输入 |
| `backfill_source_blocks.py` | 给早于 §十八 的 .py 补来源块（dry-run 先看，--write 才落盘） |
| `bunny_toolspec_pipeline.py` | ★ Bunny 扇出 → ToolSpec 批次 的**五步管线驱动**（collect → backfill → gate → remaining → build） |
| `capability_gap.py` | @brief 按**能力**对照各域缺口（补上广度地图只数 MCP 工具名的口径缺陷） |
| `census_orphan_callability.py` | @brief 可调用性普查：22 个「暴露候选」孤立能力，**真机各调一次** |
| `census_pre_calls.py` | ★ 普查 2.0：**跟调用图**再判 pre_call 有没有回读（★ 上一版只看一个函数的文本 ⇒ 假阳性 3 个） |
| `classify_audit_divergences.py` | ★ 把 bunny 对比稿里的**分歧点**抽出来分类 —— 找"批量推进"的规律（★ 业主指令） |
| `classify_unplaced_tools.py` | ★ 把「无处可放」的 30 个**分类**：★ 哪些是"纯数据/纯计算工具"（★ 本来就不该有 COM 成员） |
| `close_modify_box_and_count.py` | 关掉「修改尺寸」框（ESC），然后**复核尺寸数** —— 判 `Extension.AddDimension` 是否真建成了 |
| `close_my_orphans.py` | 清掉我这两轮 E4 探针留下的 3 个孤儿文档（**先逐条核归属，再关**） |
| `close_orphan_plate_doc.py` | ★ 极窄清理：只关「**路径为空** 且标题以 `板1_rev-1` 开头」的文档 |
| `close_our_docs.py` | ★ 关掉**我方**打开的文档（★ 一个都不碰别人的 |
| `close_own_solidworks.py` | ★ 关掉**你自己开的**那一份 SolidWorks —— 只在确认那些文档都是自己开的时才动手 |
| `close_spec207.py` | ★ 规格 207 的收尾链（一条命令）：重跑聚合件 → SC 复检 → 采纳清单 → 打印裁决输入 |
| `closure_inventory.py` | ★ 批次⑱：**收口盘点** —— 全仓还剩什么没扫（★ 逐处给结论） |
| `cluster_known_facts.py` | ★ 批次①·续：把 221 条「该吸收」的事实**按主题聚类**，找出与 L3 相关的 |
| `collect_bunny_rows.py` | ★ 收集 Bunny 扇出的**产物文件**，合成一份再过门禁（★ 扇出改成"写文件"后的配套） |
| `collect_e4_standalone.py` | E4 采集器（**独立进程**）—— 按事实 569 的结论拆出来 |
| `collect_judge_fixes.py` | ★ 从 3 份裁判稿里抽「🔴 立刻要改」清单 —— ★ 汇总成一张可执行的工作表 |
| `com_member_probe.py` | ★ 问真机：一个 COM 对象**能用哪些成员** —— 并与程序集里的名单对差 |
| `commit_mine.py` | ★ 提交纪律护栏：**只提交自己这一线的文件**，并在提交前拦住「误带删除」 |
| `compare_geometry.py` | ★ **几何等价判据**（拓扑 + \|ΔV\| + \|ΔA\|）—— 2026-10-01 · 轮 321 |
| `coop_prepare_mate_v2.py` | ★ 修正版 · 人工验收第 2 步「准备」：让上面那块**真的在 Y 方向抬高** |
| `coop_step2_prepare_mate.py` | 人工验收 · 第 2 步「准备」：摆好两块板，**保持打开**给业主看 |
| `coop_step3_execute_mate.py` | 人工验收 · 第 3 步「执行」：在两块板之间建**重合配合** |
| `demo_capture.py` | ★ **示范捕获（试教）**：把业主的一次手工示范完整接住 —— 步骤 + 画面 + 模型语义 |
| `diagnose_fact_gate_recall.py` | ★ T5-1 的 recall 诊断：查那 2 例「真复述」为什么没被报出来 |
| `discard_orphan_via_closeall.py` | ★ 按官方语义丢弃那个孤儿文档：`ISldWorks.CloseAllDocuments(True)` |
| `e4_probe_common.py` | E4 证据探针的共用小件：**边跑边写**的证据收集器 |
| `ec00_drafts_audit.py` | ★ EC00 残留 ③ 审计 —— 逐份核 `output/ENGINEERING_*.md` 的「来源+许可+可运行验收」三项 |
| `ec00_scope_inventory.py` | ★ EC00 范围清单：静态盘点代表工具集的**注入/参数/单位/风险/效果/来源/等级**（★ **不连接 COM**） |
| `emit_iview_module.py` | 生成 scripts/sw_drawing_view.py（IView 成员登记表 + 通用访问器） |
| `emit_study_options_module.py` | 生成 scripts/sw_simulation_study_options.py（含 setter 登记表） |
| `eval_lean_comprehension.py` | ★ lean 首句**可懂性**评测：模型只看到「首句（≤120 字符）+ 参数名」，能不能答对 |
| `eval_tool_selection.py` | ★ 工具选择评测：真实 `tools/list` → 拼题面 → 调模型 → 按 **specs/208 D-9** 口径判 |
| `experiment_subprocess_com.py` | @brief 小实验：**子进程能否安全地连到**同一个** SolidWorks 实例**（进程隔离方案的前提） |
| `fake_modal_dialog.py` | @brief 假模态框：造一个 **类名 `#32770`** 的窗口并停住（给判据当**靶子**） |
| `fetch_api_signature.py` | @brief 取官方 API 参考的**成员签名**（在线优先，本地 CHM 兜底），并落本地缓存 |
| `final_sweep.py` | ★ 第 19 轮：全仓最后一遍扫描 —— 判「还剩什么」 |
| `find_com_wrapper.py` | ★ 反查：这个 COM 成员，我们**已经封过**吗？ ## 为什么（业主 2026-10-26 质问） > 你怎么又开始查官方 API 了？…我们自己不是有草图阵列的这个 MCP 工具吗？ 我手写了 `AddDimension2` / ` |
| `fixtures.py` | ★ 夹具库：真实件**一次性**复制进来、**冻结哈希清单**，此后测试只认它、不再碰原目录 |
| `freeze_unattended_baseline.py` | 抓迁移前的 unattended_allowed() 真集 —— 这是等价性验收测试的黄金基线 |
| `goal_gate.py` | ★ Stop hook 的**验收条件**：`output/AUTO_HANDOFF.md` ② 段没有编号待办 ⇒ exit 0（达成） |
| `guard_run.py` | ★ **通用命令护栏**：跑任何命令时，把「弹窗」变成命令输出的一部分 |
| `harvest_scan.py` | ★ 批次②–⑥的**通用挖掘器**：扫指定目录，抽「可吸收的建模知识」，逐条判定 |
| `index_examples.py` | 把 C:\swapi 的官方示例按 14 个功能域归类，产出「域 × 官方示例」索引 |
| `index_examples2.py` | 按示例**实际用到的官方类型**把 2,839 个官方示例归到 14 个功能域 |
| `inspect_level_and_entry.py` | ★ 看 `capabilities.yaml` 的 level 取值分布 + 某条目的 limitations（★ 供 A-assembly F1 处置） |
| `lean_first_sentence.py` | ★ 给 ToolSpec 的 `doc=` **插一行短首句**（★ 只做加法、★ 不动原有内容） |
| `make_bunny_workload.py` | ★ 生成 bunny 工作量清单：一条一个操作（③强候选 + ②需人工核） |
| `make_fixture_library.py` | ★ 建/校验夹具库：真实件一次性复制进来、冻结哈希清单 |
| `make_union_workload_349.py` | ★ 编全 349 条的工作量清单（tier-aware）：①档只验证，②③档深调 |
| `map_tools_to_members.py` | ★ **筛选器**：把 277 个工具映射到「它真正调的 COM 成员」⇒ 再投影到官方结构上 |
| `mcp_tools_list.py` | ★ 一次**真 MCP 握手**取 `tools/list` —— 那是宿主**真正看得见**的那一份工具面 |
| `metric_scope.py` | ★ 指标的「口径」注册表 —— 口径必须落成可复现代码，不能只写在散文里 |
| `migrate_pilot_to_five_levels.py` | @brief `pilot` → 五级迁移（`docs/capabilities-schema-proposal.md` §1.2，裁断走选项 A） |
| `migrate_tool_evidence.py` | ★ 把每条 `ToolSpec.doc` 的**原文**搬进新字段 `evidence=`（★ 只搬运、不改写 doc） |
| `parse_cosworks_signatures.py` | 从提取出的 cosworks 官方文档页里解析出全部方法签名与参数说明 |
| `plan_obsolete_fixes.py` | ★ T1a 第一步：把**每一条废弃调用**与它**后继的官方签名**逐个对照 ⇒ 分清"纯改名"与"要改参数" |
| `propose_capability_sources.py` | @brief 为 `capabilities[].source` 生成**有证据的提案**（不写文件，只打印） |
| `reclaim_solidworks.py` | ★ **SolidWorks 会话解卡**：探连接 → 判定能不能安全重启 → 重启 → 复验 |
| `register_topology_capability.py` | @brief 把拓扑优化登记进 capabilities.yaml（护城河域） |
| `rename_pep8_names.py` | 把 ruff 报的 N812 / N806 改名成 PEP 8 口径（★ 每个名字全文件唯一才动） |
| `repair_harvest_report_line.py` | ★ 恢复 docs/harvest-report.md 里被审计输出覆盖的那一行（★ 第二次发生 |
| `restore_deliverable_width.py` | 把交付件的板宽改回设计值（100mm）并保存 —— 探针验证时把它改成 120 了 |
| `sample_cold_tools_for_rag_test.py` | ★ 机械抽样：从全部工具清单里挑一批**冷门**的（★ 不靠我的口味） |
| `selfcheck_official_source_errors.py` | ★ 自校 `docs/history/official-source-errors.md` 里写的"真名"—— ★ 逐个去官方核 |
| `selfcheck_teach.py` | 示教工具**全能力自检**：不依赖业主操作，逐项跑并给 PASS/FAIL/SKIP |
| `session_verdict.py` | ★ 会话裁决：**一个裁决、两条探路** —— 会话干不干净、有没有未保存改动 |
| `set_subagent_default_model.py` | ★ 把子代理的默认模型改成 bunny（写活配置 `profiles/web/cordis.patch.yml`，先备份） |
| `setup_mate_demo.py` | 摆好「人工做一个配合」的现场：装配里放两块板（第二块抬高 50mm），**保持打开** |
| `spec211_manual_verdicts.py` | ★ 规格 211 · B0 的**人工终判表**（★ 每条注明依据 |
| `splice_section.py` | ★ 把一段 .md 文本拼接进目标文件（★ 结构性绕开"长中文串 + 引号嵌套"这个反复踩的坑） |
| `split_rag_sample_for_fanout.py` | ★ 把抽样切成 60 份（每份 2 个工具），给 60 路 Bunny 各读一份 —— ★ 避免在提示里内联 105 条记录 |
| `survey_effect_declarations.py` | ★ 只读普查：为 448 个工具机械初判「效应声明」（改哪些状态类别），产出报告而不改声明 |
| `survive_sweep.py` | ★ 存活普查：逐工具「调一次 + 前后抓指纹」，输出「声明 vs 观察」差异表 |
| `swdoc_search.py` | ★ 三源检索入口：官方 CHM 正文树（.html + .htm）+ 我们解出来的 `_raw` 文本 |
| `teach.py` | 示教器：**记录**操作与当前模型状态 |
| `tool_caller.py` | ★ 按 `ToolSpec` 契约调一个工具（★ 给 B2 的灵敏度标定与 B3 的存活普查共用） |
| `trigger_analysis_dialogs.py` | ★ 触发用：建件 → 设材料 → 建网格 → **跑求解**（★ 没有夹具/载荷 ⇒ 求解失败 ⇒ 会弹那两级弹窗） |
| `typelib_iids.py` | ★ 从出厂 interop 程序集读**接口 IID**，并对 COM 对象做 QueryInterface |
| `watch_dialogs.py` | ★ **常驻弹窗监视器**：发现弹窗就**主动把内容打印出来**（★ 那就是对 LLM 的"报信"），**不点** |
| `watch_solver_memory.py` | ★ 内存看门狗：仿真求解进程（`cwbcbfmesh.exe`）吃过头就把它斩掉，★ 只报 + 只斩自己那份 |
| `wrap_long_comments.py` | 把超宽**注释行**按显示宽度折行（用 tokenize 精确定位，不碰代码与字符串） |
| `wrap_long_lines.py` | ★ 按**显示宽度**折长行（中文一个字符占 2 列，`len()` 会低估） |
| `wrap_long_strings.py` | 把超宽**单行字符串字面量**按隐式拼接折行（★ 字符串内容一个字节都不变） |

---

## 索引自身的债：无文件头说明的脚本（0 个）

★ 无 —— 每个脚本都有说明。

---

## 相关机制（别重复造）

| 机制 | 位置 | 作用 |
|---|---|---|
| 探针复用门禁 | `scripts/check_probe_reuse.py` | 拦住「为已有工具写了替代品」 |
| 死路台账 | `docs/dead-ends.md` | 已走死的路，动手前先扫 |
| 已知事实 | `docs/known-facts.md` | 已验证的技术事实 |
| 假设台账 | `docs/assumption-ledger.md` | 未验证的假设（不得当证据） |

