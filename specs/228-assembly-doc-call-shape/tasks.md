# tasks 228 —— `call_assembly_doc` 调用形状门禁

> ★ 每条都带**可复制执行**的验收命令。解释器：
> - 判据 / 门禁：`C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B`
> - **门禁全套**：`C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe`
>   （受管 3.13.12 **缺 comtypes/win32com** ⇒ 会触发交互式 COM 提示 ⇒ **假红 + 挂死风险**）

## T-228-01 门禁本体

- [x] 新增 `scripts/check_assembly_doc_call_shape.py`
- 验收：
  ```
  C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_assembly_doc_call_shape.py; echo EXIT=$?
  ```
  期望：`已核 19 · 含 by-ref 0 · 未核 by-ref 0 · 违规 0 · [PASS] · exit 0`

## T-228-02 ★ 先证能红（合成树端到端负例）

- [x] 负例在**仓库外**的临时树上跑（`DSH_ASSEMBLY_CALL_ROOT` + `DSH_ARITY_DUMPS`）
- 验收（裸传 by-ref ⇒ 必须 exit 1）：
  ```
  T=$(mktemp -d); mkdir -p "$T/scripts" "$T/_raw/d"
  printf '## IAssemblyDoc\n    Int32 AddMate5(Int32, Int32, Boolean, Double, Double, Double, Double, Double, Double, Double, Double, Boolean, Boolean, Int32, Int32&)\n' > "$T/_raw/d/iface_f.txt"
  printf 'from __future__ import annotations\n\n#: enum-gate: not-enum arity\n#: arity-reflect: byref=included\nASSEMBLY_DOC_ARITY: dict[str, int] = {\n    %s: 15,\n}\n\n\ndef go(doc):\n    return call_assembly_doc(doc, %s, 1, 2, True, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, False, False, 0, 0)\n' "'AddMate5'" "'AddMate5'" > "$T/scripts/fixture.py"
  DSH_ASSEMBLY_CALL_ROOT="$T" DSH_ARITY_DUMPS="$T/_raw/d/iface_f.txt" \
    C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_assembly_doc_call_shape.py; echo EXIT=$?
  ```
  期望：`[bare-byref] … 第 14 位形参是 \`Int32&\`，实参却是 \`0\`` ⇒ `exit 1`

## T-228-03 判据（13 例）

- [x] 新增 `tests/test_assembly_doc_call_shape.py`
- 验收：
  ```
  C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tests/test_assembly_doc_call_shape.py 2>&1 | tail -3
  ```
  期望：`Ran 13 tests` · `OK`

## T-228-04 接线（硬门禁）

- [x] `scripts/release_check.py`：`_run_assembly_doc_call_shape_gate()` + 调用点 + `raise` + `_gate_results`
- 验收：
  ```
  C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/release_check.py | tail -3; echo EXIT=$?
  ```
  期望：`"missing": []` · `exit 0`

## T-228-05 门禁分类登记

- [x] `docs/gate-classification.json` 新增 1 条（`kind: hard`），**39 → 40**
- 验收：
  ```
  C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_gate_wiring.py | tail -6
  ```
  期望：无 `kind_bad` / 无 `unwired_unexempted`

## T-228-06 契约写进文档

- [x] `scripts/sw_assembly_doc.py::call_assembly_doc` 的 docstring 补 by-ref 契约（**逻辑零改动**）
- 验收：
  ```
  git diff --stat scripts/sw_assembly_doc.py
  ```
  期望：只有 docstring 行数变化（无 `def` / `raise` / `return` 语句改动）

## T-228-07 回归

- [x] 224 / 225 / 226 / 227 判据全绿
- 验收：
  ```
  for t in test_enum_table_disposition test_gate_blind_spot_claim test_gate_prose_provenance_claim test_arity_tables_vs_reflection; do \
    printf "%-42s " $t; C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tests/$t.py 2>&1 | tail -1; done
  ```

## T-228-08 每轮收尾链

- [x] `pwsh -File D:\AI\SW\tools\round_chain.ps1 -Tests tests/test_assembly_doc_call_shape.py`
- 期望：`release_check: 第 1 轮 OK` · `13 passed`
