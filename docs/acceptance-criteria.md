# 验收标准 A1–A10（交付判据）

> 从 `AGENTS.md` §一 搬出，根指令文件只留摘要 + 链接。
> A1 / A8 / A9 的措辞按 [`PROJECT-CHARTER.md`](PROJECT-CHARTER.md) 第四节与
> [`ENGINEERING-PATH.md`](ENGINEERING-PATH.md) 重写：判定为「工程合格导向」，
> 不以并入广度或攻空白域作交付判据。
> A1–A10 的**编号不变**（`scripts/check_report_criteria_alignment.py` 按编号对账）。

| # | 判据 | 怎么验 |
|---|---|---|
| A1 | **工程合格优先于广度**：产品的验收判据是 [`PROJECT-CHARTER.md`](PROJECT-CHARTER.md) 第四节的 E1–E7（全约束 / 参数化可重建 / 特征树可编辑 / 装配自由度闭合 / 图样合规 / 工艺可行 / 结论可溯源），**不是工具条数**。域覆盖矩阵仍有意义，但它是**取材地图**，不再是进度指标 | 每条 E 有采集器 + 判定器 + 坏样件，见 [`ENGINEERING-PATH.md`](ENGINEERING-PATH.md) 第四节；`docs/union-coverage-matrix.md` 可重生成（作参考）|
| A2 | 两层 provenance 都要：① 来源级——`tools/union-sources.json` 的每个来源带 `owner/repo` 全名 + 许可（白名单内）+ `declared_verified` + `note`；② 能力级——`capabilities[].provenance` 对来源派生的条目（`level: source_verified`）必须齐 `repo`/`license`/`files`/`upstream_verified` 四字段。①与②不是同一件事：① 说的是「哪几家、什么许可、他们自己声明跑过什么」；② 说的是「这一条能力是从哪条来源派生的」。`level: verified` 只表示「有我们自己的运行证据」，不表示「代码是我们写的」 | ① `python scripts/check_union_conventions.py` 的「规则 5、出处与许可」段；② 同门禁的「清单形状」段 |
| A3 | 五统一门禁通过：命名/单位/选择/验证等级/出处 | `scripts/check_union_conventions.py` 退出码 0，且已接进 `release_check.py` |
| A4 | 每个条目的 `level` 取自五级枚举；`verified` 必须有我们自己的运行证据 | 逐条核对 `capabilities.yaml` |
| A5 | 每个新增文件里每个 COM 调用的参数顺序与类型与官方签名对齐 | `docs/signature-audit.md` + `scripts/check_signature_audit_freshness.py` |
| A6 | 许可无越界：AGPL/GPL/无许可/全版权保留的代码没被抄进来；Apache-2.0 来源带 NOTICE 义务 | 逐文件对照 [`sources.md`](sources.md) 的许可判定表 |
| A7 | 全文没有一处把 `source_verified` 或 `stitched` 写成 `verified` | grep 全文，禁词 0 命中 |
| A8 | **进度按施工步骤报**：写明当前走到 [`ENGINEERING-PATH.md`](ENGINEERING-PATH.md) 第六节的哪一步（S0–S6），该步的完成标准逐条是否满足，以及同一首件在 E1–E7 上的**逐条状态与证据变化**。不用代码行数、工具数、规格勾数报进度 | 该步完成标准的逐条核对 + 首件 E1–E7 状态表 |
| A9 | **规范层（L2）可查、可指认**：工程结论能给出标准条款出处；未入库的标准按规矩先征得同意再入库，入库后以原文核验 | L2 查询面 + 引用可点开原文 |
| A10 | 按需搬取：每一件搬进来的东西都过一遍「并入六条规则」，冲突在搬进来的当时解决 | `scripts/check_union_conventions.py` 退出码 0 + 并入清单逐条核对 |

> A1–A10 是交付判据，不是每轮都要全绿：A3（门禁）是可执行的不变量，任何时候都该绿；
> 其余随 E1–E7 与 S0–S6 逐条满足。

进度与下一步看 [`ENGINEERING-PATH.md`](ENGINEERING-PATH.md) 第六节的步骤状态、
`capabilities.yaml`（每条带 `level`，`verified` 另带 `evidence`）、
[`PROJECT-CHARTER.md`](PROJECT-CHARTER.md) 第四节（E1–E7 判据）——
状态由清单与判据报告承载，不写进本文件。
