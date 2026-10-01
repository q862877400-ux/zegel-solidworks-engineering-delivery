# Feature 132 · 当前活动工程图的轻量只读读数（砌墙 W2）

> 状态与进度不写在这里（宪法：那在 `ROADMAP.md` §一 游标 / `capabilities.yaml` / `docs/metrics.md`）。

## 一、要解决的问题

`solidworks_inspect_drawing`（上游 45 个之一）能读工程图结构，但它的形态是
**要 `drawing_path` + 自己开件 + 出三视图预览 + 往 output_dir 落一份 JSON**。
⇒ ★ **对"当前已经打开的那张图纸"没有轻量读数**。
而 AI 的常见需求是：「**这图几张纸？当前图幅多大？有几个视图？**」
—— 不需要出预览、不需要落文件、也不需要知道路径。

## 二、★ 本特性的范围是**核过缺口本身之后**定的（不是照数字排的活）

⑪工程图在覆盖率矩阵里"缺 49"。★ 逐个核过之后分三类：

| 类 | 内容 | 判断 |
|---|---|---|
| ① 名字差异（已覆盖） | `drawing_views` `drawing_dimensions` `drawing_annotations` `drawing_tables` `sheets` `analyze_drawing_*` `drawing_sheet_info` … | **`solidworks_inspect_drawing` 已经覆盖** —— 其实现的内核就是 `drawing_workflow.inspect_drawing_structure`；说明也逐字列了「页、视图、尺寸、注释和表格」 |
| ② 写操作 | `projected_view` `section_view` `detail_view` `auxiliary_view` `broken_view` `balloon` `center_mark` `centerline` `hole_table` `revision_table` `bom` … | **本阶段不做**（风险与验证成本高） |
| ③ ★ **真缺** | "当前活动图纸"的轻量读数 | **本特性做这个** |

★ 缺口名是**名字级**匹配（`tools/build_union_map.py` 的 `_normalize`）⇒ 「名字不同」会被算成「缺口」
⇒ 照着数字排活会把已经做过的事再做一遍。

## 三、需求（各带来源）

| # | 需求 | 来源 |
|---|---|---|
| R1 | 能给出**当前工程图有几张图纸、都叫什么、现在在哪张** | 官方 `IDrawingDoc.GetSheetCount` / `GetSheetNames` / `GetCurrentSheet` → `ISheet.GetName`；官方示例 `Get_Sheet_Numbers_and_Names_Example_VB` |
| R2 | 能给出**当前图纸的图幅**（名称 + 代码） | 官方 `ISheet.GetProperties2` 的 `[0]`；枚举 `swDwgPaperSizes_e`（`C:\swapi\enums\` 与出厂反射**两源一致**）|
| R3 | 能给出**当前图纸的宽高，单位毫米** | 官方 `ISheet.GetProperties2` 的 `[5]`/`[6]`（★ 官方给的是**米**）|
| R4 | 能给出**比例、投影角、图纸格式名** | 官方 `GetProperties2` 的 `[2]`/`[3]`/`[4]`；`ISheet.GetSheetFormatName` |
| R5 | 能列出**当前图纸上的视图**（名 + 类型） | 官方 `IDrawingDoc.GetFirstView` → `IView.GetNextView` / `GetName2` / `Type`；官方示例 `Get_Drawing_View_Names_and_Types_Example_CSharp` |
| R6 | ★ **不得把"图纸本身"当成视图列出** | ★ 真机探针实测：空图纸上 `GetFirstView()` 返回的对象 `Type == 1` 且名字等于图纸名 |
| R7 | 在**非工程图**文档上调用要**报错** | 本项目一贯纪律（类型不对要报错，不静默回空）|
| R8 | 官方返回结构变了要**报错**，不圆整 | 同上（照 W1 的除数不整除就抛错）|

## 四、不做什么（有据）

| 不做 | 原因 |
|---|---|
| 不做工程图的**写**操作（加视图 / 标注 / 表格 / BOM） | 需要另一套验证（要能断言"加完之后图纸对不对"）；本阶段不做 |
| 不搬四家外部项目的任何代码 | 我们已有实现且已挂；先挂自己的 |
| **不**给 `solidworks_inspect_drawing` 改名或替换 | 它与本特性**分工不同**（一个要路径并出证据文件，一个只看当前活动文档）|

## 五、验收（本特性的完成判据）

```
① 静态：`register_capabilities.all_specs()` 里出现 3 个新工具，且门禁全绿
② ★ 真机：`D:\AI\SW\output\drawing-query-evidence.json` 的 `verdict` == "pass"
   证据必须包含：
     · `list_views_on_empty_sheet` 为真（★ 假视图被滤掉）
     · **两个负例**命中（在零件上报错 / 返回结构不足时报错）
```
