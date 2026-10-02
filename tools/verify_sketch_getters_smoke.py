r"""@brief 真机冒烟：`sw_sketch` 的取法 —— 重点验**轮 111 换到后继的那 6 个**。

## 为什么最高优先
轮 111（Spec Kit `030`）把 6 个官方已废弃的 `ISketch` 取法换成了后继，
其中 **`GetLines2` 还多带一个参数**（`swCrossHatchFilter_e`）。
⚠ 那次**只有静态证据** —— 万一签名对不上，**代码会在运行期炸**。
⇒ 本冒烟在真机上**造一个草图**（程序化，不靠人手），再逐个调过去。

## 安全设计（轮 98 的模态框教训）
* **只在新零件上跑**，绝不碰用户文档；
* 先置 `CommandInProgress = True`；⚠ **已知事实 64**：它压不住所有弹框 ⇒ **收尾必查残留模态框**；
* 收尾：关掉自己建的件（**不保存**）。

## 判据
* 每个取法**拿到的是不是 list**（形状对不对）；
* **画了 1 条线 + 1 段弧** ⇒ `get_lines` / `get_arcs` 应**非空**（
  ★ 这才叫"验到了"，不是"没报错"）；
* 任何一步抛 ⇒ **记下来**（那才是发现）。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_sketch_getters_smoke.py
# 定位:   给轮 111（`030`）改的 6 个后继取法取**真机**证据。
# 官方依据: `scripts/sw_sketch.py` 的来源块（`ISketch` 段反射 + `C:\swapi`）
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

OUT = Path(r"D:\AI\SW\output\sketch-getters-smoke-evidence.json")
#: 轮 111 换到后继的 6 个（**本冒烟的重点**）
SUCCESSORS = ("get_lines", "get_arcs", "get_ellipses",
              "get_parabolas", "get_sketch_points", "get_user_points")


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
        print("   %s %-42s %s" % ("✓" if ok else "**✗**", name, str(detail)[:74]))

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

        from scripts import sw_part, sw_sketch

        def timed(fn):
            t0 = time.time()
            try:
                return True, fn(), time.time() - t0
            except Exception as exc:      # noqa: BLE001
                return False, "%s: %s" % (type(exc).__name__, str(exc)[:150]), time.time() - t0

        # ① 造草图：进编辑态 → 画 1 条线 + 1 段弧
        ok, r, dt = timed(lambda: sw_part.start_sketch(scratch))
        chk("start_sketch（进草图编辑态）", ok, "ok" if ok else r)
        ok2, r2, _ = timed(lambda: sw_part.sketch_line(scratch, -20.0, 0.0, 20.0, 0.0))
        chk("sketch_line（画 1 条线）", ok2, "ok" if ok2 else r2)
        ok3, r3, _ = timed(lambda: sw_part.sketch_arc(scratch, 0.0, 15.0, -10.0, 15.0, 10.0, 15.0))
        chk("sketch_arc（画 1 段弧）", ok3, "ok" if ok3 else r3)
        ev["built"] = {"line": ok2, "arc": ok3}

        # ② 拿 ActiveSketch（取法要 ISketch 对象）
        skm = sw_connect.safe_get_com_member(scratch, "SketchManager")
        sketch = sw_connect.safe_get_com_member(skm, "ActiveSketch") if skm else None
        chk("取到 ActiveSketch", sketch is not None, type(sketch).__name__ if sketch else "None")

        # ③ ★ 逐个调 6 个后继取法 —— **本冒烟的重点**
        if sketch is not None:
            for fn_name in SUCCESSORS:
                fn = getattr(sw_sketch, fn_name, None)
                if fn is None:
                    chk(fn_name, False, "模块里没有这个函数")
                    continue
                okc, rr, dtt = timed(lambda f=fn: f(sketch))
                n = len(rr) if okc and hasattr(rr, "__len__") else -1
                chk("★ %s（后继）" % fn_name, okc and isinstance(rr, list),
                    ("list · %d 个元素 · %.2fs" % (n, dtt)) if okc else rr)
                ev.setdefault("getters", {})[fn_name] = {"ok": okc, "n": n}

            # ★ **验到了才算**：画了线，lines 应非空
            got_lines = ev.get("getters", {}).get("get_lines", {}).get("n", 0)
            chk("★★ 画了线 ⇒ get_lines **非空**（不是「没报错」就算）",
                got_lines and got_lines > 0, "lines = %s" % got_lines)

            #: ★★ 轮 140 新增：**定量**判据 —— 「非空」太弱（12 对 1 也绿）。
            #: 实测：每条直线占 **12 个 float**（`tools/probe_getlines_count.py`）。
            chk("★★ **定量**：`get_lines` 的元素个数 = 条数 × 12（实测语义）",
                got_lines == 1 * 12,
                "lines=%s，期望 1×12=12" % got_lines)

            # 顺带：几个**没换**的取法作对照
            for fn_name in ("get_sketch_segments", "get_splines", "get_polylines"):
                fn = getattr(sw_sketch, fn_name, None)
                if fn is None:
                    continue
                okc, rr, _ = timed(lambda f=fn: f(sketch))
                chk("  %s（未换，对照）" % fn_name, okc,
                    "list · %d" % len(rr) if okc and hasattr(rr, "__len__") else rr)

        # ④ 收尾草图
        ok, r, _ = timed(lambda: sw_part.end_sketch(scratch))
        chk("end_sketch（退出草图）", ok, "ok" if ok else r)
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
    print("  ⚠ 只证「这些调用没抛异常 + 元素数合理」；**不证明元素内容正确**。")
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
