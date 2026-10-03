# audit-08 · 域 `08-mold-costing` · 核对 A（签名一致性）

**范围**：域 `08-mold-costing` ∩ 核对 A（把我们的调用**逐个实参**与官方 Signature 的**形参表**并排数 ⇒ 参数个数 / 顺序 / 明显类型）
**我方文件**：`scripts/sw_mold.py` · `scripts/sw_measure.py`（两份都在，无替代文件）
**官方源**：`C:\swapi\types\<接口>\<成员>.md` 的 `**Signature**` 行 · `C:\swapi\examples\*.md` 的调用序 · `C:\swapi\enums\*.md` · CHM 解包 `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\*.html` 的 .NET Syntax · 出厂类型库反射 `D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt`
**纪律**：只报「两段原文对不上」；给不出两段的不写；不下结论、不给建议。

---

## 表

| # | 我们的原文（文件 + 片段） | 官方的原文（文件 + 片段） | 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | `scripts/sw_measure.py`（`measure_selection_report`）：<br>`        ok_calc = _get(m, "Calculate")`<br>（★ 同行上一段的注释自己写着：<br>`#: ★★★ 2026-10-01（轮 311）**真机：`Calculate` 必须无参调**（★ 事实 227）——`） | ① `C:\swapi\types\IMeasure\Calculate.md`：<br>`**Signature**: `System.bool Calculate( System.object Entities )``<br>`- **Entities**: Array of entities to measure; if NULL, then this method measures the selected entities`<br>② `C:\swapi\examples\Measure_Selected_Entities_Example_CSharp.md`：<br>`            status = swMeasure.Calculate(null);`<br>③ `C:\swapi\examples\Measure_Selected_Entities_Example_VBNET.md`：<br>`        status = swMeasure.Calculate(Nothing)`<br>④ 出厂类型库反射 `D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt`：<br>`  Boolean Calculate(Object)`<br>⑤ CHM 解包 `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IMeasure~Calculate.html`：<br>`value = instance.Calculate(Entities)` | 官方四处**一致**给出**形参 1 个**（`Entities`），且两个官方例子都**显式传了 1 个实参**（`null` / `Nothing`）、出厂类型库同样是 1 个形参；我方这一行**没有传任何实参** ⇒ 实参个数 0 ≠ 形参个数 1。（`get_com_member` 的无实参分支按其 docstring「无实参 ⇒ 会**先无参调一次**」走，即以 0 参去调这个 1 形参的方法。） | 高 |

---

## 核对覆盖（逐点数的，不含"看起来没问题"的推断）

### `scripts/sw_mold.py` —— 14 个成员 / 21 个调用站点

| 成员（我方调用形态） | 官方形参个数（两源并排） | 我方实参个数 | 结果 |
|---|---|---|---|
| `fm = get_com_member(model, "FeatureManager")` | property，0 | 0 | 一致（5 个站点） |
| `get_com_member(fm, "InsertMoldPartingLine", bool(draft_analysis))` | `Feature InsertMoldPartingLine( System.bool BFlipDir )` / 反射 `Feature InsertMoldPartingLine(Boolean)` = 1 | 1 | 一致 |
| `get_com_member(fm, "InsertMoldPartingSurface", int(surface_type), bool(flip), bool(use_trim), float(distance), float(angle), int(option), float(tolerance), bool(alternate))` | `Feature InsertMoldPartingSurface( System.int Radiate, System.bool ReverseAlignment, System.bool ReverseOffset, System.double OffsetDistance, System.double Angle, System.int Smooth, System.double SmoothDistance, System.bool Knit )` / 反射同名 8 型 = 8 | 8 | 一致（8 个实参类型逐位对上：Int32, Boolean, Boolean, Double, Double, Int32, Double, Boolean） |
| `call_com_member(fm, "InsertMoldShutOffSurface")` | `Feature InsertMoldShutOffSurface()` / 反射 `Feature InsertMoldShutOffSurface()` = 0 | 0 | 一致 |
| `get_com_member(fm, "InsertMoldCoreCavitySolids", float(scale), float(thickness), bool(flip), float(offset))` | `Feature InsertMoldCoreCavitySolids( System.double Dist1, System.double Dist2, System.bool Setback, System.double Angle )` / CHM `Feature InsertMoldCoreCavitySolids( System.double Dist1, System.double Dist2, System.bool Setback, System.double Angle )` = 4 | 4 | 一致（Double, Double, Boolean, Double 逐位对上） |
| `get_com_member(model, "MoldDraftAnalysis", float(draft_angle_deg), int(analysis_type), colors, int(option))` | `void MoldDraftAnalysis( System.double Angle, System.int Options, System.object Colors, System.int Shows )` / CHM `void MoldDraftAnalysis( System.double Angle, System.int Options, System.object Colors, System.int Shows )` / 反射 `Void MoldDraftAnalysis(Double, Int32, Object, Int32)` = 4 | 4 | 一致（第 3 位形参类型是 `System.object`，我方传标量 `colors` 未与该形参类型冲突） |
| `get_com_member(fm, "MoldUndercutDetect", int(col_undercut), int(col_base), bool(b_coord_input), float(dx), float(dy), float(dz))` | `void MoldUndercutDetect( System.int ColUndercut, System.int ColBase, System.bool BCoordInput, System.double Dx, System.double Dy, System.double Dz )` / CHM VB 声明 6 参同型 / 反射 `Void MoldUndercutDetect(Int32, Int32, Boolean, Double, Double, Double)` = 6 | 6 | 一致 |
| `get_com_member(feat, "Name")` | property，0 | 0 | 一致（4 个站点） |
| `_count("GetPartingLinesCount")` / `"GetPartingSurfacesCount"` / `"GetCavitySurfacesCount"` / `"GetCoreSurfacesCount"` | `System.int GetPartingLinesCount()` · `System.int GetPartingSurfacesCount()` · `System.int GetCavitySurfacesCount()` · `System.int GetCoreSurfacesCount()` = 各 0 | 0 | 一致（4 个成员，各 0） |
| `_prop("PartingType")` / `_prop("CoreCavitySplit")` | `System.int PartingType {get; set;}` · `System.bool CoreCavitySplit {get; set;}` = 各 0 | 0 | 一致（2 个成员，各 0） |

### `scripts/sw_measure.py` —— 24 个成员 / 24 个调用站点

| 成员（我方调用形态） | 官方形参个数（两源并排） | 我方实参个数 | 结果 |
|---|---|---|---|
| `_get(_get(model, "SelectionManager"), "GetSelectedObjectCount2", -1)` | `System.int GetSelectedObjectCount2( System.int Mark )` / 反射 `Int32 GetSelectedObjectCount2(Int32)` = 1 | 1 | 一致 |
| `_get(model, "Extension")` | `ModelDocExtension Extension {get;}` = 0 | 0 | 一致 |
| `_get(ext, "CreateMeasure")` | `Measure CreateMeasure()` = 0 | 0 | 一致 |
| `_set(m, "ArcOption", opt)` | `System.int ArcOption {get; set;}` = 写侧 1 | 1 | 一致 |
| `_get(m, "Calculate")` | `System.bool Calculate( System.object Entities )` / 反射 `Boolean Calculate(Object)` = 1 | **0** | **不符 —— 表 #1** |
| `_get(m, <16 个 MEASURE_FIELDS>)`：`Distance` `NormalDistance` `CenterDistance` `Angle` `Length` `TotalLength` `ArcLength` `ChordLength` `Area` `TotalArea` `Perimeter` `Diameter` `Radius` `DeltaX` `DeltaY` `DeltaZ` | 16 个**逐个查过** `C:\swapi\types\IMeasure\*.md`，全部 `kind: property` 且全部 `System.double <名> {get;}` = 各 0 | 0 | 一致（16/16） |
| `_get(m, <3 个 MEASURE_FLAGS>)`：`IsIntersect` `IsParallel` `IsPerpendicular` | `System.bool IsIntersect {get;}` · `System.bool IsParallel {get;}` · `System.bool IsPerpendicular {get;}` = 各 0 | 0 | 一致（3/3） |

**"两源不一致"记录（本轮 0 条）**：本轮核到的每一个成员，`C:\swapi\types\*.md` 的 Signature、CHM 解包页的 .NET Syntax、出厂类型库反射 `iface_sldworks.txt` 的**参数个数三者都相同**，未出现「文档 7 个 / 类型库 14 个」那类分歧。
（顺带记一笔官方**内部**的类型不一致，本轮与我方调用无关、不进表：`C:\swapi\types\IDraftFeatureData2\GetPartingLinesCount.md` 写 `System.short GetPartingLinesCount()`，而 `C:\swapi\types\IPartingLineFeatureData\GetPartingLinesCount.md` 与 `C:\swapi\types\IPartingSurfaceFeatureData\GetPartingLinesCount.md` 都写 `System.int GetPartingLinesCount()`。）

**"查不到"记录**：无 —— 本轮 38 个成员在 `C:\swapi\types\` 下**全部**有独立页。

---

核了 **38** 个成员 / **45** 个调用站点 · 报 **1** 条 · 置信度为高的是 **第 1 条**（`IMeasure.Calculate` 实参个数 0 ≠ 官方形参个数 1）。