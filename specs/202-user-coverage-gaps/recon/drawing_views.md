<!-- domain: 工程图-视图族 -->

| 功能 | 官方成员 | 签名 | 官方例子 | 本仓现状 | 指针族 |
|---|---|---|---|---|---|
| 投影视图 | `CreateDrawViewFromModelView3` | `View CreateDrawViewFromModelView3( System.string ModelName, System.string ViewName, System.double LocX, System.double LocY, System.double LocZ )` | 无 | `scripts/sw_api_sldworks.py:3537` · `scripts/sw_api_sldworks.py:20414` | — |
| 剖面视图 | `CreateSectionViewAt5` | `View CreateSectionViewAt5( System.double X, System.double Y, System.double Z, System.string SectionLabel, System.int Options, System.object ExcludedComponents, System.double SectionDepth )` | 无 | `scripts/sw_api_sldworks.py:3557` · `scripts/sw_api_sldworks.py:20434` | — |
| 局部视图 | `CreateDetailViewAt4` | `System.object CreateDetailViewAt4( System.double X, System.double Y, System.double Z, System.int Style, System.double Scale1, System.double Scale2, System.string LabelIn, System.int Showtype, System.bool FullOutline, System.bool JaggedOutline, System.bool NoOutline, System.int ShapeIntensity )` | 无 | `scripts/sw_api_sldworks.py:3530` · `scripts/sw_api_sldworks.py:20407` | — |
| 断裂视图 | `InsertBreak` | `BreakLine InsertBreak( System.int Orientation, System.double Position1, System.double Position2, System.int Style )` | 无 | `scripts/sw_api_sldworks.py:9696` · `scripts/sw_api_sldworks.py:26363` | — |
| 辅助视图 | `CreateAuxiliaryViewAt2` | `System.object CreateAuxiliaryViewAt2( System.double X, System.double Y, System.double Z, System.bool NotAligned, System.string Label, System.bool Showarrow, System.bool Flip )` | 无 | `scripts/sw_api_sldworks.py:3520` · `scripts/sw_api_sldworks.py:20397` | — |

## 取证明细（逐项抄录）

### 1 投影视图

- 候选按序试：`CreateDrawViewFromModelView3` / `CreateDrawViewFromModelView` / `CreateUnfoldedViewAt3`
- 命中文档（第一个存在的就是答案）：`C:\swapi\types\IDrawingDoc\CreateDrawViewFromModelView3.md`
  - 同一递归搜索另存在（未被选用）：`C:\swapi\types\IDrawingDoc\CreateDrawViewFromModelView.md`、`C:\swapi\types\IDrawingDoc\CreateDrawViewFromModelView2.md`、`C:\swapi\types\IDrawingDoc\CreateUnfoldedViewAt.md`、`C:\swapi\types\IDrawingDoc\CreateUnfoldedViewAt2.md`、`C:\swapi\types\IDrawingDoc\CreateUnfoldedViewAt3.md`
- **Signature** 行（整行照抄）：`**Signature**: \`View CreateDrawViewFromModelView3( System.string ModelName, System.string ViewName, System.double LocX, System.double LocY, System.double LocZ )\``
- 官方例子（`C:\swapi\examples\` 下按文件名含成员名搜）：无
- md 全文搜 `AccessSelections`：无 ⇒ —
- 本仓 grep：`D:\AI\SW\scripts\` 命中 `scripts\sw_api_sldworks.py:3537`、`scripts\sw_api_sldworks.py:20414`；`D:\AI\SW\mcp-server\` 无

### 2 剖面视图

- 候选按序试：`CreateSectionViewAt5` / `CreateSectionViewAt3` / `CreateSectionViewAt`
- 命中文档（第一个存在的就是答案）：`C:\swapi\types\IDrawingDoc\CreateSectionViewAt5.md`
  - 同一递归搜索另存在（未被选用）：`C:\swapi\types\IDrawingDoc\CreateSectionViewAt.md`、`CreateSectionViewAt2.md`、`CreateSectionViewAt3.md`、`CreateSectionViewAt4.md`
- **Signature** 行（整行照抄）：`**Signature**: \`View CreateSectionViewAt5( System.double X, System.double Y, System.double Z, System.string SectionLabel, System.int Options, System.object ExcludedComponents, System.double SectionDepth )\``
- 官方例子（`C:\swapi\examples\` 下按文件名含成员名搜）：无
- md 全文搜 `AccessSelections`：无 ⇒ —
- 本仓 grep：`D:\AI\SW\scripts\` 命中 `scripts\sw_api_sldworks.py:3557`、`scripts\sw_api_sldworks.py:20434`；`D:\AI\SW\mcp-server\` 无

### 3 局部视图

- 候选按序试：`CreateDetailViewAt4` / `CreateDetailViewAt3`
- 命中文档（第一个存在的就是答案）：`C:\swapi\types\IDrawingDoc\CreateDetailViewAt4.md`
  - 同一递归搜索另存在（未被选用）：`C:\swapi\types\IDrawingDoc\CreateDetailViewAt.md`、`CreateDetailViewAt2.md`、`CreateDetailViewAt3.md`
- **Signature** 行（整行照抄）：`**Signature**: \`System.object CreateDetailViewAt4( System.double X, System.double Y, System.double Z, System.int Style, System.double Scale1, System.double Scale2, System.string LabelIn, System.int Showtype, System.bool FullOutline, System.bool JaggedOutline, System.bool NoOutline, System.int ShapeIntensity )\``
- 官方例子（`C:\swapi\examples\` 下按文件名含成员名搜）：无
- md 全文搜 `AccessSelections`：无 ⇒ —
- 本仓 grep：`D:\AI\SW\scripts\` 命中 `scripts\sw_api_sldworks.py:3530`、`scripts\sw_api_sldworks.py:20407`；`D:\AI\SW\mcp-server\` 无

### 4 断裂视图

- 候选按序试：`InsertBreak` / `BreakView` / `InsertBreakView`
- 命中文档（第一个存在的就是答案）：`C:\swapi\types\IView\InsertBreak.md`
  - 同一递归搜索另存在（未被选用）：`C:\swapi\types\IDrawingDoc\BreakView.md`；`InsertBreakView` 在 `C:\swapi\types\` 下不存在
- **Signature** 行（整行照抄）：`**Signature**: \`BreakLine InsertBreak( System.int Orientation, System.double Position1, System.double Position2, System.int Style )\``
- 官方例子（`C:\swapi\examples\` 下按文件名含成员名搜）：无
- md 全文搜 `AccessSelections`：无 ⇒ —
- 本仓 grep：`D:\AI\SW\scripts\` 命中 `scripts\sw_api_sldworks.py:9696`、`scripts\sw_api_sldworks.py:26363`；`D:\AI\SW\mcp-server\` 无
- ⚠ 逐字摘自该 md 第 12 行（不改写、不判优劣）：`Obsolete. Superseded by [[IView::InsertBreak2]].`

### 5 辅助视图

- 候选按序试：`CreateAuxiliaryViewAt2` / `CreateAuxiliaryViewAt`
- 命中文档（第一个存在的就是答案）：`C:\swapi\types\IDrawingDoc\CreateAuxiliaryViewAt2.md`
  - 同一递归搜索另存在（未被选用）：`C:\swapi\types\IDrawingDoc\CreateAuxiliaryViewAt.md`
- **Signature** 行（整行照抄）：`**Signature**: \`System.object CreateAuxiliaryViewAt2( System.double X, System.double Y, System.double Z, System.bool NotAligned, System.string Label, System.bool Showarrow, System.bool Flip )\``
- 官方例子（`C:\swapi\examples\` 下按文件名含成员名搜）：无
- md 全文搜 `AccessSelections`：无 ⇒ —
- 本仓 grep：`D:\AI\SW\scripts\` 命中 `scripts\sw_api_sldworks.py:3520`、`scripts\sw_api_sldworks.py:20397`；`D:\AI\SW\mcp-server\` 无
