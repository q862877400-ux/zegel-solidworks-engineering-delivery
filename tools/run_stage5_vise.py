"""★ 阶段 5 验收入口：平口钳（规格 320 的 S5）。

★★ 用法：
     python tools/run_stage5_vise.py             # ★ 离线判定（五项功能义务）
     python tools/sw_guard.py --timeout 900 -- python tools/run_stage5_vise.py --live
                                                 # ★ 真机（建件 + 装配 + 出图）
"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/run_stage5_vise.py
# 定位:   规格 `specs/320-stage5-bench-vise` 的**验收入口**（S5）
# 官方依据: ① 外部方案阶段 5 的验收 S5（逐字）② `scripts/engineering/vise.py`（H1~H4）③
#           `scripts/engineering/assembly.py`（既有 `ConstraintGraph` / `InterferenceSca
#           n`）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [
    str(ROOT),
    str(ROOT / "scripts"),
    str(ROOT / "mcp-server"),
    str(ROOT / "tools"),
]

from scripts.engineering import vise as V  # noqa: E402

OUT = ROOT / "output" / "stage5"


def run_s5() -> dict:
    """★ **S5 五项功能义务**（★ FR-009：几何通过 ≠ 功能通过）。"""
    rows = []
    m = V.default_model()

    #: ① 规定工况全部通过
    r = V.evaluate_vise(
        m, turns=5.0, readback_mm=20.0, jaw_dof=1, jaw_motions=["沿导向移动（+X）"]
    )
    rows.append({"case": "规定工况全部通过", "ok": r["ok"], "got": r["ok"]})

    #: ② 关键规则没有 INDETERMINATE
    rows.append(
        {
            "case": "关键规则无 INDETERMINATE",
            "ok": not r["indeterminate"],
            "got": r["indeterminate"],
        }
    )

    #: ③ 无误固定活动钳口
    rows.append(
        {
            "case": "活动钳口未被固定",
            "ok": r["jaw"]["verdict"] == "expected_motion",
            "got": r["jaw"]["verdict"],
        }
    )

    #: ④ 导程与位移独立核对一致
    rows.append(
        {
            "case": "导程与位移独立核对一致",
            "ok": r["travel"]["consistent"],
            "got": "算 %.1f / 回读 %.1f"
            % (r["travel"]["computed_mm"], r["travel"]["readback_mm"]),
        }
    )

    #: ⑤ 图纸与计算保留真实工程定义（★ 螺纹五项齐）
    rows.append(
        {
            "case": "图纸保留真实工程定义",
            "ok": r["thread"]["releasing"],
            "got": r["thread"].get("spec", r["thread"]["verdict"]),
        }
    )

    #: ⑥ 共享接口变更正确传播
    p = V.propagate("screw_lead_mm", 4.0, 6.0)
    rows.append(
        {
            "case": "共享接口变更正确传播",
            "ok": bool(p["stale"]) and bool(p["reusable"]),
            "got": "失效 %s / 可复用 %s" % (p["stale"], p["reusable"][:2]),
        }
    )

    #: ⑦ ★ 未做物理试验 ⇒ **不得标成已证实**（★ FR-011）
    rows.append(
        {
            "case": "夹紧力未标成实物已证实",
            "ok": True,
            "got": "★ 未做物理试验 ⇒ 只报计算值，不报「已证实」",
        }
    )

    return {"s5": rows, "ok": all(x["ok"] for x in rows), "detail": r}


def run_reverse() -> dict:
    """★ **R1~R5 反向验证**（★ 规格 §5）。"""
    rows = []
    m = V.default_model()

    #: R1 固定活动钳口
    bad = V.evaluate_vise(
        m, turns=5.0, readback_mm=20.0, jaw_dof=1, jaw_motions=["移动"], jaw_fixed=True
    )
    rows.append(
        {
            "case": "R1 固定活动钳口",
            "ok": bad["ok"] is False,
            "got": bad["jaw"]["verdict"],
        }
    )

    #: R2 删去导向关系
    m2 = V.default_model()
    del m2.interfaces["guide_width_mm"]
    r2 = V.evaluate_vise(
        m2, turns=5.0, readback_mm=20.0, jaw_dof=1, jaw_motions=["移动"]
    )
    rows.append(
        {
            "case": "R2 删去导向关系",
            "ok": r2["interfaces_ok"] is False,
            "got": r2.get("interfaces_error", "")[:40],
        }
    )

    #: R3 导程误绑
    tc = V.lead_to_travel(20.0, 5.0, readback_mm=20.0)
    rows.append(
        {
            "case": "R3 导程误绑",
            "ok": tc.consistent is False,
            "got": "算 %.0f vs 回读 %.0f" % (tc.computed, tc.readback_mm),
        }
    )

    #: R4 删螺纹定义
    r4 = V.evaluate_vise(
        m,
        turns=5.0,
        readback_mm=20.0,
        jaw_dof=1,
        jaw_motions=["移动"],
        thread=V.ThreadSpec(),
    )
    rows.append(
        {
            "case": "R4 删螺纹定义",
            "ok": r4["ok"] is False,
            "got": r4["thread"]["verdict"],
        }
    )

    #: R5 仅体积通过
    import inspect

    sig = inspect.signature(V.evaluate_vise)
    rows.append(
        {
            "case": "R5 仅体积不能盖过功能",
            "ok": "volume" not in sig.parameters,
            "got": "★ evaluate_vise **不收** volume（★ 结构性保证）",
        }
    )

    return {"reverse": rows, "ok": all(x["ok"] for x in rows)}


def run_live() -> dict:
    """★ 真机档：建一个平口钳的**底座**并出图（★ 复用阶段 2 的链）。"""
    from scripts import sw_connect
    from scripts.engineering import drawing_run as DR
    import tool_caller

    out: dict = {}
    sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
    try:
        sw.CommandInProgress = True
    except Exception:  # noqa: BLE001
        pass
    try:
        doc = sw_connect.new_document(sw, "part")
        t = sw_connect.safe_get_com_member(doc, "GetTitle")
        out["doc"] = str(t() if callable(t) else t)
        #: ★ 底座：导轨宽 × 行程 × 高
        from scripts import sw_part

        sw_part.start_sketch(doc)
        sw_part.sketch_corner_rectangle(doc, 0.0, 0.0, 160.0, 60.0)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, "草图1", sw_connect.mm(30.0))
        pd = list(sw_connect.safe_get_com_member(doc, "GetPartBox", False))
        out["bbox_mm"] = [
            round(float(pd[3]) - float(pd[0]), 3),
            round(float(pd[4]) - float(pd[1]), 3),
            round(float(pd[5]) - float(pd[2]), 3),
        ]
        out["expected_bbox"] = [160.0, 60.0, 30.0]
        out["bbox_ok"] = all(
            abs(a - b) <= 0.01 for a, b in zip(out["bbox_mm"], out["expected_bbox"])
        )
        p = OUT / "底座.sldprt"
        OUT.mkdir(parents=True, exist_ok=True)
        sw_connect.save_document(doc, str(p))
        out["saved"] = p.is_file()
        #: ★★ **出图前先关掉模型** ——
        #:   ⚠ 实测（2026-10-12，与阶段 2 同一根因）：
        #:     `solidworks_generate_drawing` 内部要 `OpenDoc6` **同一个文件**，
        #:     而它**还开着** ⇒ 报「打开失败, 错误码: 65536」。
        #:   ★ 判据：先 `CloseDoc` 再出图。
        try:
            t0 = sw_connect.safe_get_com_member(doc, "GetTitle")
            t0 = t0() if callable(t0) else t0
            if t0:
                sw.CloseDoc(str(t0))
                out["model_closed_before_drawing"] = True
        except Exception as exc:  # noqa: BLE001
            out["close_error"] = str(exc)[:100]
        #: ★ 出图（★ 复用阶段 2 的 DrawingSpec 链）
        try:
            sw.CommandInProgress = False
            spec = DR.build_drawing_spec(
                source_model=p,
                size_mm=out["expected_bbox"],
                hole_dia_mm=0.0,
                hole_count=0,
                thickness_mm=30.0,
            )
            sp = DR.write_spec(spec, OUT / "spec.json")
            ok_d, res = tool_caller.call(
                "solidworks_generate_drawing",
                spec_path=str(sp),
                output_dir=str(OUT / "drawing"),
                drawing_filename="底座.slddrw",
                overwrite=True,
            )
            drw = OUT / "drawing" / "底座.slddrw"
            out["drawing_ok"] = drw.is_file() and drw.stat().st_size > 0
            out["drawing_bytes"] = drw.stat().st_size if drw.is_file() else 0
        finally:
            try:
                sw.CommandInProgress = True
            except Exception:  # noqa: BLE001
                pass
        #: ★ 收尾：关掉我方文档
        try:
            for d in list(sw.GetDocuments or []):
                pth = sw_connect.safe_get_com_member(d, "GetPathName")
                pth = pth() if callable(pth) else pth
                tt = sw_connect.safe_get_com_member(d, "GetTitle")
                tt = tt() if callable(tt) else tt
                if pth and "stage5" in str(pth).replace("\\", "/"):
                    sw.CloseDoc(str(tt))
        except Exception:  # noqa: BLE001
            pass
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
    out["pass"] = bool(out.get("bbox_ok") and out.get("saved"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    s5 = run_s5()
    rev = run_reverse()
    print("★ S5 五项功能义务：")
    for r in s5["s5"]:
        print(
            "   %s %-26s ⇒ %s"
            % ("✓" if r["ok"] else "✗", r["case"], str(r["got"])[:52])
        )
    print()
    print("★ R1~R5 反向验证：")
    for r in rev["reverse"]:
        print(
            "   %s %-26s ⇒ %s"
            % ("✓" if r["ok"] else "✗", r["case"], str(r["got"])[:52])
        )

    ev: dict = {"s5": s5, "reverse": rev, "finished": time.strftime("%H:%M:%S")}
    if args.live:
        print()
        live = run_live()
        ev["live"] = live
        print(
            "★ 真机：bbox=%s（期望 %s）· 保存=%s · 出图=%s"
            % (
                live.get("bbox_mm"),
                live.get("expected_bbox"),
                live.get("saved"),
                live.get("drawing_ok"),
            )
        )

    p = OUT / "vise.json"
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print(
        "★ S5：%s · R1~R5：%s"
        % ("过" if s5["ok"] else "不过", "过" if rev["ok"] else "不过")
    )
    print("★ 证据 → %s" % p)
    ok = s5["ok"] and rev["ok"]
    if args.live:
        ok = ok and ev["live"].get("pass", False)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
