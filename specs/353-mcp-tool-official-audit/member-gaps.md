# 规格 353 · 仍无官方页的成员（逐条结论）

> 顺序按业主 2026-11-01 指定：**① 项目文件 → ② 本地官方文档树 → ③ 官网**。
> 本地：`tools/audit_undocumented_members.py --write`；官网：`tools/fetch_official_member_pages.py --apply`
> （25 个成员按 12 s 节奏逐页查，每 5 个成员用**对照页**排除限流；对照页 = `ISketch~GetLines`）。

| # | 接口.成员 | 用它的工具 | 结论（依据） |
|---|---|---|---|
| 1 | `ISketch.Name` | solidworks_sketch_end<br>solidworks_sketch_stretch_entities | ★ 出厂类型库 `## ISketch` 段**无 `Name`** ⇒ 该接口上没有这个成员；实现作为**试名探测**、失败即回落。本地 6 棵树 + 官网均无页。 |
| 2 | `ISketch.GetFeature` | solidworks_sketch_end | ★ `## ISketch` 段无 `GetFeature` ⇒ 同上（试名探测）。 |
| 3 | `ISketch.GetConstrainedStatus2` | solidworks_add_sketch_relation | ★ `## ISketch` 段无 `GetConstrainedStatus2`；官方有 `GetConstrainedStatus`（**有页**）⇒ 实现先试带 `2` 的名字、失败回落。 |
| 4 | `(未登记接口).Name` | solidworks_add_concentric_mate<br>solidworks_costing_list_bodies<br>solidworks_costing_read_body | ★ 本地 6 棵树 + 官网均无成员页；出厂类型库有签名（见该条 `gap`），语义不可得 —— 按铁律 5 记账，不编页。 |
| 5 | `IMate2.Name` | solidworks_assembly_add_mate_checked<br>solidworks_assembly_add_parallel_mate | ★ `## IMate2` 段无 `Name` ⇒ 用 `Name` 给 mate 改名不成立（应走 `IFeature.Name`）；两处均包在 try/except 里。 |
| 6 | `(未登记接口).Xform` | solidworks_drawing_collect_view_evidence | ★ 出厂类型库 `## IModelView` 段**有** `Object get_Xform()` ⇒ 成员存在、无文档页；实现挂在 `IView` 上取，属**取错宿主**（`docs/family-coverage.md` 记的是 `IModelView.Xform`）。 |
| 7 | `(未登记接口).GetSurfaceBodies` | solidworks_surface_midsurface_create | ★ 两套官方源 + 出厂类型库**都查不到**该名字（`specs/202` recon 已记）⇒ 实现是**试名探测**。 |
| 8 | `(未登记接口).GetSurfaceBodyCount` | solidworks_surface_midsurface_create | ★ 同上（试名探测）。 |
| 9 | `(未登记接口).CostingDefaults` | solidworks_costing_defaults | ★ 本地 6 棵树 + 官网均无成员页；出厂类型库有签名（见该条 `gap`），语义不可得 —— 按铁律 5 记账，不编页。 |
| 10 | `(未登记接口).CostingTemplateName` | solidworks_costing_read_analysis | ★ 本地 6 棵树 + 官网均无成员页；出厂类型库有签名（见该条 `gap`），语义不可得 —— 按铁律 5 记账，不编页。 |
| 11 | `(未登记接口).CurrencyCode` | solidworks_costing_read_analysis | ★ 本地 6 棵树 + 官网均无成员页；出厂类型库有签名（见该条 `gap`），语义不可得 —— 按铁律 5 记账，不编页。 |
| 12 | `(未登记接口).CurrencyName` | solidworks_costing_read_analysis | ★ 本地 6 棵树 + 官网均无成员页；出厂类型库有签名（见该条 `gap`），语义不可得 —— 按铁律 5 记账，不编页。 |
| 13 | `(未登记接口).CurrencySeparator` | solidworks_costing_read_analysis | ★ 本地 6 棵树 + 官网均无成员页；出厂类型库有签名（见该条 `gap`），语义不可得 —— 按铁律 5 记账，不编页。 |
| 14 | `(未登记接口).LotSizeForMultibody` | solidworks_costing_set_default_lot_size | ★ 本地 6 棵树 + 官网均无成员页；出厂类型库有签名（见该条 `gap`），语义不可得 —— 按铁律 5 记账，不编页。 |
| 15 | `(未登记接口).LotSizeForSingleBody` | solidworks_costing_set_default_lot_size | ★ 本地 6 棵树 + 官网均无成员页；出厂类型库有签名（见该条 `gap`），语义不可得 —— 按铁律 5 记账，不编页。 |
| 16 | `(未登记接口).LotSize` | solidworks_costing_set_lot_size | ★ 本地 6 棵树 + 官网均无成员页；出厂类型库有签名（见该条 `gap`），语义不可得 —— 按铁律 5 记账，不编页。 |
| 17 | `(未登记接口).MarkUpPercent` | solidworks_costing_set_markup | ★ 本地 6 棵树 + 官网均无成员页；出厂类型库有签名（见该条 `gap`），语义不可得 —— 按铁律 5 记账，不编页。 |
| 18 | `(未登记接口).MarkUpType` | solidworks_costing_set_markup | ★ 本地 6 棵树 + 官网均无成员页；出厂类型库有签名（见该条 `gap`），语义不可得 —— 按铁律 5 记账，不编页。 |
| 19 | `ICwAddincallback.CosmosWorks` | solidworks_simulation_collect_evidence<br>solidworks_simulation_create_study<br>solidworks_simulation_get_study_manager | ★ 出厂类型库 `## ICwAddincallback` 段有 `CosmosWorks get_CosmosWorks()` ⇒ 存在、无描述页。 |
| 20 | `(未登记接口).GetCostAnalysis` | solidworks_costing_read_body | ★ 本地 6 棵树 + 官网均无成员页；出厂类型库有签名（见该条 `gap`），语义不可得 —— 按铁律 5 记账，不编页。 |
| 21 | `(未登记接口).GetName` | solidworks_costing_read_body | ★ 本地 6 棵树 + 官网均无成员页；出厂类型库有签名（见该条 `gap`），语义不可得 —— 按铁律 5 记账，不编页。 |
| 22 | `(未登记接口).GetSWBody` | solidworks_costing_read_body | ★ 本地 6 棵树 + 官网均无成员页；出厂类型库有签名（见该条 `gap`），语义不可得 —— 按铁律 5 记账，不编页。 |
| 23 | `ICWStudyManager.CreateNewStudy2` | solidworks_simulation_create_study | ★ 出厂类型库 `## CWStudyManager` 段有 `CWStudy CreateNewStudy2(String, Int32, Int32&)` ⇒ 成员在 **VB6/CW** 接口上存在，`.NET ICW*` 侧无页；本地 2 个接口有同名页、官网无。 |
| 24 | `IModelView.GetModelDoc` | solidworks_get_view_model_doc | ★ 出厂类型库 `## IModelView` 段**有** `ModelDoc GetModelDoc()` ⇒ 成员存在、只是**没有文档页**（本地 6 棵树 + 官网均无）。 |
| 25 | `IFeature.GetSketch` | solidworks_feature_revolve_cut | ★ `## IFeature` 段无 `GetSketch` ⇒ 死分支（异常被 except 吞）。 |
