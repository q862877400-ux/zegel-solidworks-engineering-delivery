# audit-01-surface · 核对 B（前置与 mark）

范围：`scripts/sw_surface.py` · `scripts/sw_surface_features.py` · `scripts/sw_surface_edit_ops.py` · `scripts/sw_surface_ref_ops.py`
对照源：`C:\swapi\types\<接口>\<成员>.md` 的 `## Remarks` · `C:\swapi\examples\*.md` 的调用序

| # | 我们的原文（文件 + 片段） | 官方的原文（文件 + 片段） | 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | `sw_surface_features.py`：`selected = _select_all_surface_faces(model, mark=0)` → 紧接 `pre = get_com_member(fm, "PreTrimSurface", bool(mutual), bool(split_system),` … → 再 `post = get_com_member(fm, "PostTrimSurface", bool(sew))`（两步之间**没有**任何再选择） | `IFeatureManager\PostTrimSurface.md`：「Before calling this method: 1. Call [[IFeatureManager::PreTrimSurface]]. 2. **Select the trimming surfaces or trim tool.**」；`IFeatureManager\PreTrimSurface.md`：「After calling this method: 1. **Select the trimming surfaces or trim tool.** … 3. Call [[IFeatureManager::PostTrimSurface]].」；官方例子 `Create_Trimmed_Surface_Feature_Example_CSharp.md`：`status = swFeatureMgr.PreTrimSurface(false, true, false, false);` → `status = swModelDocExt.SelectByID2("", "SURFACEBODY", …, true, 0, null, 0);` → `swFeat = (Feature)swFeatureMgr.PostTrimSurface(true);` | 调用序：官方是 **Pre → 选中剪裁面/剪裁工具 → Post**；我们是 **选中 → Pre → Post**，两步之间不再选一次。 | 高 |
| 2 | `sw_surface_features.py`：`get_com_member(fm, "FeatureExtruRefSurface3", *args)`（该函数体内没有任何 `SelectByID2`），形参 `sketch_name` 只出现在返回值里：`"through_all": bool(through_all), "sketch_name": str(sketch_name),` | `IFeatureManager\FeatureExtruRefSurface3.md` Remarks：「Before calling this method, **select the entities for the extruded surface** using [[IModelDocExtension::SelectByID2]].」，并给出 mark 表「2D or 3D sketch → 0 / Sketch segments → 0 or 4 / Single planar face → 0」 | 前置：官方要求调用前先按 mark 选出实体；我们的包装**从不做选择**，`sketch_name` 这个形参只被回显进返回值、没有任何取草图的动作。 | 高 |
| 3 | `sw_surface_features.py` docstring：`★ 前置：★ **文件里要有曲面体**（★ 与 `knit_surfaces_report` 同款前置 —— ★ 而 `use_auto_select=True` 时官方会"自动选所有体"）。`；调用处 `feat = get_com_member(fm, "FeatureBossThicken",` 之前无任何选择动作 | `IFeatureManager\FeatureBossThicken.md` Remarks：「This method generates a boss feature by thickening a selected reference surface.  **The surface must be selected with a mark of 1.** See [[IModelDocExtension::SelectByID2]] for details.」＋「If **UseAutoSelect** is false, the user must select the **bodies** that the feature will affect.」 | mark 与前置：官方要求**参考曲面**先以 **mark=1** 选中（`UseAutoSelect` 管的是**体**、不是这张曲面）；我们既没选曲面、也没用 mark=1，docstring 把前置写成「文件里要有曲面体」。 | 高 |
| 4 | `sw_surface_features.py`：`if int(end_condition) not in (0, 1):`（接受 1）＋ `selected = _select_all_surface_faces(model, mark=0)`；该 helper 先 `model.ClearSelection2(True)` 再只选各体的**面** | `IModelDoc2\InsertExtendSurface.md` Remarks：「**The selected point or surface to which to extend should be in the selection list.**」＋ 参数表「1 - Extend surface up to a selected point」 | 前置：`end_condition=1` 时官方要求选区里有「点」；我们接受该值，但选区被 `ClearSelection2` 清过、之后只放面，从没有点。 | 中 |

## 附注（不计入上表）

- **查不到**：`C:\swapi\types\IModeler\CreateRevolutionSurface.md` 在本机 swapi 里不存在（`sw_surface.py` 的 `create_revolution_surface` 有包装）⇒ 按铁律 5 记「查不到」，未据此报任何条。
- **已核、判定一致故未报**：`InsertSewRefSurface`（官方 mark 1 ↔ 我们 `mark=1`）、`InsertFillSurface2`（官方 `Boundary curves = 1` ↔ 我们 `MARK_BOUNDARY = 1` 选中边）、`InsertPlanarRefSurface`（官方 `Marks of 1` ↔ 我们选草图时传 mark 1）、`InsertFeatureReplaceFace`（官方「faces to replace → 1 / replacement surfaces → 2」↔ 我们曲面面 mark 1 · 实体面 mark 2）、`InsertLoftRefSurface2`（官方「profile selections should be 1」↔ 我们 docstring 如实转录）、`InsertRevolvedRefSurface`（官方**没给** mark ↔ 我们如实写「不假定」）、`InsertOffsetSurface` / `InsertExtendSurface` / `InsertCutSurface` / `PreTrimSurface` / `PostTrimSurface` 官方 Remarks **均未规定 mark**、13 个 `IModeler.Create*Surface` 页正文无选择/mark 要求。

---

核了几处：33 处调用点（sw_surface.py 14 · sw_surface_features.py 12 · sw_surface_edit_ops.py 5 · sw_surface_ref_ops.py 2），对照官方 `## Remarks` 的成员 17 个。
报了几条：4 条（#1 · #2 · #3 · #4）。
高置信：3 条（#1 剪裁曲面调用序 · #2 曲面-拉伸缺选择前置 · #3 加厚缺 mark=1 前置）。
