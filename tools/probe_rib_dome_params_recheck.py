"""★ 真机：★ 建**筋**与**圆顶**，★ 再用 `rib_params` / `dome_params` 读回 ⇒ ★ 量三个量。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tools/probe_rib_dome_params_recheck.py（★ 只报不动 —— 证据脚本）
# 定位:   ★ 阶段 5 同族继续：★ `rib_params`（★ 第九族）· ★ `dome_params`（★ 第十族）✓
#   **官方依据**（★ 逐条查过 `C:\\swapi\\types\\`）：
#     · `IRibFeatureData2::Thickness` ⇒ `## Returns: Thickness of the rib`（★ **无单位**）
#     · `IRibFeatureData2::DraftAngle` ⇒ `## Returns: Angle for the draft`（★ **没写度/弧度**）
#     · `IDomeFeatureData2::Height` ⇒ `## Returns: Height of the dome`（★ **无单位**）
#     · `IDomeFeatureData2::ReverseDir` ⇒ `## Returns: True for concave domes,
#       false for convex domes` ✓
#   ★★★★★ **判据（★ 可核）**：
#     · ★ 筋厚 **3 mm** ⇒ ★ 读回 `Thickness` 是 **3.0** 还是 **0.003** ⇒ **口径自明**
#     · ★ 圆顶高 **5 mm** ⇒ ★ 读回 `Height` 是 **5.0** 还是 **0.005** ⇒ **口径自明**
#     · ★ `DraftAngle` ⇒ ★ 与**已知的弧度先例**（`GetDraftAngle`）比 ⇒ **度还是弧度自明**
#   覆盖:   全文件
# ---------------------------------------------------------------------------

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = ROOT / "output" / "rib-dome-params-capability-recheck.json"
ev: dict = {
    "★_判据": ("筋厚 3 mm / 圆顶高 5 mm ⇒ 看读回是 3.0/5.0（毫米）还是 0.003/0.005（米）；"
               "DraftAngle 与 `GetDraftAngle` 的 radians 先例比"),
    "steps": []}


def step(name: str, **kw) -> None:
    ev["steps"].append(dict(name=name, **kw))
    print("★ %-26s %s" % (name, json.dumps(kw, ensure_ascii=False)[:220]))


def _verdict(v, mm, label):
    if v is None:
        return "★ **没读到**（★ %s）" % label
    try:
        f = float(v)
    except Exception:                                                     # noqa: BLE001
        return "★ **非数值**：%r" % (v,)
    if abs(f - mm) < 1e-9:
        return "★ **随文档单位**（★ 毫米文档 ⇒ %.6g）" % f
    if abs(f - mm / 1000.0) < 1e-12:
        return "★ **米**（★ %.6g mm ⇒ %.6g）" % (mm, f)
    return "★ **都不是**（★ 值 %.6g、★ 期望 %.6g 或 %.6g）" % (f, mm, mm / 1000.0)


def main() -> int:
    from sw_connect import connect_solidworks, get_com_member, new_document
    import sw_feature_readback as R
    from sw_part import insert_dome_report, rib_report, sketch

    app, _ = connect_solidworks(visible=True)
    step("connect", ok=bool(app))

    # ── ★ 筋 ───────────────────────────────────────────────────────────
    #: ★★★★★★ 2026-10-04（轮 123）**必须先在**实体上**画轮廓** ⇒
    #:   ★ 我第一版画了一条**悬空**的线 ⇒ ★★ `rib_report ok=false · created=null ·
    #:     **error=""**` ✓（★ **静默失败** —— 那条能力自己的 docstring 写着
    #:     「真机表现是 **"不抛异常、也不建出特征"的静默失败**」）⇒
    #:   ★★★ **⇒ 修法：★ 先拉伸一块板、★ 再在**板的面上**画筋轮廓** ✓
    model = new_document(app, "part")
    step("new_part(rib)", title=str(get_com_member(model, "GetTitle")))
    with sketch(model, "Front Plane") as sk_base:
        sm0 = get_com_member(model, "SketchManager")
        for x1, y1, x2, y2 in ((-30.0, -20.0, 30.0, -20.0), (30.0, -20.0, 30.0, 20.0),
                               (30.0, 20.0, -30.0, 20.0), (-30.0, 20.0, -30.0, -20.0)):
            get_com_member(sm0, "CreateLine", x1, y1, 0.0, x2, y2, 0.0)
    from sw_part import extrude_boss
    r0 = extrude_boss(model, sk_base, 10.0)
    step("base_plate", depth_mm=10.0, ok=(r0 is not None))
    #: ★★ 筋的轮廓画在**前视面**上、★ 而那条线**落在板内**（★ 从 (-30,-20) 到 (30,-20)
    #:   ★ 是板的一条边 ⇒ 改用一条**穿过板内部**的线）✓
    with sketch(model, "Front Plane") as sk_rib:
        sm = get_com_member(model, "SketchManager")
        get_com_member(sm, "CreateLine", -20.0, -10.0, 0.0, 20.0, -10.0, 0.0)
    step("sketch(rib)", sketch_name=str(sk_rib), method="CreateLine ×1（在板内）")
    rep = rib_report(model, sk_rib, 3.0)
    step("rib_report", ok=rep.get("ok"), created=rep.get("created_object"),
         error=(rep.get("error") or "")[:90])
    got = R.rib_params(model)
    step("rib_params", **{k: v for k, v in got.items()
                          if not k.startswith("★_") or k == "★_单位口径"})
    ev["★_Thickness_口径"] = _verdict(got.get("Thickness"), 3.0, "筋厚 3 mm")
    step("VERDICT_Thickness", value=got.get("Thickness"), verdict=ev["★_Thickness_口径"])
    da = got.get("DraftAngle")
    ev["★_DraftAngle_口径"] = (
        "★ 未启用拔模（★ 值 %r）⇒ **本探针量不到**" % (da,)
        if da in (0.0, 0, None) else "★ 读数 %.6g ⇒ 需与 radians 先例比" % float(da))
    step("VERDICT_DraftAngle", value=da, verdict=ev["★_DraftAngle_口径"])

    # ── ★ 圆顶 ─────────────────────────────────────────────────────────
    #: ★★★★★★ 同上：★ `insert_dome` 的 docstring 逐字「⚠ **调用前必须先选好一个面**」⇒
    #:   ★ 我第一版**没选面** ⇒ `ok=false · error=""`（★ 又是静默失败）⇒
    #:   ★★ **⇒ 修法：★ 先建板、★ 再按**面上的点**选中顶面、★ 然后加圆顶** ✓
    model2 = new_document(app, "part")
    step("new_part(dome)", title=str(get_com_member(model2, "GetTitle")))
    with sketch(model2, "Front Plane") as sk_d:
        sm2 = get_com_member(model2, "SketchManager")
        for x1, y1, x2, y2 in ((-20.0, -20.0, 20.0, -20.0), (20.0, -20.0, 20.0, 20.0),
                               (20.0, 20.0, -20.0, 20.0), (-20.0, 20.0, -20.0, -20.0)):
            get_com_member(sm2, "CreateLine", x1, y1, 0.0, x2, y2, 0.0)
    r1 = extrude_boss(model2, sk_d, 10.0)
    step("base_plate(dome)", depth_mm=10.0, ok=(r1 is not None))
    #: ★★★★★★★ 2026-10-04（轮 123）**选面的调用序抄本仓现成的探针** ✓
    #:   ★ 我第一版写了 `C_select_by_point(...)` ⇒ ★★ **那个函数不存在** ✓
    #:   ★★ **⇒ 搜出来**（★ 本会话的纪律：★ 搜一行 grep 的成本 < 猜错的成本）：
    #:     ★ `tools/verify_dome_smoke.py` **L120-136 就是圆顶的现成前置** ⇒
    #:     ★★★ **官方 `IModelDoc2.InsertDome` 的 Remarks 逐字**：
    #:       「Before using this method, you must select the face for the dome
    #:         using a **selection mark of 1**.」✓
    #:     ★★★★ **而那个序是**三步****（★ 少一步就报**看不出真因**的错）：
    #:       ① ★ `SelectByID2("", "FACE", x, y, z, True, **0**, callout, 0)`（★ 先 mark=0）
    #:       ② ★ `ClearSelection2(True)`（★ 清选）
    #:       ③ ★ `SelectByID2("", "FACE", x, y, z, False, **1**, callout, 0)`（★ 再 mark=1）✓
    #:     ★★★★★ **⚠ 而那条纪律又一次被验证**：★★★ **"官方示例给的是**调用序**"** ——
    #:       签名与 Remarks 都给不出这个三步序 ✓
    #:     ★★ **⚠ 事实 33**：★ `Callout` **必须**传 `VARIANT(VT_DISPATCH, None)`
    #:       （★ `sw_part._empty_callout()`）；★ 传 `None` 得到 `类型不匹配`、
    #:       ★★ 而**那个错误看不出是 Callout 的问题** ✓
    import sw_part as _P
    callout = _P._empty_callout()
    ext2 = get_com_member(model2, "Extension")
    sel = False
    try:
        get_com_member(ext2, "SelectByID2", "", "FACE", 0.0, 0.0, 10.0, True, 0, callout, 0)
        get_com_member(model2, "ClearSelection2", True)
        sel = bool(get_com_member(ext2, "SelectByID2",
                                  "", "FACE", 0.0, 0.0, 10.0, False, 1, callout, 0))
    except Exception as exc:                                              # noqa: BLE001
        step("select_top_face_EXC", err="%s: %s" % (type(exc).__name__, str(exc)[:90]))
    step("select_top_face", ok=sel, point="(0, 0, 10)", mark=1)
    rep2 = insert_dome_report(model2, 5.0)
    step("insert_dome_report", ok=rep2.get("ok"), created=rep2.get("created_object"),
         error=(rep2.get("error") or "")[:90])
    got2 = R.dome_params(model2)
    step("dome_params", **{k: v for k, v in got2.items()
                           if not k.startswith("★_") or k == "★_单位口径"})
    ev["★_Height_口径"] = _verdict(got2.get("Height"), 5.0, "圆顶高 5 mm")
    step("VERDICT_Height", value=got2.get("Height"), verdict=ev["★_Height_口径"])

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
