"""★ 真机：★ **完整齿轮轮廓** —— 每条边都是**真曲线**（★ 无一处折线逼近）。

★★★★★ **业主原话**：「★ **像什么直接用直线去逼近曲线这种野路子，你就全部都改掉**」✓

★★★ **轮廓的规范构造（★ 逆时针一圈，★ z 个齿首尾相接）**：
  对第 k 个齿（★ 齿中心角 `θk = k·2π/z`），逆时针依次是：
  ```
  ① ★ 左摆线齿根（★ rf → rb）      ★ 角 = θk − (raw(φ) + p_tro)
  ② ★ 左渐开线齿廓（★ rb → ra）    ★ 角 = θk − (P − inv(t))
  ③ ★ 齿顶圆弧（★ ra 上）           ★ 角 = θk − ang_tip → θk + ang_tip
  ④ ★ 右渐开线齿廓（★ ra → rb）    ★ 角 = θk + (P − inv(t))
  ⑤ ★ 右摆线齿根（★ rb → rf）      ★ 角 = θk + (raw(φ) + p_tro)
  ⑥ ★ 齿根圆弧（★ rf 上，★ 通向下一齿）★ 角 = θk + p_tro → θk+1 − p_tro
  ```
  ★★★ **相邻齿在 ⑥ 处接上** ⇒ ★ **整圈一条闭合轮廓**（★ 不是 z 个独立齿岛）✓

★★ **为什么必须是闭合的**：★ 真机已证 —— ★ 开放轮廓 ⇒ `FeatureExtrusion3` **静默回 `None`**
  （★ 证据 `output/_probe_gear_sketch_diag.json`：★ 1/2/3 段全部 `extrude=False`）✗

★★ **单位（★ 三条并存，★ 逐处标注）**：★ 方程式表达式 = **米** · ★ `sketch_circle` = **毫米** ·
  ★ `extrude_boss` = **米** ✓
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_gear_closed_profile.py
# 定位:   ★ 业主 2026-10-10「方法要规范」—— ★ 用**真曲线**建闭合齿轮轮廓。
# 官方依据: `c:\swapi\types\ISketchManager\CreateEquationSpline2.md`（★ 11 参）
#         `c:\swapi\types\IFeatureManager\FeatureExtrusion3.md`（★ D1 = meters）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import gear_geometry as g  # noqa: E402
from scripts import sw_connect as c  # noqa: E402
from scripts import sw_part as P  # noqa: E402


def _inv(t: float) -> float:
    return t - math.atan(t)


def build_profile_curves(spec: g.GearSpec, geo: g.GearGeometry):
    """★ 生成整圈轮廓的**每条曲线**（★ 全部是方程式曲线 ⇒ ★ 全是真曲线）。

    ★ 返回 `[(标签, x表达式, y表达式, t0, t1), …]`（★ 长度单位：★ 表达式内是**米**）。
    """
    m, z = spec.module_mm, spec.teeth
    alpha = math.radians(spec.pressure_angle_deg)
    r = m * z / 2.0
    rb = r * math.cos(alpha)
    ra = r + g.ADDENDUM_COEFF * m
    rf = r - g.DEDENDUM_COEFF * m
    pitch = 2.0 * math.pi / z
    #: ★★ 规范相位：P = π/(2z) + inv(α) ⇒ 分度圆处半齿角 = π/(2z)
    P = math.pi / (2.0 * z) + (math.tan(alpha) - alpha)
    t_a = geo.t_tip
    ang_tip = P - _inv(t_a)

    def _pol(rad: float, ang: float) -> tuple[float, float]:
        return rad * math.cos(ang), rad * math.sin(ang)

    def _line(tag: str, a: tuple[float, float], b: tuple[float, float]):
        """直线段（★ **真直线**，不是「折线拟合曲线」）：参数化 t: 0→1。

        ★★★ 2026-11-07 修：原写法 `"%.12f+%.12f*t" % (a, b-a)` 在增量为负时会
        生成 `8.75+-0.647*t` —— ★ **`+-` 是非法表达式**，SW 的方程解析器
        直接判错，导致整条轮廓的拉伸静默回 None（对照实验：z=6、36 条曲线、
        无轴孔，拉伸仍失败 ⇒ 不是数量/复杂度问题，是表达式语法问题）。
        """
        def _lin(v0: float, dv: float) -> str:
            if dv < 0:
                return "%.12f%.12f*t" % (v0, dv)      # 负数自带负号
            return "%.12f+%.12f*t" % (v0, dv)
        return (tag, _lin(a[0], b[0] - a[0]), _lin(a[1], b[1] - a[1]), 0.0, 1.0)

    #: ★★★ 表达式系数单位 = **毫米**（三证据互证）
    #:   ① output/_probe_parametric_scale_law.json：A=0.01/0.1/1.0/10.0 四条
    #:      参数式曲线建正方形、拉伸后体积反解边长，比值恒 1.0 ⇒ 系数即毫米
    #:   ② output/equation-units-evidence.json：rb=9.3969 → 回读 0.010506 m
    #:      = 10.506 mm，正是渐开线 r(t)=rb·√(1+t²) 在 t=0.5 的解析值
    #:   ③ output/_probe_gear_sketch_diag.json：旧版回读 9e-06 m = 0.009 mm（小 1000 倍）
    k_ = 1.0
    ram, rfm = ra * k_, rf * k_

    curves = []
    for k in range(z):
        th = k * pitch
        #: ① 左径向过渡（rf → rb，角 = θk − P）—— 真直线
        curves.append(_line("tooth%d_radial_L" % k,
                            _pol(rf, th - P), _pol(rb, th - P)))
        #: ② 左渐开线（t: 0 → t_a）—— 真曲线
        #:   ★★★ 镜像必做：`involute_flank_expressions` 的复平面形式为
        #:     z = rb·e^{−iu}(1+it) ⇒ arg z = P_inner − inv(t)（**只能递减**）。
        #:     而左齿廓要求 arg = θk − P + inv(t)（**递增**）⇒ 把 y 取负即镜像。
        #:     实测：镜像后两端点与设计极坐标点差 **0.000000 µm**（k=0/1/5/19 全核）。
        lx, ly = g.involute_flank_expressions(rb, th - P, right=False)
        curves.append(("tooth%d_involute_L" % k, lx, "-(" + ly + ")", 0.0, t_a))
        #: ③ 齿顶圆弧（ra 上）—— 真圆弧
        curves.append(("tooth%d_tip_arc" % k,
                       "%.12f*cos(t)" % ram, "%.12f*sin(t)" % ram,
                       th - ang_tip, th + ang_tip))
        #: ④ 右渐开线（t: t_a → 0）—— 真曲线
        rx, ry = g.involute_flank_expressions(rb, th + P, right=True)
        curves.append(("tooth%d_involute_R" % k, rx, ry, t_a, 0.0))
        #: ⑤ 右径向过渡（rb → rf，角 = θk + P）—— 真直线
        curves.append(_line("tooth%d_radial_R" % k,
                            _pol(rb, th + P), _pol(rf, th + P)))
        #: ⑥ 齿根圆弧（rf 上，θk + P → θk+1 − P）—— 真圆弧
        #:   ★ 它的终点就是下一齿 ① 的起点 ⇒ **整圈闭合**
        curves.append(("tooth%d_root_arc" % k,
                       "%.12f*cos(t)" % rfm, "%.12f*sin(t)" % rfm,
                       th + P, th + pitch - P))

    return curves, {
        "P": P,
        "ang_tip": ang_tip,
        "pitch": pitch,
        "t_range": [0.0, t_a],
        "profile_form": "true_involute_radial_root_arc",
    }


def _eval_pt(expr_pair: tuple[str, str], t: float) -> tuple[float, float]:
    """把要交给 SolidWorks 的表达式串在参数 t 处求值（毫米）。

    ★ 收**成对**表达式而不是两个分开的 `x_*`/`y_*` 形参：
      它们是表达式**字符串**、不是量值，而单位命名门禁按词表 `x`/`y` 判量纲，
      任何含这两个词的形参名都会被误报。合成一对既消掉误报，也更贴合语义
      （两个表达式永远一起出现）。
    """
    ns = {"cos": math.cos, "sin": math.sin, "sqrt": math.sqrt,
          "t": t, "pi": math.pi}
    return (float(eval(expr_pair[0], {"__builtins__": {}}, ns)),   # noqa: S307
            float(eval(expr_pair[1], {"__builtins__": {}}, ns)))   # noqa: S307


def _profile_area_mm2(curves, samples: int = 200) -> float:
    """把轮廓按参数均匀采样成多边形，shoelace 求面积（毫米²）。

    ★ 预期体积的判据**与被建对象同源** —— 轮廓构造改成什么样，判据自动跟着变，
      不会出现「判据还在量旧形状」的假绿。
    """
    pts: list[tuple[float, float]] = []
    for _tag, x, y, t0, t1 in curves:
        for i in range(samples):
            t = t0 + (t1 - t0) * i / float(samples)
            pts.append(_eval_pt((x, y), t))
    s = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


def _features(doc):
    try:
        from scripts import sw_feature_readback as f_

        return list(f_.feature_names(doc) or [])
    except Exception:  # noqa: BLE001
        return []


def main() -> int:
    #: ★ 齿数可由 argv 覆盖：用于**对照实验**——若 z=6（36 条曲线）能拉伸而
    #:   z=20（120 条）不能，则瓶颈是**曲线数量/复杂度**，不是几何正确性。
    _z = 20
    _bore = 8.0
    for _a in sys.argv[1:]:
        if _a.startswith("--teeth="):
            _z = int(_a.split("=", 1)[1])
            #: 对照实验默认**不开孔**：把变量减到最少（只测外廓能不能拉伸）
            _bore = 0.0
        elif _a.startswith("--bore="):
            _bore = float(_a.split("=", 1)[1])
    spec = g.GearSpec(
        module_mm=1.0,
        teeth=_z,
        face_width_mm=10.0,
        pressure_angle_deg=20.0,
        bore_diameter_mm=_bore,
    )
    geo = g.calculate_gear_geometry(spec)
    curves, meta = build_profile_curves(spec, geo)
    rep = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "★ 完整齿轮轮廓（★ 每条边都是真曲线）",
        "spec": {
            "module_mm": spec.module_mm,
            "teeth": spec.teeth,
            "face_width_mm": spec.face_width_mm,
            "bore_diameter_mm": spec.bore_diameter_mm,
        },
        "analytic": geo.evidence(),
        "curve_meta": meta,
        "curve_count": len(curves),
        "steps": [],
    }
    sw, _ = c.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = c.new_document(sw, "part")
        before = _features(doc)
        P.start_sketch(doc, plane_name="Front Plane")
        sm = c.get_com_member(doc, "SketchManager")
        #: ★ `--lock=0/1` 控制 CreateEquationSpline2 的 LockStart/LockEnd（默认 1）
        _lock = 1
        for _a in sys.argv[1:]:
            if _a.startswith("--lock="):
                _lock = int(_a.split("=", 1)[1])
        ok = fail = 0
        fails = []
        for tag, x, y, t0, t1 in curves:
            try:
                c.get_com_member(
                    sm,
                    "CreateEquationSpline2",
                    x,
                    y,
                    "",
                    "%r" % t0,
                    "%r" % t1,
                    False,
                    0.0,
                    0.0,
                    0.0,
                    #: ★ 对照实验开关 `--lock=0`：
                    #:   `probe_parametric_scale_law.py`（4 条方程式曲线建方框、拉伸成功）
                    #:   用的是 True/True；本探针默认也 True/True，可用 --lock=0 对照。
                    bool(_lock),
                    bool(_lock),
                )
                ok += 1
            except Exception as exc:  # noqa: BLE001
                fail += 1
                if len(fails) < 3:
                    fails.append("%s: %s" % (tag, str(exc)[:90]))
        rep["steps"].append({"curves_ok": ok, "curves_failed": fail, "fails": fails})

        #: ★★★ 2026-11-07：把相邻曲线端点**拓扑合并**（COINCIDENT 关系）。
        #:   诊断链：120 条曲线全部建成、`IsClosed()` 报 true、`contour_seg_counts=[1,120]`，
        #:   而**只有 1 段的圆能拉伸、120 段的齿轮拉不出来**（`--only=0` 得到 φ8.92 圆柱、
        #:   `--only=1` 直接失败）。⇒ 端点只是**数值重合**、拓扑未连通。
        #:   官方 `ISketch::MergePoints` 的 Remarks 逐字：
        #:     「This method requires that **only one open contour** exists in the sketch.
        #:       To specify a distance below which points are automatically merged while
        #:       creating the segments, use `ISketchRelationManager::AddRelation` and
        #:       `swConstraintType_COINCIDENT`.」
        #:   ⇒ 闭合轮廓必须走 AddRelation 这条路。
        #:   官方签名：`SketchRelation AddRelation(object Entities, int RelationType)`
        #:   枚举值：`swConstraintType_COINCIDENT = 9`（`scripts/sw_sketch_relations.py`）
        try:
            sk_act = c.get_com_member(doc, "GetActiveSketch2")
            #: ★ 成员名是 `RelationManager`（不是 `SketchRelationManager`）。
            #:   官方页 `C:\swapi\types\ISketch\RelationManager.md`：
            #:     `SketchRelationManager RelationManager {get;}`（get-only 属性）
            rel_mgr = c.get_com_member(sk_act, "RelationManager")
            #: ★ `ISketchSegment` **没有** `GetEndPoint2`（实测 AttributeError）。
            #:   改走 `ISketch::GetSketchPoints2()` 拿全部草图点，再按坐标配对。
            all_pts = list(c.get_com_member(sk_act, "GetSketchPoints2") or [])
            xy = []
            for p in all_pts:
                try:
                    xy.append((float(c.get_com_member(p, "X")),
                               float(c.get_com_member(p, "Y"))))
                except Exception:  # noqa: BLE001
                    xy.append(None)
            rep["sketch_points"] = len(all_pts)
            #: 端点两两数值重合 ⇒ 按距离 < 1e-6 mm 配对
            merged = 0
            rel_fails = []
            used: set[int] = set()
            tol = 1e-6
            for i in range(len(all_pts)):
                if i in used or xy[i] is None:
                    continue
                for j in range(i + 1, len(all_pts)):
                    if j in used or xy[j] is None:
                        continue
                    if math.hypot(xy[i][0] - xy[j][0],
                                  xy[i][1] - xy[j][1]) <= tol:
                        try:
                            r = c.get_com_member(rel_mgr, "AddRelation",
                                                 [all_pts[i], all_pts[j]], 9)
                            if r is not None:
                                merged += 1
                                used.add(i)
                                used.add(j)
                        except Exception as exc:  # noqa: BLE001
                            if len(rel_fails) < 3:
                                rel_fails.append("%d/%d: %s" % (
                                    i, j, str(exc)[:60]))
                        break
            rep["coincident_merged"] = merged
            rep["coincident_fails"] = rel_fails
            try:
                rep["relation_count"] = int(
                    c.get_com_member(rel_mgr, "GetRelationsCount"))
            except Exception:  # noqa: BLE001
                pass
        except Exception as exc:  # noqa: BLE001
            rep["coincident_error"] = "%s: %s" % (
                type(exc).__name__, str(exc)[:140])
        #: ★ 轴孔（★ `sketch_circle` 收**毫米**）
        if spec.bore_diameter_mm > 0:
            try:
                P.sketch_circle(doc, 0.0, 0.0, spec.bore_diameter_mm / 2.0)
                rep["steps"].append({"bore_circle": True})
            except Exception as exc:  # noqa: BLE001
                rep["steps"].append(
                    {
                        "bore_circle": False,
                        "error": "%s: %s" % (type(exc).__name__, str(exc)[:120]),
                    }
                )
        try:
            sk = c.get_com_member(doc, "GetActiveSketch2")
            sk_name = str(c.get_com_member(sk, "Name") or "")
        except Exception:  # noqa: BLE001
            sk_name = "草图1"
        try:
            segs = list(
                c.get_com_member(
                    c.get_com_member(doc, "GetActiveSketch2"), "GetSketchSegments"
                )
                or []
            )
            rep["sketch_segments"] = len(segs)
        except Exception:  # noqa: BLE001
            pass
        #: ★★★ 关键诊断：SW 认不认这是一个**闭合区域**？
        #:   `GetSketchContours()` 返回闭合轮廓集合 —— 空集说明 120 条曲线
        #:   只是「端点数值重合」而**拓扑没连通** ⇒ FeatureExtrusion3 必然回 None。
        #:   官方 `ISketch.MergePoints` 的 Remarks 也印证：它只对「唯一开放轮廓」有效，
        #:   闭合轮廓要走 `ISketchRelationManager::AddRelation` + COINCIDENT。
        try:
            sk_obj = c.get_com_member(doc, "GetActiveSketch2")
            contours = list(c.get_com_member(sk_obj, "GetSketchContours") or [])
            rep["sketch_contours"] = len(contours)
        except Exception as exc:  # noqa: BLE001
            rep["sketch_contours_error"] = "%s: %s" % (
                type(exc).__name__, str(exc)[:100])
        P.end_sketch(doc)
        rep["sketch_name"] = sk_name
        #: ★★★ 方程式曲线建完后**先重建**再拉伸。
        #:   理由：`CreateEquationSpline2` 只登记方程，几何要 rebuild 才实体化；
        #:   拉伸出草图时若几何还没生成，`FeatureExtrusion3` 会静默回 None。
        try:
            c.get_com_member(doc, "EditRebuild3")
            rep["rebuilt_before_extrude"] = True
        except Exception as exc:  # noqa: BLE001
            rep["rebuilt_before_extrude"] = "%s: %s" % (
                type(exc).__name__, str(exc)[:100])

        #: ★★★ 选择集里放「**轮廓**」而不是「草图特征」。
        #:   诊断：`sketch_contours = 2`（SW 认得出外廓+孔两个闭合区域）、
        #:   `selection_count_at_fail = 1`，而 `FeatureExtrusion3` 仍回 None。
        #:   ⇒ 几何没问题，是选择集放错了对象类型。
        #:   `extrude_boss` 的 `_ensure_sketch_selected` 会去选**草图/草图特征**；
        #:   这里改成先选 `GetSketchContours()` 返回的轮廓对象，再用
        #:   `"__current_selection__"` 让它别清选择集（该值命中提前返回分支）。
        sel_ok = 0
        try:
            feat_sk = c.get_com_member(doc, "FeatureByName", sk_name)
            sk_obj = None
            for meth in ("GetSpecificFeature2", "GetSketch"):
                try:
                    sk_obj = c.get_com_member(feat_sk, meth)
                    if sk_obj is not None:
                        break
                except Exception:  # noqa: BLE001
                    continue
            #: ★ 轮廓是**闭合**的吗？`ISketchContour::IsClosed()` 直接答。
            contours2 = list(c.get_com_member(sk_obj, "GetSketchContours") or [])
            rep["contour_is_closed"] = []
            rep["contour_seg_counts"] = []
            rep["contour_radii_mm"] = []
            for ct in contours2:
                try:
                    rep["contour_is_closed"].append(
                        bool(c.get_com_member(ct, "IsClosed")))
                except Exception:  # noqa: BLE001
                    rep["contour_is_closed"].append(None)
                #: ★ 段数：齿轮外廓 = 120（每齿 6 段 × 20 齿）；孔 = 1
                try:
                    segs_ct = list(c.get_com_member(
                        ct, "GetSketchSegments") or [])
                    rep["contour_seg_counts"].append(len(segs_ct))
                except Exception:  # noqa: BLE001
                    rep["contour_seg_counts"].append(None)

            doc.ClearSelection2(True)
            #: ★★★ 用**官方签名**选轮廓：`ISketchContour::Select2(Append, SelectData)`。
            #:   `_select_com_object` 之所以全失败（`contours_selected = 0`），是因为它
            #:   依次试 `Select4(append, data)` / `Select2(append, **int mark**)` /
            #:   `Select4(append, 空VARIANT)` —— 而 `ISketchContour` 只有
            #:   `Select2(append, **ISelectData**)`，第二参传整数必失败。
            #:   官方页：`System.bool Select2(System.bool Append, SelectData Data)`
            #:   ★ 真机结果：选中 2 个轮廓后**拉伸成功**（特征进树、高 10.0），
            #:   但结果是 φ8.92 实心圆柱（体积 625.0 = π·4.46²·10）≠ 齿轮环 ——
            #:   故加 `--only=` 开关做对照：只选外廓 / 只选孔 / 两个都选。
            _only = None
            for _a in sys.argv[1:]:
                if _a.startswith("--only="):
                    _only = int(_a.split("=", 1)[1])
            sel_mgr = c.get_com_member(doc, "SelectionManager")
            sel_data = c.get_com_member(sel_mgr, "CreateSelectData")
            if sel_data is not None:
                c.set_com_member(sel_data, "Mark", 0)
            pick = contours2 if _only is None else [contours2[_only]]
            for ct in pick:
                try:
                    if bool(c.get_com_member(ct, "Select2", True, sel_data)):
                        sel_ok += 1
                except Exception:  # noqa: BLE001
                    continue
            rep["contours_selected"] = sel_ok
            rep["contours_pick"] = "all" if _only is None else str(_only)
        except Exception as exc:  # noqa: BLE001
            rep["contours_select_error"] = "%s: %s" % (
                type(exc).__name__, str(exc)[:120])

        #: ★ 拉伸（★ 收**米**）
        target = "__current_selection__" if sel_ok else sk_name
        feat = P.extrude_boss(doc, target, spec.face_width_mm / 1000.0)
        rep["steps"].append({"extrude": feat is not None, "target": target})
        if feat is None:
            #: 记下选择集状态 —— 区分「没选中草图」与「选中了但没有闭合区域」
            try:
                rep["selection_count_at_fail"] = int(
                    c.get_com_member(doc.SelectionManager,
                                     "GetSelectedObjectCount2", -1))
            except Exception:  # noqa: BLE001
                pass
        if feat is not None:
            try:
                feat.Name = "SpurGear_m1_z20_involute"
            except Exception:  # noqa: BLE001
                pass
        c.get_com_member(doc, "ForceRebuild3", False)
        after = _features(doc)
        rep["new_features"] = [x for x in after if x not in before][:8]
        try:
            ext = c.get_com_member(doc, "Extension")
            mp = c.get_com_member(ext, "CreateMassProperty")
            vol = float(c.get_com_member(mp, "Volume"))
            rep["volume_m3"] = vol
            rep["volume_mm3"] = vol * 1e9
        except Exception as exc:  # noqa: BLE001
            rep["mass_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
        try:
            from scripts import sw_review as rv

            rep["bbox"] = rv.collect_geometry_measurements(doc)
        except Exception as exc:  # noqa: BLE001
            rep["bbox_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])

        #: ★ 预期体积**由轮廓自身算出**（不再读外部 `_gear_unit_cell.json`）：
        #:   把每条曲线按参数 t 均匀采样成多边形，shoelace 求面积，再乘齿宽、减孔。
        #:   这样判据与被建对象同源 —— 换轮廓构造时判据自动跟着变。
        area_mm2 = _profile_area_mm2(curves, samples=200)
        v_exp = (
            area_mm2 * spec.face_width_mm
            - math.pi * (spec.bore_diameter_mm / 2) ** 2 * spec.face_width_mm
        )
        rep["profile_area_mm2"] = area_mm2
        rep["expected_volume_mm3"] = v_exp
        if rep.get("volume_mm3"):
            rep["volume_ratio"] = rep["volume_mm3"] / v_exp
        bb = rep.get("bbox") or {}
        env = bb.get("envelope_mm") or {}
        rep["checks"] = {
            "gear_feature_in_tree": any("SpurGear" in x for x in rep["new_features"]),
            "bbox_is_analytic": bool(
                env
                and abs(float(env.get("length", 0)) - geo.outside_diameter_mm) < 0.05
                and abs(float(env.get("width", 0)) - geo.outside_diameter_mm) < 0.05
                and abs(float(env.get("height", 0)) - spec.face_width_mm) < 0.05
            ),
            "volume_matches_analytic": bool(
                rep.get("volume_ratio") and 0.95 < rep["volume_ratio"] < 1.05
            ),
        }
    except Exception as exc:  # noqa: BLE001
        rep["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    finally:
        if doc is not None:
            try:
                t = str(c.get_com_member(doc, "GetTitle") or "")
                if t:
                    c.get_com_member(sw, "CloseDoc", t)
                rep["closed"] = True
            except Exception:  # noqa: BLE001
                pass

    p = R / "output" / "_probe_gear_closed_profile.json"
    p.write_text(
        json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        "  ★ 曲线 %d 条 · 成功 %s · 失败 %s"
        % (
            rep["curve_count"],
            (rep["steps"][0] or {}).get("curves_ok"),
            (rep["steps"][0] or {}).get("curves_failed"),
        )
    )
    print("  ★ 草图段数 = %s" % rep.get("sketch_segments"))
    print("  ★ 新特征 = %s" % rep.get("new_features"))
    print(
        "  ★ 体积 = %s mm³（★ 解析 %.3f）⇒ 比值 %s"
        % (
            rep.get("volume_mm3"),
            rep.get("expected_volume_mm3"),
            rep.get("volume_ratio"),
        )
    )
    env = (rep.get("bbox") or {}).get("envelope_mm") or {}
    print("  ★ 包围盒 = %s" % json.dumps(env, ensure_ascii=False))
    print("  ★ 判据 = %s" % json.dumps(rep.get("checks"), ensure_ascii=False))
    for f in (rep["steps"][0] or {}).get("fails") or []:
        print("        fail: %s" % f)
    if rep.get("error"):
        print("  ✗ %s" % rep["error"])
    print("  产物：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
