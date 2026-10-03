"""★ 真机：★ 用**折线**轮廓建筋（★ 照官方示例的 `CreateLine ×3`）⇒ 读回 ⇒ 量口径。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 官方示例 `C:\\swapi\\examples\\Get_Rib_Feature_Data_Example_CSharp.md`
# 文件:   tools/probe_rib_polyline_recheck.py（★ 只报不动 —— 证据脚本 · 新）
# 定位:   ★ 2026-10-04（轮 125）：★ 上一轮（★ 轮 124）把筋的账停下在**第 4 次修补**、
#   结论是「★ **没建成与 arity 无关** ⇒ ★ 下一个要查的是**轮廓的几何**」✓
#   ★★ **官方示例逐字**（★ 那是**签名与 Remarks 都给不出**的调用序）：
#     ★ `Part.SketchManager.InsertSketch(true)` ⇒
#     ★★ **`skSegment = Part.SketchManager.CreateLine(…)` **×3** ⇒ 一条**折线**** ⇒
#     ★ `Part.ClearSelection2(true)` · ★ `Part.SketchManager.InsertSketch(true)` ⇒
#     ★★ `Part.Extension.SelectByID2("Sketch2", "SKETCH", 0, 0, 0, false, 0, null, 0)` ⇒
#     ★★★ `Part.FeatureManager.InsertRib(true, false, 0.00254, 0, false, false, true,
#       0.0174532925199433, false, false)` ✓
#   ★★★ **而本仓两次都传了**一条直线** ⇒ **都没建成** ✓
#   ★★★★ **⚠ 本探针**不改**上一轮那个探针**（★ 纪律①：★ 证据脚本只报不动）⇒
#     ★ **另起一个文件**、★ **另写一份证据** ✓
#   ★★★★★ **判据（★ 可核）**：★ 板 60×40×10（毫米）⇒ 折线轮廓（★ 三段、★ 跨过板）
#     ⇒ 筋厚 **3 mm** ⇒ ★★ **建成？** ⇒ ★ 读 `Thickness` 看 3.0 还是 0.003 ✓
#   覆盖:   全文件
# ---------------------------------------------------------------------------

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = ROOT / "output" / "rib-polyline-capability-recheck.json"
ev: dict = {
    "★_判据": ("板 60×40×10（毫米）⇒ 轮廓用**折线**（★ 照官方 `CreateLine ×3`）⇒ "
               "筋厚 3 mm ⇒ 建成与否 + `Thickness` 是 3.0 还是 0.003"),
    "★_与上一轮的区别": "轮廓从**一条直线**换成**折线**（★ 那是官方示例唯一的几何线索）",
    "steps": []}


def step(name: str, **kw) -> None:
    ev["steps"].append(dict(name=name, **kw))
    print("★ %-28s %s" % (name, json.dumps(kw, ensure_ascii=False)[:210]))


def main() -> int:
    from sw_connect import connect_solidworks, get_com_member, new_document
    import sw_feature_readback as R
    import sw_part as P

    app, _ = connect_solidworks(visible=True)
    step("connect", ok=bool(app))
    model = new_document(app, "part")
    step("new_part", title=str(get_com_member(model, "GetTitle")))

    # ── ★ 板 60×40×10 ───────────────────────────────────────────────────
    with P.sketch(model, "Front Plane") as sk_base:
        sm0 = get_com_member(model, "SketchManager")
        for x1, y1, x2, y2 in ((-30.0, -20.0, 30.0, -20.0), (30.0, -20.0, 30.0, 20.0),
                               (30.0, 20.0, -30.0, 20.0), (-30.0, 20.0, -30.0, -20.0)):
            get_com_member(sm0, "CreateLine", x1, y1, 0.0, x2, y2, 0.0)
    r0 = P.extrude_boss(model, sk_base, 10.0)
    step("base_plate", depth_mm=10.0, ok=(r0 is not None))

    # ── ★★★ 照官方序：★ **先抽壳** ──────────────────────────────────────
    #: ★★★★★★ 2026-10-04（轮 125）**那条结构性线索**（★ 它就在官方示例里）：
    #:   ★ 官方示例逐字 —— `SelectByID2("", "FACE", …)` ⇒
    #:     ★★ **`Part.InsertFeatureShell(0.00254, false);`（★ 先抽壳）** ⇒
    #:     ★ `InsertRefPlane(128,0,128,0,0,0)` ⇒ ★ `CreateLine ×3` ⇒
    #:     ★ `SelectByID2("Sketch2","SKETCH",…)` ⇒ ★ `InsertRib(…)` ✓
    #:   ★★ **⇒ 而官方那条示例拿的是**抽壳过的方块**（★ `block20.sldprt`）⇒
    #:     ★★★ **⇒ 本探针照那个序：★ 板 ⇒ **抽壳** ⇒ 折线 ⇒ 筋** ✓
    #:   ★★★★ **⚠ 这是**新假设**（★ "前置的顺序"）、★ 不是重复上一轮那个"换轮廓形状"** ✓
    sh = P.shell_report(model, 2.54)
    step("shell_report", ok=sh.get("ok"), created=sh.get("created_object"),
         error=(sh.get("error") or "")[:90])

    # ── ★★ 轮廓：**折线**（★ 照官方 ×3）──────────────────────────────────
    #: ★ 官方那条折线**跨过实体**（★ 从一个方向进、★ 从另一个方向出）⇒
    #:   ★★ 本探针照办：★ 三段连成一条**跨过板**的折线（★ 起点在板外、★ 终点在板外）✓
    with P.sketch(model, "Front Plane") as sk_rib:
        sm = get_com_member(model, "SketchManager")
        #: ★ 三点连成的折线（★ 板是 x∈[-30,30] · y∈[-20,20]）
        pts = ((-40.0, -10.0), (0.0, -10.0), (0.0, 10.0), (40.0, 10.0))
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            get_com_member(sm, "CreateLine", x1, y1, 0.0, x2, y2, 0.0)
    step("sketch(polyline)", sketch_name=str(sk_rib), segments=3,
         note="★ 起点在板外、终点在板外（★ 跨过实体）；★ 且**板已抽壳**")

    #: ★★★ 官方第 ⑦ 步：★ **先选中草图**（★ `SelectByID2(<sketch>, "SKETCH", 0,0,0, false, 0, …)`）✓
    #:   本仓 `rib()` 内部走 `_ensure_sketch_selected` ⇒ 那一步**它自己做** ✓
    rep = P.rib_report(model, sk_rib, 3.0)
    step("rib_report", ok=rep.get("ok"), created=rep.get("created_object"),
         error=(rep.get("error") or "")[:110])

    got = R.rib_params(model)
    step("rib_params", feature=got.get("feature"), definition=got.get("definition"),
         error=got.get("error"), Thickness=got.get("Thickness"),
         Type=got.get("Type"), ExtrusionDirection=got.get("ExtrusionDirection"),
         DraftAngle=got.get("DraftAngle"), EnableDraft=got.get("EnableDraft"),
         IsTwoSided=got.get("IsTwoSided"))

    th = got.get("Thickness")
    if th is None or isinstance(th, str):
        ev["★_Thickness_口径"] = "★ **没读到**（★ 值 %r）" % (th,)
    elif abs(float(th) - 3.0) < 1e-9:
        ev["★_Thickness_口径"] = "★ **随文档单位**（★ 毫米文档 ⇒ 3.0）"
    elif abs(float(th) - 0.003) < 1e-12:
        ev["★_Thickness_口径"] = "★ **米**（★ 3 mm ⇒ 0.003）"
    else:
        ev["★_Thickness_口径"] = "★ **都不是**（★ 值 %.6g）" % float(th)
    step("VERDICT_Thickness", value=th, verdict=ev["★_Thickness_口径"])

    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
    print("★ 已写", OUT)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as exc:                                          # noqa: BLE001
        ev["fatal"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("★ FATAL:", ev["fatal"])
        raise SystemExit(1)
