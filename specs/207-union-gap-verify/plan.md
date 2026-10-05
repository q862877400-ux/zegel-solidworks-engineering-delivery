# 规格 207 · 计划（plan.md）

> **读法**：`spec.md` 定判据（SC）与决策（D）；本文件定**顺序、依赖、派活与写盘边界**；
> `tasks.md` 是逐任务的 checklist 与达成记录。

## 一 · Constitution Check（Spec Kit 要求）

| 检查项 | 状态 | 依据 |
|---|---|---|
| 铁律 1 · 只缝合不发明 | ✅ | 每个候选的**来源是官方 API 文档**（别家只当路标，D-5） |
| 铁律 2 · 先关弹窗、必须有超时 | ✅ | 本轮**不碰 COM**（D-3）⇒ 弹窗风险为零；真机留给后续规格 |
| 铁律 3 · 顶层白名单 | ✅ | 只写 `specs/` `tools/` `tests/` `docs/` `output/`（`output/` 已 gitignore） |
| 铁律 4 · 签名三源互证 | ✅ | 每条候选必须给 `official_signature`（逐字）+ `official_file` |
| 铁律 5 · 查不到就说查不到 | ✅ | schema 里 `official_remarks` / `units` / `dead_ends` 允许「查不到」 |
| 铁律 6 · 许可红线 | ✅ | 记录 `license`；AGPL/GPL/无许可只读思想 |
| 规则 2 · 单位后缀 | ✅ | `proposed_params` 必须写明 `_mm`/`_deg` 与换算边界 |
| 规则 3 · 不许裸坐标 | ✅ | `selection` 必须写声明式选择器 + 前置 mark |
| 规则 6 · 不静默成功 | ✅ | `verification` 必须给 L1–L4 判据 |
| 事实 24（单实例 COM） | ✅ | 全程离线，零 COM 调用（SC-6 验） |
| 事实 62（负例是唯一证明） | ✅ | `tools/verify_union_349.py` 必须带**负例**（故意造一条缺失/一条多余，断言它会红） |

## 二 · 批次与顺序（V0 → V6）

| 批 | 是什么 | 输入（复用，不重跑） | 落点 | 依赖 |
|---|---|---|---|---|
| **V0** | ★ 修我自己的假「实测」声明；把 349 条编成带编号的工作量清单（tier-aware） | `output/union-gap-v3.json` | 工具 docstring · `output/union-workload-349.json` | — |
| **V1** | ①②③档 **#1–#60**（①=验证，②③=深调） | V0 的清单 | 各 bunny 自写 `output/bunny-records/<idx>.json` | V0 |
| **V2** | **#61–#120** | 同上 | 同上 | V1 |
| **V3** | **#121–#180** | 同上 | 同上 | V2 |
| **V4** | **#181–#240** | 同上 | 同上 | V3 |
| **V5** | **#241–#300** | 同上 | 同上 | V4 |
| **V6** | **#301–#349**（49 条） | 同上 | 同上 | V5 |
| **V7** | ★ 汇总：`verify_union_349.py`（SC-1/5/6）· `report_false_positive_rate.py`（SC-2/4）· `list_adoptable.py`（SC-3） | V1–V6 的记录 | `output/union-verify-349.json` · `docs/recon-207/` | V1–V6 |

★ **顺序理由**：V0 先修假声明 —— 不先修，我就是在拿一个假的数去指挥 349 条活（与规格 206 的 T0 同理）。

## 三 · ★ 写盘边界（硬）

```
✅ 我可以写：specs/207-*/ · tools/（新建）· tests/ · docs/recon-207/ ·
            docs/known-facts.md · 我自己写过的那几处 docstring
❌ 我绝不碰：specs/206-*/ · specs/204-*/ · specs/203-*/ · docs/ROADMAP.md ·
            docs/recon/** · capabilities.yaml（level）· scripts/ 里别人的实现
★ 每批提交前先 git reset，只 add 自己这一线的路径（用 tools/commit_mine.py）
```

## 四 · ★★ 派活纪律（V1–V6 共用；这三条是上一轮事故的直接产物）

```
① **一个 bunny 只负责一个操作**，批大小 ≤60（业主给定 + 仓里既有纪律）
② ★★ **返回体不许有散文** —— schema 里 verdict / recommendation 用 **enum**；
   「为什么」写进**受长度约束的短字段**；彻底的长证据由 **bunny 自己写文件**
   （`output/bunny-records/<idx>.json`），**不进返回体** ✓
   ★ 依据（可核）：上一轮我把这两个字段写成自由 string ⇒ 返回体 **1.8 MB**、
     被工具截断、且**JSON 非法**（`Invalid control character` → `strict=False` 后变
     `Unterminated string`）⇒ 逐条映射**全丢**，我只能从 tally 里捞汇总 ✓✗
③ **零 COM** —— 明确写进 prompt 的硬约束（D-3 / 事实 24）
```

## 五 · 每批的固定工序（六步）

```
① 读清单里属于本批的编号（bunny 自查自己的那一条）
② 逐条：认领 → 核分类器线索（**可推翻**）→ 找官方成员与签名 → 查死路 → 查许可
③ ①档只判「是不是已有等价物」并给证据；②③档再起草我方版本
④ bunny 把长证据写进 output/bunny-records/<idx>.json；返回体只回枚举与短串
⑤ 跑 SC-5 的断言（合法 JSON + < 256 KB）
⑥ 落盘 + 提交（只 add 自己的路径）
```

## 六 · 风险与对策

| 风险 | 对策 |
|---|---|
| ★★ 返回体再次超长 ⇒ 截断 ⇒ 逐条映射又丢 | D-7 枚举化 + SC-5 硬断言（< 256 KB）；★ 长证据落文件 |
| ★ 分类器的线索把 bunny 带偏（我上一轮就被带偏） | D-1：prompt 里明写「线索不是结论，**可推翻且鼓励推翻**」；★ 并要求 `classifier_was_right` 字段 |
| ★ 349 条里大部分是重复语义（同一功能多个名字） | ①档只验证不实现（D-2）；②③档才花钱 |
| ★ 并发 60 个 bunny 抢资源 | 零 COM；纯文件读；批间隔串行（V1→V6 顺序 await） |
| ★ 我把 bunny 的结论当结论用 | D-4：Lead 逐条裁；★ 且 SC-4 强制两个数并列 |

## 七 · 完成判据

★ SC-1…SC-8 全绿 + `tasks.md` 逐条勾选 + 每批提交与事实都落盘 ⇒ 方可标完成。
★ 任一批**证据不足以判定**的条目，记「待复核 + 原因」，**不硬标已有/缺口**（沿用 206 的 D-5 口径）。
