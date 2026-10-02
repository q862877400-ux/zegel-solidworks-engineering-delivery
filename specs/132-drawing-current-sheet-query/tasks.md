# Tasks · Feature 132 当前活动工程图的轻量只读读数

> 每条任务都带 **`→ 验收:`**，且验收是**一条能跑出绿的命令**。

## T0 · ★ 先写真机探针（W1 证明这一步会推翻按直觉做的设计）

- [x] `tools/probe_drawing_object_routes.py`：答三个未知
      （`model` 能否直接当 `IDrawingDoc` / `GetProperties2` 的形状 / 空图纸的 `GetFirstView`）
- [x] 产物 `output/drawing-object-routes.json`

→ 验收: `python tools/probe_drawing_object_routes.py` ⇒ exit 0，且证据里
  `A_model_GetType == 3`、`B_GetCurrentSheet_on_model` 为"拿到对象"、`D_Sheet_GetProperties2.len == 8`

## T1 · 新建能力层 `scripts/sw_drawing_query.py`

- [x] `SWDOC_DRAWING = 3` · `PAPER_SIZE_NAMES`（13 个成员，两源一致）
- [x] `require_drawing(model)`：`GetType() != 3` ⇒ **RuntimeError**
- [x] `sheet_count` / `sheet_names` / `current_sheet_name` / `sheets_summary`
- [x] `current_sheet_info`：图幅 + **宽高毫米** + 比例 + 投影角 + 图纸格式名；元素 <7 ⇒ **报错**
- [x] `list_views`：`Type == 1` **过滤**；遍历设 500 上限
- [x] ★ **没有**改 `scripts/sw_drawing_view.py`（那是生成物，改了会被覆盖）

→ 验收: `python -c "import sys;sys.path.insert(0,'scripts');import sw_drawing_query as m;print(m.SWDOC_DRAWING, m.PAPER_SIZE_NAMES[6])"`
  ⇒ 输出 `3 A4`

## T2 · 写 `mcp-server/tool_specs_batch19.py`（3 个工具）

- [x] `solidworks_drawing_list_sheets` / `_get_current_sheet` / `_list_views`
- [x] 三者都 **无参数**（只作用于当前活动文档）· `inject` 用默认 `"model"`（不需 `derived_args`）
- [x] 工具说明写明与 `inspect_drawing` 的**分工**、以及**宽高已换算成毫米**

→ 验收: `python -c "import sys;sys.path[:0]=['mcp-server','.'];import register_capabilities as rc;print(len(rc.all_specs()))"` ⇒ **65**

## T3 · 注册进 `register_capabilities.BATCH_MODULES`

- [x] 加 `"tool_specs_batch19"` 并注明本批关键点

→ 验收: 同 T2（65 而不是 62）

## T4 · 写真机证据 `tools/capture_drawing_query_evidence.py`

- [x] ★ **核声明的 `module`/`function` 真的解析到能力层**（工具层与能力层没断链）
- [x] 正例：`sheets_summary` / `current_sheet_info`（**297×210 mm**）/ ★ `list_views == []`
- [x] 负例：在**零件**上报错 · `GetProperties2` 元素不足时报错
- [x] 安全：`CommandInProgress` + 只在新文档上跑 + 关件不保存

→ 验收: `python tools/capture_drawing_query_evidence.py` ⇒ exit 0，`output/drawing-query-evidence.json` 的 `verdict == "pass"`

## T5 · 收工纪律

- [x] 重建覆盖率地图（`tools/build_union_map.py`）—— ★ 门禁预判的第①类：新增了公开函数
- [x] 计数守卫同步：`test_server_wiring` 62→**65** · `test_mcp_protocol_layer` 107→**110**
- [x] 门禁链 8 条 exit 0 · 全量 pytest **0 failed**
- [x] Spec Kit 五件套 · ROADMAP §一 游标 · known-facts 160
- [x] `capabilities.yaml` 加 `drawing_current_sheet_query`（level=verified + evidence）
- [x] 两仓库各自 commit（不 push）

→ 验收: 两仓库 `git status --porcelain` 为空，且 pytest 0 failed

## 发现的偏差（实现中冒出来、计划里没预料的）

| # | 偏差 | 处置 |
|---|---|---|
| D1 | ★ **W2 原计划是"一大批"**，核过缺口后发现只读那一类**已被 `inspect_drawing` 覆盖** | 缩成 3 个工具；理由写进 `plan-10h.md` 的 W2 段与 known-facts 159 |
| D2 | ★ 我以为要"取 `IDrawingDoc` 对象" | 官方示例说 `(DrawingDoc)swModel` 是**转换** ⇒ 实测确认 `model` 直接能调 ⇒ **包装层更简单** |
| D3 | ★ 官方 `GetProperties` 文档写 **7** 个 double，实测 `GetProperties2` 是 **8** 个 | 按实测取前 7 个语义位；★ 元素 <7 报错，不猜第 8 个的含义 |
| D4 | ★ 空图纸 `GetFirstView()` 回**图纸本身**（Type=1） | 过滤；★ 不做这一步会列出假视图 |
| D5 | 模块 docstring 漏了闭合 `"""` ⇒ SyntaxError（事实 48 那一族） | 补上；★ 定则：长文本进源码后**必须 `ast.parse` 过一遍**（本轮已做成例行动作） |
