# AutoBalloon5
- 官方路径: C:\swapi\types\IDrawingDoc\AutoBalloon5.md
- Signature: `System.object AutoBalloon5( AutoBalloonOptions BalloonOptions )`
- 指针族: —
- 本仓现状: `scripts/sw_api_sldworks.py:3499`、`scripts/sw_api_sldworks.py:20376`（`mcp-server/` 下无命中）

## 接口目录名
IDrawingDoc

## Remarks（逐字）
## Remarks
This method automatically inserts BOM balloons for bill of materials items in selected drawing views. If a drawing sheet is selected, BOM balloons are automatically inserted for all of the drawing views on that drawing sheet.

To automatically insert BOM balloons:

1. Select one or more views or sheets for which to automatically create BOM balloons.

2. Call [[IDrawingDoc::CreateAutoBalloonOptions]] to create an [[IAutoBalloonOptions]] object.

3. Set the properties on the IAutoBalloonOptions object.

4. Call this method using the IAutoBalloonOptions object in the BalloonOptions argument.

## Examples
Add_Autoballoon_to_Face_Example_VB.md
Add_Autoballoon_to_Face_Example_VBNET.md
Add_Autoballoon_to_Face_Example_CSharp.md
