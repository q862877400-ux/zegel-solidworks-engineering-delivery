"""★ 真机：**高级孔** —— `SelectByRay` 定孔位 + `IFeatureManager.HoleWizard5`（27 参）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_hole_wizard5.py
# 定位:   ★ 2026-10-03（轮 589）★ 执行**事实 465 留的下一步**（★ 路径① 的前置 `SelectB
#           yRay`）。
#
#   ★★ **官方那两页**：
#     `IModelDocExtension.SelectByRay.md`\uff08\u2605 \u672a\u5e9f\u5f03\uff0c**11 \u53c2**\uff09\uff1a
#       ```
#       bool SelectByRay(double WorldX, WorldY, WorldZ, double RayVecX, RayVecY, RayVecZ,
#                        double RayRadius, int TypeWanted, bool Append, int Mark, int Option)
#       \u2605 \u8bed\u4e49\uff1a"Defines a **cylindrical region of infinite length** that starts at the
#          specified point and runs parallel to the ray direction"
#       \u2605 **\u53ea\u9009** faces/edges/vertices\uff1b\u2605 **\u4e0d\u652f\u6301**\u8349\u56fe\u5b9e\u4f53/\u8f74/\u4e2d\u5fc3\u7ebf\u7b49\u3002
#       \u2605 RayRadius **<= 2.9 m**\u3002
#       ```
#     `IFeatureManager.HoleWizard5.md`\uff08**27 \u53c2**\uff09\u7684 Remarks \u9010\u5b57\uff1a
#       \u2605 "To add a hole or slot at one or more locations, call
#          **`IModelDocExtension::SelectByRay` with Mark = 0** for each location."
#
#   ★★★ **\u6545\u5b54\u4f4d\u662f\u201c\u5c04\u7ebf\u9009\u51fa\u6765\u7684\u201d** \u2014\u2014 \u2605 \u800c**\u4e0d\u662f\u88f8\u5750\u6807**\uff1a
#     \u2605 \u4ece\u5b54\u4f4d\u4e0a\u65b9\u53d1\u4e00\u6761\u5c04\u7ebf\u6253\u5230\u9762\u4e0a\uff0c\u2605 **\u547d\u4e2d\u4ec0\u4e48\u7531\u51e0\u4f55\u51b3\u5b9a** \u2014\u2014
#     \u2605 \u800c `Mark = 0` \u6b63\u662f `HoleWizard5` \u8981\u7684\u3002
#
#   ★ `swSelFACES = 2`\uff08\u2605 \u53d6\u81ea\u672c\u673a\u53cd\u5c04 dump \u2014\u2014 \u94c1\u5f8b 4 \u7684\u88c1\u51b3\u8005\uff09\u3002
#   ★ 判据（★ 规则 6）：**特征树增量** **或** **选择计数**。
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
from scripts import sw_hole_features as HF                            # noqa: E402
import scripts.sw_feature_readback as FR                              # noqa: E402

SW_SEL_FACES = 2          #: \u2605 \u53cd\u5c04 dump\uff1a`swSelFACES = 2`
SW_SEL_EDGES = 1


def _plate(doc, t=0.02):
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                     -0.04, -0.03, 0.0, 0.04, 0.03, 0.0)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    for cand in ((names[-1] if names else "\u8349\u56fe1"), "\u8349\u56fe1", "Sketch1"):
        try:
            P.extrude_boss(doc, cand, t)
            return True
        except Exception:                                                 # noqa: BLE001
            continue
    return False


def _sel_count(doc):
    try:
        return int(C.get_com_member(C.get_com_member(doc, "SelectionManager"),
                                    "GetSelectedObjectCount2", -1) or 0)
    except Exception:                                                     # noqa: BLE001
        return -1


def _ray_select(doc, x, y, z_from=0.05, vec=(0.0, 0.0, -1.0), radius=1e-4,
                type_wanted=SW_SEL_FACES, mark=0, append=False):
    """★ 从 `(x, y, z_from)` 沿 `vec` 发一条射线（★ 官方：圆柱形区域、无限长）。"""
    ext = C.get_com_member(doc, "Extension")
    return C.get_com_member(ext, "SelectByRay",
                            float(x), float(y), float(z_from),
                            float(vec[0]), float(vec[1]), float(vec[2]),
                            float(radius), int(type_wanted), bool(append), int(mark), 0)


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "\u9ad8\u7ea7\u5b54\uff1a`SelectByRay` \u5b9a\u5b54\u4f4d + `HoleWizard5`\uff0827 \u53c2\uff09",
          "official": "SelectByRay 11 \u53c2\uff08\u672a\u5e9f\u5f03\uff09\uff1bHoleWizard5 \u7684 Remarks\uff1a"
                      "\u2605 \u5b54\u4f4d\u8981\u7528 **`SelectByRay` \u4e14 `Mark = 0`**",
          "swSelFACES": SW_SEL_FACES,
          "cases": []}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row = {"tag": "\u2605 \u5c04\u7ebf\u9009\u9762\uff08\u2605 `SelectByRay`\uff09", "ok": False}
        row["plate"] = _plate(doc)
        #: \u2605 \u5c04\u7ebf\u4ece\uff08x=0, y=0, z=+0.05\uff09**\u5411\u4e0b**\u6253 \u21d2 \u5e94\u547d\u4e2d\u9876\u9762
        before = _sel_count(doc)
        row["sel_before"] = before
        try:
            ret = _ray_select(doc, 0.0, 0.0)
            row["returned"] = str(ret)
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = _sel_count(doc)
        row["sel_after"] = after
        row["new_selected"] = (after - before) if (after >= 0 and before >= 0) else None
        row["ok"] = bool(row["new_selected"] and row["new_selected"] > 0)
        #: \u2605 \u800c**\u770b\u770b\u9009\u4e2d\u7684\u662f\u4ec0\u4e48**\uff08\u2605 \u8bed\u4e49\u6838\u5bf9\uff09
        try:
            sm = C.get_com_member(doc, "SelectionManager")
            o = C.get_com_member(sm, "GetSelectedObject6", 1, -1)
            row["sel_type"] = type(o).__name__ if o is not None else "None"
        except Exception as exc:                                          # noqa: BLE001
            row["sel_type"] = "%s" % type(exc).__name__
        ev["cases"].append(row)
        #: \u2605 \u800c\u5408\u6cd5\u503c\u4ece**\u672c\u4ed3\u81ea\u5df1\u7684 lookup**\u62ff\uff08\u2605 \u4e0d\u51ed\u5370\u8c61\u586b\uff09
        try:
            ev["hole_standards"] = HF.list_hole_standards(sw, 0)[:6]
        except Exception as exc:                                          # noqa: BLE001
            ev["hole_standards"] = "%s: %s" % (type(exc).__name__, str(exc)[:80])
        feats = list(FR.feature_names(doc) or [])
        ev["features_after_ray"] = feats[-3:]
    except Exception as exc:                                              # noqa: BLE001
        ev["fatal"] = "%s: %s" % (type(exc).__name__, str(exc)[:170])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                             # noqa: BLE001
                pass
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "ray_select_%d_of_%d" % (ev["passed"], ev["total"])
    p = R / "output" / "hole-wizard5-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**" % ev["verdict"])
    for c in ev["cases"]:
        print("  %-44s ok=%-6s \u9009\u4e2d %s \u2192 %s\uff08\u589e %s\uff09\u56de=%s" % (
            c.get("tag"), c.get("ok"), c.get("sel_before"), c.get("sel_after"),
            c.get("new_selected"), c.get("returned")))
        print("        \u677f=%s \u9009\u4e2d\u7269\u7c7b\u578b=%s" % (c.get("plate"), c.get("sel_type")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u5b54\u6807\u51c6\uff08\u524d 6\uff09\uff1a%s" % (str(ev.get("hole_standards"))[:150],))
    if ev.get("fatal"):
        print("  fatal=%s" % ev["fatal"])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
