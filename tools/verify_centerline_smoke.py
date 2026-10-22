r"""@brief 真机冒烟：`sw_part.sketch_centerline` + **再测一次长度单位**。

## 要证的三件事
1. **建成**：`ISketchManager.CreateCenterLine` 返回非 `None`；
2. ★★ **往返一致**：画完能从草图里**读回来**（`get_sketch_segments` / `get_lines`）；
3. ★★ **再测单位**：官方文档写「**in meters**」，而轮 132 实测是**毫米**
   ⇒ 本轮**再测一次**（用中心线 + 边界框）：若单位真是米，跨度会是 **1000×** 那个量级。

## 安全设计
* **只在新零件上跑**，绝不碰用户文档；收尾**关件不保存**；
* `CommandInProgress` + **收尾查模态框**（已知事实 64）。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_centerline_smoke.py
# 定位:   给 `scripts/sw_part.sketch_centerline`（轮 140 补的 `centerline`）取真机证据；
#         并**再测**官方文档那句「in meters」。
# 官方依据: `C:\swapi\types\ISketchManager\CreateCenterLine.md`；`C:\swapi\types\IBody2\
#           GetBodyBox.md`（已知事实 71：返回**毫米**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes as w
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
    Path(__file__).resolve().parents[1] / "output" / "centerline-smoke-evidence.json"
)
#: 中心线：从 (-30, 0) 到 (30, 0) —— 单位**待验证**（毫米则跨度 60，米则 60000）
X1, Y1, X2, Y2 = -30.0, 0.0, 30.0, 0.0
#: 为了量单位，另外画一个圆并拉伸：半径 25 ⇒ 毫米则跨度 50
R_CIRCLE, DEPTH = 25.0, 10.0


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
        print("   %s %-46s %s" % ("✓" if ok else "**✗**", name, str(detail)[:70]))

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

        def timed(fn):
            t0 = time.time()
            try:
                return True, fn(), time.time() - t0
            except Exception as exc:  # noqa: BLE001
                return (
                    False,
                    "%s: %s" % (type(exc).__name__, str(exc)[:140]),
                    time.time() - t0,
                )

        # ══ 第 ① 段：中心线（只画，不拉伸）════════════════════════
        scratch = sw_connect.new_document(sw, "part")
        chk("新建临时零件（不碰用户文档）", scratch is not None, "ok")
        ok, r, _ = timed(lambda: sw_part.start_sketch(scratch))
        chk("start_sketch", ok, "ok" if ok else r)
        oks, seg, dts = timed(
            lambda: sw_part.sketch_centerline(scratch, X1, Y1, X2, Y2)
        )
        chk(
            "★ sketch_centerline（(%.0f,%.0f)→(%.0f,%.0f)）" % (X1, Y1, X2, Y2),
            oks,
            ("返回 %s · %.2fs" % (type(seg).__name__, dts)) if oks else seg,
        )

        # ★★ 往返一致
        if oks:
            skm = sw_connect.safe_get_com_member(scratch, "SketchManager")
            sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")
            oka, segs, _ = timed(lambda: sw_sketch.get_sketch_segments(sk))
            na = len(segs) if oka and isinstance(segs, list) else -1
            chk(
                "★★ 往返 A：`get_sketch_segments` 读回 ≥1 段",
                na >= 1,
                "读回 %d 段" % na,
            )
            ev["segments_read_back"] = na
            okb, lns, _ = timed(lambda: sw_sketch.get_lines(sk))
            nb = len(lns) if okb and isinstance(lns, list) else -1
            #: ⚠ 中心线是**构造几何** —— `get_lines` 收不收它，**本轮量出来**
            chk(
                "★ 往返 B：`get_lines` 是否把中心线算作直线（量出来）",
                True,
                "读回 %d 条（%s）"
                % (nb, "算" if nb >= 1 else "**不算** —— 是构造几何"),
            )
            ev["lines_read_back"] = nb
        ok, r, _ = timed(lambda: sw_part.end_sketch(scratch))
        chk("end_sketch", ok, "ok" if ok else r)

        # ══ 第 ② 段：**再测单位**（圆 + 边界框）══════════════════
        scratch2 = sw_connect.new_document(sw, "part")
        timed(lambda: sw_part.start_sketch(scratch2))
        timed(lambda: sw_part.sketch_circle(scratch2, 0.0, 0.0, R_CIRCLE))
        timed(lambda: sw_part.end_sketch(scratch2))
        oke, re_, _ = timed(lambda: sw_part.extrude_boss(scratch2, "草图1", DEPTH))
        okb2, box, _ = timed(lambda: sw_part.get_bounding_box(scratch2))
        if oke and okb2:
            got = sorted(round(float(v), 6) for v in box["size"])
            ev["circle_bbox"] = got
            chk(
                "★★ **再测单位**：半径 %.0f 的圆 ⇒ 边界框 **%.0f** ⇒ %s"
                % (R_CIRCLE, 2 * R_CIRCLE, "**毫米**（官方文档的「meters」是错的）"),
                got == sorted([2 * R_CIRCLE, 2 * R_CIRCLE, DEPTH]),
                "实测 size=%s" % got,
            )
        else:
            chk("再测单位", False, str(re_)[:80] if not oke else str(box)[:80])
        if scratch2 is not None:
            t2 = str(sw_connect.safe_get_com_member(scratch2, "GetTitle") or "")
            if t2:
                sw.CloseDoc(t2)
                print("   （已关闭 %s，不保存）" % t2)
    except Exception as exc:  # noqa: BLE001
        chk("整体冒烟", False, "%s: %s" % (type(exc).__name__, str(exc)[:180]))
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
        "★ 收尾无残留模态框（已知事实 64）",
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
    print("  ⚠ 只证「建成了 + 读得回来」；**不证中心线的构造几何标记**是否设置。")
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
