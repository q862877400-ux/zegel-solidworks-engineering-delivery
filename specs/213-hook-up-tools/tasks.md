# 规格 213 · 任务清单

> ★ 勾选规则：**判据齐了才勾**（★ 改动 + 契约/负例 + 收尾链 + 按路径提交）✓
> ★★ 三种记号：★ **`[x]` = 已做** · ★★ **`[~]` = 有意挂起（不是漏做）** · ★ **`[ ]` = 未做**

## B0 · 只读侦察

- [ ] **B0-1** 枚举"没挂工具"的清单 ⇒ ★ **不靠名字 token 猜**（★ 实测会有假阳性：`form` 命中 `transform` · `flat` 命中 `flatten_surface` ✗）—— ★ 改成**逐项按实现函数名**查 `mcp-server/tool_specs_*.py` 有没有引用 ✓
- [ ] **B0-2** 摸清 `ToolSpec` 形状与 `BATCH_MODULES` 登记法（★ 照 `tool_specs_batch99.py` ✓）；记录**基线工具数**（★ 实测 **448** ✓）
- [ ] **B0-3** 把清单**分成两类**并落档：★ A 类（实现已有、只差 ToolSpec）· ★ B 类（只在探针里验过）✓

## B1 · A 类 6 个 ToolSpec

- [ ] **B1-1** `solidworks_section_properties`（`sw_mass_property.section_properties`）
- [ ] **B1-2** `solidworks_scale_feature`（`sw_part.insert_scale`）★ **参数名不能叫 `x`/`y`/`z`**（★ 撞 `_BARE_COORD_NAMES`；★ 它们是**无量纲比例**）✓
- [ ] **B1-3** `solidworks_untrim_surface`（`sw_surface_features.untrim_surface_report`）★ `distance_mm` ✓
- [ ] **B1-4** `solidworks_sweep_surface`（`sw_surface_features.sweep_surface_report`）★ `twist_angle_deg` ✓
- [ ] **B1-5** `solidworks_weldment_trim`（`sw_weldment.insert_weldment_trim_report`）★ `gap_mm` ✓
- [ ] **B1-6** `solidworks_export_flat_pattern_dxf`（`sw_export.export_flat_pattern_dxf`）★ 含 D 项的两个新形参 ✓
- [ ] **B1-7** 新建 `mcp-server/tool_specs_batch100.py` 并**登记进 `BATCH_MODULES`** ✓
- [ ] **B1-8** 契约/负例测试 + 收尾链 + 按路径提交 ✓；★ 记录**工具数 448 → ?** 的真实读数 ✓

## B2 · B 类第一步：把探针里的调用序落成模块函数

- [ ] **B2-1** `weld_symbol` ⇒ ★ 落 `scripts/sw_drawing_create_missing.py`（★ 或更贴的既有模块 ✓）—— ★ 调用序**已证实**：★ 选面 → `InsertWeldSymbol3()` → `IWeldSymbol::SetText` ✓
- [ ] **B2-2** `forming_tool` ⇒ ★ 落 `scripts/sw_sheet_metal.py` —— ★ 调用序**已证实**：★ 钣金件 → 选面 → `InsertFormToolFeature(Path, …)` ✓
- [ ] **B2-3** `explode_line_sketch` ⇒ ★ 落 `scripts/sw_assembly_doc.py`（★ 同类已在那 ✓）—— ★ `ISketchManager::InsertExplodeLineSketch()` ✓
- [ ] **B2-4** `speedpak` ⇒ ★ 落 `scripts/sw_assembly_doc.py` —— ★ 调用序**已证实**：★ 选子装配（`SelectByID2(<名>, "COMPONENT")`）→ `CreateSpeedPak(int)` ✓
- [ ] **B2-5** `curve_driven_pattern` ⇒ ★ 落 `scripts/sw_pattern.py`（★ 同类已在那 ✓）—— ★ 参数式那条**真机两档有效读数皆不建** ⇒ ★ **如实标 `stitched`** ✓
- [ ] **B2-6** 每项配契约/负例测试 + 收尾链 + 按路径提交 ✓

## B3 · B 类第二步：5 个 ToolSpec

- [ ] **B3-1** 五个 ToolSpec（★ 续 `tool_specs_batch100.py` 或起 `batch101.py` ✓）
- [ ] **B3-2** 登记进 `BATCH_MODULES` ✓ · 契约/负例 · 收尾链 · 按路径提交 ✓

## B4 · 覆盖表验收（★ 不许估数）

- [ ] **B4-1** 跑 `python D:\SW-coverage-tool\gen_user_feature_coverage.py` ⇒ ★ 记录**装配 / 焊件 / 特征 / 曲面四域的真实前后读数** ✓
- [ ] **B4-2** 跑 `git diff --stat docs/user-feature-coverage.md` 看**实际变了哪些行** ✓
- [ ] **B4-3** ★ **如实记账**：★ 涨了的写涨了 · ★ **没涨的写明为什么**（★ 不许把"挂了工具"当成"覆盖涨了" ✓）

## B5 · 收口

- [ ] **B5-1** `tasks.md` 三种记号落全 ✓
- [ ] **B5-2** `goal-bar.md` 唯一进度字段 ✓
- [ ] **B5-3** `docs/HANDOFF.md` 加新版块 ✓
- [ ] **B5-4** 全量 pytest（★ 本规格改了 `mcp-server/` 与 `scripts/` ⇒ ★ **按纪律该跑全量** ✓）+ 与基线对照 ✓
