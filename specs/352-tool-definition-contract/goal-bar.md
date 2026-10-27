# 规格 352 · 目标栏（唯一进度字段）

> ★★ **本文件是唯一进度字段** —— 进度只看上面那一行；其余段落是上下文，不是判据。

**阶段：**★ **收口** —— 498 条工具定义**全部改写完** · 契约违规 **3709 → 0** · 可懂性 **71.4% → 100%** · `release_check` **rc=0** · 当前动作 = **T-352-25**（回写游标 + 收尾提交）

---

## 一 · 业主指令（本规格唯一来源）

> 「把**你所有 SolidWorks 建模的这些 MCP 工具修正一遍**，你现在都是半成品…
> **光看一下里面的参数，你可能不懂它到底是干什么的**…我的 token 预算是无限的，
> 要**大大方方地多花 token 去验证去确认，然后再动手**。」

★ 这是同一诉求的**第三次**。前两次（2026-10-07）都只动「首句」，
而 `doc` 的**主体**仍是变更日志 + 证据链 ⇒ 本次**重写主体**，证据搬进
`ToolSpec.evidence`（非模型可见）。

## 二 · 读数（判据 A1–A8，详见 `results.md`）

| 判据 | 改前 | 改后 |
|---|---|---|
| A1 契约门禁 `--strict`（498 条全量） | **3709** 条 | ★★ **0** |
| A2 棘轮基线 | 3709 条 | ★ **0**（已降到零） |
| A3 可懂性（lean 只看 120 字符，同 21 题） | **15/21 = 71.4%** | ★★ **21/21 = 100%** |
| A3 选择准确性（55 题） | 55/55 | 55/55（**回归护栏**，不降） |
| A4 证据零丢失 | — | 475 条源码逐字 · 19 条快照 · **搬错 0** |
| A5 描述全文 / lean 目录 | 149,502 / 69,588 字 | **122,163（−18%）** / **85,018（+22%）** |
| A6 既有门禁 | — | ★ `release_check` **rc=0** |

★ A5 的两个数方向相反**必须一起看**：lean 目录变大不是退步 —— 旧目录小是因为
中文 `。` 把每行砍到 30–50 字（**便宜来自信息被砍掉**）；现在每行用满 120 字符的有效信息。

## 三 · 落地形态

- 门禁：`scripts/check_tool_contract.py`（第 65 道，**hard**，判据 K1–K5 + K9/K10），
  断句口径**复用** `check_lean_first_line_caveat.lean_first`（不另写一份）。
- 证据：`ToolSpec.evidence` + `tools/migrate_tool_evidence.py`（`--snapshot/--apply/--verify/
  --apply-docs/--validate-docs`）。
- 评测：`tools/eval_tool_selection.py`（选哪个）· `tools/eval_lean_comprehension.py`
  （只看 120 字符能不能答对，答案键从结构化字段机械取）。
- 派活：`tools/gen_tool_rewrite_briefs.py` → `output/_briefs/G1..G8.json`；
  8 组并行，产物是可评审的 `specs/352-.../rewrites/*.json`（29 个）。

## 四 · 改写暴露出来的真缺口（只登记，不在描述层修 → `results.md` §三）

1. `solidworks_simulation_solve_memory_preflight.memory_budget_gb` 默认 `0.0` ⇒ ★ **出厂默认会一律拒绝求解**；
2. `solidworks_part_sweep` 的 `profile_sketch`/`path_sketch` 默认 `""` 而实现当**必填**；
3. `unsuppress_component`/`assembly_replace_component` 默认值是**占位符 `"..."`**；
4. `insert_delete_face`·`insert_offset_surface`·`sketch_mirror`·`section_area_crosscheck`
   **需要先选而没有选择入口**（已登记 `docs/preselect-family-baseline.json`，verdict = 待修）。

## 下一个动作（只写一条）

★ **T-352-25**：回写 `docs/ROADMAP.md` 游标，然后收尾提交（`results.md` 与 `goal-bar.md`）。
→ 验收: `git status` 干净 · `python -B scripts/release_check.py` rc=0
