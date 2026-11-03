# 任务 227 · `*_ARITY` 表 × 出厂反射门禁

> 每条带**可复制执行**的验收命令。解释器：
> 判据 = 受管 3.13.12（`C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B`）；
> 门禁全套 = 3.14.7（`C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe`）。

- [x] **T1 · 红基线（先证能红）**
  ```bash
  cd D:/AI/SW && C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_arity_tables_vs_reflection.py
  ```
  实测（改动前）：`未表态 14 · 值不符 15 · [FAIL] · exit 1`。

- [x] **T2 · 实现门禁本体** `scripts/check_arity_tables_vs_reflection.py`
  ```bash
  cd D:/AI/SW && C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_arity_tables_vs_reflection.py
  ```
  实测（改动后）：`已表态 14 · 未表态 0 · 值不符 0 · [PASS] · exit 0`。

- [x] **T3 · 14 张表补约定声明**（`output/_apply_227_declarations.py`，按**表名**定位）
  ```bash
  cd D:/AI/SW && C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B output/_apply_227_declarations.py
  ```

- [x] **T4 · 订正真缺陷** `sw_view.VIEW_ARITY['ShowMagnifyingGlass']` 5 → 6
  ```bash
  cd D:/AI/SW && C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_sw_view_contract.py -q -p no:cacheprovider
  ```

- [x] **T5 · 新判据（14 例，含合成树端到端负例 + 承重性）**
  ```bash
  cd D:/AI/SW && C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tests/test_arity_tables_vs_reflection.py
  ```
  实测：`Ran 14 tests ... OK`。

- [x] **T6 · 接进 `release_check.py`**（函数 + `_gate_results` + `raise` 判据）
  ```bash
  cd D:/AI/SW && C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/release_check.py | tail -5
  ```
  实测：`EXIT=0` · `"status": "pass"` · `"missing": []` · 38 道门禁。

- [x] **T7 · 门禁分类登记** `docs/gate-classification.json`
  ```bash
  cd D:/AI/SW && C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B output/_fix_227_classification.py
  ```

- [x] **T8 · 同步打包副本 + 回归**
  ```bash
  cd D:/AI/SW && C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/release_check.py
  cd D:/AI/SW && C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_no_uncalled_helpers.py tests/test_uncalled_exempt_has_reason.py -q -p no:cacheprovider
  ```
  实测：打包 **462 文件 · pruned=[]**；未调用助手 **7 passed**（232 s）。

- [x] **T9 · 224/225/226 回归**
  ```bash
  cd D:/AI/SW && for t in test_enum_table_disposition test_gate_blind_spot_claim test_gate_prose_provenance_claim; do C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tests/$t.py; done
  ```
  实测：**8/8 · 11/11 · 9/9** 全绿。

- [x] **T10 · 收口状态载体**：`docs/ROADMAP.md` §一 · `.workbuddy-ai/memory/2026-10-09.md` ·
  `.workbuddy-ai/memory/MEMORY.md` · `output/AUTO_HANDOFF.md` · `output/AUTO_RUN_2026-10-09-0843.md`
  · `.specify/feature.json`。

## 未做（**明确不在本切片**）

- [ ] `ASSEMBLY_DOC_ARITY` 那 15 条**含 by-ref** 条目 × `call_assembly_doc` 的**潜伏陷阱**
      （按表调用会多要一个给不出的实参 ⇒ arity 校核**假拒**）—— ★ 需先定「by-ref 出参怎么占位」，
      未立项（见 `acceptance.md` §四）。
- [ ] `HEM_POSITIONS` 真机复核（**需业主另行授权 COM**）。
- [ ] 223 登记的 8 条 `HEAD` 即红既有失败（**先确认权属**）。
