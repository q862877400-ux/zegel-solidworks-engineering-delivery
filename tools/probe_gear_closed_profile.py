"""★ 真机：★ **完整齿轮轮廓** —— 每条边都是**真曲线**（★ 无一处折线逼近）。

★★★★★ **业主原话**：「★ **像什么直接用直线去逼近曲线这种野路子，你就全部都改掉**」✓

★★★ **轮廓的规范构造（★ 逆时针一圈，★ z 个齿首尾相接）**：
  对第 k 个齿（★ 齿中心角 `θk = k·2π/z`），逆时针依次是：
  ```
  ① ★ 左摆线齿根（★ rf → rb）      ★ 角 = θk − (raw(φ) + P_tro)
  ② ★ 左渐开线齿廓（★ rb → ra）    ★ 角 = θk − (P − inv(t))
  ③ ★ 齿顶圆弧（★ ra 上）           ★ 角 = θk − ang_tip → θk + ang_tip
  ④ ★ 右渐开线齿廓（★ ra → rb）    ★ 角 = θk + (P − inv(t))
  ⑤ ★ 右摆线齿根（★ rb → rf）      ★ 角 = θk + (raw(φ) + P_tro)
  ⑥ ★ 齿根圆弧（★ rf 上，★ 通向下一齿）★ 角 = θk + P_tro → θk+1 − P_tro
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
# 官方依据: `C:\swapi\types\ISketchManager\CreateEquationSpline2.md`（★ 11 参）
#         `C:\swapi\types\IFeatureManager\FeatureExtrusion3.md`（★ D1 = meters）
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

from scripts import gear_geometry as G  # noqa: E402
from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402


def _inv(t: float) -> float:
    return t - math.atan(t)


def build_profile_curves(spec: G.GearSpec, geo: G.GearGeometry):
    """★ 生成整圈轮廓的**每条曲线**（★ 全部是方程式曲线 ⇒ ★ 全是真曲线）。

    ★ 返回 `[(标签, x表达式, y表达式, t0, t1), …]`（★ 长度单位：★ 表达式内是**米**）。
    """
    m, z = spec.module_mm, spec.teeth
    alpha = math.radians(spec.pressure_angle_deg)
    r = m * z / 2.0
    rb = r * math.cos(alpha)
    ra = r + G.ADDENDUM_COEFF * m
    hf = G.DEDENDUM_COEFF * m
    rf = r - hf
    rho = G.TOOL_TIP_RADIUS_COEFF * m
    pitch = 2.0 * math.pi / z

    t_b = geo.t_root
    t_a = geo.t_tip
    inv_a = math.tan(alpha) - alpha
    #: ★★ 规范相位：★ P = π/(2z) + inv(α) ⇒ ★ 分度圆处半齿角 = π/(2z)
    P = math.pi / (2.0 * z) + inv_a

    def tro(phi):
        return G.trochoid_xy_mm(
            phi, pitch_radius_mm=r, dedendum_mm=hf, tool_tip_radius_mm=rho
        )

    #: ★ 摆线到基圆的 φ（★ 二分）
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if math.hypot(*tro(mid)) < rb:
            lo = mid
        else:
            hi = mid
    phi_b = (lo + hi) / 2.0
    raw_end = math.atan2(tro(phi_b)[1], tro(phi_b)[0])
    P_tro = P - raw_end  #: ★ 让摆线终点 = P（★ 与齿廓接上）
    ang_tip = P - _inv(t_a)
    ang_tro_start = P_tro  #: ★ φ=0 时 raw=0

    k_ = 1.0 / 1000.0  #: ★ 表达式单位是**米**
    rbm, ram, rfm = rb * k_, ra * k_, rf * k_
    curves = []
    for k in range(z):
        th = k * pitch
        #: ① 左摆线：★ φ 从 phi_b → 0（★ 由基圆下行到齿根）
        a0 = -(th - P_tro)
        x = (
            "%.12f*cos(t+%.12f)+%.12f*t*sin(t+%.12f)+%.12f*(-%.12f*cos(t+%.12f)"
            "+%.12f*t*sin(t+%.12f))/sqrt(%.12f+%.12f*t*t)"
            % (
                r * k_ - hf * k_ + rho * k_,
                a0,
                r * k_,
                a0,
                rho * k_,
                (hf - rho) * k_,
                a0,
                r * k_,
                a0,
                ((hf - rho) * k_) ** 2,
                (r * k_) ** 2,
            )
        )
        y = (
            "%.12f*sin(t+%.12f)-%.12f*t*cos(t+%.12f)+%.12f*(-%.12f*sin(t+%.12f)"
            "-%.12f*t*cos(t+%.12f))/sqrt(%.12f+%.12f*t*t)"
            % (
                r * k_ - hf * k_ + rho * k_,
                a0,
                r * k_,
                a0,
                rho * k_,
                (hf - rho) * k_,
                a0,
                r * k_,
                a0,
                ((hf - rho) * k_) ** 2,
                (r * k_) ** 2,
            )
        )
        curves.append(("tooth%d_trochoid_L" % k, x, y, phi_b, 0.0))
        #: ② 左渐开线：★ t 从 t_b → t_a（★ 基圆上行到齿顶）
        curves.append(
            (
                "tooth%d_involute_L" % k,
                G.involute_flank_expressions(rb, -th - P, right=False)[0],
                G.involute_flank_expressions(rb, -th - P, right=False)[1],
                t_b,
                t_a,
            )
        )
        #: ③ 齿顶圆弧：★ t 从 th−ang_tip → th+ang_tip
        curves.append(
            (
                "tooth%d_tip_arc" % k,
                "%.12f*cos(t)" % ram,
                "%.12f*sin(t)" % ram,
                th - ang_tip,
                th + ang_tip,
            )
        )
        #: ④ 右渐开线：★ t 从 t_a → t_b
        curves.append(
            (
                "tooth%d_involute_R" % k,
                G.involute_flank_expressions(rb, th + P, right=True)[0],
                G.involute_flank_expressions(rb, th + P, right=True)[1],
                t_a,
                t_b,
            )
        )
        #: ⑤ 右摆线：★ φ 从 0 → phi_b
        a1 = th - P_tro
        x = (
            "%.12f*cos(t+%.12f)+%.12f*t*sin(t+%.12f)+%.12f*(-%.12f*cos(t+%.12f)"
            "+%.12f*t*sin(t+%.12f))/sqrt(%.12f+%.12f*t*t)"
            % (
                r * k_ - hf * k_ + rho * k_,
                a1,
                r * k_,
                a1,
                rho * k_,
                (hf - rho) * k_,
                a1,
                r * k_,
                a1,
                ((hf - rho) * k_) ** 2,
                (r * k_) ** 2,
            )
        )
        y = (
            "%.12f*sin(t+%.12f)-%.12f*t*cos(t+%.12f)+%.12f*(-%.12f*sin(t+%.12f)"
            "-%.12f*t*cos(t+%.12f))/sqrt(%.12f+%.12f*t*t)"
            % (
                r * k_ - hf * k_ + rho * k_,
                a1,
                r * k_,
                a1,
                rho * k_,
                (hf - rho) * k_,
                a1,
                r * k_,
                a1,
                ((hf - rho) * k_) ** 2,
                (r * k_) ** 2,
            )
        )
        curves.append(("tooth%d_trochoid_R" % k, x, y, 0.0, phi_b))
        #: ⑥ 齿根圆弧：★ t 从 th+P_tro → (th+pitch)−P_tro
        curves.append(
            (
                "tooth%d_root_arc" % k,
                "%.12f*cos(t)" % rfm,
                "%.12f*sin(t)" % rfm,
                th + ang_tro_start,
                th + pitch - ang_tro_start,
            )
        )
    return curves, {
        "P": P,
        "P_tro": P_tro,
        "phi_b": phi_b,
        "ang_tip": ang_tip,
        "ang_tro_start": ang_tro_start,
        "pitch": pitch,
        "t_range": [t_b, t_a],
    }


def _features(doc):
    try:
        from scripts import sw_feature_readback as F

        return list(F.feature_names(doc) or [])
    except Exception:  # noqa: BLE001
        return []


def main() -> int:
    spec = G.GearSpec(
        module_mm=1.0,
        teeth=20,
        face_width_mm=10.0,
        pressure_angle_deg=20.0,
        bore_diameter_mm=8.0,
    )
    geo = G.calculate_gear_geometry(spec)
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
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = C.new_document(sw, "part")
        before = _features(doc)
        P.start_sketch(doc, plane_name="Front Plane")
        sm = C.get_com_member(doc, "SketchManager")
        ok = fail = 0
        fails = []
        for tag, x, y, t0, t1 in curves:
            try:
                C.get_com_member(
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
                if len(fails) < 3:
                    fails.append("%s: %s" % (tag, str(exc)[:90]))
        rep["steps"].append({"curves_ok": ok, "curves_failed": fail, "fails": fails})
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
            sk = C.get_com_member(doc, "GetActiveSketch2")
            sk_name = str(C.get_com_member(sk, "Name") or "")
        except Exception:  # noqa: BLE001
            sk_name = "草图1"
        try:
            segs = list(
                C.get_com_member(
                    C.get_com_member(doc, "GetActiveSketch2"), "GetSketchSegments"
                )
                or []
            )
            rep["sketch_segments"] = len(segs)
        except Exception:  # noqa: BLE001
            pass
        P.end_sketch(doc)
        rep["sketch_name"] = sk_name

        #: ★ 拉伸（★ 收**米**）
        feat = P.extrude_boss(doc, sk_name, spec.face_width_mm / 1000.0)
        rep["steps"].append({"extrude": feat is not None})
        if feat is not None:
            try:
                feat.Name = "SpurGear_m1_z20_involute"
            except Exception:  # noqa: BLE001
                pass
        C.get_com_member(doc, "ForceRebuild3", False)
        after = _features(doc)
        rep["new_features"] = [x for x in after if x not in before][:8]
        try:
            ext = C.get_com_member(doc, "Extension")
            mp = C.get_com_member(ext, "CreateMassProperty")
            vol = float(C.get_com_member(mp, "Volume"))
            rep["volume_m3"] = vol
            rep["volume_mm3"] = vol * 1e9
        except Exception as exc:  # noqa: BLE001
            rep["mass_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
        try:
            from scripts import sw_review as RV

            rep["bbox"] = RV.collect_geometry_measurements(doc)
        except Exception as exc:  # noqa: BLE001
            rep["bbox_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])

        cell = json.loads(
            (R / "output" / "_gear_unit_cell.json").read_text(encoding="utf-8")
        )
        a_total = float(cell["total_area_mm2"])
        v_exp = (
            a_total * spec.face_width_mm
            - math.pi * (spec.bore_diameter_mm / 2) ** 2 * spec.face_width_mm
        )
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
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
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
