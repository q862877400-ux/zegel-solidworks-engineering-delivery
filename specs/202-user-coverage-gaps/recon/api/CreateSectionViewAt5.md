# CreateSectionViewAt5
- 官方路径: C:\swapi\types\IDrawingDoc\CreateSectionViewAt5.md
- Signature: `View CreateSectionViewAt5( System.double X, System.double Y, System.double Z, System.string SectionLabel, System.int Options, System.object ExcludedComponents, System.double SectionDepth )`
- 指针族: —
- 本仓现状: scripts/sw_api_sldworks.py:3557 · scripts/sw_api_sldworks.py:20434（mcp-server/ 下无命中）
## Remarks（逐字）
## Remarks
Before calling this method, select the section line or lines to use as a section line.

This method runs silently; the end-user is not prompted for a label.

Use [[IView::GetSection]] to get the [[IDrSection]] object, and use [[IDrSection::SetLabel2]] to set the name for the label, which provides a warning if the name is a duplicate and the standard does not accept duplicate names.

## Examples
- Create_Section_View_and_Get_Some_Data_Example_VB.md
- Create_Section_View_and_Get_Some_Data_Example_VBNET.md
- Create_Section_View_and_Get_Some_Data_Example_CSharp.md
