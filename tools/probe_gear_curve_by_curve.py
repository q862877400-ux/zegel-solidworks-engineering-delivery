"""★ 真机：★ 逐条曲线**后**数段数 —— 找出那 6 条里哪一条没进去。

★★ 读数（★ `_probe_gear_tooth_pattern.json`）：★ 曲线 ok=**6/6**，
  ★★ 而 `GetSketchSegments` = **5** ⇒ ★ **有一条没成段**（★ 或被合并）✗
★ 判据：★ 逐条累加段数，★ 找出"加了但段数没涨"的那条 ✓
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_gear_curve_by_curve.py
# 定位:   ★ 业主 2026-10-10「方法要规范」—— ★ 定位"6 条曲线只成 5 段"。
# 官方依据: `c:\swapi\types\ISketchManager\CreateEquationSpline2.md`
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
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import gear_geometry as g  # noqa: E402
from scripts import sw_connect as c  # noqa: E402
from scripts import sw_part as P  # noqa: E402
from tools.probe_gear_tooth_pattern2 import tooth_curves  # noqa: E402


def _main() -> int:
    spec = g.GearSpec(
        module_mm=1.0,
        teeth=20,
        face_width_mm=10.0,
        pressure_angle_deg=20.0,
        bore_diameter_mm=8.0,
    )
    geo = g.calculate_gear_geometry(spec)
    curves, meta = tooth_curves(spec, geo)
    rep = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "★ 逐条曲线数段数（★ 找出漏掉的那条）",
        "rows": [],
    }
    sw, _ = c.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = c.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        sm = c.get_com_member(doc, "SketchManager")

        def segs():
            try:
                sk = c.get_com_member(doc, "GetActiveSketch2")
                return len(list(c.get_com_member(sk, "GetSketchSegments") or []))
            except Exception:  # noqa: BLE001
                return -1

        prev = segs()
        rep["initial_segments"] = prev
        for name, x, y, t0, t1 in curves:
            err = None
            try:
                c.get_com_member(
                    sm,
                    "CreateEquationSpline2",
                    x,
                    y,
                    "",
                    "%r" % t0,
                    "%r" % t1,
                    False,
                    0.0,
                    0.0,
                    0.0,
                    True,
                    True,
                )
            except Exception as exc:  # noqa: BLE001
                err = "%s: %s" % (type(exc).__name__, str(exc)[:90])
            now = segs()
            rep["rows"].append(
                {
                    "name": name,
                    "before": prev,
                    "after": now,
                    "delta": now - prev,
                    "error": err,
                    "x_head": x[:56],
                    "y_head": y[:56],
                    "t": [t0, t1],
                }
            )
            prev = now
        rep["final_segments"] = prev
        #: ★★ 试拉伸
        try:
            sk = c.get_com_member(doc, "GetActiveSketch2")
            rep["constrained_status"] = int(
                c.get_com_member(sk, "GetConstrainedStatus")
            )
        except Exception as exc:  # noqa: BLE001
            rep["constrained_status_error"] = str(exc)[:90]
        try:
            P.end_sketch(doc)
            f = P.extrude_boss(doc, "草图1", 0.010)
            rep["extrude_ok"] = f is not None
        except Exception as exc:  # noqa: BLE001
            rep["extrude_ok"] = False
            rep["extrude_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
    except Exception as exc:  # noqa: BLE001
        rep["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if doc is not None:
            try:
                t = str(c.get_com_member(doc, "GetTitle") or "")
                if t:
                    c.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    p = R / "output" / "_probe_gear_curve_by_curve.json"
    p.write_text(
        json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  ★ 初始段数 = %s" % rep.get("initial_segments"))
    for r in rep["rows"]:
        print(
            "  %-14s %s → %s（Δ%s）%s"
            % (r["name"], r["before"], r["after"], r["delta"], (r["error"] or "")[:70])
        )
    print(
        "  ★ 末段数 = %s · 约束状态 = %s"
        % (rep.get("final_segments"), rep.get("constrained_status"))
    )
    print(
        "  ★ 拉伸 = %s %s"
        % (rep.get("extrude_ok"), (rep.get("extrude_err") or "")[:110])
    )
    print("  产物：%s" % p)
    return 0


def main() -> int:
    try:
        return _main()
    except BaseException:  # noqa: BLE001
        (R / "output" / "_probe_gear_cbc_traceback.txt").write_text(
            _tb.format_exc(), encoding="utf-8"
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
