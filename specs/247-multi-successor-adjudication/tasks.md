---
description: "Task list for feature implementation"
---

# Tasks: 多后继的机械化表态

**Feature**: `specs/247-multi-successor-adjudication/`
**Prerequisites**: plan.md, spec.md

**Tests**: 本特性**就是**判据（spec FR-001 ~ FR-007），测试为必需。

**解释器**：`PY = "C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"`（探针用受管 3.13.12）。
★ **pytest 风格判据与 `release_check` 必须用 3.14.7**：`PY314 = "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe"`。

---

## Phase 1: 先量（★ 未量完不许写判据）

- [x] T001 量 4 条多后继条目的官方原句 + 每个链接的页首行
      → 验收: `"$PY" -B output/_probe247_multi.py` ⇒ `多后继条目（关 5 靶子）= 254`，4 条逐条列出措辞
- [x] T002 量**全部 254 条**的措辞分布（★ 爆炸半径）
      → 验收: 见 `acceptance.md` §一.1 ⇒ `SUPERSEDED-BY 235 · SEE+REMARKS 14 · SEE(other) 5`
- [x] T003 量「真树在调的多链接条目」按措辞分桶
      → 验收: `acceptance.md` §一.2 ⇒ `18 条 = SUPERSEDED-BY 16 + SEE+REMARKS 2 + SEE(other) 0`

---

## Phase 2: 判据（先绿后验红）

- [x] T004 新增纯函数 `_official_successor_links` / `_official_successor_count`（三态）
      → 验收: `"$PY314" -B -m pytest tests/test_deprecated_multi_successor_adjudication.py -q -k "counts or undecidable or single"`
- [x] T005 关 5 改三态 + `_admission_failures` 增 `adjudicated` 参数 + `_MULTI_SUCCESSOR_ADJUDICATED` 表
      → 验收: `"$PY314" -B -m pytest tests/test_deprecated_table_admission.py -q` ⇒ 全绿
- [x] T006 新建 `tests/test_deprecated_multi_successor_adjudication.py`（**11 例**）
      → 验收: `"$PY314" -B -m pytest tests/test_deprecated_multi_successor_adjudication.py -q` ⇒ `11 passed`
- [x] T007 ★★ **证明判据能红**（变异检验 7 组）
      → 验收: `"$PY314" -B output/_probe247_redbaseline.py` ⇒ **24 处 `✓` · 0 处 `✗`**

---

## Phase 3: 收表（★ 两处连带 + 生成器链）

- [x] T008 `scripts/sw_com_traps.py` 的 `DEPRECATED_ENTRIES` **+2 条**（9 → 11）
      → 验收: `"$PY314" -B -c "import sys;sys.path.insert(0,'scripts');import sw_com_traps as T;print(len(T.DEPRECATED_ENTRIES))"` ⇒ `11`
- [x] T009 `tests/test_deprecated_entry_interlock.py` 的 `_REGISTERED` **+2 处**
      → 验收: `"$PY314" -B -m pytest tests/test_deprecated_entry_interlock.py -q` ⇒ 全绿
- [x] T010 ★ 同步 `tests/test_deprecated_table_admission.py` 的 5 处「9 条」正文 → 11
      → 验收: `grep -c "9 条" tests/test_deprecated_table_admission.py` ⇒ `0`
- [x] T011 ★★ **跑生成器链**（★ 改了 `scripts/`）
      → 验收: 7 步全 `ok`
- [x] T012 相关族回归
      → 验收: `"$PY314" -B -m pytest tests/test_deprecated_multi_successor_adjudication.py tests/test_deprecated_table_admission.py tests/test_deprecated_entry_interlock.py tests/test_save_routing_interlock.py tests/test_deprecated_admissible_disposition.py tests/test_obsolete_multi_successor.py tests/test_obsolete_multi_successor_impact.py tests/test_tool_specs_batch80.py -q` ⇒ `65 passed`
- [x] T013 门禁全套 @3.14.7
      → 验收: `"$PY314" -B scripts/release_check.py` ⇒ `exit 0` · `missing []`

---

## Phase 4: 收口

- [x] T014 四件齐（spec / plan / tasks / acceptance）
      → 验收: `ls specs/247-multi-successor-adjudication/` ⇒ 4 个 `.md`
- [x] T015 ★ 确认生成器**一行未改**（FR-008）
      → 验收: `git status --short tools/build_obsolete_index.py` ⇒ 无输出
- [x] T016 事实 272 补 spec 247 段
      → 验收: `grep -c "spec 247" docs/known-facts.md` ⇒ `≥1`
- [x] T017 状态四处回写（ROADMAP §一 游标 / `feature.json` / `memory/<日期>.md` / `output/AUTO_HANDOFF.md`）
      → 验收: 四处都能 grep 到 `247`

---

## 完成判据

**全部为「命令跑绿」**，不是「我检查过了」。
★ 本特性的**核心证据是 T007**：判据**能红**（7 组变异全红，★ 含「退回 243 旧语义 ⇒ 两条判据同时红」）。
