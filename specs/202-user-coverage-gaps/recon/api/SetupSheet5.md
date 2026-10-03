# SetupSheet5
- 官方路径: `C:\swapi\types\IDrawingDoc\SetupSheet5.md`（接口目录名：`IDrawingDoc`；全库仅此 1 份）
- Signature: `**Signature**: `System.bool SetupSheet5( System.string Name, System.int PaperSize, System.int TemplateIn, System.double Scale1, System.double Scale2, System.bool FirstAngle, System.string TemplateName, System.double Width, System.double Height, System.string PropertyViewName, System.bool RemoveModifiedNotes )``
- 指针族: —（该文件全文未出现 `AccessSelections`）
- 本仓现状: `scripts\sw_api_sldworks.py:3688`（`'SetupSheet5': 11,`）、`scripts\sw_api_sldworks.py:20565`（`'SetupSheet5': 242,`）；`D:\AI\SW\mcp-server\` 内无命中

## Remarks（逐字）
Call [[IModelDoc2::ForceRebuild3]] after calling IDrawingDoc::SetupSheet5 to update any changes to first angle/third angle projections in the drawing views.

If you specify a different filename for TemplateName than what is currently being used by SOLIDWORKS, then SOLIDWORKS updates the sheet format.

## Examples
无