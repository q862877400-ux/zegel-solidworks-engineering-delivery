# 规格 219 · 任务清单（tasks）

> ★★ 通用验收（每批都适用）：
> ★ G1 三件套齐（`all_specs()` 行 + `capabilities.yaml` 归属 + 契约测试）
> ★ G2 `pwsh tools/round_chain.ps1 -Tests <新测试>` ⇒ `release_check` **一轮即绿**
> ★ G3 ★★ `git diff capabilities.yaml` 里 **`level` 变更每一处都能指认真机证据**
> ★ G4 ★ 重跑 `python D:\SW-coverage-tool\gen_user_feature_coverage.py --check` ⇒ 相关格变 ✅
> ★ G5 ★ `git diff --stat` 无意外删除（★ 事实 61）

## T-219-01 · ★★ **去伪**（12 项裁定表）—— ★ 头号任务，不许跳

- ★ 产出 `specs/219-user-coverage-100/verdicts.md`：**12 行**，每行给
  `域 | 功能 | 裁定(A/B/C) | 证据(文件:行 / 工具名 / 官方页) | 下一步`
- ★ 取证顺序：★ `all_specs()` 工具名 → `scripts/` 实现 → `capabilities.yaml` → `docs/dead-ends.md`
- ★★ **我开工前已看到的三处疑点，必须逐条落实**：
  - ★ 焊件/角撑板（焊件）⇒ ★ `solidworks_weldment_gusset_create` **在工具表里**
  - ★ 钣金/成形工具 ⇒ ★ `solidworks_insert_form_tool` **在工具表里**
  - ★ 钣金/展开折叠 ⇒ ★ `sheet_metal_create_unfold` / `create_fold` **规格 216 已真机建成**
  ★ 另：★ 曲面/旋转曲面（地图记 ✅ **其实未暴露**）⇒ ★ 反向误差，★ 一并留证
- **验收**：★ 12 行**每行都有可复算依据**；★ 与地图口径逐字对照；★ 不许有"待定" ✗

## T-219-02 · B 类（假阴性）批量处置

- ★ 手法见 `plan.md` §二（★ 别名/正名 or 纯暴露；★ **先查生成器取哪个名集合**）
- **验收**：★ G1-G5；★ 且**抽查**：★ 每个"补上"的格，★ 背后能力**真实存在**（★ 能指认源码函数）
- ★★ 红线：★ **不许只改名而不接真实实现** ✓

## T-219-03+ · A 类（真缺口）逐个攻

★ 顺序按域缺口数：★ **装配 3** · **特征 3** · **钣金/焊件 各 2** · **曲面 1** · **其他 1**（PDM 大概率落 C 类）

- ★ 每个：★ 官方页（签名 + Remarks + CHM 例）→ `dead-ends.md` → 该能力 `limitations` → `known-facts.md` → 动手 ✓
- ★ 实现形态：★ 优先 `*_report`（带回读判据）✓
- ★ 真机：★ `python tools/sw_guard.py --timeout N -- python <探针>.py` ✓；★ **用完关 SolidWorks** ✓
- **验收**：★ G1-G5 + ★ **真机读数**（特征树增量 / 几何读数 / 与官方示例同形）✓

## T-219-99 · 收口

- ★ 重跑生成器（★ `--check`）⇒ ★ **逐格核 11 个域**；★ 把最终账写进 `goal-bar.md` ✓
- ★★ **如实**：★ 若仍有未关的格 ⇒ ★ 写明"还差哪几项、属 A 还是 C、为什么" ✓
- ★ 更新 `docs/ROADMAP.md` §一 + 提交 ✓
- **验收**：★ A1-A5（见 `spec.md` §六）✓
