# InsertNote
- 官方路径: `C:\swapi\types\IModelDoc2\InsertNote.md`（接口目录名 `IModelDoc2`；递归搜索 `C:\swapi\types\**\InsertNote.md` 共命中 1 份）
- Signature: `System.object InsertNote( System.string Text )`
- 指针族: — （该文件全文无 `AccessSelections`）
- 本仓现状: `D:\AI\SW\scripts\sw_api_sldworks.py:5699` · `D:\AI\SW\scripts\sw_api_sldworks.py:6316` · `D:\AI\SW\scripts\sw_api_sldworks.py:22436` · `D:\AI\SW\scripts\sw_api_sldworks.py:23053`；`D:\AI\SW\mcp-server\` 下无命中

## Remarks（逐字）
If you use a symbol in Text, it must be formatted as:

<*LibraryName-SymbolName*>

where *LibraryName* and *SymbolName* are in the SOLIDWORKS text file **C:\ProgramData\SolidWorks\SolidWorks 20***nn*\**lang**\**english\gtol.sym****.**

**NOTE**: You must include the right- and left-angle brackets and separate *LibraryName* and *SymbolName* with a hyphen; for example, .

The leader attachment points for the new note come from the selections made before calling this method. The initial location of the note will be near the selection location. If there are no selections, the note:

- Does not have a leader

- Is free standing

- Is at the origin of the model or drawing

This method creates a default note. To adjust the display characteristics of this note, you should use the pointer that is returned by this method to access the properties and get and set methods of the Note object, such as [[INote::SetBalloon]], [[INote::Angle]], and [[INote::LockPosition]]. Use [[INote::GetAnnotation]] or [[INote::IGetAnnotation]] to retrieve the [[IAnnotation]] object.

## Examples
- [Insert Note (VBA)](../../examples/Insert_a_Note_Example_VB.md)
- [Create Block Definition and Insert Block Instance (VBA)](../../examples/Create_Block_Definition_and_Insert_Block_Instance_Example_VB.md)
- [Create Block Definition and Insert Block Instance (C#)](../../examples/Create_Block_Definition_and_Insert_Block_Instance_Example_CSharp.md)
- [Create Block Definition and Insert Block Instance (VB.NET)](../../examples/Create_Block_Definition_and_Insert_Block_Instance_Example_VBNET.md)