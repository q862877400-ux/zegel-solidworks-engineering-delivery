---
description: "Task list for feature implementation"
---

# Tasks: `admissible` 候选的收表处置

**Feature**: `specs/246-admissible-candidates/`
**Prerequisites**: plan.md, spec.md

**Tests**: 本特性**就是**判据（spec FR-001 ~ FR-008），测试为必需。

**解释器**：`PY = "C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"`（探针用受管 3.13.12）。
★ **pytest 风格判据与 `release_check` 必须用 3.14.7**：`PY314 = "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe"`。

---

## Phase 1: 先量（★ 未量完不许写判据）

- [x] T001 复算 15 个 `admissible` 候选 + 逐条过**六关** + 导出**宿主级调用点**
      → 验收: `"$PY314" -B output/_probe246_candidates.py` ⇒ `admissible 15` · 六关失败 `{multiple-official-successors: 4, successor-page-missing: 1}`
- [x] T002 对「六关全过」的候选读**两边签名**（被废弃页 vs 后继页）
      → 验收: `"$PY" -B output/_probe246_signatures.py` ⇒ 8 组签名逐条列出（★ 页首行 + Signature）

---

## Phase 2: 判据（先绿后验红）

- [x] T003 新建 `tests/test_deprecated_admissible_disposition.py`（**8 例**）
      → 验收: `"$PY314" -B -m pytest tests/test_deprecated_admissible_disposition.py -q` ⇒ `8 passed`
- [x] T004 ★★ **证明判据能红**（变异检验 8 组）
      → 验收: `"$PY314" -B output/_probe246_redbaseline.py` ⇒ 每行末尾都是 `✓`
- [x] T005 ★ 变异检验**当场抓出一处 KeyError（不是可读的失败）**并修掉
      → 验收: 判据③ 补「`collected` 必须在 `_COLLECTED_SUCCESSOR` 里」的断言 + 判据④ 补**反向一致性** ⇒ 变异 1 的期望改为 RED 后 ✓

---

## Phase 3: 收表（★ 两处连带 + 生成器链）

- [x] T006 `scripts/sw_com_traps.py` 的 `DEPRECATED_ENTRIES` **+5 条**（4 → 9）
      → 验收: `"$PY314" -B -c "import sys;sys.path.insert(0,'scripts');import sw_com_traps as T;print(len(T.DEPRECATED_ENTRIES))"` ⇒ `9`
- [x] T007 `tests/test_deprecated_entry_interlock.py` 的 `_REGISTERED` **+5 处**
      → 验收: `"$PY314" -B -m pytest tests/test_deprecated_entry_interlock.py -q` ⇒ 全绿
- [x] T008 ★ 同步 `tests/test_deprecated_table_admission.py` 的 **5 处「4 条」正文**（★ 纪律 5：文档里的现状不会自己报错）
      → 验收: `grep -c "4 条" tests/test_deprecated_table_admission.py` ⇒ `0`
- [x] T009 ★★ **跑生成器链**（★ 改了 `scripts/`）
      → 验收: `"$PY" -B scripts/sync_bundled_skill.py && … && "$PY" -B scripts/sync_bundled_skill.py` ⇒ 7 步全跑、`pruned: []`
- [x] T010 互锁族回归
      → 验收: `"$PY314" -B -m pytest tests/test_deprecated_admissible_disposition.py tests/test_deprecated_table_admission.py tests/test_deprecated_entry_interlock.py tests/test_save_routing_interlock.py tests/test_obsolete_multi_successor.py tests/test_obsolete_multi_successor_impact.py tests/test_tool_specs_batch80.py -q` ⇒ `49 passed`
- [x] T011 门禁全套 @3.14.7
      → 验收: `"$PY314" -B scripts/release_check.py` ⇒ `exit 0` · `missing []`

---

## Phase 4: 收口

- [x] T012 四件齐（spec / plan / tasks / acceptance）
      → 验收: `ls specs/246-admissible-candidates/` ⇒ 4 个 `.md`
- [x] T013 ★ 确认生成器**一行未改**（FR-009）
      → 验收: `git status --short tools/build_obsolete_index.py` ⇒ 无输出
- [x] T014 事实 272 补 spec 246 段
      → 验收: `grep -c "spec 246" docs/known-facts.md` ⇒ `≥1`
- [x] T015 状态四处回写（ROADMAP §一 游标 / `feature.json` / `memory/<日期>.md` / `output/AUTO_HANDOFF.md`）
      → 验收: 四处都能 grep 到 `246`

---

## 完成判据

**全部为「命令跑绿」**，不是「我检查过了」。
★ 本特性的**核心证据是 T004 + T005**：判据**能红**（8 组变异全红），且变异检验**当场抓出一处不可读的失败**（KeyError）并修掉。
