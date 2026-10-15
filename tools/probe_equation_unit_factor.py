"""★ 真机：★ **方程式曲线参数式的单位** —— 读回端点，与解析值比。

★★★ **已有线索**（★ `output/_probe_all_parametric_closure.json`）：
  ★ 我写 `x = 0.01·t, y = 0`（★ t: 0→1）⇒ ★★ 拉伸后**体积 0.001 mm³** ⇒
    ★★★ 边长 = **0.1 mm** ⇒ ★ 而我"想表达"10 mm（★ 即 0.01 **米**）✗
  ★★ ⇒ **比值 = 0.1 / 10 = 1/100** —— ★ **既不是 1 也不是 1/1000** ✗
  ★★★ 这不合任何单一单位错 ⇒ **必须直接量**（★ 不猜）

★★ **本探针**：★ 建 `x = A·t, y = 0`（★ t: 0→1），★ **读回草图点**：
  ★ A = 1.0 · ★ A = 0.001 · ★ A = 0.01
  ★★ 判据：★ `x_read / A` 的比值 ⇒ ★ 那就是**单位因子** ✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_equation_unit_factor.py
# 定位:   ★ 业主 2026-10-10「方法要规范」—— ★ 判**参数式**方程式曲线的单位因子。
# 官方依据: `C:\swapi\types\ISketchManager\CreateEquationSpline2.md`
#         `C:\swapi\types\ISketch\GetSketchPoints2.md`
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
R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402


def _main() -> int:
    rep = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "_": "★ 方程式曲线单位因子：★ 读回端点 ÷ 表达式系数", "cases": []}
    sw, _ = C.connect_solidworks(wait_seconds=30)

    def run(tag, ax, ay, t1, *, parametric):
        doc = None
        row = {"tag": tag, "x_expr": ax, "y_expr": ay, "t": [0, t1],
               "parametric": parametric}
        try:
            doc = C.new_document(sw, "part")
            P.start_sketch(doc, plane_name="Front Plane")
            sm = C.get_com_member(doc, "SketchManager")
            C.get_com_member(sm, "CreateEquationSpline2", ax, ay, "",
                             "0", "%r" % t1, False, 0.0, 0.0, 0.0, True, True)
            pts = []
            try:
                sk = C.get_com_member(doc, "GetActiveSketch2")
                for pt in list(C.get_com_member(sk, "GetSketchPoints2") or []):
                    try:
                        arr = list(pt)
                        pts.append([round(float(arr[0]), 12), round(float(arr[1]), 12)])
                    except Exception:                                     # noqa: BLE001
                        pass
            except Exception as exc:                                      # noqa: BLE001
                row["points_error"] = str(exc)[:90]
            row["points"] = pts
            #: ★★ 取**离原点最远**的点（★ 对应 t 最大）
            if pts:
                far = max(pts, key=lambda p: p[0] ** 2 + p[1] ** 2)
                row["far_point"] = far
                row["max_abs_x"] = abs(far[0])
                row["max_abs_y"] = abs(far[1])
            try:
                sk = C.get_com_member(doc, "GetActiveSketch2")
                row["segments"] = len(list(C.get_com_member(sk, "GetSketchSegments") or []))
            except Exception:                                             # noqa: BLE001
                pass
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
        return row

    #: ★ 参数式：x = A·t（t 0→1）⇒ 末点 x 应 = A（★ 原样读，★ 不换算）
    for A in (1.0, 0.1, 0.01, 0.001):
        rep["cases"].append(run("参数式 x=%.4f*t" % A, "%.9f*t" % A, "0.0", 1.0,
                                parametric=True))
    #: ★ 显式：y = A（x 0→1）⇒ 末点 y 应 = A
    for A in (1.0, 0.01):
        rep["cases"].append(run("显式 y=%.4f" % A, "", "%.9f" % A, 1.0, parametric=False))
    #: ★ 三角函数：x = A·cos(t)（t 0→π）⇒ 末点 x 应 = −A
    rep["cases"].append(run("参数式 x=1.0*cos(t)", "1.0*cos(t)", "0.0", 3.141592653589793,
                            parametric=True))

    p = R / "output" / "_probe_equation_unit_factor.json"
    p.write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n",
                 encoding="utf-8")
    for c in rep["cases"]:
        print("  ★ %-26s 点=%s 段=%s %s"
              % (c.get("tag"), c.get("points"), c.get("segments"),
                 (c.get("error") or c.get("points_error") or "")[:70]))
    print("  产物：%s" % p)
    return 0


def main() -> int:
    try:
        return _main()
    except BaseException:                                                 # noqa: BLE001
        (R / "output" / "_probe_eq_unit_tb.txt").write_text(
            _tb.format_exc(), encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
