# Feature 131 · 草图只读查询（砌墙 W1）

> 状态与进度不写在这里（宪法：那在 `ROADMAP.md` §一 游标 / `capabilities.yaml` / `docs/metrics.md`）。

## 一、要解决的问题

AI 需要能**读出草图里有什么**（几条线、几条弧、几段、是不是 3D 草图），
才能规划下一步（要不要加约束、能不能拉伸）。

现状：`scripts/sw_sketch.py` 有 25 个公开查询函数，**一个都没挂成 MCP 工具**，
而它们**首参全是 `sketch`**（COM 对象）—— 不在既有注入点（`model` / `sw_app` / `study`）里。

## 二、需求（各带来源）

| # | 需求 | 来源 |
|---|---|---|
| R1 | 能给出草图里**直线的条数** | 官方 `ISketch.GetLines2`；本项目 `scripts/sw_sketch.get_lines`（MIT，本仓库） |
| R2 | 能给出草图里**圆弧的条数** | 官方 `ISketch.GetArcs2`；本项目 `scripts/sw_sketch.get_arcs`（MIT，本仓库） |
| R3 | 能给出草图里**几何段的总数** | 官方 `ISketch.GetSketchSegments`；本项目 `scripts/sw_sketch.get_sketch_segments`（MIT，本仓库） |
| R4 | 能判断**是不是 3D 草图** | 官方 `ISketch.Is3D`；本项目 `scripts/sw_sketch.is_3d_sketch`（MIT，本仓库） |
| R5 | 调用方可以**给草图名**，也可以**留空**（"就要刚建的那个"） | 本项目既有模式：`sw_part.current_sketch_name` 的 fallback 设计（MIT，本仓库） |
| R6 | ★ **草图关闭后仍要能取到** | 真机探针 `tools/probe_sketch_object_routes.py` 的读数（本项目，MIT）：`GetActiveSketch2` / `ActiveSketch` 在关闭后均为 `None` |
| R7 | ★ **中文 UI 与英文 UI 都要能用** | `docs/known-facts.md` 第 9 条（名字随 UI 语言变）；本项目既有 `sw_part._get_sketch_name_candidates`（MIT，本仓库） |
| R8 | 取不到草图要**报错**，不静默返回 0 | 本项目一贯纪律（选不中就报错）|

## 三、不做什么（有据）

| 不做 | 原因 |
|---|---|
| 不在本特性里挂 `get_lines` / `get_arcs` **原样** | 它们返回**数值数组**（每条线 12 个 `float`）⇒ AI 拿回 36 个浮点数**判断不出"几条线"**；本特性挂的是翻译成条数的薄函数 |
| 不做草图的**写**操作（加几何 / 加约束 / 改尺寸） | 那需要另一套验证（要能断言"加完之后形状对不对"），不属于"只读查询"这一批 |
| 不搬四家外部项目的任何代码 | 16/17 个域都已有我们的实现，**先挂自己的**（少许可与改造两道工序） |

## 四、验收（本特性的完成判据）

```
① 静态：`register_capabilities.all_specs()` 里出现 4 个新工具，且门禁全绿
② ★ 真机：`D:\AI\SW\output\sketch-evidence.json` 的 `verdict` == "pass"
   —— 且证据里必须**同时**包含两个负例的命中记录（坏名字 / 除数不整除）
```
