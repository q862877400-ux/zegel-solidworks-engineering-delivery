# InsertBreak
- 官方路径: C:\swapi\types\IView\InsertBreak.md（接口目录名 `IView`；递归搜 `C:\swapi\types\` 下 `InsertBreak.md` 只此 1 份）
- Signature: **Signature**: `BreakLine InsertBreak( System.int Orientation, System.double Position1, System.double Position2, System.int Style )`
- 指针族: —（该文件全文无 `AccessSelections`）
- 本仓现状: D:\AI\SW\scripts\sw_drawing_view.py:273（`'InsertBreak3': 6,`）；D:\AI\SW\scripts\sw_api_sldworks.py:3618（`'InsertBreakHorizontal': 0,`）；D:\AI\SW\scripts\sw_api_sldworks.py:3619（`'InsertBreakVertical': 0,`）；D:\AI\SW\scripts\sw_api_sldworks.py:9696（`'InsertBreak': 4,`）；D:\AI\SW\scripts\sw_api_sldworks.py:9697（`'InsertBreak2': 5,`）；D:\AI\SW\scripts\sw_api_sldworks.py:9698（`'InsertBreak3': 6,`）；D:\AI\SW\scripts\sw_api_sldworks.py:20495（`'InsertBreakHorizontal': 74,`）；D:\AI\SW\scripts\sw_api_sldworks.py:20496（`'InsertBreakVertical': 81,`）；D:\AI\SW\scripts\sw_api_sldworks.py:26363（`'InsertBreak': 243,`）；D:\AI\SW\scripts\sw_api_sldworks.py:26364（`'InsertBreak2': 437,`）；D:\AI\SW\scripts\sw_api_sldworks.py:26365（`'InsertBreak3': 447,`）；mcp-server 目录：无
## Remarks（逐字）
## Remarks
A break in a drawing view consists of a pair of lines. This method inserts the break lines at the locations indicated by Position1 and Position2.

**If the orientation of the break is...**

**Then Position1 and Position2 are...**

Horizontal

Y values, relative to the drawing view origin, indicating where along the Y axis to place the breaks

Vertical

X values, relative to the drawing view origin, indicating where along the X axis to place the breaks

## Examples
无（该文件无 `## Examples` 段）