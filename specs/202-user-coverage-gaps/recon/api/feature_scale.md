# 特征/缩放·变形（feature_scale）

- 找页方式：在 `C:\swapi\types\` 下递归搜候选名 `InsertScale` / `IScaleFeatureData` / `ScaleFeatureData`。
- 命中页共 **3 份**（`ScaleFeatureData` 作为独立接口名**无**同名页；全库只有 `IScaleFeatureData` 一个接口，`C:\swapi\types\**\ScaleFeatureData*.md` 递归 0 命中）：
  1. `C:\swapi\types\IFeatureManager\InsertScale.md`
  2. `C:\swapi\types\IModelDoc2\InsertScale.md`
  3. `C:\swapi\types\IScaleFeatureData\_overview.md`（接口概览页，候选名之一 `IScaleFeatureData` 命中）
- 是否废弃：**是，1 份** —— `IModelDoc2.InsertScale` 标 `Obsolete`；后继 `IFeatureManager.InsertScale` 无 Obsolete 句，链止于此。
- 是否指针族：**是（仅在 IScaleFeatureData 接口族上）** —— 两份 `InsertScale` 页全文均无 `AccessSelections`；`IScaleFeatureData` 族有 `AccessSelections` / `IAccessSelections` / `IGetBodies` / `ISetBodies`。

## 页头逐字段（逐字）

### 命中页 1 · `C:\swapi\types\IFeatureManager\InsertScale.md`（页头前五行 → Signature 那一行，逐字）

```
---
type: IFeatureManager
member: InsertScale
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces
---

# IFeatureManager.InsertScale

Applies the specified scaling to either the current model or a selected graphic body.

**Signature**: `Feature InsertScale( System.short Type, System.bool Uniform, System.double Xscale, System.double YScale, System.double ZScale )`
```

### 命中页 2 · `C:\swapi\types\IModelDoc2\InsertScale.md`（页头前五行 → Signature 那一行，逐字）

```
---
type: IModelDoc2
member: InsertScale
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IModelDoc2.InsertScale

Obsolete. Superseded by [[IFeatureManager::InsertScale]].

**Signature**: `void InsertScale( System.double ScaleFactor_x, System.double ScaleFactor_y, System.double ScaleFactor_z, System.bool IsUniform, System.int ScaleType )`
```

### 命中页 3 · `C:\swapi\types\IScaleFeatureData\_overview.md`（页头前五行 → Description 段，逐字；★ 本页**无 Signature 行** —— 它是接口概览页，不是成员页，故「Signature 那一行」官方没写）

```
---
name: IScaleFeatureData
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Others
is_enum: False
property_count: 8
method_count: 8
enum_member_count: 0
---

# IScaleFeatureData

## Description
Allows access to a scale feature.
```

## Signature（逐字）

- 命中页 1（`IFeatureManager::InsertScale`）：`**Signature**: `Feature InsertScale( System.short Type, System.bool Uniform, System.double Xscale, System.double YScale, System.double ZScale )``
- 命中页 2（`IModelDoc2::InsertScale`，**后继页的 Signature 也逐字抄**）：`**Signature**: `void InsertScale( System.double ScaleFactor_x, System.double ScaleFactor_y, System.double ScaleFactor_z, System.bool IsUniform, System.int ScaleType )``
- 命中页 3（`IScaleFeatureData` 概览页）：官方没写（本页无 Signature 行）。
- Obsolete（命中页 1 `IFeatureManager::InsertScale`）：无
- Obsolete（命中页 2 `IModelDoc2::InsertScale`）：`Obsolete. Superseded by [[IFeatureManager::InsertScale]].`
- Obsolete（命中页 3 `IScaleFeatureData` 概览页）：无

**废弃链（逐级追到不再废弃）**

1. `IModelDoc2::InsertScale` —— `Obsolete. Superseded by [[IFeatureManager::InsertScale]].`
2. → `IFeatureManager::InsertScale` —— 页内**无** Obsolete 句 ⇒ 链止于此，无更后继页（官方页未给任何后继指针）。

**配套枚举（逐字，`C:\swapi\enums\swScaleType_e.md`，被两页的 `Type` / `ScaleType` 形参引用）**

```
# swScaleType_e

## Description
Scale types.

## Enumeration Members
| Member | Value |
| --- | --- |
| swScaleAboutCentroid | 0 |
| swScaleAboutCoordinateSystem | 2 |
| swScaleAboutOrigin | 1 |
```

## Remarks（逐字，或「本页无 ## Remarks 段」）

### 命中页 1 · `C:\swapi\types\IFeatureManager\InsertScale.md`（★ 有 `## Remarks` 标题 ⇒ 粘全文，逐字）

```
## Remarks
To scale a graphic body:

1. Select the graphic body in the Graphic Bodies folder of the FeatureManager design tree.

2. Call this method.

This method scales the selected graphic body up in the graphics view, but no scale feature is created.

**If Uniform is...**

**Then the scaling factor is...**

True

Xscale, applied in three directions.

False

All three scaling factors (Xscale, YScale, and ZScale).

Use [[IFeature::GetDefinition]] and [[IFeature::IGetDefinition]] and [[IFeature::ModifyDefinition]] and [[IFeature::IModifyDefinition2]] to gain access to the [[IScaleFeatureData]] object.
```

### 命中页 2 · `C:\swapi\types\IModelDoc2\InsertScale.md`

本页无 ## Remarks 段

### 命中页 3 · `C:\swapi\types\IScaleFeatureData\_overview.md`

本页无 ## Remarks 段

## Examples

- 命中页 1（`IFeatureManager::InsertScale`）：

```
## Examples
- [Insert Scale Feature (VBA)](../../examples/Insert_Scale_Feature_Example_VB.md)
```

（该例文件存在：`C:\swapi\examples\Insert_Scale_Feature_Example_VB.md`）

- 命中页 2（`IModelDoc2::InsertScale`）：无（该页无 `## Examples` 段）
- 命中页 3（`IScaleFeatureData` 概览页）：

```
## Examples
- [Get Data for Scale Feature (VBA)](../../examples/Get_Data_for_Scale_Feature_Example_VB.md)
- [Get Data for Scale Feature (VB.NET)](../../examples/Get_Data_for_Scale_Feature_Example_VBNET.md)
- [Get Data for Scale Feature (C#)](../../examples/Get_Data_for_Scale_Feature_Example_CSharp.md)
```

（另：`IScaleFeatureData.AccessSelections` 页列 `Get Faces Affected by Scale Feature (VBA)` → `C:\swapi\examples\Get_Faces_Affected_by_Scale_Feature_Example_VB.md`；`IScaleFeatureData.Bodies` 页列同一份。）

## 指针族 / 本仓现状

### 指针族（`AccessSelections` 全文搜）

- 命中页 1 `C:\swapi\types\IFeatureManager\InsertScale.md`：全文无 `AccessSelections` ⇒ **—**
- 命中页 2 `C:\swapi\types\IModelDoc2\InsertScale.md`：全文无 `AccessSelections` ⇒ **—**
- 命中页 3 / `IScaleFeatureData` 接口族：**⚠ 指针族**（逐条依据）：
  - `IScaleFeatureData::AccessSelections` —— `System.bool AccessSelections( System.object TopDoc, System.object Component )`
  - `IScaleFeatureData::IAccessSelections` —— `System.bool IAccessSelections( ModelDoc2 TopDoc, Component2 Component )`
  - `IScaleFeatureData::IGetBodies` —— `Body2 IGetBodies( System.int Count )`，其 Returns 段逐字写：`in-process, unmanaged C++: Pointer to an array of [[bodies]] that are scaled of size Count` / `VBA, VB.NET, C#, and C++/CLI: Not supported`
  - `IScaleFeatureData::ISetBodies` —— `void ISetBodies( System.int Count, ref Body2 BodyArr )`，其 BodyArr 形参说明同样逐字写 `in-process, unmanaged C++: Pointer to an array of [[bodies]]` / `VBA, VB.NET, C#, and C++/CLI: Not supported`
  - ⇒ ★ 官方页把「仅进程内非托管 C++」的措辞**只写在 `IGetBodies` / `ISetBodies` 两页**；`AccessSelections` / `IAccessSelections` 两页的 Returns 段**没有**这句（Returns 只写 `True if the selections were successfully accessed, false if not`）—— 此处按页面原文如实分开，不合并。
  - 非指针的对应件：`IScaleFeatureData::Bodies` —— `System.object Bodies {get; set;}`。
- 该族完整成员（`C:\swapi\index\members_by_type.md` 原样列出，8 属性 / 8 方法）：属性 `Bodies` `CoordinateSystem` `IsUniform` `ScaleUniform` `ScaleX` `ScaleY` `ScaleZ` `Type`；方法 `AccessSelections` `GetBodiesCount` `GetScale` `IAccessSelections` `IGetBodies` `ISetBodies` `ReleaseSelectionAccess` `SetScale`。

### 本仓现状（`D:\AI\SW\scripts\` 与 `D:\AI\SW\mcp-server\`，★ 已排除 `scripts/sw_api_*.py`）

- `D:\AI\SW\scripts\`：搜 `InsertScale|IScaleFeatureData|ScaleFeatureData|swScaleType_e|swFmScale` 共 **10 处命中，全部落在 `D:\AI\SW\scripts\sw_api_sldworks.py`**（行 450 / 4438 / 5721 / 6339 / 7931 / 15147 / 21195 / 22458 / 23076 / 24638）⇒ **（仅反射索引，不算实现）**。除该反射索引外，`scripts\` 下**无任何实现**。
- `D:\AI\SW\mcp-server\`：**0 命中**（无实现）。
- 全仓 `D:\AI\SW` 搜 slug `feature_scale`：**0 命中**。