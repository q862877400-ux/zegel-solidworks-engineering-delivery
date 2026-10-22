"""★ 真机验 `fillet_params` 并**测出那一族的单位口径**（★ 阶段 3 · 第 6 个能力）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\ISimpleFilletFeatureDat
# a2\`）
# 文件:   `scripts/sw_feature_readback.py::fillet_params`（★ 刚补的能力）
# 定位:   ★ **改完必须跑一次验证**（★ 本仓纪律）⇒ 调**能力层本体** ✓
#   ★★ **⚠ 前置签名**（★ **先在仓里搜出来的** —— ★ 不是猜的）：
# ★ `sw_part.fillet(model, radius, edges=None)` ⇒ ★★ **`radius` 在第 2 位、★ `edges` 关
# 键字** ✓
#     （★ 我第一版注释里猜成 `fillet(model, selection, radius_mm)` ⇒ **错的**）✓
#   ★★★ **判据**：★ 建一块板 ⇒ 给一条边打 `R5` 圆角 ⇒ `fillet_params`：
#     ★ `DefaultRadius` ⇒ ★ 期望 ≈ 5（★ 若 ≈ 0.005 则是米）· ★ `GetEdgeCount` ⇒ **1** ·
#     ★ `GetSetbackVerticesCount` ⇒ **0** · ★ `Type` / ★ `OverflowType` ⇒ int ✓
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = REPO / "output" / "fillet-params-capability-recheck.json"


def main() -> int:
    from sw_connect import connect_solidworks, get_com_member, new_document
    import sw_part as P
    from sw_feature_readback import fillet_params

    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    with P.sketch(model, "Front Plane") as sk:
        sm = get_com_member(model, "SketchManager")
        for a, b in (((-0.05, -0.03), (0.05, -0.03)), ((0.05, -0.03), (0.05, 0.03)),
                     ((0.05, 0.03), (-0.05, 0.03)), ((-0.05, 0.03), (-0.05, -0.03))):
            get_com_member(sm, "CreateLine", a[0], a[1], 0.0, b[0], b[1], 0.0)
    P.extrude_boss(model, sk, 20.0)

    #: ★★ 前置：★ 按 `index:<n>` 选一条边（★ 边没有名字 —— ★ 已知事实 32）✓
    sel = {"error": None}
    try:
        from sw_selection_spec import resolve_selection                    # noqa: PLC0415
        resolve_selection(model, "index:0", "EDGE")
        sel["ok"] = True
    except Exception as exc:                                               # noqa: BLE001
        sel["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
    fr = {"error": None, "returned": None}
    try:
        fr["returned"] = str(P.fillet(model, 5.0))[:120]      #: ★ 真签名：radius 在第 2 位 ✓
    except Exception as exc:                                               # noqa: BLE001
        fr["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])

    r = fillet_params(model)
    checks = {
        "★ 找到圆角特征": bool(r.get("feature")),
        "★ GetEdgeCount = 1": r.get("GetEdgeCount") == 1,
        "★ GetSetbackVerticesCount = 0": r.get("GetSetbackVerticesCount") == 0,
        "★ Type 是 int": isinstance(r.get("Type"), int),
        "★ OverflowType 是 int": isinstance(r.get("OverflowType"), int),
        "★ RoundCorners 是 bool": isinstance(r.get("RoundCorners"), bool),
        "★ 无 error": not r.get("error"),
    }
    #: ★★★★ **单位判定（★ 第六层）** —— ★ 判据写死、★ 只报 ✓
    verdict = "★ 判不出"
    try:
        v = float(r.get("DefaultRadius"))
        if abs(v - 5.0) < 0.5:
            verdict = "★ 随**文档单位**（★ 读数 %r ⇒ 毫米文档下就是 5mm）" % v
        elif abs(v - 0.005) < 5e-4:
            verdict = "★ 写死**米**（★ 读数 %r）" % v
        else:
            verdict = "★ 读数 %r ⇒ 两种都不是（★ 要另查）" % v
    except Exception:                                                      # noqa: BLE001
        pass

    R = {"★_目的": "★ 验 `fillet_params` + ★ **测出那一族的单位口径**（★ 官方 `## Returns` 没写）",
         "★_前置选择": sel, "★_建圆角": fr,
         "读取": {k: str(v)[:50] for k, v in r.items()},
         "★_逐条判据": checks, "★_全过": all(checks.values()),
         "★_单位判定": verdict}
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("★ 前置:", json.dumps(sel, ensure_ascii=False)[:120])
    print("★ 建圆角:", json.dumps(fr, ensure_ascii=False)[:160])
    print("★ 读取:", json.dumps(R["读取"], ensure_ascii=False)[:400])
    for k, v in checks.items():
        print("   %-36s %s" % (k, "✓" if v else "**✗**"))
    print("★ 全过 =", all(checks.values()))
    print("★ 单位判定:", verdict)
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
