# Tasks — 工作区整理：把仓库根 2814 个草稿归入 `archive/`（只搬不删）

**Feature**: `specs/294-workspace-tidy/`
**日期**: 2026-10-10

---

## 一、任务清单

- [x] **T-294-01 先量**：数根文件 ⇒ **2843**；分桶（py 1773 · txt 883 · md 67 · log 41 · json 53 · bmp 6）。
  ★ 探针 `output/_scan_root_buckets.py`（★ **收工时已删** —— ★ 规则 13；★ **结论留** `output/_root_buckets.json`）。
- [x] **T-294-02 风险核查①（活代码 import）**：AST 扫全仓 ⇒ 根级模块被 import 的只有 **2 个**（`shot` / `ctl`）。
  ★ 探针 `output/_scan_root_imports.py` ⇒ `output/_root_imports.json`（★ 探针已删 · ★ **JSON 留**）。
- [x] **T-294-03 风险核查②（验收行）**：复刻 `check_spec_acceptance_paths` 判据③ ⇒ 扫 **865** 处验收行，点根脚本 **0** 处。
  ★ 探针 `output/_scan_acceptance_rootrefs.py`（★ **收工时已删** —— ★ 规则 13；★ 结论留 `output/_acceptance_rootrefs.json`）。
- [x] **T-294-04 风险核查③（门禁 glob 根）**：枚举 `check_*.py` 的 `ROOT.glob` ⇒ **2 处**，只有
  `check_report_criteria_alignment.py` 扫 `ROOT.glob("*.md")`（★ 实测搬走后仍绿）。
- [x] **T-294-05 风险核查④（打包器）**：读 `sync_bundled_skill.TOP_LEVEL_FILES` ⇒ **9** 个顶层文件必须留根。
- [x] **T-294-06 定白名单**：**29** 个文件（打包器 9 + 门面/许可/构建 18 + `shot.py`/`ctl.py`）。
- [x] **T-294-07 干跑**：`python output/_tidy_workspace.py` ⇒ 「留 29 / 搬 2814」。
  ★ 搬运脚本 `output/_tidy_workspace.py` **收工时已删**（★ 规则 13：一次性脚本放 `output/`、不进仓库代码）；
  ★★ **它的产物留**：`output/_tidy_result.json`（★ **归档清单** —— ★ 可按名找回任何被搬走的文件）✓
- [x] **T-294-08 真搬**：`--apply` ⇒ **已移动 2814 个文件**到 `archive/root-scratch/{py,txt,md,json,logs,other}`。
- [x] **T-294-09 复核 0 删除**：归档 **2814** + 根留 **29** = **2843** ✓（守恒）。
- [x] **T-294-10 门禁**：`release_check.py` @3.14.7 ⇒ **`status pass` · `EXIT 0` · `missing []` · `gates 47`**。
  ★ 日志 `output/_gate294_tidy.log`。
- [x] **T-294-11 修真因**：`mcp-server/tool_specs_batch81.py:72` 的 `default="（必填，无默认值）"`
  ⇒ **删掉 `default=`**（★ 与全仓 **14** 处先例一致 ⇒ `Param.default` 自动是 `...` ⇒ 判必填）。
- [x] **T-294-12 登记 `archive/`**：`AGENTS.md` 铁律 3 加登记段。
- [x] **T-294-13 写判据**：`tests/test_workspace_tidy_294.py`（**6 条**）。
- [x] **T-294-14 回写四处**：`GOAL.md` §七 · `AUTO_HANDOFF.md` ① · `ROADMAP.md` §一 · `memory/2026-10-09.md`。

---

## 二、改动面

| # | ★ 文件 | ★ 性质 |
|---|---|---|
| 1 | `archive/root-scratch/**`（**2814** 个） | ★ **移动**（★ 从仓库根搬来，★ **内容一字未改**） |
| 2 | `mcp-server/tool_specs_batch81.py` | ★ **删 1 处 `default=`**（★ 修真因） |
| 3 | `AGENTS.md` | ★ **加** `archive/` 登记段（★ 铁律 3） |
| 4 | `tests/test_workspace_tidy_294.py` | ★ **新建判据**（6 例） |
| 5 | `specs/294-workspace-tidy/*` | ★ 本规格四件套 |

---

## 三、判据读数

| # | 判据 | ★ 改前 | ★ 改后 |
|---|---|---|---|
| ① | `test_root_holds_only_the_allowlist` | ❌ **FAILED**（2843 个） | ✅ pass（29 个） |
| ② | `test_nothing_was_deleted` | ✅ pass | ✅ pass |
| ③ | `test_archive_dir_is_registered_in_agents_md` | ❌ **FAILED** | ✅ pass |
| ④ | `test_no_param_default_is_a_chinese_placeholder` | ❌ **FAILED**（1 处） | ✅ pass |
| ⑤ | `test_review_run_output_dir_is_required` | ❌ **FAILED** | ✅ pass |
| ⑥ | `test_only_the_one_param_default_changed` | ✅ pass | ✅ pass |
| — | **合计** | **3 failed, 3 passed** | **6 passed** |
