"""★ 真机：★ 建一个**扫描**特征 ⇒ 用 `sweep_params` 读回 ⇒ 量两个长度量的口径。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 官方 `C:\\swapi\\types\\ISweepFeatureData\\*.md`
# 文件:   tools/probe_sweep_params_recheck.py（★ 只报不动 —— 证据脚本 · 新）
# 定位:   ★ 阶段 5 同族继续（★ `查 × 特征` ＝ 官方 **451**、★ 我们 **11**）⇒
#   ★★ **本仓有 6 个"能写"的特征工具、★ 却一个读都没有**（★ 「能写不能读」）⇒
#   ★★★ **已做 `shell` / ★ `dome`** ⇒ ★ **本族做 `sweep`** ✓
#   ★★★★ **⚠ 而 `rib` 那一支**已按事实 53 结题****（★ 6 次失败全记档；
#     ★ 而"`InsertRib2` 才是现行入口"那条线索**也断了** —— ★ 官方**没有**那一页）✓
#   **官方依据**（★ 逐条查过 `ISweepFeatureData` 的 53 个成员）：
#     · ★ `CircularProfileDiameter` ⇒ `## Returns: Diameter of the circular profile`（★ **无单位**）
#     · ★ `GetWallThickness(bool Forward)` ⇒ `## Returns: Wall thickness`（★ **无单位**）
#     · ★★ `GetTwistAngle()` ⇒ `## Returns: Angle of twist **in radians**`（★ **写了**）
#     · ★★ `GetD2TwistAngle()` ⇒ 同款逐字 ✓
#   ★★★★★ **判据（★ 可核）**：
#     ★ 用本仓 `sw_sweep.create_sweep_report` 建扫描 ⇒ ★ **建成后读回**：
#       · ★ `SweepType`（★ 只读属性）是不是 `swFmSweep(17)` / `swFmSweepCut(18)` ✓
#       · ★ `IsBossFeature()` / ★ `IsThinFeature()` 的自洽性 ✓
#       · ★ `CircularProfile` / ★ `CircularProfileDiameter`（★ **圆轮廓那条路最干净**）✓
#     ★★ **而口径**：★ 若 `CircularProfile=True` ⇒ ★ 给它一个**已知直径** ⇒
#       ★ 读回 `CircularProfileDiameter` 看是 **毫米** 还是 **米** ✓
#   覆盖:   全文件
# ---------------------------------------------------------------------------

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = ROOT / "output" / "sweep-params-capability-recheck.json"
ev: dict = {
    "★_判据": "建扫描 ⇒ 读回；口径看 `CircularProfileDiameter` / `GetWallThickness` 是毫米还是米",
    "★_注意": ("★ 官方对 `GetTwistAngle`/`GetD2TwistAngle` **写了 radians** ⇒ "
               "★ 那两条不用量；★ **要量的是 `CircularProfileDiameter` 与 `GetWallThickness`**"),
    "steps": []}


def step(name: str, **kw) -> None:
    ev["steps"].append(dict(name=name, **kw))
    print("★ %-28s %s" % (name, json.dumps(kw, ensure_ascii=False)[:220]))


def main() -> int:
    from sw_connect import connect_solidworks, get_com_member, new_document
    import sw_feature_readback as R
    import sw_part as P
    import sw_sweep as SW

    app, _ = connect_solidworks(visible=True)
    step("connect", ok=bool(app))
    model = new_document(app, "part")
    step("new_part", title=str(get_com_member(model, "GetTitle")))

    #: ★ 先建一块板（★ 扫描的实体要先有—— ★ 与 dome 同办）✓
    with P.sketch(model, "Front Plane") as sk_base:
        sm = get_com_member(model, "SketchManager")
        for x1, y1, x2, y2 in ((-30.0, -20.0, 30.0, -20.0), (30.0, -20.0, 30.0, 20.0),
                               (30.0, 20.0, -30.0, 20.0), (-30.0, 20.0, -30.0, -20.0)):
            get_com_member(sm, "CreateLine", x1, y1, 0.0, x2, y2, 0.0)
    r0 = P.extrude_boss(model, sk_base, 10.0)
    step("base_plate", depth_mm=10.0, ok=(r0 is not None))

    #: ★★ 扫描 = 轮廓 + 路径 ⇒ ★ 用本仓 `sw_sweep` 的公开入口 ✓
    #:   ★ **⚠ 先看它要什么**（★ 不猜）—— 下面按它的 `ToolSpec` 契约给（★ 见 `create_sweep_report`）
    #: ★★★★ 2026-10-04（轮 126）**边界只加在 `with` 里面**（★ 外面那次尝试会多建草图）✓
    with P.sketch(model, "Front Plane") as sk_prof:
        #: ★★★★ 2026-10-04（轮 126）**改用本仓能力层** —— ★ 裸调 `CreateCircle` 报
        #:   `com_error(-2147352561, '**非选择性的参数。**')` ✓
        #:   ★★ **⇒ 那与 `CreateCornerRectangle` 那次**同因** ⇒
        #:     ★★★ **⇒ 正解：★ `sw_part.sketch_circle`**（★ 那是 `solidworks_sketch_add_circle`
        #:       挂的那个能力、★ 它的 arity **早就修对了**）✓
        try:
            P.sketch_circle(model, 0.0, 0.0, 6.0)
            step("sketch_circle", ok=True)
        except BaseException as exc:                                      # noqa: BLE001
            step("sketch_circle_EXC", err="%s: %s" % (type(exc).__name__, str(exc)[:130]))
            raise
    step("sketch(profile)", sketch_name=str(sk_prof), radius_mm=6.0,
         via="sw_part.sketch_circle（★ 不裸调 CreateCircle）")
    with P.sketch(model, "Top Plane") as sk_path:
        sm3 = get_com_member(model, "SketchManager")
        get_com_member(sm3, "CreateLine", 0.0, 0.0, 0.0, 0.0, 40.0, 0.0)
    step("sketch(path)", sketch_name=str(sk_path), length_mm=40.0)

    built = {"error": None, "returned": None}
    #: ★★★★★ 2026-10-04（轮 126）**按官方 mark 选**（★ 那是写侧要求的**唯一前置**）✓
    #:   ★ `create_sweep_report(model, cut=False)` **不收轮廓/路径** ⇒
    #:     ★★ **⇒ 它读**当前选区**：★ `轮廓 mark=1` · ★ `路径 mark=4`** ✓
    #:     ★★★ **实现在选择缺时报的那句话逐字**：
    #:       「★ 扫描要选 **轮廓（mark=1）** 与 **路径（mark=4）**（★ 官方专文给的 mark）」✓
    #:   ★★★★ **⚠ 而选择**实体（草图）**在 pywin32 下**不能按名字**（★ 事实 32）⇒
    #:     ★ **要走 `_ensure_sketch_selected` 那条**（★ 本仓既有帮手）✓
    try:
        import sw_part as _P
        #: ★★ 轮廓：★ `_select_sketch_feature_by_name(model, name, **mark=1**)` ✓
        got_prof = _P._select_sketch_feature_by_name(model, str(sk_prof), mark=1)
        step("select(profile)", by_name=got_prof, mark=1)
        #: ★★★ 路径：★ 那个帮手**写死了 `append=False`** ⇒ ★ 会**清掉**刚选的轮廓 ⇒
        #:   ★★ **⇒ 本探针自己走 `_select_com_object(append=True, mark=4)`** ✓
        #:   （★ `FeatureByName` 收的是**草图名**、★ 而它接受中英文候选 —
        #:    ★ 这里直接给实得的名字）✓
        feat = _P._safe_com_member(model, "FeatureByName", str(sk_path))
        if feat is None:
            for cand in _P._get_sketch_name_candidates(str(sk_path)):
                feat = _P._safe_com_member(model, "FeatureByName", cand)
                if feat is not None:
                    break
        ok_path = bool(feat) and bool(_P._select_com_object(feat, append=True, mark=4))
        step("select(path)", by_name=str(sk_path), mark=4, ok=ok_path)
        sel = {}
        for mark, label in ((1, "profile"), (4, "path")):
            sel[label] = int(get_com_member(
                get_com_member(model, "SelectionManager"),
                "GetSelectedObjectCount2", mark))
        step("select_for_sweep", **sel)
    except Exception as exc:                                              # noqa: BLE001
        step("select_for_sweep_EXC", err="%s: %s" % (type(exc).__name__, str(exc)[:110]))
    try:
        built["returned"] = str(SW.create_sweep_report(model, False))[:160]
    except Exception as exc:                                              # noqa: BLE001
        built["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    step("create_sweep_report", **built)

    got = R.sweep_params(model)
    step("sweep_params", feature=got.get("feature"), definition=got.get("definition"),
         error=got.get("error"),
         **{k: got.get(k) for k in ("SweepType", "IsBossFeature", "IsThinFeature",
                                    "ThinFeature", "CircularProfile",
                                    "CircularProfileDiameter", "GetWallThickness",
                                    "GetTwistAngle", "GetPathType", "GetProfileType",
                                    "GetGuideCurvesCount") if k in got})

    d = got.get("CircularProfileDiameter")
    if d is None or isinstance(d, str):
        ev["★_CircularProfileDiameter_口径"] = "★ **没读到**（★ 值 %r）" % (d,)
    else:
        ev["★_CircularProfileDiameter_口径"] = (
            "★ **读到 %.6g** ⇒ ★ 由它反推口径（★ 本探针的圆半径是 6 mm ⇒ 直径 12 mm）" % float(d))
    step("VERDICT_diameter", value=d, verdict=ev["★_CircularProfileDiameter_口径"])

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
