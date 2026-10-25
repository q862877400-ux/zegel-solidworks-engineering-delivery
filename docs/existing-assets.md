# 已有资产名单（动手前先看这里）

**业主 2026-10-26 指令**：凡涉及项目已有的东西，**用现成的，不要纯手搓**。

本文件只挂**名单**（模块 · 一句话用途 · 先看哪几个名字），正文留在各模块的 docstring 里。
新增既有能力时在对应分组补一行；**不要**把正文复制进来。

## 一、元素与类型命名（最容易重复造的一块）

同一个元素**只许有一个名字**。下列表已存在，取值含义以官方枚举为准：

| 模块 | 用途 | 先看这些名字 |
|---|---|---|
| [`sketch_relations.py`](../scripts/sketch_relations.py) | 草图关系与**关系涉及的元素类型**（官方 swSketchRelationEntityTypes_e 映射） | `SKETCH_RELATION_ENTITY_TYPES · SKETCH_CONSTRAINT_TYPES · list_relations` |
| [`sw_selection_spec.py`](../scripts/sw_selection_spec.py) | 非草图元素类型名 + 按索引取几何 | `ENTITY_KINDS · entity_geometry · entities_on_body` |
| [`sw_enums.py`](../scripts/sw_enums.py) | 官方枚举常量（**由 tools/gen_sw_enums.py 生成，勿手改**） | `CONSTRAINT_TYPE · MATE_TYPE · SEGMENT_KIND · SKETCH_POINT_TYPE · DOC_KIND` |
| [`sw_sketch_status.py`](../scripts/sw_sketch_status.py) | 草图**定义状态**（完整 7 个值，含过定义/无解） | `CONSTRAINED_STATUS · status_meaning · get_constrained_status` |
| [`sw_units.py`](../scripts/sw_units.py) | 单位：文档单位读取 + **按量纲分派的取值器** | `dimension_reading · m_to_mm · rad_to_deg · read_units_report` |
| [`sw_entity_reference.py`](../scripts/sw_entity_reference.py) | 实体引用的**语义化与解析**（几何签名、按元数据建引用） | `geometry_signature · reference_from_metadata · resolve_semantic_reference` |

## 二、选择与几何

| 模块 | 用途 | 先看这些名字 |
|---|---|---|
| [`sw_selection.py`](../scripts/sw_selection.py) | 选择集：取当前选中的对象/面/组件、按类型筛选 | `get_selected_object · get_selected_face · get_selected_component · SELECTION_ALL_KINDS` |
| [`sw_geometry_selectors.py`](../scripts/sw_geometry_selectors.py) | 点/方向选择器（按名字解析某个点或方向） | `POINT_SELECTORS · DIRECTION_SELECTORS · resolve_point · resolve_direction` |
| [`sw_jlcfa_select.py`](../scripts/sw_jlcfa_select.py) | 界面控件级选择（下拉框/滚动/截图比对）—— 走 UI 时用 | `pick_first · wait_until_changed · scroll` |

## 三、草图

| 模块 | 用途 | 先看这些名字 |
|---|---|---|
| [`sw_sketch.py`](../scripts/sw_sketch.py) | 草图**几何读取**（按类型：直线/弧/椭圆/样条/多段线） | `get_sketch_segments · get_lines · get_arcs · get_ellipses · get_splines` |
| [`sw_sketch_primitives.py`](../scripts/sw_sketch_primitives.py) | 画草图图元（矩形/弧/椭圆弧/槽…） | `sketch_3point_corner_rectangle · sketch_tangent_arc · sketch_elliptical_arc` |
| [`sw_sketch_dimensions.py`](../scripts/sw_sketch_dimensions.py) | 标注尺寸与**完全定义** | `add_horizontal_dimension · add_vertical_dimension · fully_define_sketch · count_sketch_dimensions` |
| [`sw_sketch_relations.py`](../scripts/sw_sketch_relations.py) | 批量加草图关系 | `apply_sketch_relations · FULLY_DEFINED` |
| [`sw_sketch_edit.py`](../scripts/sw_sketch_edit.py) | 草图编辑（倒角/镜像/**转换实体**） | `create_sketch_chamfer · sketch_mirror · convert_entities` |
| [`sw_sketch_edit_ops.py`](../scripts/sw_sketch_edit_ops.py) | 草图裁剪/延伸/等距 | `sketch_trim · sketch_extend · select_sketch_segment` |

## 四、特征

| 模块 | 用途 | 先看这些名字 |
|---|---|---|
| [`sw_sketch_modify_ops.py`](../scripts/sw_sketch_modify_ops.py) | 草图整体变换（移动/旋转/缩放/拉伸/翻转） | `sketch_move · sketch_rotate · sketch_scale · sketch_stretch` |
| [`sw_feature_readback.py`](../scripts/sw_feature_readback.py) | 特征**回读**（参数/深度/存在性/包围盒）—— 读特征先看这里 | `feature_readback · extrude_params · hole_params · pattern_params · fillet_params · feature_present` |
| [`sw_part.py`](../scripts/sw_part.py) | 零件级操作与草图起止 | `start_sketch · end_sketch · PLANE_NAME_ALIASES` |
| [`sw_hole_features.py`](../scripts/sw_hole_features.py) | 孔特征（盲孔/通孔/沉头/沉孔/槽/阵列/紧固件表） | `create_blind_hole · create_counterbore_hole · list_fastener_types` |
| [`sw_surface_features.py`](../scripts/sw_surface_features.py) | 曲面特征 | `create_extruded_surface_report · knit_surfaces_report` |

## 五、装配

| 模块 | 用途 | 先看这些名字 |
|---|---|---|
| [`sw_sheet_metal.py`](../scripts/sw_sheet_metal.py) | 钣金特征 | `SW_FM_BASE_FLANGE · SW_BEND_ALLOWANCE_K_FACTOR` |
| [`sw_assembly.py`](../scripts/sw_assembly.py) | 装配：加组件 / **配合常量** / 配合错误码 | `SW_MATE_COINCIDENT · SW_MATE_DISTANCE · SW_MATE_PARALLEL · add_component` |

## 六、图样

| 模块 | 用途 | 先看这些名字 |
|---|---|---|
| [`sw_assembly_doc.py`](../scripts/sw_assembly_doc.py) | 装配体文档级操作（配合/抑制/移动/固定/解散） | `add_mate · suppress_mate · move_component · collect_assembly_doc_evidence` |
| [`sw_drawing_expose.py`](../scripts/sw_drawing_expose.py) | 工程图视图与标注 | `create_three_standard_views · create_section_view · add_drawing_note` |

## 七、连接与基础

| 模块 | 用途 | 先看这些名字 |
|---|---|---|
| [`sw_drawing_create_missing.py`](../scripts/sw_drawing_create_missing.py) | 工程图细节（断裂线/引线等常量与创建） | `SW_BREAK_LINE_* · SW_LEADER_NO_LEADER` |
| [`sw_connect.py`](../scripts/sw_connect.py) | COM 连接与**统一取值器**（读写钩子、成员读取、类型映射） | `get_com_member · set_com_write_hook · DOC_TYPE_MAP` |

## 八、硬门禁（`scripts/check_*.py`，共 63 个）

写新代码前先看有没有门禁管这块——被门禁盯着的形状**不要绕过**。

```
  check_arity_tables_vs_reflection.py             check_assembly_doc_call_shape.py                check_assumption_ledger.py                      check_backend_limited_completeness.py
  check_backend_limited_evidence.py               check_cd_host_scope.py                          check_corpus_shape.py                           check_create_definition_site_disposition.py
  check_diff_markers.py                           check_digest_freshness.py                       check_dimension_units.py                        check_dispatch_arg_guard.py
  check_dispatch_blindspot_guard.py               check_dispatch_byref_guard.py                   check_dispatch_entry_guard.py                   check_dispatch_forward_arg_guard.py
  check_dispatch_upstream_guard.py                check_docstrings_match_signatures.py            check_enum_values_vs_reflection.py              check_env_pitfalls.py
  check_evidence_freshness.py                     check_fact_provenance.py                        check_fact_single_home.py                       check_gate_wiring.py
  check_interface_member_ownership.py             check_internal_length_units.py                  check_known_facts_triage.py                     check_lean_first_line_caveat.py
  check_length_units_guard.py                     check_license_redlines.py                       check_member_names.py                           check_member_owner_interface.py
  check_negative_input_selfproof.py               check_official_md_claims.py                     check_official_source_defects.py                check_param_binding.py
  check_preselect_family.py                       check_probe_reuse.py                            check_property_form_members.py                  check_provenance.py
  check_python_syntax.py                          check_refuted_patterns.py                       check_relative_imports.py                       check_repo_uniformity.py
  check_report_criteria_alignment.py              check_report_freshness.py                       check_repro_manifest.py                         check_review_ids.py
  check_s3_blockers.py                            check_signature_audit_freshness.py              check_sketch_definition.py                      check_spec_acceptance_paths.py
  check_support_domain.py                         check_survey_cards.py                           check_tools_index_fresh.py                      check_undefined_names.py
  check_union_conventions.py                      check_unit_conversion_count.py                  check_unreachable_members.py                    check_user_decisions.py
  check_user_preference_writes.py                 check_verified_evidence.py                      check_workspace_shadowing.py
```

## 九、生成器（`tools/gen_*.py`）

| 生成器 | 产出 |
|---|---|
| [`gen_sw_enums.py`](../tools/gen_sw_enums.py) | `scripts/sw_enums.py`（官方枚举常量，`--check` 供门禁） |
| [`gen_api_map.py`](../tools/gen_api_map.py) | 见该文件 docstring |
| [`gen_com_member_index.py`](../tools/gen_com_member_index.py) | 见该文件 docstring |
| [`gen_dead_ends.py`](../tools/gen_dead_ends.py) | 见该文件 docstring |
| [`gen_dsh_sw_preset.py`](../tools/gen_dsh_sw_preset.py) | 见该文件 docstring |
| [`gen_effect_declarations.py`](../tools/gen_effect_declarations.py) | 见该文件 docstring |
| [`gen_family_coverage.py`](../tools/gen_family_coverage.py) | 见该文件 docstring |
| [`gen_fingerprint_calibration.py`](../tools/gen_fingerprint_calibration.py) | 见该文件 docstring |
| [`gen_goal_evidence.py`](../tools/gen_goal_evidence.py) | 见该文件 docstring |
| [`gen_harvest_digest.py`](../tools/gen_harvest_digest.py) | 见该文件 docstring |
| [`gen_iview_registry.py`](../tools/gen_iview_registry.py) | 见该文件 docstring |
| [`gen_member_kind_index.py`](../tools/gen_member_kind_index.py) | 见该文件 docstring |
| [`gen_member_registry.py`](../tools/gen_member_registry.py) | 见该文件 docstring |
| [`gen_metrics.py`](../tools/gen_metrics.py) | 见该文件 docstring |
| [`gen_observed_effects.py`](../tools/gen_observed_effects.py) | 见该文件 docstring |
| [`gen_precall_patch.py`](../tools/gen_precall_patch.py) | 见该文件 docstring |
| [`gen_spec211_final_table.py`](../tools/gen_spec211_final_table.py) | 见该文件 docstring |
| [`gen_spec211_ledger.py`](../tools/gen_spec211_ledger.py) | 见该文件 docstring |
| [`gen_study_options_registry.py`](../tools/gen_study_options_registry.py) | 见该文件 docstring |
| [`gen_survival_diff.py`](../tools/gen_survival_diff.py) | 见该文件 docstring |
| [`gen_tool_domain_catalogue.py`](../tools/gen_tool_domain_catalogue.py) | 见该文件 docstring |
| [`gen_tools_index.py`](../tools/gen_tools_index.py) | 见该文件 docstring |
| [`gen_usage_guide.py`](../tools/gen_usage_guide.py) | 见该文件 docstring |

## 十、复用纪律（可执行版）

1. **先查名单**：动笔前在本文件里搜一次要做的事（元素名 / 状态 / 单位 / 几何 / 特征参数）。
2. **有就复用**：直接 `from <模块> import <名字>`，不要复制一份表或重写一遍循环。
3. **要扩展**：加在**原模块**里，别在新文件里另立一套同义名。
4. **确实没有**：先查 `docs/dead-ends.md` 与 `docs/known-facts.md`，再动手；动手后在名单里补一行。
5. **两张表必须同值**：既有表与生成表之间加**一致性测试**（用显式同义词映射，不用模糊匹配）。

