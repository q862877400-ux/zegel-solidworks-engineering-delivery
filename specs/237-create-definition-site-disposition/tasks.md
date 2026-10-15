# tasks 237 · `CreateDefinition` 站点处置门禁

> ★ 每条都带**可复制执行**的验收命令。★ **改实现前判据必须先红一次。**

| # | 任务 | 验收命令 | 状态 |
|---|---|---|---|
| T1 | 写四件（spec / plan / tasks / acceptance） | `ls specs/237-create-definition-site-disposition/` | ✅ |
| T2 | ★ **先写判据** `tests/test_cd_site_disposition.py`，跑 ⇒ **必红**（门禁文件不存在） | `C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -m unittest tests.test_cd_site_disposition` | ✅ 红 |
| T3 | `check_interface_member_ownership.py` 抽 `scan_sites()` + `SITE_CODES`，`main()` 消费它 | `C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_interface_member_ownership.py` | ✅ exit 0 |
| T4 | ★ **FR-006 能红判据**：`test_module_consts_reads_trailing_comment` 先跑 ⇒ **红** | `... -B -m unittest tests.test_cd_site_disposition.CdSiteDispositionTest.test_module_consts_reads_trailing_comment` | ✅ 红 → 绿 |
| T5 | 宽化 `module_consts` 正则（容忍行尾注释） | 同上（⇒ 绿）；`... -B scripts/check_interface_member_ownership.py` 仍 exit 0 | ✅ |
| T6 | 实现门禁 `scripts/check_create_definition_site_disposition.py` | `... -B scripts/check_create_definition_site_disposition.py` | ✅ |
| T7 | ★ **红基线**：补声明**之前**跑门禁 ⇒ `[undeclared] ×5 · exit 1` | 同上（记录读数） | ✅ exit 1 |
| T8 | 5 行声明**纯插入零删除**（4 个 `scripts/sw_*.py`） | `grep -rn "^#: cd-site:" scripts/` 得 5 行；`git diff --numstat` 该 4 文件 `+5 -0` | ✅ |
| T9 | 判据全绿 + 门禁本体 `[PASS] · exit 0` | `... -B -m unittest tests.test_cd_site_disposition -v` · `... -B scripts/check_create_definition_site_disposition.py` | ✅ |
| T10 | ★ **变异检验**：短路 `judge()` ⇒ 非零 `failures` | 临时改 → 跑 → 还原（`md5sum` 复核） | ✅ |
| T11 | 接线 `release_check.py`（函数 + 调用 + `raise` + `_gate_results`） | `C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/release_check.py` | ✅ |
| T12 | `docs/gate-classification.json` 登记（46 → 47） | 同上（`classification` 字段 +1） | ✅ |
| T13 | 收尾链 | `pwsh -File D:\AI\SW\tools\round_chain.ps1 -Tests tests/test_cd_site_disposition.py` | ✅ |
| T14 | 229–237 合并回归 | `... -B -m unittest`（逐文件，见 acceptance） | ✅ |
| T15 | 更新 ROADMAP §一 + `memory/2026-10-09.md` + 交接单 + `AUTO_RUN` 报告 | 四份文件互相一致 | ✅ |
