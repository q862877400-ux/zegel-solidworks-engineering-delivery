# 钣金/褶边（sm_hem）

候选名：`InsertSheetMetalHem` / `IHemFeatureData`

## 页头逐字段（逐字）

命中页（候选名逐字搜 `C:\swapi\types\` 全递归，命中 4 份；`IHemFeatureData` 同名接口只有 1 个目录，无第二份接口）：

- `C:\swapi\types\IModelDoc2\InsertSheetMetalHem.md`
- `C:\swapi\types\IFeatureManager\InsertSheetMetalHem.md`
- `C:\swapi\types\IFeatureManager\InsertSheetMetalHem2.md`
- `C:\swapi\types\IHemFeatureData\_overview.md`

（补充：`C:\swapi\types\IHemFeatureData\` 目录下共 19 个文件 —— `_overview.md` / `AccessSelections.md` / `Angle.md` / `BendPosition.md` / `Edges.md` / `GapDistance.md` / `GetCustomBendAllowance.md` / `GetEdgesCount.md` / `IAccessSelections.md` / `IGetEdges.md` / `ISetEdges.md` / `Length.md` / `MiterGap.md` / `Radius.md` / `ReleaseSelectionAccess.md` / `ReverseDirection.md` / `SetCustomBendAllowance.md` / `Type.md` / `UseDefaultBendAllowance.md`。）

★ 注：同名前缀 `InsertSheetMetalHem` 另有两个命中页 —— `IFeatureManager\InsertSheetMetalHem.md`（Obsolete）与 `IFeatureManager\InsertSheetMetalHem2.md`（后继，非废弃）—— 已按「同名多接口 ⇒ 每份都要」逐份抄录，见下。

### 页 1 · `C:\swapi\types\IModelDoc2\InsertSheetMetalHem.md`（页头 → Signature 行，逐字）

```text
---
type: IModelDoc2
member: InsertSheetMetalHem
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IModelDoc2.InsertSheetMetalHem

Obsolete. Superseded by [[IFeatureManager::InsertSheetMetalHem]].

**Signature**: `void InsertSheetMetalHem( System.int Type, System.int Position, System.bool Reverse, System.double DLength, System.double DGap, System.double DAngle, System.double DRad, System.double DMiterGap )`
```

### 页 2 · `C:\swapi\types\IFeatureManager\InsertSheetMetalHem.md`（页头 → Signature 行，逐字）

```text
---
type: IFeatureManager
member: InsertSheetMetalHem
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces
---

# IFeatureManager.InsertSheetMetalHem

Obsolete. Superseded by [[IFeatureManager::InsertSheetMetalHem2]].

**Signature**: `Feature InsertSheetMetalHem( System.int Type, System.int Position, System.bool Reverse, System.double DLength, System.double DGap, System.double DAngle, System.double DRad, System.double DMiterGap, CustomBendAllowance PCBA )`
```

### 页 3 · `C:\swapi\types\IFeatureManager\InsertSheetMetalHem2.md`（页头 → Signature 行，逐字）

```text
---
type: IFeatureManager
member: InsertSheetMetalHem2
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces
---

# IFeatureManager.InsertSheetMetalHem2

Inserts a hem of the specified relief type at the selected edges of the current sheet metal part.

**Signature**: `Feature InsertSheetMetalHem2( System.int Type, System.int Position, System.bool Reverse, System.double DLength, System.double DGap, System.double DAngle, System.double DRad, System.double DMiterGap, CustomBendAllowance PCBA, System.bool UseDefaultRelief, System.int ReliefType, System.int ReliefTearTypes, System.bool UseReliefRatio, System.double ReliefRatio, System.double ReliefWidth, System.double ReliefDepth )`
```

### 页 4 · `C:\swapi\types\IHemFeatureData\_overview.md`（页头，逐字）

```text
---
name: IHemFeatureData
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Sheet Metal
is_enum: False
property_count: 10
method_count: 8
enum_member_count: 0
---
```

（该页全文 30 行，**没有 Signature 那一行** ⇒ 官方没写。）

## Signature（逐字）

- 页 1 `IModelDoc2.InsertSheetMetalHem`：
  `**Signature**: `void InsertSheetMetalHem( System.int Type, System.int Position, System.bool Reverse, System.double DLength, System.double DGap, System.double DAngle, System.double DRad, System.double DMiterGap )``
- 页 2 `IFeatureManager.InsertSheetMetalHem`：
  `**Signature**: `Feature InsertSheetMetalHem( System.int Type, System.int Position, System.bool Reverse, System.double DLength, System.double DGap, System.double DAngle, System.double DRad, System.double DMiterGap, CustomBendAllowance PCBA )``
- 页 3 `IFeatureManager.InsertSheetMetalHem2`：
  `**Signature**: `Feature InsertSheetMetalHem2( System.int Type, System.int Position, System.bool Reverse, System.double DLength, System.double DGap, System.double DAngle, System.double DRad, System.double DMiterGap, CustomBendAllowance PCBA, System.bool UseDefaultRelief, System.int ReliefType, System.int ReliefTearTypes, System.bool UseReliefRatio, System.double ReliefRatio, System.double ReliefWidth, System.double ReliefDepth )``
- 页 4 `IHemFeatureData`（接口页）：官方没写（本页无 Signature 行）

- Obsolete:
  - 页 1 `IModelDoc2\InsertSheetMetalHem.md`：
    > Obsolete. Superseded by [[IFeatureManager::InsertSheetMetalHem]].
  - 页 2 `IFeatureManager\InsertSheetMetalHem.md`：
    > Obsolete. Superseded by [[IFeatureManager::InsertSheetMetalHem2]].
  - 页 3 `IFeatureManager\InsertSheetMetalHem2.md`：无。
  - 页 4 `IHemFeatureData\_overview.md`：无。

### ★ 废弃链（逐级追到底，后继 Signature 逐字抄录）

链 1（入口链，3 级）：

```text
IModelDoc2.InsertSheetMetalHem            （Obsolete → IFeatureManager::InsertSheetMetalHem）
        ↓
IFeatureManager.InsertSheetMetalHem       （Obsolete → IFeatureManager::InsertSheetMetalHem2）
        ↓
IFeatureManager.InsertSheetMetalHem2      （★ 页 3 全文无 Obsolete 句 ⇒ 链条到此为止，不再废弃）
```

- 页 3 `IFeatureManager\InsertSheetMetalHem2.md` 的「页头 → Signature 行」已在上面**逐字抄录**，其 Signature 为：
  `Feature InsertSheetMetalHem2( System.int Type, System.int Position, System.bool Reverse, System.double DLength, System.double DGap, System.double DAngle, System.double DRad, System.double DMiterGap, CustomBendAllowance PCBA, System.bool UseDefaultRelief, System.int ReliefType, System.int ReliefTearTypes, System.bool UseReliefRatio, System.double ReliefRatio, System.double ReliefWidth, System.double ReliefDepth )`

⇒ 本功能项**当前有效的唯一入口是 `IFeatureManager.InsertSheetMetalHem2`**（16 参数，带 relief 系列参数）；两个 `InsertSheetMetalHem` 均已废弃。

链 2（指针族内部链，见下「指针族」节）：`IHemFeatureData.IAccessSelections` —— **无 Obsolete 句**（与 `IClosedCornerFeatureData.IAccessSelections` 不同，**本页不废弃**），且 `C:\swapi\types\IHemFeatureData\` 目录下**没有 `IAccessSelections2.md`** ⇒ 本接口无后继链。

## Remarks（逐字，或「本页无 ## Remarks 段」）

- 页 1 `IModelDoc2\InsertSheetMetalHem.md`：本页无 ## Remarks 段
- 页 2 `IFeatureManager\InsertSheetMetalHem.md`：本页无 ## Remarks 段
- 页 3 `IFeatureManager\InsertSheetMetalHem2.md`：**有** `## Remarks`，逐字全文如下 ——

```text
## Remarks
Before calling this method:

1. Call [[IFeatureManager::CreateCustomBendAllowance]] to create an instance of ICustomBendAllowance.

2. Initialize the CustomBendAllowance object.

3. Assign PCBA to the initialized CustomBendAllowance object.

4. Select one or more edges in the sheet metal model to which to add the specified hem.
```

- 页 4 `IHemFeatureData\_overview.md`：本页无 ## Remarks 段

## Examples

- 页 1 `IModelDoc2\InsertSheetMetalHem.md`：无（本页无 ## Examples 段）
- 页 2 `IFeatureManager\InsertSheetMetalHem.md`：无（本页无 ## Examples 段）
- 页 3 `IFeatureManager\InsertSheetMetalHem2.md`：
  - `Insert Sheet Metal Hem (VBA)` → `../../examples/Insert_Sheet_Metal_Hem_Example_VB.md`
  - `Insert Sheet Metal Hem (VB.NET)` → `../../examples/Insert_Sheet_Metal_Hem_Example_VBNET.md`
  - `Insert Sheet Metal Hem (C#)` → `../../examples/Insert_Sheet_Metal_Hem_Example_CSharp.md`
- 页 4 `IHemFeatureData\_overview.md`：
  - `Insert Sheet Metal Hem (VBA)` → `../../examples/Insert_Sheet_Metal_Hem_Example_VB.md`
  - `Insert Sheet Metal Hem (VB.NET)` → `../../examples/Insert_Sheet_Metal_Hem_Example_VBNET.md`
  - `Insert Sheet Metal Hem (C#)` → `../../examples/Insert_Sheet_Metal_Hem_Example_CSharp.md`

★ 三个例子文件在 `C:\swapi\examples\` 下**均已核实存在**：`Insert_Sheet_Metal_Hem_Example_VB.md` / `Insert_Sheet_Metal_Hem_Example_VBNET.md` / `Insert_Sheet_Metal_Hem_Example_CSharp.md`。

## 指针族 / 本仓现状

### AccessSelections 全文搜（命中页逐份判定）

- 页 1 `IModelDoc2\InsertSheetMetalHem.md`：全文无 `AccessSelections` ⇒ —
- 页 2 `IFeatureManager\InsertSheetMetalHem.md`：全文无 `AccessSelections` ⇒ —
- 页 3 `IFeatureManager\InsertSheetMetalHem2.md`：全文无 `AccessSelections` ⇒ —
- 页 4 `IHemFeatureData\_overview.md`：全文无 `AccessSelections` ⇒ —
- ★ 接口目录 `C:\swapi\types\IHemFeatureData\` 内另有三个页含 `AccessSelections` ⇒ **⚠ 指针族**：
  - `AccessSelections.md` — `System.bool AccessSelections( System.object TopDoc, System.object Component )`（该页**有** `## Remarks`，逐字全文如下 ——）

    ```text
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

    - [[IFeature::ModifyDefinition]] if you modified the feature

    - [[IHemFeatureData::ReleaseSelectionAccess]] if you did not
    ```

  - `IAccessSelections.md` — `System.bool IAccessSelections( ModelDoc2 TopDoc, Component2 Component )`（**无 Obsolete 句**；该页**有** `## Remarks`，逐字全文如下 ——）

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

    - [[IFeature::IModifyDefinition2]] if you modified the feature

    - [[IHemFeatureData::ReleaseSelectionAccess]] if you did not
    ```

  - `ReleaseSelectionAccess.md` —— 仅在正文里提到该名字：`[[IHemFeatureData::AccessSelections]] and [[IHemFeatureData::IAccessSelections]] put the model into a rollback state to allow access to the selections that define this feature.`

⇒ 结论：**⚠ 指针族**（`IHemFeatureData` 同时提供 `AccessSelections` 与 `IAccessSelections` 两个 rollback 型选区访问成员，配 `ReleaseSelectionAccess` 复原；本接口族无 `IAccessSelections2` 后继页）。

### 本仓现状（`D:\AI\SW\scripts\` 与 `D:\AI\SW\mcp-server\` 搜 `InsertSheetMetalHem` / `IHemFeatureData` / `swFmHem` / `HemFeatureData`）

- `D:\AI\SW\mcp-server\`：**0 命中**。
- `D:\AI\SW\scripts\`：10 处命中，**全部集中在 `scripts\sw_api_sldworks.py`**
  （第 274 / 4450 / 4451 / 4741 / 6348 / 12524 / 21207 / 21208 / 21494 / 23085 行）
  ⇒ 该文件是 `scripts/sw_api_*.py` 系列的**生成的反射索引**，**不是实现**（其文件头自述「**官方 API 的完整抄录** …… 逐个照抄自对官方 interop 程序集的**纯元数据反射**」）⇒ 命中它**不算**「本仓有实现」（仅反射索引，不算实现）。
- ⇒ 结论：**本仓对 `InsertSheetMetalHem` / `InsertSheetMetalHem2` / `IHemFeatureData` 没有实现**。