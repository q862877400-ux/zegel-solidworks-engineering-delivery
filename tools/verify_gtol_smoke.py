r"""@brief 真机冒烟：`sw_gtol` —— 验**上轮选的那条 2022 格式路径**能不能用。

## 为什么最高优先
`038`（轮 119）查到官方推荐的 `SetFrameSymbols2` **只对 2022 之前的 Gtol 有效**，
于是改走 `IGtolFrame.AddIndicator`。⚠ 那次**只有静态证据** ——
★ **整条路都押在 `AddIndicator` 上**：它若不成立，模块就是空的。

## 安全设计（轮 98 的模态框教训）
* **只在新零件上跑**，绝不碰用户文档；
* `InsertGtol()` **0 参、不建几何** ⇒ 风险低；
* 先置 `CommandInProgress = True`；⚠ **已知事实 64**：压不住所有弹框 ⇒ **收尾查模态框**；
* 收尾：关掉自己建的件（**不保存**）。

## 判据
* `insert_gtol` 拿到的**是不是对象**（不是 None）；
* `add_gtol_indicator` **返回 True**（★ 这才证明 2022 格式那条路通）；
* 任何一步抛 ⇒ **记下来**（那才是发现）。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_gtol_smoke.py
# 定位:   给 `scripts/sw_gtol.py`（`038` 补的能力）取**真机**证据。
# 官方依据: `scripts/sw_gtol.py` 的来源块（反射 + `C:\swapi`）
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "gtol-smoke-evidence.json")
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
        except Exception:      # noqa: BLE001
            pass
        scratch = sw_connect.new_document(sw, "part")
        chk("新建临时零件（不碰用户文档）", scratch is not None,
            str(sw_connect.safe_get_com_member(scratch, "GetTitle")) if scratch else "建不出来")

        from scripts import sw_gtol

        def timed(fn):
            t0 = time.time()
            try:
                return True, fn(), time.time() - t0
            except Exception as exc:      # noqa: BLE001
                return False, "%s: %s" % (type(exc).__name__, str(exc)[:160]), time.time() - t0

        ok, gtol, dt = timed(lambda: sw_gtol.insert_gtol(scratch))
        chk("insert_gtol（0 参，官方 InsertGtol()）", ok and gtol is not None,
            ("拿到 %s · %.2fs" % (type(gtol).__name__, dt)) if ok else gtol)
        ev["got_gtol"] = bool(ok and gtol is not None)

        if ok and gtol is not None:
            # ★ 本冒烟的核心：2022 格式那条路（IGtolFrame.AddIndicator）通不通
            ok2, r2, dt2 = timed(lambda: sw_gtol.add_gtol_indicator(
                gtol, tol_type=sw_gtol.GTOL_GEOM_SYMBOL["parallelism"], datum="A"))
            chk("★ add_gtol_indicator(parallelism, 基准 A) —— **2022 格式路径**",
                ok2, ("返回 True · %.2fs" % dt2) if ok2 else r2)
            ev["add_indicator"] = bool(ok2)

            # 对照：换一个符号再试一次
            ok3, r3, _ = timed(lambda: sw_gtol.add_gtol_indicator(
                gtol, tol_type=sw_gtol.GTOL_GEOM_SYMBOL["perpendicularity"], datum=""))
            chk("  再加一个（perpendicularity，无基准）", ok3, "ok" if ok3 else r3)
            ev["add_indicator2"] = bool(ok3)
    except Exception as exc:      # noqa: BLE001
        chk("整体冒烟", False, "%s: %s" % (type(exc).__name__, str(exc)[:200]))
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass
        try:
            if scratch is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(scratch, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
                    print("   （已关闭临时零件 %s，不保存）" % t)
        except Exception as exc:      # noqa: BLE001
            print("   ⚠ 收尾关文档失败（请人工确认）：%s" % str(exc)[:90])

    modals, _win_scanned = modal_dialogs()
    chk("★ 收尾无残留模态框（已知事实 64 的检查）", (not modals) and _win_scanned > 0,
        "扫了 %d 个窗口 · %s" % (_win_scanned, "无模态框" if not modals else "有 %d 个: %s" % (len(modals), modals)))

    ev.update(passed=sum(1 for c in checks if c), total=len(checks),
              verdict="pass" if checks and all(checks) else "fail",
              finished=time.strftime("%Y-%m-%d %H:%M:%S"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print("  ── %d/%d · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
    print("  ⚠ 只证「这些调用没抛异常 + 返回 True」；**不证明公差标得对**。")
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
