"""★ 真机：★ **用 `ISketch::MergePoints` 合并亚微米缝** ⇒ 让真曲线齿廓闭合可拉伸。

★★★★★ **业主原话**：「★ **像什么直接用直线去逼近曲线这种野路子，你就全部都改掉**」✓

★★★ **真因（★ 真机裁决 · ★ 数值铁证）**：
  ★ 6 条**真曲线**的端点**不严格重合** —— 实测间距
    ★★ **0.695 ~ 1.72 µm**（★ 证据 `output/_probe_gear_endpoints.json`）✗
  ★★★ **为什么**：★ `CreateEquationSpline2` **按自己的精度离散**方程 ⇒
    ★ 曲线端点落在解析位置附近 **亚微米**处，★ 而 SolidWorks 的**合并容差**比它小 ⇒
    ★★ **有的接缝自动合并了（★ 6 条变 5 段）、有的没合** ⇒ **轮廓不闭合** ⇒ 拉伸回 `None` ✗

★★★ **规范修法（★ 官方入口 · ★ 不是我发明的）**：
  ★ `ISketch::MergePoints(Distance)` —— 官方逐字：
    ★★ **"Merges sketch points within a specified distance."** ✓
  ★ 这正是为「**点之间有微小缝**」这种情况准备的官方 API ✓

★ 判据：★ 合并后 **段数 = 6**（★ 每条曲线各成一段、且首尾相接）+ ★ **拉伸返回非 None** ✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_gear_merge_points.py
# 定位:   ★ 业主 2026-10-10「方法要规范」—— ★ 真曲线齿廓的**闭合**（★ 官方 `MergePoints`）。
# 官方依据: `C:\swapi\types\ISketch\MergePoints.md`
#         （★ 逐字：`System.bool MergePoints(System.double Distance)`；
#          ★ Remarks：★ "Merges sketch points within a specified distance."）
#         `C:\swapi\types\ISketchManager\CreateEquationSpline2.md`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
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


def _counts(doc):
    out = {}
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        out["segments"] = len(list(C.get_com_member(sk, "GetSketchSegments") or []))
    except Exception:                                                     # noqa: BLE001
        pass
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        pts = list(C.get_com_member(sk, "GetSketchPoints2") or [])
        out["points"] = len(pts)
    except Exception:                                                     # noqa: BLE001
        pass
    return out


def _main() -> int:
    spec = G.GearSpec(module_mm=1.0, teeth=20, face_width_mm=10.0,
                      pressure_angle_deg=20.0, bore_diameter_mm=8.0)
    geo = G.calculate_gear_geometry(spec)
    curves, meta = tooth_curves(spec, geo)
    rep = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "_": "★ MergePoints 合并亚微米缝 ⇒ 真曲线齿廓闭合",
           "tooth_meta": meta, "cases": []}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    #: ★★ 三格：★ 不合并（对照）· ★ 合并 1 µm · ★ 合并 10 µm
    for tag, dist in (("① 不合并（对照）", None),
                      ("② MergePoints(1e-6 m = 1 µm)", 1.0e-6),
                      ("③ MergePoints(1e-5 m = 10 µm)", 1.0e-5)):
        doc = None
        row = {"tag": tag, "distance_m": dist}
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
                except Exception:                                         # noqa: BLE001
                    pass
            row["curves_ok"] = ok
            row["before"] = _counts(doc)
            if dist is not None:
                try:
                    sk = C.get_com_member(doc, "GetActiveSketch2")
                    row["merge_returned"] = bool(C.get_com_member(sk, "MergePoints", dist))
                except Exception as exc:                                  # noqa: BLE001
                    row["merge_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:110])
            row["after"] = _counts(doc)
            try:
                sk = C.get_com_member(doc, "GetActiveSketch2")
                row["constrained_status"] = int(C.get_com_member(sk, "GetConstrainedStatus"))
            except Exception:                                             # noqa: BLE001
                pass
            try:
                P.end_sketch(doc)
                f = P.extrude_boss(doc, "草图1", 0.010)
                row["extrude_ok"] = f is not None
                if f is not None:
                    try:
                        mp = C.get_com_member(C.get_com_member(doc, "Extension"),
                                              "CreateMassProperty")
                        row["volume_mm3"] = float(C.get_com_member(mp, "Volume")) * 1e9
                    except Exception:                                     # noqa: BLE001
                        pass
            except Exception as exc:                                      # noqa: BLE001
                row["extrude_ok"] = False
                row["extrude_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
        except Exception as exc:                                          # noqa: BLE001
            row["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        finally:
            if doc is not None:
                try:
                    t = str(C.get_com_member(doc, "GetTitle") or "")
                    if t:
                        C.get_com_member(sw, "CloseDoc", t)
                except Exception:                                         # noqa: BLE001
                    pass
        rep["cases"].append(row)
    p = R / "output" / "_probe_gear_merge_points.json"
    p.write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n",
                 encoding="utf-8")
    for c in rep["cases"]:
        print("  ★ %-30s 曲线=%s 段 %s→%s 点 %s→%s 合并回=%s 拉伸=%s 体积=%s"
              % (c.get("tag"), c.get("curves_ok"),
                 (c.get("before") or {}).get("segments"), (c.get("after") or {}).get("segments"),
                 (c.get("before") or {}).get("points"), (c.get("after") or {}).get("points"),
                 c.get("merge_returned"), c.get("extrude_ok"), c.get("volume_mm3")))
        if c.get("merge_error"):
            print("        merge err: %s" % c["merge_error"])
        if c.get("extrude_err"):
            print("        extrude err: %s" % c["extrude_err"])
        if c.get("error"):
            print("        err: %s" % c["error"])
    print("  产物：%s" % p)
    return 0


def main() -> int:
    try:
        return _main()
    except BaseException:                                                 # noqa: BLE001
        (R / "output" / "_probe_gear_merge_tb.txt").write_text(
            _tb.format_exc(), encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
