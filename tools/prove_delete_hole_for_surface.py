"""★ 真机：**删除孔（曲面）** `InsertDeleteHoleForSurface` —— ★ 更正事实 439 的实证入口。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_delete_hole_for_surface.py
# 定位:   ★★★★ 2026-10-03（轮 562）**更正自己上一个误判**。
#
#   ★ 轮 559/560 我试的是 **`IModelDoc2.InsertDeleteHole()`**（★ 0 参 · 回 `void`），
#     六种前置**全零效果**，★ 于是把它归成**「第五种形态：静默 no-op」**（事实 439）。
#
#   ★★★★ **而本轮扫"剩下 20 条哪些废弃"时发现**：`InsertDeleteHole` 的 md 头上写着
#     > "**Obsolete. Supserseded by `IFeatureManager::InsertDeleteHoleForSurface`.**"  ⚠⚠⚠
#     ⇒ ★★ **故"六格零效果"的真因是**入口错**（★ 我打了废弃的第一代），
#       ★ **而不是**那个成员本身是 no-op** ⚠
#
#   ★★★★★ **继任者的文档（逐字）**：
#     ```
#     Feature InsertDeleteHoleForSurface()          \u2190 \u2605 **0 \u53c2**\uff0c\u800c**\u8fd4\u56de `IFeature`**\uff08\u2605 \u4e0d\u662f void\uff09
#     Remarks: Before calling this method, call SelectByID2 to select the
#              **hole edges to remove** from the surface.
#     ```
#     ⇒ ★★ **⇒ 前置 = 选**孔的边****（★ 而那正是我轮 560 试过的那个前置）✓
#
#   ★ 本探针：★ **带内环（孔）的曲面** ⇒ 选**孔的边** ⇒ 调**继任者**。
#     ★ 判据：★ **返回 `Feature` 且带类型名** **或** 树增量 **或** 几何量变化。
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
R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402
from scripts import sw_surface_features as SF                         # noqa: E402
import scripts.sw_feature_readback as FR                              # noqa: E402


def _mk_surface_with_hole(doc):
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
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            return SF.create_extruded_surface_report(doc, 0.5, sketch_name=cand)
        except Exception:                                                 # noqa: BLE001
            continue
    return {}


def _geom(doc):
    from sw_connect import get_com_member as _g
    faces = loops = 0
    for b in list(_g(doc, "GetBodies2", 1, True) or []):
        for f in list(_g(b, "GetFaces") or []):
            faces += 1
            try:
                loops += len(list(_g(f, "GetLoops") or []))
            except Exception:                                             # noqa: BLE001
                pass
    return {"faces": faces, "loops": loops}


def _one(sw, tag, entry, pick):
    row = {"tag": tag, "entry": entry, "pick": pick, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["made"] = bool((_mk_surface_with_hole(doc) or {}).get("ok"))
        row["before"] = _geom(doc)
        from sw_connect import get_com_member as _g
        from sw_part import _select_com_object as _sel
        try:
            doc.ClearSelection2(True)
        except Exception:                                                 # noqa: BLE001
            pass
        picked = 0
        for b in list(_g(doc, "GetBodies2", 1, True) or []):
            if pick == "face":
                for f in list(_g(b, "GetFaces") or [])[:1]:
                    if _sel(f, append=False, mark=0):
                        picked += 1
            else:
                #: \u2605 **\u5185\u73af\u90a3\u5708\u8fb9**\uff08\u2605 \u5b98\u65b9 Remarks \u8bf4\u7684 "hole edges"\uff09
                for e in list(_g(b, "GetEdges") or []):
                    try:
                        if _sel(e, append=(picked > 0), mark=0):
                            picked += 1
                    except Exception:                                     # noqa: BLE001
                        pass
            break
        row["picked"] = picked
        before = list(FR.feature_names(doc) or [])
        fm = _g(doc, "FeatureManager")
        ret = None
        try:
            ret = _g(fm, entry)
            row["returned"] = type(ret).__name__ if ret is not None else "None"
            if ret is not None:
                for k, m in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
                    try:
                        row[k] = str(_g(ret, m))
                    except Exception:                                     # noqa: BLE001
                        pass
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = list(FR.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["after"] = _geom(doc)
        row["delta"] = {k: (row["after"][k] - row["before"][k]) for k in ("faces", "loops")}
        row["ok"] = bool(row["new"] or row.get("ret_type") or any(row["delta"].values()))
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
          "_": "\u5220\u9664\u5b54\uff08\u66f2\u9762\uff09\uff1a**\u7ee7\u4efb\u8005** `InsertDeleteHoleForSurface`\uff08\u2605 \u66f4\u6b63\u4e8b\u5b9e 439\uff09",
          "official": "InsertDeleteHole.md \u9010\u5b57\uff1aObsolete. Supserseded by "
                      "IFeatureManager::InsertDeleteHoleForSurface\uff1b"
                      "\u7ee7\u4efb\u8005\uff1a0 \u53c2 \u00b7 \u56de IFeature \u00b7 Remarks\uff1a\u9009 **hole edges**",
          "cases": []}
    ev["cases"].append(_one(sw, "\u2605 **\u7ee7\u4efb\u8005** + \u9009\u5b54\u7684\u8fb9", "InsertDeleteHoleForSurface", "edge"))
    ev["cases"].append(_one(sw, "\u7ee7\u4efb\u8005 + \u53ea\u9009\u9762", "InsertDeleteHoleForSurface", "face"))
    ev["cases"].append(_one(sw, "\u5bf9\u7167\uff1a**\u5e9f\u5f03\u7684\u7b2c\u4e00\u4ee3** + \u9009\u5b54\u7684\u8fb9",
                            "InsertDeleteHole", "edge"))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = ("successor_works_my_439_was_wrong" if ev["cases"][0].get("ok")
                     else "successor_also_fails")
    p = R / "output" / "delete-hole-for-surface-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        b, a = c.get("before") or {}, c.get("after") or {}
        print("  %-44s ok=%-6s picked=%s" % (c.get("tag"), c.get("ok"), c.get("picked")))
        print("        \u56de=%s \u540d=%s \u578b=%s" % (c.get("returned"), c.get("ret_name"), c.get("ret_type")))
        print("        \u9762 %s\u2192%s \u00b7 \u73af %s\u2192%s \u00b7 \u65b0\u589e=%s" % (
            b.get("faces"), a.get("faces"), b.get("loops"), a.get("loops"), c.get("new")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
