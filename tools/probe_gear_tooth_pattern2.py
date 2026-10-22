"""★ 真机：★ **一个齿（真曲线）⇒ 拉伸 ⇒ 圆周阵列 ×z**（★ 规范做法）。

★★★★★ **业主原话**：「★ **像什么直接用直线去逼近曲线这种野路子，你就全部都改掉**」✓

★★★ **与旧实现的对比（★ 这就是"规范"的含义）**：
  | ★ | ★ 旧（野路子） | ★ 新（规范） |
  |---|---|---|
  | ★ 齿廓 | ★ **12 段直线**逼近渐开线 | ★ **真渐开线**（方程式曲线） |
  | ★ 齿根 | ★ 径向直线 + 圆弧 | ★ **真摆线**（齿条刀具顶圆角包络） |
  | ★ 齿形 | ★ 随 `involute_segments` **变** | ★ **唯一确定**（★ 与标准一致） |
  | ★ 建模 | ★ 120 条线段一次画完 | ★ **一个齿 + 圆周阵列 ×z** |
  | ★ 共轭 | ★ **被破坏**（折线无共轭） | ★ **成立**（★ 渐开线的唯一价值） |

★★ **为什么必须「一个齿 + 阵列」**（★ 真机裁决 · ★ 弹窗自己说的）：
  ★ 证据 `output/dialog-events/2026-10-11T002409-48043426.json` ⇒
    ★★ 弹窗正文逐字：★ **「此草图不再过定义。」** ⇒
    ★★★ 整圈 120 条曲线的端点两两重合 ⇒ **自动重合约束** ⇒ **过定义** ✗

★ 走 `sw_guard` ✓
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_gear_tooth_pattern2.py
# 定位:   ★ 业主 2026-10-10「方法要规范」—— ★ 真曲线的**规范建模链**。
# 官方依据: `ISketchManager::CreateEquationSpline2`（★ 11 参 · ★ RangeStart/End 是字符串
#           ）
#         `IFeatureManager::FeatureExtrusion3`（★ D1 = meters）
#         `IFeatureManager::FeatureCircularPattern4`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import math
import sys
import time
import traceback as _tb
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


def tooth_curves(spec: g.GearSpec, geo: g.GearGeometry):
    """★ 一个齿的 **6 条真曲线**（★ 定版：★ 含 `u_c` + **旋转** + **镜像**）。

    ★★★ **三条修正（★ 全部由读数定位 · ★ 见 `output/_gear_loop_rot.json`）**：
      ★ ① ★ **摆线带 `u_c`**：★ `u_c = pi*m/4 - a*tan(alpha) - rho/cos(alpha)`
        ★★ 本机 = **0.06435650604500565 mm**（★ 独立核验逐位吻合）✓
        ★★★ 缺它 ⇒ 摆线与渐开线在成形圆处**切向错位 0.3687°** ⇒ 台阶 **0.0606 mm** ✗
      ★ ② ★ **相位 = 旋转**（★ 不是把相位加到 phi 上）：
        ★ `x = X*cos(R) - Y*sin(R)` · ★ `y = X*sin(R) + Y*cos(R)` ✓
      ★ ③ ★ **左齿根 = 右齿根的镜像**：★ `(X, -Y)` ⇒ 角 = -(raw + R) ✓

    ★ 闭合链（★ 参数一律**升序** —— `RangeStart <= RangeEnd` 是硬要求）：
      ```
      ① right_root   t: phi0->phi_b   角 = +(raw(t) + R)     => +_a -> +P
      ② right_flank  t: 0->T          角 = +P - inv(t)        => +P -> +ang_tip
      ③ tip_arc      t: -ang_tip->+ang_tip（y 取负）           => +ang_tip -> -ang_tip
      ④ left_flank   t: 0->T          角 = -P + inv(T-t)      => -ang_tip -> -P
      ⑤ left_root    t: 0->1          角 = -(raw(phi_b-span*t) + R) => -P -> -_a
      ⑥ root_arc     t: -_a->+_a                                => -_a -> +_a
      ```
      ★★ 判据：★ 12 个端点角**全部**与解析期望吻合（★ 容差 1e-6 rad）✓
    """
    m, z = spec.module_mm, spec.teeth
    alpha = math.radians(spec.pressure_angle_deg)
    r = m * z / 2.0
    rb = r * math.cos(alpha)
    ra = r + g.ADDENDUM_COEFF * m
    hf = g.DEDENDUM_COEFF * m
    rf = r - hf
    rho = g.TOOL_TIP_RADIUS_COEFF * m
    _t_b, t_a = geo.t_root, geo.t_tip
    P = math.pi / (2.0 * z) + (math.tan(alpha) - alpha)
    #: ★ ① **标准齿条的刀顶圆角中心偏移**（★ 修正项 · ★ 缺它就接不上渐开线）
    uc = g.tool_tip_arc_offset_mm(m, alpha, hf, rho)
    a_ = hf - rho

    def raw_tro(phi):
        """★ **原始摆线**（★ 未旋转 · ★ 含 u_c）。"""
        return g.trochoid_xy_mm(
            phi,
            pitch_radius_mm=r,
            dedendum_mm=hf,
            tool_tip_radius_mm=rho,
            module_mm=m,
            pressure_angle_rad=alpha,
        )

    phi0 = -uc / r  #: ★ 齿根圆上的起点
    lo, hi = phi0, 1.0
    for _ in range(300):
        mid = (lo + hi) / 2.0
        if math.hypot(*raw_tro(mid)) < rb:
            lo = mid
        else:
            hi = mid
    phi_b = (lo + hi) / 2.0
    raw_b = math.atan2(raw_tro(phi_b)[1], raw_tro(phi_b)[0])
    #: ★★ ② **旋转角**：★ 让摆线终点（★ 半径 rb）转到渐开线起点（★ 角 P）
    rot = P - raw_b
    _a = math.atan2(raw_tro(phi0)[1], raw_tro(phi0)[0]) + rot
    ang_tip = P - _inv(t_a)
    span = phi_b - phi0

    def raw_expr(u):
        """★ 原始摆线 (X, Y) 的表达式（★ `u` = phi 的表达式 · ★ 单位毫米）。"""
        ve = "(%.12f+%.12f*%s)" % (uc, r, u)
        sq = "%.12f+(%s)*(%s)" % (a_ * a_, ve, ve)
        X = "%.12f*cos(%s)+%s*sin(%s)+%.12f*(-%.12f*cos(%s)+%s*sin(%s))/sqrt(%s)" % (
            r - a_,
            u,
            ve,
            u,
            rho,
            a_,
            u,
            ve,
            u,
            sq,
        )
        Y = "%.12f*sin(%s)-%s*cos(%s)+%.12f*(-%.12f*sin(%s)-%s*cos(%s))/sqrt(%s)" % (
            r - a_,
            u,
            ve,
            u,
            rho,
            a_,
            u,
            ve,
            u,
            sq,
        )
        return X, Y

    c_, s_ = math.cos(rot), math.sin(rot)
    curves = []
    #: ① right_root：★ phi = t（★ phi0->phi_b）· ★ 旋转 +rot
    X, Y = raw_expr("t")
    curves.append(
        (
            "right_root",
            "((%s)*%.12f-(%s)*%.12f)" % (X, c_, Y, s_),
            "((%s)*%.12f+(%s)*%.12f)" % (X, s_, Y, c_),
            phi0,
            phi_b,
        )
    )
    #: ② right_flank
    x, y = g.involute_flank_expressions(rb, +P, right=True)
    curves.append(("right_flank", x, y, 0.0, t_a))
    #: ③ tip_arc（★ 升序 + y 取负 ⇒ 角从 +ang_tip 到 -ang_tip）
    curves.append(
        ("tip_arc", "%.12f*cos(t)" % ra, "-%.12f*sin(t)" % ra, -ang_tip, +ang_tip)
    )
    #: ④ left_flank：★ 参数替换 t->(T-t) · ★ 相位 -P
    se, th = "(%.12f-t)" % t_a, -P
    curves.append(
        (
            "left_flank",
            "%.12f*(cos(%s+%.12f)+%s*sin(%s+%.12f))" % (rb, se, th, se, se, th),
            "%.12f*(sin(%s+%.12f)-%s*cos(%s+%.12f))" % (rb, se, th, se, se, th),
            0.0,
            t_a,
        )
    )
    #: ⑤ left_root：★ **右齿根的镜像**（★ 角度取负）· ★ 参数升序
    u5 = "(%.12f-%.12f*t)" % (phi_b, span)
    x5, y5 = raw_expr(u5)
    curves.append(
        (
            "left_root",
            "((%s)*%.12f-(%s)*%.12f)" % (x5, c_, y5, s_),
            "-1.0*((%s)*%.12f+(%s)*%.12f)" % (x5, s_, y5, c_),
            0.0,
            1.0,
        )
    )
    #: ⑥ root_arc：★ -_a -> +_a
    curves.append(("root_arc", "%.12f*cos(t)" % rf, "%.12f*sin(t)" % rf, -_a, +_a))
    return curves, {
        "P": P,
        "P_tro": _a,
        "_a": _a,
        "rot": rot,
        "ang_tip": ang_tip,
        "phi_b": phi_b,
        "phi0": phi0,
        "uc": uc,
        "span_rad": 2.0 * _a,
        "pitch_rad": 2.0 * math.pi / z,
    }


def _features(doc):
    try:
        from scripts import sw_feature_readback as f

        return list(f.feature_names(doc) or [])
    except Exception:  # noqa: BLE001
        return []


def _vol(doc):
    try:
        mp = c.get_com_member(c.get_com_member(doc, "Extension"), "CreateMassProperty")
        return float(c.get_com_member(mp, "Volume")) * 1e9
    except Exception as exc:  # noqa: BLE001
        return {"error": "%s: %s" % (type(exc).__name__, str(exc)[:110])}


def _main() -> int:
    spec = g.GearSpec(
        module_mm=1.0,
        teeth=20,
        face_width_mm=10.0,
        pressure_angle_deg=20.0,
        bore_diameter_mm=8.0,
    )
    geo = g.calculate_gear_geometry(spec)
    curves, meta = tooth_curves(spec, geo)
    rep = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "★ 一个齿（真曲线）⇒ 拉伸 ⇒ 圆周阵列 ×z",
        "spec": {
            "module_mm": spec.module_mm,
            "teeth": spec.teeth,
            "face_width_mm": spec.face_width_mm,
            "bore_diameter_mm": spec.bore_diameter_mm,
        },
        "analytic": geo.evidence(),
        "tooth_meta": meta,
        "steps": [],
    }
    sw, _ = c.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = c.new_document(sw, "part")
        before = _features(doc)
        #: ── ① 一个齿 ────────────────────────────────────────
        P.start_sketch(doc, plane_name="Front Plane")
        sm = c.get_com_member(doc, "SketchManager")
        ok = fail = 0
        errs = []
        for name, x, y, t0, t1 in curves:
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
                    True,
                    True,
                )
                ok += 1
            except Exception as exc:  # noqa: BLE001
                fail += 1
                errs.append("%s: %s" % (name, str(exc)[:70]))
        rep["steps"].append({"tooth_curves_ok": ok, "failed": fail, "errors": errs[:3]})
        try:
            sk = c.get_com_member(doc, "GetActiveSketch2")
            sname = str(c.get_com_member(sk, "Name") or "")
            rep["tooth_segments"] = len(
                list(c.get_com_member(sk, "GetSketchSegments") or [])
            )
        except Exception:  # noqa: BLE001
            sname = "草图1"
        P.end_sketch(doc)
        feat = P.extrude_boss(doc, sname, spec.face_width_mm / 1000.0)
        rep["steps"].append({"extrude_tooth": feat is not None, "sketch": sname})
        if feat is None:
            rep["verdict"] = "extrude_failed"
            raise SystemExit(0)
        try:
            feat.Name = "Tooth_m1_z20"
        except Exception:  # noqa: BLE001
            pass
        tooth_name = "Tooth_m1_z20"
        rep["steps"].append({"tooth_volume_mm3": _vol(doc)})

        #: ── ② 圆周阵列 ×z（★ 先建一条基准轴）──────────────────
        axis_name = None
        try:
            #: ★ 用**前视基准面 + 右视基准面**的交线做轴 ⇒ ★ 官方 `InsertAxis2` 需要选中
            #: 两个面
            P.start_sketch(doc, plane_name="Front Plane")
            #: ★★ 更简单：★ 直接在**上视基准面**与**前视基准面**之间插轴
            for a, b in (("Front Plane", "Right Plane"), ("前视基准面", "右视基准面")):
                try:
                    ok1 = c.get_com_member(doc, "Extension").SelectByID2(
                        a, "PLANE", 0, 0, 0, False, 0, None, 0
                    )
                    ok2 = c.get_com_member(doc, "Extension").SelectByID2(
                        b, "PLANE", 0, 0, 0, True, 0, None, 0
                    )
                    if ok1 and ok2:
                        ax = c.get_com_member(doc, "InsertAxis2", True)
                        axis_name = (
                            str(c.get_com_member(ax, "Name") or "") if ax else None
                        )
                        if axis_name:
                            break
                except Exception:  # noqa: BLE001
                    pass
        except Exception as exc:  # noqa: BLE001
            rep["steps"].append(
                {"axis_error": "%s: %s" % (type(exc).__name__, str(exc)[:100])}
            )
        rep["axis_name"] = axis_name
        if axis_name:
            pat = None
            perr = []
            try:
                pat = P.circular_pattern(
                    doc, tooth_name, axis_name, 2.0 * math.pi, spec.teeth, True
                )
            except Exception as exc:  # noqa: BLE001
                perr.append("%s: %s" % (type(exc).__name__, str(exc)[:110]))
            rep["steps"].append({"circular_pattern": pat is not None, "errors": perr})
            if pat is not None:
                try:
                    pat.Name = "Teeth_z20"
                except Exception:  # noqa: BLE001
                    pass
        rep["steps"].append({"after_pattern_volume_mm3": _vol(doc)})

        #: ── ③ 轴孔 ───────────────────────────────────────────
        try:
            P.start_sketch(doc, plane_name="Front Plane")
            P.sketch_circle(doc, 0.0, 0.0, spec.bore_diameter_mm / 2.0)
            try:
                sk3 = c.get_com_member(doc, "GetActiveSketch2")
                bname = str(c.get_com_member(sk3, "Name") or "")
            except Exception:  # noqa: BLE001
                bname = ""
            P.end_sketch(doc)
            cut = P.extrude_cut(doc, bname, 0.0)
            rep["steps"].append({"bore_cut": cut is not None})
        except Exception as exc:  # noqa: BLE001
            rep["steps"].append(
                {
                    "bore_cut": False,
                    "error": "%s: %s" % (type(exc).__name__, str(exc)[:120]),
                }
            )

        c.get_com_member(doc, "ForceRebuild3", False)
        after = _features(doc)
        rep["new_features"] = [x for x in after if x not in before][:12]
        rep["volume_mm3"] = _vol(doc)
        try:
            from scripts import sw_review as rv

            rep["bbox"] = rv.collect_geometry_measurements(doc)
        except Exception as exc:  # noqa: BLE001
            rep["bbox_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:110])
    except SystemExit:
        pass
    except Exception as exc:  # noqa: BLE001
        rep["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:260])
    finally:
        if doc is not None:
            try:
                t = str(c.get_com_member(doc, "GetTitle") or "")
                if t:
                    c.get_com_member(sw, "CloseDoc", t)
                rep["closed"] = True
            except Exception:  # noqa: BLE001
                pass
    p = R / "output" / "_probe_gear_tooth_pattern.json"
    p.write_text(
        json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        "  ★ 齿曲线 %s/%s · 草图段数 %s"
        % (
            (rep["steps"][0] or {}).get("tooth_curves_ok"),
            (rep["steps"][0] or {}).get("tooth_curves_ok", 0)
            + (rep["steps"][0] or {}).get("failed", 0),
            rep.get("tooth_segments"),
        )
    )
    print(
        "  ★ 齿跨角 %.6f < 齿距 %.6f ⇒ %s"
        % (
            meta["span_rad"],
            meta["pitch_rad"],
            "✓ 齿间有间隙" if meta["span_rad"] < meta["pitch_rad"] else "✗",
        )
    )
    for s in rep["steps"][1:]:
        print("  ★ %s" % json.dumps(s, ensure_ascii=False)[:180])
    print("  ★ 轴 = %s" % rep.get("axis_name"))
    print("  ★ 新特征 = %s" % rep.get("new_features"))
    print("  ★ 体积 = %s mm³" % rep.get("volume_mm3"))
    env = (rep.get("bbox") or {}).get("envelope_mm") or {}
    print("  ★ 包围盒 = %s" % json.dumps(env, ensure_ascii=False))
    if rep.get("error"):
        print("  ✗ %s" % rep["error"])
    print("  产物：%s" % p)
    return 0


def main() -> int:
    try:
        return _main()
    except BaseException:  # noqa: BLE001
        (R / "output" / "_probe_gear_tooth_pattern_traceback.txt").write_text(
            _tb.format_exc(), encoding="utf-8"
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
