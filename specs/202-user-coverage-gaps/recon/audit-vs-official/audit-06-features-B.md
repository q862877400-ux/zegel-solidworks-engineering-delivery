# 06-features · 核对 B（前置与 mark）· audit-06-features-B

**范围**：`scripts/sw_part.py` · `scripts/sw_feature_entry_ops.py` · `scripts/sw_feature_readback.py`
**核对口径**：只读官方 `## Remarks` 的**前置**（先选什么、mark 几、调用序），与我们代码里实际做没做那一步、mark 传的对不对比。
**纪律**：每条都给「我们这边可搜索的原文片段」+「官方那边可搜索的原文片段」；给不出两段的**不写**。

| # | 我们的原文（文件 + 片段） | 官方的原文（文件 + 片段） | 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | **sw_part.py** `revolve_boss` / `revolve_cut`：<br>`    if axis_sketch_name:`<br>`        _select_revolve_axis(model, str(axis_sketch_name))`<br>`    _ensure_sketch_selected(model, sketch_name)`<br>…紧接着 `return model.FeatureManager.FeatureRevolve2(`<br>而 `_ensure_sketch_selected` → `_select_sketch_ref` 的第一步是：<br>`    model.ClearSelection2(True)` | **C:\swapi\types\IFeatureManager\FeatureRevolve2.md**<br>「Before calling this method, call [[IModelDocExtension::SelectByID2]] to select:」<br>「- the sketch to revolve, using **Mark = 0**.」<br>「- the axis of revolution, using **Mark = 4 or 16**.」 | 官方要求调用前**轮廓（mark 0）与旋转轴（mark 4/16）同时留在选择集里**；我们先选轴、紧接着走 `_ensure_sketch_selected`，其内部 `ClearSelection2(True)` 把整份选择集清空 ⇒ 调 `FeatureRevolve2` 时轴已不在选择集里。（`revolve_boss`/`revolve_cut` 两处同形） | 高 |
| 2 | **sw_part.py** `linear_pattern`（全函数只此一次选择，紧接着就调 `FeatureLinearPattern3`）：<br>`    _select_by_id(model.Extension, feature_name, "BODYFEATURE", mark=4)` | **C:\swapi\types\IFeatureManager\FeatureLinearPattern3.md**<br>「Using [[IModelDocExtension::SelectByID2]] to select features and components, **ordered selection of the features and components is required**」<br>「- **1 and 2 to mark the directions**」<br>「- 4 to mark the features to pattern」<br>（CHM 同文：`SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~FeatureLinearPattern3.html`，逐字「1 and 2 to mark the directions」） | 官方在「**选特征**」这一列要求同时用 **mark 1 / mark 2 标方向**、mark 4 标特征；我们只选了特征（mark=4），**从未选过任何方向**。 | 高 |
| 3 | **sw_part.py** `linear_pattern_report`（该函数内**没有任何** SelectByID2 / Select 调用，直接调特征入口）：<br>`        get_com_member(get_com_member(model, "FeatureManager"), "FeatureLinearPattern3",`<br>`                       n1, s1, n2, s2, False, False, "", "", False, False)` | 同上 **FeatureLinearPattern3.md**<br>「ordered selection of the features and components is required」<br>「- 1 and 2 to mark the directions」<br>「- 4 to mark the features to pattern」 | 同一处前置的**第二个站点**：这里连要阵列的特征都没选，选择集为空就调用。 | 高 |
| 4 | **sw_part.py** `auto_dimension_sketch`（缺一个基准也照样往下调 `AutoDimension2`）：<br>`    for segment, mark in ((vertical, 2), (horizontal, 4)):`<br>`        if segment is None:`<br>`            continue` | **C:\swapi\types\ISketch\AutoDimension2.md**<br>「You can supply datums for horizontal and vertical dimensioning schemes. … **It is an error to supply just one datum** as indicated by the status value swAutodimStatus_DatumNotSupplied.」 | 官方明写**只给一个基准是错误**；我们的循环对缺失的那个基准 `continue` 跳过后，仍无条件执行 `status_code = int(get_com_member(active, "AutoDimension2", 1, 1, -1, 1, -1))`。（两个 mark 值本身 2=horizontal datum / 4=vertical datum 与官方一致，不算分歧） | 高 |
| 5 | **sw_part.py** `fillet`（函数体内**无任何选择代码**，`edges` 形参收了不用）：<br>`        edges: 预先选择的边线列表，None 则使用当前选择`<br>`    return model.FeatureManager.FeatureFillet(`<br>`        195, radius, 0, 0, None, None, None` | **C:\swapi\types\IFeatureManager\FeatureFillet.md**<br>「Before calling this method to create... Do this...」<br>「Simple fillets」<br>「1. Call [[IModelDocExtension::SelectByID2]] with **Mark = 1** to select the edges to fillet.」 | 官方要求被倒圆的边以 **Mark = 1** 进选择集；我们的 `fillet()` 自己不做选择、也**没有约定 mark**，`edges` 形参完全未被使用。 | 中 |
| 6 | **sw_part.py** `shell`（函数体内**无任何选择代码**，`faces_to_remove` 形参收了不用）：<br>`        faces_to_remove: 需预先选择要移除的面`<br>…<br>`    return model.InsertFeatureShell(thickness, False)` | **C:\swapi\types\IModelDoc2\InsertFeatureShell.md**<br>「Before calling this method, select faces to remove to create the shell using [[IModelDocExtension::SelectByID2]] with **Marks of 1**.」 | 同上：官方要求被移除的面按 **Marks of 1** 选；我们不选、也不约定 mark，参数未使用。 | 中 |

---

## 查不到（官方两套源都没有前置/mark 文字 ⇒ 按铁律不报）

- `IFeatureManager.InsertCosmeticThread3` —— `C:\swapi\types\IFeatureManager\InsertCosmeticThread3.md` **没有 `## Remarks` 段**；CHM `SolidWorks.Interop.sldworks~…IFeatureManager~InsertCosmeticThread3.html` 与 `SldWorks~FeatureManager~InsertCosmeticThread3.html` 两页**均无任何 mark / select / edge 字样** ⇒ `sw_feature_entry_ops.py` 里 `SP._select_com_object(edges[0], append=False, mark=0)` 的 mark=0 **无官方原文可比**，不报。
- `IFeatureManager.InsertRib` —— `C:\swapi\types\IFeatureManager\InsertRib.md` **没有 `## Remarks` 段** ⇒ `rib()` 的选区形态无官方前置可比，不报。
- `IFeatureManager.InsertFeatureChamfer` —— `…\InsertFeatureChamfer.md` 的 `## Remarks` 只讲三种倒角的几何，**没有选择/mark 前置** ⇒ `chamfer()` 的选区约定无官方原文可比，不报。
- `IModelDoc2.AddDimension2` —— `…\AddDimension2.md` 的前置只写「Before calling this method, you must select the entities for which to add a display dimension.」并把「按位置而非按名字」的建议**限定在**「if you are using IModelDocExtension::SelectByID2」；我们的 `add_dimension_report` 走 `resolve_selection` 按对象选 ⇒ 不构成对不上，不报。

## 核过但一致（不报，仅列出以便复核）

| 站点 | 我们的做法 | 官方对应原文 |
|---|---|---|
| `circular_pattern` | `mark=4` 选特征 → `append=True, mark=1` 选轴 | `FeatureCircularPattern4.md`「4 to mark the features to pattern」「1 to mark the direction axis」；`examples\Create_Circular_Pattern_Example_VB.md` 逐字「SelectByID2("Cut-Extrude1", "BODYFEATURE", …, False, 4, …)」「SelectByID2("", "EDGE", …, True, 1, …)」——顺序与 mark 都对得上 |
| `mirror_feature` | `mark=1` 特征 + `mark=2` 平面 | `InsertMirrorFeature2.md`「Features … 1」「Planes or planar faces … 2」 |
| `insert_dome` | 不自选，注释写明调用方须 `mark=1` | `IModelDoc2\InsertDome.md`「you must select the face for the dome using a selection mark of 1」 |
| `insert_composite_curve` | 不自选，注释写明调用方须 `mark=1` | `IModelDoc2\InsertCompositeCurve.md`「select the entities by calling [[IModelDocExtension::SelectByID2]] with a mark number of 1」 |
| `_select_revolve_axis` + `revolve_boss` docstring 里的「先轴后轮廓」 | 轴用 `mark=4` | `FeatureRevolve2.md`「the axis of revolution, using Mark = 4 or 16」；`examples\Create_360-degree_Revolve_Feature_Example_VBNET.md` 逐字先 `SelectByID2("Axis1", "AXIS", 0,0,0, False, 16, …)` 后 `SelectByID2("Sketch1", "SKETCH", 0,0,0, True, 0, …)` —— docstring 引用的顺序与原文一致（**顺序本身不构成分歧**；分歧只在第 1 条的选择集被清空） |
| `thicken_surface` | 参考面 `mark=1` | `FeatureBossThicken.md`「The surface must be selected with a mark of 1.」 |
| `create_flatten_surface` | 面 `mark=1` + 锚点 `mark=16` | `InsertFlattenSurface2.md`「Faces or surfaces to flatten … 1」「Anchor point from which to flatten … 16」「An anchor point can be a vertex or point on an edge.」 |
| `extrude_boss` / `extrude_cut` / `extrude_midplane` / `rib` | 轮廓走 `_ensure_sketch_selected`（mark=0） | `FeatureExtrusion3.md` 的 mark 表限定于「to extrude a **3D** sketch」；`FeatureCut4.md`、`InsertRib.md` 无前置 mark 文字 |

---

核了 25 处调用站点（sw_part.py 20 · sw_feature_entry_ops.py 3 · sw_feature_readback.py 2）· 报了 6 条 · 置信度为高的是 #1 #2 #3 #4
