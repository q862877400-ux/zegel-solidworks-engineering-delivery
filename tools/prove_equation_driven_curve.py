"""★ 真机：**方程式驱动的曲线** —— `ISketchManager.CreateEquationSpline2`（11 参）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_equation_driven_curve.py
# 定位:   ★ 2026-10-03（轮 581）★ 照新纪律（**官方文档是第 0 步**）攻台账「方程式驱动
#           的曲线」。
#
#   ★★ **来源是官方的两页**：
#     · `C:\swapi\types\ISketchManager\CreateEquationSpline.md` \u9010\u5b57\uff1a
#       **"Obsolete. Superseded by `ISketchManager::CreateEquationSpline2`."** \u26a0
#       \uff08\u2605 \u540c\u7406 `CreateSplinesByEqnParams` \u21d2 `...2`\uff09
#     · `CreateEquationSpline2.md` \u7684**\u5b8c\u6574\u7b7e\u540d\u4e0e Remarks**\uff1a
#       ```
#       SketchSpline CreateEquationSpline2(string XExpression, string YExpression,
#           string ZExpression, string RangeStart, string RangeEnd, bool IsAngleRange,
#           double RotationAngle, double XOffset, double YOffset,
#           bool LockStart, bool LockEnd)                     \u2190 **11 \u53c2**
#
# \u2605 **\u663e\u5f0f\u66f2\u7ebf\uff08\u53ea\u6709 2D\uff09 y=f(x)**\uff1a**XExpressi
# on \u7ed9 `""`**\uff1b
# YExpression = \u4ee5 x \u8868\u8fbe\u7684\u51fd\u6570\uff08\u2605 \u4f8b\u5b50 `y=exp(
# x)`\uff09
# \u2605 **\u53c2\u6570\u66f2\u7ebf**\uff1aXExpression = x \u5173\u4e8e t\uff08\u2605 \u
# 4f8b `x=sin(t)`\uff09\uff1b
#          YExpression = y \u5173\u4e8e t\uff08\u2605 `y=cos(t)`\uff09
# \u2605 RangeStart/RangeEnd = x\uff08\u663e\u5f0f\uff09\u6216 t\uff08\u53c2\u6570\uff09
# \u7684\u8303\u56f4
# \u2605 IsAngleRange \u00b7 RotationAngle(rad) \u00b7 XOffset \u00b7 YOffset \u00b7 Loc
# kStart \u00b7 LockEnd
#       ```
#
#   ★ 判据（★ 规则 6 + 事实 436）：**草图段数增加**（★ 一条方程式曲线 ⇒ 段 +1）。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 三格：显式 / 参数 / 对照（坏表达式）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402


def _seg_count(doc):
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        return len(list(C.get_com_member(sk, "GetSketchSegments") or [])) if sk else -1
    except Exception:  # noqa: BLE001
        return -1


def _one(sw, tag, args):
    row = {"tag": tag, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        sm = C.get_com_member(doc, "SketchManager")
        before = _seg_count(doc)
        row["seg_before"] = before
        ret = None
        try:
            #: \u2605 **11 \u53c2**\uff08\u2605 \u987a\u5e8f\u7167\u5b98\u65b9\u7b7e\u54
            #: 0d\uff09
            ret = C.get_com_member(sm, "CreateEquationSpline2", *args)
            row["returned"] = type(ret).__name__ if ret is not None else "None"
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = _seg_count(doc)
        row["seg_after"] = after
        row["new_segments"] = (after - before) if (after >= 0 and before >= 0) else None
        row["ok"] = bool(row["new_segments"] and row["new_segments"] > 0)
        try:
            P.end_sketch(doc)
        except Exception:  # noqa: BLE001
            pass
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:170])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u65b9\u7a0b\u5f0f\u9a71\u52a8\u7684\u66f2\u7ebf\uff1a`ISketchManager.CreateEquationSpline2`\uff08**11 \u53c2**\uff09",
        "official": "`CreateEquationSpline.md` \u9010\u5b57\uff1aObsolete. Superseded by CreateEquationSpline2\uff1b"
        'Remarks\uff1a\u663e\u5f0f\u66f2\u7ebf\u7ed9 XExpression=""\u3001YExpression \u4ee5 x \u8868\u8fbe\uff1b'
        "\u53c2\u6570\u66f2\u7ebf\u4e24\u4e2a\u90fd\u7ed9 t \u7684\u8868\u8fbe\u5f0f",
        "cases": [],
    }
    #: \u2605 \u663e\u5f0f\uff1a`y = exp(x)`\uff0c\u2605 XExpression = ""\uff08\u2605 \u
    #: 5b98\u65b9\u8bf4\u7684\uff09
    ev["cases"].append(
        _one(
            sw,
            '\u2605 **\u663e\u5f0f** y=exp(x)\uff08X\u7ed9 ""\uff09',
            ("", "exp(x)", "", "-1", "1", False, 0.0, 0.0, 0.0, True, True),
        )
    )
    #: \u2605 \u53c2\u6570\uff1a`x=sin(t)` \u00b7 `y=cos(t)`\uff08\u2605 \u5b98\u65b9\u4
    #: f8b\u5b50\uff09
    ev["cases"].append(
        _one(
            sw,
            "\u2605 **\u53c2\u6570** x=sin(t) y=cos(t)",
            (
                "sin(t)",
                "cos(t)",
                "",
                "0",
                "6.283185307179586",
                False,
                0.0,
                0.0,
                0.0,
                True,
                True,
            ),
        )
    )
    #: \u2605 \u5bf9\u7167\uff1a\u574f\u8868\u8fbe\u5f0f
    ev["cases"].append(
        _one(
            sw,
            "\u5bf9\u7167\uff1a**\u574f\u8868\u8fbe\u5f0f** y=zzz(x)",
            ("", "zzz(x)", "", "-1", "1", False, 0.0, 0.0, 0.0, True, True),
        )
    )
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "equation_curve_%d_of_%d" % (ev["passed"], ev["total"])
    p = R / "output" / "equation-driven-curve-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u5224\u522b\uff1a**%s**" % ev["verdict"])
    for c in ev["cases"]:
        print(
            "  %-42s ok=%-6s \u6bb5 %s \u2192 %s\uff08\u589e %s\uff09\u56de=%s"
            % (
                c.get("tag"),
                c.get("ok"),
                c.get("seg_before"),
                c.get("seg_after"),
                c.get("new_segments"),
                c.get("returned"),
            )
        )
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
