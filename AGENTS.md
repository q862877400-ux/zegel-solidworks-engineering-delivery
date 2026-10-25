# AGENTS.md

本文件是 SolidWorks 工程交付系统的常驻指令；仓库根——2026-10-03 起代码与产物在同一个仓库里（原先的代码工作副本`C:\swprojects\sw-skill-fork\`已成只读归档，见 §七）。跨项目的通用纪律在`~/.dsh/AGENTS.md`（用户全局层，每轮自动注入）——缝合优先、签名以官方源为准、查不到就说查不到、许可红线、把验证责任转移到静态比对、验收判据写成可 grep 项；本文件只留 SolidWorks 专属的事实与规矩。

接手第一件事：读四份——[`docs/PROJECT-CHARTER.md`](docs/PROJECT-CHARTER.md)（目的与 E1–E7）、[`docs/ENGINEERING-PATH.md`](docs/ENGINEERING-PATH.md)（路线与 S0–S6 施工顺序）、[`docs/PLAN.md`](docs/PLAN.md)（当前游标与调整机制）、[`docs/state/INDEX.md`](docs/state/INDEX.md)（实测台账，每条带复现命令；或调用 `sw-project-state` skill）。不要通读 55 万行；要报数字先跑 `docs/state/probes/` 里的探测器，别凭记忆。

## 十二、仓库（第一件事，先确认你在哪）

| 路径 | 是什么 | 能改吗 |
|---|---|---|
| `.` | 仓库根——代码（`scripts/` `mcp-server/` `tests/` `tools/` `apps/` …）与产物（草稿/日志/报告/证据）同在一处 | 改代码与放产物 |
| `C:\swprojects\sw-skill-fork\` | 合并前的代码副本，只读归档（历史与上游对照在其中） | 只读 |
| `C:\swprojects\<owner>\` | 四家外部 MCP 项目的克隆 | 只读对照 |
| `C:\swprojects\sw-automation-skill\` | 上游的另一份克隆 | 只读对照 |
| `AI Solidworks\` | SolidWorks 工作区（官方文档/手册/模型/截图） | 只读 |
| `docs\` | 本文件里 `docs/...` 相对 AGENTS.md 解析到这里；知识文档与任务产出同在一处 | 可改 |

`仓库根`是 git 仓库（提交`1f86c5d`起；2026-10-03 并入代码（入库文件数见 docs/state/facts/A-structure.md A-02））；`.gitignore`排除了 398 MB（官方文档/反射转储/探索截图/CAD 保真数据）。

任务报告与代码都放`仓库根`下。`AI Solidworks\`是模型/截图/手册，不是代码落点。

## 十三、动手核一条路之前：先扫「已走死的路」

`docs/dead-ends.md`（`tools/gen_dead_ends.py` 生成，不要手改）。（依据见 [`docs/agents-rationale.md`](docs/agents-rationale.md#13-deadends)）

## 十四、官方文档是第 0 步

**动手碰任何一个 API 成员之前，先读完它那三样**：① `C:\swapi\types\<接口>\<成员>.md`的签名、② 它的`## Remarks`（前置与语义都在这）· ③ CHM 那页顶上的`Example`/`See Also`（例子给的是"调用序"，签名与 Remarks 都给不了）。⇒"试参数"是最后手段——★读完仍不成才开探针，★且探针`来源块`要写明读的是哪一页。顺序：① 官方页 → ② `docs/dead-ends.md` → ③ 该能力的`limitations` → ④ `known-facts.md` → ⑤ 动手。第 0.5 步：碰下面这些成员前，先查 [docs/recon-206/pre-code-conflict-lookup.md](docs/recon-206/pre-code-conflict-lookup.md)——它列了 368个成员/424条「官方`## Remarks`与官方示例不能同时成立」的位置（`unit_diff` 15、`mark_diff` 10、`return_shape_diff` 75、`precondition_diff` 324）⇒照示例写可能就写错了 ✓（★样例：`AutoDimension2`的 Remarks 要求基准打`swAutodimMark*`，而示例用没有 mark 形参的`Select4`却声明成功）（依据见 [`docs/agents-rationale.md`](docs/agents-rationale.md#14-official-first)）

## 〇、一句话任务

> **项目目的见 [`docs/PROJECT-CHARTER.md`](docs/PROJECT-CHARTER.md)**：把中国机械设计的规范与判据编译成能力，使一条指令产出的模型达到可交付水准（全约束 · 参数化可重建 · 特征树可编辑 · 装配自由度闭合 · 图样合规 · 工艺可行 · 结论可溯源）。验收判据是 charter 第 4 节的 E1–E7，不是工具条数。
> **怎么做到见 [`docs/ENGINEERING-PATH.md`](docs/ENGINEERING-PATH.md)**：四个选择、三类资产（规则包/方法包/验收包）、E1–E7 的采集器与判定器、施工顺序 S0–S6、首件范围、旧工作包迁移表。

- 集大成 · 建护城河的定位是手段（取材地图 / 差异化参考），不是目的、不计分（依据见 charter 第 2 节）。
- **先验收后能力**：S1（E1–E7 判据与坏样件）不成立就写新能力，等于继续用「条数」冒充进展。每个任务必须能回答：服务哪个首件要求、改善哪条 E、增加哪个可重复试验。
- **采集器与判定器分开**：采集器从实际产物取数，判定器对冻结要求判断。规划器不能提交「我已经检查过」代替观测。
- 正规军：命名/单位/选择/验证等级/出处五统一，机器门禁 docs/union-conventions.md + scripts/check_union_conventions.py。
- 单源交付：运行时只能有一个 SolidWorks MCP——多个进程抢同一 COM 连接会死锁（已知事实 24）。

## 十四之二、单位必须出现在名字里（米/毫米反复出错的根治）

**★★★ 一句话：任何带量纲的形参，名字里必须有单位后缀。**

```bash
python -B scripts/check_internal_length_units.py --inventory   # 看全量纲清单
```

- **硬门禁**已接进 `release_check`（`_run_unit_naming_gate`），基线
  `docs/unit-naming-baseline.json` **只许降不许升**。
- 追的是**这个根因**：本仓两套约定并存、形参都是裸名 ——
  `sw_part.sketch_circle(cx, cy, radius)` 收**毫米**，
  而 `sw_assembly.add_component(x, y, z)` 收**米**（工具层已 `mm()` 换算过）
  ⇒ **调用方无从分辨**。实测：探针传 `30.0` 想表达 30mm，组件被放到 **30 米**外；
  更糟的是射线选中的两个面因此都落在同一个组件上，
  「两组件配合」这个前提从未成立 —— 我在一个**假问题**上排除了 12 个候选。
- 后缀白名单按量纲分开：`_mm`/`_m`（长度）、`_deg`/`_rad`/`_degminsec`（角度）、
  `_s`/`_ms`（时间）、`_n`/`_kn`（力）、`_mpa`（应力）、`_nm`（力矩）、
  `_hz`（频率）、`_g`/`_kg`（质量）、`_mm2`/`_mm3`（面积/体积）等。
- ★ **选择器不算量值**：`force_type` / `length_unit` / `draft_analysis` 是「选哪个」，
  不是「多少」⇒ 门禁不报（否则误报会让人把门禁整条关掉）。
- ★ **改形参名必须跑一次真机**：只改签名不改函数体会得到
  `NameError`，静态检查抓不到（第 60 轮实测踩过）。

## 十四之三、人工验收：四步协议（业主 2026-10-26 指令）

**机器判据绿 ≠ 人工验收过。两者都要，缺一不算。**

业主原话：「很多操作你还是做一遍给我看，然后我人工确认一下吧，免得你机器判据问题，
你以为验收了实际上不对。」

四步（**阶段之间必须停顿等人**）：① 计划（做什么 + 怎么判定）② 准备（摆好场景、
说明「你现在应该看到什么」、**停下等人说对**）③ 执行 ④ 结果确认（说明「现在应该是什么样」、
给前后读数对照、**停下等人说确实**）。

全文与判据盲区实录：[docs/human-acceptance-protocol.md](docs/human-acceptance-protocol.md)。
工具：tools/coop_step2_prepare_mate.py / tools/coop_step3_execute_mate.py /
tools/sw_screenshot.py。
★ 不许替业主说「他确认了」；他没答就在报告里写「待人工确认」。

## 十四之四、动手前先查「已有资产名单」（业主 2026-10-26 指令）

**★★★★★ 凡涉及项目已有的东西，用现成的，不要纯手搓。**

业主原话：「但凡是涉及到我们项目已有的东西，就得用现成的……我们各种元素叫什么名字，
我们现在肯定是已经有了。」

- **名单**：[docs/existing-assets.md](docs/existing-assets.md) —— 元素名 / 定义状态 / 单位 /
  几何读取 / 特征参数 / 选择 / 装配 / 图样分别落在哪个模块，以及先看哪几个名字。
  只挂名单，正文留在各模块 docstring。
- **同一个东西只许有一个名字**：草图元素与关系用 `SKETCH_RELATION_ENTITY_TYPES` /
  `SKETCH_CONSTRAINT_TYPES`，非草图元素用 `ENTITY_KINDS`，定义状态用 `sw_sketch_status`，
  官方枚举用 `scripts/sw_enums.py`（生成物），数值换算用 `sw_units.dimension_reading`。
- **要扩展就改原模块**；两张表并存时必须加**同值一致性测试**（用显式同义词映射，
  模糊匹配会掩盖真漂移）。
- 实测代价（2026-10-26，三处均为「手搓替代既有」）：手写「草图点/草图线段」对不上
  `point/line`；手写 `{2:欠定义,3:完全定义}` 漏掉过定义(4)/无解(5)/无效解(6)；
  `ISketchArc` 的半径真名是 `GetRadius` 而 `Radius` 根本不存在 ⇒ 圆没有半径。

## 十五、真机命令一律走弹窗护栏

**★★★★★ 通用护栏：`tools/guard_run.py`（2026-10-26 用户要求，长效机制）**

```bash
python -B tools/guard_run.py --timeout 300 -- <任意命令…>
python -B tools/guard_run.py --since        # 只看「上一轮之后还开着的弹窗」
```

- **任何工具都可能弹窗**（不只 SolidWorks）：我用 `psr.exe` 时因上一个实例还在跑，
  它弹了「步骤记录器的某个实例正在运行中。」——**命令不输出也不退出，我就干等超时**。
- 护栏把这件事变成**输出的一部分**：开跑先报遗留弹窗；运行中每 300ms 扫新 `#32770`，
  一出现就抓**文字 + 截图**并杀掉子进程树；结束**必打** `VERDICT:` 行
  （`OK` / `EXIT n` / `DIALOG <弹窗文字>`）。
- ★★ 纪律：**命令没有输出或眼看要超时 ⇒ 第一件事是查弹窗台账**
  （`python -B tools/guard_run.py --since`），不是继续等。
- ★ 证据落在 `output/dialogs/`（`events.jsonl` + 截图）。

**★★★ 弹窗监控必须常驻（2026-10-26 用户要求）**

```bash
python -B tools/sw_dialog_watch.py --ensure   # 幂等：在跑就返回 0，没跑就后台起
python -B tools/sw_dialog_watch.py --status   # 看它活着没、最近扫到什么
```

- **每轮收尾链会调 `--ensure`**（`tools/round_chain.ps1`），所以正常开发时它一直在。
- ★ 为什么必须常驻而不是「碰到了再点」：`SLDEXITAPP.exe` 的
  `SOLIDWORKS Design 错误报告`（CEIP 遥测发送失败）**点掉即重弹** ——
  第 45 轮实测 2 分钟内被点了 **13 万余次**仍在弹，用户看到一堆 `SOLIDWORKS Rx` 窗口。
  ⇒ 现在的处置是**结束报告器进程**（`_REPORTER_EXES`），不是反复点它。
- ★ 日志去重：同一弹窗（同 exe/类/标题/首文本）**60 秒内只记一行**，之后累加 `repeat`。
  去重前 `output/dialog-watch/events.jsonl` 长到 **254 MB**。
- ⚠ 实机观察：`ISldWorks.Visible=False` 时消息框**根本显示不出来**，
  `SendMsgToUser2` 会直接回 `swMbHitOk`（0.4 秒）—— 别把它当「监控没工作」。


```
python tools/sw_guard.py --timeout 600 -- python <你的脚本>.py     # ★ 以后真机命令都这样起
python tools/sw_guard.py --scan                                    # 只看现有弹窗（不点）
python tools/sw_guard.py --clear                                   # 扫 + 两段式点掉（循环，直到 0 个）
python tools/sw_guard.py --report                                  # 打印历史弹窗事件
```（依据见 [`docs/agents-rationale.md`](docs/agents-rationale.md#15-guard)）

- 处置分两级：`auto`（唯一语义明确的确认按钮）自动点；`needs_llm`/`forbidden` 不点，并立刻 `taskkill` 冻住的调用，把证据交回（原地等 LLM = 死锁）。
- 判据不认类名：认 SolidWorks 家族进程 + 像弹窗 + 家族内兜底，契约测试 `tests/test_sw_guard_dialog_tiers.py` 必须继续绿；其余 5 条设计要点见 [`docs/agents-rationale.md`](docs/agents-rationale.md#guard-design)。

## 十六、每轮收尾链

```
pwsh -File tools\round_chain.ps1 -Tests tests/<改过的>.py
```

实测 34.8 s（生成器 2.1 s + `release_check` 31 s + 聚焦测试）。不要再手打 6 步链、不要每轮跑全量 pytest。（依据见 [`docs/agents-rationale.md`](docs/agents-rationale.md#16-round-chain)）
- **不要再单独跑** `check_union_conventions.py`/`check_param_binding.py`/`check_digest_freshness.py`/`check_report_freshness.py`（`release_check.py` 内部已含）；全量 pytest 只在两种情况跑：发布前 · 改了 `sw_connect.py` 或门禁本体。

## 十七、写探针验能力时：按`ToolSpec`的契约调，别手调内部实现

按 `ToolSpec` 的契约准备实参（`rc.all_specs()` 读 `inject`/`params`）；只有工具层本身有 bug 才调内部实现。（依据见 [`docs/agents-rationale.md`](docs/agents-rationale.md#17-probe-contract)）

配套：若工具层真有 bug（如`resolve_study`少解包一层），要在工具层修，并在记录里写清"探针按契约调之后仍失败⇒是工具层的问题"。

## 十八、新建`.py`的模板：docstring 只写一行，来源块紧随其后

模板就是：一行 docstring + 空行 + `# ── 来源 ──` 六字段块 + `from __future__ import annotations`。可复制的原文见 [`docs/agents-rationale.md`](docs/agents-rationale.md#py-template-code)。（依据见 [`docs/agents-rationale.md`](docs/agents-rationale.md#18-py-template)）

## 十九、SolidWorks 卡死：探不通就处置，不要"再探一次"

`tools/reclaim_solidworks.py --probe` 只探 · `--restart` 处置并复验（打开的文档不全是自己的就拒绝重启）。（依据见 [`docs/agents-rationale.md`](docs/agents-rationale.md#19-reclaim)）

## 十一、汇报频率

默认不汇报；三种情况发一条（≤3 行，只写结果与影响）：一批做完 · 同一处卡住 ≥2 次 · 思路需调整。进度写进 `capabilities.yaml` 与 `docs/` 下的进度台账，不在对话里复述。

## 一、验收标准（逐条全文见 [docs/acceptance-criteria.md](docs/acceptance-criteria.md)）

| # | 判据 |
|---|---|
| **A1** | 工程合格优先：按 charter 第 4 节的 E1–E7 验收，不看工具条数 |
| **A2** | 两层 provenance（来源级 + 能力级）齐 |
| **A3** | 五统一门禁通过 ← **任何时候都该绿** |
| **A4** | `level` 取自五级枚举，`verified` 有自有运行证据 |
| **A5** | COM 调用参数顺序与类型对齐官方签名 |
| **A6** | 许可无越界（AGPL/GPL/无许可不抄） |
| **A7** | 全文无「把 `stitched` 写成 `verified`」 |
| **A8** | 进度按 S0–S6 报：走到哪步、该步完成标准是否满足、首件 E1–E7 逐条状态与证据变化 |
| **A9** | 规范层（L2）可查、结论能指认标准条款 |
| **A10** | 按需搬取，每件过「并入六条规则」 |

进度与下一步看 `capabilities.yaml`（每条带 `level`，`verified` 另带 `evidence`）——状态由清单承载，不写进本文件。

## 二、六条铁律

### 铁律 1、只做「缝合」，不做「发明」

四种合法来源：① 官方 API 文档（定接口与参数顺序）· ② 其它开源项目（移植/改写，留来源头注释）· ③ 四家外部 MCP 项目（按 `provenance` 标来源与许可）· ④ 本项目自身既有模式。逐个例子见 [`docs/agents-rationale.md`](docs/agents-rationale.md#ironlaw1-sources)。

不可接受：凭印象写一个`FeatureManager.XXX(...)`然后「看着像对的」。

### 铁律 2、可以实测，但必须先关弹窗、必须有超时

验证顺序：静态签名比对（前置筛查）→ 本机实测（真跑，用`mcp__solidworks__*`或直接调 COM）→ 两关都过，才允许在文档里写「已验证/实测/跑通」。实测的三条安全约束：

- 先置`ISldWorks.CommandInProgress = True`——未抑制的模态对话框会把会话永久挂起，这是无人值守挂起的头号原因。
- 每个 COM 调用设超时——COM 是 STA 且线程亲和，调用一旦开始无法强制中止；超时只救「等待」，救不了线程，超时后不要重试同一进程。
- 收尾必做——`CommandInProgress = False`、释放 COM 引用、关掉自己开的文档。

红线：破解相关（SolidWorks-CAD/Solidworks-Crack 类投递页、破解指南）零接触；不动注册表/全局环境变量/系统层；未经确认不`git push`/不建目标远端仓库/不发 release；不删用户数据。

### 铁律 3、结构按顶层白名单，不临时起目录

**结构目录**只允许这 14个：`.github` `agents` `ai_team` `apps` `assets` `docs` `dotnet` `examples` `mcp-server` `references` `scripts` `subskills` `tests` `tools`（前 13个上游就有，`tools`是我们加的）。新增白名单外的顶层目录，要在本节登记它是什么、为什么放不进已有目录，再动手。

**产物/缓存目录**允许存在于工作树，但必须 gitignore、不入库：`.api-signatures`（签名索引）、`output`（构建产物）、`.pytest_cache`（pytest 缓存，须 ignore）。

**归档目录**：`archive/root-scratch/`（仓库根历史草稿 2814 个）与 `docs/history/`（历史文档与旧工程方案）都是只搬不删的追溯区，不被任何门禁扫描。两者的登记、判据与守恒断言见 [`docs/layout-registry.md`](docs/layout-registry.md)。

**顶层目录实况**（磁盘 42 个 = 39 仓库目录 + 3 工具缓存；白名单外 25 个的逐个说明见 [`docs/layout-registry.md`](docs/layout-registry.md)）。新增白名单外目录仍须「先登记、再动手」。

新文件落进已有位置：实现进 `scripts/`，知识文档进 `references/`，测试进 `tests/`，说明与生成物进 `docs/`（上游目录树见 [docs/upstream-layout.md](docs/upstream-layout.md)，是参考不是约束）。

### 铁律 4、签名三源互证，冲突以出厂类型库为准

本机有两套官方离线源，各有长短，都要查：`AI Solidworks\官方文档\`（CHM 解包，权威、带说明与示例，查语义与用法）与`C:\swapi\`（结构化 markdown，查精确签名与枚举值）。各源覆盖范围与检索入口见 [docs/sources.md](docs/sources.md)。

出厂类型库是第三套源，也是冲突时的裁决者：`FeatureFillet3`在本机类型库里有 14个参数，官方文档写 7个。口径是三源互证——文档、反射、CHM；冲突时以出厂类型库的反射为准。不凭记忆、不凭反射猜参数、不照抄其它项目的注释。

### 铁律 5、查不到就说查不到

两套源都查不到 → 写「查不到」并停下换思路，不要用相似名字蒙混。名字缺席 = 官方 API 里没有这个成员，不是「没写文档」。

### 铁律 6、许可红线，一次都不能越

| 许可 | 能做什么 | 义务 |
|---|---|---|
| MIT | 读、抄、改、商用 | 保留版权声明 |
| Apache-2.0 | 读、抄、改、商用 | 保留`NOTICE`（`Slacker-LLC/solidworks-mcp`是`Copyright 2026 JIALE LIU`）+ 声明改动了哪些文件 |
| AGPL/GPL | 只读思想 | 不抄代码、不抄文本 |
| 无许可/全版权保留 | 只读思想 | 同上 |

- **单源运行**：运行时只能有一个 SolidWorks MCP——多个进程抢同一 COM 连接会死锁（已知事实 24），所以 MCP 选型就是运行时依赖选型：只在 MIT 那份上跑，AGPL 的 SolidPilot 只读思想。

Apache-2.0 的 NOTICE 义务跟着分发走：一旦入库，推送任何远端时都要带`THIRD-PARTY-NOTICES.md`——该文件已存在；MIT 来源（上游与`Eduardof0nt`/`andrewbartels1`/`vespo92`）保留各自的版权声明。完整许可判定表与来源清单见 [docs/sources.md](docs/sources.md)。

## 三、上游仓库结构（对照参考）

上游的目录树、`scripts/` 现有模块清单与新增模块的硬性要求见 [docs/upstream-layout.md](docs/upstream-layout.md)。它是对照参考与取材地图，不是我们的结构约束——我们自己允许哪些顶层目录，看铁律 3。

## 五、工作方法

**施工按 S0–S6 的顺序推进，判据先行**（逐条见 [`docs/ENGINEERING-PATH.md`](docs/ENGINEERING-PATH.md) 第六节）：S0 恢复正式通路 → S1 先做 E1–E7 判据与坏样件 → S2 冻结首件需求与最小规则包 → S3 原生可编辑板件真过 E1–E3 → S4 接上装配/图样/工艺 → S5 真实 DeepSeek 端到端 → S6 限定发布与扩展。

取材与归一五步（每个方法包的内部动作）：① 建全景与对差 → ② 找来源（上游 > MIT > Apache > 只读思想 > 照官方自建）→ ③ 归一（五统一）→ ④ 标 `level` 与 `provenance` → ⑤ 门禁与实测。每步的产出文件与判据见 [`docs/work-method.md`](docs/work-method.md)。

**每个任务开工前先回答三问**：服务哪个首件要求、改善哪条 E、增加哪个可重复试验。答不出就不进当前迭代。

## 六、已知事实（完整表在 [`docs/known-facts.md`](docs/known-facts.md)）

全文在 [`docs/known-facts.md`](docs/known-facts.md)（条数以该文件为准）。动台账/源码长字符串、或写「先写文件再把路径交给 COM」的探针前，先读事实 560（三条方法论）。新增事实追加进该文件并同步条数。

### 速查：最常查的 21 条在哪

事实 1 / 2 / 8 / 9 / 12 / 24 / 32 / 33 / 36 / 40 / 43 / 47 / 48 / 51 / 53 / 55 / 57 / 58 / 59 / 61 / 62 —— 正文全在 [`docs/known-facts.md`](docs/known-facts.md)（按编号跳）；本文件只留编号（一个事实一个家）。三条方法论总纲见事实 560。

## 七、Git 规则（细节与批准表见 [docs/git-rules.md](docs/git-rules.md)）

- **仓库**：`.` 唯一；`upstream` = 上游（只读）;`origin` 故意留空（裸 `git push` 无处可去）。三条红线（不豁免）：删数据/删仓库/强推 · 对外发布 · 只有用户能给的东西（凭据、业务口径）。
- **提交**一律走 `python tools/commit_mine.py -m <信息文件> <路径…>`，信息先写成文件；禁止裸 `git commit -m "<多行带引号字符串>"`（PowerShell 会把引号/换行当 pathspec ⇒ 假提交）。
- **要批准才做**：`git push`（任何远端）· 建自建仓库/加目标远端 · 提 PR/发 release。本地 commit/branch/`git add`/改文件不需要批准。

## 八、智能体团队分工

**多用 space-bunny**（免费，实测能干机械穷举/全面阅读/逐条对账）：核心工作派三路独立做 + 第四路裁判。角色、工具限制与派活纪律见 [docs/team-roles.md](docs/team-roles.md)。

## 九、停止条件（遇到就停，不要自行拍板）

1. 两套官方源都查不到某接口，且`sw_know suggest`也给不出合理近似 → 先确认该接口是否存在，再写。
2. 某个缺口在 21个项目里都找不到可移植实现，且官方文档也没有示例 → 标为「无法缝合」，写进报告的「仍然空缺」段，不要硬编。
3. 需要碰 AGPL/GPL/无许可/全版权保留的代码才能补齐 → 停下，报告「需用户提供授权或接受缺口」。
4. 需要`git push`/建目标远端仓库/提 PR → 停下，等批准。
5. 发现实际仓库结构与铁律 3 的顶层白名单不符 → 停下报告，以实际仓库为准并更新本文件。
6. 来源没有测试、我们又无法本机实测 → 标`stitched`，不得标`verified`。
7. 某项 E 判据没有可验证的采集方式 → 列为技术风险，不能先把返回值填上。
8. 首件硬要求（孔数/孔型/位置、材料、图样、配合）在方案里没有承担节点 → 该方案是未完成方案，不能当候选。
9. 需求、阈值或盲集已冻结，但为了通过而想改它们 → 停下，走批准的需求变更。

常用路径/脚本/命令见 [docs/local-resources.md](docs/local-resources.md)；开工第一句话见 [docs/kickoff-template.md](docs/kickoff-template.md)。
