# 规格 220 · 任务清单（tasks）

> ★ 通用验收（每批都适用）：
> G1 ★ 三件套齐（`all_specs()` 行 + `capabilities.yaml` 归属 + 契约测试）
> G2 ★ `pwsh tools/round_chain.ps1 -Tests <新测试>` ⇒ `release_check` **一轮即绿**（★ 先重跑生成器）
> G3 ★ `git diff capabilities.yaml` 里 **`level` 的每一处变更都能指认真机证据** ✓
> G4 ★ 重跑 `python D:\SW-coverage-tool\gen_user_feature_coverage.py` ⇒ 目标格变 ✅
> G5 ★ **真机用完关 SolidWorks** ✓

## T-220-01 · ★★ 批 1：还"验证债"（真机验证边界特征两个 Type）

- ★ 写探针 `tools/probe_spec220_boundary.py`：★ 建 100×60×20 mm 板 ⇒ 取两个面 ⇒
  ★ 先 `blend_type=2`（**曲面**）⇒ 再 `blend_type=1`（**凸台**）⇒ ★ 打印回读（特征树计数 + 选区计数）✓
- ★ 真机：`python tools/sw_guard.py --timeout 600 -- python tools/probe_spec220_boundary.py` ✓
- ★★ **判据**：★ `ok=True` 且**特征树计数增量 ≥ 1**（★ 事实 8：布尔不可信）✓
- **验收**：★ 过了 ⇒ 台账 `surface_features` 的 `level` 与两条工具的 `evidence` 更新（★ 真机读数逐字）；
  ★ **没过 ⇒ 留在 `stitched`**，★ 把失败读数写进 `limitations` ✓（★ **两种结果都算完成，只要如实**）

## T-220-02 · ★ 批 2：焊件/圆角焊缝（⇒ 焊件 7/7 = 100%）

- ★ 按铁律 4 第 0 步读官方三样：★ `InsertFilletBeadFeature` 的签名 + `## Remarks` + CHM 例 ✓
- ★ 实现 `*_report`（★ 面集合 ⇒ **声明式面序号**）⇒ 暴露 ⇒ 台账 ⇒ 契约测试 ✓
- **验收**：★ G1–G5 + ★ 真机读数 ⇒ ★ 地图 **焊件 7/7** ✓

## T-220-03 · ★ 批 3：装配/零部件阵列（⇒ 装配 8/10）

- ★ 读官方：★ `DissolveComponentPattern` / `GetPatternComponentCount` 的签名 + Remarks ✓
- ★ 实现 + 暴露 + 台账 + 契约测试 + 真机 ✓
- **验收**：★ G1–G5 + ★ 地图 **装配 8/10** ✓

## T-220-04 · ★★ 批 4：3 格"不做 + 原因" + 收口

- ★ 把 **装配序列 · 性能分析 · PDM** 三格的**不可做原因**写进 `docs/user-feature-coverage.md`
  对应段（★ 带 `C:\swapi\types` 的**实查依据**逐条）✓
  ★ 注意：★ 该文件是**生成物**（★ 生成器在 `D:\SW-coverage-tool\`）⇒ ★ 两条路：
  ★ ① 若生成器有"不做"段 ⇒ 在**生成器**里加（★ 与 219 修 `FALSE_POS` 同法，★ 先备份）✓
  ★ ② 否则在本仓留一份 `specs/220-*/not-doing.md`（★ 本仓侧的权威记录）并在目标栏链它 ✓
- ★ 重跑生成器 ⇒ ★ **逐格核对 145 项** ⇒ ★ 写最终账（★ **141/145**，★ 差在哪、为什么）✓
- **验收**：★ A1–A5（见 `spec.md` §五）· ★ `release_check` 绿 · ★ 索引 0 ✓

## ★ 停止条件（★ 遇到就停，不硬推）

1. ★ 真机验证**不成** ⇒ ★ 按 A1 如实留 `stitched` + 记失败读数（★ 不算失败，算如实）✓
2. ★ 某格官方签名查不到 ⇒ ★ 按铁律 5 写"查不到"，★ 并把它并进"不做 + 原因"✓
3. ★ 需要许可证（★ 如 PDM）⇒ ★ 停，写"不做 + 原因"✓
