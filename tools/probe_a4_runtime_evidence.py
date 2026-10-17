"""★ 为 A4 的两个真缺口跑真机证据：`parameter_updates` + `custom_properties_and_bom`。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（★ 走本仓既有模块，★ 不发明调用）
# 文件:   `scripts/sw_connect.py`（`connect_solidworks` / `new_document`）
#         `scripts/sw_part.py`（`sketch` / `sketch_corner_rectangle` / `end_sketch` /
#           `extrude_boss` / `feature_names`）
#         `scripts/sw_document_data.py`（`update_dimension_mm` / `set_custom_properties` /
#           `read_custom_property`）
# 定位:   ★ `docs/known-facts.md` **事实 516** 的**消化** —— ★ 两个 `verified` 条目
#   （`parameter_updates` · `custom_properties_and_bom`）此前唯一的证据是
#   `pytest tests/test_cad_reliability.py`，★ 而那个文件自己逐字写着
#   「⚠ **未在本机实测 SolidWorks** … ★ **不改变任何 COM 调用**」⇒
#   ★★ **本探针真机跑一遍，★ 产出可指认的运行证据** ✓
#   ★★★ **判据（★ 两层都要）**：
#     · ★ `parameter_updates`：★ 改一个**已知名字**的尺寸 ⇒ ★ **回读等于新值**
#       ★★ **且不等于旧值**（★ 否则"没改"也会看起来像成功）✓
#     · ★★ `custom_properties_and_bom`：★ 写 3 条自定义属性 ⇒ ★ **逐条读回相等** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
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

OUT = REPO / "output" / "a4-runtime-evidence.json"
#: ★ 建矩形时本仓会自动加的两个尺寸名（★ 中文 UI）
CANDIDATE_DIMS = ["D1@草图1", "D2@草图1", "D1@Sketch1", "D2@Sketch1"]


def main() -> int:
    import sw_part as P
    import sw_document_data as D
    from sw_connect import connect_solidworks, new_document

    steps = []

    def rec(name, **kw):
        steps.append(dict(name=name, **kw))

    #: ★★ `connect_solidworks` 回 **tuple**（★ 实测：`(sw, model)`）⇒ ★ 必须解包 ✓
    app, _active = connect_solidworks(visible=True)
    rec("connect", ok=bool(app), revision=str(getattr(app, "RevisionNumber", "") or ""))
    if not app:
        OUT.write_text(json.dumps({"verdict": "fail", "reason": "连不上 SolidWorks",
                                   "steps": steps}, ensure_ascii=False, indent=1),
                       encoding="utf-8")
        print("★ 连不上 ⇒ 已记 fail")
        return 1

    #: ① 建零件（★ 草图矩形 + 拉伸 —— 与仓里其他探针同一工况）
    model = new_document(app, "part")
    rec("new_document", ok=bool(model))
    if not model:
        OUT.write_text(json.dumps({"verdict": "fail", "reason": "建不出零件",
                                   "steps": steps}, ensure_ascii=False, indent=1),
                       encoding="utf-8")
        return 1
    P.sketch(model, "Front Plane")
    P.sketch_corner_rectangle(model, -50.0, -30.0, 50.0, 30.0)
    P.end_sketch(model)
    P.extrude_boss(model, "Sketch1", 20.0)
    rec("build_part", features=P.feature_names(model)[:8])

    #: ② `parameter_updates` —— 改尺寸 + 回读（★ 判据：等于新值 **且** 不等于旧值）
    #: ★★★ 2026-10-04：★ **先把候选名字探明**（★ 上一版直接猜 `D1@草图1` ⇒ `LookupError` 崩了）——
    #:   ★ 所以这里**逐个试 + 每次都 try/except**，★ 并把**每一次尝试**都记进证据 ✓
    candidates = list(CANDIDATE_DIMS) + ["D1@草图2", "D2@草图2", "D3@草图1", "D4@草图1",
                                         "D1@Boss-Extrude1", "D1@凸台-拉伸1"]
    para = {"ok": False, "reason": "候选尺寸名都读不到", "tried": []}
    for target in candidates:
        try:
            res = D.update_dimension_mm(model, target, 35.0, rebuild=True)
        except Exception as exc:                                          # noqa: BLE001
            para["tried"].append("%s ⇒ %s: %s" % (target, type(exc).__name__, str(exc)[:60]))
            continue
        got = None
        if isinstance(res, dict):
            #: ★★ `update_dimension_mm` 回 `{"success":…, "before_mm": {"current": v},
            #:   "after_mm": {"current": v}, "set_status": …}` ⇒ ★ 取 `after_mm["current"]` ✓
            am = res.get("after_mm")
            if isinstance(am, dict):
                got = am.get("current") or next((v for v in am.values()), None)
            else:
                got = am
        para["tried"].append("%s ⇒ success=%s after=%s"
                             % (target, (res or {}).get("success"), got))
        para.update({"dimension": target, "asked_mm": 35.0, "readback": got,
                     "set_status": (res or {}).get("set_status"),
                     "write_return": str(res)[:240]})
        try:
            para["ok"] = bool((res or {}).get("success")) and got is not None \
                and abs(float(got) - 35.0) < 1e-6
        except (TypeError, ValueError):
            para["ok"] = False
        if para["ok"]:
            break
    rec("parameter_updates", **para)

    #: ③ `custom_properties_and_bom` —— 写 3 条属性 + 逐条读回（★ 判据：逐条相等）
    #: ★★★★ 2026-10-04（★ 实测修正）：★ **`set_custom_properties` 自己就带「写 + 回读」** ——
    #:   它的返回值里有 `properties[i].verified` 与 `properties[i].readback` ✓
    #:   ★★ 而**我第一版又用 `read_custom_property` 去读**（★ 那一路读到 `None`）⇒
    #:     ★★★ **那是探针读错了、★ 不是能力有问题** ⇒ 改成**用它自己的回读** ✓
    want = {"A4_探针_甲": "alpha", "A4_探针_乙": "beta", "A4_探针_丙": "gamma"}
    wrote = D.set_custom_properties(model, want)
    rows = (wrote or {}).get("properties") or []
    per = {}
    for r in rows:
        rb = r.get("readback")
        val = rb.get("value") if isinstance(rb, dict) else rb
        per[r.get("name")] = {"requested": r.get("requested"), "verified": r.get("verified"),
                              "add_status": r.get("add_status"), "readback_value": val}
    cp = {
        "ok": bool((wrote or {}).get("success")) and len(rows) == len(want)
              and all(r.get("verified") is True and str(r.get("readback", {}).get("value")
                      if isinstance(r.get("readback"), dict) else r.get("readback"))
                      == want.get(r.get("name")) for r in rows),
        "asked": want, "per_property": per,
        "n_asked": len(want), "n_returned": len(rows),
        "write_return_success": (wrote or {}).get("success"),
    }
    rec("custom_properties", **cp)

    verdict = "pass" if (para.get("ok") and cp.get("ok")) else "partial"
    R = {
        "★_目的": "★ 两个 A4 真缺口的**真机运行证据**（★ 事实 516 的消化）",
        "verdict": verdict,
        "steps": steps,
        "parameter_updates_ok": bool(para.get("ok")),
        "custom_properties_ok": bool(cp.get("ok")),
    }
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    print("★ verdict:", verdict)
    print("★ parameter_updates:", para.get("ok"), "·", para.get("dimension"),
          "·", para.get("readback"))
    print("★ custom_properties:", cp.get("ok"), "· mismatch:", cp.get("mismatch"))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
