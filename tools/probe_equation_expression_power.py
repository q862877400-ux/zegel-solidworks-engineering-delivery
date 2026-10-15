"""★ 真机：★ `CreateEquationSpline2` 的**表达式能力**（★ 决定根过渡曲线能不能用真 trochoid）。

★★★ **为什么要探**：★ 业主令「**方法要按机械工程的规范做法**」——
  ★ 直齿轮的**根过渡曲线**在标准上是**摆线（trochoid）**（★ 由齿条刀具顶圆包络生成）✓
  ★ 它的**闭合式**含 **`sqrt`** 与**长表达式**：
  ```
  ★ a = h_f − ρ（★ 齿根高 − 刀顶圆角半径）
  ★ x(φ) = (r−h_f+ρ)cos φ + rφ sin φ + ρ(−a cos φ + rφ sin φ)/sqrt(a²+r²φ²)
  ★ y(φ) = (r−h_f+ρ)sin φ − rφ cos φ + ρ(−a sin φ − rφ cos φ)/sqrt(a²+r²φ²)
  ```
  ★★ 而官方 Remarks **只举了 `sin(t)`/`cos(t)`/`exp(x)`** ⇒
    ★★★ **`sqrt`/`^`/长表达式支不支持，必须真机判**（★ 不臆造）✓

★ 判据：★ **草图段数增加**（★ 事实 436）—— ★ 不看返回值（★ 事实 40）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_equation_expression_power.py
# 定位:   ★ 业主 2026-10-10 指令「方法要规范」—— ★ 判方程式曲线的**表达力边界**。
# 官方依据: `C:\swapi\types\ISketchManager\CreateEquationSpline2.md`（★ 11 参 + Remarks）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
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


def _seg_count(doc):
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        return len(list(C.get_com_member(sk, "GetSketchSegments") or [])) if sk else -1
    except Exception:                                                     # noqa: BLE001
        return -1


def _one(sw, tag, xexpr, yexpr, t0, t1):
    row = {"tag": tag, "ok": False, "x_len": len(xexpr), "y_len": len(yexpr)}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        sm = C.get_com_member(doc, "SketchManager")
        before = _seg_count(doc)
        try:
            C.get_com_member(sm, "CreateEquationSpline2",
                             xexpr, yexpr, "", t0, t1, False, 0.0, 0.0, 0.0, True, True)
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        after = _seg_count(doc)
        row["seg"] = [before, after]
        row["ok"] = bool(after >= 0 and before >= 0 and after > before)
        try:
            P.end_sketch(doc)
        except Exception:                                                 # noqa: BLE001
            pass
    except Exception as exc:                                              # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
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
          "_": "★ 方程式曲线的**表达力**（★ sqrt / ^ / 长表达式 / 嵌套）",
          "why": "★ 判「根过渡曲线能不能用真 trochoid」—— ★ 它的闭合式含 sqrt",
          "cases": []}
    #: ★ ① 基线：只 sin/cos（★ 官方例子那类）
    ev["cases"].append(_one(sw, "① 基线 sin/cos", "sin(t)", "cos(t)", "0", "1"))
    #: ★ ② 幂运算 `^`
    ev["cases"].append(_one(sw, "② 幂 ^", "t^2", "t^3", "0", "1"))
    #: ★ ③ 乘法 `*`（★ 上轮已知可）
    ev["cases"].append(_one(sw, "③ 乘法 *", "t*sin(t)", "t*cos(t)", "0", "1"))
    #: ★ ④ `sqrt`（★ 关键）
    ev["cases"].append(_one(sw, "④ sqrt", "sqrt(t)", "t", "0.01", "1"))
    #: ★ ⑤ sqrt 嵌在分母（★ trochoid 的形态）
    ev["cases"].append(_one(sw, "⑤ sqrt 在分母", "t/sqrt(1+t*t)", "1/sqrt(1+t*t)", "0", "1"))
    #: ★ ⑥ 长表达式（★ 真 trochoid 那种长度）
    ev["cases"].append(_one(
        sw, "⑥ 长表达式（真 trochoid 形态）",
        "9.0*cos(t)+10.0*t*sin(t)+0.38*(-1.0*cos(t)+10.0*t*sin(t))/sqrt(1.0+100.0*t*t)",
        "9.0*sin(t)-10.0*t*cos(t)+0.38*(-1.0*sin(t)-10.0*t*cos(t))/sqrt(1.0+100.0*t*t)",
        "0", "0.5"))
    #: ★ ⑦ `pi` 常量
    ev["cases"].append(_one(sw, "⑦ pi 常量", "cos(pi*t)", "sin(pi*t)", "0", "1"))
    #: ★ ⑧ 加法/减法混合
    ev["cases"].append(_one(sw, "⑧ 加减混合", "t+sin(t)", "t-cos(t)", "0", "1"))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["sqrt_ok"] = bool(ev["cases"][3].get("ok"))
    ev["long_expr_ok"] = bool(ev["cases"][5].get("ok"))
    p = R / "output" / "equation-expression-power-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  ★★ sqrt=%s · 长表达式=%s · 共 %d/%d"
          % (ev["sqrt_ok"], ev["long_expr_ok"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-34s ok=%-6s 段 %s  len=%s/%s"
              % (c.get("tag", "")[:34], c.get("ok"), c.get("seg"),
                 c.get("x_len"), c.get("y_len")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:150])
    print("  产物：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
