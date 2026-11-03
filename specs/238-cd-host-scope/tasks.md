# tasks 238 · 任务与**可复制执行**的验收命令

> 解释器：判据一律 `C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B`；
> ★ 门禁全套 `scripts/release_check.py` **必须**用 `C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe`。

- [x] **T1** 加读取器 `host_pages()` / `host_consts()`（`check_interface_member_ownership.py`）
  ```
  python -B -c "import sys;sys.path.insert(0,'scripts');import check_interface_member_ownership as c;print(len(c.host_pages()), len(c.host_consts()))"
  ```
  读数：`11 46`（点名 11 条 · 收录常量 46 个）
- [x] **T2** 新门禁 `scripts/check_cd_host_scope.py`（`judge_sites()` 判罪集中一处）
  ```
  python -B scripts/check_cd_host_scope.py
  ```
  ★ **红基线（改 `build_map` 之前）**：`[should-map] sw_motion.py:212` + `[baseline-shrunk] named 0 < 下界 1` + `[zero-checked]` · `exit 1`
  改后读数：`站点 10 · 点名 1 · 违规 0 · [PASS] · exit 0`
- [x] **T3** `build_map()` 加官方宿主页点名播种 ⇒ 诊断读数 `检查过 5 → 6` 站点、`unmapped 3 → 2`、映射表 `35 → 45`、官方点名 `5 → 15`
  ```
  python -B scripts/check_interface_member_ownership.py
  ```
- [x] **T4** 237 下界同步 + 删 `sw_motion.py` 多余声明
  ```
  python -B scripts/check_create_definition_site_disposition.py
  ```
  读数：`站点 10 · checked 6 · unmapped 2 · empty-members 0 · no-members-used 2 · dynamic 0 · 违规 0 · [PASS] · exit 0`
- [x] **T5** 判据 10 例（含 `host-mismatch` / `ambiguous-host` 的**直接靶子**、`[SKIP]` gap、源隔离、下界缩小）
  ```
  python -B -m unittest tests.test_cd_host_scope -v
  ```
  读数：`Ran 10 tests · OK`
- [x] **T6** 237 判据回归（真树读数断言已同步）
  ```
  python -B -m unittest tests.test_cd_site_disposition
  ```
  读数：`Ran 15 tests · OK`
- [x] **T7** 接线 `release_check.py`（`_run_cd_host_scope_gate` + `raise` + `_gate_results`）+ `docs/gate-classification.json` 47 → 48
  ```
  C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/release_check.py
  ```
  读数：`EXIT 0 · status pass · gates 47 · cd_host_scope: pass`
- [x] **T8** 收尾链（生成器 → `release_check` → 聚焦测试）
  ```
  pwsh -File D:\AI\SW\tools\round_chain.ps1 -Tests tests/test_cd_host_scope.py
  ```
- [x] **T9** 打包副本同步（`scripts/release_check.py`，发版前才必须，本轮随收尾链跑）
