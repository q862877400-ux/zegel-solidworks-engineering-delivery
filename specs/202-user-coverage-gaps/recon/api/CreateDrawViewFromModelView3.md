# CreateDrawViewFromModelView3
- 官方路径: C:\swapi\types\IDrawingDoc\CreateDrawViewFromModelView3.md（接口目录名：IDrawingDoc —— 全盘仅此 1 份）
- Signature: `View CreateDrawViewFromModelView3( System.string ModelName, System.string ViewName, System.double LocX, System.double LocY, System.double LocZ )`
- 指针族: —
- 本仓现状: D:\AI\SW\scripts\sw_api_sldworks.py:3537、D:\AI\SW\scripts\sw_api_sldworks.py:20414；D:\AI\SW\mcp-server\ 无
## Remarks（逐字）
This method:

- Places the center of the view at the specified location.

- Uses the [swAutomaticScaling3ViewDrawings](<../../docs/swconst/SO_Drawings.md>) setting to set the view scale. If this setting is set to True, then when a new drawing view is inserted, that view automatically scales to fit nicely on the drawing sheet. If there are no views on the sheet, the sheet scale is changed to the appropriate scale, and the view created uses the sheet scale.

If a model document  is currently open in SOLIDWORKS and you don't know its full pathname, call [[IModelDoc2::GetPathName]] to populate ModelName. Include the **.sldprt** or **.sldasm** extension in the pathname.

ViewName must exactly match the name of the model view. For example, the names of the standard views begin with an asterisk. This asterisk is part of the view name and must be included (for example, "*Front").

## Examples
- Insert Model Annotations (C#)
- Insert Model Annotations (VB.NET)
- Insert Model Annotations (VBA)
