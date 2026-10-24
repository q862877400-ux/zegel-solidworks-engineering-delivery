# 验收标准 A1–A10（交付判据）

> 从 `AGENTS.md` §一 搬出（2026-10-24），逐字保留。根指令文件只留摘要 + 链接。

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
