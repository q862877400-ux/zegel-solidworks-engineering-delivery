# 焊件/焊接符号（weld_symbol）

候选成员名：`InsertWeldSymbol` / `IWeldSymbol`（线索，非答案）。

递归搜索 `C:\swapi\types\**\*WeldSymbol*.md`，**共命中 5 份成员页 + 1 份接口总览页**，全部逐字抄录如下（同名多接口，每份都抄）：

| # | 官方路径 | 成员 | 判为废弃？ |
|---|---|---|---|
| 1 | `C:\swapi\types\IDrawingDoc\InsertWeldSymbol.md` | `IDrawingDoc.InsertWeldSymbol` | 否（页内无 Obsolete 句） |
| 2 | `C:\swapi\types\IModelDoc2\InsertWeldSymbol2.md` | `IModelDoc2.InsertWeldSymbol2` | **是**（Obsolete → `InsertWeldSymbol3`） |
| 3 | `C:\swapi\types\IModelDoc2\InsertWeldSymbol3.md` | `IModelDoc2.InsertWeldSymbol3` | 否（后继，不再废弃） |
| 4 | `C:\swapi\types\IModelDoc2\IInsertWeldSymbol3.md` | `IModelDoc2.IInsertWeldSymbol3`（指针变体） | 否 |
| 5 | `C:\swapi\types\ICosmeticWeldBeadFeatureData\WeldSymbol.md` | `ICosmeticWeldBeadFeatureData.WeldSymbol`（属性，同名） | 否（页内无 Obsolete 句） |
| 6 | `C:\swapi\types\IWeldSymbol\_overview.md` | 接口 `IWeldSymbol` 总览（0 属性 / 45 方法） | — |

★ 废弃链只有一条，逐级追到不再废弃：
`IModelDoc2.InsertWeldSymbol2`（Obsolete）→ **`IModelDoc2.InsertWeldSymbol3`**（不再废弃）→ 终止。
另有 `IDrawingDoc.InsertWeldSymbol` 一条**独立**的旧式入口，官方页**未**把它标为 Obsolete，也**未**指向 `InsertWeldSymbol3` ⇒ 不构成链的一环（据实记录，不推断）。

---

## 页头逐字段（逐字）

### 1. `C:\swapi\types\IDrawingDoc\InsertWeldSymbol.md`（第 1–14 行原文）

```
---
type: IDrawingDoc
member: InsertWeldSymbol
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IDrawingDoc.InsertWeldSymbol

Creates a weld symbol located at the last edge selection.

**Signature**: `void InsertWeldSymbol( System.string Dim1, System.string Symbol, System.string Dim2, System.bool Symmetric, System.bool FieldWeld, System.bool ShowOtherSide, System.bool DashOnTop, System.bool Peripheral, System.bool HasProcess, System.string ProcessValue )`
```

### 2. `C:\swapi\types\IModelDoc2\InsertWeldSymbol2.md`（第 1–14 行原文）

```
---
type: IModelDoc2
member: InsertWeldSymbol2
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IModelDoc2.InsertWeldSymbol2

Obsolete. Superseded by [[IModelDoc2::InsertWeldSymbol3]].

**Signature**: `void InsertWeldSymbol2( System.string Dim1, System.string Symbol, System.string Dim2, System.bool Symmetric, System.bool FieldWeld, System.bool ShowOtherSide, System.bool DashOnTop, System.bool Peripheral, System.bool HasProcess, System.string ProcessValue )`
```

### 3. `C:\swapi\types\IModelDoc2\InsertWeldSymbol3.md`（第 1–14 行原文）

```
---
type: IModelDoc2
member: InsertWeldSymbol3
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IModelDoc2.InsertWeldSymbol3

Inserts a weld symbol into the model.

**Signature**: `System.object InsertWeldSymbol3()`
```

### 4. `C:\swapi\types\IModelDoc2\IInsertWeldSymbol3.md`（第 1–14 行原文）

```
---
type: IModelDoc2
member: IInsertWeldSymbol3
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IModelDoc2.IInsertWeldSymbol3

Inserts a weld symbol into the model.

**Signature**: `WeldSymbol IInsertWeldSymbol3()`
```

### 5. `C:\swapi\types\ICosmeticWeldBeadFeatureData\WeldSymbol.md`（第 1–14 行原文）

```
---
type: ICosmeticWeldBeadFeatureData
member: WeldSymbol
kind: property
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Others
---

# ICosmeticWeldBeadFeatureData.WeldSymbol

Gets or sets the weld symbol for this weld bead.

**Signature**: `System.object WeldSymbol {get; set;}`
```

### 6. `C:\swapi\types\IWeldSymbol\_overview.md`（第 1–15 行原文）

```
---
name: IWeldSymbol
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Annotation Interfaces/Table Annotations
is_enum: False
property_count: 0
method_count: 45
enum_member_count: 0
---

# IWeldSymbol

## Description
Allows access to weld symbols.
```

---

## Signature（逐字）

- `C:\swapi\types\IDrawingDoc\InsertWeldSymbol.md`
  `void InsertWeldSymbol( System.string Dim1, System.string Symbol, System.string Dim2, System.bool Symmetric, System.bool FieldWeld, System.bool ShowOtherSide, System.bool DashOnTop, System.bool Peripheral, System.bool HasProcess, System.string ProcessValue )`
- `C:\swapi\types\IModelDoc2\InsertWeldSymbol2.md`
  `void InsertWeldSymbol2( System.string Dim1, System.string Symbol, System.string Dim2, System.bool Symmetric, System.bool FieldWeld, System.bool ShowOtherSide, System.bool DashOnTop, System.bool Peripheral, System.bool HasProcess, System.string ProcessValue )`
- `C:\swapi\types\IModelDoc2\InsertWeldSymbol3.md`
  `System.object InsertWeldSymbol3()`
- `C:\swapi\types\IModelDoc2\IInsertWeldSymbol3.md`
  `WeldSymbol IInsertWeldSymbol3()`
- `C:\swapi\types\ICosmeticWeldBeadFeatureData\WeldSymbol.md`
  `System.object WeldSymbol {get; set;}`

★ 后继页 Signature 逐字（追废弃链用）：`IModelDoc2.InsertWeldSymbol3` = `System.object InsertWeldSymbol3()`；其指针变体 `IModelDoc2.IInsertWeldSymbol3` = `WeldSymbol IInsertWeldSymbol3()`。链到此终止，不再废弃。

- Obsolete:
  - `IDrawingDoc.InsertWeldSymbol`：**无**
  - `IModelDoc2.InsertWeldSymbol2`：`Obsolete. Superseded by [[IModelDoc2::InsertWeldSymbol3]].`
  - `IModelDoc2.InsertWeldSymbol3`：**无**
  - `IModelDoc2.IInsertWeldSymbol3`：**无**
  - `ICosmeticWeldBeadFeatureData.WeldSymbol`：**无**
  - `IWeldSymbol`（接口总览）：**无**

---

## Remarks（逐字，或「本页无 ## Remarks 段」）

### `C:\swapi\types\IDrawingDoc\InsertWeldSymbol.md` —— **有 `## Remarks` 标题**，全文逐字：

```
Symbol specifies the weld symbol name. You can find a list of weld symbol names in **C:\ProgramData\SolidWorks\SolidWorks 20***nn*\**lang**\**english\gtol.sym**.

The format of Symbol is **<**Standard**-**Type**>**. For example, a JIS seam is , and an ISO seam is . You must include the right- and left-angle brackets and separate Standard and Type with a hyphen.
```

### `C:\swapi\types\IModelDoc2\InsertWeldSymbol2.md` —— **本页无 `## Remarks` 段**

（该页只有 `## Parameters` 与 `## See Also`。`## Parameters` 里 `- **Symbol**: See **Remarks**.` 这句指向的 Remarks **本页并不存在** ⇒ 按标题判定，如实写「本页无 `## Remarks` 段」。）

### `C:\swapi\types\IModelDoc2\InsertWeldSymbol3.md` —— **有 `## Remarks` 标题**，全文逐字：

```
To use this method, insert the weld symbol into the model and then manipulate the properties and methods on the [[IWeldSymbol]] object.

A list of weld symbol names can be found in **C:\ProgramData\SolidWorks\SolidWorks 20***nn*\**lang**\**english\gtol.sym****.** The currently supported list of ISO weld symbols is:

- BUTT

- BUSQ

- BUSV

- BUSB

- BUSVBR

- BUSBR

- BUSU

- BUSJ

- BACK

- FILL

- PLUG

- SPOT

- SEAM

- SEAMC

- JSPT

- JSM
```

### `C:\swapi\types\IModelDoc2\IInsertWeldSymbol3.md` —— **有 `## Remarks` 标题**，全文逐字：

```
To use this method, insert the weld symbol into the model and then manipulate the properties and methods on the [[IWeldSymbol]] object.

A list of weld symbol names can be found in **C:\ProgramData\SolidWorks\SolidWorks 20***nn*\**lang**\**english\gtol.sym****.** The currently supported list of ISO weld symbols is:

- BUTT

- BUSQ

- BUSV

- BUSB

- BUSVBR

- BUSBR

- BUSU

- BUSJ

- BACK

- FILL

- PLUG

- SPOT

- SEAM

- SEAMC

- JSPT

- JSM
```

### `C:\swapi\types\ICosmeticWeldBeadFeatureData\WeldSymbol.md` —— **本页无 `## Remarks` 段**

（只有 `## Returns` 与 `## See Also`。）

### `C:\swapi\types\IWeldSymbol\_overview.md` —— **本页无 `## Remarks` 段**

（只有 `## Description` / `## Members` / `## Examples` / `## See Also`。）

---

## Examples

| 页 | `## Examples` 段列出的例子文件名 |
|---|---|
| `C:\swapi\types\IDrawingDoc\InsertWeldSymbol.md` | **无**（该页无 `## Examples` 段） |
| `C:\swapi\types\IModelDoc2\InsertWeldSymbol2.md` | **无**（该页无 `## Examples` 段） |
| `C:\swapi\types\IModelDoc2\InsertWeldSymbol3.md` | `Insert_Weld_Symbol_Example_VB.md` · `Insert_Weld_Symbol_Example_VBNET.md` · `Insert_Weld_Symbol_Example_CSharp.md` |
| `C:\swapi\types\IModelDoc2\IInsertWeldSymbol3.md` | **无**（该页无 `## Examples` 段） |
| `C:\swapi\types\ICosmeticWeldBeadFeatureData\WeldSymbol.md` | **无**（该页无 `## Examples` 段） |
| `C:\swapi\types\IWeldSymbol\_overview.md` | `Insert_Weld_Symbol_Example_VB.md` · `Insert_Weld_Symbol_Example_VBNET.md` · `Insert_Weld_Symbol_Example_CSharp.md` |

★ `InsertWeldSymbol3.md` 的 `## Examples` 段逐字：

```
- [Insert Weld Symbol Example (VBA)](../../examples/Insert_Weld_Symbol_Example_VB.md)
- [Insert Weld Symbol Example (VB.NET)](../../examples/Insert_Weld_Symbol_Example_VBNET.md)
- [Insert Weld Symbol Example (C#)](../../examples/Insert_Weld_Symbol_Example_CSharp.md)
```

三份文件**均已核实存在**（`C:\swapi\examples\` 下）：`Insert_Weld_Symbol_Example_VB.md` · `Insert_Weld_Symbol_Example_VBNET.md` · `Insert_Weld_Symbol_Example_CSharp.md`。

---

## 指针族 / 本仓现状

### 指针族（逐页全文搜 `AccessSelections`）

| 页 | `AccessSelections` |
|---|---|
| `C:\swapi\types\IDrawingDoc\InsertWeldSymbol.md` | — |
| `C:\swapi\types\IModelDoc2\InsertWeldSymbol2.md` | — |
| `C:\swapi\types\IModelDoc2\InsertWeldSymbol3.md` | — |
| `C:\swapi\types\IModelDoc2\IInsertWeldSymbol3.md` | — |
| `C:\swapi\types\ICosmeticWeldBeadFeatureData\WeldSymbol.md` | — |
| `C:\swapi\types\IWeldSymbol\_overview.md` | — |

⇒ **本组 6 份命中页全文均无 `AccessSelections` ⇒ 不是「⚠ 指针族」**。

★ 另记（不属本组成员页，仅作旁证）：同目录下的 `C:\swapi\types\ICosmeticWeldBeadFeatureData\AccessSelections.md` **存在**（签名 `System.bool AccessSelections( ModelDoc2 TopDoc, Component2 Component )`），它属于 `ICosmeticWeldBeadFeatureData` 这个** Cosmetic Weld Bead 特征数据接口**，**不是** `InsertWeldSymbol` / `IWeldSymbol` 的入口契约 ⇒ 未计入上表。

### 本仓现状（`D:\AI\SW\scripts\` 与 `D:\AI\SW\mcp-server\`，搜 `InsertWeldSymbol|IWeldSymbol|WeldSymbol`）

**`D:\AI\SW\mcp-server\`：0 命中。**

**`D:\AI\SW\scripts\`：25 处命中，逐项判读 ——**

| 文件:行 | 命中内容 | 判定 |
|---|---|---|
| `scripts\sw_api_sldworks.py:576` | `'IWeldSymbol',` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:3654` | `'InsertWeldSymbol': 10,` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:5739` | `'InsertWeldSymbol2': 10,` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:5740` | `'InsertWeldSymbol3': 0,` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:6367` | `'InsertWeldSymbol2': 10,` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:6368` | `'InsertWeldSymbol3': 0,` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:9594` | `'GetFirstWeldSymbol': 0,` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:9681` | `'GetWeldSymbolCount': 0,` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:9682` | `'GetWeldSymbols': 0,` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:9754` | `'IWeldSymbol': {` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:11118` | `'WeldSymbol',` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:11119` | `'WeldSymbol',` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:17191` | `'IWeldSymbol': (` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:20531` | `'InsertWeldSymbol': 67,` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:22476` | `'InsertWeldSymbol2': 65943,` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:22477` | `'InsertWeldSymbol3': 66220,` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:23104` | `'InsertWeldSymbol2': 65943,` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:23105` | `'InsertWeldSymbol3': 66220,` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:26261` | `'GetFirstWeldSymbol': 71,` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:26348` | `'GetWeldSymbolCount': 361,` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:26349` | `'GetWeldSymbols': 362,` | **（仅反射索引，不算实现）** |
| `scripts\sw_api_sldworks.py:26421` | `'IWeldSymbol': {` | **（仅反射索引，不算实现）** |
| `scripts\sw_drawing_view.py:199` | `'GetFirstWeldSymbol': 0,` | 真实文件，但命中的是 **`IView.GetFirstWeldSymbol`**（读工程图视图上已有焊接符号），**不是** `InsertWeldSymbol` / `IWeldSymbol` ⇒ 不算本功能项实现 |
| `scripts\sw_drawing_view.py:263` | `'GetWeldSymbolCount': 0,` | 同上（`IView.GetWeldSymbolCount`，非本功能项） |
| `scripts\sw_drawing_view.py:264` | `'GetWeldSymbols': 0,` | 同上（`IView.GetWeldSymbols`，非本功能项） |

⇒ **本仓现状结论（据实）**：
- 按死规矩排除 `scripts/sw_api_*.py`（生成的反射索引）后，**`scripts\` 与 `mcp-server\` 里对 `InsertWeldSymbol` / `InsertWeldSymbol2` / `InsertWeldSymbol3` / `IInsertWeldSymbol3` / `IWeldSymbol` / `ICosmeticWeldBeadFeatureData.WeldSymbol` 的调用实现 = 0 处** ⇒ **本仓无实现**。
- 唯一真实代码命中在 `scripts/sw_drawing_view.py`，但那是 `IView` 的三个**读取型**方法（`GetFirstWeldSymbol` / `GetWeldSymbolCount` / `GetWeldSymbols`）出现在一个名字映射字典里，**与「插入焊接符号」这一功能项不是同一成员** ⇒ 不计入本功能项。

---

## 拿不准 / 未验证项（如实标注，不推断）

1. `IDrawingDoc.InsertWeldSymbol` 与 `IModelDoc2.InsertWeldSymbol3` 是**两条不同的入口**（一个 11 参无返回、一个 0 参返回对象），官方页**均未**说明二者关系，也未标前者为 Obsolete ⇒ **是否该优先用哪一条，官方没写**。
2. `IDrawingDoc.InsertWeldSymbol` 的 Remarks 里 `a JIS seam is , and an ISO seam is .` 两处示例值为空（官方 md 里就是空的）⇒ 官方没写实际取值。
3. `IModelDoc2.InsertWeldSymbol2` 的 `## Parameters` 写 `- **Symbol**: See **Remarks**.`，但**该页无 `## Remarks` 段** ⇒ 被引用的内容官方没写在本页。
4. `IModelDoc2.InsertWeldSymbol3()` 的 Signature 写 `System.object`（后继页），而其指针变体 `IModelDoc2.IInsertWeldSymbol3()` 写 `WeldSymbol` ⇒ **两者返回类型标注不一致，官方未解释**，据实并列抄录。
5. `IWeldSymbol` 接口 45 个成员里含 `GetFieldWeld` / `SetFieldWeld` / `SetSymmetric` / `SetPeripheral` / `SetProcess` / `SetStagger` / `SetText` 等，**本次未逐页抄录**（不在候选成员名 `InsertWeldSymbol` / `IWeldSymbol` 之内；`IWeldSymbol` 是接口不是成员）。