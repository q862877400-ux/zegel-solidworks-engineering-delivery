## 四、A1–A10 逐条自评（**编号与 `AGENTS.md §一` 一致**）

> ⚠ **本节曾经用另一套编号**（**同名不同事**）：旧表的「A3」实为 A5、「A5」实为 A6、
> 「A7」实为 A8，并混入「官方 API 覆盖」「目录结构与上游一致」两条**非 A 判据**的行，
> 同时**缺 A1 / A9 / A10**。2026-10-01（轮 82）逐条重写，
> 并加门禁 `scripts/check_report_criteria_alignment.py` **把"编号一致"变成机器判据**。
> ★ 同类问题此前已犯过一次（旧 §一 的「A1」指的是官方 API 覆盖）⇒ **靠人记必然再漂**。

| # | 判据（`AGENTS.md §一` 原文精简） | 自评 | 依据（**可复跑的枚举命令**） |
|---|---|---|---|
| **A1** | 四家能力广度已并入：矩阵里每一格都有来源，或写明「不做 + 原因」 | ✅ **成立** | `docs/union-coverage-matrix.md` 可重新生成（`tools/build_union_map.py`）；「不做 + 原因」**4 条**（`docs/union-not-doing.json`），由 `check_union_conventions` 的 **R14** 守 |
| **A2** | **两层 provenance**：① 来源级（每条来源带 `owner/repo` + 许可 + `declared_verified` + `note`）；② 能力级（`source_verified` 条目须齐四字段） | ✅ **成立**（②**空满足**） | `check_union_conventions` 的「规则 5 · 出处与许可」段 `[PASS]`；其「清单形状」段 `[PASS]`。⚠ ② 的 `source_verified` 条目数现为 **0** ⇒ **空满足**（一旦新增即强制生效） |
| **A3** | 五统一门禁通过：命名 / 单位 / 选择 / 验证等级 / 出处 | ✅ **成立** | `python scripts/check_union_conventions.py` **exit 0**（七段全 PASS），且已接进 `release_check.py` |
| **A4** | `level` 取自五级枚举；`verified` 必须有我们自己的运行证据 | ✅ **成立** | 31 条：**verified 27 · stitched 3 · not_implemented 1**；**`verified` 但无 `evidence` 的 = 0 条**（R4 守） |
| **A5** | 每个新增文件里每个 COM 调用的参数顺序与类型与官方签名对齐 | ✅ **成立** | `docs/signature-audit.md` 7 批次；**711 个调用点 arity 自动比对**（**696 通过 / 0 查不到 / 2 真缺陷已修 / 0 未裁定**）；累计修复签名缺陷 **7 处**；合计行算术自洽已门禁化 |
| **A6** | 许可无越界：AGPL/GPL/无许可 的代码没被抄进来；Apache-2.0 带 NOTICE | ✅ **成立**（口径见右） | `python scripts/check_license_redlines.py` **exit 0**；`THIRD-PARTY-NOTICES.md` 已入库。⚠ **门禁只判声明是否自洽/越界**，**不判声明是否属实**（「某函数到底抄没抄」靠人核）|
| **A7** | 全文没有一处把 `source_verified` 或 `stitched` 写成 `verified` | ✅ **成立** | `check_union_conventions` 的 R4：`level` 必须在五级枚举内 + `verified` 必须有 `evidence` ⇒ 「把 stitched 写成 verified」会被**两条同时**抓住 |
| **A8** | 报告写明**并入了什么、仍空缺什么、为什么空缺** | ✅ **成立** | 本文 §二（补齐）/§三（空缺 + 原因）/§八之补（轮 13+ 的生成物 `docs/harvest-digest.md`）+ **本节**（编号已机器对齐）|
| **A9** | 空白域护城河有**可跑的工程实现**（拓扑优化优先），不是只有文档 | ⚠ **成立但有一域受限** | `topology_optimization` **verified**（`tools/capture_topology_evidence.py` 真机闭环）· `costing` **verified**（`tools/verify_costing_e2e.py`）· `animation_export` **stitched**（API 链真机通，但**缺 SolidWorks Motion 加载项** ⇒ 已如实记）|
| **A10** | 按需搬取：每件搬进来的都过一遍「并入六条规则」 | ✅ **成立** | `check_union_conventions` exit 0（R1–R14 全段）；并入清单见 `docs/union-coverage-matrix.md §五` |

**小结**：**9 条成立 · 1 条部分成立**（A9 的 `animation_export` 受**外部依赖**阻塞 ——
那需要 **SolidWorks Motion 加载项**，属 `AGENTS.md §九.4`「需要用户提供的东西」⇒ 已停下报告）。

