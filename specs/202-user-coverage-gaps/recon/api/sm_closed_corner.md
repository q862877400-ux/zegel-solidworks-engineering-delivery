# 钣金/闭合角（sm_closed_corner）

候选名：`InsertSheetMetalClosedCorner` / `IClosedCornerFeatureData`

## 页头逐字段（逐字）

命中页（候选名逐字搜 `C:\swapi\types\` 全递归，命中 3 份；同名接口只有 1 个目录，无第二份接口）：

- `C:\swapi\types\IModelDoc2\InsertSheetMetalClosedCorner.md`
- `C:\swapi\types\IClosedCornerFeatureData\_overview.md`
- `C:\swapi\types\IClosedCornerFeatureData\CornerType.md`

（补充：`C:\swapi\types\IClosedCornerFeatureData\` 目录下共 14 个文件 —— `_overview.md` / `AccessSelections.md` / `CornerType.md` / `Faces.md` / `GapDistance.md` / `IAccessSelections.md` / `IAccessSelections2.md` / `IGetFaces.md` / `IGetFacesCount.md` / `ISetFaces.md` / `OpenBendRegion.md` / `OverlapUnderlapRatio.md` / `ReleaseSelectionAccess.md`。）

### 页 1 · `C:\swapi\types\IModelDoc2\InsertSheetMetalClosedCorner.md`（页头 → Signature 行，逐字）

```text
---
type: IModelDoc2
member: InsertSheetMetalClosedCorner
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IModelDoc2.InsertSheetMetalClosedCorner

Inserts a sheet metal closed corner into this model document.

**Signature**: `void InsertSheetMetalClosedCorner()`
```

### 页 2 · `C:\swapi\types\IClosedCornerFeatureData\_overview.md`（页头，逐字）

```text
---
name: IClosedCornerFeatureData
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Sheet Metal
is_enum: False
property_count: 5
method_count: 7
enum_member_count: 0
---
```

（该页全文 30 行，**没有 Signature 那一行** ⇒ 官方没写。）

### 页 3 · `C:\swapi\types\IClosedCornerFeatureData\CornerType.md`（页头 → Signature 行，逐字）

```text
---
type: IClosedCornerFeatureData
member: CornerType
kind: property
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Sheet Metal
---

# IClosedCornerFeatureData.CornerType

Gets or sets the closed corner type.

**Signature**: `System.int CornerType {get; set;}`
```

## Signature（逐字）

- 页 1 `IModelDoc2.InsertSheetMetalClosedCorner`：`**Signature**: `void InsertSheetMetalClosedCorner()``
- 页 2 `IClosedCornerFeatureData`（接口页）：官方没写（本页无 Signature 行）
- 页 3 `IClosedCornerFeatureData.CornerType`：`**Signature**: `System.int CornerType {get; set;}``

- Obsolete:
  - 页 1：无。
  - 页 2：无。
  - 页 3：无。
  - ★ 但接口内另有 Obsolete 成员（逐字原文照抄）：
    - `C:\swapi\types\IClosedCornerFeatureData\IAccessSelections.md`（该页页头 → Signature 逐字）：
      ```text
      ---
      type: IClosedCornerFeatureData
      member: IAccessSelections
      kind: method
      assembly: SolidWorks.Interop.sldworks
      namespace: SolidWorks.Interop.sldworks
      category: Feature Interfaces/Sheet Metal
      ---

      # IClosedCornerFeatureData.IAccessSelections

      Obsolete. Superseded by [[IClosedCornerFeatureData::IAccessSelections2]].

      **Signature**: `System.bool IAccessSelections( ModelDoc TopDoc, Component Component )`
      ```
      ★ 废弃链（逐级追到底）：`IClosedCornerFeatureData.IAccessSelections`（Obsolete）→ `IClosedCornerFeatureData.IAccessSelections2`（后继，**不再废弃**）→ 到此为止。
      后继 `C:\swapi\types\IClosedCornerFeatureData\IAccessSelections2.md`（该页页头 → Signature 逐字）：
      ```text
      ---
      type: IClosedCornerFeatureData
      member: IAccessSelections2
      kind: method
      assembly: SolidWorks.Interop.sldworks
      namespace: SolidWorks.Interop.sldworks
      category: Feature Interfaces/Sheet Metal
      ---

      # IClosedCornerFeatureData.IAccessSelections2

      Gains access to the selections that describe this closed corner feature.

      **Signature**: `System.bool IAccessSelections2( ModelDoc2 TopDoc, Component2 Component )`
      ```

## Remarks（逐字，或「本页无 ## Remarks 段」）

- 页 1 `IModelDoc2.InsertSheetMetalClosedCorner.md`：本页无 ## Remarks 段
- 页 2 `IClosedCornerFeatureData\_overview.md`：本页无 ## Remarks 段
- 页 3 `IClosedCornerFeatureData\CornerType.md`：本页无 ## Remarks 段

（Obsolete 链两页的 Remarks：`IAccessSelections.md` 本页无 ## Remarks 段；`IAccessSelections2.md` **有** `## Remarks`，逐字全文如下 ——）

```text
## Remarks
Remarks

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

- [[IClosedCornerFeatureData::ReleaseSelectionAccess]] if you did not
```

## Examples

- 页 1 `IModelDoc2.InsertSheetMetalClosedCorner.md`：无（本页无 ## Examples 段）
- 页 2 `IClosedCornerFeatureData\_overview.md`：
  - `Create and Modify Closed Corner Feature (C#)` → `../../examples/Create_and_Modify_Closed_Corner_Feature_Example_CSharp.md`
  - `Create and Modify Closed Corner Feature (VB.NET)` → `../../examples/Create_and_Modify_Closed_Corner_Feature_Example_VBNET.md`
  - `Create and Modify Closed Corner Feature (VBA)` → `../../examples/Create_and_Modify_Closed_Corner_Feature_Example_VB.md`
- 页 3 `IClosedCornerFeatureData.CornerType`：
  - `Create and Modify Closed Corner Feature (C#)` → `../../examples/Create_and_Modify_Closed_Corner_Feature_Example_CSharp.md`
  - `Create and Modify Closed Corner Feature (VB.NET)` → `../../examples/Create_and_Modify_Closed_Corner_Feature_Example_VBNET.md`
  - `Create and Modify Closed Corner Feature (VBA)` → `../../examples/Create_and_Modify_Closed_Corner_Feature_Example_VB.md`

## 指针族 / 本仓现状

### AccessSelections 全文搜（命中页 3 份逐份判定）

- 页 1 `InsertSheetMetalClosedCorner.md`：全文无 `AccessSelections` ⇒ —
- 页 2 `_overview.md`：全文无 `AccessSelections` ⇒ —
- 页 3 `CornerType.md`：全文无 `AccessSelections` ⇒ —
- ★ 接口目录内另有三个 AccessSelections 族成员页 ⇒ ⚠ 指针族：
  - `AccessSelections` — `System.bool AccessSelections( System.object TopDoc, System.object Component )`（该页**有** `## Remarks`，逐字全文如下 ——）
    ```text
    ## Remarks
    Remarks

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

    - [[IClosedCornerFeatureData::ReleaseSelectionAccess]] if you did not
    ```
  - `IAccessSelections` — `System.bool IAccessSelections( ModelDoc TopDoc, Component Component )`（Obsolete，见上）
  - `IAccessSelections2` — `System.bool IAccessSelections2( ModelDoc2 TopDoc, Component2 Component )`

### 本仓现状（`D:\AI\SW\scripts\` 与 `D:\AI\SW\mcp-server\` 搜 `ClosedCorner`）

- `D:\AI\SW\mcp-server\`：0 命中。
- `D:\AI\SW\scripts\`：8 处命中，**全部集中在 `scripts\sw_api_sldworks.py`**
  （第 133 / 2440 / 5726 / 6345 / 10727 / 19343 / 22463 / 23082 行）
  ⇒ 该文件是 `scripts/sw_api_*.py` 系列的**生成的反射索引**，**不是实现** ⇒ 命中它**不算**「本仓有实现」（仅反射索引，不算实现）。
- ⇒ 结论：**本仓对 `InsertSheetMetalClosedCorner` / `IClosedCornerFeatureData` 没有实现**。

### 附：本仓其它目录里出现该名字的地方（仅登记，不算实现）

- `D:\AI\SW\tools\audit_gap_implementations.py:50` —— 字符串 `"钣金/闭合角转折褶边": ["InsertClosedCorner", "InsertJog", "InsertHem"]`（清单里的名字 `InsertClosedCorner` **不是**官方成员名）。
- `D:\AI\SW\docs\ROADMAP.md:57` —— 清单里出现 `InsertSheetMetalClosedCorner`。
- `D:\AI\SW\docs\family-coverage.md:519` / `docs\family-coverage.json`、`docs\api-map.json`、`makepy-property-direction.json`、`_merged_test.py`、`_all_families.json`、`_complete_families.json`、`_reg_low.json`、`_regen_sw_sldworks_remaining.json`、`solidpilot-salvage\调研\官方API全量清单.csv` —— 索引 / 统计产物，**非实现**。
- `D:\AI\SW\specs\202-user-coverage-gaps\research.md:50` —— 已有条目：「钣金/闭合角 | ~~`InsertClosedCorner`~~ | **`InsertSheetMetalClosedCorner`**」。
