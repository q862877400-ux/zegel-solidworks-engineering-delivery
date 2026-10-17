"""★ 真机：钣金厚度的**单位**到底是不是米？—— 用"厚度棱的长度"直接量。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_spec209_hem_units.py
# 定位:   ★ 承 `tools/probe_spec209_hem_diag.py` 的读数：60×40 的板，**边长的集合是
#   `{0.002, 40.0, 60.0}`** —— ★★ 也就是说**厚度棱只有 0.002**，而 `BaseFlangeSpec` 的 docstring
#   逐字写着「全部长度单位为**米**」（传的是 `thickness=0.002`）⇒ **两种可能**：
#     ```
#     H-A 文档单位就是米 ⇒ 0.002 m = 2 mm ⇒ 厚度棱应读 **0.002**（★ 与现读数一致）—— 而板宽 60 米？荒谬
#     H-B 文档单位是毫米 ⇒ 传 0.002 被当成 **0.002 mm** ⇒ 我们一直在造**箔片**（厚度棱读 0.002 也一致）
#     ```
#   ⇒ ★★ **两条假设给出的厚度读数相同** ⇒ 必须换一个**能分开它们**的判据：
#     **把 `thickness` 改成 `2.0` 再量一次** ——
#     · 若厚度棱读 **2.0**（文档单位=mm）⇒ H-B 成立（★ 而 `BaseFlangeSpec` 的"米"是错的）
#     · 若厚度棱读 **2000**（米）⇒ H-A 成立
#   ★ 判据 = **用端点自己算的厚度棱长度**（★ 不是任何返回值）✓
#   ★★ 另：`IEdge` 上**没有长度成员**（官方成员表逐条列过）⇒ 长度只能由 `GetStartVertex` /
#     `GetEndVertex` → `IVertex::GetPoint()` 自己算 ✓
# 官方依据: `C:\swapi\types\IEdge\{GetStartVertex,GetEndVertex}.md` ·
#   `C:\swapi\types\IVertex\GetPoint.md` · `C:\swapi\types\IFeatureManager\InsertSheetMetalHem2.md`
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
OUT = R / "output" / "spec209-hem-units.json"


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    import sw_part as P
    import sw_sheet_metal as SM
    import sw_selection_spec as SS

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "钣金厚度单位判定（用厚度棱的长度量）+ 正厚度下的 hem/unfold",
          "judge": "厚度棱长度（★ 端点自算，不是返回值）", "unit_probe": [], "hem": {}, "unfold": {}}
    opened = []

    def _close(doc):
        try:
            t = str(safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
        except Exception:                                      # noqa: BLE001
            pass

    def _edges(doc):
        rows = []
        for i, e in enumerate(SS.entities_on_body(doc, "EDGE")):
            try:
                pts = []
                for member in ("GetStartVertex", "GetEndVertex"):
                    v = get_com_member(e, member)
                    p = get_com_member(v, "GetPoint") if v is not None else None
                    pts.append(None if p is None else [float(x) for x in list(p)[:3]])
                ln = None
                if pts[0] and pts[1]:
                    ln = round(sum((pts[1][k] - pts[0][k]) ** 2 for k in range(3)) ** 0.5, 6)
                rows.append({"index": i, "length": ln})
            except Exception as exc:                           # noqa: BLE001
                rows.append({"index": i, "error": str(exc)[:80]})
        return rows

    def _plate(thickness):
        doc = sw_connect.new_document(sw, "part")
        opened.append(doc)
        with P.sketch(doc, "Front Plane") as sk:
            P.sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        SM.create_base_flange(doc, sk, SM.BaseFlangeSpec(thickness=thickness,
                                                         bend_radius=0.001, depth=0.05))
        return doc

    #: ── 单位判定：同一个零件，传两个厚度，**量厚度棱** ─────────────────────────────────────
    for th in (0.002, 2.0):
        try:
            doc = _plate(th)
            rows = _edges(doc)
            lens = sorted({r["length"] for r in rows if r.get("length") is not None})
            ev["unit_probe"].append({"thickness_passed": th, "edge_lengths": lens,
                                     "shortest_edge": (lens[0] if lens else None),
                                     "edge_count": len(rows)})
            print("  厚度传 %-6s ⇒ 边长集合 %r" % (th, lens))
            if th == 2.0:
                globals()["_LAST_DOC"] = doc
            else:
                _close(doc)
        except Exception as exc:                               # noqa: BLE001
            ev["unit_probe"].append({"thickness_passed": th,
                                     "fatal": "%s: %s" % (type(exc).__name__, str(exc)[:160])})
            print("  厚度传 %-6s FATAL %s" % (th, str(exc)[:100]))

    #: ── 判定 ─────────────────────────────────────────────────────────────────────
    verdict = "★ 判不出（两次都没读到边长）"
    try:
        short = [r.get("shortest_edge") for r in ev["unit_probe"]]
        if short[0] is not None and short[1] is not None:
            if abs(short[1] - 2.0) < 0.05 and abs(short[0] - 0.002) < 1e-6:
                verdict = ("★★ **文档长度单位就是毫米** ⇒ `IBaseFlangeFeatureData.Thickness` "
                           "按**文档单位**解释（传 2.0 ⇒ 厚度 2.0）⇒ ★★ `BaseFlangeSpec` docstring 的"
                           "「全部长度单位为米」**是错的**（传 0.002 造出的是 **0.002 mm 的箔片**）")
            elif abs(short[1] - 2000.0) < 50.0:
                verdict = "★ 米（传 2.0 ⇒ 厚度棱 2000）⇒ docstring 的「米」是对的"
            else:
                verdict = "★ 两次读数 %r ⇒ 另查" % (short,)
    except Exception:                                          # noqa: BLE001
        pass
    ev["★_unit_verdict"] = verdict
    print("  ★ 单位判定：%s" % verdict)

    #: ── 在**真厚度**的板上重试 hem（★ 之前那张是 0.002 厚的箔片）──────────────────────────
    doc2 = globals().get("_LAST_DOC")
    if doc2 is not None:
        try:
            SS.select_entity_by_index(doc2, "EDGE", 4)
            r = SM.create_hem(doc2, "index:4", length_m=0.01, gap_m=0.01, radius_m=0.005,
                              miter_gap_m=0.0011)
            ev["hem"] = {"ok": r.get("ok"), "feature": r.get("feature"),
                         "feature_type": r.get("feature_type"),
                         "hem_type_readback": r.get("hem_type_readback"),
                         "tree": [r.get("tree_before"), r.get("tree_after")],
                         "face_count": [r.get("face_count_before"), r.get("face_count_after")],
                         "bbox_changed": r.get("bbox_changed"), "error": r.get("error")}
            print("  HEM(2mm 板) ok=%s feature=%r" % (r.get("ok"), r.get("feature")))
            if r.get("feature"):
                ru = SM.create_unfold(doc2, [r["feature"]], face_index=0)
                ev["unfold"] = {"ok": ru.get("ok"), "bend_used": r["feature"],
                                "selection": ru.get("selection"),
                                "tree": [ru.get("tree_before"), ru.get("tree_after")],
                                "new_features": ru.get("new_features"),
                                "flat_pattern_count": [ru.get("flat_pattern_count_before"),
                                                       ru.get("flat_pattern_count_after")],
                                "error": ru.get("error")}
                print("  UNFOLD ok=%s new=%r" % (ru.get("ok"), ru.get("new_features")))
        except Exception as exc:                               # noqa: BLE001
            ev["hem"] = {"fatal": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
            print("  HEM FATAL %s" % str(exc)[:140])
    else:
        ev["hem"] = {"skipped": "★ 2mm 那张板没建出来"}

    for d in opened:
        _close(d)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
                   encoding="utf-8")
    print("  产物：%s" % OUT)
    try:
        sw.CommandInProgress = False
    except Exception:                                          # noqa: BLE001
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
