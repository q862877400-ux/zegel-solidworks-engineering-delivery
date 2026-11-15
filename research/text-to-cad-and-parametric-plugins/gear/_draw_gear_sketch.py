"""在 SolidWorks 里画出「理论最优曲线」齿轮草图，**留在窗口里给业主目视**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 业主 2026-11-07：「直接给我在 sw 草图窗口留着我去看」
# 构造（output/_gear_v3_curves.py，每齿 6 条，零直线段）：
#   ① 左齿根过渡（真摆线样条） ② 左齿面（真渐开线样条） ③ 齿顶面（真圆弧）
#   ④ 右齿面（真渐开线样条）   ⑤ 右齿根过渡（真摆线样条） ⑥ 槽底（真圆弧）
# ★ 只画草图、**不拉伸**、**不关文档** —— 画完把 SW 窗口留着。
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import sys
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


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    z = 20
    ref_circles = True
    for a in sys.argv[1:]:
        if a.startswith("--teeth="):
            z = int(a.split("=", 1)[1])
        elif a == "--no-ref":
            ref_circles = False

    spec = g.GearSpec(module_mm=1.0, teeth=z, face_width_mm=10.0,
                      pressure_angle_deg=20.0, bore_diameter_mm=0.0)
    d = _v3.build(spec)
    print(f"离线段数 {d['n_segs']} · 闭合超差 {d['bad']} · "
          f"最大 {d['worst_um']:.6f} µm")
    print(f"rb={d['rb']:.5f}  rf={d['rf']:.5f}  ra={d['ra']:.5f}")

    sw, _ = c.connect_solidworks(wait_seconds=30)
    try:
        c.get_com_member(sw, "Visible", True)
    except Exception:  # noqa: BLE001
        pass
    doc = c.new_document(sw, "part")
    if doc is None:
        print("✗ NewDocument 返回 None（模板不可用）")
        return 1

    P.start_sketch(doc, plane_name="Front Plane")
    n_sp = n_ar = 0
    for tag, kind, pl in d["segs"]:
        if kind == "spline":
            P.sketch_spline(doc, pl)
            n_sp += 1
        else:
            cx, cy, x1, y1, x2, y2, dr = pl
            P.sketch_arc(doc, cx, cy, x1, y1, x2, y2, dr)
            n_ar += 1
    if ref_circles:
        # 三个参照圆：齿顶 / 基圆 / 齿根（便于肉眼判断齿形是否落在正确区间）
        P.sketch_circle(doc, 0.0, 0.0, d["ra"])
        P.sketch_circle(doc, 0.0, 0.0, d["rb"])
        P.sketch_circle(doc, 0.0, 0.0, d["rf"])

    sk = c.get_com_member(doc, "GetActiveSketch2")
    segs_n = len(list(c.get_com_member(sk, "GetSketchSegments") or []))
    cts_n = len(list(c.get_com_member(sk, "GetSketchContours") or []))
    print(f"样条 {n_sp} · 圆弧 {n_ar}"
          f"{' + 3 参照圆' if ref_circles else ''}")
    print(f"草图段数 {segs_n} · SW 认定闭合轮廓数 {cts_n}")

    #: ★ **不退出草图** —— 让业主直接看着草图状态（闭合区域会有阴影）
    try:
        c.get_com_member(doc, "ViewZoomtofit2")
    except Exception:  # noqa: BLE001
        pass
    try:
        c.get_com_member(doc, "ForceRebuild3", False)
    except Exception:  # noqa: BLE001
        pass
    title = str(c.get_com_member(doc, "GetTitle") or "?")
    print(f"\n★ 文档已留在 SolidWorks 窗口：{title}")
    print("★ 草图处于**编辑中**状态；请直接看屏幕。")
    print("★ 本脚本不关闭文档（按你的要求留着）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
