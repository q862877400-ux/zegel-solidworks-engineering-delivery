

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
