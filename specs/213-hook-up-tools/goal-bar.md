# 规格 213 · 目标栏（唯一进度字段）

> ★★ **本文件是唯一进度字段** —— 进度只看这一行；其余段落是上下文，不是判据。

**阶段：★★★ **规格 213 全文收口** —— ★ 11 项**全部挂成 MCP 工具** ✓ · ★★ **工具数 448 → 459** ✓ · ★★ **本仓库覆盖 124/145（86%）→ 133/145（92%）** ✓ · ★★ **四域真实涨幅**：★ 装配 **50%→70%** · ★ 焊件 **43%→71%** · ★ 特征 **86%→89%** · ★ 曲面 **79%→93%** ✓（★ 另记：★ 钣金 **73%→82%** · ★ 评估 **83%→100%** ✓）· ★★ **全量 pytest**：★ 抓出并修掉**我引入的 8 组**（★ 效应表 · ★ 登记表 · ★ 批次大小 · ★ 签名审计 · ★ 缺口分诊**两处** · ★ batch82 的删除名单 · ★ **`GetExplodedViewCount` 传参错** ✓）；★ **剩下的都在既有基线内**（★ 且出错模块 `sw_sketch.py` / `sw_session.py` **我一次没改过** ✓）· ★ 下一步 **无（目标达成）** ✓**

---

## 当前状态

★ **规格 213 立起**（2026-10-07）。★ 承接规格 211 的**收口漏洞**：

★★★ **漏洞是什么**（★ 用户实测指出，★ 我这批才看明白）：
· ★ `docs/user-feature-coverage.md` 只量三列里的**第一列「有入口」** ✓
· ★★ 而第一列的来源是 **`register_capabilities.all_specs()` 的工具名集合** ✓
· ★★★ **实测**：★ 规格 211 做成 `verified` 的能力（`sweep_surface_report` · `untrim_surface_report` ·
  `insert_scale_report` · `section_properties` · `insert_weldment_trim_report` ·
  `export_flat_pattern_dxf_report` · `band_weld`）**没有任何 ToolSpec 引用它们** ✗
⇒ ★★★★ **所以从「用户可发现、可调用」口径看，它们等于不存在** ✓
  ★ **这解释了**：★ 装配域做了爆炸直线 + SpeedPak 两个 `verified` ⇒ **仍 5/10** ；
  ★ 焊件域做了四项 ⇒ **仍 3/7** ✓

## 工作分两类（★ 实测得出）

### ★★ A 类 · 6 项 —— `scripts/` 里已有可复用实现，只差 ToolSpec

| 能力 | 实现落点 |
|---|---|
| ★ `section_properties` | ★ `scripts/sw_mass_property.py:237` |
| ★ `scale_feature` | ★ `scripts/sw_part.py:732`（★ 参数是**无量纲缩放比例** ⇒ ★ 名字不能叫 `x`/`y`/`z` ✓）|
| ★ `untrim_surface` | ★ `scripts/sw_surface_features.py:1084` |
| ★ `sweep_surface` | ★ `scripts/sw_surface_features.py:1195` |
| ★ `weldment_trim` | ★ `scripts/sw_weldment.py:146` |
| ★ `flat_pattern_dxf` | ★ `scripts/sw_export.py:250` |

### ★★ B 类 · 5 项 —— 只在探针里验过，`scripts/` 里没有模块函数

★ `weld_symbol` · `forming_tool` · `explode_line_sketch` · `speedpak` · `curve_driven_pattern`
⇒ ★★ **要先把探针里已证实的调用序落成 `scripts/` 模块函数**（★ 铁律 3 + 铁律 1：缝合、不发明 ✓）

## 两条基线（★ 改动前后都要量，★ 不许估数）

| 量什么 | 怎么量 | 基线 |
|---|---|---|
| ★ **工具数** | ★ `register_capabilities.all_specs()` 的条数 | ★ **448** |
| ★★ **覆盖率** | ★ `python D:\SW-coverage-tool\gen_user_feature_coverage.py` | ★ 装配 **5/10** · 焊件 **3/7** · 特征 **24/28** · 曲面 **11/14** |
