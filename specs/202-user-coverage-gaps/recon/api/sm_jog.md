# 钣金/转折（sm_jog）

候选成员名：`InsertSheetMetalJog` / `IJogFeatureData`

**找页方式**：按候选名在 `C:\swapi\types\` 下递归 glob（`**/*Jog*.md` + `**/IJog*.md`）。
命中（**4 份**，候选名直接命中，无需英文关键词回退）：
`C:\swapi\types\IModelDoc2\InsertSheetMetalJog.md` ·
`C:\swapi\types\IJogFeatureData\_overview.md` ·
`C:\swapi\types\IJogFeatureData\JogAngle.md` ·
`C:\swapi\types\IJogFeatureData\JogPositionType.md`

★ 全仓 grep `Obsolete` 在 `C:\swapi\types\IJogFeatureData\`（22 份）与 `IModelDoc2\InsertSheetMetalJog.md` 中**零命中** ⇒ **未判为废弃**，无后继链可追。
★ `C:\swapi\types\IFeatureManager\CreateDefinition.md` 中 grep `swFmJog|swFmSMJog|Jog` **零命中** ⇒ 该页的常量表里没有转折项（本项**不在** CreateDefinition 入口表内）。

---

## 页头逐字段（逐字）

### ① `C:\swapi\types\IModelDoc2\InsertSheetMetalJog.md`

```
---
type: IModelDoc2
member: InsertSheetMetalJog
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IModelDoc2.InsertSheetMetalJog

Inserts a sheet metal jog in the current model document.

**Signature**: `void InsertSheetMetalJog( System.double Angle, System.double Radius, System.double OffsetDist, System.bool FlipDir, System.bool FixProjLen, System.short DimPos, System.short BendPos )`
```

### ② `C:\swapi\types\IJogFeatureData\_overview.md`

```
---
name: IJogFeatureData
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Sheet Metal
is_enum: False
property_count: 14
method_count: 8
enum_member_count: 0
---

# IJogFeatureData

## Description
Allows access to a jog feature.

## Members
- **Properties**: 14
- **Methods**: 8
```

★ 该页**没有 `**Signature**:` 行**（接口总览页，非成员页）⇒ 页头到 Signature 段在此中断。

### ③ `C:\swapi\types\IJogFeatureData\JogAngle.md`

```
---
type: IJogFeatureData
member: JogAngle
kind: property
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Sheet Metal
---

# IJogFeatureData.JogAngle

Gets or sets the jog angle for this jog feature.

**Signature**: `System.double JogAngle {get; set;}`
```

### ④ `C:\swapi\types\IJogFeatureData\JogPositionType.md`

```
---
type: IJogFeatureData
member: JogPositionType
kind: property
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Sheet Metal
---

# IJogFeatureData.JogPositionType

Gets or sets the jog position type for this jog feature.

**Signature**: `System.int JogPositionType {get; set;}`
```

---

## Signature（逐字）

- ① `IModelDoc2.InsertSheetMetalJog`（方法）：
  `void InsertSheetMetalJog( System.double Angle, System.double Radius, System.double OffsetDist, System.bool FlipDir, System.bool FixProjLen, System.short DimPos, System.short BendPos )`
- ② `IJogFeatureData`（接口总览页）：本页无 Signature 行 ⇒ **官方没写**
- ③ `IJogFeatureData.JogAngle`（属性）：
  `System.double JogAngle {get; set;}`
- ④ `IJogFeatureData.JogPositionType`（属性）：
  `System.int JogPositionType {get; set;}`

★ `InsertSheetMetalJog.md` 的 `## Parameters` 原文（逐字，未改动）：
```
## Parameters
- **Angle**: Jog angle
- **Radius**: Jog radius
- **OffsetDist**: Offset distance
- **FlipDir**: True flips the jog direction, false does not
- **FixProjLen**: True fixes the projected length, false does not
- **DimPos**: Dimension position
- **BendPos**: Bend position
```
★ 该页**未对 `DimPos` / `BendPos` 给出任何枚举交叉链接**（`## See Also` 只有三条，见下）⇒ **官方没写**其枚举取值来源。
★ 该页 `## See Also` 原文（逐字）：
```
## See Also

- [[IModelDoc2 Interface]]
- [[IModelDoc2 Members]]
- [[IJogFeatureData Interface]]
```

### Obsolete

- ① `IModelDoc2.InsertSheetMetalJog`：**无**
- ② `IJogFeatureData`（总览页）：**无**
- ③ `IJogFeatureData.JogAngle`：**无**
- ④ `IJogFeatureData.JogPositionType`：**无**

⇒ 四份命中页的「页头 → Signature」段内**均未出现 Obsolete 句**（已逐字通读，无省略）。
⇒ 判为**非废弃** ⇒ 不存在后继页、无后继链需追。

---

## Remarks（逐字，或「本页无 ## Remarks 段」）

判据＝该页**有没有 `## Remarks` 这个标题**。

- ① `C:\swapi\types\IModelDoc2\InsertSheetMetalJog.md`：**本页无 ## Remarks 段**（全文 29 行，逐字读完，段落序列为 frontmatter → 标题 → 描述 → Signature → Parameters → See Also）
- ② `C:\swapi\types\IJogFeatureData\_overview.md`：**本页无 ## Remarks 段**（段落序列为 frontmatter → 标题 → Description → Members → Examples → See Also）
- ③ `C:\swapi\types\IJogFeatureData\JogAngle.md`：**本页无 ## Remarks 段**（段落序列为 frontmatter → 标题 → 描述 → Signature → Returns → See Also）
- ④ `C:\swapi\types\IJogFeatureData\JogPositionType.md`：**本页无 ## Remarks 段**（段落序列同上，Returns 为 `Position type as defined in [[swJogPositionType_e]]`）

★ 四份命中页的 `## See Also` 原文（逐字）：
- ① `- [[IModelDoc2 Interface]]` / `- [[IModelDoc2 Members]]` / `- [[IJogFeatureData Interface]]`
- ② `- [[IJogFeatureData Members]]` / `- [[SolidWorks.Interop.sldworks Namespace]]` / `- [[IModelDoc2::InsertSheetMetalJog Method]]`
- ③ `- [[IJogFeatureData Interface]]` / `- [[IJogFeatureData Members]]`
- ④ `- [[IJogFeatureData Interface]]` / `- [[IJogFeatureData Members]]`

★ ★ **指针族的 Remarks 在同一候选接口的另两页上有，逐字抄录**（因它们是本项唯一的 Remarks 载体）：

`C:\swapi\types\IJogFeatureData\AccessSelections.md`（第 23–43 行，逐字）：
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

- [[IFeature::ModifyDefinition]] if you modified the feature

- [[IJogFeatureData::ReleaseSelectionAccess]] if you did not
```

`C:\swapi\types\IJogFeatureData\IAccessSelections.md`（第 23–43 行，逐字；★ 与上页**仅一行不同**，如实照抄）：
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

- [[IFeature::IModifyDefintion2]] if you modified the feature

- [[IJogFeatureData::ReleaseSelectionAccess]] if you did not
```
（上方 `IModifyDefintion2` 的拼写**是官方原文的拼写**，未纠正。）

---

## Examples

- ① `IModelDoc2.InsertSheetMetalJog`：**无**（该页无 `## Examples` 段）
- ② `IJogFeatureData`（总览页，有 `## Examples` 段）——逐字：
  ```
  ## Examples
  - [Get All Sheet Metal Feature Data (VBA)](../../examples/Get_All_Sheet_Metal_Feature_Data_Example_VB.md)
  - [Get All Sheet Metal Feature Data (VB.NET)](../../examples/Get_All_Sheet_Metal_Feature_Data_Example_VBNET.md)
  - [Get All Sheet Metal Feature Data (C#)](../../examples/Get_All_Sheet_Metal_Feature_Data_Example_CSharp.md)
  ```
  ⇒ 例子文件名（3 个）：
  - `Get_All_Sheet_Metal_Feature_Data_Example_VB.md`
  - `Get_All_Sheet_Metal_Feature_Data_Example_VBNET.md`
  - `Get_All_Sheet_Metal_Feature_Data_Example_CSharp.md`
- ③ `IJogFeatureData.JogAngle`：**无**
- ④ `IJogFeatureData.JogPositionType`：**无**

★ `IJogFeatureData` 接口目录（`C:\swapi\types\IJogFeatureData\`，共 22 份 md）中另有 1 页带 `## Examples` 段：`UseDefaultBendRadius.md`（非本次命中页，未展开抄录）。

---

## 指针族 / 本仓现状

### 指针族

- **四份命中页全文搜 `AccessSelections`：—（零命中）。**
- **但同一候选接口 `IJogFeatureData` 内确实存在指针族** ⇒ **⚠ 指针族**：
  - `IJogFeatureData.AccessSelections` — `System.bool AccessSelections( System.object TopDoc, System.object Component )`
  - `IJogFeatureData.IAccessSelections` — `System.bool IAccessSelections( ModelDoc2 TopDoc, Component2 Component )`
  （`I` 前缀者为 `AccessSelections` 的指针变体；两页均带 `## Remarks`，已在上节逐字抄录。）

### 本仓现状

范围：`D:\AI\SW\scripts\` 与 `D:\AI\SW\mcp-server\`。grep 模式 `InsertSheetMetalJog|IJogFeatureData|swFmJog|swFmSMJog`。

| 目录 | 命中文件 | 判定 |
|---|---|---|
| `D:\AI\SW\scripts\` | `scripts\sw_api_sldworks.py`（6 处：L292 / L4868 / L6349 / L12739 / L21617 / L23086） | ★ **按规矩排除** —— 属 `scripts/sw_api_*.py` 生成反射索引，**不是实现** ⇒ **（仅反射索引，不算实现）** |
| `D:\AI\SW\mcp-server\` | **0 命中** | — |

⇒ **本仓 `scripts/` 与 `mcp-server/` 内无该成员的实现**（`mcp-server/` 零命中；`scripts/` 唯一命中是被排除的反射索引）。

★ 同名/同串在 `scripts\` 与 `mcp-server\` **之外**出现的位置（**均非实现**，据实登记，不作任何推断）：
`docs\api-map.json` · `docs\family-coverage.md` · `docs\family-coverage.json` · `makepy-property-direction.json` · `solidpilot-salvage\调研\官方API全量清单.csv` · `specs\202-user-coverage-gaps\research.md` · `_all_families.json` · `_complete_families.json` · `_merged_test.py` · `_reg_low.json` · `_regen_sw_sldworks_remaining.json`

### 附：官方枚举页（本项参数相关的、在 `C:\swapi\enums\` 下存在的三份）

- `C:\swapi\enums\swJogDimensionPositionType_e.md`
- `C:\swapi\enums\swJogOffsetTypes_e.md`
- `C:\swapi\enums\swJogPositionType_e.md`

★ 其中**只有** `swJogPositionType_e` 被命中页正文交叉引用（`JogPositionType.md` 的 `## Returns`：`Position type as defined in [[swJogPositionType_e]]`）。
★ `swJogDimensionPositionType_e` 与 `swJogOffsetTypes_e` 在四份命中页中**零交叉引用** ⇒ 与 `DimPos` / `BendPos` 的对应关系**官方没写**（本页不做配对推断）。