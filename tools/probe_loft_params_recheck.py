"""★ 真机：★ 建一个**放样**（★ 两个轮廓）⇒ 用 `loft_params` 读回 ⇒ 量那几个量的口径。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 官方 `C:\\swapi\\types\\ILoftFeatureData\\*.md`
# 文件:   tools/probe_loft_params_recheck.py（★ 只报不动 —— 证据脚本 · 新）
# 定位:   ★ 阶段 5 同族第 5 个：★ `查 × 特征` 官方 **451**、★ 我们 **13** ⇒ ★ **本族做
#            `loft`** ✓
#   **官方依据（★ 逐字）**：★ `StartConstraintDraftAngle`/`EndConstraintDraftAngle`
#     ⇒「Draft angle」· ★ `StartTangentLength`/`EndTangentLength` ⇒「(Start/End) tangent length」·
#     ★ `GetWallThickness` ⇒「Wall thickness」· ★ `NumberOfSections` ⇒「Number of sections」
#     （★ **而类型是 `double`**）✓
#   ★★★ **⚠ 本探针只求"能建成 + 能读回"** —— ★ 那些量的口径**要另设几何才能定案** ⇒
#     ★ **不谎称量到了**（★ 如实标 `unknown`）✓
#   ★★★★ **写侧契约（★ 从 ToolSpec 读的、★ 不手调内部实现）**：
#     ★ `create_loft_report(model, **closed=False**, **use_selected_profiles=True**)` ·
#     ★★ **ToolSpec**：★ `params=['**profile_sketches**', 'closed', 'use_selected_profiles']` ⇒
#       ★ **由 `pre_call` 把轮廓解析成选区**（★ 官方 mark：★ **轮廓 mark=1**）✓
#     ★★★ **⇒ 所以本探针要**先按 mark=1 选好那些轮廓**** ✓
#     ★★★★ **⚠ 选定后**要 `ClearSelection2` 或另选** —— ★ 免得两个草图叠在一起 ✓
#   覆盖:   全文件
# ---------------------------------------------------------------------------

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = ROOT / "output" / "loft-params-capability-recheck.json"
ev: dict = {
    "★_判据": "建放样（★ 两个轮廓）⇒ `loft_params` 能读回；★ 那几个量的**口径**本轮不裁",
    "★_为何不裁口径": ("★ 官方没写单位的那几个（拔模角 / 相切长度 / 壁厚）**都带前置**"
                       "（★ 拔模角要开起/止约束）⇒ ★ **本轮只证「能建成 + 能读回」**、"
                       "★ **不谎称量到了** ✓"),
    "steps": []}


def step(name: str, **kw) -> None:
    """★ 每步**增量落盘**（★ 超时也知道卡在哪一步 —— ★ 轮 130 的教训）。"""
    ev["steps"].append(dict(name=name, **kw))
    try:
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:                                                       # pragma: no cover
        pass
    print("★ %-28s %s" % (name, json.dumps(kw, ensure_ascii=False)[:230]))


def main() -> int:
    from sw_connect import connect_solidworks, get_com_member, new_document
    import sw_feature_readback as R
    import sw_loft as L
    import sw_part as P

    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    step("new_part", title=str(get_com_member(model, "GetTitle")))

    #: ★ 两个轮廓：★ 前视面一个小方、★ 一个偏移面上一个大方（★ 放样要**两个不同平面**）✓
    with P.sketch(model, "Front Plane") as sk1:
        P.sketch_corner_rectangle(model, -10.0, -10.0, 10.0, 10.0)
    step("sketch1", sketch_name=str(sk1), rect="-10,-10 .. 10,10")

    plane_ok = None
    try:
        #: ★ 建一个**偏移基准面** —— ★ 用本仓既有能力（★ 不手拼 COM）✓
        #: ★★★ 用**对的模块** —— ★ 它们**不在** `sw_part`：
        #:   ★ `insert_ref_plane` 在 **`sw_ref_geometry`** · ★ 面选择在 **`sw_simulation`** ✓
        #:   ★★ **⇒ 本仓那条**「在仓里搜要搜够」** —— ★ 先问 `rc.all_specs()` 挂在哪** ✓
        import sw_ref_geometry as _RG
        import sw_simulation as _SIM
        _SIM.select_face_by_selector_report(model, selection="+z")
        plane_ok = _RG.insert_ref_plane(model, 4, 40.0)
        step("ref_plane", ok=plane_ok)
    except Exception as exc:                                              # noqa: BLE001
        step("ref_plane_EXC", err="%s: %s" % (type(exc).__name__, str(exc)[:130]))

    #: ★★ 第二个轮廓：★ 取"最后一个基准面"（★ 名字随语言变 ⇒ 用特征树找）✓
    names = []
    try:
        f = get_com_member(model, "FirstFeature")
        while f is not None:
            try:
                names.append((str(get_com_member(f, "Name") or ""),
                              str(get_com_member(f, "GetTypeName2") or "")))
            except Exception:                                             # noqa: BLE001
                pass
            f = get_com_member(f, "GetNextFeature")
    except Exception:                                                     # noqa: BLE001
        pass
    planes = [nm for nm, tn in names if tn == "RefPlane" and nm not in
              ("前视基准面", "上视基准面", "右视基准面", "Front Plane", "Top Plane", "Right Plane")]
    step("found_planes", planes=planes)
    target = planes[-1] if planes else "Front Plane"
    with P.sketch(model, target) as sk2:
        P.sketch_corner_rectangle(model, -20.0, -20.0, 20.0, 20.0)
    step("sketch2", sketch_name=str(sk2), on=target, rect="-20,-20 .. 20,20")

    #: ★★★ **按 mark=1 选两个轮廓**（★ 官方给的 mark）✓
    try:
        import sw_part as _P3
        a = _P3._select_sketch_feature_by_name(model, str(sk1), mark=1)
        f2 = _P3._safe_com_member(model, "FeatureByName", str(sk2))
        for cand in _P3._get_sketch_name_candidates(str(sk2)):
            if f2 is None:
                f2 = _P3._safe_com_member(model, "FeatureByName", cand)
        b = bool(f2) and bool(_P3._select_com_object(f2, append=True, mark=1))
        cnt = int(get_com_member(get_com_member(model, "SelectionManager"),
                                 "GetSelectedObjectCount2", 1))
        step("select_profiles", first=a, second=b, mark1_count=cnt)
    except Exception as exc:                                              # noqa: BLE001
        step("select_profiles_EXC", err="%s: %s" % (type(exc).__name__, str(exc)[:130]))

    built = {"error": None}
    try:
        built["returned"] = str(L.create_loft_report(model, False, True))[:180]
    except Exception as exc:                                              # noqa: BLE001
        built["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    step("create_loft_report", **built)

    #: ★ 打出真实类型名（★ 轮 130 的教训：★ 先看真名、★ 不要猜）✓
    try:
        tn = []
        f = get_com_member(model, "FirstFeature")
        while f is not None:
            try:
                tn.append(str(get_com_member(f, "GetTypeName2") or ""))
            except Exception:                                             # noqa: BLE001
                pass
            f = get_com_member(f, "GetNextFeature")
        step("type_names", distinct=sorted(set(tn)))
    except Exception as exc:                                              # noqa: BLE001
        step("type_names_EXC", err=str(exc)[:110])

    got = R.loft_params(model)
    step("loft_params", feature=got.get("feature"), definition=got.get("definition"),
         error=got.get("error"),
         **{k: got.get(k) for k in
            ("GetProfileCount", "GetGuideCurvesCount", "IsBossFeature", "IsThinFeature",
             "NumberOfSections", "Close", "StartTangencyType", "EndTangencyType",
             "StartConstraintDraftAngle", "StartTangentLength") if k in got})

    ev["★_结论"] = ("★ **建成并读回**" if got.get("feature") else "★ **没读到** ⇒ ★ 如实标")
    step("VERDICT", verdict=ev["★_结论"])

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
