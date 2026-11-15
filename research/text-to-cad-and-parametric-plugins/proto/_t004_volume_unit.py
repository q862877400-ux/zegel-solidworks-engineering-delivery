"""T004: 用 10x10x10 方块核对 mass_properties()["volume"] 的单位。

判据：读回 ≈1000 ⇒ 单位是 mm^3；读回 ≈1e-6 ⇒ 单位是 m^3。
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"D:\Agent-Studio\Deepseek-Harness\DSH-Data\workspace\SW")
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8")

import sw_connect  # noqa: E402
from sw_mass_property import mass_properties  # noqa: E402
from sw_part import extrude_boss, sketch, sketch_line  # noqa: E402
from sw_feature_readback import solid_body_extent_mm  # noqa: E402

TEMPLATE = r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_part.prtdot"


def main() -> int:
    sw, _ = sw_connect.connect_solidworks(visible=True)
    print("SolidWorks:", "已连接")

    model = sw.NewDocument(TEMPLATE, 0, 0, 0)
    if model is None:
        print("VERDICT: NewDocument 返回 None —— 模板路径可能不对")
        return 1
    print("新建零件 OK")

    pts = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    with sketch(model, "Front Plane") as sk:
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            if sketch_line(model, x1, y1, x2, y2) is None:
                print("VERDICT: sketch_line 返回 None")
                return 1
    print("草图 OK（4 条线，10x10 mm）")

    feat = extrude_boss(model, sk, sw_connect.mm(10))
    if feat is None:
        print("VERDICT: extrude_boss 返回 None —— 拉伸失败")
        return 1
    print("拉伸 OK（10 mm）")

    mp = mass_properties(model)
    bbox = solid_body_extent_mm(model)
    vol = mp["volume"]

    print()
    print("volume =", vol)
    print("units  =", mp["units"]["volume"])
    print("bbox   =", {k: bbox.get(k) for k in ("x_mm", "y_mm", "z_mm")})
    print()

    if vol is None:
        print("VERDICT: volume 读不到")
        return 1
    if abs(vol - 1000.0) < 5.0:
        print("VERDICT: volume 单位 = mm^3（10x10x10 读回 %.3f）" % vol)
        return 0
    if abs(vol - 1e-6) < 1e-8:
        print("VERDICT: volume 单位 = m^3（读回 %.3e）" % vol)
        return 0
    print("VERDICT: 单位不明（读回 %.6g，既不是 1000 也不是 1e-6）" % vol)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
