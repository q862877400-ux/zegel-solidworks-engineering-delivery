# InsertHoleTable2
- 官方路径: C:\swapi\types\IView\InsertHoleTable2.md
- Signature: `HoleTableAnnotation InsertHoleTable2( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string StartValue, System.string TableTemplate )`
- 指针族: —
- 本仓现状: scripts\sw_api_sldworks.py:9701 · scripts\sw_api_sldworks.py:26368 · mcp-server: 无

## Remarks（逐字）
This method inserts a table with the following information for selected holes:

- Datum tag

- X-location of hole center

- Y-location of hole center

- Size

This method displays datum tags next to holes that have been pre-selected in the view. The location of the datum tags is relative to a datum origin that is also pre-selected in the view.

Before calling this method, call [[IModelDocExtension::SelectByID2]] to select the datum origin, hole edges, and faces (for multiple holes) as follows:

**Selection**

**Mark**

Datum origin vertex
1

Hole edges and faces

2

Datum origin x axis direction reference

4

Datum origin y axis direction reference

8

Specify TableTemplate using a hole table template (***.sldholtbt**) in install_dir\**lang**\*language*.

Specify a TableTemplate and StartValue that matches the table you want to create. For example, to insert a hole table with letter tags, specify TableTemplate using *install_dir***\lang\English\standard hole table--letters.sldholtbt** and specify StartValue using a letter from A to Z.

## Examples
- Get_Labels_of_Datum_Origin_Example_CSharp.md
- Get_Labels_of_Datum_Origin_Example_VBNET.md
- Get_Labels_of_Datum_Origin_Example_VB.md