# 规格 352 · 结果（498 条工具定义成品化）

> 判据见 `spec.md` A1–A8。本文件只放**读数**与**改写暴露出来的缺口**，不写过程。

## 一 · 两条判据的前后对照

| 判据 | 基线 | 改写后 | 依据 |
|---|---|---|---|
| **A1 契约门禁**（`--strict`，498 条全量） | **3709** 条违规 | ★★ **0** 条 | `python -B scripts/check_tool_contract.py --strict --report` |
| **A2 棘轮**（`docs/tool-contract-baseline.json`） | 3709 条 | ★ **0** 条（基线已清空） | 同上（默认模式退出 0） |
| **A3 可懂性**（lean 只看 120 字符，同 21 题） | **15/21 = 71.4%** | ★★ **21/21 = 100%** | `output/comprehension-{baseline,after}.json` |
| **A3 选择准确性**（55 题，D-9 口径） | 55/55 = 100% | 55/55 = **100%** | `output/tool-selection-{baseline,after}.json` |
| **A4 证据零丢失** | — | 494 条：475 条在源码 `evidence=` **逐字**、19 条在快照、**搬错 0** | `python -B tools/migrate_tool_evidence.py --verify` |
| **A5 体量** | 目录 179,424 字 ≈ 49.8k token | ★ 目录 **170,877 字 ≈ 47.5k token**（−4.8%） | `python -B tools/measure_lean_catalog.py` |
| **A6 既有门禁** | — | `release_check` 全绿（含门禁 215「首句自证」15 条受约束、命中 0） | `python -B scripts/release_check.py` |

★ 关于 A3 的**两条读数要分开看**：
- **选择题 100% → 100%** 说明「选哪个工具」这个尺子**分不出描述好坏**（工具名本身就说明了用途，
  `specs/208` D-9 早就记过这条：原判据注定打平）。它现在的价值是**回归护栏**。
- ★★ **可懂性 71.4% → 100%** 才是业主抱怨的那个量（「光看一下里面的参数，
  你可能不懂它到底是干什么的」）。它的题面**只给 lean 档真正看得见的 120 字符**。

## 二 · 逐条判据的收敛（`--strict`，498 条）

| 判据代码 | 基线 | 改写后 |
|---|---|---|
| `param-default-unstated` | 708 | **0** |
| `param-desc-cjk` | 680 | **0** |
| `param-desc-no-period` | 639 | **0** |
| `first-meta`（首句是 ★/官方签名/查不到） | 264 | **0** |
| `doc-cjk` | 282 | **0** |
| `doc-no-period` | 267 | **0** |
| `doc-one-sentence` | 258 | **0** |
| `first-too-long`（>120 字符） | 215 | **0** |
| `doc-cn-period`（含中文句号） | 250 | **0** |
| `doc-too-long`（>600 字符） | 36 | **0** |
| `side-effect-unstated` | 32 | **0** |
| `param-no-desc` | 10 | **0** |
| `doc-empty` | 4 | **0** |
| `first-not-verb` | 5 | **0** |

## 三 · 改写**暴露出来**的真缺口（★ 本规格只记录，不在描述层修）

改写要求「首句必须说清前置与副作用」，于是把**原文含糊遮住**的东西顶了出来。逐条都是新发现，
按 `spec.md` §五-2 只登记、不擅自改实现：

| # | 工具 | 缺口 | 证据 |
|---|---|---|---|
| 1 | `solidworks_simulation_solve_memory_preflight` | `memory_budget_gb` 默认 `0.0`，而实现只在 `None` 时才回落到「物理内存一半、上限 16 GB」⇒ ★ **按出厂默认调用会一律拒绝求解** | 参数默认值 + `sw_simulation.py::solve_memory_preflight` |
| 2 | `solidworks_part_sweep` | `profile_sketch` / `path_sketch` 默认 `""`，而实现把两者当**必填** ⇒ 默认调用必然失败 | 规格默认值 vs 实现 |
| 3 | `solidworks_unsuppress_component` / `solidworks_assembly_replace_component` | 参数默认值是**字面量 `"..."`**（占位符），被当成真默认值暴露 | `ToolSpec` 默认值 |
| 4 | `solidworks_insert_delete_face` · `solidworks_insert_offset_surface` · `solidworks_sketch_mirror` · `solidworks_section_area_crosscheck` | **需要调用方先选，而对外没有任何选择入口**（无 `selection` 入参、无 `pre_call`）⇒ 模型无法满足前置 | 已登记 `docs/preselect-family-baseline.json`（verdict = 待修） |
| 5 | `solidworks_surface_evidence` | 旧描述说「surface bodies: counts and types」，实现只回 **Modeler 可达性 + 已注册入口**，**不读体数** | `sw_surface.py::collect_surface_evidence` |
| 6 | 一批孔/槽工具 | 参数默认值是**中文字面量**（`通孔` / `盲孔` / `半圆端槽`）⇒ ★ 英文描述里**没法照写**，只能说 "defaults to the localised default name" | `ToolSpec` 默认值 |
| 7 | 19 条工厂生成的 spec | `_spec(name, title, function, doc, params)` 生成 ⇒ 源码里**插不进** `evidence=`，原文只存 `docs/tool-evidence-migration.json` 快照 | `migrate_tool_evidence.py --verify` |

## 四 · 语言判决（D2，试点证据）

★ 试点 21 条，两臂**都是 100%** ⇒ 平手。★ 平手时选**英文**，理由按权重：
① `firstLine()` 只按 `。` 与换行断句、**ASCII `.` 不算** ⇒ 英文整段可用满 120 字符；
中文一旦按自然写法用 `。`，模型只看得到第一个短句（实测中位 30–50 字）；
② 本仓原有 **216/498 已是英文**，统一到英文是**收敛**；
③ DSH 官方 n=72 实测 82% 动词开头、99% 句号收尾。
★ **中文臂能拿 100% 的代价是「写中文时不许用中文句号」**——这条约束本身就是选英文的理由。

## 五 · 派活与写盘（可复现）

- 分组：`specs/352-tool-definition-contract/groups.json`（8 组，62–63 条/组，按批次文件切分，**不相交**）。
- 简报：`tools/gen_tool_rewrite_briefs.py` → `output/_briefs/G1..G8.json`（每条含 evidence / impl / params）。
- 产物：`specs/352-tool-definition-contract/rewrites/*.json`（29 个文件，**可评审的改写工件**）。
- 落盘：`python -B tools/migrate_tool_evidence.py --apply-docs <json>`（只改 `doc` 与 `description`，
  **不碰 `evidence=`**；演算用 `--dry-run-docs`；自检用 `--validate-docs`）。
- ★ 落盘器踩到的三个坑（都已修，且都属「静默失效」）：
  ① `params=_PARAMS()` / 工厂把 `Param` 藏在模块级函数里 ⇒ 只扫 `ToolSpec(params=[…])` **改了 0 处**；
  ② 共享参数会让**多个工具命中同一个 `Param` 节点** ⇒ 同一区间叠 4 次 ⇒ 语法错；
  ③ 值本身已被括号包住时再套一层 ⇒ `doc=(( "…" ))`。
