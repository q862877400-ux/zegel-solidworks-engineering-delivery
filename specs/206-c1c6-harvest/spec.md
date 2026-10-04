# 规格 206 · C1–C6 收获（C1C6 Harvest）：把支线产物接成主线的资产

> **一句话**：另一个对话的 C1–C6 支线已经产出**六份可核对的表 + 30 个原始 JSON**（全机器可读）；
> 本规格把它们**尽可能榨干**，接成主线的**门禁 / 测试 / 别名表 / 治理告警** —— 三条线：
> **纠错 · 提升检索命中 · 治理**。
> ★ 本规格**不重跑**支线已跑过的扫描（只复用 JSON），也**不碰** `specs/204-*`。

## 一 · 定位与前提

| 项 | 值 |
|---|---|
| 输入 A | `docs/recon/` 六份表：`official-internal-conflicts.md`(1391 行) · `precondition-vs-evidence.md` · `union-gap-tristate.md` · `fact-single-home.md` · `multiway-agreement.md` ＋ 既有产品 `official-source-defects-2.md`(142 KB · 964 条) · `member-to-example-index.md`(652 KB) · `member-inventory.md`(176 KB) |
| 输入 B | `specs/204-bunny-moat-batches/recon/` **30 个原始 JSON**（★ 结构化，含 `quote_ok/quote_bad` 分列）—— `c4-merged.json` **2.6 MB** · `c2-calls-verified.json` **812 KB** · `c3-merged.json` 220 KB · `c1-truth.json` 209 KB · `c5-gap-handcheck.json` 27 条 |
| 输入 C | `specs/204-bunny-moat-batches/verifiers.md`（三裁判门禁设计）＋ REPORT §四（派活硬约束） |
| ★★ 前提 | **支线的六件全是 `conditional_pass`**：裁判找到问题后作者改了产物、**没有重跑门禁** ⇒ ★ **一律当候选队列，逐条过闸才采纳** |

## 二 · 成功条件（SC，全部机械可测）

| # | 判据 | 怎么验 |
|---|---|---|
| **SC-1** | ★ **别名表生效**：48 题复测的检索/选择正确率**相对基线提升**，且**带口径声明** | `tools/measure_rag_*` 复跑 + 结果表 |
| **SC-2** | ★ **≥3 条「原本假绿」的测试被证明并修正**（治已知事实 57），且每条断言**配负例** | `tests/` 的负例用例 |
| **SC-3** | ★ **官方源缺陷门禁**在**修复前的原文**上命中（`git show <rev>^:<path>` 取负例），且**误报率 ≤5%**（抽检 20 条假阳性 ≤1） | `tests/test_official_source_defects_gate.py` |
| **SC-4** | ★ `unit_diff`(15) + `mark_diff`(10) **25 条逐条有结论**（成立 / 不成立 / 查不到） | `docs/recon-206/conflicts-25.md` |
| **SC-5** | ★★ **所有头条数字带口径声明**（口径 · 归一化层级 · **「不算什么」** · 顺序固定），且过三裁判（零「编造/口径」类反例） | 探针模块的 `METRIC_SCOPE` 块 + 三裁判 JSON |
| **SC-6** | ★ **一个事实一个家**：每批落点唯一，**不产生第二份同义表** | 逐批检查（`official-source-errors.md` 必须与穷举版合流） |

## 三 · 决策记录（★ 业主已授权我全权拍板）

| # | 决定 | 理由 |
|---|---|---|
| **D-1** | ★ 新建门禁的**误报率 ≤5%**（抽检 20 条、假阳性 ≤1）；**未达标的条目留「待复核」桶、不进门禁** | 支线实测：C1 抄录编造率 0.15% · C4 抽检 12 条只 4 条真互斥(33%) ⇒ ★ 宽判据是主要风险 ✓ |
| **D-2** | ★ **允许改工具 `doc`，但只「追加」别名行**；**不动** schema 契约 / 参数名 / 注入键 | ★ 词面不同、语义相同是 24/27 的真实成因；改动逐批提交、可回退 |
| **D-3** | ★ 真机验证**一次一个**、走 `tools/sw_guard.py`、**每批 ≤5 条断言** | 合本仓既有纪律（弹窗护栏 · 单会话 COM） |
| **D-4** | ★★ 支线结论**一律候选队列**，逐条过闸才采纳 | 六件全是 `conditional_pass` |
| **D-5** | ★ **只产出清单，不替主线改** `capabilities.yaml` 的 `level` | 支线明说那是主线的决定 |
| **D-6** | ★ **绝不碰** `specs/204-*` · `specs/203-*` · `docs/ROADMAP.md` · `docs/recon/**` | 另一个对话的写盘范围 |

## 四 · 派活纪律（★ 照抄支线实测出来的硬约束）

```
① 产出【只用】Bunny（`opencode-zen` / `space-bunny-free`），provider 与 model 成对写
② ★★ 一个 job 一个批次 —— `parallel` 是【全等】语义，一个 hang 锁死整批
③ 一路一份（不合并）；一波 ≤ 60 路；每件先 5 路探针；`returned: 0` 当失败查
④ ★★ 两道闸：① 引文【逐字回查】原文（挡 0.15% 编造）② 三裁判（不同模型 + 不同视角）
⑤ ★ 三票不齐只记 `conditional_pass`，不写完成
```

## 五 · 明确不做（★ 每条有依据）

| 不做 | 依据 |
|---|---|
| ✗ 重跑 C1–C6 的扫描 | 原始 JSON 已结构化、可复用 ⇒ 重跑是浪费 |
| ✗ 改 `capabilities.yaml` 的 `level` | D-5 |
| ✗ 把 3709 条 `example_more_specific` **直接**当"该补的 doc"用 | 支线自标：**只过单侧闸**，V1 估 10–25% 需复核 |
| ✗ 把 544 条冲突**直接**当"官方错了" | 支线自标：抽检 12 条只 4 条真互斥 ⇒ 真冲突约 220–270 |
| ✗ 用 `search_miss` 那类"未使用过的模板"当证据 | 支线实测：该模板从未被使用（0 条） |
| ✗ 把支线的百分比直接搬进本仓结论 | D-4 + SC-5 |
