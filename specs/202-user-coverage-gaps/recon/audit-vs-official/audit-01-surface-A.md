# audit-01-surface · 核对 A（签名一致性）

- 域：01-surface
- 我们这边的文件：`scripts/sw_surface.py` · `scripts/sw_surface_features.py` · `scripts/sw_surface_edit_ops.py` · `scripts/sw_surface_ref_ops.py`（四个都存在）
- 官方源：`C:\swapi\types\<接口>\<成员>.md`（逐条读 `**Signature**` 与 `## Parameters`）
- 判据：只报「参数个数不符 / 顺序不符 / 明显类型不符」；给不出两段原文的一律不写

## 分歧表

| # | 我们的原文（文件 + 片段）| 官方的原文（文件 + 片段）| 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | `sw_surface.py`：<br>`return _invoke(`<br>`        get_modeler(sw_app), "CreateConicalSurface",`<br>`        origin, axis, float(half_angle), float(radius),`<br>`    )` | `C:\swapi\types\IModeler\CreateConicalSurface.md`：<br>`**Signature**: \`System.object CreateConicalSurface( System.object Center, System.object Direction, System.double Radius, System.double SemiAngle )\``<br>`- **Radius**: No description`<br>`- **SemiAngle**: No description` | 位置 3 / 位置 4 两个 double 的**顺序反了**：官方第 3 位是 `Radius`、第 4 位是 `SemiAngle`，我们第 3 位传 `half_angle`、第 4 位传 `radius`。个数与类型都对得上，错的是两个量的先后 | 高 |
| 2 | `sw_surface.py`：<br>`return _invoke(`<br>`        get_modeler(sw_app), "CreateBsplineSurface",`<br>`        control_points, weights, knots, degree,`<br>`    )` | `C:\swapi\types\IModeler\CreateBsplineSurface.md`：<br>`**Signature**: \`System.object CreateBsplineSurface( System.object Props, System.object UKnots, System.object VKnots, System.object CtrlPtCoords )\``<br>`- **Props**: Array containing 8 integers packed as 4 double elements (see **Remarks**)`<br>`- **CtrlPtCoords**: Array of numCtrlPtCoord (see **Remarks**)` | 四个 object 的**顺序反了**：官方第 1 位是 `Props`（把 Uorder/Vorder 等 8 个整数打包成 4 个 double 的数组）、第 4 位才是 `CtrlPtCoords`（控制点坐标数组）；我们把 `control_points` 放在第 1 位、`degree` 放在第 4 位。个数与类型都相同，错的是四个量的先后 | 高 |
| 3 | `sw_surface.py`：<br>`return _invoke(`<br>`        get_modeler(sw_app), "CreateSheetFromSurface", surface, float(tolerance)`<br>`    )` | `C:\swapi\types\IModeler\CreateSheetFromSurface.md`：<br>`**Signature**: \`System.object CreateSheetFromSurface( System.object SurfaceIn, System.object UvRange )\``<br>`- **UvRange**: Array of UV values for this surface` | 第 2 个实参**标量 vs 数组**：官方第 2 位 `UvRange` 是「该曲面的 UV 值数组」，我们传的是单个 `float`（本包装把它叫 `tolerance`，是加厚语义）；形参类型两者都写 `System.object`，只有官方 `## Parameters` 那行说明它是数组 | 中 |
| 4 | `sw_surface_ref_ops.py`：<br>`get_com_member(model, "InsertLoftRefSurface2",`<br>`                   bool(closed), bool(keep_tangency), bool(force_non_rational),`<br>`                   float(tess_tolerance_factor), int(start_matching_type), int(end_matching_type))` | `C:\swapi\types\IModelDoc2\InsertLoftRefSurface2.md`：<br>`**Signature**: \`void InsertLoftRefSurface2( System.bool Closed, System.bool KeepTangency, System.bool ForceNonRational, System.double TessToleranceFactor, System.short StartMatchingType, System.short EndMatchingType )\`` | 第 5 / 第 6 个实参的**声明类型不一致**：官方把 `StartMatchingType` / `EndMatchingType` 声明为 `System.short`，我们用 `int(...)` 传（pywin32 送出 VT_I4 而非 VT_I2）。个数与先后都对 | 中 |

## 查不到（不计入分歧）

- `scripts/sw_surface.py` 的 `create_revolution_surface` → `SURFACE_CREATION_METHODS` 里登记的 `"CreateRevolutionSurface"`：`C:\swapi\types\IModeler\` 下**没有** `CreateRevolutionSurface.md`（同目录有 `CreateExtrusionSurface.md` 等，唯独没有这一份）⇒ 这一处**无法与官方 Signature 并排数**，按铁律 5 记「查不到」，不给结论。

## 结尾三行

- 都核了 **35 处**调用点与官方 `**Signature**`（sw_surface 16 · sw_surface_features 12 · sw_surface_edit_ops 5 · sw_surface_ref_ops 2）。
- 报了 **4 条**（#1 #2 顺序不符 · #3 标量/数组类型不符 · #4 short/int 声明类型不符）。
- 置信度为**高**的是：**#1、#2**。