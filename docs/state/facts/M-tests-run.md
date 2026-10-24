# M 维度 · 测试执行期结果（分层抽样）

> 观测时间 **2026-10-24** · 观测方式：**真跑** `tests/test_*_gate.py`（门禁类，离线静态），每文件独立子进程 + 单文件超时 240 s、总预算 1,200 s
> **不是全量**：只跑了 34 / 478 个测试文件，见 M-05
> 复现总命令：
> ```powershell
> python docs\state\probes\probe_tests_run.py --json docs/state/inventory-m.json
> ```

---

### M-01 抽样范围：34 个 `test_*_gate.py`（占 478 个测试文件 **7.1%**）

- **读数**：`tests/test_*_gate.py` **34** 个 · 全仓 `test_*.py` **478** 个（F-01）
- **选取理由（陈述）**：门禁测试是**离线静态**的，不需要 SolidWorks，可安全真跑
- **未确认**：其余 444 个文件的执行期结果——本次**未跑**

### M-02 34 个文件全部跑完：**258 passed · 1 failed · 2 skipped · 112 warnings**

- **读数**：`passed` **258** · `failed` **1** · `skipped` **2** · `warning` **112**
- **读数**：**0** 个超时 · **0** 个因预算未跑（全部在 1,200 s 预算内完成）
- **非零退出**：**1** 个文件（见 M-03）
- **证据**：`inventory-m.json` 的 `aggregate` / `rows`
- **未确认**：112 个 warning 的具体内容——本次未逐条分类

### M-03 唯一失败：`test_spec212_rule2b_gate.py::test_all_repo_specs_pass_the_new_gates`

- **读数**：该文件 `6 passed / 1 failed`，耗时 **0.4 s**
- **失败位置**：`tests/test_spec212_rule2b_gate.py:113`
- **断言原文（逐字）**：`assert not bad, "★ 有 %d 个工具过不了新门禁：\n%s" % (len(bad), "\n".join(bad[:6]))`
- **失败消息（逐字）**：
  ```
  AssertionError: ★ 有 1 个工具过不了新门禁：
    solidworks_feature_revolve_cut: 规则 2 违反：工具 'solidworks_feature_revolve_cut'
    的入参 'angle_rad' 像是**角度**，却不以 '_deg' 结尾 —— 要么改名
  ```
- **与其它维度的交点（陈述，不做关联推断）**：同一个对象也出现在 `facts/B-tools.md` B-11 的 `check_specs` 5 条问题里（第 1 条）
- **未确认**：该测试是否被任何门禁/收尾链调用——本次未查引用

### M-04 5 个「收集期阻断」文件里共有 **26** 个 test 函数

| 文件 | `def test_` 个数 |
|---|---|
| `test_mcp_backend_router.py` | **2** |
| `test_mcp_configuration_tools.py` | **4** |
| `test_mcp_drawing_tools.py` | **4** |
| `test_mcp_headless_open_format.py` | **8** |
| `test_spec212_unit_guard.py` | **8** |
| **合计** | **26** |

- **观测方式**：AST 统计（**不执行**）——这 26 个用例在收集期就被 `tool_registry.GateError` 阻断（F-03）
- **未确认**：若解除阻断，这 26 个用例会通过还是会失败——**未执行，未知**

### M-05 明确没有跑的部分（占 92.9%）

- **读数**：未跑 **444** 个测试文件（478 − 34）
- **其中含**：需要 SolidWorks 真机的用例、5 个收集期阻断文件、以及其余各类
- **记录员注（陈述）**：因此**本维度不构成**「全仓测试是否通过」的结论；它只记录「门禁类 34 个文件的执行期结果」
- **未确认**：全量执行的结果与耗时——本次刻意未跑（AGENTS 记全量 pytest 约 160.6 s，但其中三条测试内部各自又跑一遍 `release_check`）

### M-06 2 个 skipped 出现在 `test_report_freshness_gate.py`

- **读数**：`test_report_freshness_gate.py` = `7 passed / 2 skipped`
- **交叉核对（陈述）**：`AGENTS.md` §七 逐字记「`report_freshness` 门禁会 **SKIP**（那是便携性守卫，不是失败）」，
  原因是 `upstream/main` 这个 ref 不存在（本机未 `git fetch upstream`）
- **未确认**：那 2 个 skipped 的具体触发条件——本次未读该测试的 skip 判据

---

## 证据索引（每个事实号 → `inventory-m.json` 的键）

| 事实 | 证据载体 |
|---|---|
| M-01 | `scope` + `rows`（34 条） |
| M-02 | `aggregate` + `skipped_for_budget`（空） |
| M-03 | `files_with_nonzero_exit` + 单独复跑 `pytest tests\test_spec212_rule2b_gate.py` 的输出 |
| M-04 | AST 统计（本文件表格）；阻断原因见 `facts/F-tests.md` F-03 |
| M-05 | `rows` 的条数 34 与 F-01 的 478 相减 |
| M-06 | `rows` 中 `test_report_freshness_gate.py` 的 `counts.skipped` |

---

## 本节未覆盖（留给后续补充）

- 444 个未跑文件的执行期结果（尤其需要 SolidWorks 的那些）
- 112 个 warning 的内容分类
- 解除 `GateError` 阻断后那 26 个用例的结果
- 全量 pytest 的耗时与失败清单
