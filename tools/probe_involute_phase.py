"""★ 真机：★ **带相位的渐开线**能不能用一个表达式表达（★ 20 个齿共用一个式子）。

★★★ **为什么要探**：★ 渐开线方程 `x=rb(cos t+t sin t)` 的起点**固定在 (rb, 0)** ⇒
  ★★ 一个 20 齿的齿轮有 20 条齿廓，★ 它们的**相位不同** ⇒
  ★★★ **必须能把相位编进表达式**，★ 否则只能靠 `RotationAngle`（★ 那个我**没能证明它真转**）✗

★★ **两种写法**：
  ★ ① **直接相位**：`x = rb*(cos(t+P) + t*sin(t+P))`（★ 三角里带加法）
  ★ ② **展开相位**（★ 只用 cos/sin/乘/加，★ 已被上一轮证明可用）：
      ★ 令 `A=cos P` · `B=sin P`
      ★ `x = rb*[cos(t)*(A+t*B) + sin(t)*(t*A−B)]`
      ★ `y = rb*[sin(t)*(A+t*B) − cos(t)*(t*A−B)]`
      ★★ 核验：★ `t=0` ⇒ `(rb·cos P, rb·sin P)` —— ★ 落在基圆上、角度 = P ✓

★ 判据：★ **段数增加**（★ 事实 436）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_involute_phase.py
# 定位:   ★ 业主 2026-10-10 指令「方法要规范」—— ★ 判渐开线**相位**怎么表达。
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
    row = {"tag": tag, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        sm = C.get_com_member(doc, "SketchManager")
        before = _seg_count(doc)
        try:
            C.get_com_member(sm, "CreateEquationSpline2", xexpr, yexpr, "",
                             t0, t1, False, 0.0, 0.0, 0.0, True, True)
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = _seg_count(doc)
        row["seg"] = [before, after]
        row["ok"] = bool(after >= 0 and before >= 0 and after > before)
        try:
            P.end_sketch(doc)
        except Exception:                                                 # noqa: BLE001
            pass
    except Exception as exc:                                              # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:170])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                             # noqa: BLE001
                pass
    return row


RB = 9.396926208


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "★ 带**相位**的渐开线表达式（★ 20 齿共用一个式子的前提）", "cases": []}
    PSI = math.radians(9.0)          #: ★ 随便一个相位（齿中心角附近）
    A, B = math.cos(PSI), math.sin(PSI)
    #: ★ ① 直接相位（三角里带加法）
    ev["cases"].append(_one(sw, "① 直接相位 cos(t+P)",
                            "%.9f*(cos(t+%.9f)+t*sin(t+%.9f))" % (RB, PSI, PSI),
                            "%.9f*(sin(t+%.9f)-t*cos(t+%.9f))" % (RB, PSI, PSI),
                            "0", "0.6"))
    #: ★ ② 展开相位（只用 cos/sin/乘/加 —— ★ 保证可用）
    ev["cases"].append(_one(
        sw, "② 展开相位（★ 只用 cos/sin/乘/加）",
        "%.9f*(cos(t)*(%.9f+t*%.9f)+sin(t)*(t*%.9f-%.9f))" % (RB, A, B, A, B),
        "%.9f*(sin(t)*(%.9f+t*%.9f)-cos(t)*(t*%.9f-%.9f))" % (RB, A, B, A, B),
        "0", "0.6"))
    #: ★ ③ 对照：无相位（★ 上一轮已证可）
    ev["cases"].append(_one(sw, "③ 对照：无相位",
                            "%.9f*(cos(t)+t*sin(t))" % RB,
                            "%.9f*(sin(t)-t*cos(t))" % RB, "0", "0.6"))
    #: ★ ④ 摆线齿根（★ 含 sqrt · ★ 长式子）
    r, hf, rho = 10.0, 1.25, 0.38
    a = hf - rho
    ev["cases"].append(_one(
        sw, "④ 摆线齿根（★ 含 sqrt）",
        "%.9f*cos(t)+%.9f*t*sin(t)+%.9f*(-%.9f*cos(t)+%.9f*t*sin(t))/sqrt(%.9f+%.9f*t*t)"
        % (r - hf + rho, r, rho, a, r, a * a, r * r),
        "%.9f*sin(t)-%.9f*t*cos(t)+%.9f*(-%.9f*sin(t)-%.9f*t*cos(t))/sqrt(%.9f+%.9f*t*t)"
        % (r - hf + rho, r, rho, a, r, a * a, r * r),
        "0", "0.25"))
    ev["direct_phase_ok"] = bool(ev["cases"][0].get("ok"))
    ev["expanded_phase_ok"] = bool(ev["cases"][1].get("ok"))
    ev["trochoid_ok"] = bool(ev["cases"][3].get("ok"))
    p = R / "output" / "involute-phase-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  ★★ 直接相位=%s · 展开相位=%s · 摆线齿根=%s"
          % (ev["direct_phase_ok"], ev["expanded_phase_ok"], ev["trochoid_ok"]))
    for c in ev["cases"]:
        print("  %-40s ok=%-6s 段 %s" % (c.get("tag", "")[:40], c.get("ok"), c.get("seg")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  产物：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
