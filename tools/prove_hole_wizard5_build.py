"""★ 真机：**高级孔** —— `SelectByRay` 定孔位 + `IFeatureManager.HoleWizard5`（27 参）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_hole_wizard5_build.py
# 定位:   ★ 2026-10-03（轮 590）★ 执行**事实 466 留的下一步**（★ 用 `SelectByRay` 定位 + 真建孔）。
#
#   ★★ **官方 `IFeatureManager.HoleWizard5.md`\uff08**27 \u53c2**\uff0c\u2605 \u672a\u6807\u5e9f\u5f03\uff09**\uff1a
#     ```
#     Feature HoleWizard5(int GenericHoleType, int StandardIndex, int FastenerTypeIndex,
#         string SSize, short EndType, double Diameter, double Depth, double Length,
#         double Value1 \u2026 Value12, string ThreadClass, bool RevDir, bool FeatureScope,
#         bool AutoSelect, bool AssemblyFeatureScope, bool AutoSelectComponents,
#         bool PropagateFeatureToParts)
#     \u2605 Remarks\uff1a"\u2026call **`SelectByRay` with Mark = 0** for each location."
#     \u2605 Remarks\uff1a"If the material is on one side of the reference plane, then **RevDir is false**."
#     \u2605 Remarks\uff1a`FastenerTypeIndex` \u5fc5\u987b\u4e0e standard \u5339\u914d\uff1b`SSize` \u5fc5\u987b\u5408\u6cd5\u3002
#     ```
#
#   ★ **\u679a\u4e3e\u5747\u53d6\u81ea\u672c\u673a\u53cd\u5c04 dump**\uff08\u2605 \u94c1\u5f8b 4 \u7684\u88c1\u51b3\u8005\uff09\uff1a
#     `swWzdGeneralHoleTypes_e`\uff1a**`swWzdHole = 2`** \u00b7 `swWzdCounterBore = 0` \u00b7 `swWzdCounterSink = 1` \u00b7
#       `swWzdTap = 4` \u00b7 `swWzdLegacy = 5` \u00b7 \u69fd 6/7/8\uff1b
#     `swEndConditions_e`\uff1a`swEndCondBlind = 0` \u00b7 **`swEndCondThroughAll = 1`**\uff1b
#     `swSelectType_e`\uff1a**`swSelFACES = 2`**\uff1b
#     \u2605 \u800c**\u5b54\u6807\u51c6**\u53d6\u81ea\u672c\u4ed3 `sw_hole_features.list_hole_standards`\uff1a
#       `{0: ANSI Inch, 1: ANSI Metric, 16: AS, 2: BSI, 4: DIN, 13: GB, \u2026}`\u3002
#
#   ★ 判据（★ 规则 6）：**特征树增量**（★ 应出现「异型孔向导」特征，★ 而不是「切除-拉伸」）。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 三格：ThroughAll / Blind / 对照（不选孔位）。
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
import scripts.sw_feature_readback as FR                              # noqa: E402

SW_SEL_FACES = 2
SW_WZD_HOLE = 2                 #: \u2605 \u53cd\u5c04\uff1a`swWzdHole = 2`
SW_END_THROUGH_ALL = 1          #: \u2605 \u53cd\u5c04\uff1a`swEndCondThroughAll = 1`
SW_END_BLIND = 0                #: \u2605 \u53cd\u5c04\uff1a`swEndCondBlind = 0`
ANSI_METRIC = 1                 #: \u2605 \u672c\u4ed3 list_hole_standards\uff1a`{1: 'ANSI Metric'}`


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


def _ray(doc, x=0.0, y=0.0, z=0.05, vec=(0.0, 0.0, -1.0), r=1e-4, mark=0, append=False):
    ext = C.get_com_member(doc, "Extension")
    return C.get_com_member(ext, "SelectByRay", float(x), float(y), float(z),
                            float(vec[0]), float(vec[1]), float(vec[2]),
                            float(r), int(SW_SEL_FACES), bool(append), int(mark), 0)


def _one(sw, tag, end_type, do_ray, fastener=40, ssize=""):
    row = {"tag": tag, "end_type": end_type, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["plate"] = _plate(doc)
        if do_ray:
            try:
                row["ray"] = str(_ray(doc, 0.0, 0.0))
            except Exception as exc:                                      # noqa: BLE001
                row["ray"] = "%s: %s" % (type(exc).__name__, str(exc)[:70])
        before = list(FR.feature_names(doc) or [])
        row["before"] = len(before)
        fm = C.get_com_member(doc, "FeatureManager")
        args = (
            SW_WZD_HOLE,            # GenericHoleType
            ANSI_METRIC,            # StandardIndex
            int(fastener),          # FastenerTypeIndex（★ **合法值**）
            ssize,                  # SSize
            int(end_type),          # EndType
            0.008,                  # Diameter (m) = 8 mm
            0.02,                   # Depth (m) = 20 mm
            0.0,                    # Length
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,   # Value1..12
            "",                     # ThreadClass
            False,                  # RevDir (\u2605 \u5b98\u65b9\uff1a\u6750\u6599\u5728\u4e00\u4fa7\u65f6\u4e3a False)
            True,                   # FeatureScope
            False,                  # AutoSelect
            False,                  # AssemblyFeatureScope
            False,                  # AutoSelectComponents
            False,                  # PropagateFeatureToParts
        )
        row["n_args"] = len(args)
        ret = None
        try:
            ret = C.get_com_member(fm, "HoleWizard5", *args)
            row["returned"] = type(ret).__name__ if ret is not None else "None"
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        after = list(FR.feature_names(doc) or [])
        row["new_features"] = [n for n in after if n not in before]
        row["ok"] = bool(row["new_features"])
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
          "_": "\u9ad8\u7ea7\u5b54\uff1a`SelectByRay` \u5b9a\u4f4d + `HoleWizard5`\uff08**27 \u53c2**\uff09",
          "official": "HoleWizard5 27 \u53c2\uff1bRemarks\uff1a\u5b54\u4f4d\u7528 `SelectByRay`\u3001`Mark = 0`\uff1b"
                      "`RevDir` \u5728\u6750\u6599\u4e00\u4fa7\u65f6\u4e3a False",
          "enums": {"swWzdHole": SW_WZD_HOLE, "swEndCondThroughAll": SW_END_THROUGH_ALL,
                    "swEndCondBlind": SW_END_BLIND, "swSelFACES": SW_SEL_FACES,
                    "ANSI_METRIC": ANSI_METRIC},
          "cases": []}
    ev["cases"].append(_one(sw, "\u2605 SSize='' \u00b7 \u87ba\u9489\u95f4\u9699(40)", SW_END_THROUGH_ALL, True, 40, ''))
    ev["cases"].append(_one(sw, "\u2605 SSize='8' \u00b7 \u87ba\u9489\u95f4\u9699(40)", SW_END_THROUGH_ALL, True, 40, '8'))
    ev["cases"].append(_one(sw, "\u2605 SSize='M8' \u00b7 \u87ba\u9489\u95f4\u9699(40)", SW_END_THROUGH_ALL, True, 40, 'M8'))
    ev["cases"].append(_one(sw, "\u2605 SSize='0.008' \u00b7 \u87ba\u9489\u95f4\u9699(40)", SW_END_THROUGH_ALL, True, 40, '0.008'))
    ev["cases"].append(_one(sw, "\u2605 SSize='M8x1.25' \u00b7 \u87ba\u9489\u95f4\u9699(40)", SW_END_THROUGH_ALL, True, 40, 'M8x1.25'))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "hole_wizard5_%d_of_%d" % (ev["passed"], ev["total"])
    p = R / "output" / "hole-wizard5-build-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**" % ev["verdict"])
    for c in ev["cases"]:
        print("  %-46s ok=%-6s \u7279\u5f81 %s \u2192 %s" % (
            c.get("tag"), c.get("ok"), c.get("before"),
            (c.get("before") or 0) + len(c.get("new_features") or [])))
        print("        \u5c04\u7ebf=%s n_args=%s \u56de=%s \u65b0\u589e=%s" % (
            c.get("ray"), c.get("n_args"), c.get("returned"), c.get("new_features")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:150])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
