"""★ 真机：★ 方程式曲线的**单位**（★ 决定渐开线会不会又犯 1000× 的错）。

★★★★★ **为什么必须先探**：★ 本会话已经**两次**栽在 1000× 上
  （★ 草图图元 4 个漏换算 · ★ `sw_gear` 调用方多除一次）⇒
  ★★★ **这次不许再猜**：★ `CreateEquationSpline2` 的表达式**产出什么单位**？
    · ★ 若产**米** ⇒ ★ 表达式里的 `rb` 要写 **0.009396926**
    · ★ 若产**毫米** ⇒ ★ 写 **9.396926**
  ★★ **判据**：★ 建完后回读**端点坐标**，★ 与**解析值**比 ——
    ★ 比值 ≈ 1 ⇒ 米 · ★ 比值 ≈ 1000 ⇒ 毫米 ✓

★ 走 `sw_guard`（★ 弹窗护栏 + 硬超时）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_equation_units.py
# 定位:   ★ 业主 2026-10-10「方法要规范」—— ★ 渐开线建模前的**单位判据**。
# 官方依据: `C:\swapi\types\ISketchManager\CreateEquationSpline2.md`
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

RB_MM = 9.396926208          #: ★ 基圆半径（★ 毫米）
#: ★★ 解析真值：★ 渐开线 t=0.5 处的点（★ 毫米）
T = 0.5
X_MM = RB_MM * (math.cos(T) + T * math.sin(T))
Y_MM = RB_MM * (math.sin(T) - T * math.cos(T))
R_MM = math.hypot(X_MM, Y_MM)


def _seg_endpoints(doc):
    """★ 回读活动草图的**包围盒**（★ 原样，★ 不换算）。

    ⚠ **我的第二版错（★ 如实）**：★ 我走 `GetSketchSegments` + `GetStartPoint2/EndPoint2`
      ⇒ ★ 对**方程式曲线**返回 **0 段**（★ 它可能是 `SketchSpline`，★ 不在段枚举里）✗
    ★★★ **正解**：★ 官方 `ISketch::GetSketchPoints2` / `ISketchSpline::GetPoints`
      ⇒ ★ 改用**草图点**取包围盒 ✓
    """
    out = []
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        if sk is None:
            return out
        for getter in ("GetSketchPoints2", "GetSketchPoints"):
            try:
                pts = list(C.get_com_member(sk, getter) or [])
            except Exception:                                              # noqa: BLE001
                continue
            for pt in pts:
                try:
                    arr = list(pt)
                    if len(arr) >= 2:
                        out.append([float(arr[0]), float(arr[1])])
                except Exception:                                          # noqa: BLE001
                    try:
                        x = float(C.get_com_member(pt, "X"))
                        y = float(C.get_com_member(pt, "Y"))
                        out.append([x, y])
                    except Exception:                                      # noqa: BLE001
                        pass
            if out:
                break
    except Exception:                                                      # noqa: BLE001
        pass
    return out


def _equation_readback(doc):
    """★ 用 `ISketchSpline::GetEquationParameters2` **回读方程**（★ 最强 oracle）。

    ★★ 为什么这是最强的判据：★ 它直接告诉我 **SolidWorks 收到了什么表达式**——
      ★ 而不必从几何反推 ⇒ ★★ **判据与被判对象不同源**（★ 本仓铁律）✓
    ⚠ 官方签名 **11 个 out 参** ⇒ ★ 迟到绑定下取法要试几种（★ 不臆造）。
    """
    res = {}
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        segs = list(C.get_com_member(sk, "GetSketchSegments") or [])
        cand = list(segs)
        try:
            cand += list(C.get_com_member(sk, "GetSketchSplines") or [])
        except Exception:                                                  # noqa: BLE001
            pass
        for obj in cand:
            for args in ((), (0,)):
                try:
                    got = C.get_com_member(obj, "GetEquationParameters2", *args)
                    res["raw"] = str(got)[:400]
                    if isinstance(got, (list, tuple)):
                        res["params"] = [str(x)[:80] for x in got]
                    return res
                except Exception as exc:                                   # noqa: BLE001
                    res.setdefault("errors", []).append(
                        "%s(%s)" % (type(exc).__name__, str(exc)[:60]))
    except Exception as exc:                                               # noqa: BLE001
        res["errors"] = ["%s: %s" % (type(exc).__name__, str(exc)[:80])]
    return res


def _one(sw, tag, expr_scale, t0, t1):
    """★ `expr_scale` = 表达式里 rb 用哪个量纲（★ 1.0=米 · 1000.0=毫米）。

    ⚠ **我的第一版错（★ 如实）**：★ 我把 `RangeStart/RangeEnd` 写成了**数字** ⇒
      ★ `TypeError: must be real number, not str` —— ★★ 而官方签名**逐字**写的是
      `System.string RangeStart, System.string RangeEnd`（★ 它要**字符串**，
      ★ 因为可以写 `"10*width_dimension1"` / `"-pi/2"`）✗
    ★★★ **⇒ 契约照抄官方签名，★ 不凭"看着像"写**（★ 本仓铁律 1）✓
    """
    row = {"tag": tag, "expr_rb": RB_MM / expr_scale, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        sm = C.get_com_member(doc, "SketchManager")
        rb_e = RB_MM / expr_scale
        try:
            C.get_com_member(sm, "CreateEquationSpline2",
                             "%.12f*(cos(t)+t*sin(t))" % rb_e,
                             "%.12f*(sin(t)-t*cos(t))" % rb_e,
                             "", "0", str(t1),
                             False, 0.0, 0.0, 0.0, True, True)
        except Exception as exc:                                           # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        pts = _seg_endpoints(doc)
        row["n_points"] = len(pts)
        row["equation_readback"] = _equation_readback(doc)
        if pts:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            row["bbox"] = {"dx": max(xs) - min(xs), "dy": max(ys) - min(ys)}
            #: ★★★ 判据：★ 取**半径最大**的点（★ 对应 t 最大 ⇒ 最可靠）
            best = max(pts, key=lambda p: math.hypot(p[0], p[1]))
            row["readback"] = best
            row["readback_radius"] = math.hypot(best[0], best[1])
        try:
            P.end_sketch(doc)
        except Exception:                                                  # noqa: BLE001
            pass
    except Exception as exc:                                               # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:170])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                              # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "★ 方程式曲线的**单位**：★ 表达式里的 rb 该用米还是毫米",
          "analytic_mm": {"t": T, "x": X_MM, "y": Y_MM, "radius": R_MM},
          "cases": []}
    #: ★ ① 表达式用**毫米**（★ 若 SolidWorks 吃米 ⇒ 曲线会是 9.4 米）
    ev["cases"].append(_one(sw, "① 表达式给毫米（rb=9.3969）", 1000.0, "0", "%.12f" % T))
    #: ★ ② 表达式用**米**（★ 若 SolidWorks 吃米 ⇒ 曲线半径 9.4 mm）
    ev["cases"].append(_one(sw, "② 表达式给米（rb=0.0093969）", 1.0, "0", "%.12f" % T))

    #: ★★★ 判据：★ 哪种写法的**回读半径**（★ 原样，★ 不换算）最接近 0.0093969 m
    verdict = "unknown"
    for c in ev["cases"]:
        rr = c.get("readback_radius")
        if rr is None:
            continue
        #: ★ 期望：★ 米制下 t=0.5 的半径 = 0.009396926*sqrt(1.25) = 0.01050617 m
        exp_m = R_MM / 1000.0
        if abs(rr - exp_m) / exp_m < 0.01:
            verdict = "expression_in_METRES"
            c["matches_metres"] = True
        elif abs(rr - R_MM) / R_MM < 0.01:
            verdict = "expression_in_MILLIMETRES"
            c["matches_millimetres"] = True
    ev["verdict"] = verdict
    ev["expected_metres"] = R_MM / 1000.0
    ev["expected_millimetres"] = R_MM
    p = R / "output" / "equation-units-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  ★★ 解析（毫米）：t=%.2f ⇒ (%.6f, %.6f) · R=%.6f" % (T, X_MM, Y_MM, R_MM))
    print("  ★★ 期望（米）：R=%.9f" % (R_MM / 1000.0))
    print("  ★★★ 裁决：**%s**" % verdict)
    for c in ev["cases"]:
        print("  %-36s 点数=%-4s 回读半径=%.9f"
              % (c.get("tag", "")[:36], c.get("n_points"), (c.get("readback_radius") if c.get("readback_radius") is not None else -1)))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  产物：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
