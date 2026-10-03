

# ── 24h 计划 段 6 续（Spec Kit `166`）：**曲面特征族（第一条已真机验证）** ──────────────
# ★★★★★ 2026-10-01（轮 308）**本段改写了硬约束⑧的措辞**：
#   ★ 官方建曲面有**两条完全不同的路**：
#     · **`IModeler.Create*Surface`** —— ★ 造**曲面体**（body）⇒ ★★ **事实 40：返回值跨次都变**；
#     · **`IFeatureManager.Insert*Surface` / `FeatureExtruRefSurface3`** —— ★ 造**曲面特征**（feature）
#       ⇒ ★★★★ **本会话首次试，一次成功**：真机特征树 `6 → 7`、特征名 **`曲面-拉伸1`**。
#   ⇒ ★ **两条路的差别是本质的**：★ 前者把"曲面"当**几何**（要自己造 body），
#     ★ 后者把它当**特征**（★ 与 UI 里点"曲面-拉伸"完全一致）⇒ ★ 属性上属于 `IFeatureManager`。
#
# ★ **本段只包装已真机验证的那一个**（★ `FeatureExtruRefSurface3`）——
#   ★ 其余（填充 / 缝合 / 裁剪 / 加厚）**需要选中面或边**，★ 留到选区那条链打通之后
#   （★ 真机实测：`InsertSewRefSurface` 不抛、但**特征树不变** ⇒ ★ 它要求"先选中要缝合的曲面"）。
#
# ★ 规则 2 / 3：★ 对外只暴露 `depth_mm`（★ 22 个官方参数里的深度），★ 其余用**有据的默认**；
#   ★ 草图**按名字**取（★ 不传坐标）。
# ★ 判据（规则 6）：★ **它回 void** ⇒ ★★ 成败**只能看特征树**（★ 建完回读，不静默成功）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_surface_features.py —— 本文件（新）
# 定位:   24h 段 6 续：曲面**特征**族（★ 与 sw_surface.py 的"曲面体"族分开）。
# 官方签名依据: `C:\swapi\types\IFeatureManager\FeatureExtruRefSurface3.md`
#   （完整签名 **22 个参数**：Sd / Dir / StartCond / OffsetVal / T1 / T2 / D1 / D2 / Dchk1 / Dchk2 /
#    Ddir1 / Ddir2 / Dang1 / Dang2 / OffsetReverse1 / OffsetReverse2 / TranslateSurface1 /
#    TranslateSurface2 / CapEnd1 / CapEnd2 / DeleteOriginalFace / KnitResult · **返回 void**）·
#   ★ 反射 arity 表 `scripts/sw_api_sldworks.py:4300` = **22**（★ 两源一致，铁律 4）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

import math

from sw_connect import get_com_member
from sw_feature_readback import feature_names

#: ★ `swEndConditions_e` / `swStartConditions_e` 的取值（★ 从反射来）
SW_START_SKETCH_PLANE = 0
SW_END_BLIND = 0
SW_END_THROUGH_ALL = 1


def _harden_defaults(depth_m, through: bool):
    """★ **22 个官方参数**（★ 顺序即官方顺序 —— ★ 一处也不能挪）。"""
    return (
        True,                       # Sd                 单端
        False,                      # Dir                不反向
        SW_START_SKETCH_PLANE,      # StartCond
        0.0,                        # OffsetVal
        (SW_END_THROUGH_ALL if through else SW_END_BLIND),   # T1
        SW_END_BLIND,               # T2（★ Sd=True 时无效）
        depth_m,                    # D1
        depth_m,                    # D2（★ Sd=True 时无效）
        False, False,               # Dchk1 / Dchk2
        False, False,               # Ddir1 / Ddir2
        0.0, 0.0,                   # Dang1 / Dang2
        False, False,               # OffsetReverse1 / OffsetReverse2
        False, False,               # TranslateSurface1 / TranslateSurface2
        False, False,               # CapEnd1 / CapEnd2
        False,                      # DeleteOriginalFace
        True,                       # KnitResult（★ 缝合结果 ⇒ 更接近 UI 的默认）
    )


def create_extruded_surface_report(model, depth_mm: float, sketch_name: str = "",
                                   through_all: bool = False) -> dict:
    """★ **用已有草图建「曲面-拉伸」特征**（★ 走 `FeatureExtruRefSurface3`，官方 22 参）。

    ★ **它回 `void`** ⇒ ★★ 判据**不能是返回值**，只能是「**特征树多了**」（★ 规则 6）。
    ★ `depth_mm` 是**毫米**（★ 规则 2）；★ 换算在这里做一次。
    ★ 回 `{"ok", "feature_name", "tree_before", "tree_after", "args_count", "verdict_basis"}`。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    if not through_all:
        try:
            d = float(depth_mm)
        except (TypeError, ValueError) as exc:
            return {"ok": False, "error": "depth_mm 必须是数字：%s" % str(exc)[:100]}
        if not math.isfinite(d) or d <= 0.0:
            return {"ok": False, "error": "depth_mm 必须 > 0（★ 收到 %r）" % depth_mm}
    else:
        d = 0.010             #: ★ 贯穿时深度无效，★ 给一个有限值免得 API 抱怨
    before_names = feature_names(model)
    before = len(before_names)
    args = _harden_defaults(d * 0.001, through_all)     #: ★ 毫米 ⇒ 米（★ 唯一的换算处）
    try:
        fm = get_com_member(model, "FeatureManager")
        get_com_member(fm, "FeatureExtruRefSurface3", *args)
    except Exception as exc:                                # noqa: BLE001
        return {"ok": False, "stage": "call", "args_count": len(args),
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:220]),
                "★": "若报 DISP_E_BADPARAMCOUNT ⇒ 参数个数不对（官方 22 个）"}
    after_names = feature_names(model)
    new = [n for n in after_names if n not in before_names]
    return {"ok": len(after_names) > before, "feature_name": (new[-1] if new else None),
            "new_features": new, "tree_before": before, "tree_after": len(after_names),
            "args_count": len(args), "depth_mm": (None if through_all else float(depth_mm)),
            "through_all": bool(through_all), "sketch_name": str(sketch_name),
            "★": "它回 void ⇒ 判据是**特征树真的多了**（★ 规则 6）；★ 官方 22 参 · 反射 arity 22"}


# ── 24h 计划 段 6 续（Spec Kit `166` 续）：**缝合曲面（真机打通）** ────────────────────
# ★★★★★ 2026-10-01（轮 309）**真机**（`output/surface-sew-probe.json`）：
#   · ★ **按对象选面**（`IEntity.Select4(Append, Callout)` —— ★ 事实 32：实体没有名字，只能按对象选）
#     ⇒ 8 张面全选中（★ **回读 `GetSelectedObjectCount2(-1)` = 8** —— ★ 事实 8：不能信返回值）
#   · ★ **mark = 1**（★ 官方 `InsertSewRefSurface` 的 Remarks 明写 "mark number of 1"）
#   · ★ `InsertSewRefSurface(False, False, True, 0.0001, 0.0001)` ⇒ **特征树出现 `曲面-缝合1`**
#   · ★★ **body 数 `2 → 1`** ⇒ ★★★ **两张曲面真的缝成了一张** ✓
#   ★ 官方给的容差范围：★ **0.0001 mm ～ 0.1 mm**（★ 本包装按**毫米**收参数、在边界换算一次 —— ★ 规则 2）。
#
# ★ 判据（★ 规则 6）：★ **特征树出现新特征** **且** **body 数变少**（★ 两者都要 —— 只看返回值不够）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_surface_features.py —— 追加本段
# 定位:   段 6 续：缝合曲面（★ 对应四家缺口名 `knit_surfaces`）。
# 官方签名依据: `C:\swapi\types\IFeatureManager\InsertSewRefSurface.md`
#   （`Feature InsertSewRefSurface(bool UseGapFilters, bool TryToFormSolid, bool MergeEntities,
#     double KnitTolerance, double MaxValueForGapRange)` ·
#    Remarks：「Make selections using `IModelDocExtension::SelectByID2` with a **mark number of 1**」·
#    「A knit tolerance's: lower limit is **0.0001 mm** · upper limit is **0.1 mm**」）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────


def _select_all_surface_faces(model, mark: int = 1) -> int:
    """★ **把所有曲面体的面按对象选中**（★ 回**选中数** —— ★ 事实 8：不信返回值，只信回读计数）。"""
    from sw_connect import get_com_member as _get
    from sw_part import _select_com_object as _sel
    try:
        model.ClearSelection2(True)
    except Exception:                                          # noqa: BLE001
        pass
    n = 0
    try:
        bodies = list(_get(model, "GetBodies2", -1, True) or [])
    except Exception:                                          # noqa: BLE001
        bodies = []
    for b in bodies:
        try:
            faces = list(_get(b, "GetFaces") or [])
        except Exception:                                      # noqa: BLE001
            continue
        for f in faces:
            try:
                if _sel(f, append=True, mark=mark):
                    n += 1
            except Exception:                                  # noqa: BLE001
                continue
    try:
        return int(_get(_get(model, "SelectionManager"), "GetSelectedObjectCount2", -1))
    except Exception:                                          # noqa: BLE001
        return n


def _body_count(model) -> int:
    """★ 数**所有** body（★ 曲面体也算 —— `-1 = swAllBodies`）。"""
    from sw_connect import get_com_member as _get
    try:
        return len(list(_get(model, "GetBodies2", -1, True) or []))
    except Exception:                                          # noqa: BLE001
        return -1


def _solid_body_count(model) -> int:
    """★ 数**实体**数（`swSolidBody = 0`）—— ★ 加厚后它该**变多**。

    ★ 本仓既有的 `GetBodies2(-1, True)` 取的是**全部体**；
    ★ 而加厚的语义是「**曲面 ⇒ 实体**」⇒ ★★ 故要**分开数**才看得出变化
    （★ 参数取自 `swBodyType_e`：`swSolidBody = 0` · `swSheetBody = 1`）。
    """
    from sw_connect import get_com_member as _get
    try:
        return len(list(_get(model, "GetBodies2", 0, True) or []))
    except Exception:                                          # noqa: BLE001
        return -1


def _surface_body_count(model) -> int:
    """★ 数**曲面体**数（`swSheetBody = 1`）—— ★ 加厚后它该**变少**。"""
    from sw_connect import get_com_member as _get
    try:
        return len(list(_get(model, "GetBodies2", 1, True) or []))
    except Exception:                                          # noqa: BLE001
        return -1


def knit_surfaces_report(model, knit_tolerance_mm: float = 0.0001,
                         try_to_form_solid: bool = False) -> dict:
    """★ **把选中的曲面缝成一张**（★ 走 `InsertSewRefSurface`）。

    ★ 官方：★ 选中项要 **mark = 1** · ★ 容差范围 **0.0001 ～ 0.1 mm**（★ 本包装按**毫米**收，
    ★ 在边界换算一次 —— 规则 2）。
    ★ 判据（规则 6）：★ **特征树多了新特征** **且** **body 数变少**。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    try:
        tol = float(knit_tolerance_mm)
    except (TypeError, ValueError) as exc:
        return {"ok": False, "error": "knit_tolerance_mm 必须是数字：%s" % str(exc)[:100]}
    if not (0.0001 <= tol <= 0.1):
        return {"ok": False, "stage": "validate",
                "error": "knit_tolerance_mm 必须在 **0.0001 ～ 0.1 mm**（★ 官方给的上下限）；收到 %r" % tol}
    before_names = feature_names(model)
    before_bodies = _body_count(model)
    selected = _select_all_surface_faces(model, mark=1)
    if selected <= 0:
        return {"ok": False, "stage": "select", "body_before": before_bodies,
                "error": "没选中任何面（★ 文件里要有曲面体；★ 而曲面体用 GetBodies2(-1) 取）"}
    try:
        fm = get_com_member(model, "FeatureManager")
        #: ★ 容差换算：毫米 ⇒ 米（★ 唯一的换算处）
        get_com_member(fm, "InsertSewRefSurface", False, bool(try_to_form_solid), True,
                       tol * 0.001, tol * 0.001)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "call", "faces_selected": selected,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}
    after_names = feature_names(model)
    new = [n for n in after_names if n not in before_names]
    after_bodies = _body_count(model)
    return {"ok": bool(new) and after_bodies < before_bodies, "new_features": new,
            "face_count_selected": selected, "body_before": before_bodies, "body_after": after_bodies,
            "knit_tolerance_mm": tol,
            "★": "判据 = **特征树多了新特征** 且 **body 数变少**（★ 规则 6）；★ 官方 mark=1 · 容差 0.0001–0.1 mm"}

# ── B6 / T610：**加厚（曲面⇒实体）** ─────────────────────────────────────────────
# ★★★★ 2026-10-03（轮 502）★ 补 `specs/201-toolbar-gaps` 的 **T610**（★ 那条一直空着）。
#
# 官方三源（★ 铁律 4）：
#   · `C:\swapi\types\IFeatureManager\FeatureBossThicken.md`：
#     `Feature FeatureBossThicken(System.double Thickness, System.int Direction, System.int FaceIndex,
#      System.bool FillVolume, System.bool Merge, System.bool UseFeatScope, System.bool UseAutoSelect)`
#     ★★ **参数表逐字**：`FaceIndex` ⇒ 「**Not used**」 ✓
#     （★ 故本包装**不传面索引** —— ★ 那会误导调用方以为选了面在起作用）
#     · `Direction` ⇒ `swThickenThicknessType_e`（★ 枚举值本机转储里有）
#   · `C:\swapi\types\IModelDoc2\FeatureBossThicken.md` ⇒ **Obsolete**，继任者是 `IFeatureManager` 那个
#     ⇒ ★ **故必须走 `IFeatureManager`**（★ 与 `InsertRuledSurfaceFromEdge` 的 `…2` 是同一类更正）
#
# ★ 判据（★ 规则 6）：★ **特征树多了新特征** ——
#   ★ 而**加厚的语义**是"曲面变实体" ⇒ 更贴的判据是 **实体数变多 / 曲面体数变少**（★ 一并记账）。


def thicken_surface_report(model, thickness_mm: float, *, direction: int = 0,
                           fill_volume: bool = True, merge: bool = True,
                           use_feat_scope: bool = False,
                           use_auto_select: bool = True) -> dict:
    """★ **加厚**：把选中的曲面体加厚成实体（`IFeatureManager.FeatureBossThicken`）。

    ★ 官方：`FaceIndex` **「Not used」** ⇒ ★ 本包装**不收面索引**（★ 收了是骗人）。
    ★ 前置：★ **文件里要有曲面体**（★ 与 `knit_surfaces_report` 同款前置 ——
      ★ 而 `use_auto_select=True` 时官方会"自动选所有体"）。
    ★ 判据（规则 6）：★ **特征树多了新特征**；★ 并同时记账**实体数 / 曲面体数**的变化
      （★ 加厚的语义就是那个变化）。
    ★ 单位：★ `thickness_mm` 按**毫米**收，★ 在边界换算一次（规则 2）。

    ★★★★ 2026-10-03（轮 503）**真机状态：⚠ 尚未建成 —— ★ 而按事实 53 停手** ⚠
      · ★ **前置是完美的**：每次 `pre` 都是 `solid = 0 · surface = 1`
        （★ 一张曲面体、零个实体 —— ★ 正是加厚该有的起点）✓
      · ★★ 而 **7 组参数组合全部返回 `None`**、特征树不动、★ **连错误都不报**：
        ```
        基准（fill=True · scope=False · auto=True）   回 None  树不动
        scope=True + 先选中曲面体                     回 None  树不动
        auto=False                                  回 None  树不动
        scope=True + auto=False + 选体                回 None  树不动
        fill=False                                  回 None  树不动
        direction=1                                 回 None  树不动
        scope=True + auto=False                      回 None  树不动
        ```
        （★ 矩阵见 `tools/probe_thicken_matrix.py` · `output/thicken-matrix-evidence.json`）
      · ⇒ ★★ **故「不是参数没找对」在这一条上是有据的** —— ★ 官方参数表里那 4 个布尔/枚举开关的
        **主要组合已穷尽** ✓
      · ★ 形态与**事实 40**（`IModeler.Create*Surface` 返回 `None` 而几何不变）**同族**：
        ★ 即「**静默不干活**」，★ 而**不是**「报错说参数不对」。
      · ⚠ **按 A4 不登记成工具、不写 `verified`** —— ★ **不假装做到**。
      · ★ 若下一轮还要动它，**该换的方向**：★ 试 `IModelDoc2.FeatureBossThicken`
        （★ 它标 `Obsolete`，而**废弃入口有时在 pywin32 上反而更顺** —— ★ 本仓在别处见过这种反转）⚠

    ★★★★ 2026-10-03（轮 504）**那个方向也试过了 —— ★ 假设被否证** ✓
      · `IModelDoc2.FeatureBossThicken`（`kind: method` · **3 参** ·
        官方 `Obsolete. Superseded by [[IFeatureManager::FeatureBossThicken]]`）
        ⇒ ★★ **3 组（基准 / `direction=1` / 厚 5mm）全部返回 `None`**、树不动 ⚠
      · 而★ **`pre` 同样完美**（每次 `solid = 0 · surface = 1`）✓
      ⇒ ★★★ **故「废弃入口更顺」这个假设在这一条上**不成立****。

    ★★★★★ **本条的完整总账（★ 那才是"写明依据"）**：
      | 轮 | 入口 | 组数 | 结果 |
      |---|---|---|---|
      | 502 | `IFeatureManager.FeatureBossThicken`（7 参） | 1 | 全 `None` |
      | 503 | 同上 | **7**（官方开关的主要组合） | 全 `None` |
      | 504 | `IModelDoc2.FeatureBossThicken`（3 参 · Obsolete） | 3 | 全 `None` |
      ⇒ ★★ **共 11 组 · 两条入口 · 前置每次完美（`solid=0 · surface=1`）** ⇒
        ★ **「加厚」在本机是「静默不成」** —— ★★ 而**不是**「参数没找对」、
        ★ 也**不是**「废弃入口反而顺」（★ 那条假设已否证）✓
      证据：`output/thicken-surface-evidence.json` · `output/thicken-matrix-evidence.json` ·
      `output/thicken-obsolete-entry-evidence.json`
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    try:
        th = float(thickness_mm)
    except (TypeError, ValueError) as exc:
        return {"ok": False, "error": "thickness_mm 必须是数字：%s" % str(exc)[:100]}
    if not (th > 0.0):
        return {"ok": False, "stage": "validate",
                "error": "thickness_mm 必须 > 0（★ 加厚是给曲面一个壁厚）；收到 %r" % th}
    before_names = feature_names(model)
    before_solid = _solid_body_count(model)
    before_surf = _surface_body_count(model)
    try:
        fm = get_com_member(model, "FeatureManager")
        #: ★ 调用序照官方签名：Thickness(米) ⇒ Direction ⇒ FaceIndex(★「Not used」⇒ 0)
        #:   ⇒ FillVolume ⇒ Merge ⇒ UseFeatScope ⇒ UseAutoSelect
        feat = get_com_member(fm, "FeatureBossThicken",
                              th * 0.001, int(direction), 0,
                              bool(fill_volume), bool(merge),
                              bool(use_feat_scope), bool(use_auto_select))
    except Exception as exc:                                             # noqa: BLE001
        return {"ok": False, "stage": "call", "thickness_mm": th,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}
    after_names = feature_names(model)
    new = [n for n in after_names if n not in before_names]
    return {"ok": bool(new), "feature_name": (new[-1] if new else None), "new_features": new,
            "returned_none": feat is None,
            "solid_before": before_solid, "solid_after": _solid_body_count(model),
            "surface_before": before_surf, "surface_after": _surface_body_count(model),
            "thickness_mm": th, "direction": int(direction),
            "★": "判据 = **特征树多了新特征**（规则 6）；★ 官方 `FaceIndex` 标注「Not used」故传 0；"
                 "★ 而**加厚的语义**看实体数/曲面体数的变化"}

# ── objective② / 段 6 续：**延伸曲面（`IModelDoc2.InsertExtendSurface`）** ──────────────
# ★★★★ 2026-10-02（轮 386）**补 `extend_surface`** —— 它是 objective② 重核后确认的**真缺**之一
#   （★ 另两条 `delete_feature` / `rename_feature` 是**高风险写**，按硬约束⑦不碰）。
# 官方签名依据: `C:\swapi\types\IModelDoc2\InsertExtendSurface.md`
#   `void InsertExtendSurface(bool ExtendLinear, int EndCondition, double Distance)`
#   · **ExtendLinear**: True 线性延伸 / False 沿同一曲面延伸
#   · **EndCondition**: **0 = 按给定距离** · **1 = 延伸到选定点**
#   · ★ **它回 `void`** ⇒ ★★ 判据**不能是返回值**，只能是「**特征树多了**」（★ 规则 6）。
# ★ 规则 2 / 3：★ 对外只暴露 `distance_mm`（毫米）；★ 面**按对象选中**（★ 声明式，事实 32）。
# ★ 与 `sw_surface.py` 的 `create_revolution_surface` 那族**不是一回事** ——
#   ★ 那族是 `IModeler.Create*Surface`（造**曲面体**，事实 40 返回值不可靠），
#   ★ 本条是 `IModelDoc2.InsertExtendSurface`（造**曲面特征**）。


def insert_extend_surface_report(model, distance_mm: float, *, extend_linear: bool = True,
                                 end_condition: int = 0) -> dict:
    """★ **延伸曲面**（★ 官方 `IModelDoc2.InsertExtendSurface`，**3 参**，★ 回 `void`）。

    :param distance_mm: 延伸距离（**毫米** —— ★ 换算只在本函数做一次）。
    :param extend_linear: True 线性延伸 / False 沿同一曲面延伸。
    :param end_condition: **0 = 按距离**（默认）· **1 = 延伸到选定点**。
    :returns: `{ok, feature_name, new_features, tree_before, tree_after, faces_selected, distance_mm}`
        ★★ **判据是「特征树真的多了」** —— ★ 因为它回 `void`（★ 规则 6：建完必须回读）。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    try:
        d = float(distance_mm)
    except (TypeError, ValueError) as exc:
        return {"ok": False, "error": "distance_mm 必须是数字：%s" % str(exc)[:100]}
    if not math.isfinite(d) or d <= 0.0:
        return {"ok": False, "error": "distance_mm 必须 > 0（★ 收到 %r）" % distance_mm}
    if int(end_condition) not in (0, 1):
        return {"ok": False, "error": "end_condition 只支持 0（按距离）/ 1（到选定点）：%r" % end_condition}
    #: ★ 官方说 "along the **selected** faces or edges" ⇒ ★ 先按对象选面（★ 声明式）
    selected = _select_all_surface_faces(model, mark=0)
    if selected <= 0:
        return {"ok": False, "stage": "select", "faces_selected": 0,
                "error": "没有选中任何曲面面 —— 曲面延伸要求先选中要延伸的面/边",
                "★": "官方描述：Extends a surface along the **selected** faces or edges"}
    before_names = feature_names(model)
    before = len(before_names)
    try:
        #: ★ 毫米 ⇒ 米（★ 与同模块 `FeatureExtruRefSurface3` 的做法一致；★ 真机复验这一点）
        get_com_member(model, "InsertExtendSurface",
                       bool(extend_linear), int(end_condition), d * 0.001)
    except Exception as exc:                                    # noqa: BLE001
        return {"ok": False, "stage": "call", "faces_selected": selected,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}
    after_names = feature_names(model)
    new = [n for n in after_names if n not in before_names]
    return {"ok": len(after_names) > before, "feature_name": (new[-1] if new else None),
            "new_features": new, "tree_before": before, "tree_after": len(after_names),
            "faces_selected": selected, "distance_mm": d,
            "extend_linear": bool(extend_linear), "end_condition": int(end_condition),
            "★": "它回 void ⇒ 判据是**特征树真的多了**（★ 规则 6）；"
                 "★ 官方 3 参 · 反射 arity 3 · EndCondition 0=按距离 / 1=到选定点"}

# ── objective② / 第二个真缺：**填充曲面（`IFeatureManager.InsertFillSurface2`）** ──────────
# ★★★★★ 2026-10-02（轮 388）真机**打通的组合**（★ 事实 305）：
#   ```
#   ① SelectByID2("", "EDGE", <边的中点>, False, **mark = 1**, callout, 0)
#        ⇒ ★ **回 true 且 GetSelectedObjectCount2(-1) = 4**（★ 计数对上 ⇒ 真选中了）✓
#   ② InsertFillSurface2(Resolutions=2, **Options = 1**（swOptimizeSurface）, None, None, None, None)
#        ⇒ ★ **回 Feature（非 None）且特征树多出 `曲面填充1`** ✓
#   ```
# ★★ **两个关键细节**（★ 都是真机撞出来的）：
#   · **mark 必须是 1**（★ 官方 Remarks：`Boundary curves = 1`）——
#     ★ 我先前传 **mark = 4**（★ 那是"约束曲线"的 mark）⇒ `SelectByID2` **回 true 而计数 0**
#     （★ **静默失败** —— 事实 8 那条；★ **mark 值决定成败**）。
#   · **`Options = 1`（`swOptimizeSurface`）** —— 与官方示例一致；
#     ★ 枚举是 **Bitmask**（`swOptimizeSurface=1` · `swTryToFormSolid=2` · `swMergeResult=4` ·
#     `swReverseDirection=8` · `swReverseSurface=16`，★ md 表与反射两源一致）。
# 官方签名依据: `C:\swapi\types\IFeatureManager\InsertFillSurface2.md`
#   （**6 参** `int Resolutions, int Options, object VPatchBoundaries, object VCurvatureControlType,
#     object VFaces, object VConstraintCurves`；★ `Resolutions` = 1/2/3；
#     ★ Remarks 的 mark 表：Boundary = **1** · contact curvature = 257 · tangent = 513 · 约束曲线 = 4）·
#   官方示例 `Insert_Fill-surface_Feature_Example_CSharp`（★ 两平面各一圆 ⇒ 填充）。
# ★ 规则 2 / 3 / 6：★ 对外只暴露 `resolutions` / `options`；★ 边界边**按中点 + mark 选中**（声明式）；
#   ★ **判据 = 回 `Feature` 非 None 且特征树**增量**非空**（★ 两判据都要 —— 只看 diff 会踩"前面已建"）。

_SW_OPTIMIZE_SURFACE = 1
#: ★ 官方 Remarks 的 mark 表（★ 只列我们用的那个；★ 其余三个待真机验）
MARK_BOUNDARY = 1


def insert_fill_surface_report(model, resolutions: int = 2, *, options: int = _SW_OPTIMIZE_SURFACE,
                               selection: str = "") -> dict:
    """★ **填充曲面**（★ 官方 `IFeatureManager.InsertFillSurface2`，**6 参**，★ 回 `Feature`）。

    :param resolutions: 分辨率 **1 / 2 / 3**（★ 越大质量越好，官方原话）。
    :param options: `swFeatureFillSurfaceOptions_e` 的 **Bitmask**；★ 默认 `1`（`swOptimizeSurface`）。
    :param selection: ★★ **声明式选择**（★ 该填的**那一圈边**）。
        ★ 留空 = **自动取最高那一圈**（★ 保留原行为）。
        ★★ ★ 2026-10-03（轮 434）**原来这里是 `boundary_z: float`**（一个裸坐标），
        ★ 而那**违反规则 3**（★ 官方原话：必须改用**具名实体 + 声明式 selection**）。
        ★ 实测那条违反让 `tool_registry` 的声明门禁整批不过 ⇒ **4 个测试文件在收集期就 ERROR**。
    :returns: `{ok, feature_name, new_features, tree_before, tree_after, points_selected, boundary_z}`
        ★★ **判据 = 回 `Feature` 非 None** **且** **特征树增量非空**（★ 两判据都要）。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    try:
        res = int(resolutions)
    except (TypeError, ValueError):
        return {"ok": False, "error": "resolutions 必须是整数（1/2/3）"}
    if res not in (1, 2, 3):
        return {"ok": False, "error": "resolutions 只支持 1 / 2 / 3（官方 Remarks）：%r" % resolutions}
    if not (1 <= int(options) <= 31):
        return {"ok": False, "error": "options 超出 Bitmask 范围（1..31）：%r" % options}
    #: ★ 取全部边 ⇒ 按**起点/终点的中点**算 z ⇒ 选出一圈（★ 坐标单位是**米**，★ 不换算）
    #: ★★★ 2026-10-03（轮 434）**声明式分支** —— ★ 而后半段**两条路共用**：
    #:   ★ 给了 `selection` ⇒ **用它选**（★ 那是规则 3 要求的形态），★ 而 `_declarative = True`
    #:     ⇒ ★★ **跳过后面那个"按点选边"的循环**（已经选好了）；
    #:   ★ 否则走**原自动路**（按最高一圈边的 z 挑）——★ **行为不变**。
    _declarative = bool(str(selection or "").strip())
    _selected_readback = 0
    if _declarative:
        #: ★★★ 2026-10-03（轮 435）**不重选** —— 而代价是一条**文档化的契约**。
        #:   ★ 上一版走 `resolve_selection`（★ 它会**重选**），★ 而它走的是
        #:     `IEntity.Select4` —— ★★ **而 `Select4` 没有 mark 参数**（**事实 32**）
        #:     ⇒ 重选后 mark 变成 **0**，★ 而填充要 **1**（`MARK_BOUNDARY`，官方 Remarks）
        #:     ⇒ ★ 真机：选中了 4 条而填充仍不成（树 `[7, 7]`）。
        #:   ★★ **正解**：★ **尊重调用方已选好的选区（含它的 mark）** ——
        #:     ★ 而那正是规则 3 的本意：**选择由调用方做**（★ 工具不越俣代庖）。
        #:   ★ 而代价：★ **调用方选边时必须用 `mark = 1`** ⇒ ★★ 已写进工具文档与本函数的 docstring ✓
        try:
            _selected_readback = int(get_com_member(get_com_member(model, "SelectionManager"),
                                                    "GetSelectedObjectCount2", -1) or 0)
        except Exception:                                      # noqa: BLE001
            _selected_readback = 0
        if _selected_readback <= 0:
            return {"ok": False, "stage": "selection_readback", "selected": _selected_readback,
                    "error": "选区回读计数为 0（★ 事实 8：请以计数为准）",
                    "★": "请先选上该填的那一圈边，**且用 mark = 1**"
                           "（官方 Remarks：边界边用 mark 1）"}
    edges, mids = [], []
    try:
        for b in (get_com_member(model, "GetBodies2", -1, True) or []):
            for e in (get_com_member(b, "GetEdges") or []):
                try:
                    a = [float(x) for x in get_com_member(
                        get_com_member(e, "GetStartVertex"), "GetPoint")]
                    c = [float(x) for x in get_com_member(
                        get_com_member(e, "GetEndVertex"), "GetPoint")]
                    edges.append(e)
                    mids.append([(a[i] + c[i]) / 2.0 for i in range(3)])
                except Exception:                              # noqa: BLE001
                    continue
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "collect_edges", "error": str(exc)[:140]}
    if not edges:
        return {"ok": False, "stage": "collect_edges", "error": "模型上没有可选边（★ 填充要一个封闭边界）"}
    z = max(m[2] for m in mids) if not _declarative else None
    picked = [] if _declarative else [(m, e) for m, e in zip(mids, edges) if abs(m[2] - z) < 1e-9]
    if not _declarative and len(picked) < 3:
        return {"ok": False, "stage": "pick_boundary", "at_z": z,
                "error": "z=%.6f 上只找到 %d 条边（★ 封闭边界至少要 3 条）" % (z, len(picked))}
    #: ★★ **按中点 + mark=1 选中**（★ 官方 Remarks 要的 mark；★ `Select4` 没有 mark 参数 —— 事实 32）
    callout = _empty_callout()
    ext = get_com_member(model, "Extension")
    #: ★★★ 2026-10-03（轮 435）**这一句必须护住** —— ★ 它是**无条件**的，
    #:   ★★ 而它会把**调用方选好的边清掉** ⚠ ⇒ ★ 于是声明式路"回读计数 4、而选区是空的"
    #:   ⇒ ★ 填充**不建**（★ 真机：树 `[7, 7]`）✓
    #:   ★ 而**这正是**"调用方做选择、工具不越俎代庖"那条契约（规则 3 的本意）的**必要条件**。
    if not _declarative:
        try:
            model.ClearSelection2(True)
        except Exception:                                      # noqa: BLE001
            pass
    for m, _e in ([] if _declarative else picked):
        try:
            ext.SelectByID2("", "EDGE", m[0], m[1], m[2], True, MARK_BOUNDARY, callout, 0)
        except Exception:                                      # noqa: BLE001
            pass
    selected = _selected_readback
    if not _declarative:
        try:
            selected = int(get_com_member(get_com_member(model, "SelectionManager"),
                                          "GetSelectedObjectCount2", -1) or 0)
        except Exception:                                      # noqa: BLE001
            selected = 0
    #: ★★ **回读计数为零 ⇒ 选择其实没生效**（★ 事实 8：bool 返回值不可信）⇒ **早退，不假装成功**
    if selected <= 0:
        return {"ok": False, "stage": "select", "points_selected": 0, "boundary_z": z,
                "error": "SelectByID2 选了 %d 条边而回读计数为 0（★ 事实 8：静默失败）" % len(picked),
                "★": "检查 mark 是否为 1（★ 传 4 会静默失败）"}
    before_names = feature_names(model)
    before = len(before_names)
    try:
        feat = get_com_member(get_com_member(model, "FeatureManager"), "InsertFillSurface2",
                              res, int(options), None, None, None, None)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "call", "points_selected": selected,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}
    after_names = feature_names(model)
    new = [n for n in after_names if n not in before_names]
    return {"ok": (feat is not None) and len(after_names) > before,
            "feature_name": (new[-1] if new else None), "new_features": new,
            "tree_before": before, "tree_after": len(after_names),
            "points_selected": selected, "boundary_z": z,
            "resolutions": res, "options": int(options),
            "★": "判据 = **回 Feature 非 None** **且** **特征树增量非空**（★ 两判据都要）；"
                 "★ 边界按**中点 + mark=1** 选（★ 官方 Remarks；★ 传 mark=4 会静默失败）"}


def _empty_callout():
    """★ 空 `Callout`（`VARIANT(VT_DISPATCH, None)`）—— ★ 事实 33：传 `None` 会报"类型不匹配"。"""
    from sw_connect import create_empty_dispatch_variant
    return create_empty_dispatch_variant()


# ── B6 / T608：**直纹曲面** ─────────────────────────────────────────────────────
# ★★★★ 2026-10-03（轮 505）★ 补 `specs/201-toolbar-gaps` 的 **T608**。
#
# 官方三源（★ 铁律 4）—— ★★ **而本轮逮到一处两源冲突，正是铁律 4 的活教材** ⚠：
#   · `C:\swapi\types\IFeatureManager\InsertRuledSurfaceFromEdge2.md` 的**参数表**写：
#     `Type` ⇒ **0 = Tangent to Surface · 1 = Normal · 2 = Tapered to Vector ·
#     3 = Perpendicular to Vector · 4 = Sweep**（★ 看起来是 **0-based**）
#   · 而**反射转储** `_raw/enum_values_sldworks.txt` 的 `swRuledSurfaceType_e` 写：
#     `swRuledSurfaceType_TangentToSurface = **1**` · `NormalToSurface = **2**` ·
#     `TaperedToVector = **3**` · `PerpendicularToVector = **4**` · `Sweep = **5**`
#     （★ **1-based** ⇒ ★ 与上面**整体差 1**）⚠
#   · ★ `IModelDoc2.InsertRuledSurfaceFromEdge` ⇒ **Obsolete**，继任者是 `IFeatureManager` 的 `…2`
#
#   ⇒ ★★ **铁律 4 说：冲突以出厂类型库为准** ⇒ ★ 本包装**收枚举值 1..5**，
#     ★ 并把**这张对照表**写进 docstring（★ 免得后人在同一处再撞一次）✓
#
# 官方其余参数（逐字）：
#   · `Length` ⇒ "Distance at which to create the surface; valid for **Tangent to Surface,
#     Tapered to Vector, Perpendicular to Vector, and Sweep** types only"
#   · `FlipPullDir` ⇒ valid for **Normal to Surface / Tapered to Vector** only
#   · `FlipDir` ⇒ valid for **Perpendicular to Vector** only
#   · `TrimAndSew` ⇒ "True to trim and knit the surface"
#   · `Angle` ⇒ "Angle for **Tapered to Vector** type only"
#   · `CoordInput` ⇒ "True to enable coordinate input; for **Sweep** type only"
#   ⇒ ★★ **前置**：★ 官方第一句是「from the **selected edge**」⇒ ★ **要先选一条边** ✓
#
# ★ 判据（★ 规则 6）：★ **特征树多了新特征**。


def insert_ruled_surface_report(model, *, surface_type: int = 1, length_mm: float = 10.0,
                                flip_pull_dir: bool = False, flip_dir: bool = False,
                                trim_and_sew: bool = False, angle_deg: float = 0.0,
                                coord_input: bool = False) -> dict:
    """★ **直纹曲面**（`IFeatureManager.InsertRuledSurfaceFromEdge2`）。

    ★★ `surface_type` 取值 —— ★ **以出厂类型库为准**（★ 铁律 4；★ 而 md 的参数表与它差 1）：
    ```
    1 = TangentToSurface          0 = Tangent to Surface      ← md 那一栏**别用**
    2 = NormalToSurface           1 = Normal to Surface          （★ 整体 0-based，差 1）
    3 = TaperedToVector           2 = Tapered to Vector
    4 = PerpendicularToVector     3 = Perpendicular to Vector
    5 = Sweep                     4 = Sweep
    ```

    ★ 前置：★ 官方第一句「Inserts a ruled surface from the **selected edge**」
      ⇒ ★ **要先选中一条边**（★ 而边**没有名字** ⇒ ★ 按对象选 —— **事实 32**）。

    ★ 参数的有效性**按类型而变**（★ 官方逐字给了三种限制，★ 本包装**照实转录**而**不替调用方判断**）：
      · `length_mm` 只对 **1 / 3 / 4 / 5** 型有效
      · `flip_pull_dir` 只对 **2 / 3** 型有效
      · `flip_dir` 只对 **4** 型有效
      · `angle_deg` 只对 **3** 型有效
      · `coord_input` 只对 **5** 型有效

    ★ 单位：★ `length_mm` / `angle_deg` 按**毫米 / 度**收，★ 在边界各换算一次（规则 2）。
    ★ 判据（规则 6）：★ **特征树多了新特征**。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    try:
        t = int(surface_type)
    except (TypeError, ValueError):
        return {"ok": False, "stage": "validate", "error": "surface_type 必须是整数（1..5）"}
    if not (1 <= t <= 5):
        return {"ok": False, "stage": "validate",
                "error": "surface_type 必须 **1..5**（★ 出厂类型库口径：1=TangentToSurface … 5=Sweep）；"
                         "★ 而官方 md 的参数表是 0-based ⇒ ★ 别照它填" }
    try:
        ln = float(length_mm)
    except (TypeError, ValueError) as exc:
        return {"ok": False, "error": "length_mm 必须是数字：%s" % str(exc)[:100]}
    before = feature_names(model)
    try:
        #: ★ 回读选中数（★ 事实 8：不信返回值，只信回读计数）
        try:
            sel = int(get_com_member(get_com_member(model, "SelectionManager"),
                                     "GetSelectedObjectCount2", -1) or 0)
        except Exception:                                                 # noqa: BLE001
            sel = -1
        fm = get_com_member(model, "FeatureManager")
        #: ★ 调用序照官方签名：Type ⇒ Length(米) ⇒ FlipPullDir ⇒ FlipDir ⇒ TrimAndSew
        #:   ⇒ Angle(弧度) ⇒ CoordInput ⇒ **X ⇒ Y ⇒ Z ⇒ BConnectSurface**
        #:
        #: ★★★★ 2026-10-03（轮 505）**真机第一次栽在这里 —— ★ 而它是本仓的一条可复用教训** ⚠
        #:   我第一版只传了**前 7 个** ⇒ 真机回 **`非选择性的参数`**（`DISP_E_PARAMNOTOPTIONAL`，
        #:   ★ 它的意思就是"某个参数没给"）⚠
        #:   ★★ 真因：**官方 md 的 `**Signature**` 行是 11 个**（★ 我读的时候只看了它前半），
        #:     而**反射也是 11**：
        #:     ```
        #:     Feature InsertRuledSurfaceFromEdge2(Int32, Double, Boolean, Boolean, Boolean, Double,
        #:                                         Boolean, Double, Double, Double, Boolean)
        #:     ```
        #:   ⇒ ★★ **教训：`**Signature**` 行一个字都别省** ——
        #:     ★ **反射核 arity**（★ 快、无歧义）、★ **md 核每个参数的名字与语义**（★ 两源分工）✓
        feat = get_com_member(fm, "InsertRuledSurfaceFromEdge2",
                              t, ln * 0.001, bool(flip_pull_dir), bool(flip_dir),
                              bool(trim_and_sew),
                              float(angle_deg) * 3.141592653589793 / 180.0,
                              bool(coord_input),
                              0.0, 0.0, 0.0,          # ★ X / Y / Z（★ 只在 CoordInput 为真时才用）
                              False)                  # ★ BConnectSurface
    except Exception as exc:                                              # noqa: BLE001
        return {"ok": False, "stage": "call", "surface_type": t,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}
    after = feature_names(model)
    new = [n for n in after if n not in before]
    return {"ok": bool(new), "feature_name": (new[-1] if new else None), "new_features": new,
            "tree_before": len(before), "tree_after": len(after),
            "surface_type": t, "length_mm": ln, "selected": sel, "returned_none": feat is None,
            "★": "判据 = **特征树多了新特征**（规则 6）；"
                 "★ `surface_type` 用**出厂类型库**口径 1..5（★ md 参数表是 0-based，差 1 —— 铁律 4）"}


# ── ★★ 一类现象的登记处：**「调用通、而静默不干活」** ────────────────────────────
#
# ★★★★ 2026-10-03（轮 505-506）★ 本模块里出现了**两次同形**，故在此**一次写清**，
#   ★ 免得后人把它误读成"参数没找对"再重跑一遍 ⚠
#
#   | 能力 | 官方入口 | 我们试了几组 | 前置 | 调用结果 | 特征 |
#   |---|---|---|---|---|---|
#   | **加厚** | `IFeatureManager.FeatureBossThicken`（7 参） | 7 组（官方开关主要组合） | ★ 完美（`solid=0 · surface=1`） | 回 `None` | **不建** |
#   | 加厚 | `IModelDoc2.FeatureBossThicken`（3 参 · Obsolete） | 3 组 | ★ 完美 | 回 `None` | **不建** |
#   | **直纹曲面** | `InsertRuledSurfaceFromEdge2`（11 参） | 侧棱 4 条 + **水平边 4 条** + 负例 | ★ 边**选上了**（`sel=True`） | ★ **回了对象** | **不建** |
#
#   ★★ **两者的共同形态**：★ **调用不报错**（★ 或只回 `None`）、★ **而特征树一点都不动**。
#     ⇒ ★ 这不是「参数没找对」（★ 加厚 11 组已穷尽；★ 直纹的 `非选择性的参数` 在补全 11 参后**已消失**），
#     ★ 也**不是**「选择没选上」（★ 直纹的 `sel=True` 是**回读**出来的 —— 事实 8）。
#
#   ★★★ **与事实 40 同族**：`IModeler.Create*Surface` 那一族也是「返回 `None` 而几何不变」。
#     ⇒ ★★ **故这三处该并成一类看**：★ **「pywin32 这条后端上，某些曲面类特征的调用会静默失效」**。
#     ⚠ 而**为什么**静默（★ 是 COM 层吞了错误？★ 还是 SW 内部前置未满足而不报？）**尚未查明** ——
#       ★ 按**铁律 5** 写「查不到」，★ 而**不编一个理由** ✓
#
#   ★ 若要继续攻：★ 该换的是**观测手段**（★ 如查 SW 的"什么错"面板 / 试 `CreateDefinition` 新架构），
#     ★ **而不是**继续在同一入口上换参数 —— ★ 那已经证明不是参数问题。


# ── B6 / T605 · T606 · T609：**旧式方法**那一族（★ 事实 395 指出的方向） ─────────────
# ★★★★ 2026-10-03（轮 516）★ 走**事实 395 明确指出的那条方向**：
#
#   > ★ **旧式方法**那侧是成的（填充 `InsertFillSurface2` / 延伸 `InsertExtendSurface` /
#   >   缝合 `InsertSewRefSurface` / 曲面-拉伸 `FeatureExtruRefSurface3`）——
#   >   ★★ 而**新架构**（`CreateDefinition` + `CreateFeature`）那侧对扫描面/加厚/直纹**静默不成**。
#
#   ★ 而 B6 里剩的几条**恰好都有 `IModelDoc2` 上的旧式入口**（★ 与**成过**的 `InsertExtendSurface` 同层）：
#   ```
#   ✓ IModelDoc2.InsertPlanarRefSurface()                     0 参 · 回 bool  → T605 平面区域
#   ✓ IModelDoc2.InsertOffsetSurface(Thickness, Reverse)      2 参 · void     → T606 等距曲面
#   ✓ IModelDoc2.InsertFeatureReplaceFace()                   0 参 · void     → T609 替换面
#   ✓ IModelDoc2.InsertRadiateSurface(Distance, FlipDir, TangentPropagate)    → 辐射曲面（★ 本轮不做）
#   ✗ InsertTrimSurface                                       ★ **swapi 里查不到** → T607（★ 铁律 5）
#   ```
#
# 官方前置（★ 三条 md 的 `Remarks` 逐字）：
#   · `InsertPlanarRefSurface` ⇒ 「select the surface's **boundary entities** using
#     `IModelDocExtension::SelectByID2` with **Marks of 1**」
#   · `InsertOffsetSurface` ⇒ 「Make the selections using `IModelDocExtension::SelectByID2`
#     **before** calling this method」
#   · `InsertFeatureReplaceFace` ⇒ 「select the faces to **replace** … with **Marks of 1** and
#     select the re[placement face] …」（★ 两个 mark 分工）
#
# ★ 判据统一（★ 规则 6）：**特征树多了新特征**。
# ★ 单位：`thickness_mm` 按**毫米**收、★ 在边界换算一次（规则 2）。


def insert_offset_surface_report(model, thickness_mm: float, *, reverse: bool = False) -> dict:
    """★ **等距曲面**（`IModelDoc2.InsertOffsetSurface` —— ★ **旧式方法**）。

    ★ 官方：`void InsertOffsetSurface(double Thickness, bool Reverse)`
      · `Thickness` ⇒ "Offset of surface from reference" · `Reverse` ⇒ 反向
      · `Remarks` ⇒ 「**Make the selections using `SelectByID2` before calling this method**」
    ★ 前置：★ **先选中一张曲面**（★ 本包装按对象选该体所有曲面面 —— ★ 与 `knit` 同款）。
    ★ 判据（规则 6）：★ **特征树多了新特征**。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    try:
        th = float(thickness_mm)
    except (TypeError, ValueError) as exc:
        return {"ok": False, "error": "thickness_mm 必须是数字：%s" % str(exc)[:100]}
    if not (th > 0.0):
        return {"ok": False, "stage": "validate", "error": "thickness_mm 必须 > 0；收到 %r" % th}
    before = feature_names(model)
    selected = _select_all_surface_faces(model, mark=0)
    if selected <= 0:
        return {"ok": False, "stage": "select", "faces_selected": 0,
                "error": "没选中任何曲面面（★ 官方要求**先选择**；★ 文件里要有曲面体）"}
    try:
        get_com_member(model, "InsertOffsetSurface", th * 0.001, bool(reverse))
    except Exception as exc:                                              # noqa: BLE001
        return {"ok": False, "stage": "call", "faces_selected": selected,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}
    after = feature_names(model)
    new = [n for n in after if n not in before]
    return {"ok": bool(new), "feature_name": (new[-1] if new else None), "new_features": new,
            "tree_before": len(before), "tree_after": len(after),
            "faces_selected": selected, "thickness_mm": th, "reverse": bool(reverse),
            "★": "判据 = **特征树多了新特征**（规则 6）；★ 走**旧式** `IModelDoc2.InsertOffsetSurface`"}


def insert_planar_ref_surface_report(model, *, sketch_name: str = "") -> dict:
    """★ **平面区域**（`IModelDoc2.InsertPlanarRefSurface` —— ★ **旧式方法** · **零参**）。

    ★ 官方：`bool InsertPlanarRefSurface()` ⇒ "True if the reference surface is created"
      · `Remarks` ⇒ 「select the surface's **boundary entities** using `SelectByID2` with
        **Marks of 1**」

    ★★★★ 2026-10-03（轮 517）**真机定下了「boundary entities」到底是什么** ✓
      · ⚠ 轮 516 我先试了**曲面体的边**（12 条 · mark=1）⇒ **0 增量**、`返回值 False`
      · ★ 轮 517 改试**草图**（一个闭合轮廓草图 · mark=1）⇒
        **`返回值 True` · 建成 `曲面-基准面1`** ✓
      ⇒ ★★ **故「boundary entities」在这条方法上指的是**草图**，不是曲面体的边** ——
        ★ 而官方那句 `Remarks` **两种读法都通**，★ 只能靠真机定 ⚠

    ★ 前置：★ **先按 mark=1 选一个闭合草图**（★ 特征按**名字**选是可行的 ——
      ★ 事实 32 的「没有名字」只对**实体**成立）。
    ★ 参数：`sketch_name` 留空 ⇒ ★ 用**最后一个**草图。
    ★ 判据（规则 6）：★ **特征树多了新特征**。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    before = feature_names(model)
    try:
        from sw_part import _get_sketch_name_candidates as _cands
    except Exception:                                                     # noqa: BLE001
        _cands = None
    names = [n for n in (feature_names(model) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    want = sketch_name or (names[-1] if names else "")
    try:
        model.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    picked = False
    if want:
        ext = get_com_member(model, "Extension")
        cands = _cands(want) if _cands else (want,)
        for cand in cands:
            try:
                if get_com_member(ext, "SelectByID2", cand, "SKETCH", False, 0, 0.0, 0.0, 0.0,
                                  False, 1, None, 0):
                    picked = True
                    break
            except Exception:                                             # noqa: BLE001
                continue
    try:
        sel = int(get_com_member(get_com_member(model, "SelectionManager"),
                                 "GetSelectedObjectCount2", -1) or 0)
    except Exception:                                                     # noqa: BLE001
        sel = -1
    if not picked and sel <= 0:
        return {"ok": False, "stage": "select", "sketch": want, "selected": sel,
                "error": "没选中草图（★ 真机：这条方法的 boundary entities 指**草图**，"
                         "★ 不是曲面体的边 —— 见本函数 docstring）"}
    try:
        ret = get_com_member(model, "InsertPlanarRefSurface")
    except Exception as exc:                                              # noqa: BLE001
        return {"ok": False, "stage": "call", "sketch": want, "selected": sel,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}
    after = feature_names(model)
    new = [n for n in after if n not in before]
    return {"ok": bool(new), "feature_name": (new[-1] if new else None), "new_features": new,
            "tree_before": len(before), "tree_after": len(after),
            "sketch": want, "selected": sel, "returned": repr(ret)[:30],
            "★": "判据 = **特征树多了新特征**（规则 6）；★ **真机：边界实体 = 草图**（轮 517）"}


def insert_replace_face_report(model) -> dict:
    """★ **替换面**（`IModelDoc2.InsertFeatureReplaceFace` —— ★ **旧式方法** · **零参**）。

    ★ 官方：`void InsertFeatureReplaceFace()`
      · `Returns` ⇒ "True if the edges match, false if not"
      · `Remarks` ⇒ 「select the faces to **replace** … with **Marks of 1** and select the
        re[placement face] …」⇒ ★★ **两个 mark 分工**

    ★★★★ 2026-10-03（轮 517）**真机把那个被截断的 mark 定了** ✓
      · ⚠ 轮 516 我先按「**实体面 mark=1 · 曲面面 mark=2**」试 ⇒ **0 增量**
      · ★ 轮 517 把两个 mark **调过来**（**曲面面 mark=1 · 实体面 mark=2**）⇒
        **建成 `替换面1`** ✓
      ⇒ ★★ **故分工是：★ 曲面面 = mark 1（**要替换掉的那个**）· 实体面 = mark 2（**替换成它**）** ——
        ★ 而这**与官方那句「要替换的面 mark 1」一致**：★ 要替换掉的正是**曲面**、★ 替换成的是**实体的面** ⚠
        （★ 我轮 516 的推断**把方向搞反了** —— ★ 而那是**推断**、★ 不是官方明文，故本轮才有必要试第二种）

    ★ 前置：★ **两张面**（★ 一张曲面面 = mark 1 · ★ 一张实体面 = mark 2）。
    ★ 判据（规则 6）：★ **特征树多了新特征**。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    before = feature_names(model)
    selected = _select_two_faces_for_replace(model)
    if selected < 2:
        return {"ok": False, "stage": "select", "faces_selected": selected,
                "error": "替换面至少要**两张面**（★ 一张实体面 + 一张曲面面）；只选到 %d 张" % selected}
    try:
        get_com_member(model, "InsertFeatureReplaceFace")
    except Exception as exc:                                              # noqa: BLE001
        return {"ok": False, "stage": "call", "faces_selected": selected,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}
    after = feature_names(model)
    new = [n for n in after if n not in before]
    return {"ok": bool(new), "feature_name": (new[-1] if new else None), "new_features": new,
            "tree_before": len(before), "tree_after": len(after), "faces_selected": selected,
            "★": "判据 = **特征树多了新特征**（规则 6）；⚠ 两个 mark 的分工是**推断**（官方只写了"
                 "「要替换的面 mark 1」）—— ★ 故本包装的选法**待真机确认**"}


def _select_all_surface_edges(model, mark: int = 1) -> int:
    """★ 把**曲面体的边**按对象选中（★ 回**选中数** —— 事实 8：只信回读计数）。"""
    from sw_connect import get_com_member as _get
    from sw_part import _select_com_object as _sel
    try:
        model.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    n = 0
    try:
        bodies = list(_get(model, "GetBodies2", 1, True) or [])
    except Exception:                                                     # noqa: BLE001
        bodies = []
    for b in bodies:
        try:
            edges = list(_get(b, "GetEdges") or [])
        except Exception:                                                 # noqa: BLE001
            continue
        for e in edges:
            try:
                if _sel(e, append=True, mark=mark):
                    n += 1
            except Exception:                                             # noqa: BLE001
                continue
    return n


def _select_two_faces_for_replace(model) -> int:
    """★ 给**替换面**选两张面：★ **曲面面 mark=1**（要替换掉的）· ★ **实体面 mark=2**（替换成它）。

    ★★ 这个分工是**真机定的**（★ 轮 517）：把两个 mark **调过来**才建成 `替换面1` ✓
      ⚠ 而轮 516 我按「实体=1 / 曲面=2」试 ⇒ **0 增量** —— ★ 那是**推断反了**。
    ★ 它与官方那句「select the faces to **replace** … with **Marks of 1**」一致：
      ★ **要替换掉的**是那张**曲面**（★ 而实体面是"替换成"的目标）。
    """
    from sw_connect import get_com_member as _get
    from sw_part import _select_com_object as _sel
    try:
        model.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    n = 0
    #: ★ **顺序与 mark 都以真机为准**（轮 517）：曲面体(1) ⇒ mark 1；实体(0) ⇒ mark 2
    for body_type, mark in ((1, 1), (0, 2)):
        try:
            bodies = list(_get(model, "GetBodies2", body_type, True) or [])
        except Exception:                                                 # noqa: BLE001
            bodies = []
        for b in bodies[:1]:
            try:
                faces = list(_get(b, "GetFaces") or [])
            except Exception:                                             # noqa: BLE001
                continue
            if faces:
                try:
                    if _sel(faces[0], append=True, mark=mark):
                        n += 1
                except Exception:                                         # noqa: BLE001
                    pass
    return n


# ── B6 / T607：**剪裁曲面**（`IFeatureManager.PreTrimSurface` + `PostTrimSurface`） ──────
# ★★★★ 2026-10-03（轮 519）★ 补 T607 —— ★ 而**它的真名是上一轮才找到的** ⚠
#
# ★ **上一轮（518）的悬案与解答**：轮 516/518 我按 `InsertTrimSurface` 查 ⇒ **swapi 里查不到**
#   （★ 当时按铁律 5 记了「查不到」）。★ 而轮 518 从**类型库 dump** 里发现 `IModelDoc2` 上有：
#   ```
#   PreTrimSurface   arity=1  (BMutualTrimIn)
#   PostTrimSurface  arity=1  (BSewSurfaceIn)
#   ```
#   ⇒ ★★ **故真名不是 `InsertTrimSurface`，而是这一对**（★ **两段式**）✓
#   ⚠ **教训**：铁律 5 的「查不到」应当**限定在查过的名字**上 ——
#     ★ 我查的是**猜的名字**，★ 而**没有穷举** `TrimSurface` 那一族。
#
# ★ 官方三源（★ 铁律 4）—— ★★ **而这里 md 与 CHM 的分工特别典型**：
#   · `C:\swapi\types\IModelDoc2\{Pre,Post}TrimSurface.md` ⇒ 只给了签名与
#     「`BMutualTrimIn`: **No description**」（★ **四个参数一个描述都没有**）⚠
#   · **CHM**（`IFeatureManager~PreTrimSurface.html`）⇒ ★★ **逐字给了四个参数的语义**：
#     · `BMutualTrimIn` ⇒ "True to use the selected intersecting surfaces as the trimming
#       surfaces (**mutual**), false to use the selected surface, plane, or sketch as the
#       **trim tool (standard)**"
#     · `BSplitSystemIn` ⇒ "True to let SOLIDWORKS determine which surfaces to trim,
#       false to trim all possible surfaces"
#     · `BSplitLinearIn` ⇒ "False to naturally extend any trims along the intersecting surfaces,
#       true to extend any trims **linearly**"
#     · `BRemovePickedIn` ⇒ "True to **remove** the selected surfaces, false to **keep**"
#     ⇒ ★★ 「**Sets the trimming options before trimming**」✓
#   · `IFeatureManager.PostTrimSurface(BSewSurfaceIn)` ⇒ "True to **sew** the resulting
#     trimmed surfaces, false to not"
#   · 类型库（第 3 源）给 **arity 与方向**：`IFeatureManager.PreTrimSurface` ⇒
#     `(BMutualTrimIn, BSplitSystemIn, BSplitLinearIn, BRemovePickedIn, Retval)` ⇒ **4 个 in**
#     ★（★ 而 `IModelDoc2` 那两个各**只有 1 个 in** ⇒ ★ 故**新版参数更全**、★ 本包装走新版）
#
# ★ 流程（★ 两段式）：**选中「要剪裁的面」+「剪裁工具」** ⇒ `PreTrimSurface(4 布尔)`
#   ⇒ `PostTrimSurface(BSewSurfaceIn)`。
# ★ 判据（★ 规则 6）：**特征树多了新特征**。


def trim_surface_report(model, *, mutual: bool = True, split_system: bool = True,
                        split_linear: bool = False, remove_picked: bool = False,
                        sew: bool = False) -> dict:
    """★ **剪裁曲面**（`IFeatureManager.PreTrimSurface` + `PostTrimSurface` —— ★ **两段式**）。

    ★★ 参数语义（★ **CHM 逐字**；★ 而 swapi 的 md 里那四个**全是 `No description`** ⚠）：
    ```
    mutual=True  用选中的**相交面互为剪裁**（mutual）
    mutual=False 用选中的面 / 基准面 / 草图作**剪裁工具**（standard）
    split_system  True 让 SW 自己判断剪哪些；False 剪所有可能的
    split_linear  True **线性延伸**；False 自然延伸
    remove_picked True **移除**选中面；False **保留**
    sew           True 把结果**缝合**
    ```

    ★ 前置：★ **先选中「要剪裁的面」与「剪裁工具」**（★ 本包装按对象选 —— ★ 事实 32：
      实体没有名字）。
    ★ 判据（规则 6）：★ **特征树多了新特征**（★ 由 `PostTrimSurface` 那步产生）。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    before = feature_names(model)
    selected = _select_all_surface_faces(model, mark=0)
    if selected <= 0:
        return {"ok": False, "stage": "select", "faces_selected": 0,
                "error": "没选中任何曲面面（★ 剪裁要有**两张**相交曲面：一张被剪、一张作工具）"}
    fm = get_com_member(model, "FeatureManager")
    pre = None
    try:
        pre = get_com_member(fm, "PreTrimSurface", bool(mutual), bool(split_system),
                             bool(split_linear), bool(remove_picked))
    except Exception as exc:                                              # noqa: BLE001
        return {"ok": False, "stage": "PreTrimSurface", "faces_selected": selected,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}
    post = None
    try:
        post = get_com_member(fm, "PostTrimSurface", bool(sew))
    except Exception as exc:                                              # noqa: BLE001
        return {"ok": False, "stage": "PostTrimSurface", "faces_selected": selected,
                "pre_returned": repr(pre)[:40],
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}
    after = feature_names(model)
    new = [n for n in after if n not in before]
    return {"ok": bool(new), "feature_name": (new[-1] if new else None), "new_features": new,
            "tree_before": len(before), "tree_after": len(after), "faces_selected": selected,
            "mutual": bool(mutual), "split_system": bool(split_system),
            "split_linear": bool(split_linear), "remove_picked": bool(remove_picked),
            "sew": bool(sew),
            "pre_returned": repr(pre)[:40], "post_returned": repr(post)[:40],
            "★": "判据 = **特征树多了新特征**（规则 6）；★ **两段式**：PreTrimSurface(4 布尔) "
                 "⇒ PostTrimSurface(sew)；★ 参数语义取自 **CHM**（md 里四个参数都是 No description）"}


# ── ★ 曲面**切除**（`IFeatureManager.InsertCutSurface`）—— 与"剪裁曲面"是**两件事** ──────
# ★★★★ 2026-10-03（轮 521）★ 从**通配筛**（事实 401 那条手法）里抓到的第二个候选。
#
#   ★★ **先纠正一个容易混的地方**：它**不是**"剪裁曲面"（那是 B6/T607 的
#     `PreTrimSurface`/`PostTrimSurface`，剪的是**曲面**）；
#     ★ `InsertCutSurface` 官方逐字是「**Inserts a surface-cut feature** using the
#     **preselected surface or plane**」⇒ ★★ **它是拿一个曲面/基准面去**切实体**** ✓
#     ⚠ 两者中文名都含"裁/切"、API 名都含 `CutSurface`/`TrimSurface`，★ **极易混**。
#
# 官方三源（★ 铁律 4）：
#   · `C:\swapi\types\IFeatureManager\InsertCutSurface.md`：
#     `Feature InsertCutSurface(bool Flip, int KeepPieceIndex, bool UseFeatScope,
#      bool UseAutoSelect, <Bodies>, <Error out>, <Retval out>)`
#     · `Flip` ⇒ "True to flip the direction of the cut"
#     · `KeepPieceIndex` ⇒ "**Piece to keep if there is ambiguity**"
#     · `UseFeatScope` ⇒ True 只切传给 `Bodies` 且与切面相交的体
#     · `UseAutoSelect` ⇒ True 自动切**所有**与切面相交的体
#     · `Bodies` ⇒ 具体体的数组；★「**Empty array indicating to cut all bodies**」
#   · `C:\swapi\types\IModelDoc2\InsertCutSurface.md` ⇒ **Obsolete**，继任者是 `IFeatureManager` 那个
#   · 类型库（第 3 源）给 arity 与方向：`IFeatureManager.InsertCutSurface` ⇒
#     `(Flip, KeepPieceIndex, UseFeatScope, UseAutoSelect, Bodies, Error(out), Retval(out))`
#     ⇒ ★ **5 个 in + 2 个 out**（★ 与 md 一致）✓
#
# ★ 前置：★ 官方说「using the **preselected** surface or plane」⇒ ★ **先选中一个面或基准面**。
# ★ 判据（★ 规则 6）：**特征树多了新特征**。


def cut_surface_report(model, *, flip: bool = False, keep_piece_index: int = 0,
                       use_feat_scope: bool = False, use_auto_select: bool = True) -> dict:
    """★ **曲面切除**（`IFeatureManager.InsertCutSurface`）—— ★ 拿选中的面/基准面**切实体**。

    ⚠★ **别与"剪裁曲面"混**：那个是 `PreTrimSurface`/`PostTrimSurface`（剪**曲面**）；
      ★ 本条是**曲面切除**（切**实体**）—— ★ 官方逐字「Inserts a **surface-cut** feature」。

    ★ 参数（★ 官方逐字）：
      · `flip` ⇒ 反向 · `keep_piece_index` ⇒ **有歧义时留哪一块**
      · `use_feat_scope` ⇒ 只切传给 `Bodies` 的体 · `use_auto_select` ⇒ 自动切**所有**相交体
    ★ 前置：★ **先选中一个曲面或基准面**（官方：「using the **preselected** surface or plane」）。
    ★ 判据（规则 6）：★ **特征树多了新特征**。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    before = feature_names(model)
    #: ★ 试两种选区：① 曲面面（mark=0）② 基准面（按名字选）
    picked = {"surface_faces": 0, "plane": None}
    try:
        model.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    picked["surface_faces"] = _select_all_surface_faces(model, mark=0)
    if picked["surface_faces"] <= 0:
        ext = get_com_member(model, "Extension")
        for plane in ("\u524d\u89c6\u57fa\u51c6\u9762", "Front Plane", "\u4e0a\u89c6\u57fa\u51c6\u9762",
                      "Top Plane", "\u53f3\u89c6\u57fa\u51c6\u9762", "Right Plane"):
            try:
                if get_com_member(ext, "SelectByID2", plane, "PLANE", False, 0, 0.0, 0.0, 0.0,
                                  False, 0, None, 0):
                    picked["plane"] = plane
                    break
            except Exception:                                             # noqa: BLE001
                continue
    try:
        sel = int(get_com_member(get_com_member(model, "SelectionManager"),
                                 "GetSelectedObjectCount2", -1) or 0)
    except Exception:                                                     # noqa: BLE001
        sel = -1
    if sel <= 0:
        return {"ok": False, "stage": "select", "selected": sel, "picked": picked,
                "error": "没选中任何面或基准面（★ 官方：这条要用 **preselected** surface or plane）"}
    fm = get_com_member(model, "FeatureManager")
    ret = None
    #: ★★ 2026-10-03（轮 521）**真机栽在这里、而它正是事实 390 那条定则的用例** ⚠
    #:   我第一版按「**5 个 in**」调（★ 依据是事实 397：类型库的 arity 含末尾 out ⇒ pywin32 侧不传）
    #:   ⇒ 真机回 **`非选择性的参数`**（`DISP_E_PARAMNOTOPTIONAL` = **"某个参数没给"**）。
    #:   ★★ **真因**：这条方法有 **两个 out**（`Error` 与 `Retval`）——
    #:     ★ 而**事实 397 那条"不传末尾 out"只适用于末尾只有 `Retval` 的情形**；
    #:     ★ 这里有 **中间那个 `Error`**，★ 它**必须占位** ⇒ ★★ **故要传 7 个** ✓
    #:   ★ 用 **`out_i4()`**（★ **`Error` 是错误码 ⇒ `VT_BYREF|VT_I4`**）与
    #:     **`out_dispatch()`**（★ **`Retval` 是 Feature ⇒ `VT_BYREF|VT_DISPATCH`**）把两个 out 位置填上。
    #:   ⚠ **我第一版两个都用了 `out_dispatch()`** ⇒ 真机回
    #:     **`类型不匹配`（位置 6）** —— ★★ **而那正好指在第 7 个参数（`Error`）上**：
    #:     ★ 一个**错误码**位置被塞了 Dispatch 容器 ⇒ ★ 两个错码**各说了一半**
    #:     （`非选择性的参数` 说"少给了"、`类型不匹配 位置 6` 说"第 7 个给错了"）✓
    #:   ★ 而那是**事实 390 定则**（见 `DISP_E_PARAMNOTOPTIONAL` ⇒ **先数参数个数**）的正当执行。
    err_out = None
    ret_out = None
    try:
        from sw_connect import out_dispatch as _od, out_i4 as _oi4
        err_out = _oi4()
        ret_out = _od()
    except Exception:                                                     # noqa: BLE001
        pass
    attempts = []
    try:
        ret = get_com_member(fm, "InsertCutSurface", bool(flip), int(keep_piece_index),
                             bool(use_feat_scope), bool(use_auto_select), [],
                             err_out, ret_out)
        attempts.append("7 \u53c2\uff085 in + out_i4 + out_dispatch\uff09")
    except Exception as exc:                                              # noqa: BLE001
        attempts.append("7 \u53c2\uff085 in + out_i4 + out_dispatch\uff09 \u21d2 %s: %s"
                        % (type(exc).__name__, str(exc)[:90]))
        #: \u2605 \u56de\u9000\uff1a\u53ea\u4f20 **5 \u53c2**\uff08\u2605 \u4e07\u4e00\u5b83\u771f\u7684\u53ea\u8981 5 \u4e2a\uff09
        try:
            ret = get_com_member(fm, "InsertCutSurface", bool(flip), int(keep_piece_index),
                                 bool(use_feat_scope), bool(use_auto_select), [])
            attempts.append("5 \u53c2\uff08\u56de\u9000\uff09")
        except Exception as exc2:                                         # noqa: BLE001
            attempts.append("5 \u53c2\uff08\u56de\u9000\uff09 \u21d2 %s: %s"
                            % (type(exc2).__name__, str(exc2)[:90]))
            return {"ok": False, "stage": "call", "selected": sel, "picked": picked,
                    "attempts": attempts,
                    "error": "%s: %s" % (type(exc2).__name__, str(exc2)[:220])}
    after = feature_names(model)
    new = [n for n in after if n not in before]
    return {"ok": bool(new), "feature_name": (new[-1] if new else None), "new_features": new,
            "tree_before": len(before), "tree_after": len(after), "selected": sel,
            "picked": picked, "flip": bool(flip), "keep_piece_index": int(keep_piece_index),
            "use_feat_scope": bool(use_feat_scope), "use_auto_select": bool(use_auto_select),
            "attempts": attempts, "returned": repr(ret)[:40],
            "★": "判据 = **特征树多了新特征**（规则 6）；★ 它是**曲面切除**（切实体），"
                 "★ 不是「剪裁曲面」（剪曲面）；★ 参数要 **7 个**（5 in + 2 out —— 事实 390）"}
