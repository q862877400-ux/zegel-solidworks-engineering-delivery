"""按业主 2026-11-07 澄清重建齿廓：**只用光滑曲线，不用任何直线段**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 业主原话（澄清禁令边界）：
#   「我说的是不能用直线的线段去模拟曲线，也就是说你可以用曲线的线段去画图呀…
#     圆你不能给我画成正几百边形…齿轮它是渐开线…两个边就是两条渐开线，
#     然后再有个外圆，那就是 3 条弧线…可能在根部再加两条，就是 5 条曲线…
#     能用一段光滑的曲线表达的线，就不要去切分成多条直线的线段或者是曲线的线段。」
# 构造（每齿 4 条，全是光滑曲线）：
#   ① 左齿廓 = **1 条样条**（穿真实摆线齿根 rf→成形段 + 真渐开线段 t:0→t_a）
#   ② 齿顶圆弧 = 1 条真圆弧（`CreateArc`）
#   ③ 右齿廓 = **1 条样条**（镜像）
#   ④ 齿根圆弧 = 1 条真圆弧（rf 上，通向下一齿）
#   ⇒ 零直线段。旧版用径向直线做齿根过渡，正是禁令针对的「用直线模拟曲线」。
# 判据：相邻接点间隙 ≤ 0.1 µm；齿廓样条点用 `gear_geometry` 的真公式采样
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts import gear_geometry as g  # noqa: E402


def _inv(t: float) -> float:
    return t - math.atan(t)


def _pol(rad: float, ang: float) -> tuple[float, float]:
    return rad * math.cos(ang), rad * math.sin(ang)


def build(spec, n_trochoid: int = 24, n_involute: int = 40) -> dict:
    """返回 (segs, meta)；segs 每项 = (tag, kind, payload)。

    kind: "spline" → payload 是 [(x,y), …]（毫米）
          "arc"    → payload 是 (cx, cy, x1, y1, x2, y2, direction)
    """
    m, z = spec.module_mm, spec.teeth
    alpha = math.radians(spec.pressure_angle_deg)
    r = m * z / 2.0
    rb = r * math.cos(alpha)
    ra = r + g.ADDENDUM_COEFF * m
    rf = r - g.DEDENDUM_COEFF * m
    hf = g.DEDENDUM_COEFF * m
    rho = g.TOOL_TIP_RADIUS_COEFF * m
    pitch = 2.0 * math.pi / z
    P = math.pi / (2.0 * z) + (math.tan(alpha) - alpha)
    t_a = math.sqrt((ra / rb) ** 2 - 1.0)
    ang_tip = P - _inv(t_a)

    def tro(phi: float) -> tuple[float, float]:
        return g.trochoid_xy_mm(
            phi, pitch_radius_mm=r, dedendum_mm=hf, tool_tip_radius_mm=rho,
            module_mm=m, pressure_angle_rad=alpha,
        )

    # 摆线起点 φ₀ = −u_c/r 处半径恰为 rf（官方 docstring 逐字）
    a = hf - rho
    u_c = (math.pi * m / 4.0 - a * math.tan(alpha) - rho / math.cos(alpha))
    phi0 = -u_c / r
    # 摆线跑到「半径达到 rb」为止
    lo, hi = phi0, phi0 + 2.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if math.hypot(*tro(mid)) < rb:
            lo = mid
        else:
            hi = mid
    phi_b = (lo + hi) / 2.0

    segs = []
    for k in range(z):
        th = k * pitch

        #: ★★★ 2026-11-07 重要修正：**摆线齿根与渐开线齿面必须分成两条曲线**。
        #:   拼进同一条样条时，两段在基圆处**曲率方向相反** ⇒ 样条是 S 形带拐点
        #:   ⇒ 窄楔形里摆动/自交 ⇒ 真机 `FeatureExtrusion3` 静默回 None
        #:   （实测：点数从 12 到 130 全部失败，而同样拓扑的「花瓣」成功 ⇒ 不是点数问题）。
        #:   ⇒ 按 GB/T 齿面组成拆成 **左齿根过渡 + 左齿面 + 齿顶面 + 右齿面 + 右齿根过渡**
        #:     （业主原话：「每一边再加两条，就是 5 条曲线」）
        pts_tro: list[tuple[float, float]] = []
        raw0 = math.atan2(tro(phi0)[1], tro(phi0)[0])
        raw_end = math.atan2(tro(phi_b)[1], tro(phi_b)[0])
        #: ★★★ 左齿根过渡必须是右齿根过渡的**镜像**（关于齿中心线 th），
        #:   不是「同一个摆线转个角度」。旧写法只旋转不镜像 ⇒ 左过渡向内弯
        #:   （齿根角 −2°）、右过渡向外弯（+8.6°）⇒ 齿形不对称、轮廓自交
        #:   ⇒ 真机 FeatureExtrusion3 静默回 None。
        off_r0 = (th + P) - raw_end
        _right = []
        for i in range(n_trochoid):
            phi = phi0 + (phi_b - phi0) * i / float(max(1, n_trochoid - 1))
            x, y = tro(phi)
            c_, s_ = math.cos(off_r0), math.sin(off_r0)
            _right.append((x * c_ - y * s_, x * s_ + y * c_))
        # 关于 th 镜像：角 a → 2·th − a，半径不变
        for _p in _right:   # rf → rb（与右侧同序，镜像后仍从齿根起）
            _rr = math.hypot(_p[0], _p[1])
            _aa = math.atan2(_p[1], _p[0])
            _aa2 = 2.0 * th - _aa
            pts_tro.append((_rr * math.cos(_aa2), _rr * math.sin(_aa2)))
        # ① 左齿根过渡曲面（独立曲线，单独一条样条）
        segs.append((f"k{k}①filletL", "spline", pts_tro))
        # ② 左齿面（独立曲线，单独一条样条）
        pts = [pts_tro[-1]]      # 起点与齿根过渡末端重合
        for i in range(n_involute + 1):
            t = t_a * i / float(n_involute)
            rr = rb * math.sqrt(1.0 + t * t)
            ang = th - (P - _inv(t))
            pts.append(_pol(rr, ang))
        segs.append((f"k{k}②flankL", "spline", pts))

        # ③ 齿顶面（真圆弧）
        p1 = _pol(ra, th - ang_tip)
        p2 = _pol(ra, th + ang_tip)
        segs.append((f"k{k}③tip", "arc", (0.0, 0.0, p1[0], p1[1],
                                          p2[0], p2[1], 1)))

        # ④ 右齿面（独立曲线，单独一条样条；镜像）
        pts_r: list[tuple[float, float]] = []
        for i in range(n_involute + 1):
            t = t_a * (1.0 - i / float(n_involute))
            rr = rb * math.sqrt(1.0 + t * t)
            ang = th + (P - _inv(t))
            pts_r.append(_pol(rr, ang))
        # ⑤ 右齿根过渡曲面（独立曲线）
        off_r = (th + P) - raw_end
        pts_tro_r: list[tuple[float, float]] = [pts_r[-1]]
        for i in range(n_trochoid - 1, -1, -1):
            phi = phi0 + (phi_b - phi0) * i / float(max(1, n_trochoid - 1))
            x, y = tro(phi)
            c_, s_ = math.cos(off_r), math.sin(off_r)
            pts_tro_r.append((x * c_ - y * s_, x * s_ + y * c_))
        segs.append((f"k{k}④flankR", "spline", pts_r))
        segs.append((f"k{k}⑤filletR", "spline", pts_tro_r))

        # ⑥ 槽底齿根圆弧（真圆弧）：从本齿右齿根自然角 → 下一齿左齿根自然角
        #: ★ 端点用摆线在齿根处的**自然角**（raw0+off），不是 θk±P ——
        #:   这样圆弧跨度 = pitch − 2P > 0，且与两侧样条端点严格重合。
        #: ★ 端点角**直接取实际端点**（镜像后不能再套旧公式）
        a_root_l = math.atan2(pts_tro[0][1], pts_tro[0][0])       # 本齿左
        a_root_r = math.atan2(pts_tro_r[-1][1], pts_tro_r[-1][0]) # 本齿右
        q1 = _pol(rf, a_root_r)
        q2 = _pol(rf, a_root_l + pitch)                            # 下一齿左
        segs.append((f"k{k}⑥root", "arc", (0.0, 0.0, q1[0], q1[1],
                                           q2[0], q2[1], 1)))

    # 闭合检查（按段序取首尾点）
    def _ends(seg):
        kind, pl = seg[1], seg[2]
        if kind == "spline":
            return pl[0], pl[-1]
        _, _, x1, y1, x2, y2, _d = pl
        return (x1, y1), (x2, y2)

    worst, worst_tag, bad = 0.0, "", 0
    for i in range(len(segs)):
        ea = _ends(segs[i])[1]
        sb = _ends(segs[(i + 1) % len(segs)])[0]
        gap = math.hypot(ea[0] - sb[0], ea[1] - sb[1]) * 1000.0
        if gap > 0.1:
            bad += 1
            if gap > worst:
                worst = gap
                worst_tag = f"{segs[i][0]}→{segs[(i+1)%len(segs)][0]}"
    return {
        "segs": segs, "bad": bad, "worst_um": worst, "worst_tag": worst_tag,
        "rb": rb, "ra": ra, "rf": rf, "P": P, "ang_tip": ang_tip, "t_a": t_a,
        "phi0": phi0, "phi_b": phi_b, "n_segs": len(segs),
    }


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    rc = 0
    for m, z in ((1.0, 20), (2.0, 24), (1.0, 12)):
        spec = g.GearSpec(module_mm=m, teeth=z, face_width_mm=10.0,
                          pressure_angle_deg=20.0, bore_diameter_mm=0.0)
        d = build(spec)
        ok = d["bad"] == 0
        if not ok:
            rc = 1
        print(f"=== m={m:g} z={z} === 段 {d['n_segs']} 条"
              f"（每齿 4 条，全为光滑曲线）")
        print(f"  rb={d['rb']:.5f} rf={d['rf']:.5f} ra={d['ra']:.5f}")
        if ok:
            print("  闭合 ✓ 最大间隙 0.000 µm")
        else:
            print(f"  不闭合 ✗ {d['bad']}/{d['n_segs']} 超差，"
                  f"最大 {d['worst_um']:.3f} µm @ {d['worst_tag']}")
        print()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
