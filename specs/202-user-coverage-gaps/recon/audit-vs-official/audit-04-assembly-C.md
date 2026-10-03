# audit-04-assembly-C · 核对 C（废弃链与枚举取值）

- **域**：04-assembly
- **我们的文件**：`scripts/sw_assembly.py`（877 行，存在，已逐段读完）
- **核对方式**：只读比对。未运行 SolidWorks、未运行 pytest、未改动仓内任何文件。
- **官方源**：`C:\swapi\types\<接口>\<成员>.md`、`C:\swapi\enums\<枚举>.md`、`D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\*.html`（CHM 解包）
- **本路结论**：只报「我们调的成员被官方标 Obsolete」这一类；枚举字面量逐个查完，**未发现非法取值**（见文末「枚举取值 · 未报的部分」）。

| # | 我们的原文（文件 + 片段）| 官方的原文（文件 + 片段）| 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | `scripts/sw_assembly.py` — `return asm_model.AddComponent4(` | `C:\swapi\types\IAssemblyDoc\AddComponent4.md` — `Obsolete. Superseded by [[IAssemblyDoc::AddComponent5]].`（CHM 同源：`…IAssemblyDoc~AddComponent4.html` — `Obsolete. Superseded by IAssemblyDoc::AddComponent5 .`）| 我们在 `_add_component4()` 里直调官方已标 **Obsolete** 的 `AddComponent4`；官方点名后继是 `AddComponent5`（同文件 `_add_component5()` 已在调它，但 `_add_component4()` 仍作为回退路径保留调用）。 | 高 |
| 2 | `scripts/sw_assembly.py` — `mate = asm_model.AddMate5(` | `C:\swapi\types\IAssemblyDoc\AddMate5.md` — `Obsolete. Superseded by [[IAssemblyDoc::CreateMate.]]`（CHM 同源：`…IAssemblyDoc~AddMate5.html` — `Obsolete. Superseded by  IAssemblyDoc::CreateMate. `）| 我们在 `add_mate5_checked()` 里直调官方已标 **Obsolete** 的 `AddMate5`；官方点名后继是 `IAssemblyDoc::CreateMate`。该函数是 `add_mate_coincident` / `add_mate_concentric` / `add_mate_distance` / `add_mate_parallel` / `add_concentric_mate_by_cylinders` / `add_gear_mate_by_cylinders` 的唯一建配入口。 | 高 |
| 3 | `scripts/sw_assembly.py` — `if not entity1.Select2(False, mark):`（同行下一句 `if not entity2.Select2(True, mark):`）| `C:\swapi\types\IEntity\Select2.md` — `Obsolete. Superseded by [[IEntity::Select4]].`（CHM 同源：`…IEntity~Select2.html` — `Obsolete. Superseded by IEntity::Select4 .`）| `select_entities_for_mate()` 用 `IEntity::Select2` 选中两个配对实体；官方标 **Obsolete**，点名后继是 `IEntity::Select4`。注意 `AddMate5.md` 的 Remarks 又要求用 `IModelDocExtension::SelectByID2` 选（见下表备注）。 | 高 |
| 4 | `scripts/sw_assembly.py` — `if component.SetTransformAndSolve2(transform):` | `C:\swapi\types\IComponent2\SetTransformAndSolve2.md` — `Obsolete. Superseded by [[IComponent2::SetTransformAndSolve3]].`（CHM 同源：`…IComponent2~SetTransformAndSolve2.html` — `Obsolete. Superseded by IComponent2::SetTransformAndSolve3 .`）| `apply_component_transform_x()` 直调官方已标 **Obsolete** 的 `SetTransformAndSolve2`；官方点名后继是 `SetTransformAndSolve3`。 | 高 |
| 5 | `scripts/sw_assembly.py` — `asm_model.EditSuppress()` | `C:\swapi\types\IModelDoc2\EditSuppress.md` — `Obsolete. Superseded [[IModelDoc2::EditSuppress2]].`（CHM 同源：`…IModelDoc2~EditSuppress.html` — `Obsolete. Superseded IModelDoc2::EditSuppress2 .`）| `suppress_component()` 直调官方已标 **Obsolete** 的 `EditSuppress`；官方点名后继是 `EditSuppress2`。 | 高 |
| 6 | `scripts/sw_assembly.py` — `asm_model.EditUnsuppress()` | `C:\swapi\types\IModelDoc2\EditUnsuppress.md` — `Obsolete. Superseded by [[IModelDoc2::EditUnsuppress2]].`（CHM 同源：`…IModelDoc2~EditUnsuppress.html` — `Obsolete. Superseded by IModelDoc2::EditUnsuppress2 .`）| `unsuppress_component()` 直调官方已标 **Obsolete** 的 `EditUnsuppress`；官方点名后继是 `EditUnsuppress2`。 | 高 |
| 7 | `scripts/sw_assembly.py` — `"reference_type": int(get_com_member(mate_entity, "ReferenceType") or -1),` | `C:\swapi\types\IMateEntity2\ReferenceType.md` — `Obsolete. Superseded by [[IMate2Entity::Reference2]].`（CHM 同源：`…IMateEntity2~ReferenceType.html` / `…IMateEntity2_members.html` — `Obsolete. Superseded by <A href="…IMateEntity2~ReferenceType2.html">IMate2Entity::Reference2</A>.`）| `collect_mate_entity_evidence()` 读官方已标 **Obsolete** 的 `IMateEntity2::ReferenceType`；官方点名后继是 `IMate2Entity::Reference2`（**两源对后继的写法不一致**：结构化页写接口名 `IMate2Entity`，CHM 写显示名 `IMate2Entity::Reference2` 但链接指向 `IMateEntity2~ReferenceType2.html`）。 | 高 |
| 8 | `scripts/sw_assembly.py` — `sw.ActivateDoc2(title, False, errors)` | `C:\swapi\types\ISldWorks\ActivateDoc2.md` — `Obsolete. Superseded by [[ISldWorks::ActivateDoc3]].`（CHM 解包目录内**没有** `ISldWorks~ActivateDoc2.html` 成员页，只有指向它的链接 ⇒ 本条只有**单一官方源**）| `_activate_model_document()` 的 `except` 回退分支调官方已标 **Obsolete** 的 `ActivateDoc2`；官方点名后继是 `ActivateDoc3`（同函数上一分支已在用它）。 | 中（仅一源；CHM 里该成员页缺失，按铁律 5 不用相似页面顶替）|

## 枚举取值 · 逐条查完、**未报**的部分

本文件把字面量当枚举传的地方全部对过 `C:\swapi\enums\*.md`，**每个取值都是合法成员**，故不构成「两段原文对不上」，不列入上表：

| 我们的常量 / 字面量 | 官方原文（`enums/*.md`）|
|---|---|
| `SW_MATE_COINCIDENT = 0` / `SW_MATE_CONCENTRIC = 1` / `SW_MATE_PARALLEL = 3` / `SW_MATE_DISTANCE = 5` / `SW_MATE_GEAR = 10` | `swMateType_e.md` — `swMateCOINCIDENT \| 0` · `swMateCONCENTRIC \| 1` · `swMatePARALLEL \| 3` · `swMateDISTANCE \| 5` · `swMateGEAR \| 10` |
| `SW_ADD_MATE_ERROR_UNKNOWN = 0` / `SW_ADD_MATE_ERROR_NO_ERROR = 1` | `swAddMateError_e.md` — `swAddMateError_ErrorUknown \| 0 = Unknown error occurred` · `swAddMateError_NoError \| 1 = Success, no error` |
| `SW_COMPONENT_SUPPRESSED = 0` / `SW_COMPONENT_LIGHTWEIGHT = 1` / `SW_COMPONENT_FULLY_RESOLVED = 2` / `SW_COMPONENT_RESOLVED = 3` | `swComponentSuppressionState_e.md` — `swComponentSuppressed \| 0` · `swComponentLightweight \| 1` · `swComponentFullyResolved \| 2` · `swComponentResolved \| 3` |
| `SW_SOLID_BODY = 0`（传给 `GetBodies2`）| `swBodyType_e.md` — `swSolidBody \| 0 = Solid body` |
| `align=0`（`AddMate5` 的 `AlignFromEnum`）| `swMateAlign_e.md` — `swMateAlignALIGNED \| 0` |
| `width_mate_option=0`（`AddMate5` 的 `WidthMateOption`）| `swMateWidthOptions_e.md` — `swMateWidth_Centered \| 0` |
| `AddComponent5` 第 2 参传字面量 `0` | `swAddComponentConfigOptions_e.md` — `swAddComponentConfigOptions_CurrentSelectedConfig \| 0 = Add a part or assembly in its last saved configuration.` |
| `ReplaceComponents2(new_part_path, "", False, 0, True)` 的 `UseConfigChoice=0` | `swReplaceComponentsConfiguration_e.md` — `swReplaceComponentsConfiguration_MatchName \| 0 = Let SOLIDWORKS attempt to match the configuration of the old components…` |

## 查不到（不报，仅留痕）

- `scripts/sw_assembly.py` — `mate.Name = name`：`C:\swapi\types\IMate2\` 目录 37 个文件里**没有** `Name.md`，`C:\swapi\types\IMate\` 目录**整体不存在**（0 文件）⇒ 两套官方源都查不到 `IMate2::Name` 的成员页 ⇒ 按铁律 5 记「查不到」，不用相似名字顶替，故不报。
- 官方点名后继 `IMate2Entity` 在 `C:\swapi\types\` 下**没有对应目录**（该目录只有 `IMate2` / `IMateEntity2` / `IMateReference` 等）⇒ 上表第 7 条的后继成员页查不到，故第 7 条只报「Obsolete」这一事实本身，不涉及后继的可用性判断。

## 覆盖与口径

- **废弃链**：核了 **52 处**我们实际调用的官方成员（逐个查 `types/<接口>/<成员>.md`；另对 `ISurface`(83 页)、`IInterferenceDetectionMgr`(23 页)、`IMateFeatureData`(3 页)、`IMateInPlace`(6 页) 做了整目录扫描，确认这些接口**没有任何** `Obsolete` 行）。
- **枚举取值**：核了 **8 个** `enums/*.md` 文件里的 **12 个**字面量。
- **合计核了 64 处，报了 8 条**（全部属「我们调的成员被官方标 Obsolete」这一类；枚举取值一侧**零发现**）。

---

**结尾三行**
- 核了几处：**64 处**（废弃链 52 处成员 + 枚举 12 个字面量）
- 报了几条：**8 条**
- 置信度为高的：**#1 AddComponent4 · #2 AddMate5 · #3 IEntity.Select2 · #4 IComponent2.SetTransformAndSolve2 · #5 IModelDoc2.EditSuppress · #6 IModelDoc2.EditUnsuppress · #7 IMateEntity2.ReferenceType**（#8 `ISldWorks.ActivateDoc2` 为「中」，仅 `C:\swapi` 一源，CHM 成员页缺失）