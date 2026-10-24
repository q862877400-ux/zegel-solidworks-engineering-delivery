# AGENTS.md 的依据与事故记录（**不属于每轮注入**）

> 本文件是 `AGENTS.md` 各节「**为什么这么定**」的原始记录：事故经过、实测读数、当时怎么栽的。
> 按本仓分层规范，根 `AGENTS.md` 只留「1–3 行常驻指令 + 链接」，叙事搬到这里；
> 原处保留一行指针。**内容是逐字搬运，未改写**。

## <a id="13-deadends"></a>13-deadends

**为什么**：2026-10-02轮 359–362，我在`revolve_boss`的轴上重走了一遍前人早已走死的路——而结论就在`capabilities.yaml`的`limitations`里（轮 153/155 记的「6 种选法全部失败；`IEntity.Select4`没有 mark 参数、`SelectByID2`需要名字而边与草图段都没有名字」）。★我当时只查了`known-facts.md`与`git log`，没读那条能力的`limitations`——那是第一现场。⇒★★顺序：① `docs/dead-ends.md`（全局扫一眼）→ ② 该能力的`limitations`（第一现场）→ ③ `known-facts.md` → ④ 动手。★该文件由`tools/gen_dead_ends.py`从`capabilities.yaml`生成，不要手改；已接进每轮收尾链。

## <a id="14-official-first"></a>14-official-first

**为什么**：2026-10-03轮 501–548 我在这件事上栽了六次（剪裁顺序反了、分割线 mark 全错、旋转曲面缺中心线 7轮、扫描曲面从没查过`InsertSweepSurface2`、指针族误判、"会挂"没读自己的弹窗落盘）——每一处官方都写着。详见 [docs/official-docs-first.md](docs/official-docs-first.md)。

## <a id="15-guard"></a>15-guard

**为什么**（★2026-10-02轮 375–381，用户连续点破三次，每次都是我自己的机制在坑我）：

## <a id="16-round-chain"></a>16-round-chain

**为什么**：全量 pytest 160.6 s，其中三条测试（`test_release_check_passes_current_tree` 31.2 s、`test_gate_details_exposed_for_every_gate` 31.1 s、`test_no_uncalled_helpers_in_gates_and_tools` 25.6 s） 各自在内部又跑一遍`release_check`⇒占总时间 54%。★而 DSH 的`AGENTS.md`明写「Never default to the full suite or repeat a passing check for commit or push」⇒每轮跑全量是违反纪律。

## <a id="17-probe-contract"></a>17-probe-contract

**为什么**：2026-10-01轮 345–346，同一个错我犯了三次——把`doc`传给要`ISldWorks`的`ensure_simulation_addin`、把`sw`传给要 study 的`configure_*_solver_report`、还有缺`study_name`时的路径。每次"失败"都像是能力坏了，实际是我调错了。只看探针，就会把一条好能力记成坏的（而反过来也一样：探针"看起来对"不能证明工具层对）。

## <a id="18-py-template"></a>18-py-template

**为什么**：2026-10-01 本会话在同一处栽了七次——新建`.py`时把来源块写进了头部三引号里面（忘了闭合多行 docstring）⇒Python 把后面几十行当字符串吞掉，报的是`SyntaxError: invalid character '★'`（指向那个星号，不是真因）。实录：`modal_dialog_forensics`、`test_deprecated_entry_interlock`、`extract_operation_descriptions`、`judge_gap_candidates`、`check_python_syntax`、`test_compare_geometry_absolute`、`reclaim_solidworks`。⇒根因不是"不够小心"，而是模板里 docstring 是多行的——多行 docstring 与来源块挨着，就总会有人（我）把来源块写进去。一行 docstring 把这个坑从形态上消掉。★配套门禁：`scripts/check_python_syntax.py`（第 19 道，`ast.parse`每个`.py`）——它每次都抓到了，而且提示里就是修法（"在`# ── 来源 ──`之前补三引号"）。★修的时候用脚本（找`# ── 来源 ──`那行、在它之前插入），别手改——手改我失手过一次。

## <a id="19-reclaim"></a>19-reclaim

**为什么**：2026-10-01轮 24 我在主进程调`create_mesh`（还用了过大的`element_size`），把会话卡住；此后连续 7轮每轮开头只"再探一次"，一次也没处置⇒白等 7轮。轮 31 动手（清残留 python → `Stop-Process` → 重连）⇒立刻`connect: True · revision 34.4.1`。⇒★同一个状态反复观察 ≠ 处置（与事实 53 同族：连续修补 ≥3次就该停下换做法）。★脚本自带安全判定：先把 SW 主窗口标题里的打开文档逐个分类，只要有一个不是自己的就拒绝重启（依据：全局纪律「回收自己开的资源」与「不删用户数据」）。


## <a id="mission-rationale"></a>mission-rationale

选按需搬取、不整体继承的理由：整体继承会把上游的目录结构、命名与验证口径整套带进来，与同时要并入的四家外部项目在同一批文件里打架；搬一件过一遍六条规则，冲突在搬的那一刻解决，不留给后面。

「引用各家」不等于不用上游代码：上游`mcp-server/server.py`（104 KB，45个工具的现成实现，我们一行没改）与 49个`scripts/*.py`是要用的，只是身份从「本仓库的历史基底」降为来源之一，与四家同等，MIT 版权声明照留。

这仍是缝合项目，不是从零写：能力来自官方文档、外部开源项目与本仓库既有模式。

## <a id="guard-design"></a>guard-design

- 弹窗会让 COM 调用永久冻住⇒我先前的脚本"卡住一动不动"正是它。护栏给每个调用硬超时 + 子进程，最坏也会返回。
- **`PrintWindow`会挂在模态框上**（它向目标窗口发消息请其自绘，而模态框正在自己的消息循环里等人）；⇒截图已改`BitBlt`（只从屏幕 DC 拷像素、不发消息，实测 0.01 s）。
- **报信不等于处置**：护栏的哨兵进调用前先扫（旧弹窗也管）+ 执行中每 0.5 s 再扫，发现即记证 + 点掉，并把内容随返回值带回来（`dialogs`字段）⇒我每次都看得到根因线索。
- **点是分两段的**：`PostMessage`（快）⇒验窗口是否真消失（`still_present`）⇒没消失才上 真实输入事件。★`hung=True`的窗口消息永远不被取出，只有真输入事件有效。
- ★★处置要分级（`classify_dialog`）——这是"走 LLM"的落点：`auto`（唯一语义明确的确认按钮）⇒自动点；`needs_llm`（多义按钮/进度窗）·`forbidden`（危险词/在提问）⇒不点，★★并立刻`taskkill`掉那个被冻住的调用（`aborted_for_llm: true`）， 把证据交回我，我在下一次动作里判、我点。 "要 LLM 判" ≠ "原地等 LLM"——那个时刻我正阻塞在等工具返回，原地等就是死锁。
- ★判据不许认类名（那是偶然的）：认 SolidWorks 家族进程（按 exe 路径：`sldworks`/`sldProcMon`/`swCefSubProc`/`cwbcbfmesh`/`sldsurfacing`/`sldworks_fs` …）+ 像弹窗（`#32770`或有`Button`或 有可读文本）+ 兜底（家族内"不像弹窗"的也报，不让盲区静默失效）。
- ★配套测试：`tests/test_sw_guard_dialog_tiers.py`（★三级的契约 + 负例；★改判据必须让它继续绿）。

## <a id="round-chain-detail"></a>round-chain-detail

- **不要再单独跑** `check_union_conventions.py`/`check_param_binding.py`/`check_digest_freshness.py`/`check_report_freshness.py`——`release_check.py`内部已有 18 道门禁，含这四个（AST 扫出来的，非推测）。
- **全量 pytest 只在两种情况跑**：① 发布前；② 改了`sw_connect.py`或门禁本体（被大量测试共用）。
- 生成器（`sync_bundled_skill`/`gen_metrics`/`gen_harvest_digest`/`build_union_map`/`gen_level_audit`） 必须先跑：门禁查的是它们的产物。
- 「偏离上游」那行已由脚本先算好预置，所以`release_check`一轮即绿（原先白花 31.5 s 跑第二轮）。

## <a id="ironlaw1-sources"></a>ironlaw1-sources

每加一个能力，要能指认出处。四种合法来源：
| 来源 | 怎么用 | 例 |
|---|---|---|
| 官方 API 文档 | 决定接口选型与参数顺序 | Simulation 域（外部无人提供，只能照官方签名建） |
| 其它开源项目 | 直接移植/改写，保留来源头注释 | 建视图 ← codestack；VBScript ← pengxiaoan |
| 四家外部 MCP 项目 | 移植其能力广度，按`provenance`标注来源与许可 | `andrewbartels1`的草图完全定义探针；`Slacker-LLC`的声明式 selection |
| 本项目自身既有模式 | 沿用`sw_part.py`/`sw_hole_features.py`的写法与命名 | 新`sw_xxx.py`沿用`_select_by_id`/`get_com_member` |

## <a id="probe-howto"></a>probe-howto

```
① 从 mcp-server 的 ToolSpec 读它声明的 inject 与 params（`rc.all_specs()`）。
② 按那个契约准备实参（inject='study' 就给 study、inject='sw_app' 就给 ISldWorks、inject='model' 就给文档）。
③ 只有工具层本身有 bug 时才去调内部实现，并在记录里写明"这是内部函数，参数契约与工具层不同"。
```

## <a id="py-template-code"></a>py-template-code

```python
"""★ 一句话说清这个文件干什么。"""          # ← ★ 只一行，**不要多行**
                                            #    空行
# ── 来源 ─────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖     # ← ★ 六字段
# ─────────────────────────────────────────
from __future__ import annotations
```

## <a id="13-deadends-code"></a>13-deadends-code

```
docs/dead-ends.md      # ★ 由 tools/gen_dead_ends.py 生成（45 条 / 28 能力）
```
