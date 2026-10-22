"""★ 真机：**平面区域**造「真正的带孔曲面」+ 在其上试**删除孔**（★ 事实 442 留的下一步）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_planar_region_then_delete_hole.py
# 定位:   ★ 2026-10-03（轮 564）★ 执行**事实 442 留的下一步**：
#
#   > ★ 下一步：用**平面区域**（`InsertPlanarRefSurface`）从**带内环的草图**
#   >   生成**一张真正的平面曲面** —— ★ 那才是名符其实的"带孔曲面"。
#
#   ★★★★★ **官方逐字**（`C:\swapi\types\IModelDoc2\InsertPlanarRefSurface.md`）：
#     ```
# System.bool InsertPlanarRefSurface()          \u2190 \u2605 **0 \u53c2** \u00b7 \u2605
#  **\u56de bool**
#     Returns : True if the reference surface is created, false if not
#     Remarks : Before calling this method, select the surface's boundary entities
#               using IModelDocExtension::SelectByID2 with **Marks of 1**
#     ```
#     ⇒ ★★ **故前置 = 用 **mark = 1** 选边界实体（草图 / 边）** ✓
#
#   ★ 本探针两步：
#     ⓐ ★ **平面区域**：带内环（矩形 + 圆）的草图 ⇒ 选它 mark=1 ⇒ `InsertPlanarRefSurface()`
#        ⇒ ★ 应得**一张带孔的平面曲面**（★ 1 面 / 2 环 —— ★ 而不是上轮的 5 面 / 6 环）
#     ⓑ ★ **删除孔**：在 ⓐ 得到的面上选**孔的边** ⇒ `InsertDeleteHoleForSurface()`
#   ⚠ 全程走 `tools/sw_guard.py`。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402
import scripts.sw_feature_readback as FR                              # noqa: E402


def _mk_sketch_with_hole(doc, pick_sketch):
    """★ 带内环（孔）的草图 ⇒ ★ 用**平面区域**变成一张**真正的平面曲面**。"""
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name="Front Plane")
    sm = C.get_com_member(doc, "SketchManager")
    C.get_com_member(sm, "CreateCornerRectangle", -0.03, -0.03, 0.0, 0.03, 0.03, 0.0)
    C.get_com_member(sm, "CreateCircleByRadius", 0.0, 0.0, 0.0, 0.012)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    sk = names[-1] if names else "\u8349\u56fe1"
    if not pick_sketch:
        try:
            doc.ClearSelection2(True)
        except Exception:                                                 # noqa: BLE001
            pass
        return sk
    ext = C.get_com_member(doc, "Extension")
    ok = False
    for cand in P._get_sketch_name_candidates(sk):
        try:
            if P._select_by_id(ext, cand, "SKETCH", append=False, mark=1):
                ok = True
                break
        except Exception:                                                 # noqa: BLE001
            continue
    return sk if ok else None


def _geom(doc):
    from sw_connect import get_com_member as _g
    faces = loops = edges = 0
    per_loop = []
    for b in list(_g(doc, "GetBodies2", 1, True) or []):
        for f in list(_g(b, "GetFaces") or []):
            faces += 1
            for lp in list(_g(f, "GetLoops") or []):
                loops += 1
                try:
                    ne = len(list(_g(lp, "GetEdges") or []))
                except Exception:                                         # noqa: BLE001
                    ne = -1
                per_loop.append({"face": faces - 1, "edges": ne})
        try:
            edges += len(list(_g(b, "GetEdges") or []))
        except Exception:                                                 # noqa: BLE001
            pass
    return {"faces": faces, "loops": loops, "edges": edges, "per_loop": per_loop}


def _one(sw, tag, then_delete_hole):
    row = {"tag": tag, "then_delete_hole": then_delete_hole, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        before = list(FR.feature_names(doc) or [])
        sk = _mk_sketch_with_hole(doc, pick_sketch=True)
        row["sketch_selected"] = sk
        #: \u2605 \u2460 **\u5e73\u9762\u533a\u57df**
        ret = None
        try:
            ret = C.get_com_member(doc, "InsertPlanarRefSurface")
            row["planar_returned"] = str(ret)
        except Exception as exc:                                          # noqa: BLE001
            row["planar_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
        after = list(FR.feature_names(doc) or [])
        row["new_after_planar"] = [n for n in after if n not in before]
        row["geom_after_planar"] = _geom(doc)
        #: \u2605 \u5224\u636e \u2460\uff1a**\u771f\u7684\u5f97\u5230\u4e00\u5f20**\u535
        #: 5\u9762\u7684**\u5e73\u9762\u66f2\u9762**\uff08\u2605 1 \u9762\uff09
        g = row["geom_after_planar"]
        row["planar_ok"] = bool(row["new_after_planar"]) and g["faces"] == 1
        if not then_delete_hole:
            row["ok"] = row["planar_ok"]
            return row
        #: \u2605 \u2461 **\u5220\u9664\u5b54**\uff08\u2605 \u5728\u90a3\u5f20\u5e73\u97
        #: 62\u4e0a\u9009\u5b54\u7684\u8fb9\uff09
        from sw_connect import get_com_member as _g
        from sw_part import _select_com_object as _sel
        try:
            doc.ClearSelection2(True)
        except Exception:                                                 # noqa: BLE001
            pass
        picked = 0
        for b in list(_g(doc, "GetBodies2", 1, True) or []):
            for f in list(_g(b, "GetFaces") or []):
                for lp in list(_g(f, "GetLoops") or []):
                    try:
                        es = list(_g(lp, "GetEdges") or [])
                    except Exception:                                     # noqa: BLE001
                        es = []
                    #: \u2605 \u53ea\u9009**\u8fb9\u6570\u5c11\u7684\u90a3\u4e2a\u73af**
                    #: \uff08\u2605 \u5b54\u7684\u5708\u8fb9\u6570 \u2264 \u5916\u6846\u
                    #: ff09
                    if len(es) <= 1:
                        for e in es:
                            if _sel(e, append=(picked > 0), mark=0):
                                picked += 1
                break
            break
        row["hole_edges_picked"] = picked
        b2 = list(FR.feature_names(doc) or [])
        ret2 = None
        try:
            ret2 = _g(_g(doc, "FeatureManager"), "InsertDeleteHoleForSurface")
            row["del_returned"] = type(ret2).__name__ if ret2 is not None else "None"
            if ret2 is not None:
                for k, m in (("del_name", "Name"), ("del_type", "GetTypeName2")):
                    try:
                        row[k] = str(_g(ret2, m))
                    except Exception:                                     # noqa: BLE001
                        pass
        except Exception as exc:                                          # noqa: BLE001
            row["del_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
        a2 = list(FR.feature_names(doc) or [])
        row["new_after_delete"] = [n for n in a2 if n not in b2]
        row["geom_final"] = _geom(doc)
        row["loop_delta"] = row["geom_final"]["loops"] - g["loops"]
        row["ok"] = bool(row["planar_ok"] and (row["new_after_delete"]
                                              or row.get("del_type") or row["loop_delta"]))
    except Exception as exc:                                              # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:170])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                             # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "**\u5e73\u9762\u533a\u57df**\u9020\u771f\u6b63\u7684\u5e26\u5b54\u66f2\u9762 \u2192 \u518d\u5728\u5176\u4e0a\u8bd5**\u5220\u9664\u5b54**",
          "official": "IModelDoc2.InsertPlanarRefSurface() \u2014\u2014 0 \u53c2 \u00b7 \u56de bool\uff1b"
                      "Remarks\uff1aselect the surface's boundary entities with **Marks of 1**",
          "cases": []}
    ev["cases"].append(_one(sw, "\u2460 \u53ea\u5efa**\u5e73\u9762\u533a\u57df**\uff08\u2605 \u9a8c\u5b83\u81ea\u5df1\uff09", False))
    ev["cases"].append(_one(sw, "\u2461 \u5e73\u9762\u533a\u57df + **\u5220\u9664\u5b54**", True))
    ev["planar_passed"] = sum(1 for c in ev["cases"] if c.get("planar_ok"))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = ("planar_region_works" if ev["planar_passed"] else "planar_region_fails")
    if ev["planar_passed"] and ev["cases"][1].get("ok"):
        ev["verdict"] = "planar_region_and_delete_hole_work"
    p = R / "output" / "planar-region-and-delete-hole-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**" % ev["verdict"])
    print("     \u5e73\u9762\u533a\u57df\u6210\uff1a%s / %s \u00b7 \u603b\u6210\uff1a%s / %s" % (
        ev["planar_passed"], ev["total"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        g = c.get("geom_after_planar") or {}
        print("  %s" % c.get("tag"))
        print("        \u8349\u56fe\u9009\u4e2d=%s \u5e73\u9762\u56de=%s \u65b0\u589e=%s" % (
            c.get("sketch_selected"), c.get("planar_returned"), c.get("new_after_planar")))
        print("        \u51e0\u4f55\uff1a\u9762=%s \u73af=%s \u8fb9=%s\u00b7\u73af\u5f62\u6001=%s" % (
            g.get("faces"), g.get("loops"), g.get("edges"), g.get("per_loop")))
        if c.get("then_delete_hole"):
            print("        \u5b54\u8fb9\u9009\u4e86=%s \u5220\u9664\u5b54\u56de=%s \u540d=%s \u578b=%s \u65b0\u589e=%s \u73af\u0394=%s" % (
                c.get("hole_edges_picked"), c.get("del_returned"), c.get("del_name"),
                c.get("del_type"), c.get("new_after_delete"), c.get("loop_delta")))
        for k in ("planar_err", "del_err", "err"):
            if c.get(k):
                print("        %s=%s" % (k, str(c[k])[:130]))
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
