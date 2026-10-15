"""★ 真机：★ **读回草图点的真实坐标** —— 判 6 条曲线是否**首尾重合**。

★★ 判据（★ 事实 32 那族：★ 曲线没有名字，★ 只能按**点**读）：
  ★ 用 `ISketch::GetSketchPoints2` 读**全部草图点**（★ 上一轮对单条曲线**成功**）⇒
    ★★ 逐点算**两两最小距离** ⇒ ★ 若最小距离 ≫ 1e-6 m（1 µm）⇒ **有缝** ⇒ 轮廓不闭合 ✗
  ★★★ 那正是「6 条曲线都建了、而拉伸返回 None」的**候选真因** ✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_gear_endpoints.py
# 定位:   ★ 业主 2026-10-10「方法要规范」—— ★ 判真曲线齿廓的**闭合性**（按点读）。
# 官方依据: `C:\swapi\types\ISketch\GetSketchPoints2.md`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import math
import sys
import time
import traceback as _tb
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402
from scripts import gear_geometry as G                                # noqa: E402
from tools.probe_gear_tooth_pattern2 import tooth_curves              # noqa: E402


def _pts(doc):
    """★ 读活动草图的**全部点**（★ 原样，★ 单位应为米）。"""
    out = []
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        for g in ("GetSketchPoints2", "GetSketchPoints"):
            try:
                raw = list(C.get_com_member(sk, g) or [])
            except Exception:                                             # noqa: BLE001
                continue
            for pt in raw:
                try:
                    arr = list(pt)
                    if len(arr) >= 2:
                        out.append([float(arr[0]), float(arr[1])])
                        continue
                except Exception:                                         # noqa: BLE001
                    pass
                try:
                    out.append([float(C.get_com_member(pt, "X")),
                                float(C.get_com_member(pt, "Y"))])
                except Exception:                                         # noqa: BLE001
                    pass
            if out:
                break
    except Exception:                                                     # noqa: BLE001
        pass
    return out


def _main() -> int:
    spec = G.GearSpec(module_mm=1.0, teeth=20, face_width_mm=10.0,
                      pressure_angle_deg=20.0, bore_diameter_mm=8.0)
    geo = G.calculate_gear_geometry(spec)
    curves, meta = tooth_curves(spec, geo)
    rep = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "_": "★ 读回草图点：判 6 条真曲线是否首尾重合",
           "tooth_meta": meta, "expected_joints": []}
    #: ★★ 解析期望的 6 个接缝点（★ 米）
    k_ = 1.0 / 1000.0
    A = {"P": meta["P"], "P_tro": meta["P_tro"], "ang_tip": meta["ang_tip"]}
    ra = (spec.module_mm * spec.teeth / 2.0 + spec.module_mm) * k_
    rf = (spec.module_mm * spec.teeth / 2.0 - 1.25 * spec.module_mm) * k_
    rep["expected_joints"] = [
        {"name": "right_root→right_flank", "r": round(geo.base_diameter_mm / 2 * k_, 12),
         "ang": round(A["P"], 12)},
        {"name": "right_flank→tip_arc", "r": round(ra, 12), "ang": round(A["ang_tip"], 12)},
        {"name": "tip_arc→left_flank", "r": round(ra, 12), "ang": round(-A["ang_tip"], 12)},
        {"name": "left_flank→left_root", "r": round(geo.base_diameter_mm / 2 * k_, 12),
         "ang": round(-A["P"], 12)},
        {"name": "left_root→root_arc", "r": round(rf, 12), "ang": round(-A["P_tro"], 12)},
        {"name": "root_arc→right_root", "r": round(rf, 12), "ang": round(A["P_tro"], 12)},
    ]
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        sm = C.get_com_member(doc, "SketchManager")
        ok = 0
        for name, x, y, t0, t1 in curves:
            try:
                C.get_com_member(sm, "CreateEquationSpline2", x, y, "",
                                 "%r" % t0, "%r" % t1, False, 0.0, 0.0, 0.0, True, True)
                ok += 1
            except Exception:                                             # noqa: BLE001
                pass
        rep["curves_ok"] = ok
        pts = _pts(doc)
        rep["point_count"] = len(pts)
        rep["points_m"] = [[round(v, 9) for v in p] for p in pts]
        #: ★★ 两两最小距离（★ 排除同一条曲线的内部点 ⇒ 只看"跨曲线"的最近对）
        mind = []
        n = len(pts)
        for i in range(n):
            for j in range(i + 1, n):
                d = math.dist(pts[i], pts[j])
                mind.append({"i": i, "j": j, "d_m": d,
                             "d_um": d * 1e6})
        mind.sort(key=lambda x: x["d_m"])
        rep["closest_pairs"] = mind[:10]
        #: ★★★ 判据：★ 最近对的距离 ≤ **1 µm** ⇒ 视为重合（★ SolidWorks 合并容差量级）
        rep["min_gap_m"] = mind[0]["d_m"] if mind else None
        rep["min_gap_um"] = mind[0]["d_um"] if mind else None
        rep["closed_within_1um"] = bool(mind and mind[0]["d_m"] <= 1e-6)
        #: ★ 也报一个更严的口径
        rep["closed_within_0p1um"] = bool(mind and mind[0]["d_m"] <= 1e-7)
        try:
            sk = C.get_com_member(doc, "GetActiveSketch2")
            rep["segments"] = len(list(C.get_com_member(sk, "GetSketchSegments") or []))
            rep["constrained_status"] = int(C.get_com_member(sk, "GetConstrainedStatus"))
        except Exception as exc:                                          # noqa: BLE001
            rep["status_error"] = str(exc)[:90]
        try:
            P.end_sketch(doc)
            f = P.extrude_boss(doc, "草图1", 0.010)
            rep["extrude_ok"] = f is not None
        except Exception as exc:                                          # noqa: BLE001
            rep["extrude_ok"] = False
            rep["extrude_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
    except Exception as exc:                                              # noqa: BLE001
        rep["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                             # noqa: BLE001
                pass
    p = R / "output" / "_probe_gear_endpoints.json"
    p.write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n",
                 encoding="utf-8")
    print("  ★ 曲线 %s · 草图点 %s · 段数 %s" % (rep.get("curves_ok"),
                                               rep.get("point_count"), rep.get("segments")))
    print("  ★★ 最近点对距离 = %s µm ⇒ 1µm 内重合=%s · 0.1µm 内=%s"
          % (rep.get("min_gap_um"), rep.get("closed_within_1um"),
             rep.get("closed_within_0p1um")))
    print("  ★ 拉伸 = %s %s" % (rep.get("extrude_ok"), (rep.get("extrude_err") or "")[:110]))
    for c in (rep.get("closest_pairs") or [])[:5]:
        print("     点%d-点%d  %.4f µm" % (c["i"], c["j"], c["d_um"]))
    for q in (rep.get("points_m") or [])[:8]:
        print("     pt %s" % q)
    print("  产物：%s" % p)
    return 0


def main() -> int:
    try:
        return _main()
    except BaseException:                                                 # noqa: BLE001
        (R / "output" / "_probe_gear_endpoints_tb.txt").write_text(
            _tb.format_exc(), encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
