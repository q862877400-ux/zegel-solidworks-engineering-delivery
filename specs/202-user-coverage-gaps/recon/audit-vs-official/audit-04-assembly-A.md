# audit-04-assembly-A · 核对 A（签名一致性）

- **域**：04-assembly
- **我们这边的文件**：`scripts/sw_assembly.py`（存在，已逐条读完，877 行）
- **只做**：核对 A —— 把每个 COM 调用的**实参**与官方 `**Signature**` 的**形参表**并排数
- **官方源**（只读）：
  - `C:/swapi/types/<接口>/<成员>.md`（精确签名）
  - `C:/swapi/examples/*.md`（官方例子的实参配方）
  - `C:/swapi/enums/*.md`
  - `D:/AI/SW/AI Solidworks/官方文档/SWhelp/sldworksapi/`（CHM 解包）
  - 出厂类型库反射 `D:/AI/SW/_raw/reflect_sldworks/iface_sldworks.txt`（三源互证时作对照）
- **未跑**：SolidWorks、pytest；**未改仓内任何文件**

## 表

| # | 我们的原文（文件 + 片段） | 官方的原文（文件 + 片段） | 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | `scripts/sw_assembly.py` —— `add_mate5_checked()` 内：<br>`mate = asm_model.AddMate5(` …（返回 `Mate2`）<br>紧接其后：`if name:` → `try:` → **`mate.Name = name`** | **① `C:/swapi/index/members_by_type.md`（`IMate2` 段的 40 条成员行，15 property + 25 method）**：<br>`- [property] [Alignment](../types/IMate2/Alignment.md) — `System.int Alignment {get;}``<br>`- [property] [Type](../types/IMate2/Type.md) — `System.int Type {get;}``<br>`- [method] [MateEntity](../types/IMate2/MateEntity.md) — `MateEntity2 MateEntity( System.int Index )``<br>—— 全段**无 `Name`**。<br>**② CHM `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IMate2_members.html` 的 "Public Properties" 表**（16 行，逐行为）：<br>`Alignment`、`CanBeFlipped`、`DisplayDimension`、`DisplayDimension2`、`DistanceFirstArcCondition`、`DistanceSecondArcCondition`、`Flipped`、`HasLoadBearingFaces`、`HasTreatInterferenceAsShrinkFit`、`IsLoadBearingFacesBonded`、`LockMagneticMate`、`MateLoadReference`、`MaximumVariation`、`MinimumVariation`、`Type` —— **无 `Name`**。<br>**③ 出厂类型库反射 `## IMate2` 段（34 行）**：首行 `Boolean ForceMisalignment()`、末行 `Void SetUseMisalignedDeviationDocumentProperty(Boolean)` —— **无 `Name` / 无 `set_Name`**。 | 我们给 `AddMate5` 返回的 `Mate2` 对象 **赋了 1 个实参**（`name`），而官方**两源**（`C:/swapi` 的 IMate2 成员表 + CHM 的 `IMate2 Interface Members` 表，出厂反射第三源同）**都没有 `IMate2.Name` 这个成员** ⇒ 该实参在官方形参表里**没有对应形参可并排**（属「成员缺席」，不是「个数/顺序/类型不符」）。注：`C:/swapi/types/IMate2/` 目录下 40 个 `.md` 也无 `Name.md`。 | 高（三源一致缺席） |

## 查不到 / 未列（记「查不到」，不写进表）

- `C:/swapi/types/IMateInPlace/MateEntityType.md` 与 `MateComponentName.md` 两页**只有标题、没有 `**Signature**` 也没有 `## Parameters`**（各 10 行）⇒ 该两处签名改从 CHM 取：CHM `…IMateInPlace~MateEntityType.html` 写 `System.int MateEntityType( System.int NIndex ) {get;}`、CHM `…IMateInPlace~MateComponentName.html` 写 `System.string MateComponentName( System.int NIndex ) {get;}` ⇒ 与我们 `get_com_member(mate_in_place, "MateEntityType", index)` / `"MateComponentName", index` 的 **1 个实参**并排后**相符**，故不报。
- `C:/swapi/types/IModelDoc2/EditUnsuppress.md` 存在但**无 `## Parameters`**；`EditSuppress` / `EditUnsuppress` 在 `C:/swapi` 只挂在 `IModelDoc2` / `IPartDoc` 下（不在 `IAssemblyDoc` 下）⇒ 两处零实参与官方 `System.bool EditSuppress()` / `System.bool EditUnsuppress()` **相符**，不报。

## 结尾三行

核了 **56** 处（`sw_assembly.py` 里 56 个官方成员调用点，逐个把实参个数/顺序/类型与官方 `**Signature**` 形参表并排，并另与出厂类型库反射 `iface_sldworks.txt` 对了一遍）。
报了 **1** 条。
置信度为高的是第 **1** 条（`mate.Name = name`；`C:/swapi` 成员表 + CHM `IMate2 Interface Members` 表 + 出厂反射 `## IMate2` 段，**三源一致**都没有 `Name`）。
