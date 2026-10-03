# 特征/加厚·加厚切除（feature_thicken）

候选名：`InsertThickenFeature` / `FeatureThicken` / `IThickenFeatureData`

★★ 先说候选名命中情况（铁律 5，不许拿相近名字蒙混）：

- `InsertThickenFeature` —— 在 `C:\swapi\types\` 全递归**搜不到任何同名 md 文件** ⇒ 官方没写（此名不存在于本地官方离线源）。
- `FeatureThicken` —— 同样**搜不到任何以该名为文件名的 md**。但按功能项名称「加厚·加厚切除」换成官方实际用的词（加厚⇒BossThicken / 加厚切除⇒CutThicken）后**有命中**，逐份抄录如下。
- `IThickenFeatureData` —— 命中**同名接口目录 1 个**，无第二份同接口。

命中页（候选词逐字搜 `C:\swapi\types\` 全递归，共 7 份成员页 + 1 份接口页）：

- `C:\swapi\types\IModelDoc2\FeatureBossThicken.md`
- `C:\swapi\types\IModelDoc2\FeatureBossThicken2.md`
- `C:\swapi\types\IModelDoc2\FeatureCutThicken.md`
- `C:\swapi\types\IModelDoc2\FeatureCutThicken2.md`
- `C:\swapi\types\IFeatureManager\FeatureBossThicken.md`
- `C:\swapi\types\IFeatureManager\FeatureCutThicken.md`
- `C:\swapi\types\IModeler\ThickenSheet.md`（★ 命中 "Thicken" 但**属 `Model Interfaces`、非特征入口**，作为旁证一并抄录）
- `C:\swapi\types\IThickenFeatureData\_overview.md`

★ 注 1：**`IFeatureManager` 下没有 `FeatureBossThicken2.md`、也没有 `FeatureCutThicken2.md`** —— 全递归扫 `*Thicken*` 只得到上列 7 份。⇒ ★★ 「带 `2` 的那一代」**只存在于 `IModelDoc2` 上，而且它们自己就是 Obsolete**，指向的却是 `IFeatureManager` 上**不带 `2`** 的成员（见下方废弃链，方向与通常的 `X`→`X2` 相反）。

★ 注 2：`IFeatureManager\CreateDefinition.md` 全文搜 `hicken` ⇒ **0 命中** ⇒ 官方没写（`swFm*` 常量表里**没有**加厚这一项；本功能项**不走** `CreateDefinition` 那条路）。

（补充：`C:\swapi\types\IThickenFeatureData\` 目录下共 16 个文件 —— `_overview.md` / `AccessSelections.md` / `AutoSelect.md` / `FeatureScope.md` / `FeatureScopeBodies.md` / `FillVolume.md` / `GetFeatureScopeBodiesCount.md` / `IAccessSelections.md` / `IGetFeatureScopeBodies.md` / `IsBossFeature.md` / `ISetFeatureScopeBodies.md` / `Merge.md` / `ReleaseSelectionAccess.md` / `Surface.md` / `Thickness.md` / `ThicknessSide.md`。）

## 页头逐字段（逐字）

### 页 1 · `C:\swapi\types\IModelDoc2\FeatureBossThicken.md`（页头 → Signature 行，逐字）

```text
---
type: IModelDoc2
member: FeatureBossThicken
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IModelDoc2.FeatureBossThicken

Obsolete. Superseded by [[IFeatureManager::FeatureBossThicken]].

**Signature**: `void FeatureBossThicken( System.double Thickness, System.int Direction, System.int FaceIndex )`
```

### 页 2 · `C:\swapi\types\IModelDoc2\FeatureBossThicken2.md`（页头 → Signature 行，逐字）

```text
---
type: IModelDoc2
member: FeatureBossThicken2
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IModelDoc2.FeatureBossThicken2

Obsolete. Superseded by [[IFeatureManager::FeatureBossThicken]].

**Signature**: `void FeatureBossThicken2( System.double Thickness, System.int Direction, System.int FaceIndex, System.bool FillVolume )`
```

### 页 3 · `C:\swapi\types\IModelDoc2\FeatureCutThicken.md`（页头 → Signature 行，逐字）

```text
---
type: IModelDoc2
member: FeatureCutThicken
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IModelDoc2.FeatureCutThicken

Obsolete. Superseded by [[IFeatureManager::FeatureCutThicken]].

**Signature**: `void FeatureCutThicken( System.double Thickness, System.int Direction, System.int FaceIndex )`
```

### 页 4 · `C:\swapi\types\IModelDoc2\FeatureCutThicken2.md`（页头 → Signature 行，逐字）

```text
---
type: IModelDoc2
member: FeatureCutThicken2
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# IModelDoc2.FeatureCutThicken2

Obsolete. Superseded by [[IFeatureManager::FeatureCutThicken]].

**Signature**: `void FeatureCutThicken2( System.double Thickness, System.int Direction, System.int FaceIndex, System.bool FillVolume )`
```

### 页 5 · `C:\swapi\types\IFeatureManager\FeatureBossThicken.md`（页头 → Signature 行，逐字）

```text
---
type: IFeatureManager
member: FeatureBossThicken
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces
---

# IFeatureManager.FeatureBossThicken

Thickens the selected reference surface, and then generates a boss.

**Signature**: `Feature FeatureBossThicken( System.double Thickness, System.int Direction, System.int FaceIndex, System.bool FillVolume, System.bool Merge, System.bool UseFeatScope, System.bool UseAutoSelect )`
```

### 页 6 · `C:\swapi\types\IFeatureManager\FeatureCutThicken.md`（页头 → Signature 行，逐字）

```text
---
type: IFeatureManager
member: FeatureCutThicken
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces
---

# IFeatureManager.FeatureCutThicken

Thickens the selected reference surface feature, and then generates a cut.

**Signature**: `Feature FeatureCutThicken( System.double Thickness, System.int Direction, System.int FaceIndex, System.bool FillVolume, System.bool UseFeatScope, System.bool UseAutoSelect )`
```

### 页 7 · `C:\swapi\types\IModeler\ThickenSheet.md`（页头 → Signature 行，逐字）

```text
---
type: IModeler
member: ThickenSheet
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Model Interfaces
---

# IModeler.ThickenSheet

Thickens a sheet body.

**Signature**: `Body2 ThickenSheet( Body2 Sheet, System.double Thickness, System.int Direction )`
```

### 页 8 · `C:\swapi\types\IThickenFeatureData\_overview.md`（页头，逐字）

```text
---
name: IThickenFeatureData
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Feature Interfaces/Surfaces
is_enum: False
property_count: 8
method_count: 7
enum_member_count: 0
---
```

（该页全文 32 行，**没有 Signature 那一行** ⇒ 官方没写。）

## Signature（逐字）

- 页 1 `IModelDoc2.FeatureBossThicken`：
  `**Signature**: `void FeatureBossThicken( System.double Thickness, System.int Direction, System.int FaceIndex )``
- 页 2 `IModelDoc2.FeatureBossThicken2`：
  `**Signature**: `void FeatureBossThicken2( System.double Thickness, System.int Direction, System.int FaceIndex, System.bool FillVolume )``
- 页 3 `IModelDoc2.FeatureCutThicken`：
  `**Signature**: `void FeatureCutThicken( System.double Thickness, System.int Direction, System.int FaceIndex )``
- 页 4 `IModelDoc2.FeatureCutThicken2`：
  `**Signature**: `void FeatureCutThicken2( System.double Thickness, System.int Direction, System.int FaceIndex, System.bool FillVolume )``
- 页 5 `IFeatureManager.FeatureBossThicken`：
  `**Signature**: `Feature FeatureBossThicken( System.double Thickness, System.int Direction, System.int FaceIndex, System.bool FillVolume, System.bool Merge, System.bool UseFeatScope, System.bool UseAutoSelect )``
- 页 6 `IFeatureManager.FeatureCutThicken`：
  `**Signature**: `Feature FeatureCutThicken( System.double Thickness, System.int Direction, System.int FaceIndex, System.bool FillVolume, System.bool UseFeatScope, System.bool UseAutoSelect )``
- 页 7 `IModeler.ThickenSheet`：
  `**Signature**: `Body2 ThickenSheet( Body2 Sheet, System.double Thickness, System.int Direction )``
- 页 8 `IThickenFeatureData`（接口页）：官方没写（本页无 Signature 行）

- Obsolete:
  - 页 1 `IModelDoc2\FeatureBossThicken.md`：
    > Obsolete. Superseded by [[IFeatureManager::FeatureBossThicken]].
  - 页 2 `IModelDoc2\FeatureBossThicken2.md`：
    > Obsolete. Superseded by [[IFeatureManager::FeatureBossThicken]].
  - 页 3 `IModelDoc2\FeatureCutThicken.md`：
    > Obsolete. Superseded by [[IFeatureManager::FeatureCutThicken]].
  - 页 4 `IModelDoc2\FeatureCutThicken2.md`：
    > Obsolete. Superseded by [[IFeatureManager::FeatureCutThicken]].
  - 页 5 `IFeatureManager\FeatureBossThicken.md`：无。
  - 页 6 `IFeatureManager\FeatureCutThicken.md`：无。
  - 页 7 `IModeler\ThickenSheet.md`：无。
  - 页 8 `IThickenFeatureData\_overview.md`：无。

### ★ 废弃链（逐级追到底，后继 Signature 逐字抄录）

链 1（加厚 · Boss 侧，3 级）：

```text
IModelDoc2.FeatureBossThicken        （Obsolete → IFeatureManager::FeatureBossThicken）
IModelDoc2.FeatureBossThicken2       （Obsolete → IFeatureManager::FeatureBossThicken）★ 同指上一条的后继
        ↓
IFeatureManager.FeatureBossThicken   （★ 页 5 全文无 Obsolete 句 ⇒ 链条到此为止，不再废弃）
```

链 2（加厚切除 · Cut 侧，3 级）：

```text
IModelDoc2.FeatureCutThicken         （Obsolete → IFeatureManager::FeatureCutThicken）
IModelDoc2.FeatureCutThicken2        （Obsolete → IFeatureManager::FeatureCutThicken）★ 同指上一条的后继
        ↓
IFeatureManager.FeatureCutThicken    （★ 页 6 全文无 Obsolete 句 ⇒ 链条到此为止，不再废弃）
```

- 页 5 `IFeatureManager\FeatureBossThicken.md` 的「页头 → Signature 行」已在上面**逐字抄录**，其 Signature 为：
  `Feature FeatureBossThicken( System.double Thickness, System.int Direction, System.int FaceIndex, System.bool FillVolume, System.bool Merge, System.bool UseFeatScope, System.bool UseAutoSelect )`
- 页 6 `IFeatureManager\FeatureCutThicken.md` 的「页头 → Signature 行」已在上面**逐字抄录**，其 Signature 为：
  `Feature FeatureCutThicken( System.double Thickness, System.int Direction, System.int FaceIndex, System.bool FillVolume, System.bool UseFeatScope, System.bool UseAutoSelect )`

⇒ 本功能项**当前有效的入口只有两个**：`IFeatureManager.FeatureBossThicken`（加厚，7 参数，带 `Merge`）与 `IFeatureManager.FeatureCutThicken`（加厚切除，6 参数，**无 `Merge`**）；`IModelDoc2` 上那四个（含两个 `2` 代）全部废弃。

⚠ 逐字参数表差异（照抄，不改写）：页 5 的 `Direction` 写的是 `Direction as defined in [[swThickenThicknessType_e]]`；页 6 的 `Direction` **直接给了字面量**（`0 = Thicken side 1` / `1 = Thicken side 2` / `2 = Thicken both sides`），**没有**引用那个枚举页。另：两页的 `FaceIndex` 分别写 `Not used` 与 `Not currently used`。

## Remarks（逐字，或「本页无 ## Remarks 段」）

- 页 1 `IModelDoc2\FeatureBossThicken.md`：本页无 ## Remarks 段
- 页 2 `IModelDoc2\FeatureBossThicken2.md`：本页无 ## Remarks 段
- 页 3 `IModelDoc2\FeatureCutThicken.md`：本页无 ## Remarks 段
- 页 4 `IModelDoc2\FeatureCutThicken2.md`：本页无 ## Remarks 段
- 页 5 `IFeatureManager\FeatureBossThicken.md`：**有** `## Remarks`，逐字全文如下 ——

```text
## Remarks
This method generates a boss feature by thickening a selected reference surface.  The surface must be selected with a mark of 1. See [[IModelDocExtension::SelectByID2]] for details.

If FillVolume is true, other arguments are ignored. A closed surface is required when FillVolume is true.

If UseAutoSelect is false, the user must select the bodies that the feature will affect.
```

- 页 6 `IFeatureManager\FeatureCutThicken.md`：**有** `## Remarks`，逐字全文如下 ——

```text
## Remarks
This method creates a cut feature by thickening a selected reference surface. If FillVolume is True, other arguments are ignored. A closed surface is required when FillVolume is True.

When UseAutoSelect is false, the user must select the bodies that the feature will affect.

When using cut or cavity features that result in multiple bodies, you cannot select to keep all of the resulting bodies or one or more selected bodies.
```

- 页 7 `IModeler\ThickenSheet.md`：**有** `## Remarks`，逐字全文如下 ——

```text
## Remarks
If you set Direction to swThickenDirection_Both, then the value set for Thickness is used in both directions.
```

- 页 8 `IThickenFeatureData\_overview.md`：本页无 ## Remarks 段（该页只有 `## Description` / `## Members` / `## Examples` / `## See Also`）

## Examples

- 页 1 `IModelDoc2\FeatureBossThicken.md`：无（本页无 ## Examples 段）
- 页 2 `IModelDoc2\FeatureBossThicken2.md`：无（本页无 ## Examples 段）
- 页 3 `IModelDoc2\FeatureCutThicken.md`：无（本页无 ## Examples 段）
- 页 4 `IModelDoc2\FeatureCutThicken2.md`：无（本页无 ## Examples 段）
- 页 5 `IFeatureManager\FeatureBossThicken.md`：
  - `Create Thicken Feature (VBA)` → `../../examples/Create_Thicken_Feature_Example_VB.md`
  - `Fill Holes in Part (C#)` → `../../examples/Fill_Holes_in_Part_Example_CSharp.md`
  - `Fill Holes in Part (VB.NET)` → `../../examples/Fill_Holes_in_Part_Example_VBNET.md`
  - `Fill Holes in Part (VBA)` → `../../examples/Fill_Holes_in_Part_Example_VB.md`
  - `Thicken Surface and Generate Boss (VBA)` → `../../examples/Thicken_Surface_and_Generate_Boss_Example_VB.md`
  - `Thicken Surface and Generate Boss (VB.NET)` → `../../examples/Thicken_Surface_and_Generate_Boss_Example_VBNET.md`
  - `Thicken Surface and Generate Boss (C#)` → `../../examples/Thicken_Surface_and_Generate_Boss_Example_CSharp.md`
- 页 6 `IFeatureManager\FeatureCutThicken.md`：无（本页无 ## Examples 段）★ 逐字核实：该页第 39–46 行直接就是 `## See Also`
- 页 7 `IModeler\ThickenSheet.md`：
  - `Thicken Sheet Body (VBA)` → `../../examples/Thicken_Sheet_Body_Example_VB.md`
- 页 8 `IThickenFeatureData\_overview.md`：
  - `Create Thicken Feature (VBA)` → `../../examples/Create_Thicken_Feature_Example_VB.md`
  - `Thicken Surface and Generate Boss (VBA)` → `../../examples/Thicken_Surface_and_Generate_Boss_Example_VB.md`
  - `Thicken Surface and Generate Boss (VB.NET)` → `../../examples/Thicken_Surface_and_Generate_Boss_Example_VBNET.md`
  - `Thicken Surface and Generate Boss (C#)` → `../../examples/Thicken_Surface_and_Generate_Boss_Example_CSharp.md`

★ 上述 8 份例子文件在 `C:\swapi\examples\` 下**全部已核实存在**（`Create_Thicken_Feature_Example_VB.md` / `Fill_Holes_in_Part_Example_CSharp.md` / `Fill_Holes_in_Part_Example_VBNET.md` / `Fill_Holes_in_Part_Example_VB.md` / `Thicken_Surface_and_Generate_Boss_Example_VB.md` / `Thicken_Surface_and_Generate_Boss_Example_VBNET.md` / `Thicken_Surface_and_Generate_Boss_Example_CSharp.md` / `Thicken_Sheet_Body_Example_VB.md`）。

## 指针族 / 本仓现状

### AccessSelections 全文搜（命中页逐份判定）

- 页 1 `IModelDoc2\FeatureBossThicken.md`：全文无 `AccessSelections` ⇒ —
- 页 2 `IModelDoc2\FeatureBossThicken2.md`：全文无 `AccessSelections` ⇒ —
- 页 3 `IModelDoc2\FeatureCutThicken.md`：全文无 `AccessSelections` ⇒ —
- 页 4 `IModelDoc2\FeatureCutThicken2.md`：全文无 `AccessSelections` ⇒ —
- 页 5 `IFeatureManager\FeatureBossThicken.md`：全文无 `AccessSelections` ⇒ —
- 页 6 `IFeatureManager\FeatureCutThicken.md`：全文无 `AccessSelections` ⇒ —
- 页 7 `IModeler\ThickenSheet.md`：全文无 `AccessSelections` ⇒ —
- 页 8 `IThickenFeatureData\_overview.md`：全文无 `AccessSelections` ⇒ —
- ★ 接口目录 `C:\swapi\types\IThickenFeatureData\` 内另有**两个**页含 `AccessSelections` ⇒ **⚠ 指针族**：
  - `AccessSelections.md` — `System.bool AccessSelections( System.object TopDoc, System.object Component )`（该页**有** `## Remarks`，逐字全文如下 ——）

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

    - [[IThickenFeatureData::ReleaseSelectionAccess]] if you did not
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

    - [[IFeature::ModifyDefinition]] or [[IFeature::IModifyDefinition2]] if you modified the feature

    - [[IThickenFeatureData::ReleaseSelectionAccess]] if you did not
    ```

  - `ReleaseSelectionAccess.md` —— 仅在正文里提到该名字（见该页）。

⇒ 结论：**⚠ 指针族**（`IThickenFeatureData` 同时提供 `AccessSelections`（`System.object` 版）与 `IAccessSelections`（`ModelDoc2`/`Component2` 强类型版）两个 rollback 型选区访问成员，配 `ReleaseSelectionAccess` 复原；本接口族**无 `IAccessSelections2` 后继页** ⇒ 无后继链）。★ 注意：**6 个特征入口页本身一个 `AccessSelections` 都没有** ⇒ 走的是**直接调用入口**，不是指针族路径；指针族只在 `IFeature.GetDefinition` 改定义那条路上。

### 本仓现状（`D:\AI\SW\scripts\` 与 `D:\AI\SW\mcp-server\` 搜 `FeatureBossThicken` / `FeatureCutThicken` / `InsertThickenFeature` / `IThickenFeatureData` / `ThickenSheet`）

- `D:\AI\SW\mcp-server\`：这些成员名 **0 命中**。（全文搜小写 `thicken` 只有 2 处，都在 `mcp-server\server.py` 第 473 / 1381 行，**是 CadStudio / OCP 那条"smooth loft, sweep, knit, or thicken"白名单的描述文字，与 SolidWorks `feature_thicken` 无关**。）
- `D:\AI\SW\scripts\`：38 处命中，分两类 ——
  1. **`scripts\sw_api_sldworks.py`**（37 处：第 556 / 4283 / 4294 / 5529 / 5530 / 5540 / 5541 / 6132 / 6133 / 6146 / 6147 / 7037 / 9322 / 16878 / 21040 / 21051 / 22266 / 22267 / 22277 / 22278 / 22869 / 22870 / 22883 / 22884 / 23774 / 25997）—— 该文件属 `scripts/sw_api_*.py` 系列，是**生成的反射索引**，**不是实现** ⇒ 命中它**不算**「本仓有实现」（仅反射索引，不算实现）。
  2. **`scripts\sw_surface_features.py`** —— ★★ **这里才是真实现**：
     - 第 247 行 `def thicken_surface_report(model, thickness_mm: float, *, direction=0, fill_volume=True, merge=True, use_feat_scope=False, use_auto_select=True)`；
     - 第 317–320 行**真调** `get_com_member(fm, "FeatureBossThicken", th * 0.001, int(direction), 0, bool(fill_volume), bool(merge), bool(use_feat_scope), bool(use_auto_select))` ⇒ **7 参、顺序与官方 Signature 一致**，第 315–316 行注释明写「官方 `FaceIndex` 标注「Not used」故传 0」。
     - 第 234–241 行的来源块已逐字引用官方页 `IFeatureManager\FeatureBossThicken.md` 与 `IModelDoc2\FeatureBossThicken.md`（并注明后者 Obsolete）。
     - ★ 该文件 docstring（第 260–299 行）自带**真机总账**：轮 502/503 的 `IFeatureManager.FeatureBossThicken` 共 7 组、轮 504 的 `IModelDoc2.FeatureBossThicken`（3 参 · Obsolete）共 3 组，**共 11 组全部返回 `None`、特征树不动**（前置每次 `solid=0 · surface=1` 都完美）⇒ 官方原文「**⚠ 按 A4 不登记成工具、不写 `verified`**」。证据文件：`output/thicken-surface-evidence.json` · `output/thicken-matrix-evidence.json` · `output/thicken-obsolete-entry-evidence.json`；探针 `tools\probe_thicken_matrix.py`（轮 503）、`tools\prove_thicken_surface.py`（轮 502，第 73 行调 `SF.thicken_surface_report`）。
  3. **`FeatureCutThicken`（加厚切除）在 `scripts/` 与 `mcp-server/` 里除反射索引外 0 命中** ⇒ ★ **本仓对「加厚切除」没有任何实现**（连调用点都没有）。
- ⇒ 结论：**本仓对 `feature_thicken` 只覆盖了「加厚」一半**（`scripts/sw_surface_features.py::thicken_surface_report`，走 `IFeatureManager.FeatureBossThicken`，但真机 11 组全 `None`，未登记为工具）；**「加厚切除」（`IFeatureManager.FeatureCutThicken`）本仓没有实现**；**指针族 `IThickenFeatureData` 的 `AccessSelections` / `IAccessSelections` 本仓没有实现**。
