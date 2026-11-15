"""隔离：齿面「渐开线样条」本身能不能拉伸（去掉齿根过渡）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 已证：花瓣四变体（含扇角 10.7°、r 8.75→11、65 点 = 与齿同尺寸）**全部拉伸成功**
#   ⇒ 尺寸/点数不是原因（output/_probe_petal_variants.json）。
# 本脚本：用**真实齿廓曲线**，两档对照
#   T1 = 左渐开线样条 + 齿顶弧 + 右渐开线样条 + 基圆齿根弧（**无齿根过渡**）
#   T2 = 在 T1 基础上加左右齿根过渡样条（= 完整单齿）
#   ⇒ T1 成 / T2 败 ⇒ 齿根过渡曲线是元凶
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

from scripts import gear_geometry as g  # noqa: E402
from scripts import sw_connect as c  # noqa: E402
from scripts import sw_part as P  # noqa: E402


def _inv(t):
    return t - math.atan(t)


def _pol(r, a):
    return r * math.cos(a), r * math.sin(a)


def tooth(m=1.0, z=20, alpha_deg=20.0, n_inv=40, with_fillet=False,
          n_tro=24, t_start=0.0):
    alpha = math.radians(alpha_deg)
    r = m * z / 2.0
    rb = r * math.cos(alpha)
    ra = r + g.ADDENDUM_COEFF * m
    rf = r - g.DEDENDUM_COEFF * m
    hf = g.DEDENDUM_COEFF * m
    rho = g.TOOL_TIP_RADIUS_COEFF * m
    P_ = math.pi / (2.0 * z) + (math.tan(alpha) - alpha)
    t_a = math.sqrt((ra / rb) ** 2 - 1.0)
    ang_tip = P_ - _inv(t_a)

    segs = []
    if with_fillet:
        a = hf - rho
        u_c = math.pi * m / 4.0 - a * math.tan(alpha) - rho / math.cos(alpha)
        phi0 = -u_c / r

        def tro(ph):
            return g.trochoid_xy_mm(ph, pitch_radius_mm=r, dedendum_mm=hf,
                                    tool_tip_radius_mm=rho, module_mm=m,
                                    pressure_angle_rad=alpha)

        lo, hi = phi0, phi0 + 2.0
        for _ in range(200):
            mid = (lo + hi) / 2.0
            if math.hypot(*tro(mid)) < rb:
                lo = mid
            else:
                hi = mid
        phi_b = (lo + hi) / 2.0
        raw_end = math.atan2(tro(phi_b)[1], tro(phi_b)[0])
        off_r = P_ - raw_end                      # 右齿根过渡的角向偏移
        right = []
        for i in range(n_tro):
            ph = phi0 + (phi_b - phi0) * i / float(max(1, n_tro - 1))
            x, y = tro(ph)
            cc, ss = math.cos(off_r), math.sin(off_r)
            right.append((x * cc - y * ss, x * ss + y * cc))
        # 左齿根过渡 = 关于 0 的镜像（本齿中心 th=0）
        left = []
        for p in right:
            rr = math.hypot(*p)
            aa = math.atan2(p[1], p[0])
            left.append((rr * math.cos(-aa), rr * math.sin(-aa)))
        segs.append(("filletL", "spline", left))

    # 左渐开线 rb→ra
    pts = []
    for i in range(n_inv + 1):
        t = t_start + (t_a - t_start) * i / float(n_inv)
        pts.append(_pol(rb * math.sqrt(1 + t * t), -(P_ - _inv(t))))
    segs.append(("flankL", "spline", pts))
    # 齿顶弧
    p1, p2 = _pol(ra, -ang_tip), _pol(ra, ang_tip)
    segs.append(("tip", "arc", (0.0, 0.0, p1[0], p1[1], p2[0], p2[1], 1)))
    # 右渐开线 ra→rb
    pts_r = []
    for i in range(n_inv + 1):
        t = t_a - (t_a - t_start) * i / float(n_inv)
        pts_r.append(_pol(rb * math.sqrt(1 + t * t), P_ - _inv(t)))
    segs.append(("flankR", "spline", pts_r))
    if with_fillet:
        segs.append(("filletR", "spline", right))
        # 闭合：右过渡末端 → 左过渡起点（rf 上的圆弧，顺时针）
        p_end = right[-1]
        p_start = left[0]
        segs.append(("close", "arc", (0.0, 0.0, p_end[0], p_end[1],
                                      p_start[0], p_start[1], -1)))
    else:
        # 闭合：基圆上的圆弧
        q1, q2 = _pol(rb, P_), _pol(rb, -P_)
        segs.append(("close", "arc", (0.0, 0.0, q1[0], q1[1],
                                      q2[0], q2[1], -1)))
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
        fs = c.get_com_member(doc, "FeatureByName", sk_name)
        so = None
        for meth in ("GetSpecificFeature2", "GetSketch"):
            try:
                so = c.get_com_member(fs, meth)
                if so is not None:
                    break
            except Exception:  # noqa: BLE001
                continue
        cts = list(c.get_com_member(so, "GetSketchContours") or [])
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
    sw, _ = c.connect_solidworks(wait_seconds=30)
    out = []
    for label, ts in (("T1a t_start=0.00（基圆上，曲率半径→0）", 0.0),
                      ("T1b t_start=0.05", 0.05),
                      ("T1c t_start=0.15", 0.15),
                      ("T1d t_start=0.30", 0.30)):
        segs = tooth(with_fillet=False, t_start=ts)
        r = run_one(sw, label, segs)
        out.append(r)
        print(f"{label:34s} 轮廓 {r.get('contours')} "
              f"拉伸 {r.get('extrude')} 体积 {r.get('volume_mm3')}"
              f"{'  ' + r.get('error','') if r.get('error') else ''}")
    (ROOT / "output" / "_probe_tooth_isolate.json").write_text(
        __import__("json").dumps(
            {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "runs": out},
            ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
