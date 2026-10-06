# 规格 213 · 目标栏（唯一进度字段）

> ★★ **本文件是唯一进度字段** —— 进度只看这一行；其余段落是上下文，不是判据。

**阶段：B1 完成 —— ★★ **工具数 448 → 454**（★ +6，★ 实测 ✓）· ★★ **覆盖率四域真实涨幅**：★ 曲面 **11/14 → 13/14**（★ +2 ✓）· ★ 焊件 **3/7 → 4/7**（★ +1 ✓）· ★ 特征 **24/28 不变**（★ **真因已查明**：★ 仓外生成器 `gen_user_feature_coverage.py` 的 NOTES 有一条**过时的硬编码备注**把它当假阳性排除了 ✗ —— ★ 而我的 `solidworks_scale_feature` 确实进了 `all_specs()` ✓）· ★ 装配 **5/10 不变**（★ **预期**：爆炸直线 / SpeedPak 属 **B 类**、还没挂 ✓）· ★ 契约测试 **12 passed** · ★ 下一步 **B2（B 类第一步：把探针里已证实的调用序落成 `scripts/` 模块函数）** ✓**

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
