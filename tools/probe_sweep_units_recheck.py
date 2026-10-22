"""★ 真机：★ 给扫描设**圆轮廓 + 已知直径** ⇒ 用**包围盒独立判**那个长度量的口径。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 官方 `C:\\swapi\\types\\ISweepFeatureData\\*.md`
# 文件:   tools/probe_sweep_units_recheck.py（★ 只报不动 —— 证据脚本 · 新）
# 定位:   ★ 轮 126 把 `sweep_params` 建成、★ **而两个长度量的口径仍未定案**
#   （★ 读数都是 `0.0`、★ 而那是**应然的** —— ★ `CircularProfile=false` 时直径本就该 0）✓
#   ★★ **⇒ 量它们必须**让它们非零**** ⇒ ★ **本探针给圆轮廓一个**已知直径** ✓
#   **官方依据（★ 逐字）**：
#     · ★ `IFeature::ModifyDefinition(Data, TopDoc, Component)` ⇒ **3 参、回 bool** ✓
#     · ★ `ISweepFeatureData::CircularProfile` ⇒ `bool {get; set;}` ✓
# · ★★ `ISweepFeatureData::CircularProfileDiameter` ⇒ `double {get; set;}`、★ `## Remark
# s`
#       「**This property is valid only if `CircularProfile` is set to true.**」✓
#   ★★★ **⚠ 判据要**独立****（★ 不能"写 12.0 再读回 12.0"那样自证）⇒
#     ★★ **⇒ 本探针用**几何**判**：★ 设直径 `12.0` ⇒ 用 `ModifyDefinition` 落地 ⇒
#       ★★★ **⇒ 量实体的**包围盒****：
#         · ★ 若口径是**毫米** ⇒ 管径 **12 mm** ⇒ 横截面 **≈12** ✓
#         · ★ 若口径是**米** ⇒ 那个 `12.0` 是 **12 米** ⇒ 横截面 **≈12000** ✓
#   ★★★★ **⇒ 那是一个**几何独立判据**（★ 与"读回同一个属性"**完全不同**）✓
#   覆盖:   全文件
# ---------------------------------------------------------------------------

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = ROOT / "output" / "sweep-units-capability-recheck.json"
ev: dict = {
    "★_判据": (
        "设 `CircularProfile=True` + `CircularProfileDiameter=12.0` ⇒ `ModifyDefinition` ⇒ "
        "量包围盒：★ 横截面 ≈12 ⇒ **毫米**；★ ≈12000 ⇒ **米**"
    ),
    "★_为什么用几何": "★ 读回同一个属性是**循环自证**；几何是**独立**的 ✓",
    "steps": [],
}


def step(name: str, **kw) -> None:
    ev["steps"].append(dict(name=name, **kw))
    print("★ %-30s %s" % (name, json.dumps(kw, ensure_ascii=False)[:230]))


def main() -> int:
    import sw_part as P
    import sw_sweep as SW
    from sw_connect import connect_solidworks, get_com_member, new_document

    app, _ = connect_solidworks(visible=True)
    step("connect", ok=bool(app))
    model = new_document(app, "part")
    step("new_part", title=str(get_com_member(model, "GetTitle")))

    #: ★ 建一条**直的路径**（★ 这样横截面就是那个圆、★ 便于量 bbox）✓
    with P.sketch(model, "Front Plane") as sk_prof:
        P.sketch_circle(model, 0.0, 0.0, 3.0)
    with P.sketch(model, "Top Plane") as sk_path:
        P.sketch_line(model, 0.0, 0.0, 0.0, 40.0)
    step("sketches", profile=str(sk_prof), path=str(sk_path))

    got_prof = P._select_sketch_feature_by_name(model, str(sk_prof), mark=1)
    feat = P._safe_com_member(model, "FeatureByName", str(sk_path))
    for cand in P._get_sketch_name_candidates(str(sk_path)):
        if feat is None:
            feat = P._safe_com_member(model, "FeatureByName", cand)
    ok_path = bool(feat) and bool(P._select_com_object(feat, append=True, mark=4))
    step("select", profile=got_prof, path_ok=ok_path)

    rep = SW.create_sweep_report(model, False)
    step(
        "create_sweep_report",
        ok=rep.get("ok"),
        feature=rep.get("feature_name"),
        type_name=rep.get("type_name"),
    )

    #: ★★ 现在的包围盒（★ 基线：★ 草图轮廓 ⇒ 直径 6 mm 的管、★ 长 40）✓
    model.ViewZoomtofit2() if hasattr(model, "ViewZoomtofit2") else None
    try:
        b0 = P.get_bounding_box(model)
        s0 = sorted(round(float(v), 4) for v in b0["size"])
        step("bbox_before", size=s0)
    except Exception as exc:  # noqa: BLE001
        step("bbox_before_EXC", err=str(exc)[:110])
        s0 = None

    #: ★★★ 设圆轮廓 + 已知直径 ⇒ `ModifyDefinition` ✓
    feat = P._safe_com_member(
        model, "FeatureByName", str(rep.get("feature_name") or "扫描1")
    )
    step("feature_found", ok=bool(feat))
    data = get_com_member(feat, "GetDefinition") if feat is not None else None
    step("definition", type=type(data).__name__ if data is not None else None)
    applied = {"error": None}
    if data is not None:
        try:
            from sw_connect import set_com_member

            set_com_member(data, "CircularProfile", True)
            set_com_member(data, "CircularProfileDiameter", 12.0)
            applied["set"] = {"CircularProfile": True, "CircularProfileDiameter": 12.0}
            #: ★★★★★ 2026-10-04（轮 127）**第 3 参要传**空 Dispatch VARIANT**** ——
            #:   ★ **真机读数**：★ 传 `None` ⇒
            #:     `com_error: (-2147352571, '**类型不匹配。**', None, **3**)` ✓
            #: ★★ **⇒ 位置 3** 正是 `ModifyDefinition(Data, TopDoc, **Component**)` 的第
            #:  3 参 ⇒
            #:     ★★★ **⇒ 那正是**事实 12/33 那一族**：★
            #: **空 Dispatch 参数包要用 `VARIANT(VT_DISPATCH, None)`**（★ 传裸 `None` 会
            #: 报
            #:       「类型不匹配」、★ **而那个错误看不出是哪个参数**）✓
            #: ★★★★ **⇒ 正解就在本仓**（★ `sw_connect.create_empty_dispatch_variant()`）
            #: ✓
            from sw_connect import create_empty_dispatch_variant

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
    step("apply_circular_profile", **applied)

    #: ★★★★ **独立判据：★ 量包围盒** ✓
    try:
        b1 = P.get_bounding_box(model)
        s1 = sorted(round(float(v), 4) for v in b1["size"])
        step("bbox_after", size=s1)
        #: ★ 横截面 = 那两个非长度方向的尺寸（★ 长度方向 ≈40）✓
        cross = [v for v in s1 if abs(v - 40.0) > 5.0]
        ev["★_横截面"] = cross
        if cross and all(abs(v - 12.0) < 1.5 for v in cross):
            ev["★_CircularProfileDiameter_口径"] = (
                "★ **毫米**（★ 写 `12.0` ⇒ 几何横截面 ≈12 mm）✓"
            )
        elif cross and all(v > 1000 for v in cross):
            ev["★_CircularProfileDiameter_口径"] = (
                "★ **米**（★ 写 `12.0` ⇒ 几何横截面 ≈%s mm ⇒ **它把 12.0 当成 12 米**）"
                % round(max(cross))
            )
        else:
            ev["★_CircularProfileDiameter_口径"] = (
                "★ **读数不明确**（★ 横截面 %r）—— ★ 如实标、★ 不猜" % (cross,)
            )
    except Exception as exc:  # noqa: BLE001
        ev["★_CircularProfileDiameter_口径"] = "★ **量不到**：%s" % str(exc)[:90]
    step("VERDICT", verdict=ev["★_CircularProfileDiameter_口径"])

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
