# tasks 242 · 靶子表扩容的准入

> ★ 每条都带**可复制执行**的验收命令。★ 顺序即依赖顺序。

## T1 先量（★ 做任何改动之前）
```bash
cd /d/AI/SW
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B output/_probe242_buckets.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B output/_probe242_calls.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B output/_probe242_ambiguity.py
```
- [x] 分桶：1671 条 → A 后继为空 **85** · B 后继名==自己 **88** · 真树在调 **82** 个名
- [x] 歧义：字面后继口径 **115** · **链终点口径 79**（真树在调的名里 **11** 个）

## T2 先写判据（★ 实现之前必须红一次）
```bash
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_deprecated_table_admission.py -q
```
- [x] 红基线：`7 failed, 1 passed`（缺 `ambiguous_deprecated_members`）

## T3 实现（`scripts/sw_com_traps.py`）
```bash
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_deprecated_table_admission.py -q
```
- [x] `8 passed`

## T4 变异检验（★ 证明判据能红）
```bash
cd /d/AI/SW && git show HEAD:scripts/sw_com_traps.py > output/_probe242_head_traps.py && \
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B output/_probe242_head_traps.py
```
- [x] 旧实现（HEAD）在合成歧义表上 `deprecated_successor('Select2') = 'Select3'` ⇒ ★ **猜了** ⇒ 判据能红 ✓

## T5 MCP 工具补形参
```bash
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/release_check.py 2>&1 | grep -A2 '"param_binding"'
```
- [x] `param_binding: pass`（479 个工具）

## T6 聚焦回归
```bash
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_deprecated_table_admission.py tests/test_deprecated_entry_interlock.py tests/test_save_routing_interlock.py tests/test_tool_specs_batch80.py -q
```
- [x] `26 passed`

## T7 生成器链（★ 改了 `scripts/` 与 `mcp-server/` 必须跑）
```bash
cd /d/AI/SW && PY=C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe && \
$PY -B scripts/release_check.py && $PY -B scripts/gen_level_audit.py && $PY -B tools/gen_metrics.py && \
$PY -B tools/gen_harvest_digest.py && $PY -B tools/build_union_map.py && $PY -B tools/gen_dead_ends.py && \
$PY -B scripts/release_check.py
```
- [x] 打包副本 `files 471 · pruned []`

## T8 门禁全套（★ 必须 3.14.7）
```bash
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/release_check.py
```
- [x] `EXIT 0` · `status pass` · `missing []` · `gate_wiring` **44** · `classification` **48**（两个都不变）

## T9 收尾
- [x] `docs/known-facts.md` 事实 272 补 spec 242 的两件 + 歧义读数
- [x] `docs/ROADMAP.md` §一 游标 + `.specify/feature.json` + `.workbuddy-ai/memory/2026-10-09.md` + `output/AUTO_HANDOFF.md` + `output/AUTO_RUN_*.md`
