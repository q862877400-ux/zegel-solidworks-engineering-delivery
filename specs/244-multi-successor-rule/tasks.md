---
description: "Task list for feature implementation"
---

# Tasks: 多后继条目的后继选取规则

**Feature**: `specs/244-multi-successor-rule/`
**Prerequisites**: plan.md, spec.md

**Tests**: 本特性**就是**判据（spec FR-002 ~ FR-004），测试为必需。

**解释器**：`PY = "C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"`（判据用受管 3.13.12）。
★ 门禁全套 `release_check.py` 必须用 **3.14.7**：`C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe`。

---

## Phase 1: 先量（★ 未量完不许写判据）

- [x] T001 量「真树在调的成员名 ∩ 索引全部条目」与「∩ 254 条多后继条目」
      → 验收: `"$PY" -B output/_probe244_multi_successor.py` ⇒ `真树被调名 ∩ 索引全部条目(按名) : 82` · `按名命中多后继条目 : 14`
- [x] T002 导出 14 条命中名的官方原句（判形态）
      → 验收: `"$PY" -B output/_probe244_dump.py > output/_probe244_dump.txt` ⇒ 152 行、14 个名
- [x] T003 量「同名链接优先」规则在 254 条上的分桶
      → 验收: `"$PY" -B output/_probe244_rule.py` ⇒ `无同名链接 243` · `有同名-索引取对了 5` · **`有同名-索引取错了 6`**

---

## Phase 2: 判据（先红后绿）

- [x] T004 新建 `tests/test_obsolete_multi_successor.py`（4 例：张数下界 / 同名规则 / 登记表与索引一致 / 登记项须有依据）
      → 验收: `"$PY" -B tests/test_obsolete_multi_successor.py`（★ 本机无 pytest，用内置 runner 或 `-c` 直调）
- [x] T005 ★★ **证明判据能红**：清空 `_KNOWN_WRONG` 后跑同名规则 ⇒ 必须报**正好 6 条**
      → 验收: 见 `acceptance.md` §一 的命令与读数（`RED BASELINE 复现 ✓`）
- [x] T006 登记 6 条已知偏差（每条带**真后继全名 + 依据**）
      → 验收: `test_registry_entries_have_evidence` 通过

---

## Phase 3: 收口

- [x] T007 四件齐（spec / plan / tasks / acceptance）
      → 验收: `ls specs/244-multi-successor-rule/` ⇒ 4 个 `.md`
- [x] T008 ★ 确认生成器**一行未改**（FR-005）
      → 验收: `git status --short tools/build_obsolete_index.py` ⇒ 无输出
- [x] T009 门禁全套 @3.14.7
      → 验收: `"C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B scripts/release_check.py` ⇒ `exit 0`
- [x] T010 状态四处回写（ROADMAP §一 游标 / `feature.json` / `memory/<日期>.md` / `output/AUTO_HANDOFF.md`）
      → 验收: 四处都能 grep 到 `244`

---

## 完成判据

**全部为「命令跑绿」**，不是「我检查过了」。
★ 本特性的**核心证据是 T005**：判据**能红**（清空登记表 ⇒ 正好 6 条失败）。不能红的判据等于空判据。
