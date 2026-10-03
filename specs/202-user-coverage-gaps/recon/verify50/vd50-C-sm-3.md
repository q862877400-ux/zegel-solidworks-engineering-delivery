# vd50-C-sm-3 · 域 `02-sheetmetal` · 契约摘要 —— 镜像 / 阵列 / 转角处理 / 平板型式 / 导出

**范围**：`specs/202-user-coverage-gaps/recon/api-pre/` 下**缺** `api-02-sheetmetal.md`；本片只补**钣金域里「镜像 / 阵列 / 转角处理 / 平板型式 / 导出」**这 5 个子面，作为该文件的契约素材。
**方法**：每条给两段可搜索原文 ——「仓内那一段」（`D:\AI\SW\scripts\` / `mcp-server\`）+「官方那一段」（`C:\swapi\`）。
**纪律**（本轮照 `api-03-weldment.md` 的三条 + 任务五条铁律）：
① 只抄亲手读到的；查不到就说查不到 · ② 每条两段原文，**给不出两段的一律不写** · ③ **不写行号**（写原文片段）· ④ 不给建议、不下「看起来可能有问题」这种结论 · ⑤ **宁少勿滥**。
★ **未修改仓内任何文件**（本文件是本轮唯一写入）。

**三套离线源（全部本机，未联网）**

| 源 | 简称 | 抄什么 |
|---|---|---|
| `C:\swapi\types\<接口>\<成员>.md` | **[md]** | 精确签名、`## Parameters`、`## Remarks` 逐字 |
| `C:\swapi\enums\<枚举>.md` | **[en]** | 枚举成员与数值 |

---

## 0. 名字缺席（铁律：查不到就说查不到）

| 想找的 | 结果 | 证据 |
|---|---|---|
| `C:\swapi\types\IModelDoc2\ExportToDWG2.md` | **查不到该文件**；官方页面归属 **`IPartDoc`** | `Get-ChildItem 'C:\swapi\types\IModelDoc2\' -Filter '*DWG*'` → 空；`Select-String -Path 'C:\swapi\types\IModelDoc2\*.md' -Pattern 'ExportToDWG2' -List` → **0 个文件**；实际页面是 `C:\swapi\types\IPartDoc\ExportToDWG2.md`（front-matter 逐字 `type: IPartDoc`） |
| 名字含 `*Unfold*` 的 `ISheetMetalFeatureData` 成员 | **查不到** | `Get-ChildItem 'C:\swapi\types\ISheetMetalFeatureData\' -Filter '*.md' \| Where-Object Name -match 'Unfold\|FlatPattern\|BendLine'` → **0 个文件**。展开入口在**别处**（见 §四） |
| `IFlatPatternFeatureData` 下的「展开 / unfold」成员 | **查不到** | 该接口 24 个 `.md`（`_overview` / `AccessSelections` / `BreakCornerRadius` / `BreakCornerType` / `CornerTreatment` / `CornerTrimRatioToThickness` / `CornerTrimReliefDistance` / `CornerTrimReliefType` / `ExcludedFaces` / `FixedFace` / `FixedFace2` / `GetAddCornerTrim` / `GetBreakCorners` / `ReleaseSelectionAccess` / `SetAddCornerTrim` / `SetBreakCorners` / `ShowSlitInCornerRelief` / `SimplifyBends` / `UseRatioToThickness` …）**无一含 Unfold** |

---

# 一、导出（`ExportToDWG2` / `SheetMetalOptions`）

## 1.1 `SheetMetalOptions` 8 个常量 · 判定：**不成立**（与官方逐字一致）

**① 官方精确签名** —— [md] `C:\swapi\types\IPartDoc\ExportToDWG2.md` 的 `**Signature**:` 行逐字：

```
System.bool ExportToDWG2( System.string FilePath, System.string ModelName, System.int Action, System.bool ExportToSingleFile, System.object Alignment, System.bool IsXDirFlipped, System.bool IsYDirFlipped, System.int SheetMetalOptions, System.object Views )
```

★ **9 个参数**。[md] `## Parameters` 逐条：`FilePath`: Path and file name of the exported DXF/DWG file · `ModelName`: Path and file name of the active part document · `Action`: Export action as defined in [[swExportToDWG_e]] · `ExportToSingleFile`: True to save as one file; false to save as multiple files · `Alignment`: Array of 12 double values that contain information related to output alignment · `IsXDirFlipped` / `IsYDirFlipped` · `SheetMetalOptions`: **Bitmask** that contains sheet metal export options; **valid only if Action = swExportToDWG_e.swExportToDWG_ExportSheetMetal** · `Views`: Array of annotation view names to export。

**② ## Remarks 逐字（bitmask 口径）** —— [md] 原文片段 `SheetMetalOptions bitmask is`：

```
SheetMetalOptions bitmask is {14 13 12 11 10 9 8 7 6 5 4 3 2 1}, where each bit is either 0 or 1 as follows:

Bit #1: 1 to export flat-pattern geometry; 0 to not
Bit #2: 1 to include hidden edges; 0 to not
Bit #3: 1 to export bend lines; 0 to not
Bit #4: 1 to include sketches; 0 to not
Bit #5: 1 to merge coplanar faces; 0 to not
Bit #6: 1 to export library features; 0 to not
Bit #7: 1 to export forming tools; 0 to not
Bit #12: 1 to export bounding box; 0 to not
```

★ 官方自带的换算例证逐字：`if you want to export: flat-pattern geometry, bend lines, and sketches, then Bits 1, 3, and 4 are 1, the bitmask is 0001101, and you need to set SheetMetalOptions = 2^0 + 2^2 + 2^3 = 1 + 4 + 8 = 13.`
★ Alignment 口径逐字：`Array[0], Array[1], Array[2] - x,y,z coordinates of new origin` / `Array[3], Array[4], Array[5] - coordinates of new x direction vector` / `Array[6], Array[7], Array[8] - coordinates of new y direction vector` / `Array[9], Array[10], Array[11] - coordinates of the vector that is normal to the selected faces or loops`；并逐字写 `Passing an array of 12 zeros results in a default orientation being used.`

**③ 枚举** —— `Action` → [en] `C:\swapi\enums\swExportToDWG_e.md` 描述 `Options for the Action parameter of [[IPartDoc::ExportToDWG2]].`，成员表逐字：

| Member | Value |
| --- | --- |
| `swExportToDWG_ExportAnnotationViews` | 3 |
| `swExportToDWG_ExportSelectedFacesOrLoops` | 2 |
| `swExportToDWG_ExportSheetMetal` | 1; Valid only if the active document contains sheet metal |

**④ 仓内那一段** —— `scripts/sw_export.py` 的常量块逐字：

```
SW_EXPORT_TO_DWG_SHEET_METAL = 1
SW_SHEET_METAL_EXPORT_GEOMETRY = 1
SW_SHEET_METAL_EXPORT_HIDDEN_EDGES = 2
SW_SHEET_METAL_EXPORT_BEND_LINES = 4
SW_SHEET_METAL_EXPORT_SKETCHES = 8
SW_SHEET_METAL_EXPORT_MERGE_COPLANAR_FACES = 16
SW_SHEET_METAL_EXPORT_LIBRARY_FEATURES = 32
SW_SHEET_METAL_EXPORT_FORMING_TOOLS = 64
SW_SHEET_METAL_EXPORT_BOUNDING_BOX = 2048
```

同文件 `export_flat_pattern_dxf` 的调用与默认对齐逐字：

```
    options = SW_SHEET_METAL_EXPORT_GEOMETRY
```

```
    return bool(model.ExportToDWG2(
        output_path,
        model_path,
        SW_EXPORT_TO_DWG_SHEET_METAL,
        True,
        _sheet_metal_alignment_variant(alignment),
        False,
        False,
        options,
        None,
    ))
```

```
    values = tuple(alignment or (0.0,) * 12)
```

**⑤ 逐项对照（官方 2^n ↔ 仓内值）**

| 官方 bit | 官方语义 | 官方值 | 仓内常量 | 仓内值 | 对 |
|---|---|---|---|---|---|
| Bit #1 | flat-pattern geometry | 2^0 = 1 | `SW_SHEET_METAL_EXPORT_GEOMETRY` | 1 | ✔ |
| Bit #2 | hidden edges | 2^1 = 2 | `SW_SHEET_METAL_EXPORT_HIDDEN_EDGES` | 2 | ✔ |
| Bit #3 | bend lines | 2^2 = 4 | `SW_SHEET_METAL_EXPORT_BEND_LINES` | 4 | ✔ |
| Bit #4 | sketches | 2^3 = 8 | `SW_SHEET_METAL_EXPORT_SKETCHES` | 8 | ✔ |
| Bit #5 | merge coplanar faces | 2^4 = 16 | `SW_SHEET_METAL_EXPORT_MERGE_COPLANAR_FACES` | 16 | ✔ |
| Bit #6 | library features | 2^5 = 32 | `SW_SHEET_METAL_EXPORT_LIBRARY_FEATURES` | 32 | ✔ |
| Bit #7 | forming tools | 2^6 = 64 | `SW_SHEET_METAL_EXPORT_FORMING_TOOLS` | 64 | ✔ |
| Bit #12 | bounding box | 2^11 = 2048 | `SW_SHEET_METAL_EXPORT_BOUNDING_BOX` | 2048 | ✔ |
| Action | `swExportToDWG_ExportSheetMetal` | 1 | `SW_EXPORT_TO_DWG_SHEET_METAL` | 1 | ✔ |
| Alignment | 12 个 0 = 官方写明的默认朝向 | 12 zeros | `_sheet_metal_alignment_variant(None)` | 12 zeros | ✔ |

**一句话依据**：官方 Remarks 把 bit→语义的对应逐条列出并给出 `2^0 + 2^2 + 2^3 = 13` 的换算例，仓内 8 个常量的值与之**逐个相等**；`Action` 取值与 `swExportToDWG_ExportSheetMetal = 1` 相等；默认对齐参数是官方明写「合法且等于默认朝向」的 12 个零。⇒ **这一段没有可报的偏差**。

## 1.2 出处标注层 · 判定：**成立**（**仅出处标注**，非功能缺陷）

**① 仓内那一段** —— `scripts/sw_export.py` 的来源块「官方依据」逐字：

```
# 官方依据: `IModelDocExtension.SaveAs3`（★ `export_to_image` 走它）·
#   `IModelDoc2.ExportToDWG2(..., swExportToDWG_e)`（★ `export_flat_pattern_dxf` 走它）
```

**② 官方那一段** —— `C:\swapi\types\IPartDoc\ExportToDWG2.md` 的 front-matter 与标题逐字：

```
type: IPartDoc
```

```
# IPartDoc.ExportToDWG2
```

同文件 `## See Also` 末两条逐字 `- [[IPartDoc Interface]]` / `- [[IPartDoc Members]]`（**没有** `IModelDoc2`）。
★ 反向检索证据：`Get-ChildItem 'C:\swapi\types\IModelDoc2\' -Filter '*DWG*'` 返回**空**；`Select-String -Path 'C:\swapi\types\IModelDoc2\*.md' -Pattern 'ExportToDWG2' -List` 返回 **0 个文件**。

**一句话依据**：仓内把该成员的归属接口写成 `IModelDoc2`，而本机官方离线源里这一页只存在于 `IPartDoc` 之下、`IModelDoc2` 目录**零命中**。
★ **强度说明（必读）**：这只是**出处标注**与官方页面归属不符；`IModelDoc2` 在 COM 里确实暴露该成员，调用本身不是「用错接口」，故**不构成功能缺陷**，只记出处层。

---

# 二、镜像（`InsertMirrorFeature2`）

## 2.1 mark 表与 `ScopeOptions` · 判定：**不成立**（与官方逐字一致）

**① 精确签名** —— [md] `C:\swapi\types\IFeatureManager\InsertMirrorFeature2.md` 逐字：

```
Feature InsertMirrorFeature2( System.bool BMirrorBody, System.bool BGeometryPattern, System.bool BMerge, System.bool BKnit, System.int ScopeOptions )
```

★ **5 个参数**；描述句 `Mirrors selected features, faces, bodies, and structure systems about a selected plane or planar face.`；`## Returns` = `[[Feature]]`。
[md] `## Parameters` 逐条：`BMirrorBody`: True to mirror solid bodies; false to mirror a feature or face · `BGeometryPattern`: True to mirror only the feature geometry, false to solve the entire feature; **applies to mirroring features only** · `BMerge`: True to merge any mirrored solid bodies, false to not; **applies to mirroring solid bodies only** · `BKnit`: True to knit surfaces, false to not; **applies to mirroring surfaces only** · `ScopeOptions`: Feature scope as defined by [[swFeatureScope_e]]。

**② ## Remarks 逐字（★ 本片唯一「官方给了完整 mark 表」的一条）** —— [md] 原文片段 `Must be preselected and marked with a value of`：

```
This method attempts to create the mirror feature without displaying a dialog box to get information from the user. It relies on preselected and marked entities and arguments.

**Must be preselected and marked with a value of...**

Features

1

Faces

128

Bodies

256

Structure systems

134217728

Planes or planar faces

2

For information on selecting and marking entities, see [[IModelDocExtension::SelectByID2]].
```

**③ 枚举** —— `ScopeOptions` → [en] `C:\swapi\enums\swFeatureScope_e.md`，描述 `Feature scope options.`，`enum_member_count: 3`：

| Member | Value |
| --- | --- |
| `swFeatureScope_AllBodies` | 0 = All of the bodies in the multibody part are affected by the Mirror feature. |
| `swFeatureScope_SelectedBodiesWithAutoSelect` | 1 = Only the specified bodies in the multibody part are affected by the Mirror feature when AutoSelect is true. |
| `swFeatureScope_SelectedBodiesWithOutAutoSelect` | 2 = … when AutoSelect is false. |

**④ 仓内那一段** —— `scripts/sw_part.py` 的 `mirror_feature` 逐字：

```
    #: ★★★ 2026-10-01（轮 317）**mark 分配原本是反的** ——
    #:   官方 `InsertMirrorFeature2.md` 的 Remarks 给了**完整的 mark 表**：
    #:     ★ **Features ⇒ 1** · ★ Faces ⇒ 128 · ★ Bodies ⇒ 256 ·
    #:     ★ **Planes or planar faces ⇒ 2** · ★ Structure systems ⇒ 134217728
    #:   ★ 而旧写法是：特征 mark=**4**（★ **表里没有 4**）· 平面 mark=1（★ 而 1 是**特征**）
    #:   ⇒ ★★ **两个都错** ⇒ `InsertMirrorFeature2` 静默回 `None`。
```

```
    _select_by_id(model.Extension, feature_name, "BODYFEATURE", mark=1)
    _select_by_id(model.Extension, mirror_plane_name, "PLANE", append=True, mark=2)
    return model.FeatureManager.InsertMirrorFeature2(False, False, False, False, 0)
```

**⑤ 废弃链** —— **非 Obsolete**（[md] 无 `Obsolete` 字样）。**查不到后继**。

**一句话依据**：官方 mark 表给 `Features = 1`、`Planes or planar faces = 2`，仓内两处 `_select_by_id` 的 `mark=1` / `mark=2` 与之**逐个相等**；末位 `ScopeOptions=0` 落在 `swFeatureScope_e.swFeatureScope_AllBodies` 的合法取值域内；该成员官方**未标 Obsolete**。⇒ **这一段没有可报的偏差**。
★ 附带事实（不判为偏差）：官方 `BMirrorBody: … false to mirror a feature or face` 与仓内首位实参 `False` 一致；`BMerge` / `BKnit` 官方限定「applies to mirroring solid bodies / surfaces only」，仓内传 `False` 与之不冲突。

---

# 三、阵列（`FeatureLinearPattern3` / `FeatureCircularPattern4`）

## 3.1 仓内调的是官方 **Obsolete** 成员 · 判定：**成立**

**① 仓内那一段** —— `scripts/sw_part.py` 两处逐字：

```
    return model.FeatureManager.FeatureLinearPattern3(
        int(d1_count), float(d1_spacing),
        int(d2_count), float(d2_spacing),
        False, False,
        f"{d1_x} {d1_y} {d1_z}",
        f"{d2_x} {d2_y} {d2_z}",
        False, False
    )
```

```
    return model.FeatureManager.FeatureCircularPattern4(
        count, angle_rad, False, "None", False, equal_spacing, False
    )
```

第二处实参逐字：`count, angle_rad, False, "None", False, equal_spacing, False`（**7 个**，与官方签名同形）。
★ 第三处（可执行路径，非包装）：`scripts/sw_part.py` 的 `linear_pattern_report` 体内逐字

```
        get_com_member(get_com_member(model, "FeatureManager"), "FeatureLinearPattern3",
                       n1, s1, n2, s2, False, False, "", "", False, False)
```

**② 官方那一段** —— [md] `C:\swapi\types\IFeatureManager\FeatureLinearPattern3.md` 标题下第一句逐字：

```
Obsolete. Superseded by [[IFeatureManager::FeatureLinearPattern4]].
```

[md] `C:\swapi\types\IFeatureManager\FeatureCircularPattern4.md` 同位置逐字：

```
Obsolete. Superseded by [[IFeatureManager::FeatureCircularPattern5]].
```

★ 链尾（同源可查）：[md] `FeatureCircularPattern5.md` 标题下逐字 `Obsolete. See [[IFeatureManager::CreateFeature]] and the Remarks in [[ICircularPatternFeatureData]] and [[ILocalCircularPatternFeatureData]].`；[md] `FeatureLinearPattern4.md` 逐字 `Obsolete. Superseded by [[IFeatureManager::FeatureLinearPattern5]].`

**一句话依据**：仓内 `linear_pattern` / `linear_pattern_report` / `circular_pattern` 三条路径调用的两个成员，官方页**标题下第一句**就写着 `Obsolete`，并逐字点名了后继（`Pattern4` / `Pattern5`）——而这两个后继成员在仓内 `scripts/sw_api_sldworks.py` 的官方索引里**已列出**（`'FeatureCircularPattern5': 14` / `'FeatureLinearPattern4': 20`），却无任何调用点。

## 3.2 旧包装 `linear_pattern` 把**毫米**直接传给官方「in meters」的 `Spacing1` · 判定：**成立**（且**与同仓另一条路径自相矛盾**）

**① 仓内那一段** —— `scripts/sw_part.py` 的 `linear_pattern` 签名与 docstring 逐字：

```
def linear_pattern(model, feature_name, d1_x, d1_y, d1_z, d1_spacing, d1_count,
                    d2_x=0, d2_y=0, d2_z=0, d2_spacing=0, d2_count=1):
```

```
        d1_*: 方向1 的方向向量、间距（**毫米**，⚠ 间距已测；**方向向量是否归一化未测**）和数量
```

```
    return model.FeatureManager.FeatureLinearPattern3(
        int(d1_count), float(d1_spacing),
```

★ 对照**同仓另一条路径** `linear_pattern_report` 的 docstring 与换算行逐字（同一文件内）：

```
    ★★ **单位**：★ 官方原话 —— `Spacing1` “Spacing between each instance … **in meters**”
      ⇒ ★ 本包装对外收 **`spacing_mm`（毫米）**，在**这里**换算成米（★ 规则 2）。
      ⚠ ★ 这**修正**了 `linear_pattern` 原文档串里「间距（**毫米**）」那句错话。
```

```
        s1 = float(spacing_mm) * 0.001                             #: ★ 毫米 ⇒ 米
```

**② 官方那一段** —— [md] `C:\swapi\types\IFeatureManager\FeatureLinearPattern3.md` 的 `## Parameters` 两条逐字：

```
- **Spacing1**: Spacing between each instance of the linear pattern in Direction 1 in meters
```

```
- **Spacing2**: Spacing between each instance of the linear pattern in Direction 2 in meters
```

★ mark 前置同页 `## Remarks` 逐字（供交叉核对）：

```
- 4 to mark the features to pattern
```

**一句话依据**：官方把 `Spacing1/Spacing2` 的单位逐字写死为 `in meters`，而旧包装 `linear_pattern` 的 docstring 自述「间距（**毫米**）」并把 `float(d1_spacing)` **原样**透传；同仓 `linear_pattern_report` 的 docstring 明写这句「**错话**」并做了 `* 0.001` 换算 ⇒ 两条路径对同一参数的单位处理相反。
★ mark 侧无偏差：官方 `4 to mark the features to pattern`，仓内 `linear_pattern` 用的是 `mark=4`、`circular_pattern` 用的是 `mark=4`（特征）+ `mark=1`（方向轴），与 `FeatureCircularPattern4.md` Remarks 的 `1 to mark the direction axis` / `4 to mark the features to pattern` 一致。
★ 附带事实（不判为偏差）：`FeatureCircularPattern4.md` 的 `Spacing` 参数逐字写 `total angle in radians if EqualSpacing is true`，仓内 `circular_pattern` 形参名即 `angle_rad` 并原样透传。

---

# 四、平板型式（展开）

## 4.1 展开入口在仓内**零实现** · 判定：**成立**（缺口）

**① 仓内那一段** —— 全仓 `*.py` 检索 `InsertSheetMetalUnfold|GetFlatPatternFolder` 的命中**全部**落在同一份**反射抄录索引**里（该文件首行 docstring 自述其为「官方 API 的完整抄录 —— 523 个接口族、**8210 个成员**，逐个照抄自对官方 interop 程序集的**纯元数据反射**」）：

```
    call_index(对象, "族名", "成员名", *参数)
```

索引内的逐字条目（同文件 `IFeatureManager` 段与 `IModelDoc2` 段各一处）：

```
        'GetFlatPatternFolder': 0,
```

```
        'InsertSheetMetalUnfold': 0,
```

第二处（第二份文件 `_merged_test.py`，内容为同一索引的另一份副本）逐字：

```
        'FinishCornerRelief': 0,
        'GetFlatPatternFolder': 0,
```

★ 反向证据：`scripts/` 与 `mcp-server/` 的**其它**文件（`sw_sheet_metal.py` / `sw_sheet_metal_weld_entry.py` / `sw_export.py` / `sw_part.py` / 全部 `tool_specs_*.py`）对这 6 个符号**零命中**。
★ 仓内唯一**以字符串形式**提到展开的，是 `scripts/sw_capability_probe.py` 的类型库关键词表逐字：

```
    "sheet_metal": ("ISheetMetalFeatureData", "IFlatPatternFeatureData"),
```

（同文件上下文逐字 `CAPABILITY_KEYWORDS = {` / `CAPABILITY_ALIASES = {` / `"sheet_metal": "sheet_metal",` ⇒ 该字典用于**探测 typelib 是否存在**，不是功能调用。）

**② 官方那一段** —— [md] `C:\swapi\types\IModelDoc2\InsertSheetMetalUnfold.md` 逐字：

```
# IModelDoc2.InsertSheetMetalUnfold

Inserts an unfold feature at the selected objects.

**Signature**: `void InsertSheetMetalUnfold()`

## Remarks
Select the objects for the unfold feature before calling this method.
```

★ 该页**没有 `## Parameters` 段**、**没有 `## Returns` 段**（回 `void`）；`## Examples` 列 `Insert_and_Access_Fold_Feature_Example_{CSharp,VBNET,VB}`（**本轮未读这三个例子文件** ⇒ 逐字调用序查不到**）。
★ 结果读回侧官方入口：[md] `C:\swapi\types\IFlatPatternFolder\_overview.md` 与同目录 `GetFlatPatterns.md` / `GetFlatPatternCount.md` / `GetFeature.md` **存在**（本轮只确认文件存在，未逐字抄录其正文 ⇒ **正文查不到**）。
★ 前置侧官方入口：[md] `C:\swapi\types\IFeatureManager\GetFlatPatternFolder.md` **存在**（**本轮未打开 ⇒ 正文查不到**）。

**一句话依据**：官方把「插入展开特征」的入口写成一个**零参 `void`** 方法且**必须先选对象**，读回侧另有 `IFlatPatternFolder` 一族；而仓内这几个符号**只出现在反射抄录索引里**，没有任何可执行调用、没有 MCP 工具、没有 spec ⇒ **该子面在本仓是空的**。

---

# 五、转角处理

## 5.1 官方三套转角入口在仓内**零实现** · 判定：**成立**（缺口）

**① 仓内那一段** —— 同 §4.1 那份反射抄录索引内的逐字条目（第一份文件 `scripts/sw_api_sldworks.py`）：

```
        'FinishCornerRelief': 0,
```

```
        'InsertSheetMetalCornerTrim': 5,
```

```
        'SetAddCornerTrim': 1,
        'SetBreakCorners': 1,
```

（第二份副本 `_merged_test.py` 逐字相同：`'FinishCornerRelief': 0,` / `'InsertSheetMetalCornerTrim': 5,` / `'SetBreakCorners': 1,` / `'SetAddCornerTrim': 1,`。）
★ 反向证据：`scripts/` 与 `mcp-server/` 的**其它**文件对这 6 个符号**零命中**。
★ 仓内**确实实现了**的钣金转角只有一处，`scripts/sw_sheet_metal_weld_entry.py` 的入口状态表逐字：

```
SHEET_METAL_WELD_ENTRY_STATUS = {
    "钣金/斜接法兰": "IFeatureManager.InsertSheetMetalMiterFlange（14 参）"
```

```
    "钣金/闭合角": "IModelDoc2.InsertSheetMetalClosedCorner（零参 · 回 void）",
```

⇒ 该表**只列 2 项**钣金转角类入口（斜接法兰、闭合角），**不含** break-corner / corner-relief / corner-trim。

**② 官方那一段** —— 三页逐字：

[md] `C:\swapi\types\IFeatureManager\FinishCornerRelief.md`（描述句 + Signature + **完整 5 步前置**）逐字：

```
Creates a sheet metal corner relief feature.

**Signature**: `Feature FinishCornerRelief()`

## Remarks
Before calling this method, call:

1. [[IModelDocExtension::SelectByID2]] with Mark = 0 and Append = true to select the sheet metal body in which to create a corner relief feature.

2. IModelDocExtension::SelectByID2 with Mark = 4 and Append = true to select two faces that form a bend corner.

3. Call [[IFeatureManager::AddCornerReliefCorner]] to add the corner to the corner relief feature.

4. Call [[IFeatureManager::AddCornerReliefType]] to specify the corner relief for the corner.

5. Repeat steps 2 - 4 to add another corner to the corner relief feature.
```

[md] `C:\swapi\types\IFeatureManager\InsertSheetMetalCornerTrim.md` 逐字：

```
Inserts a break corner trim in the sheet metal part.

**Signature**: `Feature InsertSheetMetalCornerTrim( System.int InternalCornerFlag, System.int BreakType, System.double BreakDist, System.int ReliefType, System.double Param )`
```

同页 `## Parameters` 逐字（★ `ReliefType` / `Param` 官方给的是内联字面量表、**不是枚举**）：

```
- **InternalCornerFlag**: Do internal corners only
- **BreakType**: Type of break as defined in [[swBreakCornerTypes_e]]
- **BreakDist**: Distance to break from corner
- **ReliefType**: Type of relief:

  - 0 = circular

  - 1 = square

  - 2 = bend-waist
- **Param**: ReliefType dependent:

  - circular, its diameter

  - square, its side length

  - bend-waist, its radius
```

[md] `C:\swapi\types\IFlatPatternFeatureData\SetBreakCorners.md` 逐字（`category` 为 `Feature Interfaces/Sheet Metal`）：

```
Sets whether to add break corners to the Flat-Pattern feature.

**Signature**: `void SetBreakCorners( System.bool BBreakCorner )`

## Parameters
- **BBreakCorner**: True to add break corners, false to not
```

**一句话依据**：官方把转角处理拆成**三套**入口（`FinishCornerRelief` 的 5 步选择序、`InsertSheetMetalCornerTrim` 的 5 参、`IFlatPatternFeatureData.SetBreakCorners`），而仓内这些符号**只出现在反射抄录索引里**，可执行的钣金转角只有斜接法兰与闭合角两项 ⇒ **三套入口全部没有实现**。
★ 归属事实：`IFlatPatternFeatureData` 的 front-matter 逐字 `category: Feature Interfaces/Sheet Metal`，描述句 `Allows access to a Flat-Pattern feature.`；该接口 24 个成员里与转角相关的有 `CornerTreatment` / `BreakCornerType` / `BreakCornerRadius` / `CornerTrimRatioToThickness` / `CornerTrimReliefDistance` / `CornerTrimReliefType` / `UseRatioToThickness` / `ShowSlitInCornerRelief` / `GetAddCornerTrim` / `SetAddCornerTrim` / `GetBreakCorners` / `SetBreakCorners`（`Enums` 侧 `swBreakCornerTypes_e` **本轮未打开 ⇒ 成员与数值查不到**）。

---

# 六、本片结论（只数可核的）

| # | 子面 | 主题 | 判定 | 一句话依据 |
|---|---|---|---|---|
| 1.1 | 导出 | `SheetMetalOptions` 8 常量 + `Action` + 12 零对齐 | **不成立** | 官方 bit→语义表与仓内常量**逐个相等**（1/2/4/8/16/32/64/2048，Action=1） |
| 1.2 | 导出 | 出处标注写 `IModelDoc2.ExportToDWG2`，官方页在 `IPartDoc` | **成立**（仅出处层） | `C:\swapi\types\IModelDoc2\*.md` 对 `ExportToDWG2` **零命中** |
| 2.1 | 镜像 | `InsertMirrorFeature2` mark 表 + `ScopeOptions=0` | **不成立** | 官方 `Features=1`/`Planes or planar faces=2`，仓内 mark 相同；`0` 在 `swFeatureScope_e` 域内 |
| 3.1 | 阵列 | 调官方 **Obsolete** 的 `FeatureLinearPattern3` / `FeatureCircularPattern4` | **成立** | 两个官方页标题下第一句即 `Obsolete. Superseded by …` |
| 3.2 | 阵列 | `linear_pattern` 把毫米直接传给官方 `in meters` 的 `Spacing1` | **成立** | 官方 `Spacing1 … in meters`；同仓 `linear_pattern_report` 做了 `* 0.001` 并自述旧文档串是「错话」 |
| 4.1 | 平板型式 | `InsertSheetMetalUnfold` / `GetFlatPatternFolder` 仓内零实现 | **成立** | 官方零参 `void` + 必须先选对象；仓内只在反射抄录索引里命中 |
| 5.1 | 转角处理 | `FinishCornerRelief` / `InsertSheetMetalCornerTrim` / `SetBreakCorners` 仓内零实现 | **成立** | 官方三页逐字给出签名与 5 步前置；仓内可执行转角只有斜接法兰 + 闭合角 |

**核了 7 处 · 判定 成立 5 · 不成立 2 · 存疑 0 ⇒ 对不上 5 处。**

---

# 结尾三行

- **文件路径**：`D:\AI\SW\specs\202-user-coverage-gaps\recon\verify50\vd50-C-sm-3.md`
- **核了 7 处**（镜像 1 · 阵列 2 · 转角处理 1 · 平板型式 1 · 导出 2），每处均给出「仓内原文 + 官方原文」两段可搜索片段。
- **对不上 5 处**（阵列 2 · 转角处理 1 · 平板型式 1 · 导出出处层 1）；**对得上 2 处**（镜像 mark 表与 `ScopeOptions`、导出的 8 个 bitmask 常量 + `Action` + 12 零对齐，全部与官方逐字相等）。
