# 智能体团队分工

> 角色定义在 `~/.dsh/team-roles.yaml`（全局）；用法见 `~/.dsh/智能体团队-使用说明.md`。三个角色的工具限制是机制锁死的。

| 角色 | 工具限制 | 在本项目干什么 | 绝不能干 |
|---|---|---|---|
| researcher | 禁 write/edit/pwsh | 跑 `sw_know.py` / `swdoc.ps1` / 反射建能力全景；扫 `C:\swprojects\` 下 21 个项目定位可移植实现 | 不改任何文件；只报事实，不提改动建议 |
| coder | 可写 | 按 `gap-analysis.md` 移植或新写 `scripts/sw_*.py` + `tests/test_*.py` + `provenance` 标注 | 不启动 SolidWorks、不跑 COM、不编译 C#/C++；不写「已验证」 |
| reviewer | 禁 write/edit/pwsh | 复核签名比对表、许可合规、结构一致性、五统一门禁、禁词 | 只报问题，不动手修 |

派活按「来源 + 域」两个维度切，互不重叠：来源组一人一家（四家外部 MCP 各扫工具清单、许可与测试口径），域组按 `高级/专项`、`曲面`、`钣金` … 分批。每个任务登记 `write_scopes`（绝对路径，代码副本不在 DSH 工作区内），例如 `C:\swprojects\sw-skill-fork\scripts\sw_simulation*.py` 与其对应的 `tests\`。

lead 维护 `docs/union-coverage-matrix.md` 与 `docs/gap-analysis.md` 的打勾状态，并汇总 `docs/harvest-report.md`。
