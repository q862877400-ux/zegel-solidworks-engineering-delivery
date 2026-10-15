# tasks 241 · 任务与**可复制执行**的验收命令

> 全部命令在仓库根 `D:\AI\SW` 下执行。
> 受管解释器（纯静态判据）：`C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B`
> **pytest 风格判据**与**门禁全套**（★ 必须）：`C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe`

## T-001 先量：靶子表成员的调用形态（★ 改任何东西之前）

```
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B output/_probe241_focused.py
```
- [x] 读数：靶子表（改前）**3** 条；字面量形态 **1** 处 · **点式形态 2 处**（★ 后者**全在盲区里**）。
- [x] 全仓点式调用 **362** 个成员名 / **2923** 个调用点 ⇒ ★ 只能按靶子表筛。

## T-002 先写判据 → 跑 → ★ **确认能红**（改实现之前）

```
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B -m pytest tests/test_deprecated_entry_interlock.py -q
```
- [x] **红基线读数**：`2 failed, 4 passed`
      —— `test_registration_table_has_no_dead_entries`（登记了 `AddMate5` 而靶子表里没有 ⇒ 死条目）
      —— `test_dotted_call_form_is_not_a_blind_spot`（`assert "AddMate5" in obsolete` 失败）。

## T-003 实现：`scripts/sw_com_traps.py` 加 1 条（**只登记、不改路由**）

```
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -c "import sys;sys.path.insert(0,'scripts');import sw_com_traps as T;print(T.DEPRECATED_ENTRIES);print(T.deprecated_successor('AddMate5'))"
```
- [x] 读数：`{…, ('IAssemblyDoc','AddMate5'): 'CreateMate'}` · `successor('AddMate5') = CreateMate` ·
      `successor('Nope') = None`（★ 不认识就回 `None`，**不猜** —— 铁律 5）。

## T-004 判据转绿 + 变异检验（★ 证明扫描面改动是 **load-bearing**）

```
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B -m pytest tests/test_deprecated_entry_interlock.py tests/test_save_routing_interlock.py tests/test_tool_specs_batch80.py -q
```
- [x] 读数：`18 passed`（互锁 6 + 试点 5 + batch80 7）。
- [x] **变异检验**（旧口径 vs 新口径，同一棵树）：
      ```
      sw_assembly.py         旧=[]                新=[(415, 'AddMate5')]
      sw_assembly_doc.py     旧=[(364,'AddMate5')] 新=[(364, 'AddMate5')]
      sw_connect.py          旧=[]                新=[(1167, 'SaveAs')]
      ```
      ⇒ ★ 旧口径在两处读成 **0**、新口径读出 **1** ⇒ **不是装饰**。

## T-005 生成器链（★ 改了 `scripts/` 必须重跑）

```
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/sync_bundled_skill.py
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/gen_level_audit.py
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B tools/gen_metrics.py
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B tools/gen_harvest_digest.py
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B tools/build_union_map.py
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B tools/gen_dead_ends.py
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/sync_bundled_skill.py
```
- [x] 读数：打包副本 `files 471 · pruned []` · level `verified 117 / stitched 20 / not_implemented 3` ·
      harvest `能力 140 条 · 门禁 44 道`。

## T-006 门禁全套（★ 必须 3.14.7）

```
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/release_check.py
```
- [x] 读数：`EXIT 0` · `"status": "pass"` · `"missing": []` · `gate_wiring` 报 **44 个**门禁
      （★ **未新增门禁文件** ⇒ `release_check` 与 `gate-classification.json` **两个数都不变**）。

## T-007 规格四件 + 游标 + memory + 交接单

- [x] `specs/241-deprecated-entry-interlock-coverage/{spec,plan,tasks,acceptance}.md`
- [x] `.specify/feature.json` → `specs/241-deprecated-entry-interlock-coverage`
- [x] `docs/ROADMAP.md` §一 游标追加
- [x] `docs/known-facts.md` 事实 272 同步（★ 两族 → 三族 · 4 个 test → **6 个 test** · 4 passed → **6 passed**）
- [x] `.workbuddy-ai/memory/2026-10-09.md`（append）
- [x] `output/AUTO_RUN_2026-10-09-1618.md` · `output/AUTO_HANDOFF.md`（覆盖写）
- [x] ★ 复跑门禁（**改了 `known-facts.md` 之后**）：`EXIT 0` · `status pass` · `missing []` ·
      `refuted` 仍 PASS（10 条 `anchor_quote` 逐字命中）· `fact_single_home` 仍只有**既有** 2 处 WARN。
