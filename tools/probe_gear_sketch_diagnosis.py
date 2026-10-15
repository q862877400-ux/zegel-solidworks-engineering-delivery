"""★ 真机：★ 诊断「真曲线齿轮草图为什么拉不出来」（★ 轮廓闭合性）。

★★★ **为什么拉不出来**（★ 我的假设，★ 要证）：
  ★ 一个齿距单元需要**两条曲线 + 两段圆弧**，★ 且**首尾相接**才能闭合成一个齿；
  ★★ 而我只画了**一条渐开线 + 一条摆线** ⇒ ★ 那是**开放轮廓** ⇒
    ★★★ `FeatureExtrusion3` 对开放草图**返回 None**（★ 不报错 —— ★ 静默）✗

★★ **本探针要查的三件事**：
  ★ ① ★ 草图里到底有几条**曲线**（★ `GetSketchSegments` 数不准 —— ★ 上一轮得 4）
  ★ ② ★ 每条曲线的**端点**在哪（★ 判断首尾接不接得上）
  ★ ③ ★ 用 `ISketch::GetSketchPoints2` 看**点的个数**（★ 方程式曲线会不会产生点）

★ 走 `sw_guard` ✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_gear_sketch_diagnosis.py
# 定位:   ★ 业主 2026-10-10「方法要规范」—— ★ 真曲线齿轮的**草图闭合性**诊断。
# 官方依据: `C:\swapi\types\ISketchManager\CreateEquationSpline2.md`
#         `C:\swapi\types\ISketch\GetSketchPoints2.md`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402
from scripts import gear_geometry as G                                # noqa: E402


def _seg_info(doc):
    """★ 逐段回读类型与端点（★ 原样，★ 不换算）。"""
    out = []
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        for i, s in enumerate(list(C.get_com_member(sk, "GetSketchSegments") or [])):
            row = {"i": i}
            try:
                row["type"] = int(C.get_com_member(s, "GetType"))
            except Exception:                                             # noqa: BLE001
                pass
            for m in ("GetStartPoint2", "GetEndPoint2"):
                try:
                    pt = C.get_com_member(s, m)
                    arr = list(pt) if pt is not None else None
                    if arr and len(arr) >= 2:
                        row[m] = [float(arr[0]), float(arr[1])]
                except Exception:                                         # noqa: BLE001
                    pass
            out.append(row)
    except Exception as exc:                                              # noqa: BLE001
        out.append({"error": "%s: %s" % (type(exc).__name__, str(exc)[:120])})
    return out


def _sketch_points(doc):
    """★ `ISketch::GetSketchPoints2` 的个数与坐标。"""
    res = {"count": None, "points": []}
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        for g in ("GetSketchPointsCount2", "GetSketchPointsCount"):
            try:
                res["count"] = int(C.get_com_member(sk, g))
                break
            except Exception:                                             # noqa: BLE001
                pass
        pts = list(C.get_com_member(sk, "GetSketchPoints2") or [])
        for pt in pts[:8]:
            try:
                arr = list(pt)
                res["points"].append([round(float(arr[0]), 6), round(float(arr[1]), 6)])
            except Exception:                                             # noqa: BLE001
                try:
                    res["points"].append([round(float(C.get_com_member(pt, "X")), 6),
                                          round(float(C.get_com_member(pt, "Y")), 6)])
                except Exception:                                         # noqa: BLE001
                    pass
    except Exception as exc:                                              # noqa: BLE001
        res["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
    return res


def main() -> int:
    spec = G.GearSpec(module_mm=1.0, teeth=20, face_width_mm=10.0,
                      pressure_angle_deg=20.0, bore_diameter_mm=8.0)
    geo = G.calculate_gear_geometry(spec)
    rep = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "_": "★ 诊断真曲线齿轮草图的闭合性", "cases": []}
    sw, _ = C.connect_solidworks(wait_seconds=30)

    def run(tag, draw):
        doc = None
        row = {"tag": tag}
        try:
            doc = C.new_document(sw, "part")
            P.start_sketch(doc, plane_name="Front Plane")
            draw(doc)
            row["segments"] = _seg_info(doc)
            row["sketch_points"] = _sketch_points(doc)
            #: ★★ 判据：★ 首尾端点闭合吗？
            segs = [s for s in row["segments"] if "GetStartPoint2" in s and "GetEndPoint2" in s]
            if segs:
                ends = []
                for s in segs:
                    ends.append((tuple(round(v, 9) for v in s["GetStartPoint2"]),
                                 tuple(round(v, 9) for v in s["GetEndPoint2"])))
                #: ★ 每个端点被用了几次（★ 闭合轮廓每个端点恰用 2 次）
                cnt = {}
                for a, b in ends:
                    cnt[a] = cnt.get(a, 0) + 1
                    cnt[b] = cnt.get(b, 0) + 1
                row["endpoint_use_counts"] = sorted(cnt.values())
                row["closed_profile"] = all(v == 2 for v in cnt.values()) and len(cnt) >= 3
            try:
                P.end_sketch(doc)
            except Exception:                                             # noqa: BLE001
                pass
            #: ★★ 试拉伸（★ 判据：★ 返回非 None）
            try:
                sk = C.get_com_member(doc, "GetActiveSketch2")
                sk_name = str(C.get_com_member(sk, "Name") or "") if sk else ""
            except Exception:                                             # noqa: BLE001
                sk_name = "草图1"
            try:
                feat = P.extrude_boss(doc, sk_name, spec.face_width_mm / 1000.0)
                row["extrude_ok"] = feat is not None
            except Exception as exc:                                      # noqa: BLE001
                row["extrude_ok"] = False
                row["extrude_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
        except Exception as exc:                                          # noqa: BLE001
            row["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
        finally:
            if doc is not None:
                try:
                    t = str(C.get_com_member(doc, "GetTitle") or "")
                    if t:
                        C.get_com_member(sw, "CloseDoc", t)
                except Exception:                                         # noqa: BLE001
                    pass
        return row

    #: ★ ① 只画**渐开线**（★ 单条开放曲线）
    def d1(doc):
        sm = C.get_com_member(doc, "SketchManager")
        C.get_com_member(sm, "CreateEquationSpline2",
                         G.involute_x_expression(geo.base_diameter_mm / 2.0),
                         G.involute_y_expression(geo.base_diameter_mm / 2.0),
                         "", "%r" % geo.t_root, "%r" % geo.t_tip,
                         False, 0.0, 0.0, 0.0, True, True)
    rep["cases"].append(run("① 单条渐开线", d1))

    #: ★ ② 渐开线 + 摆线（★ 两条开放曲线，★ 端点不相接）
    def d2(doc):
        sm = C.get_com_member(doc, "SketchManager")
        C.get_com_member(sm, "CreateEquationSpline2",
                         G.involute_x_expression(geo.base_diameter_mm / 2.0),
                         G.involute_y_expression(geo.base_diameter_mm / 2.0),
                         "", "%r" % geo.t_root, "%r" % geo.t_tip,
                         False, 0.0, 0.0, 0.0, True, True)
        hf = G.DEDENDUM_COEFF * spec.module_mm
        rho = G.TOOL_TIP_RADIUS_COEFF * spec.module_mm
        C.get_com_member(sm, "CreateEquationSpline2",
                         G.trochoid_x_expression(pitch_radius_mm=geo.pitch_diameter_mm / 2.0,
                                                 dedendum_mm=hf, tool_tip_radius_mm=rho),
                         G.trochoid_y_expression(pitch_radius_mm=geo.pitch_diameter_mm / 2.0,
                                                 dedendum_mm=hf, tool_tip_radius_mm=rho),
                         "", "0", "0.235196202",
                         False, 0.0, 0.0, 0.0, True, True)
    rep["cases"].append(run("② 渐开线 + 摆线", d2))

    #: ★ ③ 完整闭合轮廓：★ 两条曲线 + **用直线补上**（★ 只为验证"闭合才能拉伸"）
    def d3(doc):
        sm = C.get_com_member(doc, "SketchManager")
        C.get_com_member(sm, "CreateEquationSpline2",
                         G.involute_x_expression(geo.base_diameter_mm / 2.0),
                         G.involute_y_expression(geo.base_diameter_mm / 2.0),
                         "", "%r" % geo.t_root, "%r" % geo.t_tip,
                         False, 0.0, 0.0, 0.0, True, True)
        hf = G.DEDENDUM_COEFF * spec.module_mm
        rho = G.TOOL_TIP_RADIUS_COEFF * spec.module_mm
        C.get_com_member(sm, "CreateEquationSpline2",
                         G.trochoid_x_expression(pitch_radius_mm=geo.pitch_diameter_mm / 2.0,
                                                 dedendum_mm=hf, tool_tip_radius_mm=rho),
                         G.trochoid_y_expression(pitch_radius_mm=geo.pitch_diameter_mm / 2.0,
                                                 dedendum_mm=hf, tool_tip_radius_mm=rho),
                         "", "0", "0.235196202",
                         False, 0.0, 0.0, 0.0, True, True)
        #: ★ 用圆闭合（★ 齿根圆 —— 轮廓会自交，★ 但能验证"闭合"这个前提）
        P.sketch_circle(doc, 0.0, 0.0, geo.root_diameter_mm / 2.0)
    rep["cases"].append(run("③ 两条曲线 + 齿根圆", d3))

    p = R / "output" / "_probe_gear_sketch_diag.json"
    p.write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    for c in rep["cases"]:
        print("  ★ %-24s 段数=%-4s 闭合=%-6s 拉伸=%s"
              % (c.get("tag"), len(c.get("segments") or []), c.get("closed_profile"),
                 c.get("extrude_ok")))
        if c.get("extrude_err"):
            print("        err=%s" % c["extrude_err"][:130])
        if c.get("error"):
            print("        err=%s" % c["error"][:130])
        for s in (c.get("segments") or [])[:3]:
            print("         seg%d type=%s start=%s end=%s"
                  % (s.get("i"), s.get("type"),
                     [round(v, 6) for v in s.get("GetStartPoint2", [])],
                     [round(v, 6) for v in s.get("GetEndPoint2", [])]))
    print("  产物：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
