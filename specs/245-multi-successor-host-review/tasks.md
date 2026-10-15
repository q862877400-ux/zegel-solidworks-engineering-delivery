---
description: "Task list for feature implementation"
---

# Tasks: 多后继「命中名」的宿主级复核

**Feature**: `specs/245-multi-successor-host-review/`
**Prerequisites**: plan.md, spec.md

**Tests**: 本特性**就是**判据（spec FR-001 ~ FR-006），测试为必需。

**解释器**：`PY = "C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"`（探针用受管 3.13.12）。
★ **pytest 风格判据必须用 3.14.7**：`PY314 = "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe"`。
★ 门禁全套 `release_check.py` 也必须用 **3.14.7**。

---

## Phase 1: 先量（★ 未量完不许写判据）

- [x] T001 导出 14 个命中名的**调用点 + 宿主表达式**
      → 验收: `"$PY" -B output/_probe245_hosts.py` ⇒ `命中名数 : 14   调用点数 : 65`
- [x] T002 量「同名页在**别的接口**下是否非废弃」（机械信号）
      → 验收: `"$PY" -B output/_probe245_pages.py` ⇒ **11** 个名有非废弃同名页（`SketchTrim`/`GetArcs2`/…），3 个无
- [x] T003 逐条读宿主表达式判接口（人工），定 14 条 code
      → 验收: 见 `acceptance.md` §二 的表 ⇒ **real-hit 6 · mixed 1 · false-hit 7**

---

## Phase 2: 判据（先绿后验红）

- [x] T004 新建 `tests/test_obsolete_multi_successor_impact.py`（**7 例**）
      → 验收: `"$PY314" -B -m pytest tests/test_obsolete_multi_successor_impact.py -q` ⇒ `7 passed`
- [x] T005 ★★ **证明判据能红**（变异检验 5 组）
      → 验收: `"$PY314" -B output/_probe245_redbaseline.py` ⇒ 每行末尾都是 `✓`
- [x] T006 ★ 变异检验**当场抓到一处空判据**并修掉
      → 验收: 判据 ④ 补「检查量下界」后，「清空登记表」这一组从 `✗` 变 `✓`（见 `acceptance.md` §三）

---

## Phase 3: 收口

- [x] T007 四件齐（spec / plan / tasks / acceptance）
      → 验收: `ls specs/245-multi-successor-host-review/` ⇒ 4 个 `.md`
- [x] T008 ★ 确认生成器与靶子表**一行未改**（FR-007）
      → 验收: `git status --short tools/build_obsolete_index.py scripts/sw_com_traps.py` ⇒ 无输出
- [x] T009 门禁全套 @3.14.7
      → 验收: `"$PY314" -B scripts/release_check.py` ⇒ `exit 0`
- [x] T010 事实 272 补 spec 245 段（★ 交接单「不要做」之外的**必做**：文档里的正文不会自己报错）
      → 验收: `grep -c "spec 245" docs/known-facts.md` ⇒ `≥1`
- [x] T011 状态四处回写（ROADMAP §一 游标 / `feature.json` / `memory/<日期>.md` / `output/AUTO_HANDOFF.md`）
      → 验收: 四处都能 grep 到 `245`
- [x] T012 ★ **关闭交接单待办 1**（FR-005 给出关闭依据：真树上零靶子）
      → 验收: `output/AUTO_HANDOFF.md` ② 段里待办 1 标注「**已关闭**」并给出读数

---

## 完成判据

**全部为「命令跑绿」**，不是「我检查过了」。
★ 本特性的**核心证据是 T005 + T006**：判据**能红**（5 组变异全红），且变异检验**当场抓出并修掉一处空判据**。
不能红的判据等于空判据。
