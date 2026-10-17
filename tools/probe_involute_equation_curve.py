"""★ 真机：**用方程式驱动曲线画真正的渐开线**（★ 替掉「12 段直线逼近」那个野路子）。

★★★ **业主原话**：「★ **像什么直接用直线去逼近曲线这种野路子，你就全部都改掉**」✓

★★ **本探针要回答一个问题**：
  ★ `ISketchManager.CreateEquationSpline2` 能不能直接建**渐开线参数方程**？
  ★ 渐开线（★ 标准定义，★ 直角坐标）：
      `x(t) = rb·(cos t + t·sin t)`
      `y(t) = rb·(sin t − t·cos t)`
    ★ 其中 `rb` = 基圆半径，`t` = 展开角参数（★ 从 `t_start` 到 `t_tip`）✓
  ★★ 官方 `CreateEquationSpline2.md` 的 Remarks 只举了 `sin(t)`/`cos(t)`/`exp(x)` ⇒
    ★ **乘法/加法/嵌套是否支持，必须真机判**（★ 铁律：查不到就实测，不臆造）✓

★ 判据（★ 规则 6 + 事实 436）：★ **草图段数增加**（★ 一条方程式曲线 ⇒ 段 +1）——
  ★★ 而**不是**「返回了非 None」（★ 事实 40：返回值不可靠）✓

★ 全程走 `tools/sw_guard.py`（★ 弹窗护栏 + 硬超时）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_involute_equation_curve.py
# 定位:   ★ 业主 2026-10-10 指令「方法要按机械工程的规范做法」——
#         ★ 渐开线**必须是真曲线**，★ 不是 12 段折线。
# 官方依据: `C:\swapi\types\ISketchManager\CreateEquationSpline2.md`（★ 11 参签名 + Remarks）
#         `C:\swapi\examples\Create_Equation-driven_Curve_Example_VB.md`（★ 调用序）
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
R = Path(Path(__file__).resolve().parents[1])
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
    row = {"tag": tag, "x": xexpr, "y": yexpr, "range": [t0, t1], "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        sm = C.get_com_member(doc, "SketchManager")
        before = _seg_count(doc)
        row["seg_before"] = before
        try:
            #: ★ **11 参**（★ 顺序照官方签名）
            ret = C.get_com_member(sm, "CreateEquationSpline2",
                                   xexpr, yexpr, "", t0, t1,
                                   False, 0.0, 0.0, 0.0, True, True)
            row["returned"] = type(ret).__name__ if ret is not None else "None"
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
        after = _seg_count(doc)
        row["seg_after"] = after
        row["new_segments"] = (after - before) if (after >= 0 and before >= 0) else None
        row["ok"] = bool(row["new_segments"] and row["new_segments"] > 0)
        #: ★★ 若是样条，★ 取回它的方程参数（★ 官方 `ISketchSpline::GetEquationParameters2`）——
        #:   ★ 那能证明「SolidWorks 认了这条方程」，★ 而不只是「画了点什么」✓
        try:
            sk = C.get_com_member(doc, "GetActiveSketch2")
            segs = list(C.get_com_member(sk, "GetSketchSegments") or [])
            if segs:
                sp = segs[0]
                got = C.get_com_member(sp, "GetEquationParameters2")
                row["equation_readback"] = str(got)[:220]
        except Exception as exc:                                          # noqa: BLE001
            row["readback_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
        try:
            P.end_sketch(doc)
        except Exception:                                                 # noqa: BLE001
            pass
    except Exception as exc:                                              # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:190])
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
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "★ 渐开线**真曲线**探针：`CreateEquationSpline2` 能否直接建渐开线参数方程",
        "why": "★ 业主令：★ 「像什么直接用直线去逼近曲线这种野路子，你就全部都改掉」",
        "official": ("`CreateEquationSpline2.md`：11 参；Remarks 显式曲线给 XExpression=\"\"、"
                     "参数曲线两个都给 t 的表达式；★ 官方例子只举 sin/cos/exp"),
        "involute_definition": {
            "x(t)": "rb*(cos(t) + t*sin(t))",
            "y(t)": "rb*(sin(t) - t*cos(t))",
            "note": "★ 标准渐开线（★ 直角坐标）；★ rb = 基圆半径；★ t = 展开角参数",
        },
        "cases": [],
    }
    RB = 9.396926  #: ★ 模数 1 · 齿数 20 · 20° ⇒ rb = m·z/2·cos20° = 10·0.9396926
    #: ★ ① **渐开线参数方程**（★ 本探针的主角）
    ev["cases"].append(_one(sw, "★ **渐开线** x=rb(cos t+t sin t) · y=rb(sin t−t cos t)",
                            "%.7f*(cos(t)+t*sin(t))" % RB,
                            "%.7f*(sin(t)-t*cos(t))" % RB,
                            "0", "0.6"))
    #: ★ ② **对照：乘法是否支持**（★ 最简形式）
    ev["cases"].append(_one(sw, "对照：**乘法** x=t*sin(t)", "t*sin(t)", "t*cos(t)", "0", "1"))
    #: ★ ③ **对照：只有 sin/cos**（★ 官方例子那种，★ 应当成功）
    ev["cases"].append(_one(sw, "对照：官方例子 x=sin(t) y=cos(t)", "sin(t)", "cos(t)", "0", "6.283185307179586"))
    #: ★ ④ **对照：纯数字常量表达式**（★ 最保守）
    ev["cases"].append(_one(sw, "对照：显式 y=exp(x)（X 给 \"\"）", "", "exp(x)", "-1", "1"))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["involute_ok"] = bool(ev["cases"] and ev["cases"][0].get("ok"))
    ev["verdict"] = "involute_equation_%s" % ("OK" if ev["involute_ok"] else "FAILED")
    p = R / "output" / "involute-equation-curve-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  ★★ 渐开线方程式曲线：**%s**" % ev["verdict"])
    for c in ev["cases"]:
        print("  %-52s ok=%-6s 段 %s → %s（增 %s）回=%s"
              % (c.get("tag", "")[:52], c.get("ok"), c.get("seg_before"),
                 c.get("seg_after"), c.get("new_segments"), c.get("returned")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:150])
        if c.get("equation_readback"):
            print("        方程回读=%s" % str(c["equation_readback"])[:130])
    print("  产物：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
