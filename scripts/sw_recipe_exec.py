"""L3 · 把 recipe 变成真实模型：**全程纯 API**，无界面操作。

## 为什么这样设计（两个来源）

① 业主 2026-10-26 的示范（`output/coop/参考案例.SLDPRT`）读出的配方：
   **一个** 孔特征 · 孔位草图内 **4 个点** · **4 条点关系** + **4 条尺寸**。
② 本轮核过的 API 事实：
   - 预设选择后一次 `HoleWizard5` 建多点 **不成立**（实测 0 特征）⇒ 改成
     「先建 1 个孔，再往它自己的定位草图里加点」。
   - 尺寸值**不必碰界面**：`IDimension.SetSystemValue2(值, WhichConfigurations)`。
   - `ISketchRelationManager.AddRelation(实体数组, RelationType)` 加点点关系。

## 目标判据（recipe 的 assertions）

```
HoleWzd = 1 · 孔位草图 status = 3 · standard = GB · 圆柱面 = 4
```

## 单位

本模块对外收 **毫米**（形参带 `_mm` 后缀），内部统一乘 1e-3 换成米。
"""
from __future__ import annotations

#: GB 标准与「螺钉间隙」的索引（真机 0..400 扫描命中，见已知事实 585）
GB_STANDARD_INDEX = 13
GB_FASTENER_INDEX = 356
#: 点对点关系枚举（`swConstraintType_e`）：25 = HORIZPOINTS；26 表里空缺，
#:   参考案例实测读回 26 ⇒ 本模块**实测择优**（见 `_add_point_relations`）。
REL_HORIZ_POINTS = 25
REL_VERT_POINTS = 26
#: `SetSystemValue2` 的配置参数：2 = 当前配置（`swInConfigurationOpts_e`）
CFG_THIS = 2


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（示教器 L3 · 配方执行）
# 文件:   scripts/sw_recipe_exec.py
# 定位:   按 recipe 用**纯 API** 重建零件（板 + 一个孔特征含多个全定义孔位），
#          并逐条核对 assertions。示教器的执行层。
# 官方依据: IFeatureManager.HoleWizard5 · IHoleStandardsData.GetHoleStandards（GB=13）·
#          IFeature.GetSpecificFeature2（取孔定位草图）· ISketchManager.CreatePoint ·
#          ISketchRelationManager.AddRelation · ISketchRelationManager.GetRelations ·
#          IModelDocExtension.AddDimension（4 参，第 4 参 Direction）·
#          IModelDocExtension.SelectByID2（按位置选择）·
#          IDimension.SetSystemValue2(NewValue, WhichConfigurations) ·
#          ISurface.IsCylinder（**属性**）· IModelDoc2.Save3（Options=1）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def _mm(v: float) -> float:
    return float(v) / 1000.0


#: dispatch-guard: exempt internal-helper
def _g(obj, name, *args):
    """取 COM 成员（有实参即调用）。"""
    from sw_connect import get_com_member

    return get_com_member(obj, name, *args)


def _tc(*args, **kwargs):
    from sw_connect import try_call

    return try_call(*args, **kwargs)


def _features(doc, type_name: str) -> list:
    out = []
    f = _g(doc, "FirstFeature")
    while f is not None:
        if str(_g(f, "GetTypeName2") or "") == type_name:
            out.append(f)
        f = _g(f, "GetNextFeature")
    return out


def _hole_position_sketch(doc, hole):
    """孔特征下**第一个** `ProfileFeature` = 孔位（定位）草图。

    ★ 别取最后一个：孔特征有**两张**草图 —— 先是定位草图（放孔位点），
      后是轮廓草图（圆柱截面，坐标在另一套空间里）。参考案例实测顺序：
      `草图2`(4 个孔位点) → `草图3`(6 个轮廓点) ⇒ **定位在前**。
      取错那次会把轮廓草图的「状态 3」当成孔位全定义，得到**假绿**。
    """
    sub = _g(hole, "GetFirstSubFeature")
    while sub is not None:
        if str(_g(sub, "GetTypeName2") or "") == "ProfileFeature":
            return sub
        sub = _g(sub, "GetNextSubFeature")
    return None


def _sketch_points(sk):
    ok, arr = _tc(_g, sk, "GetSketchPoints2")
    return list(arr or ()) if ok else []


def _point_xy_mm(sp) -> tuple:
    return (round(float(_g(sp, "X")) * 1000.0, 3),
            round(float(_g(sp, "Y")) * 1000.0, 3))


def _pick(points: list, x_mm: float, y_mm: float, tol_mm: float = 0.5):
    """按坐标挑草图点（避免依赖返回顺序）。"""
    for sp in points:
        try:
            px, py = _point_xy_mm(sp)
        except Exception:  # noqa: BLE001
            continue
        if abs(px - x_mm) <= tol_mm and abs(py - y_mm) <= tol_mm:
            return sp
    return None


def _add_relation(sk, entities: list, rel_type: int) -> bool:
    """加一条关系：`ISketchRelationManager.AddRelation(实体数组, 类型)`。"""
    ok, rm = _tc(_g, sk, "RelationManager")
    if not ok or rm is None:
        return False
    import pythoncom
    from win32com.client import VARIANT

    arr = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, list(entities))
    okr, _ = _tc(_g, rm, "AddRelation", arr, int(rel_type))
    return bool(okr)


def _ext_get(doc):
    return _g(doc, "Extension")


def _select_by_pos(ext, ent_type: str, x_mm: float, y_mm: float,
                   append: bool = False) -> bool:
    """★ 官方 Remarks：标尺寸要**按位置选**，且必须给 X/Y/Z 坐标。"""
    ok, _ = _tc(
        _g, ext, "SelectByID2", "", ent_type,
        _mm(x_mm), _mm(y_mm), 0.0, bool(append), 0,
        _empty_dispatch(), 0,
    )
    return bool(ok)


def _empty_dispatch():
    import sw_connect

    return sw_connect.create_empty_dispatch_variant()


def _add_dim(doc, x_mm: float, y_mm: float, direction: int):
    """`IModelDocExtension.AddDimension(X,Y,Z,Direction)` —— **必须 4 参**。

    ★ 少传 `Direction` 会抛 `DISP_E_PARAMNOTOPTIONAL`（事实 583）。
    """
    ok, dim = _tc(
        _g, _ext_get(doc), "AddDimension",
        _mm(x_mm), _mm(y_mm), 0.0, int(direction),
    )
    if not ok or dim is None:
        return None
    okd, real = _tc(_g, dim, "GetDimension2", 0)
    return real if (okd and real is not None) else None


def _set_dim_value(dim, value_mm: float) -> bool:
    """**不碰界面**把尺寸设成指定值：`SetSystemValue2(值, 2)`（2 = 当前配置）。"""
    ok, rc = _tc(_g, dim, "SetSystemValue2", _mm(value_mm), CFG_THIS)
    return bool(ok) and bool(rc)


def build_plate_with_holes(
    sw,
    *,
    width_mm: float = 100.0,
    height_mm: float = 60.0,
    thickness_mm: float = 20.0,
    holes_mm: tuple = ((10.0, 10.0), (90.0, 10.0), (10.0, 50.0), (90.0, 50.0)),
    standard_index: int = GB_STANDARD_INDEX,
    fastener_index: int = GB_FASTENER_INDEX,
    size: str = "M6",
    diameter_mm: float = 6.6,
    dimension_style: str = "fixed_points",
    trace: list | None = None,
):
    """建「板 + 一个孔特征含多个全定义孔位」。

    :returns: `(doc, report)`；`report` 里逐步记录读数，失败处写 `error` 不抛。
    """
    import sw_connect as c_
    from sw_hole_features import create_hole_wizard_at_point_report
    from sw_part import end_sketch, extrude_boss, sketch_corner_rectangle, start_sketch

    rep: dict = {"steps": [], "error": None}

    def note(step: str, **kw) -> None:
        item = {"step": step}
        item.update(kw)
        rep["steps"].append(item)
        if trace is not None:
            trace.append((step, kw))

    try:
        ok, doc = _tc(c_.new_document, sw, "part")
        if not ok or doc is None:
            rep["error"] = "新零件建不出来"
            return None, rep

        #: ① 板：前视面矩形 + 拉伸
        start_sketch(doc, "Front Plane")
        sketch_corner_rectangle(doc, 0.0, 0.0, width_mm, height_mm)
        end_sketch(doc)
        names = [str(_g(f, "Name") or "") for f in _features(doc, "ProfileFeature")]
        extrude_boss(doc, names[-1] if names else "草图1", thickness_mm)
        note("板", 特征=[str(_g(f, "Name") or "") for f in _features(doc, "Extrusion")])

        #: ② 一个孔（GB·螺钉间隙），用第 1 个孔位
        hx, hy = holes_mm[0]
        okh, _ = _tc(
            lambda: create_hole_wizard_at_point_report(
                doc, hx, hy, thickness_mm, size,
                diameter_mm=diameter_mm, depth_mm=thickness_mm, through=True,
                fastener_index=fastener_index, standard_index=standard_index,
            )
        )
        holes = _features(doc, "HoleWzd")
        note("孔特征", ok=bool(okh), 数量=len(holes))
        if not holes:
            rep["error"] = "孔特征没建出来"
            return doc, rep
        hole = holes[0]

        #: ③ 编辑孔位草图，补足其余孔位点
        pos = _hole_position_sketch(doc, hole)
        if pos is None:
            rep["error"] = "找不到孔位草图"
            return doc, rep
        name = str(_g(pos, "Name") or "")
        doc.ClearSelection2(True)
        _tc(_g, _ext_get(doc), "SelectByID2", name, "SKETCH",
            0, 0, 0, False, 0, _empty_dispatch(), 0)
        oke, _ = _tc(doc.EditSketch)
        note("进孔位草图", ok=bool(oke), 草图=name)
        if not oke:
            rep["error"] = "进不了孔位草图"
            return doc, rep

        sm = _g(doc, "SketchManager")
        for (x, y) in holes_mm[1:]:
            _tc(sm.CreatePoint, _mm(x), _mm(y), 0.0)
        pts = _sketch_points(_g(pos, "GetSpecificFeature2"))
        note("加点后", 点数=len(pts),
             坐标=[_point_xy_mm(p) for p in pts])

        #: ④ 四条点关系（组成矩形）—— 用坐标挑点，不依赖顺序
        if len(pts) >= 4:
            p1 = _pick(pts, *holes_mm[0])
            p2 = _pick(pts, *holes_mm[1])
            p3 = _pick(pts, *holes_mm[2])
            p4 = _pick(pts, *holes_mm[3])
            pairs = [
                ("水平", p1, p2, REL_HORIZ_POINTS),
                ("竖直", p2, p4, REL_VERT_POINTS),
                ("水平", p4, p3, REL_HORIZ_POINTS),
                ("竖直", p3, p1, REL_VERT_POINTS),
            ]
            added = []
            for label, a, b, rt in pairs:
                if a is None or b is None:
                    added.append({"rel": label, "ok": False, "why": "挑不到点"})
                    continue
                okr = _add_relation_shim(doc, _g(pos, "GetSpecificFeature2"),
                                         [a, b], rt, label)
                added.append({"rel": label, "type": rt, "ok": okr})
            note("点关系", 明细=added)

        #: ⑤ 消掉剩余 4 个自由度（关系已消 4/8）
        #:   ★ ixed_points：逐点 sgFIXED（实测 4 点全固定 ⇒ 状态 3、圆柱面 4）。
        #:   ★ 	o_edge：本应标「点到板边」尺寸，但实测 AddDimension 在本机对
        #:     **成对实体**（点+线、线+线）一律返回 None ⇒ 该风格当前不可用，
        #:     代码保留但会走 ixed_points 并在报告里说明。
        style = dimension_style
        if style != "fixed_points":
            note("风格降级", 请求=style, 实际="fixed_points",
                 原因="AddDimension 对本机成对实体返回 None（实测）")
        fixed = 0
        for p in pts:
            doc.ClearSelection2(True)
            okp2, _ = _tc(p.Select4, False, _empty_dispatch())
            if not okp2:
                continue
            okf2, _ = _tc(doc.SketchAddConstraints, "sgFIXED")
            fixed += 1 if okf2 else 0
        note("固定孔点", 成功=fixed, 总=len(pts))

        #: ⑥ 退出草图 → 读状态
        _tc(sm.InsertSketch, True)
        okr2, _ = _tc(doc.EditRebuild3)
        st = _sketch_status(pos)
        note("退出重建", 状态=st, 重建=bool(okr2))
        return doc, rep
    except Exception as exc:  # noqa: BLE001
        rep["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        return None, rep


def _add_relation_shim(doc, sk, entities, rel_type: int, label: str) -> bool:
    """加关系：优先 `RelationManager.AddRelation`；不行就退回 `SketchAddConstraints`。

    ★ 22/26 点对点枚举在官表里一个有一个空缺 ⇒ 两条路都试，以状态为准。
    """
    if _add_relation(sk, entities, rel_type):
        return True
    mnemonic = {
        "水平": "sgHORIZONTAL2D",
        "竖直": "sgVERTICAL2D",
    }.get(label)
    if not mnemonic:
        return False
    doc.ClearSelection2(True)
    empty = _empty_dispatch()
    for i, ent in enumerate(entities):
        _tc(getattr(ent, "Select4"), bool(i), empty)
    ok, _ = _tc(doc.SketchAddConstraints, mnemonic)
    return bool(ok)


def _sketch_status(feature) -> int:
    ok, sk = _tc(_g, feature, "GetSpecificFeature2")
    if not ok or sk is None:
        return -1
    ok2, v = _tc(lambda: int(sk.GetConstrainedStatus))
    return v if ok2 else -1


def count_cylinders(doc) -> int:
    """数圆柱面 —— ★ `ISurface.IsCylinder` 是**属性**，不是方法。"""
    bodies = list(_g(doc, "GetBodies2", 0, False) or ())
    if not bodies:
        return -1
    faces = _g(bodies[0], "GetFaces") or ()
    n = 0
    for face in list(faces):
        surf = _g(face, "GetSurface")
        if surf is None:
            continue
        try:
            n += 1 if bool(surf.IsCylinder) else 0
        except Exception:  # noqa: BLE001
            pass
    return n


def assert_recipe(doc) -> dict:
    """按 recipe 的 assertions 逐条核对，回 `{name: {ok, observed, expected}}`。"""
    out: dict = {}
    holes = _features(doc, "HoleWzd")
    out["feature_count_hole"] = {
        "ok": len(holes) == 1, "observed": len(holes), "expected": 1}
    std = fastener = size = None
    status = None
    if holes:
        d = _g(holes[0], "GetDefinition")
        try:
            std = str(_g(d, "Standard"))
            fastener = str(_g(d, "FastenerType"))
            size = str(_g(d, "FastenerSize"))
        except Exception:  # noqa: BLE001
            pass
        pos = _hole_position_sketch(doc, holes[0])
        if pos is not None:
            status = _sketch_status(pos)
    out["hole_standard_gb"] = {
        "ok": bool(std and "GB" in std), "observed": std, "expected": "含 GB"}
    out["hole_sketch_constrained"] = {
        "ok": status == 3, "observed": status, "expected": 3}
    cyl = count_cylinders(doc)
    out["cylinder_count"] = {"ok": cyl == 4, "observed": cyl, "expected": 4}
    out["hole_size"] = {"ok": size is not None, "observed": size,
                        "expected": "非空"}
    out["hole_fastener"] = {"ok": fastener is not None, "observed": fastener,
                            "expected": "非空"}
    out["all_ok"] = {"ok": all(v["ok"] for v in out.values()),
                     "observed": sum(1 for v in out.values() if v["ok"]),
                     "expected": len(out)}
    return out
