# 智能体团队分工

> 角色定义在 `~/.dsh/team-roles.yaml`（全局）；用法见 `~/.dsh/智能体团队-使用说明.md`。三个角色的工具限制是机制锁死的。

| 角色 | 工具限制 | 在本项目干什么 | 绝不能干 |
|---|---|---|---|
| researcher | 禁 write/edit/pwsh | 跑 `sw_know.py` / `swdoc.ps1` / 反射建能力全景；扫 `C:\swprojects\` 下 21 个项目定位可移植实现 | 不改任何文件；只报事实，不提改动建议 |
| coder | 可写 | 按 `gap-analysis.md` 移植或新写 `scripts/sw_*.py` + `tests/test_*.py` + `provenance` 标注 | 不启动 SolidWorks、不跑 COM、不编译 C#/C++；不写「已验证」 |
| reviewer | 禁 write/edit/pwsh | 复核签名比对表、许可合规、结构一致性、五统一门禁、禁词 | 只报问题，不动手修 |

派活按「来源 + 域」两个维度切，互不重叠：来源组一人一家（四家外部 MCP 各扫工具清单、许可与测试口径），域组按 `高级/专项`、`曲面`、`钣金` … 分批。每个任务登记 `write_scopes`（绝对路径，代码副本不在 DSH 工作区内），例如 `C:\swprojects\sw-skill-fork\scripts\sw_simulation*.py` 与其对应的 `tests\`。

lead 维护 `docs/union-coverage-matrix.md` 与 `docs/gap-analysis.md` 的打勾状态，并汇总 `docs/harvest-report.md`。

## 多用 space-bunny

**space-bunny 免费，且实测能干机械穷举、全面阅读、逐条对账、抄录、模板产出、语义配对与近边界探针草案**，因此这类活默认派它干。三种模式：核心工作派三路独立做（各写独立文件，避免候选正文灌进 Lead 上下文），再派第四路当裁判打分并指出该并入哪些片段；很有用但平时成本高的活整批丢给它（全面扫描、全面阅读、穷举核对、逐条对账）；判据设计、真机执行（COM 单源）、门禁本体、known-facts、提交由 Lead 自己做。

能力档实录在 `specs/202-user-coverage-gaps/recon/bunny-L1..L5*`。L1 抄录。L2 机械聚合：读 83 个函数、认出 67 个有官方成员、去重出 143 个成员名，并自己发现 `read` 工具的行号偏移。L3 模板产出：反推出工具注册的 import 机制，认出带连字符的父目录不能当模块名，找到 `scripts/sw_drawing.py` 那座兼容桥。L4 语义配对：把「能读这种表」与「能建这种表」分开判。L5 近边界探针草案：找出探针里 `GetBreakLineCount` 的 out 参数用法错。

已被真决策采用的外派产物：`recon/scan-S1a|S1b|S2a|S2b|S3-1..3|S4` 七份扫描、`recon/scan-contract-audit.md`（30 份官方契约逐份对账，可信 17 / 有缺 13 / 不可信 0）、`recon/cand-A|B|C.md` 与 `recon/cand-verdict.md`、`recon/probe-verdict.md`。

**派活时写清三条**。一，给文件路径并明确要求重新读，否则它会按过时的签名准备实参。二，显式说明 `param_alias` 要应用，否则它会把好参数当成坏参数报。三，要求每条结论带可搜索的原文片段、不要行号，因为行号随代码漂移（实测偏 47 行）。

**它的判据有已知弱点，产出永远要经 Lead 复核**：它会照抄想象或过时的契约，也会把一条错的既有结论当既定事实。因此它的产出不许直接进 `capabilities.yaml` 的 `verified`。
