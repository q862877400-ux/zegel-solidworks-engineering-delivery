# T4-1 第三步 · 判读材料齐备版：8 个「我们用到」的成员

> 生成物 —— 由 tools/t4_judge_materials.py 产出，不要手改。
> ★ 目的：把判读所需的**三样材料**（我们的调用点 / 官方 Remarks 原文 / 官方示例原文）抽到一处，
> 使判读变成小范围阅读，而不必再翻 2.6 MB 的原始 JSON。

本表不算什么：

- ★ 它**不判**对错（判读是人/模型的事，须读下面三样材料后下结论）；
- ★ 我们那一行的**上下文**只给该行与前后各一行，可能不足以判 —— 需读全函数时另行打开；
- ★ 官方侧的原文来自另一个对话的产出（`conditional_pass`），★ 采纳前须回查官方页 ✓

---

## 1 · `AutoDimension2`

### ① 我们的调用点（7 处）

- `scripts\sw_part.py:707`
  ```
  显示尺寸，不能凭空为拉伸深度或矩形轮廓生成尺寸。该函数在草图编辑态 / 选择水平/垂直基准线，再调用 ``ISketch.AutoDimension2``，因此生成的尺寸 / 会成为模型的真实 DisplayDimension，可被工程图导入并复核。
  ```
- `mcp-server\tool_specs_batch55.py:15`
  ```
  # 定位:   24h 计划 v2 段 3：把 `sw_part` 的"读草图名"与"自动标注"挂成 MCP 工具。 / # 官方签名依据: `ISketch.AutoDimension2`（★ 5 参，见 `scripts/sw_part.auto_dimension_sketch`）· / #   `IModelDoc2.GetActiveSketch2` / `ISketchManager.ActiveSketch`（★ 见 `current_sketch_name`）
  ```
- `tools\probe_autodimension_successor.py:1`
  ```
  """★ 真机验证 `ISketch.AutoDimension2` → `ISketchManager.FullyDefineSketch`。 / 
  ```
- `tools\probe_fullydefinesketch.py:71`
  ```
  act = get_com_member(sk, "ActiveSketch") / got = get_com_member(act, "AutoDimension2", 1, 1, -1, 1, -1) / elif form == "new_nulls":
  ```

### ② 冲突 1 · `mark_diff`

- ★ **官方 `## Remarks` 说**：Select and mark a unique vertical edge, vertex, sketch point, or vertical sketch line as the datum for the horizontal dimensioning scheme, using swAutodimMarkHorizontalDatum as the mark value.
- ★ **官方示例写**：`bRet = swSketchSegVert.Select4(True, Nothing)`
- ★ 示例文件：`Autodimension_All_Sketches_Example_VB.md`
- ★ 另一个对话的判读：备注要求基准必须打 swAutodimMark* 标记；示例用没有 mark 形参的 Select4 选基准却声明成功。

---

## 2 · `FeatureCircularPattern4`

### ① 我们的调用点（6 处）

- `scripts\sw_part.py:1441`
  ```
  _select_by_id(model.Extension, axis_name, "AXIS", append=True, mark=1) / return model.FeatureManager.FeatureCircularPattern4( / count, angle_rad, False, "None", False, equal_spacing, False
  ```
- `tools\probe_pattern5.py:114`
  ```
  elif form == "circular4_7": / got = get_com_member(fm, "FeatureCircularPattern4", / 4, 6.283185307179586, False, "", False, True, False)
  ```
- `tools\probe_pattern_generations.py:129`
  ```
  R["旧_FeatureCircularPattern4(7 参)"] = _try( / _g, fm, "FeatureCircularPattern4", / 4, 6.283185307179586, False, "None", False, True, False)
  ```
- `tools\prove_linear_pattern_generations.py:10`
  ```
  #     ★ 对照：`circular_pattern`（**能用**）用的是 / #        `model.FeatureManager.FeatureCircularPattern4(count, angle_rad, False, "None", False, eq, False)` / #        ⇒ ★ **直接属性调用 + 7 参**
  ```

### ② 冲突 1 · `unit_diff`

- ★ **官方 `## Remarks` 说**：Spacing between each instance of the circular pattern; total angle in radians if EqualSpacing is true
- ★ **官方示例写**：`myModel.FeatureManager.FeatureCircularPattern4 3, 1.25663706143592, True, "NULL", False, False, False`
- ★ 示例文件：`Get_Cosmetic_Threads_in_a_Part_Document_Example_VB.md`
- ★ 另一个对话的判读：成员页把弧度口径限定在 EqualSpacing=true；示例 EqualSpacing=False 仍传 1.25663706143592（=72°弧度），两侧不能同时成立

---

## 3 · `FeatureLinearPattern4`

### ① 我们的调用点（5 处）

- `tools\probe_linear_pattern_baseline.py:11`
  ```
  #                                        0, 0, 0, True, 256, Nothing, 0) / #     Set swFeature = swFeatureMgr.FeatureLinearPattern4( / #         3, 0.0254, 1, 0.00254, True, False, "NULL", "NULL", False, False,
  ```
- `tools\probe_linearpattern4.py:112`
  ```
  case = {"DName": dname or "（空）"} / case["调"] = _try(_g, fm, "FeatureLinearPattern4", / 2, 0.03, 1, 0.0,
  ```
- `tools\prove_linear_pattern_generations.py:93`
  ```
  #:   ★★★ 而本次**按 20 参填满**（★ 前 10 个同名，后 10 个取"不偏移、按数量控制、不从质心" 的常规值）✓ / ("FeatureLinearPattern4", 3, / lambda: get_com_member(get_com_member(doc, "FeatureManager"), "FeatureLinearPattern4",
  ```
- `tools\prove_pattern_members.py:41`
  ```
  NAMES = ["FeatureLinearPattern", "FeatureLinearPattern2", "FeatureLinearPattern3", / "FeatureLinearPattern4", "FeatureLinearPattern5", / "FeatureCircularPattern4", "FeatureCircularPattern5",
  ```

### ② 冲突 1 · `unit_diff`

- ★ **官方 `## Remarks` 说**：- **Offset1**: Offset in meters from a selected reference in Direction 1 (see **Remarks**); valid only if HasOffset1 is true
- ★ **官方示例写**：`* 0.l9 (Offset1; furthest instance in Direction 1 is offset by 190 mm`
- ★ 示例文件：`Create_Linear_Pattern_Example_VB.md`
- ★ 另一个对话的判读：页面写 Offset1 以米计、示例注释把同一个 0.19 说成 190 mm；同一行的 Spacing2 同样：页面「in meters」对示例「* 0.02 (Spacing2 in mm)」。

### ② 冲突 2 · `mark_diff`

- ★ **官方 `## Remarks` 说**：- 8388608 to mark a seed instance reference when FromCentroid1 or FromCentroid2 is false
- ★ **官方示例写**：`status = swModelDocExt.SelectByID2("Boss-Extrude2", "SOLIDBODY", 0, 0, 0, True, 256, Nothing, 0)`
- ★ 示例文件：`Change_Linear_Pattern_Example_VB.md`
- ★ 另一个对话的判读：F4 的 mark 表只有特征/组件两行（1/2/4/2097152/8388608），无 256；示例用 256 选实体，256 只出现在 F5 页「256 to mark the solid bodies to pattern」。

---

## 4 · `InsertProtrusionBlend2`

### ① 我们的调用点（5 处）

- `scripts\sw_loft.py:87`
  ```
  fm = get_com_member(model, "FeatureManager") / get_com_member(fm, "InsertProtrusionBlend2", *args) / except Exception as exc:                                   # noqa: BLE001
  ```
- `mcp-server\tool_specs_batch47.py:54`
  ```
  ], / doc="★ **用「轮廓草图」放样** —— 走 `IFeatureManager.InsertProtrusionBlend2`（官方 **18 参**）。" / "★ 官方 Remarks：轮廓要**按期望的顺序**先选中，mark=**1**（引导线 mark=2 · 中心线 mark=4 · "
  ```
- `tools\audit_gap_implementations.py:40`
  ```
  "草图/完全定义检查": ["GetConstrainedStatus"], / "特征/边界凸台": ["InsertProtrusionBlend2", "InsertProtrusionBlend"], / "特征/孔向导": ["HoleWizard5", "HoleWizard"],
  ```
- `tools\prove_pattern_members.py:43`
  ```
  "FeatureCircularPattern4", "FeatureCircularPattern5", / "InsertProtrusionBlend2", "FeatureExtrusion3"] / 
  ```

### ② 冲突 1 · `mark_diff`

- ★ **官方 `## Remarks` 说**：- 2 = guide curve selections
- ★ **官方示例写**：`status = swModelDocExt.SelectByID2("Sketch3", "SKETCH", 0, 0, 0, true, 4098, null, 0);`
- ★ 示例文件：`Get_Guide_Curves_in_Loft_Feature_Example_CSharp.md`
- ★ 另一个对话的判读：Remarks 只列 mark=2 作引导曲线；示例传 4098（=4096+2），4096 位在官方 mark 表与 swSelectOption_e（仅 0/1）中无出处。

---

## 5 · `InsertSewRefSurface`

### ① 我们的调用点（3 处）

- `scripts\sw_surface_features.py:263`
  ```
  #: ★ 容差换算：毫米 ⇒ 米（★ 唯一的换算处） / get_com_member(fm, "InsertSewRefSurface", False, bool(try_to_form_solid), True, / tol * 0.001, tol * 0.001)
  ```
- `mcp-server\tool_specs_batch45.py:75`
  ```
  ], / doc="★ **把曲面缝成一张** —— 走 `IFeatureManager.InsertSewRefSurface`（官方 **5 参**）。" / "★ 官方 Remarks：选中项要 **selection mark = 1**，而**缝合容差的有效范围是 0.0001 ～ 0.1 mm**。"
  ```
- `tools\t4_judge_materials.py:31`
  ```
  USED = ["AutoDimension2", "FeatureCircularPattern4", "FeatureLinearPattern4", / "InsertProtrusionBlend2", "InsertSewRefSurface", "InsertWeldmentTrimFeature2", / "SetSystemValue3", "SetupSheet6"]
  ```

### ② 冲突 1 · `unit_diff`

- ★ **官方 `## Remarks` 说**：A knit tolerance's:

- lower limit is 0.0001 mm

- upper limit is 0.1 mm
- ★ **官方示例写**：`Debug.Print("  Knit tolerance: " + swSurfaceKnitFeature.KnitTolerance * 1000 + " mm");`
- ★ 示例文件：`Create_Surface_Knit_Feature_Example_CSharp.md`
- ★ 另一个对话的判读：示例回读后要 ×1000 才标 mm，说明裸值单位是米；0.0001 裸值即 0.1 mm，与 Remarks「下限 0.0001 mm」不能同时成立。

### ② 冲突 2 · `unit_diff`

- ★ **官方 `## Remarks` 说**：A knit tolerance's:

- lower limit is 0.0001 mm

- upper limit is 0.1 mm
- ★ **官方示例写**：`swNewFeatMgr.InsertSewRefSurface(true, false, false, 3.001639406912E-05, 0.0001);`
- ★ 示例文件：`Fill_Holes_in_Part_Example_CSharp.md`
- ★ 另一个对话的判读：KnitTolerance 传 3.001639406912E-05；按 Remarks 的 mm 口径它低于 0.0001 mm 下限，按米口径才等于 0.03 mm 落在区间内。

---

## 6 · `InsertWeldmentTrimFeature2`

### ① 我们的调用点（3 处）

- `tools\probe_t302_four_families.py:181`
  ```
  ("焊件裁剪延伸 InsertWeldmentTrimFeature2", / "InsertWeldmentTrimFeature2", (0,))): / rows.append(_try(label, {
  ```
- `tools\probe_t302_four_families_v2.py:190`
  ```
  "② 裁剪延伸 InsertWeldmentTrimFeature2（★ 5 参）", model, / lambda: get_com_member(fm, "InsertWeldmentTrimFeature2", / 0, 0, 0.0, VARIANT_NONE, VARIANT_NONE)))
  ```
- `tools\t4_judge_materials.py:31`
  ```
  USED = ["AutoDimension2", "FeatureCircularPattern4", "FeatureLinearPattern4", / "InsertProtrusionBlend2", "InsertSewRefSurface", "InsertWeldmentTrimFeature2", / "SetSystemValue3", "SetupSheet6"]
  ```

### ② 冲突 1 · `mark_diff`

- ★ **官方 `## Remarks` 说**：- 1 = Body or bodies to trim

- 2 = Trimming boundaries (body or face)
- ★ **官方示例写**：`= Part.Extension.SelectByID2("Structural Member1[2]", "SOLIDBODY",
0, 0, 0, true, 2, null, 0);
boolstatus
= Part.Extension.SelectByID2("Structural Member1[1]", "SOLIDBODY",
0, 0, 0, true, 1, null, 0);
long
Count = 0;
Count
= selMgr.GetSelectedObjectCount();
if
(Count == 2)
{
obj1[0]
= (Body2)selMgr.GetSelectedObject2(1);
v1
= obj1;
obj2[0]
= (Body2)selMgr.GetSelectedObject2(2);
v2
= obj2;`
- ★ 示例文件：`Insert_Weldment_Features_Example_CSharp.md`
- ★ 另一个对话的判读：先选者标 mark2 落 v1=BodiesToTrim，后选标 mark1 落 v2=BodiesOrFaces，与 Remarks 的 1=待裁、2=裁边正好相反。

---

## 7 · `SetSystemValue3`

### ① 我们的调用点（3 处）

- `scripts\sw_document_data.py:4`
  ```
  本模块只封装已由 SolidWorks 2024 Interop 和官方 API Help 核对的接口： / ``IDimension.SetSystemValue3`` 与 ``ICustomPropertyManager.Add3/Get6``。 / """
  ```
- `tools\probe_getsystemvalue_on_existing.py:14`
  ```
  dimValue_1 = swDim_1.GetSystemValue3(swInConfigurationOpts_e.swThisConfiguration, Empty) / errors = swDim_1.SetSystemValue3(dimValue_1(0), …) ' ★★★ 注意它取 (0) ⇒ **返回值是数组** / ```
  ```
- `tools\t4_judge_materials.py:32`
  ```
  "InsertProtrusionBlend2", "InsertSewRefSurface", "InsertWeldmentTrimFeature2", / "SetSystemValue3", "SetupSheet6"] / 
  ```

### ② 冲突 1 · `unit_diff`

- ★ **官方 `## Remarks` 说**：Sets the value of this dimension in system units (meters) in the specified configuration.
- ★ **官方示例写**：`' Change D3 of LocalCirPattern1 from 360 degrees to 270 degrees (4.72 radians)`
- ★ 示例文件：`Change_Dimension_Example_VB.md`
- ★ 另一个对话的判读：成员页称该入参一律以米计（Parameters 亦写 NewValue: Dimension value in meters），示例却把同一入参当弧度用（4.72 rad=270°，把 360° 改为 270°）；两者不能同时成立。

---

## 8 · `SetupSheet6`

### ① 我们的调用点（6 处）

- `scripts\sw_drawing_expose.py:18`
  ```
  #     · `IDrawingDoc.CreateDrawViewFromModelView3`（投影视图）· `IDrawingDoc.CreateSectionViewAt5`（剖面） / #     · `IDrawingDoc.CreateDetailViewAt4`（局部，**12 参**）· `IDrawingDoc.SetupSheet6`（图纸格式） / #     · `IModelDoc2.InsertNote`（注释）· `IView.InsertHoleTable3` / `ISheet.InsertRevisionTable2`（表）
  ```
- `mcp-server\tool_specs_batch75.py:39`
  ```
  #     · `IDrawingDoc.CreateDrawViewFromModelView3`（投影）· `IDrawingDoc.CreateSectionViewAt5`（剖面） / #     · `IDrawingDoc.CreateDetailViewAt4`（局部，**12 参**）· `IDrawingDoc.SetupSheet6`（图纸格式） / #     · `IModelDoc2.InsertNote`（注释）· `IView.InsertHoleTable3` / `ISheet.InsertRevisionTable2`（表）
  ```
- `tools\probe_datum_tag_selfcontained2.py:9`
  ```
  #   ★ 事实 327 给的**具体下一步**：★ **先给图纸上 A3 图框**（用行内现成的 / #     `setup_current_sheet_as_a3` —— ★ 它走官方 `IDrawingDoc.SetupSheet6`），★ 再 `add_view`。 / #   ★ 图框文件在本机：`C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\lang\Chinese-Simplified\
  ```
- `tools\probe_drawing_tools_e2e.py:19`
  ```
  #     · `IDrawingDoc.CreateDrawViewFromModelView3` · `CreateSectionViewAt5` · `CreateDetailViewAt4` / #     · `IDrawingDoc.SetupSheet6` · `IModelDoc2.InsertNote` · `IView.InsertHoleTable3` / #     · `ISheet.InsertRevisionTable2` · `IView.AutoInsertCenterMarks2`
  ```

### ② 冲突 1 · `unit_diff`

- ★ **官方 `## Remarks` 说**：Multiplying ZoneRow by ZoneCol equals the total number of zones in the zone area of this drawing sheet. The zone area is specified by ZoneLeftMargin, ZoneRightMargin, ZoneTopMargin, and ZoneBottomMargin.
- ★ **官方示例写**：`0.2794, 0.2159, "Default", False, 0.5, 0.5, 0.5, 0.5, 3, 3)`
- ★ 示例文件：`Create_Drawing_Sheet_Zones_Example_VB.md`
- ★ 另一个对话的判读：同一次调用里 Width/Height 用米（0.2794/0.2159），四个 Zone 边距却是 0.5；同一单位下边距大于整张图，成员页又未标边距单位。

---

## ★ 判读模板（★ 每条填一行；三态：成立 / 不成立 / 查不到）

| 成员 | 类 | 我们用的是示例写法还是 Remarks 写法 | 结论 | 证据 |
|---|---|---|---|---|
| `AutoDimension2` | mark_diff | ★ **两者都不是**：我们**只在真调用里**用它（★ `ast` 判：**`scripts/sw_part.py:805`** 与 `tools/probe_fullydefinesketch.py:71`），且★ **调用前没有「选基准边并打 `swAutodimMark*`」这一步** | ★★ **成立**（★ 对**产品代码也成立** —— 2026-10-04 第 12 轮更正：`scripts/sw_part.py:805` 有真调用）| ★ 第 12 轮用 `ast` 重判：真调用 2 处（`sw_part.py:805` 的 `get_com_member` + 探针那处）；★★ 上一轮基于**文本匹配**把 805 行看成了 docstring ⇒ **结论错了，已更正** ✓ |
| `FeatureCircularPattern4` | unit_diff | （待填）| （待填）| （待填）|
| `FeatureLinearPattern4` | unit_diff | （待填）| （待填）| （待填）|
| `FeatureLinearPattern4` | mark_diff | （待填）| （待填）| （待填）|
| `InsertProtrusionBlend2` | mark_diff | （待填）| （待填）| （待填）|
| `InsertSewRefSurface` | unit_diff | （待填）| （待填）| （待填）|
| `InsertSewRefSurface` | unit_diff | （待填）| （待填）| （待填）|
| `InsertWeldmentTrimFeature2` | mark_diff | （待填）| （待填）| （待填）|
| `SetSystemValue3` | unit_diff | （待填）| （待填）| （待填）|
| `SetupSheet6` | unit_diff | （待填）| （待填）| （待填）|
