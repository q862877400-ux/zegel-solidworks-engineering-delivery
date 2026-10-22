r"""@brief 真机冒烟：`sw_sketch_edit.create_sketch_chamfer`（草图倒角）。

## 为什么挑它
`024`（轮 105）补了草图倒角/镜像，**只有静态证据**。
★ 而且它的**前置条件最具体**：官方写「creates a chamfer **between two selected sketch entities**」
⇒ 正好能验「**选中两条实体**」这个前置到底怎么起作用。

## 安全设计（轮 98 的模态框教训）
* **只在新零件上跑**，绝不碰用户文档；
* 前置**程序化造**：进草图 → 画**两条相交直线** → 用声明式选择选中两条；
* 先置 `CommandInProgress = True`；⚠ **事实 64**：压不住所有弹框 ⇒ **收尾查模态框**；
* 收尾：关掉自己建的件（**不保存**）。

## 判据
* 两条直线能不能画出来、能不能**同时选中**；
* `create_sketch_chamfer` 能否返回一个**草图线段对象**（官方返回 `SketchSegment`）；
* ★ **倒角后草图线段数应当变化**（倒角会把角切掉、多出一段）——
  这是"**能被空操作证伪**"的那种证据；
* 任何一步抛 ⇒ **记下来**。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_sketch_edit_smoke.py
# 定位:   给 `scripts/sw_sketch_edit.py` 的倒角（`024` 补的能力）取**真机**证据。
# 官方依据: `scripts/sw_sketch_edit.py` 的来源块（反射 + `C:\swapi`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
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
    Path(__file__).resolve().parents[1] / "output" / "sketch-edit-smoke-evidence.json"
)


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

        from scripts import sw_part, sw_selection_spec, sw_sketch, sw_sketch_edit

        def timed(fn):
            t0 = time.time()
            try:
                return True, fn(), time.time() - t0
            except Exception as exc:  # noqa: BLE001
                return (
                    False,
                    "%s: %s" % (type(exc).__name__, str(exc)[:160]),
                    time.time() - t0,
                )

        # ① 程序化造前置：进草图 → 画两条（首尾相接的）直线
        ok, r, _ = timed(lambda: sw_part.start_sketch(scratch))
        chk("start_sketch（进草图编辑态）", ok, "ok" if ok else r)
        ok1, r1, _ = timed(lambda: sw_part.sketch_line(scratch, -20.0, 0.0, 0.0, 0.0))
        chk("画直线 1（-20,0 → 0,0）", ok1, "ok" if ok1 else r1)
        ok2, r2, _ = timed(lambda: sw_part.sketch_line(scratch, 0.0, 0.0, 0.0, 20.0))
        chk("画直线 2（0,0 → 0,20）", ok2, "ok" if ok2 else r2)

        skm = sw_connect.safe_get_com_member(scratch, "SketchManager")
        sketch = sw_connect.safe_get_com_member(skm, "ActiveSketch") if skm else None
        segs = []
        if sketch is not None:
            oks, rs, _ = timed(lambda: sw_sketch.get_sketch_segments(sketch))
            segs = rs if oks and isinstance(rs, list) else []
        chk("取到草图线段", len(segs) >= 2, "%d 个线段（应为 2）" % len(segs))
        ev["segments_before"] = len(segs)

        # ② ★ 同时选中两条（官方前置：**between two selected sketch entities**）
        sel_cnt = 0
        if len(segs) >= 2:

            def _sel_both():
                sw_selection_spec.clear_selection(scratch)
                n1 = sw_selection_spec.select_object(scratch, segs[0], append=False)
                n2 = sw_selection_spec.select_object(scratch, segs[1], append=True)
                return max(int(n1 or 0), int(n2 or 0))

            oksel, rsel, _ = timed(_sel_both)
            sel_cnt = int(rsel) if oksel and isinstance(rsel, int) else 0
        chk(
            "★ 同时选中**两条**草图实体（官方前置）",
            sel_cnt >= 2,
            "选区计数 = %d" % sel_cnt,
        )
        ev["selection"] = sel_cnt

        # ③ ★ 核心：倒角
        #: ⚠⚠⚠ **必须用 `distance_equal`(2)** —— 轮 164 实测（`tools/probe_chamfer_forms
        #: .py`）：
        #: `type=0`（默认的 `distance_angle`）/ `type=1` ⇒ 段数**不变**且返回 None；
        #: **`type=2` ⇒ 段数 `2 → 3`**（倒角真的建出来了）。
        #: ★ 而 `type=2` 的返回对象**拿不到**（`com_error 0x80010105`）——
        #: 那只是「取返回值」失败，**不代表倒角没做**（轮 122 正是据此误判为"架构性限制"
        #: ）。
        okc, rc, dtc = timed(
            lambda: sw_sketch_edit.create_sketch_chamfer(
                scratch, chamfer_type=2, distance_mm=5.0
            )
        )
        chk(
            "★ create_sketch_chamfer(distance_equal=2, 5mm)",
            okc,
            ("返回 %s · %.2fs" % (type(rc).__name__, dtc)) if okc else rc,
        )
        ev["chamfer_ok"] = bool(okc)

        # ★★ 硬验证：倒角会把角切掉 ⇒ 线段数应当**变化**
        segs2 = []
        if sketch is not None:
            oks2, rs2, _ = timed(lambda: sw_sketch.get_sketch_segments(sketch))
            segs2 = rs2 if oks2 and isinstance(rs2, list) else []
        ev["segments_after"] = len(segs2)
        chk(
            "★★ 倒角后**线段数变了**（能被空操作证伪）",
            okc and len(segs2) != len(segs),
            "倒角前 %d → 倒角后 %d" % (len(segs), len(segs2)),
        )

        ok, r, _ = timed(lambda: sw_part.end_sketch(scratch))
        chk("end_sketch（退出草图）", ok, "ok" if ok else r)
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
    print("  ⚠ 只证「调通了 + 线段数变了」；**不证倒角的距离 5mm 对不对**。")
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
