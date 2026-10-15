# tasks 239 · 任务与**可复制执行**的验收命令

> 解释器：判据一律 `C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B`；
> ★ 门禁全套 `scripts/release_check.py` **必须**用 `C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe`。

- [x] **T1** 加第四码 `unsupported-path`（`scripts/check_cd_host_scope.py`）+ `declaration_block()` +
  `judge_unsupported()`（纯函数）+ `make_unsupported_judge()` + `no-host` 下界
  ```
  python -B scripts/check_cd_host_scope.py
  ```
  ★ **红基线（加码后、改实现前）**：`[unsupported-path] sw_sheet_metal.py:396` ·
  `[unsupported-path] sw_weldment.py:687` · `站点 10 · 点名 1 · 无宿主 2 · 违规 2 · [FAIL] · exit 1`
- [x] **T2** `create_draft` 改走官方入口 `IFeatureManager::InsertMultiFaceDraft`（6 参，度→弧度）
  ```
  python -B -m unittest tests.test_draft_official_entry -v
  ```
  ★ **红基线（跑在 `git HEAD` 的实现上）**：5 条判据**全红** —— ①仍走 `_create_from_definition` ·
  ②无 `InsertMultiFaceDraft` · ③无 `radians` · ④仍用 `SW_FM_DRAFT` · ⑤状态表是 `False`
- [x] **T3** `DraftFeatureSpec` 扩到官方 6 参对应面 + `prop_type` 越界前置拒绝
  ```
  python -B -m unittest tests.test_draft_official_entry.DraftOfficialEntryTest.test_prop_type_out_of_official_range_is_rejected_before_com
  ```
- [x] **T4** `sw_weldment` 补 `alt CreateMateData` 声明（官方替代入口，两页均无 `Obsolete`）
  ```
  python -B scripts/check_cd_host_scope.py
  ```
  改后读数：`站点 9 · 点名 1 · 无宿主 1 · 违规 0 · [PASS] · exit 0`
- [x] **T5** 237 棘轮同步（`BASELINE_SITES 10 → 9` · `BASELINE_UNMAPPED 2 → 1`）+ 删 `sw_sheet_metal` 的
  多余 `cd-site` 声明（该站点已不存在）
  ```
  python -B scripts/check_create_definition_site_disposition.py
  ```
  读数：`站点 9 · checked 6 · unmapped 1 · empty-members 0 · no-members-used 2 · dynamic 0 · 违规 0 · [PASS] · exit 0`
- [x] **T6** 238 棘轮同步（`BASELINE_SITES 10 → 9`）+ `DSH_CD_HOST_BASELINE_MIN` 变 **3 个数**
  ```
  python -B -m unittest tests.test_cd_host_scope tests.test_cd_site_disposition
  ```
  读数：`Ran 16 tests · OK` + `Ran 15 tests · OK`
- [x] **T7** 状态表 `create_draft → (None, …)` + 工具层 doc 同步（旧措辞标「已作废」）
  ```
  python -B -m pytest tests/test_tool_specs_batch4.py tests/test_sheet_metal_doc_freshness.py -q
  ```
  读数：`13 passed, 2 skipped`
- [x] **T8** 门禁全套（★ 生成器先跑，见 `plan.md` §一）
  ```
  C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/release_check.py
  ```
- [ ] **T9（下一轮）** `sw_weldment.create_profile_center_mate` 改走
  `IAssemblyDoc::CreateMateData(swMatePROFILECENTER=24)` + `CreateMate` —— **须先立项 `specs/240-*`**，
  先写能红的判据（当前只有 `alt` 声明，代码**未改**）
- [ ] **T10（需业主授权 COM）** `create_draft` 真机验证：改走官方入口后能否真的建出拔模特征
