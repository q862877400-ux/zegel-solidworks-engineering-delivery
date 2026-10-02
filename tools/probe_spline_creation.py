r"""@brief 探针：`sw_part.sketch_spline` 到底建没建成？（轮 141 里 `segments=0` 的追问）

## 疑问
`tools/probe_sketch_getter_shapes.py`：画 1/2 条样条后
`get_sketch_segments` 的**真值都是 0** ⇒ **草图里根本没有线段** ——
而调用**没有抛异常**。⇒ 要么 `CreateSpline` 静默失败，要么它建的**不是草图线段**。

## 判法
① 调 `sketch_spline`，**打印返回值**（`None`？`Dispatch`？）；
② 立刻数 `get_sketch_segments`（真值）；
③ 对照：同样流程画一条**直线** ⇒ 真值应为 1（**证明流程本身没问题**）。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_spline_creation.py
# 定位:   给 Spec Kit `060` 取证：`sketch_spline` 是否静默空操作。
# 官方依据: 出厂反射 `iface_*.txt` 的 `CreateSpline*` 成员
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

OUT = Path(r"D:\AI\SW\output\spline-creation-evidence.json")
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
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "cases": {}}
    sw = None
    docs: list = []
    try:
        import sw_connect
        from scripts import sw_part, sw_sketch
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass

        #: 打印 `sketch_spline` 的源码（先把"它到底调了什么"看清楚）
        import inspect
        print("  `sketch_spline` 的实现：")
        for l in inspect.getsource(sw_part.sketch_spline).splitlines()[:24]:
            print("    %s" % l[:100])
        print()

        for label, fn in (
            ("对照·直线", lambda d: sw_part.sketch_line(d, -10.0, 0.0, 10.0, 0.0)),
            ("样条(4 点)", lambda d: sw_part.sketch_spline(
                d, [(-20.0, 0.0), (-7.0, 8.0), (7.0, -8.0), (20.0, 0.0)])),
        ):
            d = sw_connect.new_document(sw, "part")
            docs.append(d)
            sw_part.start_sketch(d)
            try:
                ret = fn(d)
                rtxt = type(ret).__name__
            except Exception as exc:      # noqa: BLE001
                ret, rtxt = None, "EXC: %s: %s" % (type(exc).__name__, str(exc)[:90])
            skm = sw_connect.safe_get_com_member(d, "SketchManager")
            sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")
            try:
                segs = sw_sketch.get_sketch_segments(sk)
                n = len(segs) if isinstance(segs, list) else -1
                types = [type(x).__name__ for x in segs] if isinstance(segs, list) else []
            except Exception as exc:      # noqa: BLE001
                n, types = -1, ["EXC:%s" % str(exc)[:50]]
            print("  %-12s 返回值=%-16s ⇒ `get_sketch_segments` = %d %s"
                  % (label, rtxt, n, types[:3]))
            ev["cases"][label] = {"return": rtxt, "segments": n, "seg_types": types}
            #: 顺带试 `get_splines`
            try:
                sp = sw_sketch.get_splines(sk)
                spn = len(sp) if isinstance(sp, list) else -1
                spt = type(sp[0]).__name__ if isinstance(sp, list) and sp else "—"
            except Exception as exc:      # noqa: BLE001
                spn, spt = -2, "EXC:%s" % str(exc)[:50]
            print("               `get_splines` = %s（元素类型 %s）" % (spn, spt))
            ev["cases"][label]["splines"] = spn
            sw_part.end_sketch(d)
            t = str(sw_connect.safe_get_com_member(d, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
            docs.remove(d)
    except Exception as exc:      # noqa: BLE001
        print("  ⚠ 探针出错：%s: %s" % (type(exc).__name__, str(exc)[:160]))
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass
        for d in docs:
            try:
                t = str(sw_connect.safe_get_com_member(d, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
            except Exception:      # noqa: BLE001
                pass

    modals, _win_scanned = modal_dialogs()
    print()
    print("   收尾模态框: %s（扫了 %d 个窗口）"
          % ("无" if not modals else modals, _win_scanned))
    ev["modal_dialogs"] = modals
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
