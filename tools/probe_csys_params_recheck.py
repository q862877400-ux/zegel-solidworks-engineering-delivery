"""★ 真机验 `csys_params`（★ 阶段 3 补能力 · 第 7 个 · 第 6 个族）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\ICoordinateSystemFeatur
# eData\`）
# 文件:   `scripts/sw_feature_readback.py::csys_params`（★ 刚补的能力）
# 定位:   ★ **改完必须跑一次验证**（★ 本仓纪律）⇒ 调**能力层本体** ✓
#   ★★ **前置签名**（★ **先在仓里搜出来的** —— ★ 而这次我**第一版又猜错了**：★ 猜成
#     `sw_part.insert_coordinate_system` ⇒ 真机报 `AttributeError: module 'sw_part' has no
#     attribute 'insert_coordinate_system'`）⇒ ★★★ **真位置是**另一个模块****：
#     ★ `scripts/sw_ref_geometry.py::insert_coordinate_system(model, x_flipped=False,
#       y_flipped=False, z_flipped=False)` ✓
# ★★★★ **⇒ 这是那条判据的**第 5 次**生效**（★ 前 4 次：`hole_wizard` · `GetFeatureByName
# ` ·
#       `fillet` 的参序 · 本次**跨模块**）✓
#   ★★★ **判据（★ 对官方逐字）**：
#     ★ 建一个坐标系 ⇒ ★ `GetOriginEntityType()` ⇒ ★ **一个 int**（★ `swSelectType_e`）·
#     ★ 三个 `Get{X,Y,Z}AxisEntitiesCount()` ⇒ ★ **≥ 0 的 int** ·
#     ★★ `Transform` ⇒ ★ **非 None**、★ 且 `ArrayData` 是 **16 个 double**（★ 变换矩阵）✓
#   覆盖:   全文件
# ---------------------------------------------------------------------------

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = REPO / "output" / "csys-params-capability-recheck.json"


def main() -> int:
    from sw_connect import connect_solidworks, get_com_member, new_document
    import sw_part as P
    import sw_ref_geometry as RG  # noqa: PLC0415
    from sw_feature_readback import csys_params

    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    with P.sketch(model, "Front Plane") as sk:
        sm = get_com_member(model, "SketchManager")
        for a, b in (
            ((-0.05, -0.03), (0.05, -0.03)),
            ((0.05, -0.03), (0.05, 0.03)),
            ((0.05, 0.03), (-0.05, 0.03)),
            ((-0.05, 0.03), (-0.05, -0.03)),
        ):
            get_com_member(sm, "CreateLine", a[0], a[1], 0.0, b[0], b[1], 0.0)
    P.extrude_boss(model, sk, 20.0)

    cs = {"error": None, "returned": None}
    try:
        cs["returned"] = str(RG.insert_coordinate_system(model))[:80]
    except Exception as exc:  # noqa: BLE001
        cs["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])

    r = csys_params(model)
    checks = {
        "★ 找到坐标系特征": bool(r.get("feature")),
        "★ GetOriginEntityType 是 int": isinstance(r.get("GetOriginEntityType"), int),
        "★ GetXAxisEntitiesCount 是 int": isinstance(
            r.get("GetXAxisEntitiesCount"), int
        ),
        "★ GetYAxisEntitiesCount 是 int": isinstance(
            r.get("GetYAxisEntitiesCount"), int
        ),
        "★ GetZAxisEntitiesCount 是 int": isinstance(
            r.get("GetZAxisEntitiesCount"), int
        ),
        "★ Transform 非 None": bool(r.get("Transform"))
        and r.get("Transform") != "None",
        "★ Transform.ArrayData 是 16 个数": r.get("Transform.ArrayData_len") == 16,
        "★ 无 error": not r.get("error"),
    }
    R = {
        "★_判据": "★ 逐个对官方 `## Returns`（★ 见 `output/_read_csys_members.py` 的逐条读数）",
        "★_建坐标系": cs,
        "读取": {k: str(v)[:60] for k, v in r.items()},
        "★_逐条判据": checks,
        "★_全过": all(checks.values()),
    }
    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("★ 建坐标系:", json.dumps(cs, ensure_ascii=False)[:140])
    print("★ 读取:", json.dumps(R["读取"], ensure_ascii=False)[:420])
    for k, v in checks.items():
        print("   %-38s %s" % (k, "✓" if v else "**✗**"))
    print("★ 全过 =", all(checks.values()))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
