"""★ 真机：逐条边算中点、用 `SelectByID2(..., mark=1)` 试选方向 —— ★ 又是穷举表。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_pattern_direction_marks2.py
# 定位:   ★ 2026-10-03（轮 406）承 `probe_pattern_direction_marks.py`：
#   ★★ 那一版已证实 **mark 机制对特征有效**（`SelectByID2(名, "BODYFEATURE", …, mark=4)` 回 True），
#      ★ 而**方向边没选上**（`SelectByID2("", "EDGE", 0, -0.015, 0, …, mark=1)` 回 False）——
#      ★ 真因是我给的坐标**没落在边上**（★ 正是**事实 32** 警告的：实体没有名字 ⇒ 要按点选）。
#   ⇒ ★ 本版照**事实 53 的处方**：★ **把猜测变成一张穷举表** ——
#      ★ 从 `entities_on_body` 取每条边，★ 用 `IEdge.GetStartVertex/GetEndVertex` →
#      `IVertex.GetPoint` 算**中点**，★ 逐条试 `SelectByID2(…, mark=1)`，★ 直到选上。
# 官方依据: `IFeatureManager.FeatureLinearPattern3` 的 Remarks（**1/2 标方向 · 4 标要阵
#           列的特征**）·
#   `IModelDocExtension.SelectByID2`（**9 参**，第 7 个是 `Mark`）·
#   `IEdge.GetStartVertex/GetEndVertex` + `IVertex.GetPoint`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ **特征树真的长了**（★ 规则 6）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "pattern-direction-marks2-evidence.json")


def _midpoint(edge) -> list:
    """★ 一条边的**中点**（★ 用官方 `GetStartVertex` / `GetEndVertex` → `GetPoint`，单位**米**）。"""
    from sw_connect import safe_get_com_member
    a = safe_get_com_member(edge, "GetStartVertex")
    b = safe_get_com_member(edge, "GetEndVertex")
    if a is None or b is None:
        raise RuntimeError("这条边取不到端点")
    pa = safe_get_com_member(a, "GetPoint")
    pb = safe_get_com_member(b, "GetPoint")
    if not pa or not pb:
        raise RuntimeError("端点取不到坐标")
    return [(float(pa[i]) + float(pb[i])) / 2.0 for i in range(3)]


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member
    from sw_feature_readback import feature_names
    from sw_part import (current_sketch_name, end_sketch, extrude_boss, linear_pattern_report,
                         sketch_corner_rectangle, start_sketch)
    from sw_selection_spec import entities_on_body

    ev: dict = {"edge_trials": [], "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -20.0, -15.0, 20.0, 15.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 20.0)
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, 15.0, -2.0, 19.0, 2.0)
        sk2 = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk2, 20.0)
        boss = None
        for nm in ("凸台-拉伸2", "Boss-Extrude2"):
            if sw_connect.safe_get_com_member(doc, "FeatureByName", nm) is not None:
                boss = nm
                break
        ev["setup"] = {"boss": boss, "tree": len(feature_names(doc))}

        ext = get_com_member(doc, "Extension")
        empty = sw_connect.create_empty_dispatch_variant()
        edges = entities_on_body(doc, "EDGE")

        def sel(name, kind, x, y, z, mark):
            return get_com_member(ext, "SelectByID2", str(name), str(kind),
                                  float(x), float(y), float(z), False,
                                  int(mark), empty, 0)

        chosen = None
        for i, e in enumerate(edges):
            try:
                mp = _midpoint(e)
            except Exception as exc:                           # noqa: BLE001
                ev["edge_trials"].append({"edge": i, "mid": None, "err": str(exc)[:60]})
                continue
            try:
                sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
                ok = bool(sel("", "EDGE", mp[0], mp[1], mp[2], 1))
            except Exception as exc:                           # noqa: BLE001
                ev["edge_trials"].append({"edge": i, "mid": mp, "selected": False,
                                          "err": str(exc)[:60]})
                continue
            ev["edge_trials"].append({"edge": i, "mid": [round(v, 4) for v in mp],
                                      "selected": ok})
            if ok and chosen is None:
                chosen = i
                break                                          #: ★ 选上一条就够了
        ev["chosen_edge"] = chosen

        if chosen is not None:
            #: ★ 保留方向选区（mark=1），再加上要阵列的特征（mark=4）
            try:
                sel(boss or "凸台-拉伸2", "BODYFEATURE", 0.0, 0.0, 0.0, 4)
            except Exception as exc:                           # noqa: BLE001
                ev["feature_select_err"] = str(exc)[:100]
            try:
                r = linear_pattern_report(doc, boss or "凸台-拉伸2", 10.0, 3)
                ev["linear_pattern"] = {"ok": bool(r.get("ok")),
                                        "tree": [r.get("tree_before"), r.get("tree_after")],
                                        "new_features": r.get("new_features"),
                                        "error": r.get("error")}
            except Exception as exc:                           # noqa: BLE001
                ev["linear_pattern"] = {"ok": False,
                                        "err": "%s: %s" % (type(exc).__name__, str(exc)[:120])}
        ev["verdict"] = "pass" if (ev.get("linear_pattern") or {}).get("ok") else "partial"
        ev["note"] = ("★ 穷举每条边的中点去试 `SelectByID2(…, mark=1)`（事实 32：实体没有名字 ⇒ 按点选）。"
                      "★ 判据是**特征树真的长了**。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1500])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        if doc is not None:
            t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
