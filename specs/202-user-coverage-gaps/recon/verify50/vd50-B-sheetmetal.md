# vd50-B · 域 `02-sheetmetal` · 高置信条目复核

**范围**：`specs/202-user-coverage-gaps/recon/audit-vs-official/audit-02-sheetmetal-{A,B,C}.md` 中**置信度为「高」**的条目（B#3/B#4/C#3 为「中」，按任务要求**未核**）。
**方法**：每条核两件事 —— ①「官方的原文」逐字存在于 `C:\swapi\`；②「我们的原文」逐字存在于 `D:\AI\SW\scripts\`。
**纪律**：给不出两段可搜索原文的一律不写；查不到就说查不到；不写行号，只写原文片段；**未修改仓内任何文件**（本文件是本轮唯一写入）。

## 覆盖的高置信条目清单

| 来源文件 | 条目号 | 主题 |
|---|---|---|
| `audit-02-sheetmetal-A.md` | #1 | `ISketchedBendFeatureData.BendAngle` 量纲（度 vs 弧度） |
| `audit-02-sheetmetal-A.md` | #2 | `IEdgeFlangeFeatureData.BendAngle` 量纲 |
| `audit-02-sheetmetal-A.md` | #3 | `IDraftFeatureData2.Angle` 量纲 |
| `audit-02-sheetmetal-A.md` | 附录 1 | `IFeature.GetErrorCode` Obsolete（＝C#1，同一发现） |
| `audit-02-sheetmetal-B.md` | #1 | 边法兰缺 `InsertSketchForEdgeFlange` / `AddEdges` 两步前置 |
| `audit-02-sheetmetal-B.md` | #2 | `InsertSheetMetalClosedCorner` 前置选面 |
| `audit-02-sheetmetal-C.md` | #1 | `IFeature.GetErrorCode` Obsolete |
| `audit-02-sheetmetal-C.md` | #2 | `D1/D2EndConditionType = 0` 不在 `swFlangeOffsetTypes_e` 取值域 |

**表内高置信条目 8 处 → 去重后 7 处**（A 附录 1 条与 C#1 是同一发现，两处分别核、各自成立）。

---

## A#1 · `scripts/sw_sheet_metal.py` · 判定：**成立**

**我们的原文**（`scripts/sw_sheet_metal.py`，`create_one_bend` 与 `OneBendSpec.validate` 两处）：
```
        data.BendAngle = float(spec.angle)
```
```
            raise ValueError("折弯角度必须位于 0 与 360 度之间")
```

**官方的原文**（`C:\swapi\types\ISketchedBendFeatureData\BendAngle.md`，`## Returns` 段逐字）：
```
0.261799 <= Bend angle in increments of 0.261799 radians (15 degrees) <= 1.5708
```
旁证（`C:\swapi\examples\Change_Bend_Radius_of_Sketched_Bend_Example_VB.md`，该文件把 VBA 硬折行，逐行可搜）：
```
radian = 180º/p = 57.295779513º or approximately
```
```
* 57.3 & " deg"
```

**一句话依据**：官方属性页逐字写明取值域是**弧度**（15°–90°），官方例子也把 `BendAngle` 乘 `57.3` 才是度，而我们把**度**原样赋进去、校验还允许到 360。

**附注（非判定依据）**：A 文件把例子里的引用写成 `'1 radian = 180º/p = 57.295779513º`，其中 `'1 ` 与 `radian =` 在该 markdown 里**分属两行**（导出器硬折行），是引用排版拼接，不是内容不符。

---

## A#2 · `scripts/sw_sheet_metal.py` · 判定：**成立**

**我们的原文**（`scripts/sw_sheet_metal.py`，`EdgeFlangeSpec` 与 `create_edge_flange._apply`）：
```
    """@brief 边法兰的可制造参数，长度单位为米，角度为度。"""
```
```
    angle: float = 90.0
```
```
        data.BendAngle = float(spec.angle)
```
```
            raise ValueError("边法兰角度必须位于 0 与 180 度之间")
```

**官方的原文**（`C:\swapi\types\IEdgeFlangeFeatureData\BendAngle.md`，`## Returns` 段逐字）：
```
Flange angle; default value is 1.5707963267949 radians
```

**一句话依据**：官方默认值 `1.5707963267949 radians` 即 π/2 = 90°，证明该属性收**弧度**；我们的默认值就是 `90.0`（度）原样透传，量纲差约 57 倍。

---

## A#3 · `scripts/sw_sheet_metal.py` · 判定：**成立**

**我们的原文**（`scripts/sw_sheet_metal.py`，`DraftFeatureSpec` 与 `create_draft._apply`）：
```
    """@brief 拔模的可制造参数，角度为度、深度为米。"""
```
```
        data.Angle = float(spec.angle)
```
```
            raise ValueError("拔模角度必须位于 0 与 180 度之间")
```

**官方的原文**（`C:\swapi\types\IDraftFeatureData2\Angle.md`，`## Returns` 段逐字）：
```
Draft angle in radians
```

**一句话依据**：官方逐字写 `Draft angle in radians`，而 spec docstring 自述「角度为度」并把度原样赋给 `data.Angle`。

**附注（不影响判定）**：同函数源码注释自述 `CreateDefinition(3)` 真机返回 `None`，故该行真机上未必执行到；但复核的是**源码里的量纲写法**，该事实不改变结论。

---

## A 附录 1 ＝ C#1 · `scripts/sw_sheet_metal.py` · 判定：**成立**（两处分别核）

**我们的原文**（`scripts/sw_sheet_metal.py`，`create_base_flange` 与 `_create_from_definition` 各一处，两处逐字重复）：
```
    # GetErrorCode2 还带一个 by-ref ``isWarning`` 参数；此处只需拒绝硬错误，
    # 使用无歧义的 GetErrorCode 可兼容 pywin32 静态与动态代理。
    error_code = int(get_com_member(feature, "GetErrorCode") or 0)
```

**官方的原文**（`C:\swapi\types\IFeature\GetErrorCode.md`，正文首段逐字）：
```
Obsolete. Superseded by [[IFeature::GetErrorCode2]].
```
后继页 `C:\swapi\types\IFeature\GetErrorCode2.md` 的 Signature 逐字（**该页无 Obsolete 行**）：
```
System.int GetErrorCode2( out System.bool IsWarning )
```
第二源佐证（`C:\swapi\types\IFeatureManager\CreateFeature.md`，`## Remarks` 列表项逐字）：
```
- [[IFeature::GetErrorCode2]] to get any errors that occurred during the creation of the feature.
```

**一句话依据**：我们主动调用的 `IFeature.GetErrorCode()` 带官方 `Obsolete` 行、官方点名后继 `GetErrorCode2`，而代码注释明写「用无歧义的 `GetErrorCode`」—— 知情的选择，两处调用点均如此。

**注**：A 附录把 CreateFeature 那句引成「Use: [[IFeature::GetErrorCode2]] to get any errors…」；该 markdown 里它是 `## Remarks` 下的一条列表项，`Use:` 前缀是原 CHM 的小节标题、非本文件文字。内容逐字对得上。

---

## B#1 · `scripts/sw_sheet_metal.py` · 判定：**成立**

**我们的原文**（`scripts/sw_sheet_metal.py`，`create_edge_flange` 的来源块、docstring 与 `_apply`）：
```
# ⚠ 边集合由调用方在创建前用 SelectByID2 选好；本函数不代为选边，
```
```
    """@brief 在已选中的边上创建原生边法兰。

    调用前必须先用 ``sw_part._select_by_id`` 把目标边选入选区。
    """
```
```
        data.UseDefaultBendRadius = bool(spec.use_default_radius)
        data.BendRadius = float(spec.bend_radius)
        data.BendAngle = float(spec.angle)
        data.UseDefaultBendAllowance = True

    return _create_from_definition(model, SW_FM_EDGE_FLANGE, _apply)
```
★ 补充事实：全文件 grep `AddEdges|InsertSketchForEdgeFlange` 只有一条**注释**（列举接口 43 个成员），**没有任何可执行调用**。

**官方的原文**（`C:\swapi\types\IEdgeFlangeFeatureData\AddEdges.md`，`## Remarks` 段逐字）：
```
Before calling this method, call [[IModelDoc2::InsertSketchForEdgeFlange]] to associate the sketches with the edges.
```
（`C:\swapi\types\IModelDoc2\InsertSketchForEdgeFlange.md`，`## Remarks` 段逐字）：
```
After calling this method, you must create the profile for the flange on the appropriate plane. Then use [[IFeatureManager::CreateDefinition]], [[IEdgeFlangeFeatureData]], and [[IFeatureManager::CreateFeature]] to create the edge flange.
```
官方例子 `C:\swapi\examples\Create_Edge_Flange_Example_VBNET.md` 逐字：
```
        	swFeature = swModel.InsertSketchForEdgeFlange(swEdge, dAngle, False)
```
```
        	Call FeatData.AddEdges(vFlangeEdges, vSketchFeats)
```

**一句话依据**：官方为这条 FeatureData 路径写下的调用序是 `InsertSketchForEdgeFlange` → `CreateDefinition` → `AddEdges` → `CreateFeature`，而我们声明的前置只是「调用方先 `SelectByID2` 把边选进选区」，`_apply` 里这两步一个都没有。

**强度说明**：官方 `AddEdges` 页的 Remarks 约束的是「**调 AddEdges 之前**要先 `InsertSketchForEdgeFlange`」，并未逐字写「不调 `AddEdges` 会失败」；B 文件自己的「查不到」段也承认这一点。本条成立在「官方原文逐字存在 + 我们代码确无这两步」这一事实上。

---

## B#2 · `scripts/sw_sheet_metal_weld_entry.py` · 判定：**成立**

**我们的原文**（`scripts/sw_sheet_metal_weld_entry.py`，`insert_sheet_metal_closed_corner` 体内与返回值）：
```
    #: ★ 官方**零参** ⇒ 一个实参都不传（★ 官方 Signature 逐字 `void InsertSheetMetalClosedCorner()`）
    get_com_member(model, "InsertSheetMetalClosedCorner")
```
```
        "preconditions_held": None,
        "precondition_note": "★★ **官方页无 `## Remarks` 段 ⇒ 前置查不到** ⇒ 不编前置（铁律 5）",
```

**官方的原文**（`C:\swapi\examples\Create_and_Modify_Closed_Corner_Feature_Example_VBNET.md`，逐字）：
```
'Select the faces for the closed corner feature
```
```
status = swModelDocExt.SelectByID2("", "FACE", 0.0110595835492404, 0.0280018934407167, 0.0497348782814129, True, 1, Nothing, 0)
status = swModelDocExt.SelectByID2("", "FACE", 0.0181424245698736, 0.0110595835492404, 0.0495671179450028, True, 1073741824, Nothing, 0)
```
```
'Insert the closed corner feature
swModel.InsertSheetMetalClosedCorner()
```
★ 第二源核对：`C:\swapi\types\IModelDoc2\InsertSheetMetalClosedCorner.md` 全文只有描述句、`**Signature**: \`void InsertSheetMetalClosedCorner()\`` 与 `## See Also`，**确无 `## Remarks` 段** —— 与我们代码注释的「前置查不到」一致。

**一句话依据**：官方例子在这个零参调用前连做两次 `SelectByID2` 选面（第一条 mark = 1），我们一步都不选并把 `preconditions_held` 如实记成 `None`。

---

## C#2 · `scripts/sw_sheet_metal.py` · 判定：**成立**

**我们的原文**（`scripts/sw_sheet_metal.py`，常量与 `create_base_flange` 体内）：
```
SW_END_COND_BLIND = 0
```
```
    data.D1EndConditionType = SW_END_COND_BLIND
    data.D1EndConditionDistance = float(spec.depth)
    data.D2EndConditionType = SW_END_COND_BLIND
    data.D2EndConditionDistance = 0.0
```

**官方的原文**（`C:\swapi\types\IBaseFlangeFeatureData\D1EndConditionType.md`，`## Returns` 段逐字；`D2EndConditionType.md` 同句）：
```
End condition type as defined in [[swFlangeOffsetTypes_e]]
```
`C:\swapi\enums\swFlangeOffsetTypes_e.md` front matter 逐字：
```
enum_member_count: 6
```
成员表里与本条相关的两行逐字：
```
| swFlangeOffsetBlind | 1 = Positions the edge flange based on the length and direction you specify |
```
```
| swFlangeOffsetUpToVertex | 2 = Positions the edge flange up to a specified vertex; for flange length, the selected vertex may be either on a plane that is normal to the end face of the edge flange or on a plane that is parallel to the face of the base flange |
```
★ 全表 6 行的值为 `1 / 2 / 3 / 4 / 5 / 6`，**没有值为 0 的成员**。
官方例子 `C:\swapi\examples\Create_Base_Flange_Feature_Example_VBNET.md` 逐字：
```
        swBaseFlangeFeat.D1EndConditionType = 1
```

**一句话依据**：官方为 `D1/D2EndConditionType` 点名的枚举是 `swFlangeOffsetTypes_e`（「Blind」在官方是 **1**），该枚举没有 0，而我们传的是 `SW_END_COND_BLIND = 0`。

---

## 结尾三行

- **核了 8 处**（表内高置信条目 8 条：A #1/#2/#3 + A 附录 1，B #1/#2，C #1/#2）→ **去重后 7 处**（A 附录 1 与 C#1 同一发现）。
- **两侧原文都逐字对得上：7 / 7**（官方原文在 `C:\swapi` 全部命中；我们的原文在 `scripts/sw_sheet_metal.py` / `scripts/sw_sheet_metal_weld_entry.py` 全部命中）。
- **判定：成立 7 · 不成立 0 · 存疑 0** ⇒ **对不上 0 处**。
  ⚠ 附记 4 处**引用排版**瑕疵（非内容不符，未计入「对不上」）：A#1 与 A 附录各 1 处把官方 markdown 硬折行处拼成一行、A 附录把 CreateFeature 的 `## Remarks` 列表项冠上原 CHM 小节标题 `Use:`、B#1 对「两步前置是**强制**」的措辞强于官方原文（该页只约束「调 AddEdges 之前」）。