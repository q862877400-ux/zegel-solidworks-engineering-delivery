# vd50-C-sm-2 · 域 `02-sheetmetal` · 契约摘要 —— 展开 / 折弯 / 切口 / 成形工具 / 钣金参数

> ★ 本文件只抄**亲手读到**的内容。五条纪律：查不到就说查不到 · 每条给「仓内那一段」+「官方/目标那一段」两段可搜索原文（**不给行号**）· 只判 成立 / 不成立 / 存疑 · 宁少勿滥 · 只读 + 只写本文件一个。
>
> **格式模板**：`recon/api-pre/api-03-weldment.md`（源表 + 逐条 ① ② ③ + 前置/配方一句话）。
> **本片范围**：展开（unfold / 平板型式导出）· 折弯（sketched bend / 拔模常量）· 切口（slit）· 成形工具（forming tool）· 钣金参数（bend allowance / 展开导出选项）。
> **与同轮两片的分工**：`vd50-C-sm-1` = 基体法兰 / 边线法兰 / 斜接法兰 / 闭合角；`vd50-C-sm-3` = 导出常量 / 镜像 / 阵列 / 转角处理 / 平板型式。⇒ **本片不重复它们已核过的条目**（`SheetMetalOptions` 8 常量、`IModelDoc2` vs `IPartDoc` 出处层、`InsertSheetMetalUnfold` 零实现、`Initialize` 九参对齐、miter 14 参 —— 均已在那两片核过，本片只在必要处注明，不再计数）。
>
> **读过的离线源（全部本机，未联网）**
>
> | 源 | 本文件简称 | 抄什么 |
> |---|---|---|
> | `C:\swapi\types\<接口>\<成员>.md` | **[md]** | 精确签名（`System.*` 口径）、`## Parameters`、`## Remarks` 逐字 |
> | `C:\swapi\enums\<枚举>.md` | **[en]** | 枚举成员与数值 |
> | `D:\AI\SW\scripts\` · `D:\AI\SW\capabilities.yaml` | **仓内** | 我们实际写的调用、常量与注释 |

**核了 9 处，对不上 6 处。**

---

# 〇 · 名字缺席（铁律 5：查不到就说查不到）

| 想找的 | 结果 | 证据 |
|---|---|---|
| `ISlitFeatureData` 接口 | **查不到** | `C:\swapi\types\` 全库递归检索 `*Slit*` 只命中 **1 个文件**：`C:\swapi\types\IFlatPatternFeatureData\ShowSlitInCornerRelief.md` |
| `swSlitTypes_e` 枚举 | **查不到** | 同一次递归检索在 `C:\swapi\enums\` 下**零命中**（无任何 `*Slit*` 枚举页） |
| `IFeatureManager` 下的**切口 / Slit** 入口 | **查不到** | `C:\swapi\types\IFeatureManager\` 的文件名表里无 `Slit` 子串 |
| 拔模（draft）的任何 `Insert*` 入口页 | **查不到** | `C:\swapi\types\` 全库递归 `InsertDraft*.md` → **0 个文件** ⇒ 仓内 `create_draft` 那句「正确入口未查明」在**本机离线源上成立** |
| `ICustomBendAllowance` 的 `Type` 成员 | **存在**（不是查不到） | `C:\swapi\types\ICustomBendAllowance\Type.md`（`System.int Type {get; set;}`） |

---

# 一、展开（unfold / 平板型式导出）

## 1.1 ★★ V-7 · `export_to_dxf` 把**任何零件**都按钣金展开导出 —— 判定：**成立**

**① 仓内那一段** —— `scripts/sw_export.py`，`export_to_dxf` 函数体逐字：

```
    doc_type = get_com_member(model, "GetType")
    if doc_type == 3:  # 工程图
        return _export_generic(model, output_path)
    else:
        # 零件默认按“展开几何 + 折弯线”导出；其余选项由位掩码控制。
        return export_flat_pattern_dxf(model, output_path)
```

被转发到的终点，`scripts/sw_export.py` 里 `export_flat_pattern_dxf` 的入参与守卫逐字：

```
    model_path = str(get_com_member(model, "GetPathName") or "")
    if not model_path:
        raise ValueError("导出展开 DXF 前必须先保存钣金零件")
```

```python
    return bool(model.ExportToDWG2(
        output_path,
        model_path,
        SW_EXPORT_TO_DWG_SHEET_METAL,
```

（第三位实参在同文件里逐字 `SW_EXPORT_TO_DWG_SHEET_METAL = 1`。）

**② 官方那一段** —— [en] `C:\swapi\enums\swExportToDWG_e.md`，成员表 `swExportToDWG_ExportSheetMetal` 那一行逐字（**限定语就写在值那一列**）：

```
| swExportToDWG_ExportSheetMetal | 1; Valid only if the active document contains sheet metal |
```

同表其余两行逐字（说明该列的三个值是互斥的动作）：

```
| swExportToDWG_ExportAnnotationViews | 3 |
| swExportToDWG_ExportSelectedFacesOrLoops | 2 |
```

第二源核对 —— [md] `C:\swapi\types\IPartDoc\ExportToDWG2.md`，`## Parameters` 里 `Action` 与 `SheetMetalOptions` 两行逐字：

```
- **Action**: Export action as defined in [[swExportToDWG_e]] (see **Remarks**)
```
```
- **SheetMetalOptions**: [Bitmask](<../../docs/Programming with the SOLIDWORKS API/Bitmasks.md>) that contains sheet metal export options; valid only if Action = swExportToDWG_e.swExportToDWG_ExportSheetMetal (see **Remarks**)
```

**一句话依据**：官方把 `Action = 1`（展开）这一档**逐字限定**为「Valid only if the active document contains sheet metal」，而仓内把**每一个非工程图文档**都转发到这条 Action、其唯一守卫是「路径非空」。

**强度说明**：官方那句限定语针对的是**动作的有效性**，不是「不得对非钣金件调用」的禁令；本条成立在「官方逐字写了适用范围 + 仓内逐字把适用范围写成『所有零件』」这一事实上。

---

# 二、折弯（sketched bend / 拔模常量）

## 2.1 `swFmSketchBend(35)` 取代 `swFmOneBend(33)` —— 判定：**不成立**（仓内已改对）

**① 仓内那一段** —— `scripts/sw_sheet_metal.py`，常量块逐字：

```
SW_FM_DRAFT = 3
SW_FM_ONE_BEND = 33
```
```
#: ⚠ `swFmOneBend(33)` 是**合法枚举成员**，但**不在** `CreateDefinition` 接受的 35 个常量里
#: ⇒ `CreateDefinition(33)` 返回 None **是应然的**（已知事实 34 的真因，2026-10-01 查明）。
#: 「一个折弯」的**正确入口**是下面这个（官方名单里有，接口 `ISketchedBendFeatureData`）。
#: 数值来源：`D:\AI\SW\_raw\**\enum_values_sldworks.txt`（反射，130 个成员）。
SW_FM_SKETCH_BEND = 35
```

**② 官方那一段** —— [md] `C:\swapi\types\IFeatureManager\CreateDefinition.md`，`## Parameters` 的 `Type` 名单里逐字：

```
  - swFmSketchBend (sheet metal sketched bend)
```

★ 该名单共 **35** 条（逐条数过：`swFmBaseFlange` … `swFmTablePattern`），其中**没有** `swFmOneBend`、**没有** `swFmDraft`；名单里与钣金折弯相关的只有这一条。

**一句话依据**：仓内把折弯入口换成 `swFmSketchBend(35)`、并断言 `swFmOneBend(33)` 不在官方 35 个常量里 —— 官方名单逐条核对**完全对得上**。

---

## 2.2 `swFmDraft(3)` 不在 `CreateDefinition` 名单内 —— 判定：**成立**（仓内断言对上了官方）

**① 仓内那一段** —— `scripts/sw_sheet_metal.py`，`SHEET_METAL_RUNTIME_STATUS` 表内 `create_draft` 一项逐字：

```
    "create_draft": (False,
        "CreateDefinition(3) 返回 None ⇒ **该类型不走 `CreateDefinition`**；"
        "正确入口未查明"),
```

**② 官方那一段** —— [md] `C:\swapi\types\IFeatureManager\CreateDefinition.md`，`## Returns` 段逐字（返回类型清单里逐字含 `sheet metal sketched bend`，**不含任何 draft**）：

```
[[thread]], [[sweep]], [[library]], [[library form tool]], [[tab and slot]], [[bounding box]], [[ground plane]], [[mirror components]], [[projection curve]], [[sheet metal normal cut]], [[sheet metal swept flange]], [[sheet metal gusset]], [[sheet metal edge flange]], [[convert solid to sheet metal]], [[simple fillet/chamfer]], [[belt/chain]], [[sheet metal base flange]], [[sheet metal corner relief]], [[sheet metal sketched bend]], [[mate controller]], or pattern-specific feature data object (see **Remarks**); Nothing or null otherwise
```

`## Remarks` 段逐字（同样只点名 `sheet metal base flange, sheet metal corner relief, convert solid to sheet metal, library, simple fillet, and thread features` 需要各自的 initialize 方法）：

```
For sheet metal base flange, sheet metal corner relief, convert solid to sheet metal, library, simple fillet, and thread features, you must initialize feature data objects using specific initialize methods.
```

★ 另见 §〇：`C:\swapi\types\` 全库**没有** `InsertDraft*.md` ⇒ 仓内「正确入口未查明」这句在本机离线源上**查不到反驳**。

**一句话依据**：官方 35 条名单与 Returns/Remarks 两段都只承认「折弯用 `swFmSketchBend`」，拔模不在其中 ⇒ `CreateDefinition(3)` 回 `None` 是应然的，仓内如实记成不可用。

---

## 2.3 ★★ V-8 · `create_one_bend` 无条件同时设 `BendRadius` 与 `UseDefaultBendRadius=True`，且从不设 `UseGaugeTable` —— 判定：**成立**

**① 仓内那一段** —— `scripts/sw_sheet_metal.py`，`OneBendSpec` 字段默认值逐字：

```
    use_default_radius: bool = True
```

同文件 `create_one_bend` 体内 `_apply` 逐字（**四个赋值无条件连着写**）：

```
    def _apply(data):
        data.UseDefaultBendRadius = bool(spec.use_default_radius)
        data.BendRadius = float(spec.bend_radius)
        data.BendAngle = float(spec.angle)
        data.ReverseDirection = bool(spec.reverse_direction)
```

★ 反向证据：全文件对 `UseGaugeTable` 的命中**只有一条注释**（列举 `ISketchedBendFeatureData` 成员的那一段），**没有任何可执行赋值**。

**② 官方那一段** —— [md] `C:\swapi\types\ISketchedBendFeatureData\BendRadius.md`，`## Remarks` 段逐字：

```
This property is valid only if [[ISketchedBendFeatureData::UseDefaultBendRadius]] is false.

To use something other than the default bend radius, set:

- ISketchedBendFeatureData::UseDefaultBendRadius to false

   - and -

- [[ISketchedBendFeatureData::UseGaugeTable]] to false.
```

（`C:\swapi\types\ISketchedBendFeatureData\UseGaugeTable.md` **存在** ⇒ 第二个开关是可设的，仓内没设。）

**一句话依据**：官方逐字写「`BendRadius` **valid only if** `UseDefaultBendRadius` is false」并要求「改成非默认半径时**还要**把 `UseGaugeTable` 置 false」，而仓内默认 `use_default_radius=True` 时仍照设 `BendRadius`、且全程不碰 `UseGaugeTable`。

---

# 三、切口（slit）

## 3.1 ★★ V-9 · 官方「切口」在离线源里只落**一个**成员上，仓内对它**零实现** —— 判定：**成立**

**① 仓内那一段** —— `scripts/sw_api_sldworks.py`（首行 docstring 自述为「**官方 API 的完整抄录** —— 523 个接口族、**8210 个成员**，逐个照抄自对官方 interop 程序集的**纯元数据反射**」），`IFlatPatternFeatureData` 成员块内逐字：

```
        'ShowSlitInCornerRelief',
        'ShowSlitInCornerRelief',
        'SimplifyBends',
```

★ 该块的头部逐字是同一份文件里的接口名条目：

```
    'IFlatPatternFeatureData': (
```

★ 反向证据：全仓 `*.py` 检索 `ShowSlitInCornerRelief` 的命中**全部**落在同一份反射抄录索引里；`scripts/` 与 `mcp-server/` 的其它文件（`sw_sheet_metal.py` / `sw_sheet_metal_weld_entry.py` / `sw_export.py` / 全部 `tool_specs_*.py`）对它**零命中** ⇒ 没有可执行调用、没有 MCP 工具、没有 spec。

**② 官方那一段** —— [md] `C:\swapi\types\IFlatPatternFeatureData\ShowSlitInCornerRelief.md`，front-matter 与签名逐字：

```
type: IFlatPatternFeatureData
member: ShowSlitInCornerRelief
category: Feature Interfaces/Sheet Metal
```
```
**Signature**: `System.bool ShowSlitInCornerRelief {get; set;}`
```

`## Remarks` 段逐字（说明「切口」在官方语境里是什么）：

```
When you create a rectangular or circular corner relief that is smaller than the bend area, a slit is added so that the part can bend. Setting this property to true makes the slit available in the flat pattern.

This property corresponds to the **Show Slit** option in the Parameters section of the Flat-Pattern PropertyManager.
```

★ 规模事实（见 §〇）：`C:\swapi` 全库递归 `*Slit*` **只命中这一个文件** ⇒ `ISlitFeatureData` / `swSlitTypes_e` / `IFeatureManager` 的切口入口**在本机两套离线源上全部查不到**。

**一句话依据**：官方把「切口」落在平板型式特征的 `ShowSlitInCornerRelief` 这**一个布尔属性**上（且该属性所在的平板型式特征族在本仓**零实现**），仓内对它只有反射索引里的名字。

---

# 四、成形工具（forming tool）

## 4.1 `swFmFormToolInstance` → `ILibraryFormToolFeatureData` 的**官方点名**映射 —— 判定：**不成立**（仓内正确）

**① 仓内那一段** —— `scripts/check_interface_member_ownership.py`，`MANUAL_MAP` 里那条被移除后留下的注释逐字：

```
    # ⚠ 2026-10-01 轮 44：**已"升级"** —— `ILibraryFormToolFeatureData` 的 `_overview.md`
    #   里**官方直接点名** `swFmFormToolInstance` ⇒ 现在由 `officially_named()` 给出
    #   （**官方断言 > 人工确证**），故从本表移出。**留下的这条注释是记录这次升级。**
```

同文件 `officially_named()` 的 docstring 里逐字：

```
    # ⚠ **覆盖窄**：35 个常量里只有 **5 条**用了这种写法
    #     （`swFmFillet` / `swFmFormToolInstance` / `swFmNormalCut` / `swFmRefCurve` /
    #      `swFmSolidToSheetMetal`）。**⇒ 可靠但稀疏。**
```

**② 官方那一段** —— [md] `C:\swapi\types\ILibraryFormToolFeatureData\_overview.md`，`## Remarks` 的创建步骤第 3 步逐字：

```
3. Call [[IFeatureManager::CreateDefinition]](swFmFormToolInstance) to create this feature data object.
```

上下文同段第 1、2 步逐字（说明这条链的前置）：

```
1. Ensure that the Sheet Metal tab is visible on the CommandManager toolbar.

2. Call [[IModelDocExtension::SelectByRay]] to select a flat face (with Mark = 0) on which to use a forming tool.
```

同文件描述句与规模逐字：

```
Allows access to library forming tool feature data.
```
```
property_count: 10
method_count: 5
```

第三源交叉 —— [md] `C:\swapi\types\IFeatureManager\CreateDefinition.md` 的 `Type` 名单里逐字：

```
  - swFmFormToolInstance (library form tool)
```

**一句话依据**：官方接口自己的 `_overview.md` 在创建步骤里逐字写出 `CreateDefinition(swFmFormToolInstance)`，仓内据此把这条映射判为「官方点名」并移出人工表 —— 依据成立。

---

## 4.2 ★★ V-10 · 成形工具的三个入口在仓内**零实现**（其中两个官方已标 Obsolete）—— 判定：**成立**（缺口）

**① 仓内那一段** —— `scripts/sw_api_sldworks.py`，`IFeatureManager` 的 arity 表内逐字：

```
        'InsertFlexFeature': 17,
        'InsertFormToolFeature': 9,
        'InsertFreeform': 6,
```

同文件另一处（同一份索引的 arity 表）逐字：

```
        'CreateFormTool': 0,
        'CreateFormTool2': 2,
```

★ 反向证据：全仓 `*.py` 检索 `InsertFormToolFeature|CreateFormTool|ILibraryFormToolFeatureData` 的可执行命中**为零** —— 除反射索引外，只有 `scripts/check_interface_member_ownership.py` 里那条**映射注释**，以及仓根两个文档生成脚本 `doc_fact52.py` / `doc_fact5657.py`。

**② 官方那一段** —— [md] `C:\swapi\types\IFeatureManager\InsertFormToolFeature.md`，标题下第一句与签名逐字：

```
Obsolete. Superseded by [[IFeatureManager::CreateDefinition]] and [[IFeatureManager::CreateFeature]].
```
```
**Signature**: `Feature InsertFormToolFeature( System.string Path, System.bool Flip, System.double RotAngle, System.string Config, System.bool OverrideDoc, System.bool ShowPunch, System.bool ShowProfile, System.bool ShowCenter, System.bool LinkToPart )`
```

[md] `C:\swapi\types\IFeatureManager\CreateFormTool.md`，标题下第一句与签名逐字：

```
Obsolete. Superseded by [[IFeatureManager::CreateFormTool2]].
```
```
**Signature**: `Feature CreateFormTool()`
```

现行入口的官方调用序 —— [md] `C:\swapi\types\ILibraryFormToolFeatureData\_overview.md`，`## Remarks` 创建六步逐字（第 3 / 4 / 5 / 6 步）：

```
3. Call [[IFeatureManager::CreateDefinition]](swFmFormToolInstance) to create this feature data object.

4. Call [[ILibraryFormToolFeatureData::OverrideDocumentSettings]] to specify flat pattern visibility options.

5. Specify the forming tool and its rotation angle for placement using [[ILibraryFormToolFeatureData::FormToolConfiguration]], [[FormToolPath]], [[LinkToFormTool]], and [[RotationAngle]].

6. Call [[IFeatureManager::CreateFeature]] to create the feature.
```

同文件末段逐字（成形工具的定义）：

```
Forming tools are dies that dent, bend, stretch, or otherwise form sheet metal.
```

**一句话依据**：官方成形工具有**两个已 Obsolete 的直入法**与**一条现行的六步 `CreateDefinition`/`CreateFeature` 链**，而仓内这 5 个符号只出现在反射抄录索引里 ⇒ 该子面在本仓是空的。

---

# 五、钣金参数（bend allowance / 自定义折弯补偿）

## 5.1 `ICustomBendAllowance.Type` 官方要求**最后**设，仓内先设 `Type` 后设 `KFactor` —— 判定：**存疑**

**① 仓内那一段** —— `scripts/sw_sheet_metal.py`，`create_base_flange` 体内逐字（**赋值顺序就是 `Type` 在前、`KFactor` 在后**）：

```
    bend_allowance = call_com_member(manager, "CreateCustomBendAllowance")
    if bend_allowance is None:
        raise RuntimeError("CreateCustomBendAllowance 未返回对象")
    bend_allowance.Type = SW_BEND_ALLOWANCE_K_FACTOR
    bend_allowance.KFactor = float(spec.k_factor)
```

**② 官方那一段** —— [md] `C:\swapi\types\ICustomBendAllowance\Type.md`，`## Remarks` 段逐字：

```
After setting [[ICustomBendAllowance::BendAllowance]], [[ICustomBendAllowance::BendDeduction]], [[ICustomBendAllowance::BendTableFile]], [[ICustomBendAllowance::BendCalculationTableFile]], and [[ICustomBendAllowance::KFactor]] use this property to set the value for the type. If you do not set this property last, the ICustomBendAllowance property set last automatically overrides any previously set custom bend allowance type.
```

**③ 与之互相拉扯的另一段官方原文** —— [md] `C:\swapi\types\ICustomBendAllowance\KFactor.md`，`## Remarks` 段逐字：

```
When using this property to set a value for K-factor, then the [[type of custom bend allowance]] is set to this type. However, the last ICustomBendAllowance property called to set a value also re-sets the type of custom bend allowance to its type.
```

**一句话依据**：`Type` 页要求「**必须最后设**，否则被最后设的那个属性覆盖」，仓内顺序相反；但 `KFactor` 页逐字说「设 KFactor 会把类型设成 K-factor 类型」⇒ **顺序违规的后果被官方自己抵消掉了**，两段官方原文互相拉扯 ⇒ 判**存疑**、不下结论。

---

## 5.2 `SW_BEND_ALLOWANCE_K_FACTOR = 2` —— 判定：**不成立**（与官方逐字相等）

**① 仓内那一段** —— `scripts/sw_sheet_metal.py`，常量逐字：

```
SW_BEND_ALLOWANCE_K_FACTOR = 2
```

**② 官方那一段** —— [en] `C:\swapi\enums\swBendAllowanceTypes_e.md`，描述句与成员表里那一行逐字：

```
Bend allowance types.
```
```
| swBendAllowanceKFactor | 2 |
```

同一张表的其余 5 行逐字（确认 2 只有一个含义、不是笔误撞号）：

```
| swBendAllowanceBendCalculationTable | 5 |
| swBendAllowanceBendTable | 1 |
| swBendAllowanceDeduction | 4 |
| swBendAllowanceDirect | 3 |
| swBendAllowanceGaugeTable | 6 |
```

接口归属核对 —— [md] `C:\swapi\types\ICustomBendAllowance\Type.md` 的 `## Returns` 逐字：

```
Bend allowance type as defined in [[swBendAllowanceTypes_e]]
```

**一句话依据**：仓内这个常量就是官方 `swBendAllowanceKFactor` 的值，且它被写进的那个属性（`ICustomBendAllowance.Type`）官方逐字点名就是这个枚举。

---

# 六、本片结论（只数可核的）

| # | 子面 | 主题 | 判定 | 一句话依据 |
|---|---|---|---|---|
| 1.1 | 展开 | `export_to_dxf` 把任何零件都按 `Action=swExportToDWG_ExportSheetMetal` 导出 | **成立** | 官方该枚举值逐字带 `Valid only if the active document contains sheet metal`，仓内唯一守卫是「路径非空」 |
| 2.1 | 折弯 | `swFmSketchBend(35)` / `swFmOneBend(33)` | **不成立** | 官方 `CreateDefinition` 35 条名单含 `swFmSketchBend (sheet metal sketched bend)`、无 `swFmOneBend` |
| 2.2 | 折弯 | `swFmDraft(3)` 不在名单内 ⇒ `CreateDefinition(3)` 回 `None` 是应然的 | **成立** | 官方名单 / Returns / Remarks 三段都只承认折弯用 `swFmSketchBend` |
| 2.3 | 折弯 | `create_one_bend` 无条件设 `BendRadius`、从不设 `UseGaugeTable` | **成立** | 官方 `BendRadius` 页逐字「valid only if `UseDefaultBendRadius` is false」+「还要把 `UseGaugeTable` 置 false」 |
| 3.1 | 切口 | 官方只一个 `ShowSlitInCornerRelief`，仓内零实现 | **成立** | `C:\swapi` 全库 `*Slit*` 只命中这一个成员页；仓内该名字只在反射抄录索引里 |
| 4.1 | 成形工具 | `swFmFormToolInstance` → `ILibraryFormToolFeatureData` 的官方点名映射 | **不成立** | 官方 `_overview.md` 创建步骤第 3 步逐字 `CreateDefinition](swFmFormToolInstance)` |
| 4.2 | 成形工具 | 三个入口零实现（两个已 Obsolete） | **成立** | 官方两个 Obsolete 句 + 一条现行六步链；仓内 5 个符号零可执行命中 |
| 5.1 | 钣金参数 | `ICustomBendAllowance.Type` 应最后设，仓内先设 | **存疑** | `Type.md` 要求最后设、`KFactor.md` 又说设 KFactor 会把类型设成 K-factor，两段官方原文互相抵消 |
| 5.2 | 钣金参数 | `SW_BEND_ALLOWANCE_K_FACTOR = 2` | **不成立** | 官方 `swBendAllowanceKFactor | 2`，且 `Type.md` 点名就是这个枚举 |

**核了 9 处 · 判定 成立 5 · 不成立 3 · 存疑 1 ⇒ 对不上 6 处。**

★ 未计入「对不上」的 3 处**对得上**：折弯入口常量（2.1）、成形工具的官方点名映射（4.1）、K-factor 常量值（5.2）—— 三处都与官方逐字相等。
★ 本片**没有**动过仓内任何文件（本文件是本轮唯一写入）。

---

# 结尾三行

- **文件路径**：`D:\AI\SW\specs\202-user-coverage-gaps\recon\verify50\vd50-C-sm-2.md`
- **核了 9 处**（展开 1 · 折弯 3 · 切口 1 · 成形工具 2 · 钣金参数 2），每处均给出「仓内原文 + 官方原文」两段可搜索片段（5.1 另给第三段官方原文说明为何只判存疑）。
- **对不上 6 处**（展开 1 · 折弯 2 · 切口 1 · 成形工具 1 · 钣金参数存疑 1）；**对得上 3 处**（折弯入口常量、成形工具官方点名映射、K-factor 常量值）。
