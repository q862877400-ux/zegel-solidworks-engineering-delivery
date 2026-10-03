<!-- domain: 工程图-标注族 -->

# 工程图-标注族 · 官方成员勘察

来源：`C:\swapi\types\`（递归搜 `<候选名>.md`，取**第一个存在**的）、`C:\swapi\examples\`、`D:\AI\SW\scripts\`、`D:\AI\SW\mcp-server\`。

| 功能 | 官方成员 | 签名 | 官方例子 | 本仓现状 | 指针族 |
|---|---|---|---|---|---|
| 图纸格式模板 | `SetupSheet5`（`IDrawingDoc`） | `**Signature**: `System.bool SetupSheet5( System.string Name, System.int PaperSize, System.int TemplateIn, System.double Scale1, System.double Scale2, System.bool FirstAngle, System.string TemplateName, System.double Width, System.double Height, System.string PropertyViewName, System.bool RemoveModifiedNotes )`` | 无 | `scripts/sw_api_sldworks.py:3688`、`scripts/sw_api_sldworks.py:20565` | — |
| 表面粗糙度 | `InsertSurfaceFinishSymbol3`（`IModelDocExtension`） | `**Signature**: `SFSymbol InsertSurfaceFinishSymbol3( System.int SymType, System.int LeaderType, System.double LocX, System.double LocY, System.double LocZ, System.int LaySymbol, System.int ArrowType, System.string MachAllowance, System.string OtherVals, System.string ProdMethod, System.string SampleLen, System.string MaxRoughness, System.string MinRoughness, System.string RoughnessSpacing )`` | 无 | `scripts/sw_api_sldworks.py:6785`、`scripts/sw_api_sldworks.py:23522` | — |
| 基准符号 | `InsertDatumTag2`（`IModelDoc2`） | `**Signature**: `System.object InsertDatumTag2()`` | 无 | `scripts/sw_api_sldworks.py:5677`、`scripts/sw_api_sldworks.py:6291`、`scripts/sw_api_sldworks.py:22414`、`scripts/sw_api_sldworks.py:23028` | — |
| 注释文字 | `InsertNote`（`IModelDoc2`） | `**Signature**: `System.object InsertNote( System.string Text )`` | 无 | `scripts/sw_api_sldworks.py:5699`、`scripts/sw_api_sldworks.py:6316`、`scripts/sw_api_sldworks.py:22436`、`scripts/sw_api_sldworks.py:23053` | — |
| 气泡序号 | `AutoBalloon5`（`IDrawingDoc`） | `**Signature**: `System.object AutoBalloon5( AutoBalloonOptions BalloonOptions )`` | 无 | `scripts/sw_api_sldworks.py:3499`、`scripts/sw_api_sldworks.py:20376` | — |
| 孔表 | `InsertHoleTable2`（`IView`） | `**Signature**: `HoleTableAnnotation InsertHoleTable2( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string StartValue, System.string TableTemplate )`` | 无 | `scripts/sw_api_sldworks.py:9701`、`scripts/sw_api_sldworks.py:26368` | — |
| 修订表 | `InsertRevisionTable2`（`ISheet`） | `**Signature**: `RevisionTableAnnotation InsertRevisionTable2( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string TableTemplate, System.int Shape, System.bool AutoUpdateZoomCells )`` | 无 | `scripts/sw_api_sldworks.py:8065`、`scripts/sw_api_sldworks.py:24768` | — |
| 中心符号线 | `InsertCenterMark3`（`IDrawingDoc`） | `**Signature**: `CenterMark InsertCenterMark3( System.int Style, System.bool Propagate, System.bool Slot )`` | 无 | `scripts/sw_api_sldworks.py:3624`、`scripts/sw_api_sldworks.py:20501` | — |

## 候选命中过程（逐个试，第一个存在者即为答案）

| 功能 | 候选依次 | 各自结果 |
|---|---|---|
| 图纸格式模板 | `SetupSheet5` / `SetupSheet4` / `SetTemplate` | `SetupSheet5` 命中 · `SetupSheet4` 命中（未取） · `SetTemplate` 不存在 |
| 表面粗糙度 | `InsertSurfaceFinishSymbol3` / `InsertSurfaceFinishSymbol2` / `InsertSurfaceFinishSymbol` | `…3` 命中 · `…2` 命中（未取） · 无后缀命中（未取） |
| 基准符号 | `InsertDatumTag2` / `InsertDatumTag` | `InsertDatumTag2` 命中 · 无后缀命中（未取） |
| 注释文字 | `InsertNote` / `InsertNote2` | `InsertNote` 命中 · `InsertNote2` **不存在** |
| 气泡序号 | `AutoBalloon5` / `AutoBalloon4` / `InsertBOMBalloon2` | `AutoBalloon5` 命中（未取后续） |
| 孔表 | `InsertHoleTable2` / `InsertHoleTable` | `InsertHoleTable2` 命中 · 无后缀命中（未取） |
| 修订表 | `InsertRevisionTable2` / `InsertRevisionTable` | `InsertRevisionTable2` 命中 · 无后缀命中（未取） |
| 中心符号线 | `InsertCenterMark3` / `InsertCenterMark2` / `InsertCenterMark` | `InsertCenterMark3` 命中（未取后续） |

## 说明

- 「官方例子」= 在 `C:\swapi\examples\`（2839 个文件）下按文件名含该成员名搜索，**8 项全部无命中**。
- 「指针族」= 把该成员 md 全文取出搜字符串 `AccessSelections`，**8 项全部无命中**，故全部为 `—`（非指针族）。
- 「本仓现状」= 在 `D:\AI\SW\scripts\` 与 `D:\AI\SW\mcp-server\` 下按**词边界**精确匹配（已排除 `__pycache__\*.pyc`）；**8 项全部命中**，且全部集中在 `scripts/sw_api_sldworks.py` 一个文件里。