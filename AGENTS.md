# AGENTS.md

本文件是 SolidWorks Automation Skill「集大成 + 建护城河」任务的常驻指令；仓库根——2026-10-03 起代码与产物在同一个仓库里（原先的代码工作副本`C:\swprojects\sw-skill-fork\`已成只读归档，见 §七）。跨项目的通用纪律在`~/.dsh/AGENTS.md`（用户全局层，每轮自动注入）——缝合优先、签名以官方源为准、查不到就说查不到、许可红线、把验证责任转移到静态比对、验收判据写成可 grep 项；本文件只留 SolidWorks 专属的事实与规矩。

★★ **接手第一件事**：读 [`docs/state/INDEX.md`](docs/state/INDEX.md)（项目现状实测台账：A–J 结构信号 + K–O 可证伪的对应关系，每条带复现命令；或调用 `sw-project-state` skill）。**不要通读 55 万行**；要报数字先跑 `docs/state/probes/` 里的探测器，别凭记忆。

## 十二、仓库（第一件事，先确认你在哪）

| 路径 | 是什么 | 能改吗 |
|---|---|---|
| `.` | 仓库根——代码（`scripts/` `mcp-server/` `tests/` `tools/` `apps/` …）与产物（草稿/日志/报告/证据）同在一处 | 改代码与放产物 |
| `C:\swprojects\sw-skill-fork\` | 合并前的代码副本，只读归档（历史与上游对照在其中） | 只读 |
| `C:\swprojects\<owner>\` | 四家外部 MCP 项目的克隆 | 只读对照 |
| `C:\swprojects\sw-automation-skill\` | 上游的另一份克隆 | 只读对照 |
| `AI Solidworks\` | SolidWorks 工作区（官方文档/手册/模型/截图） | 只读 |
| `docs\` | 本文件里`docs/...`相对 AGENTS.md 解析到这里——知识文档与任务产出同在一处（合并后不再分家） | 可改 |

`仓库根`是 git 仓库（提交`1f86c5d`起；2026-10-03 并入代码（入库文件数见 docs/state/facts/A-structure.md A-02））；`.gitignore`排除了 398 MB（官方文档/反射转储/探索截图/CAD 保真数据）。

任务报告与代码都放`仓库根`下。`AI Solidworks\`是模型/截图/手册，不是代码落点。

## 十三、动手核一条路之前：先扫「已走死的路」

```
docs/dead-ends.md      # ★ 由 tools/gen_dead_ends.py 生成（45 条 / 28 能力）
```

**为什么**：2026-10-02轮 359–362，我在`revolve_boss`的轴上重走了一遍前人早已走死的路——而结论就在`capabilities.yaml`的`limitations`里（轮 153/155 记的「6 种选法全部失败；`IEntity.Select4`没有 mark 参数、`SelectByID2`需要名字而边与草图段都没有名字」）。★我当时只查了`known-facts.md`与`git log`，没读那条能力的`limitations`——那是第一现场。⇒★★顺序：① `docs/dead-ends.md`（全局扫一眼）→ ② 该能力的`limitations`（第一现场）→ ③ `known-facts.md` → ④ 动手。★该文件由`tools/gen_dead_ends.py`从`capabilities.yaml`生成，不要手改；已接进每轮收尾链。

## 十四、★★官方文档是第 0 步（★不是"试不出来再去查"）

**动手碰任何一个 API 成员之前，先读完它那三样**：① `C:\swapi\types\<接口>\<成员>.md`的签名、② 它的`## Remarks`（前置与语义都在这）· ③ CHM 那页顶上的`Example`/`See Also`（★例子给的是"调用序"，签名与 Remarks 都给不了）。⇒★"试参数"是最后手段——★读完仍不成才开探针，★且探针`来源块`要写明读的是哪一页。★顺序：① 官方页 → ② `docs/dead-ends.md` → ③ 该能力的`limitations` → ④ `known-facts.md` → ⑤ 动手。★★第 0.5 步（★2026-10-04 加）：碰下面这些成员前，先查 [docs/recon-206/pre-code-conflict-lookup.md](docs/recon-206/pre-code-conflict-lookup.md)——它列了 368个成员/424条「官方`## Remarks`与官方示例不能同时成立」的位置（`unit_diff` 15、`mark_diff` 10、`return_shape_diff` 75、`precondition_diff` 324）⇒★照示例写可能就写错了 ✓（★样例：`AutoDimension2`的 Remarks 要求基准打`swAutodimMark*`，而示例用没有 mark 形参的`Select4`却声明成功）

**为什么**：2026-10-03轮 501–548 我在这件事上栽了六次（剪裁顺序反了、分割线 mark 全错、旋转曲面缺中心线 7轮、扫描曲面从没查过`InsertSweepSurface2`、指针族误判、"会挂"没读自己的弹窗落盘）——每一处官方都写着。详见 [docs/official-docs-first.md](docs/official-docs-first.md)。

## 〇、一句话任务

> 自建仓库，把 SolidWorks 自动化做到「官方 SolidWorks API 全覆盖 + 集四家 MIT/Apache MCP 项目之广度 + 业界空白域护城河」；交付形态是我们自己的仓库，上游`wzyn20051216/solidworks-automation-skill`（1010 星, MIT）与四家外部项目同为来源，一件一件搬、搬一件过一遍并入六条规则。

- 集大成：把四家外部 MCP 项目的能力广度并入本仓库，使单一项目即可替代四家之和，每一步可指认出处（铁律 1）。
- 建护城河：攻业界空白域——经核实真正全网空白的只有拓扑优化、动画导出（AVI）、Costing 三个。
- 正规军：不搞大杂烩，命名/单位/选择/验证等级/出处五统一，并挂机器门禁（`docs/union-conventions.md` + `scripts/check_union_conventions.py`）。
- 单源交付：运行时只能有一个 SolidWorks MCP——多个进程抢同一 COM 连接会死锁（已知事实 24）。

选按需搬取、不整体继承的理由：整体继承会把上游的目录结构、命名与验证口径整套带进来，与同时要并入的四家外部项目在同一批文件里打架；搬一件过一遍六条规则，冲突在搬的那一刻解决，不留给后面。

「引用各家」不等于不用上游代码：上游`mcp-server/server.py`（104 KB，45个工具的现成实现，我们一行没改）与 49个`scripts/*.py`是要用的，只是身份从「本仓库的历史基底」降为来源之一，与四家同等，MIT 版权声明照留。

这仍是缝合项目，不是从零写：能力来自官方文档、外部开源项目与本仓库既有模式。

## 十五、跑任何真机命令：一律走弹窗护栏（★不要再裸跑）

```
python tools/sw_guard.py --timeout 600 -- python <你的脚本>.py     # ★ 以后真机命令都这样起
python tools/sw_guard.py --scan                                    # 只看现有弹窗（不点）
python tools/sw_guard.py --clear                                   # 扫 + 两段式点掉（循环，直到 0 个）
python tools/sw_guard.py --report                                  # 打印历史弹窗事件
```

**为什么**（★2026-10-02轮 375–381，用户连续点破三次，每次都是我自己的机制在坑我）：

- 弹窗会让 COM 调用永久冻住⇒我先前的脚本"卡住一动不动"正是它。护栏给每个调用硬超时 + 子进程，最坏也会返回。
- **`PrintWindow`会挂在模态框上**（它向目标窗口发消息请其自绘，而模态框正在自己的消息循环里等人）；⇒截图已改`BitBlt`（只从屏幕 DC 拷像素、不发消息，实测 0.01 s）。
- **报信不等于处置**：护栏的哨兵进调用前先扫（旧弹窗也管）+ 执行中每 0.5 s 再扫，发现即记证 + 点掉，并把内容随返回值带回来（`dialogs`字段）⇒我每次都看得到根因线索。
- **点是分两段的**：`PostMessage`（快）⇒验窗口是否真消失（`still_present`）⇒没消失才上 真实输入事件。★`hung=True`的窗口消息永远不被取出，只有真输入事件有效。
- ★★处置要分级（`classify_dialog`）——这是"走 LLM"的落点：`auto`（唯一语义明确的确认按钮）⇒自动点；`needs_llm`（多义按钮/进度窗）·`forbidden`（危险词/在提问）⇒不点，★★并立刻`taskkill`掉那个被冻住的调用（`aborted_for_llm: true`）， 把证据交回我，我在下一次动作里判、我点。 "要 LLM 判" ≠ "原地等 LLM"——那个时刻我正阻塞在等工具返回，原地等就是死锁。
- ★判据不许认类名（那是偶然的）：认 SolidWorks 家族进程（按 exe 路径：`sldworks`/`sldProcMon`/`swCefSubProc`/`cwbcbfmesh`/`sldsurfacing`/`sldworks_fs` …）+ 像弹窗（`#32770`或有`Button`或 有可读文本）+ 兜底（家族内"不像弹窗"的也报，不让盲区静默失效）。
- ★配套测试：`tests/test_sw_guard_dialog_tiers.py`（★三级的契约 + 负例；★改判据必须让它继续绿）。

## 十六、每轮收尾链（★一条命令）

```
pwsh -File tools\round_chain.ps1 -Tests tests/<改过的>.py
```

**实测 34.8 s**（生成器 2.1 s + `release_check` 31 s + 聚焦测试）。不要再手打 6 步链、不要每轮跑全量 pytest。

- **为什么**：全量 pytest 160.6 s，其中三条测试（`test_release_check_passes_current_tree` 31.2 s、`test_gate_details_exposed_for_every_gate` 31.1 s、`test_no_uncalled_helpers_in_gates_and_tools` 25.6 s） 各自在内部又跑一遍`release_check`⇒占总时间 54%。★而 DSH 的`AGENTS.md`明写「Never default to the full suite or repeat a passing check for commit or push」⇒每轮跑全量是违反纪律。
- **不要再单独跑** `check_union_conventions.py`/`check_param_binding.py`/`check_digest_freshness.py`/`check_report_freshness.py`——`release_check.py`内部已有 18 道门禁，含这四个（AST 扫出来的，非推测）。
- **全量 pytest 只在两种情况跑**：① 发布前；② 改了`sw_connect.py`或门禁本体（被大量测试共用）。
- 生成器（`sync_bundled_skill`/`gen_metrics`/`gen_harvest_digest`/`build_union_map`/`gen_level_audit`） 必须先跑：门禁查的是它们的产物。
- 「偏离上游」那行已由脚本先算好预置，所以`release_check`一轮即绿（原先白花 31.5 s 跑第二轮）。

## 十七、写探针验能力时：按`ToolSpec`的契约调，别手调内部实现

```
① 从 mcp-server 的 ToolSpec 读它声明的 inject 与 params（`rc.all_specs()`）。
② 按那个契约准备实参（inject='study' 就给 study、inject='sw_app' 就给 ISldWorks、inject='model' 就给文档）。
③ 只有工具层本身有 bug 时才去调内部实现，并在记录里写明"这是内部函数，参数契约与工具层不同"。
```

**为什么**：2026-10-01轮 345–346，同一个错我犯了三次——把`doc`传给要`ISldWorks`的`ensure_simulation_addin`、把`sw`传给要 study 的`configure_*_solver_report`、还有缺`study_name`时的路径。每次"失败"都像是能力坏了，实际是我调错了。只看探针，就会把一条好能力记成坏的（而反过来也一样：探针"看起来对"不能证明工具层对）。

★与本条配套：若工具层真有 bug（如`resolve_study`少解包一层），要在工具层修，并在记录里写清"探针按契约调之后仍失败⇒是工具层的问题"。

## 十八、新建`.py`的模板：docstring 只写一行，来源块紧随其后

```python
"""★ 一句话说清这个文件干什么。"""          # ← ★ 只一行，**不要多行**
                                            #    空行
# ── 来源 ─────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖     # ← ★ 六字段
# ─────────────────────────────────────────
from __future__ import annotations
```

**为什么**：2026-10-01 本会话在同一处栽了七次——新建`.py`时把来源块写进了头部三引号里面（忘了闭合多行 docstring）⇒Python 把后面几十行当字符串吞掉，报的是`SyntaxError: invalid character '★'`（指向那个星号，不是真因）。实录：`modal_dialog_forensics`、`test_deprecated_entry_interlock`、`extract_operation_descriptions`、`judge_gap_candidates`、`check_python_syntax`、`test_compare_geometry_absolute`、`reclaim_solidworks`。⇒根因不是"不够小心"，而是模板里 docstring 是多行的——多行 docstring 与来源块挨着，就总会有人（我）把来源块写进去。一行 docstring 把这个坑从形态上消掉。★配套门禁：`scripts/check_python_syntax.py`（第 19 道，`ast.parse`每个`.py`）——它每次都抓到了，而且提示里就是修法（"在`# ── 来源 ──`之前补三引号"）。★修的时候用脚本（找`# ── 来源 ──`那行、在它之前插入），别手改——手改我失手过一次。

## 十九、SolidWorks 卡死：探不通就处置，不要"再探一次"

```
python tools/reclaim_solidworks.py --probe      # 只探（不动任何东西）
python tools/reclaim_solidworks.py --restart    # 探不通且打开的文档都是自己的 ⇒ 重启并复验
```

**为什么**：2026-10-01轮 24 我在主进程调`create_mesh`（还用了过大的`element_size`），把会话卡住；此后连续 7轮每轮开头只"再探一次"，一次也没处置⇒白等 7轮。轮 31 动手（清残留 python → `Stop-Process` → 重连）⇒立刻`connect: True · revision 34.4.1`。⇒★同一个状态反复观察 ≠ 处置（与事实 53 同族：连续修补 ≥3次就该停下换做法）。★脚本自带安全判定：先把 SW 主窗口标题里的打开文档逐个分类，只要有一个不是自己的就拒绝重启（依据：全局纪律「回收自己开的资源」与「不删用户数据」）。

## 二十、汇报频率

默认不汇报；只在三种情况发一条消息：一批做完、同一处卡住 ≥2次、计划要变。消息 ≤3行，只写结果与影响；进度写进 ROADMAP §一与 capabilities.yaml，不在对话里复述。

## 一、验收标准（做完这几条才算完成）

| # | 判据 | 怎么验 |
|---|---|---|
| A1 | 四家的能力广度已并入：域覆盖矩阵里本仓库每一格都有来源，或写明「不做 + 原因」 | `docs/union-coverage-matrix.md`可重新生成且无空白格 |
| A2 | 两层 provenance 都要：① 来源级——`tools/union-sources.json`的每个来源带`owner/repo`全名 + 许可（白名单内）+ `declared_verified` + `note`；② 能力级——`capabilities[].provenance`对来源派生的条目（`level: source_verified`）必须齐`repo`/`license`/`files`/`upstream_verified`四字段。 ①与②不是同一件事：① 说的是「哪几家、什么许可、他们自己声明跑过什么」；② 说的是「这一条能力是从哪条来源派生的」。`level: verified`只表示「有我们自己的运行证据」，不表示「代码是我们写的」——两条线不该混。 | ① `python scripts/check_union_conventions.py`的「规则 5、出处与许可」段；② 同门禁的「清单形状」段（现`source_verified`条目数为 0，故②空满足；一旦新增`source_verified`条目，②即强制生效）|
| A3 | 五统一门禁通过：命名/单位/选择/验证等级/出处 | `scripts/check_union_conventions.py`退出码 0，且已接进`release_check.py` |
| A4 | 每个条目的`level`取自五级枚举；`verified`必须有我们自己的运行证据 | 逐条核对`capabilities.yaml` |
| A5 | 每个新增文件里每个 COM 调用的参数顺序与类型与官方签名对齐 | `docs/signature-audit.md` |
| A6 | 许可无越界：AGPL/GPL/无许可/全版权保留的代码没被抄进来；Apache-2.0 来源带 NOTICE 义务 | 逐文件对照「许可判定表」 |
| A7 | 全文没有一处把`source_verified`或`stitched`写成`verified` | grep 全文，禁词 0 命中 |
| A8 | 报告写明并入了什么、仍空缺什么、为什么空缺 | `docs/harvest-report.md` |
| A9 | 空白域护城河有可跑的工程实现（拓扑优化优先），不是只有文档 | 对应`scripts/`模块 + `tests/` |
| A10 | 按需搬取：每一件搬进来的东西都过一遍「并入六条规则」，冲突在搬进来的当时解决 | `scripts/check_union_conventions.py`退出码 0 + 并入清单逐条核对 |

> A1–A10 是交付判据，不是每轮都要全绿：A3（门禁）是可执行的不变量，任何时候都该绿；其余随并入逐条满足。

进度与下一步看`capabilities.yaml`（能力清单：每条带`level`，`verified`另带`evidence`）——状态由清单承载，不写进本文件。`docs/union-coverage-matrix.md`第五节的「并入清单」是缺口地图（每域缺什么、从哪抄、该来源声明跑过没有），不是进度。

## 二、六条铁律

### 铁律 1、只做「缝合」，不做「发明」

每加一个能力，要能指认出处。四种合法来源：
| 来源 | 怎么用 | 例 |
|---|---|---|
| 官方 API 文档 | 决定接口选型与参数顺序 | Simulation 域（外部无人提供，只能照官方签名建） |
| 其它开源项目 | 直接移植/改写，保留来源头注释 | 建视图 ← codestack；VBScript ← pengxiaoan |
| 四家外部 MCP 项目 | 移植其能力广度，按`provenance`标注来源与许可 | `andrewbartels1`的草图完全定义探针；`Slacker-LLC`的声明式 selection |
| 本项目自身既有模式 | 沿用`sw_part.py`/`sw_hole_features.py`的写法与命名 | 新`sw_xxx.py`沿用`_select_by_id`/`get_com_member` |

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

**归档目录 `archive/`（★ 2026-10-10 登记 · 规格 294）**：`archive/root-scratch/{py,txt,md,json,logs,other}` 装的是**仓库根曾经就地写的 2814 个草稿**（`_factNNN.txt` / `_commit_msg_NNN.txt` / `_roadmap_*.md` / `fx*` / `dbg*` / `probe_*.py` 等）。为什么放不进已有目录：它们是**历史产物、不是活代码**（`tools/` 只收「正式、会被反复用的工具」；`docs/` 只收知识文档），而根目录自 2026-10-01 起就是草稿区（`README-workspace.md` §分类规矩）。归档后根只剩 **29** 个文件（打包器顶层文件 + 仓库门面 + 被 `scripts/sw_jlcfa_*.py` import 的 `shot.py`/`ctl.py`）。★ **只搬不删**；判据 `tests/test_workspace_tidy_294.py`（守恒断言：归档数 + 根数 == 整理前总数）。★ 该目录**不被任何门禁扫描**（门禁扫描根是 `scripts`/`tools`/`tests`/`mcp-server`/`subskills`/`apps`/`dotnet`/`examples`），故是惰性的。

**★★ 顶层目录实况登记（★ 2026-10-18 · ★ 落实 §九 停止条件 #5「以实际仓库为准并更新本文件」）**

★ 实测：★ 本仓**实际有 39 个顶层目录**（不含 `.git`、**不含 3 个工具缓存**），★ 而上面白名单只有 **14** 个 ⇒ ★★ **结构与白名单不符** ✗。
★★ **2026-10-21 复核更正**：★ 原先记作 **40**，是把 `.pytest_cache`（**工具缓存、gitignore、不入库**）也当成仓库目录算进去了 ✗。
★ 正确口径：★ **磁盘顶层 = 39 个仓库目录 + 3 个工具缓存**（`.pytest_cache` / `.codebase-memory` / `.ruff_cache`，★ 三者均已 gitignore ✓）。
★ 复核命令：`python -c "import pathlib;[print(d.name) for d in pathlib.Path('.').iterdir() if d.is_dir() and d.name!='.git']"` ✓
★ 逐个登记**多出的 25 个**（★ 每个一句"是什么 / 为什么放不进已有目录" ✓）：

| ★ 目录 | ★ 是什么 | ★ 为什么放不进已有目录 |
|---|---|---|
| `.specify/` | ★ Spec Kit **1.0.13** 集成（commands/templates/scripts/workflows/memory ✓）| ★ 是**第三方工具的检出态**：★ 有它自己的 `.gitignore` 与目录约定 ⇒ ★ 塞进 `tools/` 会破坏它的自更新 ✗ |
| `.dsh/` | ★ DSH 宿主侧项目配置（★ 角色表等 ✓）| ★ **宿主约定目录**（★ 名字由宿主定，★ 不能改 ✗）|
| `.workbuddy-ai/` | ★ 旧宿主留下的**历史开发记忆**（★ 4 份 memory · 420 KB ✓）| ★ 是**史料**不是活代码；★ 已登记在 `output/LEGACY_LOOP_REFERENCES.md` ✓ |
| `AI Solidworks/` | ★ SolidWorks 官方文档/手册/模型/截图（★ **29749 文件** ✓）| ★ **只读外部素材**（★ 与 `references/`＝本仓知识文档**性质不同** ✗）· ★ **不得写入** ✗ |
| `specs/` | ★★ **Spec Kit 规格**（★ 规格数与编号范围见 docs/state/facts/H-specs.md H-01/H-02）| ★ **规格的落点**（★ 不是代码、★ 不是 `docs/` 知识文档、★ 不是 `output/` 产物 ✗）—— ★★ **且门禁 `check_spec_acceptance_paths` 读它们的 `→ 验收:` 行（处数见 docs/state/facts/H-specs.md H-03）** ⇒ ★ **删了会断门禁** ✗ |

★ **产物 / 证据 / 侦察类（★ 均不承载活代码；★ 应 gitignore 或已 ignore ✓）**：
`_proof` · `_raw` · `audit` · `batch_evidence` · `cadir` · `commit-messages` · `corpus` ·
`evidence` · `explore` · `mcp-tool-draft` · `MCP_CALIB` · `metadata` · `net-guard` ·
`research` · `shots` · `solidpilot-salvage` · `swpublished` · `.api-signatures` · `output` · `.pytest_cache`

★★ **结论**：★★ 本节的**白名单数字（14）已不反映实际** ✗ —— ★ **以实际 39 个仓库目录为准** ✓（★ 上面已逐个登记 ✓；★ 工具缓存另计 ✓）；
★★ **新增白名单外的顶层目录，仍须按本节规矩「先登记、再动手」** ✓

新文件落进已有位置：能力实现进`scripts/`，知识文档进`references/`，测试进`tests/`，说明与生成物进`docs/`。上游目录树与新增模块的硬性要求见 [docs/upstream-layout.md](docs/upstream-layout.md)（对照参考，不是约束来源）。

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

### 4.1 两套官方离线源 + 反射（各管一头）

本机两套官方源都要查：`AI Solidworks\官方文档\`（CHM 解包，权威、带说明与示例，查语义与用法）与`C:\swapi\`（结构化 markdown，查精确签名与枚举值）；检索入口是`手册\swdoc.ps1`与`mech-design` skill 的`sw_know.py`。出厂类型库的反射是第三套源，也是冲突时的裁决者。各源的文件量、检索子命令与覆盖缺口见 [docs/sources.md](docs/sources.md)。

### 4.2 其它项目（`C:\swprojects\`）

四家与本项目重叠的外部 MCP 项目（克隆在`C:\swprojects\<owner>\`，已逐份读真实 LICENSE 文件，不采信 README 徽章）：
| 克隆目录 | 项目（owner/repo） | 工具 | 许可 | 测试文件 | 自己声明跑过的环境 |
|---|---|---|---|---|---|
| `Eduardof0nt` | Eduardof0nt/Solidworks-MCP-Server | 187 | MIT | 0个 | 未声明 |
| `andrewbartels1` | andrewbartels1/SolidworksMCP-python | 128 | MIT | 147（7 live） | 未声明（README 自述 under active construction） |
| `SolidworksMCP-TS` | vespo92/SolidworksMCP-TS | 103 | MIT | 7（0 live） | 未声明 |
| `Slacker-LLC` | Slacker-LLC/solidworks-mcp | 92 | Apache-2.0 | 2（1 live） | SW 2026 SP3.2 简体中文 |

- 工具最多的那家（187）测试文件数为 0：README 写着「Verified on SolidWorks 2024」，仓库里没有任何测试文件——README 说验过不等于验过。
- 四家里只有`Slacker-LLC`声明全工具真机跑过，而它的工具数最少（92）；它的 92个里没有仿真/动画/拓扑/钣金/焊件/公差。
- `Slacker-LLC`是 Apache-2.0：可抄，但要保留`NOTICE`（`Copyright 2026 JIALE LIU`）并声明改动了哪些文件；推送任何远端时产生硬性义务，`THIRD-PARTY-NOTICES.md`已存在（规模见 docs/state/facts/I-license.md I-02）。

其余 21个外部项目克隆的清单、逐项能补什么、许可判定表与 MIT 唯一例外，见 [docs/sources.md](docs/sources.md)。

### 4.3 来源标注制（每个移植函数都要有）

每个移植函数必须带来源头注释，并入`capabilities.yaml`的条目另带结构化`provenance`字段；格式模板、字段定义与「未实测」标注规则见 [docs/provenance-format.md](docs/provenance-format.md)。许可必须与来源表一致。

## 五、工作方法（并入五步）

1. 建全景与对差：`sw_know.py domain --list`拿 14个域，`swdoc.ps1` + 反射补`cosworks`/Routing/Costing/PDM，对照上游`capabilities.yaml` + `scripts/` + `subskills/`建`docs/capability-matrix.md`与`docs/gap-analysis.md`（从零建表，不预设缺口结论）。
2. 找来源：按优先级取素材——上游相邻模块 > MIT 项目现成实现 > MIT 项目文档/示例 > Apache-2.0 项目实现（带 NOTICE）> 只读思想（AGPL/GPL/无许可，绝不抄文本）> 照官方签名自建。
3. 归一：按「并入六条规则」改造，命名/单位/选择/验证等级/出处五统一。
4. 标等级与出处：`capabilities.yaml`每条给`level`（五级）与`provenance{repo, license, files, upstream_verified}`。
5. 门禁与实测：`check_union_conventions.py` → `python -m compileall -q scripts subskills` → 逐 COM 调用与官方签名对齐（`docs/signature-audit.md`）→ 本机实测；缺我们自己的运行证据的条目留在`stitched`。

产出：`docs/capability-matrix.md`、`docs/gap-analysis.md`、`docs/signature-audit.md`、`docs/union-coverage-matrix.md`、`docs/harvest-report.md`。判据优先去开源项目里找（先去四家找现成判据，找不到再自己搓）见 [docs/evidence-first.md](docs/evidence-first.md)。

## 六、已知事实（完整表在 [`docs/known-facts.md`](docs/known-facts.md)）

**全文在** [`docs/known-facts.md`](docs/known-facts.md)（条数以该文件为准）；本节只留最常查的 21条速查。事实 560 是三条方法论——中文引号一律用「」、探针先关护栏沙盒那一层、「入口修好 ≠ 效果验证」与「一直是红的验收脚本可能只是它自己建错了试件」成对——动台账/源码的长字符串、或写"先写文件再把路径交给 COM"的探针之前先读它。分开的原因：该表曾占 AGENTS.md 的 ~71%，而本文件受 65536字节指令预算限制，超预算会静默截断末尾最新条目。新增事实：最常查的留这里，其余追加进那个文件并同步条数。

### 速查：最常查的 21 条在哪

事实 **1 / 2 / 8 / 9 / 12 / 24 / 32 / 33 / 36 / 40 / 43 / 47 / 48 / 51 / 53 / 55 / 57 / 58 / 59 / 61 / 62** —— 正文全在 [`docs/known-facts.md`](docs/known-facts.md)（按编号跳），本文件**不再复制**（一个事实一个家）。三条方法论总纲见事实 **560**。

## 七、Git 规则

```
仓库：        .\                ← **唯一的仓库**（2026-10-03 合并；代码 + 产物同仓）
  upstream : https://github.com/wzyn20051216/solidworks-automation-skill   ← 来源与对照（**只读**）
  origin   : **故意留空** —— 自建远端的目标 URL 由用户给定后再 `git remote add origin <url>`
  MIT · 上游是来源之一，不是本仓库的历史基底
归档：        C:\swprojects\sw-skill-fork\   合并前的代码副本，**只读保留**（B 是 shallow clone，历史在其中）
```

 上游改叫`upstream`（不再叫`origin`）是刻意的：只有`origin`指向上游时，一次裸`git push`就会误推上游仓库（AGENTS.md 一贯点名的风险）。现在`origin`空着⇒裸`git push`无处可去，从结构上消掉这个风险。

用`git diff upstream/main --stat`看我们相对上游的增量。`upstream`目前只登记了 URL、还没 fetch（本机未联网取）⇒`upstream/main`这个 ref 不存在，`round_chain.ps1`会优雅跳过那行统计、`report_freshness`门禁会 SKIP（那是便携性守卫，不是失败）。要用对照能力就先`git fetch upstream`。

- 三条红线（任何模式都不豁免）：删数据/删仓库/强推；对外发布；只有用户能提供的东西（凭据、业务口径）。
- ★★提交一律走`python tools/commit_mine.py -m <信息文件> <路径…>`——且信息先写成文件。★禁止裸`git commit -m "<多行带引号的字符串>"`：PowerShell 会把信息里的引号/换行当成 pathspec（报`did not match any file(s) known to git`），而`git add`已经成功⇒产生「表面像提交了、实际没提交」的假提交（与事实 48 定则①同族）。★2026-10-05 我同一条犯了三次，前两次还写进了提交信息与规格，⇒★纪律写在提交信息里没用（我不会每轮重读它）；它必须写在本文件（每轮注入）才拦得住 ✓
- 推送前置义务：并入了 Apache-2.0 来源（`Slacker-LLC/solidworks-mcp`）⇒推送任何远端都要带`THIRD-PARTY-NOTICES.md`（含`Copyright 2026 JIALE LIU`与改动文件清单），该文件已存在；MIT 来源保留版权声明。这条对上游与四家一体适用。
- 分支策略：`main`与上游保持一致便于 rebase；每个功能域一个分支（`feat/simulation`、`feat/drawing-views` …）；每个 PR 一句话写清「补了哪个官方接口族，来源是哪个项目/哪套文档」。

| 动作 | 是否需要用户批准 |
|---|---|
| 本地 clone/分支/commit/`git add`/`git remote add\|remove` | 不需要 |
| 改文件、跑`compileall`、跑`sw_know.py`/`swdoc.ps1` | 不需要 |
| 建自建仓库、加目标远端（`gh repo create`/改 origin） | 要先批准 |
| `git push`（任何远端） | 要先批准 |
| 提 PR/发布 release | 要先批准 |

## 八、智能体团队分工

**多用 space-bunny**（免费，实测能干机械穷举/全面阅读/逐条对账）：核心工作派三路独立做 + 第四路裁判。角色、工具限制与派活纪律见 [docs/team-roles.md](docs/team-roles.md)。

## 九、停止条件（遇到就停，不要自行拍板）

1. 两套官方源都查不到某接口，且`sw_know suggest`也给不出合理近似 → 先确认该接口是否存在，再写。
2. 某个缺口在 21个项目里都找不到可移植实现，且官方文档也没有示例 → 标为「无法缝合」，写进报告的「仍然空缺」段，不要硬编。
3. 需要碰 AGPL/GPL/无许可/全版权保留的代码才能补齐 → 停下，报告「需用户提供授权或接受缺口」。
4. 需要`git push`/建目标远端仓库/提 PR → 停下，等批准。
5. 发现实际仓库结构与铁律 3 的顶层白名单不符 → 停下报告，以实际仓库为准并更新本文件。
6. 来源没有测试、我们又无法本机实测 → 标`stitched`，不得标`verified`。

## 十、本地资源速查

常用路径/脚本/命令的速查表见 [docs/local-resources.md](docs/local-resources.md)。

## 十一、开工第一句话模板

开工第一句话模板见 [docs/kickoff-template.md](docs/kickoff-template.md)。
