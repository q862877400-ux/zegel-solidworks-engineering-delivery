# 焊件/裁剪·延伸焊件（weld_trim_extend）

候选成员名检索结果（`C:\swapi\types\` 递归）：

| 候选名 | 命中 |
|---|---|
| `IWeldmentTrimExtendFeatureData` | 有 —— 接口目录 `C:\swapi\types\IWeldmentTrimExtendFeatureData\`（`_overview.md` + 12 个成员页） |
| `InsertWeldmentTrimFeature` | 有 —— `C:\swapi\types\IFeatureManager\InsertWeldmentTrimFeature.md` |
| `InsertWeldmentTrimExtend` | **无** —— 全 `C:\swapi\types\*\*.md` 全文搜 `InsertWeldmentTrimExtend` **0 命中**。官方没写 |
| （追加检索）| `InsertWeldmentTrimFeature2` 有 —— `C:\swapi\types\IFeatureManager\InsertWeldmentTrimFeature2.md`；枚举页 `C:\swapi\enums\swWeldmentTrimExtendOptionType_e.md` |

英文回退关键词（Jog / Hem / Unfold / FlatPattern / EndCap / Gusset / Trim / WeldSymbol / MidSurface / Combine / Thicken）**未使用**——候选名已直接命中 3 项中的 2 项，且第 3 项经全文确认官方不存在。

命中页共 **14 份**（`IFeatureManager` 2 份 + `IWeldmentTrimExtendFeatureData` 12 份），全部逐字抄录如下。

---

## 页头逐字段（逐字）

### ① `C:\swapi\types\IFeatureManager\InsertWeldmentTrimFeature.md`

```
---
type: IFeatureManager
member: InsertWeldmentTrimFeature
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces
---

# IFeatureManager.InsertWeldmentTrimFeature

Inserts a weldment trim feature.

**Signature**: `Feature InsertWeldmentTrimFeature( System.int EndCond )`
```

### ② `C:\swapi\types\IFeatureManager\InsertWeldmentTrimFeature2.md`

```
---
type: IFeatureManager
member: InsertWeldmentTrimFeature2
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces
---

# IFeatureManager.InsertWeldmentTrimFeature2

Inserts a weldment trim feature for the specified weldment bodies or faces.

**Signature**: `Feature InsertWeldmentTrimFeature2( System.int EndCond, System.int Options, System.double GapValue, System.object BodiesToTrim, System.object BodiesOrFaces )`
```

### ③ `C:\swapi\types\IWeldmentTrimExtendFeatureData\_overview.md`

```
---
name: IWeldmentTrimExtendFeatureData
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Weldments
is_enum: False
property_count: 2
method_count: 10
enum_member_count: 0
---

# IWeldmentTrimExtendFeatureData

## Description
Allows access to the data that defines a weldment trim extend feature.
```

★ 该页**没有 `**Signature**:` 行**（接口页非成员页）——官方没写。

### ④ `C:\swapi\types\IWeldmentTrimExtendFeatureData\AccessSelections.md`

```
---
type: IWeldmentTrimExtendFeatureData
member: AccessSelections
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Weldments
---

# IWeldmentTrimExtendFeatureData.AccessSelections

Gains access to the selections that define this weldment trim extend feature.

**Signature**: `System.bool AccessSelections( ModelDoc2 PTopDoc, Component2 PComponent )`
```

### ⑤ `C:\swapi\types\IWeldmentTrimExtendFeatureData\BodiesToBeTrimmed.md`

```
---
type: IWeldmentTrimExtendFeatureData
member: BodiesToBeTrimmed
kind: property
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Weldments
---

# IWeldmentTrimExtendFeatureData.BodiesToBeTrimmed

Gets or sets the bodies to trim.

**Signature**: `System.object BodiesToBeTrimmed {get; set;}`
```

### ⑥ `C:\swapi\types\IWeldmentTrimExtendFeatureData\CornerType.md`

```
---
type: IWeldmentTrimExtendFeatureData
member: CornerType
kind: property
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Weldments
---

# IWeldmentTrimExtendFeatureData.CornerType

Gets or sets the corner type.

**Signature**: `System.int CornerType {get; set;}`
```

### ⑦ `C:\swapi\types\IWeldmentTrimExtendFeatureData\GetBodiesToBeTrimmedCount.md`

```
---
type: IWeldmentTrimExtendFeatureData
member: GetBodiesToBeTrimmedCount
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Weldments
---

# IWeldmentTrimExtendFeatureData.GetBodiesToBeTrimmedCount

Gets the number of bodies to trim.

**Signature**: `System.int GetBodiesToBeTrimmedCount()`
```

### ⑧ `C:\swapi\types\IWeldmentTrimExtendFeatureData\GetTrimmingBoundary.md`

```
---
type: IWeldmentTrimExtendFeatureData
member: GetTrimmingBoundary
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Weldments
---

# IWeldmentTrimExtendFeatureData.GetTrimmingBoundary

Gets the entities used to define the trimming boundaries.

**Signature**: `System.object GetTrimmingBoundary( out System.int Type )`
```

### ⑨ `C:\swapi\types\IWeldmentTrimExtendFeatureData\GetTrimmingBoundaryCount.md`

```
---
type: IWeldmentTrimExtendFeatureData
member: GetTrimmingBoundaryCount
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Weldments
---

# IWeldmentTrimExtendFeatureData.GetTrimmingBoundaryCount

Gets the number of trimming boundaries.

**Signature**: `System.int GetTrimmingBoundaryCount()`
```

### ⑩ `C:\swapi\types\IWeldmentTrimExtendFeatureData\IGetBodiesToBeTrimmed.md`

```
---
type: IWeldmentTrimExtendFeatureData
member: IGetBodiesToBeTrimmed
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Weldments
---

# IWeldmentTrimExtendFeatureData.IGetBodiesToBeTrimmed

Gets the bodies to trim.

**Signature**: `Body2 IGetBodiesToBeTrimmed( System.int Count )`
```

### ⑪ `C:\swapi\types\IWeldmentTrimExtendFeatureData\IGetTrimmingBoundary.md`

```
---
type: IWeldmentTrimExtendFeatureData
member: IGetTrimmingBoundary
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Weldments
---

# IWeldmentTrimExtendFeatureData.IGetTrimmingBoundary

Gets the entities used to define the trimming boundaries.

**Signature**: `System.object IGetTrimmingBoundary( System.int Count, out System.int Type )`
```

### ⑫ `C:\swapi\types\IWeldmentTrimExtendFeatureData\ISetBodiesToBeTrimmed.md`

```
---
type: IWeldmentTrimExtendFeatureData
member: ISetBodiesToBeTrimmed
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Weldments
---

# IWeldmentTrimExtendFeatureData.ISetBodiesToBeTrimmed

Sets the bodies to trim.

**Signature**: `void ISetBodiesToBeTrimmed( System.int Count, ref Body2 BodiesIn )`
```

### ⑬ `C:\swapi\types\IWeldmentTrimExtendFeatureData\ISetTrimmingBoundary.md`

```
---
type: IWeldmentTrimExtendFeatureData
member: ISetTrimmingBoundary
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Weldments
---

# IWeldmentTrimExtendFeatureData.ISetTrimmingBoundary

Gets the entities used to define the trimming boundaries.

**Signature**: `void ISetTrimmingBoundary( System.int Count, ref System.object TrimBoundArr )`
```

### ⑭ `C:\swapi\types\IWeldmentTrimExtendFeatureData\ReleaseSelectionAccess.md`

```
---
type: IWeldmentTrimExtendFeatureData
member: ReleaseSelectionAccess
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Weldments
---

# IWeldmentTrimExtendFeatureData.ReleaseSelectionAccess

Releases the selections that define this weldment trim extend feature.

**Signature**: `void ReleaseSelectionAccess()`
```

### ⑮ `C:\swapi\types\IWeldmentTrimExtendFeatureData\SetTrimmingBoundary.md`

```
---
type: IWeldmentTrimExtendFeatureData
member: SetTrimmingBoundary
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Weldments
---

# IWeldmentTrimExtendFeatureData.SetTrimmingBoundary

Sets the trimming boundaries for this weldment trim extend feature.

**Signature**: `void SetTrimmingBoundary( System.object TrimBoundVar )`
```

---

## Signature（逐字）

| 页 | 逐字 Signature |
|---|---|
| `IFeatureManager\InsertWeldmentTrimFeature.md` | **Signature**: `Feature InsertWeldmentTrimFeature( System.int EndCond )` |
| `IFeatureManager\InsertWeldmentTrimFeature2.md` | **Signature**: `Feature InsertWeldmentTrimFeature2( System.int EndCond, System.int Options, System.double GapValue, System.object BodiesToTrim, System.object BodiesOrFaces )` |
| `IWeldmentTrimExtendFeatureData\_overview.md` | 官方没写（接口页无 Signature 行） |
| `IWeldmentTrimExtendFeatureData\AccessSelections.md` | **Signature**: `System.bool AccessSelections( ModelDoc2 PTopDoc, Component2 PComponent )` |
| `IWeldmentTrimExtendFeatureData\BodiesToBeTrimmed.md` | **Signature**: `System.object BodiesToBeTrimmed {get; set;}` |
| `IWeldmentTrimExtendFeatureData\CornerType.md` | **Signature**: `System.int CornerType {get; set;}` |
| `IWeldmentTrimExtendFeatureData\GetBodiesToBeTrimmedCount.md` | **Signature**: `System.int GetBodiesToBeTrimmedCount()` |
| `IWeldmentTrimExtendFeatureData\GetTrimmingBoundary.md` | **Signature**: `System.object GetTrimmingBoundary( out System.int Type )` |
| `IWeldmentTrimExtendFeatureData\GetTrimmingBoundaryCount.md` | **Signature**: `System.int GetTrimmingBoundaryCount()` |
| `IWeldmentTrimExtendFeatureData\IGetBodiesToBeTrimmed.md` | **Signature**: `Body2 IGetBodiesToBeTrimmed( System.int Count )` |
| `IWeldmentTrimExtendFeatureData\IGetTrimmingBoundary.md` | **Signature**: `System.object IGetTrimmingBoundary( System.int Count, out System.int Type )` |
| `IWeldmentTrimExtendFeatureData\ISetBodiesToBeTrimmed.md` | **Signature**: `void ISetBodiesToBeTrimmed( System.int Count, ref Body2 BodiesIn )` |
| `IWeldmentTrimExtendFeatureData\ISetTrimmingBoundary.md` | **Signature**: `void ISetTrimmingBoundary( System.int Count, ref System.object TrimBoundArr )` |
| `IWeldmentTrimExtendFeatureData\ReleaseSelectionAccess.md` | **Signature**: `void ReleaseSelectionAccess()` |
| `IWeldmentTrimExtendFeatureData\SetTrimmingBoundary.md` | **Signature**: `void SetTrimmingBoundary( System.object TrimBoundVar )` |

### Obsolete

- Obsolete: 无（`InsertWeldmentTrimFeature.md`）—— 该页全文**没有** `Obsolete` / `Deprecated` 句。
- Obsolete: 无（`InsertWeldmentTrimFeature2.md`）
- Obsolete: 无（`IWeldmentTrimExtendFeatureData\_overview.md`）
- Obsolete: 无（`IWeldmentTrimExtendFeatureData\` 下 12 个成员页，逐页全文搜 `Obsolete|Deprecated` **0 命中**）

★ **14 份命中页全文 `Obsolete|Deprecated` 扫描 = 0 命中** ⇒ **无一判为废弃**，故不触发「追后继链」。

★ 但官方在两页的 `## See Also` 里给出了后继指针，逐字如下（非 Obsolete 判定，仅照录）：

`InsertWeldmentTrimFeature.md` 第 29–34 行：

```
## See Also

- [[IFeatureManager Interface]]
- [[IFeatureManager Members]]
- [[IWeldmentTrimExtendFeatureData Interface]]
- [[IFeatureManager::InsertWeldmentTrimFeature2 Method]]
```

`InsertWeldmentTrimFeature2.md` 第 42–47 行：

```
## See Also

- [[IFeatureManager Interface]]
- [[IFeatureManager Members]]
- [[IFeatureManager::InsertWeldmentTrimFeature Method]]
- [[IWeldmentTrimExtendFeatureData Interface]]
```

`_overview.md` 第 31–36 行：

```
## See Also

- [[IWeldmentTrimExtendFeatureData Members]]
- [[SolidWorks.Interop.sldworks Namespace]]
- [[IFeatureManager::InsertWeldmentTrimFeature2 Method]]
- [[IFeatureManager::InsertWeldmentTrimFeature Method]]
```

⇒ 后继链（官方 See Also 指向，**非** Obsolete 判定）：`InsertWeldmentTrimFeature` → `InsertWeldmentTrimFeature2`；链止于 `InsertWeldmentTrimFeature2`（该页无 Obsolete、无更高代 See Also）。

---

## Remarks（逐字）

> 判据：以「该页有没有 `## Remarks` 这个标题」为准。14 份命中页**全部**有 `## Remarks` 标题，故全部粘贴。

### ① `IFeatureManager\InsertWeldmentTrimFeature.md` 第 22–27 行

```
## Remarks
Use [[IModelDocExtension::SelectByID2]] and specify the following marks to select the body, or bodies, to trim and the trimming boundaries:

- 1 = Body or bodies to trim

- 2 = Trimming boundaries (body or face)
```

### ② `IFeatureManager\InsertWeldmentTrimFeature2.md` 第 26–35 行

```
## Remarks
Use [[IModelDocExtension::SelectByID2]] and specify the following marks to select the body, or bodies, to trim and the trimming boundaries:

- 1 = Body or bodies to trim

- 2 = Trimming boundaries (body or face)

If you include swWeldmentTrimExtendOption_WeldGap in the Options parameter, then the GapValue parameter is used. Specify 0 for GapValue to ensure that there is no weld gap.

If you exclude swWeldmentTrimExtendOption_WeldGap from the Options parameter, then the weld gap defaults to the last value specified in the SOLIDWORKS Design user-interface.
```

### ③ `IWeldmentTrimExtendFeatureData\_overview.md` 第 17–20 行

```
## Remarks
Only bodies created by weldment features can be trimmed and extended. Only End Trim corner types can have multiple target and boundary bodies to trim. All
other corner types can have only one target and boundary body to trim. For all other corner types, first valid body specified is used if more than one body is
specified.
```

### ④ `IWeldmentTrimExtendFeatureData\AccessSelections.md`

```
## Remarks
**To modify a feature in a...**
**Then...**

Part

- TopDoc argument is the [[IModelDoc2]] for the part

- Component argument is NULL

Assembly

- TopDoc is the IModelDoc2 object for the assembly

- Component argument is the [[IComponent2]] object in which the feature is to be modified

This method puts the model into a rollback state to allow access to the selections that define this feature. You must use either of the following methods to restore the rollback state:

- [[IFeature::ModifyDefinition]] or [[IFeature::IModifyDefinition2]] if you modified the feature

- [[IWeldmentTrimExtendFeatureData::ReleaseSelectionAccess]] if you did not
```

### ⑤ `IWeldmentTrimExtendFeatureData\BodiesToBeTrimmed.md`

```
## Remarks
Only end-trim corner types (swEndConditionTrim) can have multiple bodies to trim. Use [[IWeldmentTrimExtendFeatureData::CornerType]] to determine the type of corner.

You must set the bodies to trim and set the [[trimming boundary]] if changing a corner type.

See [Accessing Selections that Define Features](<../../docs/Programming with the SOLIDWORKS API/Selections that Define Features.md>) for additional details.
```

### ⑥ `IWeldmentTrimExtendFeatureData\CornerType.md`

```
## Remarks
You must set the bodies to trim and the trimming boundary when changing the corner type.

Valid values for type are:

- swEndConditionButt1

- swEndConditionButt2

- swEndConditionMiter

- swEndConditionTrim

These values are not valid for type:

- swEndConditionNone

- swEndConditionUseDefault

See [Accessing Selections that Define Features](<../../docs/Programming with the SOLIDWORKS API/Selections that Define Features.md>) for additional details.
```

### ⑦ `IWeldmentTrimExtendFeatureData\GetBodiesToBeTrimmedCount.md`

```
## Remarks
Only end-trim corner types (swEndConditionTrim) can have multiple bodies to trim. Use [[IWeldmentTrimExtendFeatureData::CornerType]] to determine the type of corner.

Call this method before calling [[IWeldmentTrimExtendFeatureData::IGetBodiesToBeTrimmed]] to get the size of the array for that method.
```

### ⑧ `IWeldmentTrimExtendFeatureData\GetTrimmingBoundary.md`

```
## Remarks
Only end-trim corner types (swEndConditionTrim) can have multiple boundaries. Use [[IWeldmentTrimExtendFeatureData::CornerType]] to determine the type of corner.
```

### ⑨ `IWeldmentTrimExtendFeatureData\GetTrimmingBoundaryCount.md`

```
## Remarks
Only end-trim corner types (swEndConditionTrim) can have multiple boundaries. Use [[IWeldmentTrimExtendFeatureData::CornerType]] to determine the type of corner.

Call this method before calling [[IWeldmentTrimExtendfeature::IGetTrimmingBoundary]]
```

### ⑩ `IWeldmentTrimExtendFeatureData\IGetBodiesToBeTrimmed.md`

```
## Remarks
Only end-trim corner types (swEndConditionTrim) can have multiple bodies to trim. Use [[IWeldmentTrimExtendFeatureData::CornerType]] to determine the type of corner.

Before calling this method, call [[IWeldmentTrimExtendFeatureData::GetBodiesToBeTrimmedCount]] to get Count.
```

### ⑪ `IWeldmentTrimExtendFeatureData\IGetTrimmingBoundary.md`

```
## Remarks
Only end-trim corner types (swEndConditionTrim) can have multiple boundaries. Use [[IWeldmentTrimExtendFeatureData::CornerType]] to determine the type of corner.

Before calling this method, call [[IWeldmentTrimExtendFeatureData::GetTrimmingBoundaryCount]] to get Count.
```

### ⑫ `IWeldmentTrimExtendFeatureData\ISetBodiesToBeTrimmed.md`

```
## Remarks
Only end-trim corner types (swEndConditionTrim) can have multiple bodies to trim. Use [[IWeldmentTrimExtendFeatureData::CornerType]] to determine the type of corner.

See [Accessing Selections that Define Features](<../../docs/Programming with the SOLIDWORKS API/Selections that Define Features.md>) for additional details.
```

### ⑬ `IWeldmentTrimExtendFeatureData\ISetTrimmingBoundary.md`

```
## Remarks
Faces are valid for end-trim corner types only. You can only specify multiple trimming boundaries for end-trim corner types. Use [[IWeldmentTrimExtendFeatureData::CornerType]] to determine the type of corner.

You must set the [[bodies to trim]] and set the trimming boundary if changing a corner type.

See [Accessing Selections that Define Features](<../../docs/Programming with the SOLIDWORKS API/Selections that Define Features.md>) for additional details.
```

### ⑭ `IWeldmentTrimExtendFeatureData\ReleaseSelectionAccess.md`

```
## Remarks
[[IWeldmentTrimExtendFeatureData::AccessSelections]] puts the model in a rollback state to allow access to the selections that define the feature.

Use this method to restore the rollback state if you did not modify the feature, or use [[IFeature::ModifyDefinition]] or [[IFeature::IModifyDefinition2]] if you did modify the feature.
```

### ⑮ `IWeldmentTrimExtendFeatureData\SetTrimmingBoundary.md`

```
## Remarks
Faces are valid for end-trim corner types only. You can only specify multiple trimming boundaries for end-trim corner types. Use [[IWeldmentTrimExtendFeatureData::CornerType]] to determine the type of corner.

You must set the [[bodies to trim]] and set the trimming boundary if changing a corner type.

See [Accessing Selections that Define Features](<../../docs/Programming with the SOLIDWORKS API/Selections that Define Features.md>) for additional details.
```

---

## Examples

逐页列出 `## Examples` 段里的例子文件名：

| 页 | 例子文件名 | 链接（逐字） |
|---|---|---|
| `IFeatureManager\InsertWeldmentTrimFeature.md` | 无（该页无 `## Examples` 段） | — |
| `IFeatureManager\InsertWeldmentTrimFeature2.md` | 3 个 | `- [Insert Weldment Features (VBA)](../../examples/Insert_Weldment_Features_Example_VB.md)`<br>`- [Insert Weldment Features (VB.NET)](../../examples/Insert_Weldment_Features_Example_VBNET.md)`<br>`- [Insert Weldment Features (C#)](../../examples/Insert_Weldment_Features_Example_CSharp.md)` |
| `IWeldmentTrimExtendFeatureData\_overview.md` | 3 个 | `- [Get Weldment Trim Extend Corner Type (VBA)](../../examples/Get_Weldment_Trim_Extend_Corner_Type_Example_VB.md)`<br>`- [Get Weldment Trim Extend Corner Type (VB.NET)](../../examples/Get_Weldment_Trim_Extend_Corner_Type_Example_VBNET.md)`<br>`- [Get Weldment Trim Extend Corner Type (C#)](../../examples/Get_Weldment_Trim_Extend_Corner_Type_Example_CSharp.md)` |
| `IWeldmentTrimExtendFeatureData\` 下 12 个成员页 | 无（12 页均无 `## Examples` 段） | — |

---

## 指针族 / 本仓现状

### 指针族（判据：14 份命中页全文搜 `AccessSelections`）

⚠ **指针族** —— 命中 2 页、4 处：

- `IWeldmentTrimExtendFeatureData\AccessSelections.md` 第 3 行（`member: AccessSelections`）
- `IWeldmentTrimExtendFeatureData\AccessSelections.md` 第 10 行（`# IWeldmentTrimExtendFeatureData.AccessSelections`）
- `IWeldmentTrimExtendFeatureData\AccessSelections.md` 第 14 行（`**Signature**: \`System.bool AccessSelections( ModelDoc2 PTopDoc, Component2 PComponent )\``）
- `IWeldmentTrimExtendFeatureData\ReleaseSelectionAccess.md` 第 17 行（`[[IWeldmentTrimExtendFeatureData::AccessSelections]] puts the model in a rollback state to allow access to` / `the selections that define the feature.`）

`IFeatureManager\InsertWeldmentTrimFeature.md` 与 `InsertWeldmentTrimFeature2.md` 两页**均无** `AccessSelections` 字样（它们走 `SelectByID2` + mark 的路径）。

★ 另：同接口内 4 个成员 `IGetBodiesToBeTrimmed` / `IGetTrimmingBoundary` / `ISetBodiesToBeTrimmed` / `ISetTrimmingBoundary` 的 `## Returns` / `## Parameters` 里逐字写有：

```
- in-process, unmanaged C++: Pointer to an array of ...
- VBA, VB.NET, C#, and C++/CLI: Not supported

See [In-process Methods](<../../docs/Programming with the SOLIDWORKS API/In-process Methods.md>) for details about this type of method.
```

### 本仓现状

搜索范围：`D:\AI\SW\scripts\` + `D:\AI\SW\mcp-server\`，模式 `WeldmentTrim|TrimExtend|InsertWeldmentTrim`。

| 位置 | 命中 | 判定 |
|---|---|---|
| `D:\AI\SW\scripts\`（**排除** `sw_api_*.py` 后） | **0 命中** | 本仓**无实现** |
| `D:\AI\SW\mcp-server\` | **0 命中** | 本仓**无实现** |

排除项（按指令，**不算实现**）：

- `D:\AI\SW\scripts\sw_api_sldworks.py` —— 文件头自述「**官方 API 的完整抄录** —— 523 个接口族、**8210 个成员**，逐个照抄自对官方 interop 程序集的**纯元数据反射**」⇒ 生成的反射索引。命中行：580 `'IWeldmentTrimExtendFeatureData',` · 4478 `'InsertWeldmentTrimFeature': 1,` · 4479 `'InsertWeldmentTrimFeature2': 5,` · 9815 `'IWeldmentTrimExtendFeatureData': {` · 17222 `'IWeldmentTrimExtendFeatureData': (` · 21235 `'InsertWeldmentTrimFeature': 65,` · 21236 `'InsertWeldmentTrimFeature2': 177,` · 26482 `'IWeldmentTrimExtendFeatureData': {` —— **（仅反射索引，不算实现）**

范围外（不在 `scripts/` 与 `mcp-server/`，仅记录，不作实现判定）：

- `D:\AI\SW\tools\gen_family_coverage.py:100` —— `"ICosmeticWeldBeadFeatureData", "IWeldSymbol", "IWeldmentTrimExtendFeatureData",`（覆盖度清单数据）
- `D:\AI\SW\tools\audit_gap_implementations.py:53` —— `"焊件/裁剪延伸焊件": ["InsertTrimExtend"],`（缺口审计清单；**注意其拼写为 `InsertTrimExtend`，与官方 `InsertWeldmentTrimFeature` 不同名**）
- `D:\AI\SW\_merged_test.py`（仓库根）—— 580 / 4478 / 4479 / 9815 / 17222 / 24685 / 24686 / 37949 行，形似 `sw_api_sldworks.py` 的合并/反射副本

相关但无该成员名的模块：

- `D:\AI\SW\scripts\sw_weldment.py` —— 存在（焊件模块），但对 `(?i)trim` **0 命中** ⇒ 未实现本功能项。