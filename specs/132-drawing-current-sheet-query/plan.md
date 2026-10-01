# Plan · Feature 132 当前活动工程图的轻量只读读数

## 一、要查的官方源与冲突裁决顺序

| 序 | 源 | 本特性用它查什么 |
|---|---|---|
| 1 | 出厂类型库反射（`D:\AI\SW\_raw\reflect_sldworks\`） | **裁决者**：`IDrawingDoc` / `ISheet` / `IView` 的成员名与 arity |
| 2 | `C:\swapi\types\{IDrawingDoc,ISheet,IView}\*.md` | 精确签名与返回说明 |
| 3 | `C:\swapi\enums\swDwgPaperSizes_e.md` | 图幅代码 → 名称 |
| 4 | `C:\swapi\examples\` 的官方示例 | ★ **调用序列**（本特性最有用的一源）|
| 5 | 本机实测 | ★ **返回结构的实际形状 + 假视图现象**（官方没写）|

**冲突裁决**：以**出厂类型库反射**为准（铁律 4）。本特性实际用到的两处**两源一致**：
`swDwgPaperSizes_e`（13 成员值全同）· `GetProperties`/`GetProperties2` 的存在与 Obsolete 关系。

## 二、★ 官方示例给出的调用序列（照抄，不发明）

`C:\swapi\examples\Get_Drawing_View_Names_and_Types_Example_CSharp.md`：
```csharp
swModel = (ModelDoc2)swApp.ActiveDoc;
swDraw  = (DrawingDoc)swModel;          // ★ 转换，不是"取子对象"
swSheet = (Sheet)swDraw.GetCurrentSheet();
swView  = (View)swDraw.GetFirstView();
while (swView != null) { swView.GetName2(); swView.Type; swView = swView.GetNextView(); }
// Postconditions: **Traverses the views on the CURRENT SHEET**
```

## 三、★★★ 三个关键未知 —— 全部由**真机探针**回答（`tools/probe_drawing_object_routes.py`）

| 问题 | 真机读数 | 对设计的影响 |
|---|---|---|
| pywin32 迟到绑定下，`model` 能不能**直接调** `IDrawingDoc` 的方法？ | `model.GetType()` → **3**，且 `GetCurrentSheet()` **拿到对象** | ★ **不需要"取 drawing 对象"**（比 W1 的草图简单）；但**必须判类型**，否则在零件上静默出错 |
| `ISheet.GetProperties2()` 返回什么形状？ | **8 个 double**（官方 `GetProperties` 文档写 7 个）：`[6.0, 12.0, 1.0, 1.0, 1.0, 0.297, 0.21, 1.0]` | 图幅取 `[0]`=6=A4 · 宽高取 `[5]`/`[6]` **单位米** ⇒ **换算成 mm**（规则 2）· ★ 元素 <7 要**报错** |
| 空图纸上 `GetFirstView()` 是什么？ | ★ 返回**图纸本身**（`Type == 1`、名字 = 图纸名），**不是 None** | ★ **列视图必须过滤 `Type == 1`**，否则会把图纸当视图列出来 |

★ 两条独立证据同指 A4：`paperSize = 6`（枚举）与 `0.297 × 0.21 m`（尺寸）⇒ 互相印证。

## 四、分层落点

| 逻辑 | 落在哪 | 为什么 |
|---|---|---|
| 类型判定 / 图纸读数 / 视图链 | ★ **新模块 `scripts/sw_drawing_query.py`** | ⚠ **不能**放 `scripts/sw_drawing_view.py` —— 那是 `tools/gen_iview_registry.py` 的**生成物**，改了会被覆盖 |
| 工具声明（参数搬运） | `mcp-server/tool_specs_batch19.py` | 只做声明；★ `inject` 用默认 `"model"`（目标函数首参就是 `model`）⇒ **不需要 `derived_args`** |

## 五、与 `solidworks_inspect_drawing` 的分工（★ 不重叠，也不替换）

| | `solidworks_inspect_drawing` | 本特性 3 个工具 |
|---|---|---|
| 入参 | **`drawing_path`** | ★ **无**（只看当前活动文档）|
| 开件 | 自己开（read_only） | ★ 不开 |
| 产物 | 三视图预览 + JSON 报告 | ★ 不落文件 |
| 用途 | 审视一份图纸、留证据 | 「这图几张纸？什么图幅？几个视图？」|

## 六、风险与对策

| 风险 | 对策 |
|---|---|
| 在**零件**上调用 ⇒ 静默回无意义结果 | `require_drawing` 判 `GetType() != 3` ⇒ **报错**（负例已验） |
| 官方返回结构变了 | 元素 <7 ⇒ **报错**，不猜（负例已验） |
| 图纸被当成视图 | 过滤 `Type == 1`（正例已验：空图纸回 `[]`） |
| 视图链可能循环 | 遍历设 **500 次上限**，不无限循环 |
