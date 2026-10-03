# 焊件/顶端盖（weld_end_cap）

- 检索方式：在 `C:\swapi\types\` 下递归搜候选名（`InsertEndCapFeature3` / `InsertEndCapFeature2` / `InsertEndCapFeature` / `IEndCapFeatureData`）。候选名 **全部命中**，无需换英文关键词。
- 命中清单（5 份，逐份转录于下）：
  1. `C:\swapi\types\IFeatureManager\InsertEndCapFeature3.md`
  2. `C:\swapi\types\IFeatureManager\InsertEndCapFeature2.md`
  3. `C:\swapi\types\IFeatureManager\InsertEndCapFeature.md`（**判为废弃**）
  4. `C:\swapi\types\IEndCapFeatureData\_overview.md`（候选名 `IEndCapFeatureData` 本身的接口页）
  5. `C:\swapi\types\IEndCapFeatureData\IsEndCapInward.md`
  6. `C:\swapi\types\IEndCapFeatureData\AccessSelections.md`（指针族判据页，见 §指针族）
- 补充事实（只记，不展开转录）：`C:\swapi\types\IEndCapFeatureData\` 目录下共 **13 份**成员页 —— `_overview.md` / `AccessSelections.md` / `ChamferDistance.md` / `DepthDistance.md` / `Face.md` / `IsEndCapInward.md` / `OffsetDistance.md` / `ReleaseSelectionAccess.md` / `Thickness.md` / `ThicknessRatioForOffset.md` / `UseChamferCorners.md` / `UseCornerTreatment.md` / `UseReverse.md`。本功能项候选名只点到接口与两个入口，故逐字转录限于上列 5 份。

---

## 页头逐字段（逐字）

### [1] `IFeatureManager\InsertEndCapFeature3.md` —— 第 1–14 行整段

```text
---
type: IFeatureManager
member: InsertEndCapFeature3
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces
---

# IFeatureManager.InsertEndCapFeature3

Inserts an end cap feature for one or more pre-selected open ends of a structural member.

**Signature**: `Feature InsertEndCapFeature3( System.double Depth, System.bool BIsGivenOffset, System.bool BIsChamfer, System.double OffsetValue, System.double WallThicknessRatio, System.double ChamferValue, System.bool BIsCornerTreatment, System.double DepthOffset, System.bool BIsReverse, System.int BIsEndCapInward )`
```

### [2] `IFeatureManager\InsertEndCapFeature2.md` —— 第 1–14 行整段

```text
---
type: IFeatureManager
member: InsertEndCapFeature2
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces
---

# IFeatureManager.InsertEndCapFeature2

Inserts an end cap feature using the specified end faces of a structural member.

**Signature**: `Feature InsertEndCapFeature2( System.double Depth, System.bool BIsGivenOffset, System.bool BIsChamfer, System.double OffsetValue, System.double WallThicknessRatio, System.double ChamferValue, System.object Faces )`
```

### [3] `IFeatureManager\InsertEndCapFeature.md` —— 第 1–14 行整段

```text
---
type: IFeatureManager
member: InsertEndCapFeature
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces
---

# IFeatureManager.InsertEndCapFeature

Obsolete. Superseded by [[IFeatureManager::InsertEndCapFeature3]].

**Signature**: `Feature InsertEndCapFeature( System.double Depth, System.bool BIsGivenOffset, System.bool BIsChamfer, System.double OffsetValue, System.double WallThicknessRatio, System.double ChamferValue )`
```

### [4] `IEndCapFeatureData\_overview.md` —— 第 1–16 行整段

```text
---
name: IEndCapFeatureData
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Weldments
is_enum: False
property_count: 11
method_count: 2
enum_member_count: 0
---

# IEndCapFeatureData

## Description
Allows access to an end-cap feature.
```

（该页是**接口页**，全文无 `**Signature**:` 行 —— 接口本身不是可调用成员。）

### [5] `IEndCapFeatureData\IsEndCapInward.md` —— 第 1–14 行整段

```text
---
type: IEndCapFeatureData
member: IsEndCapInward
kind: property
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Weldments
---

# IEndCapFeatureData.IsEndCapInward

Gets or sets the thickness direction of this end cap feature.

**Signature**: `System.int IsEndCapInward {get; set;}`
```

### [6] `IEndCapFeatureData\AccessSelections.md` —— 第 1–14 行整段

```text
---
type: IEndCapFeatureData
member: AccessSelections
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Weldments
---

# IEndCapFeatureData.AccessSelections

Gains access to the selections that define this end-cap feature.

**Signature**: `System.bool AccessSelections( ModelDoc2 TopDoc, Component2 Component )`
```

---

## Signature（逐字）

### [1] `InsertEndCapFeature3`
**Signature**: `Feature InsertEndCapFeature3( System.double Depth, System.bool BIsGivenOffset, System.bool BIsChamfer, System.double OffsetValue, System.double WallThicknessRatio, System.double ChamferValue, System.bool BIsCornerTreatment, System.double DepthOffset, System.bool BIsReverse, System.int BIsEndCapInward )`

- Obsolete: 无

### [2] `InsertEndCapFeature2`
**Signature**: `Feature InsertEndCapFeature2( System.double Depth, System.bool BIsGivenOffset, System.bool BIsChamfer, System.double OffsetValue, System.double WallThicknessRatio, System.double ChamferValue, System.object Faces )`

- Obsolete: 无

### [3] `InsertEndCapFeature`
**Signature**: `Feature InsertEndCapFeature( System.double Depth, System.bool BIsGivenOffset, System.bool BIsChamfer, System.double OffsetValue, System.double WallThicknessRatio, System.double ChamferValue )`

- Obsolete: `Obsolete. Superseded by [[IFeatureManager::InsertEndCapFeature3]].`

### [4] `IEndCapFeatureData`（接口页）
官方没写（该页无 `**Signature**:` 行）

- Obsolete: 无

### [5] `IsEndCapInward`
**Signature**: `System.int IsEndCapInward {get; set;}`

- Obsolete: 无

### [6] `AccessSelections`
**Signature**: `System.bool AccessSelections( ModelDoc2 TopDoc, Component2 Component )`

- Obsolete: 无

### 废弃链（逐级追到不再废弃）

```text
IFeatureManager.InsertEndCapFeature  ——「Obsolete. Superseded by [[IFeatureManager::InsertEndCapFeature3]].」
  └─→ IFeatureManager.InsertEndCapFeature3  —— 该页**无** Obsolete 句 ⇒ 链在此终止（不再废弃）
```

⚠ 只追一条链。`InsertEndCapFeature2` **不在**这条链上：它的页**无** Obsolete 句，且其 Remarks 明写它是「用 Faces 数组」那条并列入口（`Call [[IFeatureManager::InsertEndCapFeature3]] if you want to pre-select the faces to end-cap in the graphics area.`）。⇒ `InsertEndCapFeature` 与 `InsertEndCapFeature2` 都直接指向 `InsertEndCapFeature3`，**不是** `1 → 2 → 3` 的线性继承。

---

## Remarks（逐字，或「本页无 ## Remarks 段」）

### [1] `InsertEndCapFeature3` —— 有 `## Remarks` 段（第 31–34 行），全文逐字：

```text
## Remarks
Before calling this method, select one or more end [[faces]] of a structural member in the graphics area.

Instead of using this method, you can pass the faces in an argument array of [[IFeatureManager::InsertEndCapFeature2]].
```

### [2] `InsertEndCapFeature2` —— 有 `## Remarks` 段（第 28–29 行），全文逐字：

```text
## Remarks
Call [[IFeatureManager::InsertEndCapFeature3]] if you want to pre-select the faces to end-cap in the graphics area.
```

### [3] `InsertEndCapFeature`
本页无 `## Remarks` 段

### [4] `IEndCapFeatureData`（接口页）
本页无 `## Remarks` 段

### [5] `IsEndCapInward`
本页无 `## Remarks` 段

### [6] `AccessSelections` —— 有 `## Remarks` 段（第 23–43 行），全文逐字：

```text
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

- [[IEndCapFeatureData::ReleaseSelectionAccess]] if you did not
```

---

## Examples

### [1] `InsertEndCapFeature3` —— 有 `## Examples` 段（第 36–39 行），逐字：

```text
## Examples
- [Insert Weldment End Cap (VBA)](../../examples/Insert_Weldment_End_Cap_Example_VB.md)
- [Insert Weldment End Cap (VB.NET)](../../examples/Insert_Weldment_End_Cap_Example_VBNET.md)
- [Insert Weldment End Cap (C#)](../../examples/Insert_Weldment_End_Cap_Example_CSharp.md)
```

### [2] `InsertEndCapFeature2` —— 有 `## Examples` 段（第 31–34 行），逐字：

```text
## Examples
- [Insert Weldment Features (VBA)](../../examples/Insert_Weldment_Features_Example_VB.md)
- [Insert Weldment Features (VB.NET)](../../examples/Insert_Weldment_Features_Example_VBNET.md)
- [Insert Weldment Features (C#)](../../examples/Insert_Weldment_Features_Example_CSharp.md)
```

### [3] `InsertEndCapFeature`
无（该页无 `## Examples` 段）

### [4] `IEndCapFeatureData`（接口页）—— 有 `## Examples` 段（第 21–24 行），逐字：

```text
## Examples
- [Insert Weldment End Cap (VBA)](../../examples/Insert_Weldment_End_Cap_Example_VB.md)
- [Insert Weldment End Cap (VB.NET)](../../examples/Insert_Weldment_End_Cap_Example_VBNET.md)
- [Insert Weldment End Cap (C#)](../../examples/Insert_Weldment_End_Cap_Example_CSharp.md)
```

### [5] `IsEndCapInward`
无（该页无 `## Examples` 段）

### [6] `AccessSelections` —— 有 `## Examples` 段（第 45–46 行），逐字：

```text
## Examples
- [List End-cap Feature Properties (VBA)](../../examples/List_End-Cap_Feature_Properties_Example_VB.md)
```

### 例子文件落盘核验（`C:\swapi\examples\` 下逐个 `Test-Path`）

| 例子文件 | 存在 |
|---|---|
| `Insert_Weldment_End_Cap_Example_VB.md` | 是 |
| `Insert_Weldment_End_Cap_Example_VBNET.md` | 是 |
| `Insert_Weldment_End_Cap_Example_CSharp.md` | 是 |
| `Insert_Weldment_Features_Example_VB.md` | 是 |
| `Insert_Weldment_Features_Example_VBNET.md` | 是 |
| `Insert_Weldment_Features_Example_CSharp.md` | 是 |
| `List_End-Cap_Feature_Properties_Example_VB.md` | 是 |

去重后共 **7 个**不同例子文件。

---

## 指针族 / 本仓现状

### 指针族判据（逐页全文搜 `AccessSelections`）

| 页 | 全文含 `AccessSelections`？ | 判据 |
|---|---|---|
| [1] `InsertEndCapFeature3.md` | 否 | — |
| [2] `InsertEndCapFeature2.md` | 否 | — |
| [3] `InsertEndCapFeature.md` | 否 | — |
| [4] `IEndCapFeatureData\_overview.md` | 否（该页自身无） | — |
| [5] `IsEndCapInward.md` | 否 | — |
| [6] `IEndCapFeatureData\AccessSelections.md` | **是**（本体即为该成员） | ⚠ 指针族 |

⚠ **指针族判定：`IEndCapFeatureData` 是指针族接口。** 依据逐字：其 `AccessSelections` 签名 `System.bool AccessSelections( ModelDoc2 TopDoc, Component2 Component )`，Remarks 明写 `This method puts the model into a rollback state to allow access to the selections that define this feature.`，并要求用 `IFeature::ModifyDefinition` / `IFeature::IModifyDefinition2` / `IEndCapFeatureData::ReleaseSelectionAccess` 恢复回滚态；`_overview.md` 的 front matter 记 `method_count: 2`，即该接口只有 2 个方法（`AccessSelections` + `ReleaseSelectionAccess`），**没有任何纯几何建模方法**。
⇒ **三个 `Insert*` 入口方法本身的页都不含 `AccessSelections`**（它们是「一步到位」的建模入口，不是指针接口）；但凡是要事后改该顶端盖特征的属性（`Depth` / `Thickness` / `ThicknessRatioForOffset` / `UseCornerTreatment` / `IsEndCapInward` 等 11 个属性），按官方契约**必须**先走 `AccessSelections` 进入回滚态 —— 即本功能项存在指针族环节。

### 本仓现状（`D:\AI\SW\scripts\` 与 `D:\AI\SW\mcp-server\`）

检索式：递归全文件、大小写不敏感，关键词 `EndCap` 与 `end_cap`。

**命中总数：仅 1 个文件，且是生成的反射索引 —— 本仓无实现。**

| 文件 | 命中数 | 性质 |
|---|---|---|
| `D:\AI\SW\scripts\sw_api_sldworks.py` | 12 | **`sw_api_*.py` = 生成的反射索引（仅反射索引，不算实现）** |
| `D:\AI\SW\scripts\__pycache__\sw_api_sldworks.cpython-314.pyc` | 3 | 同上文件的字节码缓存（**不算实现**） |
| `D:\AI\SW\mcp-server\`（整个目录） | **0** | — |
| `D:\AI\SW\scripts\` 下除 `sw_api_*.py` / `__pycache__` 外的任何文件 | **0** | — |

反射索引内的 12 处命中（**仅反射索引，不算实现**）：

```text
scripts\sw_api_sldworks.py:214      'IEndCapFeatureData',
scripts\sw_api_sldworks.py:3756     'IEndCapFeatureData': {
scripts\sw_api_sldworks.py:4378     'InsertEndCapFeature': 6,
scripts\sw_api_sldworks.py:4379     'InsertEndCapFeature2': 7,
scripts\sw_api_sldworks.py:4380     'InsertEndCapFeature3': 10,
scripts\sw_api_sldworks.py:11948    'IEndCapFeatureData': (
scripts\sw_api_sldworks.py:11955    'IsEndCapInward',
scripts\sw_api_sldworks.py:11956    'IsEndCapInward',
scripts\sw_api_sldworks.py:20633    'IEndCapFeatureData': {
scripts\sw_api_sldworks.py:21135    'InsertEndCapFeature': 68,
scripts\sw_api_sldworks.py:21136    'InsertEndCapFeature2': 176,
scripts\sw_api_sldworks.py:21137    'InsertEndCapFeature3': 240,
```

⇒ **结论：本仓对 `weld_end_cap` 无任何实现、无工具、无测试；仅由 `sw_api_sldworks.py` 这份反射索引记录了三个入口的 arity（6 / 7 / 10），与上录官方签名形参个数一致。**

### 拿不准的地方（据实标注，未猜）

- `InsertEndCapFeature3` 的 `BIsEndCapInward` 形参类型是 `System.int`，其官方参数说明为 `Thickness direction as defined in [[swEndCapThicknessDirection_e]]`；但 `DepthOffset` 的说明又写 `valid only if BIsEndCapInward = 2`（把枚举当成整数比值用）。**官方这两句的语义不自洽**，本文件只逐字抄录，不作调和、不给推荐值。
- `_overview.md` 的 `property_count: 11` / `method_count: 2` 与目录下实际成员页文件数一致（11 个属性页 + `AccessSelections` + `ReleaseSelectionAccess` = 2 个方法页）。
- `[[swEndCapThicknessDirection_e]]` 枚举的取值表本文件**未查**（不在本次转录范围），故不给具体数值。