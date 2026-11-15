"""单变量对照：花瓣 vs 单齿，差异到底是**扇角**还是**半径跨度**还是**点数**？

# ── 来源 ─────────────────────────────────────────────────────────────
# 已知：花瓣（扇角 60°、r 6→10、样条 21 点）拉伸 **OK**；
#       单齿（扇角 10.7°、r 8.75→11、样条曲率反向）拉伸 **FAIL**。
# 做法：四个变体，同一会话、逐档拉伸，每次只动一个量：
#   A 扇角 60° · r 6→10   · 21 点   （基线，应 OK）
#   B 扇角 10.7° · r 6→10 · 21 点   （只改扇角）
#   C 扇角 60° · r 8.75→11 · 21 点   （只改半径跨度）
#   D 扇角 10.7° · r 8.75→11 · 65 点 （齿的尺寸 + 多点数）
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts import sw_connect as c  # noqa: E402
from scripts import sw_part as P  # noqa: E402


def _pol(r, a):
    return r * math.cos(a), r * math.sin(a)


def build_variant(sweep_deg: float, r_in: float, r_out: float, npts: int):
    """普通「花瓣」：外弧 + 右样条 + 内弧 + 左样条。"""
    a0, a1 = 0.0, math.radians(sweep_deg)
    segs = []
    p1, p2 = _pol(r_out, a0), _pol(r_out, a1)
    segs.append(("out_arc", "arc", (0.0, 0.0, p1[0], p1[1], p2[0], p2[1], 1)))
    pts = []
    for i in range(npts):
        u = i / float(npts - 1)
        rr = r_out + (r_in - r_out) * u
        ang = a1 + 0.05 * math.sin(math.pi * u)
        pts.append(_pol(rr, ang))
    segs.append(("right", "spline", pts))
    q1, q2 = _pol(r_in, a1), _pol(r_in, a0)
    segs.append(("in_arc", "arc", (0.0, 0.0, q1[0], q1[1], q2[0], q2[1], -1)))
    pts2 = []
    for i in range(npts):
        u = i / float(npts - 1)
        rr = r_in + (r_out - r_in) * u
        ang = a0 - 0.05 * math.sin(math.pi * u)
        pts2.append(_pol(rr, ang))
    segs.append(("left", "spline", pts2))
    return segs


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
            res["volume_mm3"] = round(
                float(c.get_com_member(mp, "Volume")) * 1e9, 3)
    except Exception as exc:  # noqa: BLE001
        res["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
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
    variants = [
        ("A 扇角60 r6→10 点21", 60.0, 6.0, 10.0, 21),
        ("B 扇角10.7 r6→10 点21", 10.7, 6.0, 10.0, 21),
        ("C 扇角60 r8.75→11 点21", 60.0, 8.75, 11.0, 21),
        ("D 扇角10.7 r8.75→11 点65", 10.7, 8.75, 11.0, 65),
    ]
    sw, _ = c.connect_solid_access = c.connect_solidworks(wait_seconds=30) \
        if False else c.connect_solidworks(wait_seconds=30)
    out = []
    for label, swp, rin, rout, n in variants:
        segs = build_variant(swp, rin, rout, n)
        r = run_one(sw, label, segs)
        out.append(r)
        print(f"{label:28s} 轮廓 {r.get('contours')} "
              f"拉伸 {r.get('extrude')} 体积 {r.get('volume_mm3')}"
              f"{'  ' + r.get('error','') if r.get('error') else ''}")
    (ROOT / "output" / "_probe_petal_variants.json").write_text(
        json.dumps({"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "runs": out},
                   ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
