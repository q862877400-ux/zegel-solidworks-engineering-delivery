# Q3 维度 · 空白 2：全量测试的**执行期**结果

> 观测时间 **2026-10-24** · 观测方式：**真跑** `python -m pytest tests -q`
> 复现：
> ```powershell
> # ① 直接跑（会被收集期阻断）
> python -m pytest tests -q -p no:cacheprovider
> # ② 排除 5 个阻断文件后跑（本文件的主要读数）
> python -m pytest tests -q -p no:cacheprovider --ignore=tests/test_mcp_backend_router.py ^
>   --ignore=tests/test_mcp_configuration_tools.py --ignore=tests/test_mcp_drawing_tools.py ^
>   --ignore=tests/test_mcp_headless_open_format.py --ignore=tests/test_spec212_unit_guard.py
> ```

---

### Q3-01 直接跑全量：**在收集期被中断**，一条用例都没执行

- **读数**：`pytest tests -q` ⇒ **2.37 s** 结束，`1 skipped, 1 warning, 5 errors`，
  末行 `Interrupted: 5 errors during collection`
- **5 个阻断文件**（逐字）：`test_mcp_backend_router` · `test_mcp_configuration_tools` · `test_mcp_drawing_tools` ·
  `test_mcp_headless_open_format` · `test_spec212_unit_guard`（原因均为 `tool_registry.GateError: 声明未过门禁`）
- **交叉核对**：`facts/F-tests.md` F-03 已记同一现象 ⇒ 本轮确认它**至今仍在**，且**导致全量无法一次跑完**
- **未确认**：无

### Q3-02 排除 5 个阻断文件后：**3944 passed · 89 failed · 63 errors · 16 skipped**，耗时 **1238 s（20 分 38 秒）**

- **读数**（pytest 汇总行逐字）：
  `89 failed, 3944 passed, 16 skipped, 2078 warnings, 63 errors, 39 subtests passed in 1238.29s (0:20:38)`
- **交叉核对**：`AGENTS.md` 记「全量 pytest **160.6 s**」⇒ 与本次 **1238 s** 相差约 7.7 倍
  （两侧口径可能不同：AGENTS 的 160.6 s 是某一时点、可能与本次机器状态/用例增长不同）
- **未确认**：耗时差异的成因（机器状态 / 用例增长 / 内部重复调 `release_check`）——未分段计时

### Q3-03 89 个失败按文件聚（前 12）

| 失败数 | 文件 |
|---|---|
| 14 | `tests/test_ec03_compiler.py` |
| 9 | `tests/test_stage7_housing.py` |
| 8 | `tests/test_s327_manifest_rules_runs.py` |
| 8 | `tests/test_relation_enum_alignment.py` |
| 5 | `tests/test_ec12_eval.py` |
| 4 | `tests/test_arity_tables_vs_reflection.py` |
| 4 | `tests/test_stage4_planner.py` |
| 3 | `tests/test_unattended_equivalence.py` |
| 3 | `tests/test_corpus_315.py` |
| 2 | `tests/test_official_names_only_contract.py` |
| 2 | `tests/test_effect_declarations.py` |
| 2 | `tests/test_ec03_unsat_core.py` |

- **未确认**：每个失败的根因——本次只统计分布，未逐个读断言

### Q3-04 63 个 error（setup 期）按文件聚（前 5）

| 错误数 | 文件 |
|---|---|
| 27 | `tests/test_s323_catalog.py` |
| 15 | `tests/test_stage1_registry.py` |
| 8 | `tests/test_server_wiring.py` |
| 7 | `tests/test_stage1_authorization.py` |
| 6 | `tests/test_stage2_expand.py` |

- **交叉核对**：`test_server_wiring.py` 的 8 个 error 与 `facts/B-tools.md` B-13 记的「8 errors at collection」一致
- **未确认**：其余 4 个文件的 error 原因（fixture 缺失 / 导入失败 / 断言前置）——未逐个读

### Q3-05 本维度**不构成**「项目测试是否健康」的结论

- **记录员注（陈述）**：以上是**本机、此刻**的读数。`AGENTS.md` 事实 57 与 62 都记过「测试绿灯可能只是环境恰好满足」
  ⇒ 换机器、换 SolidWorks 文档状态，这些数字会变
- **未确认**：89 failed + 63 errors 里有多少属于「需要 SolidWorks/真机」、多少属于「纯逻辑回归」——本次未按依赖分类

---

## 与本台账其它条目的关系

| 条目 | 读数 | 关系 |
|---|---|---|
| `facts/F-tests.md` F-03 | 收集期 5 errors | 本轮确认仍在，且**阻断全量** |
| `facts/M-tests-run.md` M-02 | 34 个门禁类文件：258 passed / 1 failed | 门禁类单独跑只有 1 个失败；全量有 89 个 ⇒ 失败集中在非门禁类 |
| `facts/B-tools.md` B-13 | `test_server_wiring.py` 8 errors | 本轮同样 8 个 |
