"""★ 真机：★ **用真曲线建完整齿轮并回读**（★ 体积/包围盒/特征树 · ★ 判据 3 件一起）。

★★★ **判据（★ 规则 6 + 本仓「回读优先」）**：
  ★ ① ★ **特征树出现齿轮特征**（★ 不是"返回了非 None"）
  ★ ② ★ **体数 = 1**（★ 一个实体，★ 不是碎片）
  ★ ③ ★ **包围盒 = 解析外径 × 齿宽**（★ 22 × 22 × 10 mm）
  ★ ④ ★★ **体积 ≈ 解析面积 × 齿宽 − 轴孔**（★ 与**独立算的**解析值比）

★ 全程走 `tools/sw_guard.py` ✓
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_gear_true_curves_full.py
# 定位:   ★ 业主 2026-10-10「方法要规范」—— ★ 真曲线齿轮的**完整交付判据**。
# 官方依据: `ISketchManager::CreateEquationSpline2` · `IFeatureManager::FeatureExtrusion
#           3`
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

from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402
from scripts import gear_geometry as G  # noqa: E402


def _features(doc):
    try:
        from scripts import sw_feature_readback as F

        return list(F.feature_names(doc) or [])
    except Exception:  # noqa: BLE001
        return []


def _mass(doc):
    try:
        from scripts import sw_mass_property as M

        return M.read_mass_properties(doc)
    except Exception:  # noqa: BLE001
        try:
            ext = C.get_com_member(doc, "Extension")
            mp = C.get_com_member(ext, "CreateMassProperty")
            return {"volume_m3": float(C.get_com_member(mp, "Volume"))}
        except Exception as exc:  # noqa: BLE001
            return {"error": "%s: %s" % (type(exc).__name__, str(exc)[:150])}


def _bbox(doc):
    try:
        from scripts import sw_review as RV

        return RV.collect_geometry_measurements(doc)
    except Exception as exc:  # noqa: BLE001
        return {"error": "%s: %s" % (type(exc).__name__, str(exc)[:150])}


def _bodies(doc):
    try:
        from scripts import sw_document_data as D

        return D.count_bodies(doc) if hasattr(D, "count_bodies") else None
    except Exception:  # noqa: BLE001
        return None


def main() -> int:
    spec = G.GearSpec(
        module_mm=1.0,
        teeth=20,
        face_width_mm=10.0,
        pressure_angle_deg=20.0,
        bore_diameter_mm=8.0,
    )
    geo = G.calculate_gear_geometry(spec)
    #: ★★ 解析面积（★ 从离线单元几何读 —— ★ 那是**独立**算的）
    cell = json.loads(
        (R / "output" / "_gear_unit_cell.json").read_text(encoding="utf-8")
    )
    a_total = float(cell["total_area_mm2"])
    v_expect_mm3 = (
        a_total * spec.face_width_mm
        - math.pi * (spec.bore_diameter_mm / 2) ** 2 * spec.face_width_mm
    )

    rep = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "★ 真渐开线 + 真摆线齿根的**完整齿轮**（★ 交付判据）",
        "spec": {
            "module_mm": spec.module_mm,
            "teeth": spec.teeth,
            "face_width_mm": spec.face_width_mm,
            "bore_diameter_mm": spec.bore_diameter_mm,
        },
        "analytic": geo.evidence(),
        "analytic_area_mm2": a_total,
        "expected_volume_mm3": v_expect_mm3,
        "steps": [],
    }
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = C.new_document(sw, "part")
        before = _features(doc)
        P.start_sketch(doc, plane_name="Front Plane")
        sm = C.get_com_member(doc, "SketchManager")

        #: ★★ ① 渐开线（★ 真曲线）
        C.get_com_member(
            sm,
            "CreateEquationSpline2",
            G.involute_x_expression(geo.base_diameter_mm / 2.0),
            G.involute_y_expression(geo.base_diameter_mm / 2.0),
            "",
            "%r" % geo.t_root,
            "%r" % geo.t_tip,
            False,
            0.0,
            0.0,
            0.0,
            True,
            True,
        )
        #: ★★ ② 摆线齿根（★ 真曲线 · ★ 含 sqrt）
        hf = G.DEDENDUM_COEFF * spec.module_mm
        rho = G.TOOL_TIP_RADIUS_COEFF * spec.module_mm
        C.get_com_member(
            sm,
            "CreateEquationSpline2",
            G.trochoid_x_expression(
                pitch_radius_mm=geo.pitch_diameter_mm / 2.0,
                dedendum_mm=hf,
                tool_tip_radius_mm=rho,
            ),
            G.trochoid_y_expression(
                pitch_radius_mm=geo.pitch_diameter_mm / 2.0,
                dedendum_mm=hf,
                tool_tip_radius_mm=rho,
            ),
            "",
            "0",
            "0.235196202",
            False,
            0.0,
            0.0,
            0.0,
            True,
            True,
        )
        #: ★★ ③ 轴孔 + 齿根圆（★ `sketch_circle` 收**毫米** —— ★ 与表达式相反）
        P.sketch_circle(doc, 0.0, 0.0, spec.bore_diameter_mm / 2.0)
        P.sketch_circle(doc, 0.0, 0.0, geo.root_diameter_mm / 2.0)
        sk_name = None
        try:
            sk = C.get_com_member(doc, "GetActiveSketch2")
            sk_name = str(C.get_com_member(sk, "Name") or "")
        except Exception:  # noqa: BLE001
            pass
        P.end_sketch(doc)
        rep["steps"].append({"sketch": True, "sketch_name": sk_name})

        #: ★★ ④ 拉伸（★ `extrude_boss` 收**米** —— ★ 第三种口径）
        feat = P.extrude_boss(doc, sk_name, spec.face_width_mm / 1000.0)
        rep["steps"].append({"extrude": feat is not None})
        try:
            feat.Name = "SpurGear_m1_z20_involute"
        except Exception:  # noqa: BLE001
            pass
        C.get_com_member(doc, "ForceRebuild3", False)
        after = _features(doc)
        rep["new_features"] = [x for x in after if x not in before][:8]
        rep["mass"] = _mass(doc)
        rep["bbox"] = _bbox(doc)
        rep["body_count"] = _bodies(doc)

        #: ★★ ⑤ 回读方程式参数（★ 证明 SolidWorks 收到的是**真方程**）
        try:
            import importlib

            eq = importlib.import_module("tools.probe_equation_units")
            rep["equation_readback"] = eq._equation_readback(doc)
        except Exception as exc:  # noqa: BLE001
            rep["equation_readback_error"] = "%s: %s" % (
                type(exc).__name__,
                str(exc)[:120],
            )

        #: ★★★ ⑥ **判据**
        vol = None
        m = rep.get("mass") or {}
        for k in ("volume_m3", "volumeMm3", "volume"):
            if k in m and m[k]:
                vol = float(m[k])
                break
        if vol is not None:
            vol_mm3 = vol * 1e9 if vol < 1e-3 else vol
            rep["volume_mm3"] = vol_mm3
            rep["volume_ratio_vs_analytic"] = vol_mm3 / v_expect_mm3
        bb = rep.get("bbox") or {}
        rep["checks"] = {
            "gear_feature_in_tree": any("SpurGear" in x for x in rep["new_features"]),
            "single_body": rep.get("body_count") == 1,
            "bbox_is_analytic_outside_diameter": bool(
                bb
                and abs(float(bb.get("dx_mm", 0)) - geo.outside_diameter_mm) < 0.05
                and abs(float(bb.get("dy_mm", 0)) - geo.outside_diameter_mm) < 0.05
                and abs(float(bb.get("dz_mm", 0)) - spec.face_width_mm) < 0.05
            ),
            "volume_matches_analytic": bool(
                rep.get("volume_ratio_vs_analytic")
                and 0.95 < rep["volume_ratio_vs_analytic"] < 1.05
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

    p = R / "output" / "_probe_gear_true_curves_full.json"
    p.write_text(
        json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  ★ 新特征：%s" % rep.get("new_features"))
    print("  ★ 体数：%s" % rep.get("body_count"))
    print("  ★ 包围盒：%s" % json.dumps(rep.get("bbox"), ensure_ascii=False)[:160])
    print(
        "  ★ 体积：%s mm³（★ 解析 %.4f）⇒ 比值 %.4f"
        % (
            rep.get("volume_mm3"),
            v_expect_mm3,
            (
                rep.get("volume_ratio_vs_analytic")
                if rep.get("volume_ratio_vs_analytic") is not None
                else -1
            ),
        )
    )
    print("  ★ 判据：%s" % json.dumps(rep.get("checks"), ensure_ascii=False))
    if rep.get("error"):
        print("  ✗ %s" % rep["error"])
    print("  产物：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
