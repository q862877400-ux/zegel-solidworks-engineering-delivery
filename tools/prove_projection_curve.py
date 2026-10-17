"""★ 真机：**投影曲线**（★ 第三代：`CreateDefinition(swFmRefCurve=14)` + `IProjectionCurveFeatureData`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_projection_curve.py
# 定位:   ★ 2026-10-03（轮 566）★ 照新纪律（**官方文档是第 0 步**）攻「曲线-投影曲线」。
#
#   ★★★★ **本轮发现：这条的**两代都是废弃的****（★ 事实 433 那张地图只挖到第二代）：
#     · `IModelDoc2.InsertProjectedSketch`  ⇒ md 逐字：Superseded by `InsertProjectedSketch2`
#     · `IModelDoc2.InsertProjectedSketch2` ⇒ ★ **它自己也是废弃的**：
#       > "**Obsolete. See `IProjectionCurveFeatureData` and `IFeatureManager::CreateDefinition`.**"
#     ⇒ ★★ **故正路是**第三代**** ✓
#
#   ★★★★★ **而官方把第三代给成了**一条五步配方**（`IProjectionCurveFeatureData` 的 `## Remarks` 逐字）**：
#     ```
#     1. \u7528 `SelectByID2` \u9884\u9009\u5b9e\u4f53\uff0cMarks\uff1a
#        \u00b7 **target faces on which to project a sketch = 1**
#        \u00b7 **sketch to project = 2**
#        \u00b7 target sketch on which to project a sketch = 4
#        \u00b7 projection direction entity = 8
#     2. `IFeatureManager::CreateDefinition(swFmRefCurve)` \u21d2 \u62ff\u5230\u8fd9\u4e2a\u63a5\u53e3
#     3. \u5728\u8be5\u63a5\u53e3\u4e0a\u8bbe**\u975e\u5b9e\u4f53**\u5c5e\u6027
#     4. `IFeatureManager::CreateFeature` \u21d2 \u5efa\u51fa\u7279\u5f81
#     ```
#     ★ **而常量值来自**反射**（★ 铁律 4）**：**`swFmRefCurve = 14`** \u2713
#
#   ★ 判据（★ 规则 6 + 事实 420）：**返回 `Feature` 带类型名** **或** 树增量。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 两组：★ 投到面（mark 1 + 2）/ 对照（只给草图）。
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

#: \u2605 \u53cd\u5c04\u91cc\u7684\u503c\uff08\u2605 \u94c1\u5f8b 4\uff1a\u6570\u503c\u53bb\u53cd\u5c04\uff09
SW_FM_REF_CURVE = 14


def _mk_target(doc):
    """★ 一个**实体**（★ 供 mark=1 的目标面用）+ ★ 一个**要投影的草图**（mark=2）。"""
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                     -0.03, -0.03, 0.0, 0.03, 0.03, 0.0)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    solid = False
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            P.extrude_boss(doc, cand, 0.02)
            solid = True
            break
        except Exception:                                                 # noqa: BLE001
            continue
    #: \u2605 \u8981\u6295\u5f71\u7684\u8349\u56fe\uff08\u2605 \u5728\u524d\u89c6\u9762\u4e0a\uff09
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name="Front Plane")
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCircleByRadius",
                     0.0, 0.0, 0.0, 0.012)
    P.end_sketch(doc)
    nm2 = [n for n in (P.feature_names(doc) or [])
           if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    return solid, (nm2[-1] if nm2 else None)


def _one(sw, tag, with_face, with_sketch_prop=True):
    row = {"tag": tag, "with_face": with_face, "with_sketch_prop": with_sketch_prop, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        solid, sk = _mk_target(doc)
        row["solid"] = solid
        row["sketch_to_project"] = sk
        from sw_connect import get_com_member as _g
        from sw_part import _select_com_object as _sel
        ext = _g(doc, "Extension")
        try:
            doc.ClearSelection2(True)
        except Exception:                                                     # noqa: BLE001
            pass
        marks = {}
        #: \u2605 **mark = 1** \u2014\u2014 \u76ee\u6807\u9762
        if with_face:
            for b in list(_g(doc, "GetBodies2", 0, True) or []):
                for f in list(_g(b, "GetFaces") or []):
                    if _sel(f, append=(bool(marks)), mark=1):
                        marks["1"] = 1
                    break
                break
        #: \u2605 **mark = 2** \u2014\u2014 \u8981\u6295\u5f71\u7684\u8349\u56fe
        for cand in (P._get_sketch_name_candidates(sk) if sk else []):
            try:
                if P._select_by_id(ext, cand, "SKETCH", append=bool(marks), mark=2):
                    marks["2"] = 1
                    break
            except Exception:                                             # noqa: BLE001
                continue
        row["marks"] = marks
        before = list(FR.feature_names(doc) or [])
        fm = _g(doc, "FeatureManager")
        feat = None
        try:
            data = _g(fm, "CreateDefinition", SW_FM_REF_CURVE)
            row["data_type"] = type(data).__name__ if data is not None else "None"
            if data is not None:
                #: \u2605 \u7b2c 3 \u6b65\uff1a\u8bbe**\u975e\u5b9e\u4f53**\u5c5e\u6027 \u2014\u2014
                #:   \u2605 \u800c\u63a5\u53e3\u6b63\u597d\u6709 **3 \u4e2a**\uff1a`Bidirectional` \u00b7 `Reverse` \u00b7 **`Sketch`**
                setp = {}
                for k, v in (("Bidirectional", False), ("Reverse", False)):
                    try:
                        C.set_com_member(data, k, bool(v))
                        setp[k] = "ok"
                    except Exception as exc:                              # noqa: BLE001
                        setp[k] = "%s" % type(exc).__name__
                #: \u2605 **`Sketch`** \u2014\u2014 \u628a\u201c\u8981\u6295\u5f71\u7684\u90a3\u4e2a\u8349\u56fe\u201d\u8bbe\u8fdb\u53bb
                if with_sketch_prop and sk:
                    try:
                        fobj = None
                        for cand in P._get_sketch_name_candidates(sk):
                            try:
                                fobj = _g(doc, "FeatureByName", cand)
                                if fobj is not None:
                                    break
                            except Exception:                             # noqa: BLE001
                                continue
                        if fobj is not None:
                            sk_obj = _g(fobj, "GetSpecificFeature2")
                            C.set_com_member(data, "Sketch", sk_obj)
                            setp["Sketch"] = "ok"
                        else:
                            setp["Sketch"] = "\u62ff\u4e0d\u5230\u8349\u56fe\u5bf9\u8c61"
                    except Exception as exc:                              # noqa: BLE001
                        setp["Sketch"] = "%s" % type(exc).__name__
                row["props_set"] = setp
                #: \u2605\u2605\u2605 \u7b2c 98 \u8f6e\uff08\u8f6e 567\uff09\u8865\u7684\u90a3\u4e00\u6b65\uff1a
                #:   **`AccessSelections` \u2192 \u8bbe\u5b9e\u4f53\u6570\u636e \u2192 `CreateFeature` \u2192 `ReleaseSelectionAccess`**
                #:   \u2605 \u4f9d\u636e\uff1a\u4e8b\u5b9e 425/426\uff08\u2605 FeatureData \u90a3\u65cf\u7684 `AccessSelections`
                #:   **6/6 \u901a**\uff1b\u2605 \u800c `Component` \u8981\u4f20**\u7a7a Dispatch \u53d8\u4f53**\uff09\u3002
                try:
                    acc = C.get_com_member(data, "AccessSelections", doc,
                                           C.create_empty_dispatch_variant())
                    row["access_selections"] = str(acc)
                except Exception as exc:                                  # noqa: BLE001
                    row["access_selections"] = "%s: %s" % (type(exc).__name__, str(exc)[:90])
                feat = _g(fm, "CreateFeature", data)
                try:
                    C.get_com_member(data, "ReleaseSelectionAccess")
                    row["released"] = True
                except Exception as exc:                                  # noqa: BLE001
                    row["released"] = "%s" % type(exc).__name__
            row["returned"] = type(feat).__name__ if feat is not None else "None"
            if feat is not None:
                for k, m in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
                    try:
                        row[k] = str(_g(feat, m))
                    except Exception:                                     # noqa: BLE001
                        pass
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = list(FR.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["ok"] = bool(row["new"] or row.get("ret_type"))
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
          "_": "\u6295\u5f71\u66f2\u7ebf\uff1a**\u7b2c\u4e09\u4ee3** `CreateDefinition(swFmRefCurve=14)` + `IProjectionCurveFeatureData`",
          "official": "InsertProjectedSketch2 \u81ea\u5df1\u4e5f\u5df2\u5e9f\u5f03\uff1b"
                      "IProjectionCurveFeatureData \u7684 Remarks \u7ed9\u4e86 **\u4e94\u6b65\u914d\u65b9**"
                      "\uff08mark 1 = \u76ee\u6807\u9762 \u00b7 2 = \u8981\u6295\u7684\u8349\u56fe \u00b7 4 = \u76ee\u6807\u8349\u56fe \u00b7 8 = \u65b9\u5411\uff09",
          "cases": []}
    ev["cases"].append(_one(sw, "\u2605 \u4e09\u4ee3\uff1a\u76ee\u6807\u9762(mark=1) + \u8349\u56fe(mark=2)", True))
    ev["cases"].append(_one(sw, "\u5bf9\u7167\uff1a**\u4e0d\u8bbe `Sketch` \u5c5e\u6027**", True, False))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "projection_curve_works" if ev["cases"][0].get("ok") else "projection_curve_fails"
    p = R / "output" / "projection-curve-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-44s ok=%-6s solid=%s marks=%s" % (
            c.get("tag"), c.get("ok"), c.get("solid"), c.get("marks")))
        print("        data=%s \u56de=%s \u540d=%s \u578b=%s \u65b0\u589e=%s" % (
            c.get("data_type"), c.get("returned"), c.get("ret_name"), c.get("ret_type"), c.get("new")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
