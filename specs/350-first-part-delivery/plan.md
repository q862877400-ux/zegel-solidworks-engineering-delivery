# Implementation Plan: S2–S6 — 首件交付族

**Feature**: `350-first-part-delivery`

**对应 PLAN 阶段**: S2 / S3 / S4 / S5 / S6（`docs/ENGINEERING-PATH.md` 第六节）

## Summary

冻结首件需求与最小规则包 → 板件真过 E1–E3 → 接上装配/图样/工艺 →
真实 DeepSeek 端到端 → 限定发布。

**本特性是五个阶段的合并 spec**：它们共用同一首件对象、同一套 E1–E7 判据、
同一份证据链，拆成五份 spec 会产生五套重复的上下文。合并后在 tasks.md 里按阶段分 Phase。

## Technical Context

- 语言：Python 3.14.7
- 真机：SolidWorks（COM），**必须走 `tools/sw_guard.py`**（弹窗护栏）
- 单源：同一时刻只允许一个 SolidWorks MCP 进程（已知事实 24）
- 复用：`scripts/engineering/` 下的 `jobs` / `executor` / `recovery` / `authorization`
- 依赖：`specs/348` 与 `specs/349` 必须先完成

## Constitution Check

| 原则 | 满足方式 |
|---|---|
| I 缝合优先 | 全部复用本仓既有 `scripts/engineering/` 模块与既有 SolidWorks 工具 |
| II 签名三源互证 | **每个新涉及的 COM 调用必须过 CHM + `C:\swapi` + 反射三源**，冲突以反射为准；进 `docs/signature-audit.md` |
| III 查不到就写查不到 | 见下方「待查清单」 |
| IV 许可红线 | 不引入外部代码；复用本仓 MIT |
| V 验收判据能跑 | tasks.md 每条带 `→ 验收:` |

### 待查清单（宪法原则 III）

以下成员名**本文件不杜撰**，必须在 S3 开工前按铁律 4 三源互证后写入：

| 用途 | 待查什么 | 查法 |
|---|---|---|
| E1 草图求解状态 | 读草图欠约束实体数与完全定义状态的官方成员 | `python "$env:USERPROFILE\.agents\skills\mech-design\tools\sw_know.py" member <Type> <Member>` |
| E1 驱动尺寸 | 枚举草图驱动尺寸的官方成员 | 同上 |
| E4 配合状态 | 读配合对象与剩余自由度的官方成员 | 同上 |
| E4 干涉检查 | 干涉检查的官方入口与返回形状 | 同上 |
| E5 图纸标注绑定 | 创建并绑定指定语义尺寸的官方入口（阶段 317 报过 `DRAWING_REQUIRED_DIMENSIONS_UNSUPPORTED`） | 同上 + `docs/dead-ends.md` |

**查不到就写「查不到」并停线**，不得用相似名字蒙混。

## Project Structure

### Documentation (this feature)

```
specs/350-first-part-delivery/
├── spec.md
├── plan.md
├── tasks.md
├── acceptance.md      收口记录
└── evidence/          真机证据（截图、日志、JSON 读数）
```

### Source Code

| 阶段 | 主要落点 |
|---|---|
| S2 | `scripts/engineering/{rules,rule_service,manufacturing_rules,protocols}.py` · 新增需求冻结表 |
| S3 | `scripts/sw_sketch_relations.py` · `scripts/engineering/{part_loop,reference_resolver}.py` · `tools/run_stage2_plate.py` |
| S4 | `scripts/engineering/{assembly,processes,drawing_obligations,drawing_run,compliance}.py` |
| S5 | 宿主接入层（复用 `jobs`/`executor`/`recovery`/`authorization`） |
| S6 | `scripts/engineering/release_manifest.py` · 发布说明 |

## 关键设计决定

### 决定 1：S2 的需求冻结表是**唯一**的需求来源

`scripts/engineering_contract.py` 与 `scripts/engineering/design_ir.py` 二者
各自决定缺项/单位/批准状态的现状必须消除。S2 先做字段归属与调用方对照，
再定唯一权威。

### 决定 2：S3 的原生编辑**必须**在已交付件副本上做

`tools/run_stage2_plate.py` 的 `run_change` 当前是「新建文档重跑」
（出处：`R-engineering-path.md` R-10）。它能证明「新参数重新生成」，
**不能**证明「打开已交付件改既有驱动尺寸」。

S3 必须补后者。本仓已有 `scripts/sw_document_data.py` 的 `update_dimension_mm`
（走 `SetSystemValue3`），S3 复用它与它挂的工具，不新造。

### 决定 3：S4 移除 `drawing_run` 里写死的材料与公差文字

`scripts/engineering/drawing_run.py` 固定追加「材料：45 钢；未注公差按 GB/T 1804-m」
（出处：`R-engineering-path.md` R-11），与请求实际材料无关。
S4 必须改为取批准需求；读取不完整返回 `unknown`。

### 决定 4：S5 的「真实」指真实模型，不是测试脚本代填

测试脚本偷偷代填工具序列 = 没验证模型。S5 的验收场景必须由真实 DeepSeek 驱动。

### 决定 5：S6 的发布范围宁窄勿宽

发布说明写「支持这些参数域、这些工艺、这个 SW 版本」，不写「机械设计全覆盖」。
超出范围必须拒绝，不勉强生成。

## Complexity Tracking

| 项 | 为什么需要 | 更简单的替代为何不够 |
|---|---|---|
| 五个阶段合并一份 spec | 共用同一首件与同一套判据 | 拆五份会产生五套重复上下文，且跨阶段证据链对不上 |
| S3 补「改已交付件」而非只「新建重跑」 | 这是 E2/E3 的实质要求 | 用新建重跑冒充，等于 E2/E3 从未被真正验证 |
| 单独 `evidence/` 目录 | 真机证据是交付包的一部分，必须版本绑定 | 混在 `output/`（gitignore）会丢证据 |
