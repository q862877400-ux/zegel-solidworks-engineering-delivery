"""★ 真机：★ 建**薄壁**扫描、写一个**已知壁厚** ⇒ 用**体积**独立判它的口径。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 官方 `C:\\swapi\\types\\ISweepFeatureData\\*.md`
# 文件:   tools/probe_sweep_wall_units_recheck.py（★ 只报不动 —— 证据脚本 · 新）
# 定位:   ★ 轮 127 量出了 `CircularProfileDiameter`（★ 随文档单位）⇒
# ★★ **而 `GetWallThickness` 仍未定案**（★ 官方：valid only if `IsThinFeature` is true）
# ⇒
#   ★★★ **⇒ 本探针**建一个薄壁扫描**、★ 写一个**已知壁厚** ⇒ **量体积** ✓
#   **官方依据（★ 逐字）**：
# · ★ `IsThinFeature()` ⇒ `System.bool IsThinFeature()` ⇒「True if a thin-walled sweep f
# eature」
#       ★ `## Remarks: Note that you can make …`（★ 截断）✓
#     · ★ `ThinFeature {get; set;}` ⇒「True to make a thin-walled sweep feature」✓
#     · ★ `ThinWallType {get; set;}` ⇒「0 = One Direction …」✓
#     · ★★ `SetWallThickness(bool Forward, double WallThickness)` ⇒ **2 参** ✓
#     · ★★ `GetWallThickness(bool Forward)` ⇒ `## Returns: Wall thickness`（★ **无单位**）✓
#   ★★★★★ **判据（★ 几何、★ 独立、★ 两个量级差得很开）**：
#     ★ 轮廓：圆 **半径 3 mm**（★ 直径 6）· ★ 路径长 **40 mm** ⇒
#       · ★ **实体**圆柱体积 = π·3²·40 = **1131.0** mm³ ✓
#       · ★★ **写壁厚 `0.002`** ⇒
# - ★ 若口径是**米** ⇒ `0.002 m = **2 mm**` ⇒ 环带面积 = π·(3²−1²)=25.13 ⇒ 体积 **1005.3
# ** ✓
#         - ★ 若口径是**毫米** ⇒ `0.002 mm` ⇒ 环带面积 = π·(3²−2.998²)=0.0377 ⇒ 体积 **1.51** ✓
#     ★★★ **⇒ 1005 与 1.5 差**三个量级**** ⇒ **口径自明**、★ **而那是几何、不是读回属性** ✓
#   ★★★★ **⚠ 第 3 参**走本仓正解****：★ `create_empty_dispatch_variant()`
#     （★ 轮 127 实测：★ 传裸 `None` ⇒ `com_error(-2147352571, '类型不匹配。', None, 3)`）✓
#   覆盖:   全文件
# -----------------------------------------------------------------──────────

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = ROOT / "output" / "sweep-wall-units-capability-recheck.json"
R_MM, L_MM, T_WRITE = 3.0, 40.0, 0.002
SOLID = math.pi * R_MM**2 * L_MM
RING_M = math.pi * (R_MM**2 - (R_MM - 2.0) ** 2) * L_MM  # ★ 0.002 m = 2 mm
RING_MM = math.pi * (R_MM**2 - (R_MM - 0.002) ** 2) * L_MM  # ★ 0.002 mm

ev: dict = {
    "★_判据": (
        "轮廓半径 3 mm · 路径 40 mm · **写壁厚 0.002** ⇒ 量体积："
        "★ ≈%.1f ⇒ **米**（0.002 m = 2 mm）· ★ ≈%.2f ⇒ **毫米**（0.002 mm）"
        % (RING_M, RING_MM)
    ),
    "★_参照": {
        "实体圆柱": round(SOLID, 2),
        "若口径是米_环带": round(RING_M, 2),
        "若口径是毫米_环带": round(RING_MM, 2),
    },
    "steps": [],
}


def step(name: str, **kw) -> None:
    ev["steps"].append(dict(name=name, **kw))
    print("★ %-30s %s" % (name, json.dumps(kw, ensure_ascii=False)[:230]))


def main() -> int:
    from sw_connect import (
        connect_solidworks,
        create_empty_dispatch_variant,
        get_com_member,
        new_document,
        set_com_member,
    )
    import sw_part as P
    import sw_sweep as SW

    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    step("new_part", title=str(get_com_member(model, "GetTitle")))

    with P.sketch(model, "Front Plane") as sk_prof:
        P.sketch_circle(model, 0.0, 0.0, R_MM)
    with P.sketch(model, "Top Plane") as sk_path:
        P.sketch_line(model, 0.0, 0.0, 0.0, L_MM)
    got_prof = P._select_sketch_feature_by_name(model, str(sk_prof), mark=1)
    feat = P._safe_com_member(model, "FeatureByName", str(sk_path))
    for cand in P._get_sketch_name_candidates(str(sk_path)):
        if feat is None:
            feat = P._safe_com_member(model, "FeatureByName", cand)
    P._select_com_object(feat, append=True, mark=4)
    rep = SW.create_sweep_report(model, False)
    step("create_sweep_report", ok=rep.get("ok"), type_name=rep.get("type_name"))

    vol0 = None
    try:
        mp = get_com_member(model, "Extension")
        mp = get_com_member(mp, "CreateMassProperty") if mp is not None else None
        vol0 = float(get_com_member(mp, "Volume")) if mp is not None else None
        step(
            "volume_before",
            mm3=round(vol0, 3) if vol0 is not None else None,
            expect_solid=round(SOLID, 2),
        )
    except Exception as exc:  # noqa: BLE001
        step("volume_before_EXC", err="%s: %s" % (type(exc).__name__, str(exc)[:120]))

    #: ★★ 设薄壁 + 已知壁厚 ⇒ `ModifyDefinition`（★ 第 3 参走正解）✓
    feat = P._safe_com_member(
        model, "FeatureByName", str(rep.get("feature_name") or "扫描1")
    )
    data = get_com_member(feat, "GetDefinition") if feat is not None else None
    applied = {"error": None}
    if data is not None:
        try:
            set_com_member(data, "ThinFeature", True)
            set_com_member(data, "ThinWallType", 0)  #: 0 = One Direction
            get_com_member(data, "SetWallThickness", True, T_WRITE)
            applied["set"] = {
                "ThinFeature": True,
                "ThinWallType": 0,
                "SetWallThickness(True, %r)" % T_WRITE: True,
            }
            applied["modify_ok"] = bool(
                get_com_member(
                    feat,
                    "ModifyDefinition",
                    data,
                    model,
                    create_empty_dispatch_variant(),
                )
            )
        except Exception as exc:  # noqa: BLE001
            applied["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
    step("apply_thin_wall", **applied)

    try:
        mp = get_com_member(get_com_member(model, "Extension"), "CreateMassProperty")
        vol1 = float(get_com_member(mp, "Volume"))
        step("volume_after", mm3=round(vol1, 3))
        ev["★_体积_实测"] = round(vol1, 3)
        #: ★★★★ **容差要**小于两个候选之间距离的一半**** ——
        #:   ★ 第一版写 `max(30, RING_M*0.15) = 150.8` ⇒ ★★ **把"没生效"（1130.97）
        #:     判成了"米"（1005.31）**（★ 两者只差 11%、★ 而容差 15%）✗
        #:   ★★ **⇒ 改成 5%**（★ 远小于两候选距离的一半、★ 也远大于数值噪声）✓
        #: ★★★★ **最近候选分类**（★ 第三版 —— ★ 前两版的容差带都误判了）✓
        #:   ★ **三个候选**（★ 这次**不漏**）：★ 没生效（= 实体体积）· ★ 米 · ★ 毫米 ✓
        _cands = [
            ("★ **薄壁没生效**（★ 体积与实体一致 ⇒ `ThinFeature` 没被采纳）", SOLID),
            ("★ **米**（★ 写 `0.002` ⇒ 实际 2 mm）", RING_M),
            ("★ **毫米**（★ 写 `0.002` ⇒ 0.002 mm）", RING_MM),
        ]
        _near = min(_cands, key=lambda kv: abs(vol1 - kv[1]))
        _gap = abs(vol1 - _near[1])
        _others = min(abs(vol1 - v) for k, v in _cands if k != _near[0])
        ev["★_体积_实测"] = round(vol1, 3)
        ev["★_最近候选"] = _near[0]
        ev["★_与最近候选的距离"] = round(_gap, 3)
        ev["★_与次近候选的距离"] = round(_others, 3)
        if _gap < _others * 0.5:
            ev["★_GetWallThickness_口径"] = (
                "%s ⇒ ★ 实测体积 %.3f（★ 候选 %.2f · ★ 次近 %.2f）"
                % (_near[0], vol1, _near[1], _others)
            )
        else:
            ev["★_GetWallThickness_口径"] = (
                "★ **读数不明确**（★ 实测 %.3f · ★ 最近 %s(%.2f) · ★ 次近 %.2f）⇒ ★ 如实标、★ 不猜"
                % (vol1, _near[0], _near[1], _others)
            )
    except Exception as exc:  # noqa: BLE001
        ev["★_GetWallThickness_口径"] = "★ **量不到**：%s" % str(exc)[:90]
    step("VERDICT", verdict=ev["★_GetWallThickness_口径"])

    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
    print("★ 已写", OUT)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as exc:  # noqa: BLE001
        ev["fatal"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("★ FATAL:", ev["fatal"])
        raise SystemExit(1)
