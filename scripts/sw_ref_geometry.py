"""★ B8 参考几何体（4 条）+ T701 边界框：基准面 / 坐标系 / 点 / 质心 / 边界框。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_ref_geometry.py
# 定位:   ★ 2026-10-03（轮 479）★ 承 `specs/201-toolbar-gaps` 的 **B8**（参考几何体 4 条）
#   与 **T701**（边界框）。用户工具栏里判「不能」的那些，本模块收这 5 条。
#
#   ==================  ==================================================  ==================
#   工具栏原文           官方成员                                             判据
#   ==================  ==================================================  ==================
#   基准面               `IFeatureManager.InsertRefPlane`（6 参）→ object      回非 None + 树增量
#   坐标系               `IFeatureManager.InsertCoordinateSystem`（3 参）→ Feature  同
#   点                   `IFeatureManager.InsertReferencePoint`（4 参）→ object  同
#   质心                 `IFeatureManager.InsertCenterOfMass()` → Feature        同
#   边界框               `IModelDocExtension.Create3DBoundingBox()` → void       **只有树增量**
#   ==================  ==================================================  ==================
#
#   ★★ **代际**（★ 铁律 4：以后继版为准）：
#     `IModelDoc2.InsertCoordinateSystem` **官方标 Obsolete**：
#     > Obsolete. Superseded by [[IFeatureManager::InsertCoordinateSystem]].
#     ⇒ ★ 本模块用 **`IFeatureManager` 那个**（★ 且它回 `Feature`，★ 比旧版的 `bool` 信息多）✓
#
#   ★★★ **三张枚举表**（★ 全部从官方 swapi 的 `enums/` 取，**不凭记忆**）：
#     · `swRefPlaneReferenceConstraints_e`：
#       `Parallel=1 · Coincident=4 · Distance=8 · Angle=16 · MidPlane=128`
#       （另有 Option* 位：`OptionFlip=256 · OptionOriginOnCurve=512 ·
#         OptionProjectToNearestLocation=1028 · OptionProjectAlongSketchNormal=2056 ·
#         OptionReferenceFlip=8192`）
#     · `swRefPointType_e`：`Invalid=0 · Undefined=1 · AlongCurve=2 · CenterEdge=3 ·
#       FaceCenter=4 · FaceVertexProjection=5 · Intersection=6 · SketchPoint=7`
#     · `swRefPointAlongCurveType_e`：`Distance=0 · Percentage=1 · EvenlyDistributed=2`
#
#   ★★ **两条官方 Remarks 的硬约束**（★ 逐字）：
#     · 基准面：「Before calling this method, you must have selected the reference entities
#       using these **marks** with `IModelDocExtension::SelectByID2`」
#       ⇒ ★ **调用前要按 mark 选好参考实体**（★ 铁律 3 第三句）。
#     · 点：「The **NumberOfRefPoints** argument **must contain a value of 1** to successfully
#       create one reference point feature.」⇒ ★ 本模块**默认 1**，且**拒绝其它值** ✓
#
# 官方依据（三源）:
#   · `C:\swapi\types\IFeatureManager\InsertRefPlane.md`（6 参 · mark 的 Remarks）
#   · `C:\swapi\types\IFeatureManager\InsertCoordinateSystem.md`（3 参 → Feature）
#   · `C:\swapi\types\IModelDoc2\InsertCoordinateSystem.md`（★ **Obsolete** 那一行）
#   · `C:\swapi\types\IFeatureManager\InsertReferencePoint.md`（4 参 · NumberOfRefPoints=1）
#   · `C:\swapi\types\IFeatureManager\InsertCenterOfMass.md`（`Feature ()`）
#   · `C:\swapi\types\IModelDocExtension\Create3DBoundingBox.md`（`void ()`）
#   · `C:\swapi\enums\swRefPlaneReferenceConstraints_e.md` / `swRefPointType_e.md` /
#     `swRefPointAlongCurveType_e.md`（★ 三张取值表）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件（★ 逐函数另有来源块）。
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 每个函数回 `{"ok": …, "verified_by": …}`；★ 判据 = **回对象非 None** + **特征树增量**
#   （★ 事实 8：COM 返回值单独不可信；★ 规则 6：不静默成功）。
#   ★★ 树增量**必须**走 `sw_part.feature_names`（★ 轮 473 的教训：自己拼的那条路真机回 None）。

from __future__ import annotations

try:
    from .sw_connect import get_com_member, set_com_member          # noqa: F401
except ImportError:                                                 # 顶层载入（脚本 / 探针）
    from sw_connect import get_com_member, set_com_member           # noqa: F401

__all__ = [
    "insert_ref_plane",
    "insert_coordinate_system",
    "insert_reference_point",
    "insert_center_of_mass",
    "create_3d_bounding_box",
    "insert_global_bounding_box",
    "REF_PLANE_CONSTRAINTS",
    "REF_POINT_TYPES",
    "REF_POINT_ALONG_CURVE_TYPES",
    "GLOBAL_BBOX_FIT_OPTIONS",
    "GLOBAL_BBOX_RESULT",
    "REF_GEOMETRY_STATUS",
]

#: ★ 官方 `swRefPlaneReferenceConstraints_e`（★ 逐字抄自 `C:\swapi\enums\`）
REF_PLANE_CONSTRAINTS = {
    "Parallel": 1, "Coincident": 4, "Distance": 8, "Angle": 16, "MidPlane": 128,
    "OptionFlip": 256, "OptionOriginOnCurve": 512,
    "OptionProjectToNearestLocation": 1028, "OptionProjectAlongSketchNormal": 2056,
    "OptionReferenceFlip": 8192,
}

#: ★ 官方 `swRefPointType_e`
REF_POINT_TYPES = {
    "Invalid": 0, "Undefined": 1, "AlongCurve": 2, "CenterEdge": 3,
    "FaceCenter": 4, "FaceVertexProjection": 5, "Intersection": 6, "SketchPoint": 7,
}

#: ★ 官方 `swRefPointAlongCurveType_e`
REF_POINT_ALONG_CURVE_TYPES = {"Distance": 0, "Percentage": 1, "EvenlyDistributed": 2}

#: ★ 官方 `swGlobalBoundingBoxFitOptions_e`（★ 逐字抄自 `C:\swapi\enums\`）
GLOBAL_BBOX_FIT_OPTIONS = {"BestFit": 1, "CustomPlane": 2, "CustomCoordSys": 3}

#: ★ 官方 `swGlobalBoundingBoxResult_e` —— ★ **`Success = 0`**（★ 本模块据此判成败）
GLOBAL_BBOX_RESULT = {
    "Success": 0, "NoValidBodiesFound": 1, "NonPlanarFaceSelected": 2,
}

#: ★ 本模块覆盖到的工具栏项 ⇒ 官方成员（★ 与 `docs/toolbar-ledger.json` 对齐用）
REF_GEOMETRY_STATUS = {
    "基准面": "IFeatureManager.InsertRefPlane",
    "坐标系": "IFeatureManager.InsertCoordinateSystem",
    "点": "IFeatureManager.InsertReferencePoint",
    "质心": "IFeatureManager.InsertCenterOfMass",
    "边界框": "IModelDocExtension.Create3DBoundingBox",
}


def _tree_names(model):
    """★ 特征树的**有序特征名清单**（★ 判据用）。

    ★★ **必须用本仓已验证的 `sw_part.feature_names`** —— ⚠ 轮 473 我自己拼过一条
      （`GetFeatureCount(True)` + `FeatureByPositionReverse(i)`），★ **真机上回 `None`**
      ⇒ 5 条能力**全被记成"不能"**，★ 而那是**判据坏了**、不是能力不行。
    """
    try:
        from .sw_part import feature_names as _fn
    except ImportError:
        from sw_part import feature_names as _fn
    try:
        return list(_fn(model) or [])
    except Exception:                                                # noqa: BLE001
        return None


def _delta(before, after):
    """★ 新增的特征名（★ `None` 表示量不到 ⇒ 判据降级，★ 不猜）。"""
    if before is None or after is None:
        return None
    return [x for x in after if x not in before]


def _judge(model, r, op):
    """★ 统一判据：**回对象非 None** **且** **特征树有新特征**（★ 两判据都要）。"""
    after = _tree_names(model)
    added = _delta(r.pop("_before", None), after)
    r.update({"op": op, "tree_after": after, "new_features": added,
              "ok": bool(r.get("returned_is_none") is False and added),
              "verified_by": "returned_object + tree_delta"})
    return r


def insert_ref_plane(model, first_constraint: int, first_angle_or_dist: float = 0.0,
                     second_constraint: int = 0, second_angle_or_dist: float = 0.0,
                     third_constraint: int = 0, third_angle_or_dist: float = 0.0) -> dict:
    """★ **基准面**：`IFeatureManager.InsertRefPlane(6 参)` → object（回 [[Reference plane]]）。

    ★ 官方原话：「Inserts a **constraint-based reference plane** using the **selected reference
      entities**.」

    :param first_constraint / second_ / third_: 取值见 `REF_PLANE_CONSTRAINTS`
      （★ 拷自官方 `swRefPlaneReferenceConstraints_e`）。
    :param *_angle_or_dist: 对应约束的角度**或**距离。⚠ ★ 本模块**不做单位换算** ——
      ★ 官方只说 "Angle or distance of the … constraint"，★ **没说单位** ⇒
      ★ 故按**文档原样**透传，并把这一点写进返回值（★ 铁律 5：查不到就不编）。

    ⚠ **调用前要按 mark 选好参考实体**（★ 官方 Remarks 逐字："you must have selected the
      reference entities using these **marks** with `IModelDocExtension::SelectByID2`"）。
      ★★ 而官方**没给出 mark 的取值表**（★ 只说"these marks"）⇒ ★ 本模块**不假定 mark**，
        ★ 如实写进返回值 ✓

    ★ 判据 = **回对象非 None** **且** **特征树有新特征**。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    fm = get_com_member(model, "FeatureManager")
    if fm is None:
        return {"ok": False, "error": "取不到 FeatureManager"}
    before = _tree_names(model)
    obj = get_com_member(fm, "InsertRefPlane",
                         int(first_constraint), float(first_angle_or_dist),
                         int(second_constraint), float(second_angle_or_dist),
                         int(third_constraint), float(third_angle_or_dist))
    return _judge(model, {"_before": before, "returned_is_none": obj is None,
                          "constraints": [int(first_constraint), int(second_constraint),
                                          int(third_constraint)],
                          "angle_or_dist_unit": "★ 官方未给单位 —— 按文档原样透传，本模块不换算",
                          "selection_mark": "★ 官方 Remarks 只说「these marks」、**未给取值表** ⇒ 不假定"},
                  "ref_plane")


def insert_coordinate_system(model, x_flipped: bool = False, y_flipped: bool = False,
                             z_flipped: bool = False) -> dict:
    """★ **坐标系**：`IFeatureManager.InsertCoordinateSystem(3 参)` → `Feature`。

    ★★ **用的是 `IFeatureManager` 那个，不是 `IModelDoc2` 那个**（★ 铁律 4）——
      `IModelDoc2.InsertCoordinateSystem` 官方标 **Obsolete**：
      > Obsolete. Superseded by [[IFeatureManager::InsertCoordinateSystem]].
      ★ 且旧版回 `bool`、新版回 **`Feature`** ⇒ ★ 新版判据更强 ✓

    :param x_flipped / y_flipped / z_flipped: 各轴是否翻转（★ 官方形参名 `XFlippedIn` 等）。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    fm = get_com_member(model, "FeatureManager")
    if fm is None:
        return {"ok": False, "error": "取不到 FeatureManager"}
    before = _tree_names(model)
    feat = get_com_member(fm, "InsertCoordinateSystem",
                          bool(x_flipped), bool(y_flipped), bool(z_flipped))
    return _judge(model, {"_before": before, "returned_is_none": feat is None,
                          "flipped": [bool(x_flipped), bool(y_flipped), bool(z_flipped)]},
                  "coordinate_system")


def insert_reference_point(model, ref_point_type: int, along_curve_type: int = 0,
                           distance_or_percent: float = 0.0,
                           number_of_ref_points: int = 1) -> dict:
    """★ **点**：`IFeatureManager.InsertReferencePoint(4 参)` → object。

    :param ref_point_type: 取值见 `REF_POINT_TYPES`（★ 官方 `swRefPointType_e`）。
    :param along_curve_type: 取值见 `REF_POINT_ALONG_CURVE_TYPES`（★ 官方 `swRefPointAlongCurveType_e`）。
    :param distance_or_percent: 沿曲线的距离或百分比（★ 官方原文 "Distance at which … or percentage of…"）。
    :param number_of_ref_points: ★★ 官方 Remarks 逐字：
      「The **NumberOfRefPoints** argument **must contain a value of 1** to successfully create
        one reference point feature.」⇒ ★ 本模块**拒绝非 1**（★ 而不是把它悄悄传下去）。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    if int(number_of_ref_points) != 1:
        return {"ok": False, "error": "官方 Remarks：NumberOfRefPoints **必须是 1**，收到 %r"
                % number_of_ref_points}
    if int(ref_point_type) not in set(REF_POINT_TYPES.values()):
        return {"ok": False, "error": "ref_point_type 不在 swRefPointType_e 的取值表内：%r（表：%s）"
                % (ref_point_type, REF_POINT_TYPES)}
    if int(along_curve_type) not in set(REF_POINT_ALONG_CURVE_TYPES.values()):
        return {"ok": False, "error": "along_curve_type 不在 swRefPointAlongCurveType_e 内：%r（表：%s）"
                % (along_curve_type, REF_POINT_ALONG_CURVE_TYPES)}
    fm = get_com_member(model, "FeatureManager")
    if fm is None:
        return {"ok": False, "error": "取不到 FeatureManager"}
    before = _tree_names(model)
    obj = get_com_member(fm, "InsertReferencePoint",
                         int(ref_point_type), int(along_curve_type),
                         float(distance_or_percent), 1)
    return _judge(model, {"_before": before, "returned_is_none": obj is None,
                          "ref_point_type": int(ref_point_type),
                          "along_curve_type": int(along_curve_type)},
                  "reference_point")


def insert_center_of_mass(model) -> dict:
    """★ **质心**：`IFeatureManager.InsertCenterOfMass()` → `Feature` —— ★ **零参数**。"""
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    fm = get_com_member(model, "FeatureManager")
    if fm is None:
        return {"ok": False, "error": "取不到 FeatureManager"}
    before = _tree_names(model)
    feat = get_com_member(fm, "InsertCenterOfMass")
    return _judge(model, {"_before": before, "returned_is_none": feat is None},
                  "center_of_mass")


def create_3d_bounding_box(model) -> dict:
    """★ **3D 边界框（焊件切割清单用）**：`IModelDocExtension.Create3DBoundingBox()` → `void`。

    ★★★ 2026-10-03（轮 479）**这条的语义要写清楚，★ 否则会被误当"工具栏的边界框"** ——
      官方原话逐字：
      > Creates a 3D bounding box for a **cut list item in a weldment part**.
      ⇒ ★★ **它只对「焊件零件的切割清单项」有意义**。
      ★ 真机实测（★ 普通零件 + 一个拉伸实体 + 选中一个面）：**树无增量** ——
        ★ 那是**应然的**（★ 这台机器上的文档不是焊件、也没有切割清单项）✓
      ⇒ ★★ ★ **工具栏「边界框」对应的其实是 `insert_global_bounding_box`**（见下一个函数）✓

    ⚠ ★ 官方另注：调用后选中项的类型是 `swSelSKETCH`（★ 它建出来的是**草图**）——
      ⇒ ★ 若真要判它成没成，★ 判据该是"选中了一个 sketch"，★ 而**不是**顶层特征树增量。
    ⚠ ★ 官方回 `void` ⇒ 本函数**只能**给树增量判据（★ 并如实标 `verified_by`）。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    ext = get_com_member(model, "Extension")
    if ext is None:
        return {"ok": False, "error": "取不到 model.Extension"}
    before = _tree_names(model)
    get_com_member(ext, "Create3DBoundingBox")
    r = _judge(model, {"_before": before, "returned_is_none": False}, "bounding_box")
    r["verified_by"] = "tree_delta"        # ★ 官方回 void ⇒ 判据只有树增量
    r["scope"] = "★ 官方：**焊件零件的切割清单项**专用 —— 普通零件上不成是应然的"
    return r


def insert_global_bounding_box(model, bbox_type: int = 1, lwta_direction_type: int = 0,
                               include_hidden_bodies: bool = False,
                               include_surface_bodies: bool = False) -> dict:
    """★ **边界框（普通零件/装配体）**：`IFeatureManager.InsertGlobalBoundingBox2(…)` → `IFeature`。

    ★★ 这才是工具栏「边界框」对应的官方成员（★ 台账 T701 给的 `Create3DBoundingBox`
      是**焊件切割清单**专用的另一个，★ 见上一个函数的说明）。

    :param bbox_type: 官方 `swGlobalBoundingBoxFitOptions_e`：
      `BestFit=1 · CustomPlane=2 · CustomCoordSys=3`（★ 默认 1 = BestFit）。
      ⚠ 官方 Remarks：「If `BBoxType` is `swBoundingBoxType_CustomPlane`, then **select a face
        or plane** using …」⇒ ★ **只有 `CustomPlane`(2) 才要先选面** ✓
    :param lwta_direction_type: 官方 `swGlobalBBoxLWTADirectionType_e`
      （`Unspecified=0 · LWTDir_XYZ=1 · YXZ=2 · YZX=3 · XZY=6 · AxisDir_X=7/8/9`）。
    :param include_hidden_bodies / include_surface_bodies: 是否含隐藏体 / 曲面体。

    ★ 官方签名第 5 个形参 `Status` 是 **out**（`swGlobalBoundingBoxResult_e`，**`Success=0`**）
      ⇒ ★ 本函数**同时收**返回值与 out（★ 若 pywin32 把它并进返回元组，就取出来一起报）。
    ★ 判据 = **回 `IFeature` 非 None** **且** **特征树有新特征**；
      ★ 并**额外报出 `Status`**（★ 那是官方给的成败码，★ 有就以它为准）。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    if int(bbox_type) not in set(GLOBAL_BBOX_FIT_OPTIONS.values()):
        return {"ok": False, "error": "bbox_type 不在 swGlobalBoundingBoxFitOptions_e 内：%r（表：%s）"
                % (bbox_type, GLOBAL_BBOX_FIT_OPTIONS)}
    fm = get_com_member(model, "FeatureManager")
    if fm is None:
        return {"ok": False, "error": "取不到 FeatureManager"}
    #: ★★★ 2026-10-03（轮 479）**`Status` 是 out ⇒ 必须包成 BYREF VARIANT** ——
    #:   ⚠ 我第一版直接传 `0`，真机回：
    #:     `com_error: (-2147352571, '类型不匹配。', None, **5**)`
    #:     ★ **位置 5** 就是它 ⇒ ★ **裸 int 传不进 out 形参** ⚠
    #:   ★★ 而**本仓早有现成的**：`sw_connect.out_i4()` —— 它的 docstring 逐字是
    #:     「创建 `Int32&` 出参的 VARIANT 包装 —— **唯一被真机验证通过的形态**」
    #:     （★ 本仓还有一道门禁 `tools/audit_byref_args.py` 专管这件事）✓
    try:
        from .sw_connect import out_i4 as _out_i4
    except ImportError:
        from sw_connect import out_i4 as _out_i4
    status_buf = _out_i4(0)
    before = _tree_names(model)
    raw = get_com_member(fm, "InsertGlobalBoundingBox2",
                         int(bbox_type), int(lwta_direction_type),
                         bool(include_hidden_bodies), bool(include_surface_bodies), status_buf)
    #: ★ out 值从**那个 VARIANT 里读回来**（★ 不是从返回值）✓
    status = None
    try:
        status = int(getattr(status_buf, "value", status_buf))
    except Exception:                                                    # noqa: BLE001
        status = None
    feat = raw[0] if isinstance(raw, (tuple, list)) and raw else raw
    r = _judge(model, {"_before": before, "returned_is_none": feat is None,
                       "bbox_type": int(bbox_type), "raw_type": type(raw).__name__},
               "global_bounding_box")
    r["status"] = status
    #: ★ 反查：字典是 `名 → 值`，而 out 给的是**值** ⇒ 必须反向找名
    #:   （★ 我第一版写成 `GLOBAL_BBOX_RESULT.get(status)` ⇒ 永远不中、显示"(未知)"）
    _by_val = {v: k for k, v in GLOBAL_BBOX_RESULT.items()}
    r["status_meaning"] = _by_val.get(status) if isinstance(status, int) else None
    if isinstance(status, int):
        r["ok"] = (status == GLOBAL_BBOX_RESULT["Success"]) and bool(r.get("new_features"))
        r["verified_by"] = "status_code(Success=0) + tree_delta"
    return r
