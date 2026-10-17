"""★ 真机：★ **规范做法建齿轮** —— 一个齿（真曲线闭合）⇒ 拉伸 ⇒ 圆周阵列 ×z ⇒ 加轮缘。

★★★★★ **业主原话**：「★ **像什么直接用直线去逼近曲线这种野路子，你就全部都改掉**」✓

★★★ **为什么不能用「整圈 120 条曲线」**（★ 真机裁决 · ★ 弹窗自己说的）：
  ★ 证据 `output/dialog-events/2026-10-11T002409-48043426.json` ⇒
    ★★ 弹窗正文逐字：★ **「此草图不再过定义。」** ⇒
    ★★★ **根因**：★ 120 条曲线的**端点两两重合** ⇒ SolidWorks **自动加重合约束** ⇒
      ★★ **约束数 >> 自由度数** ⇒ **过定义** ✗

★★★ **规范做法（★ 机械 CAD 通行套路 · ★ 本仓 `circular_pattern` 就是为此存在）**：
  ```
  ★ ① 画**一个齿**的**闭合**轮廓（★ 6 条边 · ★ 全部真曲线）
  ★ ② 拉伸 ⇒ 一个齿
  ★ ③ **圆周阵列 ×z** ⇒ z 个齿
  ★ ④ 加**轮缘**（★ 根圆盘）⇒ 与齿合并
  ```
  ★★ 曲线数从 **120 降到 6** ⇒ ★ 约束数降 **20 倍** ⇒ ★ **不过定义** ✓

★ 走 `sw_guard` ✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_gear_tooth_pattern.py
# 定位:   ★ 业主 2026-10-10「方法要规范」—— ★ 一个齿 + 圆周阵列（★ 不是整圈 120 条线）。
# 官方依据: `ISketchManager::CreateEquationSpline2` · `IFeatureManager::FeatureCircularPattern4`
#         `IFeatureManager::FeatureExtrusion3`（★ D1 = meters）
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

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402
from scripts import gear_geometry as G                                # noqa: E402


def _inv(t: float) -> float:
    return t - math.atan(t)


def tooth_curves(spec: G.GearSpec, geo: G.GearGeometry):
    """★ **一个齿**的闭合轮廓 —— 6 条边，★ 全部是方程式驱动曲线（★ 真曲线）。

    ★ 逆时针顺序（★ 角度相对**齿中心** = 0）：
      ```
      ① 右摆线    φ: 0 → phi_b      角 = +(raw(φ) + P_tro)
      ② 右渐开线  t: t_b → t_a      角 = +(P − inv(t))
      ③ 齿顶弧    t: −ang_tip → +ang_tip
      ④ 左渐开线  t: t_a → t_b      角 = −(P − inv(t))
      ⑤ 左摆线    φ: phi_b → 0      角 = −(raw(φ) + P_tro)
      ⑥ 齿根弧    角: −P_tro → +P_tro  （★ 短弧，★ 从齿下方闭合）
      ```
    ★★ 判据：★ ①的起点 = ⑥的终点（★ 角度 +P_tro）· ★ ⑤的终点 = ⑥的起点（★ 角度 −P_tro）✓
    """
    m, z = spec.module_mm, spec.teeth
    alpha = math.radians(spec.pressure_angle_deg)
    r = m * z / 2.0
    rb = r * math.cos(alpha)
    ra = r + G.ADDENDUM_COEFF * m
    hf = G.DEDENDUM_COEFF * m
    rf = r - hf
    rho = G.TOOL_TIP_RADIUS_COEFF * m

    t_b, t_a = geo.t_root, geo.t_tip
    inv_a = math.tan(alpha) - alpha
    P = math.pi / (2.0 * z) + inv_a

    def tro(phi):
        return G.trochoid_xy_mm(phi, pitch_radius_mm=r, dedendum_mm=hf,
                                tool_tip_radius_mm=rho)

    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if math.hypot(*tro(mid)) < rb:
            lo = mid
        else:
            hi = mid
    phi_b = (lo + hi) / 2.0
    raw_end = math.atan2(tro(phi_b)[1], tro(phi_b)[0])
    P_tro = P - raw_end
    ang_tip = P - _inv(t_a)

    k_ = 1.0 / 1000.0
    curves = []

    def tro_expr(phase):
        a0 = phase
        x = ("%.12f*cos(t+%.12f)+%.12f*t*sin(t+%.12f)+%.12f*(-%.12f*cos(t+%.12f)"
             "+%.12f*t*sin(t+%.12f))/sqrt(%.12f+%.12f*t*t)"
             % (r * k_ - hf * k_ + rho * k_, a0, r * k_, a0, rho * k_,
                (hf - rho) * k_, a0, r * k_, a0, ((hf - rho) * k_) ** 2, (r * k_) ** 2))
        y = ("%.12f*sin(t+%.12f)-%.12f*t*cos(t+%.12f)+%.12f*(-%.12f*sin(t+%.12f)"
             "-%.12f*t*cos(t+%.12f))/sqrt(%.12f+%.12f*t*t)"
             % (r * k_ - hf * k_ + rho * k_, a0, r * k_, a0, rho * k_,
                (hf - rho) * k_, a0, r * k_, a0, ((hf - rho) * k_) ** 2, (r * k_) ** 2))
        return x, y

    #: ① 右摆线 φ 0→phi_b，★ 相位 = −P_tro（★ 让终点落在 +P）
    x, y = tro_expr(-P_tro)
    curves.append(("right_trochoid", x, y, 0.0, phi_b))
    #: ② 右渐开线 t t_b→t_a，★ 相位 = +P
    x, y = G.involute_flank_expressions(rb, P, right=True)
    curves.append(("right_involute", x, y, t_b, t_a))
    #: ③ 齿顶弧
    curves.append(("tip_arc", "%.12f*cos(t)" % (ra * k_), "%.12f*sin(t)" % (ra * k_),
                   -ang_tip, ang_tip))
    #: ④ 左渐开线 t t_a→t_b，★ 相位 = −P
    x, y = G.involute_flank_expressions(rb, -P, right=False)
    curves.append(("left_involute", x, y, t_a, t_b))
    #: ⑤ 左摆线 φ phi_b→0，★ 相位 = +P_tro
    x, y = tro_expr(P_tro)
    curves.append(("left_trochoid", x, y, phi_b, 0.0))
    #: ⑥ 齿根弧：★ −P_tro → +P_tro
    curves.append(("root_arc", "%.12f*cos(t)" % (rf * k_), "%.12f*sin(t)" % (rf * k_),
                   -P_tro, P_tro))
    return curves, {"P": P, "P_tro": P_tro, "phi_b": phi_b, "ang_tip": ang_tip,
                    "t_range": [t_b, t_a], "span_rad": 2.0 * P_tro,
                    "pitch_rad": 2.0 * math.pi / z}


def _features(doc):
    try:
        from scripts import sw_feature_readback as F
        return list(F.feature_names(doc) or [])
    except Exception:                                                     # noqa: BLE001
        return []


def main() -> int:
    #: ★★ 顶层兜底：★ 把 traceback **落盘**（★ guard 的 stderr_tail 会截断 ⇒ 看不到真因）✓
    import traceback as _tb
    try:
        return _main()
    except BaseException:                                                 # noqa: BLE001
        (R / "output" / "_probe_gear_tooth_pattern_traceback.txt").write_text(
            _tb.format_exc(), encoding="utf-8")
        raise


def _main() -> int:
    spec = G.GearSpec(module_mm=1.0, teeth=20, face_width_mm=10.0,
                      pressure_angle_deg=20.0, bore_diameter_mm=8.0)
    geo = G.calculate_gear_geometry(spec)
    curves, meta = tooth_curves(spec, geo)
    rep = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "_": "★ 一个齿（真曲线）+ 圆周阵列 ×z（★ 规范做法）",
           "spec": {"module_mm": spec.module_mm, "teeth": spec.teeth,
                    "face_width_mm": spec.face_width_mm,
                    "bore_diameter_mm": spec.bore_diameter_mm},
           "analytic": geo.evidence(), "tooth_meta": meta,
           "curve_count": len(curves), "steps": []}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = C.new_document(sw, "part")
        before = _features(doc)
        #: ── ① 一个齿的闭合草图 ────────────────────────────────
        P.start_sketch(doc, plane_name="Front Plane")
        sm = C.get_com_member(doc, "SketchManager")
        ok = fail = 0
        fails = []
        for tag, x, y, t0, t1 in curves:
            try:
                C.get_com_member(sm, "CreateEquationSpline2", x, y, "",
                                 "%r" % t0, "%r" % t1, False, 0.0, 0.0, 0.0, True, True)
                ok += 1
            except Exception as exc:                                      # noqa: BLE001
                fail += 1
                fails.append("%s: %s" % (tag, str(exc)[:80]))
        rep["steps"].append({"tooth_curves_ok": ok, "failed": fail, "fails": fails[:3]})
        try:
            sk = C.get_com_member(doc, "GetActiveSketch2")
            tooth_sketch = str(C.get_com_member(sk, "Name") or "")
        except Exception:                                                 # noqa: BLE001
            tooth_sketch = "草图1"
        P.end_sketch(doc)

        #: ── ② 拉伸一个齿 ──────────────────────────────────────
        feat = P.extrude_boss(doc, tooth_sketch, spec.face_width_mm / 1000.0)
        rep["steps"].append({"extrude_tooth": feat is not None, "sketch": tooth_sketch})
        tooth_name = None
        if feat is not None:
            tooth_name = "Tooth_m1_z20"
            try:
                feat.Name = tooth_name
            except Exception:                                             # noqa: BLE001
                tooth_name = str(C.get_com_member(feat, "Name") or "")
        rep["tooth_feature"] = tooth_name

        #: ── ③ 圆周阵列 ×z ─────────────────────────────────────
        if feat is not None:
            try:
                #: ★ 需要一条**轴线** —— 用临时轴（★ 前视基准面的法向）
                ax = C.get_com_member(doc, "GetActiveSketch2")
                #: ★★ 直接用**基准轴**：★ 尝试几种常见命名
                pat = None
                errs = []
                for axis_name in ("Axis1", "基准轴1", "Z Axis", "Z轴"):
                    try:
                        pat = P.circular_pattern(doc, tooth_name, axis_name,
                                                 2.0 * math.pi, spec.teeth, True)
                        if pat is not None:
                            break
                    except Exception as exc:                              # noqa: BLE001
                        errs.append("%s: %s" % (axis_name, str(exc)[:60]))
                rep["steps"].append({"circular_pattern": pat is not None,
                                     "axis_errors": errs[:3]})
            except Exception as exc:                                      # noqa: BLE001
                rep["steps"].append({"circular_pattern": False,
                                     "error": "%s: %s" % (type(exc).__name__, str(exc)[:150])})

        #: ── ④ 轮缘（★ 根圆盘）────────────────────────────────
        try:
            P.start_sketch(doc, plane_name="Front Plane")
            P.sketch_circle(doc, 0.0, 0.0, geo.root_diameter_mm / 2.0)
            try:
                sk2 = C.get_com_member(doc, "GetActiveSketch2")
                rim_sketch = str(C.get_com_member(sk2, "Name") or "")
            except Exception:                                             # noqa: BLE001
                rim_sketch = "草图2"
            P.end_sketch(doc)
            rim = P.extrude_boss(doc, rim_sketch, spec.face_width_mm / 1000.0)
            rep["steps"].append({"rim_extrude": rim is not None, "sketch": rim_sketch})
            if rim is not None:
                try:
                    rim.Name = "GearRim"
                except Exception:                                         # noqa: BLE001
                    pass
        except Exception as exc:                                          # noqa: BLE001
            rep["steps"].append({"rim_extrude": False,
                                 "error": "%s: %s" % (type(exc).__name__, str(exc)[:150])})

        #: ── ⑤ 轴孔 ────────────────────────────────────────────
        try:
            P.start_sketch(doc, plane_name="Front Plane")
            P.sketch_circle(doc, 0.0, 0.0, spec.bore_diameter_mm / 2.0)
            try:
                sk3 = C.get_com_member(doc, "GetActiveSketch2")
                bore_sketch = str(C.get_com_member(sk3, "Name") or "")
            except Exception:                                             # noqa: BLE001
                bore_sketch = "草图3"
            P.end_sketch(doc)
            bore = P.extrude_cut(doc, bore_sketch, 0.0)
            rep["steps"].append({"bore_cut": bore is not None, "sketch": bore_sketch})
        except Exception as exc:                                          # noqa: BLE001
            rep["steps"].append({"bore_cut": False,
                                 "error": "%s: %s" % (type(exc).__name__, str(exc)[:150])})

        C.get_com_member(doc, "ForceRebuild3", False)
        after = _features(doc)
        rep["new_features"] = [x for x in after if x not in before][:12]
        try:
            ext = C.get_com_member(doc, "Extension")
            mp = C.get_com_member(ext, "CreateMassProperty")
            vol = float(C.get_com_member(mp, "Volume"))
            rep["volume_m3"] = vol
            rep["volume_mm3"] = vol * 1e9
        except Exception as exc:                                          # noqa: BLE001
            rep["mass_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
        try:
            from scripts import sw_review as RV
            rep["bbox"] = RV.collect_geometry_measurements(doc)
        except Exception as exc:                                          # noqa: BLE001
            rep["bbox_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
    except Exception as exc:                                              # noqa: BLE001
        rep["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
                rep["closed"] = True
            except Exception:                                             # noqa: BLE001
                pass

    p = R / "output" / "_probe_gear_tooth_pattern.json"
    p.write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  ★ 齿曲线 %d 条 · ok=%s fail=%s" % (rep["curve_count"],
          (rep["steps"][0] or {}).get("tooth_curves_ok"),
          (rep["steps"][0] or {}).get("failed")))
    print("  ★ 齿跨角 %.6f rad · 齿距 %.6f rad ⇒ %s"
          % (meta["span_rad"], meta["pitch_rad"],
             "✓ 齿间有间隙" if meta["span_rad"] < meta["pitch_rad"] else "✗ 齿会重叠"))
    for s in rep["steps"][1:]:
        print("  ★ %s" % json.dumps(s, ensure_ascii=False)[:170])
    print("  ★ 新特征 = %s" % rep.get("new_features"))
    print("  ★ 体积 = %s mm³" % rep.get("volume_mm3"))
    env = ((rep.get("bbox") or {}).get("envelope_mm") or {})
    print("  ★ 包围盒 = %s" % json.dumps(env, ensure_ascii=False))
    if rep.get("error"):
        print("  ✗ %s" % rep["error"])
    print("  产物：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
