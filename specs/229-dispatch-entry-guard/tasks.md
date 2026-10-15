# tasks 229 —— 分发口守卫覆盖门禁

> ★ 每条都带**可复制执行**的验收命令。解释器：
> - 判据 / 门禁：`C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B`
> - **门禁全套**：`C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe`
>   （受管 3.13.12 **缺 comtypes/win32com** ⇒ 会触发交互式 COM 提示 ⇒ **假红 + 挂死风险**）

## T-229-01 量测（★ 先量，再动手）

- [x] 探针 `output/_probe229_buckets.py`（一次性，**不进仓库代码**）
- 验收：
  ```
  C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -W ignore output/_probe229_buckets.py 2>&1 | tail -3
  ```
  期望：`param 类分发口 = 37` · `buckets = {'generated-api': 12, 'has-nonliteral-caller': 18, 'all-callers-literal': 7}`

## T-229-02 门禁本体

- [x] 新增 `scripts/check_dispatch_entry_guard.py`
- 验收：
  ```
  C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_dispatch_entry_guard.py; echo EXIT=$?
  ```
  期望：`分发口 37 · 已表态 37 · 违规 0 · 可见 1219 · 不可见 91 · [PASS] · exit 0`

## T-229-03 ★ 先证能红（改动前的红基线）

- [x] 门禁写完、**声明未插**时先跑一次
- 验收（历史读数，已由 S3 消费）：
  ```
  [FAIL] 违规 37 处：[undeclared] … `def` 正上方缺 `#: dispatch-guard: <code> …`
  分发口 37 · 已表态 0 · 违规 37 · [FAIL] · exit 1
  ```
- [x] 合成树端到端负例（**可重复执行**）：
  ```
  C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tests/test_dispatch_entry_guard.py -v 2>&1 | grep -c "ok$"
  ```
  期望：`20`（含 `test_undeclared_dispatch_entry_is_red`）

## T-229-04 逐张表态（37 条，纯插入零删除）

- [x] `output/_add_229_declarations.py` 跑一次；复跑必须 `插入 = 0`（幂等）
- 验收：
  ```
  C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -W ignore output/_add_229_declarations.py 2>&1 | tail -2
  ```
  期望：`分发口 = 37` · `插入 = 0`
- 验收（分布）：
  ```
  grep -rn "#: dispatch-guard:" scripts/*.py | sed 's/.*dispatch-guard: //' | sort | uniq -c | sort -rn
  ```
  期望：`12 exempt generated-api` · `20 exempt internal-helper` · `2 exempt module-local` · `2 covered-wrappers` · `1 covered check_assembly_doc_call_shape.py`（合计 **37**）

## T-229-05 接线（硬门禁）

- [x] `scripts/release_check.py`：`_run_dispatch_entry_guard_gate()` + 调用点 + `raise` + `_gate_results`
- 验收：
  ```
  C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/release_check.py | tail -3; echo EXIT=$?
  ```
  期望：`"missing": []` · `exit 0`

## T-229-06 门禁分类登记

- [x] `docs/gate-classification.json` 新增 1 条（`kind: hard`），**40 → 41**，diff **+6 行**
- 验收：
  ```
  C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_gate_wiring.py | tail -6
  ```
  期望：无 `kind_bad` / 无 `unwired_unexempted`

## T-229-07 回归

- [x] 224 / 225 / 226 / 227 / 228 判据全绿
- 验收：
  ```
  for t in test_enum_table_disposition test_gate_blind_spot_claim test_gate_prose_provenance_claim test_arity_tables_vs_reflection test_assembly_doc_call_shape; do \
    printf "%-44s " $t; C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tests/$t.py 2>&1 | tail -1; done
  ```

## T-229-08 每轮收尾链

- [x] `pwsh -File D:\AI\SW\tools\round_chain.ps1 -Tests tests/test_dispatch_entry_guard.py`
- 期望：`release_check: 第 1 轮 OK` · `20 passed`
