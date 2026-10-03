"""★ 真机：**解除剪裁曲面** —— 先造出它的前置（★ 一张**真被剪裁过**的曲面）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_untrim_with_trimmed_surface.py
# 定位:   ★ 2026-10-03（轮 557）★ 执行**事实 433 留的下一步**：
#
#   > ★ 状态：**入口与 arity 已定，前置（得先有一张被剪裁的曲面）尚未搭对**。
#
#   ★★ **本轮的思路（★ 承轮 556 的成功路径）**：★ 把"缺什么"逼到具体 ——
#     ★ 缺的是**一张被剪裁过的曲面**。★ 那就要**先造出它**：
#       ⓐ 造一张曲面（直线拉出的平面曲面）
#       ⓑ **用另一张曲面去切它** ⇒ ★ 于是它**被剪裁了**
#       ⓒ 再对切剩的那张面调 `InsertUntrimSurface2`
#
#   ★ **两把"裁刀"都试**（★ 因为哪把真剪成过、账上并不清楚）：
#     · `FeatureManager.InsertCutSurface`（★ 曲面切除 —— ★ 事实 406：它**回对象**、而对象在树外）
#     · `ModelDoc2.PreTrimSurface` + `PostTrimSurface`（★ 剪裁曲面 —— ★ 事实 415：顺序是
#       PreTrimSurface → 选 SURFACEBODY → PostTrimSurface）
#
#   ★ **而"有没有真被剪裁"本身要记账**：★ 数**曲面体数 / 面数**（★ 剪裁会让它们变）。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 规则 6 + 事实 420）：**树增量** **或** **返回对象带类型名**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                   # noqa: E402
from scripts.sw_connect import create_empty_dispatch_variant as _av    # noqa: E402
from scripts import sw_part as P                                      # noqa: E402
from scripts import sw_surface_features as SF                         # noqa: E402
import scripts.sw_feature_readback as FR                              # noqa: E402


def _mk_two_crossing_surfaces(doc):
    made = 0
    for i, (plane, rect) in enumerate((("Front Plane", (-0.02, -0.02, 0.02, 0.02)),
                                       ("Top Plane", (-0.02, -0.01, 0.02, 0.01)))):
        try:
            doc.ClearSelection2(True)
        except Exception:                                                     # noqa: BLE001
            pass
        P.start_sketch(doc, plane_name=plane)
        C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                         rect[0], rect[1], 0.0, rect[2], rect[3], 0.0)
        P.end_sketch(doc)
        names = [n for n in (P.feature_names(doc) or [])
                 if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
        for cand in ((names[-1],) + tuple(names) + ("\u8349\u56fe%d" % (i + 1),))[:4]:
            try:
                if SF.create_extruded_surface_report(doc, 30.0, sketch_name=cand).get("ok"):
                    made += 1
                    break
            except Exception:                                                 # noqa: BLE001
                continue
    return made


def _geom(doc):
    from sw_connect import get_com_member as _g
    try:
        bodies = list(_g(doc, "GetBodies2", 1, True) or [])
    except Exception:                                                         # noqa: BLE001
        bodies = []
    faces = 0
    for b in bodies:
        try:
            faces += len(list(_g(b, "GetFaces") or []))
        except Exception:                                                     # noqa: BLE001
            pass
    return {"surface_bodies": len(bodies), "surface_faces": faces}


def _run(sw, tag, cutter):
    row = {"tag": tag, "cutter": cutter, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["made"] = _mk_two_crossing_surfaces(doc)
        row["geom_before"] = _geom(doc)
        from sw_connect import get_com_member as _g, out_i4 as _oi4
        from sw_part import _select_com_object as _sel
        fm = _g(doc, "FeatureManager")
        trimmed = None
        if cutter == "cutsurface":
            try:
                doc.ClearSelection2(True)
            except Exception:                                                 # noqa: BLE001
                pass
            for b in list(_g(doc, "GetBodies2", 1, True) or []):
                fs = list(_g(b, "GetFaces") or [])
                if fs:
                    _sel(fs[0], append=True, mark=0)
                break
            trimmed = _g(fm, "InsertCutSurface", False, 0, False, True, [], _oi4())
            row["cut_returned"] = type(trimmed).__name__ if trimmed is not None else "None"
        else:
            #: \u2605 \u7167\u4e8b\u5b9e 415 \u7684\u987a\u5e8f\uff1a\u5148 Pre \u2192 \u518d\u9009 \u2192 \u518d Post
            try:
                row["pre"] = str(_g(fm, "PreTrimSurface", False, True, False, False))
                doc.ClearSelection2(True)
            except Exception as exc:                                          # noqa: BLE001
                row["pre_err"] = str(exc)[:100]
            ext = _g(doc, "Extension")
            picked = False
            for pt in ((0.0, 0.0, 0.0), (0.005, 0.0, 0.005), (-0.005, 0.0, -0.005)):
                try:
                    if _g(ext, "SelectByID2", "", "SURFACEBODY", pt[0], pt[1], pt[2],
                          True, 0, _av(), 0):
                        picked = True
                        break
                except Exception:                                             # noqa: BLE001
                    continue
            row["picked_body"] = picked
            trimmed = _g(fm, "PostTrimSurface", True)
            row["post_returned"] = type(trimmed).__name__ if trimmed is not None else "None"
        row["geom_after_trim"] = _geom(doc)
        before = list(FR.feature_names(doc) or [])
        #: \u2605 **\u73b0\u5728\u5bf9\u5b83\u8c03\u89e3\u9664\u526a\u88c1**\uff08\u2605 5 \u53c2\uff09
        try:
            doc.ClearSelection2(True)
        except Exception:                                                     # noqa: BLE001
            pass
        npick = 0
        for b in list(_g(doc, "GetBodies2", 1, True) or []):
            for f in list(_g(b, "GetFaces") or [])[:1]:
                if _sel(f, append=(npick > 0), mark=0):
                    npick += 1
            break
        row["faces_for_untrim"] = npick
        ret = None
        try:
            ret = _g(fm, "InsertUntrimSurface2", 0, 2, 0.005, True, False)
            row["untrim_returned"] = type(ret).__name__ if ret is not None else "None"
            if ret is not None:
                for k, m in (("untrim_name", "Name"), ("untrim_type", "GetTypeName2")):
                    try:
                        row[k] = str(_g(ret, m))
                    except Exception:                                         # noqa: BLE001
                        pass
        except Exception as exc:                                              # noqa: BLE001
            row["untrim_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = list(FR.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["geom_final"] = _geom(doc)
        row["ok"] = bool(row["new"] or row.get("untrim_type"))
    except Exception as exc:                                                  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                                 # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "\u89e3\u9664\u526a\u88c1\uff1a**\u5148\u9020\u51fa\u4e00\u5f20\u771f\u88ab\u526a\u88c1\u8fc7\u7684\u66f2\u9762**\uff08\u2605 \u4e8b\u5b9e 433 \u7684\u4e0b\u4e00\u6b65\uff09",
          "official": "InsertUntrimSurface2 \u4e0e 5 \u53c2\uff1bRemarks\uff1avalid only for surface parts\u3001"
                      "requires preselection of the face or edges you want to untrim",
          "cases": []}
    ev["cases"].append(_run(sw, "\u2460 \u7528**\u66f2\u9762\u5207\u9664**\u5f53\u88c1\u5200", "cutsurface"))
    ev["cases"].append(_run(sw, "\u2461 \u7528**\u526a\u88c1\u66f2\u9762**(Pre/Post)\u5f53\u88c1\u5200", "pretrim"))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "untrim_works" if ev["passed"] else "untrim_still_fails"
    p = R / "output" / "untrim-with-trimmed-surface-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %s" % c.get("tag"))
        print("        \u4f53/\u9762 \u521d=%s \u526a\u540e=%s \u6700\u540e=%s" % (
            c.get("geom_before"), c.get("geom_after_trim"), c.get("geom_final")))
        print("        \u88c1\u5200\u56de=%s \u89e3\u9664\u526a\u88c1\u56de=%s \u540d=%s \u578b=%s" % (
            c.get("cut_returned") or c.get("post_returned"), c.get("untrim_returned"),
            c.get("untrim_name"), c.get("untrim_type")))
        print("        \u65b0\u589e=%s" % (c.get("new"),))
        for k in ("pre", "pre_err", "untrim_err", "err"):
            if c.get(k):
                print("        %s=%s" % (k, str(c[k])[:120]))
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
