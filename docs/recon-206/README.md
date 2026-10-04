# recon 原始数据集（★ **只读**）—— 登记与使用说明

> 生成物 —— 由 `tools/t5_3_register_recon.py` 产出，不要手改。
> ★ 目的：把另一个对话那两批扫描的**原始 JSON** 登记成**只读数据集**，
> 使后来的人知道**它们是什么、谁维护、能不能改** ✓

## 一 · ★ 铁律（★ 三条，违反其一就会破坏可复核性）

```
① ★★ 这两个目录【只读】—— 它们是【另一个对话】的写盘范围，
   本线（规格 206）**只读复用**，绝不改写、绝不提交（★ 见规格 206 的 git 纪律）✓
② ★★ **不重跑**已跑过的扫描 —— 那些扫描（Bunny 逐页核对）花了对方大量算力，
   重跑既浪费又会产生**与基线不一致的第二份真值** ⇒ ★ 只读现成的 JSON ✓
③ ★★ 引用它们的数据时必须带**口径**：这些是 `conditional_pass` 产出
   （★ 对方 REPORT §七 自陈：C4 只覆盖 91% 箱、丢箱系统偏向尾部 等）
   ⇒ **一律当候选队列，逐条过闸才采纳**（规格 206 的 D-4）✓
```

## 二 · 清单（★ **40** 个 JSON）

### 规格 203 的那批（**10** 个）

| 文件 | 大小 | ★ 已知用途 |
|---|---:|---|
| `a-task-ifaces.json` | 637.7 KB | ★ A 路：任务→接口映射 |
| `b1-merged.json` | 232.2 KB | ★ B1：合并后的扫描结果 |
| `b1-state.json` | 0.5 KB | （未标注） |
| `b2-deadlinks.json` | 136.8 KB | ★ 死链候选 212 条 |
| `b2-defects.json` | 591.2 KB | ★ 官方源缺陷 970 条（verified 964）—— `check_official_source_defects` 的输入 |
| `b2-unknown-classified.json` | 35.6 KB | （未标注） |
| `b3-4-merged.json` | 3700.3 KB | （未标注） |
| `b4-unknown-classified.json` | 13.0 KB | （未标注） |
| `b5-ledger.json` | 163.5 KB | （未标注） |
| `claims-norm.json` | 2113.4 KB | （未标注） |

### 规格 204 的那批（**30** 个）

| 文件 | 大小 | ★ 已知用途 |
|---|---:|---|
| `c1-ab-agreement.json` | 1.8 KB | （未标注） |
| `c1-gate-v1-deepseek.json` | 7.6 KB | （未标注） |
| `c1-gate-v2-bunny.json` | 5.1 KB | （未标注） |
| `c1-gate-v3-bunny.json` | 3.5 KB | （未标注） |
| `c1-truth.json` | 208.9 KB | ★ C1 真值集 |
| `c2-absent-resolved.json` | 3.8 KB | （未标注） |
| `c2-calls-verified.json` | 811.9 KB | ★ C2 调用核验 |
| `c2-gate-v1-deepseek.json` | 9.8 KB | （未标注） |
| `c2-gate-v2-bunny.json` | 7.3 KB | （未标注） |
| `c2-gate-v3-bunny.json` | 4.2 KB | （未标注） |
| `c2-jobs.json` | 57.3 KB | （未标注） |
| `c2-rates.json` | 3.9 KB | （未标注） |
| `c3-gate-v1-deepseek.json` | 10.2 KB | （未标注） |
| `c3-gate-v2-bunny.json` | 9.6 KB | （未标注） |
| `c3-gate-v3-bunny.json` | 2.9 KB | （未标注） |
| `c3-jobs.json` | 318.9 KB | （未标注） |
| `c3-merged.json` | 220.3 KB | ★ 前置对账 98 能力 / 534 条前置 —— T2 的输入 |
| `c4-gate-v1.json` | 10.7 KB | （未标注） |
| `c4-gate-v2.json` | 14.0 KB | （未标注） |
| `c4-gate-v3.json` | 4.1 KB | （未标注） |
| `c4-jobs.json` | 989.4 KB | （未标注） |
| `c4-merged.json` | 2629.5 KB | ★ 内部冲突 598 条（`unit_diff`/`mark_diff` 等）—— T4 的输入 |
| `c5-gap-handcheck.json` | 9.7 KB | ★ 换名已有 24 行 —— T1 别名表的输入 |
| `c5-gate-v1.json` | 8.6 KB | （未标注） |
| `c5-gate-v2-bunny.json` | 6.9 KB | （未标注） |
| `c5-gate-v3.json` | 6.1 KB | （未标注） |
| `c5-triage.json` | 84.9 KB | ★ C5 分诊 |
| `c6-gate-v1.json` | 5.3 KB | （未标注） |
| `c6-gate-v2.json` | 10.8 KB | （未标注） |
| `c6-gate-v3.json` | 8.5 KB | （未标注） |

## 三 · ★ 本线（规格 206）已经从它们里榨出了什么

| 产出 | 用了哪个 JSON | 落在哪 |
|---|---|---|
| 别名表（三道闸 → 留 5 条）| `c5-gap-handcheck.json` | `docs/tool-aliases.md` |
| 前置缺口清单（可机检 102 条）| `c3-merged.json` | `docs/precondition-coverage-gaps.md` |
| 官方源缺陷门禁（修 5 处真断链）| `b2-defects.json` | `scripts/check_official_source_defects.py` |
| 错拼→正确名 130 对 | `b2-defects.json` | `docs/recon-206/spelling-pairs.md` |
| 25 条冲突 + 逐条核 + 判读材料 | `c4-merged.json` | `docs/recon-206/conflicts-25*.md` |
| ★ 写码前必查表（368 成员 / 424 条）| `c4-merged.json` | `docs/recon-206/pre-code-conflict-lookup.md` |

## 四 · ★ 还没榨的（★ 留给接手的人）

- ★ `c4-merged.json` 的 **3709 条 `example_more_specific`**（★ T4-2：对方自标只过单侧闸、10–25% 需复核）
- ★ `c4-merged.json` 的 **`precondition_diff` 324 条**（★ 已进必查表，但未逐条判）
- ★ `c2-calls-verified.json`（812 KB）**本线一次都没用**（★ 可能的用途：与我们自己的调用点对账）

★ **给主线的建议**（★ 只出建议，不替它决定）：
★ 若要把这两个目录固化成数据集，建议**加一条门禁**：断言它们**未被修改**
（如记下各文件的 sha256，改动即报）—— ★ 但那是主线的决定，本文件只登记 ✓
