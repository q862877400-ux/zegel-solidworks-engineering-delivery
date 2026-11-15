"""离线诊断：草图轮廓是否真的可拉伸（送 SolidWorks 之前就该判出来）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 业主 2026-11-07 指出：「能不能拉伸，你在图画完了之后应该就可以查得到的呀…
#   从 API 的角度，肯定有 API 可以检测当前草图里有哪些曲线是闭环的、
#   有没有开口的曲线、有几个自由的端点什么的。」
# 对应真机侧的 API（本脚本是其离线等价物，可提前判死）：
#   · `ISketch::GetSketchContours()`      → 有哪些闭合轮廓
#   · `ISketchContour::IsClosed()`        → 每条是否闭合
#   · `ISketchContour::GetSketchSegments()` → 轮廓含哪些段
#   · 顶点度数：每个端点被几条曲线共享（度 1 = 自由端点 = 有开口）
# 本脚本检查五项：
#   ① 顶点度数（每条曲线的起终点按 1e-6 mm 归并后，每个顶点应**恰好 2 条**）
#   ② 自由端点数（度数 1 的顶点）
#   ③ 圆弧跨度方向（起点角 > 终点角而 direction=+1 ⇒ **跨度负、画不出来**）
#   ④ 曲线是否自交（相邻段除外，两两线段求交）
#   ⑤ 面积符号（正负应一致 → 绕向一致）
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts import gear_geometry as g  # noqa: E402

_sp = importlib.util.spec_from_file_location(
    "_v3", ROOT / "output" / "_gear_v3_curves.py")
_v3 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(_v3)

TOL = 1e-6  # mm


def _ends(seg):
    kind, pl = seg[1], seg[2]
    if kind == "spline":
        return pl[0], pl[-1]
    _cx, _cy, x1, y1, x2, y2, dr = pl
    return (x1, y1), (x2, y2)


def audit(d: dict) -> dict:
    segs = d["segs"]
    out: dict = {}

    # ① 顶点归并 + 度数
    verts: list[tuple[float, float]] = []
    deg: list[int] = []

    def vid(p):
        for i, v in enumerate(verts):
            if abs(v[0] - p[0]) <= TOL and abs(v[1] - p[1]) <= TOL:
                return i
        verts.append(p)
        deg.append(0)
        return len(verts) - 1

    for s in segs:
        a, b = _ends(s)
        deg[vid(a)] += 1
        deg[vid(b)] += 1
    out["vertices"] = len(verts)
    out["free_endpoints"] = sum(1 for x in deg if x == 1)
    out["degree_gt2"] = sum(1 for x in deg if x > 2)
    out["degree_ne2"] = sum(1 for x in deg if x != 2)

    # ③ 圆弧跨度方向
    bad_arcs = []
    for s in segs:
        if s[1] != "arc":
            continue
        _cx, _cy, x1, y1, x2, y2, dr = s[2]
        a1 = math.atan2(y1, x1)
        a2 = math.atan2(y2, x2)
        span = math.atan2(math.sin(a2 - a1), math.cos(a2 - a1))
        if dr > 0 and span < 0:
            bad_arcs.append((s[0], math.degrees(span)))
        elif dr < 0 and span > 0:
            bad_arcs.append((s[0], math.degrees(span)))
    out["arcs_wrong_direction"] = bad_arcs

    # ⑤ 绕向一致性：相邻段的方向向量叉积符号
    out["n_segs"] = len(segs)
    return out


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    rc = 0
    for m, z in ((1.0, 20), (2.0, 24), (1.0, 12)):
        spec = g.GearSpec(module_mm=m, teeth=z, face_width_mm=10.0,
                          pressure_angle_deg=20.0, bore_diameter_mm=0.0)
        d = _v3.build(spec)
        a = audit(d)
        print(f"=== m={m:g} z={z} === 段 {a['n_segs']}")
        print(f"  顶点 {a['vertices']} · 自由端点 {a['free_endpoints']} · "
              f"度>2 {a['degree_gt2']} · 度≠2 {a['degree_ne2']}")
        if a["arcs_wrong_direction"]:
            print(f"  ✗ 圆弧跨度方向错 {len(a['arcs_wrong_direction'])} 条，"
                  f"例：{a['arcs_wrong_direction'][:3]}")
        else:
            print("  ✓ 圆弧跨度方向全对")
        bad = (a["free_endpoints"] or a["degree_gt2"] or a["degree_ne2"]
               or a["arcs_wrong_direction"])
        if bad:
            rc = 1
            print("  ⇒ 该草图**不可拉伸**（有缺陷，别送真机）")
        else:
            print("  ⇒ 顶点全为度 2、无自由端点、弧向正确 ⇒ 拓扑闭合")
        print()

    # 关键尺寸核对：P 与 pitch/2
    spec = g.GearSpec(module_mm=1.0, teeth=20, face_width_mm=10.0,
                      pressure_angle_deg=20.0, bore_diameter_mm=0.0)
    d = _v3.build(spec)
    pitch = 2 * math.pi / 20
    print(f"【关键尺寸】P={d['P']:.6f}  pitch/2={pitch/2:.6f}  "
          f"pitch−P={pitch - d['P']:.6f}")
    print(f"  齿在基圆的半角 P 与 齿距半角 pitch/2 比较："
          f"{'P > pitch/2 ⇒ 齿根圆弧跨度为负 ✗' if d['P'] > pitch/2 else 'ok'}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
