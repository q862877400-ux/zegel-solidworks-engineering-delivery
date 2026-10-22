"""★ 真机：★ **全参数式正方形的尺度律** —— 直接量出单位因子（★ 不猜）。

★★★ **已有读数**（★ `output/_probe_all_parametric_closure.json`）：
  ★ 4 条参数式曲线（★ `x = 0.01·t` 那种）⇒ ★ 闭合 ✓ · ★ 拉伸 ✓ · ★★ **体积 0.001 mm³**
  ★★ 而**边长应为 10 mm**（★ 若 0.01 是**米**）⇒ ★ 体积应 **1000 mm³** ⇒ **差 1e6** ✗
  ★★★ **⇒ 不猜，直接扫**：★ a = 0.01 / 0.1 / 1.0 / 10.0 ⇒ ★ 读体积 ⇒
    ★★ `体积 ∝ A³` ⇒ ★ 由比例**反解单位因子** ✓

★ 判据：★ 哪一格给出 **1000 mm³**（★ 10×10×10）⇒ ★ 那个 a 就是"10 mm 的米制写法" ✓
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_parametric_scale_law.py
# 定位:   ★ 业主 2026-10-10「方法要规范」—— ★ 参数式曲线的**单位因子**（★ 扫描法）。
# 官方依据: `c_:\swapi\types\ISketchManager\CreateEquationSpline2.md`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ---------------------------------------------------------------------
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

from scripts import sw_connect as c_  # noqa: E402
from scripts import sw_part as p_  # noqa: E402


def _main() -> int:
    rep = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "★ 全参数式正方形的尺度律（★ 反解单位因子）",
        "cases": [],
    }
    sw, _ = c_.connect_solidworks(wait_seconds=30)

    def square(a):
        def draw(doc):
            sm = c_.get_com_member(doc, "SketchManager")
            c_.get_com_member(
                sm,
                "CreateEquationSpline2",
                "%.12f*t" % a,
                "0.0",
                "",
                "0",
                "1",
                False,
                0.0,
                0.0,
                0.0,
                True,
                True,
            )
            c_.get_com_member(
                sm,
                "CreateEquationSpline2",
                "%.12f" % a,
                "%.12f*t" % a,
                "",
                "0",
                "1",
                False,
                0.0,
                0.0,
                0.0,
                True,
                True,
            )
            c_.get_com_member(
                sm,
                "CreateEquationSpline2",
                "%.12f-%.12f*t" % (a, a),
                "%.12f" % a,
                "",
                "0",
                "1",
                False,
                0.0,
                0.0,
                0.0,
                True,
                True,
            )
            c_.get_com_member(
                sm,
                "CreateEquationSpline2",
                "0.0",
                "%.12f-%.12f*t" % (a, a),
                "",
                "0",
                "1",
                False,
                0.0,
                0.0,
                0.0,
                True,
                True,
            )

        return draw

    for a in (0.01, 0.1, 1.0, 10.0):
        doc = None
        row = {"a": a}
        try:
            doc = c_.new_document(sw, "part")
            p_.start_sketch(doc, plane_name="Front Plane")
            square(a)(doc)
            try:
                sk = c_.get_com_member(doc, "GetActiveSketch2")
                row["segments"] = len(
                    list(c_.get_com_member(sk, "GetSketchSegments") or [])
                )
                row["points"] = len(
                    list(c_.get_com_member(sk, "GetSketchPoints2") or [])
                )
            except Exception:  # noqa: BLE001
                pass
            p_.end_sketch(doc)
            f = p_.extrude_boss(doc, "草图1", 0.010)
            row["extrude_ok"] = f is not None
            if f is not None:
                try:
                    mp = c_.get_com_member(
                        c_.get_com_member(doc, "Extension"), "CreateMassProperty"
                    )
                    v = float(c_.get_com_member(mp, "Volume")) * 1e9
                    row["volume_mm3"] = round(v, 9)
                    #: ★★ 反解边长（★ 假设深度 10 mm 对）
                    if v > 0:
                        row["implied_side_mm"] = round((v / 10.0) ** 0.5, 9)
                        row["side_over_A"] = round(row["implied_side_mm"] / a, 6)
                except Exception as exc:  # noqa: BLE001
                    row["mass_error"] = str(exc)[:100]
        except Exception as exc:  # noqa: BLE001
            row["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
        finally:
            if doc is not None:
                try:
                    t = str(c_.get_com_member(doc, "GetTitle") or "")
                    if t:
                        c_.get_com_member(sw, "CloseDoc", t)
                except Exception:  # noqa: BLE001
                    pass
        rep["cases"].append(row)

    p = R / "output" / "_probe_parametric_scale_law.json"
    p.write_text(
        json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  ★ a 扫描（★ 全参数式正方形 · ★ 拉伸 10 mm）：")
    for c in rep["cases"]:
        print(
            "     a=%-8s 段=%-3s 点=%-3s 拉伸=%-6s 体积=%-14s 反解边长=%-10s 边长/a=%s %s"
            % (
                c.get("a"),
                c.get("segments"),
                c.get("points"),
                c.get("extrude_ok"),
                c.get("volume_mm3"),
                c.get("implied_side_mm"),
                c.get("side_over_A"),
                (c.get("error") or c.get("mass_error") or "")[:50],
            )
        )
    print("  产物：%s" % p)
    return 0


def main() -> int:
    try:
        return _main()
    except BaseException:  # noqa: BLE001
        (R / "output" / "_probe_scale_tb.txt").write_text(
            _tb.format_exc(), encoding="utf-8"
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
