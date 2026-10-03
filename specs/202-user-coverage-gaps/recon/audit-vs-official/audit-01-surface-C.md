# audit-01 · 域 01-surface · 核对 C（废弃链与枚举取值）

- **范围**：`scripts/sw_surface.py` · `scripts/sw_surface_features.py` · `scripts/sw_surface_edit_ops.py` · `scripts/sw_surface_ref_ops.py`（四个文件全部存在，无「该域无对应文件」）
- **只做核对 C**：① 调的是不是官方标了 Obsolete 的成员（官方点名了谁当后继）② 当枚举传的**字面量**在 `enums/*.md` 里是不是合法成员
- **官方源**：只读 `C:\swapi\types\<接口>\<成员>.md`、`C:\swapi\enums\*.md`
- **纪律**：给不出「我们原文 + 官方原文」两段的，一律不写；只写亲手读到的；宁少勿滥

## 表

| # | 我们的原文（文件 + 片段）| 官方的原文（文件 + 片段）| 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | `scripts/sw_surface.py` —— `return _invoke(get_modeler(sw_app), "CreatePlanarSurface", point, normal)` ／ `get_modeler(sw_app), "CreateCylindricalSurface", origin, axis, float(radius)` ／ `_invoke(get_modeler(sw_app), "CreateSphericalSurface", center, float(radius))` ／ `get_modeler(sw_app), "CreateConicalSurface",`（另有 `require_runtime_available("CreatePlanarSurface")` 等四处同名守卫） | `C:\swapi\types\IModeler\CreatePlanarSurface.md` —— `Obsolete. Superseded by [[IModeler::CreatePlanarSurface2]].`<br>`C:\swapi\types\IModeler\CreateCylindricalSurface.md` —— `Obsolete. Superseded by [[IModeler::CreateCylindricalSurface2]].`<br>`C:\swapi\types\IModeler\CreateSphericalSurface.md` —— `Obsolete. Superseded by [[IModeler::CreateSphericalSurface2]].`<br>`C:\swapi\types\IModeler\CreateConicalSurface.md` —— `Obsolete. Superseded by [[IModeler::CreateConicalSurface2]].` | 四个薄封装实际调用的成员**全部**带官方 `Obsolete` 行，且官方逐个点名了后继（各自 `…2`）；同一文件的 `SURFACE_CREATION_METHODS` 里同时登记了 `CreatePlanarSurface2` / `CreateCylindricalSurface2` / `CreateSphericalSurface2` / `CreateConicalSurface2`，但**没有任何封装调它们** ⇒ 被调用的一代与官方指定的后继一代不一致 | 高 |
| 2 | `scripts/sw_surface_features.py` —— `if int(end_condition) not in (0, 1):`<br>　　`return {"ok": False, "error": "end_condition 只支持 0（按距离）/ 1（到选定点）：%r" % end_condition}`（同函数 docstring：`:param end_condition: **0 = 按距离**（默认）· **1 = 延伸到选定点**。`） | `C:\swapi\types\IModelDoc2\InsertExtendSurface.md` —— `- **EndCondition**:` 下的 `  - 2 - Extend surface up to a selected surface`<br>`C:\swapi\enums\swSurfaceExtendEndCond_e.md` —— `| swSurfaceExtendEndCondUpToSurface | 2 |`（该枚举共 3 个成员：`swSurfaceExtendEndCondDistance \| 0`、`swSurfaceExtendEndCondUpToPoint \| 1`、`swSurfaceExtendEndCondUpToSurface \| 2`）| 我们把 `EndCondition` 的合法取值收窄成 `{0,1}` 并**显式拒绝 2**；官方参数表与官方枚举都列了第三个合法值 `2`（延伸到选中的曲面）⇒ 一个官方合法成员在本包装里被当成非法 | 高 |
| 3 | `scripts/sw_surface_edit_ops.py` —— `RULED_TYPE_MEANINGS = {`<br>　　`    0: "Tangent to Surface",`<br>　　`    1: "Normal to Surface",`<br>　　`    2: "Tapered to Vector",`<br>　　`    3: "Perpendicular to Vector",`<br>　　`    4: "Sweep",`<br>`}`（同文件另有 `if int(ruled_type) not in RULED_TYPE_MEANINGS:` 与 `"type_meaning": RULED_TYPE_MEANINGS[int(ruled_type)]`）| `C:\swapi\enums\swRuledSurfaceType_e.md` —— `| swRuledSurfaceType_TangentToSurface | 1 |` · `| swRuledSurfaceType_NormalToSurface | 2 |` · `| swRuledSurfaceType_TaperedToVector | 3 |` · `| swRuledSurfaceType_PerpendicularToVector | 4 |` · `| swRuledSurfaceType_Sweep | 5 |` | 我们把直纹曲面 `Type` 的合法取值写成 **0..4**，而官方枚举 `swRuledSurfaceType_e` 的合法成员是 **1..5**（枚举里**没有 0**）⇒ 我们表里的 `0` 不是合法成员；且按我们的表传 `4` 表示 Sweep，按官方枚举 `4` 是 `PerpendicularToVector`、Sweep 是 `5` ⇒ 同一个字面量在两侧指向不同语义。<br>★ 附注（**两源不一致，不判谁对**）：`C:\swapi\types\IFeatureManager\InsertRuledSurfaceFromEdge2.md` 的参数表确实是 0-based（`0 = Tangent to Surface` … `4 = Sweep`），但该页**没有**把 `Type` 指向 `swRuledSurfaceType_e`；同仓 `scripts/sw_surface_features.py` 已在用 1..5 口径（`if not (1 <= t <= 5):`），与本模块相反 | 高 |

## 已核但**未**报（避免含水，仅记账）

以下位置查过官方原文且**对得上**，故不列为分歧：`IModelDocExtension.InsertDeleteFace` 的 `swFaceDeleteOption_e` 0..3（`sw_surface_edit_ops.py` 一致）；`IFeatureManager.InsertRevolvedRefSurface` 的 `RevType` 0/1/2（`sw_surface_ref_ops.py::REVOLVE_TYPE_MEANINGS` 逐字一致）；`FeatureExtruRefSurface3` 的 `StartCond/T1/T2`（`swStartSketchPlane=0` / `swEndCondBlind=0` / `swEndCondThroughAll=1` 逐条对上）；`InsertFillSurface2` 的 `Resolutions 1/2/3` 与 `swFeatureFillSurfaceOptions_e`；`GetBodies2` 的 `-1/0/1`（`swAllBodies/swSolidBody/swSheetBody`）；以及各成员的**代际**——`InsertRuledSurfaceFromEdge2` / `InsertFillSurface2` / `FeatureExtruRefSurface3` / `InsertLoftRefSurface2` / `IModelDocExtension.InsertDeleteFace` / `IFeatureManager.InsertCutSurface` / `IFeatureManager.PreTrimSurface`+`PostTrimSurface` 均已是官方点名的那一代。

## 结尾三行

- 都核了 **38 处**调用点：`sw_surface.py` 19（`SURFACE_CREATION_METHODS` 登记的全部 `IModeler.Create*Surface`）／`sw_surface_features.py` 12／`sw_surface_edit_ops.py` 5／`sw_surface_ref_ops.py` 2。
- 报了 **3 条**。
- 置信度为高的是 **第 1、2、3 条**（全部）。