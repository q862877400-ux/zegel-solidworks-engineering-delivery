# InsertRevisionTable2
- 官方路径: `C:\swapi\types\ISheet\InsertRevisionTable2.md`（接口目录名：`ISheet`）
- Signature: `RevisionTableAnnotation InsertRevisionTable2( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string TableTemplate, System.int Shape, System.bool AutoUpdateZoomCells )`
- 指针族: —
- 本仓现状: `scripts/sw_api_sldworks.py:8065`、`scripts/sw_api_sldworks.py:24768`（`mcp-server\` 无命中）
## Remarks（逐字）
By default, the revision table templates are in install_dir\**lang**\language and have a filename extension of **.sldrevtbt**. The template and table must be of the same type. For example, you must specify TableTemplate with *install_dir***\lang\English\standard revision block.sldrevtbt** if you want to insert the English version of a revision block table.

## Examples
- Create_Drawing_Sheet_Zones_Example_VB.md
- Create_Drawing_Sheet_Zones_Example_VBNET.md
- Create_Drawing_Sheet_Zones_Example_CSharp.md