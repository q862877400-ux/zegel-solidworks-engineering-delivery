"""最小隔离：2 样条 + 2 圆弧的闭合图形能不能拉伸。

# ── 来源 ─────────────────────────────────────────────────────────────
# 目的:     齿轮整圈轮廓（80 段样条+圆弧）拉伸一律回 None，而圆（1 段）能拉伸。
#           做一个**最小**对照：只画 2 条样条 + 2 条圆弧闭合成一个「花瓣」，
#           若它能拉伸 ⇒ 问题在**段数/复杂度**；若不能 ⇒ 问题在**样条或圆弧本身**。
# 依据:     `sw_part.sketch_spline`（VARIANT 包装，mm→m）、`sw_part.sketch_arc`
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

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


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    # 花瓣：外圆 r=10（两段圆弧）、内圆 r=6（两段样条）围成
    r_out, r_in = 10.0, 6.0
    a0, a1 = 0.0, math.pi / 3.0
    segs = []
    # 外弧：a0 → a1
    p1, p2 = _pol(r_out, a0), _pol(r_out, a1)
    segs.append(("out_arc", "arc", (0.0, 0.0, p1[0], p1[1], p2[0], p2[1], 1)))
    # 右样条：外圈 a1 → 内圈 a1
    pts = []
    for i in range(21):
        u = i / 20.0
        rr = r_out + (r_in - r_out) * u
        # 沿径向但带一点弧，形成真实的曲线
        ang = a1 + 0.05 * math.sin(math.pi * u)
        pts.append(_pol(rr, ang))
    segs.append(("right_spline", "spline", pts))
    # 内弧：a1 → a0（顺）
    q1, q2 = _pol(r_in, a1), _pol(r_in, a0)
    segs.append(("in_arc", "arc", (0.0, 0.0, q1[0], q1[1], q2[0], q2[1], -1)))
    # 左样条：内圈 a0 → 外圈 a0
    pts2 = []
    for i in range(21):
        u = i / 20.0
        rr = r_in + (r_out - r_in) * u
        ang = a0 - 0.05 * math.sin(math.pi * u)
        pts2.append(_pol(rr, ang))
    segs.append(("left_spline", "spline", pts2))

    # 闭合检查
    def ends(s):
        if s[1] == "spline":
            return s[2][0], s[2][-1]
        _cx, _cy, x1, y1, x2, y2, _d = s[2]
        return (x1, y1), (x2, y2)

    worst = 0.0
    for i in range(len(segs)):
        ea = ends(segs[i])[1]
        sb = ends(segs[(i + 1) % len(segs)])[0]
        worst = max(worst, math.hypot(ea[0] - sb[0], ea[1] - sb[1]) * 1000)
    print(f"段数 {len(segs)}  闭合最大间隙 {worst:.6f} µm")

    sw, _ = c.connect_solidworks(wait_seconds=30)
    doc = None
    ok = False
    try:
        doc = c.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        n_sp = n_ar = 0
        for tag, kind, pl in segs:
            if kind == "spline":
                P.sketch_spline(doc, pl)
                n_sp += 1
            else:
                cx, cy, x1, y1, x2, y2, dr = pl
                P.sketch_arc(doc, cx, cy, x1, y1, x2, y2, dr)
                n_ar += 1
        sk = c.get_com_member(doc, "GetActiveSketch2")
        sk_name = str(c.get_com_member(sk, "Name") or "草图1")
        seg_n = len(list(c.get_com_member(sk, "GetSketchSegments") or []))
        ct_n = len(list(c.get_com_member(sk, "GetSketchContours") or []))
        print(f"样条 {n_sp} 圆弧 {n_ar} · 草图段数 {seg_n} · 轮廓数 {ct_n}")
        P.end_sketch(doc)

        # 选轮廓再拉伸
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
        print(f"选中轮廓 {sel}/{len(cts)}")
        target = "__current_selection__" if sel else sk_name
        feat = P.extrude_boss(doc, target, 0.010)
        print(f"拉伸 = {feat is not None}")
        ok = feat is not None
        if ok:
            c.get_com_member(doc, "ForceRebuild3", False)
            ext = c.get_com_member(doc, "Extension")
            mp = c.get_com_member(ext, "CreateMassProperty")
            vol = float(c.get_com_member(mp, "Volume")) * 1e9
            print(f"体积 = {vol:.3f} mm³（花瓣面积 × 10）")
    except Exception as exc:  # noqa: BLE001
        print("✗", type(exc).__name__, str(exc)[:200])
    finally:
        if doc is not None:
            try:
                t = str(c.get_com_member(doc, "GetTitle") or "")
                if t:
                    c.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    print("VERDICT:", "OK 样条+圆弧能拉伸" if ok else "FAIL 样条+圆弧不能拉伸")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
