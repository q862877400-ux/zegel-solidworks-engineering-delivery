"""★ 真机：★ **闭合齿廓的过定义根因** —— `LockStart`/`LockEnd` 是嫌疑。

★★★ **弹窗自己给了线索**（★ 证据 `output/dialog-events/2026-10-11T002512-48043426.json`）：
  ★ 正文逐字：★ **「此草图不再过定义。」** ⇒ ★ 草图**过定义** ✗

★★★ **我的假设（★ 要证）**：★ `CreateEquationSpline2` 的 **`LockStart`/`LockEnd`**
  ★★ 会给曲线**两端加"锁定"约束** ⇒ ★ 6 条曲线共享端点时，
    ★★★ **锁定约束 + 自动重合约束 互相矛盾** ⇒ **过定义** ✗
  ★ 而官方 Remarks 对这两个参数只说 "True to lock the start point of the curve" ⇒
    ★★ **它的语义边界要真机判** ✓

★★ **本探针三格对照**：
  ★ ① `LockStart=True, LockEnd=True`（★ 我一直在用的）
  ★ ② `LockStart=False, LockEnd=False`
  ★ ③ `LockStart=False, LockEnd=True`

★ 判据：★ **草图是否过定义** —— 走 `ISketch::GetConstrainedStatus()`
  （★ 官方：`0` = fully defined · 负值/其他 = 欠定义/过定义 ⇒ ★ 真机读数）✓
★ 走 `sw_guard` ✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_gear_lock_flags.py
# 定位:   ★ 业主 2026-10-10「方法要规范」—— ★ 闭合齿廓过定义的**根因判据**。
# 官方依据: `C:\swapi\types\ISketchManager\CreateEquationSpline2.md`（★ LockStart/LockEnd 语义）
#         `C:\swapi\types\ISketch\GetConstrainedStatus.md`
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


def _inv(t: float) -> float:
    return t - math.atan(t)


def tooth_curves(spec, geo):
    """★ 一个齿的 6 条真曲线（★ 与 `probe_gear_tooth_pattern` 同）。"""
    m, z = spec.module_mm, spec.teeth
    alpha = math.radians(spec.pressure_angle_deg)
    r = m * z / 2.0
    rb = r * math.cos(alpha)
    ra = r + G.ADDENDUM_COEFF * m
    hf = G.DEDENDUM_COEFF * m
    rf = r - hf
    rho = G.TOOL_TIP_RADIUS_COEFF * m
    t_b, t_a = geo.t_root, geo.t_tip
    inv_a = math.tan(alpha) - alpha
    P = math.pi / (2.0 * z) + inv_a

    def tro(phi):
        return G.trochoid_xy_mm(phi, pitch_radius_mm=r, dedendum_mm=hf,
                                tool_tip_radius_mm=rho)

    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if math.hypot(*tro(mid)) < rb:
            lo = mid
        else:
            hi = mid
    phi_b = (lo + hi) / 2.0
    P_tro = P - math.atan2(tro(phi_b)[1], tro(phi_b)[0])
    ang_tip = P - _inv(t_a)
    k_ = 1.0 / 1000.0

    def tro_expr(phase):
        a0 = phase
        x = ("%.12f*cos(t+%.12f)+%.12f*t*sin(t+%.12f)+%.12f*(-%.12f*cos(t+%.12f)"
             "+%.12f*t*sin(t+%.12f))/sqrt(%.12f+%.12f*t*t)"
             % (r * k_ - hf * k_ + rho * k_, a0, r * k_, a0, rho * k_,
                (hf - rho) * k_, a0, r * k_, a0, ((hf - rho) * k_) ** 2, (r * k_) ** 2))
        y = ("%.12f*sin(t+%.12f)-%.12f*t*cos(t+%.12f)+%.12f*(-%.12f*sin(t+%.12f)"
             "-%.12f*t*cos(t+%.12f))/sqrt(%.12f+%.12f*t*t)"
             % (r * k_ - hf * k_ + rho * k_, a0, r * k_, a0, rho * k_,
                (hf - rho) * k_, a0, r * k_, a0, ((hf - rho) * k_) ** 2, (r * k_) ** 2))
        return x, y

    x, y = tro_expr(-P_tro)
    c = [("right_trochoid", x, y, 0.0, phi_b)]
    x, y = G.involute_flank_expressions(rb, P, right=True)
    c.append(("right_involute", x, y, t_b, t_a))
    c.append(("tip_arc", "%.12f*cos(t)" % (ra * k_), "%.12f*sin(t)" % (ra * k_),
              -ang_tip, ang_tip))
    x, y = G.involute_flank_expressions(rb, -P, right=False)
    c.append(("left_involute", x, y, t_a, t_b))
    x, y = tro_expr(P_tro)
    c.append(("left_trochoid", x, y, phi_b, 0.0))
    c.append(("root_arc", "%.12f*cos(t)" % (rf * k_), "%.12f*sin(t)" % (rf * k_),
              -P_tro, P_tro))
    return c


def _status(doc):
    """★ `ISketch::GetConstrainedStatus()`（★ 官方：★ 它报草图的约束状态）。"""
    out = {}
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        if sk is None:
            return {"sketch": None}
        out["constrained_status"] = int(C.get_com_member(sk, "GetConstrainedStatus"))
    except Exception as exc:                                              # noqa: BLE001
        out["status_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:100])
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        out["segments"] = len(list(C.get_com_member(sk, "GetSketchSegments") or []))
    except Exception:                                                     # noqa: BLE001
        pass
    return out


def _one(sw, tag, curves, lock_start, lock_end):
    row = {"tag": tag, "lock_start": lock_start, "lock_end": lock_end}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        sm = C.get_com_member(doc, "SketchManager")
        #: ★★★ **关掉命令锁**（★ 否则过定义弹窗会**冻住 COM** ⇒ guard 只能 `taskkill`）——
        #:   ★★ 本仓的做法：★ `ISldWorks.CommandInProgress = True` 会**抑制模态框** ✓
        try:
            C.set_com_member(sw, "CommandInProgress", True)
            row["command_lock"] = True
        except Exception as exc:                                          # noqa: BLE001
            row["command_lock"] = "%s" % str(exc)[:80]
        ok = fail = 0
        for _, x, y, t0, t1 in curves:
            try:
                C.get_com_member(sm, "CreateEquationSpline2", x, y, "",
                                 "%r" % t0, "%r" % t1, False, 0.0, 0.0, 0.0,
                                 lock_start, lock_end)
                ok += 1
            except Exception:                                             # noqa: BLE001
                fail += 1
        row["curves_ok"] = ok
        row["curves_failed"] = fail
        row["status"] = _status(doc)
        #: ★★ 试拉伸（★ 判据：★ 返回非 None）
        try:
            sk = C.get_com_member(doc, "GetActiveSketch2")
            name = str(C.get_com_member(sk, "Name") or "") if sk else "草图1"
        except Exception:                                                 # noqa: BLE001
            name = "草图1"
        try:
            P.end_sketch(doc)
            feat = P.extrude_boss(doc, name, 0.010)
            row["extrude_ok"] = feat is not None
        except Exception as exc:                                          # noqa: BLE001
            row["extrude_ok"] = False
            row["extrude_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
        try:
            C.set_com_member(sw, "CommandInProgress", False)
        except Exception:                                                 # noqa: BLE001
            pass
    except Exception as exc:                                              # noqa: BLE001
        row["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:170])
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
    try:
        return _main()
    except BaseException:                                                 # noqa: BLE001
        (R / "output" / "_probe_gear_lock_traceback.txt").write_text(
            _tb.format_exc(), encoding="utf-8")
        raise


def _main() -> int:
    spec = G.GearSpec(module_mm=1.0, teeth=20, face_width_mm=10.0,
                      pressure_angle_deg=20.0, bore_diameter_mm=8.0)
    geo = G.calculate_gear_geometry(spec)
    curves = tooth_curves(spec, geo)
    rep = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "_": "★ 闭合齿廓过定义的根因：★ LockStart/LockEnd", "cases": []}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    rep["cases"].append(_one(sw, "① 双锁 True/True", curves, True, True))
    rep["cases"].append(_one(sw, "② 不锁 False/False", curves, False, False))
    rep["cases"].append(_one(sw, "③ 只锁末端 False/True", curves, False, True))
    p = R / "output" / "_probe_gear_lock_flags.json"
    p.write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n",
                 encoding="utf-8")
    for c in rep["cases"]:
        st = c.get("status") or {}
        print("  ★ %-22s 曲线 %s/%s · 约束状态=%s · 段数=%s · 拉伸=%s"
              % (c.get("tag"), c.get("curves_ok"), c.get("curves_ok", 0) + c.get("curves_failed", 0),
                 st.get("constrained_status"), st.get("segments"), c.get("extrude_ok")))
        if c.get("extrude_err"):
            print("        err=%s" % c["extrude_err"][:130])
        if c.get("error"):
            print("        err=%s" % c["error"][:130])
    print("  产物：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
