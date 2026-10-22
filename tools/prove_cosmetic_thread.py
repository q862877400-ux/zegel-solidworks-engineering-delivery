"""★ 真机：**螺纹线** `InsertCosmeticThread3`（★ 7 参 · 未废弃）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_cosmetic_thread.py
# 定位:   ★ 2026-10-03（轮 568）★ 照新纪律（**官方文档是第 0 步**）攻台账「螺纹线」。
#
#   ★★★★★ **签名（7 参）与参数（逐字，`InsertCosmeticThread3.md`）**：
#     ```
#     Feature InsertCosmeticThread3(int Standard, string StandardType, string Size,
#                                   double Diameter, int EndType, double Depth, string Note)
#     Standard   : swCosmeticStandardType_e
# EndType    : swCosmeticEndConditions_e\uff08Depth \u4ec5\u5728 Blind \u7c7b\u4e0b\u670
# 9\u6548\uff09
#     Note       : \u5de5\u7a0b\u56fe\u91cc\u7684\u6807\u6ce8\u6587\u5b57
#     ```
# ★ **md 头上**未标 `Obsolete`****\uff08\u2605 \u53f0\u8d26\u7ed9\u7684 api \u540d\u662f
# \u5bf9\u7684\uff09\u2713
#
#   ★★★ **两个枚举的值来自**反射**（★ 铁律 4）**：
#     ```
# swCosmeticStandardType_e : 0=ANSI Inch \u00b7 **1=ANSI Metric** \u00b7 2=BSI \u00b7 4=
# DIN \u00b7 8=ISO \u00b7 9=JIS
# swCosmeticEndConditions_e: **0=Blind** \u00b7 1=BlindUptoNext \u00b7 **2=Through** \u0
# 0b7 3=Blind2Dia
#     ```
#
#   ★ 前置：★ **实体 + 一个圆孔** ⇒ ★ **选孔的圆边**（★ 螺纹线加在圆形边上）。
#   ★ 判据（★ 规则 6 + 事实 436）：**树增量** **或** **返回对象带类型名**。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 三组：选圆边 / 选圆柱面 / 不选（对照）。
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

#: \u2605 \u53cd\u5c04\u91cc\u7684\u503c
STD_ANSI_METRIC = 1
END_THROUGH = 2


def _mk_block_with_hole(doc, hole_dia_m=0.008):
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
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCircleByRadius",
                     0.0, 0.0, 0.0, hole_dia_m / 2.0)
    P.end_sketch(doc)
    names2 = [n for n in (P.feature_names(doc) or [])
              if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    for cand in (names2[-1] if names2 else "\u8349\u56fe2", "\u8349\u56fe2"):
        try:
            P.extrude_cut(doc, cand, 0.0)
            break
        except Exception:                                                 # noqa: BLE001
            try:
                P.extrude_cut(doc, cand, 0.02)
                break
            except Exception:                                         # noqa: BLE001
                pass
    return solid


def _one(sw, tag, pick):
    row = {"tag": tag, "pick": pick, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["built"] = _mk_block_with_hole(doc)
        from sw_connect import get_com_member as _g
        from sw_part import _select_com_object as _sel
        try:
            doc.ClearSelection2(True)
        except Exception:                                                 # noqa: BLE001
            pass
        picked = 0
        #: \u2605 \u5148\u627e**\u5706\u67f1\u9762**\uff08\u2605 \u5b83\u7684\u8fb9\u5c3
        #: 1\u662f\u90a3\u4e24\u4e2a\u5706\uff09
        cyl = None
        for b in list(_g(doc, "GetBodies2", 0, True) or []):
            for f in list(_g(b, "GetFaces") or []):
                try:
                    #: \u2605\u2605 \u7528**\u5b98\u65b9\u7684\u5224\u5f62\u65b9\u6cd5**
                    #: \uff08`ISurface.IsCylinder()`\uff09
                    #: \u2014\u2014 \u2605 \u800c**\u4e0d\u662f\u731c `Surface.Identity`
                    #:  \u7684\u5b57\u7b26\u4e32** \u26a0
                    #: \uff08\u2605 \u6211\u7b2c\u4e00\u7248\u5c31\u662f\u90a3\u4e48\u73
                    #: 1c\u7684 \u21d2 \u2605 **\u4e09\u7ec4\u5168 `cyl=False`**\uff09
                    if bool(_g(_g(f, "GetSurface"), "IsCylinder")):
                        cyl = f
                        break
                except Exception:                                         # noqa: BLE001
                    continue
            break
        row["cyl_face_found"] = cyl is not None
        if pick == "edge" and cyl is not None:
            for e in list(_g(cyl, "GetEdges") or [])[:1]:
                if _sel(e, append=False, mark=0):
                    picked += 1
        elif pick == "face" and cyl is not None:
            if _sel(cyl, append=False, mark=0):
                picked += 1
        row["picked"] = picked
        before = list(FR.feature_names(doc) or [])
        fm = _g(doc, "FeatureManager")
        ret = None
        try:
            #: \u2605 7 \u53c2\uff1aStandard \u00b7 StandardType \u00b7 Size \u00b7 Diam
            #: eter \u00b7 EndType \u00b7 Depth \u00b7 Note
            ret = _g(fm, "InsertCosmeticThread3", STD_ANSI_METRIC, "", "",
                     0.008, END_THROUGH, 0.0, "")
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
          "_": "\u87ba\u7eb9\u7ebf\uff1a`InsertCosmeticThread3`\uff08\u2605 7 \u53c2 \u00b7 \u672a\u5e9f\u5f03\uff09",
          "official": "Standard = swCosmeticStandardType_e\uff081 = ANSI Metric\uff09\uff1b"
                      "EndType = swCosmeticEndConditions_e\uff082 = Through\uff09\uff1b"
                      "\u679a\u4e3e\u503c\u53d6\u81ea\u53cd\u5c04",
          "cases": []}
    ev["cases"].append(_one(sw, "\u2605 \u9009**\u5706\u67f1\u9762\u7684\u5706\u8fb9**", "edge"))
    ev["cases"].append(_one(sw, "\u5bf9\u7167\uff1a\u9009**\u5706\u67f1\u9762**\u672c\u8eab", "face"))
    ev["cases"].append(_one(sw, "\u5bf9\u7167\uff1a**\u4ec0\u4e48\u90fd\u4e0d\u9009**", "none"))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "cosmetic_thread_works" if ev["cases"][0].get("ok") else "cosmetic_thread_fails"
    p = R / "output" / "cosmetic-thread-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-32s ok=%-6s built=%s cyl=%s picked=%s" % (
            c.get("tag"), c.get("ok"), c.get("built"), c.get("cyl_face_found"), c.get("picked")))
        print("        \u56de=%s \u540d=%s \u578b=%s \u65b0\u589e=%s" % (
            c.get("returned"), c.get("ret_name"), c.get("ret_type"), c.get("new")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
