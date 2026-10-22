"""★ 真机：★ 建**旋转**特征（★ 已知角度 30°）⇒ 用 `revolve_params` 读回 ⇒ 判度/弧度。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 官方 `C:\\swapi\\types\\IRevolveFeatureData2\\*.md`
# 文件:   tools/probe_revolve_params_recheck.py（★ 只报不动 —— 证据脚本 · 新）
# 定位:   ★ 阶段 5 同族继续：★ `查 × 特征` 官方 **451**、★ 我们 **12** ⇒ ★ **本族做 `r
#           evolve`** ✓
#   **官方依据（★ 逐字）**：
#     · ★ `GetRevolutionAngle(bool Forward)` ⇒ `## Returns: **Angle of revolution**`（★ **无单位**）
#       ⇒ ★★ **而那要看是**度**还是**弧度**** ✓
#     · ★ `GetWallThickness(bool Forward)` ⇒ `## Returns: Wall thickness`、
#       ★ `## Remarks: **This method only affects thin features.**` ✓
#     · ★ `GetAxisType()` ⇒ `swSelectType_e` ⇒「`swSelDATUMAXES` / `swSelEDGES` / `swSelSK…`」✓
#   ★★★ **判据（★ 可核）**：
#     ★ 建一个**30°** 的旋转（★ 本仓 `revolve_boss` 收**度**）⇒
#       · ★ 若 `GetRevolutionAngle` 回 **≈30.0** ⇒ **度** ✓
#       · ★ 若回 **≈0.5236**（= π/6）⇒ **弧度** ✓
#     ★★ **⇒ 两个候选差 57 倍** ⇒ **口径自明** ✓
#     ★★★ **而报告口径时**不能用 `revolve_boss` 的入参去反推** ——
#       那要看**它内部**是不是把它转成了弧度 ⇒ ★ **所以要用**独立**的几何判据**：
#     ★★★★ **⇒ 本探针再量**体积**：★ 半圆盘 30° 的体积**能解析算出来** ✓
#   覆盖:   全文件
# ---------------------------------------------------------------------------

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = ROOT / "output" / "revolve-params-capability-recheck.json"
ANGLE_DEG = 30.0
ev: dict = {
    "★_判据": ("建 **30.0**° 的旋转 ⇒ 读 `GetRevolutionAngle`："
               "★ ≈30.0 ⇒ **度** · ★ ≈0.5236（π/6）⇒ **弧度**"),
    "★_为什么还要量体积": "★ 只读角度是**读回我写的东西** ⇒ ★ 体积是**独立几何** ✓",
    "steps": []}


def step(name: str, **kw) -> None:
    """★ 每步**增量落盘** —— ★ 那样即使超时、★ 也知道卡在**哪一步** ✓

    ★★★★★ 2026-10-04（轮 130）**为什么加这个**（★ 我自己的流程错）：
      ★ 真机跑报 `seconds: **120.43**`（★ 超时）⇒ ★★ **而证据文件**根本没写**** ⇒
      ★★★ **⇒ 我读到的却是"找不到旋转特征"** —— ★ 那是**上一轮**留下的**旧文件** ✗
      ★★★★ **⇒ 判据**：★★★ **读证据文件前要**确认它是这一次写的**** ✓
      ★★ 而"每步落盘"让**超时那一刻的状态**也留下来 ✓
    """
    ev["steps"].append(dict(name=name, **kw))
    try:
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:                                                       # pragma: no cover
        pass
    print("★ %-28s %s" % (name, json.dumps(kw, ensure_ascii=False)[:230]))


def main() -> int:
    from sw_connect import connect_solidworks, get_com_member, new_document
    import sw_feature_readback as R
    import sw_part as P

    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    step("new_part", title=str(get_com_member(model, "GetTitle")))

    #: ★ 轮廓：★ 一个**矩形**（★ 它绕一条中心线转 30° ⇒ 得到一段"扇形环"体）✓
    #:   ★★ 用 `sketch_corner_rectangle` —— ★ 它在本仓**已改成 `get_com_member` 形态**（★ 轮 126）✓
    with P.sketch(model, "Front Plane") as sk:
        P.sketch_corner_rectangle(model, 10.0, 0.0, 20.0, 10.0)
        #: ★ 中心线（★ 旋转轴）—— ★ 沿 Y 轴、★ 在 x=0 ✓
        get_com_member(get_com_member(model, "SketchManager"),
                       "CreateCenterLine", 0.0, -20.0, 0.0, 0.0, 20.0, 0.0)
    step("sketch", sketch_name=str(sk), rect="(10,0)-(20,10)", centerline="x=0")

    #: ★★★★★★★ 2026-10-04（轮 130）**要传**弧度**** —— ★ 我先前传了**度** ✗
    #:   ★ 真机读数（★ 三条独立证据吻合，★ 差 **0.000000°**）：
    #:     ★ 传 `30.0` ⇒ ★ 读回 `GetRevolutionAngle = **4.867259 rad = 278.8734°**` ⇒
    #:     ★★ 而 `30 rad mod 360° = **278.8734°**` · ★ 体积比 `0.774648` = `278.8734/360` ✓
    #:   ★★★ **真因**：★ `revolve_boss(model, sketch_name, **angle_rad**, …)` ——
    #:     ★ **形参名就是 `angle_rad`**、★ docstring 逐字「**弧度**，2*pi 表示 360 度」✓
    #:   ★★★★ **而 ToolSpec 那层**是对的****：★ `Param("angle_deg", …)` +
    #:     ★ `derived_args` 里 `_radians_of_deg(p)` ⇒ **在边界换算一次** ✓
    #:   ★★★★★ **⇒ 三层都对、★ 只有**我**那一层错了**（★ 我**绕过 ToolSpec 直调能力层**）⇒
    #:     ★★ **那正是 AGENTS.md 明写的**：★「跑探针验能力时：**按 `ToolSpec` 的契约调，
    #:       别手调内部实现**」✓
    built = {"error": None, "★_注意": "★ 能力层的契约是**弧度**（★ 形参名 angle_rad）"}
    try:
        built["returned"] = str(P.revolve_boss(model, str(sk), math.radians(ANGLE_DEG)))[:80]
    except Exception as exc:                                              # noqa: BLE001
        built["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    step("revolve_boss", angle_deg=ANGLE_DEG, **built)

    #: ★★★★★★ 2026-10-04（轮 130）**先把真实类型名打出来** —— ★ 不要继续猜 `Revolve` ✓
    #:   ★ 真机读数：★ 特征**建成了**（★ 体积 0 → **7300.888**）、
    #:     ★★ **而 `revolve_params` 报**「找不到旋转特征（类型名含 `Revolve`）」**** ⇒
    #:     ★★★ **⇒ 那是**兜底判据的名字猜错了**** ⇒ **⇒ 打出来看** ✓
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
    except Exception as exc:                                              # noqa: BLE001
        names = [("EXC", str(exc)[:80])]
    step("feature_type_names", all=names)
    ev["★_真实的类型名"] = names

    #: ★★★★★★ 2026-10-04（轮 130）**原样跑一遍兜底循环** —— ★ 别猜、★ 看它看到什么 ✓
    #:   ★ 矛盾：★ 类型名是 `Revolution`、★ 而 `"Revolve" in "Revolution"` 本该是 `True`、
    #:     ★★ **可 `revolve_params` 报**找不到**** ✓
    #:   ★★ **⇒ 先把 `_CONTAINER_NODES` 也打出来**（★ 万一 `旋转1` 在里面？）✓
    try:
        import sw_feature_readback as _R
        step("container_nodes", count=len(_R._CONTAINER_NODES),
             has_my_feature=("旋转1" in _R._CONTAINER_NODES))
    except Exception as exc:                                              # noqa: BLE001
        step("container_nodes_EXC", err=str(exc)[:110])
    trace = []
    try:
        from sw_connect import safe_get_com_member as _sg
        f = _sg(model, "FirstFeature")
        while f is not None:
            try:
                nm = str(_sg(f, "Name") or "")
                tn = str(_sg(f, "GetTypeName2") or "")
                trace.append((nm, tn, ("Revolve" in tn)))
            except Exception as exc:                                      # noqa: BLE001
                trace.append(("EXC", str(exc)[:50], False))
            f = _sg(f, "GetNextFeature")
    except Exception as exc:                                              # noqa: BLE001
        trace.append(("LOOP_EXC", str(exc)[:90], False))
    step("fallback_trace", tail=[x for x in trace if x[1] not in (
        "FavoriteFolder", "HistoryFolder", "SelectionSetFolder", "SensorFolder",
        "DocsFolder", "DetailCabinet", "InkMarkupFolder", "EnvFolder")][-6:])

    got = R.revolve_params(model)
    step("revolve_params", feature=got.get("feature"), definition=got.get("definition"),
         error=got.get("error"), GetAxisType=got.get("GetAxisType"),
         IsBossFeature=got.get("IsBossFeature"), IsThinFeature=got.get("IsThinFeature"),
         GetContoursCount=got.get("GetContoursCount"),
         ReverseDirection=got.get("ReverseDirection"),
         GetRevolutionAngle=got.get("GetRevolutionAngle"))

    ga = got.get("GetRevolutionAngle")
    fwd = ga.get("forward") if isinstance(ga, dict) else None
    if fwd is None:
        ev["★_GetRevolutionAngle_口径"] = "★ **没读到**"
    else:
        #: ★★★ **最近候选分类**（★ 轮 128/129 的教训：容差带不可靠）✓
        #: ★ 本次传的是 **π/6 弧度**（= 30°）⇒ ★ 期望读回 **≈0.5236**（弧度）✓
        #:   ★★ **⇒ 若读回 ≈0.5236 ⇒ 那**只能**是弧度**（★ 若它回度、★ 该是 30.0）✓
        cands = [("★ **度**（★ 若它回 30.0 ⇒ 那是**度**）", 30.0),
                 ("★ **弧度**（★ 若它回 0.5236 ⇒ 那是**弧度**）", math.pi / 6)]
        near = min(cands, key=lambda kv: abs(float(fwd) - kv[1]))
        gap = abs(float(fwd) - near[1])
        others = min(abs(float(fwd) - v) for k, v in cands if k != near[0])
        ev["★_读数"] = fwd
        ev["★_最近候选"] = near[0]
        ev["★_最近距离"] = round(gap, 6)
        ev["★_次近距离"] = round(others, 6)
        if gap < others * 0.5:
            ev["★_GetRevolutionAngle_口径"] = (
                "%s ⇒ ★ 实测 %.6f（★ 最近 %.6f · ★ 次近 %.6f）" % (near[0], float(fwd),
                                                                    near[1], others))
        else:
            ev["★_GetRevolutionAngle_口径"] = (
                "★ **不明确**（★ 实测 %.6f · ★ 最近 %s %.6f · ★ 次近 %.6f）⇒ ★ 如实标"
                % (float(fwd), near[0], near[1], others))
    step("VERDICT", verdict=ev["★_GetRevolutionAngle_口径"])

    #: ★★★★ **独立几何**：★ 量体积 ✓
    try:
        mp = get_com_member(get_com_member(model, "Extension"), "CreateMassProperty")
        vol = float(get_com_member(mp, "Volume"))
        #: ★ 矩形 x∈[10,20] · y∈[0,10] ⇒ 绕 x=0 转 30° 的体积 =
        #:   (30/360)·π·(20²−10²)·10 = (1/12)·π·300·10 ✓
        expect = (ANGLE_DEG / 360.0) * math.pi * (20.0 ** 2 - 10.0 ** 2) * 10.0
        step("volume", mm3=round(vol, 3), expect_deg=round(expect, 3))
        ev["★_体积_实测"] = round(vol, 3)
        ev["★_体积_期望"] = round(expect, 3)
    except Exception as exc:                                              # noqa: BLE001
        step("volume_EXC", err=str(exc)[:110])

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
