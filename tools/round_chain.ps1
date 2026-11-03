# 每轮收尾链（★ 精简版）—— 把 200 s 压到 ~34 s
#
# ## 为什么有这个脚本（★ 2026-10-01 轮 342，用户问"chain 为什么这么慢"）
# ★ 我量了每一段（实测，非估计）：
# ```
#   pytest 全量 1291 个 ........ 160.6 s   ← 绝对大头，其余全加起来 ~37 s
#   聚焦 2 个测试文件 ..........   0.3 s   ← 差 535 倍
#   release_check .............  31.5 s
#   check_union_conventions ...   3.3 s
#   gen_metrics ...............   0.9 s
#   其余 5 步 .................   1.0 s
# ```
# ★★ 而全量里最慢的三条**占总时间 54%**，★ 它们**各自在内部又跑一遍 `release_check`**：
# ```
#   test_release_check_passes_current_tree ....... 31.2 s
#   test_gate_details_exposed_for_every_gate ..... 31.1 s
#   test_no_uncalled_helpers_in_gates_and_tools .. 25.6 s
# ```
#
# ## ★★★ 三段冗余（★ 实测确认，非推测）
# ① `release_check` **内部已有 18 道门禁**，含 `_run_union_conventions_gate` /
#    `_run_param_binding_gate` / `_run_digest_freshness_gate` / `_run_report_freshness_gate`
#    ⇒ ★ 我另外单独跑的 `check_union_conventions` / `check_param_binding` **是重复的**。
# ② 我原先写了 `sync_bundled_skill` **两次**（sync + sync2）⇒ 冗余。
# ③ ★ **每轮跑全量 pytest** —— ★★ **而 DSH 的 AGENTS.md 明写**：
#    「**Never default to the full suite** or repeat a passing check for commit or push.
#      CI owns exhaustive coverage and the platform matrix」
#    ⇒ ★ **跑全量不是我"勤快"，是**违反纪律**。**
#
# ## 用法
# ```
# pwsh -File tools\round_chain.ps1                 # 默认：聚焦测试 = 我改过的模块
# pwsh -File tools\round_chain.ps1 -Full           # 发布前 / 改了共享基础设施时：加跑全量
# pwsh -File tools\round_chain.ps1 -Tests a.py,b.py
# ```
# ★ `-Full` 只在两种情况用：① 发布前；② 改了 `sw_connect.py` 或门禁本体（★ 它们被大量测试共用）。
#
# # ── 来源 ─────────────────────────────────────────────────────────────
# # 仓库:   本项目自身（工具）
# # 文件:   tools/round_chain.ps1
# # 定位:   每轮收尾：跑**生成器**（门禁查它们的产物）→ **一次** release_check → **聚焦**测试。
# # 依据:   `scripts/release_check.py` 的 18 个 `_run_*_gate`（★ AST 扫出来的，不是猜的）；
# #         DSH `AGENTS.md` 的 "Run relevant checks locally" 段（★ 不默认跑全量）。
# # 未在本机实测: 不适用 —— ★ 本脚本**已实测**（★ 各段耗时是 Measure-Command 量出来的）。
# # 许可:   本仓库 MIT。无第三方代码引入。
# # 覆盖:   全文件
# # ─────────────────────────────────────────────────────────────────────

[CmdletBinding()]
param(
    [switch]$Full,
    [string[]]$Tests = @(),
    #: ★ 只打印「将要做的写操作」，不真做。
    #:   T010/T011：本脚本含 3 处 `git add -A` 与 1 步「关 SolidWorks」——
    #:   它们都是**副作用**，而收尾链常被当成「只读检查」跑。
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
#: ★ 2026-10-03 合并后**自定位**：本脚本住在 <仓库根>/tools/ 下，
#:   所以仓库根 = 本脚本所在目录的上一级。原先写死 。
$R = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $R
$env:PYTHONPATH = "$R;$R\scripts;$R\mcp-server;$R\tools"
$env:PYTHONIOENCODING = 'utf-8'
#: ★★★ 2026-10-26（第 46 轮）**弹窗监控必须常驻** —— 每轮先确保它在跑。
#:   用户要求：「开发这个项目的时候必须这个弹窗的监控要一直常驻」。
#:   `--ensure` 是幂等的：已在跑就打印 PID 并返回 0，不会起第二份。
#:   ★ 为什么值得占这一步：`SLDEXITAPP.exe` 的 CEIP 错误框**点掉即重弹**，
#:     2 分钟就刷出 13 万行日志、用户看到一堆 Rx 窗口（第 46 轮查证）。
try {
    & python -B tools\sw_dialog_watch.py --ensure 2>&1 | ForEach-Object { "  $_" }
} catch {
    Write-Host "  ⚠ 弹窗监控 --ensure 失败（不因此中断收尾链）：$_"
}

$sw = [System.Diagnostics.Stopwatch]::StartNew()
function Step([string]$Name, [scriptblock]$Body) {
    $t = [System.Diagnostics.Stopwatch]::StartNew()
    & $Body
    "{0,-26} {1,7:N1} s" -f $Name, $t.Elapsed.TotalSeconds
}

Write-Output '── ① 生成器（门禁查的是它们的产物，必须先跑）──'
Step 'gen_level_audit'    { python scripts/gen_level_audit.py     *> $null }
Step 'gen_metrics'        { python tools/gen_metrics.py           *> $null }
Step 'gen_harvest_digest' { python tools/gen_harvest_digest.py    *> $null }
Step 'build_union_map'    { python tools/build_union_map.py       *> $null }
#: ★ 2026-10-02（轮 363）新增：把「已走死的路」清单重算一遍
#:   （★ 来源：轮 359–362 我重走了前人早已走死的 `revolve_boss` 轴路径）
Step 'gen_dead_ends'      { python tools/gen_dead_ends.py          *> $null }
Step 'gen_com_member_index' { python tools/gen_com_member_index.py *> $null }
# ★ 生成器可能有副作用（重写 metrics 等）⇒ 再同步一次快照（★ 0.3 s，便宜且必要）

Write-Output ''
Write-Output '── ② release_check（★ 内部已含 18 道门禁，**不必再单独跑**它们）──'
if ($DryRun) {
    $n = @(git status --porcelain | Measure-Object -Line).Lines
    Write-Output ("  [DryRun] 跳过 git add -A（原本会暂存 {0} 个改动）" -f $n)
} else {
    git add -A
    Write-Output "  git add -A 已执行（暂存全部改动）"
}
#: ★★★ 2026-10-01（轮 342）**先自己算出「偏离上游」那行，让它一轮就绿** ——
#:   实测：`release_check` 每轮 **31.5 s**，而它**第 1 轮总会因偏离数字不符而失败** ⇒
#:   改一行再跑第 2 轮 ⇒ **白花 31.5 s**（★ 91.5 s 里有 63 s 是这个）。
#:   ★ 而那行数字**我自己就能算**（`git diff --shortstat` + `git rev-list --count`）⇒
#:   ★★ **先预置，再跑一次** ⇒ 省掉一整轮。
#: ★ 2026-10-03 合并后：上游在合并后的仓库里**改叫 `upstream`**（`origin` 留给自建远端 ——
#:   否则裸 `git push` 会误推上游仓库，那是 AGENTS.md §七 点名的风险）。
#:   ★★ 而**远端不存在时不报错、优雅跳过**：没有上游照样能跑收尾链（那段只是刷新一行说明）。
$UP = 'upstream/main'
$stat = if (git rev-parse --verify -q $UP) { (git diff --shortstat $UP) -replace '\s+', ' ' } else { '' }
if ($stat -match '(\d+) files? changed(?:, (\d+) insertions?\(\+\))?(?:, (\d+) deletions?\(-\))?') {
    $nf = $Matches[1]
    #: ★ 正则捕到的是**字符串** ⇒ 要千分位就得先转 int。
    #:   ⚠ PowerShell 的 `if` 是**语句**不是表达式 ⇒ `[int](if … )` 会报"术语 if 不被识别"；
    #:   正确写法是 `$x = if (…) { [int]… } else { 0 }`。
    $ni = if ($Matches[2]) { [int]$Matches[2] } else { 0 }
    $nd = if ($Matches[3]) { [int]$Matches[3] } else { 0 }
    $nc = (git rev-list --count "$UP..HEAD").Trim()
    $dirty = if ((git status --porcelain | Measure-Object).Count -eq 0) { 'clean' } else { 'dirty' }
    $target = "> 偏离上游：$nf 个文件 / +$($ni.ToString('N0')) 行 / -$($nd.ToString('N0')) 行 · $nc 个 commit · 工作区 $dirty"
    python -c @"
import re, sys
from pathlib import Path
p = Path(r'''$R\docs\harvest-report.md''')
t = p.read_text(encoding='utf-8')
m = re.search(r'> 偏离上游：.*', t)
if m and m.group(0) != '''$target''':
    p.write_text(t.replace(m.group(0), '''$target''', 1), encoding='utf-8')
    print('  \u9884\u7f6e\u504f\u79bb\u884c: $target')
else:
    print('  \u504f\u79bb\u884c\u5df2\u5bf9')
"@
    if ($DryRun) {
        $n = @(git status --porcelain | Measure-Object -Line).Lines
        Write-Output ("  [DryRun] 跳过 git add -A（原本会暂存 {0} 个改动）" -f $n)
    } else {
        git add -A
        Write-Output "  git add -A 已执行（暂存全部改动）"
    }
    python tools/gen_harvest_digest.py *> $null
} else {
    Write-Output "  （算不出偏离统计，交给 release_check 自己的修法提示）"
}
$ok = $false
for ($i = 1; $i -le 3; $i++) {
    $o = python scripts/release_check.py 2>&1
    if ($LASTEXITCODE -eq 0) { Write-Output "  release_check: 第 $i 轮 OK"; $ok = $true; break }
    #: ★★ 2026-10-05 修（第三次数据损坏事故的根因）：**必须锚定行首**。
    #:   旧写法 `-match '> 偏离上游：'` 会命中 `check_negative_input_selfproof` 的审计诊断 ——
    #:   因为它**逐字回显** `probe_skip_semantics.py` 里含该串的那一行**源码**；
    #:   而那条在 release_check 输出里是**唯一**匹配（实测），`Select-Object -Last 1` 必中它
    #:   ⇒ 于是把**审计源码**写进了 `docs/harvest-report.md`（真报告那行被替换掉）。
    #:   ★ 形态实测：该行被重复前缀 **86** 次 / 2383 字符；**每跑一轮链就再污染一次**。
    #:   真报告那行是**带 4 空格缩进**的（见 `check_report_freshness.py` 的打印）⇒
    #:   `^\s*>` 两项都对得上：**命中真行**、**放过** `   L101 …` 那条诊断。
    $want = ($o | Where-Object { $_ -match '^\s*> 偏离上游：' } | Select-Object -Last 1)
    if (-not $want) {
        Write-Output '  release_check: 非"偏离"问题 —— 尾部：'
        $o | Select-Object -Last 8 | ForEach-Object { Write-Output ("    " + ([string]$_).Trim()) }
        break
    }
    $line = ([string]$want).Trim()
    python -c @"
import re, sys
from pathlib import Path
p = Path(r'''$R\docs\harvest-report.md''')
t = p.read_text(encoding='utf-8')
m = re.search(r'> 偏离上游：.*', t)
if m and m.group(0) != '''$line''':
    p.write_text(t.replace(m.group(0), '''$line''', 1), encoding='utf-8')
"@
    if ($DryRun) {
        $n = @(git status --porcelain | Measure-Object -Line).Lines
        Write-Output ("  [DryRun] 跳过 git add -A（原本会暂存 {0} 个改动）" -f $n)
    } else {
        git add -A
        Write-Output "  git add -A 已执行（暂存全部改动）"
    }
    python tools/gen_harvest_digest.py *> $null
}
if (-not $ok) { Write-Output '  ⚠ release_check 未在 4 轮内变绿' }

Write-Output ''
Write-Output '── ③ 测试（★ 默认聚焦；-Full 才跑全量）──'
if ($Full) {
    Write-Output '  ★ 全量（★ 只在发布前 / 改了共享基础设施时用）'
    python -m pytest tests -q --no-header -p no:cacheprovider 2>&1 |
        Select-String -Pattern 'passed|failed|^FAILED' | Select-Object -Last 3
} elseif ($Tests.Count -gt 0) {
    #: ★★★ 2026-10-01（轮 343）**加存在性检查** —— 真机踩到：★ 我传了 `tests/test_mold.py`
    #:   而真名是 `tests/test_sw_mold_contract.py` ⇒ ★ **pytest 静默跳过、脚本照样报 OK**
    #:   ⇒ ★★ **"跑了 0 个测试"与"测试通过"看起来一样**（★ 与事实 8/250 同一族纪律）。
    #:   ⇒ ★ 现在不存在的路径**直接报错并列出候选**（★ 让"没跑"可见）。
    $missing = @($Tests | Where-Object { -not (Test-Path (Join-Path $R $_)) })
    if ($missing.Count -gt 0) {
        Write-Output "  **✗ 这些测试文件不存在**：$($missing -join ', ')"
        $stem = ($missing[0] -replace '^tests/|\.py$', '') -replace '^test_', ''
        $cand = Get-ChildItem (Join-Path $R 'tests') -Filter "*$stem*" -ErrorAction SilentlyContinue |
                Select-Object -First 5 | ForEach-Object { "tests/$($_.Name)" }
        if ($cand) { Write-Output "    候选：$($cand -join ' · ')" }
        Write-Output '    ⚠ **不许把"文件不存在"当成"测试通过"**'
    } else {
        python -m pytest @Tests -q --no-header -p no:cacheprovider 2>&1 |
            Select-String -Pattern 'passed|failed|no tests ran' | Select-Object -Last 1
    }
} else {
    Write-Output '  （未指定 -Tests ⇒ 跳过；★ 那是有意的：本仓 1291 个测试里绝大多数与本轮改动无关）'
}

Write-Output ''
"── 合计 {0:N1} s（★ 全量 pytest 单独要 ~160 s）──" -f $sw.Elapsed.TotalSeconds

#: ★★★★★★★ 2026-10-04（轮 139）**收尾链跑完就关 SolidWorks** —— ★ 用户点的那条纪律：
#:   ★ 「★ **用完了就关掉 SolidWorks** —— 一轮真机活收尾时它是**关着的**、
#:      ★ **不是最小化的**、★ **也不是留着下轮接着用**」
#:   ★★ 「★ **同一轮里还有后续真机步骤时可以留着它；跨轮不许留** —— **收尾链跑完就关**」
#:     （★ 归口：`~/.dsh/纪律/资源与环境.md` §一 · ★ 由 `~/.dsh/AGENTS.md` 每轮注入）✓
#:   ★★★ **为什么必须**机械化**（★ 值记）**：★ 那条纪律**一直在**、
#:     而我**跨了十几轮没收** —— ★★ **⇒ 实测代价**：★ `cwbcbfmesh` **两个进程合计 27.4 GB**
#:        （★ 纪律记的实测是 8286 MB）⇒ ★★★ **⇒ "我会记得"不是机制** ✓
#:   ★★★★ **⚠ 为什么是 `--close` 而不是 `--restart`**：★ `--restart` 是"停完**重连**" ⇒
#:     ★★ **⇒ 重连会把它**又拉起来** ✗（★ 实测：★ kill 掉 28539 MB 那 9 个进程后
#:       几秒它就回来了、★ PID 全新 ⇒ 真凶是 `mcp-server/server.py` 的 connect）✓
#:   ★★★★★ **⚠ 安全**：★ `--close` **自带文档判定** —— ★ 只要有一个**不是自己开的**文档就**拒绝关闭** ✓
Write-Output ''
Write-Output '── ④ 关 SolidWorks（★ 纪律：跨轮不许留 · 收尾链跑完就关）──'
if ($DryRun) {
    Write-Output "  [DryRun] 跳过「关 SolidWorks」（原本会调 reclaim_solidworks.py --close）"
} else {
    python tools\reclaim_solidworks.py --close 2>&1 |
        Select-String -Pattern 'BEFORE|AFTER|拒绝|关完' |
        ForEach-Object { Write-Output ("  " + ([string]$_).Trim()) }
}
Write-Output '  ★ 关完**不要再调真机工具** —— 一调它就会被 `mcp-server` 拉起来。'
