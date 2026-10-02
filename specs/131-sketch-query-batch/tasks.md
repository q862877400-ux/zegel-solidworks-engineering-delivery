# Tasks · Feature 131 草图只读查询

> 每条任务都带 **`→ 验收:`**，且验收是**一条能跑出绿的命令**。

## T1 · 在 `scripts/sw_sketch.py` 加"只回读数"的薄函数

- [x] `ELEMS_PER_LINE = 12` / `ELEMS_PER_ARC = 16`（★ 附真机证据指针）
- [x] `_count_by_divisor(...)`：长度不是整数倍 ⇒ **抛错**，不圆整
- [x] `count_lines(sketch) -> int`
- [x] `count_arcs(sketch) -> int`
- [x] `count_segments(sketch) -> int`
- [x] `sketch_by_name(model, name)`：按名取，取不到 ⇒ **RuntimeError**

→ 验收: `python -c "import sys;sys.path.insert(0,'scripts');import sw_sketch as m;print(m.ELEMS_PER_LINE, m.ELEMS_PER_ARC, callable(m.count_lines))"`

## T2 · 加 `resolve_sketch(model, name="")`（★ 真机抓出的 bug 的修法）

- [x] 显式名 ⇒ 试中英文候选名
- [x] 留空 ⇒ `current_sketch_name` 的结果 + 候选名
- [x] 都不行 ⇒ ★ 从**特征树**找最后一个 `Sketch`/`草图` 特征（语言无关）
- [x] 仍不行 ⇒ **抛错**（不静默）

→ 验收: `D:\AI\SW\output\sketch-evidence.json` 里 `resolve.by_blank_on_closed_sketch == true`

## T3 · 写 `mcp-server/tool_specs_batch18.py`（4 个工具，全声明式）

- [x] `solidworks_sketch_count_lines` / `_count_arcs` / `_count_segments` / `_is_3d`
- [x] `param_alias = _consumed("sketch_name")`；`derived_args = _sketch_args`；**不设 `inject`**
- [x] ★ 工具说明写明「**整圆算一段弧**」（真机实测：1 线 + 1 圆 ⇒ lines=1 / arcs=1 / segments=2）

→ 验收: `python -c "import sys;sys.path[:0]=['mcp-server','.'];import register_capabilities as rc;print(len(rc.all_specs()))"` ⇒ **62**

## T4 · 注册进 `register_capabilities.BATCH_MODULES`

- [x] 加 `"tool_specs_batch18"` 并注明本批的关键点

→ 验收: 同 T3 的命令（62 而不是 58）

## T5 · 写真机证据脚本 `tools/capture_sketch_evidence.py`

- [x] ★ **走工具真实路径**（import `_sketch_args`），不是只调底层函数
- [x] 正例 4 个读数 + 2 个负例（坏名字 / 除数不整除）
- [x] 安全：`CommandInProgress` + 只在新零件上跑 + 关件不保存

→ 验收: `python tools/capture_sketch_evidence.py` ⇒ exit 0，且 `output/sketch-evidence.json` 的 `verdict == "pass"`

## T6 · 收工纪律

- [x] 修 harvest-report 偏离数字 → 门禁链 → 全量 pytest 0 failed
- [x] ROADMAP §一 游标 · known-facts 一条
- [x] 两仓库各自 commit（不 push）

→ 验收: 门禁链八条命令 exit 0 且 `pytest` 0 failed；两仓库 `git status --porcelain` 为空

## 发现的偏差（实现中冒出来、计划里没预料的）

| # | 偏差 | 处置 |
|---|---|---|
| D1 | ★ `current_sketch_name` 在**草图关闭**时回**英文 fallback**「Sketch1」，中文 UI 下必错 | 新增 `resolve_sketch`（T2）；★ **只有真机能暴露** |
| D2 | ★ 我的**期望值错了**：以为圆不算弧 | 改正期望值（不是改代码）+ 写进工具说明 |
| D3 | `derived_args` 里拿不到注入的 `model` | 照 `batch4::_model` 自己连一次 |
