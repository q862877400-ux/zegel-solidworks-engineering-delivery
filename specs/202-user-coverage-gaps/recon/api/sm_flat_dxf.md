# 钣金/平板型式导出DXF（sm_flat_dxf）

> 纯抄录。凡官方没写的写「官方没写」，不补全、不推测。

## 页头逐字段（逐字）

★ 命中 **3 份**（候选名逐个命中，无需换英文关键词）：
`C:\swapi\types\IPartDoc\ExportFlatPatternView.md` · `C:\swapi\types\IPartDoc\ExportToDWG.md` · `C:\swapi\types\IPartDoc\ExportToDWG2.md`

---

### 命中① `C:\swapi\types\IPartDoc\ExportFlatPatternView.md` —— 页头至 Signature 行（逐字）

```text
---
type: IPartDoc
member: ExportFlatPatternView
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IPartDoc.ExportFlatPatternView

Obsolete. Superseded by [[IPartDoc::ExportToDWG2]].

**Signature**: `System.bool ExportFlatPatternView( System.string FilePath, System.int Options )`
```

### 命中② `C:\swapi\types\IPartDoc\ExportToDWG.md` —— 页头至 Signature 行（逐字）

```text
---
type: IPartDoc
member: ExportToDWG
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IPartDoc.ExportToDWG

Obsolete. Superseded by [[IPartDoc::ExportToDWG2]].

**Signature**: `System.bool ExportToDWG( System.string FilePath, System.string ModelName, System.int Action, System.bool ExportToSingleFile, System.object Alignment, System.bool IsXDirFlipped, System.bool IsYDirFlipped, System.int SheetMetalOptions, System.object Views )`
```

### 命中③ `C:\swapi\types\IPartDoc\ExportToDWG2.md` —— 页头至 Signature 行（逐字）

```text
---
type: IPartDoc
member: ExportToDWG2
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IPartDoc.ExportToDWG2

Saves various aspects of a part (sheet metal, faces, loops, and annotation views) to one or more DXF/DWG files, preserving the specified file name.

**Signature**: `System.bool ExportToDWG2( System.string FilePath, System.string ModelName, System.int Action, System.bool ExportToSingleFile, System.object Alignment, System.bool IsXDirFlipped, System.bool IsYDirFlipped, System.int SheetMetalOptions, System.object Views )`
```

---

## Signature（逐字）

- `ExportFlatPatternView`：`System.bool ExportFlatPatternView( System.string FilePath, System.int Options )`
- `ExportToDWG`：`System.bool ExportToDWG( System.string FilePath, System.string ModelName, System.int Action, System.bool ExportToSingleFile, System.object Alignment, System.bool IsXDirFlipped, System.bool IsYDirFlipped, System.int SheetMetalOptions, System.object Views )`
- `ExportToDWG2`：`System.bool ExportToDWG2( System.string FilePath, System.string ModelName, System.int Action, System.bool ExportToSingleFile, System.object Alignment, System.bool IsXDirFlipped, System.bool IsYDirFlipped, System.int SheetMetalOptions, System.object Views )`

### 后继链（逐级追到不再废弃）

1. `IPartDoc.ExportFlatPatternView` —— **Obsolete** ⇒ 后继 `IPartDoc.ExportToDWG2` ⇒ 其页**无** Obsolete 句（链止）。
   - 后继页 `ExportToDWG2` 的 Signature 逐字（同上第三条）：
     `System.bool ExportToDWG2( System.string FilePath, System.string ModelName, System.int Action, System.bool ExportToSingleFile, System.object Alignment, System.bool IsXDirFlipped, System.bool IsYDirFlipped, System.int SheetMetalOptions, System.object Views )`
2. `IPartDoc.ExportToDWG` —— **Obsolete** ⇒ 后继 `IPartDoc.ExportToDWG2` ⇒ 其页**无** Obsolete 句（链止）。
   - 后继页 `ExportToDWG2` 的 Signature 逐字：同上。

### Obsolete（逐字重抄）

- `ExportFlatPatternView`：**`Obsolete. Superseded by [[IPartDoc::ExportToDWG2]].`**
- `ExportToDWG`：**`Obsolete. Superseded by [[IPartDoc::ExportToDWG2]].`**
- `ExportToDWG2`：**无**（该页无 Obsolete 句）

---

## Remarks（逐字，或「本页无 ## Remarks 段」）

### `ExportFlatPatternView`（有 `## Remarks` 标题）—— 全段逐字

```text
## Remarks
Call this method before calling [[IModelDocExtension::SaveAs]].
```

### `ExportToDWG`

**本页无 ## Remarks 段**（该页 `## Returns` 之后直接是 `## See Also`）。

### `ExportToDWG2`（有 `## Remarks` 标题）—— 全段逐字

```text
## Remarks
This method supersedes IPartDoc::IExportToDWG by:

- Adding an option to SheetMetalOptions to export a sheet metal bounding box.

- Not pre-pending the flat-pattern name to the FilePath file name of the exported DXF/DWG when ExportToSingleFile is false.

Alignment array is as follows:

Array[0], Array[1], Array[2] - x,y,z coordinates of new origin

Array[3], Array[4], Array[5] - coordinates of new x direction vector

Array[6], Array[7], Array[8] - coordinates of new y direction vector

Array[9], Array[10], Array[11] - coordinates of the vector that is normal to the selected faces or loops

NOTE:

- Passing an array of 12 zeros results in a default orientation being used. This is equivalent to not selecting any edges to be used for axis alignment in the user interface.

- Sheet-metal part exports are automatically constrained to align the flat-pattern normal to the 2D sheet normal, thereby limiting the degrees of freedom available to the API caller.

- The last three elements of the array are valid only if Action = swExportToDWG_e.swExportToDW_ExportSelectedFacesOrLoops.

SheetMetalOptions bitmask is {14 13 12 11 10 9 8 7 6 5 4 3 2 1}, where each bit is either 0 or 1 as follows:

Bit #1: 1 to export flat-pattern geometry; 0 to not

Bit #2: 1 to include hidden edges; 0 to not

Bit #3: 1 to export bend lines; 0 to not

Bit #4: 1 to include sketches; 0 to not

Bit #5: 1 to merge coplanar faces; 0 to not

Bit #6: 1 to export library features; 0 to not

Bit #7: 1 to export forming tools; 0 to not

Bit #8: 0

Bit #9: 0

Bit #10: 0

Bit #11: 0

Bit #12: 1 to export bounding box; 0 to not

Bit #13: 1 to export cosmetic threads; 0 to not

Bit #14: 1 to export hidden sketches; 0 to not

For example, if you want to export:

- flat-pattern geometry, bend lines, and sketches, then Bits 1, 3, and 4 are 1, the bitmask is 0001101, and you need to set SheetMetalOptions = 2^0 + 2^2 + 2^3 = 1 + 4 + 8 = 13.

- only the bounding box, then Bit 12 is 1, the bitmask is 100000000000, and you need to set SheetMetalOptions = 2^11 = 2048.

You must select multi-body sheet-metal features (i.e., multiple flat-pattern features) before calling this method.
```

---

## Examples

- `ExportFlatPatternView`：**无**（该页无 `## Examples` 段）
- `ExportToDWG`：**无**（该页无 `## Examples` 段）
- `ExportToDWG2`：3 个，文件名逐字如下
  - `Export_Part_To_DWG_Example_VB.md` —— 原文行：`- [Export Part to DWG (VBA)](../../examples/Export_Part_To_DWG_Example_VB.md)`
  - `Export_Part_To_DWG_Example_VBNET.md` —— 原文行：`- [Export Part to DWG (VB.NET)](../../examples/Export_Part_To_DWG_Example_VBNET.md)`
  - `Export_Part_To_DWG_Example_CSharp.md` —— 原文行：`- [Export Part to DWG (C#)](../../examples/Export_Part_To_DWG_Example_CSharp.md)`

---

## 指针族 / 本仓现状

### 指针族

- 对 `C:\swapi\types\IPartDoc\` 目录全文搜 `AccessSelections`：**0 命中** ⇒ **—**（无指针族标记）。
- ⚠ 附注（不是指针族判据，只是页内逐字事实）：`IExportToDWG2` 页的 `## Parameters` 里，`Alignment` 与 `Views` 两项分别写着
  `- In-process, unmanaged C++: Pointer to an array of …` 与 `See [In-process Methods](<../../docs/Programming with the SOLIDWORKS API/In-process Methods.md>)`。该页不在候选名单内，仅作记录，见下节。

### 本仓现状（`D:\AI\SW\scripts\` 与 `D:\AI\SW\mcp-server\`）

搜的是候选成员名 `ExportFlatPatternView` / `ExportToDWG`。

**★ 真实现实现在 `scripts/sw_export.py`：**

| 位置 | 内容（逐字摘） |
|---|---|
| `D:\AI\SW\scripts\sw_export.py:136` | `"""@brief 创建 ``ExportToDWG2`` 要求的 12 个双精度对齐参数。"""` |
| `D:\AI\SW\scripts\sw_export.py:191` | `return bool(model.ExportToDWG2(` |
| `D:\AI\SW\scripts\sw_export.py:743` | `#   `IModelDoc2.ExportToDWG2(..., swExportToDWG_e)`（★ `export_flat_pattern_dxf` 走它）` |

⇒ 本仓走的是 **`ExportToDWG2`**（非废弃那一支）；`ExportFlatPatternView` 与 `ExportToDWG` 在 `scripts\` / `mcp-server\` 的**非反射文件**里 **0 命中**。

**★ 反射索引命中（不算实现）：** `D:\AI\SW\scripts\sw_api_sldworks.py`
- 行 7312–7314：`'ExportFlatPatternView': 2,` / `'ExportToDWG': 9,` / `'ExportToDWG2': 9,`
- 行 24039–24041：`'ExportFlatPatternView': 150,` / `'ExportToDWG': 155,` / `'ExportToDWG2': 159,`
⇒ **（仅反射索引，不算实现）**。

**`mcp-server\`：** 候选成员名 `ExportFlatPatternView` / `ExportToDWG` **0 命中**；仅 `D:\AI\SW\mcp-server\tool_specs_batch59.py:15` 有一条注释提到 `export_flat_pattern_dxf`（**非成员名命中、且是注释，不是实现**）。

---

## 附：See Also 指向的 `I` 前缀变体（★ 候选名单外，仅逐字记录，不替代上三条）

★ 这两份**不在**候选成员名里，是 `ExportToDWG` / `ExportToDWG2` 两页 `## See Also` 指向的同名变体页。

### `C:\swapi\types\IPartDoc\IExportToDWG.md` —— 页头至 Signature 行（逐字）

```text
---
type: IPartDoc
member: IExportToDWG
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IPartDoc.IExportToDWG

Obsolete. Superseded by [[IPartDoc::IExportToDWG2]].

**Signature**: `System.bool IExportToDWG( System.string FilePath, System.string ModelName, System.int Action, System.bool ExportToSingleFile, ref System.double Alignment, System.bool IsXDirFlipped, System.bool IsYDirFlipped, System.int SheetMetalOptions, System.int ViewsCount, ref System.string Views )`
```

- Obsolete（逐字重抄）：**`Obsolete. Superseded by [[IPartDoc::IExportToDWG2]].`**
- 后继链：`IExportToDWG` → `IExportToDWG2`；后者页**无** Obsolete 句（链止）。
- Remarks：**本页无 ## Remarks 段**。
- Examples：**无**。

### `C:\swapi\types\IPartDoc\IExportToDWG2.md` —— 页头至 Signature 行（逐字）

```text
---
type: IPartDoc
member: IExportToDWG2
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IPartDoc.IExportToDWG2

Saves various aspects of a part (sheet metal, faces, loops, and annotation views) to one or more DXF/DWG files, preserving the specified filename.

**Signature**: `System.bool IExportToDWG2( System.string FilePath, System.string ModelName, System.int Action, System.bool ExportToSingleFile, ref System.double Alignment, System.bool IsXDirFlipped, System.bool IsYDirFlipped, System.int SheetMetalOptions, System.int ViewsCount, ref System.string Views )`
```

- Obsolete（逐字重抄）：**无**。
- Examples：**无**（该页无 `## Examples` 段）。
- Remarks：**有** `## Remarks` 段，全文见下（逐字）：

```text
## Remarks
This method supersedes IPartDoc::IExportToDWG by:

- Adding an option to SheetMetalOptions to export a sheet metal bounding box.

- Not prepending the flat-pattern name to the FilePath filename of the exported DXF/DWG when ExportToSingleFile is false.

Alignment array is as follows:

Array[0], Array[1], Array[2] - XYZ coordinates of new origin

Array[3], Array[4], Array[5] - coordinates of new x direction vector

Array[6], Array[7], Array[8] - coordinates of new y direction vector

Array[9], Array[10], Array[11] - coordinates of the vector that is normal to the selected faces or loops

          NOTE:

- Passing an array of 12 zeros results in a default orientation being used. This is equivalent to not selecting any edges to be used for axis alignment in the user interface.

- Sheet-metal part exports are automatically constrained to align the flat-pattern normal to the 2D sheet normal, thereby limiting the degrees of freedom available to the API caller.

- The last three elements of the array are valid only if Action = swExportToDWG_e.swExportToDW_ExportSelectedFacesOrLoops.

SheetMetalOptions bitmask is {12 11 10 9 8 7 6 5 4 3 2 1}, where each bit is either 0 or 1 as follows:

Bit #1: 1 to export flat-pattern geometry; 0 to not

Bit #2: 1 to include hidden edges; 0 to not

Bit #3: 1 to export bend lines; 0 to not

Bit #4: 1 to include sketches; 0 to not

Bit #5: 1 to merge coplanar faces; 0 to not

Bit #6: 1 to export library features; 0 to not

Bit #7: 1 to export forming tools; 0 to not

Bit #8: 0

Bit #9: 0

Bit #10: 0

Bit #11: 0

Bit #12: 1 to export bounding box; 0 to not

Examples:

If you want to export flat-pattern geometry, bend lines, and sketches, then Bits 1, 3, and 4 are 1, the bitmask is 0001101, and you need to set SheetMetalOptions = 2^0 + 2^2 + 2^3 = 1 + 4 + 8 = 13.

If you want to export only the bounding box, then Bit 12 is 1, the bitmask is 100000000000, and you need to set SheetMetalOptions = 2^11 = 2048.
```