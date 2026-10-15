# tasks 243 · 准入口径的收口

> ★ 每条都带**可复制执行**的验收命令。★ 顺序即依赖顺序。

## T1 先量（★ 做任何改动之前）
```bash
cd /d/AI/SW
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B output/_probe243_admission.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B output/_probe243_verify.py
```
- [x] 分桶：真树在调 **82** 个废弃名 ⇒ `successor-same-name 34 · terminal-never-called 23 · admissible 15 · ambiguous-terminal 9 · chain-broken-all 1`
- [x] ★ 第一版探针**自造了一条"终点接口必须同源"的过滤器** ⇒ 不是规格口径 ⇒ **已删重跑**（读数从 49 → 15 再定桶）
- [x] 索引多后继条目 = **254 / 1671**；真案例 `IModelDoc2::SketchTrim` ⇒ 索引只记 `SketchExtend`（★ **错后继**）
- [x] 现表 4 条**预先核过**：官方那句都是**单链接**、后继页首行都不是 `Obsolete.` ⇒ 新关不会假红

## T2 先写判据（★ 实现之前必须红一次）
```bash
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_deprecated_table_admission.py -q
```
- [x] 红基线：`3 failed, 9 passed`（缺关 4/关 5/关 6；且 `_admission_failures` 还是三参）

## T3 实现（★ 只改 `tests/test_deprecated_table_admission.py`）
```bash
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_deprecated_table_admission.py -q
```
- [x] `_admission_failures(table, imap, called, entries)` + 关 4/5/6
- [x] 新增 `_successor_links` / `_successor_page` / `_page_first_body_line` / `SWAPI_TYPES`
- [x] 4 处旧调用点改四参
- [x] `12 passed`

## T4 互锁族回归
```bash
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_deprecated_table_admission.py tests/test_deprecated_entry_interlock.py tests/test_save_routing_interlock.py tests/test_tool_specs_batch80.py -q
```
- [x] `30 passed`

## T5 文档同步
```bash
cd /d/AI/SW && grep -n "spec 243" docs/known-facts.md
```
- [x] 事实 272 补 spec 243 的三关 + 分桶读数 + `8 → 12 个 test`

## T6 门禁全套（★ 必须 3.14.7；★ 未改 `scripts/` 与 `mcp-server/` ⇒ **生成器链不必跑**）
```bash
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/release_check.py
```
- [x] `EXIT 0` · `status pass` · `missing []` · `gate_wiring` **44** · `classification` **48**（两个都不变）

## T7 收尾
- [x] `docs/ROADMAP.md` §一 游标 + `.specify/feature.json` + `.workbuddy-ai/memory/2026-10-09.md` + `output/AUTO_HANDOFF.md` + `output/AUTO_RUN_*.md`
