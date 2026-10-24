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

