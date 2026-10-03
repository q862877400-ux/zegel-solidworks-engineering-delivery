# audit-08 · 域 08-mold-costing · 核对 C（废弃链与枚举取值）

**核对员**：逐条核对（只读）· **日期**：2026-10-03
**范围（两框交集）**：域 `08-mold-costing` ∩ 核对 `C`
**我这边读的文件**：`scripts/sw_mold.py` · `scripts/sw_measure.py`（两个都在，无需 glob 兜底）
**官方源**：`C:\swapi\types\` · `C:\swapi\enums\` · `C:\swapi\docs\` · `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\`（CHM 解包）
**做法**：只报「两段原文对不上」的条目；给不出两段可搜索原文的一律不写；不判谁对，不给建议。

| # | 我们的原文（文件 + 片段） | 官方的原文（文件 + 片段） | 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | `scripts/sw_mold.py` · `mold_undercut_detect()`：`return get_com_member(fm, "MoldUndercutDetect",` ／ `int(col_undercut), int(col_base), bool(b_coord_input),` ／ `float(dx), float(dy), float(dz))`；同函数 docstring 写 `"""**底切检测**（官方 `IFeatureManager.MoldUndercutDetect`，6 参，返回 `Void`）。` | `C:\swapi\types\IFeatureManager\MoldUndercutDetect.md`：`Obsolete. Superseded by [[IFeatureManager::MoldUndercutDetect2]].`<br>CHM `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~MoldUndercutDetect.html`：`Obsolete. Superseded by IFeatureManager::MoldUndercutDetect2 .`<br>（后继页 `C:\swapi\types\IFeatureManager\MoldUndercutDetect2.md`：`void MoldUndercutDetect2( System.int ColUndercut1, System.int ColUndercut2, System.int ColOccluded, System.int ColStraddle, System.int ColBase, System.bool BCoordInput, System.double Dx, System.double Dy, System.double Dz )`） | 我们调用的成员被官方**两个源**都标为 **Obsolete**（swapi md 与 CHM 解包页逐字一致），官方点名的后继是 `MoldUndercutDetect2`；我们调的仍是旧版，且**后继的形参是 9 个（5 个颜色 + BCoordInput + Dx/Dy/Dz），与我们仍传的 6 个不一致** —— 换后继不是同名同位替换 | 高 |
| 2 | `scripts/sw_mold.py` · `insert_parting_surface()`：`int(option),            # 6 Int32 未查证`（该字面量按位置传给 `InsertMoldPartingSurface` 的第 6 参，函数默认值 `option: int = 0`；docstring 亦写 `⚠ **8 个参数里只有 3 个的语义可推断**（`distance`/`angle`/`tolerance`）、其余 5 个（`surface_type` / `flip` / `use_trim` / `option` / `alternate`）**语义未查证**`） | `C:\swapi\types\IFeatureManager\InsertMoldPartingSurface.md`：`- **Smooth**: Smooth mold parting surface as defined by [[swPartingSurfaceSmoothingType_e]]`（第 6 形参即 `System.int Smooth`）<br>`C:\swapi\enums\swPartingSurfaceSmoothingType_e.md`：`enum_member_count: 2`，成员表只有 `\| swPartingSurfaceSharp \| 1 \|`、`\| swPartingSurfaceSmooth \| 2 \|` | 我们当作枚举传的**字面量 `0` 不在该官方枚举的成员表内**（该枚举只有 1 与 2 两个成员），而我们把它写进了官方明确定义为该枚举类型的那一位 | 高 |

---

**核过的、确认「无分歧」的地方（不计入上表，只记账）**：

- **废弃标记逐个对过 `C:\swapi\types\` 页面，结论=无 Obsolete**：`InsertMoldPartingLine` · `InsertMoldPartingSurface` · `InsertMoldShutOffSurface` · `InsertMoldCoreCavitySolids`（四页均无 `Obsolete` 字样；CHM 解包同名页亦无）· `IModelDoc2\MoldDraftAnalysis.md`（`IModelDoc2` 目录下只有 `MoldDraftAnalysis.md` 一个，**不存在 `MoldDraftAnalysis2`**；CHM 同名页无 `Obsolete`）· `IModelDocExtension\CreateMeasure.md` · `IMeasure\` 下 32 个成员页**全目录无一个含 `Obsolete`** · `ISelectionMgr\GetSelectedObjectCount2.md`（无 `Obsolete`）。
- **枚举字面量逐值对过 `C:\swapi\enums\`**：第 1 位 `Radiate` 的字面量 `0` = `swPartingSurfaceMoldParmTangent | 0`（`swPartingSurfaceMoldParmType_e.md`，`enum_member_count: 3`）⇒ 合法；`sw_measure.py` 的 `arc_option` 限定值 `0 / 1 / 2` = `swMeasureArcCircle_CenterToCenter | 0` / `swMeasureArcCircle_MinimumDistance | 1` / `swMeasureArcCircle_MaximumDistance | 2`（`swMeasureArcCircleOption_e.md`，`enum_member_count: 12`）⇒ 三个值全是合法成员；`GetSelectedObjectCount2(-1)` 的 `-1` 在官方 `Mark` 说明里明写（`-1 = All selections regardless of marks`）⇒ 合法。
- **查不到官方依据、故按铁律 5 不报**：`sw_mold.py` 的 `MoldDraftAnalysis` 把 `int(analysis_type)=0` 传给 `Options`（`[[swDraftAnalysisOptions_e]]`，成员 1/2）、`int(option)=0` 传给 `Shows`（`[[swDraftAnalysisShow_e]]`，成员 1/2/4/8/16/32/64）—— 这两个枚举页**头部都写 `[Bitmask](<../docs/Programming with the SOLIDWORKS API/Bitmasks.md>)`**，而 `Bitmasks.md` 只讲「两个以上选项把值相加」**未说 0 是否合法** ⇒ 官方原文不足以与我们的 `0` 对撞，**不写成条目、不猜**。
- **`sw_measure.py` 在核对 C 范围内 0 条**：`Measure_Selected_Entities_Example_VB.md` 与 `IMeasure/ArcOption.md`、`IMeasure/Calculate.md`、`IModelDocExtension/CreateMeasure.md` 都逐页读过，除上表两条外无「废弃链 / 枚举取值」类分歧。

---

**都核了几处**：43 处 = 38 个 COM 成员（`sw_mold.py` 13：FeatureManager · InsertMoldPartingLine · InsertMoldPartingSurface · InsertMoldShutOffSurface · InsertMoldCoreCavitySolids · MoldDraftAnalysis · MoldUndercutDetect · GetPartingLinesCount · GetPartingSurfacesCount · GetCavitySurfacesCount · GetCoreSurfacesCount · PartingType · CoreCavitySplit；`sw_measure.py` 25：SelectionManager · GetSelectedObjectCount2 · Extension · CreateMeasure · ArcOption · Calculate + IMeasure 读成员 19＝MEASURE_FIELDS 16 + MEASURE_FLAGS 3）＋ 5 处枚举字面量（`swPartingSurfaceMoldParmType_e` 0 · `swPartingSurfaceSmoothingType_e` 0 · `swDraftAnalysisOptions_e` 0 · `swDraftAnalysisShow_e` 0 · `swMeasureArcCircleOption_e` 0/1/2）。
**报了几条**：2 条（第 1–2 条，均在 `scripts/sw_mold.py`；`scripts/sw_measure.py` 报 0 条）。
**高置信**：第 1、2 条 —— 2 条全部为高置信（每条的两段原文均已逐字抄录、可 grep）。