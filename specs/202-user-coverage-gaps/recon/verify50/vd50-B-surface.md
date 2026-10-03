# vd50-B · surface · 「置信度＝高」条目双段原文复核

**范围**：`recon/audit-vs-official/` 下与 **surface** 有关的三个文件里，**置信度标「高」**的条目 ——
`audit-01-surface-A.md`（第 1、2 条为高；第 3、4 条为「中」**未核**）·
`audit-01-surface-B.md`（第 1、2、3 条为高；第 4 条为「中」**未核**）·
`audit-01-surface-C.md`（第 1、2、3 条**全部**为高）。
**共 8 条，一条不落。** 同一批条目的合并编号见 `AUDIT-INDEX.md` 的 **H01–H08**。
**只读核验**（未改仓内任何文件）；本文件是唯一写入。
**核了 8 处，对不上 1 处**（明确「不成立」0 处 · 「存疑」1 处）。

每条两问：**①「官方的原文」是否真的存在于 `C:\swapi\`**；**②「我们的原文」是否真的存在于 `D:\AI\SW\`**。两段均逐字给出，可直接 grep。

---

## 总表

| 条目 | 合并号 | 文件（仓内那一侧） | 官方原文在不在 | 我们的原文在不在 | 判定 |
|---|---|---|---|---|---|
| A-1 | H01 | `scripts/sw_surface.py` | ✅ 在 | ✅ 在 | **成立** |
| A-2 | H02 | `scripts/sw_surface.py` | ✅ 在 | ✅ 在 | **成立** |
| B-1 | H03 | `scripts/sw_surface_features.py` | ✅ 在 | ✅ 在 | **成立** |
| B-2 | H04 | `scripts/sw_surface_features.py` | ✅ 在 | ✅ 在 | **成立** |
| B-3 | H05 | `scripts/sw_surface_features.py` | ✅ 在 | ✅ 在 | **成立**（★ 作用域限该文件，见该条附注） |
| C-1 | H06 | `scripts/sw_surface.py` | ✅ 在 ×4 | ✅ 在 | **成立** |
| C-2 | H07 | `scripts/sw_surface_features.py` | ✅ 在 | ✅ 在 | **成立** |
| C-3 | H08 | `scripts/sw_surface_edit_ops.py` | ✅ 在 | ✅ 在 | **存疑**（官方两源自相矛盾） |

> **8 条里 7 条的「两段原文」都能逐字 grep 到，1 条（C-3）原文全在但分歧不成立为缺陷。**
> ★ **没有任何一条出现「用相似名字顶替」的情况** —— 8 条点名的官方文件全部真实存在（逐一 `read` 过）。

---

## A-1（H01）· `CreateConicalSurface` 第 3/4 位两个 double 顺序反了

**判定：成立** —— 官方第 3 位是 `Radius`、第 4 位是 `SemiAngle`，我们第 3 位传的是半角、第 4 位传的是半径。

**官方那一段** —— `C:\swapi\types\IModeler\CreateConicalSurface.md`：
```
**Signature**: `System.object CreateConicalSurface( System.object Center, System.object Direction, System.double Radius, System.double SemiAngle )`
```
其 `## Parameters` 逐字为：
```
- **Radius**: No description
- **SemiAngle**: No description
```

**仓内那一段** —— `scripts/sw_surface.py`，`create_conical_surface`：
```python
def create_conical_surface(sw_app, origin, axis, half_angle, radius):
    """由原点 + 轴 + 半角 + 半径创建圆锥面。``(Object, Object, Double, Double)``"""
    require_runtime_available("CreateConicalSurface")
    return _invoke(
        get_modeler(sw_app), "CreateConicalSurface",
        origin, axis, float(half_angle), float(radius),
    )
```

**一句话依据**：形参表第 3 位 `Radius`、第 4 位 `SemiAngle`，而实参第 3 位是 `float(half_angle)`、第 4 位是 `float(radius)` —— 两个 double 的先后与官方相反。

---

## A-2（H02）· `CreateBsplineSurface` 四个 object 顺序反了

**判定：成立** —— 官方第 1 位是 `Props`、第 4 位才是 `CtrlPtCoords`，我们第 1 位传控制点、第 4 位传次数。

**官方那一段** —— `C:\swapi\types\IModeler\CreateBsplineSurface.md`：
```
**Signature**: `System.object CreateBsplineSurface( System.object Props, System.object UKnots, System.object VKnots, System.object CtrlPtCoords )`
```
其 `## Parameters` 逐字为：
```
- **Props**: Array containing 8 integers packed as 4 double elements (see **Remarks**)
- **UKnots**: Array of numUKnots (see **Remarks**)
- **VKnots**: Array of numVKnots (see **Remarks**)
- **CtrlPtCoords**: Array of numCtrlPtCoord (see **Remarks**)
```

**仓内那一段** —— `scripts/sw_surface.py`，`create_bspline_surface`：
```python
def create_bspline_surface(sw_app, control_points, weights, knots, degree):
    """由控制点 / 权重 / 节点 / 次数创建 B 样条曲面。``(Object, Object, Object, Object)``"""
    require_runtime_available("CreateBsplineSurface")
    return _invoke(
        get_modeler(sw_app), "CreateBsplineSurface",
        control_points, weights, knots, degree,
    )
```

**一句话依据**：官方第 1 位 `Props`（8 个整数打包成 4 个 double 的数组）与第 4 位 `CtrlPtCoords`（控制点坐标数组），在我们这里被 `control_points` 与 `degree` 占住 —— 四个 object 的对应关系整体错位。

---

## B-1（H03）· 剪裁曲面的调用序：官方是「Pre → 选 → Post」，我们是「选 → Pre → Post」

**判定：成立** —— 官方两页的 Remarks **都**把「选剪裁面」写在 `PreTrimSurface` **之后**，官方例子也是这个序；我们的两步之间没有任何再选择。

**官方那一段** —— `C:\swapi\types\IFeatureManager\PostTrimSurface.md` 的 `## Remarks`：
```
Before calling this method:

1. Call [[IFeatureManager::PreTrimSurface]].

2. Select the trimming surfaces or trim tool.

3. Optionally, call [[IFeatureManager::SolidForTrim]].
```
`C:\swapi\types\IFeatureManager\PreTrimSurface.md` 的 `## Remarks`：
```
After calling this method:

1. Select the trimming surfaces or trim tool.

2. Optionally, call [[IFeatureManager::SolidForTrim]].

3. Call [[IFeatureManager::PostTrimSurface]].
```
`C:\swapi\examples\Create_Trimmed_Surface_Feature_Example_CSharp.md` 逐字三连（**中间夹着一次选择**）：
```
            status = swFeatureMgr.PreTrimSurface(false, true, false, false);
            // Trim the surface
            status = swModelDocExt.SelectByID2("", "SURFACEBODY", 0.0289416986472588, 0.00781827749557351, 0.0290635845400971, true, 0, null, 0);
            swFeat = (Feature)swFeatureMgr.PostTrimSurface(true);
```

**仓内那一段** —— `scripts/sw_surface_features.py`，剪裁曲面包装（`_select_all_surface_faces` 之后**直接**调 `PreTrimSurface`，再**直接**调 `PostTrimSurface`，中间只有 `try/except`、无任何选择）：
```python
    selected = _select_all_surface_faces(model, mark=0)
    ...
        pre = get_com_member(fm, "PreTrimSurface", bool(mutual), bool(split_system),
                             bool(split_linear), bool(remove_picked))
    ...
        post = get_com_member(fm, "PostTrimSurface", bool(sew))
```
该函数 docstring 自述的前置是：
```
    ★ 前置：★ **先选中「要剪裁的面」与「剪裁工具」**（★ 本包装按对象选 —— ★ 事实 32：
      实体没有名字）。
```

**一句话依据**：官方 `Remarks` 与官方例子都要求 `PreTrimSurface` 之后、`PostTrimSurface` 之前**再选一次**，而我们的代码在 `PreTrimSurface` 之前就选完、之后不再选 —— 顺序与官方相反。

---

## B-2（H04）· `FeatureExtruRefSurface3` 缺「调用前先选择」这条前置

**判定：成立** —— 官方 `Remarks` 点名 `SelectByID2` 且给了 mark 表；我们的包装整个函数体没有任何选择动作，`sketch_name` 只出现在返回字典里。

**官方那一段** —— `C:\swapi\types\IFeatureManager\FeatureExtruRefSurface3.md` 的 `## Remarks`：
```
Before calling this method, select the entities for the extruded surface using [[IModelDocExtension::SelectByID2]].
```
紧随其后的 mark 表逐字为：
```
Base

- 2D or 3D sketch

- Sketch segments

- Single planar face

- Multiple co-planar faces

- 0

- 0 or 4

- 0

- 0 for first planar face and 256 for all other co-planar faces
```

**仓内那一段** —— `scripts/sw_surface_features.py`，`create_extruded_surface_report`（函数体自 `if model is None:` 到 `return {…}`，**无** `SelectByID2`、**无** `_select_all_surface_faces`）：
```python
    fm = get_com_member(model, "FeatureManager")
    get_com_member(fm, "FeatureExtruRefSurface3", *args)
```
`sketch_name` 在整个文件里的落点只有返回值那一处：
```python
            "through_all": bool(through_all), "sketch_name": str(sketch_name),
```

**一句话依据**：官方要求调用前用 `SelectByID2` 选出被拉伸的实体（草图/草图段/平面 0），我们的包装从头到尾不做任何选择，形参 `sketch_name` 只被原样回显进返回值、没有任何取草图的动作。

---

## B-3（H05）· `FeatureBossThicken` 缺「参考曲面按 mark=1 选中」这条前置

**判定：成立**（★ **作用域限本文件**，见下方附注）—— 官方 `Remarks` 要求参考曲面以 mark=1 选中；本包装调用前无任何选择，docstring 把前置写成「文件里要有曲面体」。

**官方那一段** —— `C:\swapi\types\IFeatureManager\FeatureBossThicken.md` 的 `## Remarks`：
```
This method generates a boss feature by thickening a selected reference surface.  The surface must be selected with a mark of 1. See [[IModelDocExtension::SelectByID2]] for details.
```
以及同页：
```
If UseAutoSelect is false, the user must select the bodies that the feature will affect.
```

**仓内那一段** —— `scripts/sw_surface_features.py`，加厚包装的 docstring 前置：
```
    ★ 前置：★ **文件里要有曲面体**（★ 与 `knit_surfaces_report` 同款前置 ——
      ★ 而 `use_auto_select=True` 时官方会"自动选所有体"）。
```
调用点（其上只有 `model is None` 判断、`thickness_mm` 校验、`feature_names` / `_solid_body_count` / `_surface_body_count` 三个记账，**无任何选择动作**）：
```python
        feat = get_com_member(fm, "FeatureBossThicken",
                              th * 0.001, int(direction), 0,
                              bool(fill_volume), bool(merge),
                              bool(use_feat_scope), bool(use_auto_select))
```

> ★★ **附注（★ 必须一并记下，否则这条会被读大）**：同一个官方成员，**仓内另有一个包装确实做对了 mark=1** ——
> `scripts/sw_feature_entry_ops.py` 的 `thicken_surface`（返回值 `"op": "thicken_surface"`）里逐字写着：
> ```python
>         if not SP._select_com_object(face, append=False, mark=1):
>             out["ok"] = False
>             out["preconditions_held"] = False
>             out["error"] = "★ 前置未成立：参考面**没按 `mark=1` 选上**"
> ```
> ⇒ **所以这不是「仓内没有这条前置」，而是「两个包装对同一个官方成员做法不一致」**，
> 且 `sw_surface_features.py` 那个包装的 docstring 已自记「11 组参数全回 `None`、静默不成」「按 A4 不登记成工具」。
> ★ 这与 `AUDIT-INDEX.md` 的 H05 旁注「与 06-B 的 `thicken_surface` 结论相反」**吻合** —— 两路说的不是同一处代码。

**一句话依据**：官方逐字要求「参考曲面必须以 mark of 1 选中」，而 `sw_surface_features.py` 这个包装在调用前没有任何选择、docstring 把前置降级成「文件里要有曲面体」。

---

## C-1（H06）· 四个薄封装调用的成员**全部**带官方 `Obsolete`，且后继 `…2` 只登记不调用

**判定：成立** —— 四页官方文档**逐个**写着 `Obsolete. Superseded by [[IModeler::Create*Surface2]].`；我们的四个薄封装调的都是被标废弃的那一代，而同文件的签名表里登记的四个 `…2` **一个都没被任何封装调用**。

**官方那一段** —— 四页 `C:\swapi\types\IModeler\` 下逐字（各自正文第 12 行）：
```
# IModeler.CreatePlanarSurface
Obsolete. Superseded by [[IModeler::CreatePlanarSurface2]].
```
```
# IModeler.CreateCylindricalSurface
Obsolete. Superseded by [[IModeler::CreateCylindricalSurface2]].
```
```
# IModeler.CreateSphericalSurface
Obsolete. Superseded by [[IModeler::CreateSphericalSurface2]].
```
```
# IModeler.CreateConicalSurface
Obsolete. Superseded by [[IModeler::CreateConicalSurface2]].
```

**仓内那一段** —— `scripts/sw_surface.py`，四个薄封装（各带同名守卫）：
```python
    require_runtime_available("CreatePlanarSurface")
    return _invoke(get_modeler(sw_app), "CreatePlanarSurface", point, normal)
```
```python
    require_runtime_available("CreateCylindricalSurface")
    return _invoke(
        get_modeler(sw_app), "CreateCylindricalSurface", origin, axis, float(radius)
    )
```
```python
    require_runtime_available("CreateSphericalSurface")
    return _invoke(get_modeler(sw_app), "CreateSphericalSurface", center, float(radius))
```
```python
    require_runtime_available("CreateConicalSurface")
    return _invoke(
        get_modeler(sw_app), "CreateConicalSurface",
        origin, axis, float(half_angle), float(radius),
    )
```
同文件的 `SURFACE_CREATION_METHODS` 里四个后继确实**只作为字典项存在**（全仓 grep `"CreatePlanarSurface2"` 等四个名字，命中处**全部**在这张表里，**无一处**作为 `_invoke` 的方法名出现）：
```python
    "CreatePlanarSurface2": ("Object", ("Object", "Object", "Object")),
    "CreateCylindricalSurface2": ("Object", ("Object", "Object", "Object", "Double")),
    "CreateSphericalSurface2": ("Object", ("Object", "Object", "Object", "Double")),
    "CreateConicalSurface2": ("Object", ("Object", "Object", "Object", "Double", "Double")),
```

**一句话依据**：四个被调成员官方逐个标了 `Obsolete` 并点名 `…2` 为后继，而我们同文件已把四个 `…2` 登记进签名表却没有任何封装真的调它们 —— 被调用的一代与官方指定的后继一代不一致。

---

## C-2（H07）· `InsertExtendSurface` 的 `EndCondition` 把官方合法的 `2` 当成非法

**判定：成立** —— 官方成员页的参数表列了三个值、官方枚举页列了三个成员（含值 2）；我们的包装只收 `{0,1}` 并**显式报错拒绝** 2。

**官方那一段** —— `C:\swapi\types\IModelDoc2\InsertExtendSurface.md` 的 `## Parameters`：
```
- **EndCondition**:
  - 0 - Extend surface by given distance

  - 1 - Extend surface up to a selected point

  - 2 - Extend surface up to a selected surface
```
`C:\swapi\enums\swSurfaceExtendEndCond_e.md`（头部 `enum_member_count: 3`，成员表逐字）：
```
| swSurfaceExtendEndCondDistance | 0 |
| swSurfaceExtendEndCondUpToPoint | 1 |
| swSurfaceExtendEndCondUpToSurface | 2 |
```

**仓内那一段** —— `scripts/sw_surface_features.py`，延伸曲面包装：
```python
    :param end_condition: **0 = 按距离**（默认）· **1 = 延伸到选定点**。
```
```python
    if int(end_condition) not in (0, 1):
        return {"ok": False, "error": "end_condition 只支持 0（按距离）/ 1（到选定点）：%r" % end_condition}
```

**一句话依据**：官方参数表与官方枚举都把 `2`（延伸到选中的曲面）列为合法成员，而我们的守卫 `not in (0, 1)` 会把它当非法直接返回错误 —— 一个官方合法值在本包装里走不通。

---

## C-3（H08）· `RULED_TYPE_MEANINGS` 用 0..4，官方枚举页是 1..5

**判定：存疑（不判谁对）** —— ★ **两段原文全部逐字存在**，但**官方自己两个源互相矛盾**：成员页参数表确实是 0-based、而枚举页是 1..5；我们的注释引的正是成员页、且**引对了**。★ 唯一坐实的是**同仓自相矛盾**（同一个官方成员，两个包装用了不同的取值域）。

**官方那一段（枚举页）** —— `C:\swapi\enums\swRuledSurfaceType_e.md`（头部 `enum_member_count: 5`，成员表逐字，**没有值为 0 的成员**）：
```
| swRuledSurfaceType_NormalToSurface | 2 |
| swRuledSurfaceType_PerpendicularToVector | 4 |
| swRuledSurfaceType_Sweep | 5 |
| swRuledSurfaceType_TangentToSurface | 1 |
| swRuledSurfaceType_TaperedToVector | 3 |
```
**官方那一段（成员页，与上段互相矛盾）** —— `C:\swapi\types\IFeatureManager\InsertRuledSurfaceFromEdge2.md` 的 `## Parameters`：
```
- **Type**:
  - 0 = Tangent to Surface

  - 1 = Normal to Surface

  - 2 = Tapered to Vector

  - 3 = Perpendicular to Vector

  - 4 = Sweep
```
★ 该页**通篇没有**把 `Type` 指向 `swRuledSurfaceType_e` 的任何链接（已通读全页确认）。

**仓内那一段** —— `scripts/sw_surface_edit_ops.py`：
```python
#: ★ 官方给的 `Type` 取值表（★ 逐字来自 `InsertRuledSurfaceFromEdge2.md` 的 Parameters）
RULED_TYPE_MEANINGS = {
    0: "Tangent to Surface",
    1: "Normal to Surface",
    2: "Tapered to Vector",
    3: "Perpendicular to Vector",
    4: "Sweep",
}
```
门禁与回显（同文件）：
```python
    if int(ruled_type) not in RULED_TYPE_MEANINGS:
        return {"ok": False, "error": "ruled_type 不在官方取值表 0..4 内：%r（表：%s）"
```
```python
            "type": int(ruled_type), "type_meaning": RULED_TYPE_MEANINGS[int(ruled_type)],
```

★ **同仓自相矛盾的另一半（这条是坐实的）** —— `scripts/sw_surface_features.py` 对**同一个官方成员**用的是 1..5，且 docstring 明写这是按铁律 4「以出厂类型库为准」的选择：
```python
    if not (1 <= t <= 5):
        return {"ok": False, "stage": "validate",
                "error": "surface_type 必须 **1..5**（★ 出厂类型库口径：1=TangentToSurface … 5=Sweep）；"
                         "★ 而官方 md 的参数表是 0-based ⇒ ★ 别照它填" }
```
其 docstring 把两源冲突逐字记了下来：
```
#   ⇒ ★★ **铁律 4 说：冲突以出厂类型库为准** ⇒ ★ 本包装**收枚举值 1..5**，
```

**一句话依据**：两个官方源对同一个 `Type` 参数给出 1..5 与 0..4 两套取值，我们两个包装各采一套 —— 所以「我们表里的 `0` 不是合法成员」只在枚举页口径下成立，**分歧本身判不了**；能坐实的只有**同仓两个包装对同一成员用了不同取值域**这一条。

---

## 查不到的（按铁律 5，如实记，不拿相似名字顶替）

- `audit-01-surface-A.md` 的「查不到」段与 `audit-01-surface-B.md` 的附注都提到同一个事实：
  `sw_surface.py` 的 `create_revolution_surface` 包装了 `"CreateRevolutionSurface"`，
  但 `C:\swapi\types\IModeler\` 下**没有** `CreateRevolutionSurface.md`。
  ★ 我复核时同样**只找到 `CreateExtrusionSurface.md` 等同族页、没有这一份** ⇒
  **与两份核对表所记一致**：此处**无法与官方 `**Signature**` 并排数**，**本轮不据此报任何条**。
  （★ 注意 `SURFACE_CREATION_METHODS` 里确实登记了 `CreateRevolutionSurface`，但那是我们自己的表、不是官方文档，故不拿它当「官方原文」。）

---

## 口径与纪律自述

- ★ **只读**：全程未改仓内任何文件；本文件是本次唯一写入。
- ★ **两段原文**：8 条**每条都给了**「官方那一段」+「仓内那一段」，全部为可直接 grep 的逐字片段；**没有一条**以「看起来可能有问题」「建议检查」充数。
- ★ **不写行号**：只给原文片段。
- ★ **查不到就说查不到**：见上一节（`CreateRevolutionSurface`）。
- ★ **宁少勿滥**：只报本域「置信度＝高」的 8 条；A 的第 3、4 条与 B 的第 4 条（中置信）**一律未核、未写**。
- ★ **交叉查证**：C-3 额外核了同仓另一包装的 1..5 口径；B-3 额外核了 `sw_feature_entry_ops.py` 里确实做了 mark=1 的那一处 —— 两条都写进正文，避免把结论读大。

## 结尾三行

- 核了 **8 处**（surface 域「置信度＝高」的全部条目：A 2 条 · B 3 条 · C 3 条）。
- **对不上 1 处** —— C-3（H08）：两段原文都在，但官方成员页与官方枚举页**互相矛盾**，分歧判不了，判**存疑**。
- 明确「**不成立**」的：**0 处**。