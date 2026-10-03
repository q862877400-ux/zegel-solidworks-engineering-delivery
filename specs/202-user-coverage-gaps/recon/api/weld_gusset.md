# 焊件/角撑板（weld_gusset）

★ 抄录来源：`C:\swapi\types\` 下递归命中的 md 文件（逐字抄录，未改写、未总结、未补全）。
★ 候选成员名（线索）：`InsertGussetFeature` / `IGussetFeatureData` / `ISMGussetFeatureData`
★ **三个候选名全部命中**。同名多接口 ⇒ 每份都抄。

命中清单（共 7 页，逐份抄录）：

| # | 页 | 归属接口 | 是否含 `## Remarks` | 是否含 `## Examples` |
|---|---|---|---|---|
| 1 | `C:\swapi\types\IFeatureManager\InsertGussetFeature.md` | IFeatureManager | 否 | 否 |
| 2 | `C:\swapi\types\IFeatureManager\InsertGussetFeature2.md` | IFeatureManager | 是 | 是 |
| 3 | `C:\swapi\types\IFeatureManager\InsertGussetFeature3.md` | IFeatureManager | 是 | 是 |
| 4 | `C:\swapi\types\IGussetFeatureData\_overview.md` | IGussetFeatureData（焊件） | 否 | 是 |
| 5 | `C:\swapi\types\IGussetFeatureData\AccessSelections.md` | IGussetFeatureData（焊件） | 是 | 是 |
| 6 | `C:\swapi\types\ISMGussetFeatureData\_overview.md` | ISMGussetFeatureData（钣金） | 是 | 是 |
| 7 | `C:\swapi\types\ISMGussetFeatureData\AccessSelections.md` | ISMGussetFeatureData（钣金） | 是 | 否 |

---

## 页头逐字段（逐字）

### 页 1 · `C:\swapi\types\IFeatureManager\InsertGussetFeature.md`

```markdown
---
type: IFeatureManager
member: InsertGussetFeature
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces
---

# IFeatureManager.InsertGussetFeature

Obsolete. Superseded by [[IFeatureManager::InsertGussetFeature3]].

**Signature**: `Feature InsertGussetFeature( System.double Depth, System.short DirType, System.short LocType, System.bool BIsProfile, System.double ProfileD1, System.double ProfileD2, System.double ProfileD3, System.double ProfileAngle, System.double ProfileD4, System.bool BOffset, System.double DProfileOffset, System.int CrvIndex, System.bool BReverseDir, System.bool BReverseFace, System.bool BUseLenDim )`
```

### 页 2 · `C:\swapi\types\IFeatureManager\InsertGussetFeature2.md`

```markdown
---
type: IFeatureManager
member: InsertGussetFeature2
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces
---

# IFeatureManager.InsertGussetFeature2

Inserts a gusset feature for the specified faces.

**Signature**: `Feature InsertGussetFeature2( System.double Depth, System.short DirType, System.short LocType, System.bool BIsProfile, System.double ProfileD1, System.double ProfileD2, System.double ProfileD3, System.double ProfileAngle, System.double ProfileD4, System.bool BOffset, System.double DProfileOffset, System.int CrvIndex, System.bool BReverseDir, System.bool BReverseFace, System.bool BUseLenDim, System.object Faces )`
```

### 页 3 · `C:\swapi\types\IFeatureManager\InsertGussetFeature3.md`

```markdown
---
type: IFeatureManager
member: InsertGussetFeature3
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces
---

# IFeatureManager.InsertGussetFeature3

Inserts a gusset feature for pre-selected faces of a weldment.

**Signature**: `Feature InsertGussetFeature3( System.double Depth, System.short DirType, System.short LocType, System.bool BIsProfile, System.double ProfileD1, System.double ProfileD2, System.double ProfileD3, System.double ProfileAngle, System.double ProfileD4, System.bool BOffset, System.double DProfileOffset, System.int CrvIndex, System.bool BReverseDir, System.bool BReverseFace, System.bool BUseLenDim, System.double ProfileD5, System.double ProfileD6, System.double ProfileChamferAngle, System.bool BUseLenDimForChamfer, System.bool BNeedChamferInGusset )`
```

### 页 4 · `C:\swapi\types\IGussetFeatureData\_overview.md`

★ 本页**没有 `**Signature**` 行**（它是接口 overview 页，不是成员页）⇒ 抄到 `# 标题` + `## Description` 为止。

```markdown
---
name: IGussetFeatureData
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Weldments
is_enum: False
property_count: 14
method_count: 4
enum_member_count: 0
---

# IGussetFeatureData

## Description
Allows access to a weldment gusset feature.
```

### 页 5 · `C:\swapi\types\IGussetFeatureData\AccessSelections.md`

```markdown
---
type: IGussetFeatureData
member: AccessSelections
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Weldments
---

# IGussetFeatureData.AccessSelections

Gains access to the selections that define this gusset feature.

**Signature**: `System.bool AccessSelections( ModelDoc2 TopDoc, Component2 Component )`
```

### 页 6 · `C:\swapi\types\ISMGussetFeatureData\_overview.md`

★ 本页**没有 `**Signature**` 行**（它是接口 overview 页，不是成员页）⇒ 抄到 `# 标题` + `## Description` 为止。

```markdown
---
name: ISMGussetFeatureData
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Sheet Metal
is_enum: False
property_count: 28
method_count: 2
enum_member_count: 0
---

# ISMGussetFeatureData

## Description
Allows access to a sheet metal gusset feature.
```

### 页 7 · `C:\swapi\types\ISMGussetFeatureData\AccessSelections.md`

```markdown
---
type: ISMGussetFeatureData
member: AccessSelections
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Sheet Metal
---

# ISMGussetFeatureData.AccessSelections

Gains access to a sheet metal gusset.

**Signature**: `System.bool AccessSelections( ModelDoc2 TopDoc, Component2 Component )`
```

---

## Signature（逐字）

- 页 1 `IFeatureManager.InsertGussetFeature`：
  `Feature InsertGussetFeature( System.double Depth, System.short DirType, System.short LocType, System.bool BIsProfile, System.double ProfileD1, System.double ProfileD2, System.double ProfileD3, System.double ProfileAngle, System.double ProfileD4, System.bool BOffset, System.double DProfileOffset, System.int CrvIndex, System.bool BReverseDir, System.bool BReverseFace, System.bool BUseLenDim )`
- 页 2 `IFeatureManager.InsertGussetFeature2`：
  `Feature InsertGussetFeature2( System.double Depth, System.short DirType, System.short LocType, System.bool BIsProfile, System.double ProfileD1, System.double ProfileD2, System.double ProfileD3, System.double ProfileAngle, System.double ProfileD4, System.bool BOffset, System.double DProfileOffset, System.int CrvIndex, System.bool BReverseDir, System.bool BReverseFace, System.bool BUseLenDim, System.object Faces )`
- 页 3 `IFeatureManager.InsertGussetFeature3`：
  `Feature InsertGussetFeature3( System.double Depth, System.short DirType, System.short LocType, System.bool BIsProfile, System.double ProfileD1, System.double ProfileD2, System.double ProfileD3, System.double ProfileAngle, System.double ProfileD4, System.bool BOffset, System.double DProfileOffset, System.int CrvIndex, System.bool BReverseDir, System.bool BReverseFace, System.bool BUseLenDim, System.double ProfileD5, System.double ProfileD6, System.double ProfileChamferAngle, System.bool BUseLenDimForChamfer, System.bool BNeedChamferInGusset )`
- 页 5 `IGussetFeatureData.AccessSelections`：
  `System.bool AccessSelections( ModelDoc2 TopDoc, Component2 Component )`
- 页 7 `ISMGussetFeatureData.AccessSelections`：
  `System.bool AccessSelections( ModelDoc2 TopDoc, Component2 Component )`
- 页 4 / 页 6：**官方没写**（接口 overview 页不含 Signature 行）。

### Obsolete

- 页 1 `InsertGussetFeature`：`Obsolete. Superseded by [[IFeatureManager::InsertGussetFeature3]].`
- 页 2 `InsertGussetFeature2`：**无**（该页正文无 `Obsolete` 句；其 `## Remarks` 只写「Instead of using this method, you can: … Call InsertGussetFeature3.」—— 那是建议句，**不是** Obsolete 标注）。
- 页 3 `InsertGussetFeature3`：**无**
- 页 4 / 页 5 / 页 6 / 页 7：**无**

### 废弃链（逐级追到不再废弃）

| 级 | 成员 | 该页 Obsolete 原句 | 页自身给出的后继 |
|---|---|---|---|
| 1 | `InsertGussetFeature` | `Obsolete. Superseded by [[IFeatureManager::InsertGussetFeature3]].` | `InsertGussetFeature3`（正文直给）· `## See Also` 另列 `[[IFeatureManager::InsertGussetFeature2 Method]]` |
| 2 | `InsertGussetFeature3` | 无 | —— 链终点（再无后继页） |

⚠ 中间代 `InsertGussetFeature2` 的页**没有** Obsolete 标注，官方在此处**断链**：第 1 代直接指向第 3 代，第 2 代只是 See Also 里被列名。**官方没写**第 2 代的废弃状态。

---

## Remarks（逐字）

### 页 1 `InsertGussetFeature`
本页无 ## Remarks 段

### 页 2 `InsertGussetFeature2`

```markdown
## Remarks
Instead of using this method, you can:

1. Select two faces in the graphics area that are the supporting legs of this gusset.

2. Call [[IFeatureManager::InsertGussetFeature3]].
```

### 页 3 `InsertGussetFeature3`

```markdown
## Remarks
See the SOLIDWORKS Help for more information about profile and chamfer distances and angles in weldment gussets.

Before calling this method, you must call [[IModelDocExtension::SelectByID2]] to select two faces that are the supporting legs of this gusset with a Mark of 1.

Instead of using this method, you can pass an array of faces to [[IFeatureManager::InsertGussetFeature2]].
```

### 页 4 `IGussetFeatureData`（overview）
本页无 ## Remarks 段

### 页 5 `IGussetFeatureData.AccessSelections`

```markdown
## Remarks
**To modify a feature in a...**
**Then...**

Part

- TopDoc argument is the [[IModelDoc2]] for the part

- Component argument is Nothing or null

Assembly

- TopDoc is the IModelDoc2 object for the assembly

- Component argument is the [[IComponent2]] object in which the feature is to be modified

This method puts the model into a rollback state to allow access to the selections that define this feature. You must use either of the following methods to restore the rollback state:

- [[IFeature::ModifyDefinition]] or [[IFeature::IModifyDefinition2]] if you modified the feature

- [[IGussetFeatureData::ReleaseSelectionAccess]] if you did not
```

### 页 6 `ISMGussetFeatureData`（overview）

```markdown
## Remarks
To create a sheet metal gusset feature:

1. Call [[IFeatureManager::CreateDefinition]] to instantiate this feature data object.

2. Pre-select faces, lines, edges, vertices, or points as follows:

To...
Call [[IModelDocExtension::SelectByID2]] to select...

Specify the legs of the gusset feature

   - Two flat faces of a bend.

   - or -

   - Two flat faces adjacent to a cylindrical bend face.

   - or -

   - One cylindrical bend face.

   - or -

   - One flat face and one non-planar face adjacent to a toroidal bend.

   - or -

   - One toroidal bend face.

Optionally orient the gusset section plane

   One linear edge or sketch segment that is perpendicular to the gusset section plane.

   If you do not pre-select either entity, then the bend line adjacent to the gusset legs is used as the reference.

Optionally position the gusset section plane

   One vertex, sketch point, or reference point.

   If you do not pre-select any of these entities, then you must set [[ISMGussetFeatureData::UseOffset]] to true and specify [[ISMGussetFeatureData::OffsetDistance]] to define the reference point. For insertion of the first gusset, the assumed reference point is on the end of the sheet metal bend. For second and subsequent gusset insertions, the assumed reference point is on the edge of the gusset last inserted.

3. Specify [[ISMGussetFeatureData::ProfileDimensionScheme]] and modify other properties on this feature data object as follows:

   If ISMGussetFeatureData::ProfileDimensionScheme=

   [[swSheetMetalGussetProfileDimType_e]].

   swSheetMetalGussetProfileDimType_ProfileDimensions, to dimension the gusset profile using...

Specify ISMGussetFeatureData::...

Both legs of the gusset

   - [[ProfileLengthDim]] for d1 leg

   - [[ProfileHeightDim]] for d2 leg

   - [[UseAngleDimForProfile]] = false

   - [[FlipDimSides]] = true to swap d1 and d2 legs during dimensioning

d1 leg and the angle it forms with the gusset

   - ProfileLengthDim for d1 leg

   - [[ProfileAngleDim]] of angle formed by gusset intersecting d1 leg

   - UseAngleDimForProfile = true

   - FlipDimSides = true to swap d1 and d2 legs during dimensioning

d2 leg and the angle it forms with the gusset

   - ProfileHeightDim for d2 leg

   - ProfileAngleDim of angle formed by gusset intersecting d2 leg

   - UseAngleDimForProfile = true

   - FlipDimSides = true to swap d1 and d2 legs during dimensioning

4. Call [[IFeatureManager::CreateFeature]].

For more information, see the **SOLIDWORKS Design user-interface help > Sheet Metal > Using Sheet Metal Tools > Adding Sheet Metal Gussets > Sheet Metal Gusset PropertyManager** topic.
```

### 页 7 `ISMGussetFeatureData.AccessSelections`

```markdown
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

- [[IFeature::ModifyDefinition]] if you modified the feature

- [[ISMGussetFeatureData::ReleaseSelectionAccess]] if you did not
```

---

## Examples

### 页 1 `InsertGussetFeature`
无

### 页 2 `InsertGussetFeature2`
- `Insert_Weldment_Features_Example_VB.md`
- `Insert_Weldment_Features_Example_VBNET.md`
- `Insert_Weldment_Features_Example_CSharp.md`

### 页 3 `InsertGussetFeature3`
- `Insert_Gusset_Feature_Example_VB.md`
- `Insert_Gusset_Feature_Example_VBNET.md`
- `Insert_Gusset_Feature_Example_CSharp.md`

### 页 4 `IGussetFeatureData`（overview）
- `Get_Gusset_Feature_Data_Example_CSharp.md`
- `Get_Gusset_Feature_Data_Example_VBNET.md`
- `Get_Gusset_Feature_Data_Example_VB.md`

### 页 5 `IGussetFeatureData.AccessSelections`
- `Get_Gusset_Feature_Data_Example_CSharp.md`
- `Get_Gusset_Feature_Data_Example_VBNET.md`
- `Get_Gusset_Feature_Data_Example_VB.md`

### 页 6 `ISMGussetFeatureData`（overview）
- `Create_Sheet_Metal_Gusset_Example_VBNET.md`
- `Create_Sheet_Metal_Gusset_Example_CSharp.md`

### 页 7 `ISMGussetFeatureData.AccessSelections`
无

---

## 指针族 / 本仓现状

### 指针族（AccessSelections 全文搜）

- 页 1 `InsertGussetFeature`：**—**
- 页 2 `InsertGussetFeature2`：**—**
- 页 3 `InsertGussetFeature3`：**—**
- 页 4 `IGussetFeatureData`（overview）全文：**—**
- 页 5 `IGussetFeatureData.AccessSelections`：**⚠ 指针族**（既有成员名，也有 `**Signature**` 行 `System.bool AccessSelections( ModelDoc2 TopDoc, Component2 Component )`）
- 页 6 `ISMGussetFeatureData`（overview）全文：**—**
- 页 7 `ISMGussetFeatureData.AccessSelections`：**⚠ 指针族**（同上签名）

★ 同族旁证（同一批官方页里的交叉引用，**逐字**）：
- `C:\swapi\types\IGussetFeatureData\ReleaseSelectionAccess.md` 第 17 行：
  `[[IGussetFeatureData::AccessSelections]] puts the model into a rollback state to allow access to the selections that define this gusset feature.`
- `C:\swapi\types\ISMGussetFeatureData\ReleaseSelectionAccess.md` 第 17 行：
  `[[ISMGussetFeatureData::AccessSelections]] puts the model in a rollback state to allow access to the selections that define the feature.`

### 两个同族接口的官方分类（逐字抄自各自 front matter，非推断）

| | `IGussetFeatureData` | `ISMGussetFeatureData` |
|---|---|---|
| `category` | `Feature Interfaces/Weldments` | `Feature Interfaces/Sheet Metal` |
| `## Description` | `Allows access to a weldment gusset feature.` | `Allows access to a sheet metal gusset feature.` |
| `property_count` | `14` | `28` |
| `method_count` | `4` | `2` |

⚠ **两个接口同名不同族**：`InsertGussetFeature3` 三份 `## See Also` 只列 `[[IGussetFeatureData Interface]]`（**焊件**那个），**没有一处**列 `ISMGussetFeatureData`；而 `ISMGussetFeatureData` overview 的 See Also 列的是 `[[IFeatureManager::InsertSheetMetalGussetFeature Method ()]]` / `…InsertSheetMetalGussetFeature2 Method ()`。

### 本仓现状（`D:\AI\SW\scripts\` + `D:\AI\SW\mcp-server\`）

搜的是三个候选成员名：`InsertGussetFeature` / `IGussetFeatureData` / `ISMGussetFeatureData`。

| 位置 | 命中 | 性质 |
|---|---|---|
| `D:\AI\SW\mcp-server\` | **0 命中** | 无 |
| `D:\AI\SW\scripts\sw_api_sldworks.py` | `InsertGussetFeature`(4400/21157)、`InsertGussetFeature2`(4401/21158)、`InsertGussetFeature3`(4402/21159)、`IGussetFeatureData`(271/4721/12461/21474)、`ISMGussetFeatureData`(442/7868/15049/24575) | ★ **仅反射索引，不算实现**（按要求排除） |
| `D:\AI\SW\scripts\sw_sheet_metal.py` | 命中 3 处，全部是**注释 / 文档字符串里的散文**：`SHEET_METAL_RUNTIME_STATUS` 里第 120–127 行、`#:` 第 310/313 行、来源块第 548/554/567–568 行 | **不是**对该成员名的调用 |

**结论**：**本仓没有**焊件角撑板入口 `InsertGussetFeature` / `InsertGussetFeature2` / `InsertGussetFeature3` 的实现（`scripts/` 除反射索引外无命中，`mcp-server/` 零命中）。

**别被 `scripts\sw_sheet_metal.py` 的 `create_gusset` 误导** —— 逐字读它的代码路径：
- 它走的是 `return _create_from_definition(model, SW_FM_SM_GUSSET, _apply)`（第 608 行），即 **`CreateDefinition` + `CreateFeature`** 路线，**不是** `InsertGussetFeature*`；
- `_apply` 里设的属性是 `ProfileDimensionScheme` / `GussetThickness` / `UseAngleDimForProfile` / `ProfileLengthDim` / `ProfileAngleDim` / `ProfileHeightDim` / `UseOffset` / `OffsetDistance`（第 584–606 行），全是 **`ISMGussetFeatureData`（钣金）** 的成员；
- 该文件注释自己写明：「本函数创建的是 **钣金**加强筋（`swFmSMGusset=118`，枚举描述明写 "**Sheet metal** gusset"）」。
⇒ 它是**钣金角撑板**实现，与本页抄的**焊件**入口（`IFeatureManager::InsertGussetFeature*` + `IGussetFeatureData`）**不是同一条路**，不能算作焊件入口的实现。

### 相邻但**不同名**的官方成员（仅备录，不作替代）

`C:\swapi\types\IFeatureManager\` 下另有 6 个同名族页面，成员名与本次候选**不同**（`InsertSheetMetalGussetFeature` / `…2` / `…3`，各含 Sheet Metal 版）：
`InsertSheetMetalGussetFeature.md` · `InsertSheetMetalGussetFeature2.md` · `InsertSheetMetalGussetFeature3.md`。
★ 未在此逐字抄录 —— 它们**不是**候选名，按死规矩**不拿相近名字代替**。此处只作存在性备录。

★ 未跑 SolidWorks，未跑 pytest；未改动任何已有文件（本文件为新建）。
