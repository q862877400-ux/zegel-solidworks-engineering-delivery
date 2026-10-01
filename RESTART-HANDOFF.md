# 重启交接（RESTART-HANDOFF）

> 写于：2026-10-01 · **轮 60 收工后** · 用户要求重启会话
> 用途：重启后**先读这一份**，不必翻长会话历史。
>
> ⚠⚠ **本文件里出现的任何具体数字（HEAD 哈希、文件数、条数、测试通过数、游标编号）
> 都是**写这份时的快照**，**不是权威**。**权威是现场**：`git log/status/diff` 与
> §四 那串门禁命令。**
> **为什么写这句**：本文件**第一版**就把 HEAD 写死在文里，而**提交它的那次提交立刻让它失真**
> —— 那是本项目「数字失真」家族的**第 5 例**，且是**当场造的**。
> ⇒ 凡「会随提交而变」的值，要么**现场取**，要么指向**有门禁守着的那一处**
> （`docs/harvest-report.md` 开篇那行由 `scripts/check_report_freshness.py` 守）。

## 一、目标（未变）

按 `docs/ROADMAP.md` 全自动推进 SolidWorks 自动化项目：
1. Spec Kit 全路径跑每个特性，产出落 `D:\AI\SW\specs\<NNN>-<slug>\`；
2. 完成 P0–P8，补齐 A1/A2/A5/A6/A8/A9/A10；
3. **每阶段收工必须**：跑该阶段验收命令确认真绿 → 更新 `ROADMAP.md §一` 游标 → 写调整记录 → **两仓库各自 commit**。

**三条红线（任何模式不豁免）**：不删数据 / 不删仓库 / 不强推 · 不对外发布 · 不碰只有用户能提供的东西（凭据、业务口径）。
**推送仍未授权**（用户：「GitHub 上的东西不着急，等我们完全开发完毕了再上传」）⇒ 只做**本地** commit。

**Goal 工具**：`goal-a428b6f9-6683-46e6-b406-2cc4f394a769` · `roundsStarted=60` · `maxGoalRounds=200` · phase `active`。
⚠ **重启后 goal 会被 disarm** ⇒ 用户说「继续」时用 `update_goal action=resume` 重新激活。

## 二、落盘状态（写这份时**两仓库都干净**）

⚠ **不要在本文件里找 HEAD 哈希** —— 写死的那一刻它就开始过期（**本文件第一版就犯了这个错**：
写了 `24eb97f`，而我提交这份文件的那次提交立刻让它失真 —— 这是本项目「数字失真」家族的**第 5 例**，
且是**当场造的**）。 ⇒ **现场取，那才是它的「家」**：

```powershell
git -C 'D:\AI\SW'                  log --oneline -1     # 工作区（只放产物）
git -C 'C:\swprojects\sw-skill-fork' log --oneline -1   # 代码副本（唯一改代码的地方）
git -C 'D:\AI\SW' status --porcelain                    # 期望：空
git -C 'C:\swprojects\sw-skill-fork' status --porcelain  # 期望：空
```

规模（相对上游 `origin/main` = `8be39ac`，**这个也要现场取**）：
```powershell
git -C 'C:\swprojects\sw-skill-fork' diff origin/main --shortstat
```
⚠ 精确值在 `docs/harvest-report.md` 开篇那行，且**它有门禁守着**（`scripts/check_report_freshness.py`）
—— **别在这里抄一份**（那就又造了一个会腐坏的数字）。

## 三、下一步（按优先级，**轮 61 收工后更新**）

| 优先 | 做什么 | 为什么是它 |
|---|---|---|
| ~~1~~ | ~~`costing` 升 `verified`~~ | **✅ 轮 61 已完成**（真机完整闭环 `verdict: pass`，`total_to_manufacture = 3.271449904`；验收命令 `python tools/verify_costing_e2e.py`） |
| **1** | ★ **`animation_export` 的两源查证** | 护城河三域里**唯一剩下的空缺**（现 `not_implemented`）。用 `C:\swapi\` + CHM 查「**AVI 由哪个成员真正写出**」；查不到就按 `§九.2` 标「无法缝合」并写进报告空缺段。⚠ **不要**拿 `SaveEntireAnimation` 蒙混（那是「是否保存整个动画」的属性） |
| **2** | ★ **`x or <默认值>` 吞掉 0 的 38 处存量** | 门禁（`check_env_pitfalls.py` 检查③）已记账在 `docs/falsy-zero-baseline.txt`，**只拦新增**。修一处就从基线删一行。⚠ **每处都要判断「那个成员的 0 是否有意义」**，不要无脑批改（事实 61） |
| 3 | `harvest-report.md` 正文**轮 13–61 的产出**仍未逐段补 | 现状已指向 `ROADMAP §一` 游标；这份报告落后 48 轮 |
| 4 | `signature-audit.md` 的**批次 1–4 手工统计**未纳入门禁 | 它们记录的是**当时的查证动作**，不是当前状态 ⇒ 若要核需先给可跑定义 |
| 5 | `D:\AI\SW\` 根上有一批我的临时脚本（`_debug_*.py` / `_scan_*.py` / `probe_costing_*.py` / `promote_costing.py` / `gen_falsy_zero_baseline.py` / `_allf.py` / `_bak_c3.py`） | 都是**我自己的产物**，未清理。要么收进 `tools/`（若还有用），要么归档 —— **下次顺手做** |

## 四、验收命令（**gate 绿基线** —— 重启后照这个跑一遍确认没坏）

```powershell
cd C:\swprojects\sw-skill-fork
$env:PYTHONPATH='C:\swprojects\sw-skill-fork;C:\swprojects\sw-skill-fork\scripts'
$env:PYTHONIOENCODING='utf-8'

python -W error::SyntaxWarning -m compileall -q scripts tools mcp-server tests   # exit 0
python scripts\sync_bundled_skill.py                                            # 282 files（改了运行时文件必须重跑）
foreach ($g in 'check_provenance','check_member_names','check_diff_markers','check_union_conventions',
               'check_env_pitfalls','check_spec_acceptance_paths','check_report_freshness',
               'check_signature_audit_freshness','check_license_redlines') {
  python "scripts\$g.py"; "  $g exit=$LASTEXITCODE"                              # 全部 0
}
python scripts\gen_level_audit.py                                               # R8：生成 docs/union-level-audit.md
python scripts\release_check.py                                                 # exit 0 / status: pass
python -m pytest tests -q --no-header -p no:cacheprovider                       # 912 passed / 17 skipped / 0 failed
```

⚠ **读退出码要精确**（事实 50）：`python x.py > out.txt 2>&1` 再读 `$LASTEXITCODE`，**不要**管道给 `Select-Object`。
⚠ **回归基线依赖 SolidWorks 的文档/选择状态**（事实 57）⇒ 记基线时要**同时记环境**。

**`release_check.py` 里的 9 道硬门禁 + 1 道诊断**：
`provenance · diff_markers · member_names · union_conventions(R1-R13) · env_pitfalls ·
spec_acceptance_paths · report_freshness · signature_audit_freshness · license_redlines · (interface_ownership 诊断)`

## 五、环境状态（⚠ **重启会改变它**）

| 项 | 写这份时 | 重启后 |
|---|---|---|
| SolidWorks | **PID 24252** · SW 2026 SP4.1（`revision 34.4.1`）· 窗口 `[零件1]` | **进程消失** ⇒ 需重连（`mcp__solidworks__solidworks_connect`） |
| Simulation 加载项 | **未加载**（`GetAddInObject('SldWorks.Simulation')` 返 None 那一族） | 重连后**再查一次**；拓扑/仿真的真机动作需要它 |
| 中文 UI | 草图名 `草图N`、基准面 `前视基准面` | 不变 |
| 界面语言/单位 | — | 不变 |

⚠ **永不 `OpenDoc6` 打开零件文件**（用 `new_document`）；`CommandInProgress=True` 与收尾释放是硬要求（铁律 2）。

## 六、地图（去哪找什么）

| 要什么 | 在哪 |
|---|---|
| **常驻指令 + 三条红线 + 六条铁律 + A1–A10** | `D:\AI\SW\AGENTS.md`（§六 只留 21 条速查） |
| **已知事实完整表（63 条）** | `D:\AI\SW\docs\known-facts.md` ← **查事实看这里** |
| **长程计划 + §一 游标（㊻ 条，最新一条 ㊻）** | `D:\AI\SW\docs\ROADMAP.md` |
| Spec Kit 产物 | `D:\AI\SW\specs\{001-topology-result-readout,002-merge-template,003-topology-closed-loop}\`（各 4 件，**全部 converged**） |
| 能力清单（**31 条**，带 `level` + `source` + `source_evidence`） | `C:\swprojects\sw-skill-fork\capabilities.yaml` |
| 等级审计（**R8 生成物**） | `C:\swprojects\sw-skill-fork\docs\union-level-audit.md` |
| 签名比对表（A5） | `...\docs\signature-audit.md` |
| 交付报告（A8） | `...\docs\harvest-report.md` |
| 第三方许可（A6） | `...\THIRD-PARTY-NOTICES.md` + `LICENSE` |
| 门禁实现 | `...\scripts\check_*.py` · 生成器 `...\scripts\gen_*.py` · 工具 `...\tools\*.py` |
| 外部只读来源 | `C:\swprojects\{Eduardof0nt,andrewbartels1,vespo92,Slacker-LLC}\` · 官方源 `D:\AI\SW\AI Solidworks\官方文档\` + `C:\swapi\` |
| 反射转储 | `D:\AI\SW\_raw\**\iface_*.txt`（**13 个不同程序集 / 15 份文件**）+ `enum_*.txt` |

## 七、本轮系列最容易重犯的坑（**都已记进 known-facts.md，这里只列最要命的**）

1. **「存在但数字失真」** —— 本项目**连续 4 例**（`harvest-report` 偏离数字、`signature-audit` 逐模块调用点、`THIRD-PARTY-NOTICES` 改动文件数、`ROADMAP §一` 的 `22/29`）。
   ⇒ **改了任何「当前状态」的数字，就要问「谁在守它」**；没有门禁守的，就给它一个（或指向有门禁的那一处）。现有守门人：`check_report_freshness` / `check_signature_audit_freshness` / `check_docs`(R8) / `check_map_fresh`。
2. **门禁必须有负例** —— 「一个存在但没人用的守卫与没有守卫等价」（事实 62）。加门禁**必须**同时加负例，并用 `git show <修复前>:<path>` 当负例输入。
3. **长内容走独立文件**（事实 48）—— Python 跨行字符串、PowerShell `` `u `` 是 Unicode 转义、here-string 里的反引号；`git commit -F <file>`。
4. **批量脚本先看 `git diff --stat`**（事实 61）—— 出现 `deletions` 就当自己的 bug 查；能用 `edit` 就别写批量替换。
5. **脚本失败后要 `git status`** —— 我失败过的脚本留下过乱名文件与「假提交」。
6. **分析范围要贴合组织单元**（事实 51）—— 一个测试文件的 import **不等于**一个能力的实现清单（轮 58 因此走错过）。
7. **静态分析判据要精确到结构** —— 子串匹配会撞上 CALL vs DEF、`MPL` 撞 `sample`、`.avi` 撞 `cavity`。

## 八、重启后第一句话该做什么

```
读 D:\AI\SW\RESTART-HANDOFF.md（本文件）
→ get_goal 看 roundsStarted；若 phase != active，用 update_goal resume
→ 跑 §四 的验收命令确认基线还是绿的
→ 从 §三 的「优先 1」接着做：costing 升 verified
```
