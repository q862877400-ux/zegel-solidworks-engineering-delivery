"""★ 真机：规格 209 · B3-1（idx 115 edges + idx 145 faces 合并）—— ★ 判据 = 计数 + 欧拉公式。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_spec209_b3_entities.py
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B3-1**：外部项目 idx **115 `edges`** +
# idx **145 `faces`**（★ 裁决书强制**合并成一条工具**、**扩**已有 `solidworks_entities_o
# n_body`）。
# ★★ 裁决书点名的**真风险**是「**读属性读不到**」（事实 3x：`IModelDoc2.ActiveView.Name/
# Type`
#     报 `unknown.X`）⇒ ★ **先单独做一条小验证**再落 ⇒ 本探针就是那条验证 ✓
#   ★★ 判据（规则 6，全回读）：
#     ```
#     ① 计数         ★ 20×20×10 盒子应回 FACE=6 · EDGE=12 · VERTEX=8（★ 与几何相符）
#     ② 欧拉公式     ★ V − E + F == 2（★ **不需要任何新 API** —— 它是本仓既有的判据）
#     ③ 逐条几何     ★ EDGE 的两个端点 + 自己算的边长（★ 官方 IEdge **没有**长度成员）
#                       FACE 的 `GetArea()` · VERTEX 的 `GetPoint()`
#     ④ 负例         ★ 越界序号 / 非法 kind ⇒ 必须**大声报**（不静默回空）
#     ```
# 官方依据: `C:\\swapi\\types\\IBody2\\{GetEdges,GetFaces,GetVertices}.md` ·
# `IEdge\\{GetStartVertex,GetEndVertex}.md` · `IVertex\\GetPoint.md` · `IFace2\\GetArea.
# md` ·
#   ★★ **`IEdge` 的成员表里没有 Length**（★ 这是"名字缺席 = 官方没有"的现场）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R / "scripts"))
OUT = R / "output" / "spec209-b3-entities.json"


def main() -> int:
    import sw_connect
    import sw_part as p
    import sw_selection_spec as ss
    from sw_connect import get_com_member, safe_get_com_member

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "规格 209 · B3-1（idx 115 edges + 145 faces）—— 判据 = 计数 + 欧拉公式 + 逐条几何",
        "judge": "回读：三类计数 · V−E+F==2 · 每条的几何字段 · 负例必须大声报",
        "reports": {},
        "negative": {},
        "verdict": {},
    }
    opened = []

    def _close(doc):
        try:
            t = str(safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass

    try:
        doc = sw_connect.new_document(sw, "part")
        opened.append(doc)
        with p.sketch(doc, "Front Plane"):
            p.sketch_corner_rectangle(doc, -10.0, -10.0, 10.0, 10.0)
        p.end_sketch(doc)
        p.extrude_boss(doc, "草图1", 10.0)
        #: ★ 先确认体上一个面都没有的极端情况（★ 只作前置读数，不当判据）
        ev["body_count"] = len(list(get_com_member(doc, "GetBodies2", 0, False) or []))
        for kind in ("FACE", "EDGE", "VERTEX"):
            r = ss.entities_report(doc, kind)
            ev["reports"][kind] = {
                "ok": r.get("ok"),
                "count": r.get("count"),
                "euler": r.get("euler"),
                "error": r.get("error"),
                "sample": (r.get("entities") or [None])[0],
                "all_have_error": sorted(
                    {bool(x.get("error")) for x in (r.get("entities") or [])}
                ),
            }
            print(
                "  %-7s count=%-3s euler=%s"
                % (kind, r.get("count"), json.dumps(r.get("euler"), ensure_ascii=False))
            )
        #: ③ 边长与面积要**非空**才有说服力（★ 只报计数是不够的）
        edges = ev["reports"]["EDGE"].get("sample") or {}
        faces = ev["reports"]["FACE"].get("sample") or {}
        ev["verdict"] = {
            "counts_match_box": (
                ev["reports"]["FACE"].get("count") == 6
                and ev["reports"]["EDGE"].get("count") == 12
                and ev["reports"]["VERTEX"].get("count") == 8
            ),
            "euler_holds": ev["reports"]["FACE"].get("euler", {}).get("holds"),
            "edge_geometry_readable": edges.get("length_mm") is not None,
            "face_area_readable": faces.get("area_mm2") is not None,
        }
        ev["verdict"]["all_ok"] = all(v is True for v in ev["verdict"].values())
        print("  verdict =", json.dumps(ev["verdict"], ensure_ascii=False))

        #: ④ 负例：越界序号 / 非法 kind ⇒ **必须大声报**（★ 注意：`entity_geometry` 是**
        #: 报告函数**，
        #: ★ 它**回字典不抛** ⇒ 判据是 `error` 非空，**不是"有没有抛"**（★ 我在 B2 批已
        #: 栽过同一形态）✓
        bad_g = ss.entity_geometry(doc, "EDGE", 99)
        ev["negative"]["bad_index"] = {
            "error": bad_g.get("error"),
            "judged_ok": bool(bad_g.get("error")) and "越界" in str(bad_g.get("error")),
            "_": "★ 报告函数回字典 ⇒ 判据看 error 字段（不抛）",
        }
        bad = ss.entities_report(doc, "SPHERE")
        ev["negative"]["bad_kind"] = {
            "ok": bad.get("ok"),
            "error": bad.get("error"),
            "judged_ok": (bad.get("ok") is False and bool(bad.get("error"))),
        }
        print("  负例 bad_index error=%s" % str(bad_g.get("error"))[:80])
        print(
            "  负例 bad_kind  ok=%s error=%s"
            % (bad.get("ok"), str(bad.get("error"))[:60])
        )
        _close(doc)
    except Exception as exc:  # noqa: BLE001
        ev["fatal"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        print("  FATAL %s" % str(exc)[:140])

    for d in opened:
        _close(d)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  产物：%s" % OUT)
    try:
        sw.CommandInProgress = False
    except Exception:  # noqa: BLE001
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
