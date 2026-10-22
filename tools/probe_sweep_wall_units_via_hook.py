"""★ 真机：★ 用**新钩子**在 `CreateFeature` **之前**设薄壁 ⇒ 量 `GetWallThickness` 的口径。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 官方 `C:\\swapi\\types\\ISweepFeatureData\\*.md`
# 文件:   tools/probe_sweep_wall_units_via_hook.py（★ 只报不动 —— 证据脚本 · 新）
# 定位:   ★ 轮 128 查清：★ **"先建后改"这条路**不存在**** —— ★ 官方 `## Remarks` 逐字：
#     ★「To make a thin sweep, you must set this property **before calling
#       `IFeatureManager::CreateFeature`**. ★★ **You cannot make a thin-walled sweep feature
#       after the sweep has been created**, and ★★ **you cannot edit a sweep feature to
#       make it thin walled**.」✓
#   ★★ **⇒ 轮 129 给 `sw_sweep.create_sweep_report` 加了一个显式钩子 `mutate=None`**
#     （★ 它在 `CreateDefinition` 之后、★ `CreateFeature` **之前**被调用）✓
#   ★★★ **本探针用那个钩子**在正确的位置设薄壁 ⇒ ★ **再量体积** ✓
#   **判据（★ 几何、★ 独立、★ 三个候选分得开）**：
#     ★ 轮廓：圆 **半径 3 mm** · ★ 路径 **40 mm** ⇒
#       · ★ **实体**圆柱 = π·3²·40 = **1130.97** ✓
# · ★★ **写壁厚 `0.002`** ⇒ ★ 若口径是**米** ⇒ 实际 **2 mm** ⇒ 环带 = π·(3²−1²)·40 = **1
# 005.31** ✓
#       · ★★ 若口径是**毫米** ⇒ `0.002 mm` ⇒ 环带 = π·(3²−2.998²)·40 = **1.51** ✓
#     ★★★ **⇒ 1130.97 / 1005.31 / 1.51 三个候选分得开** ⇒ ★ **最近候选分类即可判** ✓
#   ★★★★ **⚠ 判定用**最近候选**、★ 且**候选表不许漏****（★ 轮 128 我漏了"没生效"那个、
#     ★ 于是误判成"米"）⇒ ★ **本探针把三个候选都摆上** ✓
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

OUT = ROOT / "output" / "sweep-wall-via-hook-recheck.json"
R_MM, L_MM, T_WRITE = 3.0, 40.0, 0.002
C_SOLID = math.pi * R_MM**2 * L_MM
C_METER = math.pi * (R_MM**2 - (R_MM - 2.0) ** 2) * L_MM
C_MM = math.pi * (R_MM**2 - (R_MM - 0.002) ** 2) * L_MM

ev: dict = {
    "★_判据": (
        "轮廓半径 3 mm · 路径 40 mm · **写壁厚 0.002** ⇒ 量体积、"
        "★ **最近候选分类**：实体 %.2f / 米 %.2f / 毫米 %.2f" % (C_SOLID, C_METER, C_MM)
    ),
    "★_候选": {
        "实体_即薄壁没生效": round(C_SOLID, 2),
        "若口径是米_环带": round(C_METER, 2),
        "若口径是毫米_环带": round(C_MM, 2),
    },
    "steps": [],
}


def step(name: str, **kw) -> None:
    ev["steps"].append(dict(name=name, **kw))
    print("★ %-30s %s" % (name, json.dumps(kw, ensure_ascii=False)[:230]))


def main() -> int:
    import sw_part as P
    import sw_sweep as SW
    from sw_connect import (
        connect_solidworks,
        get_com_member,
        new_document,
        set_com_member,
    )

    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    step("new_part", title=str(get_com_member(model, "GetTitle")))

    with P.sketch(model, "Front Plane") as sk_prof:
        P.sketch_circle(model, 0.0, 0.0, R_MM)
    with P.sketch(model, "Top Plane") as sk_path:
        P.sketch_line(model, 0.0, 0.0, 0.0, L_MM)
    P._select_sketch_feature_by_name(model, str(sk_prof), mark=1)
    feat = P._safe_com_member(model, "FeatureByName", str(sk_path))
    for cand in P._get_sketch_name_candidates(str(sk_path)):
        if feat is None:
            feat = P._safe_com_member(model, "FeatureByName", cand)
    P._select_com_object(feat, append=True, mark=4)

    #: ★★★★ 钩子：★ 在 `CreateFeature` **之前**设薄壁 ✓
    hook_log: dict = {}

    def _thin(data):
        set_com_member(data, "ThinFeature", True)
        set_com_member(data, "ThinWallType", 0)  #: 0 = One Direction
        get_com_member(data, "SetWallThickness", True, T_WRITE)
        hook_log["set"] = {
            "ThinFeature": True,
            "ThinWallType": 0,
            "SetWallThickness(True, %r)" % T_WRITE: True,
        }
        try:
            hook_log["ThinFeature_readback"] = get_com_member(data, "ThinFeature")
        except Exception as exc:  # noqa: BLE001
            hook_log["ThinFeature_readback"] = "err: %s" % str(exc)[:60]

    rep = SW.create_sweep_report(model, False, mutate=_thin)
    step(
        "create_sweep_report(mutate=钩子)",
        ok=rep.get("ok"),
        feature=rep.get("feature_name"),
        type_name=rep.get("type_name"),
    )
    step("hook", **hook_log)

    got = None
    try:
        import sw_feature_readback as R

        got = R.sweep_params(model)
        step(
            "sweep_params",
            feature=got.get("feature"),
            IsThinFeature=got.get("IsThinFeature"),
            ThinFeature=got.get("ThinFeature"),
            GetWallThickness=got.get("GetWallThickness"),
        )
    except Exception as exc:  # noqa: BLE001
        step("sweep_params_EXC", err="%s: %s" % (type(exc).__name__, str(exc)[:130]))

    vol = None
    try:
        mp = get_com_member(get_com_member(model, "Extension"), "CreateMassProperty")
        vol = float(get_com_member(mp, "Volume"))
        step("volume", mm3=round(vol, 3))
    except Exception as exc:  # noqa: BLE001
        step("volume_EXC", err=str(exc)[:110])

    #: ★★★★ **最近候选分类**（★ 三个候选都摆上、★ 不许漏）✓
    cands = [
        ("★ **薄壁没生效**（★ 体积 = 实体）", C_SOLID),
        ("★ **米**（★ `0.002` ⇒ 2 mm 环带）", C_METER),
        ("★ **毫米**（★ `0.002` ⇒ 0.002 mm 环带）", C_MM),
    ]
    if vol is None:
        ev["★_GetWallThickness_口径"] = "★ **量不到体积** ⇒ ★ 如实标"
    else:
        near = min(cands, key=lambda kv: abs(vol - kv[1]))
        gap = abs(vol - near[1])
        others = min(abs(vol - v) for k, v in cands if k != near[0])
        ev["★_体积_实测"] = round(vol, 3)
        ev["★_最近候选"] = near[0]
        ev["★_最近距离"] = round(gap, 3)
        ev["★_次近距离"] = round(others, 3)
        if gap < others * 0.5:
            ev["★_GetWallThickness_口径"] = (
                "%s ⇒ ★ 实测 %.3f（★ 最近候选 %.2f · ★ 次近 %.2f）"
                % (near[0], vol, near[1], others)
            )
        else:
            ev["★_GetWallThickness_口径"] = (
                "★ **读数不明确**（★ 实测 %.3f · ★ 最近 %s %.2f · ★ 次近 %.2f）⇒ ★ 如实标、★ 不猜"
                % (vol, near[0], near[1], others)
            )
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
