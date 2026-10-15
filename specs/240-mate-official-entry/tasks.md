# tasks 240 · 任务与**可复制执行**的验收命令

> 全部命令在仓库根 `D:\AI\SW` 下执行。
> 受管解释器（判据）：`C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B`
> 门禁全套（★ 必须）：`C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe`

## T-001 先量：站点与调用方

```
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -c "import sys,pathlib;sys.path.insert(0,'scripts');import check_interface_member_ownership as c;print([(s['path'].name,s['line'],s['const']) for s in c.scan_sites(sorted(pathlib.Path('scripts').glob('*.py')))])"
```
- [x] 读数：站点 **9**，`sw_weldment.py` 的 `swFmMateProfileCenter` 只 **1** 个；
      `_create_from_definition` 调用方 **只有** `create_profile_center_mate`
      ⇒ ★ 交接单「还有别的调用方」的前提**被推翻**（第九次）。

## T-002 先写判据并确认**能红**（改实现之前）

```
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tests/test_mate_official_entry.py
```
- [x] 红基线读数：`Ran 10 tests … FAILED (failures=3, errors=3)`
      （③ `_create_from_definition` 仍在 · ② 直接调共用骨架 · ⑥⑦⑩ `SW_MATE_PROFILE_CENTER` 不存在）。

## T-003 实现：`scripts/sw_weldment.py` 改走官方入口

```
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -c "import sys;sys.path.insert(0,'scripts');import ast,pathlib;t=ast.parse(pathlib.Path('scripts/sw_weldment.py').read_text(encoding='utf-8'));print([n.name for n in t.body if isinstance(n,ast.FunctionDef) and n.name in ('_create_from_definition','create_profile_center_mate')])"
```
- [x] 读数：`['create_profile_center_mate']` —— 骨架已删（**只剩墓碑注释**）。
- [x] 判据复跑：`Ran 10 tests … OK`。

## T-004 连带改动：两条棘轮 + 两份测试 + 一份契约测试 + 工具 doc

```
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_create_definition_site_disposition.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_cd_host_scope.py
```
- [x] 读数：`站点 8 · checked 6 · unmapped 0 · empty-members 0 · no-members-used 2 · dynamic 0 · 违规 0 · [PASS] · exit 0`
- [x] 读数：`站点 8 · 点名 1 · 无宿主 0 · 违规 0 · [PASS] · exit 0`
- [x] ★ **改下界之前**两条门禁的**红基线**（这就是「能红的判据」）：
      `[baseline-shrunk] sites 8 < 下界 9` + `unmapped 0 < 下界 1`（另一条同形，`no-host 0 < 1`）。

## T-005 聚焦判据

```
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tests/test_cd_host_scope.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tests/test_cd_site_disposition.py
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B -m pytest tests/test_extended_modules_contract.py tests/test_mate_official_entry.py -q
```
- [x] `test_cd_host_scope` 16/16 OK · `test_cd_site_disposition` 15/15 OK
- [x] `pytest … -q` → `25 passed`
      （★ `test_extended_modules_contract.py` 是 pytest 风格 ⇒ 必须用 3.14.7 跑；
      3.13.12 下 `_main()` 里 `test_add_relation_passes_two_arguments` 因缺 `pythoncom` 失败 —— **既有**，非本切片引入）

## T-006 生成器 + 门禁全套

```
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/sync_bundled_skill.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/gen_level_audit.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tools/gen_metrics.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tools/gen_harvest_digest.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tools/build_union_map.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tools/gen_dead_ends.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/sync_bundled_skill.py
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/release_check.py
```
- [x] 生成器全部 `exit 0`；打包副本 `files 471 · pruned []`
- [x] 门禁全套读数见 `acceptance.md` §三。

## T-007 收尾文档

- [x] `specs/240-mate-official-entry/{spec,plan,tasks,acceptance}.md` 四件齐
- [x] `docs/ROADMAP.md` §一 游标追加 240 段 + 「下一 WIP」
- [x] `.workbuddy-ai/memory/2026-10-09.md`（append）
- [x] `output/AUTO_HANDOFF.md`（覆盖写）
- [x] `output/AUTO_RUN_2026-10-09-<时间>.md`
