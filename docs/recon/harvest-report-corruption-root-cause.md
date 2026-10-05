# `docs/harvest-report.md` 第三次被写坏的**根因**（★ 与两份交接文档的归因**不一致**）

> ★★ **一句话**：写坏那行文件的不是 `tools/probe_skip_semantics.py`（它**只读**，坏副本写去 `%TEMP%`），
> 而是**每轮都要跑的 `tools/round_chain.ps1`** —— 它的「抓偏移行」判据太松，
> 命中了 `check_negative_input_selfproof.py` 的**审计诊断**（那条诊断**逐字回显了源码**）。
> ★ 本文不含行号。★ 证据可复跑。★ **已修**（见 §五），并已按本仓自带工具修回文件。

---

## 一 · 事实（本轮实测，2026-10-05）

| # | 事实 | 证据 |
|---|---|---|
| 1 | `docs/harvest-report.md` 第 6 行被写坏，**working tree 脏、未提交** | `git diff` ⇒ `1 insertion(+), 1 deletion(-)`；mtime `21:02:54`（**发现时已 49 分钟**，无 git 进程在跑） |
| 2 | 坏行 **2383 字符**，其中审计片段 `L101  bad2_text` 重复 **86 次** | 直接读该行：出现次数 = 86 |
| 3 | 那行**结尾**是 \"…\", ro, c   [自证✓] | 即 `check_negative_input_selfproof.py` 的输出格式 `   L%-4d %-76s [%s]` |
| 4 | ★ 该损坏使 **`report_freshness` 门禁变红** | 直接调 `_run_report_freshness_gate()` ⇒ 返回体 `status` = fail |
| 5 | ★ 修复后该门禁变绿、文件与 HEAD **逐字节相同** | 跑本仓自带 `tools/repair_harvest_report_line.py` ⇒ exit 0；`git diff --stat` 空 |

---

## 二 · ★★★ 根因链（四环，每环都有实测）

```
① tools/probe_skip_semantics.py 的第 101 行**源码里含字面量**「> 偏离上游：」
      （它是个 re.sub —— 拿真报告造「坏报告」用的）
                 ↓
② scripts/check_negative_input_selfproof.py 审计「负例输入有没有自证」时，
      **把那一行源码逐字回显**到自己的输出里（★ 按设计这是给修法看的）
                 ↓
③ tools/round_chain.ps1 抓「偏离行」用的判据是**子串** -match '> 偏离上游：' ⇒
      ★ 它同时命中②那条诊断；而实测**那条在 release_check 输出里是唯一匹配**
      ⇒ Select-Object -Last 1 **必中它**
                 ↓
④ round_chain 把这条**审计源码**写进 docs/harvest-report.md
      （t.replace(m.group(0), $line, 1)，m = re.search(r'> 偏离上游：.*')）
```

### 2.1 ★ 为什么会**越滚越多**（86 次那个形态的解释）

第 ④ 步写进去的那行**它自己就含**「> 偏离上游：」（在 `re.sub(r` 之后 29 个字符处）。
⇒ 下一轮 `re.search(r'> 偏离上游：.*')` 命中的是**它自己的中段**，
   替换时就在前面**又拼一段** `L101  bad2_text = re.sub(r` ⇒ **每轮 +1，单调累积**。

★ 这解释了坏行长度与重复计数，也解释了本仓修复工具注释里那句
「实测：那一行前面被拼了**三段**重复的审计源码文本」（那次发现得早）。

---

## 三 · ★★ 归因更正（两份交接文档都写错了）

| 文档 | 逐字原文 | ★ 事实 |
|---|---|---|
| `specs/207-agent-team-tool-routing/HANDOFF.md` §一 1.3 | 「`tools/probe_skip_semantics.py` —— ★ **它会把 `docs/harvest-report.md` 写坏**，**不要跑**」 | ★ **它对该文件只读不写** —— 坏副本写去 `tempfile.gettempdir()` 下的 `bad-harvest-report.md` |
| `specs/207-agent-team-tool-routing/DECISIONS.md` §三 | 「一个活的雷：`probe_skip_semantics.py` **会把 `docs/harvest-report.md` 写坏**（读真文件做正则替换再写回）」 | ★ 「写回」那半句不成立 |

★★ **这个错误归因有实际危害**：它让人以为「**只要不跑那个脚本就安全**」，
⇒ ★★ **于是放心跑 `round_chain.ps1`（每个回合的标准动作）—— 而它才是写坏文件的那一个**。
★ 这也解释了为什么**同一事故发生了三次**：前两次只修好了**症状**（把那一行改回去），
**根因一次都没动**。

---

## 四 · ★★★ 根因的可复跑证明（不写任何文件，只打印会选哪一行）

```powershell
$env:PYTHONIOENCODING='utf-8'
$o = python scripts/release_check.py 2>&1
$old = ($o | Where-Object { $_ -match '> 偏离上游：' })      # 旧判据（有 bug）
$new = ($o | Where-Object { $_ -match '^\s*> 偏离上游：' })  # 新判据（已修）
Write-Output ('旧判据匹配 ' + $old.Count + ' 行')
$old | ForEach-Object { Write-Output ('  ' + ([string]$_).Trim().Substring(0,90)) }
Write-Output ('新判据匹配 ' + $new.Count + ' 行')
```

**实测结果**（在修好文件、但自证门禁**仍然红**的当前树上跑）：

| 判据 | 匹配行数 | 命中的是什么 | 会不会写坏报告 |
|---|---|---|---|
| 旧 `-match '> 偏离上游：'` | **1** | `L101  bad2_text = re.sub(...)` 那条审计诊断（**88 字符**，不以 `> ` 开头） | ★★ **会** |
| 新 `-match '^\s*> 偏离上游：'` | **0** | —（这次红的是自证门禁，**本来就不该抓偏离行**） | ★ **不会** |

**两行负例对照**（真行 vs 诊断行）：

| 判据 | 命中真行 `    > 偏离上游：570 个文件 / …` | 命中那条诊断 | 结论 |
|---|---|---|---|
| 旧 | True | **True** | ★ **错**（分不开） |
| 新 | True | **False** | ✓ 正确 |

★ 真报告那行**带 4 空格缩进**（由 `check_report_freshness.py` 打印），所以 `^\s*>` 既命中真行、又放过缩进后是 `L101` 的那条诊断。

---

## 五 · ★ 已做的修复（一处，最小改动）

| 文件 | 改动 | 验证 |
|---|---|---|
| `tools/round_chain.ps1` | 抓偏离行的判据 `-match '> 偏离上游：'` ⇒ **`-match '^\s*> 偏离上游：'`**（加行首锚定 + 注释写明三次事故的根因） | ① `Parser::ParseFile` ⇒ **0 处语法错误**；② §四 两张表（真实输出 + 负例对照） |
| `docs/harvest-report.md` | ★ **用本仓自带 `tools/repair_harvest_report_line.py` 修回**（从 HEAD 取值，只改那一行，不手打） | 修后 `git diff --stat` **空**；`report_freshness` 从 fail ⇒ pass |

★ **副作用（好的）**：修好判据后，若 release_check 红在**别的**门禁上，
`round_chain` 会走 `if (-not $want)` 分支 ⇒ **如实报「非偏离问题 —— 尾部」**，
而**不再**把别的门禁的输出塞进报告。

---

## 六 · ⚠ 仍未处理（**不属本次写盘范围**）

| # | 事项 | 现状 |
|---|---|---|
| 1 | `tools/verify_union_349.py` L112 缺自证 ⇒ **自证门禁仍红**（`release_check` exit 1） | ★ 属**规格 207-union-gap-verify** 那条线的文件；本轮**未动**。修法门禁自己给了：在该行后加 `assert new != old` 或打印字节数 |
| 2 | ★ **缺一条负例测试** | 本仓纪律（事实 62）：「一个门禁『写了』不等于它『有效』—— 负例测试是唯一的证明」。本轮只做了**手工**负例对照（§四），**未落成测试** |
| 3 | 两份交接文档的错误归因**未改原文** | 本文件只做更正与指认；改那两份文档是否越界，留给主线判断 |
| 4 | `docs/recon/` 下**大量产物未被 git 跟踪** | 含规格 207 路由研究的终稿；本轮只提交了与本更正相关的那一份 |

---

## 七 · 可复用的三条

1. ★★★ **「抓某一行」的判据必须锚定行首** —— 子串匹配会在「别的东西回显了同一段文本」时静默抓错。
2. ★★★ **一个「只读」的脚本被指控为「写坏文件」时，要去读它到底写没写** ——
   本轮两条交接文档的归因**都没读代码**，代价是**根因多活了两次事故**。
3. ★★ **事故修「症状」时要在同一处留根因** —— 本仓已为这件事写了专门的修复工具（说明那时就知道形态），
   而**修复工具治不了复发**；★ 根因在**写方**，不在**被写方**。
