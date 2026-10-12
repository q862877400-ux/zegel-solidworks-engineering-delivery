# `capabilities.yaml` · `evidence` 回读核查（规格 203 · B1）

> **这份文件回答一个问题**：`capabilities.yaml` 里写 `level: verified` 的条目，
> **它自己点名的证据到底在不在、证据自己有没有说它失败**。
>
> **为什么值得做**：仓库**自己已经承认过一次**这类缺陷 —— 有一个条目**唯一真机证据顶层写着
> `verdict: fail`、`passed: 9 / total: 12`，而 `level` 仍写 `verified`**（后已降级）。
> **但那是手工撞见的。** 本文件是**穷举**核查。
>
> **来源与口径**
> - **条目侧**：`D:\AI\SW\capabilities.yaml`（`yaml.safe_load` 解析）——
>   顶层键 `schema_version` / `verified_versions` / `backend_schema_version` /
>   `backend_catalog` / `operation_routes` / `capabilities`。
> - **抄录与核查**：**Bunny（`opencode-zen` / `space-bunny-free`）一路一个条目**，
>   每路**只读那一条 + 它 evidence 点名的文件**，按固定 schema 写一份 JSON。
>   两波 **60 + 50 路**（实测零失败）。
> - **Lead 复核（第二道闸）**：① 每条 `path` 的**存在性**由 Lead **独立重查**；
>   ② 每个 `.json` 证据的**顶层 `verdict`/`passed`/`total`** 由 Lead **独立打开重读**，
>   与 agent 的读数比对，不符即列出（见第三节）。
>
> ⚠ **本文件不含任何行号**；每条结论都给**文件名 + 可 `grep` 的原文片段**。

## 一、统计

| 指标 | 数 |
|---|---|
| `capabilities.yaml` 里的条目 | **110** |
| —— `level: verified` | 97 |
| —— `level: stitched` | 11 |
| —— `level: not_implemented` | 2 |
| `evidence` **条数** | **314** |
| —— `pytest_file` | 44 |
| —— `py_script` | 72 |
| —— `json_artifact` | 96 |
| —— `prose`（**不是路径**，是叙述/更正记录） | 98 |
| —— `other` | 3 |
| 证据**可达性**：`all` | 69 |
| —— `some` | 37 |
| —— `none` | 4 |
| `level_supported`：`yes` | 64 |
| —— `no`（**证据自称失败**） | **42** |
| —— `cannot_tell` | 4 |
| ★ **`level=verified` 而证据自称失败（矛盾）** | **34** |
| 路径**不存在**的 evidence | **1** |

交叉验算：64 + 42 + 4 = 110 = 条目总数。

## 二、★ 矛盾清单：`level: verified` 而证据自称失败（**34 条**）

> ★ **判定权在主线**：本表只报「**证据自己写了什么**」，**不**建议改 `level`。
> 「证据自称失败」= JSON 顶层 `verdict` 是 `fail`/`False`/`partial*`，或 `passed < total`，
> 或脚本/文档自述阴性结果。

| # | 条目 id | 证据（可 grep 的原文片段） | 证据自己写的 | 备注（agent 查到的） |
|---|---|---|---|---|
| 1 | `costing` | （见备注） | 见备注 | 唯一 evidence 自述 verdict=partial 非 pass，passed 5/of 6，点名 list_templates 未过；产物 costing-evidence.json 实读亦为 partial/5/6，而 level 标 verified。 |
| 2 | `costing_readback` | `output/costing-evidence.json` | verdict=partial · passed=5 / total=查不到 | evidence[0] 逐字写「**5/6**」；其 output/costing-evidence.json 顶层 verdict=partial、passed=5/of=6，list_templates 步 ok=false |
| 3 | `curve_and_split` | （见备注） | 见备注 | 第1条自述「★ 2026-10-03（轮 481）**真机 2/4**」——4 项目标仅成2（其引的json顶层 passed=2/total=4）；第7、8条又记「缺任一个都不成」「特征建出来而一个面也切不开」的阴性结果。 |
| 4 | `drawing_view_operations` | `output/drawing-view-evidence.json` | verdict=partial · passed=2 / total=查不到 | 第2条 output/drawing-view-evidence.json：顶层 verdict=partial、passed=2(of=3)，set_scale ok=false；第1条亦记 set_verified.ok=false。 |
| 4 | `drawing_view_operations` | `output/drawing-query-evidence.json` | verdict=pass · passed=查不到 / total=查不到 | 第2条 output/drawing-view-evidence.json：顶层 verdict=partial、passed=2(of=3)，set_scale ok=false；第1条亦记 set_verified.ok=false。 |
| 5 | `export_delivery` | （见备注） | 见备注 | 第6条 probe_export_magic_matrix.py 原文：9/10 名实相符…「pdf 在零件上失败：AttributeError <unknown>.GetSldWorksObject」；第7条称已修好。 |
| 6 | `feature_cosmetic_thread` | `output/cosmetic-thread-evidence.json` | verdict=cosmetic_thread_works · passed=1 / total=3 | evidence1 output/cosmetic-thread-evidence.json：顶层 passed=1/total=3；cases 里 pick=face、pick=none 两格 ok=false。 |
| 7 | `feature_hole_wizard5` | `output/hole-wizard5-build-evidence.json` | verdict=hole_wizard5_1_of_5 · passed=1 / total=5 | 两条可达JSON顶层passed<total：hole-wizard5-build-evidence.json(1/5)、hole-wizard-wrapper-evidence.json(1/2)。 |
| 7 | `feature_hole_wizard5` | `output/hole-wizard-wrapper-evidence.json` | verdict=wrapper_1_of_2 · passed=1 / total=2 | 两条可达JSON顶层passed<total：hole-wizard5-build-evidence.json(1/5)、hole-wizard-wrapper-evidence.json(1/2)。 |
| 8 | `gtol_insert` | （见备注） | 见备注 | 第1条证据脚本产物 output/gtol-smoke-evidence.json 顶层 verdict=fail、passed 3<total 5（两项 add_gtol_indicator 失败；limitations 声明不含该半） |
| 9 | `loft_and_sweep` | `output/sweep-evidence.json` | verdict=partial · passed=2 / total=查不到 | evidence[0]→output/sweep-evidence.json：顶层 verdict=partial、passed=2 of=3，其 circle_path2 ok=false；yaml 原文只写「扫描建成 扫描1」。 |
| 9 | `loft_and_sweep` | `output/loft-evidence.json` | verdict=pass · passed=3 / total=查不到 | evidence[0]→output/sweep-evidence.json：顶层 verdict=partial、passed=2 of=3，其 circle_path2 ok=false；yaml 原文只写「扫描建成 扫描1」。 |
| 10 | `modeling_feature_readback_tools` | （见备注） | 见备注 | evidence[2] tools/verify_composite_curve_smoke.py 原文自述 7/8 · verdict: fail，且写明「前置成立 ⇒ 这是真失败」—— 可达证据自称失败，level 却标 verified。 |
| 11 | `part_and_features` | `output/dimension-edge-pairs-evidence.json` | verdict=pass · passed=查不到 / total=查不到 | 第20条引 output/revolve-axis-fixed-evidence.json 顶层 verdict=partial（passed=1 of=2）；第18条称阴性：InsertCompositeCurve 返回 False。 |
| 11 | `part_and_features` | `output/undo-evidence.json` | verdict=pass · passed=查不到 / total=查不到 | 第20条引 output/revolve-axis-fixed-evidence.json 顶层 verdict=partial（passed=1 of=2）；第18条称阴性：InsertCompositeCurve 返回 False。 |
| 11 | `part_and_features` | `tests/test_cad_reliability.py` | verdict=不适用 · passed=不适用 / total=不适用 | 第20条引 output/revolve-axis-fixed-evidence.json 顶层 verdict=partial（passed=1 of=2）；第18条称阴性：InsertCompositeCurve 返回 False。 |
| 11 | `part_and_features` | `output/bbox-smoke-evidence.json` | verdict=pass · passed=8 / total=8 | 第20条引 output/revolve-axis-fixed-evidence.json 顶层 verdict=partial（passed=1 of=2）；第18条称阴性：InsertCompositeCurve 返回 False。 |
| 11 | `part_and_features` | `output/ellipse-smoke-evidence.json` | verdict=pass · passed=11 / total=11 | 第20条引 output/revolve-axis-fixed-evidence.json 顶层 verdict=partial（passed=1 of=2）；第18条称阴性：InsertCompositeCurve 返回 False。 |
| 11 | `part_and_features` | `output/centerline-smoke-evidence.json` | verdict=pass · passed=8 / total=8 | 第20条引 output/revolve-axis-fixed-evidence.json 顶层 verdict=partial（passed=1 of=2）；第18条称阴性：InsertCompositeCurve 返回 False。 |
| 11 | `part_and_features` | `tools/probe_getlines_count.py` | verdict=不适用 · passed=不适用 / total=不适用 | 第20条引 output/revolve-axis-fixed-evidence.json 顶层 verdict=partial（passed=1 of=2）；第18条称阴性：InsertCompositeCurve 返回 False。 |
| 11 | `part_and_features` | `tools/probe_sketch_getter_shapes.py` | verdict=不适用 · passed=不适用 / total=不适用 | 第20条引 output/revolve-axis-fixed-evidence.json 顶层 verdict=partial（passed=1 of=2）；第18条称阴性：InsertCompositeCurve 返回 False。 |
| 11 | `part_and_features` | `tools/probe_slot_and_point_shapes.py` | verdict=不适用 · passed=不适用 / total=不适用 | 第20条引 output/revolve-axis-fixed-evidence.json 顶层 verdict=partial（passed=1 of=2）；第18条称阴性：InsertCompositeCurve 返回 False。 |
| 11 | `part_and_features` | `tools/verify_dome_smoke.py` | verdict=不适用 · passed=不适用 / total=不适用 | 第20条引 output/revolve-axis-fixed-evidence.json 顶层 verdict=partial（passed=1 of=2）；第18条称阴性：InsertCompositeCurve 返回 False。 |
| 11 | `part_and_features` | `tools/audit_get_com_member_semantics.py` | verdict=不适用 · passed=不适用 / total=不适用 | 第20条引 output/revolve-axis-fixed-evidence.json 顶层 verdict=partial（passed=1 of=2）；第18条称阴性：InsertCompositeCurve 返回 False。 |
| 11 | `part_and_features` | `tools/probe_window_vs_graphics.py` | verdict=不适用 · passed=不适用 / total=不适用 | 第20条引 output/revolve-axis-fixed-evidence.json 顶层 verdict=partial（passed=1 of=2）；第18条称阴性：InsertCompositeCurve 返回 False。 |
| 11 | `part_and_features` | `tests/test_modal_dialogs_can_fire.py` | verdict=不适用 · passed=不适用 / total=不适用 | 第20条引 output/revolve-axis-fixed-evidence.json 顶层 verdict=partial（passed=1 of=2）；第18条称阴性：InsertCompositeCurve 返回 False。 |
| 11 | `part_and_features` | `tools/verify_composite_curve_smoke.py` | verdict=不适用 · passed=不适用 / total=不适用 | 第20条引 output/revolve-axis-fixed-evidence.json 顶层 verdict=partial（passed=1 of=2）；第18条称阴性：InsertCompositeCurve 返回 False。 |
| 11 | `part_and_features` | `tools/probe_add_relation_forms.py` | verdict=不适用 · passed=不适用 / total=不适用 | 第20条引 output/revolve-axis-fixed-evidence.json 顶层 verdict=partial（passed=1 of=2）；第18条称阴性：InsertCompositeCurve 返回 False。 |
| 11 | `part_and_features` | `output/revolve-axis-evidence.json` | verdict=pass · passed=4 / total=查不到 | 第20条引 output/revolve-axis-fixed-evidence.json 顶层 verdict=partial（passed=1 of=2）；第18条称阴性：InsertCompositeCurve 返回 False。 |
| 11 | `part_and_features` | `output/wrap-evidence.json` | verdict=pass · passed=3 / total=查不到 | 第20条引 output/revolve-axis-fixed-evidence.json 顶层 verdict=partial（passed=1 of=2）；第18条称阴性：InsertCompositeCurve 返回 False。 |
| 11 | `part_and_features` | `output/sensor-evidence.json` | verdict=pass · passed=3 / total=查不到 | 第20条引 output/revolve-axis-fixed-evidence.json 顶层 verdict=partial（passed=1 of=2）；第18条称阴性：InsertCompositeCurve 返回 False。 |
| 11 | `part_and_features` | `output/units-evidence.json` | verdict=pass · passed=4 / total=查不到 | 第20条引 output/revolve-axis-fixed-evidence.json 顶层 verdict=partial（passed=1 of=2）；第18条称阴性：InsertCompositeCurve 返回 False。 |
| 12 | `replace_face` | `output/planar-replace-variants-evidence.json` | verdict=查不到 · passed=2 / total=3 | output/planar-replace-variants-evidence.json 顶层 passed=2/total=3（无 verdict）；cases[1]「变体A」ok=false、new_features 空 |
| 13 | `sheet_metal` | `tests/test_sw_sheet_metal.py` | verdict=不适用（非 .json） · passed=不适用（非 .json） / total=不适用（非 .json） | 第3条 evidence 自述前两条 pytest「都不构成我们自己的运行证据」、第2条 no tests ran(exit 1)；第1条自述不碰 COM；第4条自述开放折线实测失败 —— 而 level 仍为 verified。 |
| 13 | `sheet_metal` | `tests/solidworks_sheet_metal_regression.py` | verdict=不适用（非 .json） · passed=不适用（非 .json） / total=不适用（非 .json） | 第3条 evidence 自述前两条 pytest「都不构成我们自己的运行证据」、第2条 no tests ran(exit 1)；第1条自述不碰 COM；第4条自述开放折线实测失败 —— 而 level 仍为 verified。 |
| 14 | `simulation_load_family_breadth` | `output/rigid-twobody-evidence.json` | verdict=pass · passed=查不到 / total=查不到 | 第5条(轮402)所引 output/loads-simple6-evidence.json 顶层 verdict=partial，6条里5条 ok=false 计数不涨；第3、4条原文亦自称 remote_load/temperature「仍不注册」。 |
| 14 | `simulation_load_family_breadth` | `output/thermal-loads-evidence.json` | verdict=pass · passed=查不到 / total=查不到 | 第5条(轮402)所引 output/loads-simple6-evidence.json 顶层 verdict=partial，6条里5条 ok=false 计数不涨；第3、4条原文亦自称 remote_load/temperature「仍不注册」。 |
| 14 | `simulation_load_family_breadth` | `output/loads-groupa3-evidence.json` | verdict=pass · passed=查不到 / total=查不到 | 第5条(轮402)所引 output/loads-simple6-evidence.json 顶层 verdict=partial，6条里5条 ok=false 计数不涨；第3、4条原文亦自称 remote_load/temperature「仍不注册」。 |
| 14 | `simulation_load_family_breadth` | `output/thermal-loads-evidence.json` | verdict=pass · passed=查不到 / total=查不到 | 第5条(轮402)所引 output/loads-simple6-evidence.json 顶层 verdict=partial，6条里5条 ok=false 计数不涨；第3、4条原文亦自称 remote_load/temperature「仍不注册」。 |
| 14 | `simulation_load_family_breadth` | `output/loads-simple6-evidence.json` | verdict=partial · passed=查不到 / total=查不到 | 第5条(轮402)所引 output/loads-simple6-evidence.json 顶层 verdict=partial，6条里5条 ok=false 计数不涨；第3、4条原文亦自称 remote_load/temperature「仍不注册」。 |
| 14 | `simulation_load_family_breadth` | `output/loadfamily-evidence.json` | verdict=pass · passed=查不到 / total=查不到 | 第5条(轮402)所引 output/loads-simple6-evidence.json 顶层 verdict=partial，6条里5条 ok=false 计数不涨；第3、4条原文亦自称 remote_load/temperature「仍不注册」。 |
| 15 | `simulation_solver_options` | `output/batch36-evidence.json` | verdict=pass · passed=6 / total=查不到 | evidence[4]（第5条）自述 output/batch37-evidence.json 顶层 verdict=partial、passed=1/of=4、三步 ok=False；同文称那三步属另一些选项、不属本条。 |
| 15 | `simulation_solver_options` | `output/batch37-evidence.json` | verdict=partial · passed=1 / total=查不到 | evidence[4]（第5条）自述 output/batch37-evidence.json 顶层 verdict=partial、passed=1/of=4、三步 ok=False；同文称那三步属另一些选项、不属本条。 |
| 16 | `sketch_dimension_horizontal` | `output/hv-dimension-with-selection-evidence.json` | verdict=hv_dimension_works · passed=2 / total=3 | 第1条：output/hv-dimension-with-selection-evidence.json 顶层 passed=2 < total=3；未过的是 cases[2] 对照不选，ok:false。 |
| 17 | `sketch_dimension_vertical` | `output/hv-dimension-with-selection-evidence.json` | verdict=hv_dimension_works · passed=2 / total=3 | evidence[0] 的 JSON 顶层 verdict="hv_dimension_works"，但 passed=2 < total=3 —— 第 3 格「对照：不选」ok=false、dim_after_h/v=0 |
| 18 | `sketch_edit_ops` | （见备注） | 见备注 | E0（tools/verify_sketch_edit_smoke.py，文件在盘上）自报「**8/10** —— 选中前置成立，但倒角报错」，该脚本判据本就含「倒角后线段数应变化」⇒ 证据自称阴性，而 level 标 verified。 |
| 19 | `sketch_edit_ops_b3` | `output/b3-sketch-edit-evidence.json` | verdict=partial · passed=查不到 / total=7 | 唯一证据 output/b3-sketch-edit-evidence.json 顶层 verdict=partial（total=7）；items 第7项「交叉曲线」verdict=不能、built=false，而 yaml 该条 level=verified。 |
| 20 | `sketch_equation_curve` | `output/equation-driven-curve-evidence.json` | verdict=equation_curve_1_of_3 · passed=1 / total=3 | evidence[0] 指向的 JSON 产物顶层 passed=1 < total=3、verdict=equation_curve_1_of_3，而 level=verified。 |
| 21 | `sketch_line2` | `output/createline2-and-createspline-evidence.json` | verdict=partial_1 · passed=1 / total=3 | output/createline2-and-createspline-evidence.json 顶层 verdict=partial_1、passed=1<total=3（CreateSpline 那格 ok=false），而本条 level 仍标 verified。 |
| 22 | `sketch_offset_on_surface` | （见备注） | 见备注 | evidence[0] 所引 offset-on-surface-per-example-evidence.json 实存：顶层 passed=2<total=3、verdict=2_of_3；level 为 verified。 |
| 23 | `sketch_rotate_or_copy_3d` | `output/rotate-or-copy-3d-evidence.json` | verdict=rotate_or_copy_works · passed=1 / total=2 | evidence[0] 指向 output/rotate-or-copy-3d-evidence.json，其顶层 passed=1 < total=2（cases[1].ok=false），自称失败；而 level=verified。 |
| 24 | `sketch_spline` | `output/spline-with-variant-evidence.json` | verdict=spline_variant_works · passed=1 / total=4 | evidence[0] 的 output/spline-with-variant-evidence.json 顶层 passed=1 < total=4（3 格 ok=false），自称部分失败，level 却 verified。 |
| 25 | `sketch_spline3_2d` | `output/createspline3-evidence.json` | verdict=spline3_2d_True_on_surface_False · passed=1 / total=3 | 第1条 output/createspline3-evidence.json 顶层passed=1<total=3、verdict='spline3_2d_True_on_surface_False'；yaml level=verified |
| 26 | `surface_features` | `output/fill-surface-evidence.json` | verdict=pass · passed=查不到 / total=查不到 | 第4条 output/surface-feature-evidence.json 顶层 verdict=partial、passed=2（of=3）、through.ok=false；原文写「through_all=True 未通过」。 |
| 26 | `surface_features` | `output/extend-surface-evidence.json` | verdict=pass · passed=查不到 / total=查不到 | 第4条 output/surface-feature-evidence.json 顶层 verdict=partial、passed=2（of=3）、through.ok=false；原文写「through_all=True 未通过」。 |
| 26 | `surface_features` | `output/surface-knit-evidence.json` | verdict=pass · passed=2 / total=查不到 | 第4条 output/surface-feature-evidence.json 顶层 verdict=partial、passed=2（of=3）、through.ok=false；原文写「through_all=True 未通过」。 |
| 26 | `surface_features` | `output/surface-feature-evidence.json` | verdict=partial · passed=2 / total=查不到 | 第4条 output/surface-feature-evidence.json 顶层 verdict=partial、passed=2（of=3）、through.ok=false；原文写「through_all=True 未通过」。 |
| 26 | `surface_features` | `output/surface-feature-probe.json` | verdict=pass · passed=查不到 / total=查不到 | 第4条 output/surface-feature-evidence.json 顶层 verdict=partial、passed=2（of=3）、through.ok=false；原文写「through_all=True 未通过」。 |
| 27 | `surface_flatten` | `output/flatten-with-anchor-evidence.json` | verdict=flatten_with_marks_works · passed=2 / total=4 | 证据1的 flatten-with-anchor-evidence.json 顶层 passed=2 < total=4（② ④ 无锚点格不成）；但 verdict 字段是正面结论 |
| 28 | `surface_offset` | `output/surface-oldstyle-three-evidence.json` | verdict=查不到 · passed=2 / total=3 | evidence[0] 的 JSON 顶层 passed=2/total=3（ok=false 的是 T605 平面区域，非本条）；本条的 T606 等距曲面 ok=true。 |
| 29 | `surface_planar_region` | `output/planar-replace-variants-evidence.json` | verdict=查不到 · passed=2 / total=3 | evidence 1 的 output/planar-replace-variants-evidence.json 顶层 passed=2<total=3（失败格「T609 变体A: 实体面=1 曲面面=2」ok:false），而 level 标 verified。 |
| 30 | `surface_ref_ops` | `output/b6b-surface-ref-evidence.json` | verdict=查不到 · passed=1 / total=2 | 第1条 output/b6b-surface-ref-evidence.json：顶层 passed=1<total=2；items[0]旋转曲面 verdict=不能、5组全部新增=[]；仅放样曲面 ok=true |
| 31 | `surface_revolve` | `output/revolve-oldstyle-evidence.json` | verdict=revolve_oldstyle_works · passed=2 / total=3 | output/revolve-oldstyle-evidence.json 顶层 passed=2 < total=3（3 例中「无中心线」那格 ok=false、new=[]），level=verified。 |
| 32 | `surface_untrim` | `output/untrim-matrix-evidence.json` | verdict=untrim_works · passed=1 / total=6 | 第1条 evidence（output/untrim-matrix-evidence.json，2472B）顶层 verdict=untrim_works（非 fail/partial），但 passed=1 < total=6：cases 里 ①②③④⑥ 的 ok 均为 false，只有 ⑤ ok=true；第2条散 … |
| 33 | `topology_constraints_and_controls` | （见备注） | 见备注 | 唯一那条 evidence（py 脚本）原文写「真机：8 项过 7 · set_goal 的 before/after 计数变化是设置真生效的硬证据」——它自己写明 8 项检查只过 7 项（7 < 8），而该条目 level 仍为 verified。 |
| 34 | `topology_readback` | （见备注） | 见备注 | evidence[1]（可达 py_script）自述「真机：读回部分通过；★ run 未通过」；evidence[0] 自述 7/8 通过、set_iteration_options 报错；level=verified。 |

## 二·一、★ 这 34 条的**读法**（**必须看清，否则会夸大**）

「证据自称失败」在本轮里混着**两种形态**，处置**不同**：

| 形态 | 长什么样 | 为什么不能一刀切 |
|---|---|---|
| **① 白纸黑字的失败** | JSON 顶层 `verdict` 是 `fail` / `False`；或脚本/文档**自述阴性结果**（「返回 False」「静默空操作，段数 0」） | 这一类**没有任何解释空间** |
| **② 部分通过**（`passed < total`） | 例：`replace_face` = `passed 2 / total 3`、`costing` = `5 / 6`、`surface_untrim` = `1 / 6` | ★ **要看该能力自己的前置判据**。仓库**自己写过**这条规矩：`docs/acceptance-status.md` 里「**判据已改成「前提成立才要求 True」**」⇒ 未通过的那几条**可能是前置不成立的应然失败** ⇒ 那就**不构成矛盾** |

⇒ ★★ **所以本节的 34 条是「按最严格口径（只要 `passed < total` 就算）」的候选**，
**不是**「34 条已坐实的错误标注」。
**哪一条属于①、哪一条属于②、②里哪些有正当前置理由 —— 由主线逐条判**（这需要看能力自己的判据）。

### 逐条形态标注

| # | 条目 id | 形态 | 依据 |
|---|---|---|---|
| 1 | `costing` | ② 部分通过 | 查不到 |
| 2 | `costing_readback` | ② 部分通过 | 查不到 |
| 3 | `curve_and_split` | ① 白纸黑字 | （散文/脚本自述）阴性对照：缺任一mark都不成（M3/M4/S6/S7） |
| 4 | `drawing_view_operations` | ② 部分通过 | 查不到 |
| 5 | `export_delivery` | ① 白纸黑字 | （散文/脚本自述）文件在盘（7779 字节）；条目自述 9/10，pdf 一项失败 |
| 6 | `feature_cosmetic_thread` | ① 白纸黑字 | （散文/脚本自述）散文：对照三格——选边成功、选面/不选失败，定前置；（散文/脚本自述）散文：更正记录——失败在探测脚本瞂猜圆柱面，换 IsCylinder() 即成 |
| 7 | `feature_hole_wizard5` | ② 部分通过 | output/hole-wizard5-build-evidence.json（1/5）；output/hole-wizard-wrapper-evidence.json（1/2） |
| 8 | `gtol_insert` | ② 部分通过 | 查不到 |
| 9 | `loft_and_sweep` | ② 部分通过 | 查不到 |
| 10 | `modeling_feature_readback_tools` | ① 白纸黑字 | （散文/脚本自述）脚本在盘上 13689 字节；原文自述 7/8 · verdict: fail 判真失败 |
| 11 | `part_and_features` | ① 白纸黑字 | （散文/脚本自述）更正记录：称实跑 12 对、成 8、失败 4（自述已复核 JSON）；（散文/脚本自述）三个脚本均在；自述 sketch_spline 静默空操作（阴性） |
| 12 | `replace_face` | ② 部分通过 | output/planar-replace-variants-evidence.json（2/3） |
| 13 | `sheet_metal` | ① 白纸黑字 | （散文/脚本自述）散文：引 sw_sheet_metal.py 闭轮廓真机建成，自述开放折线失败 |
| 14 | `simulation_load_family_breadth` | ② 部分通过 | 查不到 |
| 15 | `simulation_solver_options` | ② 部分通过 | 查不到 |
| 16 | `sketch_dimension_horizontal` | ② 部分通过 | output/hv-dimension-with-selection-evidence.json（2/3） |
| 17 | `sketch_dimension_vertical` | ② 部分通过 | output/hv-dimension-with-selection-evidence.json（2/3） |
| 18 | `sketch_edit_ops` | ② 部分通过 | 查不到 |
| 19 | `sketch_edit_ops_b3` | ② 部分通过 | 查不到 |
| 20 | `sketch_equation_curve` | ② 部分通过 | output/equation-driven-curve-evidence.json（1/3） |
| 21 | `sketch_line2` | ② 部分通过 | output/createline2-and-createspline-evidence.json（1/3） |
| 22 | `sketch_offset_on_surface` | ② 部分通过 | 查不到 |
| 23 | `sketch_rotate_or_copy_3d` | ① 白纸黑字 | （散文/脚本自述）纯叙述：Copy=False 时段 1→1、也回 True |
| 24 | `sketch_spline` | ② 部分通过 | output/spline-with-variant-evidence.json（1/4） |
| 25 | `sketch_spline3_2d` | ② 部分通过 | output/createspline3-evidence.json（1/3） |
| 26 | `surface_features` | ② 部分通过 | 查不到 |
| 27 | `surface_flatten` | ② 部分通过 | output/flatten-with-anchor-evidence.json（2/4） |
| 28 | `surface_offset` | ② 部分通过 | output/surface-oldstyle-three-evidence.json（2/3） |
| 29 | `surface_planar_region` | ① 白纸黑字 | （散文/脚本自述）轮516选曲面体边→False/0增量；轮517改选闭合草图→True并建成 |
| 30 | `surface_ref_ops` | ② 部分通过 | output/b6b-surface-ref-evidence.json（1/2） |
| 31 | `surface_revolve` | ② 部分通过 | output/revolve-oldstyle-evidence.json（2/3） |
| 32 | `surface_untrim` | ② 部分通过 | output/untrim-matrix-evidence.json（1/6） |
| 33 | `topology_constraints_and_controls` | ① 白纸黑字 | （散文/脚本自述）脚本真实存在；路径是 .py 无顶层 verdict；散文称「8 项过 7」 |
| 34 | `topology_readback` | ② 部分通过 | 查不到 |

## 三、Lead 独立复核：agent 读数与盘上不符的（1 处）

> 我**不看 agent 的结论**，自己把每个 `.json` 证据的顶层字段重读一遍并与它的读数比对。
> ⚠ **本轮我自己错过一次**：第一版复核器用 `is_file()`，把 `pytest tests（全量…）` 里的
> **目录** `tests` 误判成「agent 报错」⇒ 报了 7 处假不符。改成 `exists()`（文件或目录都算）后归零。
> **留档原因**：这是「复核器本身也会错」的实证，主线的门禁同样要防这一层。

| 条目 | 路径 | agent 报的 | 盘上实际 |
|---|---|---|---|
| `preview_and_review_report` | `output/review-tools-evidence.json#total` | 查不到（顶层无 total 键，实际用键 of，值 = 4） | 查不到 |

## 四、路径**不存在**的 evidence（1 条）

> 这是**最硬的一类缺陷**：证据指向的文件/目录在盘上找不到 ⇒ 该证据**不可复算**。

| # | 条目 id | level | 路径 | evidence 原文 |
|---|---|---|---|---|
| 1 | `mesh_size_sanity_gate` | verified | `output/simulation-evidence.json` | ★ **对照证据**：tools/capture_simulation_evidence.py 的 `output/simulation-evidence.json`（sugge |

## 五、`evidence` 里**不是路径**的那些（`kind: prose`，98 条）

> ★ **这是本轮的一个结构性发现**：`evidence` 字段里混着**叙述**（更正记录、推理说明、
> 「本结论只由 12 对样本得出」这类限定）—— 它们**不可机械复算**，但**承载着最重要的限定**。
> 只按「路径存不存在」判 `verified` 会**漏掉这一整类**。

| # | 条目 id | level | 原文片段（可 grep） |
|---|---|---|---|
| 3 | `part_and_features` | verified | ⚠⚠⚠ **2026-10-04（接手轮）更正三处读数 —— 处置 `JUDGE-A_B.md` 的 A-features F1（🔴 立刻要改）** —— ★ 裁判逐字：「★ 条目说「66 对 / 8-8 / 含边 0 都成」，★ 而证据文件记的是 **试了 12 对**、★ 其中 **4 对含边 0 的明确失败**」✓。★★ **我实测复核**（★ 逐字读那份 JSON）：★ `tried: 12` · ★ `edge_count: 12` · ★ successes = … |
| 3 | `part_and_features` | verified | ⇒ ★★ **上一句里那三处要分开看**（★ 不是一句「夸大」就能说完）：<br>① ★ **「66 对」** = ★ **计划数 C(12,2) = 66**，★ 而**实跑 12 对**（★ 到上限就停）⇒ ★ 原文没说清「计划」与「实跑」的区别 ✓<br>② ★★ **「8/8」** = ★ **成功的 8 个**（★ 8 项 `successes`），★ **不是「8 对里 8 个成功」** —— ★ 12 对里成功 8、★ **失败 4** ✓<br>③ ★★★ * … |
| 3 | `part_and_features` | verified | ★★★ **而真正的规律在证据的 `note` 里**（★ 原文逐字：「★ 盒体的 12 条边按 SolidWorks 惯例分组：**0-3 / 4-7 是上下两个面环、8-11 是竖边**」）⇒ ★★ 按分组看那 12 对：<br>· ★ **0↔1/2/3**（同一条面环内）**成** · ★ **0↔4/7**（对面环的对应边）**成** · ★ **0↔8/11**（竖边）**成**<br>· ★★ **0↔5/6**（对面环的**错位**边）**不成** · ★★  … |
| 3 | `part_and_features` | verified | ★ **正确的一句话**：★ **同一面环内的边对、对面环的对应边、以及与竖边的组合能建成尺寸；而对面环上错位的边对不能。**★（★ 本结论只由那 12 对样本支撑，★ 未穷举 66 对 ⇒ ★ 不要外推）✓ |
| 6 | `parameter_updates` | verified | ★ **真机运行证据（★ 2026-10-04 补 —— 这才是 A4 要的那一条）**：`python tools/sw_guard.py --timeout 300 -- python tools/probe_a4_runtime_evidence.py` ⇒ ★ `sw_alive: true` · ★ **零弹窗** · ★ `parameter_updates_ok: **True**`；★ 证据文件 output/a4-runtime-evidence.json … |
| 6 | `parameter_updates` | verified | ⚠★ **同一次真机顺带量到一处可疑（★ 未定性 —— ★ 要另核）**：★ 那次调用的 `before_mm.current` 是 **20000.0**，★ 而该模型那个尺寸的**本意是 20 mm**（★ `extrude_boss(..., 20.0)`）⇒ ★★ **20 → 20000 正好是 ×1000 两次** ⇒ ★★★ **可能是 `_dimension_value_mm` 的单位换算多做了一次**（★ **也可能是我读错了对象** —— ★ 例如那个名字 … |
| 11 | `drawing_dimension_insertion` | not_implemented | ⚠⚠ ★★★★ **2026-10-04（接手轮）如实标注：上面那条**不是运行证据**** —— 处置 `JUDGE-A_B.md` 的 🔴 **A-drawing 一**，★ 裁判逐字：「★ `drawing_dimension_insertion` 的 evidence 唯一相关行是 `assert index[...]["level"] == "verified"` —— ★ **循环自证**，★ 测试文件**自己写「未在本机实测」**」✓ ★★ **我复核了那个文件 … |
| 13 | `export_delivery` | verified | python 真机（轮 403）★ **PASS** —— 24h 计划 v2 段 6（导出）：`solidworks_export_image`（`sw_export.export_image_report`）。真机（走 `sw_guard`，4.0 s 无弹窗）：一张 PNG ⇒ **`exists=true` · `size_bytes=67997` · `grew_or_created=true`**；负例（非法目录）⇒ `ok=false`。★ 判据**复用本模块既 … |
| 19 | `sheet_metal` | verified | 🕓 **2026-10-04（接手轮）更正上两条 —— 它们都不构成「我们自己的运行证据」** （★ 处置 `JUDGE-C_D_E.md` 的 🔴 **#10** · `C-sm-1 V-2 / V-3`）—— ★ 裁判逐字：「★ 两条 evidence 一条**不碰 COM**、一条按字面 pytest **收 0 个用例** ⇒ ★ 直接**违反验收标准 A4**」✓ ★★ **我逐条复核（★ 两条都实跑了）**：<br>· ★ **第 1 条**：★ pytest  … |
| 19 | `sheet_metal` | verified | ★ **真机运行证据（★ 这才是 A4 要的那一条）**：`scripts/sw_sheet_metal.py::SHEET_METAL_RUNTIME_STATUS` 的 `create_base_flange` 项逐字 —— 「★ **闭轮廓**真机建成：特征树出现「钣金6 / 基体-法兰1 / 平展型式6」」· ★ 时间/版本：2026-10-01 · SW 2026 SP4.1 → ★ `sheet_metal_evidence` 项：「★ 真机读回正确：thickn … |
| 20 | `weldments` | verified | python 真机（轮 428）★ **PASS** —— **结构构件**（焊件族第一条）。真机（走 `sw_guard`，无弹窗）：前视基准面上一段 100 mm 直线作路径 + **GB 方管轮廓**（`GB\square-rods.sldlfp`）⇒ **建成 `square-rods (1)`**，★ 判据是**特征树**（不是计数）：`new_type_names` = **["WeldMemberFeat", "WeldmentFeature"]**。证据 ou … |
| 23 | `simulation_and_fea` | verified | ⚠⚠ 2026-10-04（接手轮）**如实补记（铁律 5）**：★ **`output/simulation-evidence.json` 这个产物当前不在仓里**（★ 探针脚本 `tools/capture_simulation_evidence.py` 在）⇒ ★★ 所以这一条与下一条里引用的具体数字（`element_count: 7310` · `suggested_size_mm: 4.933908705960544` · `plot_count: 4`）**回不 … |
| 23 | `simulation_and_fea` | verified | ⚑ 2026-10-01 真机整链（SW 2026 SP4.1 / 34.4.1，100×60×20 mm 单实体板）：赋材料 → 按**面坐标**选面 → 夹具 → 载荷（`Count == 2`）→ `CreateMesh`（**7,310 个单元**）→ `RunAnalysis`（1 秒）→ **`study.Results` 非空、`GetPlotCount == 4`、`GetPlotNames == ('品质1','应力1','位移1','应变1')`**。** … |
| 29 | `topology_optimization` | verified | ⚠⚠ 2026-10-04（接手轮）**如实补记（铁律 5）**：★ **`output/topology-evidence.json` 当前不在仓里**（★ 脚本在、★ `output/` 被 gitignore）⇒ ★★ 本条目里引用的那些读数（`AnalysisType == 13` · `GetPlotCount == 4` 等）**回不到原文**，要复现就**重跑 `tools/capture_topology_evidence.py`** ✓ |
| 35 | `sketch_query` | verified | python 真机（轮 399）★ **PASS** —— 24h 计划 v2 段 3：`solidworks_current_sketch_name`（读当前活动草图名）。真机（走 `sw_guard`）：草图打开时回 **「草图1」**（**真名**，不是 English fallback）；草图**关闭后** + 自定义回退值 ⇒ 回**那个回退值**（★ 验证的是**已文档化的局限**：★ 回退值 ≠ 真名 ⇒ 别拿它去按名取草图）。证据 output/part-re … |
| 37 | `standard_parts_toolbox` | verified | tb.search('bearing') ⇒ **184** 条（检索可用） |
| 40 | `drawing_current_sheet_query` | verified | pytest tests（全量 0 failed，含两个「钉死数量」守卫已同步：all_specs() 65 / 协议层 110） |
| 41 | `file_custom_property_read` | verified | pytest tests（全量 0 failed；两个「钉死数量」守卫已同步：all_specs() 67 / 协议层 112） |
| 50 | `analysis_run_readback` | stitched | ⚠ **无** —— 真机实测 `timed_out=True`（300s 后杀子进程）；★ 该结果已如实记入 `output/mesh-solve-evidence.json` 的 `run_analysis.timed_out` |
| 50 | `analysis_run_readback` | stitched | ★ **反证（有价值）**：同一份证据里 `mesh_size` 与 `create_mesh` **成功** ⇒ ★ 说明失败点**精确定位在「跑求解」**，而不是整条链 |
| 51 | `simulation_load_family_breadth` | verified | python 真机（轮 348/349）★ **两处通用修复（都在能力层 `_check`，一处 ⇒ 整批受益）**：① **末尾 `ByRef ErrorCode` 统一补 `out_i4()`**（★ 缺它 ⇒ `DISP_E_PARAMNOTOPTIONAL`「非选择性的参数」）；② **第 3 参 `RefGeom` 裸传 `None` ⇒ 换成空 Dispatch 参数包**（★ 裸 `None` ⇒ com_error(-2147352571, '类型不匹配', … |
| 51 | `simulation_load_family_breadth` | verified | python 真机（轮 245 的历史发现，本批兑现）★ `RegGeom`/`RefGeom` **不能裸传 `None`** —— ★ 而那时**只修了 `add_torque`，`add_force` 漏了**（★ 本轮补上）。 |
| 52 | `topology_iteration_options_backend_limited` | stitched | ★ **反证（有价值）**：同一份证据里 `set_goal` **成功**（0→1）⇒ ★ 说明**不是「拓扑域整体不行」**，而是**这一个调用**撞后端限制 |
| 53 | `mesh_size_sanity_gate` | verified | ⚠⚠ 2026-10-04（接手轮）**如实补记（铁律 5）**：★ **`output/simulation-evidence.json` 当前不在仓里**（★ 脚本在、★ `output/` 被 gitignore）⇒ ★★ 上面那三个数字**回不到原文**，要复现就**重跑 `tools/capture_simulation_evidence.py`** ✓ |
| 54 | `feature_readback_criterion` | verified | ★ **三轮真机打磨**：① 直接调 `GetWhatsWrong2` ⇒ 取不到；② 改用 `Extension.GetWhatsWrongCount` ⇒ 取到（0 条错）；③ 过滤从「枚举容器名」改成「`GetTypeName2` 非空」（★ 与 UI 语言无关） |
| 57 | `render_materials_and_appearance` | verified | ★ 既有工具（本批**没有**新建工具）：`solidworks_list_render_materials` / `solidworks_collect_appearance_evidence` / `solidworks_refresh_scene_graph` |
| 59 | `declarative_hole_creation` | verified | python 真机（轮 292/293）：入口链 PASS · 有视图的图 · 见 drawing_view_operations 条 |
\| 60 \| `weldment_cut_list` \| verified \| ★★★ 2026-10-03（轮 496-498）**更正上面那条（轮 270）的「create_cut_list 后端限制」定性** —— ★ 它**不是后端限制**：★ 回筛：`GetIDsOfNames("InsertWeldmentCutList2")` ⇒ **`dispid = 174`**（★ **不是 1**）；Invoke(174, 0, DISPATCH_METHOD, True, VARIANT(VT_ARRAY\|VT_DISPATCH, bodie … \|
| 61 | `simulation_solver_options` | verified | python 真机（轮 346）★ **工具层修掉一处一行之差**：`resolve_study` 原先 `next(iter(iter_studies(sw)), None)` **没解包**（★ `iter_studies` 产 `(index, study)` 元组）⇒ 把元组当 study 传下去 ⇒ ★ **所有没声明 `study_name` 的工具全中招**。★ 修后 `study` = **`CDispatch`**，三个配置入口的报错**换了层次**（★ 从 … |
| 61 | `simulation_solver_options` | verified | python 真机（轮 345）★ **建研究的两个真实前置查清**：① 第一参必须是 **`ISldWorks`**（★ 传 `doc` ⇒ `AttributeError: <unknown>.GetAddInObject`）· ② 文档里**必须有实体**（★ 否则 `swsStudyError_e = 1`）⇒ `create_study_report` 真机 `ok=true`。 |
| 61 | `simulation_solver_options` | verified | ★ 上一条里那份 `batch37` 的真实状态**已如实记在这里**（★ 而不是让它沉默）：★ **它是 1/4 partial、★ 三步失败** —— ★ 那三步测的是**另一些求解器选项**（★ `ComputeFrequencyModes` / `ContactPenetrationStiffness`），★ **不属本条**（本条是「9 个族 / 202 个 setter 名」的清单读取），★ 故**不改变本条的 `level`**；★ 但**后续若要攻那两项，★  … |
| 63 | `topology_readback` | verified | python 真机（轮 383）★ **7/8 通过**（`tools/capture_topology_readback_evidence.py`，走 `sw_guard` 护栏，5.3 s 无弹窗）：`bindings` ✓ · `material` = `AISI 1020` ✓ · `create_study` ✓ · `collect_numbers` ✓（`status: no_results`，合理 —— 不跑求解）· `constraints` ✓（9 kin … |
| 65 | `render_material_library` | verified | python 真机（轮 373）★ **真因是 `FileName` 必须绑 `.p2m`** —— 四轮收窄的终点（known-facts 287→290）：`CreateRenderMaterial(name)` 建出的外观**没有绑定材质文件**时，`AddDisplayStateSpecificRenderMaterial` **照样回 true** 且 `GetLinkedDisplayStates` **显示已链接**，而 `GetMaterialIds` 回  … |
| 65 | `render_material_library` | verified | python 真机（轮 367）★ **顺带修掉第 12 处「设属性写成取或调」**：`create_render_material` 的 `spec.extra` 循环原为 `get_com_member(material, key, float(value))`（事实 227）⇒ `TypeError`；已改 `set_com_member`（★ 前人轮 319 修了 11 处，这一处漏了）。 |
| 65 | `render_material_library` | verified | python 真机（轮 371/372）★ **观察点**：`IRenderMaterial.GetLinkedDisplayStates()` 直接回答「外观挂到了哪些显示状态」，★ 不经过「清单」那条可疑中介 ⇒ 用它证明 `Add…` 的**链接**确实生效（而清单仍空）。 |
| 66 | `sheet_metal_creation` | stitched | ★ `create_base_flange` 真机验过（SW 2026 SP4.1 ⇒ 特征树出现钣金特征）· ⚠ 其余三条到不了（known-facts 47/43） |
| 72 | `costing_templates_and_defaults` | verified | python 真机（轮 366）★ **真 bug 修在一行上**：`list_costing_templates_report` 原先把 `d`（`CostingDefaults`）传给 `list_templates`，而 `GetTemplatePathnames` **挂在 `ICostManager` 上**（反射转储 `iface_sldcostingapi.txt` 的 `## ICostManager`：`GetTemplateCount(Int32)` /  … |
| 72 | `costing_templates_and_defaults` | verified | python 真机（轮 366）★ **受控实验定位**：A（只取 defaults）/ B（先取 model 再取 defaults）都通，而工具层入口不通 ⇒ 把嫌疑缩到“工具层内部那一处传参”上。 |
| 73 | `mold_parting_geometry` | stitched | ⚠ **仍无真机证据**：本族 4 个工具需**先选拔模方向参考**，★ 而在**未准备的分型件**上会弹框 ⇒ ★ 前置得由人配合。（★ 2026-10-01 轮 343：已删去旧 evidence 里那句**已过时**的「冒烟 3/5 fail」—— ★ 那是 **`mold_analysis` 的脚本键形状**问题，与本族无关。） |
| 74 | `pattern_and_mirror` | verified | python 真机（轮 317）★ **两半都建成**：镜像 ⇒ **`镜向1`** · type=**`MirrorPattern`**；阵列 ⇒ **`阵列(圆周)1`** · type=**`CirPattern`**（★ 前置 `基准轴1` 由 `IModelDoc2.InsertAxis2` 建） |
| 74 | `pattern_and_mirror` | verified | ★ 关键修正：镜像的 mark **原本是反的**（特征 4→1 · 平面 1→2，★ 官方 `InsertMirrorFeature2.md` 的 Remarks 给了完整 mark 表） |
| 82 | `sketch_modify_ops` | verified | ★ 三源互证（swapi + CHM + 出厂反射，**成员名三方一致**）：`IModelDoc2.SketchModify{Translate,Rotate,Scale,Flip}`、`IModelDocExtension.Stretch`。★ **不用 `Tools*` 族**（`ToolsSketchTranslate()` 零参数、交互式弹框，与无人值守红线冲突）。 |
| 83 | `surface_edit_ops` | verified | ★ 三源互证里**两处“台账给的名字是旧的”**：`InsertRuledSurface` ⇒ 真名在 `IFeatureManager`，且 `…FromEdge` 官方标 **Obsolete**（用 `…FromEdge2`）；`InsertReplaceFace` ⇒ `InsertFeatureReplaceFace`。 |
| 84 | `surface_ref_ops` | verified | ★ 三源互证里**台账给的两个名字都不对**：`FeatureRevolveRefSurface` ⇒ swapi 里**根本没有**（真名 `IFeatureManager.InsertRevolvedRefSurface`）；`InsertProtrusionBlend2(Surface)` ⇒ 真名 **`IModelDoc2.InsertLoftRefSurface2`**。★ 同族 `FeatureExtruRefSurface{,2,3}` 命名不同 ⇒ **不能 … |
| 85 | `ref_geometry` | verified | ★★ **`out` 参数的正确传法**（本轮踩到并修好）：`InsertGlobalBoundingBox2` 的第 5 个形参 `Status` 是 **out**，★ 裸传 `0` 真机回 `com_error: (-2147352571, '类型不匹配。', None, **5**)`（**位置 5 就是它**）；★ 必须用 **`sw_connect.out_i4()`**（其 docstring：「创建 `Int32&` 出参的 VARIANT 包装 —— **唯 … |
| 85 | `ref_geometry` | verified | ★★ **台账 T701 给的成员是错的**：它写 `Create3DBoundingBox`，而官方原话是「for a **cut list item in a weldment part**」⇒ **焊件切割清单专用**，普通零件上不成是**应然的**；★ 工具栏那个的真名是 **`InsertGlobalBoundingBox2`**。 |
| 85 | `ref_geometry` | verified | ★★ 2026-10-03（轮 480）**补齐到 5/5** —— 上一轮那两条（基准面 / 点）**缺的是同一件事**：★ **调用前按 `mark` 选一个参考实体**。★ 真机：基准面 `预选 ok=True {face_index:0, mark:0, sel_count:1}` ⇒ 树新增 **`基准面1`**；点同样 `mark=0` ⇒ 树新增 **`点1`**。★ 而 **mark 表就在官方 Remarks 里**：0 = First reference … |
| 86 | `curve_and_split` | verified | ★ 2026-10-03（轮 481）**真机 2/4**（走 `tools/sw_guard.py`，`sw_alive: true`、**零弹窗**）：`python tools/prove_b7a_curve_split.py`。★ **通过参考点的曲线**：树新增 **`曲线1`**（`InsertCurveFileBegin/Point/End` 三步式）；★ **配合参考**：树新增 **['配合参考', 'MCP_MateRef-<1>', '配合参考___E … |
| 86 | `curve_and_split` | verified | ★★ **`类型不匹配` 位置 6 ⇒ 未用的 entity 槽要传「空 Dispatch」**：`InsertMateReference2` 的 `Secondary/TertiaryReferenceEntity` 类型是 `Entity`，★ 裸传 `None` 不行；★ 用本仓 `sw_connect.create_empty_dispatch_variant()`（★ 它就是**事实 12**那条）。 |
| 86 | `curve_and_split` | verified | ★★ **`无效的参数数目` ⇒ 官方第三组少一个形参**：完整签名是 **12** 个（`… TertiaryReferenceType, TertiaryReferenceAlignment )` |
| 86 | `curve_and_split` | verified | —— **没有 `TertiaryReferenceAlignAxes`**）；★ 我按“三组同形”推成 13 个 ⇒ 报错。★ **别按同形推，要逐数完整签名**。 |
| 86 | `curve_and_split` | verified | ★★★★ **2026-10-03（接手轮）分割线（投影）真机建成**（走 `tools/sw_guard.py`，`sw_alive: true`、**零弹窗**）：`python tools/prove_split_line_geometry_per_example.py` + `tools/prove_split_line_minimal_matrix.py`。★ 判据**三条一起**：树新增 **`分割线1`**（`GetTypeName2` = `PLine`）·  … |
| 86 | `curve_and_split` | verified | ★★★★ **2026-10-03（接手轮）分割线（轮廓）真机建成**：`python tools/prove_split_line_silhouette_marks.py` 的 **S5**：树新增 `分割线1` · **面数 +1** · 圆柱侧面 **2 环 → 两张各 1 环**（`[1,1,2] → [1,1,1,1]`）。证据 output/split-line-silhouette-marks-evidence.json。 |
| 86 | `curve_and_split` | verified | ★★★ **前置（真机单变量对照，★ 两个前件都必要）**：投影型 = **草图 mark 4 + 面 mark 1**；轮廓型 = **方向项 mark 2 + 面 mark 1**。★ 缺任一个都**不成**（M3/M4 · S6）；★ 而轮廓型**只把 mark 2 换成 mark 0**（S7）就不成 ⇒ **官方那个 2 是承重的**。 |
| 86 | `curve_and_split` | verified | ★★★ **几何前提（★ 官方签名与 Remarks 都没写，★ 只有官方例子的调用序给得出，★ 并由真机单变量对照确认）**：★ 投影型要求**投影草图所在面在实体之外**、与目标面平行、沿投影方向隔开；★ 轮廓型要求**视线不能顺着回转轴**（圆柱轴 = +Z 时用前视面不成、换上视面成）。★ 反例：草图被实体夹住时**特征会建出来而一个面也切不开**（`分割线1` 进树、面数 6→6）。 |
| 86 | `curve_and_split` | verified | ★★★ **`InsertSplitLineProject` / `InsertSplitLineSil` 建成时都回 `None`** ⇒ ★ 「回 `None` ⇒ 真的没建」**不成立**（本轮真机证伪了 `docs/known-facts.md` 事实 420 的那条分类判据）。 |
| 87 | `surface_thicken_silent_noop` | stitched | ★★ 2026-10-03（轮 502-504）**真机总账：共 11 组 · 两条入口 · 前置每次完美**——结果**全部 `None`、特征树不动、连错误都不报**：★ 轮 502：`IFeatureManager.FeatureBossThicken`（7 参）**1 组**；★ 轮 503：同上**7 组**（官方开关的主要组合）；★ 轮 504：**`IModelDoc2.FeatureBossThicken`（3 参 · Obsolete）**3 组。★ 而每次 … |
| 87 | `surface_thicken_silent_noop` | stitched | ★ **两个软件侧的事实**：① 官方参数表逐字写 `FaceIndex` ⇒ **「Not used」**（★ 故本包装**不收面索引** —— 收了是骗人）；② 形态与**事实 40**（`IModeler.Create*Surface` 返 `None` 而几何不变）**同族**：★ 「**静默不干活**」，**而不是**「报错说参数不对」。 |
| 88 | `surface_offset` | verified | ★ **走的是「旧式方法」那侧**（`IModelDoc2.InsertOffsetSurface` · **2 参 · void**）—— ★★ 而不是新架构（`CreateDefinition` + `CreateFeature`）。★ 依据：**事实 395** 指出「旧式方法那侧是成的」（填充 `InsertFillSurface2` / 延伸 `InsertExtendSurface` / 缝合 `InsertSewRefSurface` / 曲面-拉伸 Feat … |
| 89 | `surface_planar_region` | verified | ★★★ **而「boundary entities」到底是什么，是真机定的**：★ 轮 516 先试**曲面体的边**（12 条 · mark=1）⇒ **0 增量**、返回值 `False`；★ 轮 517 改试**草图**（闭合轮廓 · mark=1）⇒ **返回 `True` · 建成** ✓ ⇒ ★★ **故它指的是草图**（★ 而官方那句 `Remarks` **两种读法都通**）。 |
| 90 | `replace_face` | verified | ★★★ **两个 mark 的分工是真机定的**（★ 官方那句 `Remarks` **被截断了**）：★ 轮 516 按「实体面=1 · 曲面面=2」⇒ **0 增量**；★ 轮 517 调过来（实体面=2 · 曲面面=1）⇒ **建成 `替换面1`** ✓ ⇒ ★★ **曲面面 = mark 1（要替换掉的）· 实体面 = mark 2（替换成它）**，★ 而它与官方「要替换的面 mark 1」**一致**。 |
| 91 | `surface_revolve` | verified | ★★★ **而根因是一组对照定下的：「无中心线」那组**不成**（树 0 增量）** —— ★ 而官方原话逐字是「by revolving a profile around a **centerline**」。 ⇒ ★★ **故：本仓此前对它的「不成」（轮 501，5 组全试过）真因是**前置缺中心线**，而**不是**架构问题** ✓ ★ 而它**修正了一个归因**：「新架构那侧不成」在**旋转曲面上不成立**。 |
| 92 | `sketch_dimension_horizontal` | verified | ★★★ **而根因是一组对照定下的：「**不选**」那组 `尺寸 0 → H:0 → V:0`（**不成**）** —— ★ 故**前置就是“**必须先选中实体**”**。 |
| 92 | `sketch_dimension_horizontal` | verified | ★★★ **而它顺手推翻了一条旧定性**：这两条此前被记作「**会挂**」（`sw_alive: null`）—— ★ 而真相是它弹了一个「修改」**数值输入框**（★ 事实 421：`hung = false`，控件树 `SLIDER×3 + THUMB WHEEL×3`）。**选中实体后它就不弹了** ✓ |
| 93 | `sketch_dimension_vertical` | verified | ★★★ **而根因是一组对照定下的：「**不选**」那组 `尺寸 0 → H:0 → V:0`（**不成**）** —— ★ 故**前置就是“**必须先选中实体**”**。 |
| 93 | `sketch_dimension_vertical` | verified | ★★★ **而它顺手推翻了一条旧定性**：这两条此前被记作「**会挂**」（`sw_alive: null`）—— ★ 而真相是它弹了一个「修改」**数值输入框**（★ 事实 421：`hung = false`，控件树 `SLIDER×3 + THUMB WHEEL×3`）。**选中实体后它就不弹了** ✓ |
| 94 | `feature_revolve_cut` | verified | ★★ 2026-10-03（轮 550）**真机建成**（走 `sw_guard`，零弹窗）：实体盒 + 前视面上的**中心线 + 剖面**，调 `FeatureRevolve2(..., IsCut=True, ...)` ⇒ **树新增 `切除-旋转1`**，★ **体积 0.8255 倍**（**变小 = 真切除**）。证据 `output/revolve-cut-evidence.json`。 |
| 94 | `feature_revolve_cut` | verified | ★★ **而对照组同时跑**：`IsCut=False` ⇒ 树新增 `旋转1`、★ **体积 1.1745 倍**（**变大）** —— ★ 故**那一个布尔就是“切除”与“加料”的分界** ✓ |
| 95 | `sketch_slot_types` | verified | ★ 对应台账四条（★ 而**它们是同一个方法的四个枚举值**）：直槽口 / 中心点直槽口 / 中心点圆弧槽口 / 三点圆弧槽口。 |
| 96 | `surface_flatten` | verified | ★★★ **而根因是一组**四格对照**定下的**： ① 面(1) + **锚点(16)** ⇒ **成** ✓ ② 面(1) + 引导边(2)（**无锚点**）⇒ **不成** ✗ ③ 面(1) + 锚点(16) + 引导边(2) ⇒ **成** ✓ ④ **只给面(1)** ⇒ **不成** ✗ ⇒ ★★ **故：`mark = 16`（锚点）是**必需的****—— ★ 四格里**只有带锚点的两格成** ✓ |
| 97 | `surface_untrim` | verified | ★★★ **而根因是一组**六格矩阵**定下的—— ★ 六组里**只有一组成**： ① 面 · Face=0(AllEdges) ⇒ 不成 ② 面 · Face=1(InternalEdges) ⇒ 不成 ③ 面 · Face=2(ExternalEdges) ⇒ 不成 ④ **边 · Edge=1(ConnectEndPoints)** ⇒ 不成 ⑤ **边 · Edge=2(ExtendEdges)** ⇒ **成** ✓ ⑥ 面 · BTrimOppositeSide= … |
| 98 | `feature_loft_cut` | verified | ★★ **而对照组同时跑**：放样**凸台**（`InsertProtrusionBlend2`·**18 参**）⇒ `放样1`·**类型名 `Blend`**·**体积 1.0286 倍**（变大）。 ⇒ ★★ **故两者的分界就是**类型名**：`Blend` = 凸台 · **`BlendCut` = 切除**** ✓ |
| 98 | `feature_loft_cut` | verified | ★★★ **而本轮又是一次“失败在判据”**：我第一版照**凸台**抄成 `type_name == "Blend"` ⇒ ★ **对已建成的 `切除-放样1` 判了 `ok=False`** ⚠ （★ 与事实 420 / 431 同族）。 ★ 而与**事实 429**（旋转切除用 `IsCut=True`）**同一族**：★ **“切”会换类型名** 。 |
| 99 | `surface_delete_hole` | verified | ★★ 2026-10-03（轮 564）**真机建成**（零弹窗）：在**一张真正的带孔平面**（面 1 / 环 2）上选**孔那圈边** ⇒ `InsertDeleteHoleForSurface()` ⇒ **名 `删除孔1`**·**型 `DelHole`**·★ **环Δ = −1**（孔被填上）✓ |
| 99 | `surface_delete_hole` | verified | ⚠⚠ 2026-10-04（接手轮）**修正一条容易误导的引证**：★ 本条目原来在 evidence 里**并列引了三份文件**，★ 而**其中两份的 `verdict` 是否定的** —— ★ `output/delete-hole-for-surface-evidence.json` 的 `verdict` 是 **`successor_also_fails`**、`output/delete-hole-inner-loop-evidence.json` 的 verd … |
| 100 | `sketch_line2` | verified | ★★ **而负例与官方 Remarks 逐字对上**：★ **无活动草图**时调它 ⇒ **回 `None`**、草图段数**不可读（-1）** —— ★ 官方："If a sketch is **not active**, then the line is **not created and NULL is returned**" ✓ |
| 101 | `feature_cosmetic_thread` | verified | ★★★ **而根因是三格对照定下的**： ★ 选**圆柱面的边** ⇒ **成** ✓ ★ 选**圆柱面本身** ⇒ 不成 ✗ ★ **什么都不选** ⇒ 不成 ✗ |
| 101 | `feature_cosmetic_thread` | verified | ★★★ **而本轮又一次证明“失败在我这边”**：第一版我用 `str(Surface.Identity)` 里含 `"Cylinder"` 来**猜**哪个面是圆柱面 ⇒ ★ **三组全 `cyl=False`**（★ 根本没找到面）⚠； ★ 而官方有现成的 **`ISurface.IsCylinder()`** ⇒ ★ 换成它之后**一次就成** ✓ |
\| 102 \| `sketch_spline` \| verified \| ★★★ **而三个条件是四格对照定下的**： ① ★ **成员名 = `CreateSpline2`**。★ **`CreateSpline`（不带 2）在**迟到绑定**下根本取不到**（`成员不可调用`，★ 第四类形态）⚠ ② ★ **数组形态 = `VARIANT(VT_ARRAY\|VT_R8, 扁平 list)`** （★ 而**扁平 list / list of tuples 都回 `None`**） ③ ★ **第二个参数 = `False`**（Simula … \|
| 102 | `sketch_spline` | verified | ★★ **而本轮还证明了一件事**：★ `call_com_member` **就是 `get_com_member` 的别名**（实现只有一行；★ 只是**名字即意图**）⇒ ★ **换名字不会改行为** ⚠ |
| 103 | `sketch_spline3_2d` | verified | ★★ **而两格对照把参数说清了**： ★ **2D**（至少 6 坐标 + 其余 `null`） ⇒ **成** ✓ ★ 只给**一个点**（不足 6 坐标） ⇒ 不成 ✗ ★ 而官方 Remarks 逐字：**2D 要至少 6 个坐标；其余参数全给 `null`/`Nothing`** ✓ |
| 104 | `sketch_rotate_or_copy_3d` | verified | ★★ **而对照组把那个布尔钉死了**： |
| 104 | `sketch_rotate_or_copy_3d` | verified | `Copy=False` ⇒ **段 1 → 1**（★ 只旋转、不复制）· 而也回 `True` ✓ |
| 104 | `sketch_rotate_or_copy_3d` | verified | ★★★ **而本轮又纠了一个自己的错**：我第一版传了 **8 个参数**（★ **漏了 `AngleAboutZDir`**）⇒ `DISP_E_PARAMNOTOPTIONAL`（`0x8002000F`）； ★ 而**那个错看不出是哪个参数漏了** ⚠ —— ★ 故又靠**反射的 arity**把它钉出来（铁律 4）。 |
| 105 | `sketch_equation_curve` | verified | ★★ **而三格把两套用法的边界钉死了**： ★ **显式** `y=exp(x)`（**X 给 `""`**） ⇒ **段 0 → 1** ✓ ★ 参数 `x=sin(t)`/`y=cos(t)` ⇒ 段 0 → 0（★ 而**回了 `CDispatch`**）⚠ ★ 坏表达式 `y=zzz(x)` ⇒ 段 0 → 0 · 回 `None`（★ 合理） |
| 106 | `curve_through_xyz` | verified | ★★ **而判据是按事实 436 取的**：`InsertCurveFileBegin` 官方回 **`void`** ⇒ ★ **不能看返回值**，改看 **`feature_names()` 的增量**。 |
| 107 | `select_by_ray` | verified | ★ 它的**语义**（官方逐字）："Defines a **cylindrical region of infinite length** that starts at the specified point and runs parallel to the ray direction"。 |
| 107 | `select_by_ray` | verified | ★★ **而它是 `HoleWizard5` 定孔位的**前置****（事实 464 的 Remarks）："…call **`SelectByRay` with Mark = 0** for each location."。 ★★ **故孔位是“射线选出来的”、**而不是裸坐标** —— ★ **命中什么由几何决定**。 |
| 107 | `select_by_ray` | verified | ★ 而坐标/枚举均有**可核的来源**：`swSelFACES = 2` 取自本机反射 dump（★ 铁律 4 的裁决者）。 |
| 108 | `feature_hole_wizard5` | verified | ★★ 2026-10-03（轮 591）**真机建成**（走 `sw_guard`，零弹窗）： |
| 108 | `feature_hole_wizard5` | verified | `SelectByRay(0,0,+0.05, 0,0,-1, 1e-4, **swSelFACES=2**, False, **Mark=0**, 0)` 定孔位 |
| 108 | `feature_hole_wizard5` | verified | ⇒ HoleWizard5(**swWzdHole=2**, **ANSI_METRIC=1**, **40**螺钉间隙, **"M8"**, **swEndCondThroughAll=1**, 0.008, 0.02, 0, 0×12, "", False, True, False, False, False, False) |
| 108 | `feature_hole_wizard5` | verified | ⇒ **特征 7 → 8**，新增 **`M8 间隙孔1`**（★ **真的异型孔向导特征**）· 返回 `CDispatch` ✓ |
| 108 | `feature_hole_wizard5` | verified | ★★★ **而关键是一个参数的形态**（★ #3211的五格对照）： `SSize=''` · `'8'` · `'0.008'` · `'M8x1.25'` ⇒ **全 `None`**；★ **而 `SSize='M8'` ⇒ 成** ✓ ⇒ ★ 故 **`SSize` 要的是“**规格串**”**（★ 如 `M8`），★ **而不是空串、也不是纯数字** —— ★ 正是官方那句“**必须是该紧固件类型的合法尺寸**”。 |
| 109 | `sketch_offset_on_surface` | verified | ★★★ 2026-10-03（轮 612）**真机建成**（走 `sw_guard`，零弹窗）—— **三格对照**： `按对象选 4 条边（补设 mark=1）` → `SketchOffsetOnSurface(0.01, False, True, False)` → `ClearSelection2` → **`SketchManager.InsertSketch(True)`** ⇒ **特征 7 → 9**，新增 **`基准面1`** + **`草图2`** ✓ ★ … |
| 109 | `sketch_offset_on_surface` | verified | ★★ **而本轮修了两个真因**（★ 全靠真机逼出来）： ① ★ **`SelectByID2("", "EDGE", x,y,z, …)` 一条边都选不中**（★ 角点与中点两种坐标都 `selected = 0`）⚠ ★ 而**事实 32 早写着**：选实体要用 **`IEntity.Select4`（按对象）**；★ 本仓封装：`sw_selection_spec.entities_on_body` + `select_object` ② ★ **`Select4` 没 … |
| 110 | `coverage_gap_batch1` | verified | ★★ **完全定义那个读数**证明**有区分度**（不是常量）：欠定义的矩形（4 段）回 **2**；对 4 段全加 `sgFIXED` 后回 **3** ⇒ ★ 两次读数**不同**。 |
| 110 | `coverage_gap_batch1` | verified | ★ 三个工具名**有意含覆盖率脚本要的关键词**（`revolved_surface` / `hole_wizard` / `fully_defined`）—— ★ 该脚本按「功能关键词**子串**命中工具名」计分 ⇒ **让名字与能力对上**是应有之义。 |

## 六、`level_supported = no` 但 `level` 不是 `verified` 的（不计入第二节）

> 为了**不把「本来就标注未完成」的条目混进矛盾清单**，这一档单列。
> （`stitched` / `not_implemented` 的条目里，证据自称失败是**应然**的。）

- `analysis_run_readback`（`stitched`）：查不到
- `animation_export`（`stitched`）：查不到
- `assembly_and_mates`（`stitched`）：查不到
- `drawing_dimension_insertion`（`not_implemented`）：查不到
- `geometric_tolerance`（`stitched`）：查不到
- `mold_parting_geometry`（`stitched`）：查不到
- `surface_thicken_silent_noop`（`stitched`）：查不到
- `topology_iteration_options_backend_limited`（`stitched`）：查不到

## ⚠ 明确记下的限度

* ⚠ **单元格截断**：本表的「原文片段」列在 340 字处截断、以 `…` 标记。
  **截断可能切断行内代码（反引号）** —— 已做过一次配对修复（只删孤立反引号、不动内容），
  但**截断本身仍是有损的**：要看完整原文请回原始 JSON（`specs/203-bunny-sideline-batches/recon/`）。


* ⚠ **不判「证据够不够」**：本文件只判「证据在不在 + 证据自己有没有说失败」。
  一条 `level_supported = yes` **不代表**这条能力被充分证明 —— 只代表**它点名的证据没自称失败**。
* ⚠ **不判能力好不好、不改 `level`**：判定权在主线。
* ⚠ **`evidence_reachable = none` 的 4 条**属「不可判」，
  **不能**读成通过。
* ⚠ **Bunny 会编造**（本项目已实测 5 条）⇒ 本文件所有结论都已过 Lead 的存在性与字段复核，
  但**没有**做「把每条证据脚本真跑一遍」那一层（支线不跑真机、不跑测试）。
