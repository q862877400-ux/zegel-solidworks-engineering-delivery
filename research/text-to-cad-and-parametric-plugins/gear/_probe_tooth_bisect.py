"""变体二分：单齿拉伸失败，主因是**点数**还是**几何**？

# ── 来源 ─────────────────────────────────────────────────────────────
# 已知：花瓣（2 样条 21 点 + 2 圆弧，半径跨 6→10）拉伸 OK；
#       单齿（2 样条 65 点 + 2 圆弧，半径跨 8.75→11）拉伸 FAIL。
# 做法：同一 SolidWorks 会话里，只改**样条点数**（摆线段/渐开线段各取几段），
#       其余几何完全不变，逐档拉伸 —— 单变量。
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts import gear_geometry as g  # noqa: E402
from scripts import sw_connect as c  # noqa: E402
from scripts import sw_part as P  # noqa: E402

_sp = importlib.util.spec_from_file_location(
    "_v3", ROOT / "output" / "_gear_v3_curves.py")
_v3 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(_v3)


def tooth_segs(spec, n_tro, n_inv):
    d = _v3.build(spec, n_trochoid=n_tro, n_involute=n_inv)
    segs = list(d["segs"][:3])
    p_start = segs[0][2][0]
    p_end = segs[2][2][-1]
    segs.append(("root_close", "arc",
                 (0.0, 0.0, p_end[0], p_end[1], p_start[0], p_start[1], -1)))
    return segs, d


def _ends(s):
    if s[1] == "spline":
        return s[2][0], s[2][-1]
    _cx, _cy, x1, y1, x2, y2, _dr = s[2]
    return (x1, y1), (x2, y2)


def run_one(sw, label, segs):
    doc = None
    res = {"label": label}
    try:
        doc = c.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        for tag, kind, pl in segs:
            if kind == "spline":
                P.sketch_spline(doc, pl)
            else:
                cx, cy, x1, y1, x2, y2, dr = pl
                P.sketch_arc(doc, cx, cy, x1, y1, x2, y2, dr)
        sk = c.get_com_member(doc, "GetActiveSketch2")
        sk_name = str(c.get_com_member(sk, "Name") or "草图1")
        res["segments"] = len(list(
            c.get_com_member(sk, "GetSketchSegments") or []))
        res["contours"] = len(list(
            c.get_com_member(sk, "GetSketchContours") or []))
        P.end_sketch(doc)

        feat_sk = c.get_com_member(doc, "FeatureByName", sk_name)
        sk_obj = None
        for meth in ("GetSpecificFeature2", "GetSketch"):
            try:
                sk_obj = c.get_com_member(feat_sk, meth)
                if sk_obj is not None:
                    break
            except Exception:  # noqa: BLE001
                continue
        cts = list(c.get_com_member(sk_obj, "GetSketchContours") or [])
        doc.ClearSelection2(True)
        sm = c.get_com_member(doc, "SelectionManager")
        sd = c.get_com_member(sm, "CreateSelectData")
        if sd is not None:
            c.set_com_member(sd, "Mark", 0)
        sel = 0
        for ct in cts:
            try:
                if bool(c.get_com_member(ct, "Select2", True, sd)):
                    sel += 1
            except Exception:  # noqa: BLE001
                pass
        target = "__current_selection__" if sel else sk_name
        feat = P.extrude_boss(doc, target, 0.010)
        res["extrude"] = feat is not None
        if feat is not None:
            c.get_com_member(doc, "ForceRebuild3", False)
            ext = c.get_com_member(doc, "Extension")
            mp = c.get_com_member(ext, "CreateMassProperty")
            res["volume_mm3"] = float(
                c.get_com_member(mp, "Volume")) * 1e9
    except Exception as exc:  # noqa: BLE001
        res["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
    finally:
        if doc is not None:
            try:
                t = str(c.get_com_member(doc, "GetTitle") or "")
                if t:
                    c.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    return res


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    spec = g.GearSpec(module_mm=1.0, teeth=20, face_width_mm=10.0,
                      pressure_angle_deg=20.0, bore_diameter_mm=0.0)
    sw, _ = c.connect_solidworks(wait_seconds=30)
    out = []
    #: 单变量：只改样条点数（摆线段数 / 渐开线段数）
    for n_tro, n_inv in ((2, 3), (4, 6), (8, 12), (24, 40)):
        segs, d = tooth_segs(spec, n_tro, n_inv)
        npts = sum(len(s[2]) for s in segs if s[1] == "spline")
        worst = 0.0
        for i in range(len(segs)):
            ea = _ends(segs[i])[1]
            sb = _ends(segs[(i + 1) % len(segs)])[0]
            worst = max(worst, math.hypot(ea[0] - sb[0],
                                          ea[1] - sb[1]) * 1000)
        label = f"tro={n_tro} inv={n_inv} 样条点合计={npts} 闭合={worst:.4f}µm"
        r = run_one(sw, label, segs)
        out.append(r)
        print(f"{label}")
        print(f"   段 {r.get('segments')} · 轮廓 {r.get('contours')} · "
              f"拉伸 {r.get('extrude')} · 体积 {r.get('volume_mm3')}")
    (ROOT / "output" / "_probe_tooth_bisect.json").write_text(
        json.dumps({"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "runs": out},
                   ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
