# AGENTS.md

本文件是 SolidWorks Automation Skill「集大成 + 建护城河」任务的常驻指令；仓库根——2026-10-03 起代码与产物在同一个仓库里（原先的代码工作副本`C:\swprojects\sw-skill-fork\`已成只读归档，见 §七）。跨项目的通用纪律在`~/.dsh/AGENTS.md`（用户全局层，每轮自动注入）——缝合优先、签名以官方源为准、查不到就说查不到、许可红线、把验证责任转移到静态比对、验收判据写成可 grep 项；本文件只留 SolidWorks 专属的事实与规矩。

接手第一件事：读 [`docs/state/INDEX.md`](docs/state/INDEX.md)（项目现状实测台账：A–J 结构信号 + K–O 可证伪的对应关系，每条带复现命令；或调用 `sw-project-state` skill）。不要通读 55 万行；要报数字先跑 `docs/state/probes/` 里的探测器，别凭记忆。

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

- 集大成 · 建护城河的定位是手段（取材地图 / 差异化参考），不是目的、不计分（依据见 charter 第 2 节）。
- 正规军：命名/单位/选择/验证等级/出处五统一，机器门禁 docs/union-conventions.md + scripts/check_union_conventions.py。
- 单源交付：运行时只能有一个 SolidWorks MCP——多个进程抢同一 COM 连接会死锁（已知事实 24）。

## 十五、真机命令一律走弹窗护栏

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
| **A8** | 报告写明哪些能力过了 E1–E7、哪些没过、缺什么 |
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

**归档目录 `archive/`**：`archive/root-scratch/{py,txt,md,json,logs,other}` 装的是仓库根曾经就地写的 2814 个草稿（草稿文件名模式见 [`docs/layout-registry.md`](docs/layout-registry.md)）。为什么放不进已有目录：它们是历史产物、不是活代码（`tools/` 只收「正式、会被反复用的工具」；`docs/` 只收知识文档），而根目录一直是草稿区（`README-workspace.md` §分类规矩）。归档后根只剩 29 个文件（打包器顶层文件 + 仓库门面 + 被 `scripts/sw_jlcfa_*.py` import 的 `shot.py`/`ctl.py`）。只搬不删；判据 `tests/test_workspace_tidy_294.py`（守恒断言：归档数 + 根数 == 整理前总数）。该目录不被任何门禁扫描（门禁扫描根是 `scripts`/`tools`/`tests`/`mcp-server`/`subskills`/`apps`/`dotnet`/`examples`），故是惰性的。

**顶层目录实况**（磁盘 42 个 = 39 仓库目录 + 3 工具缓存；白名单外 25 个的逐个说明、产物/证据类清单，见 [`docs/layout-registry.md`](docs/layout-registry.md)）。新增白名单外目录仍须「先登记、再动手」。

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

上游的目录树、`scripts/`现有模块清单与新增模块的硬性要求见 [docs/upstream-layout.md](docs/upstream-layout.md)。它是对照参考与取材地图，不是我们的结构约束——我们自己允许哪些顶层目录，看铁律 3。

## 四、素材库

**两套官方离线源 + 反射**

本机两套官方源都要查：`AI Solidworks\官方文档\`（CHM 解包，权威、带说明与示例，查语义与用法）与`C:\swapi\`（结构化 markdown，查精确签名与枚举值）；检索入口是`手册\swdoc.ps1`与`mech-design` skill 的`sw_know.py`。出厂类型库的反射是第三套源，也是冲突时的裁决者。各源的文件量、检索子命令与覆盖缺口见 [docs/sources.md](docs/sources.md)。

**其它项目（`C:\swprojects\`）**

四家与本项目重叠的外部 MCP 项目（`Eduardof0nt` 187 工具 MIT · `andrewbartels1` 128 MIT · `vespo92` 103 MIT · `Slacker-LLC` 92 Apache-2.0）：工具数、测试文件数、各自声明跑过的环境与逐条许可判定，见 [`docs/sources.md`](docs/sources.md) 与 [`docs/state/facts/N-external.md`](docs/state/facts/N-external.md)。

其余 21个外部项目克隆的清单、逐项能补什么、许可判定表与 MIT 唯一例外，见 [docs/sources.md](docs/sources.md)。

**来源标注制**（每个移植函数都要有）

每个移植函数必须带来源头注释，并入`capabilities.yaml`的条目另带结构化`provenance`字段；格式模板、字段定义与「未实测」标注规则见 [docs/provenance-format.md](docs/provenance-format.md)。许可必须与来源表一致。

## 五、工作方法（并入五步）

① 建全景与对差 → ② 找来源（上游 > MIT > Apache > 只读思想 > 照官方自建）→ ③ 归一（五统一）→ ④ 标 `level` 与 `provenance` → ⑤ 门禁与实测。每步的产出文件与判据见 [`docs/work-method.md`](docs/work-method.md)。

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

常用路径/脚本/命令见 [docs/local-resources.md](docs/local-resources.md)；开工第一句话见 [docs/kickoff-template.md](docs/kickoff-template.md)。
