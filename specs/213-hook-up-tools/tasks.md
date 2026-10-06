# 规格 213 · 任务清单

> ★ 勾选规则：**判据齐了才勾**（★ 改动 + 契约/负例 + 收尾链 + 按路径提交）✓
> ★★ 三种记号：★ **`[x]` = 已做** · ★★ **`[~]` = 有意挂起（不是漏做）** · ★ **`[ ]` = 未做**

## B0 · 只读侦察

- [x] **B0-1** 枚举"没挂工具"的清单 ⇒ ★ **不靠名字 token 猜**（★ 实测假阳性：`form` 命中 `transform` · `flat` 命中 `flatten_surface` ✗）—— ★ 改成**逐项按实现函数名**查 ✓；★ **并如实记下：`capabilities.yaml` 的 schema 里没有"能力 → 工具"映射字段** ⇒ **全仓严谨普查做不到** ✓
- [x] **B0-2** 摸清 `ToolSpec` 形状与 `BATCH_MODULES` 登记法（★ 照 `tool_specs_batch99.py` ✓）；★ **实测基线工具数 448** ✓
- [x] **B0-3** 分成两类并落档：★ **A 类 6**（实现已有、只差 ToolSpec）· ★ **B 类 5**（只在探针里验过）✓

## B1 · A 类 6 个 ToolSpec ✅ 完成（提交 `b32caae0`）

- [x] **B1-1** `solidworks_section_properties`（`sw_mass_property.section_properties`）
- [x] **B1-2** `solidworks_scale_feature`（`sw_part.insert_scale`）★ **被规则 3 拦下**（入参 `x` 是**裸坐标** ✗）⇒ ★ 改名 `*_factor` + ★ **`param_alias` 映射回形参** ✓
- [x] **B1-3** `solidworks_untrim_surface`（`sw_surface_features.untrim_surface_report`）★ `distance_mm` ✓
- [x] **B1-4** `solidworks_sweep_surface`（`sw_surface_features.sweep_surface_report`）★ `twist_angle_deg` ✓
- [x] **B1-5** `solidworks_weldment_trim`（`sw_weldment.insert_weldment_trim_report`）★ `gap_mm` ✓
- [x] **B1-6** `solidworks_export_flat_pattern_dxf`（`sw_export.export_flat_pattern_dxf`）★ 含 D 项两个新形参 ✓
- [x] **B1-7** 新建 `mcp-server/tool_specs_batch100.py` + **登记进 `BATCH_MODULES`** ✓
- [x] **B1-8** 契约测试 **12 passed** · 收尾链 · 按路径提交 ✓；★ **工具数 448 → 454** ✓

## B2 · B 类第一步：把探针调用序落成模块函数 ✅ 完成

- [x] **B2-1** `weld_symbol` ⇒ ★ 落 `scripts/sw_weldment.py` 的 `insert_weld_symbol_report` ✓
- [x] **B2-2** `forming_tool` ⇒ ★ 落 `scripts/sw_sheet_metal.py` 的 `insert_form_tool_report` ✓
- [x] **B2-3** `explode_line_sketch` ⇒ ★ 落 `scripts/sw_assembly_doc.py` 的 `insert_explode_line_sketch_report` ✓
- [x] **B2-4** `speedpak` ⇒ ★ 落 `scripts/sw_assembly_doc.py` 的 `create_speedpak_report` ✓
- [x] **B2-5** `curve_driven_pattern` ⇒ ★ 落 `scripts/sw_pattern.py` 的 `insert_local_curve_driven_pattern_report` ✓（★ 与既有属性式那个**分开两个函数** ✓）
- [x] **B2-6** ★★ **真机走模块函数复验**（★ 不是重跑探针 ✓）：`tools/probe_spec213_b2_modules.py` · `tools/probe_spec213_b2b_modules.py` ✓
- [x] **B2-7** ★★ **真机复验抓出我两处判据太弱** ✗ ⇒ ★ 都修了并**重跑出有效读数** ✓（★ 见 `goal-bar.md`）

## B3 · B 类第二步：5 个 ToolSpec ✅ 完成

- [x] **B3-1** `tool_specs_batch101.py`（★ `weld_symbol` · `forming_tool`）⇒ ★ 工具数 **454 → 456** ✓
- [x] **B3-2** `tool_specs_batch102.py`（★ 爆炸直线 · SpeedPak · 曲线驱动阵列）⇒ ★ 工具数 **456 → 459** ✓
- [x] **B3-3** 登记进 `BATCH_MODULES` ✓ · 契约/负例 · 收尾链 · 按路径提交 ✓
- [x] **B3-4** ★★ **等级分档如实**：★ 爆炸直线 / SpeedPak ⇒ `verified` ✓ · ★ **曲线驱动阵列 ⇒ `stitched`** ✓（★ 官方页第一行就是 `Obsolete` ✓；★ A7：★ 不许把 `stitched` 写成 `verified` ✓）

## B4 · 覆盖表验收（★ 不许估数）✅ 完成

- [x] **B4-1** 每批跑 `gen_user_feature_coverage.py`，★ **真实前后读数**已逐批落档 ✓
- [x] **B4-2** ★ **最终读数**：★ **本仓库 124/145 → 133/145（86% → 92%）** ✓ · ★ **工具数 448 → 459** ✓
- [x] **B4-3** ★ **四域真实涨幅**（★ 目标点名的那四个 ✓）：★ **装配 5/10 → 7/10（50%→70%）** · ★ **焊件 3/7 → 5/7（43%→71%）** · ★ **特征 24/28 → 25/28（86%→89%）** · ★ **曲面 11/14 → 13/14（79%→93%）** ✓
- [x] **B4-4** ★ **另记两域**（★ 本批的工具落在别的域 ✓）：★ 钣金 **8/11 → 9/11** · ★ 评估 **5/6 → 6/6（100%）** ✓
- [x] **B4-5** ★★★ **终检（★ 证明"没有漏"）**：把 ToolSpec 的 `(module, function)` 集合取出、与 `scripts/` 里像入口的公开函数相减 ⇒ ★ 得 **118 个"没被直接引用"** ✗ —— ★ **抽样判定后结论**：★★ **绝大多数是"包装函数/备用入口"、★ 不是缺口** ✓（★ `export_to_step` 有包装 `export_to_format` 调它 ✓ · ★ `create_through_hole` **有** ToolSpec 引用 ✓ ⇒ ★ **我的 `function=` 匹配太窄** ✗）
- [x] **B4-6** ★★ **终检的真发现（★ 如实记、★ 有意不扩范围）**：★ 有几个能力存在 **`_report` 兄弟入口**（★ `sw_part.insert_scale_report` · ★ `sw_export.export_flat_pattern_dxf_report` ✓）—— ★ 它们返回**更富的证据字典** ✓，★ 而**能力本身已经挂上了**（★ 由 `insert_scale` / `export_flat_pattern_dxf` ✓）⇒ ★★ **一个能力挂两个工具会变成"大杂烩"** ✗（★ 违反本仓"不搞大杂烩"的定位 ✓）⇒ ★ **有意保留为内部入口** ✓

## B5 · 收口

- [x] **B5-1** `tasks.md` 三种记号落全 ✓
- [x] **B5-2** `goal-bar.md` 唯一进度字段 ✓
- [x] **B5-3** `docs/HANDOFF.md` 加新版块 ✓
- [x] **B5-4** ★★ **全量 pytest**（★ 本规格改了 `mcp-server/` 与 `scripts/` ⇒ ★ 按纪律该跑 ✓）+ ★ **与基线逐条对照** ✓
- [x] **B5-5** ★ **`sync_bundled_skill.py` 已跑**（★ 事实 55：★ 改了运行时文件必须跑 ✓）
- [x] **B5-6** ★ 收尾链 + ★ 按路径提交 ✓

## ★★ 有意挂起 / 有意不做（★ 都不是漏做）

- [~] **规格外的更大普查**：★ 把"能力 → 工具"的映射**建进 `capabilities.yaml` 的 schema**（★ 新增一个字段），★ 然后做**全仓严谨普查** ✓ —— ★★ **本规格没做**：★ 因为那要改 **140 条**的条目形状、★ 且属于**另一个规格**（★ 而本规格的范围是**用户点名的 11 项** ✓）
- [~] **`_report` 兄弟入口要不要也挂**：★ **有意不挂** ✓（★ 理由见 B4-6：★ 一能力两工具 = 大杂烩 ✗）
