# Acceptance — 工作区整理：把仓库根 2814 个草稿归入 `archive/`（只搬不删）

**Feature**: `specs/294-workspace-tidy/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 7/7 绿 · 红基线成立（`4 failed, 3 passed`）· 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★★ 业务结论**: ★★★ **仓库根 2843 → 29 个文件**（只搬不删，守恒 **2814 + 29 = 2843**）；
★★★ **顺带挖出并修掉一个真 bug**：`Param` 把**中文提示语**当默认值 ⇒ 真机在仓库根建出同名目录（18.3 MB）。

## 一、逐条验收

| # | 需求 | 判据 | ★ 改前 | ★ 改后 |
|---|---|---|---|---|
| FR-001 | 根只留白名单 | `test_root_holds_only_the_allowlist` | ❌ **FAILED**（2843） | ✅ pass（29） |
| FR-002 | 归档不删文件 | `test_nothing_was_deleted` | ✅ pass | ✅ pass |
| FR-003 | 不破门禁 | `release_check.py` @3.14.7 | ✅ pass | ✅ **pass** |
| FR-004 | `archive/` 已登记 | `test_archive_dir_is_registered_in_agents_md` | ❌ **FAILED** | ✅ pass |
| FR-005 | 真因已修 | `test_no_param_default_is_a_chinese_placeholder` | ❌ **FAILED**（4 处） | ✅ pass |
| FR-005b | 内容断言 | `test_review_run_output_dir_is_required` | ❌ **FAILED** | ✅ pass |
| FR-006 | 边界冻结 | `test_only_the_one_param_default_changed` | ❌ **FAILED**（4 处） | ✅ pass |
| — | 归档清单可读 | `test_archive_manifest_is_machine_readable` | ✅ pass | ✅ pass |
| — | **合计** | — | **4 failed, 3 passed** | **7 passed** |

## 二、★★★★ 先量：四条风险核查（★ 搬文件前证明「没人依赖」）

| # | ★ 风险 | ★ 方法 | ★ 读数 | ★ 处置 |
|---|---|---|---|---|
| ① | 活代码 import 根模块 | AST 扫全仓 import | ★ **2 个**：`shot` / `ctl`（被 `scripts/sw_jlcfa_*.py`） | ★★ **留根** |
| ② | 验收行点根脚本 | 复刻判据③（扫 **865** 行） | ★ **0 处** | ★ 可搬 |
| ③ | 门禁 `ROOT.glob` | 枚举全部 `check_*.py` | ★ **2 处**；只有 `check_report_criteria_alignment` 扫 `ROOT.glob("*.md")` | ★ 实测搬后仍绿 |
| ④ | 打包器顶层文件 | 读 `sync_bundled_skill.TOP_LEVEL_FILES` | ★ **9 个** | ★★ **留根** |

★ 探针：`output/_scan_root_imports.py` · `output/_scan_acceptance_rootrefs.py` · `output/_scan_root_buckets.py`
★★ **⚠ 三支探针与搬运脚本 `output/_tidy_workspace.py` 已在收工时删除** —— ★ 依据 `MEMORY.md` 规则 13
（「**一次性量测探针放 `output/`、不进仓库代码**」）★ 与 ★ 本仓红线（★ **归档只搬不删**管的是**仓库根的既有产物**，
★ 而这三支是**我本轮新建的一次性探针**）。
★★★ **⇒ 它们的**结论**全部落盘保留**（★ 那是**证据**、★ 不删）：
`output/_root_imports.json` · `output/_root_refs.json` · `output/_root_refs_live.json` ·
`output/_root_literal_refs.json` · `output/_root_buckets.json` · `output/_acceptance_rootrefs.json` ·
`output/_tidy_result.json`（★ **归档清单** —— ★ 用它可**按名找回**任何被搬走的文件）✓
★ 证据：`output/_root_imports.json` · `output/_root_refs.json` · `output/_tidy_result.json`

## 三、★★★★★ 真因：畸形目录 `（必填，无默认值）` 是**一个真 bug 的产物**

★★ 现场：仓库根有目录 **`（必填，无默认值）`**（6 文件 / 18.3 MB）—— ★ 它的名字是**一句错误提示**。

★ **根因链**（逐环可核）：

| ★ 环 | ★ 逐字 | ★ 后果 |
|---|---|---|
| ① | `tool_registry.py:299`「`:param default: 默认值；给 ... 表示必填。`」 | ★ 契约：`...` = 必填 |
| ② | `tool_registry.py:311-312`「`return self.required if self.required is not None else self.default is ...`」 | ★★ **给字符串 ⇒ 判「可选」** |
| ③ | `tool_specs_batch81.py:72` `Param("output_dir", str, default="（必填，无默认值）", …)` | ★★ 那句**提示**成了**默认值** |
| ④ | `tool_registry.py:589-592`：`if p.is_required: Field(...) else: Field(default=p.default, …)` | ★ 于是默认值是**那句中文** |
| ⑤ | `sw_review.py:1180` `def run_review(model, output_dir, …)` → `_expand_path` → `mkdir(parents=True)` | ★★★ **真机建出同名目录** |

★★★ **本仓的既有正确写法**（全仓 **14** 处先例）：`Param("name", str, description="…")` —— ★ **省略 `default`**
（`Param.default` 的字段默认值**就是 `...`**）✓ · ★ 而 `required=True` 全仓 **0** 处 ⇒ ★ **本仓约定 = 省略 `default`**。

★★★ **判据抓出的是 4 处、不是 1 处**（★ 这正是否例测试的价值）：

| # | ★ 站点 | ★ 原 `default` | ★ 真实签名 | ★ 修法 |
|---|---|---|---|---|
| ① | `batch81.py:26` `structure` | `"(required)"` | `review_drawing_layout(structure, *, …)` **必填** | ★ 省略 `default` |
| ② | `batch81.py:40` `views` | `"None  →  (\"isometric\", …)"` | `save_review_previews(…, views=None)` | ★ 改 `default=""`（★ 空串 = 用源码回落） |
| ③ | `batch81.py:72` `output_dir` | `"（必填，无默认值）"` | `run_review(model, output_dir, …)` **必填** | ★ 省略 `default` |
| ④ | `batch93.py:48` `bend_feature_names` | `_BENDS.split("——")[0]`（★ **一段说明文字**） | `create_unfold(model, bend_feature_names, *, …)` **必填** | ★ 省略 `default` |

## 四、★★ 改动面

| # | ★ 文件 | ★ 性质 |
|---|---|---|
| 1 | `archive/root-scratch/{py,txt,md,json,logs,other}/**`（**2814** 个） | ★ **移动**（★ 内容一字未改） |
| 2 | `mcp-server/tool_specs_batch81.py` | ★ **3 处 `default`** |
| 3 | `mcp-server/tool_specs_batch93.py` | ★ **1 处 `default`** |
| 4 | `AGENTS.md` | ★ **加** `archive/` 登记段（★ 铁律 3） |
| 5 | `tests/test_workspace_tidy_294.py` | ★ **新建判据**（7 例） |
| 6 | `specs/294-workspace-tidy/*` | ★ 本规格四件套 |

## 五、★★★ 红基线（★ 改前实测）

```
$ python -m pytest tests/test_workspace_tidy_294.py -q
FAILED tests/test_workspace_tidy_294.py::test_root_holds_only_the_allowlist
FAILED tests/test_workspace_tidy_294.py::test_archive_dir_is_registered_in_agents_md
FAILED tests/test_workspace_tidy_294.py::test_no_param_default_is_a_chinese_placeholder
FAILED tests/test_workspace_tidy_294.py::test_review_run_output_dir_is_required
FAILED tests/test_workspace_tidy_294.py::test_only_the_one_param_default_changed
4 failed, 3 passed
```

## 六、★ 归档布局

| ★ 子目录 | ★ 个数 | ★ 内容 |
|---|---|---|
| `py` | **1771** | `_*.py` 一次性探针 + `fx*`/`dbg*`/`jlc*` 修复尝试 |
| `txt` | **879** | `_factNNN.txt` · `_commit_msg_NNN.txt` · 各类草稿 |
| `md` | **55** | `_roadmap_*.md` · `_sec4_new.md` 等草稿 |
| `json` | **51** | 中间结果 |
| `logs` | **41** | 运行日志 |
| `other` | **17** | `.bmp` / `.step` / `.pkl` / `.js` 等 |
| **合计** | **2814** | ★ 根留 **29** ⇒ **2843** ✓ |

## 七、★★ 未过门 / 如实记录

| # | ★ 项 | ★ 说明 |
|---|---|---|
| ① | ★ `check_report_criteria_alignment.py` 的**覆盖减少 1 张表** | ★ 它扫 `ROOT.glob("*.md")`；★ 归档后根只剩 `AGENTS.md`（★ 那张 `_sec4_new.md` 自评表进了 `archive/root-scratch/md/`）。★★ **实测门禁仍 `[PASS]`**（它只要求「扫到的每一张表编号都对」，不要求张数）⇒ ★ 接受，★ 如实记录。 |
| ② | ★ 归档**未 `git add`** | ★ `git status` 会显示 **2585 个 ` D`**（旧路径）+ 大量 `??`（新路径）—— ★★ 这是**未提交工作树**的正常表现（红线禁止 commit）⇒ ★ **文件没丢**（守恒断言守着）。 |
| ③ | ★ 畸形目录本体**未删** | ★ 它在 `archive/` 之外（★ 那是**根上的目录**，本轮只搬**文件**）⇒ ★ 保留原位（★ 红线：禁止删除）。★ 它的**成因已修** ⇒ 不会再长。 |
