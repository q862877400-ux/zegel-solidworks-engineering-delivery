# 核对 A · 签名一致性 —— 域 `02-sheetmetal`

**范围（只做这两个框的交集）**：`scripts/sw_sheet_metal.py` · `scripts/sw_sheet_metal_weld_entry.py`
**只做**：核对 A —— 把我们的调用**逐个实参**与官方 Signature 的**形参表**并排数（个数 / 顺序 / 类型·量纲）。
**不跑 SolidWorks、不跑 pytest、未修改仓内任何文件。**

**核对计数口径**：18 处方法/函数调用点（含 `Initialize` 与 5 个直入法入口）+ 7 处 FeatureData 属性页 = **25 处**。
其中**带实参列表、逐个实参并排数过的共 15 处**：`Initialize`(9) · `CreateDefinition`(1) · `CreateFeature`(1) · `CreateCustomBendAllowance`(0) · `GetBodies2`(2) · `GetSelectedObjectCount2`(1) · `InsertSheetMetalMiterFlange`(14) · `InsertEndCapFeature3`(10) · `InsertGussetFeature3`(20) · `InsertMidSurface`(4) 及各自的调用点。

**第三方源（出厂类型库反射，用于与文档页互证）**：`D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt`
—— 本次逐条比对的 arity 与 `C:\swapi\types\` 各页 Signature **全部一致**，未出现「文档与类型库参数个数不同」的两源不一致（对照 `IModelDoc2.InsertSheetMetalMiterFlange` 两份同名页：文档 11 参、类型库 11 参，也一致）。

---

## 发现

| # | 我们的原文（文件 + 片段）| 官方的原文（文件 + 片段）| 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | `scripts/sw_sheet_metal.py`：`data.BendAngle = float(spec.angle)`（`create_one_bend` 的 `_apply` 内）；同文件 `OneBendSpec.validate`：`raise ValueError("折弯角度必须位于 0 与 360 度之间")` | `C:\swapi\types\ISketchedBendFeatureData\BendAngle.md`：**Signature** `System.double BendAngle {get; set;}` · **Returns**「0.261799 <= Bend angle in increments of 0.261799 radians (15 degrees) <= 1.5708」；另 `C:\swapi\examples\Change_Bend_Radius_of_Sketched_Bend_Example_VB.md`：`'1 radian = 180º/p = 57.295779513º` 与 `"    BendAngle = " & swSketchBend.BendAngle * 57.3 & " deg"` | 实参的**量纲**与官方成员接受的量纲不符：官方该属性收**弧度**且取值域 `0.261799..1.5708`（15°–90°），我们把**度**原样赋进去（校验允许到 360）。 | 高 |
| 2 | `scripts/sw_sheet_metal.py`：`data.BendAngle = float(spec.angle)`（`create_edge_flange` 的 `_apply` 内）；同文件 `EdgeFlangeSpec` docstring：`"""@brief 边法兰的可制造参数，长度单位为米，角度为度。"""`，字段默认 `angle: float = 90.0`，`validate` 内 `raise ValueError("边法兰角度必须位于 0 与 180 度之间")` | `C:\swapi\types\IEdgeFlangeFeatureData\BendAngle.md`：**Signature** `System.double BendAngle {get; set;}` · **Returns**「Flange angle; default value is 1.5707963267949 radians」 | 同上：官方收**弧度**（默认值 π/2 即 90°），我们把**度**原样赋进去；仅默认值就会传 `90.0`，超出官方量纲约 57 倍。 | 高 |
| 3 | `scripts/sw_sheet_metal.py`：`data.Angle = float(spec.angle)`（`create_draft` 的 `_apply` 内）；同文件 `DraftFeatureSpec` docstring：`"""@brief 拔模的可制造参数，角度为度、深度为米。"""`，`validate` 内 `raise ValueError("拔模角度必须位于 0 与 180 度之间")` | `C:\swapi\types\IDraftFeatureData2\Angle.md`：**Signature** `System.double Angle {get; set;}` · **Returns**「Draft angle in radians」 | 同上：官方收**弧度**，我们把**度**原样赋进去。 | 高 |

**以上三条为本次 A（签名/实参一致性）范围内报出的全部内容。** 判定依据统一为：官方成员页给出的**取值域/单位**（Returns 段）与我们**实参的量纲**不一致。

### 未报但已核过、判定为一致的（备查，不进表）

- `IBaseFlangeFeatureData.Initialize`：官方 9 参（`UseMaterialSheetMetalParameters, OverrideDefaultBendAllowance, CustomBendAllowance, OverrideDefaultBendRelief, ReliefType, UseReliefRatio, ReliefRatio, ReliefWidth, ReliefDepth`），我们 `data.Initialize(False, True, bend_allowance, True, SW_SHEET_METAL_RELIEF_RECTANGULAR, True, float(spec.relief_ratio), 0.0, 0.0)` **9 个、顺序与类型逐位对齐**；类型库反射 `Void Initialize(Boolean, Boolean, Object, Boolean, Int32, Boolean, Double, Double, Double)`（`## IBaseFlangeFeatureData`）同为 9。
- `IFeatureManager.CreateDefinition` / `CreateFeature` / `CreateCustomBendAllowance`：官方各 1 / 1 / 0 参，与我们的实参一致。
- `IFeatureManager.InsertSheetMetalMiterFlange`（14）、`InsertEndCapFeature3`（10）、`InsertGussetFeature3`（20）、`InsertMidSurface`（4）：实参个数与**顺序**逐位对齐官方形参表；类型库反射同 arity 且 `DirType/LocType` 为 `Int16`（= 官方 `System.short`，与本仓已在代码里声明的 `short_param_note` 相符）。
- `IModelDoc2.InsertSheetMetalClosedCorner`：官方 `void InsertSheetMetalClosedCorner()` 零参，我们零参 —— 一致。
- `IPartDoc.GetBodies2`（2）、`ISelectionMgr.GetSelectedObjectCount2`（1）、`IFeature.GetNextFeature`（0）、`IPartDoc.FirstFeature`（0）、`IFeature.GetDefinition`（0）、`IFeature.GetTypeName2`（0）、`IBody2.GetFaces`（0）、`IBody2.IsSheetMetal`（0）、`IModelDoc2.FeatureManager` / `SelectionManager`（0 参属性）—— 全部一致。
- `IEdgeFlangeFeatureData.BendRadius`：「default value is 0.00073666 m」⇒ 我们的米制口径**正确**，反衬出上表第 2 条的角度量纲分歧。

### 查不到（铁律 5 · 不写进表）

- `sw_sheet_metal_weld_entry.py` 的 `_surface_body_count` 依次尝试 `"GetSurfaceBodies"` 与 `"GetSurfaceBodyCount"` 两个成员名；**`C:\swapi\types\` 全库无这两个成员的任何页面**（`glob **/GetSurfaceBod*.md` 零命中）⇒ **查不到**，不拿相似名字顶替，故不报。
- `ISMGussetFeatureData.ProfileAngleDim` 官方页 **未给单位**（Returns 段只写「Angle formed where gusset intersects the sheet metal part」）⇒ 我们 `create_gusset` 里 `data.ProfileAngleDim = float(spec.profile_angle)` 的量纲**无官方原文可比** ⇒ 不报。

---

## 附：以下一条**不属于核对 A**（核对 C · 废弃链范围），只作备记、不计入上表

| 我们的原文 | 官方的原文 | 分歧点 | 置信度 |
|---|---|---|---|
| `scripts/sw_sheet_metal.py` 两处：`error_code = int(get_com_member(feature, "GetErrorCode") or 0)`（`create_base_flange` 与 `_create_from_definition` 各一处） | `C:\swapi\types\IFeature\GetErrorCode.md`：**Obsolete. Superseded by [[IFeature::GetErrorCode2]].** ；同库 `C:\swapi\types\IFeatureManager\CreateFeature.md` 的 **Remarks** 亦写「Use: [[IFeature::GetErrorCode2]] to get any errors that occurred during the creation of the feature.」 | 我们调用的成员被官方标 **Obsolete**（后继 `GetErrorCode2`）。★ 属核对 C 范围，本次不判、只记。 | 高 |

---

核了 25 处（18 处方法调用点 + 7 处 FeatureData 属性页；其中 15 处带实参列表逐个实参并排数过）。
报 3 条（全部在核对 A 表内；附录 1 条属核对 C 范围、未计入）。
高置信 3 条 —— #1、#2、#3（均为「官方成员收弧度、我们把度原样传入」的实参量纲不符）。