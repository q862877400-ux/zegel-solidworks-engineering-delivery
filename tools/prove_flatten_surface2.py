"""★ 真机：**曲面展平** `InsertFlattenSurface2`（★ 官方给了 2 参与五个 mark）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_flatten_surface2.py
# 定位:   ★ 2026-10-03（轮 555）★ 照新纪律（**官方文档是第 0 步**）攻「曲面展平」。
#
#   ★★★★ **而台账写的 `InsertFlattenSurface` 是废弃的第一代**（★ 事实 433 的地图）：
#     > "**Obsolete. Superseded by `IFeatureManager::InsertFlattenSurface2`.**"
#
#   ★★★★★ **第二代的签名（★ 只 2 参）与 Remarks（★ 五个 mark 分工）逐字**：
#     ```
#     Feature InsertFlattenSurface2(int AccuracyFactor, bool ShouldUseTears)
#
#     AccuracyFactor : 10 >= Accuracy of flattened triangle mesh >= 1; 1 is highest accuracy
#     ShouldUseTears : True to use relief cuts, false to not
#
#     Before calling this method, select… By calling SelectByID2 with Mark…
#       1  = **Faces or surfaces to flatten**   \u2190 \u2605 \u5fc5\u9700
#       2  = Edges to guide the shape and length of the flattened surface
#       4  = Map edges
#       8  = Tear edges
#       16 = Anchor point from which to flatten
#     ```
#     ★ See Also ⇒ `ISurfaceFlattenFeatureData`\u3002
#
#   ★ 本探针：★ **一张曲面 + 选它的面 mark=1 ⇒ 调 2 参**。
#     ★ 判据（★ 规则 6 + 事实 420）：**树增量** **或** **返回对象带类型名**。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
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


def _mk_surface(doc):
    """★ 一张**可展平的曲面**（★ 用直线拉出的曲面 —— ★ 那才是"能展平"的形态）。"""
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name="Front Plane")
    #: \u2605 \u7528**\u76f4\u7ebf**\u62c9\uff08\u2605 \u76f4\u7ebf\u62c9\u51fa\u7684\u66f2\u9762\u53ef\u5c55\u5e73\uff1b\u2605 \u800c\u5c01\u95ed\u77e9\u5f62\u62c9\u51fa\u7684\u662f\u7b52\u72b6\uff09
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateLine",
                     -0.03, 0.0, 0.0, 0.03, 0.0, 0.0)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            return SF.create_extruded_surface_report(doc, 40.0, sketch_name=cand)
        except Exception:                                                 # noqa: BLE001
            continue
    return {}


def _one(sw, tag, entry, accuracy, tears):
    row = {"tag": tag, "entry": entry, "accuracy": accuracy, "tears": tears, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["surface"] = bool((_mk_surface(doc) or {}).get("ok"))
        from sw_connect import get_com_member as _get
        from sw_part import _select_com_object as _sel
        try:
            doc.ClearSelection2(True)
        except Exception:                                                 # noqa: BLE001
            pass
        #: \u2605 \u9009**\u66f2\u9762\u7684\u9762**\uff08\u2605 \u5b98\u65b9 mark = **1**\uff09
        picked = 0
        for b in list(_get(doc, "GetBodies2", 1, True) or []):
            for f in list(_get(b, "GetFaces") or [])[:1]:
                if _sel(f, append=(picked > 0), mark=1):
                    picked += 1
            break
        row["faces_mark1"] = picked
        try:
            row["mark1_count"] = int(_get(_get(doc, "SelectionManager"), "GetSelectedObjectCount2", 1))
        except Exception:                                                 # noqa: BLE001
            row["mark1_count"] = -1
        before = list(FR.feature_names(doc) or [])
        fm = _get(doc, "FeatureManager")
        ret = None
        try:
            ret = _get(fm, entry, int(accuracy), bool(tears))
            row["returned"] = type(ret).__name__ if ret is not None else "None"
            if ret is not None:
                for k, m in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
                    try:
                        row[k] = str(_get(ret, m))
                    except Exception:                                     # noqa: BLE001
                        pass
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:170])
        after = list(FR.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["ok"] = bool(row["new"] or row.get("ret_type"))
    except Exception as exc:                                              # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
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
          "_": "\u66f2\u9762\u5c55\u5e73\uff1a`InsertFlattenSurface2`\uff08\u2605 \u7b2c\u4e8c\u4ee3\u3001\u53ea 2 \u53c2\u3001\u9762 mark=1\uff09",
          "official": "InsertFlattenSurface.md \u9010\u5b57\uff1aObsolete. Superseded by InsertFlattenSurface2\uff1b"
                      "\u7b2c\u4e8c\u4ee3 Remarks\uff1a1=faces to flatten / 2=guide / 4=map / 8=tear / 16=anchor",
          "cases": []}
    ev["cases"].append(_one(sw, "\u2605 InsertFlattenSurface2\uff08\u7b2c\u4e8c\u4ee3\uff09", "InsertFlattenSurface2", 4, False))
    ev["cases"].append(_one(sw, "\u5bf9\u7167\uff1a\u7b2c\u4e00\u4ee3 InsertFlattenSurface\uff08\u5df2\u5e9f\u5f03\uff09",
                            "InsertFlattenSurface", 4, False))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "flatten2_works" if ev["cases"][0].get("ok") else "flatten2_fails"
    p = R / "output" / "flatten-surface2-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-46s ok=%-6s \u66f2\u9762=%s mark1=%s" % (
            c.get("tag"), c.get("ok"), c.get("surface"), c.get("mark1_count")))
        print("        \u65b0\u589e=%s \u540d=%s \u578b=%s" % (c.get("new"), c.get("ret_name"), c.get("ret_type")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:150])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
