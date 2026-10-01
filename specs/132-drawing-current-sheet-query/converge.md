# Converge · Feature 132 当前活动工程图的轻量只读读数

## 一、交付了什么

| 层 | 文件 | 内容 |
|---|---|---|
| 探针 | `tools/probe_drawing_object_routes.py`（新增） | ★ 答三个未知；产物 `output/drawing-object-routes.json` |
| 能力层 | `scripts/sw_drawing_query.py`（**新模块**） | `require_drawing` · `sheet_count` · `sheet_names` · `current_sheet_name` · `sheets_summary` · `current_sheet_info` · `list_views` · `SWDOC_DRAWING` · `PAPER_SIZE_NAMES` |
| 工具层 | `mcp-server/tool_specs_batch19.py`（新增） | 3 个只读工具，无参数、`inject="model"` |
| 注册 | `mcp-server/register_capabilities.py` | `BATCH_MODULES` 加 `tool_specs_batch19` |
| 证据 | `tools/capture_drawing_query_evidence.py`（新增） | 真机验证 ⇒ `output/drawing-query-evidence.json` |
| 能力清单 | `capabilities.yaml` | 新增 `drawing_current_sheet_query`（`verified` + evidence） |

`all_specs()` 从 **62 → 65**。

## 二、★ 本特性的最大价值是**它没有硬凑**

```
W2 原计划是"工程图族，缺口最大（49），先只读" —— 听起来是一大批活。
★ 按纪律**先去核缺口本身**，49 个名字逐个核完：
   · 只读那一类 ⇒ **`solidworks_inspect_drawing` 已经覆盖**（内核就是
     `drawing_workflow.inspect_drawing_structure`，说明逐字列了"页、视图、尺寸、注释和表格"）
   · 写操作那一类 ⇒ 本阶段不做
   · ★ 真缺的只是「**不等路径、不开件、不出预览、不落文件**」的轻量读数
⇒ ★★ **所以本批只有 3 个工具。** 若照缺口数字排活，会把已经做过的事再做一遍。
★ 这正是"不用工具数当进度"的原因（`docs/plan-10h.md` §五）。
```

## 三、收敛判据

| 判据 | 结果 |
|---|---|
| `all_specs()` | 65 |
| 门禁链（8 条） | 全 exit 0（★ 其中「地图与来源同步」先红一次 —— 门禁自己预判的第①类"新增了公开函数"，重建即绿）|
| 全量 pytest | **0 failed**（计数守卫 62→65 / 107→110 同步）|
| 真机证据 `verdict` | `pass`，含 **1 正例（假视图过滤）+ 2 负例** |
| 真机验证覆盖（`docs/metrics.md` 最窄口径） | 本轮**上涨** |

## 四、遗留（明确标注）

| # | 遗留 | 为什么留着 |
|---|---|---|
| L1 | 工程图的**写**操作（加视图 / 标注 / 表格 / BOM）没做 | 需要另一套验证（要能断言"加完之后图纸对不对"）；本阶段不做 |
| L2 | 本批**只在空白新图纸上验过**，没在**有视图的真实图纸**上验 | ★ 要验 `list_views` 在有视图时的读数，需要一个零件 + 生成视图（较重）。**现状：`list_views` 的"有视图"路径未真机验证** ⇒ 已在此注明，不假称验过 |
| L3 | `GetProperties2` 第 8 个元素的含义未查 | 官方没写；不猜（宪法 §III） |
| L4 | `sheets_summary` 在**多图纸**工程图上未真机验证 | 同上（空新图纸只有 1 张）|

## 五、给下一批（W3）的可复用套路（在 W1 基础上补）

```
① 先写**真机探针**回答"对象怎么取" —— 本批再次证明：按命名直觉会选错
   （我以为要"取 IDrawingDoc 对象"，官方示例说 model **就是**它）
② ★ **先去核缺口本身**：缺口名是名字级匹配 ⇒ 「名字不同」会被算成「缺口」
   ⇒ 排活前必须逐个核"是不是已经做过"（本批正是靠这一步把一大批缩成 3 个）
③ 能力逻辑落 `scripts/`（★ 不要改生成物文件 —— `sw_drawing_view.py` 会被重生成覆盖）
④ 证据脚本**走工具真实路径**（核 `module`/`function` 真的解析得到），不是只调底层函数
⑤ 证据里**必须带负例**（类型不对 / 形状不对）
⑥ ★ **期望值本身也要被怀疑**（W1 就错在期望值上）
⑦ ★ **长文本进源码后立刻 `ast.parse`**（本批又踩了一次漏闭合 `"""`）
```
