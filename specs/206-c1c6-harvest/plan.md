# 规格 206 · 计划（plan.md）

> **读法**：`spec.md` 定判据（SC）与决策（D）；本文件定**顺序、依赖、派活与写盘边界**；
> `tasks.md` 是逐任务的 checklist 与达成记录。

## 一 · ★★ 先摆一个判断：六件里只有一件直接服务「检索命中」

```
C5（别名）    ⇒ ★★ 唯一【直接】提升检索命中的（词面不同、语义相同 ⇒ 别名即可命中）
C1–C4 · C6    ⇒ 服务的是「不出错」（纠错 / 前置 / 冲突 / 治理）

★ 而按我前面的实测（真模型自己挑 87–91%，前二 96%），【不出错】的当前价值高于【提召回】
⇒ 两条线都做，但【派活批次必须分开】（一个 job 一个批次）
★ 顺序上把 T0（修判据）放最前，因为不先修它，后面每一个"改善"的数字都不可信
```

## 二 · 批次与顺序（T0 → T5）

| 批次 | 线 | 是什么 | 输入（复用，不重跑）| 落点 | 依赖 |
|---|---|---|---|---|---|
| **T0** | 判据 | ★★ 修我自己的检索探针：加 `METRIC_SCOPE` 口径块（口径 · 归一化层级 · **不算什么** · 顺序固定）+ 给头条数字上三裁判 | 我这几轮的 6 个探针 | `tools/probe_*.py` 的模块头 + `output/metric-scope-*.json` | — |
| **T1** | ★ 检索命中 | ★★ 别名表：24 条「换名已有」→ 别名行接进工具 `doc` | `c5-gap-handcheck.json`(27) · `c5-triage.json`(349) | `docs/tool-aliases.md` + 433 个 ToolSpec 的 `doc`（**只追加**）| T0（要用带口径的复测） |
| **T2** | 纠错 | ★★ 前置断言（治假绿测试）| `c3-merged.json`(220 KB) · `precondition-vs-evidence.md` | `tests/test_preconditions_*.py`（**带负例**）+ 给主线的清单 | T0 |
| **T3** | 纠错 | 官方源缺陷：先机械复核 212 条死链 ⇒ 再做门禁 ⇒ 与既有手工表合流 | `official-source-defects-2.md`(964) + 本机 566 接口/963 枚举名字集合 | `scripts/check_official_source_defects.py` + `tests/` + `docs/official-source-errors.md`（合流）| — |
| **T4** | 纠错 | 冲突：先 25 条（`unit_diff` 15 + `mark_diff` 10）⇒ 再复核 3709 条 ⇒ 接成"写码前必查表" | `c4-merged.json`(2.6 MB) · `official-internal-conflicts.md` | `docs/recon-206/conflicts-25.md` + `AGENTS.md` 加一行链接 | — |
| **T5** | 治理 | `fact-single-home` 告警 · `competitor-signature-crosscheck` 归档 · 原始 JSON 只读登记 | 三份表 + 30 JSON | `scripts/check_fact_single_home.py`（告警级）· `docs/recon-206/README.md` | T1–T4（产物落位后） |

## 三 · ★ 写盘边界（硬）

```
✅ 我可以写：specs/206-*/ · scripts/check_*.py（新建）· tests/ · tools/ ·
            docs/known-facts.md · docs/metrics.md · docs/tool-aliases.md ·
            docs/recon-206/ · mcp-server/tool_specs_batch*.py（仅 doc 追加）
❌ 我绝不碰：specs/204-*/ · specs/203-*/ · docs/ROADMAP.md · docs/recon/** ·
            capabilities.yaml（level）· scripts/ 里别人的实现（除有证据的 bug）
★ 每批提交前先 `git reset`，只 add 自己这一线的路径
```

## 四 · 每批的固定工序（七步）

```
① 读输入（JSON 优先，不读散文的表）  ② 机械预处理（join / 去重 / 复核）
③ 派活（5 路探针 → ≤60 路；一个 job 一批次；一路一份）
④ 两道闸：引文逐字回查 + 三裁判
⑤ 落地（门禁 / 测试 / 表 / doc 追加）
⑥ 验收：跑 spec.md 的对应 SC；三门禁全绿（check_param_binding / check_union_conventions / release_check）
⑦ 逐批 git 提交（只 add 自己路径）+ 写事实
```

## 五 · 风险与对策

| 风险 | 对策 |
|---|---|
| ★★ 把 `conditional_pass` 的结论当结论用 | D-4：一律候选队列；每条采纳前过闸（SC-3/SC-4 的抽检） |
| ★ 宽判据导致假阳性（支线实测 33%）| D-1：误报率 ≤5%；不达标进「待复核」桶 |
| ★★ 大 `parallel` 锁死整批（我上几轮的失败根因）| 派活纪律②：一个 job 一个批次 |
| ★ 改 433 个 `doc` 造成 schema 膨胀 | D-2：**只追加别名行**；★ 逐批复测 token 体量（现成的 `probe_tool_surface_language_overlap`） |
| ★ 与另一个对话写盘冲突 | 第三节的硬边界 + 每批 `git reset` |
| ★ 前置断言只能"看起来对" | SC-2：**负例是唯一证明**（本仓定则） |

## 六 · 完成判据

★ 六条 SC 全绿 + `tasks.md` 的逐条勾选 + 每批的提交与事实都落盘 ⇒ 方可标完成。
★ 任一批若**证据不足以采纳**，其产物记「待复核 + 原因」，**不硬标完成**（FR-002/D-5 的既有口径）。
