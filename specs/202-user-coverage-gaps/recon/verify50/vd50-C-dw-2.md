# vd50-C-dw-2 —— 工程图域（尺寸 / 公差 / GD&T / 表面粗糙度 / 基准符号 / 气泡序号）契约摘要与双向核对

**补的缺口**：`recon/api-pre/api-05-drawing.md` —— 全仓库 0 命中（`glob **/api-05-drawing.md` 返回 `No files found`；`recon/api-pre/INDEX.md` 的源清单里它那一行也写着 `⚠ **不存在**`）。
本文件是**按 `recon/api-pre/api-03-weldment.md` 的同格式**写出来的分域契约摘要 + 逐条双向核对，**不改仓内任何文件**。

> ★ 三条纪律：只抄亲手读到的内容 · 每条给「仓内那一段」+「官方那一段」两段可搜索原文 · **不写行号**（行号会漂移，只写原文片段）。
> ★ 判定口径：**成立** = 两段原文逐字对得上、仓内按官方契约做 · **不成立** = 对不上 · **存疑** = 官方没写或查不到。
> ★ 给不出两段原文的一律不写；查不到就说查不到。

**本片用的源（全部本机，未联网）**

| 简称 | 路径 | 抄什么 |
|---|---|---|
| **[md]** | `C:\swapi\types\<接口>\<成员>.md` | 精确签名、`## Parameters`、`## Remarks`、`## Examples` 逐字 |
| **[ex]** | `C:\swapi\examples\<例子>.md` | 官方例子调用序与实参取值 |
| **[en]** | `C:\swapi\enums\<枚举>.md` | 枚举成员与数值 |
| **仓内** | `scripts/` · `mcp-server/` · `subskills/` · `tools/` · `capabilities.yaml` | 实际调用点与逐字注释 |

---

## 总表

| # | 主题 | 契约对象 | 判定 | 一句话依据 |
|---|---|---|---|---|
| DW2-1 | 尺寸 | `IDisplayDimension.GetText(0)` 当「全文本」 | **不成立** | 官方逐字把 `swDimensionTextAll` 排除在 `GetText` 的合法值之外。 |
| DW2-2 | 尺寸 | 兜底读 `IDisplayDimension.GetTextFormat()` | **不成立** | 官方逐字 `Obsolete. Superseded by IAnnotation::GetTextFormat`。 |
| DW2-3 | 公差 | `TABLE_ANNOTATION_KINDS[6] = "general_tolerance"` | **不成立** | 官方 `6 = swTableAnnotation_WeldTable`、`9 = swTableAnnotation_GeneralTolerance`。 |
| DW2-4 | GD&T（写） | `GTOL_INDICATOR_ALLOWED_TOL_TYPES` 五个值 | **成立** | 与官方 `AddIndicator` Remarks 逐字列的 5 个 `swGcs*` 一一对应。 |
| DW2-5 | GD&T（读） | `range(frame_count)` 遍历 `GetFrameSymbols3/GetFrameValues` | **不成立** | 官方 `FrameNumber: Frame number to examine (1 or 2)`，且限「2022 之前创建的 Gtol」。 |
| DW2-6 | 表面粗糙度（写） | `leader_type == 0` 时主动传 `0,0,0` | **成立** | 官方 Remarks 逐字「位置参数仅在 `leaderType != swNO_LEADER` 时被使用」。 |
| DW2-7 | 表面粗糙度（读） | 先读 `ISFSymbol.GetSymbolType` 再读 `GetSymbol` | **不成立** | 官方逐字 `Obsolete. Superseded by ISFSymbol::GetSymbol`。 |
| DW2-8 | 基准符号 | `InsertDatumTag2()` 零参 + 前置「先选位置」 | **成立** | 官方签名零参、描述逐字「at a selected location」、示例逐字先 `SelectByID2("", "EDGE", …)`。 |
| DW2-9 | 气泡序号 | `AutoBalloon5` 四步调用序 + 示例默认值 | **成立** | 官方 `AutoBalloon5` / `CreateAutoBalloonOptions` 的 Remarks 与示例逐字对得上。 |

**合计：9 条 · 成立 4（DW2-4 / DW2-6 / DW2-8 / DW2-9）· 不成立 5（DW2-1 / DW2-2 / DW2-3 / DW2-5 / DW2-7）· 存疑 0。**

---

## 〇 · 名字缺席 / 查不到（铁律 5）

| 想找的 | 结果 | 证据 |
|---|---|---|
| 工程图域的**尺寸公差**读写（`IDimension.GetToleranceType` / `GetToleranceValues` / `IDimensionTolerance`）在**能力模块**里的调用点 | **查不到** | 全仓 `GetToleranceType\|SetToleranceType\|SetToleranceValues` 只命中 12 处，**全部**在生成物 `scripts/sw_api_sldworks.py` 与其副本 `_merged_test.py` 的接口登记表里；`scripts/` / `subskills/` 下无任何工程图能力模块调用它们。⇒ 本仓工程图域的尺寸公差**读写是空的**。 |
| 本仓 `TABLE_ANNOTATION_KINDS` 是否覆盖官方全部表类型 | **查不到**（不是「不成立」） | 仓内该字典只有 7 个键，官方 `swTableAnnotationType_e` 有 11 个成员；**仓内没有任何注释声明这是刻意只列一部分**，官方页也没有说「某些类型可以不列」⇒ 只在 DW2-3 记**已证伪的那一条**，不推断其余 4 个缺口。 |

---

# 一、尺寸（2 条）

## DW2-1 · `IDisplayDimension.GetText(0)` 当「全文本」 ★不成立

**① 精确签名 —— [md] `C:\swapi\types\IDisplayDimension\GetText.md` 的 `**Signature**:` 逐字**

```
System.string GetText( System.int WhichText )
```

**② ## Remarks 逐字 —— [md] 同一文件 `## Remarks` 段**

```
swDimensionTextParts_e.swDimensionTextAll is not a valid value for the WhichText parameter for this method.
```

**③ 枚举 —— [en] `C:\swapi\enums\swDimensionTextParts_e.md` 成员表逐字（两行）**

```
| swDimensionTextAll | 0 = Entire dimension text string ([[IDisplayDimension::SetText]] only) |
| swDimensionTextPrefix | 1 = Prefix portion of the text |
```

**④ 仓内那一段 —— `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py` 的 `_dimension_text_evidence` 逐字**

```python
    for index, label in ((0, "all"), (1, "prefix"), (2, "suffix"), (3, "callout_above"), (4, "callout_below")):
        value = str(_safe_member(display_dimension, "GetText", index, default="") or "")
```

紧接着它把 `0` 的返回值当主值，逐字：

```python
    all_text = next((item["text"] for item in parts if item["kind"] == "all"), "")
```

同一函数里已有一句自述症状的注释，逐字：

```python
        # GetText() 在 SW2026 常只返回用户前后缀，不返回格式化后的主尺寸值。
```

**⑤ 官方例子调用序 —— [ex] `C:\swapi\examples\Get_Annotations_Array_Example_VB.md`** 里读尺寸**不走 `GetText`**，逐字走 `IDimension`：

```
                Set swDim = DisplayDimension.GetDimension
```

```
                    msg = "Display dimension found: " & swView.GetName2 & ":" & DisplayDimension.GetAnnotation.GetName & " = " & swDim.GetSystemValue2("") & " meters"
```

**判定：不成立。**
一句话依据：官方逐字把 `swDimensionTextAll` 排除在 `GetText` 的合法 `WhichText` 之外（枚举条目自身也写 `([[IDisplayDimension::SetText]] only)`），而仓内把 `0` 标成 `"all"` 并用它当 `all_text` 的唯一来源 ⇒ 这一支**按官方契约永远取不到值**，与仓内注释观察到的症状一致。
★ 官方给的读法在同仓可查：`IDisplayDimension.GetDimension` + `IDimension.GetSystemValue2`（[ex] 上文两行逐字）。

**前置一句话**：`GetText` 无前置；合法 `WhichText` 只有 1/2/3/4/5/6/7/8，**0 不在其中**。
**配方一句话**：查不到（官方该成员没有 `## Examples` 段里与 `GetText` 直接配对的调用序；[md] 该文件没有 `## Examples` 段）。

---

## DW2-2 · 尺寸文字格式的兜底读法用了官方标 Obsolete 的成员 ★不成立

**① 精确签名 —— [md] `C:\swapi\types\IDisplayDimension\GetTextFormat.md` 逐字三行**

```
# IDisplayDimension.GetTextFormat

Obsolete. Superseded by [[IAnnotation::GetTextFormat]].
```

签名逐字：

```
System.object GetTextFormat()
```

**② 后继成员签名 —— [md] `C:\swapi\types\IAnnotation\GetTextFormat.md` 逐字**

```
System.object GetTextFormat( System.int Index )
```

同一文件 Remarks 里关于**显示尺寸**的那一段逐字：

```
- [[Geometric Tolerance]], [[display dimensions]], [[simple notes]], [[surface finish]], and [[weld symbols]]

  These symbols can either use the document default setting to display text within
  the symbol (dimension text setting for the geometric tolerance symbols and display
  dimensions, or note text setting for notes) or they can use a local format. The index
  argument is not used and should be set to 0.
```

**③ 仓内那一段 —— `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py` 的 `estimate_dimension_text_box` 逐字**

```python
    text_format = _safe_member(annotation, "GetTextFormat", 0)
    format_source = "IAnnotation.GetTextFormat(0)"
    if text_format is None:
        text_format = _safe_member(display_dimension, "GetTextFormat")
        format_source = "IDisplayDimension.GetTextFormat()"
```

**判定：不成立。**
一句话依据：官方逐字把 `IDisplayDimension.GetTextFormat` 标 `Obsolete` 并点名后继是 `IAnnotation::GetTextFormat`，而仓内**主路径已经走对了后继**（`IAnnotation.GetTextFormat(0)`，与官方「display dimensions … index … should be set to 0」一致），**兜底那一支仍调被废弃的 `IDisplayDimension.GetTextFormat()`**。

---

# 二、公差（1 条）

## DW2-3 · 通用公差表（general tolerance table）的类型号被写成 6 ★不成立

**① 精确契约 —— [md] `C:\swapi\types\ITableAnnotation\Type.md` 逐字**

```
System.int Type {get;}
```

`## Returns` 逐字：

```
Type of table as defined in [[swTableAnnotationType_e]]
```

**② 枚举 —— [en] `C:\swapi\enums\swTableAnnotationType_e.md` 成员表逐字（`enum_member_count: 11`，全 11 行照抄）**

```
| Member | Value |
| --- | --- |
| swTableAnnotation_BendTable | 7 |
| swTableAnnotation_BillOfMaterials | 2 |
| swTableAnnotation_FamilyTable | 10 |
| swTableAnnotation_General | 0 |
| swTableAnnotation_GeneralTolerance | 9 |
| swTableAnnotation_HoleChart | 1 |
| swTableAnnotation_PunchTable | 8 |
| swTableAnnotation_RevisionBlock | 3 |
| swTableAnnotation_TitleBlock | 5 |
| swTableAnnotation_WeldmentCutList | 4 |
| swTableAnnotation_WeldTable | 6 |
```

**③ 仓内那一段 —— `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py` 的 `TABLE_ANNOTATION_KINDS` 逐字**

```python
TABLE_ANNOTATION_KINDS = {
    0: "general",
    1: "hole_chart",
    2: "bom",
    3: "revision",
    4: "weldment_cut_list",
    5: "title_block",
    6: "general_tolerance",
}
```

它的唯一消费点逐字（同文件 `_table_evidence`，值来自 `ITableAnnotation.Type`）：

```python
        "kind": TABLE_ANNOTATION_KINDS.get(normalized_type, "unknown"),
```

**判定：不成立。**
一句话依据：官方把 `6` 定义为 `swTableAnnotation_WeldTable`、把 `swTableAnnotation_GeneralTolerance` 定为 `9`，而仓内字典把 `6` 标成 `"general_tolerance"` 且**没有 `9` 这个键** ⇒ 真正的通用公差表（Type=9）会被打成 `"unknown"`，而焊接表（Type=6）会被误报成公差表。

---

# 三、GD&T / 形位公差（2 条）

## DW2-4 · `AddIndicator` 的 `TolType` 允许清单（写侧） ★成立

**① 精确签名 —— [md] `C:\swapi\types\IGtolFrame\AddIndicator.md` 逐字**

```
System.bool AddIndicator( System.int BorderType, System.int TolType, System.string Datum )
```

**② ## Remarks 逐字 —— [md] 同一文件（`TolType may be one of only` 那段）**

```
TolType may be one of only swGtolGeomCharSymbol_e.:

- swGcsANG

- swGcsPARALLEL

- swGcsPERP

- swGcsCIRCRUNOUT

- swGcsSYMMETRY
```

**③ 枚举 —— [en] `C:\swapi\enums\swGtolGeomCharSymbol_e.md` 里这 5 个成员逐字**

```
| swGcsANG | 20 |
| swGcsCIRCRUNOUT | 25 |
| swGcsPARALLEL | 22 |
| swGcsPERP | 21 |
| swGcsSYMMETRY | 13 |
```

**④ 仓内那一段 —— `scripts/sw_gtol.py` 逐字**

```python
GTOL_INDICATOR_ALLOWED_TOL_TYPES = {
    20: "angularity", 22: "parallelism", 21: "perpendicularity",
    25: "circular_runout", 13: "symmetry",
}
```

它的注释逐字：

```python
#: ★★★ **官方限制**（轮 166 读 `C:/swapi/types/IGtolFrame/AddIndicator.md` 的 Remarks 读出）：
#: `IGtolFrame.AddIndicator` 的 `TolType` **只能是这 5 个** `swGtolGeomCharSymbol_e` 成员。
```

**判定：成立。**
一句话依据：官方 Remarks 列的 5 个 `swGcs*` 与 `swGtolGeomCharSymbol_e` 的数值逐字合成 `{20, 22, 21, 25, 13}`，与仓内 `GTOL_INDICATOR_ALLOWED_TOL_TYPES` 的键**一一对应、无多无缺**。

**前置一句话**：`AddIndicator` 要先有 2022 格式的 `IGtolFrame` —— 官方 `IGtol.GetFrame` 的 `FrameIndex` 逐字写 `One-based index of Gtol frame to retrieve`，`IGtol.AddFrame` 的 Remarks 逐字写 `This method is valid only if this Gtol was created in SOLIDWORKS 2022 or later.`；仓内逐字 `FIRST_FRAME = 1` 与之一致。
**配方一句话**：`AddFrame()` → `GetFrame(1)` → `AddIndicator(<swGtolIndicatorBorderType_e>, <上表 5 值之一>, <Datum 串>)`。

---

## DW2-5 · 工程图上读 GTol 帧用 0 基索引 + 2022 之前的读法 ★不成立

**① ## Parameters / ## Remarks 逐字 —— [md] `C:\swapi\types\IGtol\GetFrameSymbols3.md`**

签名：

```
System.object GetFrameSymbols3( System.int FrameNumber )
```

`## Parameters`：

```
- **FrameNumber**: Frame number to examine (1 or 2)
```

`## Remarks`：

```
This method is valid only if this Gtol was created in a version of SOLIDWORKS earlier than 2022.
```

**② 同一族的另一条 —— [md] `C:\swapi\types\IGtol\GetFrameValues.md`** 签名与 Remarks 逐字：

```
System.object GetFrameValues( System.short FrameNumber )
```

```
This method is valid only if this Gtol was created in a version of SOLIDWORKS earlier than 2022.
```

**③ 帧号为什么不能 0 基 —— [md] `C:\swapi\types\IGtol\GetFrameCount.md` 的 `## Remarks` 逐字**

```
This method returns the number of frames that this symbol has stored, which may be different than the number of frames that actually appear when this frame is displayed.

For example, the symbol can be displayed with three 3 frames, but upon examination, it could be that those are frames 1, 2, and 5. Frames 3 and 4 are empty. Every symbol must have at least 2 frames.
```

**④ 2022 之后的读法 —— [md] `C:\swapi\types\IGtol\GetFrame.md` 逐字**

```
- **FrameIndex**: One-based index of Gtol frame to retrieve
```

```
This method is valid only if this Gtol was created in SOLIDWORKS 2022 or later.
```

**⑤ 仓内那一段 —— `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py` 逐字**

```python
        record["frames"] = [
            {
                "index": index,
                "symbols": _as_sequence(_safe_member(owner, "GetFrameSymbols3", index, default=[])),
                "values": _as_sequence(_safe_member(owner, "GetFrameValues", index, default=[])),
            }
            for index in range(frame_count)
        ]
```

`frame_count` 的来源（同一函数上文）逐字：

```python
            frame_count = int(_safe_member(owner, "GetFrameCount", default=0) or 0)
```

**判定：不成立。**
一句话依据：官方把 `FrameNumber` 明确限定为 `1 or 2` 且 `GetFrame` 逐字写 `One-based`，而仓内 `range(frame_count)` 从 `0` 起 ⇒ 第 0 次调用越界；官方还把 `GetFrameSymbols3/GetFrameValues` 限定为「2022 **之前**创建的 Gtol」，与同仓 `scripts/sw_gtol.py` 已确认的现行路径（`IGtol.AddFrame` + `IGtol.GetFrame` + `IGtolFrame.AddIndicator`）相反。
★ 一句补充（不改判定）：官方 `GetFrameCount` 自己说明「显示 3 帧时存储的可能是第 1、2、5 帧」，所以 `range(frame_count)` 即使改成 1 基也不能直接当帧号序列。

**前置一句话**：要读 2022 格式的 GTol 帧，得先走 `IGtol.GetFrame`（`FrameIndex` **1 基**），不能用 `GetFrameSymbols3/GetFrameValues`。
**配方一句话**：查不到（[md] `IGtol.GetFrame.md` 的 `## Examples` 段没有；[md] `Get_Text_Items_in_GTol_Frame_Example_*` 三个例子文件本轮未读）。

---

# 四、表面粗糙度（2 条）

## DW2-6 · `leaderType == swNO_LEADER` 时位置参数被官方无视 —— 仓内照做 ★成立

**① 精确签名 —— [md] `C:\swapi\types\IModelDocExtension\InsertSurfaceFinishSymbol3.md` 的 `**Signature**:` 逐字**

```
SFSymbol InsertSurfaceFinishSymbol3( System.int SymType, System.int LeaderType, System.double LocX, System.double LocY, System.double LocZ, System.int LaySymbol, System.int ArrowType, System.string MachAllowance, System.string OtherVals, System.string ProdMethod, System.string SampleLen, System.string MaxRoughness, System.string MinRoughness, System.string RoughnessSpacing )
```

★ **14 个参数**。

**② 描述行 + ## Remarks 逐字 —— [md] 同一文件**

描述行：

```
Creates a surface-finish symbol based on the last selection.
```

`## Remarks`：

```
The SOLIDWORKS Design software uses the location parameters for this method only if the surface finish symbol has a leader leaderType != swNO_LEADER.
```

**③ 枚举 —— [en] `C:\swapi\enums\swSFSymType_e.md`（`enum_member_count: 10`）与 `C:\swapi\enums\swLeaderStyle_e.md` 逐字**

```
| swSFBasic | 0 |
| swSFDont_Machine | 2 |
| swSFJIS_Basic | 8 |
| swSFJIS_Machining_Req | 1 |
| swSFJIS_No_Machining | 7 |
| swSFJIS_Surface_Texture_1 | 3 |
| swSFJIS_Surface_Texture_2 | 4 |
| swSFJIS_Surface_Texture_3 | 5 |
| swSFJIS_Surface_Texture_4 | 6 |
| swSFMachining_Req | 9 |
```

```
| swBENT | 2 = Creates a bent leader |
| swNO_LEADER | 0 = No leader |
| swSPLINE | 4 = Creates a spline leader from a note; for drawings only |
| swSTRAIGHT | 1 = Creates a straight leader |
| swUNDERLINED | 3 = Creates an underlined leader; for parts only |
| swVDA | 8 = Creates an inspection leader |
```

**④ 官方例子调用序 —— [ex] `C:\swapi\examples\Get_Annotations_Array_Example_VB.md` 逐字**

```
        swModel.Extension.InsertSurfaceFinishSymbol3 swSFBasic, swSTRAIGHT, 0.01, 0.01, 0.01, swSFCircular, swDOT_ARROWHEAD, "", "", "", "", "", "", ""
```

同例的回读逐字：

```
            count = swView.GetSFSymbolCount
```

```
                Annotations = swView.GetSFSymbols
```

**⑤ 仓内那一段 —— `scripts/sw_drawing_create_missing.py` 的 `insert_surface_finish_symbol` 逐字**

```python
    location_applied = int(leader_type) != SW_LEADER_NO_LEADER
    loc_x, loc_y, loc_z = ((mm(float(x_mm)), mm(float(y_mm)), mm(float(z_mm)))
                           if location_applied else (0.0, 0.0, 0.0))
```

它把官方 Remarks 原样挂在返回值里，逐字：

```python
        "official_remark_verbatim": (
            "The SOLIDWORKS Design software uses the location parameters for this method only "
            "if the surface finish symbol has a leader leaderType != swNO_LEADER."
        ),
```

工具层的同一句注释在 `mcp-server/tool_specs_batch73.py` 的 ToolSpec `doc` 里逐字：

```
            "★★ **官方 `## Remarks` 逐字**：「The SOLIDWORKS Design software uses the location "
            "parameters for this method **only if** the surface finish symbol has a leader "
            "leaderType **!= swNO_LEADER**.」⇒ ★★ `leader_type = 0` 时**三个位置参数被官方无视**"
```

**判定：成立。**
一句话依据：官方 Remarks 逐字把 `LocX/LocY/LocZ` 的生效条件绑定在 `leaderType != swNO_LEADER`，仓内在该档**主动传 `0,0,0`** 并把被丢掉的原坐标回在 `ignored_location_mm`，与契约一致；两个枚举表（`swSFSymType_e` 0/1/2/3..6/7/8/9、`swLeaderStyle_e` 0/1/2/3/4/8）也与工具层 `Param` 里逐字写的默认值一一对上。

**前置一句话**：官方描述行逐字 `based on the last selection` ⇒ 调用前必须有选区；仓内只**回读选区计数**写进 `preconditions_held`，不代选。
**配方一句话**：14 参，示例实参逐字 `swSFBasic, swSTRAIGHT, 0.01, 0.01, 0.01, swSFCircular, swDOT_ARROWHEAD, "", "", "", "", "", "", ""`。

---

## DW2-7 · 读表面粗糙度符号先调官方标 Obsolete 的 `GetSymbolType` ★不成立

**① 精确签名 + 废弃链 —— [md] `C:\swapi\types\ISFSymbol\GetSymbolType.md` 逐字**

```
# ISFSymbol.GetSymbolType

Obsolete. Superseded by [[ISFSymbol::GetSymbol]].
```

```
System.int GetSymbolType()
```

**② 后继成员 —— [md] `C:\swapi\types\ISFSymbol\GetSymbol.md` 的 `## Returns` 逐字**

```
Type of symbol as defined in [[swSFSymType_e]] (see **Remarks**)
```

**③ 同族的非废弃成员 —— [md] `C:\swapi\types\ISFSymbol\GetDirectionOfLay.md` 的 `## Returns` 逐字**

```
Direction of lay as defined in [[swSFLaySym_e]]
```

**④ 仓内那一段 —— `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py` 逐字**

```python
        record.update({
            "symbol_type": _safe_member(owner, "GetSymbolType", default=None),
            "symbol": _safe_member(owner, "GetSymbol", default=None),
            "direction_of_lay": _safe_member(owner, "GetDirectionOfLay", default=None),
        })
```

**⑤ 官方例子 —— [ex] `C:\swapi\examples\Get_Annotations_Array_Example_VB.md`** 只读 `GetAnnotation`，逐字：

```
                    msg = "Surface finish symbol found: " & swView.GetName2 & ":" & sfsymbol.GetAnnotation.GetName
```

**判定：不成立。**
一句话依据：官方逐字把 `ISFSymbol.GetSymbolType` 标 `Obsolete` 并点名后继 `ISFSymbol::GetSymbol`，而仓内**同一条记录里既调被废弃的 `GetSymbolType`、又调后继 `GetSymbol`**，两个字段语义重复且第一个必然是官方已弃的读法（`GetDirectionOfLay` 不是 Obsolete，那一项没问题）。

---

# 五、基准符号（1 条）

## DW2-8 · `InsertDatumTag2()` 零参、落点全由选区决定 ★成立

**① 精确签名 —— [md] `C:\swapi\types\IModelDoc2\InsertDatumTag2.md` 逐字三处**

描述行：

```
Inserts a datum tag symbol at a selected location.
```

签名：

```
System.object InsertDatumTag2()
```

`## Returns`：

```
Newly created [[datum tag]]
```

★ 该页**没有 `## Remarks` 段**（全文依次是 front-matter / 标题 / 描述行 / Signature / Returns / Examples / See Also）。**查不到**。

**② 官方例子调用序 —— [ex] `C:\swapi\examples\Get_Annotations_Array_Example_VB.md` 的 `Build_Part` 段逐字（两行，紧邻）**

```
        retval = swModel.Extension.SelectByID2("", "EDGE", 0.06001738353251, -0.01284975502705, -0.05001738353241, False, 0, Nothing, 0)
        Dim dTag As SldWorks.DatumTag
        Set dTag = swModel.InsertDatumTag2
```

同例的回读逐字：

```
            count = swView.GetDatumTagCount
```

```
                Annotations = swView.GetDatumTags
```

**③ 读侧成员 —— [md] `C:\swapi\types\IView\GetDatumTags.md` 描述行与签名逐字**

```
Gets all of the datum tags on this drawing view.
```

```
System.object GetDatumTags()
```

`[md] C:\swapi\types\IDatumTag\GetLabel.md` 签名逐字：

```
System.string GetLabel()
```

**④ 仓内那一段 —— `scripts/sw_drawing_create_missing.py` 的 `insert_datum_tag` docstring 逐字**

```
    """★ **基准符号（datum tag）**：`IModelDoc2.InsertDatumTag2()` → `DatumTag`（★ **零参**）。
```

紧接着的三行逐字：

```
      · 官方摘要逐字「Inserts a datum tag symbol **at a selected location**.」
        ⇒ ★★ **调用前必须先选中一个位置**（官方示例里是 `SelectByID2("", "EDGE", …)`）。
      · ★ 官方**零参数** ⇒ ★ 落点**完全由选区决定** ⇒ ★ 本模块**没有坐标入口**，
```

函数体逐字：

```python
    tag = get_com_member(model, "InsertDatumTag2")
```

读侧逐字（同一模块，`drawing_workflow.py`）：

```python
    for owner in _as_sequence(_safe_member(view, "GetDatumTags", default=[])):
        record = _professional_annotation_record(owner, "datum", view_record)
        record["label"] = str(_safe_member(owner, "GetLabel", default="") or "")
```

**判定：成立。**
一句话依据：官方签名逐字 `System.object InsertDatumTag2()`（零参）、描述行逐字 `at a selected location`、示例逐字**先 `SelectByID2("", "EDGE", …)` 再 `Set dTag = swModel.InsertDatumTag2`**，与仓内 docstring 与「没有坐标入口」的写法逐字对得上；回读用的 `IView.GetDatumTagCount / GetDatumTags / IDatumTag.GetLabel` 三个成员在官方页上均存在且签名一致。

**前置一句话**：调用前必须在图形区选中一个位置（官方示例选的是 `EDGE`）；官方该成员页**没有 `Remarks` 段**，这条前置来自描述行 + 示例，**不是**来自 Remarks。
**配方一句话**：`SelectByID2("", "EDGE", …)` → `InsertDatumTag2()`；回读 `sum(IView.GetDatumTagCount)`。

---

# 六、气泡序号（1 条）

## DW2-9 · `AutoBalloon5` 的四步调用序与默认值 ★成立

**① 精确签名 —— [md] `C:\swapi\types\IDrawingDoc\AutoBalloon5.md` 逐字**

```
System.object AutoBalloon5( AutoBalloonOptions BalloonOptions )
```

`## Returns`：

```
Array of [[INotes]]
```

**② ## Remarks 逐字 —— [md] 同一文件（四步）**

```
1. Select one or more views or sheets for which to automatically create BOM balloons.

2. Call [[IDrawingDoc::CreateAutoBalloonOptions]] to create an [[IAutoBalloonOptions]] object.

3. Set the properties on the IAutoBalloonOptions object.

4. Call this method using the IAutoBalloonOptions object in the BalloonOptions argument.
```

**③ 第 2 步的成员 —— [md] `C:\swapi\types\IDrawingDoc\CreateAutoBalloonOptions.md`** 签名与 `## Returns` 逐字：

```
AutoBalloonOptions CreateAutoBalloonOptions()
```

```
[[IAutoBalloonOptions]]
```

`[md] C:\swapi\types\IAutoBalloonOptions\_overview.md` 的 front-matter 逐字：

```
property_count: 19
method_count: 0
```

**④ 官方例子调用序 —— [ex] `C:\swapi\examples\Add_Autoballoon_to_Face_Example_VB.md` 逐字（选视图 → 建 options → 逐条设 → 调）**

```
    boolstatus = Part.Extension.SelectByID2("Drawing View1", "DRAWINGVIEW", 0, 0, 0, False, 0, Nothing, 0)
    Set autoballoonParams = Part.CreateAutoBalloonOptions()
    autoballoonParams.Layout = swDetailingBalloonLayout_Square
    autoballoonParams.ReverseDirection = False
    autoballoonParams.IgnoreMultiple = True
    autoballoonParams.InsertMagneticLine = True
    autoballoonParams.LeaderAttachmentToFaces = True
    autoballoonParams.Style = swBS_Circular
    autoballoonParams.Size = swBF_5Chars
    autoballoonParams.UpperTextContent = swBalloonTextItemNumber
    autoballoonParams.Layername = "-None-"
    autoballoonParams.ItemNumberStart = 1
    autoballoonParams.ItemNumberIncrement = 1
    autoballoonParams.ItemOrder = swBalloonItemNumbers_DoNotChangeItemNumbers
    autoballoonParams.EditBalloons = True
    autoballoonParams.EditBalloonOption = swEditBalloonOption_Resequence
    vNotes = Part.AutoBalloon5(autoballoonParams)
```

**⑤ 仓内那一段 —— `scripts/sw_drawing_create_missing.py` 的 `auto_insert_balloons` 逐字**

docstring 里照抄的官方四步：

```
    ★★★ **官方 `## Remarks` 给的是**四步**，★ 本模块**严格照那四步走**（逐字转述）：
      > 1. Select one or more views or sheets for which to automatically create BOM balloons.
      > 2. Call `IDrawingDoc::CreateAutoBalloonOptions` to create an `IAutoBalloonOptions` object.
      > 3. Set the properties on the `IAutoBalloonOptions` object.
      > 4. Call this method using the `IAutoBalloonOptions` object in the `BalloonOptions` argument.
```

函数体三处逐字：

```python
    opts = get_com_member(model, "CreateAutoBalloonOptions")
```

```python
        "Layout": int(layout),
        "Style": int(style),
        "Size": int(size),
        "UpperTextContent": int(upper_text_content),
        "UpperText": str(upper_text),
        "Layername": str(layername),
        "ItemNumberStart": int(item_number_start),
        "ItemNumberIncrement": int(item_number_increment),
        "ItemOrder": int(item_order),
        "EditBalloons": bool(edit_balloons),
        "EditBalloonOption": int(edit_balloon_option),
        "ReverseDirection": bool(reverse_direction),
        "IgnoreMultiple": bool(ignore_multiple),
        "InsertMagneticLine": bool(insert_magnetic_line),
        "LeaderAttachmentToFaces": bool(leader_attachment_to_faces),
```

```python
    notes = get_com_member(model, "AutoBalloon5", opts)
```

docstring 里点名出处的那句逐字：

```
    ★ 其余默认值**逐条照官方示例**（`Add_Autoballoon_to_Face_Example_VB.md`）——
      `ReverseDirection=False` / `IgnoreMultiple=True` / `InsertMagneticLine=True` /
      `LeaderAttachmentToFaces=True` / `Layername="-None-"` / `ItemNumberStart=1` /
      `ItemNumberIncrement=1` / `EditBalloons=True`。
```

**⑤b 工具层为什么没有它 —— `mcp-server/tool_specs_batch73.py` 逐字**

```
#: ★★ **本批**刻意**不给「气泡序号」建 ToolSpec** —— ★ 不是遗漏，是**形态不同**：
#:   `IDrawingDoc.AutoBalloon5` 的形参是 **`AutoBalloonOptions` 这个 COM 对象**
#:   （官方签名逐字 `System.object AutoBalloon5( AutoBalloonOptions BalloonOptions )`），
```

**判定：成立。**
一句话依据：官方 `AutoBalloon5` / `CreateAutoBalloonOptions` 的 Remarks 四步与仓内 docstring 逐字同文、官方示例的 `SelectByID2("Drawing View1","DRAWINGVIEW",…)` → `CreateAutoBalloonOptions()` → 逐条设属性 → `AutoBalloon5(params)` 与仓内函数体同序，仓内点名的 8 个默认值逐条等于示例里的同名赋值，且 `wanted` 里 15 个属性名在官方 `IAutoBalloonOptions`（`property_count: 19`）的成员文件清单中逐个存在。

**前置一句话**：先选中一个或多个**视图或图纸**（官方第 1 步；示例选的是 `DRAWINGVIEW`）。
**配方一句话**：选中 → `CreateAutoBalloonOptions()`（零参）→ 设 15 条属性 → `AutoBalloon5(options)` → 返回 `Array of INotes`，数组长度即气泡数。

---

## 附 · 本片**没有**下结论的地方（铁律 5：查不到就说查不到）

| 项 | 状态 |
|---|---|
| 工程图域**尺寸公差**（`IDimension.GetToleranceType` / `GetToleranceValues` / `IDimensionTolerance`）的仓内调用点 | **查不到** —— 见 §〇 第一行；因此本片对它**一条结论都没写**。 |
| `TABLE_ANNOTATION_KINDS` 未覆盖的 4 个官方表类型（7 / 8 / 9 / 10） | **查不到** —— 官方页没写「可只列一部分」，仓内也没声明；只对**已证伪的 6** 下结论（DW2-3）。 |
| `IGtol.GetFrame` / `IGtolFrame.AddIndicator` 的官方示例调用序 | **查不到** —— `[md] IGtol\GetFrame.md` 无 `## Examples` 段，`Get_Text_Items_in_GTol_Frame_Example_*` 三个例子文件本轮未打开。 |
| `swSFLaySym_e` / `swArrowStyle_e` 里 `0` 的语义 | **查不到** —— 仓内自己逐字写了「**本轮没查 `0` 是什么** ⇒ 本工具**原样透传、不作断言**」，本片沿用该口径，不再补断言。 |

---

## 三行

- **核了几处**：**9 处**（DW2-1 … DW2-9，覆盖尺寸 / 公差 / GD&T / 表面粗糙度 / 基准符号 / 气泡序号六项；另记 4 条「查不到」，不计入核处数）
- **对不上几处**：**5 处**（DW2-1 · DW2-2 · DW2-3 · DW2-5 · DW2-7 判定「不成立」；其余 4 处判定「成立」）—— 集中全在**读侧**：两处调用官方标 `Obsolete` 的成员（`IDisplayDimension.GetTextFormat`、`ISFSymbol.GetSymbolType`）、一处把官方 `9` 的通用公差表写成 `6`、一处用 0 基索引读官方只接受 `1 or 2` 且限「2022 之前」的 GTol 帧；**写侧三条（DW2-4 / DW2-6 / DW2-8）与气泡序号（DW2-9）全对得上**。
