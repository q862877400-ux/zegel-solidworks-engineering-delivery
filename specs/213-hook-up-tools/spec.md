# 规格 213 · 把已验过的能力挂成 MCP 工具（能力 → ToolSpec 的最后一跳）

> **来源**：用户 2026-10-07 指令 —— 「★ **那就把所有的没挂工具的都挂上**」·
> ★ 「★ 你先设置个目标，…然后按照 spec 规则全自动施工」✓
> ★★ **本规格的中心思想**：**能力做完 ≠ 用户能用** ✓ —— 缺的是**最后一跳「能力 → ToolSpec」** ✗

## 一、要解决什么（★ 归因要准，★ 这是用户实测指出的）

★ 用户问「剩下的 9 项有没有核心功能，就是没有的话某个领域功能其他的工具都没有用武之地」⇒
★★ 我查了三处（覆盖表口径 · 领域分布 · 工具注册表），**答案不是"缺地基能力"** ✗：

| 查了什么 | 读数 |
|---|---|
| ★ `docs/user-feature-coverage.md` 的**口径** | ★★ **它只量三列里的第一列「有入口」**（文件头部逐字：「① 有入口 \| 有没有这么个工具/名字 \| ★ **本表量的是这个**」）—— ★ 而"能建成"见 §五、★ "真机验过"见 `capabilities.yaml` 的 `level` ✓ |
| ★★ 第一列的**数据来源** | ★ 生成器 `_load_ours()` 读的是 **`register_capabilities.all_specs()` 的工具名集合** ✓ |
| ★★★ **实测** | ★★ 规格 211 收口时做成 `verified` 的能力 —— `sweep_surface_report` · `untrim_surface_report` · `insert_scale_report` · `section_properties` · `insert_weldment_trim_report` · `export_flat_pattern_dxf_report` · `band_weld` —— ★ **没有任何 ToolSpec 引用它们** ✗ |

⇒ ★★★★ **所以从「用户可发现、可调用」这个口径看，它们**等于不存在**** ✓✓
★ **后果（用户看到的怪现象）**：★ 装配域做了**爆炸直线 + SpeedPak** 两个 `verified` ⇒ 覆盖率**仍 5/10** ；
★ 焊件域做了**四项** ⇒ **仍 3/7** ✓
⇒ ★★★ **不是缺地基，是证据链断在最后一跳** ✓

## 二、工作分两类（★ 实测得出，★ 不是估计）

| 类 | 定义 | 项 |
|---|---|---|
| ★★ **A** | ★ **`scripts/` 里已有可复用实现** ⇒ **只差 ToolSpec** | `section_properties`(sw_mass_property.py:237) · `scale_feature`(sw_part.py:732) · `untrim_surface`(sw_surface_features.py:1084) · `sweep_surface`(sw_surface_features.py:1195) · `weldment_trim`(sw_weldment.py:146) · `flat_pattern_dxf`(sw_export.py:250) |
| ★★ **B** | ★★ **只在探针里验过、`scripts/` 里没有模块函数** ⇒ ★ **要先把调用序落成模块函数**（铁律 3 + 铁律 1：缝合、不发明）| `weld_symbol` · `forming_tool` · `explode_line_sketch` · `speedpak` · `curve_driven_pattern` |

## 三、接进既有链的约定（★ 来自本仓「工具可发现性」主线）

★★ **工具成品须同时进入三处**：★ ① `all_specs()` 行 · ★ ② `capabilities.yaml` 条目 ·
★ ③ `output/*-evidence.json` ✓
· ★ **落点**：★ 新建 `mcp-server/tool_specs_batch100.py` 起（★ 末批 `batch99`、★ 基线 **448** 个工具 ✓）
· ★★ **必须登记**进 `register_capabilities.py` 的 `BATCH_MODULES` **显式清单**（★ 不登记 = 不生效 ✓）
· ★ **形状照** `tool_specs_batch99.py`：`name` / `title` / `module` / `function` / `inject` / `params=[Param(...)]` / `doc` ✓
· ★★ `params` 名**可独立于**函数形参名（`make_tool_function` 按 `spec.params` 逐项 `kwargs[target] = getattr(params, p.name)` ✓）

## 四、参数命名必须过两道既有门禁（★ 规格 212 的产出）

· ★★ **规则 2**：★ **长度参数必须 `_mm` 结尾、角度必须 `_deg` 结尾** ✓；
  ★ 且 `_BARE_COORD_NAMES = {"x","y","z","point","coordinate"}` ⇒ ★ **裸坐标名会被判"像坐标分量"** ✗
· ★★ **规则 2b**：★ **名字带单位后缀 ⇒ 描述必须有单位词** ✓；★ **无量纲/枚举/布尔 ⇒ 名字不许带单位后缀** ✓

## 五、验收判据（★★ 必须真跑、★ 不许估数）

★ ① ★★ **覆盖率真实涨幅**：★ 跑 `python D:\SW-coverage-tool\gen_user_feature_coverage.py`，
  记录**四个域**（装配 / 焊件 / 特征 / 曲面）的**前后读数** ✓
★ ② ★ **工具数**：★ `all_specs()` 的条数（★ 基线 **448** ✓）
★ ③ ★ **全部既有门禁过**：★ `check_spec` 的规则 2 / 规则 2b · ★ 返回出口单位守卫 ·
  ★ `scripts/check_union_conventions.py` · ★ `scripts/release_check.py` ✓
★ ④ ★ **每项有契约/负例测试**（★ 事实 62：★ **门禁只靠负例证明** ✓）
