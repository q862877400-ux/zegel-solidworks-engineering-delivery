# 钣金/展开·折叠（sm_unfold）

> 纯抄录。四条候选线索里 **2 条命中**（`InsertSheetMetalUnfold` / `IFlatPatternFeatureData`），
> 2 条**官方没写**（`InsertFlatPattern` / `IUnfoldFeatureData`，见文末「没找到的」）。
> 命中页 **2 份**，逐页分块抄。

---

## 命中页 ①

- 文件：`C:\swapi\types\IModelDoc2\InsertSheetMetalUnfold.md`
- 命中线索：`InsertSheetMetalUnfold`

## 命中页 ②

- 文件：`C:\swapi\types\IFlatPatternFeatureData\_overview.md`
- 命中线索：`IFlatPatternFeatureData`（**接口总览页**，非成员页）

---

## 页头逐字段（逐字）

### 命中页 ① `IModelDoc2\InsertSheetMetalUnfold.md`

```markdown
---
type: IModelDoc2
member: InsertSheetMetalUnfold
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IModelDoc2.InsertSheetMetalUnfold

Inserts an unfold feature at the selected objects.

**Signature**: `void InsertSheetMetalUnfold()`
```

### 命中页 ② `IFlatPatternFeatureData\_overview.md`

（从 `---` 到 `## Description` 段止。★ **该页没有 `**Signature**:` 行** —— 它是接口总览页，
官方没在这页写签名。）

```markdown
---
name: IFlatPatternFeatureData
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Sheet Metal
is_enum: False
property_count: 13
method_count: 11
enum_member_count: 0
---

# IFlatPatternFeatureData

## Description
Allows access to a Flat-Pattern feature.
```

---

## Signature（逐字）

### 命中页 ① `IModelDoc2\InsertSheetMetalUnfold.md`

```markdown
**Signature**: `void InsertSheetMetalUnfold()`
```

- Obsolete: 无

### 命中页 ② `IFlatPatternFeatureData\_overview.md`

官方没写（★ 该页无 `**Signature**:` 行 —— 接口总览页只有 `property_count: 13` / `method_count: 11` 两个计数）。

- Obsolete: 无

### ★ 废弃链

命中页 ①② **均无 Obsolete 句** ⇒ 不需要追后继页，无废弃链。

（抄录时另行撞见、但**不属于四条候选名**、故不并入上面两页的一个事实：接口成员
`IFlatPatternFeatureData\IAccessSelections.md` 第 12 行逐字为
`Obsolete. Superseded by [[IFlatPatternFeatureData::IAccessSelections2]].`，
其 Signature 逐字为
`` `System.bool IAccessSelections( ModelDoc TopDoc, Component Component )` ``；
后继 `IAccessSelections2` 的 Signature 逐字为
`` `System.bool IAccessSelections2( ModelDoc2 TopDoc, Component2 Component )` ``。）

---

## Remarks（逐字，或「本页无 ## Remarks 段」）

### 命中页 ① `IModelDoc2\InsertSheetMetalUnfold.md`

★ **该页有 `## Remarks` 标题** ⇒ 以下为全文（逐字）：

```markdown
## Remarks
Select the objects for the unfold feature before calling this method.
```

### 命中页 ② `IFlatPatternFeatureData\_overview.md`

本页无 ## Remarks 段

---

## Examples

### 命中页 ① `IModelDoc2\InsertSheetMetalUnfold.md`

（★ 该页有 `## Examples` 段，逐字列出 **3** 个例子文件名：）

```markdown
## Examples
- [Insert and Access Fold Feature (C#)](../../examples/Insert_and_Access_Fold_Feature_Example_CSharp.md)
- [Insert and Access Fold Feature (VB.NET)](../../examples/Insert_and_Access_Fold_Feature_Example_VBNET.md)
- [Insert and Access Fold Feature (VBA)](../../examples/Insert_and_Access_Fold_Feature_Example_VB.md)
```

（三个文件均已核实存在于 `C:\swapi\examples\`。）

### 命中页 ② `IFlatPatternFeatureData\_overview.md`

（★ 该页有 `## Examples` 段，逐字列出 **4** 个例子文件名：）

```markdown
## Examples
- [Get Fixed Face of Flat-Pattern Feature (VBA)](../../examples/Get_Fixed_Face_of_Flat-Pattern_Feature_Example_VB.md)
- [Exclude Faces Before Flattening (VBA)](../../examples/Exclude_Faces_Before_Flattening_Example_VB.md)
- [Exclude Faces Before Flattening (VB.NET)](../../examples/Exclude_Faces_Before_Flattening_Example_VBNET.md)
- [Exclude Faces Before Flattening (C#)](../../examples/Exclude_Faces_Before_Flattening_Example_CSharp.md)
```

（四个文件均已核实存在于 `C:\swapi\examples\`。）

---

## 指针族 / 本仓现状

### 指针族（对命中页全文搜 `AccessSelections`）

| 命中页 | 该页正文是否出现 `AccessSelections` | 判定 |
|---|---|---|
| ① `IModelDoc2\InsertSheetMetalUnfold.md` | 无（0 命中） | **—** |
| ② `IFlatPatternFeatureData\_overview.md` | 无（0 命中） | **—** |

★ **但接口本身是指针族**：对 `C:\swapi\types\IFlatPatternFeatureData\` 整个目录搜 `AccessSelections`
**13 命中**，含三个成员页 —— `AccessSelections.md` / `IAccessSelections.md`（Obsolete）/
`IAccessSelections2.md`，且 `ReleaseSelectionAccess.md` 的 Remarks 反向引用它们。

| 文件 | `**Signature**:` 逐字 |
|---|---|
| `IFlatPatternFeatureData\AccessSelections.md` | ``System.bool AccessSelections( System.object TopDoc, System.object Component )`` |
| `IFlatPatternFeatureData\IAccessSelections.md` | ``System.bool IAccessSelections( ModelDoc TopDoc, Component Component )`` ← Obsolete |
| `IFlatPatternFeatureData\IAccessSelections2.md` | ``System.bool IAccessSelections2( ModelDoc2 TopDoc, Component2 Component )`` ← 后继 |

⇒ **⚠ 指针族（接口层）**。

### 本仓现状（在 `D:\AI\SW\scripts\` 与 `D:\AI\SW\mcp-server\` 搜这四个名字）

| 文件 | 命中内容 | 性质 |
|---|---|---|
| `scripts\sw_api_sldworks.py` | L256 `'IFlatPatternFeatureData',` · L4532 / L12360 / L21289 `'IFlatPatternFeatureData': {` / `(` · L5729 & L6351 `'InsertSheetMetalUnfold': 0,` · L22466 & L23088 `'InsertSheetMetalUnfold': 66175,` | **（仅反射索引，不算实现）** —— 该文件匹配 `scripts/sw_api_*.py`，是生成的反射索引，**不是实现** |
| `scripts\sw_capability_probe.py` | L68 `"sheet_metal": ("ISheetMetalFeatureData", "IFlatPatternFeatureData"),` | **仅字符串常量** —— 出现在 `CAPABILITY_KEYWORDS` 字典里，用于按接口名归类能力关键词；**没有任何 COM 调用指向该接口或 `InsertSheetMetalUnfold`**，不算入口实现 |
| `mcp-server\` | 0 命中 | — |

⇒ **结论：本仓无该入口的实现**（`sw_api_sldworks.py` 的命中已按要求排除；`sw_capability_probe.py`
只有一处关键词字面量，不构成实现）。

### 没找到的（两条候选线索，官方没写）

| 候选名 | 检索方式 | 结果 |
|---|---|---|
| `InsertFlatPattern` | 全 `C:\swapi\` 全文 grep `InsertFlatPattern` | **0 命中**（无同名文件、无正文提及）。改用英文关键词 `FlatPattern` 再找，命中的是 `IAnnotationView\FlatPatternView.md`、`IOneBendFeatureData\FlatPatternSketchSegment{,s,2}.md`、`IFlatPatternFeatureData\` 目录、`IFeatureManager\GetFlatPatternFolder.md` —— **都不是 `InsertFlatPattern`**，不许用相近名字代替 |
| `IUnfoldFeatureData` | 全 `C:\swapi\` 全文 grep `IUnfoldFeatureData`；目录 glob `**/IUnfoldFeatureData*/**` | **0 命中**（无目录、无正文提及）。改用英文关键词 `Unfold` 再找，命中的是 `IModelDoc2\InsertSheetMetalUnfold.md` 与 `IDrawingDoc\CreateUnfoldedViewAt{,2,3}.md` —— **都不是 `IUnfoldFeatureData`**，不许用相近名字代替 |

### 抄录时顺带撞见、但**不属于**四条候选线索的官方事实（仅登记，未抄录全文）

- `C:\swapi\enums\swFeatureNameID_e.md` L66 逐字：`| swFmFlatPattern | Flat pattern |`
- `C:\swapi\enums\swFeatureNameID_e.md` L145 逐字：`| swFmUnfoldedView | Unfolded view |`
  （★ 该枚举表的「Value」列装的是描述而非数值 —— **本次未核实**，故不给数值。）