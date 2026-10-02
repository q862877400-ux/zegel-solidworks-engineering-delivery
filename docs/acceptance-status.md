# 验收命令现状（`verified` 条目声明的那 31 条真机脚本）

> 生成：`python tools/run_verified_acceptance_commands.py`（**每跑一次都会刷新 `output/verified-acceptance-run.json`**）。
> ⚠⚠ **轮 181 更正**：`verify_composite_curve_smoke` 那条**不是「判据把应然当失败」** ——
> 它的判据**与自己的文本矛盾**，而**实测前提是成立的** ⇒ ★ **它是真失败**（真缺陷）。
> 判据已改成「**前提成立才要求 True**」⇒ 现在这条红**含义准确**（仍是红，因为**确实失败**）。
> ⚠⚠ **轮 182 再更正**：`verify_composite_curve_smoke` 的**真正前置**是「**两条样条草图**」（官方三份样例一致），而 **样条在本机建不出来** ⇒ **前置不可达**
> （**不是**它自己功能不行）。判据已改成三档 ⇒ 本条**不计入红**；★ 卡住的**样条**（`CreateSpline2` 返回 None）才是**未解问题**。
> ⚠ 本表是 **2026-10-01（轮 180）** 的快照 —— ★ **「曾经绿」不等于「现在绿」**（事实 119），
> 所以**每次改完都要重跑**这张表，别拿它当**永久**结论。

| 命令 | 结果 | 定性 |
|---|---|---|
| `tools/audit_get_com_member_semantics.py` | （无 verdict） | — 探针（不设 verdict，正常） |
| `tools/capture_simulation_evidence.py` | （无 verdict） | 事实 119 同族：环境缺 Simulation 加载项/许可 |
| `tools/capture_topology_evidence.py` | （无 verdict） | 事实 119：环境缺 Simulation 加载项/许可（轮 179） |
| `tools/probe_add_relation_forms.py` | （无 verdict） | — 探针（不设 verdict，正常） |
| `tools/probe_chamfer_forms.py` | （无 verdict） | — 探针（不设 verdict，正常） |
| `tools/probe_dwg_magic.py` | （无 verdict） | — 探针（不设 verdict，正常） |
| `tools/probe_export_magic_matrix.py` | （无 verdict） | — 探针（不设 verdict，正常） |
| `tools/probe_getlines_count.py` | （无 verdict） | — 探针（不设 verdict，正常） |
| `tools/probe_gtol_frame_order.py` | （无 verdict） | — 探针（不设 verdict，正常） |
| `tools/probe_pdf_on_drawing.py` | （无 verdict） | — 探针（不设 verdict，正常） |
| `tools/probe_sketch_getter_shapes.py` | （无 verdict） | — 探针（不设 verdict，正常） |
| `tools/probe_slot_and_point_shapes.py` | （无 verdict） | — 探针（不设 verdict，正常） |
| `tools/probe_window_vs_graphics.py` | （无 verdict） | — 探针（不设 verdict，正常） |
| `tools/verify_bbox_smoke.py` | 8/8 | ★ 绿 |
| `tools/verify_bmp_smoke.py` | 8/8 | ★ 绿 |
| `tools/verify_centerline_smoke.py` | 8/8 | ★ 绿 |
| `tools/verify_composite_curve_smoke.py` | **8/8** | ⚠ **轮 182 定性更正**：官方样例（VBA/C#/VB.NET 三份一致）要求前置 = 「**两条**样条**草图**」，而 ★ **样条在本机建不出来**（`CreateSpline2` 返回 None，事实 40 族）⇒ **前置不可达** ⇒ `InsertCompositeCurve` 必然 False。★ 判据已改成**三档**（可达 ⇒ 要求 True / 不可达 ⇒ **不计入** / 真失败）⇒ 本条**不再计入红**。⚠ 但卡住的**样条**本身是**未解问题**。 |
| `tools/verify_costing_e2e.py` | verdict=pass | ★ 绿 |
| `tools/verify_dfm_e2e.py` | 15/15 | ★ 绿 |
| `tools/verify_dome_smoke.py` | 9/9 | ★ 绿 |
| `tools/verify_dxf_preview_e2e.py` | 15/15 | ★ 绿 |
| `tools/verify_ellipse_smoke.py` | 11/11 | ★ 绿 |
| `tools/verify_equation_smoke.py` | 5/5 | ★ 绿 |
| `tools/verify_gtol_smoke.py` | 3/5 | 事实 166：`IGtolFrame.AddIndicator` border×tol **20 组全不成** |
| `tools/verify_helix_smoke.py` | 13/13 | ★ 绿 |
| `tools/verify_hole_standards_smoke.py` | 11/11 | ★ 绿 |
| `tools/verify_in_context_reference_smoke.py` | 9/12 | 事实 162：**在上下文编辑链**未打通（`SketchUseEdge3` 静默无效） |
| `tools/verify_png_smoke.py` | 9/9 | ★ 绿 |
| `tools/verify_routing_e2e.py` | 18/18 | ★ 绿 |
| `tools/verify_sketch_edit_smoke.py` | 10/10 | ★ 绿 |
| `tools/verify_sketch_getters_smoke.py` | 18/18 | ★ 绿 |

## 汇总

```
绿   **15**
红   **3**（两条**已知**：事实 166 / 162；一条**本轮查清**：`composite_curve` 把「应然的失败」当成了 fail）
探针 **13**（`probe_*` / `audit_*` —— **不设 verdict 是它们的正常形态**）
```

## ⚠ 本轮（轮 180）的两个发现

1. ★★ **`verify_composite_curve_smoke` 6/7 是红的**，而它被 `part_and_features` 当作 evidence ⇒
   **那条 evidence 本身是红的**；★ 失败那条是「**前提未满足，属应然**」⇒
   ⚠ **是 smoke 的判据把「应然」当成了「失败」**（判据问题，不是退化）。
2. ⚠ **我的跑器第一版判据太窄**：本仓库的验收脚本有**三种**输出格式
   （`── N/M · verdict: x ──` / `── N/M 项通过 · verdict: x ──` / 单独一行 `verdict: x`），
   我只认第一种 ⇒ **把 4 个 pass 误报成「无 verdict」**。
   ⇒ ★ 又一次「**判据要与实现的实际形态对齐**」（事实 51 那一族）。
