# Git 规则（仓库/上游/归档 + 提交纪律 + 批准边界）

> 从 `AGENTS.md` §七 搬出（2026-10-24），逐字保留。

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
