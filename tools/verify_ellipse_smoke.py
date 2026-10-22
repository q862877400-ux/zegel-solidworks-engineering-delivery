r"""@brief 真机冒烟：`sw_part.sketch_ellipse` + **顺带量准 sketch 助手的单位**。

## 为什么挑它
`ellipse` 在「真缺」档里；而且**有现成的验证手段** ——
轮 117 已验过 `sw_sketch.get_ellipses`（当时返回 0，因为没画椭圆）
⇒ ★ 本轮可以**造一个椭圆再读回来**，做**往返一致**的证据。

## 顺带要量清的（轮 132 发现的疑点）
`sw_part` 的 `sketch_circle` / `sketch_corner_rectangle` 的 docstring 写「单位: 米」，
但轮 127 的冒烟里传 **80 / 60 / 50** 得到的是 **80×60×50 mm** 的盒子
⇒ **docstring 与实际不符**。本轮用**圆 + 边界框**把它量准。

## 安全设计
* **只在新零件上跑**，绝不碰用户文档；只进草图、画、读；收尾**关件不保存**；
* `CommandInProgress` + **收尾查模态框**。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_ellipse_smoke.py
# 定位:   给 `scripts/sw_part.sketch_ellipse`（轮 132 补的 `ellipse`）取真机证据；
#         并**量准 sketch 助手的长度单位**。
# 官方依据: `C:\swapi\types\ISketchManager\CreateEllipse.md`；`C:\swapi\types\IBody2\Get
#           BodyBox.md`（已知事实 71：返回**毫米**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "ellipse-smoke-evidence.json"
)
#: 椭圆：中心 (0,0)，长半轴 40（沿 +x），短半轴 20（沿 +y）—— 单位**待验证**
CX, CY, MAJ, MIN = 0.0, 0.0, 40.0, 20.0
#: 「圆 + 边界框」用来量单位：半径 25
R_CIRCLE = 25.0


def modal_dialogs() -> tuple:
    """★ 已改为**委托共享实现**（2026-10-01 轮 149）。"""
    try:
        from scripts.sw_connect import residual_dialogs
    except ImportError:
        from sw_connect import dismiss_residual_dialogs, residual_dialogs
    #: ★ 2026-10-01（轮 169）：**查到了就点掉**（兜底）——
    #: 只查不点的脚本在真发现弹窗时**什么也没处置**，弹窗还在 ⇒ 下一轮挂在这儿。
    _dialogs, _scanned = residual_dialogs()
    if _dialogs:
        dismiss_residual_dialogs()
    return _dialogs, _scanned


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {}}
    checks: list = []

    def chk(name, ok, detail):
        checks.append(bool(ok))
        ev["checks"][name] = {"ok": bool(ok), "detail": str(detail)[:300]}
        print("   %s %-44s %s" % ("✓" if ok else "**✗**", name, str(detail)[:72]))

    sw = None
    scratch = None
    try:
        import sw_connect

        from scripts import sw_part, sw_sketch

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        scratch = sw_connect.new_document(sw, "part")
        chk("新建临时零件（不碰用户文档）", scratch is not None, "ok")

        def timed(fn):
            t0 = time.time()
            try:
                return True, fn(), time.time() - t0
            except Exception as exc:  # noqa: BLE001
                return (
                    False,
                    "%s: %s" % (type(exc).__name__, str(exc)[:150]),
                    time.time() - t0,
                )

        # ══ 第 ① 段：量准单位（圆 → 边界框）══════════════════════
        ok, r, _ = timed(lambda: sw_part.start_sketch(scratch))
        chk("start_sketch", ok, "ok" if ok else r)
        ok, r, _ = timed(lambda: sw_part.sketch_circle(scratch, 0.0, 0.0, R_CIRCLE))
        chk("sketch_circle(半径 %.0f，**未做换算**)" % R_CIRCLE, ok, "ok" if ok else r)
        ok, r, _ = timed(lambda: sw_part.end_sketch(scratch))
        chk("end_sketch", ok, "ok" if ok else r)
        oke, re_, _ = timed(lambda: sw_part.extrude_boss(scratch, "草图1", 10.0))
        chk("extrude_boss(10)", oke, "ok" if oke else re_)
        okb, box, _ = timed(lambda: sw_part.get_bounding_box(scratch))
        if okb:
            size = [float(v) for v in box["size"]]
            #: 圆的直径 = 2R = 50；拉伸 10 ⇒ {50, 50, 10}
            got = sorted(round(v, 6) for v in size)
            ev["circle_bbox_mm"] = got
            chk(
                "★★ 半径 %.0f 的圆 ⇒ 边界框跨度 **%.0f** ⇒ 输入单位就是**毫米**"
                % (R_CIRCLE, 2 * R_CIRCLE),
                got == sorted([2 * R_CIRCLE, 2 * R_CIRCLE, 10.0]),
                "实测 size=%s（若单位是「米」这里会是 50000 量级）" % got,
            )
        else:
            chk("量单位（边界框）", False, box)

        # ══ 第 ② 段：椭圆本身（新零件，干净）════════════════════
        scratch2 = sw_connect.new_document(sw, "part")
        ok, r, _ = timed(lambda: sw_part.start_sketch(scratch2))
        chk("（新件）start_sketch", ok, "ok" if ok else r)
        oks, seg, dts = timed(
            lambda: sw_part.sketch_ellipse(scratch2, CX, CY, MAJ, CY, CX, MIN)
        )
        chk(
            "★ sketch_ellipse（长半轴 %.0f / 短半轴 %.0f）" % (MAJ, MIN),
            oks,
            ("返回 %s · %.2fs" % (type(seg).__name__, dts)) if oks else seg,
        )
        ev["ellipse_created"] = bool(oks)

        # ★★ 往返一致：读回来
        if oks:
            skm = sw_connect.safe_get_com_member(scratch2, "SketchManager")
            sketch = sw_connect.safe_get_com_member(skm, "ActiveSketch")
            okr, ell, _ = timed(lambda: sw_sketch.get_ellipses(sketch))
            n = len(ell) if okr and isinstance(ell, list) else -1
            chk(
                "★★ 往返：`get_ellipses` 读回**至少 1 个**椭圆",
                n >= 1,
                "读回 %d 个（轮 117 时是 0 —— 那时没画）" % n,
            )
            ev["ellipses_read_back"] = n
            if n >= 1:
                print("       首项 = %r" % (ell[0],))
        ok, r, _ = timed(lambda: sw_part.end_sketch(scratch2))
        chk("end_sketch（椭圆那个件）", ok, "ok" if ok else r)
        if scratch2 is not None:
            t2 = str(sw_connect.safe_get_com_member(scratch2, "GetTitle") or "")
            if t2:
                sw.CloseDoc(t2)
                print("   （已关闭 %s，不保存）" % t2)
    except Exception as exc:  # noqa: BLE001
        chk("整体冒烟", False, "%s: %s" % (type(exc).__name__, str(exc)[:200]))
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if scratch is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(scratch, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
                    print("   （已关闭临时零件 %s，不保存）" % t)
        except Exception as exc:  # noqa: BLE001
            print("   ⚠ 收尾关文档失败（请人工确认）：%s" % str(exc)[:90])

    modals, _win_scanned = modal_dialogs()
    chk(
        "★ 收尾无残留模态框（已知事实 64 的检查）",
        (not modals) and _win_scanned > 0,
        "扫了 %d 个窗口 · %s"
        % (
            _win_scanned,
            "无模态框" if not modals else "有 %d 个: %s" % (len(modals), modals),
        ),
    )

    ev.update(
        passed=sum(1 for c in checks if c),
        total=len(checks),
        verdict="pass" if checks and all(checks) else "fail",
        finished=time.strftime("%Y-%m-%d %H:%M:%S"),
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print()
    print("  ── %d/%d · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
    print("  ⚠ 只证「建成了 + 读得回来」；**不证长短半轴的具体数值对不对**。")
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
