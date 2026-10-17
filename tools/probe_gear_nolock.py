"""★ 真机：★ 闭合齿廓**不用** LockStart/LockEnd 能不能建（★ 只测这一格）。

★★★ **假设**（★ 要证）：★ `LockStart=True, LockEnd=True` 会给曲线两端加**锁定**，
  ★★ 6 条曲线共享端点 ⇒ ★ **锁定 + 自动重合 = 过定义** ✗
  ⇒ ★ 改成 `False, False` ⇒ ★ **不过定义** ✓

★ 判据：★ ① 草图段数 = 6 · ★ ② `GetConstrainedStatus()` 读数 · ★ ③ 拉伸返回非 None ✓
★ 走 `sw_guard`（★ 出现弹窗它会**正确地中止** —— ★ 那本身也是判据）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_gear_nolock.py
# 定位:   ★ 业主 2026-10-10「方法要规范」—— ★ 闭合齿廓的**最小可建形态**判据。
# 官方依据: `C:\swapi\types\ISketchManager\CreateEquationSpline2.md`（★ LockStart/LockEnd）
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
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402
from scripts import gear_geometry as G                                # noqa: E402
from tools.probe_gear_lock_flags import tooth_curves                  # noqa: E402


def _main() -> int:
    spec = G.GearSpec(module_mm=1.0, teeth=20, face_width_mm=10.0,
                      pressure_angle_deg=20.0, bore_diameter_mm=8.0)
    geo = G.calculate_gear_geometry(spec)
    curves = tooth_curves(spec, geo)
    rep = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "_": "★ 闭合齿廓 lock=False/False（★ 最小可建形态）",
           "curve_count": len(curves), "cases": []}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    for tag, ls, le in (("① lock False/False", False, False),):
        doc = None
        row = {"tag": tag, "lock": [ls, le]}
        try:
            doc = C.new_document(sw, "part")
            P.start_sketch(doc, plane_name="Front Plane")
            sm = C.get_com_member(doc, "SketchManager")
            ok = fail = 0
            errs = []
            for name, x, y, t0, t1 in curves:
                try:
                    C.get_com_member(sm, "CreateEquationSpline2", x, y, "",
                                     "%r" % t0, "%r" % t1, False, 0.0, 0.0, 0.0, ls, le)
                    ok += 1
                except Exception as exc:                                  # noqa: BLE001
                    fail += 1
                    errs.append("%s: %s" % (name, str(exc)[:60]))
            row["curves_ok"] = ok
            row["curves_failed"] = fail
            row["curve_errors"] = errs[:3]
            try:
                sk = C.get_com_member(doc, "GetActiveSketch2")
                row["segments"] = len(list(C.get_com_member(sk, "GetSketchSegments") or []))
                row["constrained_status"] = int(C.get_com_member(sk, "GetConstrainedStatus"))
                name = str(C.get_com_member(sk, "Name") or "")
            except Exception as exc:                                      # noqa: BLE001
                row["status_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:90])
                name = "草图1"
            P.end_sketch(doc)
            try:
                feat = P.extrude_boss(doc, name, 0.010)
                row["extrude_ok"] = feat is not None
                if feat is not None:
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
            row["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        finally:
            if doc is not None:
                try:
                    t = str(C.get_com_member(doc, "GetTitle") or "")
                    if t:
                        C.get_com_member(sw, "CloseDoc", t)
                except Exception:                                         # noqa: BLE001
                    pass
        rep["cases"].append(row)
    p = R / "output" / "_probe_gear_nolock.json"
    p.write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n",
                 encoding="utf-8")
    for c in rep["cases"]:
        print("  ★ %-20s 曲线 %s/%s 段=%s 约束状态=%s 拉伸=%s 体积=%s"
              % (c.get("tag"), c.get("curves_ok"),
                 (c.get("curves_ok") or 0) + (c.get("curves_failed") or 0),
                 c.get("segments"), c.get("constrained_status"),
                 c.get("extrude_ok"), c.get("volume_mm3")))
        for e in c.get("curve_errors") or []:
            print("        curve err: %s" % e)
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
        (R / "output" / "_probe_gear_nolock_traceback.txt").write_text(
            _tb.format_exc(), encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
