r"""@brief 真机冒烟：`sw_part.get_bounding_box`（边界框）。

## 为什么挑它
`bbox` 在 `docs/union-gap-triage.md`「真缺」档里，而且**可以用精确数字验证** ——
建一个**已知尺寸**的盒子，量出来的 `size` 应当与它相符。★ 这是最强的一档证据。

## ⚠⚠ 但官方对 `GetBodyBox` 有一句重话（本冒烟就是去**量它有多"近似"**）
> The values returned are **approximate** and **should not be used for comparison or
> calculation purposes**. Furthermore, the bounding box **may vary after rebuilding the model**.

⇒ **本冒烟的判据不能是"完全相等"**，只能是"**在容差内**"；
而且本冒烟**专门去量那个偏差有多大**（那才是这轮真正想知道的事）。

## 安全设计（轮 98 的模态框教训）
* **只在新零件上跑**，绝不碰用户文档；
* 前置**程序化造**：前视基准面 → 矩形 → 拉伸；
* `CommandInProgress` + **收尾查模态框**；收尾**关件不保存**。

## 判据
* 拿到的 `size` **在容差内**等于设计尺寸；
* ★ **量出偏差**（若偏差为 0，说明官方那句"近似"在这一情形下不影响；若不为 0，记下来）；
* 任何一步抛 ⇒ **记下来**。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_bbox_smoke.py
# 定位:   给 `scripts/sw_part.get_bounding_box`（轮 127 补的 `bbox`）取**真机**证据。
# 官方依据: `C:\swapi\types\IBody2\GetBodyBox.md`（含 IMPORTANT 的"近似"声明）
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "bbox-smoke-evidence.json")
#: 设计尺寸（毫米）：矩形 80 × 60，拉伸 50
W_MM, H_MM, D_MM = 80.0, 60.0, 50.0
#: 容差（毫米）—— 官方说"近似"，所以给一个**明确写下**的容差
TOL_MM = 1e-6


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

        from scripts import sw_part

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        scratch = sw_connect.new_document(sw, "part")
        chk(
            "新建临时零件（不碰用户文档）",
            scratch is not None,
            "ok" if scratch else "建不出来",
        )

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

        # ① 造一个已知尺寸的盒子：矩形 (0,0)-(80,60) 拉伸 50
        ok, r, _ = timed(lambda: sw_part.start_sketch(scratch))
        chk("start_sketch（进草图编辑态）", ok, "ok" if ok else r)
        ok2, r2, _ = timed(
            lambda: sw_part.sketch_corner_rectangle(scratch, 0.0, 0.0, W_MM, H_MM)
        )
        chk(
            "sketch_corner_rectangle(0,0 → %.0f,%.0f)" % (W_MM, H_MM),
            ok2,
            "ok" if ok2 else r2,
        )
        ok3, r3, _ = timed(lambda: sw_part.end_sketch(scratch))
        chk("end_sketch", ok3, "ok" if ok3 else r3)
        ok4, r4, _ = timed(lambda: sw_part.extrude_boss(scratch, "草图1", D_MM))
        chk("extrude_boss(%.0f mm)" % D_MM, ok4, "ok" if ok4 else r4)

        # ② ★ 本冒烟的核心
        okb, box, dtb = timed(lambda: sw_part.get_bounding_box(scratch))
        chk(
            "★ get_bounding_box 跑通",
            okb,
            ("size=%s · %.2fs" % (box.get("size"), dtb)) if okb else box,
        )
        ev["box"] = box if okb else None

        if okb:
            size = [float(v) for v in box["size"]]
            #: 归一化：拉伸方向（z）与两个平面方向之一应是 50，另两个是 80 / 60。
            #: ⚠ 草图在**前视基准面**上，z 是拉伸方向 ⇒ 期望 {80, 60, 50}
            want = sorted([W_MM, H_MM, D_MM])
            got = sorted(size)
            dev = [abs(a - b) for a, b in zip(got, want)]
            ev["deviation_mm"] = dev
            chk(
                "★★ size 在 %.0e mm 容差内等于 %.0f×%.0f×%.0f"
                % (TOL_MM, W_MM, H_MM, D_MM),
                all(d <= TOL_MM for d in dev),
                "got=%s want=%s 偏差=%s mm"
                % (
                    [round(x, 6) for x in got],
                    [round(x, 6) for x in want],
                    ["%.2e" % d for d in dev],
                ),
            )
            # 顺带记：min/max 也报出来
            print("       min=%s" % [round(v, 6) for v in box["min"]])
            print("       max=%s" % [round(v, 6) for v in box["max"]])
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
    print("  ⚠ 只证「这一个盒子」；⚠ 官方说该值是**近似值** ⇒ 即使这里偏差为 0，")
    print("     也**不要**据此认为它可以在别处当尺寸依据（见该函数的 docstring）。")
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
