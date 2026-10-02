r"""@brief 真机冒烟：`sw_equation`（把 `stitched` 往 `verified` 推一步）。

## 安全设计（轮 98 的模态框教训）
* **只在新零件上跑**，**绝不碰用户文档**；
* 只做**全局变量方程式**（官方示例里最简单的一种：`"B" = 2`），**不建几何**；
* 先置 `CommandInProgress = True`；⚠ 已知事实 64：它**不能**抑制所有模态框 ⇒
  **跑完立刻检查有没有模态框**；
* 收尾：关掉**我自己建的那个件**（不保存）、释放 `CommandInProgress`。

## 判据（**不下"可用"结论**）
* ✅ 加 == 返回非负下标；列 == 条数对得上；求解 == 不抛；
* ❌ 任何一步抛 ⇒ 记下来（**那才是发现**）。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_equation_smoke.py
# 定位:   给 `scripts/sw_equation.py`（`028` 补的能力）取**真机**证据。
# 官方依据: `scripts/sw_equation.py` 的来源块（反射 + `C:\swapi`）
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

OUT = Path(r"D:\AI\SW\output\equation-smoke-evidence.json")
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
        print("   %s %-40s %s" % ("✓" if ok else "**✗**", name, str(detail)[:76]))

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

        from scripts import sw_equation

        def timed(fn):
            t0 = time.time()
            try:
                return True, fn(), time.time() - t0
            except Exception as exc:      # noqa: BLE001
                return False, "%s: %s" % (type(exc).__name__, str(exc)[:150]), time.time() - t0

        # 官方示例里最简单的形态：全局变量方程式
        ok, r, dt = timed(lambda: sw_equation.add_equation(scratch, '"SMOKE_B" = 2'))
        chk("add_equation('\"SMOKE_B\" = 2')", ok, ("下标=%s · %.2fs" % (r, dt)) if ok else r)
        ev["add_index"] = (r if ok else None)

        ok, r, dt = timed(lambda: sw_equation.list_equations(scratch))
        chk("list_equations（应含刚加的那条）",
            ok and isinstance(r, list) and len(r) >= 1,
            ("%d 条；首条=%r" % (len(r), r[0]) if ok and isinstance(r, list) and r else r))
        ev["listed"] = (len(r) if ok and isinstance(r, list) else None)

        ok, r, dt = timed(lambda: sw_equation.evaluate_equations(scratch))
        chk("evaluate_equations", ok, ("ok · %.2fs" % dt) if ok else r)
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

    # ⚠ 已知事实 64：CommandInProgress **不能**抑制所有模态框 ⇒ 收尾必查
    modals, _win_scanned = modal_dialogs()
    chk("★ 收尾无残留模态框（已知事实 64 的收尾检查）", (not modals) and _win_scanned > 0,
        "扫了 %d 个窗口 · %s" % (_win_scanned, "无模态框" if not modals else "有 %d 个: %s" % (len(modals), modals)))

    ev.update(passed=sum(1 for c in checks if c), total=len(checks),
              verdict="pass" if checks and all(checks) else "fail",
              finished=time.strftime("%Y-%m-%d %H:%M:%S"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print("  ── %d/%d · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
    print("  ⚠ 本冒烟**不下「可用」结论**：只证「这几步没抛异常」。")
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
